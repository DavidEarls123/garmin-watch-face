# Building the Overhead Radar

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
| 7 | M2 / M2.5 / M3 screw kit (874 pcs, 6–12 mm) | [amazon.ie/dp/B0DRSKGTH3](https://www.amazon.ie/dp/B0DRSKGTH3) | ~€11 |
| 8 | 1 mm double-sided foam tape | [search](https://www.amazon.ie/s?k=1mm+foam+tape+double+sided) | ~€6 |
| *Optional receiver* | | | |
| 9 | RTL-SDR Blog V4 dongle | [amazon.ie/dp/B0CD745394](https://www.amazon.ie/dp/B0CD745394) | ~€55 |
| 10 | Bingfu 1090 MHz magnetic antenna (SMA, 3 m lead) | [amazon.ie/dp/B07ZH5FJBW](https://www.amazon.ie/dp/B07ZH5FJBW) | ~€15 |

The total is about €390 without the receiver, or €460 with it.

- **Cheaper Pi:** Amazon.ie prices for the Pi are well above the official price. A Pi 5 bought from an approved Raspberry Pi reseller (several ship to Ireland) typically costs around half as much.
- **Smaller, cheaper screen:** the Waveshare 3.4″ HDMI round touch display (800×800, around €107 on Amazon.ie) also works, but it's harder to read from across a desk. You would need to measure it and set the case dimensions yourself.
- **Screw kit:** it has countersunk heads only up to 12 mm. The bezel needs M3 × 16, so either buy a few M3 × 16 cap screws separately, or set `lip_t`/`margin` so M3 × 12 is long enough (the screw needs about 6 mm of thread in the box).

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
| 4 × M3 × 16 (instrument) or 3 × M3 × 16 (puck) | Bezel into the box or body. Self-tapping into the printed pilot holes, or set `screw_pilot = 4.0` and use M3 heat-set inserts. |
| 4 × M2.5 × 8 | Retaining ring into the back of the bezel, clamping the screen |
| 4 × M2.5 × 6 | Raspberry Pi onto the standoffs |
| 1 mm foam tape | A ring on the back of the screen where the retaining ring presses |

### Assembly

1. Put the screen face-down into the bezel pocket. Stick foam tape around its back edge, then screw the retaining ring on. Tighten gently and evenly; the glass only needs to be held, not squeezed.
2. Screw the Pi to the standoffs in the box. Connect the screen's video and touch cables, and feed the power cable through the back hole.
3. Close the bezel onto the box with the corner screws. Then sit it in the stand (instrument) or straight on the desk (puck).

If your screen has a square driver board bigger than the glass, the retaining ring won't fit over it. In that case, increase `margin` and `depth`, and screw the board to the box instead.
