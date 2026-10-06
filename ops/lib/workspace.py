"""Where things are in the workspace, and what a project rolls up to.

`customers/<client>/<project>` and `own/<project>` are the two project shapes; a
project is any folder with its own AGENTS.md (legacy: CLAUDE.md). Before this module each consumer walked
the tree itself, so adding a shape meant finding every walker.

Read-only. Pure stdlib, ASCII-only.
"""
import glob
import os

__all__ = ["ROOT", "customer_dirs", "project_dirs", "billing_entity", "customer_name",
           "task_file", "TASK_STATES", "IDENTITY_FILES", "identity_file"]

ROOT = os.environ.get("DEV_WORKSPACE", r"C:\Dev")

TASK_STATES = ("open", "in-progress", "done", "cancelled")

# The file that holds a folder's Identity block. AGENTS.md is current; CLAUDE.md is read
# until every project has been renamed.
IDENTITY_FILES = ("AGENTS.md", "CLAUDE.md")


def identity_file(d):
    """The identity file in folder `d`: AGENTS.md, else the legacy CLAUDE.md. A folder with
    neither gets the AGENTS.md path, so callers that test existence see it missing."""
    for name in IDENTITY_FILES:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return os.path.join(d, IDENTITY_FILES[0])


def customer_dirs(root=None):
    """-> [(name, dir)] for every folder under customers/, sorted by path."""
    base = root or ROOT
    out = []
    for d in sorted(glob.glob(os.path.join(base, "customers", "*"))):
        if os.path.isdir(d):
            out.append((os.path.basename(d), d))
    return out


def project_dirs(root=None, branch=None):
    """-> [(key, dir)] for every project folder, sorted by path.

    A project is a folder with an identity file (`identity_file`), under `customers/<client>/` or `own/`. The
    key is the workspace-relative path with forward slashes -- the same string the
    heartbeats, the task files and the F&O dimension lookup all use for a project.

    `branch` narrows the walk: None is everything, "own" is the internal projects, and
    a client name is that client's. The workspace root itself ("Dev") is not a project
    and is never returned."""
    base = root or ROOT
    if branch == "own":
        pattern = [os.path.join(base, "own", "*")]
    elif branch:
        pattern = [os.path.join(base, "customers", branch, "*")]
    else:
        pattern = [os.path.join(base, "customers", "*", "*"),
                   os.path.join(base, "own", "*")]
    out = []
    for d in sorted(p for g in pattern for p in glob.glob(g)):
        if not os.path.isfile(identity_file(d)):
            continue
        out.append((os.path.relpath(d, base).replace("\\", "/"), d))
    return out


def billing_entity(project):
    """The entity a project bills to: `customers/<client>`, else the project itself.

    A day cap only means something at this grain -- "you billed me 18 hours in one day"
    is a statement about a client, not about a folder. Internal work is its own entity
    so it is never merged with a client."""
    parts = project.split("/")
    return "/".join(parts[:2]) if project.startswith("customers/") and len(parts) > 1 else project


def customer_name(project):
    """The bare client name, or None for internal work.

    The None is load-bearing: the value model uses it to decide whether a record is
    subject to the customer cap at all. `billing_entity` never returns None, because
    its caller needs a grouping key for every project."""
    parts = project.split("/")
    if parts[0] == "customers" and len(parts) > 1:
        return parts[1]
    return None


def task_file(slug, states=TASK_STATES, root=None):
    """-> (state, path) for a task slug, or (None, None). Searched in `states` order."""
    base = root or ROOT
    for state in states:
        p = os.path.join(base, "ops", "tasks", state, slug + ".md")
        if os.path.exists(p):
            return state, p
    return None, None
