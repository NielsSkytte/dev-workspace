# Power BI reports and semantic models: failures seen when they ship through git and a pipeline

Evidence: Carl Ras "Webadfærd og salg" (PBIR, thin report on the Direct Lake model "Web engagement"),
2026-11-17/18. Every item below cost at least one round trip with the customer's owner, because the
report was promoted without anyone seeing it render. Read with failure 8 in `SKILL.md`.

## 1. "Unable to load report", and nothing anywhere says why

**Symptom.** The whole report fails with "Something went wrong / Unable to load report" in every
stage. All service calls return 200 (`modelsAndExploration`, `conceptualschema`), the browser console
is empty, the PBIR validator finds nothing new, and Update from git and the deployment both succeed.

**Cause seen.** One visual (a back button on a hidden page) carried `"parentGroupName": "<id>"` for a
visual group that did not exist in that page. It came in from a visual copied from another report.
A dangling `parentGroupName` is fatal to the whole report, not to the visual.

**How it was found (use this order):**
1. Model first: evaluate every measure the report uses with `executeQueries` (`EVALUATE ROW("v",[m])`).
   If they all return, the model is not the cause.
2. Rollback test: if the previous report version also fails, the defect is either old or the service
   changed what it accepts (inference in this case; v3 had the same line and had opened earlier).
3. **Bisect with test copies in DEV.** Copy the report folder under a new name with a NEW `logicalId`
   in `.platform` (or Update from git sees a duplicate), keep a subset of pages, push, update, open.
   First split by theme / report filters / report objects, then one page per copy. The failing copy
   names the page; diff that page's visuals.
4. Delete the test copies from the repo and the workspace afterwards.

**Rule.** Strip `parentGroupName` from any visual you copy unless you copy its group too. When a
generator or agent notices a defect in a visual, it fixes it or stops; "left as it was" shipped this
one to PROD.

## 2. A visual fails but the report loads

| Defect | Fix |
|---|---|
| A report-level measure (in `definition/reportExtensions.json`) referenced from a visual without `"Schema": "extension"` in its `SourceRef` | `"SourceRef": {"Schema": "extension", "Entity": "<table>"}` in every field and in `sortDefinition` |
| Report-level measure `dataType: "Integer"` | use `"Double"` (what Desktop writes; every working report in the Carl Ras repo uses `Double` or `Text`) |
| Shape map / fillRule gradient colours as a bare `{"Literal": ...}` render blank | wrap as `{"expr": {"Literal": ...}}`. `powerbi-report-author validate` reports `PBIR_FILLRULE_STOP_DOUBLE_WRAP` and advises the opposite; ignore that rule |
| Line chart over daily dates gets a scroll bar | `categoryAxis.axisType = 'Continuous'` |

A report-level measure is the way to add a measure without changing (and redeploying) the model;
it ships with the report through the same pipeline.

## 3. Model defects that surface in the report

- **`Missing_References` / "no visual work":** two names in the model that differ only by case
  (a generated hidden column `date` in a measure table next to `Date[Date]`). The engine unifies
  casing across the model and the report's `Date[Date]` reference breaks. Never let two object
  names differ only by case anywhere in a model.
- **Measures hit the memory limit** (`Resource Governance`, 70-80 s, then error): a
  `FILTER('Fact', ...)` over a whole fact table inside `CALCULATE`. Write column filters,
  `KEEPFILTERS('T'[col] = ...)`; the same measures then took 2-3 s.
- **Month-offset filters:** check the sign of an offset column in the data before writing a
  relative filter. At Carl Ras `Cur Month Offset` is positive for past months, the opposite of its
  description; `-13..0` showed future months.

## 4. The model's per-stage source

A deployment carries the source stage's model parameters (here `OneLakeSourceUrl`), so PROD arrived
pointing at TEST data. **Deployment rules are set in the portal only; there is no API for them.**
Interim fix: `Default.UpdateParameters` on the target model after the deploy. Durable fix: the owner
sets a parameter rule per stage once, in the deployment pipeline UI. Check the target model's
parameter values after every model deploy until the rules exist.

## 4b. Direct Lake in production: viewers see empty visuals

**Symptom.** Report owners and the team see data; new business users with Read (+Build) on the model and
the report see every visual empty. Evidence: Carl Ras 2026-11-18, first users after the move from Import to
Direct Lake on OneLake.

**Cause.** A Direct Lake model with no bound connection reads OneLake as the viewer (SSO). Workspace
Contributors and higher have ReadAll; everyone else needs Read + ReadAll on the source warehouse or
lakehouse ([Direct Lake security](https://learn.microsoft.com/fabric/fundamentals/direct-lake-security-integration)).
An Import model never needed this, so the gap only shows at go-live.

**Fix used (fixed identity, no secret).** (1) Share the source item with the model workspace's
workspace identity: Read + "Read all OneLake data (ReadAll)", notification off. (2) `POST /v1/connections`
ShareableCloud, type and creationMethod `AzureDataLakeStorage`, parameters `server` =
`onelake.dfs.fabric.microsoft.com`, `path` = `/<ws>/<item>/`, credentials `WorkspaceIdentity`,
`singleSignOnType: None`. (3) `POST /v1/workspaces/<ws>/semanticModels/<id>/bindConnection` with that
connection id and the full `https://onelake...` path. (4) Refresh. Check with `GET datasets/<id>/datasources`
(datasourceId = the connection id). A service-principal connection works too but stores a secret.

**Also check at go-live:**
- The model's source parameter per stage (`OneLakeSourceUrl`): PROD `Model_OneLake` read TEST data for a
  week because the per-stage rule existed for one model and not the other (section 4).
- Turn "Keep your Direct Lake data up to date" off (model settings > Refresh, portal only, not in TMDL)
  when the pipeline frames the model after the build; automatic framing fires during drop + CTAS and
  fails with `DirectLake_TableNotFound`.

## 5. You cannot see the report, so test it this way

- Export-to-image can be disabled tenant-wide (`Export report to image is disabled on tenant level`,
  403). Power BI Desktop may exist only as the Store app (not on the default path; the CLI reports
  `DESKTOP_EXE_NOT_FOUND`). Neither is a render check you can count on.
- **The render check is the browser, signed in as the customer account, in DEV, before promoting.**
  Use the browser profile that holds that account (with several Chrome profiles connected, select it
  explicitly; the wrong one triggers an MFA push for the wrong tenant). Open each changed page and
  confirm no "Unable to load report" and no broken visual. After the deploy, open TEST and PROD once.
- Measures on tables that are not deployed yet cannot be tested with `DEFINE MEASURE`; deploy the
  model to DEV first, then test, then build the report on it.
