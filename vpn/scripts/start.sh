#!/bin/bash
set -ex

# LDAP settings for scripts/ldap-auth.py (pam_exec does not pass the container environment)
cat > /etc/openvpn/ldap-auth.env <<EOF
LDAP_URI=ldap://ldap:389
LDAP_BASE_DN=${LDAP_BASE_DN}
EOF

PKI=/etc/openvpn/easy-rsa/pki
mkdir -p /var/log/openvpn

# Initialize easy-rsa if not already done
if [ ! -d "$PKI" ]; then
    echo "Initializing easy-rsa PKI..."
    # easy-rsa may already exist as an (empty) volume mount, so copy instead of make-cadir
    mkdir -p /etc/openvpn/easy-rsa
    cp -rn /usr/share/easy-rsa/* /etc/openvpn/easy-rsa/
    cd /etc/openvpn/easy-rsa

    # Initialize PKI without interaction
    ./easyrsa init-pki

    # Build CA without password
    echo "Building CA..."
    EASYRSA_BATCH=1 ./easyrsa build-ca nopass

    # Generate server certificate
    echo "Generating server certificate..."
    EASYRSA_BATCH=1 ./easyrsa build-server-full server nopass

    echo "PKI initialization complete"
fi

# Renew the server certificate well before it expires (clients trust the CA, so this is seamless).
# auto-update.sh restarts the container when renewal is due.
if ! openssl x509 -checkend $((VPN_CERT_RENEW_DAYS * 86400)) -noout -in "$PKI/issued/server.crt"; then
    echo "Renewing server certificate..."
    (cd /etc/openvpn/easy-rsa && EASYRSA_BATCH=1 ./easyrsa renew server)
fi
cd /etc/openvpn

# tls-crypt key (encrypts the control channel) and session token secret
# (lets clients reconnect without OTP, also across server restarts)
[ -f "$PKI/tc.key" ] || openvpn --genkey tls-crypt "$PKI/tc.key"
[ -f "$PKI/auth-token.key" ] || openvpn --genkey auth-token "$PKI/auth-token.key"

# VPN_SUBNET is split in half: first half for UDP clients, second half for TCP clients.
# In each half the first 3/4 of the hosts are fixed per-device IPs (scripts/client-ip.py),
# the rest is a dynamic pool for devices that do not send a device id.
read -r UDP_CIDR UDP_NET UDP_MASK UDP_POOL TCP_CIDR TCP_NET TCP_MASK TCP_POOL STATIC_COUNT < <(python3 -c '
import ipaddress, sys
halves = ipaddress.ip_network(sys.argv[1], strict=False).subnets(1)
out = []
for n in halves:
    hosts = n.num_addresses - 2
    static = (hosts - 1) * 3 // 4
    first = n.network_address + 2 + static
    last = n.broadcast_address - 1
    out += [str(n), n.network_address, n.netmask, f"{first},{last}"]
print(*out, static)' "$VPN_SUBNET")

MAP_FILE=/etc/openvpn/easy-rsa/ip-map.json
[ -f "$MAP_FILE" ] || echo '{}' > "$MAP_FILE"
chown nobody:nogroup "$MAP_FILE"

# Generate client ovpn file if SITE_DOMAIN is set
if [ -n "$SITE_DOMAIN" ]; then
    echo "Generating client configuration..."
    cat > /etc/ovpn/client.ovpn <<EOF
client
setenv CLIENT_CERT 0
nobind
dev tun
remote ${SITE_DOMAIN} 1194 udp
remote ${SITE_DOMAIN} 1194 tcp
server-poll-timeout 5
connect-retry 1 10
resolv-retry infinite
persist-tun
push-peer-info
remote-cert-tls server
verify-x509-name server name
tls-version-min 1.3
tls-groups X25519:prime256v1:secp384r1
data-ciphers AES-256-GCM:CHACHA20-POLY1305
verb 3
auth-user-pass
auth-nocache
static-challenge "Enter OTP:" 1
<ca>
$(cat $PKI/ca.crt)
</ca>
<tls-crypt>
$(cat $PKI/tc.key)
</tls-crypt>
EOF
    echo "Client configuration saved to /etc/ovpn/client.ovpn"
fi

# Set up iptables rules
iptables -A FORWARD -i tun+ -o eth0 -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0 -o tun+ -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT

# NAT web traffic (80/443) from VPN clients to VPN_NAT_HOSTS (comma-separated hostnames)
for host in ${VPN_NAT_HOSTS//,/ }; do
    for gate_ip in $(dig +short "$host" | grep -E '^[0-9.]+$'); do
        iptables -t nat -A POSTROUTING -s $VPN_SUBNET -d $gate_ip -j MASQUERADE -p tcp --dport 80
        iptables -t nat -A POSTROUTING -s $VPN_SUBNET -d $gate_ip -j MASQUERADE -p tcp --dport 443
    done
done

# Options shared by both servers: pushed routes and session tokens
COMMON_ARGS=(--auth-gen-token "$VPN_SESSION_LIFETIME" "$VPN_SESSION_RENEWAL" --auth-gen-token-secret "$PKI/auth-token.key")
for cidr in ${VPN_PUSH_ROUTES//,/ }; do
    route=$(python3 -c 'import ipaddress,sys; n=ipaddress.ip_network(sys.argv[1], strict=False); print(n.network_address, n.netmask)' "$cidr")
    COMMON_ARGS+=(--push "route $route")
done

# TCP fallback server for networks that block UDP
sed -e 's/^proto udp$/proto tcp-server/' \
    -e 's/^dev tun0$/dev tun1/' \
    -e '/^explicit-exit-notify/d' \
    -e 's#openvpn-status.log#openvpn-status-tcp.log#' \
    /etc/openvpn/server.conf > /etc/openvpn/server-tcp.conf

VPN_SUBNET="$VPN_SUBNET" scripts/update_iptables_rules.py &

openvpn --config /etc/openvpn/server.conf "${COMMON_ARGS[@]}" \
    --server $UDP_NET $UDP_MASK nopool --ifconfig-pool ${UDP_POOL/,/ } $UDP_MASK \
    --client-connect "/etc/openvpn/scripts/client-ip.py $UDP_CIDR $STATIC_COUNT" &
openvpn --config /etc/openvpn/server-tcp.conf "${COMMON_ARGS[@]}" \
    --server $TCP_NET $TCP_MASK nopool --ifconfig-pool ${TCP_POOL/,/ } $TCP_MASK \
    --client-connect "/etc/openvpn/scripts/client-ip.py $TCP_CIDR $STATIC_COUNT" &

# On docker stop, let both servers shut down cleanly so they tell clients to reconnect right away
# (explicit-exit-notify) instead of clients waiting for ping-restart
trap 'kill -TERM $(jobs -p) 2>/dev/null; wait; exit 0' TERM INT

# Exit when either server dies so Docker restarts the container
wait -n
exit 1
