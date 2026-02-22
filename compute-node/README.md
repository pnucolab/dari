# dari-compute-node

A Debian package that automatically provisions compute nodes to integrate with the DARI infrastructure management system.

## What It Does

Upon installation, the package configures three core subsystems:

### 1. LDAP Authentication

Configures the node to authenticate users against the DARI LDAP server so that all DARI-managed accounts can log in seamlessly.

- Installs and configures **nslcd** (LDAP NSS daemon) to resolve users/groups from `ou=users` and `ou=groups` under the DARI base DN
- Deploys **nsswitch.conf** to look up `passwd` and `group` entries from LDAP after local files
- Configures **PAM** modules (`pam_ldap`) for LDAP-based login
- Fetches the LDAP TLS CA certificate from `db/ldap_certs/ca.crt` on the DARI server for secure connections (LDAPS on port 636)
- **Server-side filtering**: The DARI backend only returns LDAP entries for users belonging to the server's allowed groups. Compute nodes only see users that are authorized to access them, preventing enumeration of unrelated accounts

### 2. NFS Shares via Automounter

Mounts NFS home directories and shared storage using **autofs**, with access controlled by DARI server settings. Home directories are automounted from the NFS server — `pam_mkhomedir` is intentionally not used.

- Installs and configures **autofs** for on-demand NFS mounting
- At install time, migrates existing local home directories from `/home/` to `/home.local/` and updates `/etc/passwd` accordingly, freeing `/home/` for autofs
- Sets up a **home directory map** (`/etc/auto.home`) that automounts user home directories from the DARI NFS server under `/home/`
- Periodically fetches the node's allowed NFS exports from the DARI API (`/api/myservers`) based on the `allowed_groups` configuration set by the admin in the DARI panel
- Generates autofs map files from the API response — mount points and export paths are defined on the server, not hardcoded locally
- Runs a **systemd timer** (or cron job) to poll the API and regenerate maps when the admin changes group-to-server assignments, then reloads autofs
- Admins control which groups can access which NFS servers entirely from the DARI web admin panel (Admin > Servers > Allowed Groups)

#### Mount Layout

```
/home/<username>/                     # automounted from nfs-server:/dari-home/<username>

<mount_point>/                        # mount points retrieved from DARI server
├── <server1-export>/                 # e.g., /data/shared/
├── <server2-export>/                 # e.g., /scratch/
└── ...
```

Mount points and export paths are configured per-server in the DARI admin panel and retrieved by the compute node at runtime. Only servers whose `allowed_groups` include a group that exists on this node will be mounted. If `allowed_groups` is empty, the server is accessible to all nodes.

### 3. Server Status via all-smi

Reports GPU/accelerator hardware status back to the DARI dashboard using [all-smi](https://github.com/lablup/all-smi).

- Installs **all-smi** (from the lablup PPA or bundled binary)
- Configures all-smi in **API mode** to expose Prometheus-compatible metrics on a local port
- The DARI backend polls each registered node's all-smi endpoint to display real-time GPU temperature, utilization, and memory usage in the admin Servers panel

## Installation

### Prerequisites

- Ubuntu/Debian-based system
- Network access to the DARI server (LDAP port 636, API port 8080)
- NFS client support (`nfs-common`)

### Install

```bash
sudo dpkg -i dari-compute-node_<version>.deb
sudo apt-get install -f   # resolve dependencies if needed
```

### Configure

After installation, run the setup script or edit the configuration file:

```bash
sudo dpkg-reconfigure dari-compute-node
```

Or edit `/etc/dari/compute-node.conf` directly:

```ini
[network]
# Network adapter for management traffic (DARI API, LDAP, all-smi)
management_iface = eno1

# Network adapter for NFS data traffic
nfs_iface = eno2

[dari]
# DARI server URL (required)
api_url = https://dari.example.com/api

# API key for this node (generated in DARI admin panel)
api_key = <node-api-key>

[ldap]
# LDAP server URI (defaults to the DARI LDAP server)
uri = ldaps://dari.example.com
base_dn = dc=dari
tls_cacert = /etc/dari/ldap-ca.crt

[nfs]
# Polling interval in seconds for NFS map updates
poll_interval = 60

# autofs options (e.g., timeout, mount flags)
mount_options = rw,soft,intr,timeo=30

[allsmi]
# Port for all-smi API mode
port = 9100
```

## Package Contents

```
/etc/dari/
├── compute-node.conf        # main configuration
├── ldap-ca.crt              # LDAP TLS certificate (placed during setup)
├── auto.home                # autofs map for home directories
├── auto.dari.*              # generated autofs maps for shared storage (managed by daemon)
└── update-nfs-maps.sh       # script to fetch and regenerate autofs maps

/etc/nslcd.conf.d/
└── dari.conf                # nslcd drop-in for DARI LDAP

/etc/nsswitch.conf           # updated to include ldap lookups

/etc/auto.master.d/
└── dari.autofs              # autofs master map entry

/usr/lib/systemd/system/
├── dari-nfs-update.service  # NFS map update oneshot service
└── dari-nfs-update.timer    # periodic trigger (default: every 1 min)

/usr/bin/
└── dari-compute-setup       # interactive first-time setup script
```

## How NFS Access Control Works

1. Admin registers a server in the DARI web panel (Admin > Servers) with its domain name, IP, and optionally restricts access to specific Linux groups via **Allowed Groups**
2. The `dari-nfs-update` timer periodically calls the DARI API to fetch the list of servers this node is allowed to mount (based on group membership)
3. The response (including mount points and export paths defined on the server) is translated into autofs map files
4. autofs mounts the NFS shares on-demand when users access the configured mount points
5. The LDAP server only returns user/group entries for the allowed groups of this server — users outside those groups are not visible on the node
6. When the admin changes group assignments, the next poll picks up the change, reloads autofs, and updates the LDAP filter accordingly

## Uninstallation

```bash
sudo apt-get remove dari-compute-node
```

This removes all configuration and restores the original `nsswitch.conf`. Active NFS mounts are unmounted. LDAP users will no longer be resolvable on this node.

## Dependencies

| Package | Purpose |
|---|---|
| `nslcd` | LDAP NSS lookups |
| `libpam-ldapd` | PAM LDAP authentication (no mkhomedir) |
| `autofs` | On-demand NFS automounting |
| `nfs-common` | NFS client utilities |
| `all-smi` | GPU/accelerator monitoring |
| `curl` | API communication |
| `jq` | JSON parsing for API responses |
