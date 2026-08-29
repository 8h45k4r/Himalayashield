# Damage assessment methodology

How damage is recorded here, and what this register is not.

## What it is

A **damage register**: per-event, per-category records in
`data/damage/<event-id>.json`, rendered on the event page and served at
`/api/damage.json`. Each entry carries `value`, `status`, `source`,
`source_class`, `retrieved`, and an optional `note`. It exists so the
eventual verified assessment has a dated, sourced baseline to diff against
— the same role the event record plays for casualties.

## What it is not

- **Not an assessment.** Real damage assessment is field survey plus earth
  observation, done by mandated bodies (NDRRMA, NEA, district authorities,
  Copernicus EMS rapid mapping). This register *collects and attributes*
  their public figures; it never generates its own.
- **Not summable.** Unverified figures are never added into totals — a
  press bridge-count plus an EO building-count is not "total damage".
  Totals appear only when a mandated body publishes one, attributed.
- **Not complete.** EO figures (e.g., Copernicus EMSR927 building counts)
  cover mapped areas of interest only, and the register says so per entry.

## Source classes (recorded, but not a substitute for verification)

| `source_class` | Meaning | Example |
|---|---|---|
| earth-observation service | EO-derived analysis by a mapping service | Copernicus EMS EMSR927 |
| official agency via press | An agency's figure, reported second-hand | NEA hydropower counts |
| press synthesis citing government | Journalistic aggregation of official statements | bridge/road counts |
| press synthesis | Reporting without a named official source | early extent claims |

Higher classes are *better leads*, not verified facts: promotion to
`verified` is custodian-signed against the primary document (GOVERNANCE.md),
regardless of class. Until a custodian exists, everything stays unverified.

## Update rules

1. New figures append with their own `retrieved` date; superseded figures
   are replaced, with the replacement's note naming what it superseded.
2. A figure that officials retract flips to `null` with a note — never
   silently deleted.
3. Per-asset records (a named bridge, a named plant) enter only from
   official lists or EO products, never reconstructed from prose.
