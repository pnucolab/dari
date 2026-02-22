#!/bin/bash
# Build the dari-compute-node deb package
set -e

cd "$(dirname "$0")"

# Copy LDAP CA certificate from db/ldap_certs
CERT_SRC="../db/ldap_certs/ca.crt"
CERT_DST="pkg/etc/dari/ldap-ca.crt"
if [ -f "$CERT_SRC" ]; then
    cp "$CERT_SRC" "$CERT_DST"
    chmod 644 "$CERT_DST"
    echo "Copied LDAP CA certificate from $CERT_SRC"
else
    echo "Error: LDAP CA certificate not found at $CERT_SRC"
    exit 1
fi

# Set permissions
chmod 755 pkg/DEBIAN/config
chmod 755 pkg/DEBIAN/postinst
chmod 755 pkg/DEBIAN/prerm
chmod 755 pkg/usr/bin/dari-compute-setup
chmod 755 pkg/usr/lib/dari/update-config.sh
chmod 644 pkg/DEBIAN/control
chmod 644 pkg/DEBIAN/conffiles
chmod 644 pkg/DEBIAN/templates
chmod 644 pkg/etc/dari/compute-node.conf
chmod 644 pkg/etc/auto.master.d/dari.autofs
chmod 644 pkg/lib/systemd/system/dari-update.service
chmod 644 pkg/lib/systemd/system/dari-update.timer

# Build
dpkg-deb --build pkg dari-compute-node_1.0.0_all.deb

echo "Built: dari-compute-node_1.0.0_all.deb"
