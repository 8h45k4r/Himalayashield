# 0004 — `offline` is purple, by measurement

Date: 2026-08-28
Status: accepted (supersedes the colour value — not the principle — of the
`offline` state in ADR 0002)

## Context

ADR 0002 set `offline` to magenta (#d02670), "deliberately outside the
amber→orange→red hazard scale". The *principle* — the not-watching state
must be impossible to confuse with the hazard scale — is untouched. The
*value* failed measurement: validated in OKLab with CVD simulation, magenta
vs danger red (#da1e28) is **ΔE ≈ 9 for normal vision and ΔE 9.0 under
deutan** — below the ΔE 15 legibility floor. The state whose one job is
"never be mistaken for danger" was optically adjacent to danger. Every
magenta step failed (best candidate: ΔE 14.5). This is exactly the failure
eyeballing invites: magenta *feels* far from red and measures near it.

## Decision

- **`offline` = purple**: #8a3ffc (light) / #be95ff (dark). Measured against
  danger red: ΔE 34.0 normal, 32.3 worst-CVD (protan) — passes with a wide
  margin in both modes.
- **`unverified` = magenta**: #d02670 (light) / #ff7eb6 (dark). Safe there
  because unverified is a text badge (`✱ UNVERIFIED`) rendered with label
  and glyph beside a figure, never a colour-coded mark competing with the
  hazard scale.
- The label+shape rule stays mandatory everywhere (`⊘ OFFLINE`,
  `✱ UNVERIFIED`); measurement reduces reliance on it, never replaces it.
- Any future palette change must ship its validator numbers in the PR
  (Gate 1); colour decisions are computed here, not eyeballed. Method and
  full results: `docs/DATAVIZ.md`.

## Consequences

- `web/tokens.css` updated; both deployed pages pick it up on next build.
- ADR 0002's prose mentioning magenta remains as written (ADRs are
  immutable); this ADR is the correction of record.
