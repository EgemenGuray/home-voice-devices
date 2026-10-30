#!/usr/bin/env bash
# Writes the firewall and systemd units for the Show device under a root directory
# (/ on the Pi; a temp dir in tests). Called by install.sh.
# Usage: KIOSK_USER=kiosk HA_HOST_IP=192.0.2.10 ./render.sh [root]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-/}"
: "${KIOSK_USER:?set KIOSK_USER}" "${HA_HOST_IP:?set HA_HOST_IP}"

# One IPv4 host only: a range or a name here would open the satellite port to more than HA.
octet='(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
if [[ ! "$HA_HOST_IP" =~ ^$octet\.$octet\.$octet\.$octet$ || "$HA_HOST_IP" == 0.0.0.0 ]]; then
  echo "HA_HOST_IP must be a single IPv4 address, got '$HA_HOST_IP'." >&2; exit 1
fi
if [[ ! "$KIOSK_USER" =~ ^[a-z_][a-z0-9_-]{0,31}$ || "$KIOSK_USER" == root ]]; then
  echo "KIOSK_USER must be an ordinary user name, got '$KIOSK_USER'." >&2; exit 1
fi

install -d "$ROOT/etc/systemd/system"
sed "s|@HA_HOST_IP@|$HA_HOST_IP|g" "$HERE/nftables.conf" > "$ROOT/etc/nftables.conf"
for unit in home-show-wakeword.service home-show-satellite.service; do
  sed "s|@USER@|$KIOSK_USER|g" "$HERE/systemd/$unit" > "$ROOT/etc/systemd/system/$unit"
done
