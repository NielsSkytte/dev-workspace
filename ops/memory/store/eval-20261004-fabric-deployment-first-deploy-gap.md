---
id: eval-20261004-fabric-deployment-first-deploy-gap
ts: 2026-10-04T12:00:00Z
type: evaluative
scope: skill:fabric-deployment
tags: [eval, fabric-deployment, pingala-fabric-platform, email-outlook-ready, writing-voice]
status: distilled
description: "fabric-deployment named the warehouse three-part-name failure but had no first-deploy-into-empty-workspace case (added as failure 7); pingala-fabric-platform duplicate-item rule helped; customer email needed what-works-first framing"
---

- 2026-10-02 Aeven first git deploy: fabric-deployment failure 1 diagnosed the
  DmsImportDatabaseException at once (cure: shell warehouses). It had no case for a first sync into an
  EMPTY workspace, where every dependency (shortcuts, metadata, model path, variable-library ids)
  fails in sequence; the owner called the start "way too difficult". Added failure 7, pre-flight
  point 6 and a first-deploy trigger (C:\Dev commits a534adc, 0b56593).
- pingala-fabric-platform (never fab import into a git workspace; pre-existing items duplicate) gave
  the right answer on the colleague's empty items: delete them before the first sync.
- email-outlook-ready + writing-voice were used for two Aeven emails. The owner found the access email
  unclear ("thought we were just missing sys_dictionary", "what is the integration user"): an email to
  a customer admin should state what works before what does not, and name an account by its role in
  the connection.
- A correction a skill should have prevented: a lock file was proposed for overlapping runs before
  checking the native pipeline concurrency setting; the owner asked for a Fabric-native review and the
  lock was reverted.
