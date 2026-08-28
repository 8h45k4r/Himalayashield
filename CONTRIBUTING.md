# Contributing

All contributions go through the maintainer, **Bhaskar**
([@8h45k4r](https://github.com/8h45k4r), 8h45k4r@gmail.com). Open an issue or
email before sending work — this project's constraints are unusual and worth
knowing up front.

## What is most needed right now

1. **A seismologist.** [Issue #1](https://github.com/8h45k4r/Himalayashield/issues/1)
   needs a named, on-the-record yes/no on whether the 26 August collapse
   signal is separable from ordinary seismicity fast enough to warn
   downstream. Everything else is downstream of that answer.
2. **A data custodian**
   ([issue #2](https://github.com/8h45k4r/Himalayashield/issues/2)) — the
   named person who signs figures from `unverified` to `verified`.

## Ground rules

- **Data:** every figure carries `status`, `source`, `retrieved`. `null` beats
  a guess; press figures inside 72 hours are presumed wrong. See
  `data/README.md` and `GOVERNANCE.md`. CI rejects records without provenance.
- **Decisions:** anything that constrains future work becomes an ADR in
  `docs/decisions/` — raise it with Bhaskar before building on an assumption.
- **Design:** ADR 0002 is enforced, not advisory. Last-metre pages are tokens
  only, under 50 KB, working with JavaScript off; CI fails anything over
  budget. The magenta `offline` state and label+shape rule are not negotiable.
- **Changes** come as pull requests; Bhaskar reviews and merges.

## Licensing note

The repository does not yet carry a license (tracked in `PUSH.md`), so treat
your contribution as pending the license decision — by contributing you agree
to its inclusion under the license the project adopts.
