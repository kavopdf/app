# Watchdog — 25 Nov 2026, 12:05 IST

Two stages are stopped: classify and txt. The fixer is moving, and Google clean rose from 35 to 42 against yesterday's row.

## Stages

| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | done | 213 of 213 | 0.1 h |
| matrix | done | 213 of 213 | 32.3 h |
| classify | stopped | | 10.6 h |
| fix | moving | 7 attempt(s) in 3 h | 0.2 h |
| txt | stopped | 199 clean, 14 failing | 26.3 h |

## Trend

Today's row was stale against the live tables, so progress.py --amend rewrote it from them: docx open 59, txt failing 14, Google 213 measured and 42 clean. Against 24 Nov: docx open 59 to 59, no change on its sixth consecutive row; txt failing 14 to 14; Google 190 to 213 measured, clean 35 to 42.

## Round

The phase is fix, so the fixer runs until no class is OPEN. No cron was paused, resumed, recreated or deleted: this watchdog has no cron tool, so the platform steps of the brief did not run.

## Why those two rows are stopped

classify: the younger class table was committed yesterday at 19:59 UTC and gverify has committed results since, so the classifier cron has produced no table for ten hourly slots. stage.py names classify on its own - the table is older than the results.

txt: its table is 26.3 h old against engine inputs 4.5 h old. I re-scored the corpus on this tree with restamp_txt.py --report: 213 scored, none newly clean, none newly failing, 213 unchanged. The 14 are real failures on the current engine, not a stale table.

New this pass: the baseline cron is silent as well. Its LibreOffice output last changed 32.3 h ago, and health.py cannot flag it because matrix reads done at 213 of 213. txt is the baseline's other output, so the red txt row and the silent baseline are one fact, and it is the one no tool here can move.

## Decision on the txt stall

txt is past 24 hours with nothing moved, so this pass decided rather than deferred: no class parked, no approach replaced, instrument left alone. The restamp is the evidence - the table measures today's engine, and the failures have named mechanisms, the ligature identity in the word-invention check against a corrupt page ToUnicode and the Effra reference face in the word-accuracy check. The fixer is moving, 7 attempts in 3 h, its last three commits landing findings rather than reverting engine patches.

What would overturn it: a restamp that reports documents newly failing; two further attempts on the word-invention class ending with an empty file list and no explanation; or a pending queue back above the 26 the 18:12 pass set as its line, which it has since fallen below.

## Written to BLOCKERS.md

One row each: the two stopped stages, the silent baseline cron, the missing cron tool with the exact calls I would have made and the ids from HEALTH-BRIEF's table, and a slot-release write I made by mistake on an already-free slot, which I reverted so the fixer's own release stands.
