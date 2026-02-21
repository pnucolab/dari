from celery import shared_task
from django.utils import timezone

from .models import User
from backend.utils import ldapops

import os

@shared_task
def remove_users():
    for u in User.objects.filter(is_active=False, profile__date_removal__lt=timezone.now()):
        print(f"Removing user {u.profile.name}...")
        if u.vpn:
            print(f"Removing VPN QR code of {u.username}...")
            os.system(f"rm -f /etc/qr/{u.username}")
        if u.linux:
            print(f"Removing {u.linux.username} from LDAP...")
            ldapops.delete_user(u.linux.username)
            print(f"Archiving /dari-home/{u.linux.username} to /mnt/archive/{u.linux.username}.tar.gz...")
            os.system(f"tar -czf /mnt/archive/{u.linux.username}.tar.gz /dari-home/{u.linux.username}")
            print(f"Removing /dari-home/{u.linux.username}...")
            os.system(f"rm -rf /dari-home/{u.linux.username}")
        u.delete()
        print(f"User {u.profile.name} removed.")

@shared_task
def deactivate_users():
    for u in User.objects.filter(is_active=False, profile__date_expire__lt=timezone.now()):
        print(f"Deactivating user {u.profile.name}...")
        u.profile.date_removal = timezone.now() + timezone.timedelta(days=6*30)
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