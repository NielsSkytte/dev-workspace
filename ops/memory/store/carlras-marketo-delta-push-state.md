---
id: carlras-marketo-delta-push-state
ts: 2026-09-09T14:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:session_01VVkv3Dm4Aerpg1xZFDu2cU
tags: [project, marketo, write-back, reverse-etl, delta, census, fivetran]
status: distilled
description: "Marketo write-back is a delta push: Lakehouse_Util.MarketoPushState holds the payload last accepted per email and changed() decides the send; Benno's Census screenshot (Sync Tracking / Changed columns) shows Fivetran does the same, re-offering ~163k rejected rows daily; steady state is 2,000-11,700 updates a day"
---

Built 2026-09-09 (`Fabric-ETL` `f1fe9f2`) after Benno (Impact) said Fivetran keeps an internal change table so it never updates all 100k+ rows. `changed()` / `push_state()` had existed in `tools/marketo_payload.py` since `f8cdd1c` (08-21) but nothing used them; the notebook was a full push of 218,490 rows.

- `MarketoPushState`: one row per accepted (`updated`) write, payload exactly as sent, typed per POLICY; append-only, newest row per email wins. A run that dies half way keeps completed batches. No table = every lead is a change.
- The screenshot on file (`datahub/data/Screenshot 2026-08-21 183824.png`) already shows the mechanism: Records 222,803 / Changed 171,653 / Updated 8,094 / Rejected 163,559, and Changed = Updated + Rejected every day. Rejected rows never enter the change table, so Census re-offers them daily. Ours has the same property; ~188k of our rows are not Marketo leads and cost ~627 wasted calls a run until filtered to known leads.
- First-run measurement vs Marketo's 08-20 snapshot: 29,617 of 30,807 shared leads differ; `HasWebLogin` 19,840 by source design, 1,158 `accountDiscountGroup` clears ride on an account-resolution disagreement (order counts differ by orders of magnitude on the same leads). Inference, not proven.
- Synthetic test leads cannot be used through the pipeline (not AX09 contacts). Three real leads identical to Marketo on every field were chosen so the only write is the datetime offset.
- Full record: `customers/Carl-Ras/datahub/design/MARKETO_WRITEBACK_GOAL.md` section 17.
