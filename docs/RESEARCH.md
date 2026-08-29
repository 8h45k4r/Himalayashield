# State of the art, and the three gaps

Landscape assessment for the seismic-detection question (issue #1). This
reframes it: the *binary* question — can mass movements be detected and
discriminated in seismic data — is answered in principle by operational
prior art. What remains open is sharper, and it is three specific holes.

## What already exists (with provenance)

| Claim | Status | Source |
|---|---|---|
| ETH Zurich's Swiss Seismological Service (SED) runs automatic avalanche/landslide/rockfall detection and keeps a mass-movement catalogue | **verified** | [SED project page](https://www.seismo.ethz.ch/en/research-and-teaching/projects/automatic-avalanche-landslide-and-rockfall-detection/), [SED mass-movement catalogue](https://www.seismo.ethz.ch/en/earthquakes/switzerland/massmovements/) |
| …on one of the densest networks on earth (~400 stations in Switzerland) | **verified** | [SED monitoring](http://www.seismo.ethz.ch/en/monitoring/measuring-earthquakes/) |
| Single-station avalanche detection with hidden Markov models is published (Hammer et al. 2017); array+ML classification runs near-real-time | **verified** | [Heck et al., ESurf 2019](https://esurf.copernicus.org/articles/7/491/2019/) and refs therein |
| ESEC — the Exotic Seismic Events Catalog of seismogenic mass movements — exists; its update doubled it from 121 to 242 events | **verified** | [ESEC at IRIS](https://ds.iris.edu/ds/products/esec/), [SRL data product](https://pubs.geoscienceworld.org/ssa/srl/article-abstract/90/3/1355/569840/Exotic-Seismic-Events-Catalog-ESEC-Data-Product), [2022 update](https://ui.adsabs.harvard.edu/abs/2022EGUGA..24.3172C/abstract) |
| A version-controlled GLOF inventory for High Mountain Asia exists | **verified** | [ESSD 2023](https://essd.copernicus.org/articles/15/3941/2023/) |
| A 2026 machine-learning landslide catalogue for the European Alps exists | *unverified — cite the paper before relying on it* | supplied in review, 2026-08-28 |
| Landslide volume can be estimated from waveform features | *unverified here; literature anchor to confirm:* Ekström & Stark 2013 (Science) and successors | supplied in review, 2026-08-28 |
| ESEC's coverage concentrates on North America, Europe and the Pacific; High Mountain Asia is under-represented | *unverified — check against the ESEC event list directly* | supplied in review, 2026-08-28 |
| HMA holds ~9.3 of the world's ~15 million GLOF-exposed people | *unverified — confirm against Taylor et al. 2023 (Nat. Commun.) before citing* | supplied in review, 2026-08-28 |

Per GOVERNANCE.md, the unverified rows are recorded so they can be checked,
not so they can be repeated. Verifying them is part of issue #1's ADR.

## The three gaps

**G1 — Sparse networks.** Switzerland's result rides on station density.
Nobody has published a method tuned for a dozen mixed-quality stations plus
citizen-grade sensors — which is what Nepal, Peru, Pakistan, Kyrgyzstan and
Tajikistan actually have. The real research question is **degradation**: how
much detection confidence survives at twelve stations instead of hundreds,
and how do you fuse a Raspberry Shake with a research broadband without the
weak sensor poisoning the result. This is what issue #1's seismologist must
now answer — not "is it separable" (in principle: yes, operationally proven
elsewhere) but "does separability survive our network, quantified".

**G2 — High Mountain Asia is missing from the labelled corpus.** Labelled
training data — not code — is the scarce asset in this field, and the
region with the most GLOF-exposed people is the one the corpora skip.
Nepal is positioned to produce those labels because the events keep
happening here. The 26 August Rasuwa waveforms (public via FDSN) are the
first entry. Tracked as issue #7.

**G3 — The science stops where the siren begins.** Everything above outputs
retrospective research catalogues. Nothing turns a detection into a
machine-readable warning with per-settlement arrival times. The bridge is:
detection → corridor model (issue #4's distances and travel times) →
CAP-format alert (Common Alerting Protocol, the OASIS standard emergency
systems already ingest) → last-metre page (issue #6). This is engineering,
not research — and it is exactly the part an operational agency (DHM) must
own, per docs/PLAN.md's boundary statement.

## The remote-sensing axis: prioritization, not detection

A second landscape review (2026-08-28) covered the AI/remote-sensing side.
The structural insight: warning operates on **two timescales**, and they are
different disciplines that must not be confused.

- **Prioritization (weeks to months):** which lakes to watch. AI on
  satellite data — deep-learning lake segmentation from Sentinel-1/2 and
  Landsat, ML susceptibility ranking, SAR/InSAR deformation of moraine dams,
  AI surrogates for inundation modelling. This axis decides where sensors,
  sirens and attention go.
- **Detection (minutes):** an event has begun. The seismic axis above
  (gaps G1–G3). No satellite revisit cadence can do this.

Himalayashield's detection work (issues #1, #7) sits on the second axis; the
first axis feeds the corridor inventory (#4) and a lake watchlist (#8).

### Verified on this axis

| Claim | Source |
|---|---|
| Tsho Rolpa: lake grew 0.23→1.53 km² over five decades; level lowered by the government in 2000 | [Wikipedia/The New Humanitarian](https://www.thenewhumanitarian.org/photo-feature/2017/01/05/global-warming-turns-heat-glacial-lake-risk-himalayas) |
| **Tsho Rolpa's early warning system is reported damaged and non-operational, in an area without reliable mobile network** — the South Lhonak pattern, live, today | [PreventionWeb reporting](https://www.preventionweb.net/news/nepal-worries-about-its-most-dangerous-glacial-lake) |
| Imja Tsho: lowered 3.4 m (2016, GoN/UNDP/GEF); EWS with automated sirens in six downstream settlements + SMS along ~50 km of the Imja–Dudh Koshi | [EGU21 case study](https://meetingorganizer.copernicus.org/EGU21/EGU21-4163.html) |
| Targeted time-series-SAR segmentation of high-risk Himalayan lakes toward automated GLOF warning is active research (Dec 2025 preprint) | [arXiv:2512.24117](https://arxiv.org/pdf/2512.24117) |
| HMAGLOFDB is the ESSD version-controlled HMA GLOF database (already in the table above) | [ESSD 2023](https://essd.copernicus.org/articles/15/3941/2023/) |
| ITS_LIVE (NASA global glacier velocity) and SWOT (NASA/CNES surface-water level/extent mission) are real, open datasets usable for this axis | [ITS_LIVE](https://its-live.jpl.nasa.gov/), [SWOT](https://swot.jpl.nasa.gov/) |

### Recorded pending verification (supplied in review, 2026-08-28)

Named platforms "IceWatch", "HiGLMN", "GOATAI" (read as proposals, not
operating systems, until shown otherwise); specific model AUC ranges
(0.83–0.96); "15–20% of lakes high-susceptibility"; "40–500% basin-level
lake growth"; order-of-magnitude AI-surrogate speedups over HEC-RAS. None of
these may be repeated as fact from this repo before checking the underlying
papers.

### What it changed here

`data/lakes.json` now carries a provenance-stamped lake watchlist rendered
on the workbench: Tsho Rolpa as `⊘ OFFLINE` (its EWS is reported dead — the
exact failure mode this project exists to make loud) and Imja as
`✱ UNVERIFIED` (an EWS was installed in 2016; its *current* state is the
thing to verify, not assume). Issue #8 tracks building the open
remote-sensing watchlist pipeline on the free stack.

## What this changes in the plan

- Issue #1 is reframed (see the issue): the seismologist's question is G1,
  quantified, with the 26 August event as the test case.
- Phase 4 in PLAN.md becomes a G1 degradation replay: take the 26 August
  signal from open FDSN waveform archives, decimate the network
  synthetically, measure confidence decay. Cheap, offline, publishable.
- G2 becomes issue #7 (corpus), custodian-governed like all data here.
- G3 stays split across issues #4 and #6, now with CAP named as the output
  format so "machine-readable warning" has a concrete definition.
