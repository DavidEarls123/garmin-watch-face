#!/usr/bin/env python3
"""Overhead Radar server.

Serves index.html and a small, normalised JSON feed of nearby aircraft at
/api/aircraft, so the page never has to deal with API keys, CORS or the
different formats of each data source.

Sources:
  adsblol       https://api.adsb.lol          (free, no key, community ADS-B network)
  airplaneslive https://api.airplanes.live    (free, no key, ~1 request/second limit)
  readsb        your own receiver (RTL-SDR dongle + readsb/dump1090/tar1090)
  hybrid        your receiver merged with an online network (--online), freshest position wins

Tapping an aircraft asks /api/info, which looks up the owner and type and the route
(hexdb.io), plus a photo of that airframe (planespotters.net, credited on screen).

Only the Python standard library is used.
"""

import argparse
import concurrent.futures
import functools
import json
import re
import threading
import time
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
USER_AGENT = "overhead-radar/1.0 (+desktop display)"

SOURCES = {
    "adsblol": "https://api.adsb.lol/v2/point/{lat}/{lon}/{radius}",
    "airplaneslive": "https://api.airplanes.live/v2/point/{lat}/{lon}/{radius}",
}
SOURCE_CHOICES = list(SOURCES) + ["readsb", "hybrid"]
CALLSIGN_URLS = {
    "adsblol": "https://api.adsb.lol/v2/callsign/{cs}",
    "airplaneslive": "https://api.airplanes.live/v2/callsign/{cs}",
}
# IATA airline code -> ICAO callsign prefix, so a flight number like EI105 also finds EIN105
AIRLINES = {
    "EI": "EIN", "FR": "RYR", "BA": "BAW", "AA": "AAL", "DL": "DAL", "UA": "UAL", "AC": "ACA", "LH": "DLH", "AF": "AFR",
    "KL": "KLM", "U2": "EZY", "W6": "WZZ", "VS": "VIR", "EK": "UAE", "QR": "QTR", "EY": "ETD", "TK": "THY", "IB": "IBE",
    "VY": "VLG", "SK": "SAS", "AY": "FIN", "LX": "SWR", "OS": "AUA", "SN": "BEL", "TP": "TAP", "LS": "EXS", "LM": "LOG",
    "B6": "JBU", "WS": "WJA", "TS": "TSC", "FI": "ICE", "DY": "NOZ", "D8": "IBK", "SQ": "SIA", "CX": "CPA", "ET": "ETH",
    "AI": "AIC", "QF": "QFA", "AS": "ASA", "WN": "SWA", "EW": "EWG", "BY": "TOM", "MT": "TCX", "AZ": "ITY",
}


def callsign_candidates(query):
    q = "".join(c for c in query.upper() if c.isalnum())[:8]
    out = [q] if q else []
    m = re.match(r"^([A-Z0-9]{2})(\d{1,4}[A-Z]?)$", q)
    if m and m.group(1) in AIRLINES:
        out.insert(0, AIRLINES[m.group(1)] + (m.group(2).lstrip("0") or "0"))
    return out


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
        "category": ac.get("category") or "",
        "seen": ac.get("seen_pos", ac.get("seen", 0)) or 0,
    }


class Feed:
    """Aircraft around the centre, from an online network, your own receiver, or both ("hybrid").

    Online sources are fetched at most once per --interval seconds; the receiver at most once a second.
    In hybrid mode the two are merged per aircraft, keeping whichever position is fresher, so your
    antenna gives fast updates nearby and the network fills in what it can't hear.
    """

    def __init__(self, args):
        self.args = args
        self.lock = threading.Lock()
        self.online = {"key": None, "at": 0.0, "list": None, "error": None}
        self.local = {"at": 0.0, "list": None, "error": None}

    @staticmethod
    def _read(location):
        """Read readsb-style JSON from a URL or a local file (readsb writes /run/readsb/aircraft.json)."""
        if location.startswith(("http://", "https://")):
            req = urllib.request.Request(location, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = json.load(r)
        else:
            with open(location.removeprefix("file://"), encoding="utf-8") as fh:
                raw = json.load(fh)
        records = raw.get("ac") or raw.get("aircraft") or []
        aircraft = [a for a in (normalise(x) for x in records) if a]
        # readsb data carries its own timestamp; age positions from that moment.
        if isinstance(raw.get("now"), (int, float)) and raw["now"] < 1e11:
            lag = max(0.0, time.time() - raw["now"])
            for a in aircraft:
                a["seen"] = round(a["seen"] + lag, 1)
        return aircraft

    def _online(self, lat, lon):
        name = self.args.online if self.args.source == "hybrid" else self.args.source
        c, key = self.online, (name, lat, lon)
        if c["list"] is not None and c["key"] == key and time.time() - c["at"] < self.args.interval:
            return c["list"]
        try:
            c["list"] = self._read(SOURCES[name].format(lat=lat, lon=lon, radius=self.args.radius))
            c["error"] = None
        except Exception as e:
            c["error"] = str(e)
            if c["key"] != key or c["list"] is None:
                c["list"] = None
            if self.args.source != "hybrid":
                raise
        c["key"], c["at"] = key, time.time()
        return c["list"] or []

    def _local(self):
        c = self.local
        if c["list"] is not None and time.time() - c["at"] < 1.0:
            return c["list"]
        try:
            c["list"] = self._read(self.args.readsb_url)
            c["error"] = None
        except Exception as e:
            c["list"], c["error"] = None, str(e)
            if self.args.source == "readsb":
                raise
        c["at"] = time.time()
        return c["list"] or []

    def get(self, lat=None, lon=None):
        """lat/lon: centre chosen on the screen; defaults to --lat/--lon."""
        lat = self.args.lat if lat is None else round(lat, 3)
        lon = self.args.lon if lon is None else round(lon, 3)
        src = self.args.source
        with self.lock:
            if src == "readsb":
                aircraft = [dict(a, via="receiver") for a in self._local()]
                label = "receiver"
            elif src == "hybrid":
                local = {a["hex"]: dict(a, via="receiver") for a in self._local()}
                merged = {a["hex"]: dict(a, via="network") for a in self._online(lat, lon)}
                for hex_, a in local.items():
                    net = merged.get(hex_)
                    if net is None or a["seen"] <= net["seen"]:
                        # keep the receiver's fresher position, but borrow identity fields it may lack
                        for k in ("reg", "type", "flight", "category"):
                            if not a.get(k) and net and net.get(k):
                                a[k] = net[k]
                        merged[hex_] = a
                aircraft = list(merged.values())
                parts = []
                if self.local["error"] is None:
                    parts.append("receiver")
                if self.online["error"] is None:
                    parts.append(self.args.online)
                label = "+".join(parts) or "no feed"
                if not parts:
                    raise RuntimeError(f"receiver: {self.local['error']}; online: {self.online['error']}")
            else:
                aircraft = [dict(a, via="network") for a in self._online(lat, lon)]
                label = src
            return {"source": label, "now": time.time(), "aircraft": aircraft,
                    "receiver_count": sum(1 for a in aircraft if a.get("via") == "receiver")}


class Lookup:
    """Details for a tapped aircraft: owner/type (hexdb.io), route (hexdb.io) and a photo (planespotters.net).

    Every source is optional: if one is down or has nothing, that part is simply left out.
    Results are cached so tapping the same aircraft again costs nothing.
    """

    TTL = 6 * 3600

    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=6)

    def _get_json(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.load(r)

    def _cached(self, key, fn, ttl=TTL):
        with self.lock:
            hit = self.cache.get(key)
            if hit and time.time() - hit[0] < ttl:
                return hit[1]
        try:
            val = fn()
        except Exception:
            val = None
        with self.lock:
            self.cache[key] = (time.time(), val)
        return val

    def aircraft(self, hex_):
        def fetch():
            d = self._get_json(f"https://hexdb.io/api/v1/aircraft/{hex_}")
            if not isinstance(d, dict) or d.get("status") == "404":
                return None
            return {"registration": d.get("Registration") or "", "type_code": d.get("ICAOTypeCode") or "",
                    "manufacturer": d.get("Manufacturer") or "", "type": d.get("Type") or "",
                    "owner": d.get("RegisteredOwners") or ""}
        return self._cached(("ac", hex_), fetch)

    def airport(self, icao):
        def fetch():
            d = self._get_json(f"https://hexdb.io/api/v1/airport/icao/{icao}")
            return {"icao": icao, "iata": d.get("iata") or "", "name": d.get("airport") or icao,
                    "lat": d.get("latitude"), "lon": d.get("longitude")}
        return self._cached(("apt", icao), fetch, ttl=30 * 24 * 3600) or {"icao": icao, "iata": "", "name": icao}

    def route(self, callsign):
        def fetch():
            d = self._get_json(f"https://hexdb.io/api/v1/route/icao/{urllib.parse.quote(callsign)}")
            parts = [p for p in str(d.get("route") or "").split("-") if p]
            if len(parts) < 2:
                return None
            return {"origin": self.airport(parts[0]), "destination": self.airport(parts[-1])}
        return self._cached(("rt", callsign), fetch) if callsign else None

    def photo(self, hex_):
        def fetch():
            d = self._get_json(f"https://api.planespotters.net/pub/photos/hex/{hex_}")
            photos = d.get("photos") or []
            if not photos:
                return None
            ph = photos[0]
            src = (ph.get("thumbnail_large") or ph.get("thumbnail") or {}).get("src")
            return {"src": src, "link": ph.get("link") or "", "photographer": ph.get("photographer") or ""} if src else None
        return self._cached(("ph", hex_), fetch)

    def find_callsign(self, callsign, network, feed):
        """Where is this callsign now? Checks the radar feed first, then asks the network worldwide."""
        for lst in (feed.local.get("list"), feed.online.get("list")):
            for a in lst or []:
                if a.get("flight") == callsign:
                    return a

        def fetch():
            d = self._get_json(CALLSIGN_URLS[network].format(cs=urllib.parse.quote(callsign)))
            found = [a for a in (normalise(x) for x in (d.get("ac") or [])) if a]
            return min(found, key=lambda a: a["seen"]) if found else None
        return self._cached(("cs", callsign), fetch, ttl=10)

    def track(self, query, network, feed):
        result = {"query": query, "callsign": None, "aircraft": None, "route": None}
        for cs in callsign_candidates(query):
            ac = self.find_callsign(cs, network, feed)
            if ac:
                result["callsign"], result["aircraft"] = cs, ac
                break
        cs = result["callsign"] or (callsign_candidates(query) or [None])[0]
        if cs:
            result["route"] = self.route(cs)
        return result

    def info(self, hex_, callsign):
        f_ac = self.pool.submit(self.aircraft, hex_)
        f_rt = self.pool.submit(self.route, callsign)
        f_ph = self.pool.submit(self.photo, hex_)
        return {"hex": hex_, "callsign": callsign, "aircraft": f_ac.result(), "route": f_rt.result(), "photo": f_ph.result()}


class Handler(SimpleHTTPRequestHandler):
    lookup = None
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
        path, _, query = self.path.partition("?")
        if path == "/api/config":
            return self.send_json({"name": self.args.name, "lat": self.args.lat, "lon": self.args.lon,
                                   "poll_seconds": 2 if self.args.source in ("readsb", "hybrid") else self.args.interval,
                                   "source": self.args.source})
        if path == "/api/aircraft":
            q = urllib.parse.parse_qs(query)
            try:
                lat = float(q["lat"][0]) if "lat" in q else None
                lon = float(q["lon"][0]) if "lon" in q else None
                if (lat is not None and not -85 <= lat <= 85) or (lon is not None and not -180 <= lon <= 180):
                    raise ValueError
            except ValueError:
                return self.send_json({"error": "lat must be -85..85 and lon -180..180"}, 400)
            try:
                return self.send_json(self.feed.get(lat, lon))
            except Exception as e:  # upstream down, network error, bad JSON…
                self.log_error("feed error: %s", e)
                return self.send_json({"error": str(e)}, 502)
        if path == "/api/info":
            q = urllib.parse.parse_qs(query)
            hex_ = (q.get("hex", [""])[0]).strip().lower()
            callsign = "".join(c for c in q.get("callsign", [""])[0].upper() if c.isalnum())[:8]
            if not hex_ or not all(c in "0123456789abcdef~" for c in hex_) or len(hex_) > 7:
                return self.send_json({"error": "hex must be the aircraft's 24-bit ICAO address"}, 400)
            if self.args.no_lookups:
                return self.send_json({"hex": hex_, "callsign": callsign, "aircraft": None, "route": None, "photo": None})
            return self.send_json(self.lookup.info(hex_.lstrip("~"), callsign))
        if path == "/api/track":
            q = urllib.parse.parse_qs(query).get("flight", [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9 ]{3,10}", q or ""):
                return self.send_json({"error": "flight must be a flight number or callsign, e.g. EI105"}, 400)
            if self.args.no_lookups:
                return self.send_json({"error": "lookups are turned off (--no-lookups)"}, 503)
            network = self.args.online if self.args.source in ("readsb", "hybrid") else self.args.source
            return self.send_json(self.lookup.track(q, network, self.feed))
        if path not in ("/", "/index.html", "/geo.js"):
            self.send_error(404)
            return
        return super().do_GET()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=SOURCE_CHOICES, default="adsblol",
                    help="online network, your own receiver (readsb), or both merged (hybrid)")
    ap.add_argument("--online", choices=list(SOURCES), default="adsblol", help="network used by --source hybrid")
    ap.add_argument("--lat", type=float, default=53.2707, help="centre latitude (default: Galway)")
    ap.add_argument("--lon", type=float, default=-9.0568, help="centre longitude (default: Galway)")
    ap.add_argument("--name", default="Galway", help="label shown on screen")
    ap.add_argument("--radius", type=int, default=100, help="search radius in nm for online sources (max 250)")
    ap.add_argument("--interval", type=float, default=5, help="seconds between upstream fetches")
    ap.add_argument("--readsb-url", default="/run/readsb/aircraft.json",
                    help="readsb/dump1090 aircraft.json: a file path or an http:// URL")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-lookups", action="store_true", help="don't look up routes, owners or photos for tapped aircraft")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    Handler.args = args
    Handler.feed = Feed(args)
    Handler.lookup = Lookup()
    server = ThreadingHTTPServer((args.host, args.port), functools.partial(Handler, directory=str(HERE)))
    print(f"Overhead Radar on http://{args.host}:{args.port}  source={args.source}  centre={args.lat},{args.lon}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
