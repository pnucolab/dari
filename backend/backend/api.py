from typing import List
from ninja import NinjaAPI
from ninja.security import django_auth
from ninja.pagination import paginate, PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django_ratelimit.decorators import ratelimit

from django.contrib.auth.models import User
from dariauth.models import Default, Profile, VPNInfo, LinuxInfo, GuestInfo, Server, LinuxGroup, Log, NFSShare
from django.db.models import Max
from .schema import *
from .utils import check_active_status, check_admin_status, check_groupadmin_status, validate, ldapops, get_serverstat, send_email, send_verification_email, add_ip, delete_ip
from .logging import logger

from django.middleware.csrf import get_token
import os
import base64
import subprocess
import json
from django.utils import timezone
from django.http import FileResponse, HttpResponse

api = NinjaAPI(auth=django_auth)

@api.get("/csrftoken", auth=None)
def get_csrf_token(request):
    token = get_token(request)
    return {"csrftoken": token}

@api.get("/ldap")
def ldap(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    ldapops.update_ldap()
    return {"success": True}

@api.get("/brand", auth=None)
def brand(request):
    try:
        logo = Default.objects.get(key="logo").value
    except Default.DoesNotExist:
        logo = None
    try:
        sitename = Default.objects.get(key="sitename").value
    except Default.DoesNotExist:
        sitename = None
    return {"sitename": sitename, "logo": logo}

@api.get("/allowed-email-domains", auth=None)
def allowed_email_domains(request):
    try:
        domains = Default.objects.get(key="allowed_email_domains").value
    except Default.DoesNotExist:
        domains = ''
    return {"allowed_email_domains": domains}

@api.post("/init", auth=None)
def init(request):
    """Initial system setup: save defaults + create first admin user"""
    if User.objects.count() > 0:
        return api.create_response(request, {"error": "System already initialized"}, status=400)

    data = json.loads(request.body)

    # Defaults
    sitename = data.get('sitename', '')
    logo = data.get('logo', '')
    gid = data.get('gid', '')
    shell = data.get('shell', '')
    if not sitename or not gid or not shell:
        return api.create_response(request, {"error": "Missing required settings"}, status=400)

    # Admin info
    username = data.get('username', '')
    password = data.get('password', '')
    name = data.get('name', '')
    email = data.get('email', '')
    if not username or not password or not name or not email:
        return api.create_response(request, {"error": "Missing admin account fields"}, status=400)

    if not validate(username):
        return api.create_response(request, {"error": "Invalid username format"}, status=400)

    try:
        # Save defaults
        Default.objects.update_or_create(key="sitename", defaults={'value': sitename})
        Default.objects.update_or_create(key="gid", defaults={'value': gid})
        Default.objects.update_or_create(key="shell", defaults={'value': shell})
        if logo:
            Default.objects.update_or_create(key="logo", defaults={'value': logo})
        else:
            Default.objects.get_or_create(key="logo", defaults={'value': ''})
        for key in ['allowed_email_domains']:
            Default.objects.update_or_create(key=key, defaults={'value': data.get(key, '')})

        # Create group
        lg, _ = LinuxGroup.objects.get_or_create(name=gid, defaults={'gid': 70000})

        # Create admin user
        user = User(username=username, email=email, is_active=True, is_staff=True, is_superuser=True)
        user.save()

        # Create verified email address for admin
        from allauth.account.models import EmailAddress
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)

        profile = Profile(user=user, name=name, sta="사용자")
        profile.save()

        # Create Linux/LDAP account
        uid = LinuxInfo.objects.aggregate(Max('uid'))['uid__max'] or 69999
        uid += 1
        linux = LinuxInfo(user=user, username=username, uid=uid, group=lg, shell=shell)
        linux.save()

        ldapops.add_user(linux.username, linux.uid, lg.gid, shell, password)

        # Create home directory
        os.system(f'cp -r /etc/skel /dari-home/{username}')
        os.system(f'chmod 750 /dari-home/{username}')
        os.system(f'chown -R {uid}:{lg.gid} /dari-home/{username}')

        logger.warning(f"System initialized. Admin user {username} created.")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error during init: {e}")
        if 'user' in locals():
            user.delete()
        return api.create_response(request, {"error": str(e)}, status=500)

@api.post("/login", auth=None)
def login(request):
    data = json.loads(request.body)
    username = data.get('id')
    password = data.get('pw')
    agree = data.get('agree')
    if not agree:
        return api.create_response(request, None, status=400)

    # Try to get existing user
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        logger.warning("Portal user {} failed to login (reason: user does not exist).".format(username))
        return api.create_response(request, None, status=401)

    # Authenticate based on user type
    if username.startswith('guest'):
        # Guest users use Django auth
        auth_user = authenticate(request, username=username, password=password)
        if auth_user is None:
            user.logs.create(service="Portal", content="Login failed.")
            logger.warning("Portal user {} failed to login (reason: invalid password).".format(username))
            return api.create_response(request, None, status=401)
    else:
        # Regular users authenticate via LDAP, fall back to Django password
        if not hasattr(user, 'linux'):
            user.logs.create(service="Portal", content="Login failed.")
            logger.warning("Portal user {} failed to login (reason: no linux account).".format(username))
            return api.create_response(request, None, status=401)

        if not ldapops.authenticate_user(user.linux.username, password):
            # LDAP auth failed - try Django password (first login, LDAP not yet provisioned)
            if not user.check_password(password):
                user.logs.create(service="Portal", content="Login failed.")
                logger.warning("Portal user {} failed to login (reason: invalid password).".format(username))
                return api.create_response(request, None, status=401)

    if not user.is_active:
        logger.warning("Portal user {} failed to login (reason: not active)".format(username))
        user.logs.create(service="Portal", content="Login failed.")
        if hasattr(user, 'profile') and user.profile.date_expire is None and user.profile.date_removal is None:
            return api.create_response(request, {"error": "pending_approval"}, status=403)
        return api.create_response(request, {"error": "account_deactivated"}, status=403)

    # Check email verification (skip for guest users)
    if not username.startswith('guest'):
        from allauth.account.models import EmailAddress
        if not EmailAddress.objects.filter(user=user, verified=True).exists():
            logger.warning("Portal user {} failed to login (reason: email not verified)".format(username))
            return api.create_response(request, {"error": "email_not_verified"}, status=403)

    auth_login(request, user)

    # Provision LDAP account and home directory on first login
    if hasattr(user, 'linux') and not username.startswith('guest'):
        if not os.path.exists(f'/dari-home/{user.linux.username}'):
            ldapops.add_user(user.linux.username, user.linux.uid, user.linux.group.gid, user.linux.shell, password)
            os.system(f'cp -r /etc/skel /dari-home/{user.linux.username}')
            os.system(f'chmod 750 /dari-home/{user.linux.username}')
            os.system(f'chown -R {user.linux.uid}:{user.linux.group.gid} /dari-home/{user.linux.username}')
            logger.warning(f"Provisioned LDAP account and home directory for {username}")

    # Update expiry date on login (non-staff users expire 6 months after last login)
    if not user.is_staff and hasattr(user, 'profile'):
        user.profile.date_expire = (timezone.now() + timezone.timedelta(days=6*30)).date()
        user.profile.save(update_fields=['date_expire'])

    logger.warning("Portal user {} authentication successful.".format(username))
    user.logs.create(service="Portal", content="Login successful.")
    return {"success": True, "sessionid": request.session.session_key}

@api.get("/logout")
def logout(request):
    auth_logout(request)
    return {"success": True}

@api.post("/register", auth=None)
def register(request):
    """Register a new regular user with LDAP account"""
    from allauth.account.models import EmailAddress, EmailConfirmationHMAC

    data = json.loads(request.body)
    username = data.get('username', '')
    password = data.get('password', '')
    name = data.get('name', '')
    email = data.get('email', '')
    if not username or not password or not name or not email:
        return api.create_response(request, {"error": "Missing required fields"}, status=400)

    if username.startswith('guest'):
        return api.create_response(request, {"error": "Username cannot start with 'guest'"}, status=400)

    if not validate(username):
        return api.create_response(request, {"error": "Invalid username format"}, status=400)

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return api.create_response(request, {"error": "User already exists"}, status=409)

    # Check if Linux username already exists
    if LinuxInfo.objects.filter(username=username).exists():
        return api.create_response(request, {"error": "Linux username already exists"}, status=409)

    # Check if email already in use
    if User.objects.filter(email=email).exists():
        return api.create_response(request, {"error": "Email already in use"}, status=409)

    # Check allowed email domains
    try:
        allowed_domains = Default.objects.get(key="allowed_email_domains").value
        if allowed_domains:
            domains = [d.strip().lower() for d in allowed_domains.split(',') if d.strip()]
            email_domain = email.split('@')[-1].lower()
            if domains and email_domain not in domains:
                return api.create_response(request, {"error": "Email domain not allowed"}, status=400)
    except Default.DoesNotExist:
        pass

    try:
        # Create Django user
        is_first_user = User.objects.count() == 0
        user = User(username=username, email=email, is_active=is_first_user)
        user.save()

        # Create profile
        profile = Profile(user=user, name=name, sta="사용자")
        profile.save()

        # Create Linux account with LDAP entry
        default_gid = Default.objects.get(key="gid").value
        default_shell = Default.objects.get(key="shell").value

        uid = LinuxInfo.objects.aggregate(Max('uid'))['uid__max'] or 69999
        uid += 1
        lg = LinuxGroup.objects.get(name=default_gid)
        linux = LinuxInfo(user=user, username=username, uid=uid, group=lg, shell=default_shell)
        linux.save()

        # Store password in Django for now; LDAP + home dir created on first login
        user.set_password(password)
        user.save()

        # If this is the first user, make them admin and provision immediately
        if is_first_user:
            user.is_staff = True
            user.is_superuser = True
            user.save()
            ldapops.add_user(linux.username, linux.uid, lg.gid, default_shell, password)
            os.system(f'cp -r /etc/skel /dari-home/{username}')
            os.system(f'chmod 750 /dari-home/{username}')
            os.system(f'chown -R {uid}:{lg.gid} /dari-home/{username}')

        # Email verification via allauth
        email_address = EmailAddress.objects.create(
            user=user, email=email, primary=True,
            verified=is_first_user  # Auto-verify first user (admin)
        )
        if not is_first_user:
            logger.warning("Sending an email verification link...")
            confirmation = EmailConfirmationHMAC(email_address)
            lang = request.COOKIES.get('lang', 'ko')
            from dariauth.tasks import send_verification_email_task
            send_verification_email_task.delay(email, confirmation.key, lang)

        logger.warning(f"New user {username} registered successfully.")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error registering user {username}: {e}")
        # Clean up on failure
        if 'user' in locals():
            user.delete()
        return api.create_response(request, {"error": str(e)}, status=500)

@api.get("/verify-email", auth=None)
def verify_email(request, key: str):
    """Verify email address using allauth HMAC confirmation"""
    from allauth.account.models import EmailConfirmationHMAC
    confirmation = EmailConfirmationHMAC.from_key(key)
    if not confirmation:
        return api.create_response(request, {"error": "Invalid or expired key"}, status=400)
    confirmation.confirm(request)

    # Notify admins that a new user needs approval
    user = confirmation.email_address.user
    if not user.is_staff:
        lang = request.COOKIES.get('lang', 'ko')
        from dariauth.tasks import send_admin_approval_email_task
        send_admin_approval_email_task.delay(
            user.username,
            user.profile.name if hasattr(user, 'profile') else user.username,
            user.email,
            lang
        )

    return {"success": True}

@api.post("/server")
def server(request, domainname: str, ip: str, port: int = None, allowed_groups: str = '', server_type: str = 'compute', pk: int = None):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)

    if server_type == 'storage':
        port = None

    if pk:
        try:
            srv = Server.objects.get(pk=pk)
            srv.domainname = domainname
            srv.ip = ip
            srv.port = port
            srv.server_type = server_type
            srv.save()
        except Server.DoesNotExist:
            return api.create_response(request, {"error": "Server not found"}, status=404)
    else:
        srv = Server.objects.create(domainname=domainname, ip=ip, port=port, server_type=server_type)
    add_ip(ip)

    if allowed_groups:
        group_names = [g.strip() for g in allowed_groups.split(',') if g.strip()]
        groups = LinuxGroup.objects.filter(name__in=group_names)
        srv.allowed_groups.set(groups)
    else:
        srv.allowed_groups.clear()

    ldapops.regenerate_acls()
    return {"success": True}

@api.delete("/server")
def server_delete(request, pk: int):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)

    server = Server.objects.get(pk=pk)
    delete_ip(server.ip)
    server.delete()

    ldapops.regenerate_acls()
    return {"success": True}

@api.post("/guest")
def guest(request, username: str, pw: str, name: str, institute: str, date_of_birth: str, reference: str, mobile: str, date_expire: str, otp: bool = None):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    
    if date_expire == '':
        date_expire = None
    if date_of_birth == '':
        date_of_birth = None

    if len(username) > 0:
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return api.create_response(request, None, status=404)
        if len(pw) > 0:
            user.set_password(pw)
            user.save()
        if not otp:
            if hasattr(user, 'vpn'):
                user.vpn.delete()
    else:
        user = User(
            username="guest" + str(User.objects.filter(username__startswith="guest").count() + 1),
        )
        user.set_password(pw)
        user.save()
    Profile.objects.update_or_create(user=user, name=name, sta="게스트", date_expire=date_expire)
    GuestInfo.objects.update_or_create(user=user, institute=institute, date_of_birth=date_of_birth, mobile=mobile, reference=reference)

    return {"success": True}

@api.get("/servers")
def servers(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    servers = Server.objects.prefetch_related('allowed_groups').all()
    rtn = []
    for server in servers:
        allowed = list(server.allowed_groups.values_list('name', flat=True))
        rtn.append({
            "pk": server.pk,
            "domainname": server.domainname,
            "ip": server.ip,
            "port": server.port,
            "visible": server.visible,
            "allowed_groups": allowed,
            "api_key": str(server.api_key),
            "server_type": server.server_type,
        })
    return rtn

@api.get("/servers/stats")
def servers_stats(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    servers = Server.objects.all()
    rtn = {}
    for server in servers:
        try:
            rtn[server.pk] = get_serverstat(server)
        except Exception:
            rtn[server.pk] = None
    return rtn

@api.get("/myservers", response=List[UserServerSchema])
def myservers(request):
    if not check_active_status(request.user):
        return api.create_response(request, None, status=403)
    from django.db.models import Q, Count
    # Get user's group names from LinuxGroup members field
    user = request.user
    username = user.linux.username if hasattr(user, 'linux') else ''
    user_groups = LinuxGroup.objects.filter(
        Q(members__exact=username) |
        Q(members__startswith=username + ',') |
        Q(members__endswith=',' + username) |
        Q(members__contains=',' + username + ',')
    )
    # Also include user's primary group
    if hasattr(user, 'linux') and user.linux.group:
        user_groups = user_groups | LinuxGroup.objects.filter(pk=user.linux.group.pk)
    servers = Server.objects.filter(visible=True).annotate(
        num_allowed=Count('allowed_groups')
    ).filter(
        Q(num_allowed=0) | Q(allowed_groups__in=user_groups)
    ).distinct()
    return servers

@api.get("/me", response=UserSchema)
def me(request):
    if not check_active_status(request.user):
        return api.create_response(request, None, status=403)
    return request.user
    
@api.get("/users", response=List[UserSchema])
def users(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    users = User.objects.filter(guestinfo__isnull=True, is_active=True).order_by('-is_staff', 'username', 'profile__name')
    return users

@api.get("/guests", response=List[UserSchema])
def guests(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    users = User.objects.filter(guestinfo__isnull=False, is_active=True).order_by('username')
    return users

@api.get("/deactivated", response=List[UserSchema])
def deactivated(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    users = User.objects.filter(is_active=False).order_by('username')
    return users

@api.get("/groupadmins", response=List[GroupAdminSchema])
def groupadmins(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    groupadmins = User.objects.filter(profile__is_groupadmin=True)
    rtn = []
    for groupadmin in groupadmins:
        group_names = groupadmin.groupadmins.values_list('group__name', flat=True)
        rtn.append({
            "linux_username": groupadmin.linux.username,
            "group_names": group_names
        })
    return rtn

@api.post("/groupadmin")
def groupadmin(request, linux_username: str, group_names: str):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    user = User.objects.get(linux__username=linux_username)
    user.groupadmins.all().delete()
    is_groupadmin = False
    if group_names != '':
        for group_name in group_names.split(','):
            group = LinuxGroup.objects.get(name=group_name)
            user.groupadmins.create(group=group)
            is_groupadmin = True
    user.profile.is_groupadmin = is_groupadmin
    user.profile.save()
    return {"success": True}

@api.delete("/groupadmin")
def groupadmin(request, linux_username: str):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    user = User.objects.get(linux__username=linux_username)
    user.groupadmins.all().delete()
    user.profile.is_groupadmin = False
    user.profile.save()
    return {"success": True}

@api.get("/groups", response=List[LinuxGroupSchema])
def groups(request):
    if check_admin_status(request.user):
        groups = LinuxGroup.objects.all().order_by('gid')
    else:
        if check_groupadmin_status(request.user):
            group_ids = request.user.groupadmins.values_list('group_id', flat=True)
            groups = LinuxGroup.objects.filter(id__in=group_ids)
        else:
            return api.create_response(request, None, status=403)        
    return groups

@api.get("/logs")
def logs(request, all: bool = False, page: int = 1, per_page: int = 20):
    if all and check_admin_status(request.user):
        qs = Log.objects.select_related('user', 'user__profile').all().order_by("-created_at")
    else:
        qs = request.user.logs.select_related('user', 'user__profile').all().order_by("-created_at")
    total = qs.count()
    offset = (page - 1) * per_page
    items = qs[offset:offset + per_page]
    return {
        "items": [
            {"username": log.user.username, "name": log.user.profile.name if hasattr(log.user, 'profile') else "", "service": log.service, "content": log.content, "created_at": str(log.created_at)}
            for log in items
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }

@api.post("/group")
def group(request, name: str, gid: int, members: str):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    LinuxGroup.objects.create(name=name, gid=gid, members=members)
    ldapops.add_or_modify_group(name, gid, members.split(','))
    ldapops.regenerate_acls()
    return {"success": True}

@api.put("/group")
def group(request, pk: int, name: str, gid: int, members: str):
    if not check_admin_status(request.user):
        if check_groupadmin_status(request.user):
            if not request.user.groupadmins.filter(group_id=pk).exists():
                return api.create_response(request, None, status=403)
        else:
            return api.create_response(request, None, status=403)
    lg = LinuxGroup.objects.get(pk=pk)
    ldapops.delete_group(lg.name)
    if check_admin_status(request.user):
        lg.name = name
        lg.gid = gid
    lg.members = members
    lg.save()
    ldapops.add_or_modify_group(lg.name, lg.gid, members.split(','))
    ldapops.regenerate_acls()
    return {"success": True}

@api.delete("/group")
def group(request, pk: int):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    group = LinuxGroup.objects.get(pk=pk)
    ldapops.delete_group(group.name)
    group.delete()
    ldapops.regenerate_acls()
    return {"success": True}

@api.patch("/user")
def user(request, username: str, linuxid: str = None, linuxuid: int = None, linuxgroup: str = None, email: str = None, staff: bool = None, otp: bool = None, date_expire: str = None,
         pw: str = None, name: str = None, institute: str = None, date_of_birth: str = None, reference: str = None, mobile: str = None,
         is_active: bool = None):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    user = User.objects.get(username=username)
    if email is not None:
        user.email = email
    if hasattr(user, 'linux'):
        if linuxid is not None or linuxuid is not None or linuxgroup is not None:
            old_linuxid = user.linux.username
            if linuxid is not None:
                user.linux.username = linuxid
            if linuxuid is not None:
                user.linux.uid = linuxuid
            if linuxgroup is not None:
                user.linux.group = LinuxGroup.objects.get(name=linuxgroup)
            user.linux.save()
            ldapops.delete_user(old_linuxid)
            ldapops.add_user(user.linux.username, user.linux.uid, user.linux.group.gid)
        # Allow admin to reset password for regular users
        if pw is not None and not hasattr(user, 'guestinfo'):
            ldapops.set_password(user.linux.username, pw)
            user.logs.create(service="Portal", content="Password reset by admin.") 
    if staff is not None:
        if user.is_superuser and staff == False:
            return api.create_response(request, None, status=400)
        user.is_staff = staff
    if otp is not None:
        if otp:
            if not hasattr(user, 'vpn'):
                vpn = VPNInfo(user=user) # This assume QR code is generated before this
                vpn.save()
        else:
            if hasattr(user, 'vpn'):
                user.vpn.delete()
    if date_expire is not None:
        user.profile.date_expire = date_expire
    if hasattr(user, 'guestinfo'):
        if pw is not None:
            user.set_password(pw)
        if name is not None:
            user.profile.name = name
        if institute is not None:
            user.guestinfo.institute = institute
        if date_of_birth is not None:
            user.guestinfo.date_of_birth = date_of_birth
        if reference is not None:
            user.guestinfo.reference = reference
        if mobile is not None:
            user.guestinfo.mobile = mobile
        user.guestinfo.save()
    if is_active is not None:
        user.is_active = is_active
        if is_active:
            user.profile.date_expire = None
            user.profile.date_removal = None
        else:
            user.profile.date_expire = timezone.now()
            user.profile.date_removal = timezone.now() + timezone.timedelta(days=6*30)
    user.save()
    return {"success": True}

@api.get("/defaults")
def defaults(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    defaults = Default.objects.all()
    rtn = {}
    for default in defaults:
        rtn[default.key] = default.value
    return rtn

@api.post("/defaults")
def defaults(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    data = json.loads(request.body)
    sitename = data.get('sitename', '')
    logo = data.get('logo', '')
    gid = data.get('gid', '')
    shell = data.get('shell', '')
    allowed_email_domains = data.get('allowed_email_domains', '')

    if sitename == '' or gid == '' or shell == '':
        return api.create_response(request, None, status=400)

    if Default.objects.filter(key="logo").exists():
        if logo != '':
            Default.objects.get(key="logo").update(value=logo)
    else:
        Default.objects.create(key="logo", value=logo)

    Default.objects.update_or_create(key="sitename", defaults={'value': sitename})
    Default.objects.update_or_create(key="gid", defaults={'value': gid})
    Default.objects.update_or_create(key="shell", defaults={'value': shell})
    Default.objects.update_or_create(key="allowed_email_domains", defaults={'value': allowed_email_domains})

    return {"success": True}

@api.post("/transfer")
def transfer(request, username_from: str, username_to: str):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    try:
        user_from = User.objects.get(username=username_from)
        user_to = User.objects.get(username=username_to)
    except ObjectDoesNotExist:
        return api.create_response(request, None, status=404)

    if hasattr(user_from, 'vpn'):
        if hasattr(user_to, 'vpn'):
            os.system(f'rm -f /etc/qr/{user_to.username}')
            user_to.vpn.delete()
        vi = user_from.vpn
        vi.user = user_to
        vi.save()
        os.system(f'mv /etc/qr/{user_from.username} /etc/qr/{user_to.username}')
    
    if hasattr(user_from, 'linux'):
        if hasattr(user_to, 'linux'):
            backupdir = f'/dari-home/{user_from.linux.username}/{user_to.linux.username}-backup'
            os.system(f'mkdir -p {backupdir}')
            os.system(f'cp -r /dari-home/{user_to.linux.username}/* {backupdir}/')
            os.system(f'chown -R {user_from.linux.username}:{user_from.linux.group.name} {backupdir}')
            os.system(f'rm -fr /dari-home/{user_to.linux.username}')
            user_to.linux.delete()
        li = user_from.linux
        li.user = user_to
        li.save()
    
@api.post("/emailsend")
def emailsend(request, subject: str, body: str):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    try:
        send_email(subject, body)
    except:
        return api.create_response(request, None, status=500)
    return {"success": True}

@api.post("/password")
def change_password(request, old_password: str, new_password: str):
    """Change user's LDAP password"""
    if not check_active_status(request.user):
        return api.create_response(request, None, status=403)

    user = request.user
    if not hasattr(user, 'linux'):
        return api.create_response(request, {"error": "No Linux account"}, status=400)

    # Check if user is locked out from a previous failed attempt
    if user.profile.password_fail_at:
        elapsed = (timezone.now() - user.profile.password_fail_at).total_seconds()
        if elapsed < 30:
            remaining = int(30 - elapsed)
            return api.create_response(request, {"error": f"Too many attempts. Try again in {remaining} seconds."}, status=429)

    # Verify old password
    if not ldapops.authenticate_user(user.linux.username, old_password):
        logger.warning(f"User {user.username} failed to change password (invalid old password)")
        user.profile.password_fail_at = timezone.now()
        user.profile.save(update_fields=['password_fail_at'])
        from dariauth.tasks import clear_password_fail
        clear_password_fail.apply_async(args=[user.username], countdown=30)
        return api.create_response(request, {"error": "Invalid old password"}, status=401)

    try:
        # Set new password in LDAP
        ldapops.set_password(user.linux.username, new_password)
        user.profile.password_fail_at = None
        user.profile.save(update_fields=['password_fail_at'])
        logger.warning(f"User {user.username} changed password successfully")
        user.logs.create(service="Portal", content="Password changed.")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error changing password for {user.username}: {e}")
        return api.create_response(request, {"error": str(e)}, status=500)

@api.post("/qr")
def qr(request):
    if not check_active_status(request.user):
        return api.create_response(request, None, status=403)
    user = request.user
    if hasattr(user, 'vpn'):
        return api.create_response(request, None, status=409)
    secpath = f'/etc/qr/{user.username}'
    os.system(f'rm -f {secpath} && google-authenticator -t -d -r3 -R30 -e0 -q -f -C -W -l test -s {secpath}')
    qrsec = open(secpath).readline().rstrip()
    qrstr = "otpauth://totp/{}%40DARI?secret={}&issuer=DARI".format(user.username, qrsec)
    qrimg = base64.b64encode(subprocess.Popen(['qrencode', '-d150' , '-o-', qrstr], stdout=subprocess.PIPE).communicate()[0]).decode('ascii')

    vpn = VPNInfo(user=user)
    vpn.save()

    return {"success": True, "qr": "data:image/png;base64," + qrimg}

@api.get("/vpn/profile", auth=None)
def vpn_profile(request):
    """Serve OpenVPN profile for import via URL"""
    ovpn_path = '/etc/ovpn/client.ovpn'

    if not os.path.exists(ovpn_path):
        return api.create_response(request, {"error": "VPN profile not available"}, status=404)

    try:
        with open(ovpn_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/x-openvpn-profile')
            response['Content-Disposition'] = 'attachment; filename="client.ovpn"'
            return response
    except Exception as e:
        logger.error(f"Error serving VPN profile: {e}")
        return api.create_response(request, {"error": str(e)}, status=500)

# --- NFS Share Management ---

@api.get("/nfsshares")
def nfsshares(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    shares = NFSShare.objects.prefetch_related('allowed_groups', 'allowed_servers').all()
    rtn = []
    for share in shares:
        allowed = list(share.allowed_groups.values_list('name', flat=True))
        allowed_srvs = list(share.allowed_servers.values_list('domainname', flat=True))
        rtn.append({
            "pk": share.pk,
            "name": share.name,
            "server_ip": share.server_ip,
            "export_path": share.export_path,
            "mount_point": share.mount_point,
            "allowed_groups": allowed,
            "allowed_servers": allowed_srvs,
        })
    return rtn

@api.post("/nfsshare")
def nfsshare(request, name: str, server_ip: str, export_path: str, mount_point: str, allowed_groups: str = '', allowed_servers: str = ''):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)

    share, _ = NFSShare.objects.update_or_create(name=name, defaults={
        'server_ip': server_ip,
        'export_path': export_path,
        'mount_point': mount_point,
    })

    if allowed_groups:
        group_names = [g.strip() for g in allowed_groups.split(',') if g.strip()]
        groups = LinuxGroup.objects.filter(name__in=group_names)
        share.allowed_groups.set(groups)
    else:
        share.allowed_groups.clear()

    if allowed_servers:
        server_names = [s.strip() for s in allowed_servers.split(',') if s.strip()]
        servers = Server.objects.filter(domainname__in=server_names)
        share.allowed_servers.set(servers)
    else:
        share.allowed_servers.clear()

    ldapops.regenerate_acls()
    return {"success": True}

@api.delete("/nfsshare")
def nfsshare_delete(request, pk: int):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    NFSShare.objects.get(pk=pk).delete()
    ldapops.regenerate_acls()
    return {"success": True}

# --- Compute Node Config ---

@api.get("/node/config", auth=None)
def node_config(request, key: str):
    """Compute node fetches its config using its API key."""
    try:
        server = Server.objects.prefetch_related('allowed_groups').get(api_key=key)
    except (Server.DoesNotExist, ValueError):
        return api.create_response(request, {"error": "Invalid API key"}, status=403)

    from django.db.models import Q, Count

    # Determine allowed groups for this server
    server_groups = list(server.allowed_groups.all())
    has_restrictions = len(server_groups) > 0

    if has_restrictions:
        group_names = [g.name for g in server_groups]
        # Resolve all usernames in these groups (primary + secondary)
        allowed_users = set()
        for g in server_groups:
            # Users with this as primary group
            for li in LinuxInfo.objects.filter(group=g):
                allowed_users.add(li.username)
            # Users listed in group members (secondary)
            if g.members:
                for m in g.members.split(','):
                    m = m.strip()
                    if m:
                        allowed_users.add(m)
    else:
        group_names = list(LinuxGroup.objects.values_list('name', flat=True))
        allowed_users = set(LinuxInfo.objects.values_list('username', flat=True))

    # Get NFS shares accessible to this server's groups
    if has_restrictions:
        nfs_shares = NFSShare.objects.filter(
            Q(allowed_groups__in=server_groups) | Q(allowed_groups__isnull=True)
        ).distinct()
        # Also include shares with no group restrictions
        nfs_shares = nfs_shares | NFSShare.objects.annotate(
            num_groups=Count('allowed_groups')
        ).filter(num_groups=0)
        nfs_shares = nfs_shares.distinct()
    else:
        nfs_shares = NFSShare.objects.all()

    # Resolve dari-home server IP
    home_server_ip = ""
    try:
        home_server_pk = Default.objects.get(key="dari_home_server").value
        home_server = Server.objects.get(pk=int(home_server_pk))
        home_server_ip = home_server.ip
    except (Default.DoesNotExist, Server.DoesNotExist, ValueError):
        pass

    return {
        "nfs_shares": [
            {"server_ip": s.server_ip, "export_path": s.export_path, "mount_point": s.mount_point}
            for s in nfs_shares
        ],
        "allowed_users": sorted(allowed_users),
        "allowed_groups": sorted(group_names),
        "ldap_base_dn": "dc=" + os.environ.get('LDAP_DOMAIN', 'dari'),
        "home_server_ip": home_server_ip,
    }

# --- Storage Node Config ---

@api.get("/storage/config", auth=None)
def storage_config(request, key: str):
    """Storage node fetches its export config using its API key."""
    try:
        server = Server.objects.get(api_key=key, server_type='storage')
    except (Server.DoesNotExist, ValueError):
        return api.create_response(request, {"error": "Invalid API key"}, status=403)

    from django.db.models import Count

    # Find NFS shares hosted on this storage server (matched by IP)
    shares = NFSShare.objects.prefetch_related('allowed_servers').filter(server_ip=server.ip)

    # All compute server IPs (for unrestricted shares and dari-home)
    all_compute_ips = list(Server.objects.filter(server_type='compute').values_list('ip', flat=True))

    exports = []
    for share in shares:
        allowed_srvs = list(share.allowed_servers.all())
        if allowed_srvs:
            allowed_ips = sorted(set(s.ip for s in allowed_srvs))
        else:
            allowed_ips = sorted(set(all_compute_ips))
        exports.append({
            "path": share.export_path,
            "allowed_ips": allowed_ips,
        })

    # Check if this server exports dari-home
    dari_home = False
    dari_home_ips = []
    try:
        home_server_pk = Default.objects.get(key="dari_home_server").value
        if int(home_server_pk) == server.pk:
            dari_home = True
            dari_home_ips = sorted(set(all_compute_ips))
    except (Default.DoesNotExist, ValueError):
        pass

    return {
        "exports": exports,
        "dari_home": dari_home,
        "dari_home_ips": dari_home_ips,
    }

# --- Dari Home Server Setting ---

@api.post("/dari-home-server")
def set_dari_home_server(request, server_pk: int):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    try:
        srv = Server.objects.get(pk=server_pk, server_type='storage')
    except Server.DoesNotExist:
        return api.create_response(request, {"error": "Storage server not found"}, status=404)
    Default.objects.update_or_create(key="dari_home_server", defaults={'value': str(server_pk)})
    return {"success": True}

@api.get("/dari-home-server")
def get_dari_home_server(request):
    if not check_admin_status(request.user):
        return api.create_response(request, None, status=403)
    try:
        pk = Default.objects.get(key="dari_home_server").value
        srv = Server.objects.get(pk=int(pk))
        return {"server_pk": srv.pk, "domainname": srv.domainname}
    except (Default.DoesNotExist, Server.DoesNotExist, ValueError):
        return {"server_pk": None, "domainname": None}

# --- Password Reset ---

@api.post("/forgot-password", auth=None)
def forgot_password(request, username: str, email: str):
    """Send password reset email if user exists."""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    try:
        user = User.objects.get(username=username)
        if (user.email.lower() == email.lower()
            and user.is_active
            and hasattr(user, 'linux')
            and not username.startswith('guest')):
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            lang = request.COOKIES.get('lang', 'ko')
            from dariauth.tasks import send_password_reset_email_task
            send_password_reset_email_task.delay(user.email, uidb64, token, lang)
    except User.DoesNotExist:
        pass

    return {"success": True}

@api.post("/reset-password", auth=None)
def reset_password(request, uid: str, token: str, new_password: str):
    """Reset password using token from email."""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode

    try:
        user_pk = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_pk)
    except (User.DoesNotExist, ValueError, TypeError):
        return api.create_response(request, {"error": "Invalid link"}, status=400)

    if not default_token_generator.check_token(user, token):
        return api.create_response(request, {"error": "Invalid or expired link"}, status=400)

    if not hasattr(user, 'linux'):
        return api.create_response(request, {"error": "No Linux account"}, status=400)

    try:
        ldapops.set_password(user.linux.username, new_password)
        user.logs.create(service="Portal", content="Password reset via email.")
        logger.warning(f"User {user.username} reset password via email.")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error resetting password for {user.username}: {e}")
        return api.create_response(request, {"error": str(e)}, status=500)