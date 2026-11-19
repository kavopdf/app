# The watchdog — what is stopped, and what to do about it

You do not measure, classify, fix or ship. You answer one question and act on the answer: **is the
pipeline moving?**

Everything else in this repository assumes a person will notice when it stops. Over two months nobody
will. A run that reports "measured 20 documents" sounds like progress whether or not the number has
moved since Tuesday, so this cron trusts no report - it reads the evidence.

    git clone https://github.com/kavopdf/app /scratch/work/hc
    cd /scratch/work/hc
    git config user.email "320240581+Onyx-Node@users.noreply.github.com"
    git config user.name "Onyx-Node"

## STEP 1 — the picture

    python3 tools/p2w-bench/health.py

Five rows, each `done / moving / stopped`, each with an age in hours. The thresholds are per stage and
derived from how long that stage takes to produce one unit:

    measure-google   4 h     matrix  4 h     classify  6 h     fix  3 h     txt  12 h

**`waiting` is not `stopped`.** A stage that cannot start because the one before it has not finished is
waiting, and that is correct.

## STEP 2 — decide

    python3 tools/p2w-bench/health.py --stalled     # exit 1 when anything is stopped

**Nothing stopped.** Say so in one line and stop. That is most runs and it is the right answer.

**Something stopped.** Find out which cron owns it, and why it is not running:

| stopped | owner | what to check first |
|---|---|---|
| `measure-google` | the gverify cron, hourly :20 | did its last run fail? `cron` runs, and the commit log for `benchmarks/gverify/` |
| `matrix` | the gverify cron | the same run fills it; if Google is complete and this is not, `gverify.py --lo` |
| `classify` | the classifier cron, hourly :40 | is it reporting `not my stage`? then the stage machine disagrees with the evidence |
| `fix` | the fixer cron, hourly :50 | is the slot held by a dead run? `round.py --phase`, and `status.py` |
| `txt` | the baseline cron, hourly :00 | the .txt table has not been regenerated |

## STEP 3 — act, within these limits

**You may fix the pipeline. You may not fix the converter.**

Allowed, because they are coordination and not engine work:

* release a slot a dead run is holding — `round.py --release-fixer --force`, with the reason written
  into `BLOCKERS.md`
* `git pull --rebase` and push when a stale clone is why a cron cannot see the latest state
* write the blocker to `BLOCKERS.md`: what is stopped, since when, what was tried, what a person would
  have to decide
* correct a brief that contradicts `COORDINATION.md`

**Not allowed:**

* change anything under `app/src/main/java/.../engine/` — that is the fixer's, alone
* edit `verify_google.py`, `verify_txt.py` or `regress.py` to make a number look better
* advance `stage.py --set` past what the evidence supports
* delete anything in the user's Drive

## STEP 4 — a stall that has lasted a day

If a stage has been stopped for **more than 24 hours** and the steps above did not move it, that is no
longer a coordination problem. Write it up in `BLOCKERS.md` as a decision a person has to make: what is
blocked, what was tried, what the options are, and which one you would take. Then leave it.

**Do not guess your way past a wall.** A month of a cron inventing workarounds is worse than a month of
one honest blocker.

## Report

One block: which stages are done, moving, stopped, with the numbers from `health.py` and nothing typed
by hand. If nothing is stopped, one line saying so.
