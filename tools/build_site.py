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
.corridor.status-normal { border-left-color: var(--state-normal); }
.corridor.status-unverified { border-left-color: var(--state-unverified); }
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

CONSOLE_CSS = """
.panels { display: grid; grid-template-columns: 1fr; gap: var(--space-05); }
.panel { border: 1px solid var(--border-subtle); background: var(--bg-layer);
  padding: var(--space-04); }
.panel h2 { margin: 0 0 var(--space-03); font-size: 1.05rem; }
.panel .stat { font-family: var(--font-mono); font-size: 1.6rem;
  font-weight: 600; }
.panel-head { display: flex; justify-content: space-between; gap: var(--space-03);
  align-items: baseline; flex-wrap: wrap; }
#clock { color: var(--text-secondary); font-family: var(--font-mono);
  font-size: 0.85rem; }
"""

CONSOLE_NOTE = (
    "Live view of public catalogs, not a warning surface: the USGS catalog "
    "itself lags events by minutes to tens of minutes, and the station panel "
    "shows registered metadata — existence, not live health. Every panel "
    "carries its data age; a frozen panel goes purple, never quietly stale.")


def render_console(corridors, lakes, console_js, tokens_css, generated):
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>{SITE_TITLE} — operations console</title>
<style>{tokens_css}{PAGE_CSS}{CONSOLE_CSS}</style>
</head>
<body>
<main>
<div class="panel-head"><h1>{SITE_TITLE} — operations console <small>v0</small></h1>
<span id="clock"></span></div>
<p class="tagline">{CONSOLE_NOTE} <a href="../">Workbench (works without
JavaScript)</a>.</p>
<div class="notice">This is a workbench, not a warning system. Nothing on
this page can warn anyone of anything. For live hazard information contact
Nepal's Department of Hydrology and Meteorology or your local authority.</div>
<noscript><div class="notice offline-hero">⊘ The console needs JavaScript
for live polling. Use the <a href="../">workbench page</a> instead — it
works without it.</div></noscript>
<div class="panels">
<section class="panel"><div class="panel-head">
<h2>Live seismicity — Himalaya arc, last 48 h (M≥2.0)</h2>
<span id="feed-chip" class="chip chip-offline">⊘ CONNECTING…</span></div>
<p><span class="stat" id="event-count">–</span> catalogued events ·
polled every 60 s from the USGS FDSN service</p>
<div class="scroll" id="chart"></div>
<div class="scroll"><table>
<thead><tr><th>Time (UTC)</th><th class=num>Mag</th>
<th class=num>Depth km</th><th>Region (USGS text)</th></tr></thead>
<tbody id="events-body"><tr><td colspan="4">Waiting for first poll…</td></tr></tbody>
</table></div></section>
<section class="panel"><div class="panel-head">
<h2>Seismic stations registered in the box</h2>
<span id="station-chip" class="chip chip-offline">⊘ CONNECTING…</span></div>
<p><span class="stat" id="station-count">–</span> stations in FDSN metadata
(lat {BBOX["minlatitude"]}–{BBOX["maxlatitude"]}, lon {BBOX["minlongitude"]}–{BBOX["maxlongitude"]}).
Sparse-network reality check for
<a href="{REPO_URL}/issues/1">issue #1</a>.</p>
<div class="scroll"><table>
<thead><tr><th>Net</th><th>Station</th><th class=num>Lat, Lon</th><th>Name</th></tr></thead>
<tbody id="stations-body"><tr><td colspan="4">Waiting…</td></tr></tbody>
</table></div></section>
<section class="panel"><h2>Corridor watch</h2>{status_board(corridors)}</section>
<section class="panel"><h2>Glacial-lake watch</h2>{status_board(lakes)}</section>
</div>
<footer>
<p>Console generated {generated.strftime("%d %b %Y %H:%M UTC")}; the data on
it is fetched live by your browser from earthquake.usgs.gov and
service.iris.edu — no other host is contacted. Boards are baked from the
repository's provenance-stamped data. <a href="{REPO_URL}">{REPO_URL}</a></p>
</footer>
</main>
<script>{console_js}</script>
</body></html>"""


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


def status_board(items):
    """Shared renderer for corridor and lake watch boards. Unknown statuses
    render as OFFLINE — absence must be loud, never green or blank."""
    glyphs = {"normal": ("●", "NORMAL", "chip-live"),
              "offline": ("⊘", "OFFLINE", "chip-offline"),
              "unverified": ("✱", "UNVERIFIED", "chip-unverified")}
    out = []
    for c in items:
        glyph, word, cls = glyphs.get(c["status"], ("⊘", "OFFLINE", "chip-offline"))
        status_cls = c["status"] if c["status"] in glyphs else "offline"
        out.append(
            '<div class="corridor status-' + status_cls + '"><strong>{}</strong> '
            '<span class="chip {}">{} {}</span>'
            '<p class="note">{} <em>(source: {}, {})</em></p></div>'.format(
                html.escape(c["name"]), cls, glyph, word,
                html.escape(c["note"]), html.escape(c["source"]),
                html.escape(c["retrieved"])))
    return "".join(out)


def render_page(events, corridors, lakes, tokens_css, generated, live):
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
{status_board(corridors)}
<h2>Glacial-lake watch</h2>
{status_board(lakes)}
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
<p>The <a href="console/">operations console</a> shows the same picture
live (polls public catalogs every minute; needs JavaScript; this page
doesn't).</p>
<p>Everything about this project — data provenance rules, decision records,
the five gates — is public: <a href="{REPO_URL}">{REPO_URL}</a>.
The <a href="events/2026-08-26-rasuwa/">26 August Rasuwa event record</a>
is press-derived and
<span class="chip chip-unverified">✱ UNVERIFIED</span>.</p>
<p>Machine-readable: <a href="api/meta.json">api/meta.json</a> ·
<a href="api/events.json">api/events.json</a> ·
<a href="api/corridors.json">api/corridors.json</a> ·
<a href="api/lakes.json">api/lakes.json</a> ·
<a href="feed.xml">Atom feed</a> — every payload carries the same
disclaimer and provenance rules as this page.</p>
<p>Contributions route through the maintainer, Bhaskar
(<a href="mailto:8h45k4r@gmail.com">8h45k4r@gmail.com</a>).</p>
</footer>
</main>
{STALE_SCRIPT}
</body></html>"""


DISCLAIMER = ("This is a workbench, not a warning system. Nothing in this "
              "data can warn anyone of anything. Figures marked unverified "
              "are press-derived and presumed wrong in detail; null means "
              "deliberately not guessed.")


def write_api(out, events, corridors, lakes, generated, live):
    """Static, versionless JSON 'API' — same honesty rules, machine-readable."""
    api = out / "api"
    api.mkdir(parents=True, exist_ok=True)
    gen = generated.strftime("%Y-%m-%dT%H:%M:%SZ")
    def dump(name, payload):
        payload = {"generated": gen, "disclaimer": DISCLAIMER, **payload}
        (api / name).write_text(json.dumps(payload, indent=1), "utf-8")
    dump("meta.json", {"feed": "live" if live else "offline",
                       "window_days": WINDOW_DAYS, "min_magnitude": MIN_MAG,
                       "bbox": BBOX, "source": "USGS FDSN automated catalog",
                       "events_in_window": len(events)})
    dump("events.json", {"status": "catalog-automated",
                         "source": "USGS FDSN automated catalog",
                         "events": [{"time": e["time"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                                     "mag": e["mag"], "depth_km": e["depth_km"],
                                     "place": e["place"]} for e in events]})
    dump("corridors.json", {"corridors": corridors})
    dump("lakes.json", {"lakes": lakes})


def write_feed(out, events, generated, live):
    """Atom feed of catalogued events; valid-but-empty when offline."""
    gen = generated.strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = []
    for e in (sorted(events, key=lambda e: e["time"], reverse=True)[:25] if live else []):
        t = e["time"].strftime("%Y-%m-%dT%H:%M:%SZ")
        entries.append(
            "<entry><id>urn:himalayashield:evt:{}</id>"
            "<title>M{:.1f} — {}</title><updated>{}</updated>"
            "<content type=\"text\">USGS automated catalog entry. {}</content>"
            "</entry>".format(int(e["time"].timestamp()), e["mag"],
                              html.escape(e["place"]), t,
                              html.escape(DISCLAIMER)))
    (out / "feed.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        "<id>urn:himalayashield:feed</id>"
        "<title>Himalayashield — catalogued seismicity, Himalaya arc</title>"
        f"<subtitle>{html.escape(DISCLAIMER)}"
        f"{'' if live else ' FEED OFFLINE at build time.'}</subtitle>"
        f"<updated>{gen}</updated>"
        f"<link href=\"{REPO_URL}\"/>"
        f"<author><name>Himalayashield workbench</name></author>"
        + "".join(entries) + "</feed>", "utf-8")


def _provenance_rows(node, path=""):
    """Flatten an event record into (label, leaf) rows, preserving order."""
    rows = []
    for key, val in node.items():
        label = (path + " · " + key if path else key).replace("_", " ")
        if isinstance(val, dict):
            if "status" in val or "value" in val:
                rows.append((label, val))
            else:
                rows.extend(_provenance_rows(val, label))
    return rows


def damage_section(damage):
    if damage is None:
        return ""
    rows = []
    for c in damage.get("categories", []):
        rows.append(
            "<tr><td>{}</td><td>{}</td>"
            '<td><span class="chip chip-unverified">✱ UNVERIFIED</span></td>'
            "<td>{} — {}{}</td></tr>".format(
                html.escape(c["metric"]), html.escape(str(c["value"])),
                html.escape(c.get("source_class", "")),
                html.escape(c.get("source", "")),
                html.escape((" · " + c["note"]) if c.get("note") else "")))
    mapping = damage.get("authoritative_mapping", {})
    map_line = ""
    if mapping:
        map_line = ('<p>Authoritative EO mapping: <a href="{}">{}</a>.</p>'.format(
            html.escape(mapping.get("source", "")),
            html.escape(str(mapping.get("value", "")))))
    return f"""
<h2>Damage register</h2>
{map_line}
<div class="scroll"><table>
<caption>Per docs/DAMAGE.md: this register collects and attributes public
figures; it generates none of its own, and unverified figures are never
summed into totals. EO counts cover mapped areas of interest only.</caption>
<thead><tr><th>Category</th><th>Reported figure</th><th>Status</th>
<th>Source class — source / note</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>"""


def render_event_page(record, tokens_css, generated, damage=None):
    chips = {"unverified": '<span class="chip chip-unverified">✱ UNVERIFIED</span>',
             "verified": '<span class="chip chip-live">✓ VERIFIED</span>',
             "null": '<span class="chip chip-offline">∅ NULL — not guessed</span>'}
    rows = []
    for label, leaf in _provenance_rows(record):
        if not isinstance(leaf, dict):
            continue
        value = leaf.get("value")
        status = leaf.get("status", "unverified")
        if value is None and "value" in leaf:
            status = "null"
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(label),
                html.escape("null" if value is None else str(value)),
                chips.get(status, chips["unverified"]),
                html.escape(str(leaf.get("source", "")) +
                            ((" — " + str(leaf["note"])) if leaf.get("note") else ""))))
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>{html.escape(record.get("name", record["id"]))} — event record</title>
<style>{tokens_css}{PAGE_CSS}
/* provenance table: the status chip and source must be visible, so wrap */
td:nth-child(2), td:nth-child(4) {{ white-space: normal; }}
td .chip {{ white-space: nowrap; }}</style></head>
<body>
<main>
<h1>{html.escape(record.get("name", record["id"]))}</h1>
<p class="tagline">Event record <code>{html.escape(record["id"])}</code> ·
record status <span class="chip chip-unverified">✱ {html.escape(record.get("record_status", "unverified").upper())}</span>
· created {html.escape(record.get("record_created", "?"))}</p>
<div class="notice">This is a workbench, not a warning system. Every figure
below carries its provenance; unverified means press-derived and presumed
wrong in detail; null means deliberately not guessed.</div>
<p>{html.escape(record.get("summary", ""))}</p>
<h2>Figures and provenance</h2>
<div class="scroll"><table>
<caption>Promotion from unverified to verified is custodian-signed
(GOVERNANCE.md); the custodian role is currently vacant.</caption>
<thead><tr><th>Field</th><th>Value</th><th>Status</th><th>Source / note</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
{damage_section(damage)}
<footer><p>Generated {generated.strftime("%d %b %Y %H:%M UTC")} ·
<a href="../../">workbench</a> · <a href="{REPO_URL}">{REPO_URL}</a></p></footer>
</main></body></html>"""


NOT_FOUND = """<h1>404 — this path is not watched</h1>
<p>Nothing exists here, and in this project an absence must be loud:</p>
<p><span class="chip chip-offline">⊘ OFFLINE — no such page</span></p>
<p>Try the <a href="/Himalayashield/">workbench</a>, the
<a href="/Himalayashield/console/">operations console</a>, or the
<a href="https://github.com/8h45k4r/Himalayashield">repository</a>.</p>"""


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
    lakes = json.loads((ROOT / "data" / "lakes.json").read_text("utf-8"))["lakes"]
    page = render_page(events, corridors, lakes, tokens_css, now, live)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    index = out / "index.html"
    index.write_text(page, "utf-8")
    shutil.copy(ROOT / "web" / "_headers", out / "_headers")

    console_js = (ROOT / "web" / "console.js").read_text("utf-8")
    console_dir = out / "console"
    console_dir.mkdir(parents=True, exist_ok=True)
    (console_dir / "index.html").write_text(
        render_console(corridors, lakes, console_js, tokens_css, now), "utf-8")

    write_api(out, events, corridors, lakes, now, live)
    write_feed(out, events, now, live)
    damage_by_event = {}
    damage_dir = ROOT / "data" / "damage"
    if damage_dir.is_dir():
        for f in sorted(damage_dir.glob("*.json")):
            d = json.loads(f.read_text("utf-8"))
            damage_by_event[d["event_id"]] = d
    (out / "api" / "damage.json").write_text(json.dumps(
        {"generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "disclaimer": DISCLAIMER,
         "methodology": "docs/DAMAGE.md — figures are collected and "
                        "attributed, never generated or summed",
         "events": damage_by_event}, indent=1), "utf-8")
    for ev_file in sorted((ROOT / "data" / "events").glob("*.json")):
        record = json.loads(ev_file.read_text("utf-8"))
        ev_dir = out / "events" / record["id"]
        ev_dir.mkdir(parents=True, exist_ok=True)
        (ev_dir / "index.html").write_text(
            render_event_page(record, tokens_css, now,
                              damage_by_event.get(record["id"])), "utf-8")
    (out / "404.html").write_text(
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>404 — not watched</title><style>" + tokens_css + PAGE_CSS +
        "</style></head><body><main>" + NOT_FOUND + "</main></body></html>", "utf-8")

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
