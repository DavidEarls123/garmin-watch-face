# Overhead Radar

A live radar of the aircraft around you, designed for a round desktop screen. It is centred on Galway by default.

- North-up scope with range rings, compass, a slow sweep and the local airfields (EICM, EINN, EIKN, EICA, EIIM)
- A smooth outline of the land, coast and lakes from 100 m OpenStreetMap data, with a finer level of detail at 5–20 nm, plus towns and area names (Galway Bay, Lough Corrib, the Burren, Connemara…)
- **Eight looks:** Night Scope, Glass Cockpit, Paper Chart, Green Chart, Phosphor, Amber Tower, Red Devils and Minimal. Pick one from ⚙ settings (the *Look* row), or fine-tune it in the Appearance panel. The radar server saves the choice as a system setting in `settings.json`, so it survives restarts and browser resets and applies to every screen. Choose the starting look with `--theme` (or `setup-pi.sh --theme greenchart`). You can adjust any look: six bundled fonts, aircraft colour schemes, and layout options (clock, info card, labels, rings, compass, map style, sweep, trails, scanlines). The panel docks on the right of wide screens, sits below the radar on phones, and opens from ⚙ → *Appearance…* (or `A`) on the round display. Add `?theme=chart` and similar to the URL to pick a look directly.
- Aircraft icons point along their track, are coloured by altitude and leave a short trail
- Each label shows callsign, flight level or altitude, a climb/descent arrow and ground speed
- A **Nearest / Overhead now** panel shows type, registration, distance and bearing
- **Tap any plane** for its details: route, operator, type, registration, live altitude/speed/climb, and a photo of that exact aircraft (or a drawn outline of its type when there's no photo)
- Emergency squawks (7500 / 7600 / 7700) flash red
- Touch buttons zoom in and out (5–80 nm), switch between saved **places**, and edit or add places (presets, typed coordinates, the device's location, or tap a spot on the map)
- **Track a flight** by flight number or callsign (EI105 or EIN105): a progress card on the scope, plus a great-circle view showing distance flown, distance to go and ETA, even when the flight is far away
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
| `hybrid` | Your receiver **and** an online network (`--online`, default adsb.lol), merged per aircraft so the fresher position wins | Recommended with a receiver. |
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
| `--no-lookups` | off | Don't look up routes, owners or photos when a plane is tapped |

The page also accepts URL overrides: `?lat=53.30&lon=-8.94&name=Carnmore&range=20`.

### Changing the centre point

Tap ⚙ (bottom-left) or press `S`. You can:

- pick a preset (Galway, Carnmore, Shannon, Knock, Dublin),
- type or paste coordinates (pasting `53.27, -9.05` into Latitude fills both boxes),
- use the device's location, if it can provide one,
- or choose **Pick on the map** and tap the spot.

The choice is saved on that screen and survives restarts. **Reset** goes back to the server's `--lat`/`--lon`. The order of priority is: URL parameters, then the centre saved on the screen, then `--lat`/`--lon`, then Galway.

With an online source, the server fetches traffic around whichever centre the screen asks for. With your own receiver, the centre only moves the view; the receiver still hears what it hears.

## Map

`geo.js` holds the land and lake outlines for Ireland and the surrounding area (longitude −12° to −3°, latitude 50.3° to 56.8°), at two levels of detail: about 60 m for ranges up to 25 nm and 250 m beyond. The outlines are drawn with gentle curves. Fonts in `fonts/` are bundled under the SIL Open Font License, so the display works offline. If you move the centre outside that area, the traffic still works but there's no map underneath.

To build a map for another area, edit the bounds at the top of `tools/build_geo.py` and follow the instructions in that file.

Map data © OpenStreetMap contributors, available under the [Open Database License](https://opendatacommons.org/licenses/odbl/1.0/), via [@geo-maps](https://github.com/simonepri/geo-maps) (100 m resolution).

**Building the physical display:** see [HARDWARE.md](HARDWARE.md) for the parts list, controls, and the 3D-printable cases in `case/`.

### Flight details and photos

When you tap a plane, the server looks it up, caching each answer for 6 hours:

- **hexdb.io:** owner, type and registration, plus the route. Routes are crowd-sourced from callsigns, so a charter or a changed flight number can show the wrong route.
- **planespotters.net:** a photo of that airframe. The photographer is credited on screen, as their terms require.

Both are free community services. Use `--no-lookups` to turn them off.

## Raspberry Pi setup in one step

```bash
sudo ./tools/setup-pi.sh --with-receiver --lat 53.2707 --lon -9.0568 --name Galway
```

This installs Chromium, readsb (if you have a receiver) and a systemd service, and sets the radar to open full screen at login. Leave out `--with-receiver` if you have no dongle. Add `--rtlsdr-v4` for an RTL-SDR Blog V4. The script hasn't yet been run on a real Pi, so watch its output the first time.

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
