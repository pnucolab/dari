#!/bin/bash
# update-config.sh: Fetch DARI config and regenerate autofs maps
# Called by dari-update.timer every minute

set -e

CONF="/etc/dari/compute-node.conf"
AUTOFS_MASTER="/etc/auto.master.d/dari.autofs"
AUTO_HOME="/etc/dari/auto.home"
DARI_DIR="/etc/dari"

# Parse config file
parse_conf() {
    local key="$1"
    grep -oP "(?<=^${key} = ).*" "$CONF" 2>/dev/null | head -1
}

API_URL=$(parse_conf "api_url")
API_KEY=$(parse_conf "api_key")
NFS_IFACE=$(parse_conf "nfs_iface")
MOUNT_OPTIONS=$(parse_conf "mount_options")

if [ -z "$API_URL" ] || [ -z "$API_KEY" ]; then
    # Not configured yet, skip silently
    exit 0
fi

# Determine source IP for NFS traffic
NFS_IP=""
if [ -n "$NFS_IFACE" ]; then
    NFS_IP=$(ip -4 addr show "$NFS_IFACE" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -1)
fi

# Fetch config from DARI API
CONFIG_URL="${API_URL}/node/config?key=${API_KEY}"
RESPONSE=$(curl -sSf "$CONFIG_URL" 2>/dev/null) || {
    logger -t dari-update "Failed to fetch config from ${CONFIG_URL}"
    exit 1
}

# Parse NFS shares from JSON response
NFS_SHARES=$(echo "$RESPONSE" | jq -r '.nfs_shares // []')
NFS_COUNT=$(echo "$NFS_SHARES" | jq 'length')
LDAP_BASE_DN=$(echo "$RESPONSE" | jq -r '.ldap_base_dn // "dc=dari"')

# Track if anything changed
CHANGED=false

# Generate auto.home (home directory map)
# Use home_server_ip from API response; fall back to DARI host
HOME_SERVER_IP=$(echo "$RESPONSE" | jq -r '.home_server_ip // ""')
if [ -z "$HOME_SERVER_IP" ]; then
    HOME_SERVER_IP=$(echo "$API_URL" | sed -E 's|https?://([^:/]+).*|\1|')
fi
NEW_AUTO_HOME="* -fstype=nfs4,${MOUNT_OPTIONS} ${HOME_SERVER_IP}:/dari-home/&"

if [ ! -f "$AUTO_HOME" ] || [ "$(cat "$AUTO_HOME" 2>/dev/null)" != "$NEW_AUTO_HOME" ]; then
    echo "$NEW_AUTO_HOME" > "$AUTO_HOME"
    CHANGED=true
fi

# Generate autofs maps for NFS shares
# Build new master map entries
MASTER_CONTENT="# DARI automounter - managed by dari-compute-node
# Home directories
/home /etc/dari/auto.home --timeout=600"

# Clean up old dari share maps
rm -f "${DARI_DIR}"/auto.dari.* 2>/dev/null

for i in $(seq 0 $((NFS_COUNT - 1))); do
    SERVER_IP=$(echo "$NFS_SHARES" | jq -r ".[$i].server_ip")
    EXPORT_PATH=$(echo "$NFS_SHARES" | jq -r ".[$i].export_path")
    MOUNT_POINT=$(echo "$NFS_SHARES" | jq -r ".[$i].mount_point")

    # Create a safe filename from mount point
    MAP_NAME=$(echo "$MOUNT_POINT" | sed 's|/|_|g; s|^_||')
    MAP_FILE="${DARI_DIR}/auto.dari.${MAP_NAME}"

    # Generate indirect map content
    # Mount the export path as a direct mount under mount_point
    ADDR="$SERVER_IP"
    if [ -n "$NFS_IP" ]; then
        ADDR="${SERVER_IP},addr=${NFS_IP}"
    fi
    echo "* -fstype=nfs4,${MOUNT_OPTIONS} ${ADDR}:${EXPORT_PATH}/&" > "$MAP_FILE"

    # Add to master map
    MASTER_CONTENT="${MASTER_CONTENT}
${MOUNT_POINT} ${MAP_FILE} --timeout=600"

    CHANGED=true
done

# Update master map if changed
if [ ! -f "$AUTOFS_MASTER" ] || [ "$(cat "$AUTOFS_MASTER" 2>/dev/null)" != "$MASTER_CONTENT" ]; then
    echo "$MASTER_CONTENT" > "$AUTOFS_MASTER"
    CHANGED=true
fi

# Reload autofs if maps changed
if [ "$CHANGED" = true ]; then
    systemctl reload autofs 2>/dev/null || systemctl restart autofs 2>/dev/null || true
    logger -t dari-update "Autofs maps updated (${NFS_COUNT} NFS shares)"
fi
