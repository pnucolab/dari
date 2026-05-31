# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an IT infrastructure management system (DARI) that provides centralized user management, VPN access, Linux account provisioning, and LDAP-based authentication. The system manages Linux accounts, LDAP directory, VPN access with OTP, NFS share/export management, cluster compute/storage nodes, and user lifecycle management.

The repository contains both the **central server** (a Docker Compose stack) and two **Debian node-agent packages** (`compute-node/`, `storage-node/`) that are installed on cluster machines and pull their configuration from the server's API.

## Architecture

### Multi-Service Docker Architecture
- **Frontend**: SvelteKit application with SSR (port 3000 internally)
- **Backend**: Django + Django Ninja REST API (port 8080 internally)
- **Database**: PostgreSQL 13
- **LDAP**: OpenLDAP server for Linux authentication (port 636)
- **VPN**: OpenVPN server with OTP authentication (port 1194/udp)
- **Reverse Proxy**: Caddy server handling HTTPS and access control
- **Task Queue**: Celery with RabbitMQ for async tasks (user removal, deactivation)

### Key Integration Points
1. **LDAP Authentication**: All regular users authenticate via LDAP with passwords stored as SSHA hashes
2. **LDAP Sync**: Backend maintains LDAP directory synchronized with Django database for Linux PAM authentication
3. **VPN Auth**: OpenVPN uses openvpn-auth-ldap plugin to authenticate directly against LDAP server + PAM for OTP validation
4. **Session Management**: Frontend uses cookies for Django session authentication
5. **IP Whitelisting**: Caddy restricts most routes to configured networks (default: 10.125.0.0/16, 164.125.0.0/16)

### Data Flow
- **Registration**: User registers via `/api/register` → Backend atomically creates:
  - Django User + Profile + LinuxInfo
  - LDAP entry with SSHA-hashed password
  - Home directory with proper ownership
  - First user automatically becomes superuser
- **Login**: User logs in via frontend → Backend authenticates via LDAP (regular users) or Django auth (guest users) → Creates session
- **Password Management**: User changes password via `/api/password` → Backend updates LDAP password (SSHA hash)
- **VPN Setup**: User enables VPN → Backend generates Google Authenticator QR code → Stores in `/etc/qr/` → VPN server validates OTP + LDAP password

## Development Commands

### Environment Setup
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with required credentials (DB, LDAP, secrets)
```

### Development Mode (compose-dev.yml)
```bash
# Start all services with hot-reload and debug enabled
docker compose -f compose-dev.yml up --build

# Access frontend at http://localhost:8080
# Backend DEBUG=True, logs to /dev/null
# Volumes mount source code for hot-reload
```

### Production Mode (compose.yml)
```bash
# Start production services
docker compose up -d --build

# View logs
docker compose logs -f [service_name]

# Services: db, caddy, ldap, rabbitmq, celery_worker, celery_beat, vpn, backend, frontend
```

### Backend Development
```bash
# Enter backend container
docker compose exec backend bash

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run Django shell
python manage.py shell

# Test Celery tasks
celery -A backend inspect active
```

### Frontend Development
```bash
# Enter frontend container (dev mode)
docker compose -f compose-dev.yml exec frontend sh

# Install dependencies
cd /app && pnpm install

# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

### Database Operations
```bash
# Access PostgreSQL
docker compose exec db psql -U dari -d dari

# Backup database
docker compose exec db pg_dump -U dari dari > backup.sql

# Restore database
docker compose exec -T db psql -U dari dari < backup.sql
```

## Critical Backend Components

### [backend/backend/api.py](backend/backend/api.py)
Main API endpoints using Django Ninja (single module, ~45 routes). Auth is `django_auth` (session cookie) by default; routes that are public or machine-to-machine pass `auth=None`. Key routes:

**Setup & auth**
- `/api/init` - First-run setup: saves defaults + creates the first admin (only works while there are zero users)
- `/api/register` - Register a regular user (Django user + Profile + LinuxInfo; LDAP entry + home dir are provisioned on first login, except the first user who is provisioned immediately)
- `/api/login` - Authenticates via LDAP (regular users, with Django-password fallback before LDAP provisioning) or Django auth (guest users); enforces email verification + active status
- `/api/logout`, `/api/csrftoken`, `/api/brand`, `/api/allowed-email-domains`

**Email verification & password reset** (allauth + Celery email)
- `/api/verify-email` - Confirm email via allauth HMAC key; notifies admins for approval
- `/api/forgot-password`, `/api/reset-password` - Token-based LDAP password reset
- `/api/password` - Change own LDAP password (verifies old password, 30s lockout on failure)

**User & group management (admin)**
- `/api/user` (PATCH) - Update user attributes, incl. admin password reset and (de)activation
- `/api/guest` - Create/update guest accounts
- `/api/users`, `/api/guests`, `/api/deactivated`, `/api/me`
- `/api/group` (POST/PUT/DELETE), `/api/groups` - LDAP groups with member sync + ACL regen
- `/api/groupadmin` (POST/DELETE), `/api/groupadmins` - Delegate group administration
- `/api/transfer` - Move a user's VPN/Linux/home assets to another user
- `/api/logs`, `/api/defaults`, `/api/emailsend`

**VPN**
- `/api/qr` - Generate Google Authenticator secret + QR for VPN OTP
- `/api/vpn/profile` - Download the generated OpenVPN client profile (public)

**Servers, NFS, and node provisioning**
- `/api/server` (POST/DELETE), `/api/servers`, `/api/servers/stats`, `/api/myservers`
- `/api/nfsshare` (POST/DELETE), `/api/nfsshares` - Manage NFS exports/mounts
- `/api/dari-home-server` (GET/POST) - Designate which storage server hosts `/dari-home`
- `/api/node/config` - Compute node pulls its allowed users/groups + NFS mounts (auth by Server `api_key`)
- `/api/storage/config` - Storage node pulls its exports + allowed client IPs (auth by Server `api_key`)
- `/api/ldap` - Force a full LDAP resync (admin)

### [backend/backend/utils.py](backend/backend/utils.py)
Core utilities:
- `LDAPOps` class - Manages LDAP operations (add/delete users/groups, password management)
  - `add_user()` - Creates LDAP entry with optional password (SSHA hash)
  - `set_password()` - Updates user's LDAP password
  - `authenticate_user()` - Validates username/password against LDAP
- `send_email()` - Bulk email to active users via SMTP/IMAP

### [backend/dariauth/models.py](backend/dariauth/models.py)
Django models (app label is `dariauth`):
- `Profile` - One-to-one with `User`: name, status (`sta`), `date_expire`/`date_removal`, `is_groupadmin`, `password_fail_at` (password-change lockout)
- `LinuxInfo` - Linux account details (username, UID, primary group FK, shell)
- `VPNInfo` - VPN/OTP enablement flag (presence = enabled)
- `GuestInfo` - Guest user metadata (institute, DOB, mobile, reference)
- `LinuxGroup` - LDAP group: name, gid, comma-separated `members`
- `GroupAdmin` - Links a user to the group(s) they may administer
- `Server` - Managed node: domainname, ip, port, `server_type` (`compute`/`storage`), `api_key` (UUID used for node auth), `allowed_groups`
- `NFSShare` - NFS export: server_ip, export_path, mount_point, `allowed_groups`, `allowed_servers`
- `Default` - Key/value store for site settings (sitename, logo, gid, shell, allowed_email_domains, dari_home_server)
- `Log` - Per-user audit log entries

### [backend/dariauth/tasks.py](backend/dariauth/tasks.py)
Celery tasks:
- `remove_users()` - (scheduled) Archives `/dari-home` to `/mnt/archive`, deletes LDAP entry + user after `date_removal`
- `deactivate_users()` - (scheduled) Marks users inactive after `date_expire`, sets `date_removal` 6 months out
- `update_users_sta()` - Placeholder for status sync
- `clear_password_fail(username)` - Clears the password-change lockout flag (scheduled by `/api/password`)
- `send_verification_email_task` / `send_admin_approval_email_task` / `send_password_reset_email_task` - Async transactional email (implementations in [backend/backend/utils.py](backend/backend/utils.py))

## Critical Frontend Components

### [frontend/src/lib/fetch.js](frontend/src/lib/fetch.js)
API client for backend communication. Handles:
- Cookie-based authentication (sessionid + CSRF token)
- Automatic header injection
- Base URL configuration via `API_BASE_URL` env var (defaults to `http://backend:8080/api/`)

### [frontend/src/routes/+layout.server.js](frontend/src/routes/+layout.server.js)
Root layout server load function:
- Fetches brand info (sitename, logo)
- Validates user session via `/api/me`
- Redirects to `/login` if unauthenticated
- Forces admin to `/init` if sitename not configured
- Sets up i18n locale from cookies

### Route Groups
- `(nonadmin)/` - Regular user pages: profile, VPN, Linux accounts, groups
- `admin/` - Admin pages: user management, groups, servers, settings, email
- `init/` - Initial setup page for first admin
- `login/`, `logout/` - Authentication

## Important Configuration

### LDAP Integration
- Base DN is derived from `LDAP_DOMAIN` in one place — `settings.LDAP_BASE_DN` (e.g. "dari" → `dc=dari`, "example.com" → `dc=example,dc=com`) — and threaded through `LDAPOps(base_dn=...)` in [utils.py](backend/backend/utils.py), the `/api/node/config` response, and the VPN auth config. Do **not** hardcode `dc=dari`; use `self.base_dn` / `settings.LDAP_BASE_DN`.
- The VPN plugin config [vpn/auth-ldap.conf](vpn/auth-ldap.conf) is a template whose `__BASE_DN__` and `PUT_LDAP_PASSWORD_HERE` placeholders are substituted by [vpn/scripts/start.sh](vpn/scripts/start.sh) at container start (from `LDAP_BASE_DN`/`LDAP_DOMAIN` and `LDAP_ADMIN_PASSWORD`).
- Admin credentials: `cn=admin,dc=...` with `LDAP_ADMIN_PASSWORD`
- Two OUs: `ou=users` and `ou=groups` under base DN
- Users: `cn=<username>,ou=users,dc=...` with posixAccount + inetOrgPerson objectClasses
- Groups: `cn=<groupname>,ou=groups,dc=...` with posixGroup objectClass
- Passwords stored as SSHA hashes in `userPassword` attribute

### User Management
- **Regular Users**: Authenticate via LDAP, passwords stored as SSHA hashes in LDAP
- **Guest Users**: Authenticate via Django, passwords stored as Django password hashes
- **User Creation**: Use `/api/register` endpoint or admin panel
- **Password Changes**: Regular users use `/api/password`, admins can reset via `/api/user` PATCH endpoint

### Home Directory Management
- Production: `/mnt/dari-home/<username>` (mounted volume)
- Development: `./dari-home/<username>` (local directory)
- Created from `/etc/skel` template with proper UID/GID ownership

### VPN OTP Flow
1. User requests QR via `/api/qr` → Backend runs `google-authenticator` → Stores secret in `/etc/qr/<username>`
2. VPN server uses two authentication plugins in sequence:
   - `openvpn-auth-ldap.so` - Validates username/password against LDAP (`ou=users,dc=bce`)
   - `openvpn-plugin-auth-pam.so` - Validates OTP code via Google Authenticator PAM module
3. VPN access granted only if both LDAP password and OTP are valid
4. Configuration: [vpn/auth-ldap.conf](vpn/auth-ldap.conf) and [vpn/server.conf](vpn/server.conf)

## Cluster Node Packages

Two Debian packages let cluster machines self-configure from the central server. Each is built with `dpkg-deb` via its `build.sh` and packaged under `pkg/` (debconf templates in `pkg/DEBIAN/`).

### [compute-node/](compute-node/)
Installs an LDAP client (nslcd) and an autofs-based automounter. A systemd timer ([dari-update.timer](compute-node/pkg/lib/systemd/system/dari-update.timer)) periodically runs [update-config.sh](compute-node/pkg/usr/lib/dari/update-config.sh), which:
1. Reads [/etc/dari/compute-node.conf](compute-node/pkg/etc/dari/compute-node.conf) (`api_url`, `api_key`, NIC names, mount options)
2. Calls `GET {api_url}/node/config?key={api_key}`
3. Regenerates autofs maps (`/etc/auto.master.d/dari.autofs`, `auto.home`, per-share `auto.dari.*`) for `/home` (from the dari-home server) and each allowed NFS share, then reloads autofs
- Reconfigure on a host with `dari-compute-setup` (wraps `dpkg-reconfigure`).

### [storage-node/](storage-node/)
Configures NFS exports. Pulls `GET {api_url}/storage/config?key={api_key}` to learn which paths to export and to which compute IPs (including `/dari-home` if this server is the designated home server). Reconfigure with `dari-storage-setup`.

Both authenticate to the server purely via the per-`Server` `api_key` (UUID). The server resolves visibility/ACLs per node IP — see `LDAPOps.regenerate_acls()` in [utils.py](backend/backend/utils.py).

## Deployment Notes

### Required Environment Variables
See [.env.example](.env.example) for all variables. Critical ones:
- `SECRET_KEY` - Django secret (generate with `openssl rand -base64 32`)
- `LDAP_ADMIN_PASSWORD` - LDAP admin password
- `LDAP_DOMAIN` - LDAP domain (e.g., "dari" becomes dc=dari)
- `RABBITMQ_DEFAULT_USER/PASS` - RabbitMQ credentials for Celery
- `SITE_DOMAIN` - Domain for Caddy HTTPS certificates

**Note**: External authentication environment variables are no longer required. The system uses LDAP-based authentication with passwords managed directly in LDAP.

### Volume Mounts
Production volumes in `./db/`:
- `postgres_data/` - PostgreSQL database
- `ldap_data/`, `ldap_config/`, `ldap_certs/` - LDAP directory, config, and auto-generated TLS certificates
- `caddy_data/`, `caddy_config/` - Caddy certificates and config
- `vpn_easy_rsa/` - VPN PKI and auto-generated certificates
- `ovpn/` - Generated OpenVPN client profile
- `qr/` - VPN OTP secrets
- `ip_addresses` - Server IP whitelist file

### Access Control
Caddy enforces IP whitelist for all routes except `/guest/{uuid}`. Add IPs via admin interface → backend writes to `/etc/ip_addresses`.

## Testing

The `test/` directory contains Docker configuration for testing LDAP/PAM integration with nslcd on a client container.
