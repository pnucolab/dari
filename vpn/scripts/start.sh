#!/bin/bash
set -ex

# Configure LDAP authentication with environment variables
sed -i "s/PUT_LDAP_PASSWORD_HERE/${LDAP_ADMIN_PASSWORD}/g" /etc/openvpn/auth-ldap.conf

# Initialize easy-rsa if not already done
if [ ! -d "/etc/openvpn/easy-rsa/pki" ]; then
    echo "Initializing easy-rsa PKI..."
    cd /etc/openvpn
    make-cadir easy-rsa
    cd easy-rsa

    # Initialize PKI without interaction
    ./easyrsa init-pki

    # Build CA without password
    echo "Building CA..."
    EASYRSA_BATCH=1 ./easyrsa build-ca nopass

    # Generate DH parameters
    echo "Generating DH parameters..."
    ./easyrsa gen-dh

    # Generate server certificate
    echo "Generating server certificate..."
    EASYRSA_BATCH=1 ./easyrsa build-server-full server nopass

    echo "PKI initialization complete"
fi

# Generate client ovpn file if SITE_DOMAIN is set
if [ -n "$SITE_DOMAIN" ]; then
    echo "Generating client configuration..."
    cat > /etc/ovpn/client.ovpn <<EOF
client
setenv CLIENT_CERT 0
nobind
dev tun
remote ${SITE_DOMAIN} 1194 udp
cipher AES-256-CBC
key-direction 1
verb 3
auth-user-pass
static-challenge "Enter OTP:" 1
reneg-sec 0
<ca>
$(cat /etc/openvpn/easy-rsa/pki/ca.crt)
</ca>
EOF
    echo "Client configuration saved to /etc/ovpn/client.ovpn"
fi

# Set up iptables rules
iptables -A FORWARD -i tun0 -o eth0 -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0 -o tun0 -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT

gate_ip=`dig +short gate.pusan.ac.kr`
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -d $gate_ip -j MASQUERADE -p tcp --dport 80
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -d $gate_ip -j MASQUERADE -p tcp --dport 443

scripts/update_iptables_rules.py &

openvpn --daemon ovpn-server --cd /etc/openvpn --config /etc/openvpn/server.conf --log /var/log/openvpn.log

tail -f /var/log/openvpn.log