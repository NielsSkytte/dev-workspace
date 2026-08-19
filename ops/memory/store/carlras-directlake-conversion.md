---
id: carlras-directlake-conversion
type: semantic
status: distilled
created: 2026-08-19
source: ops/memory/daily/2026-08-17.md, 2026-08-18.md, 2026-08-19.md
project: customers/Carl-Ras/datahub
---

# Carl Ras semantic model: Import -> pure Direct Lake on OneLake

The Import model could no longer refresh - DEV failed at 122 s with `consumed 4665 MB, memory limit
4661 MB`, and `NB_Refresh_SemanticModel_Full` exists only to work around that with an adaptive
batch-halving ladder. Direct Lake removes the rebuild: framing is metadata only, **22 s**.

**Shape that shipped:** 27 Direct Lake tables, 7 calculated/parameter tables, no Import tables, one
`AzureDataLakeStorage` source, no connection or credentials to manage.

**What Direct Lake refuses:** calculated columns, in both flavours, absolutely. Measures, calculation
groups, field parameters and what-if parameters are fine. Calculated tables are fine unless they
reference a Direct Lake table. The two calculated columns moved into the curated views (GEN-008
`MonthSelector`, GEN-009 `Linje`); `Last Refresh` was dropped because with no import there is no
model refresh to report - the measure now reports data freshness from the newest fact date.

**Direct Lake models do not autobind on deployment** (MS Learn, explicit). Without a data source rule
per target stage, a model deployed to TEST keeps reading DEV, silently. One source means one rule.

**A workspace-identity connection needs a role in the workspace holding the data** - the refresh
reports "the credentials are invalid" until Semantic-Model-DEV's identity gets Contributor on
Fabric-ETL-DEV.

Verified: 177/177 measures evaluate, revenue reconciles to SQL within 0.011 kr on 2.8 bn, renders
within a few hundred ms of Import, guardrails clear by an order of magnitude (84 parquet files per
table against 1,000; 3.15 GB against 10 GB).
