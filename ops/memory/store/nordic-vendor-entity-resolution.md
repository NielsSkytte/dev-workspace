---
id: nordic-vendor-entity-resolution
ts: 2026-08-01T12:44:00Z
type: procedural
scope: workspace
source: session:11777a94
tags: [entityresolution, matching, mdm, splink, zingg, cvr, nordic, vendor, dataquality, matas]
description: "Cross-system vendor matching without a shared key: Splink/Zingg, why legal-suffix stripping is dangerous across DK/SE/NO/FI, and what CVR/VAT can and cannot be trusted for"
status: distilled
---

For "same vendor across two ERPs, no shared key". Researched outside MS Learn 2026-07-31.

## The category to borrow from

Two established fields, neither of which is quite this:

- **Migration validation** (DMF, Great Expectations, reconciler tools) treats it as a
  **one-shot cutover check**.
- **Entity resolution / MDM** (Data Ladder, Profisee, Senzing, Zingg, Reltio) owns the hard
  part but sells a golden record, not a drift report.

A *standing daily* cross-ERP reconciliation sits between them. No published reference
implementation found. Borrow the matching from the ER side, not from migration testing.

## Tools

- **Splink** (github.com/moj-analytical-services/splink) - Fellegi-Sunter probabilistic
  linkage, **runs on DuckDB**, unsupervised (EM), no labelled training data. Its "blocking
  rules" are the deterministic layer; its match probability replaces a hand-picked threshold.
  Best fit when the pipeline is already pandas/duckdb.
- **Zingg** - same problem, ML-based, runs natively on **Fabric Spark notebooks**, reads/writes
  OneLake Delta, writes a persistent `ZINGG_ID`, supports incremental. Costs Spark.
- **cleanco** - legal-suffix stripping. **Do not use as a default** (see below).

## Nordic caveat that inverts the usual advice

Standard practice strips legal suffixes so "Amazon" matches "Amazon Ltd". Across a Nordic
group this **manufactures false matches**: `Matas A/S` (DK) and `Matas AB` (SE) collapse to
one string while being **different legal entities**. Keep the suffix and use it as a
**country signal** instead:

| | DK | SE | NO | FI |
|---|---|---|---|---|
| Forms | A/S, ApS, I/S, K/S | AB, HB, KB | AS, ASA, ANS | Oy, Oyj, Ky |

Corollary: **match-normalization and compare-normalization are different operations.** For
comparison, "Matas A/S" vs "Matas" is a genuine discrepancy to report. A config with one
normalization setting per field cannot express both.

## Tax/registration numbers - high precision, low coverage, NOT unique

- Danish **CVR** = 8 digits with an offline-verifiable **check digit**. Cheap pre-filter.
- **CVR is not a VAT registration.** An entity has a CVR whether or not it is momsregistreret;
  VIES lists only VAT-registered ones. So the field may hold a CVR that is not a VAT number.
- **The same CVR legitimately appears on several vendor records** (branches, separate SE
  numbers). A naive deterministic join on tax number therefore **fans out into a cross
  product**. Any tax-number match rule needs a duplicate-key guard that routes to review.

## Registry coverage (uneven - Sweden is the gap)

| | Register | Access |
|---|---|---|
| NO | Enhetsregisteret (Brreg) | Free open JSON API, no key |
| FI | PRH / YTJ | Free open API, no key |
| DK | Virk / CVR | Service account; a **working ingestion already exists** at `Carl-Ras/datahub` (`Landingzone-ETL/CVR/`, enriched view `CentralCompanyRegister`) - note its Virk credentials are hardcoded in plaintext, route through Key Vault on any reuse |
| SE | Bolagsverket | No equivalent free open bulk API found |

Brreg also publishes a **Nordic** dataset searchable by organisation number (NO/SE/FI/IS) -
likeliest single route to Swedish coverage; contents and licence unverified.
