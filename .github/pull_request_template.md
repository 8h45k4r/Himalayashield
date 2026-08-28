# What this changes

<!-- One paragraph. What, and why now. -->

## The five gates (docs/GATES.md — all five, every PR; N/A needs one line of why)

### 1 · UI/UX
- [ ] Offline/absent states render loud (`⊘ OFFLINE`, purple) — never blank, zero, or stale-green
- [ ] No meaning on colour alone (label + shape everywhere); palette changes validated, numbers in this PR
- [ ] Tier discipline: public pages tokens-only, < 50 KB, work with JS off; light+dark both readable

### 2 · Code
- [ ] Fails loud (fetch failure → OFFLINE page, bad data → raise); deterministic build
- [ ] No new dependency, or one sentence justifying it; no secrets/keys/PII anywhere

### 3 · QA/QC
- [ ] Tests for this change run in CI, including the failure path
- [ ] Data records pass provenance checks; nothing guessed that a warning could ride on

### 4 · Documentation
- [ ] Constraining decision → ADR in this PR; affected docs updated in this PR
- [ ] Every rendered figure carries source + status (`✱` badge on unverified)

### 5 · VAPT
- [ ] Workflows least-privilege; actions from trusted owners, pinned
- [ ] Upstream data escaped at render; no external scripts/fonts/CDN added
