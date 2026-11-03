---
id: servicenow-oauth-and-sys-choice-role
ts: 2026-11-03T22:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
tags: [servicenow, oauth, fabric-pipeline, acl, sys_choice, sys_dictionary, aeven]
status: distilled
description: "ServiceNow OAuth client credentials in a Fabric pipeline (two connections, header rules); personalize_choices opens sys_choice fields + sys_dictionary/sys_db_object; Aeven sys_choice back to 4 fields"
---

- OAuth client credentials (Zurich): property `glide.oauth.inbound.client.credential.grant_type.enabled = true`,
  OAuth client with Application User = integration user, `POST /oauth_token.do` grant_type=client_credentials,
  no refresh token. Token carries the user's roles.
- Fabric: two connections, because a Web v2 connection holds one credential and has no Bearer type:
  token connection (Basic = client id/secret, base `https://<instance>/`) and Anonymous data connection
  (`/api/now/`) with the pipeline adding the header. One token per run (an If cannot nest in an If), so
  the token lifespan must cover the longest run.
- Copy `additionalHeaders` must be an object; under basic it must be empty: an empty Authorization value
  overrides the connection's Basic credential (401), a string value is rejected. `json('{}')` works.
- Switch: `ServiceNow_Auth` in VL_RunSettings (basic | oauth) per value set. Both proven on PDI dev443926
  (oauth full `20261103T104947Z`, basic delta `20261103T172626Z`). MasterDataPlan `3b8ab2e`, Aeven = basic.
- With roles itil + snc_read_only, sys_choice returns only label, sys_id, sys_domain, sys_domain_path.
  Read ACL `sys_choice.*` needs personalize_choices | personalize_responses | pa_admin | playbook.write.
  `personalize_choices` gives all 19 fields and full sys_dictionary (154,011) / sys_db_object (6,290) on
  the PDI, but also create/write/delete on sys_choice. Asked Aeven for it or a read-only role (2026-11-03).
- Aeven run `20261103T144624Z`: sys_choice back to the 4 fields (all fields on 10-20), so ChoiceLabel 0.
  Inference, not proven: Aeven's access changed after 10-20.
