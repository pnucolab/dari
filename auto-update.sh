#!/bin/bash
# Apply security updates to every DARI service:
#  - pull newer upstream images (db, caddy, rabbitmq)
#  - rebuild a local image when its base image or Alpine packages have updates, or when it is
#    older than AUTO_UPDATE_REBUILD_DAYS (picks up patch releases of Python packages)
#  - restart services whose TLS certificate is due for renewal (vpn, ldap renew on start)
#  - recreate only the containers whose image changed
# VPN clients reconnect on their own with their session token and keep their IP.
set -euo pipefail
cd "$(dirname "$0")"

log() { logger -t dari-update "$*"; echo "$*"; }
envval() { grep -E "^$1=" .env | cut -d= -f2-; }

REBUILD_DAYS=$(envval AUTO_UPDATE_REBUILD_DAYS)
REBUILD_DAYS=${REBUILD_DAYS:-7}

# service image dockerfile-base, one line per locally built service
mapfile -t BUILT < <(docker compose config --format json | python3 -c '
import json, os, sys
cfg = json.load(sys.stdin)
project = cfg["name"]
for name, svc in cfg["services"].items():
    build = svc.get("build")
    if not build:
        continue
    dockerfile = os.path.join(build["context"], build.get("dockerfile", "Dockerfile"))
    base = next(l.split()[1] for l in open(dockerfile) if l.upper().startswith("FROM "))
    print(name, svc.get("image") or f"{project}-{name}", base)')
if [ ${#BUILT[@]} -eq 0 ]; then
    log "error: could not list locally built services"
    exit 1
fi

running() { docker compose ps --status running -q "$1" | grep -q .; }

log "pulling upstream images"
docker compose pull -q --ignore-buildable

rebuild=()
for line in "${BUILT[@]}"; do
    read -r svc image base <<< "$line"
    docker pull -q "$base" >/dev/null
    # A local image built on the current base contains the base's top layer
    base_top=$(docker image inspect -f '{{json .RootFS.Layers}}' "$base" | python3 -c 'import json,sys; print(json.load(sys.stdin)[-1])')
    reason=""
    if ! docker image inspect "$image" >/dev/null 2>&1; then
        reason="image missing"
    elif ! docker image inspect -f '{{json .RootFS.Layers}}' "$image" | grep -q "$base_top"; then
        reason="new $base base image"
    elif [ $(( ($(date +%s) - $(date -d "$(docker image inspect -f '{{.Created}}' "$image")" +%s)) / 86400 )) -ge "$REBUILD_DAYS" ]; then
        reason="older than $REBUILD_DAYS days"
    elif running "$svc"; then
        pending=$(docker compose exec -T "$svc" sh -c 'apk update -q >/dev/null 2>&1 && apk upgrade --simulate 2>/dev/null | grep -c Upgrading' || true)
        [ "${pending:-0}" -gt 0 ] && reason="$pending package update(s)"
    fi
    if [ -n "$reason" ]; then
        log "$svc: rebuilding ($reason)"
        rebuild+=("$svc")
    fi
done

if [ ${#rebuild[@]} -gt 0 ]; then
    docker compose build --pull --no-cache "${rebuild[@]}"
fi

# Recreates every container whose image changed (pulled or rebuilt); untouched ones keep running
docker compose up -d --remove-orphans

# Certificates are renewed by the service's start script; restart when renewal is due
for svc_cert in "vpn:/etc/openvpn/easy-rsa/pki/issued/server.crt:VPN_CERT_RENEW_DAYS" \
                "ldap:/etc/openldap/certs/ldap.crt:LDAP_CERT_RENEW_DAYS"; do
    IFS=: read -r svc cert var <<< "$svc_cert"
    days=$(envval "$var")
    if running "$svc" && ! docker compose exec -T "$svc" openssl x509 -checkend $(( ${days:-60} * 86400 )) -noout -in "$cert" >/dev/null; then
        log "$svc: certificate renewal due, restarting"
        docker compose restart "$svc"
    fi
done

docker image prune -f >/dev/null
log "update check finished"
