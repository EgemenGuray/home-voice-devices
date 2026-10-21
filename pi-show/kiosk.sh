#!/usr/bin/env bash
# Started by labwc. Shows the HA dashboard full screen and restarts Chromium if it dies.
# shellcheck disable=SC1091
source /etc/home-show.env
URL="${DASHBOARD_URL:?set DASHBOARD_URL in /etc/home-show.env}"
while true; do
  chromium-browser --kiosk --noerrdialogs --disable-infobars --no-first-run \
    --disable-features=Translate,MediaRouter --disable-session-crashed-bubble \
    --password-store=basic \
    --ozone-platform=wayland --app="$URL"
  sleep 3
done
