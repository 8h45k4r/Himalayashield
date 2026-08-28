# 0002 — Design system: Carbon, with a hard two-tier scope

Date: 2026-08-28
Status: accepted; the `offline` colour value is superseded by ADR 0004
(magenta → purple, by measurement — the principle is unchanged)

## Context

The project will ship two very different kinds of interface:

1. **An operations console** for a DHM duty officer or a hydropower plant
   operator: desktop, good connectivity, dense data, long sessions, often at
   night. Density and dark mode are features.
2. **Last-metre pages** for a person on a phone in a valley: unreliable 2G/3G,
   old handsets, possibly no JavaScript, read in seconds under stress.

A single design system used naively would fail one of the two. A 500 KB
component bundle is not a warning system on a 2G handset — that is a
last-metre constraint, not an aesthetic one.

## Decision

Adopt **IBM Carbon Design System**, split into two tiers with a hard boundary:

- **Tier 1 — operations console:** full Carbon React. Data tables, dark theme
  (`g90`/`g100`), dense layouts. Desktop only.
- **Tier 2 — last-metre pages:** Carbon **design tokens only**
  (`web/tokens.css`), hand-written HTML. Hard budget: **under 50 KB total,
  fully functional with JavaScript off.** No Carbon components, no framework,
  no client-side rendering. CI enforces the byte budget.

### Why Carbon

- Accessibility is engineered in (WCAG 2.1 AA components, focus management,
  contrast-checked palettes), not bolted on.
- Built for data-dense operational UIs — exactly what a duty-officer console is.
- First-class dark theme, which night-shift monitoring needs.
- Its typeface is IBM Plex, which the strategy brief already uses: one type
  system across documents and interfaces, for free.

(Deliberately **not** argued: lineage from other open hazard-monitoring
projects. The case above carries on its own.)

### Status colours: the `offline` state

The hazard scale is amber → orange → red. Alongside it there is a fourth
first-class state:

- **`offline` is magenta**, deliberately outside the hazard scale's hue range.
  It must be impossible to read "we are not watching this corridor" as
  "nothing is happening here." This is the South Lhonak failure expressed in
  CSS: their system was reported as installed while the camera was dead and
  the breach sensor had never been fitted.
- **Colour never carries meaning alone.** Every state is rendered with a text
  label and a distinct shape/icon. Roughly one man in twelve has a colour
  vision deficiency, and siren panels get read in bad light.

## Consequences

- Two codepaths to maintain; the boundary between tiers is enforced, not
  advisory (CI fails a Tier 2 page that exceeds 50 KB or imports a framework).
- Tier 2 pages will look plainer than Tier 1. That is acceptable and expected.
- Token values live in `web/tokens.css` and are the single source of truth for
  both tiers; Tier 1 maps them onto Carbon theme tokens.

## Alternatives rejected

- **Custom design system:** cannot match Carbon's accessibility engineering
  with this project's resources.
- **Lighter systems (Pico, plain Bootstrap):** fine for Tier 2, but Tier 1
  needs dense operational data components, and running two unrelated systems
  costs more than scoping one.
- **Full Carbon everywhere:** fails the last-metre budget outright.
