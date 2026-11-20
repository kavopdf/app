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

---

## THE STUCK-CRON FIX: pause then resume

Verified 19 Nov. A fixer run started 18:52, hung with no beacon, and the platform still called it
running - so `next_fire_at` stayed at 18:50, in the past, and the cron never fired again. Three hours
of the only cron allowed to change the engine, gone, with nothing to show.

**A run cannot be cancelled through the `cron` tool. It can be cleared:**

    cron(action="pause",  cron_id="<id>")
    cron(action="resume", cron_id="<id>")

The resume recomputes the next fire. On the fixer that took `next_fire_at` from 18:50 in the past to
22:50, and the pipeline moved again.

**This is the watchdog's one real power and it should use it whenever `health.py --stalled` names the
fix stage and the slot is free but the cron is not firing.** Do it once per stalled stage per run, then
check `cron(action="runs")` - if the old run is still listed `running`, say so and stop. Repeated
pause/resume on a run that will not die is noise, not a fix.

### The cron ids, so a watchdog does not have to look them up

    baseline    01M7N3RTAM7SATT9TXMQPP7QRM     hourly :00
    classifier  01M733RFR3D71C2E0T2TQ9PW0R     hourly :40
    fixer       01M7TA3F4NTRWQZD6AQQESR51A     hourly :50   <- the one that matters
    apk         01M72XD9FD9MDM35X4Z7TQ6RRW     daily 22:00
    gverify     01M7T6STKQJ2KPZAYFMCZVCG85     hourly :20
    watchdog    01M7T903P1BTMEEG8SJ9SA47MQ     every 3 h

**Never pause a cron and leave it paused.** Pause and resume in the same run, or do not pause at all.
A paused cron is silent and nothing else in the system reports that it is paused.

## What the watchdog should check that health.py cannot

`health.py` reads files. It cannot see the cron platform. Two things it will never catch:

1. **A cron that is enabled but not firing** - `next_fire_at` in the past while the stage is stopped.
   Read it with `cron(action="list")`.
2. **A cron that is paused** - `status` reads `paused`. Nothing else in the repo knows.

Check both, every run. A paused cron is the quietest way for this pipeline to die.

---

## DONE IS NOT THE END — the reopen

`rounds_total` rounds finish and `round.py` sets the phase to `done`. From then on every claim refuses:
baseline, classifier and fixer all stop, permanently. **If the corpus is not actually perfect at that
point, that is a silent stop** - the app ships, the documents still fail, and nothing anywhere says so.

    python3 tools/p2w-bench/round.py --reopen

It reopens a round, and it refuses unless there is something left to fix:

    refused: the phase is fix, not done - there is nothing to reopen.
    refused: nothing fails in either format - the pipeline is finished.
    reopened as round 4 - 65 .docx and 47 .txt still fail

**The watchdog should run it whenever the phase is `done` and `health.py` still shows failing
documents.** A reopen with nothing failing would loop forever, which is why the guard exists; a reopen
with failures is the pipeline admitting it is not finished, which is exactly what a two-month run needs
it to be able to say.

---

## THE TREND — the only thing that says whether two months worked

    python3 tools/p2w-bench/progress.py

Appends one dated row to `benchmarks/PROGRESS.md` - once per day, never twice - and prints the change
since the previous row. **Run it every watchdog pass and commit the file.** It is the only place the
corpus is compared against itself across time; every other report says what happened this hour.

    date        docx open   txt failing   google   google clean
    2026-11-19      65           47          84          7

**A row that does not move is the signal.** Not a failure - a fact. If three days pass with the same
`docx open` and the same `txt failing`, the pipeline is running and producing nothing, and the watchdog
should say so plainly in `BLOCKERS.md` with the fixer's attempt count beside it.

**Never edit a past row.** The value of a trend is that it was not adjusted afterwards. If a row is
wrong because a table was regenerated, append a new row with a note; do not rewrite history.

---

## A ZOMBIE RUN: pause/resume is not always enough

Found 19 Nov, hours after the first fix. A fixer run started 18:52, released its slot, and stayed
`status: running` on the platform for over three hours. `pause` then `resume` recomputed
`next_fire_at` correctly and the pipeline looked healthy - **but the zombie was still there, and the
cron still would not fire.** Every later run was blocked by a run that had already finished its work
and never exited.

**`pause`/`resume` clears a stale `next_fire_at`. It does not clear a zombie run.** Those are two
different faults and only one of them is fixed by pause/resume.

    cron(action="runs", cron_id="<id>")     # is the OLD run still listed `running`?

If a run has been `running` for more than an hour with `ended_at: null` and the slot is free, it is a
zombie. **The only way to clear it is to recreate the cron:**

    cron(action="delete", cron_id="<id>")     # then create it again with the same prompt
    cron(action="create", name=..., schedule=..., prompt=...)

Deleting a cron does not delete the repository, the state or the work - only the schedule and its run
history. The new cron fires on the next matching minute.

**After recreating, the id changes.** Update the table above in this file and in the watchdog's own
prompt, or the watchdog will try to pause a cron that no longer exists and report success while nothing
happens. **That is the quietest failure in the whole system.**

### The order, when a stage is stopped

    1. health.py --stalled                       which stage
    2. cron(action="runs")                       is a run still `running`?
       no  -> pause/resume, done
       yes -> and it has been running >1 h with ended_at null -> zombie -> delete + recreate
    3. update the id in this file and in the watchdog prompt
    4. write what you did into BLOCKERS.md

---

## DOES THE WATCHDOG ACTUALLY HAVE THE `cron` TOOL?

The baseline cron's own prompt says, and has said since it was written:

> *"A run cannot manage crons - the `cron` tool is not in a run's tool list."*

**If that is true of cron runs generally, then everything in this brief about pause/resume and
delete/recreate cannot be executed by the watchdog**, and the two failures it exists to fix - a paused
cron and a zombie run - are not automatable at all.

**The watchdog must therefore check its own tool list first and say which world it is in.**

* **No `cron` tool** → do health, progress, `round.py --reopen` and `round.py --release-fixer`, then
  write into BLOCKERS.md: *"the watchdog has no cron tool; a paused or zombie cron needs a person."*
  **Say it in the report.** A watchdog that reports "nothing to do" while unable to do the one thing it
  exists for is worse than no watchdog.
* **Has `cron`** → the zombie and stale-fire procedures above apply.

This was found during the final audit, not by a run failing. That is the point of writing it down: the
next run does not have to discover it.

---

## YOUR REPORT IS GENERATED AND VERIFIED. IT IS NOT WRITTEN.

The user's instruction, 20 Nov: *"sabhi ke reports me yeh ensure karna koi bhi report hath se na likha
jaaye mujhe sabhi crons ke report me hamesha 100% accuracy chahiye."*

**Every number in your message must be one a tool printed.** Not remembered, not rounded, not
reconstructed from what you think the run did.

Write the report, then run this before you commit it:

    python3 tools/p2w-bench/lastmessage.py --file /tmp/report.md --for CRON

where `CRON` is `gverify` or `health`. It compares **every integer** in your message against what the
tools print, character for character. Dates and clock times are stripped first - a date is not a
measurement.

    REFUSED - 1 number(s) in this gverify report are not in the tool output:
      gverify: 999 is not in the gverify output - ...32_stroke_lines fails 999 documents in Google...
    A number a run types is a number a run can get wrong.

Exit 3 means a number you wrote is not in the tool output. **Do not "fix" it by re-running until the
numbers match** - open the tool, read what it prints, and copy that. If the sentence needs a number no
tool prints, delete the sentence.

**A report that fails this check is not committed.** The numbers that matter, and the tool that owns
each:

    how many measured, scored, refused    gverify.py --report
    which check fails how many docs       gverify.py --report
    the stage and what is next            stage.py
    the capability table                  gverify.py --matrix
    each stage done/moving/stopped        health.py
    the day's trend row                  progress.py

