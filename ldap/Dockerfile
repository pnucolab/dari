FROM alpine:3

RUN apk upgrade --no-cache \
    && apk add --no-cache bash openssl gettext-envsubst \
       openldap openldap-back-mdb openldap-clients \
    && rm -rf /etc/openldap/slapd.d/* /var/lib/openldap/openldap-data/*

COPY bootstrap /etc/openldap/bootstrap
COPY start.sh /start.sh

EXPOSE 389 636

CMD ["bash", "/start.sh"]
