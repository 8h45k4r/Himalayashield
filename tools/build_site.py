#!/usr/bin/env python3
"""Build the Himalayashield public workbench page.

Computes everything at build time (fetch, scaling, SVG) so the shipped page
is one file under ADR 0002's Tier 2 budget: < 50 KB, no external requests,
fully readable with JavaScript off. A failed fetch builds the OFFLINE page —
never a stale or partial page presented as live (the South Lhonak rule).

Stdlib only, keyless by design (Gate 2/Gate 5). Run: python3 tools/build_site.py
"""

import argparse
import html
import json
import math
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDGET_BYTES = 51200
WINDOW_DAYS = 60
MAX_PLOTTED = 120
TABLE_ROWS = 12
STALE_HOURS = 26  # cron is 6-hourly; >4 missed builds means something is wrong

# Himalaya arc around the Rasuwa corridor (deg)
BBOX = {"minlatitude": 26.0, "maxlatitude": 31.5,
        "minlongitude": 78.0, "maxlongitude": 90.5}
MIN_MAG = 2.5
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
RASUWA_COLLAPSE_UTC = "2026-08-26"

SITE_TITLE = "Himalayashield"
REPO_URL = "https://github.com/8h45k4r/Himalayashield"

PAGE_CSS = """
* { box-sizing: border-box; margin: 0; }
body { background: var(--bg); color: var(--text-primary);
  font-family: var(--font-sans); line-height: 1.5; font-size: 1rem; }
main { max-width: 60rem; margin: 0 auto; padding: var(--space-05); }
a { color: var(--link); }
h1 { font-size: 1.6rem; margin-bottom: var(--space-02); }
h2 { font-size: 1.15rem; margin: var(--space-07) 0 var(--space-03); }
p { margin-bottom: var(--space-03); }
.tagline { color: var(--text-secondary); }
.notice { border: 2px solid var(--text-primary); padding: var(--space-04);
  margin: var(--space-05) 0; font-weight: 600; }
.chip { display: inline-block; padding: 0.1rem 0.55rem; border-radius: 1rem;
  font-weight: 700; font-size: 0.85rem; border: 1.5px solid currentColor;
  white-space: nowrap; }
.chip-live { color: var(--state-normal); }
.chip-offline { color: var(--state-offline); background: var(--state-offline-bg); }
.chip-unverified { color: var(--state-unverified); }
.corridor { border: 1px solid var(--border-subtle); border-left: 6px solid
  var(--state-offline); padding: var(--space-04); margin: var(--space-03) 0;
  background: var(--bg-layer); }
.corridor .note { color: var(--text-secondary); font-size: 0.9rem; }
.offline-hero { border: 2px solid var(--state-offline);
  background: var(--state-offline-bg); padding: var(--space-05);
  margin: var(--space-05) 0; }
figure { margin: var(--space-04) 0; }
.scroll { overflow-x: auto; }
figcaption, .meta { color: var(--text-secondary); font-size: 0.85rem;
  margin-top: var(--space-02); }
table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
caption { text-align: left; color: var(--text-secondary); font-size: 0.85rem;
  margin-bottom: var(--space-02); }
th, td { text-align: left; padding: 0.35rem 0.6rem;
  border-bottom: 1px solid var(--border-subtle); white-space: nowrap; }
th { color: var(--text-secondary); font-weight: 600; }
td.num, th.num { text-align: right; font-family: var(--font-mono); }
footer { margin: var(--space-08) 0 var(--space-05);
  border-top: 1px solid var(--border-subtle); padding-top: var(--space-04);
  color: var(--text-secondary); font-size: 0.9rem; }
#stale-banner { display: none; }
body.stale #stale-banner { display: block; }
svg text { font-family: var(--font-sans); }
"""

STALE_SCRIPT = (
    '<script>(function(){try{var g=document.body.getAttribute("data-generated");'
    'if(g&&Date.now()-Date.parse(g)>%d*3600*1000){document.body.className+=" stale";}'
    '}catch(e){}})();</script>' % STALE_HOURS
)


def fetch_usgs(now):
    start = (now - timedelta(days=WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%S")
    params = {"format": "geojson", "starttime": start, "orderby": "time",
              "minmagnitude": MIN_MAG, **BBOX}
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(USGS_URL + "?" + qs,
                                 headers={"User-Agent": "himalayashield-build"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_events(geojson):
    """Untrusted upstream input: parse strictly, escape at render."""
    events = []
    for feat in geojson.get("features", []):
        props = feat.get("properties") or {}
        geom = (feat.get("geometry") or {}).get("coordinates") or [None, None, None]
        mag, time_ms = props.get("mag"), props.get("time")
        if mag is None or time_ms is None:
            continue
        events.append({
            "time": datetime.fromtimestamp(float(time_ms) / 1000, tz=timezone.utc),
            "mag": float(mag),
            "depth_km": float(geom[2]) if len(geom) > 2 and geom[2] is not None else None,
            "place": str(props.get("place") or "unknown location"),
        })
    events.sort(key=lambda e: e["time"])
    return events


def _x(t, start, end, w, pad):
    return pad + (t - start) / (end - start) * (w - 2 * pad)


def _y(mag, lo, hi, h, pad):
    return h - pad - (mag - lo) / (hi - lo) * (h - 2 * pad)


def svg_timeline(events, now):
    """Magnitude-over-time dot timeline, single accent hue, inline SVG."""
    w, h, pad = 720, 260, 40
    end, start = now.timestamp(), (now - timedelta(days=WINDOW_DAYS)).timestamp()
    lo = 2.0
    hi = max(5.0, math.ceil(max((e["mag"] for e in events), default=4.0)) + 0.5)
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" width="{w}" '
             f'aria-label="Magnitude of catalogued events over the last '
             f'{WINDOW_DAYS} days">']
    # horizontal grid at integer magnitudes
    m = int(math.ceil(lo))
    while m <= hi:
        y = round(_y(m, lo, hi, h, pad), 1)
        parts.append(f'<line x1="{pad}" y1="{y}" x2="{w - pad}" y2="{y}" '
                     'stroke="var(--border-subtle)" stroke-width="1"/>')
        parts.append(f'<text x="{pad - 8}" y="{y + 4}" text-anchor="end" '
                     f'font-size="11" fill="var(--text-secondary)">M{m}</text>')
        m += 1
    # date ticks every 15 days
    for d in range(0, WINDOW_DAYS + 1, 15):
        t = start + d * 86400
        x = round(_x(t, start, end, w, pad), 1)
        label = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%d %b")
        parts.append(f'<line x1="{x}" y1="{h - pad}" x2="{x}" y2="{h - pad + 5}" '
                     'stroke="var(--text-secondary)" stroke-width="1"/>')
        parts.append(f'<text x="{x}" y="{h - pad + 18}" text-anchor="middle" '
                     f'font-size="11" fill="var(--text-secondary)">{label}</text>')
    # 26 Aug reference line
    ref = datetime.strptime(RASUWA_COLLAPSE_UTC, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    if start <= ref <= end:
        x = round(_x(ref, start, end, w, pad), 1)
        parts.append(f'<line x1="{x}" y1="{pad - 10}" x2="{x}" y2="{h - pad}" '
                     'stroke="var(--text-primary)" stroke-width="1" '
                     'stroke-dasharray="4 3"/>')
        parts.append(f'<text x="{x + 5}" y="{pad}" font-size="11" '
                     'fill="var(--text-primary)">26 Aug collapse</text>')
    # marks: thin rings + fill, single hue; native tooltips via <title>
    biggest = max(events, key=lambda e: e["mag"], default=None)
    for e in events[-MAX_PLOTTED:]:
        x = round(_x(e["time"].timestamp(), start, end, w, pad), 1)
        y = round(_y(e["mag"], lo, hi, h, pad), 1)
        r = round(2.5 + (e["mag"] - lo) * 1.4, 1)
        tip = html.escape(f'M{e["mag"]:.1f} — {e["place"]} — '
                          f'{e["time"].strftime("%d %b %Y %H:%M UTC")}')
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--link)" '
                     'fill-opacity="0.55" stroke="var(--bg)" stroke-width="2">'
                     f'<title>{tip}</title></circle>')
    if biggest is not None:  # selective direct label: the maximum only
        x = round(_x(biggest["time"].timestamp(), start, end, w, pad), 1)
        y = round(_y(biggest["mag"], lo, hi, h, pad), 1)
        anchor, dx = ("end", -10) if x > w / 2 else ("start", 10)
        parts.append(f'<text x="{x + dx}" y="{y - 8}" text-anchor="{anchor}" '
                     f'font-size="12" font-weight="600" '
                     f'fill="var(--text-primary)">M{biggest["mag"]:.1f}</text>')
    parts.append("</svg>")
    return "".join(parts)


def events_table(events):
    rows = []
    for e in sorted(events, key=lambda e: e["time"], reverse=True)[:TABLE_ROWS]:
        depth = f'{e["depth_km"]:.0f}' if e["depth_km"] is not None else "—"
        rows.append(
            "<tr><td>{}</td><td class=num>{:.1f}</td><td class=num>{}</td>"
            "<td>{}</td></tr>".format(
                e["time"].strftime("%d %b %Y %H:%M"), e["mag"], depth,
                html.escape(e["place"])))
    return (
        '<div class="scroll"><table>'
        "<caption>Latest catalogued events (of {} in window). Source: USGS "
        "FDSN automated catalog — subject to revision by USGS; not reviewed "
        "by this project.</caption>"
        "<thead><tr><th>Time (UTC)</th><th class=num>Mag</th>"
        "<th class=num>Depth km</th><th>Region (USGS text)</th></tr></thead>"
        "<tbody>{}</tbody></table></div>".format(len(events), "".join(rows)))


def corridor_board(corridors):
    glyphs = {"normal": ("●", "NORMAL", "chip-live"),
              "offline": ("⊘", "OFFLINE", "chip-offline")}
    out = []
    for c in corridors:
        glyph, word, cls = glyphs.get(c["status"], ("⊘", "OFFLINE", "chip-offline"))
        out.append(
            '<div class="corridor"><strong>{}</strong> '
            '<span class="chip {}">{} {}</span>'
            '<p class="note">{} <em>(source: {}, {})</em></p></div>'.format(
                html.escape(c["name"]), cls, glyph, word,
                html.escape(c["note"]), html.escape(c["source"]),
                html.escape(c["retrieved"])))
    return "".join(out)


def render_page(events, corridors, tokens_css, generated, live):
    gen_str = generated.strftime("%d %b %Y %H:%M UTC")
    feed_chip = ('<span class="chip chip-live">● FEED LIVE</span>' if live else
                 '<span class="chip chip-offline">⊘ FEED OFFLINE</span>')
    if live:
        data_section = f"""
<h2>Seismicity — Himalaya arc, last {WINDOW_DAYS} days</h2>
<figure><div class="scroll">{svg_timeline(events, generated)}</div>
<figcaption>Catalogued events M≥{MIN_MAG}, lat {BBOX["minlatitude"]}–{BBOX["maxlatitude"]},
lon {BBOX["minlongitude"]}–{BBOX["maxlongitude"]}. Dot size and height both encode
magnitude. Teleseismic catalog latency is minutes to hours — this view can
never warn anyone; see the notice above. Exact values in the table.</figcaption>
</figure>
{events_table(events)}"""
    else:
        data_section = """
<div class="offline-hero"><span class="chip chip-offline">⊘ OFFLINE</span>
<p><strong>The data feed could not be reached when this page was built.</strong>
No charts are shown because no fresh data exists. This state is loud on
purpose: an absent feed must never look like a quiet mountain.</p></div>"""

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>{SITE_TITLE} — workbench</title>
<style>{tokens_css}{PAGE_CSS}</style>
</head>
<body data-generated="{generated.strftime("%Y-%m-%dT%H:%M:%SZ")}">
<main>
<h1>{SITE_TITLE}</h1>
<p class="tagline">An open workbench toward honest glacial-hazard monitoring
in Himalayan river corridors. {feed_chip}</p>
<div class="notice">This is a workbench, not a warning system. Nothing on
this page can warn anyone of anything. For live hazard information contact
Nepal's Department of Hydrology and Meteorology or your local authority.</div>
<div class="notice offline-hero" id="stale-banner">⊘ This page is more than
{STALE_HOURS} hours old — its build pipeline has stopped. Treat everything
below as OFFLINE.</div>
<h2>Corridor watch status</h2>
{corridor_board(corridors)}
<p class="meta">States: <span class="chip chip-live">● NORMAL</span>
<span class="chip">▲ WATCH</span> <span class="chip">◆ WARNING</span>
<span class="chip">■ DANGER</span>
<span class="chip chip-offline">⊘ OFFLINE</span>
<span class="chip chip-unverified">✱ UNVERIFIED</span> — every state always
carries its word and shape; colour never means anything alone.</p>
{data_section}
<footer>
<p>Generated {gen_str}. Rebuilt every 6 hours; if the timestamp is much
older, treat this page as OFFLINE (with JavaScript on, it flags itself).</p>
<p>Everything about this project — data provenance rules, decision records,
the five gates — is public: <a href="{REPO_URL}">{REPO_URL}</a>.
The 26 August Rasuwa event record it holds is press-derived and
<span class="chip chip-unverified">✱ UNVERIFIED</span>.</p>
<p>Contributions route through the maintainer, Bhaskar
(<a href="mailto:8h45k4r@gmail.com">8h45k4r@gmail.com</a>).</p>
</footer>
</main>
{STALE_SCRIPT}
</body></html>"""


def build(out_dir, fixture=None, force_offline=False, now=None):
    now = now or datetime.now(timezone.utc).replace(microsecond=0)
    live, events = False, []
    if not force_offline:
        try:
            if fixture is not None:
                geojson = json.loads(Path(fixture).read_text("utf-8"))
            else:
                geojson = fetch_usgs(now)
            events = parse_events(geojson)
            live = True
        except Exception as exc:  # any failure → the OFFLINE page, loudly
            print(f"feed unavailable, building OFFLINE page: {exc}", file=sys.stderr)
    tokens_css = (ROOT / "web" / "tokens.css").read_text("utf-8")
    corridors = json.loads((ROOT / "data" / "corridors.json").read_text("utf-8"))["corridors"]
    page = render_page(events, corridors, tokens_css, now, live)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    index = out / "index.html"
    index.write_text(page, "utf-8")
    shutil.copy(ROOT / "web" / "_headers", out / "_headers")

    size = index.stat().st_size
    if size > BUDGET_BYTES:
        print(f"FAIL: {index} is {size} bytes (> {BUDGET_BYTES})", file=sys.stderr)
        return 1
    print(f"built {index}: {size} bytes ({'live' if live else 'OFFLINE'}), "
          f"{len(events)} events")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "_site"))
    ap.add_argument("--input", help="fixture GeoJSON file instead of the network")
    ap.add_argument("--force-offline", action="store_true",
                    help="build the OFFLINE page without touching the network")
    args = ap.parse_args(argv)
    epoch = os.environ.get("SOURCE_DATE_EPOCH")  # deterministic builds in tests
    now = (datetime.fromtimestamp(int(epoch), tz=timezone.utc) if epoch else None)
    return build(args.out, fixture=args.input,
                 force_offline=args.force_offline, now=now)


if __name__ == "__main__":
    sys.exit(main())
