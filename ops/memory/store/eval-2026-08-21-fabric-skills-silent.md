---
id: eval-2026-08-21-fabric-skills-silent
ts: 2026-08-21T09:00:00Z
type: evaluative
scope: global
tags: [evaluation, skills, fabric-deployment, fabric-warehouse-git, microsoft-docs]
source: session:8374f87e-2a3d-4166-8017-4515139d44c8
status: distilled
description: "A session spent entirely on deployment mechanics, variable libraries, value sets and DEV-TEST drift, and neither fabric-deployment nor fabric-warehouse-git ever fired; the microsoft-docs MCP carried the session instead"
---

## What did not fire

`fabric-deployment` and `fabric-warehouse-git` were silent across a session whose subject matter is
almost a recitation of their trigger lists: a deployment DEV -> TEST, a new variable library and its
value sets, an alias that would fail at submit with `BadRequest`, `LastModifiedBy` / item ownership,
schedules surviving a sync, `Invalid object name` on a warehouse query, and a full DEV/TEST drift
comparison. Nothing was wrong with the output, but the conventions applied came from
`datahub/CLAUDE.md` and from `CONTEXT.md`, not from the skills that were built to hold them.

This is the tenth consecutive session with the domain skills silent. The pattern is now the finding:
skills whose knowledge has been duplicated into a project's `CLAUDE.md` stop being reached for,
because the cascading file answers first and there is never a felt gap.

## What did fire, and earned it

The `microsoft-docs` MCP, used heavily and decisively. Two facts came from the reference pages and
would not have come from anywhere else:

- `executeDaxQueries` takes a single `query` string where `executeQueries` takes a `queries` array -
  the wrong shape returns an empty Arrow stream with HTTP 200, so it fails silently and looks like
  "the endpoint returns nothing".
- The `executeQueries` limitation line disclaiming INFO functions, which is **stale for
  `INFO.VIEW.*`** (measured: 841 rows) and **accurate for `INFO.STORAGE*`** (measured: HTTP 400).
  Believing the doc wholesale, or dismissing it wholesale, would both have been wrong.

Reading the docs also settled a contradiction *between* two Microsoft pages on whether `objects[]`
is published mid-refresh - resolved by measurement, not by picking a page.

## Correction the session had to make about itself

I told Niels the Curated rebuild would repopulate two empty dimensions. It did not - the run
completed and both stayed at 0 rows while their transform views return 5,114 and 1,320. The claim
was inference from a known drop-create failure mode, stated as expectation rather than labelled as
inference. Verify after the run before saying a defect is resolved by it.

## Corroboration — a second, independent session the same day

A parallel session on the same project spent 2026-08-16 to 08-21 on deployment pipelines, variable libraries, value-set overrides, DEV-vs-TEST drift and warehouse DDL reconciliation, and `fabric-deployment` and `fabric-warehouse-git` never fired there either. It hit three of their named triggers verbatim - a value-set differing between stages, `Invalid object name` on a warehouse deploy, and "is this item portable" - and reached for the project's `CLAUDE.md` each time instead. Two sessions arriving at the same finding from unrelated work makes this a trigger problem, not a sampling artefact.
