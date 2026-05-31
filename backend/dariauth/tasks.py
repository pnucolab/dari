from celery import shared_task
from django.utils import timezone

from .models import User
from backend.utils import ldapops

import os
import shutil
import subprocess

@shared_task
def remove_users():
    for u in User.objects.filter(is_active=False, profile__date_removal__lt=timezone.now()):
        print(f"Removing user {u.profile.name}...")
        if hasattr(u, 'vpn'):
            print(f"Removing VPN QR code of {u.username}...")
            qr = os.path.join('/etc/qr', u.username)
            if os.path.exists(qr):
                os.remove(qr)
        if hasattr(u, 'linux'):
            print(f"Removing {u.linux.username} from LDAP...")
            ldapops.delete_user(u.linux.username)
            home = os.path.join('/dari-home', u.linux.username)
            archive = os.path.join('/mnt/archive', f'{u.linux.username}.tar.gz')
            print(f"Archiving {home} to {archive}...")
            subprocess.run(['tar', '-czf', archive, home], check=False)
            print(f"Removing {home}...")
            shutil.rmtree(home, ignore_errors=True)
        u.delete()
        print(f"User {u.profile.name} removed.")

@shared_task
def deactivate_users():
    for u in User.objects.filter(is_active=True, is_staff=False, profile__date_expire__lt=timezone.now()):
        print(f"Deactivating user {u.profile.name}...")
        u.profile.date_removal = (timezone.now() + timezone.timedelta(days=6*30)).date()
        u.profile.save(update_fields=['date_removal'])
        u.is_active = False
        u.save()
        print(f"User {u.profile.name} deactivated.")

@shared_task
def update_users_sta():
    pass

@shared_task
def clear_password_fail(username):
    from .models import Profile
    Profile.objects.filter(user__username=username, password_fail_at__isnull=False).update(password_fail_at=None)

@shared_task
def send_verification_email_task(to_email, key, lang='ko'):
    from backend.utils import send_verification_email
    send_verification_email(to_email, key, lang)

@shared_task
def send_admin_approval_email_task(username, name, email, lang='ko'):
    from backend.utils import send_admin_approval_email
    send_admin_approval_email(username, name, email, lang)

@shared_task
def send_password_reset_email_task(to_email, uidb64, token, lang='ko'):
    from backend.utils import send_password_reset_email
    send_password_reset_email(to_email, uidb64, token, lang)