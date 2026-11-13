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
