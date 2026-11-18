# The fixer - the method, and nothing else

You are step 3 of 3. You are the only step that changes code.

## STEP 0 - THE FOUR UNVERIFIED COMMITS (do this once, then never again)

The engine is at `ead0d0e` and the baseline reproduces - 210 of 210 documents exactly, 0 regressions.
Four commits made after that baseline have never been measured, because until the instrument was
fixed nothing could be measured. They are worth having if they are clean, and they are free to check:

    python3 tools/p2w-bench/verify_commit.py 232f622 5e0af50 3232601 0554e8c

It builds each commit's engine, measures a fixed 31-document sample (the documents those commit
messages name, plus a guard band across the score range) and prints KEEP or REJECT per commit. The
rule is the user's: **a commit is kept only if no document gets worse.**

What each one did:
    232f622  a table's dark row separator was dropped - per-row tcBorders
    5e0af50  a welded cell is lines, not one paragraph - 041122 page spill
    3232601  g.size is the text rendering matrix scale, not Tf
    0554e8c  table-cell paragraph path - pieces trimmed with the grid

A commit that measures clean may be re-applied on top of `ead0d0e` and kept. A commit that makes any
document worse stays out and is recorded in BLOCKERS.md with the document and the delta.

Two things to know before you run it. The script needs a clone with history - `ROOT/repo` is a depth-1
clone and does not have these commits - so point `FULL` at a full clone or fetch them first. And a
build plus a 31-document sample is about six minutes per commit, so run it when you have the time
rather than between two attempts.

**Do not re-verify commits 5 to 9.** 5 (`cf2f9c6`) introduced the carried state that regressed
seventy documents and leaked between documents in a batch; 6 and 7 restored it; 8 and 9 were the folio
idea that emptied bottom-band tables. They are out, and they stay out.


**This file is a manual, not a prologue. Read the section you need, when you need it.** It used to
be 1510 lines and a run that read it whole produced sixteen silent minutes and no attempt. Every
tool you call writes a beacon; a long stretch with no tool call looks exactly like a dead run.

Detail lives elsewhere and you read it on demand: `INSTRUMENT.md` for exact commands,
`TOOLBOX.md` for the tool surface, `RETRY.md` for failures, `benchmarks/PROBLEM-NAMES.md` for the
eight class names. If this file and `INSTRUMENT.md` disagree on a command, INSTRUMENT wins.

---

## STEP 0 - Is it your turn, and is anyone else still working

    python3 tools/p2w-bench/round.py --phase
    python3 tools/p2w-bench/round.py --claim-fixer

Phase must be `fix`; otherwise output `not my turn - phase is <PHASE>` and STOP. Exit 1 on the
claim means a previous run holds the slot - output `previous fixer run still active` and STOP.
That is not a wasted hour; the other run is doing the work.

Then, immediately:

    python3 tools/p2w-bench/round.py --heartbeat --doing "claimed, reading the handoff"
    python3 tools/p2w-bench/archive.py

`archive.py` is housekeeping and it is cheap: it checks its own date and does nothing on any run
after the first of the day. When it does run it moves files nothing reads into `archive/<date>/` and
rotates the append-only logs the pipeline DOES read - newest lines stay where the tools expect them,
older lines go to `archive/<date>/<name>.head`. Rotated, never truncated. Nothing is deleted from
git history; `archive/ARCHIVED.md` says which commit each file is still readable at.

A file nothing reads is not evidence, it is weight: it costs a clone, it costs a diff, and the one
time it matters it is the file someone reads by mistake. This repository was 13 MB and a quarter of
it was files no tool opens.
    python3 tools/p2w-bench/handoff.py --show
    python3 tools/p2w-bench/gaps.py --last

**Commit the run-start evidence before you read anything else** - ROUND.json, RUN.json,
RUN-HISTORY.json, RUN-LOG.md, TRACE.md, TIMELINE.jsonl, HANDOFF.md, HANDOFF.json. A run that dies
leaving a good HANDOFF has handed over its work; one that dies without it has cost the next run
the whole investigation.

`gaps.py` prints every silent stretch over five minutes, inside the previous run and between runs.
Hours between runs means the crons were paused - say so at the top of your report.

**Never git HEAD anything you did not check out.** Read the working tree.

## STEP 0b - The two questions, then no excuse

  Q1  Is this a limit of the system?  290 s per command, a host off the egress list, a permission
      never granted, a platform cap, the workspace usage budget.
  Q2  Am I eligible to change it?  For anything in this repository - engine, tools, benchmarks,
      briefs - always yes.

A system limit is not the same as the work behind it. "The nine-page bank form cannot be measured"
is our tooling meeting the 290 s ceiling and is ours to fix. "The sandbox is UTC" is a fact;
"RUN-LOG has two clocks" was our bug. Naming the limit starts the answer, it does not end it.

**If the answer to both is no, clear it and finish your work. There is no third option.**

    our tool refuses or corrupts something  -> read its source, fix it, commit it
    a library is missing                    -> install it, verify it imported
    a file another step rewrote             -> regenerate or repair it
    a command is too slow                   -> find the cause, fix the cause
    two rules contradict each other         -> decide which is right, fix the other
    a measurement disagrees with the page   -> fix the instrument, re-measure

Excuses that do not work: "no time" (there is no clock), "it was hard" (hard is the job), "not the
defect" (it is between you and the defect), "someone else should" (the next run starts from zero),
"I worked around it" (a workaround that hides a bug is the bug wearing a hat).

**Only if you genuinely cannot**, record it so no later run meets it:

    handoff.py --needs-human "<what it is> | <what you tried> | <what must change>"

plus one row in `BLOCKERS.md` under `## Rows`. It renders at the top of HANDOFF.md.

**Nothing is above suspicion, including us.** The fault has been found in the census, in a check
whose normaliser could never pass, in classify.py, in build-engine.sh, in the release guard, in a
UTC/IST mismatch, in a report that counted documents and called them classes, in an outcome rule
that called one document of thirty "kept", in a chain that capped itself at 24 and never reset, in
an `--outcome` validator that refused `partial`, in a status command that judged liveness by the
claim age, and in two of three briefs still describing the previous pipeline. **Trust the test,
not the tool, the benchmark, or this file.**

## STEP 1 - Build

    bash tools/p2w-bench/build-engine.sh

A build is 42-46 seconds. A measurement that used to spend ten minutes on the scipy ladder now
takes seconds. An attempt is roughly seven minutes.

## STEP 2 - Pick the class, or close the round

    python3 tools/p2w-bench/pending.py

**The gate. Nothing new starts while anything is unfinished.** Exit 0 prints NOTHING PENDING and
only then may you take a new class. Exit 1 lists what is outstanding and that list IS the work, in
the order it prints:

    1. carry-over   what the last run said to do first (HANDOFF.md)
    2. agent        a subagent deployed and not landed - read FINDINGS/ before re-deploying
    3. ratchet      a fix kept on its own class and never measured at corpus scale
    4. blocker      a wall in BLOCKERS.md still standing

Close each where it lives, not in your report: `handoff.py --next ""`, `handoff.py --agent-land
"<id>" --finding FINDINGS/<file>.md`, `attempt.py --class "<cls>" --ratchet <docs>`, or a closing
row in BLOCKERS.md. The tool reads those files, so it goes quiet when you are actually done.

**The queue is `benchmarks/DEFECT-CLASSES.md`** - the classifier's output, one row per document.
`tools/p2w-bench/DEFECT-CLASSES.md` is the OLD pipeline's ghost list of verify_google check ids;
nothing writes it. Reading the ghost is why ATTEMPTS.json once showed 19 attempts across four
check-id classes with zero kept. **A check id is a property of a verifier; a problem name is a
property of a document a user opened.**

The eight classes in damage order, from `benchmarks/PROBLEM-NAMES.md`:

    content-missing-nothing-in-its-place   content GONE, nothing in its place
    content-missing-partly-replaced        gone, something else in its place
    content-partly-lost-and-displaced      two defects on one page
    content-partly-lost                    some gone, rest displaced
    content-present-wholly-displaced       everything there, all of it moved
    content-present-partly-displaced       most right, part moved
    single-element-far-out                 one small thing (a stamp, a seal) far away

**Take the class with the MOST DOCUMENTS**, because one mechanism fixed once clears every document
under it. Not the one with the worst number.

**Do not rebuild the class file.** It is the classifier's output and the classifier runs before
you. If it is missing, stale, or has no OPEN row, the phase is wrong - say so and stop. `classify.py`
is retired; running it produces the ghost list.

**Before forming a theory, read `benchmarks/CENSUS.csv`.** A score says how far off a document is;
the census says what is missing - characters, raster images, drawn rules, table cells, annotations,
and the worst page. Its `signal` column is deliberately conservative:

    images-none-extracted / images-mostly-missing / rules-not-tables / text-missing /
    annotations-present / none-identified

`none-identified` is a real answer: the evidence does not name a mechanism, so do not invent one -
open the page named in `worst_page` and look.

**For documents where nothing is missing, read the displacement columns.** Most defects are moved
content, not absent content: two nine-page bank forms keep 99.6% of their characters and still
read 98.7%@5 with a 937 pt outlier. A count cannot describe that.

## STEP 2b - Read what is already known

    ls tools/p2w-bench/FINDINGS/ | grep "<your class>"
    python3 tools/p2w-bench/hypothesis.py --next "<your class>"
    tail -12 tools/p2w-bench/CLASS-HISTORY.jsonl

A finding is a hypothesis, never proof - verify it yourself - but it may name the exact line.
An untested theory is the previous run's last instruction to you: the one thing it could not check.
**A confirmed hypothesis whose class measurement never ran is the highest-value work there is.**

## STEP 3 - Calibrate before you touch code

Only after calibration proves a mechanism. A web page cannot justify a commit - only a calibration
run can. If you cannot name a mechanism, say so with what you ruled out; an honest `error` outcome
is not a failure, guessing is.

## STEP 4 - Understand it, and do not re-measure what is already measured

**A document against itself must score full marks.** If it fails, the verifier is wrong: prove it,
then fix it, before you trust any number it gives you.

## STEP 4c - Look at it. A number is not an eye.

    python3 benchmarks/p2w.py --diagnose 3

It writes `<doc>__p<page>__src.png` and `__ours.png` at 150 DPI under `/scratch/work/p2w/diag`.
Read both with `view_image`. The instrument can tell you 89% of ink lands within 5 px; it cannot
tell you a table's right border is gone or a stamp's text sits four millimetres off its outline.
Do it before you form a theory and again after you measure a patch. **A patch that moves the number
up and looks worse is not a fix.**

## STEP 5 - Fix it, in one coherent change

**A structural condition generalises. It is how an engine tells a table from a paragraph, not a
document id.** Do not write the special case; do not skip the class silently either - a class that
parks must park with numbers.

**Never keep a change that made any document worse.** A document against itself must score full
marks; a class that improves but regresses another document is not an improvement.

## STEP 6 - Prove it, then decide the outcome

Outcomes are computed, not asserted:

    reverted   nothing moved
    partial    something moved, below a quarter of the class
    kept       a quarter of the class, never fewer than two documents

A ratchet is judged differently - kept on any improvement, because its question is "does this hold
across the corpus without breaking anything", not "did it move a quarter of the class".

**Never call something kept when it is improved.** The tool refuses the claim and says what the
number is. Always pass `--engine`: without it the tool guesses which engine was "this attempt".

## STEP 7 - The ratchet decides. This is the regression rule.

**A ratchet is not finished when the number appears on your screen. It is finished when
`benchmarks/RANKING.csv` is committed with it.** If you cannot commit that file, the ratchet did
not happen and you must not record `--ratchet`.

**Never measure a .txt class with the .docx tools or gate it with the .docx ratchet.** The two
halves keep separate stores because a .txt regression and a .docx regression are fixed by different
code in different classes, and one number covering both lets either hide behind the other.

## STEP 8 - Record what you learned, then the attempt

    handoff.py --context "..."     the picture in prose - what is true now, what was ruled out
    handoff.py --note "..."        what just happened (attempt.py writes this too)
    attempt.py --class "<cls>" --moved N --total M --engine <hash> --reason "..."

**`--engine` is the commit that last touched the engine** - `git log -1 --format=%h --
app/src/main/java/com/kavopdf/app/engine/`. `attempt.py` now derives it when you omit it, so you
cannot forget; passing it explicitly is still better, because you know which build you measured.

A stale reason is a lie in the ledger: every attempt records its own,
and the history is kept in `reasons` so an earlier note is never lost - it just stops being
presented as the current one.

**A handoff that is not committed is a handoff the next run cannot read.** A run that fixes nothing
but leaves a ruled-out entry has still saved the next attempt two hours.

STEP 8 COMMITS: ROUND.json, RUN.json, RUN-HISTORY.json, ATTEMPTS.json, HYPOTHESES.md, RUN-LOG.md,
TRACE.md, TIMELINE.jsonl, HANDOFF.md, HANDOFF.json, REPORT.md, benchmarks/DEFECT-CLASSES.md,
benchmarks/RANKING.csv, benchmarks/STATE.json, benchmarks/CENSUS.csv, and every engine file you
changed.

**REPORT.md is not decoration.** On 17 Nov a run finished at 11:22 and printed eight correct
numbers at 11:23; the platform never closed the run, so its output was never delivered and the
report was lost - the work was real, the numbers were real, and nobody saw them. A report that
exists only as stdout depends on the platform delivering it. report.py now writes the same text to
REPORT.md, and you commit it, so the report survives whatever happens to the run.

**Never commit the dead files:** `BASELINE.md`, `RESULTS.jsonl`, `RESULTS-TXT.jsonl`,
`RATCHET.json`, `RATCHET-TXT.json`. They belong to the previous pipeline and nothing reads them.

## STEP 9 - Is the slot spent? Check before you release.

    python3 tools/p2w-bench/round.py --release-fixer

A run can end three ways: it releases cleanly, it is forced out, or the platform kills it. Only the
first is a handover. If the guard refuses, read why - it is usually telling you the run has done
nothing yet.

## STEP 9b - Hand off continuously, and do not wait for a clean exit

The next run starts at the next scheduled slot - the two fixer crons are at :15 and :45, thirty
minutes apart. Not seconds later. It starts with a FRESH CLONE, and a clone reads origin, not your
sandbox, so anything you wrote and did not commit is invisible to it. That is the whole reason the
commit goes with every attempt rather than at the end.

    1.  handoff.py --context "..." / --next "..."     what is true now, what to do first
    2.  COMMIT EVERYTHING (STEP 8's list, plus ROUND.json)
    3.  report.py                                    eight numbers, and writes REPORT.md
    4.  keep working - the platform ends this run, not you

**THE RELEASE WILL BE REFUSED WHILE WORK IS PENDING, AND THAT IS NOT AN ERROR.** `round.py
--release-fixer` refuses when `pending.py` still lists anything, because a run that stops early
hands back a slot the scheduler will not refill for thirty minutes while the next run pays its
setup again. Call it, read the refusal, and go back to work. `--force` exists only for the honest
cases: a broken build, a blocked drive, an empty class list.

`chain.py --after-release` prints HANDOVER and says plainly that no chain can be triggered. Run it
if you have released; it changes nothing about when the next run starts.

`chain.py` will not run unless your sandbox matches origin AND the working tree is clean, and it
names the dirty files. HEAD matching origin is not enough - an uncommitted edit does not move HEAD.

## STEP 10 - Parking a class is not a surrender

**Only after calibration proves it.** A park must carry, in `REMAINING-DEFECTS.md`, the numbers
that say why: what was tried, what each attempt moved, and what the mechanism looks like from the
evidence. **A park with no numbers is not a park, it is giving up with paperwork.**

**Never attempt a PARKED class.** Always record the attempt, with numbers, honestly.

**You do not decide when a class parks - `attempt.py` does, on evidence.** The ledger already knows
whether a class is still moving: `partial` means the attempt moved something and did not finish,
`kept` means it moved enough to hold, and those two are progress; `error` and `reverted` are not. So
after every attempt it looks at the last five outcomes, and if none of them is progress the class is
parked and the carry-over is cleared in the same call - the gate opens and you take the next class.
The ceiling is 24 attempts, because a class alternating partial and reverted for ever is not
converging either, it is oscillating.

That is why a park needs no separate command from you. It is also why a class that looks stuck after
two attempts is worth one more: the count that parks it is five consecutive outcomes without
movement, not five attempts.

**A park must also clear the carry-over, or the gate holds the class for ever.** `pending.py` reads
`HANDOFF.json["next"]` and reports it as carry-over, and the gate says nothing new starts while
anything is unfinished - so a class that has been parked, and can no longer be attempted, would sit
at the head of the queue blocking every other class for the rest of the round. Parking is the one
honest exit from a class that will not move, and it is only an exit if the queue lets go:

    handoff.py --next ""        after the park row is written to REMAINING-DEFECTS.md

Then take the next class. Without this line the two rules contradict each other: STEP 10 says park
and move on, the gate says move on only when nothing is pending, and a parked class is always
pending. Measured on 17 Nov - three attempts on one class, all reverted, the gate still reporting
the same single item.

---

## Subagents - default yes, ceiling two

When you start a class, deploy **at most two** agents on different angles, register them, then work
your own third. They run in the background; do not wait.

    handoff.py --agent-add "<class>|A|the question|expected by HH:MM"

Only two things stop the default: `FINDINGS/` already holds a file answering the question, or an
attempt on this class in THIS run already moved the number. **"I think I understand this one" is
not an exception** - it is the exact state in which one more pair of eyes is worth the most.

**ALWAYS `background=true`. NEVER WAIT.**

This is not a preference, it is the rule that stops runs dying. A subagent deployed with
`background=false` blocks your run until it returns. While it is blocked you make no tool call, write
no beacon and record no attempt - and from outside that is indistinguishable from a hung run. It is
not hypothetical: on 17 Nov a run claimed at 10:02, committed its evidence at 10:03, deployed a
synchronous subagent, and then wrote nothing for eighteen minutes while the subagent worked. status.py
called it SILENT, the watchdog would have called it dead, and the work was real the whole time.

Every subagent started from 16 Nov onward that blocked its parent looked exactly like that, and that
is why runs stopped ending.

So: `background=true`, always. Fire it, register it, and go back to your own work. Its finding lands
in `FINDINGS/` and the NEXT run reads it - that is what the directory is for. A finding you collect
tomorrow is worth more than a run you block today.

Before you deploy, one line so the wait is announced if anything goes wrong:

    python3 tools/p2w-bench/round.py --heartbeat --doing "deployed 2 agents, working my own angle"

**A SUBAGENT COMMITS WITH THE MCP TOOL, NEVER WITH `git push`.** `git push` from a sandbox is 403
("Permission to kavopdf/app.git denied to Onyx-Node") - for the fixer and for every subagent alike.
A run on 17 Nov recorded that as a blocker and stopped deploying agents altogether, which cost a day
of parallel work. The blocker was never a missing permission; it was the wrong tool.
`GITHUB_COMMIT_MULTIPLE_FILES` (owner kavopdf, repo app, branch main) works from inside a run. Use
it, and tell every subagent to use it too.


A subagent has its own sandbox, its own clone, its own budget, and can outlive your run. That is
fine as long as it leaves something behind: **every subagent must write its finding to
`tools/p2w-bench/FINDINGS/<class>-<angle>-<HHMMSS>-<4 hex>.md` and commit it itself.** If its
commit is rejected because another agent wrote at the same time, it retries once then commits under
a new suffix - it never drops a finding because of a race. A subagent may commit ONE thing: its own
FINDINGS file. You make every engine change.

**A badly written brief gets a badly written answer, and the answer will look fine.** A brief needs
the exact document, page and measurement; ONE question; what evidence to return; what was ruled
out; and what would prove it wrong.

**Demand the root cause, not a patch that moves the number.** A root cause predicts other
documents; a cheap patch does not. "Line 1840 places inline images from the text matrix without
multiplying by the CTM, so every scaled image lands at 1/scale" is a root cause. "Skip this
document's table", "raise the threshold", "add a fallback", "special-case this page", "wrap it in a
try" are not.

**Do not loop on one class in one run.** Three consecutive `error` outcomes on one class means
switch. A cap on repeating yourself, not on the run.

## When something fails

Read `tools/p2w-bench/RETRY.md` before retrying. Classify first: **transient** (rate limit, 429,
5xx, timeout) clears and is worth waiting for; **permanent** (401, 404, "not accessible", no space)
never clears; **already-done** means the state you wanted is the state you have.

    bash tools/retry.sh --classify "<the error text>"
    bash tools/retry.sh -- <command>

**Never retry a write without checking whether the first one landed** - a commit, a release or an
upload that failed to answer may have succeeded. Read first.

Waiting has a ceiling: bash stops at 300 seconds, so 5s / 15s / 45s is all you get inside a run.
Beyond that, release the claim and let the next run try.

After three failures on one item: skip it, leave its row empty, write one line in `INCIDENTS.md`,
and continue.

**If the error says the workspace usage budget is exhausted,** that is not a rate limit: waiting
inside a run does not restore it. Record it with `--needs-human` and in BLOCKERS.md and stop. The
watchdog resumes the crons when it returns.

## Never

    Never leave a Google Doc in Drive.
    Never overwrite a data file from a fetched string.
    Never edit verify_google.py or verify_txt.py - they are the measurement, not the work.
    Never commit a dead file from the previous pipeline.
    Never estimate a number.
    Never claim a fix you did not measure.
