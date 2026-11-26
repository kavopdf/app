# P2W Watchdog - Run Report

**26 Nov 2026 · 09:24 IST**

> Nothing is stopped.

## Stages


| stage | state | progress | age |
|:--|:--|--:|--:|
| measure-google | moving | 67 of 213 | 0.5 h |
| matrix | done | 213 of 213 | 0.2 h |
| classify | waiting |  | 2.9 h |
| fix | moving | 3 attempt(s) in 3 h | 0.9 h |
| txt | moving | 205 clean, 8 failing | 2.8 h |

## Trend

| | 2026-11-25 | 2026-11-26 | |
|:--|--:|--:|:--|
| .docx open | 59 | **59** | no change |
| .txt failing | 9 | **8** | -1 |
| Google measured | 213 | **208** | -5 |
| Google clean | 42 | **42** | no change |

## What this pass did

* Read health.py, health.py --stalled, stage.py, progress.py, round.py --phase and status.py.
* **The fix slot was held by a dead run** - released with round.py --release-fixer --force. See BLOCKERS.md.

## What was stopped, and what this pass did about it

The read this pass opened on found fix stopped: 3 attempt(s) in 3 h, age 0.9 h, on a run still marked
running that had not beaconed and was holding the fix slot. Every other row was healthy - measure-google
moving at 67 of 213, matrix done, classify waiting because the measurement it groups is still incomplete,
txt moving at 205 clean and 8 failing.

The second read, taken before this report was written, found the same claim past the fixer's stale window
and still held, with no attempt recorded against it and no engine change since it was taken. A window that
has passed and freed nothing is a dead run, so the slot was released with round.py --release-fixer --force
and the reason went into BLOCKERS.md. The read taken after that release is the one this report is
generated from, which is why it now says nothing is stopped.

## The flat .docx axis, decided again on today's evidence

.docx open reads 59 in every committed row of the trend including today's, and google clean is 42 to 42,
so that axis has not moved in more than a day. Nothing was parked. The class is not what is failing: the
gate charges a full corpus re-score to every change, so a change is measured, reverted and never lands.
What replaces it is a scope keyed on the documents a change can actually move. Today's evidence
strengthens that rather than reopening it - the .txt axis moved, 9 to 8, on a change whose .docx output
was unchanged and which therefore needed no re-score. Overturned by: one engine change that lands and
moves .docx open.

## The instrument, and the one thing this pass could not do

Google measured reads 208, which looks like documents lost against the corpus of 213. It is not:
measure-google is mid-pass at 67 of 213, so the 208 is a settled count from a measurement still being
rewritten. The number to read is google clean, and it is flat.

No cron was recreated, paused or resumed, because this pass has no cron tool at all. It cannot read
next_fire_at, cannot read a run list, and cannot see a cron left paused - so a cron that is enabled but
not firing stays invisible to it. That is written into BLOCKERS.md as a missing tool, with the exact
calls it would have made, and not as a decision for a person to make.

