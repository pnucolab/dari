#!/usr/bin/env python3
# pam_exec helper: verify a VPN user's LDAP password by binding as that user.
# PAM_USER comes from the environment, the password from stdin (expose_authtok).
import os
import sys

import ldap

CONFIG = "/etc/openvpn/ldap-auth.env"


def valid_username(s):
    # Same rule as backend utils.validate(); also keeps the DN free of special characters
    return 0 < len(s) <= 31 and s[0].isalpha() and s.isalnum() and s.islower()


def main():
    user = os.environ.get("PAM_USER", "")
    password = sys.stdin.buffer.read().rstrip(b"\0").decode("utf-8", "replace")
    if not valid_username(user) or not password:
        return 1

    with open(CONFIG) as f:
        cfg = dict(line.rstrip("\n").split("=", 1) for line in f if "=" in line)

    conn = ldap.initialize(cfg["LDAP_URI"])
    conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10)
    try:
        conn.simple_bind_s(f"cn={user},ou=users,{cfg['LDAP_BASE_DN']}", password)
    except ldap.LDAPError:
        return 1
    finally:
        conn.unbind_s()
    return 0


if __name__ == "__main__":
    sys.exit(main())
