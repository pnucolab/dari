#!/bin/bash
# update-exports.sh: Fetch DARI config and regenerate /etc/exports
# Called by dari-storage-update.timer every minute

set -e

CONF="/etc/dari/storage-node.conf"
EXPORTS_FILE="/etc/exports"

# Parse config file
parse_conf() {
    local key="$1"
    grep -oP "(?<=^${key} = ).*" "$CONF" 2>/dev/null | head -1
}

API_URL=$(parse_conf "api_url")
API_KEY=$(parse_conf "api_key")
NFS_IFACE=$(parse_conf "nfs_iface")
EXPORT_OPTIONS=$(parse_conf "export_options")

if [ -z "$API_URL" ] || [ -z "$API_KEY" ]; then
    # Not configured yet, skip silently
    exit 0
fi

# Default export options
if [ -z "$EXPORT_OPTIONS" ]; then
    EXPORT_OPTIONS="rw,sync,no_subtree_check,sec=sys"
fi

# Fetch config from DARI API
CONFIG_URL="${API_URL}/storage/config?key=${API_KEY}"
RESPONSE=$(curl -sSf "$CONFIG_URL" 2>/dev/null) || {
    logger -t dari-storage-update "Failed to fetch config from ${CONFIG_URL}"
    exit 1
}

# Build new /etc/exports content
NEW_EXPORTS="# Managed by dari-storage-node - do not edit manually"

# Parse regular exports
EXPORT_COUNT=$(echo "$RESPONSE" | jq '.exports | length')
for i in $(seq 0 $((EXPORT_COUNT - 1))); do
    EXPORT_PATH=$(echo "$RESPONSE" | jq -r ".exports[$i].path")
    IP_COUNT=$(echo "$RESPONSE" | jq ".exports[$i].allowed_ips | length")

    LINE="${EXPORT_PATH}"
    for j in $(seq 0 $((IP_COUNT - 1))); do
        IP=$(echo "$RESPONSE" | jq -r ".exports[$i].allowed_ips[$j]")
        LINE="${LINE} ${IP}(${EXPORT_OPTIONS})"
    done

    NEW_EXPORTS="${NEW_EXPORTS}
${LINE}"
done

# Parse dari-home export
DARI_HOME=$(echo "$RESPONSE" | jq -r '.dari_home')
if [ "$DARI_HOME" = "true" ]; then
    DARI_HOME_IPS=$(echo "$RESPONSE" | jq -r '.dari_home_ips[]' 2>/dev/null)
    LINE="/dari-home"
    for IP in $DARI_HOME_IPS; do
        LINE="${LINE} ${IP}(${EXPORT_OPTIONS})"
    done
    NEW_EXPORTS="${NEW_EXPORTS}
${LINE}"
fi

# Compare with existing and update if changed
CURRENT_EXPORTS=""
if [ -f "$EXPORTS_FILE" ]; then
    CURRENT_EXPORTS=$(cat "$EXPORTS_FILE")
fi

if [ "$CURRENT_EXPORTS" != "$NEW_EXPORTS" ]; then
    echo "$NEW_EXPORTS" > "$EXPORTS_FILE"
    exportfs -ra 2>/dev/null || true
    logger -t dari-storage-update "NFS exports updated (${EXPORT_COUNT} shares)"
fi
