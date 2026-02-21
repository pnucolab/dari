from typing import Union
from ninja import Schema
from datetime import datetime, date

from django.contrib.auth.models import User

class ProfileSchema(Schema):
    name: str
    sta: str
    date_expire: Union[date, None]
    date_removal: Union[date, None]
    is_groupadmin: bool

class GuestInfoSchema(Schema):
    institute: str
    date_of_birth: Union[date, None]
    mobile: str
    reference: str

class VPNSchema(Schema):
    pass

class LinuxGroupSchema(Schema):
    pk: int
    name: str
    gid: int
    members: Union[str, None]

class LinuxGroupShortSchema(Schema):
    name: str

class LinuxSchema(Schema):
    username: str
    group: Union[LinuxGroupSchema, None]
    uid: int

class LinuxShortSchema(Schema):
    username: str
    group: Union[LinuxGroupShortSchema, None]
    uid: int

class UserSchema(Schema):
    username: str
    email: str
    date_joined: datetime
    profile: Union[ProfileSchema, None] = None
    guestinfo: Union[GuestInfoSchema, None] = None
    vpn: Union[VPNSchema, None] = None
    linux: Union[LinuxShortSchema, None] = None
    is_active: bool
    is_staff: bool

class ServerSchema(Schema):
    domainname: str
    ip: str
    port: Union[int, None]
    visible: bool
    stats: Union[dict[str, str], None]
    allowed_groups: list[str]

class UserServerSchema(Schema):
    domainname: str
    ip: str
    port: Union[int, None]

class LogSchema(Schema):
    username: str
    name: str
    service: str
    content: str
    created_at: datetime

class GroupAdminSchema(Schema):
    linux_username: str
    group_names: list[str]