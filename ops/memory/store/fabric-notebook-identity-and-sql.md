---
id: fabric-notebook-identity-and-sql
ts: 2026-08-18T18:30:00Z
type: semantic
scope: workspace
source: session:metaatomic-fabric-host
tags: [fabric, notebook, workspace-identity, service-principal, notebookutils, scheduling, verified-2026-08-18]
status: distilled
description: "Fabric notebooks: what the code runs as vs what it authenticates as, getToken takes an audience key not a resource URL, and connect_to_artifact queries a lakehouse or warehouse with no connection at all"
---

Four facts about running code in a Fabric notebook, all verified against MS Learn on 2026-08-18 and
three of the four exercised in a live workspace the same day.

## 1. Two identity questions, two answers

**What the notebook's code runs as** is the triggering identity:

| Trigger | Runs as |
|---|---|
| Interactive | the current user |
| Pipeline activity | the pipeline's **last modified user** — not its owner, not the notebook's |
| Schedule | **whoever created or last updated the schedule** |

([how-to-use-notebook#security-context-of-running-notebook](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook#security-context-of-running-notebook))

So a scheduled notebook dies with its creator's account. Creating a schedule on someone's behalf
hands them that outage — it is an ownership decision, not a deployment step.

**What it authenticates to data sources as** can be the **workspace identity**. Create a connection
with *Workspace identity* as the authentication kind and tick **"Allow Code-First Artifacts like
Notebooks to access this connection"** — settable only at creation, never after — bind it to the
notebook, read it with `notebookutils.connections.getCredential(<id>)`
([fabric-connection-with-notebook](https://learn.microsoft.com/fabric/data-engineering/fabric-connection-with-notebook)).

A Fabric **Apache Airflow Job** goes further: with the *Fabric Connections* toggle on, it runs
items — notebooks, pipelines, copy jobs, semantic-model refresh — with the workspace identity
directly ([apache-airflow-jobs-workspace-identity](https://learn.microsoft.com/fabric/data-factory/apache-airflow-jobs-workspace-identity)).
The **Invoke pipeline** activity has its own WI path (create the WI, enable *Service principals can
call Fabric public APIs*, grant the WI Contributor).

Do not state the first answer as if it were the whole picture. That mistake is
[[eval-2026-08-18-answered-a-narrower-question]].

## 2. `getToken` takes an audience KEY, not a resource URL

`notebookutils.credentials.getToken` accepts only `pbi`, `storage`, `keyvault`, `kusto`
([notebookutils-credentials](https://learn.microsoft.com/fabric/data-engineering/notebookutils/notebookutils-credentials)).
Passing `https://api.fabric.microsoft.com` — the shape every workstation-side helper uses — fails.
Any engine ported from a laptop into a notebook needs a resource → key mapping.

Under a **service principal**, `getToken("pbi")` returns a *reduced* scope (Lakehouse / Notebook /
Workspace `.ReadWrite.All` and a few more), not the full Fabric scope a user gets. MSAL is the
documented way to get the full scope under an SPN.

## 3. There is no audience key for a SQL analytics endpoint — and none is needed

A **Python** notebook queries a Fabric item directly, under its own identity:

```python
conn = notebookutils.data.connect_to_artifact("Warehouse_Curated", workspace_id)
df = conn.query("SELECT ... FROM INFORMATION_SCHEMA.COLUMNS")
```

([using-python-experience-on-notebook](https://learn.microsoft.com/fabric/data-engineering/using-python-experience-on-notebook),
preview, Python notebooks only). No connection object, no secret, no ODBC driver, no pyodbc. There
is also a `%%tsql -artifact <name> -type Warehouse|Lakehouse|SQLDatabase -bind df` magic.

This is what makes an ODBC-based online enrichment portable into Fabric: replace the SQL runner,
keep everything else. Verified live — a full catalog enrichment ran this way, 12,956 nodes.

**A Fabric Connection is still the right instrument for an EXTERNAL source** (ADLS, SQL Server, a
REST API) reached from a notebook. For Fabric's own items it is machinery you do not need.

## 4. Practical consequences

- `pyodbc` and an ODBC driver are a **workstation** dependency, not a Fabric one.
- A `ProcessPoolExecutor` may not start in a notebook kernel (`BrokenProcessPool`). Buffer results
  and fall back to serial rather than emitting a half-built result.
- A zipapp on the lakehouse (`sys.path.insert(0, ".../x.pyz")`) makes a whole toolchain importable
  with nothing installed into the runtime — `zipimport` handles pure-Python dependencies. Package
  data must be read with `importlib.resources`, never `Path(__file__).with_name(...)`.

Related: [[fabric-notebook-token-identity]], [[metaatomic-distributable-and-scheduled]]
