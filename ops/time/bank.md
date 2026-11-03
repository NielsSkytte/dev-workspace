# Hour bank

Hours already spent but not ready for invoicing: held for a later invoice under the customer
agreement, or saved up to be spread (engine work across customers, a build across months).
Read by `ops/lib/bank.py`; `python ops/bin/bank.py` prints the balances.

- Deposit: move the timesheet lines to the `own/` project whose work it was (Time page
  reassign; internal, so not entered into F&O), then add a row here. `Hours` = what may be
  invoiced (the F&O entry figure when banked); `Work h` / `Weighted h` = evidence.
  `For` = customer(s), comma-separated, or `-`.
- Withdrawal: add the hours to a customer line on a later, open day (the timesheet file, by
  hand), then add a row here naming the deposit. Never touch a closed month.
- Reclaim (under-billed hours recovered later) is a deposit with Holding `-`.

## Deposits

| Id | Opened | Holding | Hours | Work h | Weighted h | For | Terms | Basis |
|---|---|---|---|---|---|---|---|---|
| R1 | 2026-09-07 | - | 14.50 | 13.50 | 28.00 | Matas | reclaim in 2026-09 on 212-01 / Task-65904 / 111953 | July 16 - Aug 3 backend build (config store, canonical layer, match engine): billed 13.50 h measured vs 28.00 h weighted (ops/time/value/*) |
| R2 | 2026-09-08 | - | 11.50 | 5.25 | 16.75 | Matas | reclaim in 2026-09 on 212-01 / Task-65904 / 111953 | ESTIMATE: 8 billed July days with no value record; keyboard 2.31 h x 7.26 = 16.75 h weighted, less 5.25 h billed (owner's method, 2026-09-08) |
| B1 | 2026-11-03 | own/ProcessInsight | 42.75 | 16.50 | 53.39 | Carl Ras | held by owner at the October close (2026-11-01); terms to be decided later (owner, 2026-11-03) | process-insight lines with no task, October, moved to own/ProcessInsight 2026-11-03 (F&O entry h as banked): 10-15 9.25, 10-19 4.50, 10-21 4.00, 10-23 8.25, 10-25 7.75, 10-27 3.50, 10-28 5.50 |

## Withdrawals

| Date | Deposit | Project | F&O line | Hours | Note |
|---|---|---|---|---|---|
| 2026-09-01 | R1 | customers/Matas/DataCompare | 212-01 / 111953 / Task-65904 | 4.00 | placed for capacity, not work performed on that date (owner, 2026-09-08) |
| 2026-09-02 | R1 | customers/Matas/DataCompare | 212-01 / 111953 / Task-65904 | 4.00 | as above |
| 2026-09-03 | R1 | customers/Matas/DataCompare | 212-01 / 111953 / Task-65904 | 4.50 | as above |
| 2026-09-04 | R1 | customers/Matas/DataCompare | 212-01 / 111953 / Task-65904 | 2.00 | 8.00 h placed this day: 2.00 from R1, 6.00 from R2 |
| 2026-09-04 | R2 | customers/Matas/DataCompare | 212-01 / 111953 / Task-65904 | 6.00 | as above |
| 2026-09-08 | R2 | customers/Matas/DataCompare | 212-01 / 111953 / Task-65904 | 5.50 | placed 2026-09-21; reclaim must sit before the 2026-09-10 PoC demo (owner) |

## Notes

- 2026-11-03: the reclaim ledger (`reclaim.md`) moved here; its notes are in git history
  (`git log -- ops/time/reclaim.md`).
