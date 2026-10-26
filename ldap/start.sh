#!/bin/bash
# OpenLDAP for DARI: bootstraps cn=config and the base DN on first start,
# keeps the TLS certificate valid, then runs slapd in the foreground.
set -euo pipefail

LDAP_BASE_DN=${LDAP_BASE_DN:-dc=${LDAP_DOMAIN//./,dc=}}
CERTS=/etc/openldap/certs
CONFIG=/etc/openldap/slapd.d
DATA=/var/lib/openldap/openldap-data

# --- TLS: self-signed CA (10 years) + server certificate renewed before it expires
mkdir -p "$CERTS"
if [ ! -f "$CERTS/ca.crt" ]; then
    echo "Generating LDAP CA..."
    openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 3650 \
        -subj "/CN=DARI LDAP CA" -keyout "$CERTS/ca.key" -out "$CERTS/ca.crt"
fi
if [ ! -f "$CERTS/ldap.crt" ] || ! openssl x509 -checkend $((LDAP_CERT_RENEW_DAYS * 86400)) -noout -in "$CERTS/ldap.crt"; then
    echo "Issuing LDAP server certificate..."
    openssl req -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
        -subj "/CN=${SITE_DOMAIN}" -keyout "$CERTS/ldap.key" -out "$CERTS/ldap.csr"
    san="DNS:ldap,DNS:localhost"
    if [[ "$SITE_DOMAIN" =~ ^[0-9.]+$ ]]; then san="$san,IP:$SITE_DOMAIN"; else san="$san,DNS:$SITE_DOMAIN"; fi
    openssl x509 -req -in "$CERTS/ldap.csr" -CA "$CERTS/ca.crt" -CAkey "$CERTS/ca.key" -CAcreateserial \
        -days 825 -out "$CERTS/ldap.crt" \
        -extfile <(printf "subjectAltName=%s\nextendedKeyUsage=serverAuth\nkeyUsage=digitalSignature" "$san")
    rm -f "$CERTS/ldap.csr"
fi
chown -R ldap:ldap "$CERTS"
chmod 600 "$CERTS"/*.key

# --- First start: build cn=config (with the schemas spliced in at #SCHEMAS) and the base entry
mkdir -p "$CONFIG" "$DATA"
if [ -z "$(ls -A "$CONFIG")" ]; then
    echo "Bootstrapping LDAP for $LDAP_BASE_DN..."
    export LDAP_BASE_DN LDAP_ORGANISATION LDAP_TLS_VERIFY_CLIENT
    export LDAP_ADMIN_HASH=$(slappasswd -s "$LDAP_ADMIN_PASSWORD")
    export LDAP_CONFIG_HASH=$(slappasswd -s "$LDAP_CONFIG_PASSWORD")
    export LDAP_DC=$(echo "$LDAP_BASE_DN" | sed -E 's/^dc=([^,]+).*/\1/')
    config=$(envsubst < /etc/openldap/bootstrap/config.ldif.in)
    {
        echo "$config" | sed '/^#SCHEMAS$/,$d'
        for s in core cosine nis inetorgperson; do echo; grep -v '^#' "/etc/openldap/schema/$s.ldif"; done
        echo
        echo "$config" | sed '1,/^#SCHEMAS$/d'
    } | slapadd -n0 -F "$CONFIG"
    envsubst < /etc/openldap/bootstrap/base.ldif.in | slapadd -n1 -F "$CONFIG"
fi

mkdir -p /run/openldap /var/lib/openldap/run  # ldapi socket lives in the latter
chown -R ldap:ldap "$CONFIG" "$DATA" /run/openldap /var/lib/openldap/run

exec slapd -d stats -u ldap -g ldap -F "$CONFIG" -h "ldap:/// ldaps:/// ldapi:///"
