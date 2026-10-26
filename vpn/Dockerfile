FROM alpine:3

RUN apk upgrade --no-cache \
    && apk add --no-cache bash openvpn openvpn-auth-pam google-authenticator linux-pam \
       easy-rsa iptables bind-tools python3 py3-ldap py3-requests py3-yaml

WORKDIR /etc/openvpn

COPY scripts /etc/openvpn/scripts
COPY server.conf /etc/openvpn/server.conf

CMD ["bash", "scripts/start.sh"]
