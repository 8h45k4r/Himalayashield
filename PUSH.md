# Repository setup — state and remaining steps

Originally this file carried the one command to create the repo, because the
session that wrote it had no GitHub API access. The repo now exists
(`8h45k4r/Himalayashield`, private) and the content and day-one issues were
pushed/filed directly. What remains needs a human in the GitHub UI.

## Done

- [x] Repository created and content pushed; made public 2026-08-28 (ADR 0003)
- [x] Six day-one issues filed (texts preserved below as the source of record)
- [x] CI: unit tests, JSON validation, provenance check, Tier 2 page budget
- [x] Live workbench pipeline: `tools/build_site.py` → GitHub Pages
      (auto-enabled by the Deploy workflow) + Cloudflare Workers, 6-hourly cron
- [x] Five gates (docs/GATES.md) wired into the PR template and CI
- [x] CodeQL + release workflow; CODEOWNERS routes everything to @8h45k4r

## Still manual (GitHub UI — Settings)

0. **Enable GitHub Pages (one click, blocks the Pages deploy):** Settings →
   Pages → Build and deployment → Source: **GitHub Actions**. The Deploy
   workflow's `deploy-pages` job fails with "Resource not accessible by
   integration" until this is set — creating the Pages site the first time
   needs repo-admin rights the workflow token doesn't have. The next run
   (or Actions → Deploy → Run workflow) publishes immediately after.
1. **Default branch** — the first branch pushed became the default. Create
   `main` from it (or rename) so feature branches have a base to PR against:
   Settings → Branches → default branch.
2. **Branch protection** on the default branch: require PRs, require CI to
   pass, no force pushes. Settings → Branches → Add rule.
3. **Topics** — the repo is public, so add them now (Repo page → About → ⚙):
   `glof`, `early-warning`, `himalaya`, `nepal`, `disaster-risk`,
   `carbon-design-system`.
4. **Cloudflare custom domain** — create an API token ("Edit Cloudflare
   Workers" template, scoped to the `allgetz.com` zone) and add it as the
   `CLOUDFLARE_API_TOKEN` Actions secret; the next Deploy run then publishes
   https://himalayashield.allgetz.com automatically. Steps: docs/RELEASE.md.
   *Verified 2026-08-29:* the secret is still unset — every Deploy run's
   `deploy-cloudflare` job skips with "Cloudflare not configured yet".
   Everything else is ready: tests pass, the build fits the budget, and
   `npx wrangler@4 deploy --dry-run` validates `wrangler.toml` cleanly
   (account `3fbb398edde83c2c0dc375cbe435175b`, custom domain
   `himalayashield.allgetz.com`). No manual DNS or subdomain creation in
   the Cloudflare dashboard is needed — `custom_domain = true` makes
   Wrangler create the record on first deploy. The token is the only
   missing piece.
5. **License — now urgent.** A public repository with no license is
   all-rights-reserved: nobody may legally reuse anything here, which defeats
   the point of being public. It is still a decision, not boilerplate:
   Apache-2.0 is the likely candidate for code, CC BY 4.0 separately for
   data. Decide this week.

## Going public

Done — the maintainer made the repository public on 2026-08-28, ahead of the
original week-one conditions. The decision and its compensating controls
(every figure stamped `unverified`/`null`, no conclusions before the
validated retrospective) are recorded in
`docs/decisions/0003-public-from-day-two.md`; GOVERNANCE.md now carries
"Rules while public" instead of visibility conditions.

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
watch / warning / danger) plus first-class `offline` (purple, per ADR 0004),
dark theme, data-dense. Scope per ADR 0002. Weeks 5–6.

### 6. Last-metre page prototype (Tier 2)

Tokens-only HTML from `web/tokens.css`: under 50 KB, works with JS off,
readable on a 2G handset in bad light. Every state carries label + shape, not
colour alone. CI enforces the budget. Weeks 5–6.
