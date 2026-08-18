---
id: metaatomic-distributable-and-scheduled
ts: 2026-08-18T18:35:00Z
type: semantic
scope: project:own/MetaAtomic
tags: [metaatomic, distribution, packaging, zipapp, fabric, ado, publishing]
status: distilled
description: "MetaAtomic went from one machine to a shared ADO repo, a one-file deployable, and a scheduled Fabric notebook writing into a util lakehouse - in two sessions, with every step verified from a clean clone"
---

MetaAtomic was a working tool on one machine. It is now something a colleague can clone and a
customer's own Fabric can run. Published to `Pingala Atomic Tools/MetaAtomic` in the Pingala ADO.

## What made it distributable (ADR 0010, 0011)

- **One entry point.** `metaatomic.py run|doctor|selftest`. `run` composes lineage → stream matrix
  → portal; the three packages keep their own `-m` entries.
- **A synthetic fixture ships with it** (`tests/fixtures/`, two repos), so `selftest` proves an
  install on a machine that has never seen a customer. The engine ships **no customer data**; the
  guards that need a real platform read env vars and skip.
- **`build.py`** — `app` (a 0.8 MB zipapp with `sqlglot` vendored), `wheel`, and `publish`.
- **`publish` refuses to ship a customer name**, deriving the forbidden tokens from the deployment
  folders on the machine rather than hardcoding them — a list of customer names inside a shipped
  file would be the thing it guards against. It scans the *transformed* content, which is how it
  caught `CLAUDE.md`'s identity block.
- **Installation naming left the engine.** `atomic_rules.INSTALLATION` is empty by default and is
  filled from a `metaatomic.rules.json` in the deployment. One customer's exchange lakehouse,
  serving schema and stale targets had been hardcoded, so every other customer's copy carried them.

## The shared repo is a published subset, not a mirror

Colleagues clone it and may push its contents into a **customer's** repo, so the bar is not
"internal audience" but "must not carry another customer's name". Working notes (CONTEXT,
DELIVERABLES, ADRs, the retired `meta.*` design) stay in the working repo. Sync is one-way by
design; a colleague's edit has to be brought back by hand.

## Multi-repo is the normal case

A platform is rarely one repo — ETL, landing zone and semantic model are each a git-connected
workspace. Point at the **folder holding them**: `.git` marks a repo, `definition/tables/*.tmdl`
marks a semantic model (by content, not by the `.SemanticModel` name), and each repo becomes its own
provenance chip with its own branch. Naming repos explicitly still means exactly those, and what was
left out is printed.

## It runs in Fabric on a schedule (ADR 0012)

The zipapp is uploaded to `Files/MetaAtomic/metaatomic.pyz` in the util lakehouse and put on
`sys.path`; nothing is installed into the runtime and an upgrade is replacing one file. Output lands
in `Files/MetaAtomic/out/metaAtomic/` as self-contained HTML the customer downloads and opens.
Verified in a live DEV workspace: offline 3m36s / 9,753 nodes, then **online 12,956 nodes / 8,898
edges with 38 catalog-only tables**. See [[fabric-notebook-identity-and-sql]] for the host specifics.

## Defects that only the real deployments exposed

Each of these passed every local test and failed the moment it met a real host:

| Found by | Defect |
|---|---|
| following the README from a fresh clone | a semantic model one folder deeper than auto-discovery said **nothing** — reports shipped with no semantic layer. Worth 978 nodes / 1,213 edges at one customer |
| running in a notebook kernel | `ProcessPoolExecutor` died; view analysis now buffers and falls back to serial |
| running with output in a lakehouse | the project name came from the output folder, so the page read `<Customer> MetaAtomic` |
| running twice | the document's `sources` block froze at first derivation while the store refreshed under it — on a schedule, a false claim about what the page knows |

**The pattern is the lesson:** local green means the code works, not that the product does. Every
one of these needed a real clone, a real host, or a second run.
