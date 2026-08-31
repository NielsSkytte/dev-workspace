# Bounded turns

Every heartbeat that ran past the rollup's bound, with what the transcript said
was happening inside it. Written by `value.py --stalls` at /log, because transcripts
do not survive. The timesheet is corrected by hand; note the decision in Verdict.

| Key | Date | Session | Start | Span h | Busy min | Largest gap min | Counted h | Error | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| `2026-08-27/ec7d4a00/18:54:06Z` | 2026-08-27 | ec7d4a00 | 20:54 | 22.21 | 19.4 | 767 | 1.00 | Command did not complete within its 120s timeout and was moved to the background (ID: b0dqkfbes). Output is being writte | |
| `2026-06-25/77bf7026/02:53:50Z` | 2026-06-25 | 77bf7026 | 04:53 | 3.65 | - | - | 1.00 | no transcript | |
| `2026-06-29/e0072224/06:38:37Z` | 2026-06-29 | e0072224 | 08:38 | 1.24 | - | - | 1.00 | no transcript | |
| `2026-07-03/145cec04/10:56:38Z` | 2026-07-03 | 145cec04 | 12:56 | 1.11 | - | - | 1.00 | no transcript | |
| `2026-07-07/ec3422aa/10:34:35Z` | 2026-07-07 | ec3422aa | 12:34 | 1.52 | - | - | 1.00 | no transcript | |
| `2026-07-23/36359848/07:25:03Z` | 2026-07-23 | 36359848 | 09:25 | 2.20 | - | - | 1.00 | no transcript | |
| `2026-08-03/5bbffdc6/08:23:46Z` | 2026-08-03 | 5bbffdc6 | 10:23 | 5.66 | 9.3 | 335 | 0.00 | - | **Waiting - duplicate, dropped in full** (2026-08-31). Not a long turn: the same session holds the real turn `10:23:46 -> 10:24:39` (0.9 min), and this record shares its `ts_start`. No transcript event between 10:27:57 and 16:03:22; the duplicate was written when a `!`-bash-input re-Stopped the session at 16:03 with no `UserPromptSubmit` to refresh the start. Timesheet 2026-08-03 corrected 14.25 -> 8.75 h. Root cause fixed in `track_time.py` the same day. |
| `2026-08-20/45041831/07:10:41Z` | 2026-08-20 | 45041831 | 09:10 | 5.42 | 20.2 | 310 | 0.42 | - | **Waiting - AskUserQuestion unanswered** (2026-08-31). The turn genuinely never ended: question issued 09:15:55, answered 14:25:44. Reconstructed as the two real activity windows `09:10:41-09:15:55` and `14:25:44-14:36:03` rather than bounded at 60 min, which would keep 65 min for a 5 min stretch and drop the 11 min worked after the answer. Timesheet 2026-08-20 corrected 12.25 -> 7.25 h, all on the internal Dev line. Root cause fixed by the PreToolUse/PostToolUse wait deduction the same day. |
