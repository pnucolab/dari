import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Default(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()

class GroupAdmin(models.Model):
    user = models.ForeignKey(User, related_name='groupadmins', on_delete=models.CASCADE)
    group = models.ForeignKey('LinuxGroup', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.profile.name} ({self.group.name})"

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    sta = models.CharField(max_length=255)
    date_expire = models.DateField(blank=True, null=True, default=None)
    date_removal = models.DateField(blank=True, null=True, default=None)
    is_groupadmin = models.BooleanField(default=False)
    password_fail_at = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name

class GuestInfo(models.Model):
    user = models.OneToOneField(User, related_name='guestinfo', on_delete=models.CASCADE, null=True)
    institute = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.profile.name} ({self.institute})"

class VPNInfo(models.Model):
    user = models.OneToOneField(User, related_name='vpn', on_delete=models.CASCADE, null=True)

class LinuxInfo(models.Model):
    user = models.OneToOneField(User, related_name='linux', on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey('LinuxGroup', on_delete=models.SET_NULL, null=True)
    uid = models.IntegerField()
    shell = models.CharField(max_length=255)

    def __str__(self):
        return self.username

class Log(models.Model):
    user = models.ForeignKey(User, related_name='logs', on_delete=models.CASCADE)
    service = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.created_at}] {self.content}"

class LinuxGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    gid = models.IntegerField()
    members = models.TextField(blank=True, null=False, default='')

    def __str__(self):
        return self.name

class Server(models.Model):
    SERVER_TYPES = [('compute', 'Compute'), ('storage', 'Storage')]
    domainname = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(null=True)
    visible = models.BooleanField(default=True)
    allowed_groups = models.ManyToManyField('LinuxGroup', related_name='allowed_servers', blank=True)
    api_key = models.UUIDField(default=uuid.uuid4, unique=True)
    server_type = models.CharField(max_length=10, choices=SERVER_TYPES, default='compute')

    def __str__(self):
        return self.domainname

class NFSShare(models.Model):
    name = models.CharField(max_length=255)
    server_ip = models.GenericIPAddressField()
    export_path = models.CharField(max_length=512)
    mount_point = models.CharField(max_length=512)
    allowed_groups = models.ManyToManyField('LinuxGroup', related_name='allowed_nfs_shares', blank=True)
    allowed_servers = models.ManyToManyField('Server', related_name='accessible_nfs_shares', blank=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
        if hasattr(instance, 'guestinfo'):
            instance.guestinfo.save()
    except:
        pass