# 0005 — Console v0: live polling, dependency-free

Date: 2026-08-29
Status: accepted (narrows ADR 0002's Tier 1 for v0; Carbon React remains the
committed direction for the console once its triggers below fire)

## Context

The operations console (issue #5) becomes a live monitoring surface now:
client-side polling of the USGS FDSN APIs from a static page, SED-dashboard
style, still serverless and free. ADR 0002 assigned Tier 1 "full Carbon
React". For a v0 whose UI is four panels and a table, a React+Carbon build
pipeline adds a large dependency surface (Gate 5: every dependency is
supply chain) and days of tooling before the first live pixel.

## Decision

- **Console v0 is dependency-free**: hand-written HTML + `web/console.js`
  (vanilla, inlined at build time — no external scripts anywhere, same as
  Tier 2), styled by `web/tokens.css`. Served at `/console/` from the same
  build and deploys.
- **Realtime honesty is a hard requirement**: every live panel carries a
  data-age stamp updated every second; a panel whose data is older than
  5 minutes or whose fetch fails flips to the purple OFFLINE state. A
  frozen panel must never look live. The page states the underlying
  catalog latency (minutes to tens of minutes) — this is a live view of a
  slightly delayed catalog, not a warning surface.
- **Carbon React comes in when its value does** — any of: a second screen,
  sortable/filterable data tables, operator preferences, or a real duty-
  officer workflow. That migration keeps this ADR's honesty requirements.
- The Tier 2 rules (50 KB, JS-off) do not apply to the console; the
  workbench page remains the JS-off front door and links here.

## Consequences

- Zero new dependencies; the whole console audits in one file.
- Content-Security-Policy gains `connect-src` for exactly two hosts
  (earthquake.usgs.gov, service.iris.edu) on the Cloudflare deployment.
- Some Carbon components will be hand-approximated until migration.
