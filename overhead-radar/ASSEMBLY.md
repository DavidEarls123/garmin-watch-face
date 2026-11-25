# Assembling the Overhead Radar

For the Waveshare 5″ round screen, Raspberry Pi 5, RTL-SDR V3 and the printed case. There's an interactive 3D version of the case, with these same steps, in `case/viewer/index.html`.

## What to print (`case/stl/waveshare-5in-round/`)

| Instrument style | Puck style | Notes |
|---|---|---|
| `instrument_bezel.stl` | `puck_bezel.stl` | Prints face-down |
| `instrument_box.stl` | `puck_body.stl` | Prints back-down; the longest print |
| `retaining_ring.stl` | `puck_retaining_ring.stl` | The puck ring is trimmed to clear the flat underside. Don't swap them. |
| `instrument_stand.stl` | none | Prints standing on its foot |
| `antenna_grommet.stl` | `antenna_grommet.stl` | Print two, as one may snap |

Use PETG or PLA, 0.2 mm layers, 3 walls, 15–20 % infill, **no supports**. Print the ring and the bezel first and test-fit the screen.

## Screws and bits

| Qty | Item | Where |
|---|---|---|
| 4 (puck: 3) | M3 × 12 or × 16 button head | Bezel to box/body |
| 4 | M2.5 × 8 button head | Retaining ring into the back of the bezel |
| 4 | M2.5 × 6 or × 8 button head | Pi onto the standoffs |
| ~0.5 m | 6 mm × 1 mm foam tape | Ring cushion, and a strip to hold the dongle |
| tools | 2 mm and 1.5 mm hex keys, soft cloth, a computer with a microSD reader | |

## Steps

Steps 1–3 test everything on the bench first.

1. **Prepare the microSD card.** In Raspberry Pi Imager choose *Raspberry Pi 5* → *Raspberry Pi OS (64-bit)*, the version with the desktop. In the settings, set a username and password and your Wi-Fi, and enable SSH. Write the card and put it in the Pi.
2. **Fit the Active Cooler and bench test the screen.**
   - Peel the film off the thermal pads, click the two spring pins into the Pi, and plug the fan lead into **FAN**.
   - Connect the micro-HDMI cable to **HDMI 0** (next to the USB-C power socket), and the screen's USB cable to a Pi USB port. That cable carries touch and powers the screen.
   - Power up and check the picture and touch.
   - **Tape-mark the top edge of the screen.**
   - If there's no picture, add the `config.txt` lines from the Waveshare wiki's "5inch 1080x1080 LCD" page.
3. **Install the software.** Plug the dongle into the USB extension and the extension into the Pi. Screw the antenna's SMA plug onto the dongle; you don't need the MCX adapter. Then, in a terminal:
   ```bash
   git clone -b claude/garmin-forerunner-watchface-options-esgt9b https://github.com/davidearls123/garmin-watch-face.git
   cd garmin-watch-face/overhead-radar
   sudo ./tools/setup-pi.sh --with-receiver --lat 53.2707 --lon -9.0568 --name Galway
   sudo reboot
   ```
   If the repository is private, Git asks you to sign in: use your GitHub username and a personal access token as the password. After the reboot, the radar opens full screen and shows **RECEIVER+ADSBLOL** under the clock. Try tapping a plane, zooming, changing place, and tracking a flight.
4. **Shut down** with `sudo shutdown now`, then unplug everything.
5. **Pad the retaining ring.** Run the foam tape around the ring's flat face near its inner edge. Butt the ends; don't overlap them. **Leave the backing film on** the exposed side, so it cushions the screen rather than gluing it.
6. **Screen into the bezel.** Lay the bezel face-down on a cloth and drop the screen in face-down, with the **taped top edge at the top**. On the instrument, the top is opposite the stand window; on the puck, it's opposite the flat. Screw the ring on with 4 × M2.5 × 8, tightening in a cross pattern until snug. **Don't overtighten.**
7. **Pi into the box.** Screw the Pi onto the standoffs (4 × M2.5 × 6/8), cooler towards the screen. Feed the power supply's USB-C plug in through the 16 mm hole from outside and plug it in.
8. **Dongle and antenna lead.** Plug the extension into the Pi and stick the dongle to the floor with foam tape, away from the Pi. From **outside**, push the antenna's SMA plug in through the 13 mm port and screw it on. Click the cable into the grommet's slot and press the grommet into the port from outside until it snaps.
9. **Connect and close.** Connect the micro-HDMI (Pi HDMI 0) and the screen's USB cable. Tuck the cables beside the Pi so nothing presses on the screen. Fit the bezel, top edges matching, and drive in the M3 button heads.
10. **Stand it up.**
    - **Instrument:** underside on the stand's shelf, back against the rest, leads out through the window.
    - **Puck:** on its flat underside.
    - **Antenna:** upright, high in a window, away from the Pi, ideally on a metal plate.
11. **Power on.** The radar starts in about a minute. Add your places with the pin button → *Add a place…*. After a day or two, run `sudo readsb-gain autogain`.

## Troubleshooting

| Problem | Try |
|---|---|
| Black screen | Use HDMI 0. Check the screen's USB cable is connected, since it powers the screen. Add the Waveshare `config.txt` lines. |
| No touch | The touch signal travels over the screen's USB cable to the Pi |
| Picture rotated | Use *Screen Configuration* on the Pi, or turn the screen in the bezel |
| No RECEIVER under the clock | `lsusb` should list a Realtek RTL2838. Check `journalctl -u readsb -n 50`. |
| Radar doesn't open | `journalctl -u overhead-radar -n 50`, or open `http://localhost:8000` in a browser |
| Few planes from the receiver | Move the antenna higher, nearer the window and away from the Pi, on metal. Run autogain after a day. |
