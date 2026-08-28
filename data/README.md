# Data

Event records and, later, corridor inventories. The rules (enforced by CI and
by GOVERNANCE.md):

- Every figure carries `value`, `status`, `source`, and `retrieved`.
- `status` is one of:
  - `unverified` — captured from press or secondary reporting; presumed wrong
    in detail; kept only so verified figures have something to diff against.
  - `verified` — signed by the named data custodian against an official or
    primary source. **No custodian is named yet, so nothing is verified yet.**
- A field whose true value is unknown is `null` with a `note` saying what
  would fill it. We do not guess numbers a warning decision could ride on.
