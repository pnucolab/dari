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
- **VPN**: OpenVPN server with OTP authentication (port 1194/udp)
- **Reverse Proxy**: Caddy server handling HTTPS and access control
- **Task Queue**: Celery with RabbitMQ for async tasks

### Key Technologies

- **Backend**: Python, Django 4.2, Django Ninja, Celery
- **Frontend**: SvelteKit, Flowbite, Tailwind CSS
- **Database**: PostgreSQL 13
- **Directory**: OpenLDAP with python-ldap
- **VPN**: OpenVPN with openvpn-auth-ldap and PAM OTP
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
   - `LDAP_DOMAIN`: LDAP domain (e.g., "dari" becomes dc=dari)
   - `SITE_DOMAIN`: Domain for the service (e.g., vpn.example.com)
   - `DB_USER`, `DB_PASSWORD`, `DB_NAME`: PostgreSQL credentials
   - `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`: RabbitMQ credentials

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
  1. **LDAP password**: Validated via openvpn-auth-ldap plugin
  2. **OTP code**: Validated via PAM with Google Authenticator
- Client profile is dynamically generated using `SITE_DOMAIN`
- Profile available at `/api/vpn/profile` for URL import

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
docker compose exec ldap ldapsearch -x -H ldap://localhost -b "ou=users,dc=dari" -D "cn=admin,dc=dari" -w <admin_password>

# Search groups
docker compose exec ldap ldapsearch -x -H ldap://localhost -b "ou=groups,dc=dari" -D "cn=admin,dc=dari" -w <admin_password>
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

### LDAP Structure

- Base DN: `dc=<LDAP_DOMAIN>`
- Users OU: `ou=users,dc=<LDAP_DOMAIN>`
- Groups OU: `ou=groups,dc=<LDAP_DOMAIN>`
- Admin DN: `cn=admin,dc=<LDAP_DOMAIN>`

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