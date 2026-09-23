# Running this on another machine, and running it by hand

## 1. What the system actually consists of

Three layers. Only the first two are load-bearing.

| Layer | Files | If you delete it |
|---|---|---|
| **The model** | `ops/time/README.md` - the spec and the by-hand recipe | the system is gone |
| **The data** | `ops/time/heartbeats/`, `timesheet/`, `lines/`, `value/`, and the five registers | hours and decisions are gone (the derived parts rebuild, the registers do not) |
| **The accelerators** | `rollup.py`, `value.py`, `bonus.py`, `ops/bin/linedesc.py`, the dashboard, the hooks, the slash commands | nothing is lost but speed - the model still runs by hand |

That split is deliberate: the harness may be deleted without losing knowledge or capability. If you
adopt this under a different LLM, port the accelerators and keep the model file as written.

## 2. What to install

1. **Copy the substrate:** `ops/time/README.md`, `rollup.py`, `value.py`, `bonus.py`,
   `ops/bin/linedesc.py`, and `ops/lib/` (`attribution.py`, `fno.py`, `fnotasks.py`,
   `heartbeats.py`, `lines.py`, `noinvoice.py`, `sessionlines.py`, `substrate.py`,
   `workspace.py`). Python, no third-party dependencies.
2. **Copy the capture hook** (`.claude/hooks/track_time.py`) and the session-task hook
   (`.claude/hooks/session_task.py`).
3. **Register the hooks in two places.** Claude Code settings **do not cascade**: hooks registered
   only in the workspace's `.claude/settings.json` never fire for sessions rooted *below* the
   workspace, which is most sessions. Register them in the **user-level** `~/.claude/settings.json`
   as well, with **byte-identical command strings** - Claude Code deduplicates identical strings, so
   the dual registration runs once per event. If they diverge, both run in parallel: harmless for
   hours, because the rollup merges overlapping intervals, but the memory-capture hook's daily-file
   rewrite is not parallel-safe. The scripts self-guard to working directories under the workspace
   root. This cost two customers' sessions their tracking before it was found.
4. **Register the capture hook on the question tool too**, with a matcher on that tool name - not on
   every tool call. Without it an unanswered question is billed as work (310 of a 325-minute
   heartbeat); with a matcher that is too broad you get one process per tool call.
5. **Set the workspace root** and the F&O codes. Every project carries `fno_code` in its own
   `CLAUDE.md` identity block; every customer node carries `fno_requires`, and optionally
   `fno_billable`, `fno_description`, `fno_firma`, `fno_code`, `fno_activity`.
6. **Set up the backup.** The data directories are gitignored, so the git remote does not protect
   them. A plain mirror, run at every review gate:

   ```
   robocopy "C:\Dev\ops\time" "%OneDrive%\Backup\Dev-ops-time" /E /R:2 /W:5 /NP
   ```

   From Git Bash, prefix it with `MSYS_NO_PATHCONV=1` - MSYS rewrites the `/E` switch into a path
   (`Invalid Parameter #3 : "E:/"`, exit 16). Found when the backup step failed silently under
   `>/dev/null`: **check the exit code, do not assume.** Robocopy 0-7 is success.

## 3. What is machine-specific

| Thing | Where |
|---|---|
| The workspace root (`C:\Dev`) | hooks, the scripts' path guards, the dashboard |
| The dashboard port (`127.0.0.1:8787`) | the dashboard, the entry runbook's links |
| The transcript location (`~/.claude/projects/**/*.jsonl`) | `value.py` only - this is the one tool-specific dependency |
| The F&O tenant URL and company codes | the entry runbook |
| Scripts are **ASCII-only** | Windows PowerShell 5.1 would fail on non-cp1252 output, and the hooks fail silent, so the error would be swallowed. Task titles do carry such characters, so hook output is ASCII-sanitised on purpose. |

## 4. The commands

| Command | Does |
|---|---|
| `python ops/time/rollup.py` | finalize every complete past day that has no day file yet, then run the coverage check |
| `... --preview` | today's live tally; writes nothing |
| `... --week [YYYY-Www]` / `--month [YYYY-MM]` | by-date report (work time, not entry hours); writes nothing |
| `... --merge` | consolidate sub-2 h entries per week onto one day |
| `... --check [YYYY-Www]` | coverage vs the full-period target; unaccounted workdays; days under a full day |
| `... --topup <period>` | dry run of a deliberate close; `--apply` writes |
| `python ops/time/value.py` | derive value records for complete days |
| `... --stalls [--date D]` | why a bounded turn ran long; appends to `stalls.md` |
| `python ops/bin/linedesc.py <date>` | prepare the material for line descriptions; prints, never writes |
| `... --check <YYYY-MM>` | which lines have no description |
| `python ops/time/bonus.py <hours> --basis <n>` | the faktureringsprocent tier and the distance to the next boundary |

Under the Claude harness these are wrapped as `/time`, `/switch-task`, `/log` and `/fno`. The
commands are the accelerator; the table above is the system.

## 5. The whole model by hand

No scripts, no LLM. This is what the accelerators do.

1. **Capture.** Per work session, append a line per turn: start time, end time, and the project of
   the folder you are in (or the task you are on). UTC.
2. **Attribute.** The active task decides the project; the folder is the fallback. A task may
   override the folder only within the same customer, and never for internal work.
3. **Roll up.** Per (local date, project, task): sort the intervals, merge any pair whose gap is
   <= 15 min, discard the gaps above that, add 5 min to each stretch, sum, round to 0.25 h, floor
   at 0.5 h. Bound any single turn at 60 min and write down which one you bounded.
4. **Write the day.** A table of `Project | Proj ID | Activity | Task | Hours | Billable`, one row
   per F&O line, into `timesheet/<YYYY-MM>/<date>.md`. Eyeball it. Correct it here, never in the
   heartbeats.
5. **Describe each line** in one sentence, from what actually happened. Blank if the evidence does
   not support one.
6. **Value, if you want the ceiling.** Per turn: active minutes excluding gaps over 5 min, times the
   tier multiplier from `value-and-entry-figure.md`; sum per project per day.
7. **Check the period.** 7.5 h x workdays, less absence. Answer every unaccounted workday into
   `absence.md`. Close a short period deliberately, never past the weighted evidence.
8. **Enter.** One journal per ISO week per company, the fields in `fno-entry.md`, reconcile per
   journal, then Godkendelse -> Finished. Never Bogfoer.
