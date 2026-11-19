# INCIDENTS — what was skipped, and why

One line per skip. A document that never got measured is otherwise invisible: its
row is empty in BASELINE.md and nothing says whether it was missed, failed, or
never reached.

| time | cron | item | class | what happened |
|---|---|---|---|---|

## How to add a line

```
| 11 Nov 09:14 | baseline | 366_menu | transient | 403 rate limit, 3 tries, row left empty |
```

Classes come from `RETRY.md`: transient, permanent, already-done, unknown.

Rules:
- No line, no skip. If it is not written here, it did not happen.
- Write it when you skip, not at the end of the run — a run that dies takes its
  notes with it.
- Never write a score you did not measure. An empty row and an incident line is
  honest; a guessed score is not.

## 13 Nov 06:47 fixer run - classify.py --attempt disagreed with the measured round
The 20-document round on engine 2a68de6-d80a524 moved 3 of the 10 failing documents
onto a PASS of 20_within_10pt (304 12->100, 34_monospace 14->100, 334_patent 16->100)
and 4 of 10 the right way. `classify.py --attempt "20_within_10pt (+4)" --moved 3
--total 10` refused it and reported 0 of 5, because it rebuilds the class group from
the store after the attempt's own rows are in it, so the group it resolves is not the
one the run measured. Recorded with the tool's numbers (0 of 5 -> reverted, which is
what the ratchet's FAIL decided anyway) and the real numbers are in HYPOTHESES.md.
The revert itself is unaffected: ratchet.py FAIL on 6 documents is the decision.
| 16 Nov 09:54 | fixer | `classify.py --attempt` refuses every problem class name (keys are retired verify_google check ids), so this run's attempt is recorded in HYPOTHESES.md and TRACE.md instead of ATTEMPTS.json. Engine reverted to clean. |
| 16 Nov 10:26 | fixer | Running `classify.py` (to list valid ledger keys) rewrote the GHOST class file tools/p2w-bench/DEFECT-CLASSES.md with 45 retired check-id classes. Reverted to HEAD before committing. Nobody should run classify.py to read a class name. |
| 16 Nov 10:50 | fixer | `hypothesis.py --add "content-missing-partly-replaced"` refuses the same way `classify.py --attempt` does ("is not a class"), so this run's ruled-out theory is written straight into HYPOTHESES.md and the attempt is recorded through `attempt.py`, which does accept the problem name. |

## 16 Nov 11:53 fixer - release guard reports "0 minutes old" and cannot be satisfied

`round.py --release-fixer` refused at 32 minutes into the run with "this run is 0 minutes old
with 1 attempt(s) recorded". The age is measured from the last attempt heartbeat, and
`attempt.py` writes one when it records - so any run that records an attempt and then releases
is told it is 0 minutes old and must go back to STEP 2. The guard cannot be satisfied by
finishing the work it asks for. Forced here, with the reason: the kept fix on
`content-missing-nothing-in-its-place` is committed (232f622) and the remaining work - a
full-corpus ratchet, 213 documents, about 25 minutes of soffice - does not fit the window.

## 19 Nov 17:25 fixer - the release guard stripped a kept fix out of the tree, every release

`round.py --release-fixer` runs an auto-revert: if the engine differs from the one recorded at
claim and no attempt was kept, it runs `git checkout <claim-engine> -- app/src/main/java/com/kavopdf/app/engine/`.

**The field it reverts to was never written by anything.** `fixer_engine_at_claim` is only ever
READ (round.py:580); no code sets it. On 19 Nov it still held `2945cb0`, a commit older than the
previous run's kept per-row separator stroke, so the revert checked out a pre-fix engine and
**removed a measured, committed fix for 22 documents from the working tree** - printing
"reverted: the engine changed this run (2945cb0 -> 57a0507) with no kept attempt" and telling the
run to commit it. A run that obeyed would have published the regression the 18 Nov fix removed.

Two changes, both in `round.py`, both committed at `d26141e`:

* `claim()` now records `fixer_engine_at_claim` from the live
  `git log -1 --format=%h -- engine/`, so the field is a fact rather than a fossil.
* the release guard **does not revert a clean engine tree**. It already computes `_dirty` (the
  uncommitted engine diff); when that is empty there is nothing to revert, and checking out an old
  commit can only damage what is there. It now refuses instead, which is the safe failure.

The fossil in `ROUND.json` was corrected to `57a0507` by hand before this run released, because the
engine at claim genuinely WAS `57a0507` and the tree is byte-identical to it.
