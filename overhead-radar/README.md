# Overhead Radar

A live radar of the aircraft around you, designed for a round desktop screen. It is centred on Galway by default.

- North-up scope with range rings, compass, a slow sweep and the local airfields (EICM, EINN, EIKN, EICA, EIIM)
- Aircraft icons point along their track, are coloured by altitude and leave a short trail
- Each label shows callsign, flight level or altitude, a climb/descent arrow and ground speed
- A **Nearest / Overhead now** panel shows type, registration, distance and bearing
- Emergency squawks (7500 / 7600 / 7700) flash red
- Tap the screen (or press `+` / `-`) to cycle the range: 10, 20, 40, 80 nm
- If no live feed is reachable, it falls back to **demo traffic** (labelled `DEMO`)

Altitude colours run green (low) → yellow (FL100) → amber (FL200) → red (FL300) → purple (FL400). Grey means on the ground.

## Run it

Needs Python 3.8+ only; no packages to install.

```bash
python3 server.py
```

Then open <http://localhost:8000>. To see the look without any data, open <http://localhost:8000/?demo=1>.

### Data sources

| `--source` | What it is | Notes |
|---|---|---|
| `adsblol` (default) | [adsb.lol](https://adsb.lol), a free community ADS-B network | No key. Coverage over Galway depends on volunteer receivers. |
| `airplaneslive` | [airplanes.live](https://airplanes.live), another free community network | No key. Keep `--interval` at 2 s or more. |
| `readsb` | Your own receiver: RTL-SDR dongle + 1090 MHz antenna running readsb, dump1090 or tar1090 | Best coverage of low traffic overhead, and it works offline. |

```bash
python3 server.py --source airplaneslive
```

```bash
python3 server.py --source readsb --readsb-url http://localhost:8080/data/aircraft.json
```

### Options

| Option | Default | |
|---|---|---|
| `--lat`, `--lon` | 53.2707, -9.0568 | Centre of the scope (your house) |
| `--name` | Galway | Label under the clock |
| `--radius` | 100 | Search radius in nm for online sources |
| `--interval` | 5 | Seconds between data fetches |
| `--host`, `--port` | 127.0.0.1, 8000 | Use `--host 0.0.0.0` to view from other devices on your network |

The page also accepts URL overrides: `?lat=53.30&lon=-8.94&name=Carnmore&range=20`.

## Putting it on a round screen

A Raspberry Pi with a round display works well:

- **Screen:** any round display the Pi can drive, e.g. a 480×480 2.1″ round HAT, or a larger round HDMI panel. The page scales to whatever size it gets and fills the shortest side.
- **Pi:** a Pi 4, Pi 5 or Zero 2 W. The drawing is light, but a Zero is slower to start Chromium.
- **Optional receiver:** an RTL-SDR dongle and a 1090 MHz antenna near a window, running readsb. Then use `--source readsb`. You can also share your data with adsb.lol to improve local coverage for everyone.

### Start on boot

1. Copy this folder to the Pi, e.g. `/home/pi/overhead-radar`.

2. Create `/etc/systemd/system/overhead-radar.service`:

   ```ini
   [Unit]
   Description=Overhead Radar
   After=network-online.target
   Wants=network-online.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/overhead-radar/server.py --source adsblol
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable the service:

   ```bash
   sudo systemctl enable --now overhead-radar
   ```

4. Open the page full screen at login. On Raspberry Pi OS Bookworm (labwc desktop), add this line to `~/.config/labwc/autostart`:

   ```bash
   chromium --kiosk --noerrdialogs --disable-infobars --password-store=basic http://localhost:8000 &
   ```

   On older Raspberry Pi OS versions the browser is called `chromium-browser`.

## Notes

- Community ADS-B data is unfiltered and can be delayed or incomplete. This is a display toy, not a navigation or traffic-avoidance tool.
- Aircraft without ADS-B, and many light aircraft with Mode S only, may not appear on the online sources.
- Positions are dead-reckoned between updates, so the motion is smooth even with a 5-second feed.
