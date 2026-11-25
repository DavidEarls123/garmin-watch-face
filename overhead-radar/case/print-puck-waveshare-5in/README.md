# Puck case: print these

For the Waveshare 5″ round screen, Raspberry Pi 5 and RTL-SDR dongle. These are the only files the puck style needs. All are exported in print orientation.

| File | Qty | Lay it on the bed | Approx. size (mm) |
|---|---|---|---|
| `puck_bezel.stl` | 1 | Face-down (as exported) | 178 × 172 × 10.5 |
| `puck_body.stl` | 1 | Back-down (as exported) | 178 × 169 × 52.4 |
| `puck_retaining_ring.stl` | 1 | Flat (as exported) | 164 × 159 × 2.5 |
| `antenna_grommet.stl` | 2 (one spare) | Flange down (as exported) | 18 × 18 × 5.4 |

**Settings:** PETG or PLA, 0.2 mm layers, 3 walls, 15–20 % infill, no supports. The bezel and body need a bed of at least 180 × 180 mm.

**Print order:**
1. Print the retaining ring and the bezel first.
2. Check that the screen drops into the bezel pocket and that the ring's screw holes line up.
3. Then print the body, which is the long print.

Use `puck_retaining_ring.stl`, not the plain `retaining_ring.stl`; the puck ring is trimmed to clear the flat underside.

**You'll also need:** 3 × M3 × 12 or × 16 button-head screws (bezel to body), 4 × M2.5 × 8 (ring), 4 × M2.5 × 6 or × 8 (Pi), and 6 mm foam tape. Assembly steps are in [../../ASSEMBLY.md](../../ASSEMBLY.md).

These are copies of the files in `../stl/waveshare-5in-round/`. If the case design changes, regenerate them from `../overhead_radar_case.scad`.
