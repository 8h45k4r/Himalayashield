# 0001 — Record architecture decisions

Date: 2026-08-28
Status: accepted

## Context

This project will make choices with life-safety consequences — what counts as
a verified number, what an alert state means, what a page must work on. Those
choices must survive contributor turnover and be auditable after an incident.
Chat history and commit messages are not auditable.

## Decision

Every decision that constrains future work is recorded here as a numbered ADR:
context, decision, consequences, and the alternatives rejected. ADRs are
immutable once accepted; a reversal is a new ADR that supersedes the old one.

## Consequences

- Slightly more ceremony per decision.
- Any post-incident review can reconstruct why the system behaved as designed.
- Rejected alternatives stay visible, so they are not re-litigated from zero.
