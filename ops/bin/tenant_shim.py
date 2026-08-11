"""Tenant-scoped CLI credentials - resolve cwd to a customer node, then run the real
CLI against that customer's isolated credential store.

Why this exists
---------------
`fab` hardcodes its state directory to `expanduser("~/.config/fab/")`
(fabric_cli/core/fab_state_config.py:13-17). There is no --config-dir flag and no
config-dir environment variable, so one Windows user gets one Fabric tenant: two
sessions on different tenants overwrite each other's auth.json and cache.bin. On
2026-07-31 a `fab ls` in a Matas session returned the Carl Ras estate, which is what
produced Guardrail 11.

Windows' ntpath.expanduser resolves `~` from USERPROFILE (it never consults HOME), so
pointing USERPROFILE at a per-customer directory gives each customer its own auth.json
and MSAL token cache. USERPROFILE is a blunt instrument - it moves `~` for everything
in the process, including git, gh and az - so it is set ONLY in the child process that
runs the CLI. The calling shell is never modified.

Resolution: cwd at or under C:\\Dev\\customers\\<Name> -> that customer's profile.
Anything else (C:\\Dev itself, own\\...) -> no redirection, i.e. the real ~/.config/fab,
which holds Niels's own Pingala identity. Failing to resolve therefore falls back to the
DEFAULT profile, not to whatever was authenticated last.

This makes the common case correct; it does not make it certain. See Guardrail 11 in
AGENTS.md - a wrong-tenant listing still looks like an answer.

Invoked by the shims in ~/.local/bin (installed by ops/bin/heal-repos.ps1):
    python tenant_shim.py --shim-dir <dir> fab <args...>

ASCII only (Conventions / Guardrail 9).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePath

CUSTOMERS = Path("C:/Dev/customers")

# tool -> subdirectory of %LOCALAPPDATA% holding that tool's per-customer profiles.
# fab only, deliberately. az has its own AZURE_CONFIG_DIR and would need a shim dir
# ahead of PATH index 2 (C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin); pac has
# native named auth profiles. Both stay out until there is a real need.
TOOLS = {
    "fab": "fab-profiles",
}


def resolve_customer(cwd):
    """Return the customer node name if cwd is at or under C:/Dev/customers/<Name>."""
    try:
        rel = PurePath(os.path.relpath(str(cwd), str(CUSTOMERS)))
    except ValueError:
        # different drive - relpath raises rather than returning a parent walk
        return None
    parts = rel.parts
    if not parts or parts[0] == os.pardir or parts[0] == ".":
        return None
    return parts[0]


def real_exe(tool, shim_dir):
    """Find the real tool on PATH, skipping the directory the shim lives in.

    Skipping by directory (not by name) is load-bearing: without it the shim finds
    itself and recurses until the caller times out.
    """
    dirs = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d:
            continue
        try:
            if Path(d).resolve() == shim_dir:
                continue
        except OSError:
            continue
        dirs.append(d)
    return shutil.which(tool, path=os.pathsep.join(dirs))


def main(argv):
    # Belt and braces against the recursion above: if we are already inside a shim,
    # refuse rather than spawn another level.
    if os.environ.get("TENANT_SHIM_ACTIVE"):
        sys.stderr.write("tenant_shim: re-entry detected, aborting\n")
        return 126

    shim_dir = Path(__file__).resolve().parent
    if len(argv) >= 2 and argv[0] == "--shim-dir":
        shim_dir = Path(argv[1]).resolve()
        argv = argv[2:]

    if not argv or argv[0] not in TOOLS:
        sys.stderr.write("tenant_shim: usage: tenant_shim.py [--shim-dir D] <tool> [args]\n")
        return 2

    tool = argv[0]
    args = argv[1:]

    exe = real_exe(tool, shim_dir)
    if exe is None:
        sys.stderr.write("tenant_shim: cannot find the real '%s' on PATH\n" % tool)
        return 127

    env = dict(os.environ)
    env["TENANT_SHIM_ACTIVE"] = "1"
    # fab dies with a charmap codec error printing its own checkmark otherwise.
    env["PYTHONIOENCODING"] = "utf-8"

    # Precedence: explicit override > cwd's customer > default profile.
    # ops/bin/fab-as.ps1 names a customer explicitly and calls bare `fab`, which this shim
    # now shadows. Without this override, `fab-as.ps1 Carl-Ras ls` run from a Matas folder
    # would resolve to Matas and silently ignore the customer the user asked for.
    home = os.environ.get("TENANT_PROFILE_HOME")
    if not home:
        customer = resolve_customer(Path.cwd())
        if customer:
            home = str(Path(os.environ["LOCALAPPDATA"]) / TOOLS[tool] / customer)

    if home:
        Path(home).mkdir(parents=True, exist_ok=True)
        env["USERPROFILE"] = home
        env["HOME"] = home

    return subprocess.call([exe] + args, env=env)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
