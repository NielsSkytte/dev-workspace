---
id: matas-datacompare-poc-approved
ts: 2026-09-21T10:40:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [project, matas, datacompare, poc, production, master, requirements]
status: distilled
description: "Matas approved the DataCompare PoC on 2026-09-14 (first demo 2026-09-10). Master is MFO until 2026-11-01, then GFO. Production: all data is already production data, only the rules database is split Dev/Prod. Owner requirements: a first-seen date on every unhandled finding (accepted findings hidden) instead of a day-to-day view; configurable match keys (existing PK or composite)"
---

Owner statements at the 2026-09-21 check-in:

- **PoC:** demoed with the deck and the app and approved on 2026-09-14; the first demo was
  2026-09-10.
- **Master flag:** MFO until 2026-11-01, then GFO, as agreed with Matas. Settles the
  `seed_static.sql` (GFO) vs prototype (MFO) disagreement: MFO is right until the switch.
- **Production:** `GFO_DataCompare_ETL_Prod` is ready. Every source read is already production data;
  only the database that stores the rules etc. (`SQLDB_DataCompare`) is kept as separate Dev and Prod.
- **Findings over time:** "if a new finding comes up but is not handled, we need to know the date on
  which it occurred" - a first-seen date per unhandled finding, accepted findings not shown, preferred
  over a day-to-day delta view.
- **Match keys:** each new dimension still needs its own match evidence, and the key must be
  configurable: point to an existing primary key, or create a composite key where relevant.
- **Customer asks closed:** `CustTable` + `CustBankAccount` synced into Link to Fabric; email 06 is
  old, the region is West Europe; `PaymTerm`/`PaymMode` joined the scope; "Buy from creditor" is
  unresolved and out of scope for now. Matas still owes the rulings on the big buckets.
