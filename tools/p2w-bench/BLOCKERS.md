# BLOCKERS — what stopped a run, and what it was doing when it happened

One row per obstacle that a run could not clear. INCIDENTS.md records a *document* that was
skipped; RETRY.md records how to retry a *class*. This file records a *wall*: something that
stopped the run itself, that the run could not fix with the access it had.

The row is the deliverable. A run that hits a wall and writes one good row has done more for the
pipeline than a run that hides the wall and reports success. The final message is read once; this
file is read by every run after it.

| time | what I was doing | the obstacle | what I tried | can I fix it | what is needed |
|---|---|---|---|---|---|
| 2026-11-17 14:05 | CLEARED, not a wall. A subagent could not land its FINDINGS file: `git push` and the contents API both refused (`Permission to kavopdf/app.git denied to Onyx-Node`, 403; `Resource not accessible by integration`). | The run concluded the GitHub App lacked write access and filed this row for a human. | yes - the tool was wrong, not the permission: `git push` is 403 for every run in this pipeline, and a commit goes through the GitHub MCP tool `GITHUB_COMMIT_MULTIPLE_FILES` (owner kavopdf, repo app, branch main), which works from a subagent and from a run. | nothing - cleared 17 Nov 14:05. Tell every subagent to commit with GITHUB_COMMIT_MULTIPLE_FILES and never with `git push`. |

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
| 2026-11-17 11:40 | `chain.py --after-release` prints FIRE, but the `cron` tool is not in the fixer agent's tool list, so the next run cannot be triggered from inside the run. | Called `cron action=list` - TOOL_NOT_FOUND; `tool_search "cron list scheduled jobs"` returns only GitHub and HuggingFace job tools, no cron. chain.py had already appended a 12:23 entry to CHAIN.json; that false fire was removed and the reason written into the file. | Either give the fixer agent the `cron` tool, or stop requiring `chain.py --after-release` from it. Until then every run ends with FIRE printed and nothing fired, and the 3/3 cron has to be re-armed by hand. |
