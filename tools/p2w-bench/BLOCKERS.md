# BLOCKERS — what stopped a run, and what it was doing when it happened

One row per obstacle that a run could not clear. INCIDENTS.md records a *document* that was
skipped; RETRY.md records how to retry a *class*. This file records a *wall*: something that
stopped the run itself, that the run could not fix with the access it had.

The row is the deliverable. A run that hits a wall and writes one good row has done more for the
pipeline than a run that hides the wall and reports success. The final message is read once; this
file is read by every run after it.

| time | what I was doing | the obstacle | what I tried | can I fix it | what is needed |
|---|---|---|---|---|---|

## How to add a row

```
| 16 Nov 11:20 | STEP 6, measuring content-missing-partly-replaced on the two nine-page bank forms | soffice: "convert failed, exit 1" after 290 s on 041122-Account_Opening_Form.docx | raised the call limit, split the document, retried twice | no - the render is slower than the sandbox allows | a page-by-page converter, or a raised per-call limit |
```

- **what I was doing** — the step and the class, not "working". The next run needs to know where
  the wall is, so it can avoid it or approach from another side.
- **the obstacle** — the error text, not a paraphrase. "It failed" is not a row.
- **what I tried** — every attempt. This is the field that stops the next run repeating you.
- **can I fix it** — `yes` (and you did), `no`, or `not in this run`.
- **what is needed** — the specific thing: a package, a permission, a code change, a decision.

## Rules

- Solve it yourself first. If it is our own tool refusing or corrupting something, you have the
  source - read it, find why, fix it. That is the work, not an interruption to it.
- Write the row when you hit the wall, not at the end. A run that dies takes its notes with it.
- Never work around a tool by editing its output by hand. That is the bug wearing a hat.
- Never record an obstacle you did not actually attempt to clear.

## Rows

## Rows

| when | what | what was tried | what must change |
|---|---|---|---|
| 2026-11-16 18:53 | Workspace usage budget exhausted. All 3 crons failed 5 times and the platform paused them. Pipeline dead 849 minutes (14h 11m) - the longest outage it has had. | Nothing could be tried: a run that cannot start cannot report. Resumed all three crons at 09:22 on 17 Nov once budget returned; the fixer claimed and ran normally. | A human must watch the cron runs list for `failed` with `usage budget`. The platform pauses a cron after 5 consecutive failures and nothing inside the repo can see or prevent it. |
