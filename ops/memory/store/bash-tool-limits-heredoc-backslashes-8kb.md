---
id: bash-tool-limits-heredoc-backslashes-8kb
ts: 2026-09-16T14:45:00Z
type: procedural
scope: workspace
source: /log
tags: [claude-code, bash-tool, gotcha, windows]
description: Claude Code's Bash tool on this machine fails on commands over about 8 KB and de-escapes backslash sequences inside heredocs; write large or backslash-heavy content with the Write tool and use forward slashes or bytes() in heredoc Python.
status: distilled
---

Measured 2026-09-16 while writing the Carl Ras card and the /task command text:
- a 9.5 KB heredoc failed with "unexpected EOF" - the command length limit is about 8 KB. Write the
  file with the Write tool instead; keep heredocs small.
- inside a heredoc, Python string literals had their backslashes de-escaped before Python saw them:
  `C:\Dev\ops\bin` became `C:\Dev\ops<backspace>in` (a `\b`), with a SyntaxWarning on `\D`. Fix
  applied at byte level (`raw.replace(bytes([8]), bytes([92, 98]))`). Rule: no Windows paths with
  backslashes in heredoc Python; use forward slashes, `os.path.join`, or the Write tool.
- hook test JSON piped from a heredoc with `"cwd":"C:\\Dev"` silently became invalid and the hook
  no-op'ed; use `"C:/Dev"` in test input.
- `bc` is not installed in this Git Bash; use awk. The shell cwd drifts after `cd` in a compound
  command; use absolute paths.
