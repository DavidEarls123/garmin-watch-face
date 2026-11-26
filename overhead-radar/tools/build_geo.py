"""Crop/simplify OSM-derived land & lakes GeoJSON to a bbox and write geo.js for the radar.

Usage:
    npm pack @geo-maps/earth-lands-100m @geo-maps/earth-lakes-100m   # then untar both
    python3 build_geo.py lands/package/map.geo.json lakes/package/map.geo.json ../geo.js

Change W, S, E, N below to cover a different area.
"""
import json, math, sys
lands_path, lakes_path, out_path = sys.argv[1:4]
LODS = [  # (use up to this range in nm, simplify tolerance in degrees, min lake km2, min island km2, decimals)
    (25, 0.0005, 0.4, 0.02, 4),
    (1e9, 0.0025, 6.0, 0.3, 3),
]
W, S, E, N = -12.0, 50.3, -3.0, 56.8
TOL = 0.0025        # degrees, Douglas-Peucker tolerance (~200 m)
MIN_LAKE_KM2 = 6.0   # smaller lakes (and lake holes in the land) are dropped to keep the map calm
MIN_ISLAND_KM2 = 0.3
EPS = 1e-9

def rings_of(geom):
    """Yield (ring, is_hole)."""
    polys = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates'] if geom['type'] == 'MultiPolygon' else []
    for poly in polys:
        for i, ring in enumerate(poly):
            yield ring, i > 0

def clip(ring):
    def inside(p, edge):
        x, y = p
        return {'W': x >= W, 'E': x <= E, 'S': y >= S, 'N': y <= N}[edge]
    def inter(a, b, edge):
        (x1, y1), (x2, y2) = a, b
        if edge in 'WE':
            x = W if edge == 'W' else E
            t = (x - x1) / (x2 - x1)
            return (x, y1 + t * (y2 - y1))
        y = S if edge == 'S' else N
        t = (y - y1) / (y2 - y1)
        return (x1 + t * (x2 - x1), y)
    pts = [tuple(p[:2]) for p in ring]
    for edge in 'WESN':
        if not pts: break
        out = []
        for i, cur in enumerate(pts):
            prev = pts[i - 1]
            if inside(cur, edge):
                if not inside(prev, edge): out.append(inter(prev, cur, edge))
                out.append(cur)
            elif inside(prev, edge):
                out.append(inter(prev, cur, edge))
        pts = out
    return pts

def dp(pts, tol):
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1e-12
        best, idx = -1, None
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L
            if d > best: best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True; stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]

def area_km2(pts):
    lat0 = math.radians(sum(p[1] for p in pts) / len(pts))
    a = 0
    for i in range(len(pts)):
        x1, y1 = pts[i - 1]; x2, y2 = pts[i]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2 * 111.32 ** 2 * math.cos(lat0)

def on_edge(p):
    x, y = p
    return abs(x - W) < EPS or abs(x - E) < EPS or abs(y - S) < EPS or abs(y - N) < EPS

DEC = 3
def flat(pts):
    return [v for p in pts for v in (round(p[0], DEC), round(p[1], DEC))]

def process(path, min_km2, min_hole_km2):
    fills, strokes = [], []
    d = json.load(open(path))
    geoms = [f['geometry'] for f in d['features']] if 'features' in d else d.get('geometries', [d])
    for g in geoms:
        for ring, hole in rings_of(g):
            xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
            if max(xs) < W or min(xs) > E or max(ys) < S or min(ys) > N: continue
            c = clip(ring)
            if len(c) < 3: continue
            # simplify, but split at bbox-edge points so the cut lines stay exact
            m = len(c) // 2
            s = dp(c[:m + 1], TOL)[:-1] + dp(c[m:] + [c[0]], TOL)[:-1]
            if len(s) < 3 or area_km2(s) < (min_hole_km2 if hole else min_km2): continue
            fills.append(flat(s))
            if hole: continue  # lake holes are filled but not stroked as coastline
            # coastline strokes: skip segments lying along the bbox edge
            cur = []
            for i in range(len(s) + 1):
                p = s[i % len(s)]
                if cur and on_edge(cur[-1]) and on_edge(p):
                    if len(cur) > 1: strokes.append(flat(cur))
                    cur = []
                cur.append(p)
            if len(cur) > 1: strokes.append(flat(cur))
    return fills, strokes

lands_data = json.load(open(lands_path)); lakes_data = json.load(open(lakes_path))
_load = json.load
json.load = lambda fh, _cache={lands_path: lands_data, lakes_path: lakes_data}: _cache[fh.name]
lods = []
for max_range, tol, min_lake, min_island, dec in LODS:
    TOL, DEC = tol, dec
    land, coast = process(lands_path, min_island, min_lake)
    lakes, _ = process(lakes_path, min_lake, min_lake)
    lods.append({'maxRange': max_range if max_range < 1e8 else None, 'land': land, 'coast': coast, 'lakes': lakes})
    pts = lambda arr: sum(len(r) // 2 for r in arr)
    print(f'LOD <= {max_range} nm: land pts {pts(land)}, lakes {len(lakes)} ({pts(lakes)} pts)')
json.load = _load
geo = {'attribution': '© OpenStreetMap contributors (ODbL)', 'bbox': [W, S, E, N], 'lods': lods}
with open(out_path, 'w') as fh:
    fh.write('// Generated by build_geo.py from OpenStreetMap-derived land and lake outlines (@geo-maps, 100 m).\n')
    fh.write('// Map data © OpenStreetMap contributors, available under the Open Database License (ODbL).\n')
    fh.write('window.RADAR_GEO = ' + json.dumps(geo, separators=(',', ':')) + ';\n')

