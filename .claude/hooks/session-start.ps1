$ErrorActionPreference = 'SilentlyContinue'
$ops = 'C:\Dev\ops'
$inprog = @(Get-ChildItem -Path (Join-Path $ops 'tasks\in-progress') -Filter *.md -File)
$open   = @(Get-ChildItem -Path (Join-Path $ops 'tasks\open') -Filter *.md -File)
$todoFile = Join-Path $ops 'TODO.md'
$todos = @()
if (Test-Path $todoFile) { $todos = @(Get-Content $todoFile | Where-Object { $_ -match '^\s*- \[ \]' }) }
Write-Output "[Continuity / M] Session start - run the workspace walk before the first reply."
Write-Output ("Open work: {0} in-progress, {1} open, {2} unprocessed todo(s)." -f $inprog.Count, $open.Count, $todos.Count)
Write-Output "Read C:\Dev\ops\tasks\in-progress and \open, the unchecked items in C:\Dev\ops\TODO.md, and the latest entry in C:\Dev\ops\log\sessions.md; then briefly surface open work and suggest a focus. (AGENTS.md > Continuity loop)"
