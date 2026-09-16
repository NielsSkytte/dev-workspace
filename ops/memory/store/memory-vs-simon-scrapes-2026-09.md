---
id: memory-vs-simon-scrapes-2026-09
ts: 2026-09-16T14:45:00Z
type: semantic
scope: workspace
source: /log
tags: [memory, comparison, simon-scrapes, recall, injection]
description: Compared ops/memory with Simon Scrapes' 2026 memory video (storage / injection / recall + team RLS): even on storage and injection mechanics, behind on recall (grep only) and on injection content selection (alphabetical snapshot), and his model does not address project resume, which our card + task Progress now covers.
status: distilled
---

Source: youtube.com/watch?v=H9BUkgDf5Y4, captions pulled with yt-dlp (`--write-auto-sub --sub-format
json3`) on 2026-09-16. His three legs: storage (a hook captures every turn), injection (a capped
snapshot at session start), recall (semantic search over the store, scoped per team member with row-level
security). Ours: storage matches (capture_turn.py per turn to ops/memory/daily), injection matches the
mechanics (build_snapshot.py, 4000 chars) but selects records alphabetically, not by relevance or recency
(flaw, parked as a Tier A fix), recall is grep over ops/memory/store only. Neither model on its own answers
"start a new session on any project and be up to date on the work": that is project knowledge (goal,
what we are working on, what we tried, what is next), which lives in the project card and the task
Progress blocks, not in the memory store. The store keeps durable facts and decisions; the card keeps
state; the session log keeps history.
