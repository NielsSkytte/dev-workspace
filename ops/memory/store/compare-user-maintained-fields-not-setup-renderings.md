---
id: compare-user-maintained-fields-not-setup-renderings
ts: 2026-09-07T12:00:00Z
type: semantic
scope: workspace
source: distilled
tags: [data-quality, reconciliation, fno, atomic, field-metadata, convention, matas]
status: distilled
description: "Reconciliation rule from the owner (2026-09-07): compare the fields a user maintains, never the strings F&O renders from them through setup (formatted address, ISO code lookups); and every compared field states its origin, an actual source column or a DataCompare composite, plus an Atomic-style numbered group with composites in their own group"
---

**Rule 1 - compare data, not configuration.** `FormattedPrimaryAddress` differed on 11,285 of
11,496 vendors because GFO's address-format setup renders a literal `%1` on the country line;
`AddressCountryRegionISOCode` is a lookup on the country table. Both were dropped from the
comparison: "F&O configuration is someone else's problem, I am concerned about the data". The
components Street / ZipCode / City / CountryRegionId stay. Test for any future field: is the value
typed or chosen by a user on the record, or derived by the system from setup? Only the first is
reconciled. Dropping the two moved agreement from 84.8% to 87.1% with no rule accepted.

**Rule 2 - say what a field is.** Denormalising is fine ("similar to what Atomic does"), but it
must be unmistakable which values are actual F&O fields and which are composites built by us
(e.g. `BankAccountCount` = number of VendBankAccount rows; `VendorPartyType` derived from a
DirPersonName row existing, because `DirPartyTable.InstanceRelationType` is a table id that differs
per environment). Every field carries `origin` (field | composite), `source` (Table.Column and join
path, or how it is built), `scope` (customer list | added by us) and `group`.

**Atomic's own conventions** (checked in the Carl-Ras and ElementLogic repos): no per-column
derived flag; derived columns are separated by section comments in the views ("Semantic columns"
vs "Additional columns from <table>") and by the `05 Calculated Columns` display folder in the
semantic model; presentation groups are numbered display folders (`00 Keys`, `01 Ids`, `02 Date`,
`03 Numeric`, `04 Labels`, `07 System`) so the name is the sort order; `XId` next to `X` keeps raw
code and resolved label; the platform skill documents none of this (a gap). DataCompare mirrors the
numbering and puts every composite in `09 Calculated`.
