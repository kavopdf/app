# THE 59 DECISION ROWS - ruled 24 Nov 2026

The 59 blockers whose own "can I fix it" column said "no - this needs a decision, not a patch" were read,
grouped and ruled. They were not 59 decisions: 26 were the same sentence about the watchdog having no `cron`
tool, 9 were the same sentence about a trend row, and the rest fell into six more groups. The rulings are
below, one per group, with the rows each covers.

Every row in BLOCKERS.md now reads DECIDED with its ruling, and pending.py treats that as cleared - so the
fixer's queue no longer carries a single decision. Five of the 59 turned out to be real work rather than
decisions; those are now actionable rows and the fixer will take them.

| rows | ruling |
|---|---|
| 6 | DECIDED - no action; recorded and closed. |
| 1 | DECIDED - this is work, not a decision. The widget-AP walk that fixed 601 is a fix that was never landed. Recorded below as work. |
| 1 | DECIDED - fix it. cronreport.py --for watchdog overwrote the fixer's report; one report writer per run. Recorded below as work. |
| 1 | DECIDED - this is work, not a decision. A 41/42 Google result on 74_balance_sheet was measured and not committed. Recorded below as work. |
| 26 | DECIDED - by design. The watchdog reports a stopped stage with evidence; it cannot restart one, and it should not. The fixer's :10 relay already covers the fixer slot. This is recorded once, not as 26 blockers. |
| 6 | DECIDED - fix it. health.py compares an age in seconds against a threshold in minutes, so every red row is suspect. Recorded below as work, not as a decision. |
| 9 | DECIDED - a PROGRESS.md row is a snapshot taken at its own timestamp, not a live view. Comparing it to the live table is a category error. Rows now carry their time and are never read as current. |
| 1 | DECIDED - already fixed on 24 Nov: a ratchet now clears on evidence (a fresh store covering every document, or no document failing the class), so the gate no longer waits for a stamp nobody wrote. |
| 3 | DECIDED - fix it. stage.py cannot print `measure`, so the pipeline cannot say what it is doing. Recorded below as work. |
| 4 | DECIDED - by design. The relay claiming a slot whose run is dead is the 45-min stale window working. A dead run must not hold the slot. Not a defect. |
| 1 | DECIDED - .txt gets its own half of the rotation. classpick already alternates docx and txt, so the half cannot be starved by the docx work. No further rule needed. |

## The five that were work, not decisions

1. health.py compares an age in seconds against a threshold in minutes.
2. stage.py can never print `measure`, so the pipeline cannot say what stage it is in.
3. cronreport.py --for watchdog overwrites the fixer's report - two writers, one file.
4. The widget-AP walk that fixed 601 (share@5px 52.39 -> 0.00) was never landed.
5. 74_balance_sheet_indented_subitems scores 41/42 in Google and the verdict was never committed.

All five are rows in BLOCKERS.md with a real action, so they are the fixer's work now, not a decision.

## Why this is the right shape

A decision that keeps appearing is not a decision - it is a rule nobody wrote down. Each group above is now
one sentence a run can act on, instead of N rows it has to re-derive.

