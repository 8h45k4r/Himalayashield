# Governance

This project publishes information that people might one day act on in a
life-safety context. Governance exists to make sure no number, claim, or alert
semantic reaches a reader without a named human having taken responsibility
for it.

## Roles

### Maintainer
Owns the repository, the plan, and the merge button. Currently: @8h45k4r.

### Data custodian — **vacant, blocking**
Every figure in `data/` needs an owner: one named person who signs the
promotion of a figure from `unverified` to `verified` against an official or
primary source, and who is accountable for the correction when it is wrong.
Until this role is filled (issue #2), no figure is promoted.

### Domain reviewers
Named specialists (seismology, glaciology, hydrology) who answer specific
questions on the record. A domain answer is citable only when it is attached
to a name and a date. "The literature suggests" is not an answer; a
seismologist saying *yes, separable, here is how* or *no, and here is why* is.

## Rules for data

1. **Provenance is mandatory.** Every record in `data/` carries `source`,
   `retrieved`, and `status` (`unverified` | `verified` | `null`). CI rejects
   records without them.
2. **Null beats guess.** A field whose true value is unknown is `null`, with a
   note saying what would fill it. We never interpolate a number a warning
   decision could ride on.
3. **Press figures decay.** Anything sourced from press inside 72 hours of an
   event is presumed wrong in detail and must be re-verified against official
   tallies before any public use.
4. **Absence is loud.** Any system state, dataset, or sensor we describe must
   represent "not watching / not fitted / not reporting" as an explicit,
   visually distinct state — never as a blank, a zero, or a stale green. This
   is the South Lhonak rule.

## Rules for decisions

Anything that constrains future work — scope, data policy, design system,
alert semantics — gets an ADR in `docs/decisions/`, numbered, with the
alternatives that were rejected and why. Decisions live in the repo, not in
chat history.

## Rules while public

The repository has been public since 2026-08-28 by the maintainer's decision
(ADR 0003). The verification gates that originally guarded visibility now
guard presentation:

1. Nothing here may be presented as fact. Every figure carries its
   `unverified`/`null` stamp in the data, and the README says in plain words
   that nothing here can warn anyone. Removing a stamp is a custodian-signed
   act, never an edit.
2. The project publishes no conclusions — no retrospective, no findings —
   before the seismic separability question (issue #1) has a named,
   on-the-record answer and the event record has been through a custodian
   verification pass (issue #2, issue #3).
