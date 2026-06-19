---
name: fabric-pipeline-notebook
bundle: custom
description: Best practices for designing and debugging Microsoft Fabric pipelines that orchestrate notebooks. Use this skill whenever building, migrating, or troubleshooting any Fabric pipeline that includes notebook activities, JSON ingestion, Delta table writes, or REST API data extraction. Also use when diagnosing unexpected data volumes, silent data loss, or notebook behaviour that differs between interactive and pipeline-triggered runs.
---

# Fabric Pipeline & Notebook Integration

## Core Principle: Never Assume the Notebook Runs Alone

A notebook behaves differently when triggered by a pipeline vs run interactively. Always design and test with the pipeline context in mind.

---

## Critical Platform Facts

### SQL Endpoint is Read-Only
The Fabric Lakehouse SQL endpoint only supports SELECT. Any INSERT, UPDATE, DELETE, or DDL must be done via a notebook or pipeline activity — never via the SQL endpoint directly.

### Spark Cold Start
Every notebook triggered by a pipeline pays a cold start penalty (typically 3-5 minutes on Default Starter Pool) unless High Concurrency mode is configured. The first `spark.*` call triggers JVM initialisation — structure cells so this happens early and predictably.

**Cold start mitigation options:**
- High Concurrency mode with session tag in pipeline notebook activity settings
- Python notebooks (no JVM, no Spark, 2-3 second startup)
- Custom pool with keepalive configured

### Cadence vs Execution Time
Always verify that pipeline cadence > notebook execution time with meaningful headroom. If runs overlap due to queuing spikes, the same watermark gets read twice — leading to duplicate processing or race conditions on the tracking table.

---

## JSON Ingestion from Fabric Copy Activity

### The Pagination File Structure Problem
When a Fabric Copy activity uses pagination (REST API with nextPageToken, offset-based, or similar), it writes **each page response as a new line** in the same output file. This produces newline-delimited JSON (NDJSON), not a single multiline JSON object.

**WRONG — only processes first page, silently drops all others:**
```python
raw_df = spark.read.option("multiLine", "true").json(file_list)
```

**CORRECT — processes all pages:**
```python
raw_df = spark.read.json(file_list)
```

> This is one of the most dangerous silent failures in Fabric pipelines. The notebook runs without errors, processes exactly maxResults rows, and appears correct while silently discarding all subsequent pages.

### Always Verify Page Count
After ingestion, flag suspiciously round numbers that match your maxResults setting:
```python
MAX_RESULTS = 1000  # set to your API's pagination page size
num_rows = int(df.count())
if num_rows > 0 and num_rows % MAX_RESULTS == 0:
    print(f"WARNING: Exactly {num_rows} rows — possible pagination truncation")
```

### File Discovery in Fabric
Glob patterns (e.g. **/*.json) do not work in Fabric. Always use recursive mssparkutils.fs.ls():
```python
def get_recursive_files(path, extension=".json"):
    file_list = []
    try:
        items = mssparkutils.fs.ls(path)
        for item in items:
            if item.isDir:
                file_list.extend(get_recursive_files(item.path, extension))
            elif item.path.endswith(extension):
                file_list.append(item.path)
    except Exception:
        pass
    return file_list
```

---

## Pipeline Watermark Design

### Watermark Query Must Target the Correct Lakehouse
The Lookup activity must explicitly reference the correct lakehouse connection. In multi-environment setups, verify the connection in the Lookup activity settings — never assume it points to the right place.

### Validate Watermark Advancement
A healthy watermark advances proportionally to pipeline cadence. Replace <tracking_table> and <cadence_minutes> with your values:
```sql
SELECT
    run_timestamp,
    latest_updated_raw,
    DATEDIFF(MINUTE,
        LAG(TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23)))
            OVER (ORDER BY run_timestamp),
        TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23))
    ) AS minutes_advanced,
    CASE
        WHEN DATEDIFF(MINUTE,
            LAG(TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23)))
                OVER (ORDER BY run_timestamp),
            TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23))
        ) = 0 THEN 'Watermark stuck'
        WHEN DATEDIFF(MINUTE,
            LAG(TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23)))
                OVER (ORDER BY run_timestamp),
            TRY_CONVERT(datetime, LEFT(latest_updated_raw, 23))
        ) > (<cadence_minutes> * 2) THEN 'Large gap'
        WHEN num_rows_processed = 0 THEN 'Empty run'
        ELSE 'OK'
    END AS health_flag
FROM <tracking_table>
WHERE latest_updated_raw != ''
ORDER BY run_timestamp DESC
OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY
```

### Common Stuck Watermark Causes
1. **> instead of >= in merge condition** — boundary record re-fetched every run but never written to target
2. **NULL in sort/merge column** — deduplication or merge silently skips records
3. **Schema mismatch** — merge fails silently when source/target schemas diverge
4. **Boundary record re-fetch** — if API query uses >=, combine with >= on merge condition to allow boundary records through

---

## Connection & Permissions Validation at Go-Live

Before going live with a migrated pipeline:
1. Verify new connection has identical permissions to old — check every data source individually
2. Run explicit test queries from the new connection against each source
3. Run a parallel validation period where both old and new systems process the same data
4. Compare output volumes and spot-check specific known records

Never assume credentials were migrated with identical access. Silent permission gaps are nearly impossible to detect without explicit validation — the pipeline runs without errors and simply never returns the inaccessible data.

---

## PySpark vs Python Notebooks

For incremental pipelines processing small-to-medium batches, Python notebooks are almost always the better choice:

| | PySpark | Python |
|---|---|---|
| Cold start | 3-5 min | 2-3 sec |
| Complexity | High | Low |
| Delta writes | Native | Via delta-rs |
| Best for | Large batch, complex transforms | Incremental, simple transforms |

Use PySpark only when batch sizes or transformation complexity genuinely justify the overhead.

---

## Related skills

- **timestamp-timezone-pipelines** — the watermark `>=` vs `>` rule and the UTC/DST handling for the date filters these pipelines send to APIs. Reach for it whenever a watermark drifts or records go missing in a specific time window.
- **medallion-migration-validation** — go-live validation, tracking-table design, and the silent-failure catalogue these pipeline bugs feed into; use it when validating a migrated pipeline or backfilling a gap.
- **spark-operations-cli** (Microsoft) — when a pipeline-triggered notebook fails at the *engine* level (OOM, data skew, stuck/dead Livy session), hand off to this diagnostic skill. This skill covers the *silent data-loss logic* bugs; that one covers *engine* failures.
