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
