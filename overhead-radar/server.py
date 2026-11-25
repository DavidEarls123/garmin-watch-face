#!/usr/bin/env python3
"""Overhead Radar server.

Serves index.html and a small, normalised JSON feed of nearby aircraft at
/api/aircraft, so the page never has to deal with API keys, CORS or the
different formats of each data source.

Sources:
  adsblol       https://api.adsb.lol          (free, no key, community ADS-B network)
  airplaneslive https://api.airplanes.live    (free, no key, ~1 request/second limit)
  readsb        your own receiver (RTL-SDR dongle + readsb/dump1090/tar1090)

Only the Python standard library is used.
"""

import argparse
import functools
import json
import threading
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
USER_AGENT = "overhead-radar/1.0 (+desktop display)"

SOURCES = {
    "adsblol": "https://api.adsb.lol/v2/point/{lat}/{lon}/{radius}",
    "airplaneslive": "https://api.airplanes.live/v2/point/{lat}/{lon}/{radius}",
    "readsb": None,  # uses --readsb-url
}


def normalise(ac):
    """Map one readsb-style record (also used by adsb.lol and airplanes.live) to the page's format."""
    lat, lon = ac.get("lat"), ac.get("lon")
    if lat is None or lon is None:
        return None
    alt = ac.get("alt_baro", ac.get("alt_geom"))
    ground = alt == "ground"
    return {
        "hex": ac.get("hex", "").lower(),
        "flight": (ac.get("flight") or "").strip(),
        "reg": ac.get("r") or "",
        "type": ac.get("t") or "",
        "lat": lat,
        "lon": lon,
        "alt": None if ground or not isinstance(alt, (int, float)) else int(alt),
        "ground": ground,
        "gs": ac.get("gs"),
        "track": ac.get("track", ac.get("true_heading")),
        "vr": ac.get("baro_rate", ac.get("geom_rate")) or 0,
        "squawk": ac.get("squawk") or "",
        "seen": ac.get("seen_pos", ac.get("seen", 0)) or 0,
    }


class Feed:
    """Fetches upstream at most once per `interval` seconds and caches the result."""

    def __init__(self, args):
        self.args = args
        self.lock = threading.Lock()
        self.cached = None
        self.fetched_at = 0.0

    def url(self):
        if self.args.source == "readsb":
            return self.args.readsb_url
        return SOURCES[self.args.source].format(lat=self.args.lat, lon=self.args.lon, radius=self.args.radius)

    def get(self):
        with self.lock:
            if self.cached and time.time() - self.fetched_at < self.args.interval:
                return self.cached
            req = urllib.request.Request(self.url(), headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = json.load(r)
            records = raw.get("ac") or raw.get("aircraft") or []
            aircraft = [a for a in (normalise(x) for x in records) if a]
            # readsb data has a timestamp; age positions from that moment.
            fetch_lag = max(0.0, time.time() - raw["now"]) if isinstance(raw.get("now"), (int, float)) and raw["now"] < 1e11 else 0.0
            for a in aircraft:
                a["seen"] = round(a["seen"] + fetch_lag, 1)
            self.cached = {"source": self.args.source, "now": time.time(), "aircraft": aircraft}
            self.fetched_at = time.time()
            return self.cached


class Handler(SimpleHTTPRequestHandler):
    feed = None
    args = None

    def log_message(self, fmt, *a):  # keep the console quiet apart from errors
        if self.args.verbose:
            super().log_message(fmt, *a)

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/config":
            return self.send_json({"name": self.args.name, "lat": self.args.lat, "lon": self.args.lon,
                                   "poll_seconds": self.args.interval, "source": self.args.source})
        if path == "/api/aircraft":
            try:
                return self.send_json(self.feed.get())
            except Exception as e:  # upstream down, network error, bad JSON…
                self.log_error("feed error: %s", e)
                return self.send_json({"error": str(e)}, 502)
        if path not in ("/", "/index.html"):
            self.send_error(404)
            return
        return super().do_GET()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=SOURCES, default="adsblol")
    ap.add_argument("--lat", type=float, default=53.2707, help="centre latitude (default: Galway)")
    ap.add_argument("--lon", type=float, default=-9.0568, help="centre longitude (default: Galway)")
    ap.add_argument("--name", default="Galway", help="label shown on screen")
    ap.add_argument("--radius", type=int, default=100, help="search radius in nm for online sources (max 250)")
    ap.add_argument("--interval", type=float, default=5, help="seconds between upstream fetches")
    ap.add_argument("--readsb-url", default="http://localhost:8080/data/aircraft.json")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    Handler.args = args
    Handler.feed = Feed(args)
    server = ThreadingHTTPServer((args.host, args.port), functools.partial(Handler, directory=str(HERE)))
    print(f"Overhead Radar on http://{args.host}:{args.port}  source={args.source}  centre={args.lat},{args.lon}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
