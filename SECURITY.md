# Security policy

## Reporting a vulnerability

Report privately to the maintainer, **Bhaskar — 8h45k4r@gmail.com** — not in
public issues. Include what you found, where, and how to reproduce it.
You'll get an acknowledgement within 72 hours. If it affects anything a
reader could act on (page integrity, misleading states), it is treated as a
data-honesty incident, not just a bug.

## Scope

- The build pipeline (`tools/`), workflows (`.github/workflows/`), and the
  published pages (github.io and himalayashield.allgetz.com).
- The pipeline is keyless and serverless by design; the interesting attack
  surface is supply chain, workflow permissions, and injection via upstream
  API data. The standing checklist is Gate 5 in `docs/GATES.md`.

## What ships hardened

- Least-privilege `permissions:` on every workflow; deploys only from the
  default branch.
- CodeQL on every PR and weekly; GitHub secret scanning with push
  protection.
- All upstream data HTML-escaped at render; no runtime CDN/script/font
  fetches (CI-enforced).
- Security headers (CSP, nosniff, frame-deny) served via `web/_headers` on
  the Cloudflare deployment.
