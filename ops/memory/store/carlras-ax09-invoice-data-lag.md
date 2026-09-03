---
id: carlras-ax09-invoice-data-lag
ts: 2026-09-02T16:30:00Z
type: semantic
scope: customers/Carl-Ras/datahub
source: session:09fdd4d6
tags: [data-freshness, ax09, filters]
status: distilled
description: "enriched.SalesInvoiceTransactions ran 14 days behind on 2026-09-02 (max order date 2026-08-19), which silently breaks any narrow CURRENT_TIMESTAMP window - rank on recency instead"
---

On 2026-09-02, `[Warehouse_Enriched_AX09].[enriched].[SalesInvoiceTransactions]` had a maximum
order and invoice date of **2026-08-19** — **14 days behind** the query date. Whether that is the
normal ingest cadence or a stalled load is **unverified**; it belongs with the operational-hardening
task.

**The consequence is a silent filter defect, not an error.** A window anchored on
`CURRENT_TIMESTAMP` narrows against data that has already stopped:

| Window | Contacts with an order |
|---|---|
| 14 days | 875 |
| 30 days | 7,370 |
| 90 days | 27,224 |
| 365 days | 61,854 |

The collapse between 30 and 14 days is the lag, not a business signal. Anyone reading 875 as
"contacts active in the last fortnight" is reading an artefact.

**Design rule taken from it:** for a narrow selection, **rank on the record's own latest date and
take the top N** rather than windowing on the clock. Ranking is immune to the lag and hits a target
count exactly. A wide window (365 days) is unaffected in practice — it is a ~351-day window and
nobody cares — so windowing stays fine there.

Check `MAX(OrderDate)` before trusting any date filter narrower than a quarter on this platform.
