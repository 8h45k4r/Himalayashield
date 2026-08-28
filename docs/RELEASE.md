# Release & deployment

Two deployment targets, one build. `tools/build_site.py` produces `_site/`;
the deploy workflow publishes that identical artifact to:

1. **GitHub Pages** — https://8h45k4r.github.io/Himalayashield/ — zero
   config, always on.
2. **Cloudflare Workers (static assets)** — https://himalayashield.allgetz.com
   — via Wrangler, activates when the repo has a `CLOUDFLARE_API_TOKEN`
   secret (see below). Cloudflare serves the `web/_headers` security headers,
   which GitHub Pages cannot.

## The pipeline

```
push to default branch ──┐
cron (every 6 h) ────────┼──► build (fetch data → _site/, budget-checked)
manual dispatch ─────────┘        │
                                  ├──► deploy to GitHub Pages
                                  └──► deploy to Cloudflare (if token secret set)
```

- The cron exists because the page contains live data: a site that stops
  rebuilding goes visibly stale (and flags itself OFFLINE after 26 h).
- Deploys come **only** from the default branch. There is no other path to
  production; branch protection (PUSH.md) makes that structural.
- A build over the 50 KB budget or failing tests never deploys — the deploy
  jobs depend on the build job succeeding.

## One-time Cloudflare setup (maintainer, ~5 minutes)

Prereq: `allgetz.com` is an active zone in the Cloudflare account
(`3fbb398edde83c2c0dc375cbe435175b` — already in `wrangler.toml`; account
IDs are not secrets, tokens are).

1. Cloudflare dashboard → My Profile → **API Tokens → Create Token** → use
   the **"Edit Cloudflare Workers"** template; scope it to this account and
   include the `allgetz.com` zone (the template's Workers Routes permission
   is what lets Wrangler attach the custom domain).
2. GitHub repo → Settings → Secrets and variables → Actions → **New
   repository secret**: name `CLOUDFLARE_API_TOKEN`, value = the token.
   Nothing else — the workflow reads everything else from `wrangler.toml`.
3. Run the **Deploy** workflow (Actions → Deploy → Run workflow). Wrangler
   creates the `himalayashield.allgetz.com` custom domain and its DNS record
   automatically (`custom_domain = true`); no manual DNS entry needed.

To change the subdomain later, edit the `pattern` in `wrangler.toml` — one
line, next deploy moves it.

## Releases

Versioning is `v<major>.<minor>.<patch>`; minor tracks the phase plan in
`docs/PLAN.md` (Phase 1 → `v0.1.0`). To cut a release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow builds the site from the tag, zips `_site/` as the
auditable artifact of exactly what was deployable at that version, and
creates a GitHub Release with generated notes. Releases are checkpoints for
the record (the retrospective will cite one); deployment itself is
continuous and does not wait for tags.

## Rollback

`git revert` the offending commit on the default branch and push — the
deploy workflow republishes the previous good state. Never roll back by
force-push; never hotfix in the Cloudflare or Pages UI (the next cron build
would silently overwrite it).
