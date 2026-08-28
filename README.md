# Himalayashield

An attempt to build an honest, open early-warning capability for glacial hazards
in Himalayan river corridors — starting from the 26 August 2026 Rasuwa
(Nepal–Tibet border) disaster and the failures that preceded it.

**Live workbench:** https://himalayashield.allgetz.com ·
https://8h45k4r.github.io/Himalayashield/ — rebuilt every 6 hours from the
USGS catalog; goes loudly OFFLINE rather than quietly stale.

## Read this first

**Nothing in this repository is ready to warn anyone.** There is no sensor, no
feed, no alert channel, and no validated model here. If you are looking for
live hazard information, contact Nepal's Department of Hydrology and
Meteorology (DHM) or your local authority. This repository is a workbench, not
a warning system, and it must never be mistaken for one.

## Why this exists

On 26 August 2026 an ice–rock avalanche high on the Nepal–Tibet border sent a
wall of water, ice and debris down through Rasuwa district. The collapse was
violent enough that seismic networks initially registered it as a magnitude 4.4
earthquake; only afterwards was the signal reinterpreted as the avalanche
itself. That reinterpretation is the seed of this project: **if the collapse
wrote a readable signature into the seismic record before the flood reached
anyone, then minutes of warning existed and nobody could use them.** Whether
that signal is separable from ordinary seismicity fast enough to act on —
answered by a named seismologist, not by us — is
[issue #1](https://github.com/8h45k4r/Himalayashield/issues/1),
and everything else in this repository is downstream of that answer.

The failure mode we refuse to repeat is South Lhonak (Sikkim, October 2023):
a monitoring system reported as installed while the camera was dead and the
breach sensor had never been fitted. A system that is silently absent is worse
than no system, because it converts "we are not watching" into "nothing is
happening." That principle is load-bearing everywhere here, down to the design
tokens: `offline` is a first-class state, rendered in purple measured to sit
far outside the amber→orange→red hazard scale (ADR 0004 — the original
magenta *felt* distinct and measured nearly identical to danger red), always
with a label and a shape, never colour alone.

## Data honesty

Every number in `data/` carries provenance. As of today:

- **Casualty and damage figures are press-derived, captured inside 72 hours of
  the event, and unverified.** They will be wrong. They exist only so that the
  eventual verified figures have something to diff against.
- **Corridor distances and flood-wave travel times are null.** We do not
  publish guesses for numbers that determine whether a warning is usable.

No figure is promoted from `unverified` until the named data custodian
([issue #2](https://github.com/8h45k4r/Himalayashield/issues/2)) signs it against an official or primary source.
Until a custodian exists, nothing gets promoted.

## Plan (eight weeks)

| Weeks | Focus |
|---|---|
| 1–2 | Seismic separability question answered yes/no by a named seismologist; custodian named; verified event record |
| 3–4 | Corridor inventory (settlements, bridges, hydropower, travel times) for the Bhotekoshi/Trishuli corridor |
| 5–6 | Operations console v0 (Carbon React) and last-metre page prototype (tokens only, <50 KB, works with JS off) |
| 7–8 | Public retrospective of the 26 August event, published only after validation |

This repository is **public from day two** by the maintainer's decision
([ADR 0003](docs/decisions/0003-public-from-day-two.md)). What that does *not*
change: every figure stays stamped `unverified` or `null` until a custodian
signs it, and the project publishes no conclusions before the validated
retrospective in weeks 7–8. Reading the workbench early is welcome; citing it
as fact is not.

## Layout

- `data/` — event records with explicit provenance; see `data/README.md`
- `docs/decisions/` — architecture decision records (ADRs)
- `docs/PLAN.md` — the functional plan: architecture, free-tools stack, phases
- `docs/GATES.md` — **the five gates** (UI/UX · Code · QA/QC · Documentation ·
  VAPT) every change passes before merge
- `docs/DATAVIZ.md` — how charts are built and colours are validated
- `docs/RELEASE.md` — release & deployment (GitHub Pages + Cloudflare Workers)
- `tools/` — the build pipeline and its tests
- `web/` — design tokens and, later, the last-metre pages
- `GOVERNANCE.md` — who decides what, and what a number needs before it is real
- `CONTRIBUTING.md` — contributions route through the maintainer, Bhaskar
  (8h45k4r@gmail.com)
- `PUSH.md` — repository setup state: what is done, what still needs a human in the GitHub UI

## Design system

Carbon Design System, adopted with a hard two-tier scope split — full Carbon
React only for the desktop operations console; hand-written tokens-only HTML
for anything opened on a phone in a valley. Rationale and the non-negotiable
constraints are in [`docs/decisions/0002-design-system.md`](docs/decisions/0002-design-system.md).
