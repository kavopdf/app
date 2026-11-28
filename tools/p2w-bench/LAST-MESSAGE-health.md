## Watchdog - 28 Nov 09:06 IST

**Nothing is stopped.** `health.py --stalled` exits 0. Corpus 214.

| stage | state | age |
|:--|:--|:--|
| measure-google | done, 214 of 214 | 3.5 h |
| matrix | done, 214 of 214 | 1.7 h |
| classify | superseded | 1.1 h |
| fix | moving, 5 attempt(s) in 3 h | 0.1 h |
| txt | moving, 208 clean, 6 failing | 2.3 h |

Matrix is the change since the last pass: it read stopped and now reads 214 of 214 with
214 of 214 results on the engine. The trend row is docx open 116, txt failing 6 of 214, google 206,
google clean 48 - docx open and txt failing unchanged from the previous row, google clean up 2, with the
fixer at 5 attempt(s) in 3 h beside it. Today's row already existed, so nothing was appended and nothing
was invented. Round phase is fix, so the reopen did not fire; the fixer claim is under an hour old and
still producing attempts, so no slot was released.

No cron was inspected, recreated, paused or resumed: this watchdog's tool list carries no cron
operation, so a paused or zombie cron cannot be moved by automation. Recorded in BLOCKERS.md with the
exact calls.
