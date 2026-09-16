---
id: elementlogic-deployment-no-keyvault
ts: 2026-09-16T08:30:00Z
type: decision
scope: customers/ElementLogic/LineageDocumentation
source: /log
tags: [element-logic, metaatomic, deployment, pat, key-vault, security]
description: Element Logic has no reachable Key Vault, so the read-only PAT sits in clear text in the pipeline parameter GIT_PAT (owner's stopgap decision 2026-09-16); target is a Fabric HTTP connection + Copy activity with REPO_ZIP, or a vault
status: distilled
---

Facts stated to the owner before the decision: the PAT lands in `pipeline-content.json` in the ETL repo
and its history, readable by everyone with repo read or workspace Contributor; a PAT is scoped by
permission not repo, so Code: Read reads every repo its owner can read; expires within a year and dies
with the owner's account; the repo already carried a committed SPN secret. Owner chose the stopgap so
Lars can deploy this week. Notebook gained `GIT_PAT` as third sign-in path after SPN and Key Vault PAT
(`own` 6fc1649). Vault-free alternative documented: HTTP connection (Basic auth holds the PAT encrypted
in Fabric) + Copy activity calling the DevOps Items API `$format=zip` into the util lakehouse, notebook
runs with `REPO_ZIP`. Runbook section 1a and checklist step 2.3 state the exposure; step 6.4 the way out.
Element Logic's environment workspace ids were already in the repo (`VL_Id_Workspace`: 5 DEV + 5 PROD,
no TEST value set), so `ENVIRONMENTS` is pre-filled and Lars confirms rather than supplies. The repo
also holds an outbound copy `CP_eLogicExchange` (curated -> eLogic data workspace), not in the matrix.
