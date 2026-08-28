# Repository setup — state and remaining steps

Originally this file carried the one command to create the repo, because the
session that wrote it had no GitHub API access. The repo now exists
(`8h45k4r/Himalayashield`, private) and the content and day-one issues were
pushed/filed directly. What remains needs a human in the GitHub UI.

## Done

- [x] Repository created (private) and content pushed
- [x] Six day-one issues filed (texts preserved below as the source of record)
- [x] CI: JSON validation, provenance check, Tier 2 page budget

## Still manual (GitHub UI — Settings)

1. **Default branch** — the first branch pushed became the default. Create
   `main` from it (or rename) so feature branches have a base to PR against:
   Settings → Branches → default branch.
2. **Branch protection** on the default branch: require PRs, require CI to
   pass, no force pushes. Settings → Branches → Add rule.
3. **Topics**: `glof`, `early-warning`, `himalaya`, `nepal`, `disaster-risk`,
   `carbon-design-system`. (Add these only when the repo goes public.)
4. **License** — deliberately not chosen yet; it is a decision, not
   boilerplate. Apache-2.0 is the likely candidate for the code; data likely
   wants CC BY 4.0 separately. Decide before going public.

## Going public

Not before week one lands. Conditions are in GOVERNANCE.md: a named answer to
issue #1 and a named custodian (issue #2). One command when it is time:

```bash
gh repo edit 8h45k4r/Himalayashield --visibility public
```

## The six day-one issues

Filed on the tracker; kept here verbatim so the tracker can be reconstructed.

### 1. Is the 26 August seismic signal separable? ← the only one that matters this week

The Rasuwa collapse was catalogued by USGS as an M4.4 earthquake before being
reinterpreted as the avalanche itself. Question for a named seismologist, on
the record: can a signature like that be discriminated from ordinary
seismicity automatically and fast enough (minutes) to warn downstream — yes or
no? Either answer is an outcome. A "no, and here is why" kills the detection
concept early and cheaply; a "yes, and here is how" defines the entire
technical roadmap. Everything else in this repository is downstream of this
answer.

### 2. Name a data custodian

Every figure needs one named person who signs promotions from `unverified` to
`verified` against official/primary sources and owns the corrections. Until
this role is filled, nothing is promoted and the repo stays private
(GOVERNANCE.md).

### 3. Verify the 26 August event record

`data/events/2026-08-26-rasuwa.json` is press-derived from inside 72 hours and
presumed wrong in detail. Re-verify every figure against NDRRMA (Nepal),
official Chinese tallies, and the final USGS event page; promote or correct
via the custodian.

### 4. Corridor inventory: fill the nulls

Source-to-settlement distances and flood-wave travel times for the
Bhotekoshi/Trishuli corridor are `null` on purpose. Map settlements, bridges,
hydropower intakes; get travel times from hydraulic input, not guesses.
Weeks 3–4.

### 5. Operations console v0 (Carbon React, Tier 1)

Duty-officer screen: corridor status board with the four states (normal /
watch / warning / danger) plus first-class `offline`, dark theme, data-dense.
Scope per ADR 0002. Weeks 5–6.

### 6. Last-metre page prototype (Tier 2)

Tokens-only HTML from `web/tokens.css`: under 50 KB, works with JS off,
readable on a 2G handset in bad light. Every state carries label + shape, not
colour alone. CI enforces the budget. Weeks 5–6.
