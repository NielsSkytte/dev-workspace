$ErrorActionPreference = 'SilentlyContinue'

# Injection: capped memory snapshot (built by Python from ops/memory/store; ASCII output).
# Native Claude auto-memory is disabled (autoMemoryEnabled:false), so this is the only injection.
$snap = & python "C:\Dev\.claude\hooks\build_snapshot.py" 2>$null
if ($snap) {
    Write-Output ($snap -join "`n")
    Write-Output ""
}

# The workspace walk / day brief is emitted by session_task.py (daybrief_hook.py) since 2026-09-16;
# this script only injects the memory snapshot.
