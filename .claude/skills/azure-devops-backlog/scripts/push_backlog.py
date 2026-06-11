#!/usr/bin/env python3
"""
push_backlog.py — Expand a Pingala Datahub parameters YAML into the full
standard backlog and push it to Azure DevOps via the REST API.

Key features:
    * Parameters file is small and editable; the full backlog is generated.
    * Dry-run mode prints the full tree without making any network calls.
    * Existing items (matched by exact title) are skipped silently so
      re-running after adding new scope is safe.
    * Items within the same level are created in parallel (default 10 workers),
      parents always finish before their children start.
    * Retries on 429 with exponential backoff.
    * Final summary is a clean markdown table.

Usage:
    python push_backlog.py --yaml backlog.yaml --dry-run
    python push_backlog.py --yaml backlog.yaml --execute

Credentials (one of):
    Environment variables:
        AZDO_ORG_URL=https://dev.azure.com/my-org
        AZDO_PROJECT=CustomerX-Datahub
        AZDO_PAT=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
    Or a .env file in the same directory as the YAML (same keys).
    Or `project.org_url` / `project.name` in the YAML (never put the PAT there).
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import os
import random
import sys
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import requests
    import yaml
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e.name}\n"
        "Install with: pip install requests pyyaml python-dotenv\n"
    )
    sys.exit(1)

try:
    from dotenv import load_dotenv  # optional
except ImportError:
    load_dotenv = None


# ----------------------------------------------------------------------------
# Data model
# ----------------------------------------------------------------------------

@dataclass
class Item:
    """A work item in the in-memory tree. Flat list with parent refs after expansion."""
    type: str                                   # Epic, Feature, Work Package, User Story, Task
    title: str
    description: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    children: list["Item"] = field(default_factory=list)
    # Assigned after expansion:
    depth: int = 0
    parent: "Item | None" = None
    # Assigned after push:
    ado_id: int | None = None
    ado_url: str | None = None
    status: str = "pending"                     # pending | created | skipped | failed
    error: str = ""


# ----------------------------------------------------------------------------
# Parameter expansion (parameters YAML  →  full backlog tree)
# ----------------------------------------------------------------------------

def _load_data_excellence_html() -> str:
    """Load the Data Excellence description HTML from the template file next to this script."""
    path = Path(__file__).resolve().parent.parent / "templates" / "data_excellence_description.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Fallback if running from a flat dir:
    alt = Path(__file__).resolve().parent / "data_excellence_description.html"
    if alt.exists():
        return alt.read_text(encoding="utf-8")
    return "<p>Data Excellence maturity journey — see Pingala playbook.</p>"


def expand_backlog(config: dict[str, Any]) -> list[Item]:
    """Turn a parameters dict into a list of top-level Items (with nested children)."""
    top: list[Item] = []

    # ── CUSTOMER-SPECIFIC: Business area epics ─────────────────────────────
    for ba in config.get("business_areas") or []:
        top.append(_build_business_area_epic(ba))

    # ── GENERIC: Shared masterdata ─────────────────────────────────────────
    top.append(_build_shared_masterdata_epic(config.get("shared_masterdata") or {}))

    # ── GENERIC: Data platform ─────────────────────────────────────────────
    top.append(_build_data_platform_epic(config))

    # ── GENERIC: Data excellence ───────────────────────────────────────────
    top.append(_build_data_excellence_epic())

    # ── OPTIONAL: Extra items appended verbatim ────────────────────────────
    for raw in config.get("extra_items") or []:
        top.append(_item_from_dict(raw))

    return top


def _item_from_dict(d: dict[str, Any]) -> Item:
    it = Item(
        type=d["type"],
        title=d["title"],
        description=d.get("description", "") or "",
        acceptance_criteria=list(d.get("acceptance_criteria") or []),
    )
    for child in d.get("children") or []:
        it.children.append(_item_from_dict(child))
    return it


def _build_business_area_epic(ba: dict[str, Any]) -> Item:
    name = ba["name"]
    epic = Item(
        type="Epic",
        title=f"Business area: {name}",
        description=f"All data platform work for the {name} business area: ingestion, curated model, semantic model, and Power BI reporting.",
    )

    # ── Feature: Power BI Reports ──────────────────────────────────────────
    reports = ba.get("power_bi_reports") or []
    if reports:
        feat = Item(type="Feature", title=f"Power BI Reports: {name}")
        for r in reports:
            feat.children.append(Item(
                type="Work Package",
                title=f"Report: {r}",
                description=f"Build and publish the {r} Power BI report.",
                acceptance_criteria=[
                    "Report is published to the reporting workspace",
                    "Access is granted to the relevant user group",
                    "Data refresh is scheduled and green",
                ],
            ))
        epic.children.append(feat)

    # ── Feature: Semantic model ────────────────────────────────────────────
    sem = Item(type="Feature", title=f"Semantic model: {name}")
    # Relationships
    rel_wp = Item(
        type="Work Package",
        title=f"{name}: Relationships",
        description=f"Define and validate all relationships in the {name} semantic model.",
    )
    for rel in ba.get("relationships") or []:
        rel_wp.children.append(Item(type="Task", title=rel))
    sem.children.append(rel_wp)
    # Business measures
    meas_wp = Item(
        type="Work Package",
        title=f"{name}: Business measures",
        description=f"Implement all DAX measures in the {name} semantic model.",
    )
    for m in ba.get("measures") or []:
        meas_wp.children.append(Item(type="Task", title=f"{name} measures: {m}"))
    sem.children.append(meas_wp)
    # RLS
    sem.children.append(Item(
        type="Work Package",
        title=f"{name}: Row-level-Security",
        description=f"Define and implement row-level security for the {name} semantic model.",
        acceptance_criteria=[
            "RLS roles are defined and documented",
            "Test users validated against expected visibility",
        ],
    ))
    epic.children.append(sem)

    # ── Feature: Curated ───────────────────────────────────────────────────
    cur = Item(type="Feature", title=f"Curated: {name}")
    for dim in ba.get("dim_tables") or []:
        cur.children.append(Item(
            type="Work Package",
            title=f"Dimension table: {dim}",
            description=f"Build the curated dimension table {dim}.",
        ))
    for fact in ba.get("fact_tables") or []:
        cur.children.append(Item(
            type="Work Package",
            title=f"Fact table: {fact}",
            description=f"Build the curated fact table {fact}.",
        ))
    for br in ba.get("bridge_tables") or []:
        cur.children.append(Item(
            type="Work Package",
            title=f"Bridge table: {br}",
            description=f"Build the bridge table {br}.",
        ))
    epic.children.append(cur)

    return epic


def _build_shared_masterdata_epic(shared: dict[str, Any]) -> Item:
    epic = Item(
        type="Epic",
        title="Shared masterdata",
        description="Shared dimensions, measures, and semantic model components used across all business areas.",
    )

    # Curated: Shared masterdata
    cur = Item(type="Feature", title="Curated: Shared masterdata")
    cur.children.append(Item(type="Work Package", title="Dimension table: Department"))
    cur.children.append(Item(type="Work Package", title="Dimension table: Calendar"))
    epic.children.append(cur)

    # Semantic Model: Shared masterdata
    sem = Item(type="Feature", title="Semantic Model: Shared masterdata")
    rel_wp = Item(type="Work Package", title="Shared masterdata: Relationships")
    for rel in shared.get("relationships") or []:
        rel_wp.children.append(Item(type="Task", title=rel))
    sem.children.append(rel_wp)
    meas_wp = Item(type="Work Package", title="Shared masterdata: Business measures")
    for m in shared.get("measures") or []:
        meas_wp.children.append(Item(type="Task", title=f"Shared measures: {m}"))
    sem.children.append(meas_wp)
    sem.children.append(Item(type="Work Package", title="Shared masterdata: Row-level security"))
    epic.children.append(sem)

    return epic


def _build_data_platform_epic(config: dict[str, Any]) -> Item:
    epic = Item(
        type="Epic",
        title="Data platform",
        description="Infrastructure and platform work: ingestion layers, workspaces, CI/CD, environments.",
    )
    sources = config.get("data_sources") or []
    business_areas = [ba["name"] for ba in (config.get("business_areas") or [])]

    # Feature: Landing zone
    lz = Item(type="Feature", title="Landing zone")
    for src in sources:
        us = Item(
            type="User Story",
            title=f"Landing zone: {src['name']}",
            description=f"Establish landing zone for {src['name']}.",
        )
        us.children.append(Item(type="Task", title=f"{src['name']}: Build ingest"))
        us.children.append(Item(type="Task", title=f"{src['name']}: Establish access to data source"))
        us.children.append(Item(type="Task", title=f"{src['name']}: Establish data store"))
        lz.children.append(us)
    epic.children.append(lz)

    # Feature: Raw
    raw = Item(type="Feature", title="Raw")
    for src in sources:
        us = Item(
            type="User Story",
            title=f"Raw: {src['name']}",
            description=f"Establish Raw layer for {src['name']}.",
        )
        us.children.append(Item(type="Task", title=f"{src['name']}: Build load and type 2 history"))
        us.children.append(Item(type="Task", title=f"{src['name']}: Build direct load without type 2 history for PII"))
        us.children.append(Item(type="Task", title=f"{src['name']}: Data store"))
        raw.children.append(us)
    epic.children.append(raw)

    # Feature: Enriched
    enr = Item(type="Feature", title="Enriched")
    for src in sources:
        wp = Item(
            type="Work Package",
            title=f"Enriched: {src['name']}",
            description=f"Build enriched entities for {src['name']}.",
        )
        for ent in src.get("entities") or []:
            wp.children.append(Item(type="Task", title=f"{src['name']}: {ent}"))
        enr.children.append(wp)
    epic.children.append(enr)

    # Feature: Util & platform
    util = Item(type="Feature", title="Util & platform")

    ws = Item(type="Work Package", title="Workspaces")
    ws.children.append(Item(type="Task", title="Landing zone workspace"))
    ws.children.append(Item(type="Task", title="Landing zone ETL"))
    ws.children.append(Item(type="Task", title="ETL workspace"))
    for area in business_areas:
        ws.children.append(Item(type="Task", title=f"{area} data workspace"))
    for area in business_areas:
        ws.children.append(Item(type="Task", title=f"{area} reporting workspace"))
    util.children.append(ws)

    ado = Item(type="Work Package", title="Azure DevOps & Deployment pipelines")
    ado.children.append(Item(type="Task", title="Azure DevOps repos & git"))
    util.children.append(ado)

    util.children.append(Item(type="Work Package", title="Roles and groups"))

    envs = Item(type="Work Package", title="Environments")
    envs.children.append(Item(type="Task", title="Dev environment"))
    envs.children.append(Item(type="Task", title="Test environment"))
    envs.children.append(Item(type="Task", title="Prod environment"))
    util.children.append(envs)

    epic.children.append(util)

    return epic


def _build_data_excellence_epic() -> Item:
    epic = Item(
        type="Epic",
        title="Data excellence",
        description=_load_data_excellence_html(),
    )
    features = [
        "1. Data culture",
        "2. Executive sponsor",
        "3. Business alignment",
        "4. Content ownership and management",
        "5. Content delivery scope",
        "6. Center of Excellence",
        "7. Governance",
        "8. Mentoring and user enablement",
        "9. Community of practice",
        "10. User support",
        "11. System oversight",
        "12. Change management",
    ]
    for name in features:
        epic.children.append(Item(type="Feature", title=name))
    return epic


# ----------------------------------------------------------------------------
# Tree helpers
# ----------------------------------------------------------------------------

def flatten(tops: list[Item]) -> list[Item]:
    """Walk the tree, attaching parent and depth, return in creation order (BFS)."""
    out: list[Item] = []
    queue: list[tuple[Item, Item | None, int]] = [(t, None, 0) for t in tops]
    while queue:
        node, parent, depth = queue.pop(0)
        node.parent = parent
        node.depth = depth
        out.append(node)
        for child in node.children:
            queue.append((child, node, depth + 1))
    return out


def print_tree(tops: list[Item], *, show_counts: bool = True) -> None:
    """Pretty tree for dry-run / preview."""
    def walk(node: Item, prefix: str, is_last: bool) -> None:
        branch = "└── " if is_last else "├── "
        status_glyph = {
            "created": "✓ ",
            "skipped": "= ",
            "failed": "✗ ",
            "pending": "",
        }.get(node.status, "")
        tag = f"[{node.type}] "
        tail = ""
        if node.ado_id:
            tail = f"  (#{node.ado_id})"
        elif node.status == "skipped":
            tail = "  (already exists)"
        elif node.status == "failed":
            tail = f"  ⚠ {node.error}"
        print(f"{prefix}{branch}{status_glyph}{tag}{node.title}{tail}")
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            walk(child, child_prefix, i == len(node.children) - 1)

    for i, top in enumerate(tops):
        walk(top, "", i == len(tops) - 1)

    if show_counts:
        flat = flatten(tops)
        by_type: dict[str, int] = {}
        for it in flat:
            by_type[it.type] = by_type.get(it.type, 0) + 1
        total = len(flat)
        summary = ", ".join(f"{by_type[t]} {t}" for t in sorted(by_type))
        print(f"\nTotal: {total} items ({summary})")


# ----------------------------------------------------------------------------
# Azure DevOps API client
# ----------------------------------------------------------------------------

class AdoClient:
    def __init__(self, org_url: str, project: str, pat: str,
                 area_path: str | None = None, iteration_path: str | None = None,
                 workers: int = 10):
        self.org_url = org_url.rstrip("/")
        self.project = project
        self.area_path = area_path
        self.iteration_path = iteration_path
        self.workers = workers
        token = base64.b64encode(f":{pat}".encode()).decode()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
        })

    # --- existing items lookup ------------------------------------------------

    def fetch_existing_titles(self) -> dict[str, int]:
        """WIQL → returns {title: id} for all non-removed items in the project."""
        wiql_url = f"{self.org_url}/{self.project}/_apis/wit/wiql?api-version=7.1"
        query = {
            "query": (
                "SELECT [System.Id] FROM WorkItems "
                f"WHERE [System.TeamProject] = '{self.project}' "
                "AND [System.State] <> 'Removed'"
            )
        }
        r = self.session.post(wiql_url, json=query, timeout=30)
        r.raise_for_status()
        ids = [w["id"] for w in r.json().get("workItems", [])]
        if not ids:
            return {}

        # Fetch titles in batches of 200
        titles: dict[str, int] = {}
        for i in range(0, len(ids), 200):
            batch_ids = ids[i:i + 200]
            url = f"{self.org_url}/{self.project}/_apis/wit/workitemsbatch?api-version=7.1"
            body = {"ids": batch_ids, "fields": ["System.Id", "System.Title"]}
            r = self.session.post(url, json=body, timeout=30)
            r.raise_for_status()
            for w in r.json().get("value", []):
                t = w["fields"].get("System.Title")
                if t:
                    titles[t] = w["id"]
        return titles

    # --- create one item ------------------------------------------------------

    def create_item(self, item: Item) -> None:
        """Create a single work item. Sets item.ado_id / item.status / item.error in place."""
        type_segment = urllib.parse.quote(f"${item.type}", safe="$")
        url = f"{self.org_url}/{self.project}/_apis/wit/workitems/{type_segment}?api-version=7.1"

        body: list[dict[str, Any]] = [
            {"op": "add", "path": "/fields/System.Title", "value": item.title},
        ]
        if item.description:
            body.append({"op": "add", "path": "/fields/System.Description", "value": item.description})
        if item.acceptance_criteria:
            ac_html = "<ul>" + "".join(f"<li>{c}</li>" for c in item.acceptance_criteria) + "</ul>"
            body.append({"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "value": ac_html})
        if self.area_path:
            body.append({"op": "add", "path": "/fields/System.AreaPath", "value": self.area_path})
        if self.iteration_path:
            body.append({"op": "add", "path": "/fields/System.IterationPath", "value": self.iteration_path})
        if item.parent and item.parent.ado_id:
            body.append({
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"{self.org_url}/_apis/wit/workitems/{item.parent.ado_id}",
                },
            })

        headers = {"Content-Type": "application/json-patch+json"}
        delay = 1.0
        for attempt in range(5):
            try:
                r = self.session.post(url, headers=headers, data=json.dumps(body), timeout=30)
            except requests.RequestException as e:
                item.status = "failed"
                item.error = f"Network error: {e}"
                return
            if r.status_code in (200, 201):
                data = r.json()
                item.ado_id = data["id"]
                item.ado_url = data.get("_links", {}).get("html", {}).get("href") \
                    or f"{self.org_url}/{self.project}/_workitems/edit/{data['id']}"
                item.status = "created"
                return
            if r.status_code == 429:
                # Rate limited — back off and retry
                time.sleep(delay + random.uniform(0, 0.5))
                delay *= 2
                continue
            # Any other error: record and stop
            item.status = "failed"
            try:
                msg = r.json().get("message") or r.text
            except ValueError:
                msg = r.text
            item.error = f"HTTP {r.status_code}: {msg[:300]}"
            return

        item.status = "failed"
        item.error = "Rate-limited after 5 attempts"


# ----------------------------------------------------------------------------
# Push orchestration (level-by-level parallel)
# ----------------------------------------------------------------------------

def push(items_flat: list[Item], client: AdoClient, existing: dict[str, int]) -> None:
    """Push items level by level. Within a level, creates run in parallel."""
    # Pre-mark items that already exist — skip them, reuse their ID for child linking
    for it in items_flat:
        if it.title in existing:
            it.ado_id = existing[it.title]
            it.status = "skipped"

    # Group by depth
    by_depth: dict[int, list[Item]] = {}
    for it in items_flat:
        by_depth.setdefault(it.depth, []).append(it)

    for depth in sorted(by_depth):
        to_create = [it for it in by_depth[depth] if it.status == "pending"]
        if not to_create:
            continue
        print(f"  Level {depth}: creating {len(to_create)} item(s)...", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=client.workers) as ex:
            list(ex.map(client.create_item, to_create))

        # If any parent failed, mark all pending descendants as skipped/failed
        # (to avoid orphan children at the next level)
        failed_ids = {id(it) for it in to_create if it.status == "failed"}
        if failed_ids:
            for it in items_flat:
                if it.status == "pending" and it.parent is not None and id(it.parent) in failed_ids:
                    it.status = "failed"
                    it.error = "Parent creation failed"
                    failed_ids.add(id(it))


def print_summary(items_flat: list[Item]) -> None:
    created = [it for it in items_flat if it.status == "created"]
    skipped = [it for it in items_flat if it.status == "skipped"]
    failed  = [it for it in items_flat if it.status == "failed"]

    print("\n" + "=" * 70)
    print(f"Summary: {len(created)} created, {len(skipped)} skipped (existed), {len(failed)} failed")
    print("=" * 70)

    if failed:
        print("\nFailed items:")
        for it in failed:
            print(f"  [{it.type}] {it.title}\n    → {it.error}")

    if created:
        print("\n| ID   | Type         | Title |")
        print("|------|--------------|-------|")
        for it in created:
            print(f"| {it.ado_id} | {it.type:<12} | {it.title} |")


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def _load_config(yaml_path: Path) -> dict[str, Any]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_credentials(config: dict, env_file: Path | None) -> tuple[str, str, str]:
    if env_file and env_file.exists() and load_dotenv:
        load_dotenv(env_file)
    proj_cfg = config.get("project") or {}
    org_url  = os.environ.get("AZDO_ORG_URL") or proj_cfg.get("org_url")
    project  = os.environ.get("AZDO_PROJECT") or proj_cfg.get("name")
    pat      = os.environ.get("AZDO_PAT")
    missing = [n for n, v in [("AZDO_ORG_URL", org_url), ("AZDO_PROJECT", project), ("AZDO_PAT", pat)] if not v]
    if missing:
        sys.stderr.write(f"Missing credential(s): {', '.join(missing)}\n")
        sys.stderr.write("Set them as env vars or in a .env file.\n")
        sys.exit(2)
    return org_url, project, pat


def main() -> int:
    p = argparse.ArgumentParser(description="Push a Pingala Datahub backlog to Azure DevOps.")
    p.add_argument("--yaml", required=True, type=Path, help="Path to backlog parameters YAML.")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Expand and print the tree only. No network calls.")
    mode.add_argument("--execute", action="store_true", help="Actually push to Azure DevOps.")
    p.add_argument("--env", type=Path, default=None, help="Path to a .env file with credentials.")
    p.add_argument("--workers", type=int, default=10, help="Parallel workers per level (default 10).")
    args = p.parse_args()

    if not args.yaml.exists():
        sys.stderr.write(f"YAML file not found: {args.yaml}\n")
        return 2

    config = _load_config(args.yaml)
    tops = expand_backlog(config)
    items_flat = flatten(tops)

    if args.dry_run:
        print("Dry run — no items will be created.\n")
        print_tree(tops)
        return 0

    org_url, project, pat = _resolve_credentials(config, args.env)
    proj_cfg = config.get("project") or {}
    area_path      = proj_cfg.get("area_path") or project
    iteration_path = proj_cfg.get("iteration_path") or project

    client = AdoClient(
        org_url=org_url, project=project, pat=pat,
        area_path=area_path, iteration_path=iteration_path,
        workers=args.workers,
    )

    print(f"Fetching existing items in {project}...", flush=True)
    try:
        existing = client.fetch_existing_titles()
    except requests.HTTPError as e:
        sys.stderr.write(f"Failed to fetch existing items: {e}\n")
        return 3
    print(f"  Found {len(existing)} existing item(s) — duplicates will be skipped.\n")

    print(f"Pushing backlog ({len(items_flat)} items total)...")
    push(items_flat, client, existing)

    print_summary(items_flat)

    # Non-zero exit if anything failed
    return 1 if any(it.status == "failed" for it in items_flat) else 0


if __name__ == "__main__":
    sys.exit(main())
