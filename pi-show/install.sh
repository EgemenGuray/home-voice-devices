#!/usr/bin/env bash
# S0.7.3: Show-style device on a Raspberry Pi 5 + Touch Display 2 + ReSpeaker XVF3800 (USB).
# Turns a fresh Raspberry Pi OS Bookworm Lite (64-bit) into a kiosk that shows the HA
# dashboard and runs a voice satellite for Assist. Camera-free.
# Usage on the Pi: sudo ./install.sh   (reads /etc/home-show.env; see home-show.env.example)
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE=/etc/home-show.env
[[ -f "$ENV_FILE" ]] || { install -m 600 "$HERE/home-show.env.example" "$ENV_FILE"; echo "Edit $ENV_FILE, then run again."; exit 1; }
# shellcheck disable=SC1090
source "$ENV_FILE"
: "${KIOSK_USER:=kiosk}" "${HA_HOST_IP:?set HA_HOST_IP in $ENV_FILE}" "${SATELLITE_NAME:=Living room show}"
# Check the values before anything is installed; the real files are written further down.
KIOSK_USER="$KIOSK_USER" HA_HOST_IP="$HA_HOST_IP" "$HERE/render.sh" "$(mktemp -d)" >/dev/null

echo "== Packages"
apt-get update
apt-get install -y --no-install-recommends \
  labwc chromium-browser wlr-randr seatd \
  python3-venv python3-dev git alsa-utils libopenblas0 \
  nftables unattended-upgrades

echo "== Kiosk user with auto-login on tty1"
id "$KIOSK_USER" >/dev/null 2>&1 || useradd -m -G video,audio,input,render "$KIOSK_USER"
passwd -l "$KIOSK_USER"
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<CONF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $KIOSK_USER --noclear %I \$TERM
CONF

echo "== labwc session that starts Chromium in kiosk mode"
KHOME=$(getent passwd "$KIOSK_USER" | cut -d: -f6)
install -d -o "$KIOSK_USER" "$KHOME/.config/labwc"
install -m 755 -o "$KIOSK_USER" "$HERE/kiosk.sh" "$KHOME/kiosk.sh"
echo "$KHOME/kiosk.sh &" > "$KHOME/.config/labwc/autostart"
chown "$KIOSK_USER" "$KHOME/.config/labwc/autostart"
grep -q 'exec labwc' "$KHOME/.bash_profile" 2>/dev/null || \
  echo '[[ -z $WAYLAND_DISPLAY && $(tty) == /dev/tty1 ]] && exec labwc' >> "$KHOME/.bash_profile"

echo "== Voice satellite (Wyoming) with local wake word"
install -d -o "$KIOSK_USER" /opt/home-show
if [[ ! -d /opt/home-show/wyoming-satellite ]]; then
  sudo -u "$KIOSK_USER" git clone --depth 1 https://github.com/rhasspy/wyoming-satellite /opt/home-show/wyoming-satellite
  sudo -u "$KIOSK_USER" bash -c 'cd /opt/home-show/wyoming-satellite && script/setup'
fi
if [[ ! -d /opt/home-show/wyoming-openwakeword ]]; then
  sudo -u "$KIOSK_USER" git clone --depth 1 https://github.com/rhasspy/wyoming-openwakeword /opt/home-show/wyoming-openwakeword
  sudo -u "$KIOSK_USER" bash -c 'cd /opt/home-show/wyoming-openwakeword && script/setup'
fi

echo "== Firewall (the satellite port is reachable only from Home Assistant) and services"
KIOSK_USER="$KIOSK_USER" HA_HOST_IP="$HA_HOST_IP" "$HERE/render.sh" /
systemctl enable --now nftables

echo "== Hardening"
systemctl disable --now ssh 2>/dev/null || true   # re-enable only over Tailscale if you need it
systemctl disable --now bluetooth 2>/dev/null || true
dpkg-reconfigure -f noninteractive unattended-upgrades

systemctl daemon-reload
systemctl enable --now home-show-wakeword.service home-show-satellite.service
echo "Done. Reboot; then in HA add the Wyoming integration for this Pi (port 10700)."
