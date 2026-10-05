---
id: secrets-committed-customer-repos
ts: 2026-10-05T12:00:00Z
type: semantic
scope: workspace
source: session:ee830441
tags: [security, carl-ras, element-logic, key-vault]
status: distilled
description: "Two customer repos have plaintext secrets committed: Carl Ras CVR notebook (Virk user/password) and Element Logic NB_Manage_Shortcut_LZ_To_Raw (SPN client secret); not fixed, owner informed 2026-10-05"
---

Found 2026-10-05 by read-only repo research (Atomic Part 2):
- Carl Ras: `datahub/Landingzone-ETL/CVR/NB_Ingest_CVR.Notebook/notebook-content.py` --
  `VIRK_USERNAME` / `VIRK_PASSWORD` literals. Marketo in the same repo uses Key Vault.
- Element Logic: `03 - Raw/FO/Maintenance/NB_Manage_Shortcut_LZ_To_Raw.Notebook/notebook-content.py`
  lines 171-173 -- service principal client secret (repo snapshot under LineageDocumentation/Input).

Not changed (customer repos). Recommended: rotate both, move to Key Vault. Values are not copied
into any workspace file.
