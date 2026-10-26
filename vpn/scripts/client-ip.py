#!/usr/bin/env python3
# client-connect script: give every device (username + IV_HWADDR) the same VPN IP on every
# reconnect, so connections over the tunnel survive reconnects and server restarts.
# Usage: client-ip.py <server-subnet-cidr> <static-host-count> <dynamic-config-file>
# The n-th device gets host n+2 of the subnet (host 1 is the server) in both the UDP and the
# TCP subnet. Devices without IV_HWADDR, or when the static range is full, use the dynamic pool.
import fcntl
import ipaddress
import json
import os
import sys

MAP_FILE = "/etc/openvpn/easy-rsa/ip-map.json"


def main():
    subnet = ipaddress.ip_network(sys.argv[1])
    static_count = int(sys.argv[2])
    config_file = sys.argv[3]

    user = os.environ.get("common_name", "")
    device = os.environ.get("IV_HWADDR", "")
    if not user or not device:
        return 0

    key = f"{user}|{device}"
    with open(MAP_FILE, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        mapping = json.loads(f.read() or "{}")
        if key not in mapping:
            used = set(mapping.values())
            free = next((i for i in range(static_count) if i not in used), None)
            if free is None:
                return 0
            mapping[key] = free
            f.seek(0)
            f.truncate()
            json.dump(mapping, f, indent=1, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        index = mapping[key]

    ip = subnet.network_address + 2 + index
    with open(config_file, "w") as out:
        out.write(f"ifconfig-push {ip} {subnet.netmask}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
