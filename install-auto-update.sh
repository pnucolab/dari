#!/bin/bash
# Install a systemd timer on the Docker host that runs auto-update.sh
# on the schedule given by AUTO_UPDATE_SCHEDULE in .env.
set -euo pipefail
DARI_DIR="$(cd "$(dirname "$0")" && pwd)"

SCHEDULE=$(grep -E '^AUTO_UPDATE_SCHEDULE=' "$DARI_DIR/.env" | cut -d= -f2-)
SCHEDULE=${SCHEDULE:-"*-*-* 04:00:00"}

cat > /etc/systemd/system/dari-update.service <<EOF
[Unit]
Description=Apply security updates to DARI containers
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=$DARI_DIR/auto-update.sh
EOF

cat > /etc/systemd/system/dari-update.timer <<EOF
[Unit]
Description=DARI security update check

[Timer]
OnCalendar=$SCHEDULE
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now dari-update.timer
systemctl list-timers dari-update.timer --no-pager
