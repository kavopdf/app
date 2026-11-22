## Watchdog - run report

Corpus 213. Read at 18:11 IST, 22 Nov 2026.

## The five stages

| stage | state | progress | age |
|---|---|---|---|
| measure-google | done | 213 of 213 | 11.9 h |
| matrix | done | 213 of 213 | 18.2 h |
| classify | superseded | - | 11.3 h |
| fix | moving | - | 0.6 h |
| txt | superseded | 197 clean, 16 failing | 19.6 h |

The fix row says moving only because this pass released the claim behind it. The run that held it
died at 17:36:55 inside the report writer and never committed or released; the timeline has no beat,
no claim and no release after that line until this pass's own tools.

## The trend

| measure | 21 Nov | today |
|---|---|---|
| docx open | 59 | 59 |
| txt failing | 23 | 16 |
| google | 192 | 192 |
| google clean | 6 | 23 |

Today's row was already written by an earlier pass, so nothing was appended. The .txt half moved;
the .docx half has now been flat for two rows.

## What this pass changed

The fixer slot was held by a dead run, so I released it, forced past the pending gate. The release
printed the claim's age and the attempt it had recorded.

I then moved the round back to measure with the remeasure call the 15:09 blocker had deferred to
this pass, now that the slot was free. The reason is not a guess: the live docx fingerprint is
226f7f2df3013ad7 and the table is stamped 6c6cf642e13b7ed2, so the .docx table is a measurement of
an engine that no longer exists - the engine last changed at 462353f9 on 21 Nov. That is why 59
cannot move. The round number, the attempt ledger and the hypothesis ledger are untouched, and the
baseline cron re-measures the corpus on 462353f9.

That call printed an empty engine id, which is the one thing it exists to record: its git call ran
from the tools directory, so the pathspec matched nothing. Fixed in round.py to run from the
repository root and verified in isolation.

## Blockers

This watchdog has no cron tool, so a paused or zombie cron cannot be moved by automation. That is a
missing tool, not a decision for a person. It matters this pass: three scheduled fires - the fixer
slot, the baseline and the relay - produced no claim and no timeline line at all. A stage stopped
because nothing fires looks exactly like a stage with nothing to do. The exact calls I would have
made, and the two fixer ids that must not be deleted as duplicates, are in BLOCKERS.md.

All three rows for this pass are in BLOCKERS.md. What would overturn the remeasure: a baseline pass
on 462353f9 that reproduces 59.
