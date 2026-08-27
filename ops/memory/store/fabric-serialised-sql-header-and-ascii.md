---
id: fabric-serialised-sql-header-and-ascii
ts: 2026-08-27T10:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:50082637-f235-4ee7-be0d-fd881b292a68
tags: [fabric, warehouse, git, authoring, encoding]
status: distilled
description: "Two ways to break a Fabric warehouse .sql, both reporting the identical 'Incorrect syntax near' hyphen: writing the Auto Generated header yourself, and any non-ASCII character in a line comment"
---

Hand-written from the session. Both rules are now in `customers/Carl-Ras/datahub/CLAUDE.md`.

## 1. Fabric owns line 1

Do **not** write `-- Auto Generated (Do not modify) <hash>` on a new serialised `.sql`. Fabric's
normalising commit prepends its own header, and the copy of yours that survives has lost its
leading `-`:

```
-- Auto Generated (Do not modify) BD103033...      <- Fabric's
- Auto Generated (Do not modify) 12539B5A...       <- ours, one hyphen short
```

A single `-` is not a comment. Update from git **accepts** the file (it was clean when it
imported), so the defect only appears later, at deployment. Ship the body starting at its own
comment block.

## 2. Serialised .sql must be pure ASCII

An em dash in a comment does not survive the round trip: read back with `OBJECT_DEFINITION` it
returns as an invalid character. Inside a `/* */` block that is harmless; inside a `--` line
comment it ends the comment early and the parser meets a stray `-`.

## Why they are hard to tell apart

Both produce `DmsImportDatabaseException ... Incorrect syntax near '-'`. Check line 2 for a
single-hyphen header first, then grep the file for bytes > 127.

Cost: one failed deployment of `Warehouse_Enriched_AX09` to TEST and one failed Update from git
of `Warehouse_Curated` into DEV, 2026-08-21. Fixed in `Fabric-ETL` `ed66b3a` and `f1ed16c`.
