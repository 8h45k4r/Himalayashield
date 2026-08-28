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

## What this changes in the plan

- Issue #1 is reframed (see the issue): the seismologist's question is G1,
  quantified, with the 26 August event as the test case.
- Phase 4 in PLAN.md becomes a G1 degradation replay: take the 26 August
  signal from open FDSN waveform archives, decimate the network
  synthetically, measure confidence decay. Cheap, offline, publishable.
- G2 becomes issue #7 (corpus), custodian-governed like all data here.
- G3 stays split across issues #4 and #6, now with CAP named as the output
  format so "machine-readable warning" has a concrete definition.
