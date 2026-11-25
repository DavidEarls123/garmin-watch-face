include <../overhead_radar_case.scad>
style = "instrument";
which = "bezel";
module W() {
    if (style == "instrument") instrument_world() children();
    else translate([0, 0, -z_cut]) rotate([a_lean, 0, 0]) children();
}
module pi_dummy() {
    translate([0, 0, -depth + standoff_h]) {
        translate([-32.5, -28, 0]) cube([85, 56, 1.6]);
        translate([-10, -20, 1.6]) cube([40, 40, 9]);
    }
}
port_x = style == "instrument" ? 34 : 32;
port_y = style == "instrument" ? -(S / 2 - 22) : -(R - 44);
if (which == "bezel") W() { if (style == "instrument") instrument_bezel(); else puck_bezel(); }
if (which == "body") W() { if (style == "instrument") instrument_box(); else puck_body(); }
if (which == "ring") W() { if (style == "instrument") translate([0, 0, -ring_t]) retaining_ring(); else puck_retaining_ring(); }
if (which == "screen") W() translate([0, 0, pad_t]) cylinder(d = disp_d, h = disp_t - 0.3);
if (which == "glass") W() translate([0, 0, pad_t + disp_t - 0.3]) cylinder(d = view_d, h = 0.3);
if (which == "pi") W() pi_dummy();
if (which == "grommet") W() translate([port_x, port_y, -box_h - 1.6]) antenna_grommet();
if (which == "stand" && style == "instrument") stand_with_slot();
