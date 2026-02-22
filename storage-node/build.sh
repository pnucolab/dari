#!/bin/bash
# Build the dari-storage-node deb package
set -e

cd "$(dirname "$0")"

# Set permissions
chmod 755 pkg/DEBIAN/config
chmod 755 pkg/DEBIAN/postinst
chmod 755 pkg/DEBIAN/prerm
chmod 755 pkg/usr/bin/dari-storage-setup
chmod 755 pkg/usr/lib/dari/update-exports.sh
chmod 644 pkg/DEBIAN/control
chmod 644 pkg/DEBIAN/conffiles
chmod 644 pkg/DEBIAN/templates
chmod 644 pkg/etc/dari/storage-node.conf
chmod 644 pkg/lib/systemd/system/dari-storage-update.service
chmod 644 pkg/lib/systemd/system/dari-storage-update.timer

# Build
dpkg-deb --build pkg dari-storage-node_1.0.0_all.deb

echo "Built: dari-storage-node_1.0.0_all.deb"
