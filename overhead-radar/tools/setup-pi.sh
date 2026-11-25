#!/usr/bin/env bash
# Overhead Radar – one-time setup on a Raspberry Pi (Raspberry Pi OS Bookworm, desktop).
#
#   sudo ./tools/setup-pi.sh                         # online data only (adsb.lol)
#   sudo ./tools/setup-pi.sh --with-receiver         # + RTL-SDR dongle (V3 or similar) and readsb
#   sudo ./tools/setup-pi.sh --with-receiver --rtlsdr-v4   # RTL-SDR Blog V4: also installs its driver
#   sudo ./tools/setup-pi.sh --with-receiver --lat 53.2707 --lon -9.0568 --name Galway
#
# What it does:
#   1. installs Chromium (for the full-screen page)
#   2. with --with-receiver: installs readsb (wiedehopf's installer), blacklists the TV-tuner driver
#      and sets the receiver's location; with --rtlsdr-v4 also the RTL-SDR Blog V4 driver
#   3. creates a systemd service for server.py (source "hybrid" with a receiver, "adsblol" without)
#   4. opens the radar full screen when the desktop starts
# Safe to run again; each step checks what is already there.

set -euo pipefail

LAT=53.2707
LON=-9.0568
NAME=Galway
RECEIVER=0
V4=0
KIOSK=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --with-receiver) RECEIVER=1 ;;
        --rtlsdr-v4) RECEIVER=1; V4=1 ;;
        --no-kiosk) KIOSK=0 ;;
        --lat) LAT="$2"; shift ;;
        --lon) LON="$2"; shift ;;
        --name) NAME="$2"; shift ;;
        -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
        *) echo "Unknown option: $1 (try --help)"; exit 1 ;;
    esac
    shift
done

if [[ $EUID -ne 0 ]]; then
    echo "Run with sudo: sudo $0 $*"; exit 1
fi
RUN_USER="${SUDO_USER:-pi}"
RUN_HOME="$(getent passwd "$RUN_USER" | cut -d: -f6)"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
step() { echo; echo "==> $*"; }

step "Packages"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 curl ca-certificates
if ! command -v chromium >/dev/null && ! command -v chromium-browser >/dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq chromium || DEBIAN_FRONTEND=noninteractive apt-get install -y -qq chromium-browser
fi
BROWSER="$(command -v chromium || command -v chromium-browser)"

SOURCE=adsblol
if [[ $RECEIVER -eq 1 ]]; then
    SOURCE=hybrid

    step "readsb (decodes ADS-B from the dongle)"
    if ! systemctl list-unit-files readsb.service >/dev/null 2>&1 || ! command -v readsb >/dev/null; then
        tmp="$(mktemp -d)"
        curl -fsSL -o "$tmp/readsb-install.sh" https://raw.githubusercontent.com/wiedehopf/adsb-scripts/master/readsb-install.sh
        # NO_TAR1090: skip the extra web map; the radar page replaces it
        NO_TAR1090=1 bash "$tmp/readsb-install.sh"
        rm -rf "$tmp"
    else
        echo "readsb already installed"
    fi

    if [[ $V4 -eq 1 ]]; then
    step "RTL-SDR Blog V4 driver (the stock library may not support the V4's tuner)"
    if [[ ! -f /usr/local/lib/.rtlsdr-blog-installed ]]; then
        DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git cmake build-essential pkg-config libusb-1.0-0-dev
        # readsb is already built, so the distribution's library can go (as the vendor's guide does)
        DEBIAN_FRONTEND=noninteractive apt-get purge -y -qq '^librtlsdr' || true
        rm -rf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*
        tmp="$(mktemp -d)"
        git clone --depth 1 https://github.com/rtlsdrblog/rtl-sdr-blog "$tmp/rtl-sdr-blog"
        cmake -S "$tmp/rtl-sdr-blog" -B "$tmp/build" -DINSTALL_UDEV_RULES=ON >/dev/null
        make -C "$tmp/build" -j"$(nproc)" >/dev/null
        make -C "$tmp/build" install >/dev/null
        cp "$tmp/rtl-sdr-blog/rtl-sdr.rules" /etc/udev/rules.d/
        rm -rf "$tmp"
        ldconfig
        touch /usr/local/lib/.rtlsdr-blog-installed
    else
        echo "RTL-SDR Blog driver already installed"
    fi
    fi
    echo 'blacklist dvb_usb_rtl28xxu' > /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
    udevadm control --reload-rules || true

    step "Receiver location"
    if command -v readsb-set-location >/dev/null; then
        readsb-set-location "$LAT" "$LON" || true
    fi
    systemctl restart readsb || true
fi

step "Overhead Radar service ($SOURCE)"
cat > /etc/systemd/system/overhead-radar.service <<EOF
[Unit]
Description=Overhead Radar
After=network-online.target readsb.service
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 $APP_DIR/server.py --source $SOURCE --lat $LAT --lon $LON --name "$NAME"
Restart=always
RestartSec=5
User=$RUN_USER

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now overhead-radar
systemctl restart overhead-radar

if [[ $KIOSK -eq 1 ]]; then
    step "Full-screen start at login"
    LINE="$BROWSER --kiosk --noerrdialogs --disable-infobars --password-store=basic --check-for-update-interval=31536000 http://localhost:8000 &"
    # labwc (current Raspberry Pi OS desktop)
    install -d -o "$RUN_USER" -g "$RUN_USER" "$RUN_HOME/.config/labwc"
    AUTOSTART="$RUN_HOME/.config/labwc/autostart"
    touch "$AUTOSTART"; chown "$RUN_USER:$RUN_USER" "$AUTOSTART"
    grep -q 'localhost:8000' "$AUTOSTART" || echo "$LINE" >> "$AUTOSTART"
    # wayfire (earlier Bookworm desktop)
    WAYFIRE="$RUN_HOME/.config/wayfire.ini"
    if [[ -f "$WAYFIRE" ]] && ! grep -q 'localhost:8000' "$WAYFIRE"; then
        grep -q '^\[autostart\]' "$WAYFIRE" || printf '\n[autostart]\n' >> "$WAYFIRE"
        sed -i "/^\[autostart\]/a radar = $LINE" "$WAYFIRE"
    fi
fi

step "Checks"
sleep 2
if curl -fsS http://localhost:8000/api/config >/dev/null; then echo "Radar server: running on http://localhost:8000"; else echo "Radar server: NOT responding. See: journalctl -u overhead-radar -n 50"; fi
if [[ $RECEIVER -eq 1 ]]; then
    if [[ -s /run/readsb/aircraft.json ]]; then echo "readsb: writing /run/readsb/aircraft.json"; else echo "readsb: no data yet. Plug in the dongle, reboot, then: journalctl -u readsb -n 50"; fi
    echo "Tip: after a day running, 'sudo readsb-gain autogain' tunes the gain."
fi
echo
echo "Done. Reboot to start the full-screen display:  sudo reboot"
