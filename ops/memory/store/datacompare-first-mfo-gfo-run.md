---
id: datacompare-first-mfo-gfo-run
ts: 2026-09-07T12:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: distilled
tags: [project, matas, datacompare, fno, vendor, migration, findings]
status: distilled
description: "First real MFO<->GFO vendor comparison (2026-09-07): account numbers survive the migration so [D7] closes, the legal-entity map is derived from account overlap, and the findings that matter are recoded classification codes, 2,497 on-hold vendors released in GFO, bank accounts and person names absent in GFO, and a literal %1 on every GFO formatted address"
---

Snapshot 2026-09-07, Link-to-Fabric tables of both environments (13 vendor tables each, no
customer tables on either link). MFO 11,534 vendor rows in 20 legal entities, GFO 11,509 in 8.

**Matching.** 11,264 of 11,290 distinct MFO account numbers exist in GFO, so the F&O pair matches
deterministically on (legal entity, account); fuzzy stays for AX/NAV. Legal-entity map derived from
shared-account counts: maop->modk (6,435), kise->kise (3,499), kino->kino (1,060), kifi->kifi (373),
mato->mafo (108), maas->madk (21); the Kicks entities also share accounts with each other (same
vendor set up in several Nordic companies). Awaits Matas confirmation. MFO `dataareaid` is
mixed-case (`MAOP` 2,960 rows and `maop` 3,476, disjoint accounts): case-fold it. GFO has exactly
one VendTable row per party; MFO has 135 parties with two.

**Findings (29 fields, 11,496 matched, 42,989 field findings, agreement 87.1% before any rule):**

- The three value-mapped fields are recoded on nearly every vendor and the recode is clean: tax
  group collapses per-country domestic groups into one (DK_KOB / SE_PUR / NO_PUR / FIN_PUR ->
  DOM_AP, EU_* -> EU_AP, 3LAND/EXT -> EXT_AP); vendor group IND->DOM, HUS->RENT, 3L->EXT; payment
  terms `03`->`N14` etc. No Excel map exists for the F&O pair; the dominant recoding per field and
  legal-entity pair is derived from the data, deviations are the mismatches.
- 2,497 vendors on hold = All in MFO are on hold = No in GFO (kise 2,334, kifi 155, mato 8). The 38
  MFO vendors missing in GFO are all on hold in MFO (not migrated, on the evidence by choice).
- GFO `vendbankaccount` has zero rows (MFO 12,519); `dirpersonname` 68 vs 11,698; electronic
  addresses 4,914 vs 15,782. Cause (not migrated vs sync not run) cannot be told from Fabric;
  Matas checks one vendor's Bank accounts tab.
- 8 address descriptions (a free-text field a user types) overwritten with "Primary address" in
  GFO, one of them carrying a note ("ANVAND EJ, SKA TILL Love Beauty OY") that is gone in GFO; 55
  more filled where MFO was empty.
- Every GFO formatted address ends in a literal `%1` instead of the country line: F&O renders that
  string from the country's address-format setup, so it is configuration, not vendor data.
- `vatnum` is populated on 99.6% but only ~81% distinct: secondary key at best.

**"Buy from creditor"** (owner's question) is not in the 13 link tables or the option-set labels;
`paymmode` is blank on every VendTable row on both sides; payment-term labels (30 dage -> 30 days)
sit in `PaymTerm`, outside the link scope. All three are questions to Matas (emails 05/06).
