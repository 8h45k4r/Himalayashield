# The five gates

Every change passes all five gates before merge. "Pass" means the checklist
item is true, not that it was considered. The PR template mirrors these; CI
enforces the automatable subset; the maintainer (Bhaskar) enforces the rest.
A gate that does not apply to a change is marked N/A with one line saying
why — silence is not N/A.

## Gate 1 — UI/UX

- [ ] **The offline rule:** any state meaning "not watching / not fitted /
      not reporting" renders loud (purple `⊘ OFFLINE`, per ADR 0004) — never
      blank, zero, or stale-green.
- [ ] **Never colour alone:** every state carries a text label and a shape
      (`● ▲ ◆ ■ ⊘ ✱`). Verified with the palette validator where colours
      change (see docs/DATAVIZ.md), not by eye.
- [ ] **Tier discipline (ADR 0002):** last-metre/public pages are tokens-only
      HTML, < 50 KB, fully functional with JavaScript off (CI-enforced).
      Carbon React only in the operations console.
- [ ] Works in light and dark; readable at 320 px width; real `<table>` for
      tabular data; every figure has a text alternative.
- [ ] Every timestamp is UTC and explicit; nothing implies freshness it
      doesn't have.

## Gate 2 — Code

- [ ] Stdlib-first Python for the pipeline; a new dependency needs one
      sentence of justification in the PR (each is supply-chain surface —
      see Gate 5).
- [ ] Build fails loud: fetch errors produce the OFFLINE page, never a stale
      or partial page presented as live; unexpected data shapes raise, not
      guess.
- [ ] No secrets, tokens, or personal data in code, config, or generated
      output — the pipeline must run keyless by design.
- [ ] Deterministic: same inputs → byte-identical page (timestamps come from
      the data, not from randomness).
- [ ] Comments state constraints the code can't (budgets, API quirks), not
      narration.

## Gate 3 — QA/QC

- [ ] Tests exist for the change and run in CI (`python -m unittest` — zero
      install). The offline path is tested, not just the happy path.
- [ ] The generated page is built in CI from a fixture (no network in tests)
      and checked against the budget and required markers.
- [ ] Data QC: every record passes the provenance check (CI); figures a
      warning could ride on are `verified` or `null`, never guessed
      (GOVERNANCE.md).
- [ ] Reproduced locally once: the reviewer can run one documented command
      and get the artifact.

## Gate 4 — Documentation

- [ ] A decision that constrains future work → ADR in `docs/decisions/`
      before or with the code, not after.
- [ ] README / PLAN / DATAVIZ / RELEASE updated in the same PR as the
      behaviour they describe — docs never trail a merge.
- [ ] Every number in prose or on the page states its source and status;
      unverified figures carry the `✱` badge wherever rendered.
- [ ] The change is explained for the next contributor, not the current one
      (no session-local shorthand).

## Gate 5 — VAPT (vulnerability assessment & pentest posture)

Threat model for a static, keyless pipeline — in priority order:

1. **Supply chain** (malicious/compromised dependency or action):
   - [ ] GitHub Actions pinned to major versions from trusted owners
         (`actions/*`, `github/*`) only; third-party actions need
         maintainer sign-off in the PR.
   - [ ] No runtime CDN/script/font fetches in any page (CI-enforced: the
         no-external-script check). All assets inline.
2. **Injection via upstream data** (USGS/OSM responses are untrusted input):
   - [ ] Everything interpolated into HTML is escaped (`html.escape`);
         numbers are parsed as numbers, not spliced as strings; place names
         are text, never markup.
3. **Workflow privilege**:
   - [ ] Workflows declare least-privilege `permissions:` blocks; nothing
         gets `write` it doesn't use; no `pull_request_target` with
         checkout of PR code.
4. **Secrets & PII**:
   - [ ] Secret scanning + push protection on; no personal data beyond the
         maintainer's published contact; CodeQL runs on every PR and weekly.
5. **Integrity of what readers see**:
   - [ ] Deploys come only from the default branch via the Pages workflow;
         branch protection once configured (PUSH.md) makes that the only
         path to production.
- [ ] Report vulnerabilities per SECURITY.md — through Bhaskar
      (8h45k4r@gmail.com), not public issues.
