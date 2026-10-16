---
id: eval-20261016-capture-assistant-mojibake
ts: 2026-10-16T12:00:00Z
type: evaluative
scope: workspace
source: sentinel review at /log, session a007db1c
tags: [memory, capture_turn, encoding, sentinel, secret]
status: distilled
description: "Sentinel 10-15/16: assistant bodies with non-ASCII are double-encoded (mojibake) while user lines are clean (inference: assistant text decoded as cp1252 in capture_turn.py); a pasted ServiceNow password was captured verbatim and redacted at /log"
---

- **Encoding:** every assistant body with Danish or arrow characters in `daily/2026-10-15.md`
  and `daily/2026-10-16.md` reads `Ã¸`, `â†’` etc.; the user lines are correct. Inference: the
  capture path decodes the assistant text as cp1252. Not fixed this session.
- **Secret:** the ServiceNow PDI admin password Niels pasted on 2026-10-16 was captured verbatim
  in `daily/2026-10-16.md`. Redacted at /log before the workspace commit; not in git history.
  The capture hook has no secret filter.
- **Pairing:** several 10-15 records still pair a body with the wrong user line (after the
  2026-10-15 hook fix, records before it).
