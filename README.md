# DARI - IT Infrastructure Management System

A comprehensive IT infrastructure management platform that provides centralized user management, VPN access, Linux account provisioning, and LDAP-based authentication.

## Features

- **Centralized User Management**: Web-based portal for managing users, profiles, and access
- **LDAP Integration**: OpenLDAP directory service for Linux authentication with SSHA password hashing
- **VPN Access**: OpenVPN server with OTP (Google Authenticator) support and profile URL import
- **Linux Account Provisioning**: Automated creation of Linux accounts with home directories
- **Group Management**: LDAP-based group management with member synchronization
- **Role-Based Access Control**: Admin, group admin, and regular user roles
- **User Lifecycle Management**: Automatic deactivation and archival of expired accounts
- **Email Notifications**: Bulk email system for active users
- **IP Whitelisting**: Caddy-based access control for network security

## Architecture

### Services

- **Frontend**: SvelteKit application with SSR (port 3000 internally)
- **Backend**: Django + Django Ninja REST API (port 8080 internally)
- **Database**: PostgreSQL 13
- **LDAP**: OpenLDAP server for Linux authentication (port 636)
- **VPN**: OpenVPN server with OTP authentication (port 1194/udp, 1194/tcp fallback)
- **Reverse Proxy**: Caddy server handling HTTPS and access control
- **Task Queue**: Celery with RabbitMQ for async tasks

### Key Technologies

- **Backend**: Python, Django 4.2, Django Ninja, Celery
- **Frontend**: SvelteKit, Tailwind CSS
- **Database**: PostgreSQL 13
- **Directory**: OpenLDAP with python-ldap
- **VPN**: OpenVPN with PAM (LDAP bind + Google Authenticator OTP)
- **Reverse Proxy**: Caddy 2
- **Message Queue**: RabbitMQ

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Linux host with `/dev/net/tun` support (for VPN)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dari
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required variables:
   - `SECRET_KEY`: Django secret key (generate with `openssl rand -base64 32`)
   - `LDAP_ADMIN_PASSWORD`: LDAP admin password
   - `LDAP_DOMAIN`: LDAP domain (e.g., "pnu.med")
   - `LDAP_BASE_DN`: LDAP base DN (e.g., "dc=pnu,dc=med"; derived from `LDAP_DOMAIN` if empty)
   - `SITE_DOMAIN`: Domain for the service (e.g., vpn.example.com)
   - `DB_USER`, `DB_PASSWORD`, `DB_NAME`: PostgreSQL credentials
   - `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`: RabbitMQ credentials

   VPN variables:
   - `VPN_PUSH_ROUTES`: Comma-separated CIDRs pushed to clients as routes
   - `VPN_NAT_HOSTS`: Comma-separated hostnames clients reach via NAT on 80/443
   - `VPN_SUBNET`: Client subnet (first half UDP, second half TCP fallback)
   - `VPN_SESSION_LIFETIME`: Max session length before OTP is required again (0 = never while online)
   - `VPN_SESSION_RENEWAL`: Token renewal interval; offline clients reconnect without OTP for up to 2x this
   - `VPN_CERT_RENEW_DAYS`: Renew the server certificate this many days before expiry

3. **Start services**

   **Development mode** (with hot-reload):
   ```bash
   docker compose -f compose-dev.yml up --build
   ```

   **Production mode**:
   ```bash
   docker compose up -d --build
   ```

4. **Access the application**
   - Open your browser to `http://localhost:8080` (dev) or `http://<SITE_DOMAIN>` (production)
   - Register the first user (automatically becomes admin)
   - Complete initial setup at `/init`

## User Management

### User Types

1. **Regular Users**
   - Authenticate via LDAP
   - Have Linux accounts with home directories
   - Can access VPN with OTP
   - Passwords stored as SSHA hashes in LDAP

2. **Guest Users**
   - Authenticate via Django
   - No Linux accounts
   - Temporary access with expiration dates
   - Usernames start with "guest"

3. **Administrators**
   - Full system access
   - Manage users, groups, and settings
   - Can reset passwords and configure system

4. **Group Admins**
   - Manage specific LDAP groups
   - Limited administrative privileges

### Registration Flow

1. User registers at `/register` with username, password, and name
2. Backend atomically creates:
   - Django User + Profile + LinuxInfo
   - LDAP entry with SSHA-hashed password
   - Home directory with proper ownership
3. First user automatically becomes superuser

## VPN Setup

### For Users

1. **Enable OTP**
   - Navigate to VPN page in portal
   - Generate QR code
   - Scan with Google Authenticator, FreeOTP, or Microsoft Authenticator

2. **Download OpenVPN Profile**
   - Click "Download Profile" button, or
   - Use profile import URL in OpenVPN Connect app

3. **Connect to VPN**
   - Username: Your Linux username
   - Password: Your LDAP password + OTP code (e.g., `mypassword123456`)

### VPN Architecture

- OpenVPN uses two-factor authentication:
  1. **LDAP password**: Validated by binding as the user (PAM `pam_exec` + `vpn/scripts/ldap-auth.py`)
  2. **OTP code**: Validated via PAM with Google Authenticator
- Client profile is dynamically generated using `SITE_DOMAIN`
- Profile available at `/api/vpn/profile` for URL import

### VPN Security and Reconnection

- Control channel is wrapped with `tls-crypt` (unauthenticated packets are dropped, port scans see nothing)
- TLS 1.3 only with ECDHE (X25519); data channel is AEAD only (AES-256-GCM, ChaCha20-Poly1305)
- Clients verify the server certificate (`remote-cert-tls server`, `verify-x509-name`)
- After the first login the server issues a session token (`auth-gen-token`), so reconnects,
  hourly key rotation and server restarts do not prompt for OTP again (see `VPN_SESSION_LIFETIME`/`VPN_SESSION_RENEWAL`)
- Every device (username + device id sent via `push-peer-info`) keeps the same VPN IP across reconnects
  and server restarts (`vpn/scripts/client-ip.py`, map stored in the PKI volume)
- The server certificate is renewed automatically `VPN_CERT_RENEW_DAYS` before expiry
- Clients roam between networks without dropping the session (`float`), keep the tunnel
  interface up while reconnecting, and fall back to TCP when UDP is blocked
- Profiles generated before tls-crypt was enabled must be downloaded again

## Security Updates

All images are Alpine based (official `*-alpine` images, or `alpine:3` for vpn/ldap) and use
floating tags (`postgres:18-alpine`, `caddy:2-alpine`, `rabbitmq:4-alpine`, `python:3.15-alpine`,
`node:24-alpine`) so patch releases are picked up automatically. Python dependencies are pinned
to compatible releases (`~=`) so rebuilds take patch versions.

`auto-update.sh` pulls newer upstream images, rebuilds local images when their base image or
Alpine packages have updates (or when they are older than `AUTO_UPDATE_REBUILD_DAYS`), restarts
services whose TLS certificate is due for renewal, and recreates only the changed containers.
Install it as a systemd timer on the Docker host (`AUTO_UPDATE_SCHEDULE`, daily by default):

```bash
./install-auto-update.sh
```

Variables: `AUTO_UPDATE_SCHEDULE`, `AUTO_UPDATE_REBUILD_DAYS`, `VPN_CERT_RENEW_DAYS`, `LDAP_CERT_RENEW_DAYS`.

## Development

### Backend Development

```bash
# Enter backend container
docker compose exec backend bash

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Check Celery tasks
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

### LDAP Operations

```bash
# Search users
docker compose exec ldap ldapsearch -x -H ldap://localhost -b "ou=users,dc=pnu,dc=med" -D "cn=admin,dc=pnu,dc=med" -w <admin_password>

# Search groups
docker compose exec ldap ldapsearch -x -H ldap://localhost -b "ou=groups,dc=pnu,dc=med" -D "cn=admin,dc=pnu,dc=med" -w <admin_password>
```

## API Endpoints

Key endpoints in `/api/`:

- `POST /register` - Register new user with Linux/LDAP account
- `POST /login` - Authenticate via LDAP (regular) or Django (guest)
- `POST /password` - Change user's LDAP password
- `POST /qr` - Generate Google Authenticator QR for VPN OTP
- `GET /vpn/profile` - Download OpenVPN client profile (public)
- `GET /me` - Get current user info
- `GET /users` - List users (admin)
- `PATCH /user` - Update user attributes (admin)
- `POST /guest` - Create guest user (admin)
- `GET /groups` - List LDAP groups
- `POST /group` - Create LDAP group (admin)
- `PUT /group` - Update LDAP group
- `POST /emailsend` - Send bulk email (admin)

## Configuration

### Admin Settings

Configured in the portal (Admin > Settings / Email), stored in the database:

- **Institution name** (Korean, and optionally English shown when the UI is in English) and logo
- **Top bar colors**: two colors and the share (%) of each
- **SMTP** (Email > SMTP settings): host, port, SSL/TLS / STARTTLS / none, credentials, from address,
  subject prefix, with a test send. The `EMAIL_*` values in `.env` are used until SMTP is saved here;
  the saved password is never sent back to the browser.

### LDAP Structure

- Base DN: `<LDAP_BASE_DN>`
- Users OU: `ou=users,<LDAP_BASE_DN>`
- Groups OU: `ou=groups,<LDAP_BASE_DN>`
- Admin DN: `cn=admin,<LDAP_BASE_DN>`

### Home Directories

- **Production**: `/mnt/dari-home/<username>`
- **Development**: `./dari-home/<username>`
- Created from `/etc/skel` template
- Proper UID/GID ownership applied automatically

### Celery Scheduled Tasks

Runs daily at midnight:
- `remove_users()` - Archives and deletes expired users after 6 months
- `deactivate_users()` - Marks users inactive after expiration date

## Security

- All passwords stored securely (LDAP: SSHA hash, Django: PBKDF2)
- IP whitelisting via Caddy reverse proxy
- TLS support for LDAP (port 636)
- Two-factor authentication for VPN
- CSRF protection on all API endpoints
- Session-based authentication with secure cookies

## Volume Mounts

Production volumes in `./db/`:
- `postgres_data/` - PostgreSQL database
- `ldap_data/`, `ldap_config/`, `ldap_certs/` - LDAP directory, config, and auto-generated TLS certificates
- `caddy_data/`, `caddy_config/` - Caddy certificates and config
- `vpn_easy_rsa/` - VPN PKI and auto-generated certificates
- `ovpn/` - Generated OpenVPN client profile
- `qr/` - VPN OTP secrets
- `ip_addresses` - Server IP whitelist file

All certificates (LDAP, VPN) are auto-generated on first initialization.

## Troubleshooting

### Container Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f vpn
docker compose logs -f ldap
```

### Common Issues

1. **LDAP connection failed**
   - Check LDAP container is running: `docker compose ps ldap`
   - Verify LDAP_ADMIN_PASSWORD in .env
   - Check LDAP logs: `docker compose logs ldap`

2. **VPN connection failed**
   - Ensure OTP is enabled in user profile
   - Verify password + OTP format: `<password><6-digit-code>`
   - Check VPN logs: `docker compose logs vpn`

3. **Database migration errors**
   - Run migrations manually: `docker compose exec backend python manage.py migrate`
   - Check database is accessible: `docker compose exec db psql -U dari -d dari`

## License

MIT License

Copyright (c) 2025 Level4

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.