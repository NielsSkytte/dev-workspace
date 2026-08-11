---
name: medallion-migration-validation
bundle: custom
description: Best practices for migrating, validating, and operating medallion architecture (bronze/silver/gold) data pipelines in Microsoft Fabric. Use this skill when planning a pipeline migration, validating a go-live, designing quality control queries, diagnosing data discrepancies between systems, or designing watermark and tracking table patterns. Also use when backfilling data after a bug fix or go-live gap is identified.
---

# Medallion Architecture Migration & Validation

## Core Principle: Never Trust a Migration Without Validation

A pipeline that runs without errors is not necessarily correct. Silent data loss, wrong metrics, and schema mismatches are common and undetectable without explicit validation queries.

---

## Go-Live Validation Checklist

Before decommissioning an old system, verify all of the following:

### 1. Connection & Permissions
- [ ] All data sources accessible by new connection — verify every source individually, not just primary
- [ ] New service account has identical project/schema/container access as old
- [ ] Run explicit test queries against each data source from the new connection
- [ ] Never assume credentials were migrated with identical access

### 2. Data Volume Sanity Check
Compare record counts and key metrics between old and new target tables:
```sql
-- Run in both systems and compare results
SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT <key_column>) AS unique_records,
    MAX(TRY_CONVERT(datetime, LEFT(<timestamp_column>, 23))) AS latest_update,
    MIN(TRY_CONVERT(datetime, LEFT(<timestamp_column>, 23))) AS earliest_update
FROM <target_table>
```

### 3. Recent Activity Validation
New system should capture updates at similar or higher rate than old system:
```sql
SELECT 
    CAST(<timestamp_column> AS date) AS update_date,
    COUNT(*) AS record_count
FROM <target_table>
WHERE TRY_CONVERT(datetime, LEFT(<timestamp_column>, 23)) >= DATEADD(DAY, -7, GETUTCDATE())
GROUP BY CAST(<timestamp_column> AS date)
ORDER BY update_date DESC
```

### 4. Spot Check Known Updates
Identify 5-10 specific records that changed recently in the source system and verify they exist with correct values in the new target table. Do not rely solely on aggregate counts.

### 5. Pipeline Health Baseline
Record these metrics immediately after go-live to establish a baseline for future comparison:
- Average rows per run
- Watermark advancement per run (should match cadence)
- Execution time per run

---

## Tracking Table Design

Every incremental pipeline should maintain a run tracking table:

```sql
CREATE TABLE <schema>.delta_load_tracking (
    run_id                  VARCHAR(36),    -- UUID per run
    run_timestamp           TIMESTAMP,      -- When the run executed (UTC)
    latest_updated_raw      VARCHAR(50),    -- High-water mark from source (UTC with offset)
    num_rows_processed      INT,            -- Total rows in batch before dedup
    num_duplicates_removed  INT,            -- Rows removed by dedup
    num_upserted            INT,            -- Actual rows updated in target (from Delta history)
    num_new_rows            INT             -- Actual new inserts (from Delta history)
)
```

### Get Metrics from Delta History, Not Row Counts
```python
# WRONG: counts staging rows, not actual writes to target
num_upserted = int(staging_df.count())

# CORRECT: reads what Delta actually committed
history = target_table.history(1).collect()[0]["operationMetrics"]
num_upserted = int(history.get("numTargetRowsUpdated", 0))
num_new_rows = int(history.get("numTargetRowsInserted", 0))
```

---

## Watermark Seeding When Migrating History

If you migrate tracking history from an old system to a new one:
- The new pipeline's first run uses MAX(latest_updated_raw) from migrated history
- This may be ahead of any data the new pipeline has actually processed
- Any source updates that occurred before that watermark will be permanently missed
- **Solution:** either seed with a watermark before the earliest data in the new target, or do not migrate tracking history and start fresh with a deliberate backfill

---

## Backfill Patterns

### Triggering a Backfill via Watermark Reset
The Fabric SQL endpoint is read-only — watermark manipulation must happen via notebook:

```python
from datetime import datetime

backfill_data = [(
    'backfill-manual',
    datetime.utcnow(),
    '<backfill_start_date_UTC>',  # e.g. '2026-01-01T00:00:00.000000+00:00'
    0, 0, 0, 0
)]

backfill_df = spark.createDataFrame(backfill_data, [
    'run_id', 'run_timestamp', 'latest_updated_raw',
    'num_rows_processed', 'num_duplicates_removed',
    'num_upserted', 'num_new_rows'
])

backfill_df.write.format('delta').mode('append').saveAsTable('<tracking_table>')
```

> Note: This only works if the backdated watermark value is older than all existing rows in the tracking table. If existing rows are more recent, MAX() will ignore the inserted row. In that case use the hardcoded watermark approach below.

### Hardcoded Watermark for Backfill (Pipeline)
Temporarily replace the Lookup watermark query with a hardcoded value:
```sql
SELECT '<backfill_start_date>' AS LastUpdatedDate
```
After one run completes, immediately revert to the MAX query. Subsequent runs cascade forward automatically from the backfill run's watermark.

### Monitoring Backfill Progress
```sql
SELECT 
    CAST(run_timestamp AS date) AS run_date,
    COUNT(*) AS num_runs,
    SUM(num_rows_processed) AS total_rows_fetched,
    SUM(num_new_rows) AS total_new,
    SUM(num_upserted) AS total_updated,
    MAX(TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23))) AS watermark_reached
FROM <tracking_table>
WHERE latest_updated_raw != ''
GROUP BY CAST(run_timestamp AS date)
ORDER BY run_date DESC
```

Backfill is complete when watermark_reached reaches the current date.

---

## Metadata Table Migration

When migrating configuration or mapping tables between systems:
- Verify column names match exactly — small differences (e.g. id vs field_id) break downstream logic silently
- Verify all rows migrated — count comparison is not sufficient, check key values explicitly
- Establish a sync mechanism if the source metadata changes over time
- Never assume a one-time copy stays valid indefinitely

---

## Ongoing Quality Control

```sql
-- Daily pipeline health summary
SELECT 
    CAST(run_timestamp AS date) AS run_date,
    COUNT(*) AS num_runs,
    AVG(num_rows_processed) AS avg_rows_per_run,
    MAX(num_rows_processed) AS max_rows_per_run,
    SUM(num_new_rows) AS total_new,
    SUM(num_upserted) AS total_updated
FROM <tracking_table>
WHERE latest_updated_raw != ''
GROUP BY CAST(run_timestamp AS date)
ORDER BY run_date DESC
```

---

## Common Silent Failure Modes

These all produce no errors but result in wrong or missing data:

| Failure | Symptom | Root Cause |
|---|---|---|
| Pagination truncation | Always exactly maxResults rows per run | multiLine=true on NDJSON file |
| Watermark stuck | Same watermark across consecutive runs | > instead of >= in merge condition |
| Timezone blind spot | Missing updates in specific time windows | Offset stripped before API query |
| Permission gap | Specific record types never appear | New connection missing source access |
| Metadata mismatch | Columns NULL in target | Column name changed during migration |
| Watermark seeding gap | Pre-migration records correct, post-migration stale | Migrated watermark ahead of actual processing |
| Metric inflation | num_upserted equals batch size not actual writes | Counting staging rows instead of Delta history |

---

## Related skills

- **fabric-pipeline-notebook** — the pipeline/notebook gotchas (NDJSON pagination truncation, stuck watermark, permission gaps) behind several rows of the Common Silent Failure Modes table above.
- **timestamp-timezone-pipelines** — UTC/DST handling and the merge `>=` rule behind the "timezone blind spot" failure mode.
- **e2e-medallion-architecture** (Microsoft) — the build counterpart: it constructs the Bronze/Silver/Gold stack, this skill validates the migration and go-live. Reach for it for the build mechanics rather than restating them here.
