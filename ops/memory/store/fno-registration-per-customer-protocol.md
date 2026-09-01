---
id: fno-registration-per-customer-protocol
ts: 2026-09-01T15:15:00Z
type: semantic
scope: workspace
source: session:e15b57a5
tags: [fno, time, registration, carl-ras, matas, element-logic, vestforbraending, protocol]
status: distilled
description: "Each customer accepts time on a different F&O dimension - Carl Ras on Task only (activity is derived), Element Logic on Activity only and in company PNO1, Matas on ADO Task, Vestforbraending No charge - established line by line against F&O's own lookups"
---

Closing August 2026 required tagging every timesheet line to the dimension its customer actually
accepts. The rules below were each confirmed against F&O's own task/activity lookups or against a
posted July journal, not inferred. They live in `ops/time/README.md` §4.1 as the canonical table.

**Carl Ras (`230-02`) — Task always, Activity never.** Niels, verbatim: *"all carl-ras is project-id
230-02, from there its tasks which by default give their own activity id"* and *"for everything we
work on at carl-ras we need a task (not an activity as that is given by default)"*. Writing an
`activity:` on a Carl Ras line is wrong — F&O derives it from the task. The August work spanned
tasks `490 483 491 493 498 524 553 555 255 258 259`, grouped as Marketo inbound (490 build ingest,
255), Marketo write-back (553), Tag Manager, Operational hardening (555), and budget.
Also recorded in `customers/Carl-Ras/datahub/CLAUDE.md`.

**Element Logic (`6001-01`) — Activity only, and a different company.** Activity `600003`
"Operations", Opgave blank, in company **PNO1** (Pingala Norge AS), not PING. Established by finding
no `6001-01` in any PING journal and reading the posted July PNO1-004271. The `45394` that appears
in the sheet note is not the Task field.

**Matas (`212-01`) — ADO Task.** F&O fills the Activity automatically. `Task-65905` "Configuration
of PoC" and `Task-65904` "Design" — but **65904 does not exist in F&O** (*"Opgaven eksisterer ikke -
nye opgaver bør oprettes via DevOps"*), so all its time books to 65905 until DevOps creates it.
Eight timesheet files were retagged.

**Vestforbrænding (`222`) — not billable.** F&O books it `No charge`. The workspace still counts
every `customers/…` project billable, so a billable total spanning July overstates by 5.75 h.
Documented, not encoded.

**Two operational notes.** A task id that does not resolve returns an *empty* lookup, not an error —
`CarlRData-555` and `-524` both read as missing until Niels created them mid-session. And only
`Kategori` auto-fills once Opgave resolves; `Timer` never recomputes from Starttidspunkt /
Sluttidspunkt and must be typed. Fill date, project-id, task and hours; nothing else.
