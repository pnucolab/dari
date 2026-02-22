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
    api_key: str
    server_type: str

class UserServerSchema(Schema):
    domainname: str
    ip: str
    port: Union[int, None]

class NFSShareSchema(Schema):
    pk: int
    name: str
    server_ip: str
    export_path: str
    mount_point: str
    allowed_groups: list[str]
    allowed_servers: list[str]

class NodeNFSShareSchema(Schema):
    server_ip: str
    export_path: str
    mount_point: str

class NodeConfigSchema(Schema):
    nfs_shares: list[NodeNFSShareSchema]
    allowed_users: list[str]
    allowed_groups: list[str]
    ldap_base_dn: str
    home_server_ip: str

class StorageExportSchema(Schema):
    path: str
    allowed_ips: list[str]

class StorageConfigSchema(Schema):
    exports: list[StorageExportSchema]
    dari_home: bool
    dari_home_ips: list[str]

class LogSchema(Schema):
    username: str
    name: str
    service: str
    content: str
    created_at: datetime

class GroupAdminSchema(Schema):
    linux_username: str
    group_names: list[str]