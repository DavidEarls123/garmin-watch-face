# Building the Overhead Radar

## The build as ordered

| Part | Notes |
|---|---|
| Raspberry Pi 5 (4 GB) | ✓ |
| Waveshare 5″ HDMI round touch, 1080×1080 | ✓ The case STLs in `case/stl/waveshare-5in-round/` are sized for it. |
| BOXPUT 27 W USB-C, UK plug | ✓ 5.1 V / 5 A is what the Pi 5 wants. |
| SanDisk Extreme 32 GB microSD | ✓ |
| Silkland micro-HDMI → HDMI 30 cm | ✓ The Pi 5 has micro-HDMI. Check that the screen's socket is full-size HDMI when it arrives; Waveshare often includes an adapter too. |
| Raspberry Pi Active Cooler | ✓ Needed, since the case is closed. |
| FandWay M2 / M2.5 / M3 button-head kit (ISO 7380) | ✓ The case takes M3 × 12 or M3 × 16 for the bezel, M2.5 × 8 for the ring, and M2.5 × 6 or 8 for the Pi. |
| YoiYee 1 mm × 6 mm double-sided foam tape | ✓ Stick it to the retaining ring and **leave the backing film on the side facing the screen**, so it acts as a pad and the screen comes out cleanly. |
| RTL-SDR Blog **V3** dongle | ✓ Works with the standard driver, so run `setup-pi.sh --with-receiver` without `--rtlsdr-v4`. |
| Bingfu 1090 MHz magnetic antenna (SMA male, 3 m lead) | ✓ Fits the V3's SMA socket directly. The magnetic base works best on a metal surface: a biscuit-tin lid on the window sill makes a good ground plane. |
| **Missing: short USB extension, ~30 cm, USB-A male → female** | The dongle is too long to plug straight into the Pi inside the case. Use the extension and stick the dongle to the box floor with a strip of the foam tape. [Amazon.ie search](https://www.amazon.ie/s?k=Kenable+USB+2.0+extension+30cm) (~€4) |

### Antenna lead out of the case

The back of the box (and the puck) has a **13 mm antenna port** beside the 16 mm power hole, closed by the printed `antenna_grommet`:

1. From inside the case, push the antenna's SMA plug out through the port. Connect it to the dongle inside.
2. Click the cable sideways into the grommet's slit. It's sized for a 3.2 mm lead; change `coax_d` if yours differs.
3. Press the grommet into the port from outside until the barb snaps behind the wall. It holds the cable and closes the hole.

## Shopping list (Amazon.ie, checked November 2026)

Prices are approximate and Amazon listings change often, so check each one before ordering. Ireland uses the same Type G plug as the UK, so "UK plug" power supplies are correct.

| # | Item | Link | Approx. |
|---|---|---|---|
| 1 | **Waveshare 5″ HDMI round capacitive touch display, 1080×1080** | [amazon.ie/dp/B0C14CZ2GG](https://www.amazon.ie/dp/B0C14CZ2GG) | €165–176 |
| 2 | **Raspberry Pi 5 (4 GB)** | [amazon.ie/dp/B0CK3L9WD3](https://www.amazon.ie/dp/B0CK3L9WD3) | €160–165 |
| 3 | Raspberry Pi 5 power supply, 27 W, UK plug | [amazon.ie/dp/B0F8B4QHLJ](https://www.amazon.ie/dp/B0F8B4QHLJ) | ~€15 |
| 4 | SanDisk Extreme 32 GB microSD (A1) | [amazon.ie/dp/B06XYTDCC5](https://www.amazon.ie/dp/B06XYTDCC5) | ~€13 |
| 5 | Micro-HDMI to HDMI cable, 30 cm (Silkland) | [search "Silkland micro HDMI 30cm"](https://www.amazon.ie/s?k=Silkland+micro+HDMI+to+HDMI+30cm) | ~€10 |
| 6 | Raspberry Pi 5 Active Cooler (the case is enclosed) | [search](https://www.amazon.ie/s?k=raspberry+pi+5+active+cooler) | ~€8 |
| 7 | Screws: 4 × **M3 × 16 button head** + 8 × **M2.5 × 6–8** (see *Hardware for the case*). The 874-piece kit covers the M2.5; get M3 × 16 button heads separately. | [M2.5 kit B0DRSKGTH3](https://www.amazon.ie/dp/B0DRSKGTH3) · [search M3×16 button head](https://www.amazon.ie/s?k=M3+x+16+button+head+screw) | ~€15 |
| 8 | **1 mm thick, 5 mm wide, single-sided** black EVA or neoprene foam tape (about 0.5 m used) | [search](https://www.amazon.ie/s?k=foam+tape+1mm+thick+5mm+wide+single+sided) | ~€6 |
| *Optional receiver* | | | |
| 9 | RTL-SDR Blog V4 dongle | [amazon.ie/dp/B0CD745394](https://www.amazon.ie/dp/B0CD745394) | ~€55 |
| 10 | Bingfu 1090 MHz magnetic antenna (SMA, 3 m lead) | [amazon.ie/dp/B07ZH5FJBW](https://www.amazon.ie/dp/B07ZH5FJBW) | ~€15 |

The total is about €390 without the receiver, or €460 with it.

- **Cheaper Pi:** Amazon.ie prices for the Pi are well above the official price. A Pi 5 bought from an approved Raspberry Pi reseller (several ship to Ireland) typically costs around half as much.
- **Smaller, cheaper screen:** the Waveshare 3.4″ HDMI round touch display (800×800, around €107 on Amazon.ie) also works, but it's harder to read from across a desk. You would need to measure it and set the case dimensions yourself.
- **Screw kit:** the 874-piece kit has M2.5 × 6/8 for the Pi and the retaining ring, but no M3 longer than 12 mm. M3 × 12 would only bite about 3 mm into the box, so get M3 × 16 button-head screws separately.

### Case files for this screen

`case/stl/waveshare-5in-round/` holds STLs already sized for the 5″ Waveshare round display. They use the dimensions Waveshare publishes: 150 mm round panel, 127.6 mm visible area, 7 mm deep, with 50 mm of space behind for the Pi and cables. The outer size is 178 mm, which fits a 220 mm print bed.

The published drawing doesn't show where the HDMI and USB-C sockets on the back of the panel sit. When the screen arrives, check that its connectors fit inside the 144 mm opening of the retaining ring and that the plugs have room behind. Increase `depth` if they don't.

## Parts list

| Part | Recommendation | Approx. cost |
|---|---|---|
| **Computer** | Raspberry Pi 4 (2 GB) or Raspberry Pi 5 (2 GB). A Zero 2 W works, but Chromium is slow on it and struggles with a high-resolution screen. | €45–70 |
| **Screen** | A **round, capacitive-touch** display about **4–5″** across. Smaller is hard to read across a desk. See *Choosing the screen* below. | €60–120 |
| **Storage** | 32 GB microSD card (A1/A2 rated) | €10 |
| **Power** | The official Raspberry Pi USB-C supply for your Pi (27 W for a Pi 5, 15 W for a Pi 4) | €10–15 |
| **Cables** | Whatever the screen needs: usually a short, flexible HDMI (or a DSI ribbon) plus a USB cable for touch. A right-angle USB-C power lead keeps the back tidy. | €10 |
| **Screws** | See *Hardware for the case* below | €5 |
| **Optional: receiver** | RTL-SDR Blog V4 dongle (or FlightAware Pro Stick Plus, which has a 1090 MHz filter built in) and a 1090 MHz antenna by a window. It picks up low traffic the online networks miss, and works with no internet. | €40–70 |

### Choosing the screen

Round display models change often, so check these points rather than buying a specific part number:

1. **Capacitive touch.** It's needed to tap planes and use the buttons. Resistive touch screens feel poor.
2. **Works with your Pi and Raspberry Pi OS Bookworm**, with a current driver or setup guide from the maker. HDMI + USB-touch screens are the most plug-and-play. DSI screens need the right ribbon cable, and the Pi 5 uses a smaller DSI connector than the Pi 4.
3. **Resolution of at least 480×480.** 720×720 or 1080×1080 makes the labels crisp. The page scales to any size.
4. **A mechanical drawing.** You need the glass diameter, the visible-area diameter, the thickness, and the size of any driver board behind the glass to set up the case.

Good places to look: Waveshare's round HDMI and DSI touch displays, which come in several sizes from about 2.8″ to 5″. Pimoroni's HyperPixel 2.1 Round Touch (480×480) also works, but it's small and covers the Pi's GPIO pins.

## Controls

Everything works by touch. A keyboard also works, for setting up.

| Action | Touch | Keyboard |
|---|---|---|
| Zoom in / out (5, 10, 20, 40, 80 nm) | **+** / **−** buttons at the sides | `+` / `-` |
| See a flight's details | Tap the plane | `Enter` opens the nearest one |
| Change location | Pin button (bottom-left), then tap a place | `L` |
| Add or edit a place | ⚙ button (bottom-right), or **Add a place…** in the places list | `S` |
| Close a panel | Tap outside it, or × | `Esc` |

The flight details card shows:
- the callsign, operator and route (e.g. DUB → JFK)
- the aircraft type and registration
- live altitude, speed, track, climb rate, distance and squawk
- a **photo of that exact aircraft** from planespotters.net, with the photographer credited

If there's no photo, a drawn outline of the aircraft type is shown instead: four-engine widebody, twin widebody, narrowbody, regional jet, turboprop, business jet, light aircraft or helicopter. The card closes itself after a minute.

## Case

`case/overhead_radar_case.scad` is a parametric OpenSCAD design with two styles. Ready-made STLs are in `case/stl/`, but **they use placeholder display measurements** for a ~5″ panel (136 mm glass, 126 mm visible area, 6 mm thick). Check them against your screen first.

| Style | Parts | Look |
|---|---|---|
| **Instrument** | `instrument_bezel`, `instrument_box`, `instrument_stand`, `retaining_ring` | A square bezel with four corner screws, like a cockpit instrument. The box leans back 15° in a separate desk stand. |
| **Puck** | `puck_bezel`, `puck_body`, `retaining_ring` | A round housing with a flat cut underneath, so it leans back 15° on the desk by itself. |

### Making the STLs for your screen

1. Install [OpenSCAD](https://openscad.org) and open `case/overhead_radar_case.scad`.
2. Open the Customizer (Window → Customizer) and set the **Display** values from your screen's drawing:
   - `disp_d`: glass diameter
   - `view_d`: visible area
   - `disp_t`: glass + panel thickness
3. Increase `depth` if the screen has tall connectors on the back.
4. Pick each **part**, press F6, then File → Export → STL.

To export a part from a terminal:

```bash
openscad -D 'part="puck_body"' -D 'disp_d=100' -D 'view_d=92' -o puck_body.stl overhead_radar_case.scad
```

Check the fit before printing everything. Print `retaining_ring` first, then the bezel at the same settings, and test the glass in the pocket.

### Printing

- **PETG** or **PLA**, 0.2 mm layers, 3 walls, 15–20 % infill, **no supports**. Every part is exported in its print orientation.
- Bezels print face-down. A matte or textured sheet gives a nice front finish.
- The puck body prints back-down. The flat underside is the angled face.
- The holes for the power cable (14 mm) and an SMA antenna socket (6.6 mm) are in the back. Set `sma_hole=false` if you don't use a receiver.

### Hardware for the case

| Screws | Where |
|---|---|
| 4 × **M3 × 12 or M3 × 16, button head** (ISO 7380), or 3 for the puck | Bezel into the box or body. The heads sit in 4 mm recesses, so 12 mm screws grip 5.5 mm and 16 mm screws grip 9.5 mm of the box's 2.6 mm pilot holes. For stronger threads, set `screw_pilot = 4.0` and fit M3 × 5 heat-set inserts. |
| 4 × **M2.5 × 8** (any head) | Retaining ring into the back of the bezel. They pass the 2.5 mm ring and bite 5.5 mm into the bezel; the pilot holes stop 0.8 mm short of the front, so nothing comes through. |
| 4 × **M2.5 × 6 or × 8** | Raspberry Pi onto the 7 mm standoffs, whose pilot holes run their full height. |
| **1 mm × 5 mm single-sided foam tape**, about 0.5 m | Stick it to the retaining ring, not the screen, so the screen comes out cleanly. The ring overlaps the back edge of the screen by 3 mm (its opening is 144 mm), so 5 mm tape covers it with a little to trim. The bezel pocket is 8 mm deep: 7 mm for the panel plus 1 mm for the foam. |

### Assembly

1. Put the screen face-down into the bezel pocket. Stick foam tape around its back edge, then screw the retaining ring on. Tighten gently and evenly; the glass only needs to be held, not squeezed.
2. Screw the Pi to the standoffs in the box. Connect the screen's video and touch cables, and feed the power cable through the back hole.
3. Close the bezel onto the box with the corner screws. Then sit it in the stand (instrument) or straight on the desk (puck).

If your screen has a square driver board bigger than the glass, the retaining ring won't fit over it. In that case, increase `margin` and `depth`, and screw the board to the box instead.
