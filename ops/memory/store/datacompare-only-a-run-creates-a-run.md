---
id: datacompare-only-a-run-creates-a-run
ts: 2026-09-08T12:35:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [project, matas, datacompare, rules, runs, versioning, audit]
status: distilled
description: "Accepting, retiring or reactivating a rule never creates a run: it re-judges the latest run's findings in place and recomputes that run's numbers, so the last point on the agreement chart moves rather than a new point appearing. Only the pipeline creates a run. Because only the latest run is recomputed, older points stay frozen at their own judgement, so a step up between the last two points can be data improving or rules accepted since. dc.run_rule records which rules were in force per run"
---

**The separation is deliberate.** A run answers what the two systems held at a snapshot; a rule
changes how the same findings are judged. If accepting created a run, a rising agreement line would
mix data change with opinion change and mean nothing.

**What was missing until 2026-09-08.** Nothing recorded which rules produced a run's numbers - only
rules that happened to accept at least one finding left a trace in dc.finding.rule_id. dc.run_rule now
holds one row per run and rule with what it accepted; load_sql.py writes the set at load, and the relay
keeps the latest run's set in step on create (upsert), retire (delete) and reactivate (upsert). The
backfill recovered past runs from dc.finding.rule_id, which cannot recover a rule that was in force and
accepted nothing.
