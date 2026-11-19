# The system, in one page

Everything below is measured or verified. Nothing here is a plan.

## What it is trying to do

Convert every PDF in the 213-document corpus to a `.docx` and a `.txt` that match the original, as the
user's phone renders it. The renderer that matters is **Google Docs**, because that is what opens the
file. LibreOffice is a fast local proxy that hides the faults Google shows.

    LibreOffice   65 open of 213     70 % clean
    Google Docs    7 clean of 84     92 % FAIL

That gap is the whole problem. LibreOffice honours nearly every construct the engine emits - absolute
indents, floating drawings, character-width scaling - and Google honours almost none of them. The model
is therefore **flowing text**, which is also what Acrobat Pro and iLovePDF produce. The engine is not
being rewritten: one construct at a time, measured before and after, kept only if nothing gets worse.

## The six crons

| time | cron | does | may touch the engine? |
|---|---|---|---|
| :00 | baseline | measures the corpus with soffice, refreshes the .txt table | no |
| :20 | gverify | 20 documents through Google **and** LibreOffice | no |
| :40 | classifier | groups the failures into classes, both formats | no |
| :50 | **fixer** | one construct, measured, kept or reverted | **yes - only this one** |
| every 3 h | watchdog | finds anything stopped and moves it | no |
| 22:00 | apk | ships once, when every round is done | no |

The fixer is the only cron allowed to change `app/src/main/java/.../engine/`. The other five exist so
that it never has to guess what to fix and never has to prove its own work.

## The four things to look at

    python3 tools/p2w-bench/health.py            is each stage done, moving, stopped or waiting
    python3 tools/p2w-bench/progress.py          one dated row a day - the only trend
    python3 tools/p2w-bench/round.py             round, phase, open classes
    python3 tools/p2w-bench/stage.py             how far the Google measurement has got

`health.py --stalled` exits 1 when something has stopped. `progress.py` appends a row to
`benchmarks/PROGRESS.md` once a day; **a row that does not move is the signal** - it means a day of the
pipeline produced nothing.

## What goes wrong, and what fixes it

| symptom | cause | fix |
|---|---|---|
| `git pull` says "please commit or stash them" | a dead run left state files dirty | `git checkout -- tools/p2w-bench/` then pull |
| a cron's `next_fire_at` is in the past | a stale fire time | `cron(action="pause")` then `cron(action="resume")` |
| a run has been `running` for over an hour, `ended_at: null`, slot free | **zombie** - it finished and never exited | `cron(action="delete")` then recreate it. **The id changes - update HEALTH-BRIEF's table and the watchdog prompt, or the next watchdog pauses a cron that no longer exists** |
| phase is `done` but documents still fail | `done` stops every claim forever | `round.py --reopen` (refuses when nothing is failing) |
| the fixer keeps measuring the corpus and records no attempt | it took the baseline's job | the brief forbids it; record the attempt *before* the measurement |
| a change improves LibreOffice and not Google | the gate is soffice's | `verify-change.py` prints the Google candidates; put them through `gverify.py` first |

## What is settled and must not be re-litigated

* **The renderer is Google Docs.** LibreOffice is the gate because it is fast and covers all 213; it is
  not the target.
* **The model is flowing text.** Four measured attempts to keep the canvas model all made things worse -
  see `tools/p2w-bench/FINDINGS/GOOGLE-LAYOUT-THREE-FIXES-TRIED.md`.
* **No engine rewrite.** One construct, one measurement, one commit.
* **Nothing changes without a measurement before and after.**
* **`share@5px` is not a cross-renderer measure.** Use the 42 checks in `verify_google.py`.
* **A refused document is not a pass.** `--collect` records `page_count_refused` separately.
* **Negative results are committed.** Four are already recorded so nobody re-derives them.

## Where the evidence lives

    benchmarks/RANKING.csv              the .docx scores, soffice render
    benchmarks/RANKING-TXT.csv          the .txt scores
    benchmarks/gverify/                 the 42 checks through Google, one JSON per document
    benchmarks/gverify-lo/              the same 42 checks through LibreOffice
    benchmarks/GOOGLE-VS-LIBREOFFICE.md which checks each renderer fails, and by how much
    benchmarks/PROGRESS.md              one row per day
    tools/p2w-bench/FINDINGS/           every measured result, positive and negative
    tools/p2w-bench/ATTEMPTS.json       every fixer attempt, kept or reverted

## If it all stops

`BLOCKERS.md` is where the watchdog writes anything it could not move in 24 hours, with what it tried
and what a person would have to decide. **Read that file first.** If it is empty and nothing is running,
the answer is in `cron(action="list")` - a paused cron is the quietest way this pipeline dies, and
nothing in the repository reports it.
