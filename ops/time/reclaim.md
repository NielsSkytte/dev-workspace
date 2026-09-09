# Reclaim ledger

Hours under-billed in a closed month that the owner decided to recover in a later month, on the
same project and task, as part of the work then in progress. Consumed at /log when the later
days are finalized: add to the day's line and record the amount here. Never touch the closed month.

| Opened | Project | Proj ID | Task / activity | Amount h | Basis | Consume in | Consumed h | Remaining h |
|---|---|---|---|---|---|---|---|---|
| 2026-09-07 | customers/Matas/DataCompare | 212-01 | Task-65904 / 111953 | 14.50 | July 16 - Aug 3 backend build (config store, canonical layer, match engine): billed 13.50 h measured vs 28.00 h weighted (ops/time/value/*) | 2026-09, distributed at month end | 14.50 | 0.00 |
| 2026-09-08 | customers/Matas/DataCompare | 212-01 | Task-65904 / 111953 | 11.50 | ESTIMATE. The 8 remaining billed July days (1, 2, 3, 4, 6, 23, 24, 26) never got a value record and cannot be re-derived - the July/August Matas transcripts are gone. Keyboard 2.31 h from heartbeats x the 7.26x factor measured on July's recorded days = 16.75 h weighted, less 5.25 h billed = 11.50 h (owner chose this method, 2026-09-08) | 2026-09, distributed at month end | 6.00 | 5.50 |

Consumption log:

| Date | Project | Added h | Remaining h | Note |
|---|---|---|---|---|
| 2026-09-01 | customers/Matas/DataCompare | 4.00 | 22.00 | placed for capacity, not work performed on that date (owner, 2026-09-08); 212-01 / 111953 / Task-65904 |
| 2026-09-02 | customers/Matas/DataCompare | 4.00 | 18.00 | placed for capacity, not work performed on that date (owner, 2026-09-08); 212-01 / 111953 / Task-65904 |
| 2026-09-03 | customers/Matas/DataCompare | 4.50 | 13.50 | placed for capacity, not work performed on that date (owner, 2026-09-08); 212-01 / 111953 / Task-65904 |
| 2026-09-04 | customers/Matas/DataCompare | 8.00 | 5.50 | placed for capacity, not work performed on that date (owner, 2026-09-08); 212-01 / 111953 / Task-65904 |

Note 2026-09-08: task corrected 65905 -> 65904. The basis is the backend build, and 65904 is the engine and app work; 65905 is the configuration (Link to Fabric, access, setup) - owner, 2026-09-08.
Note 2026-09-08: not drawn day by day. The owner distributes the 14.50 h across the September days when the month is done, before the month is closed.

Note 2026-09-08 (weighted-hours review): July billed 17.00 h and August 1.75 h, 18.75 h over 16 days, but weighted records exist for only 9 of them (28.00 h). The other 7 days have no weighted figure and no transcript left to derive one from, so the second row estimates them. Total outstanding: 26.00 h.

Note 2026-09-08: 20.50 h placed on 1-4 September, the days of last week with capacity and no Matas work. Row 1 (evidence) is fully consumed; 6.00 h of row 2 (estimate) is consumed, 5.50 h remains for the Matas days still to come in September.
