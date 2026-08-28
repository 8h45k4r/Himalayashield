# Functional plan — from workbench to working monitor

This is the concrete path from "a repo of documents" to "a functioning,
publicly visible monitoring workbench", on free tools only, with zero servers
and zero secrets. It does not change the project's one hard truth: **nothing
here warns anyone** until issue #1 has its answer and the gates below are
passed. What it does change: the workbench becomes *live* — real data,
rebuilt on a schedule, published where anyone can inspect it.

## Architecture: static everything, compute at build time

```
                (free, no keys, no servers)
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions (cron every 6h + on push + manual)           │
│                                                             │
│  tools/build_site.py                                        │
│    ├── USGS FDSN event API  ── seismicity, Himalaya bbox    │
│    ├── data/corridors.json  ── corridor watch states (ours) │
│    ├── data/events/*.json   ── event records (ours)         │
│    └── web/tokens.css       ── single source of design truth│
│            │                                                │
│            ▼                                                │
│  _site/index.html  (one file, <50 KB, inline SVG, JS-off OK)│
└───────────────┬─────────────────────────────────────────────┘
                ▼
        GitHub Pages  →  https://8h45k4r.github.io/Himalayashield/
```

The page is **computed at build time, dumb at runtime**. All fetching,
scaling, and chart drawing happens in Python inside the Action; the browser
receives finished HTML+SVG. That is what makes a 2G, JS-off, old-handset
budget achievable, and it means an API outage can never make the page lie —
a failed fetch builds the page in its `OFFLINE` state instead.

### Offline semantics (the South Lhonak rule, executable)

- Feed fetch fails at build → the page is generated with a loud OFFLINE
  banner and no charts. Never stale data dressed as fresh.
- Every page carries its build timestamp in plain text. A tiny inline script
  (progressive enhancement, <1 KB) flags the page as stale if it is older
  than 26 h (cron is 6 h, so >4 missed builds); with JS off, printed text
  tells the reader to check the timestamp themselves.
- A corridor with no monitoring renders as `OFFLINE ⊘` — never as blank,
  never as green.

## Free-tools inventory

| Need | Tool | Cost / limit |
|---|---|---|
| Hosting | GitHub Pages | free for public repos |
| Compute / cron | GitHub Actions | free & unlimited minutes for public repos |
| Seismicity | USGS FDSN event API | free, no key, no auth |
| Weather / precipitation (later) | Open-Meteo API | free, no key, non-commercial |
| Terrain / corridor profiles (issue #4) | Copernicus GLO-30 DEM via OpenTopography | free, key is free-tier |
| Bridges, settlements (issue #4) | OpenStreetMap Overpass API | free |
| Glacial-lake inventories (later) | ICIMOD / NASA Earthdata portals | free |
| Static code security | GitHub CodeQL | free for public repos |
| Secret scanning | GitHub secret scanning + push protection | free for public repos |
| Dependency alerts | Dependabot | free |
| Type/typeface | IBM Plex system-fallback stack | free (no CDN fetch — budget) |

Deliberately **no** paid or key-holding services in the critical path: the
pipeline must be forkable by anyone with a GitHub account, and there are no
secrets to leak (VAPT gate, threat 1).

## Phases and exit criteria

**Phase 0 — done.** Repo, governance, ADRs 0001–0004, tokens, CI, issues.

**Phase 1 — live workbench (this push).**
`build_site.py` + Pages deployment + 6-hourly cron. Seismicity chart for the
Himalaya box from the USGS catalog, corridor status board (truthfully all
OFFLINE), event table, offline semantics as above. Exit: page live on
github.io, rebuilt on schedule, all five gates documented and wired into CI
and the PR template.

**Phase 2 — verified event layer.** Blocked on issues #2/#3. The custodian
signs the Rasuwa record; the page renders verified vs unverified with the
`✱ UNVERIFIED` badge; retrospective drafting begins. Exit: zero unverified
figures rendered without their badge; first tagged release `v0.2.0`.

**Phase 3 — corridor inventory rendered.** Blocked on issue #4. OSM/DEM
derived corridor profile (distances, settlements, bridges) replaces the
nulls; the corridor board gains real geography. Exit: no `null` a mapped
source could fill; corridor page under the same 50 KB budget.

**Phase 4 — detection experiments.** Blocked on issue #1's answer being YES.
Offline (non-real-time) replay of the 26 August seismic signal against the
proposed discriminator, published as notebooks + a results page. **Real-time
anything stays out of scope** until a partner institution (DHM) owns the
operational side — a GitHub cron is a workbench, not a siren.

## What this is not

A 6-hour cron on a free CI runner, reading a teleseismic catalog with
minutes-to-hours latency, cannot warn anyone of anything and never will. The
functional system this plan builds is a **transparency and analysis
instrument** — the warning capability, if it ever exists, runs on
infrastructure owned by an operational agency, informed by what is proven
here. That boundary is stated on the page itself.
