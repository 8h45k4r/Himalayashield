# 0003 — Public from day two

Date: 2026-08-28
Status: accepted (supersedes the visibility conditions in the original
GOVERNANCE.md and README)

## Context

The original plan kept this repository private until week one landed: a named
answer to the seismic separability question (issue #1) and a named data
custodian (issue #2). The argument was reputational: a public repo carrying
unverified press-derived numbers about a days-old disaster, under a real name.

The maintainer decided on 2026-08-28 to make the repository public
immediately.

## Decision

The repository is public now. The verification gates do not disappear — they
move from *visibility* to *presentation*:

1. **Nothing here may be presented as fact.** Every figure is stamped
   `unverified` or `null` in the data itself; the README's first section says
   in plain words that nothing here can warn anyone. These stamps are the
   compensating control for early visibility, and removing one is a
   custodian-signed act, never an edit.
2. **The retrospective still waits for validation** (weeks 7–8). Being able
   to read the workbench early is not the same as the project publishing
   conclusions.
3. **The two week-one gates (issues #1 and #2) still block promotion** of any
   figure and any public claim beyond "this is an open workbench."

## Consequences

- Anyone can read press-derived, presumed-wrong figures. Mitigated by the
  stamps above and by never rendering an unverified figure without its status.
- The work happens in the open from the start — earlier scrutiny, earlier
  potential collaborators (the seismologist issue #1 needs is now linkable).
- **A license is now urgent, not optional.** A public repository with no
  license is all-rights-reserved: nobody may legally reuse anything, which
  defeats the point of being public. Tracked in PUSH.md.

## Alternatives rejected

- **Stay private until week one** (the original plan): rejected by the
  maintainer, whose call visibility is.
