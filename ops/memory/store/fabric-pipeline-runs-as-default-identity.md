---
id: fabric-pipeline-runs-as-default-identity
ts: 2026-09-23T08:40:00Z
type: semantic
scope: workspace
source: /log
tags: [fabric, pipeline, identity, spn, conditional-access, carl-ras, operation-hardening]
status: distilled
description: "A Fabric data pipeline always runs as its default identity (the principal stored on the item, which falls back to the last-modifying user), never as whoever presses Run; at Carl Ras a tenant-wide Conditional Access policy (AADSTS530036) refused that user's stored refresh token, and the fix was re-stamping every pipeline and schedule owner to the SPN"
---

Measured at Carl Ras, 2026-09-23 (`PL_ScaleProcess_SP`, then `PL_MainExecution`).

- A data pipeline executes as its **default identity**. With none set explicitly, that is the
  account that last modified the item. Fabric stores that account's refresh token and mints a
  delegated token from it at every submit. Pressing Run only authorises the submit.
- Error seen: `AADSTS530036` - a Conditional Access authentication-flows policy now applies
  tenant-wide and refuses the stored user token.
- Fix: re-stamp the item's identity and the schedule owners to the SPN
  (`tools/fabric_release.py`). DEV 2026-09-23: 29 items (24 pipelines + schedule owners), all ok.
  PROD 2026-09-25: all pipelines, schedules, lakehouses and warehouses re-stamped after the deploy.
- A deployment or an edit by a person puts the item back on that person. Re-stamp after every
  deploy (TEST's `PL_MainExecution` schedule was still open on 2026-09-25).
