
FROM debian:trixie

RUN apt update && apt install -y \
    libpam-google-authenticator \
    openvpn \
    openvpn-auth-ldap \
    iptables \
    python3 \
    python3-requests \
    python3-yaml \
    dnsutils \
    easy-rsa \
    && apt clean

WORKDIR /etc/openvpn

COPY scripts /etc/openvpn/scripts
COPY auth-ldap.conf /etc/openvpn/auth-ldap.conf
COPY server.conf /etc/openvpn/server.conf

CMD ["bash", "scripts/start.sh"]