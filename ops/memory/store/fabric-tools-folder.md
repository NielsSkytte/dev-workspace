---
id: fabric-tools-folder
ts: 2026-11-02T12:00:00Z
type: semantic
scope: own:FabricTools
source: session fff04b8f
tags: [fabric, tools, spn, identity, atomic-tools]
status: distilled
description: "Small Fabric admin scripts live in own/FabricTools, published to ADO Pingala Atomic Tools/FabricTools; fabric_identity.py is the first"
---

- `C:\Dev\own\FabricTools` holds small standalone Fabric admin scripts, with a README per script.
  First: `fabric_identity.py` (moves schedule owner, pipeline LastModifiedBy, warehouse owner,
  lakehouse identity and connection roles to an SPN). own commit `581dba8`.
- Published by hand to ADO `PingalaGlobal/Data and AI/_git/Pingala Atomic Tools`, folder
  `FabricTools/` (`66e649b`), beside CapacityManager, EnvDiscovery, MetaAtomic. No local clone of
  Atomic Tools exists; clone to the scratchpad, copy, commit, push.
- The Carl Ras copy `customers/Carl-Ras/datahub/tools/fabric_identity.py` stays: `fabric_release.py:369`
  calls it from its own folder (Niels, 2026-11-02). Credentials stay there; use `--env-file`.
- Both copies had a crash in the connection grant (`self.spn_object_id`), fixed 2026-11-02.
- 2026-11-13: `own/SoWSkill` published to Atomic Tools as `FabricTools/SoWSkill/` (`cd26bd1`), by hand.
  Left out: `examples/CustomerX_Data_Platform_SoW_v2.*` and `templates/Data_Statement*.docx`, which hold a real
  customer's name.
