---
id: fabric-scd2-merge-needs-one-row-per-key
ts: 2026-08-21T11:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
tags: [fabric, atomic, delta, scd2, ingest, marketo, data-quality]
status: distilled
description: "A Delta MERGE takes at most one source row per key, but a first load CREATES instead of merging and swallows duplicates silently - so a windowed API extract poisons the table on load one and only fails on load two"
---

Atomic's `NB_Ingest_IngestChangedRecords` loads raw with a Delta `MERGE` keyed on the primary key
from `rawtablekeymap_<source>`. Two behaviours combine badly for any source that windows by date.

**1. A MERGE refuses ambiguity; a CREATE does not.** If two source rows claim the same key, Delta
raises `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` rather than pick one. But the
loader's first pass takes a different branch — `if not DeltaTableExists(...)` writes with
`saveAsTable`, which has no such check. **Duplicates enter silently on the first load and are only
reported on the second.** Carl Ras's `raw.leads` held 551 doubled ids for eleven days, in DEV and
TEST both, before anything complained.

Diagnostic value: `FirstLoadedTimestamp == LatestLoadedTimestamp` in `AutoLoader_<source>` means
the table has never been merged, so its duplicate count has never been tested.

**2. The existing dedupe cannot help.** The loader calls `drop_duplicates()` with no subset, which
removes rows identical across *every* column. A windowed extract re-reading its open window emits
a fresh snapshot of a record it already sent, differing in real values and in landing-zone
provenance columns (`_export_id`, `_window_end`, `_lz_ingested_at_utc`). Those are legitimately
different rows for one key.

**Fix (Fabric-ETL `a106aec`):** an optional `prep_dedupeByKeyOrderBy` parameter. Set it to the
column that says which snapshot is newer and the loader keeps one row per key, ordered descending,
before both the create and the merge path. Unset, behaviour is unchanged, so sources that cannot
repeat a key pass nothing. Marketo uses `_lz_ingested_at_utc`.

Pair it with `scd_columnsToOmit` for the same volatile columns, or every run looks like a change
and stamps a new SCD2 version on every unchanged row — on a daily schedule that is tens of
thousands of fabricated versions a day, which quietly destroys the table's value as a baseline.

**The fix is not retroactive.** It prevents new duplicates; it does not clean existing ones, and a
re-run cannot repair them because a MERGE updates both offending target rows rather than collapsing
them. Where the table has one SCD version and every row current, the cheap repair is to delete it
and let the pipeline rebuild — with `cdc_incrementalLoad = false`, which takes the full-load branch
and deliberately does **not** advance the CDC bookmark. Deleting without that flag rebuilds from
the bookmark forward and leaves a partial table.

Scale of what was hiding: rebuilding collapsed **759,996** duplicate rows out of `activities`,
which had never surfaced because that table had not been merged either.
