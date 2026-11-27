## Watchdog, 27 Nov 21:05

One stage is stopped: matrix. The rest are moving, or waiting correctly behind it.

| stage | state | progress | age |
|---|---|---|---|
| measure-google | moving | 213 of 214 | 0.3 h |
| matrix | stopped | 213 of 214 | 4.2 h |
| classify | waiting | behind matrix | 18.9 h |
| fix | moving | 5 attempt(s) in 3 h | 0.3 h |
| txt | moving | 208 clean, 6 failing | 1.3 h |

Trend, today's row against 26 Nov: docx open 60 to 59, txt failing 8 to 8 with no change, google 205 to 212, google clean 47 to 42. Today's row already existed, so progress.py appended nothing and there was nothing to commit.

Round phase: fix.

## Why matrix stopped, and what I did about it

The LibreOffice half is on no engine at all. gverify.py --matrix reads LibreOffice on it 0 of 206 pairs against Google on it 205 of 206. The engine moved after the last LibreOffice commit, and every gverify run since measured Google only. stage.py now reads classify, and the matrix stage fills only documents that have no LibreOffice result - with every document carrying one, nothing routes to that half again.

The fault was a contradiction between two paragraphs of GVERIFY-BRIEF.md: "every run does both" against "if it is not your stage, stop". I corrected the brief, with the measurement beside the correction, and named the tool: gverify.py --lo-stale 40. It is idempotent - it skips anything already stamped with the tree engine - so it costs nothing on a pass with no stale work.

I did not run it. Measuring is the gverify cron's job, and a second soffice pool beside a live fixer is the contention that loses conversions.

## What this run could not do

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation: cron list, cron runs and pause then resume are calls it cannot make. That is a missing tool, not a decision anyone has to make. It does not explain this stall - the gverify cron is firing, and its Google results committed four times since the engine moved.

The fixer slot is live, with a recent claim and a recent beacon, so round.py --release-fixer was not run. round.py --reopen refused: the phase is fix, not done.

## One instrument fault

Today's trend row overstates the corpus. It reads txt failing 8 and google 212 clean 42; progress.py --json reads txt failing 6 and google 206 clean 46. The .txt fix landed after the row was written, so "8 to 8 no change" is wrong. That row is a past row and was not edited.
