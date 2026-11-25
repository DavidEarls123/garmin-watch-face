// Overhead Radar – parametric cases for a round display + Raspberry Pi
//
// Two styles:
//   "instrument" – a square aircraft-instrument bezel with corner screws, a back box and a desk stand
//   "puck"       – a round housing with a flat underside that leans back on the desk
//
// Both clamp the display between the front bezel and a printed retaining ring.
//
// 1. Measure your display (or read its drawing) and set the values under [Display].
// 2. Pick a part, press F6 (render), then File > Export > STL.
//    Or from a terminal:  openscad -D 'part="instrument_bezel"' -o bezel.stl overhead_radar_case.scad
//
// Parts are exported in print orientation. The defaults are a placeholder for a ~5" round panel:
// CHECK THEM AGAINST YOUR SCREEN BEFORE PRINTING.

/* [Part] */
part = "preview_instrument"; // [preview_instrument, preview_puck, instrument_bezel, instrument_box, instrument_stand, puck_bezel, puck_body, retaining_ring]

/* [Display] */
disp_d = 136;     // outer diameter of the glass / panel (mm)
disp_t = 6;       // thickness of the glass + panel that sits in the bezel pocket
view_d = 126;     // diameter of the visible screen area (the window)
pad_t = 1;        // foam tape between the display and the retaining ring
tol = 0.4;        // printing clearance

/* [Case] */
wall = 2.4;       // wall thickness
margin = 14;      // bezel width around the glass
depth = 45;       // free depth behind the display for the Pi and cables
tilt = 15;        // how far the screen leans back from vertical (degrees)
corner_r = 9;     // instrument bezel corner radius
lip_t = 2.5;      // bezel lip in front of the glass
ring_t = 2.5;     // retaining ring thickness
ring_lip = 3;     // how far the ring overlaps the back of the display

/* [Raspberry Pi] */
pi_holes = [58, 49];   // Pi 3/4/5 mounting-hole pattern (M2.5)
standoff_h = 6;
standoff_d = 6.5;
standoff_pilot = 2.2;  // for M2.5 self-tapping screws (use 3.5 for M2.5 heat-set inserts)

/* [Screws] */
screw_clear = 3.4;     // M3 clearance hole in the bezel
screw_head = 6.4;      // M3 head counterbore
screw_pilot = 2.6;     // M3 self-tapping pilot (4.0 for M3 heat-set inserts)
ring_screw_pilot = 2.2; // M2.5 into the bezel for the retaining ring
ring_screw_clear = 2.9;

/* [Openings] */
power_hole_d = 14;     // USB-C cable with its plug fed through
sma_hole = true;       // hole for an SMA bulkhead (ADS-B antenna)
sma_d = 6.6;

$fn = 120;

// ---------- derived ----------
pocket = disp_t + pad_t;           // glass pocket depth in the bezel
bezel_h = lip_t + pocket;
S = disp_d + 2 * margin;           // instrument square size / puck diameter
R = S / 2;
ring_screw_r = disp_d / 2 + 4;     // retaining-ring screws, between glass and box wall
ring_od = 2 * (ring_screw_r + 3.2);
box_h = depth + wall;              // back box / puck body height (behind the bezel)
corner_c = S / 2 - 7;              // instrument corner screws
E = 0.01;

// ---------- helpers ----------
module rsq(s, r, h) { linear_extrude(h) offset(r) square(s - 2 * r, center = true); }

module pi_standoffs(z0) {
    for (x = [-1, 1], y = [-1, 1])
        translate([x * pi_holes[0] / 2, y * pi_holes[1] / 2, z0])
            difference() {
                cylinder(d = standoff_d, h = standoff_h);
                translate([0, 0, 1]) cylinder(d = standoff_pilot, h = standoff_h);
            }
}

module vent_slots(z0, y0) {
    for (i = [-3:3]) translate([i * 9, y0, z0]) hull() {
        translate([0, -18, 0]) cylinder(d = 4, h = wall + 2, $fn = 24);
        translate([0, 18, 0]) cylinder(d = 4, h = wall + 2, $fn = 24);
    }
}

// Glass pocket, window with a 45° bevel, and pilot holes for the retaining ring (bezel frame: back at z=0, front at z=bezel_h)
module bezel_cuts() {
    translate([0, 0, -1]) cylinder(d = disp_d + 2 * tol, h = pocket + 1);
    translate([0, 0, -1]) cylinder(d = view_d, h = bezel_h + 2);
    translate([0, 0, pocket - E]) cylinder(d1 = view_d, d2 = view_d + 2 * lip_t, h = lip_t + 2 * E);
    for (a = [45:90:359]) rotate(a) translate([ring_screw_r, 0, -1]) cylinder(d = ring_screw_pilot, h = bezel_h - 0.8 + 1, $fn = 24);
}

// ---------- retaining ring (shared) ----------
module retaining_ring() {
    difference() {
        cylinder(d = ring_od, h = ring_t);
        translate([0, 0, -1]) cylinder(d = disp_d - 2 * ring_lip, h = ring_t + 2);
        for (a = [45:90:359]) rotate(a) translate([ring_screw_r, 0, -1]) cylinder(d = ring_screw_clear, h = ring_t + 2, $fn = 24);
    }
}

// ---------- instrument style ----------
module instrument_bezel() {
    difference() {
        rsq(S, corner_r, bezel_h);
        bezel_cuts();
        for (x = [-1, 1], y = [-1, 1]) translate([x * corner_c, y * corner_c, 0]) {
            translate([0, 0, -1]) cylinder(d = screw_clear, h = bezel_h + 2, $fn = 32);
            translate([0, 0, bezel_h - 1.8]) cylinder(d = screw_head, h = 2, $fn = 32);
        }
        // fine groove around the window, like an instrument's inner bezel
        translate([0, 0, bezel_h - 0.6]) difference() {
            cylinder(d = view_d + 2 * lip_t + 5, h = 1);
            cylinder(d = view_d + 2 * lip_t + 3.4, h = 1);
        }
    }
}

// back box: z from -box_h (back) to 0 (meets the bezel)
module instrument_box() {
    difference() {
        union() {
            difference() {
                translate([0, 0, -box_h]) rsq(S, corner_r, box_h);
                translate([0, 0, -depth]) rsq(S - 2 * wall, max(corner_r - wall, 1), depth + 1);
            }
            for (x = [-1, 1], y = [-1, 1]) translate([x * corner_c, y * corner_c, -depth - E]) cylinder(d = 8, h = depth + E, $fn = 40);
            pi_standoffs(-depth);
        }
        for (x = [-1, 1], y = [-1, 1]) translate([x * corner_c, y * corner_c, -depth + 4]) cylinder(d = screw_pilot, h = depth, $fn = 24);
        // back: power cable, antenna, vents
        translate([0, -(S / 2 - 22), -box_h - 1]) cylinder(d = power_hole_d, h = wall + 2);
        if (sma_hole) translate([30, -(S / 2 - 22), -box_h - 1]) cylinder(d = sma_d, h = wall + 2, $fn = 32);
        vent_slots(-box_h - 1, S / 2 - 38);
    }
}

// desk stand: holds the bezel+box assembly leaning back by `tilt`
module instrument_stand() {
    T = box_h + bezel_h;               // front-to-back thickness of the assembly
    w = S * 0.72;
    lip_h = 7; lip_w = 5; pt = 5; hgt = S * 0.55; base_t = 4;
    y0 = T * cos(2 * tilt) / cos(tilt); // where the leaning back face meets the desk
    translate([-w / 2, 0, 0]) rotate([90, 0, 90]) linear_extrude(w) difference() {
        union() {
            translate([-lip_w, -base_t]) square([y0 + pt + 30 + lip_w, base_t]);             // base
            translate([-lip_w, 0]) square([lip_w, lip_h]);                                     // front lip
            polygon([[y0, 0], [y0 + hgt * sin(tilt), hgt * cos(tilt)],
                     [y0 + hgt * sin(tilt) + pt, hgt * cos(tilt)], [y0 + pt, 0]]);             // back rest
        }
    }
    // side gussets
    for (sx = [-1, 1]) translate([sx * (w / 2 - 3) - 3, 0, 0]) rotate([90, 0, 90]) linear_extrude(6)
        polygon([[y0 + pt - E, 0], [y0 + pt + 30, 0], [y0 + hgt * 0.6 * sin(tilt) + pt - E, hgt * 0.6 * cos(tilt)]]);
}

module stand_with_slot() {
    T = box_h + bezel_h;
    y0 = T * cos(2 * tilt) / cos(tilt);
    difference() {
        instrument_stand();
        // cable slot up the back rest
        translate([-12, y0 - 5, -1]) cube([24, 20, 42]);
    }
}

// ---------- puck style ----------
// The puck leans back on a flat cut into its underside. The cut is defined in the desk frame
// and mapped into the part frame (front face +z, screen "up" +y).
a_lean = 90 - tilt;
z_cut = -R * sin(a_lean) + bezel_h * cos(a_lean) + 6; // flat is 6 mm deep at the front

module desk_cut() {
    rotate([-a_lean, 0, 0]) translate([-500, -500, z_cut - 1000]) cube(1000);
}

module puck_bezel() {
    difference() {
        cylinder(d = S, h = bezel_h);
        bezel_cuts();
        for (a = [0, 120, 240]) rotate(a + 90) translate([R - 3, 0, 0]) {
            translate([0, 0, -1]) cylinder(d = screw_clear, h = bezel_h + 2, $fn = 32);
            translate([0, 0, bezel_h - 1.8]) cylinder(d = screw_head, h = 2, $fn = 32);
        }
        desk_cut();
    }
}

// body: z from -box_h (back) to 0
module puck_body() {
    difference() {
        union() {
            difference() {
                translate([0, 0, -box_h]) cylinder(d = S, h = box_h);
                translate([0, 0, -depth]) cylinder(d = S - 2 * wall, h = depth + 1);
            }
            for (a = [0, 120, 240]) rotate(a + 90) translate([R - 3, 0, -depth - E]) cylinder(d = 6.5, h = depth + E, $fn = 40);
            pi_standoffs(-depth);
            // floor under the cut, so the flat is closed
            intersection() {
                translate([0, 0, -box_h]) cylinder(d = S, h = box_h);
                rotate([-a_lean, 0, 0]) translate([-500, -500, z_cut]) cube([1000, 1000, wall]);
            }
        }
        for (a = [0, 120, 240]) rotate(a + 90) translate([R - 3, 0, -depth + 4]) cylinder(d = screw_pilot, h = depth, $fn = 24);
        translate([0, -(R - 34), -box_h - 1]) cylinder(d = power_hole_d, h = wall + 2);
        if (sma_hole) translate([28, -(R - 34), -box_h - 1]) cylinder(d = sma_d, h = wall + 2, $fn = 32);
        vent_slots(-box_h - 1, R - 42);
        desk_cut();
    }
}

// ---------- previews ----------
module display_dummy() {
    color("#111") translate([0, 0, 0]) cylinder(d = disp_d, h = disp_t);
    color("#0b2a3a") translate([0, 0, disp_t - 0.2]) cylinder(d = view_d, h = 0.3);
}

module preview_instrument() {
    T = box_h + bezel_h;
    color("#c9ced6") stand_with_slot();
    // assembly: front-bottom edge at the stand origin, leaning back by `tilt`
    translate([0, 0, 0]) rotate([-tilt, 0, 0]) translate([0, 0, S / 2]) rotate([90, 0, 0]) translate([0, 0, -bezel_h]) {
        color("#2b2f36") instrument_bezel();
        translate([0, 0, pad_t]) display_dummy();
        color("#3a3f47") instrument_box();
    }
}

module preview_puck() {
    translate([0, 0, -z_cut]) rotate([a_lean, 0, 0]) {
        color("#2b2f36") puck_bezel();
        translate([0, 0, pad_t]) display_dummy();
        color("#3a3f47") puck_body();
    }
}

// ---------- part selection (print orientation) ----------
if (part == "preview_instrument") preview_instrument();
else if (part == "preview_puck") preview_puck();
else if (part == "instrument_bezel") translate([0, 0, bezel_h]) rotate([180, 0, 0]) instrument_bezel();
else if (part == "instrument_box") translate([0, 0, box_h]) instrument_box();
else if (part == "instrument_stand") translate([0, 0, 4]) stand_with_slot();
else if (part == "puck_bezel") translate([0, 0, bezel_h]) rotate([180, 0, 0]) puck_bezel();
else if (part == "puck_body") translate([0, 0, box_h]) puck_body();
else if (part == "retaining_ring") retaining_ring();
