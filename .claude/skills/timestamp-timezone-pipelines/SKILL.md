---
name: timestamp-timezone-pipelines
description: Best practices for handling timestamps and timezones in data pipelines, particularly when data crosses system boundaries (APIs, databases, Delta tables). Use this skill whenever designing or debugging pipelines that involve timestamps, watermarks, date filters sent to external APIs, or data sources that return timezone-aware timestamps. Critical to consult when diagnosing missing records, watermark drift, or inconsistent data between systems in different timezones.
---

# Timestamp & Timezone Handling in Data Pipelines

## Core Principle: UTC as the Single Source of Truth

All timestamps should be stored and compared in UTC internally. Convert to local time only at the presentation layer. Never strip timezone offsets without first converting to UTC.

---

## The Offset-Stripping Trap

The most common pipeline timezone bug is stripping a timezone offset without converting first:

```sql
-- WRONG: strips offset without converting, stores local time as if it were UTC
LEFT([<timestamp_column>], 23)  -- e.g. "2026-03-03T16:38:00.495" stored as-is

-- CORRECT: convert to UTC first, then strip offset
-- See platform-specific section below
```

**Why this causes silent data loss:**
If the pipeline stores local time and sends it to an external API that interprets it as UTC, there is an effective N-hour forward shift (where N = UTC offset). Any records updated in that gap are permanently missed — no error, no warning.

---

## DST Awareness is Non-Negotiable

Hardcoded offset corrections break twice a year at DST transitions. Always extract and apply the actual offset from the stored timestamp dynamically.

**Validate DST behaviour empirically** — query your tracking table to confirm whether your data source returns multiple offsets across seasons:
```sql
SELECT RIGHT(<timestamp_column>, 6) AS offset, COUNT(*) AS count
FROM <tracking_table>
WHERE <timestamp_column> != ''
GROUP BY RIGHT(<timestamp_column>, 6)
```

If you see multiple offsets (e.g. +0100 and +0200), dynamic DST handling is required. Never hardcode a fixed hour subtraction.

---

## UTC Conversion in Fabric Notebooks

When storing watermarks derived from API responses that include timezone offsets:

```python
import datetime
from datetime import timezone

raw_ts = <dataframe>.selectExpr("max(<timestamp_column>) as max_ts").collect()[0]["max_ts"]

# Parse with offset awareness and convert to UTC
dt = datetime.datetime.fromisoformat(str(raw_ts)).astimezone(timezone.utc)

# Store as UTC with explicit +00:00 offset for consistency
<watermark_variable> = dt.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
```

This ensures the tracking table always contains UTC regardless of what the source returns — no platform-specific timezone functions needed.

---

## External API Timestamp Queries

When sending timestamps to external APIs as query filters:

1. **Determine empirically how the API interprets bare timestamps** — send a known timestamp and verify which records are returned
2. **Never assume** — the same API can behave differently depending on service account timezone configuration
3. **Convert to UTC before sending** if the API interprets bare timestamps as UTC
4. **Respect API precision limits** — some APIs only accept minute precision, not seconds

**Watermark query pattern for Fabric SQL endpoint** (handles variable UTC offsets, DST-safe):
```sql
SELECT 
    FORMAT(
        DATEADD(
            MINUTE,
            -(
                CAST(SUBSTRING(MAX(RIGHT([<timestamp_column>], 5)), 2, 2) AS int) * 60 +
                CAST(SUBSTRING(MAX(RIGHT([<timestamp_column>], 5)), 4, 2) AS int)
            ),
            MAX(TRY_CONVERT(datetime, LEFT([<timestamp_column>], 23)))
        ),
        'yyyy-MM-dd HH:mm'
    ) AS LastUpdatedDate
FROM [<tracking_table>]
WHERE <timestamp_column> != ''
```

> Note: TODATETIMEOFFSET and AT TIME ZONE are not supported on the Fabric SQL endpoint. Use manual offset arithmetic as above.

---

## Merge Condition Timestamp Comparisons

When merging incremental data into a Delta table using timestamp-based conditions:

```python
# WRONG: > blocks boundary records, watermark gets stuck
condition = "source.<timestamp_column> > target.<timestamp_column>"

# CORRECT: >= allows boundary records through, watermark advances
condition = "source.<timestamp_column> >= target.<timestamp_column>"
```

**Why >= is correct:**
- If the API query uses >= on the watermark, boundary records are always re-fetched
- If merge uses >, boundary records pass the fetch but fail the merge condition
- Watermark never advances because the re-fetched boundary record never changes the target
- Causes cascading gaps as each run re-fetches and discards the same record

---

## String vs Typed Timestamp Comparisons

If timestamps are stored as strings in Delta (common when mapping from JSON), comparisons are lexicographic, not chronological.

This works correctly only if:
- Timestamps are ISO 8601 format
- Timezone representation is consistent across all rows

Mixed formats (e.g. some +0100, some +00:00) produce incorrect ordering. Always store timestamps in a consistent format — preferably UTC with +00:00 suffix throughout the entire pipeline.

---

## Validation Checklist

Before deploying any pipeline that handles timestamps:

- [ ] Confirmed how the source API interprets bare timestamps (UTC or local)
- [ ] Verified DST behaviour — checked for multiple offsets in historical data
- [ ] Watermark stored in UTC with explicit offset throughout
- [ ] Merge condition uses >= not >
- [ ] No hardcoded offset corrections — offset extracted dynamically from stored value
- [ ] Timestamp comparison in merge is consistent (no mixed formats)
