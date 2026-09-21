"""Does what a session is producing match what it started with?

Every turn writes a heartbeat carrying a project and, if one is held, a task slug
(`ops/time/README.md` sec.2, ADR-003). The rollup turns those into F&O lines. When the tag
is dropped -- no task held, the held task belongs to another customer, the turn landed on a
customer node -- the line still gets written, just without the dimension the customer
requires, and nobody finds out until the month is entered.

`track_time.resolve()` already knows which of those happened; it simply never said. This
module is the sentence it should say, and the same judgement the dashboard renders for a
session that is still running.

Three ways a turn produces a line that cannot be typed:

  `no-task`    a customer that registers on task, worked with none held
  `elsewhere`  a task IS held, but on another customer -- so the tag was dropped and the
               work billed to the folder instead
  `node`       the turn landed on `customers/<Client>` itself, which has no `fno_code` and
               bills at customer level with Proj ID UNSET (decided 2026-07-28)

Anything on `Dev` or `own/` is silent: internal time is never entered in F&O, so it cannot
be short of anything.

Read-only. Pure stdlib, ASCII-only.
"""
import os

from . import fno
from .substrate import file_field
from .workspace import ROOT, customer_name, task_file

__all__ = ["KINDS", "project_id_of", "drift"]

KINDS = ("no-task", "elsewhere", "node")


def project_id_of(project, root=None):
    """The F&O Proj ID a project would put on a line, or "" when it has none.

    Mirrors rollup.project_id without importing it: this runs inside a per-turn hook, and
    the rollup pulls in the whole 15+5 model to answer one field lookup."""
    if project == "Dev":
        return "INTERNAL-RND"
    path = os.path.join(root or ROOT, project.replace("/", os.sep), "CLAUDE.md")
    return file_field(path, "fno_code") or ""


def task_dims(slug, root=None):
    """(activity, fno_task) a work-task lends to every line worked under it.

    Mirrors rollup.task_dims without importing it: this runs inside a per-turn hook, and
    the rollup pulls in the whole 15+5 model to answer two field lookups."""
    if not slug:
        return "", ""
    _, path = task_file(slug, root=root or ROOT)
    if not path:
        return "", ""
    return file_field(path, "activity") or "", file_field(path, "fno_task") or ""


def _is_node(project):
    """`customers/<Client>` with no project under it -- the customer node itself."""
    return project.startswith("customers/") and project.count("/") == 1


def drift(project, task_slug, held_slug, held_project, rules=None, sheet=None, root=None):
    """-> {kind, project, why, fix} for a turn about to be billed, or None when it is fine.

    `project` and `task_slug` are what the turn will actually record; `held_slug` and
    `held_project` are what the session started with.

    The Proj ID and Activity are resolved by `fno.resolve_dims`, the same call the entry
    page makes, so this cannot say a line is fine when the page will say it is short (or
    the reverse). One finding, most specific first -- a turn is reported once, not three
    times."""
    if not project or not project.startswith("customers/"):
        return None                       # Dev and own/ are never entered in F&O
    cust = customer_name(project)
    rules = rules if rules is not None else fno.rules(root or ROOT)
    sheet = sheet if sheet is not None else fno.companies(root or ROOT)
    key = fno.norm(cust) if cust else ""
    rule = rules.get(key)
    sheet_row = next((c for c in sheet if c["key"] == key), None)
    requires = set((rule or {}).get("requires") or ())

    if held_slug and held_project and held_project != project and not task_slug:
        return {
            "kind": "elsewhere", "project": project,
            "why": ("this turn bills to %s, but the task the session started with is on %s"
                    % (project, held_project)),
            "fix": "/switch-task to a task on %s, or work from that project's folder" % project,
        }

    # What this turn's line would actually carry, resolved the way the entry page resolves
    # it: the work-task's own values first, then the customer's default, then the sheet.
    # Holding a work-task is NOT enough -- `fno_task: none` is the convention for "no
    # DevOps work item yet", so a session can be correctly tagged and still produce a line
    # that cannot be typed.
    t_act, t_task = task_dims(task_slug, root)
    dims = fno.resolve_dims(project_id_of(project, root), t_act, rule, sheet_row)
    task_id = fno.value_or_blank(t_task)

    if _is_node(project):
        return {
            "kind": "node", "project": project,
            "why": ("this turn bills to the %s customer node, which is not a project -- it "
                    "goes in at customer level with Proj ID %s"
                    % (cust, dims["proj_id"] or "UNSET")),
            "fix": "work from one of %s's project folders, or /switch-task to one of its tasks"
                   % cust,
        }
    if not dims["proj_id"]:
        return {
            "kind": "no-task", "project": project,
            "why": "%s has no fno_code and the sheet has nothing usable, so the line has "
                   "no Proj ID" % project,
            "fix": "set fno_code on the project from the Time page",
        }
    if "task" in requires and not task_id:
        return {
            "kind": "no-task", "project": project,
            "why": (("the work-task held (%s) has no DevOps id yet, and %s registers on "
                     "task" % (task_slug, cust)) if task_slug
                    else "%s registers on task and no task is held" % cust)
                   + ", so the line cannot be entered",
            "fix": ("put the DevOps id on that work-task -- Projects, under %s" % cust)
                   if task_slug else "/switch-task to the task this work belongs to",
        }
    if "activity" in requires and not dims["activity"]:
        return {
            "kind": "no-task", "project": project,
            "why": ("%s registers on activity and nothing supplies one -- not the work-task, "
                    "not the customer default, not the sheet -- so the line cannot be entered"
                    % cust),
            "fix": "set fno_activity on the customer, or the activity on the work-task",
        }
    return None
