from django.contrib.auth.models import User
from dariauth.models import LinuxGroup, Default, Server

import os
import ssl
import requests
import ldap
import json
from urllib import parse, request
import ldap.modlist as modlist

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import ssl

from django.utils import timezone
from .logging import logger

ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT')

# PNU-specific authentication removed - now using LDAP authentication
# def get_userinfo(pnu_id, pnu_pw):
#     data = parse.urlencode({
#         "resultType": 'json',
#         "serviceKey": os.environ.get('SERVICE_KEY'),
#         "apiKey": os.environ.get('API_KEY'),
#         "id": pnu_id,
#         "pswd": pnu_pw,
#         "agreeYn": "Y"
#     }).encode("ascii")
#     o = request.urlopen(os.environ.get('AUTH_URL'), data, context=ctx)
#     rtn = json.loads(o.read().decode("utf-8"))["result"]
#
#     if rtn['code'] != "0000":
#         raise RuntimeError(rtn['message'])
#
#     return rtn['data'][0]

class LDAPOps:
    def __init__(self, uri, id, pw):
        self.uri = uri
        self.id = id
        self.pw = pw
        self.__conn = None
        def ensure_ou_exists(ou_name):
            try:
                self.conn.search_s(f"ou={ou_name},dc=dari", ldap.SCOPE_BASE)
            except ldap.NO_SUCH_OBJECT:
                print(f"Cannot find ou={ou_name},dc=dari. Creating one...")
                attr = {
                    'objectClass': [b'organizationalUnit', b'top']
                }
                ldif = modlist.addModlist(attr)
                self.conn.add_s(f"ou={ou_name},dc=dari", ldif)
        ensure_ou_exists("users")
        ensure_ou_exists("groups")
    
    @property
    def conn(self):
        if self.__conn:
            try:
                self.__conn.unbind_s()
            except:
                pass
        self.__conn = ldap.initialize(self.uri)
        self.__conn.bind(self.id, self.pw)
        return self.__conn

    def add_user(self, uid, uid_number, gid_number, loginshell="/bin/zsh", password=None):
        attr = {}
        attr['objectClass'] = [b'posixAccount', b'inetOrgPerson', b'top']
        attr['sn'] = [uid.encode("utf-8")] # required for inetOrgPerson
        attr['cn'] = [uid.encode("utf-8")]
        attr['uid'] = [uid.encode("utf-8")]
        attr['uidNumber'] = [str(uid_number).encode("utf-8")]
        attr['gidNumber'] = [str(gid_number).encode("utf-8")]
        attr['loginShell'] = [loginshell.encode("utf-8")]
        attr['homeDirectory'] = [('/home/' + uid).encode("utf-8")]
        if password:
            # Store password as SSHA hash
            import hashlib
            import os as os_mod
            salt = os_mod.urandom(4)
            h = hashlib.sha1(password.encode('utf-8'))
            h.update(salt)
            import base64
            passwd_hash = "{SSHA}" + base64.b64encode(h.digest() + salt).decode('ascii')
            attr['userPassword'] = [passwd_hash.encode("utf-8")]
        ldif = modlist.addModlist(attr)
        try:
            self.conn.delete_s("cn=%s,ou=users,dc=dari"%uid)
        except ldap.NO_SUCH_OBJECT:
            pass
        self.conn.add_s("cn=%s,ou=users,dc=dari"%uid, ldif)

    def modify_attr(self, cn, key, val):
        attr = [(
            ldap.MOD_REPLACE,
            key,
            str(val).encode("utf-8")
        )]
        self.conn.modify_ext_s(cn, attr)

    def modify_user(self, uid, key, val):
        self.modify_attr("cn=%s,ou=users,dc=dari"%uid, key, val)

    def set_password(self, uid, password):
        """Set LDAP password for a user"""
        import hashlib
        import os as os_mod
        import base64
        salt = os_mod.urandom(4)
        h = hashlib.sha1(password.encode('utf-8'))
        h.update(salt)
        passwd_hash = "{SSHA}" + base64.b64encode(h.digest() + salt).decode('ascii')
        attr = [(
            ldap.MOD_REPLACE,
            'userPassword',
            passwd_hash.encode("utf-8")
        )]
        self.conn.modify_ext_s("cn=%s,ou=users,dc=dari"%uid, attr)

    def authenticate_user(self, uid, password):
        """Authenticate a user against LDAP"""
        try:
            conn = ldap.initialize(self.uri)
            conn.bind("cn=%s,ou=users,dc=dari"%uid, password)
            conn.unbind_s()
            return True
        except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
            return False
        except Exception as e:
            print(f"LDAP auth error: {e}")
            return False

    def add_or_modify_group(self, cn, gid_number, member_uid=[]):
        attr = {}
        attr['objectClass'] = [b'posixGroup', b'top']
        attr['gidNumber'] = [str(gid_number).encode("utf-8")]
        if len(member_uid) > 0:
            attr['memberUid'] = [uid.encode("utf-8") for uid in member_uid]
        ldif = modlist.addModlist(attr)
        try:
            self.conn.delete_s("cn=%s,ou=groups,dc=dari"%cn)
        except:
            pass
        self.conn.add_s("cn=%s,ou=groups,dc=dari"%cn, ldif)

    def get_children_or_create_ou(self, groupname):
        try:
            grp = self.conn.search_s("ou=%s,dc=dari"%groupname, ldap.SCOPE_ONELEVEL)
        except:
            attr = {}
            attr['objectClass'] = [b'organizationalUnit', b'top']
            ldif = modlist.addModlist(attr)
            self.conn.add_s("ou=%s,dc=dari"%groupname, ldif)
            grp = []
        return grp

    def delete_user(self, uid):
        try:
            self.conn.delete_s("cn=%s,ou=users,dc=dari"%uid)
        except ldap.NO_SUCH_OBJECT:
            pass

    def delete_group(self, cn):
        try:
            self.conn.delete_s("cn=%s,ou=groups,dc=dari"%cn)
        except ldap.NO_SUCH_OBJECT:
            pass

    def delete_entries(self, entries):
        for e in entries:
            self.conn.delete_s(e[0])

    def regenerate_acls(self):
        """Regenerate OpenLDAP ACLs based on server allowed_groups.
        Uses peername.ip and filter= to restrict per-node visibility."""
        try:
            servers = Server.objects.prefetch_related('allowed_groups').all()
            acls = []

            # Rule 0: admin always gets write access, others break to next rule
            acls.append(b'{0}to * by dn="cn=admin,dc=dari" write by * break')

            # Rule 1: password access
            acls.append(b'{1}to attrs=userPassword by self write by anonymous auth by * none')

            idx = 2
            restricted_ips = set()
            unrestricted_ips = set()

            for srv in servers:
                groups = list(srv.allowed_groups.all())
                if not groups:
                    unrestricted_ips.add(srv.ip)
                    continue

                restricted_ips.add(srv.ip)
                # Resolve all member usernames
                usernames = set()
                group_names = []
                for g in groups:
                    group_names.append(g.name)
                    # Primary group members
                    for li in LinuxInfo.objects.filter(group=g):
                        usernames.add(li.username)
                    # Secondary group members
                    if g.members:
                        for m in g.members.split(','):
                            m = m.strip()
                            if m:
                                usernames.add(m)

                if usernames:
                    uid_filter = '(|' + ''.join(f'(uid={u})' for u in sorted(usernames)) + ')'
                    by_clause = f'by peername.ip={srv.ip} read by * break'
                    acls.append(f'{{{idx}}}to dn.subtree="ou=users,dc=dari" filter={uid_filter} {by_clause}'.encode())
                    idx += 1

                if group_names:
                    cn_filter = '(|' + ''.join(f'(cn={g})' for g in sorted(group_names)) + ')'
                    by_clause = f'by peername.ip={srv.ip} read by * break'
                    acls.append(f'{{{idx}}}to dn.subtree="ou=groups,dc=dari" filter={cn_filter} {by_clause}'.encode())
                    idx += 1

            # Unrestricted nodes: full read access to users and groups
            if unrestricted_ips:
                by_parts = ' '.join(f'by peername.ip={ip} read' for ip in sorted(unrestricted_ips))
                acls.append(f'{{{idx}}}to dn.subtree="ou=users,dc=dari" {by_parts} by * break'.encode())
                idx += 1
                acls.append(f'{{{idx}}}to dn.subtree="ou=groups,dc=dari" {by_parts} by * break'.encode())
                idx += 1

            # Default deny
            acls.append(f'{{{idx}}}to * by * none'.encode())

            # Apply to cn=config
            config_conn = ldap.initialize(self.uri)
            config_conn.bind("cn=admin,cn=config", self.pw)

            # Find the MDB database DN
            results = config_conn.search_s("cn=config", ldap.SCOPE_SUBTREE, "(olcDatabase={1}mdb)")
            if results:
                db_dn = results[0][0]
                mod = [(ldap.MOD_REPLACE, 'olcAccess', acls)]
                config_conn.modify_s(db_dn, mod)
                logger.warning(f"LDAP ACLs regenerated: {len(acls)} rules for {len(restricted_ips)} restricted + {len(unrestricted_ips)} unrestricted nodes")
            else:
                logger.error("Could not find LDAP MDB database in cn=config")

            config_conn.unbind_s()
        except Exception as e:
            logger.error(f"Error regenerating LDAP ACLs: {e}")

    def update_ldap(self):
        all_users = self.get_children_or_create_ou("users")
        all_groups = self.get_children_or_create_ou("groups")
        try:
            shell = Default.objects.get(key="shell").value
        except ObjectDoesNotExist:
            shell = "/bin/zsh"
        self.delete_entries(all_users)
        for u in User.objects.exclude(linux__isnull=True):
            self.add_user(u.linux.username, u.linux.uid, u.linux.group.gid, shell)

        self.delete_entries(all_groups)
        for g in LinuxGroup.objects.all():
            members = g.members.split(',')
            self.add_or_modify_group(g.name, g.gid, members)

ldapops = LDAPOps("ldap://ldap", settings.LDAP_ID, settings.LDAP_PW)

def check_active_status(user):
    if user.is_active:
        return True
    return False

def check_admin_status(user):
    if user.is_active and user.is_staff:
        return True
    return False

def check_groupadmin_status(user):
    if user.is_active and user.profile.is_groupadmin:
        return True
    return False

def validate(s):
    if len(s) == 0 or len(s) > 31:
        return False
    elif not s[0].isalpha():
        return False
    elif not s.isalnum():
        return False
    elif not s.islower():
        return False
    return True

def get_serverstat(server):
    ip = server.ip
    rtn = requests.get("http://%s:8438/stats"%ip)
    if rtn.status_code != 200:
        raise RuntimeError
    
    return json.loads(rtn.text)

def send_email(subject, body):
    """Send email to all active users with email addresses using Django email settings."""
    from django.core.mail import send_mass_mail

    prefix = settings.EMAIL_SUBJECT_PREFIX
    full_subject = f"{prefix} {subject}" if prefix else subject

    recv_emails = [u.email for u in User.objects.exclude(email__isnull=True).exclude(email__exact='').filter(is_active=True)]
    messages = [(full_subject, body, settings.DEFAULT_FROM_EMAIL, [email]) for email in recv_emails]
    send_mass_mail(messages, fail_silently=False)

def send_verification_email(to_email, key, lang='ko'):
    """Send email verification link to a user."""
    logger.warning("Test")
    from django.core.mail import send_mail

    domain = os.environ.get('SITE_DOMAIN', 'localhost:8080')
    scheme = 'https' if not settings.DEBUG else 'http'
    verify_url = f"{scheme}://{domain}/verify-email?key={key}"

    prefix = settings.EMAIL_SUBJECT_PREFIX

    if lang == 'ko':
        subject_text = "이메일 인증"
        body = f"아래 링크를 클릭하여 이메일 주소를 인증해 주세요:\n\n{verify_url}"
    else:
        subject_text = "Email Verification"
        body = f"Please click the link below to verify your email address:\n\n{verify_url}"

    subject = f"{prefix} {subject_text}" if prefix else subject_text
    logger.warning(subject)
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])

def send_password_reset_email(to_email, uidb64, token, lang='ko'):
    """Send password reset link to a user."""
    from django.core.mail import send_mail

    domain = os.environ.get('SITE_DOMAIN', 'localhost:8080')
    scheme = 'https' if not settings.DEBUG else 'http'
    reset_url = f"{scheme}://{domain}/reset-password?uid={uidb64}&token={token}"

    prefix = settings.EMAIL_SUBJECT_PREFIX

    if lang == 'ko':
        subject_text = "비밀번호 재설정"
        body = f"아래 링크를 클릭하여 비밀번호를 재설정해 주세요:\n\n{reset_url}\n\n이 요청을 하지 않았다면 이 이메일을 무시하세요."
    else:
        subject_text = "Password Reset"
        body = f"Please click the link below to reset your password:\n\n{reset_url}\n\nIf you did not request this, please ignore this email."

    subject = f"{prefix} {subject_text}" if prefix else subject_text
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])

def send_admin_approval_email(username, name, email, lang='ko'):
    """Send notification to all admin users that a new user has registered and needs approval."""
    from django.core.mail import send_mail

    domain = os.environ.get('SITE_DOMAIN', 'localhost:8080')
    scheme = 'https' if not settings.DEBUG else 'http'
    admin_url = f"{scheme}://{domain}/admin/users"

    prefix = settings.EMAIL_SUBJECT_PREFIX

    if lang == 'ko':
        subject_text = "새 사용자 승인 요청"
        body = (
            f"새로운 사용자가 가입했습니다. 승인이 필요합니다.\n\n"
            f"아이디: {username}\n"
            f"이름: {name}\n"
            f"이메일: {email}\n\n"
            f"사용자 관리 페이지에서 승인할 수 있습니다:\n{admin_url}"
        )
    else:
        subject_text = "New User Approval Required"
        body = (
            f"A new user has registered and requires approval.\n\n"
            f"Username: {username}\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"You can approve the user from the admin panel:\n{admin_url}"
        )

    subject = f"{prefix} {subject_text}" if prefix else subject_text

    admin_emails = [
        u.email for u in User.objects.filter(is_staff=True, is_active=True)
        .exclude(email__isnull=True).exclude(email__exact='')
    ]

    for admin_email in admin_emails:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [admin_email])

def add_ip(ip):
    import yaml
    import os
    config_file = "/etc/ip_addresses/conf.yml"

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        config = {}

    if 'ip_addresses' not in config:
        config['ip_addresses'] = []

    if ip not in config['ip_addresses']:
        config['ip_addresses'].insert(0, ip)
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)

def delete_ip(ip):
    import yaml
    config_file = "/etc/ip_addresses/conf.yml"

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return

    if 'ip_addresses' in config and ip in config['ip_addresses']:
        config['ip_addresses'].remove(ip)
        with open(config_file, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)