# THE CHARTER

**You own this. Not the procedure - the outcome.**

---

## THE GOAL

**Every document in the corpus matches its original at 99% or better in Google Docs, in both the .docx
and the .txt.**

That is the whole job. Everything below this charter is a means to it, and any means that does not move a
document towards 99% is wasted time however tidy it looks.

    corpus      213 PDFs
    today       6 clean of 192 scored in Google;  186 clean of 213 in txt
    the gap     186 documents, and they are the reason this exists

## WHAT DONE LOOKS LIKE

A document is done when **all 42 Google checks pass** on it and its `.txt` describes the same document.
Not "improved", not "moved", not "the class was worked" - **that document, in the renderer the user
opens.**

## A RULE IS A METHOD. IT NEVER NAMES A CLASS.

The user, 22 Nov: *"koi bhi rules kisi ek specific class ke liye nhi hona chahiye yeh iska kaam karne ka tareeka hona chahiye"*

**Every rule in this file is a way of deciding, not a thing to do to one class.** The difference matters,
because a class-specific rule is dead the moment that class is fixed, and it takes a run to notice.

| a method (right) | a class rule (wrong) |
|---|---|
| "fix the construct the checks share, not one check of five" | "fix `32_stroke_lines`" |
| "ask which documents become CLEAN if this works" | "work `18_displacement` next" |
| "a measured lead outranks everything" | "finish `w:tblpPr`" |
| "the biggest class with no verdict is the biggest prize" | "`47_margins` is 26 documents" |
| "an unmeasured change is not a pass" | "re-stamp the table after `47_margins`" |

**So no rule here may be written in terms of a class name.** Evidence may be - a measurement of
`32_stroke_lines` on 21 Nov is a fact and belongs in the file - but a rule must be stateable without naming
any class, because the class it names is the class that will not exist next month.

**And if you find yourself writing a rule that only makes sense for one class, you have found a symptom, not
a rule. Write it in `FINDINGS/` as a measurement and leave the method alone.**

**The tools already obey this: no script in `tools/p2w-bench/` branches on a class name.** Class names
appear in `verify_google.py` and `verify_txt.py` because those files ARE the check catalogue, and in tests
because a test asserts a specific check catches a specific mutation. Neither is a rule about what to work on.

## THE ONLY THINGS THAT ARE NOT YOURS TO DECIDE

Six, and they are not preferences - each one is a mistake this project has already paid for.

1. **Google is the truth.** LibreOffice is a fast local proxy that hides what the phone shows. A change
   that only improves LibreOffice is not a fix. (That one shipped as 3.53.5 and broke every stamp.)
2. **Nothing changes without a measurement before and after.** A change you cannot measure is a guess;
   write it into `FINDINGS/` as a proposal instead of committing it.
3. **No document may get worse.** `regress.py --check` must pass, and it now refuses a Google regression
   as well as a LibreOffice one.
4. **No construct Google ignores.** `google_safe.py` lists them; the gate refuses a commit that spreads
   one. A construct LibreOffice honours and Google drops IS the defect, not the fix.
5. **Never delete anything** - not a file, a row, a branch, a release asset or a Drive file. Deleting is
   how evidence disappears and how the next run repeats this one.
6. **No secret in the repo, and nothing in the user's Drive root.**

**Everything else is yours.** Which class, which construct, which approach, which tool, which document to
prove it on, whether to write a new tool, whether to change a table, whether the rotation is right, whether
the instrument is lying - all of it. There is no person behind this pipeline to ask. Decide on evidence,
record what you decided and why, and move.

## WHAT YOU HAVE

The whole repository read and write, `git push`, bash, Python and the doc libraries, the engine toolchain,
Google Drive yourself with the three calls for a Google verification, two sub-agents a run, the corpus,
every measurement, and the whole history in `FINDINGS/`, `LESSONS.md`, `SETTLED.md`, `HYPOTHESES.md`,
`BLOCKERS.md` and `git log`.

**If a tool you need does not exist, write it.** Sixty in `tools/p2w-bench/` were written by runs that
needed one.

## HOW TO DECIDE, WHEN NOBODY TELLS YOU

**Research the repository first** - most of what you are about to try has been tried and written down.
**Verify by measurement** - a claim you have not measured is an opinion. **Prove with a number before and
after, and say which evidence.** When the evidence does not settle it, take the reversible decision and
record what would overturn it.

**And ask the only question that matters before every attempt: if this works, which documents become
CLEAN?** If the answer is none, it cannot be a fix, whatever the class table says.

## WHAT THE REST OF THIS FILE IS

**A record of what has already been learned, and one way of working that has produced results.**

**It is not a checklist and not a script.** The steps below are numbered because that is how they were
written down, not because a run must perform them in that order or at all. A run that reads the situation,
decides what is worth doing, and does it - and gets documents to 99% - has followed this file better than
one that performs every step and moves nothing.

**When a step here contradicts the evidence in front of you, the evidence wins.** Say so in the report, so
the next run inherits the correction instead of the contradiction.

---

# HOW TO THINK ABOUT A DEFECT. THIS IS THE PART THAT MATTERS.

A check failing is not the problem. It is the symptom. **A run that fixes the symptom has done nothing that
survives the next document.** This is how to get from the symptom to the thing that causes it.

## 1. Three things, not one

For any defect, look at all three before you touch code:

| | what it is | how to look |
|---|---|---|
| **the page** | what the PDF actually draws - position, colour, width, the order things are in | render the page, and read the PDF's own operators; the text layer is not the page |
| **the engine** | what our `.docx` says about it | unzip the `.docx`, find the construct, read the numbers it wrote |
| **the renderer** | what Google does with that construct | upload, convert, export, look. LibreOffice does not count here |

**The defect is the gap between the first and the third, and the second is the only thing you can change.**
A run that looks at one of the three is guessing.

## 2. The cause has to explain every symptom, not the loudest one

If a document fails `32_stroke_lines` and `05_chars_extra`, **that is one cause with two symptoms, not two
defects.** Find the thing that produces both - on 21 Nov it was one floating `<w:drawing>` per rule: Google
drops the shape (the rule is lost) and leaves the anchor (a `U+200B` appears).

**A hypothesis that explains one symptom and ignores the other is wrong, however well the fix works on the
one you looked at.** Check the shapes:

    python3 tools/p2w-bench/classpick.py --leverage

Checks that always travel together share a cause. One fix clears all of them; fixing one of five has done a
fifth of the work and reported a success.

## 3. Three places a defect can live, and they need different fixes

* **The engine is wrong** - it emits something the page did not draw, or the wrong number. Fix the engine.
* **The instrument is wrong** - the check fails a document against itself, or counts what the page never
  drew. Fix the instrument, with a finding and a re-measurement. `26_text_overlap` counted absolute overlaps
  instead of new ones for days and made the hardest documents unfixable.
* **Google cannot do it** - the construct is not honoured, or honoured differently. **That is not a fix, it
  is a finding.** Write it down, use the construct Google does honour, or park the class with the proof.

**Getting this wrong is the most expensive mistake in this repository.** Four attempts at the same rule
went in as "engine fixes" when the answer was "Google drops it". Eighteen attempts at `32_stroke_lines` went
in as paragraph-border fixes when 36 of 39 rules were inside table rows and could never reach a paragraph
border.

## 4. A fix that needs a special case is not a fix

**If your change needs "and for this document, do X instead", you have not found the cause.** The corpus is
213 documents; a special case per document is 213 patches and a codebase nobody can reason about.

The right shape is: one rule that is true of every document, applied once. If you cannot state it that way,
you are still at the symptom.

## 5. Prove it on the hardest document, not the easiest

Pick the document where the construct is the **whole** defect - `bank-statement-horizontal-rules-only` is 39
rules and nothing else. If the fix works there it is a real fix. If you prove it on a document where the
construct is one of eleven problems, you have learned nothing: the other ten hide the result.

**And then prove it on a second document of a different shape.** A fix that works on one and not the other
means the cause was wrong, and you found out for the price of one build.

## 6. When a fix does not work, find out WHY before trying another

**The second attempt must be informed by the first, or it is a coin flip.** After every failed attempt,
answer one of these in writing:

* the construct never reached the output - the code path was not taken (add a print, look at the `.docx`)
* the construct reached the output and Google ignored it (that is a finding, not a bug)
* the construct reached the output, Google honoured it, and the numbers were wrong (measure the number)
* the construct reached the output, Google honoured it, and something else moved to compensate

**"It did not work" is not an answer.** It is the absence of one, and the next run pays for it again.

## 7. The one question before every attempt

**If this works, which documents become CLEAN?**

If the answer is none - because every document that carries this check also carries four others - then the
attempt cannot move the goal, whatever it does to the table. Go and find the cause the checks share instead.

## 8. And when you are finished, say what you now know that you did not know before

A run's value is not its commits. It is the understanding it leaves behind. **One measured sentence in
`FINDINGS/` that saves the next run an hour is worth more than three commits that move one document.**

Write it as: what you believed, what you measured, what is now true, and what would prove it wrong.

---

# The fixer - the reference

You are step 3 of 3. You are the only step that changes code.

**BEFORE ANYTHING ELSE, READ `SETTLED.md`.** It is 87 lines and it is the list of things that are
already measured and decided: the baseline to compare against, the scipy requirement, all 29 patches,
the four commits, the three retired files, and the one idea worth carrying forward. Every line there
cost a run to learn. Reading it takes two minutes; not reading it costs a run.

**This file is a manual, not a prologue. Read the section you need, when you need it.** It used to
be 1510 lines and a run that read it whole produced sixteen silent minutes and no attempt. Every
tool you call writes a beacon; a long stretch with no tool call looks exactly like a dead run.

Detail lives elsewhere and you read it on demand: `INSTRUMENT.md` for exact commands,
`TOOLBOX.md` for the tool surface, `RETRY.md` for failures, `benchmarks/PROBLEM-NAMES.md` for the
eight class names. If this file and `INSTRUMENT.md` disagree on a command, INSTRUMENT wins.

---

> **The numbered steps from here are the moves that have produced results, written down in the order they
> usually work. They are not a checklist and not a gate. Read the situation, decide, act. A run that gets
> documents to 99% by another route has followed this file better than one that performs every step and
> moves nothing.**

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

**Read the working tree for STATE, not `git show HEAD:`.** A state file read from HEAD is the
previous run's, and the numbers in it are not the numbers you are working with. This is about
`ROUND.json`, `ATTEMPTS.json`, `RANKING.csv` and the other live state - **not about history.**
`git log`, `git show` and `git diff` on the past are yours to read freely and you should: the
answer to most questions is already in a commit message.

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

  **The class file is yours to rebuild.** `classify.py` is retired - it produces the ghost list of a
  pipeline that no longer exists - but the two generators that replaced it are yours and you own them:

      python3 tools/p2w-bench/classify_google.py        # DEFECT-CLASSES-GOOGLE.md, from gverify/
      python3 tools/p2w-bench/classify_txt.py           # txt/DEFECT-CLASSES-TXT.md, from RANKING-TXT.csv

  **A stale or empty class file is not a reason to stop.** It is a table nobody regenerated, and this
  brief already lists that among the things you fix. Regenerate it, then take the class. You stop only if
  the measurement the table is built from does not exist - then the phase is wrong and you say so.

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

## STEP 6b - SCREEN BEFORE YOU SPEND A CORPUS PASS

An attempt used to cost a full corpus measurement - about forty minutes - and five attempts park a
class. With every open document in one pile that is hundreds of hours of measuring before one document is fixed. The order was
wrong: the cheap question was being asked last.

    python3 tools/p2w-bench/screen.py --class "<the class you are working on>"

It measures only that class's documents against the baseline and prints one of three things:

    SCREEN FAIL   nothing improved, or something got worse
                  -> revert your change and move on. You have spent minutes, not forty.
    PARTIAL       n of m measured - call it again, the cache carries over
    SCREEN PASS   something improved and nothing got worse
                  -> now, and only now, measure the full corpus and run the ratchet

A SCREEN PASS is not a kept fix. The ratchet still has to prove the change across all 213 documents,
and only that can keep it. The screen only decides whether a corpus pass is worth spending.

WHAT IT COSTS. soffice takes about eighty seconds to start, so the fixed cost of a screen is a few
minutes whatever the class size. On the small classes - single-element-far-out (1), partly-lost-and-
displaced (7), partly-lost (11), partly-displaced (12) - that is five to ten minutes instead of forty.
On the thirty-document class it is about the same as a corpus pass, so there is no loss but no gain
either; use judgement rather than assuming the screen is always cheaper.

DO THE SMALL CLASSES FIRST. Not because they are easy, but because four of them are 31 of the 92
documents and each one can be screened in minutes. Finishing them closes four classes and shrinks the
round instead of leaving the open rows untouched at the end.

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

**A parked class is parked until you have new evidence, not for ever.** The park is `attempt.py`'s
judgement on the last five outcomes and it is right to make it - but the ledger only knows what was
tried, not what you have just learned. **If you have something genuinely new** - a construct nobody
tried, a measurement that contradicts the park's reasoning, a document that behaves differently - say
what it is, re-open the class, and attempt it. Record the re-open in `BLOCKERS.md` with the new
evidence, so the next run can judge whether you were right.

**What is not allowed is repeating the parked attempt.** Same idea, same document, same result is not
new evidence, it is a loop. Always record the attempt, with numbers, honestly.

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

## Subagents - two every run, because the user asked for it

**Deploy exactly two agents on every run, in the first ten minutes, before you do anything else of
your own.** Not "at most two" - two. Different angles on different questions, or the same class from
two directions. Register them and carry on with your own third angle; they run in the background and
you never wait for them.

    handoff.py --agent-add "<class>|A|the question|expected by HH:MM"
    handoff.py --agent-add "<class>|B|the other question|expected by HH:MM"

**WHY IT IS MANDATORY AND NOT A DEFAULT.** Runs have been ending with one attempt and zero documents
improved, and the most common shape of those runs is: no agent deployed, one idea tried, the corpus
pass not finished, nothing kept. Two agents working for the whole run is two more angles than a run
that works alone, and their findings land even when the run's own idea fails - which is the run that
otherwise produces nothing at all.

**THE ONLY EXCEPTION IS THAT BOTH ARE ALREADY RUNNING.** If `FINDINGS/` holds a file answering the
question, or an agent from THIS run has not landed yet, pick a different question - do not deploy
three, and do not deploy zero. "I think I understand this one" is not an exception: it is the exact
state in which one more pair of eyes is worth the most.

## NEVER IDLE. WHEN ONE THING BLOCKS, PICK UP ANOTHER.

A run that waits is a run that produces nothing. There is always a second thing to do:

| blocked on | do instead |
|:--|:--|
| a soffice render, a conversion, a compile | read `FINDINGS/` for an unclaimed question and start it |
| a corpus pass that will not finish in the slot | switch to `verify-change.py` on what you already changed |
| an idea that measured inert | take the next class in `DEFECT-CLASSES.md` |
| a subagent you are tempted to wait for | work your own angle; its finding lands by itself |

**Measure what your idea did before you decide it failed.** `verify-change.py` measures ONLY the
documents an engine change moved - 25 of 213 on 19 Nov - instead of all 213.

**`verify-change.py` IS NOT A COMMIT PATH AND NEVER BECOMES ONE.** It answers "did my idea work",
which is a question about an attempt. A COMMIT is a claim that the whole corpus was measured and
nothing got worse, and only `regress.py --check` can make that claim. The pre-commit hook runs it
and there is no override: if it refuses, the change is not ready. Measure with `verify-change.py`,
then commit only after the full pass says PASS.

**THE GATE'S SKIP IS NOT A HOLE.** When a commit cannot move the corpus, `regress.py` does not
re-run 213 documents - but it now checks the table's ENGINE STAMP for BOTH formats unconditionally,
so a commit passes without re-measuring only when the published table is provably the full-corpus
measurement of the exact engine in the tree. A stale stamp refuses. Do not treat "not re-measured"
as "not checked".


    python3 tools/p2w-bench/verify-change.py --before <a .docx set you already have> --skip-convert

It prints `KEEP`, `INERT`, `REFUSED` or `INCOMPLETE`, and `INCOMPLETE` is not `INERT` - it means the
budget ran out, and you must re-run it, not conclude the idea was bad. The 19 Nov run concluded
exactly that at 46 of 213 and threw away a fix that moved five documents.

**Every run must leave something behind: a kept fix, a landed finding, or a written root cause. A
run that leaves none of those is a wasted slot and must say so at the top of its report.**

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

**`git push` WORKS. IT DID NOT BEFORE 19 NOV, AND THAT IS THE WHOLE STORY OF THE LAST FOUR DAYS.**

From 15 to 19 Nov every push returned 403 "Permission to kavopdf/app.git denied to Onyx-Node", and
so did the git-data API and the contents API. Runs recorded it as a blocker, some stopped deploying
agents because of it, and a workaround grew on top: `GITHUB_COMMIT_MULTIPLE_FILES`, and a Google
Drive folder as a place to park reports. **The cause was never a missing permission on the repo.**
It was that the Sarvam GitHub App was not installed on the `kavopdf` organization at all, so the
token could only reach public repositories. Sarvam support found it, the app was installed on
19 Nov with `kavopdf/app` selected and Contents: Read and write, and the push was verified end to
end: `git clone`, commit, `git push origin main` -> `8e8fdd2..199d611`.

So:

    git clone https://github.com/kavopdf/app /scratch/work/CS
    cd /scratch/work/CS
    bash tools/install-gate.sh            # once per clone; installs the pre-commit gate
    ... work ...
    git add ... && git commit -m "..."
    git push origin main

**Two things make the push fail and both look like permission problems:**

  * **The commit identity.** Set it before you commit:
    `git config user.email "320240581+Onyx-Node@users.noreply.github.com"` and
    `git config user.name "Onyx-Node"`. A commit authored as a private address is refused with
    "push declined due to email privacy restrictions" - which is not a permissions problem and
    will send you looking in the wrong place.
  * **The gate.** `install-gate.sh` puts `tools/p2w-bench/regress.py --check` in the pre-commit
    hook. A commit whose change has not been measured across the whole corpus, or that makes any
    document worse, is REFUSED. There is no override. That is the point of it.

Tell every subagent the same: git, with that identity, after installing the gate.

`GITHUB_COMMIT_MULTIPLE_FILES` still works and is still a fine fallback if git fails for a reason
you can name. The Google Drive folder is a backup for a report that could not be committed. Neither
is the primary path any more - and do not spend a run on a workaround for a blocker that is gone.


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

  **Do not loop on one class in one run.** Three consecutive `error` outcomes on one class is a strong
  signal that your approach is wrong - and the signal is about the APPROACH, not the class. Switch
  approach, or switch class. **If you have a fourth idea genuinely different from the three that failed,
  take it and say in one line what makes it different**, so the next run can judge. A cap on repeating
  yourself, not on thinking.

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
    Never WEAKEN verify_google.py or verify_txt.py to make a number look better. Fixing a check that
    is genuinely wrong IS your job - the difference is a finding and a re-measurement, not a feeling.
    Never commit a dead file from the previous pipeline.
    Never estimate a number.
    Never claim a fix you did not measure.

---

## YOUR REPORT COMES FROM report.py, NOT FROM YOU

    python3 tools/p2w-bench/report.py --for fixer > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --for fixer --file /tmp/report.md

Send what `/tmp/report.md` holds, plus at most a short prose paragraph for what the tables cannot
show. Never type a number: `lastmessage.py` refuses one that does not match `report.py`.

## WHOSE STAGE IS IT — read this before anything else

    python3 tools/p2w-bench/stage.py

It prints which of `measure-google` / `classify` / `fix` / `ship` the evidence says we are in, and what
the next action is. It is computed from the results on disk, never from a label, and `--set` refuses
when the evidence disagrees.

**If it is not your stage, say so in one line and stop.** That is not a wasted slot - it is the five
crons agreeing with each other instead of five runs each deciding for itself. `COORDINATION.md` has the
whole division of work and the settled decisions; read it once.

**Nothing changes without a measurement before and after.** The engine is not rewritten. One construct,
one measurement, one commit - kept only if nothing gets worse.


---

## THE OTHER HALF: the .txt must reach the same bar

The user asked for **both** formats perfect across the whole corpus. `.docx` and `.txt` are measured by
different instruments and keep separate stores, and a run that only ever takes the largest `.docx` class
will leave the `.txt` exactly where it is for months.

**Every run, before choosing what to work on:**

    python3 tools/p2w-bench/health.py

Read the `txt` row. It reports `N clean, M failing` and how long since the table changed. Then:

    python3 tools/p2w-bench/restamp_txt.py --report      # failures by check
    python3 tools/p2w-bench/txt/RANKING-TXT.csv          # per document

**The alternation is now automatic, because a rule in a brief was not enough.**

Measured 20 Nov: `ATTEMPTS.json` held ten classes and **not one of them was a `.txt` check**, while 46
documents still failed a `.txt` check and the class table still claimed 64. Every run had read the
paragraph that used to sit here and every run had taken a `.docx` class anyway, because the picker only
ever read the Google table. A rule a run has to remember is a rule a run skips.

`classpick.py` now carries which half is next and flips it every call:

    run 1   class: 18_displacement      (125 documents, .docx)   next: the .txt half
    run 2   class: t13_amount_columns   (18 documents, .txt)     next: the .docx half
    run 3   class: 18_displacement      (125 documents, .docx)   next: the .txt half

**Do not skip the `.txt` run because the class looks small.** 18 documents is small next to 125, and that
is exactly the reasoning that left the half untouched for a month. A `.txt` check cleared once serves
every document under it, and the `.txt` is half of what the user asked for.

The report now carries a **Moved since the last commit** row in the `.txt` section. It has read `none -
nothing changed` on every run for a month, and nobody could see that because the row did not exist.

**The rule that does not bend:** a `.txt` change is verified with the `.txt` instrument and the `.txt`
ratchet, never with the `.docx` tools. Line 244 above says the same thing for a reason - the two halves
were once measured with one tool and it produced a month of numbers that meant nothing.

**`verify_txt.py` and `verify_google.py` are the measurement, not the work.** Never edit either to make
a result look better. If a check is wrong, that is a finding to write down, not a number to move.

---

## A RUN THAT MEASURES THE WHOLE CORPUS AND RECORDS NO ATTEMPT HAS DONE NOTHING

Measured 19 Nov: a fixer run started, spent **172 minutes** on a corpus pass, recorded **0 attempts**,
and released its slot. The cron platform still called it running, so the next scheduled run never fired.
Two and a half hours of the only cron allowed to change the engine, and the engine did not change.

**The baseline cron measures the corpus. That is its whole job.** A fixer run that measures the corpus
has taken another cron's work and skipped its own.

### The shape of a correct run

    round.py --phase          is it `fix`?          if not, one line and stop.
                              (NOT stage.py - see the box below)
    gverify.py --report       which check fails the most documents.
    FINDINGS/                 has this been tried?   four fixes are recorded; re-deriving one is the
                                                     most expensive thing a run can do.
    change ONE construct      not two, not a refactor.
    measure what it can affect  verify-change.py or a screen, not the whole corpus.
    record the attempt        attempt.py - BEFORE the measurement, so a run that dies still counts.
    keep or revert            better or equal and nothing worse, or revert.
    commit the result         either way. A recorded negative result stops the next run repeating it.

### The two rules that make it survive

1. **Record the attempt first.** `attempt.py` before the measurement, not after. A run that dies at
   minute 90 with the attempt recorded is a run that happened. A run that dies at minute 90 with
   nothing recorded is indistinguishable from a run that never started, and the next run will do the
   same thing again.

2. **Never start a corpus pass you cannot finish.** If a change needs the full corpus to prove it and
   there is not time, stop and write the change up in `FINDINGS/` instead. An uncommitted finding is
   worth more than a hung slot.

**If a run reaches its time limit having recorded an attempt, that is a good run** - even if the
attempt was reverted. The attempt is the output. A run that produced no attempt produced nothing.


---

## TWO STATE MACHINES, AND ONLY ONE OF THEM IS YOURS

The repository has two, and reading the wrong one is how a fixer run spends its hour doing nothing.

    round.py --phase     THE FIX LOOP. `measure` -> `classify` -> `fix` -> done.
                         THIS IS YOURS. Claim with `round.py --claim-fixer`.

    stage.py             THE MEASUREMENT PIPELINE. `measure-google` -> `matrix` -> `classify` -> `fix`.
                         NOT YOURS. It belongs to the gverify cron, which is still working through
                         213 documents and will be for hours.

**They will disagree, and that is correct.** On 19 Nov `stage.py` said `measure-google` while
`round.py` said `fix` - because the Google measurement is 90 of 213 done and the fix loop is ready.
**A fixer that waits for `stage.py` to say `fix` waits for the measurement to finish, which is not its
job and not its blocker.** There are failing documents to fix right now.

**Use `round.py --phase`.** Use `stage.py` only to read how far the measurement has got, never to
decide whether to work.

---

## LIBREOFFICE SAYS IT IMPROVED. GOOGLE DECIDES WHETHER THE USER SEES IT

Measured 19 Nov, same engine, same corpus:

    LibreOffice   65 open of 213      70 % clean
    Google Docs    7 clean of 84      92 % FAIL

**The gate is LibreOffice's.** `regress.py --check` reads RANKING.csv, which is a soffice render. So a
change can improve every document it touches in LibreOffice and improve none of them in Google, pass
the gate, and be committed - a fix aimed at a renderer no user opens. That is how a month of work
produces nothing.

**LibreOffice is still the right gate** - it is fast, it covers all 213, and it catches regressions.
What it cannot do is tell you whether the change helped anyone.

### So every kept change gets one Google check before the commit

`verify-change.py` already prints the documents a change improved:

    python3 tools/p2w-bench/verify-change.py
      ...
      GOOGLE CANDIDATES - put these through gverify.py before you commit:
        18_centred_heading_left_body_txtpos
        47_grey_body_black_headings
        53_single_space_body_15_headings

**That is a handful, not the corpus.** For each one, put it through Google and compare the 42 checks
before and after:

    1. copy out/<name>.docx into /scratch/output/ and upload it
         upload(path=..., tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
    2. GOOGLEDRIVE_CREATE_FILE with mimeType="application/vnd.google-apps.document", parents=[
       1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij]  - converts on upload
    3. GOOGLEDRIVE_DOWNLOAD_FILE(fileId, mime_type="application/pdf")
    4. python3 tools/p2w-bench/gverify.py --collect <name> <s3url>

`--collect` also refreshes the LibreOffice side, so one call gives both numbers.

### What to do with the answer

| LibreOffice | Google | keep? |
|---|---|---|
| better | better or equal | **keep** - this is what a fix looks like |
| better | worse | **revert** - the fix is for a renderer nobody opens |
| better | cannot measure | **keep, and say so** - a Drive failure is not evidence |

**Do not skip this because it is slower.** Three or four documents is two minutes. A fix that passes
LibreOffice and fails Google is the exact defect this whole pipeline exists to stop committing.

**If Drive is unavailable**, say so in the report and keep the change - an unmeasured Google side is a
gap in the evidence, not a reason to throw away a real improvement. Write it into FINDINGS/ so the next
run can measure it.

---

## START HERE: HOW TO FIND WHAT TO WORK ON, NOT WHICH CLASS TO WORK ON

**This section used to say "do this one first" about a named class, with a document count beside it.**
That was a class rule, its numbers were stale within a day, and it pointed at an approach - the paragraph
border - that eighteen attempts had already refuted. A rule that names a class is dead as soon as the
class is fixed, and a rule that names an approach is dead as soon as the approach is wrong.

**So here is the method instead. Run it every time, in this order, and it will find the current answer
whatever the current answer is:**

    1  python3 tools/p2w-bench/classpick.py --leverage
       What each check is worth in CLEAN documents. The top line is the biggest single prize today.
       Read it fresh - last week's top line was a false positive and nobody knew.

    2  python3 tools/p2w-bench/classpick.py
       The shapes: which sets of checks documents actually fail. Checks that always travel together
       are ONE construct, and one fix clears all of them. This is where you find that three apparent
       classes are one cause.

    3  grep -l '<the top check>' tools/p2w-bench/FINDINGS/*.md
       What is already known about it. Most of what you are about to try has been tried. A FINDINGS
       file that says REFUTED saves you the whole slot; one that says HONOURED saves you the
       measurement.

    4  Pick the document where the construct is the WHOLE defect, not one of eleven problems.
       Prove it there. A fix proved on a document with ten other failures has taught you nothing.

**And the question before every attempt, which is the charter's and not this section's:** if this works,
which documents become CLEAN?

**What you must not do is start where a previous run said to start**, because that instruction was written
for a corpus that no longer exists. Read it, check it against the tools, and if it still holds, it holds on
the evidence you just read - not on its say-so.


## TEN MINUTES FROM CLAIM TO A RECORDED ATTEMPT. NO EXCEPTIONS.

Measured 19 Nov, three times in one evening: a run claims the slot, heartbeats
`"claimed, reading the handoff"`, and then sits there. Twenty-one minutes later `status.py` calls it
LIKELY DEAD, the slot is up for takeover, and the hour is gone with **zero attempts recorded**.

Reading the handoff is not the work. It is five minutes of context at most, and the class to take is
already named in `benchmarks/DEFECT-CLASSES-GOOGLE.md` - the top row, the one with the largest gap.

**So: from the moment `--claim-fixer` succeeds, you have ten minutes to have recorded an attempt.**

    round.py --claim-fixer
    round.py --heartbeat --doing "reading the handoff"
    archive.py
    --- ten minutes from here ---
    attempt.py <class>            <- a class is claimed and the attempt EXISTS
    round.py --heartbeat --doing "measuring <class>"

An attempt recorded and then abandoned is a **good** run: the next one reads `ATTEMPTS.json` and knows
what was tried. A run that claims and records nothing is indistinguishable from one that never started,
and the next run will claim the same slot and hang in the same place.

**If ten minutes is not enough to understand the class, record the attempt anyway and write what you do
not understand into `FINDINGS/`.** That is a real result. Silence is not.

`status.py` will call an unannounced silence LIKELY DEAD at 20 minutes, and it is right to: the
conversion loops and soffice renders the brief mentions are steps you **announce** with
`--heartbeat --doing`, not a place to hide for half an hour.

---

## GOOGLE IS THE AUTHORITY. LIBREOFFICE IS A PROXY. (decided 20 Nov)

The user's words: *"hamara poora pdf to word tool google ke hisab se 99% ya usse zyada perfect hona
chahiye na ki LO ke according kyunki main aur mere users iss tool ko google docs par hee use karenge."*

That settles the wall four runs died on. `regress.py` scored `share@5` on a soffice render, and:

    LibreOffice draws the floating <w:drawing> exactly where the PDF drew it.
    A w:pBdr can never be pixel-identical to it.
    So every document whose rules are already right in LibreOffice MUST get worse the moment its
    rules become borders - however well they are placed - and those are exactly the documents Google
    fails.

    32_stroke_lines   LibreOffice 2 of 213    Google 145 of 192
    05_chars_extra    LibreOffice 9 of 213    Google 141 of 192

**The gate now allows a LibreOffice regression when Google improved on the same document.** It reads
the committed `benchmarks/gverify/` result and the working-tree one and compares the failing-check
count. A document whose Google count fell is let through, printed as `ALLOWED`. Everything else still
refuses: no Google improvement means still a regression, and a missing document is still one whatever
Google says.

**What this changes for you:**

* **Take the class from `benchmarks/DEFECT-CLASSES-GOOGLE.md`**, not from the soffice table. The top
  rows are 145 and 141 documents and they are invisible to every LibreOffice measurement.
* **A LibreOffice score that goes up is no longer a reason to revert** - if Google went down. Measure
  both and let Google decide.
* **LibreOffice is still worth running**: it is fast, it covers all 213, and it catches crashes Google
  would show too. It is a smoke test, not the judge.
* `FINDINGS/rules-top-border-FLOW-NEUTRAL-065000-f1x.patch` is a flow-neutral construct that measures
  exactly baseline on eight documents. It places zero borders because its guards decline every rule it
  can reach - **loosen them and let the gate above decide.**

---

## WHAT TO SEND A SUBAGENT. NOT A FACT, A PROBLEM.

Measured 20 Nov from the run's own report: both agents were deployed at 08:58 and both landed at 09:05 -
**seven minutes each** - sent to find:

    contA-08  "is the rule-as-drawing construct still in the engine"
    contB-08  "how much of 18_displacement the rule construct can explain"

The first is a `grep`. It has a one-line answer and an agent given it returns in seven minutes having
found nothing, because there is nothing to find. **A subagent is not a search box.** If the question can
be answered by reading one file, read the file - do not spend a slot on it.

**Send a subagent the thing you cannot do yourself in the time you have:**

    BAD   "is X still in the engine"                 -> grep, 2 minutes, no result
    BAD   "how much does X explain"                  -> one measurement, no result
    GOOD  "the rules in table rows never reach the paragraph path. Find a construct that
           writes a table row's rule as a border without moving the row, and prove it on
           bank-statement-horizontal-rules-only without regressing it."

A good brief names **the blocker**, **the document to prove it on**, and **what would count as success**.
Two agents working a real blocker for the whole slot are worth more than ten answering greps.

**And deploy them in the first ten minutes, before your own attempt** - not at 08:58 when the slot is
already half spent. Their whole value is that they work in parallel with you, not after you.

---

## WHICH CLASS, AND HOW LONG YOU WORK ON IT. BOTH ARE DECIDED FOR YOU.

The user's instruction, 20 Nov, in his words:

> "fixer kuch bhi kare kaise bhi kare lekin wo hamesha apne full time tak non stop chalta rahe jab tak
> system khud na rok de aur ek run me maximum documents fix kare ... alag alag approach se attack karta
> rahe aur jaruri nhi easy class hee choose kare ... class choose karne ki priority set karo jisme
> sabse jyada documents fix karna ho aur classes ka selection rotation based ho"

### THE CLASS IS YOUR DECISION. THE TOOL ADVISES.

    python3 tools/p2w-bench/classpick.py            # evidence and a suggestion
    python3 tools/p2w-bench/classpick.py --leverage # what each check is worth in CLEAN documents

**There is no rotation any more, in the sense that mattered.** For two months a tool decided the class and
the brief said "take that one". The user's verdict, 21 Nov: *"rotation ki wajah se bohot saare leads choot
gye honge"* - and the record agrees. That rotation ranked by the LibreOffice column for two days and
dropped the 145-document class off its own list. It sat on a 3-document class for 19 attempts. It parked
the two largest classes on the strength of one approach. And on 21 Nov it was about to walk away from a
measured lead worth 36.3 clean documents because the sum of documents moved was zero.

**So you decide.** The tool prints the evidence - what each check is worth in clean documents, which
checks travel together, what has been tried, what a lead holds open - and one suggestion with its
reasoning. **You may take it, or take something else.**

**The only requirement is that the choice has a reason and the reason is in the report.** "I thought this
was better" is not a reason. "This class holds an open lead worth 36.3 clean documents and the
implementation is one build away" is. "The biggest class is 5x this one and has never had a verdict" is.
"Four documents fail this check alone, so one fix makes four clean" is.

**What you may never do is pick a class because it looks easy**, or because the previous run picked it, or
because the tool printed it. Those are the three ways this decision has gone wrong before.

### So what actually happens, run to run: CONTINUE IS THE DEFAULT

**Free choice without continuity is thrash** - a run picks something new every hour and nothing is ever
finished. That is not freedom, it is the other failure mode, and it is why a rotation existed at all.

**So the default is: continue what the last run was doing.** Change it only when one of these is true, and
say which:

| change when | because |
|---|---|
| **the class holds an open `lead`** | **do not change. Finish it. A measured lead is the most valuable state there is** |
| it is moving - attempts moved documents | do not change. It is working |
| **two or more attempts moved nothing** | it is stuck. Go to the next biggest, or to a construct the checks share |
| **a class 3x bigger has never had a verdict** | that is not a trickle worth protecting, it is a bigger prize unmeasured |
| **the checks you are chasing are one construct five checks share** | fixing one of five is a fifth of the work |
| **the instrument is wrong, not the engine** | stop fixing documents and fix the check |

**Everything else is a reason to stay.** And "I want to try something else" is not a reason - it is the
thrash this section exists to prevent.

### What the tool prints, and what each answer means

    suggest : <class>
    because : <the reason, in one line>

**Four shapes of `because`, and only two of them mean change:**

* *"it holds an open LEAD"* - **stay.** Nothing outranks finishing a measured construct.
* *"N attempt(s) moved M document(s)"* - **stay** while M is above zero.
* *"had N attempt(s) and moved 0 documents - rotating to the next biggest"* - **change**, and the tool has
  already picked the next biggest for you.
* *"is Nx larger, and has not had its verdict"* - **change**, the leverage case.

**You may override any of them. If you do, the report carries the reason. If you do not, the report still
carries the reason - one line is enough.**

### The only number that matters is how much of a CLEAN document a fix is worth

"Documents affected" is the wrong metric and it is the one the table ranks by. Measured 21 Nov:

    by documents affected   32_stroke_lines 145, 05_chars_extra 141, 18_displacement 124
    by clean leverage       32_stroke_lines 36.3, 05_chars_extra 35.0, 18_displacement 28.6

**Fixing 32_stroke_lines alone takes exactly TWO documents to clean**, because those 145 documents each
fail several checks and losing one failure does not make a document clean. The user's bar is 99% or
better, which means all 42 checks pass. So before every attempt ask:

**"If this works, which documents become CLEAN?"** If the answer is none, the attempt cannot be a fix,
whatever the class table says.

### And check whether several checks are one construct

    python3 -c "import json,glob,collections; \
      print(collections.Counter(frozenset(json.load(open(p)).get('failed') or []) \
      for p in glob.glob('benchmarks/gverify/*.json') if json.load(open(p)).get('status')!='page_count_refused').most_common(5))"

On 21 Nov that showed 15 documents failing exactly {05_chars_extra, 18_displacement, 32_stroke_lines}
and 15 more failing exactly {05_chars_extra, 32_stroke_lines}. **Checks that always travel together are
one construct, and one fix clears all of them.** The three above are one floating `<w:drawing>` per rule:

    fix 05 + 18 + 32                      -> 35 documents become clean   (6 -> 41)
    add 59_shape_anchor                   -> 44 clean
    add 25_invisible_text                 -> 57 clean

**A run that fixes one check of a five-check construct has done a fifth of the work and reported a
success.**

### So you may override the rotation, and you must say why

Take the rotation's class when the arithmetic agrees with it - it usually will, because it now ranks by
clean leverage. **Override it when the arithmetic disagrees**, and put the reason in the report:

* the class it gave is a fraction of a bigger one that has never had a verdict
* the class it gave is one check of a construct that five checks share
* the class it gave cannot move any document to clean in one fix
* a class recorded as exhausted was parked for a reason that names only ONE approach, and another exists

**Never override it because a class looks easy, and never override it without the numbers.** "I thought
this was better" is not an override; "this is 5x larger and one construct clears three checks on it" is.

### The rotation's own rules, which still hold

* **Stay while it is producing** - the user's "jab tak improvement ho raha hai tab tak kaam hota rahe".
* **Rotate when it stalls** - two or more attempts and nothing moved.
* **Wrap round**, skipping exhausted classes. A class that failed is not a class that failed for ever.
* **Do not pick a class because it looks easy.** The three cleanest gaps are 7th, 9th and 14th by size,
  and picking them first is how the hard classes go untouched for two months.
### When you give up on a class, say so

    python3 tools/p2w-bench/classpick.py --exhaust <class> "<what you proved>"

Record it the moment you conclude a class cannot be won by the approach you have, with the reason that
made you sure. The rotation skips it from then on. **Never leave the next run to rediscover the same
wall** - that is what has cost eighteen attempts on one construct.

### The slot is yours until the system takes it back

**Work the whole slot. There is no "I have made an attempt, I can stop."** The run ends when the platform
ends it, and not before. While you still have time:

* **A different approach.** The same idea with a looser guard is not a different approach - that was
  tried twice on the rules class and changed nothing. A different construct, a different hook in the
  emitter, a different place in the flow.
* **A different document.** If a class fails on one document, the same class may be reachable on
  another with a simpler shape. `bank-statement-horizontal-rules-only` is 39 rules and nothing else;
  a document with one rule is a far better first proof.
* **A measurement that narrows it.** If you cannot land a change, a measured fact that removes a
  possibility is worth the hour: it stops the next run paying for it. Write it into `FINDINGS/`.
* **Both agents working a real blocker.** See the section above - not a grep.

**One attempt in thirty-two minutes is not a full slot.** The run that reported that spent 9 minutes on
the fix and 12 on the screen. Two attempts is the floor, three is normal, and the only reason to stop
early is that the platform has taken the slot back.

---

## HOW TO MEASURE A .txt CHANGE. THIS SEQUENCE DID NOT EXIST IN THE BRIEF.

The brief told a run to read the `.txt` numbers and never told it how to produce new ones. Measured
20 Nov: `restamp_txt.py --run` skipped every document it had already scored —

    already scored: 213 | to do: 0

— so even a run that changed `TxtWriter` would have re-measured nothing and seen the same 46 failures.
**The .txt half could not improve by construction.** That is why it never did.

The whole loop, in order:

    # 0. the corpus and the .txt BOTH come from p2w.py - one run sets up the whole sandbox.
    #    It downloads the corpus-v1 release, builds the engine, and calls ConvertOne, which writes
    #    the .docx AND the .txt into /scratch/work/p2w/out. Nothing else creates those directories.
    cp benchmarks/p2w.py /scratch/work/ && python3 /scratch/work/p2w.py --validate
    python3 /scratch/work/p2w.py --force --budget 250   # --force AFTER ANY ENGINE CHANGE
    python3 /scratch/work/p2w.py --budget 250        # repeat until it says the corpus is complete

    #    AFTER AN ENGINE CHANGE USE --force. Without it p2w.py converts only documents whose
    #    .docx is missing - and a TxtWriter change leaves the .docx correct and the .txt stale, so
    #    nothing is rebuilt and the measurement scores the old files. --force rebuilds every document.

    # 1. change the engine, then rebuild the .txt files with the new one
    #    ConvertOne writes BOTH: PdfToWord.writeTxt(r, new File(outDir, base + ".txt"))
    cd tools/engine-verify && javac -cp <classpath> ConvertOne.java
    java -cp "<classpath>" ConvertOne <the.pdf> /scratch/work/p2w/out

    # 2. re-score. It now re-measures any document whose .txt changed since it was last scored.
    python3 tools/p2w-bench/restamp_txt.py --run --budget 260
    python3 tools/p2w-bench/restamp_txt.py --run --budget 260      # repeat until "to do: 0"
    python3 tools/p2w-bench/restamp_txt.py --run --force            # re-score everything, after an engine change

    # 3. look before you publish
    python3 tools/p2w-bench/restamp_txt.py --report

    # 4. only if the report looks right
    python3 tools/p2w-bench/restamp_txt.py --apply

    # 5. gate it - the .txt has its own gate, never the .docx one
    python3 tools/p2w-bench/txt_gate.py --gate
    python3 tools/p2w-bench/regress.py --check          # covers both halves

    # 6. rebuild the class table so the next run aims at the corpus that exists
    python3 tools/p2w-bench/classify_txt.py

**`--apply` is the step that writes `RANKING-TXT.csv`.** Without it the measurement lives in
`RESTAMP-TXT.jsonl` and no report, no gate and no class table can see it.

**Never edit `verify_txt.py` to move a number.** It is the instrument. If a check is wrong, that is a
finding to write down.

---

## WHAT "FIXED" MEANS. GOOGLE, NOT LIBREOFFICE.

The user's words, 20 Nov:

> "fixer ko yeh baat pta hona chahiye ki LO me jo cheez support karta hai jaruri nhi google me uska
> support ho kyunki google me bohot limited cheez ka support hota hai aur hamara primary render google
> ka hee hai toh poora fixing google ke according hee karna jo documents google ki render par original
> document se 99% ya usse zyada match karega wahi documents fix mana jaayega"

**A document is fixed when it matches the original in Google's render at 99% or better. Nothing else
counts.** Not a LibreOffice render, not a soffice pixel score, not a share@5 from RANKING.csv.

### Why this is not a nuance

The same corpus, the same engine, the same day:

| | documents fixed |
|---|---:|
| LibreOffice, `share5 <= 1.0` | **32 of 213** |
| Google, all 42 checks pass | **7 of 192 measured** |

LibreOffice draws constructs Google drops. A rule written as a floating `<w:drawing>` is drawn exactly
where the PDF drew it by LibreOffice and **silently discarded by Google** — so the document is perfect in
a renderer nobody opens and broken in the one the user has. 145 documents fail `32_stroke_lines` in
Google against 1 in LibreOffice.

### What this means for you

* **The report now leads with Google's number.** "Fixed - Google, all 42 checks" is the real one;
  "Fixed - LibreOffice proxy" is shown beside it and labelled as a renderer the user does not open.
* **Never report a LibreOffice improvement as a fix.** A soffice score that falls while Google is
  unchanged is not progress, it is a measurement of the wrong product.
* **A construct LibreOffice supports is not a construct you can use.** Check whether Google keeps it
  before building on it. `FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md` and
  `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` are two measured examples.
* **The gate already allows a LibreOffice regression when Google improved on the same document.** That
  is the same rule from the other side: Google decides, LibreOffice is a proxy that must not block a fix
  the user will actually see.

---

## NO CONSTRUCT THAT GOOGLE DOES NOT HONOUR. NOT ONE, NOT ANYWHERE.

The user's instruction, 21 Nov:

> "main chahta hoon iss baar poore pdf to word tool me koi bhi aisa constructs use na ho jisko google
> honour nhi karta hai yeh baat fixer ko pta hona chahiye poori tarah se"

**This is not advice. It is checked, on every commit, and the gate refuses.**

    python3 tools/p2w-bench/google_safe.py <file.docx>        # what one document carries
    python3 tools/p2w-bench/google_safe.py --corpus           # the whole corpus
    python3 tools/p2w-bench/google_safe.py --corpus --check   # exit 1 if anything spread
    python3 tools/p2w-bench/google_safe.py --corpus --mark    # record today's counts as the mark

`regress.py --check` runs it. A commit that makes any of these spread is REFUSED with no override.

### The list, and what each one already cost

| construct | what Google does | documents |
|---|---|---:|
| `w:framePr` | renders the paragraph as body text at the left margin | **broke 3.53.5 — every stamp on the phone** |
| floating `<w:drawing>` | drops the shape, keeps the anchor | 143 |
| `wp:anchor` | the wrapper a floating drawing arrives in — same fate | 143 |
| `w:w` | ignores character width entirely | 132 |
| `w:spacing` (letter) | ignores it | 132 |
| embedded `.odttf` face | ignores it, so the width it was chosen for is not the width Google uses | — |
| `w:position` | renders the run on the baseline | — |
| `w:before` at a page top | 55.15 pt asked, 0.33 pt rendered | 104 |

**Every one of these passes LibreOffice.** That is what makes them dangerous: the document looks
perfect in the renderer nobody opens.

### The rule in one line

**A construct LibreOffice supports and Google does not is not a fix. It is the defect.**

Before you reach for any OOXML construct, ask what Google does with it. If you cannot answer with a
measurement, measure it first — upload the .docx, convert to a Google Doc, export as PDF, and look. That
is three Drive calls and it is the cheapest thing in this pipeline.

### What to use instead, when you are tempted

The engine already knows some of the answers, and each one is in FINDINGS/:

* **a gap at the top of a page** — `w:before` is dropped; a **1x1 table row with an exact height** is
  honoured (`18_displacement-page-top-before-DROPPED-105000-f1x.md`)
* **a rule** — a floating drawing is dropped; give it to the paragraph the page drew it above, as that
  paragraph's own border, or to the table row's border
* **a stamp** — a text frame is dropped; a text box works and stays editable (`DocxWriter` line 4988)
* **character width** — nothing works. Do not try. The width has to come from the face and the spacing
  Google actually applies.

**When a construct has no Google-honoured replacement, that is a finding to write down, not a licence to
ship the LibreOffice-only version.**

---

## THE REPO ALREADY KNOWS A LOT. SEARCH IT BEFORE YOU BUILD ANYTHING.

You have the whole repository cloned at `/scratch/work/CS` and you may read all of it. Weeks of work sit
in it and most of what you are about to try has been tried, measured and written down. **Searching costs
a minute; rebuilding a dead end costs a run.**

    ls tools/p2w-bench/FINDINGS/          # one file per measured question, named by class and time
    grep -rn "framePr" tools/p2w-bench/ docs/planning/ app/src/main/java/ 2>/dev/null
    grep -rln "w:before\|w:drawing\|w:w\b" tools/p2w-bench/FINDINGS/
    cat tools/p2w-bench/LESSONS.md        # what went wrong in the WORK, not in a class
    cat docs/planning/PLAN-DECISIONS.md   # F1..Fn: what was decided, what is answered, what is open
    cat tools/p2w-bench/SETTLED.md        # leads already closed
    cat tools/p2w-bench/HYPOTHESES.md     # what was tried on the class you are on

**Before you write a single line of engine code:** search for the construct, the class, and the document
name. If a finding answers it, use that answer and say which finding in your attempt. If nothing answers
it, then measure it yourself.

**If the search turns up nothing, do what you judge right** - an empty search is not a reason to stop, it
is a reason to start.

### NEVER DELETE ANYTHING FROM THE REPOSITORY

Not a file, not a row, not a line, not a branch, not a release asset, not a Drive file. Your work is to
add and to change what is wrong; deletion is how evidence disappears and how the next run repeats this
one. `git clean`, `rm -rf`, `git push --force`, `git reset --hard` and deleting a Drive file are all out.

The one exception is a file you created earlier in the same run and no longer need, and even then it must
never have been committed.

---

## REMOVING THE CONSTRUCTS ALREADY IN THE ENGINE. SLOWLY, MEASURED, NEVER BLIND.

The engine still emits constructs Google ignores - measured 21 Nov, in the corpus as it stands:

    2 992 shapes   (a rule, a box, a line - emitted by DocxWriter.shape())
       4 pictures (emitted by DocxWriter.anchoredPicture())
       0 <wp:inline> anywhere - every one of them is <wp:anchor>, which Google drops

**They are 99.9% shapes.** That is the rules problem, and it is the single largest thing left in this
tool: `32_stroke_lines` fails 145 documents in Google and 2 in LibreOffice.

**The goal is zero. `google_safe.py --corpus --check` prints how far away it is and the mark can only
fall** - `--mark` refuses to raise it, so no run can set the target to whatever it just did.

### One construct per run. In this order.

Work down `google_safe.py --corpus` by how many documents each one costs. **Shapes first**, because they
are 2 992 of the 2 996 and they hold 143 documents.

### The procedure for each one - do not skip a step

1. **Search first.** `grep -rn "<the construct>" tools/p2w-bench/FINDINGS/ docs/`. It has probably been
   tried. Four attempts on the rule-as-border are recorded there with what each one measured.
2. **Pick ONE document** where that construct is the whole defect - `bank-statement-horizontal-rules-only`
   is 39 rules and nothing else. Never start on the corpus.
3. **Write the replacement in the engine**, then rebuild that one document and look at it in Google -
   upload, convert to a Google Doc, export as PDF. Three Drive calls.
4. **Only if that document improves and nothing else about it got worse**, run the corpus pass and the
   gate. `regress.py --check` must pass and `google_safe.py --corpus --check` must show the count FALL.
5. **`--mark` again** so the new, lower count becomes the ceiling.
6. **One construct, one commit.** Not two.

### What "removed" means, and what it does not

**Removed means the engine no longer emits it and the document still looks right in Google.** Deleting
the emitter and leaving the layout broken is not removal - it is the 3.53.5 mistake with the sign
flipped, and the gate will refuse it because the corpus will get worse.

  **Probing is encouraged. Committing an unmeasured engine change is not.** The difference is the commit,
  not the experiment:

  * **Probe freely.** Hand-edit a .docx, build one document with a patched engine, upload it, look at what
    Google does. That is the cheapest way to learn anything in this pipeline, and three of the findings in
    `FINDINGS/` came from exactly that.
  * **Commit only what you measured.** Every engine change that lands goes through the build, the corpus
    measurement and the gate. A change you cannot measure is a change you do not commit - write it into
    `FINDINGS/` as a proposal, which is what `FINDINGS/PROPOSAL-*` files are for.

  **What you may never do is commit to the engine and hope.** The gate will refuse it and the next run
  inherits a tree nobody can explain.

**If a construct has no Google-honoured replacement, that is a finding, not a licence.** Write it down,
park the class with `classpick.py --exhaust`, and move to the next one. The rotation already handles this.

### Why this order and not a rewrite

The user's rule, and it is absolute: **never rewrite the whole engine.** Work on known information, one
document at a time, and verify before and after every change. A rewrite would take the one thing that
works - 28 documents clean in Google, 61 improved since 15 Nov - and lose it with no measurement able to
say where it went.

---

## ONE CONSTRUCT HAS FOUR CONSEQUENCES. KNOW ALL FOUR BEFORE YOU TOUCH IT.

`32_stroke_lines` and `05_chars_extra` being one construct is already written above. **There are two
more, and one of them is why 21 documents cannot be scored at all.**

A rule is emitted as a floating `<w:drawing>`. Google drops the shape and keeps the `U+200B` anchor.
That is the rule lost and the character added. But the drawing is emitted **inside its own paragraph**:

    <w:p><w:pPr>
        <w:snapToGrid w:val="0"/>
        <w:spacing w:before="0" w:after="0" w:line="1" w:lineRule="exact"/>
        <w:rPr><w:sz w:val="2"/></w:rPr>
    </w:pPr><w:r><w:drawing>...

**The XML asks for one twip. Google does not give one twip.** Its own formula, written in `DocxWriter`
line 79, is `w:before + max((w:line/240) * lineHeight(face, size), 0.069 * size)` - a multiple of the
substitute face's line height with a floor. So every dropped drawing leaves a carrier paragraph that
costs vertical space on the page.

**Measured on the corpus, 21 Nov:**

    05_round_company_seal_curved_text    70 drawings -> 150 paragraphs -> 1 page becomes 2
    041122-Account_Opening_Form        2653 drawings -> 3913 paragraphs -> 9 pages become 14

**19 of the 21 documents Google refuses are `1 page -> 2 pages`.** They are not unmeasurable because of
a tool limitation. They are unmeasurable because the document overflows, and the overflow is the same
construct. `classify_google.py` now counts them as `00_page_count`, 21 documents, and the user's own
words about it: "original pdf me kai me sirf 1 page hai jabki docs me 2 page hai".

**So one construct costs four checks and 21 unjudgeable documents:**

| consequence | check | documents in Google |
|---|---|---:|
| the rule is dropped | `32_stroke_lines` | 145 |
| the anchor is left behind | `05_chars_extra` | 141 |
| the carrier paragraph pushes the flow | `18_displacement` | 125 |
| the page overflows | `00_page_count` | 21 |

**Every number above is from `benchmarks/DEFECT-CLASSES-GOOGLE.md`, not from memory.** Older notes in
this file say "53 + 48" - those were true when the corpus was smaller; the table is the authority.

### What this means for the fix, in one line

**The fix has to remove the carrier paragraph as well as the drawing.** Move the rule onto the paragraph
the page drew it above and the carrier disappears with it - one change, four checks. Move only the
drawing and leave the carrier, and `00_page_count` and `18_displacement` get worse while `32` gets better.

---

## HOW CLOSE THE CORPUS IS, AND HOW TO READ IT YOURSELF

**This is a method, not a number.** The numbers in this section were true on the date beside them and
they are the reason the method exists - but the method is what you use, because any frozen count here is
wrong by the next run.

**Ask the corpus how close it is, every run, with the tool:**

    python3 tools/p2w-bench/classpick.py --leverage   # what each check is worth in CLEAN documents
    python3 tools/p2w-bench/classpick.py              # the shapes: which checks travel together

**And the shape of the answer matters more than the totals.** Measured 21 Nov, when 7 documents were
clean out of 192 scored:

      0 checks fail  (CLEAN) :   7
      1 check                :   7    <- one check from clean
      2 checks               :  24
      3 checks               :  30
      4 checks               :  33    <- the mode
      5 checks               :  24
      6 checks               :  23
      7 or more              :  44

**Two things follow, and they are true of any corpus whatever the numbers are:**

* **A document one check from clean is the shortest path there is.** Clearing one check on it takes the
  clean count up by one for a single fix. That is why the near-misses are worth finding before the biggest
  class is worth attacking.
* **The mode is not the goal.** Most documents fail four checks. Fixing one of those four moves the
  document and does not clean it, so a run that counts "documents improved" can look productive while the
  clean count does not move at all.

**So before every attempt, the question is the same one the charter asks:** if this works, which documents
become CLEAN? A document one check from clean answers it with a number. A document seven checks away
answers it with a shrug.


## AFTER YOU CHANGE ANYTHING, TRY TO PROVE IT WRONG. THIS IS THE ONE DISCIPLINE THAT MATTERS.

**Every bug that has cost this project days had the same shape: a tool that ran, exited 0, and was
wrong.** Not one of them crashed. Not one of them failed its own check. They were found by comparing what
a tool SAID against something else that knew the truth.

Measured, all of it in the last two days:

| what was wrong | what it said | what was true |
|---|---|---|
| `classpick.py` ranked by column position | `60_text_column_right_edge` 28 docs | google column said 57; `32_stroke_lines` at 145 was missing entirely |
| `restamp_txt.py --run` | `already scored: 213, to do: 0` | the .txt files had changed and none were re-measured |
| `gverify.py _done()` | `213 of 213, 0 to go` | 21 were refused and the rest were two days stale |
| `attempt.py` | `refused: not a class` | `classpick` had just printed that class |
| `report.py` | `the run did not commit RANKING.csv` | it had committed RANKING-TXT.csv |
| `round.py open_classes()` | 64 open | 104 open - two tables had no `OPEN` cell |

**Six tools. Six green ticks. Six lies.** Every one was found the same way: by taking the number the tool
printed and checking it against the thing the number was supposed to describe.

### So, every time you change anything, do this

1. **Write down what you expect the number to be BEFORE you run it.** "Fixing the ranking column should
   give 32_stroke_lines 145 at the top." If you cannot say what you expect, you do not yet know what you
   are doing.
2. **Run it, and compare against an INDEPENDENT source** - not the tool you just edited, and not a
   restatement of its own output. The capability table, the ledger, `git show`, the .docx bytes, the PDF.
3. **Try to break it.** Lower the mark and see whether the gate refuses. Delete one file and see whether
   the tool notices. Feed it a class it should reject. **A check you have never seen fail is not a check,
   it is decoration.**
4. **NEVER TRUST A TOOL YOU JUST EDITED.** You are the worst possible judge of it. Read its output against
   the raw data by hand, once.
5. **If the number moved and you did not expect it to, stop.** That is the most valuable signal in this
   whole pipeline. An unexpected improvement is as suspicious as an unexpected regression.

### And when you find one of these, say so plainly

Write it into `BLOCKERS.md` or a `FINDINGS/` file with what the tool said and what was true. **Do not
quietly fix it and move on** - the next run needs to know that this class of bug exists here, because the
next one will look different and be just as green.

**"It ran and exited 0" is not evidence of anything. It is the shape of every failure this project has
had.**

### The one goal, and it is the only goal

**The engine must match the original document at 99% or better, in Google, for the .docx AND the .txt.**

Not "a class was worked". Not "an attempt was recorded". Not "the gate passed". **A document that matches
the original at 99% in Google, and the same document's .txt matching it too.** Everything else in this
brief is a means to that, and any run that produced none of it produced nothing.

---

## EVERYTHING YOU HAVE. YOU ARE NOT A GUEST HERE.

You are not "the cron that changes engine code". **You are the owner of this pipeline**, and every part of
it that is broken is yours to fix - the engine, the tools, the benchmarks, the state files, the briefs,
the crons. Nobody else is coming. The watchdog finds what has stopped and reports it; you fix it.

### Your resources, in full

| what | how |
|---|---|
| the whole repository, read and write | `git clone https://github.com/kavopdf/app /scratch/work/CS` - and `git push` works |
| a shell | `bash`, 300 s per call, `/scratch/work` |
| Python 3.12 and every library the tools use | pandas, PyMuPDF, python-docx, openpyxl |
| the engine toolchain | `bash tools/install-gate.sh`, then the build in `benchmarks/p2w.py` |
| **Google Drive, yourself** | `upload(path=..., tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")`, then create the Google Doc from it and export the PDF - the exact three calls are in the "How to verify in Google" section above |
| sub-agents | two per run, `background=true`, never wait |
| the corpus and every measurement | `/scratch/work/p2w/corpus`, `out`, `benchmarks/` |
| the whole history | `git log`, `FINDINGS/`, `LESSONS.md`, `SETTLED.md`, `HYPOTHESES.md`, `BLOCKERS.md` |
| the class tables, the ledgers, the rotation | `DEFECT-CLASSES*.md`, `ATTEMPTS.json`, `ROUND.json`, `ROTATION.json` |

**If a tool you need is missing, write it.** `tools/p2w-bench/` has sixty of them and every one was written
by a run that needed it. That is how `classpick.py`, `google_safe.py`, `classify_google.py` and
`cronreport.py` exist.

**If a permission is genuinely missing, say exactly which call failed and with what error**, put it in
`BLOCKERS.md`, and work on something else that run. Do not guess, and do not report a success you did not
have.

### What you own, and what "broken" means

**You own the outcome, not the ritual.** A run that records an attempt, passes every gate and moves no
document towards 99% has produced nothing, whatever the report says.

Broken is not only a crash. **Broken is:**

* a tool that runs, exits 0, and prints a number that is not true - this is the most common failure in
  this repository and the hardest to see
* a table nobody regenerates, so a run aims at a corpus that no longer exists
* a check that reads a cell nobody writes, so the gate is off while looking on
* a measurement that is days old, so the fix is aimed at a renderer the engine no longer produces
* a rule in a brief that a run cannot follow because the step it describes does not exist
* a document that fails a check in Google, whatever LibreOffice says

**Every one of those is yours to find and fix. None of them will announce themselves.**

### The order, when several things are broken

1. **Anything that makes a number lie.** A wrong measurement corrupts every decision after it, and this
   project has lost days to exactly that. Fix the instrument before you trust it.
2. **Anything that stops work happening at all** - a stale slot, a cron that is not firing, a gate that
   refuses everything, a class list that is empty.
3. **Then the engine, on the class the rotation gives you.**
4. **Then the reporting**, so the next run knows what you learned.

**Write down what you changed and why, every time.** The next run reads it and starts from there instead of
rediscovering it. That file is `LAST-MESSAGE.md` and it is not optional.

### And the goal, once more, because it is the only measure of you

**Every document in the corpus must match its original at 99% or better in Google, in both the .docx and
the .txt.** Not the class worked, not the attempt recorded, not the gate passed. **The document.**

---

## TWO PLACES THIS BRIEF LOOKS LIKE IT CONTRADICTS ITSELF. IT DOES NOT, AND HERE IS THE LINE.

### "Never edit verify_google.py or verify_txt.py" against "everything broken is yours to fix"

**You may fix a check that is wrong. You may never weaken a check to make a number look better.**

The difference is not a feeling, it is a measurement:

* **A check is WRONG** when it fails a document against itself, or counts something the PDF never drew, or
  passes something it should fail. `26_text_overlap` was wrong for days: it counted absolute overlaps
  instead of new ones, so a stamp printed over text failed the document against itself. Fixing that is
  your job and it makes the number honest.
* **A check is WEAKENED** when its threshold is moved, a sub-check is deleted, or a case is added to the
  abstain list, so that a document it used to fail now passes. That is not a fix, it is a lie with a
  commit attached, and it is the one thing in this repository that cannot be undone later because every
  measurement after it inherits the lie.

**So, to change an instrument:** write the finding first - what the check does, what it should do, the
document that shows the difference, and the measurement before and after - then change it, then
re-measure the whole corpus, then say in the report that the instrument changed and what moved. **An
instrument change with no finding and no re-measurement is refused even if the new number is better.**

`regress.py` will not catch this for you. Nothing will. It is the one place where you are trusted.

### "Change ONE construct, not two" against "two attempts is the floor"

**Both are true and they count different things.**

* **One construct per COMMIT.** A commit that changes how rules are emitted *and* how a stamp is anchored
  cannot be measured: if the corpus moves you cannot say which half moved it, and if it regresses you
  cannot say which half regressed it.
* **Two ATTEMPTS per run, minimum.** Both attempts are on the same class and usually the same construct -
  a second idea for the same problem, or the same idea proved on a second document. They are separate
  commits only if each stands on its own measurement.

**So: two or three attempts a run, each attempt its own commit, all of them on the class the rotation gave
you, and one construct per commit.** There is no contradiction, and a run that does one attempt has done
half a run.

---

## NOBODY IS COMING. EVERY DECISION IS YOURS.

The user's instruction, 21 Nov:

> "fixer ko yeh bhi batao ki kisi bhi decision ke liye koi nhi aayega tumhe har ek decision khud Lena
> hoga research, verification, proof and evidence ke basis par"

**There is no person behind this pipeline. No one reads `BLOCKERS.md` and acts on it, no one is waiting to
answer a question, and no run is coming that will know more than you do about the thing you are looking
at.** A run that stops and waits for a decision has not paused the work - it has ended it, because the
next run starts from the same question with less context.

### So you decide. All of it.

Every one of these is yours, and none of them needs anyone's permission:

* which document to prove a construct on
* whether a class can be won, and when to park it
* whether a check is wrong or whether the engine is wrong
* whether a fix is worth its blast radius
* whether a finding is good enough to stop on
* whether two rules in this file contradict each other, and which one is right
* whether a number in a report is real
* whether to change a tool, a table, a brief, or the engine
* what to do when the gate refuses, and what to do when it passes
* what the next run should work on

### On what basis

**Research, verification, proof and evidence. In that order.**

1. **Research first.** `grep` the repository before you build anything. Weeks of measured work sit in
   `FINDINGS/`, `LESSONS.md`, `PLAN-DECISIONS.md`, `SETTLED.md`, `HYPOTHESES.md` and the git log. Most
   questions have already been answered and the answer is written down.
2. **Verify.** A claim you have not measured is an opinion. The three Drive calls that show you what
   Google does with a construct cost less than the hour you would spend guessing.
3. **Prove.** Write the number before and after. A change with no measurement is a guess with a commit.
4. **Evidence, and say which.** "It seemed right" is not evidence. "FINDINGS/x says 55.15 asked and 0.33
   rendered, and I reproduced it on document y" is.

**When the evidence does not settle it, take the decision that is reversible and say what would settle
it.** A run that guesses and records the guess is worth more than a run that waits, because the next run
can overturn a recorded guess and cannot overturn silence.

### The one thing that is not a decision: "a person has to decide"

`BLOCKERS.md` carries fifteen rows that end in *"a person has to look"* or *"a person has to decide two
things"*. **That is not a blocker, it is a run that stopped working.** Every one of those rows describes a
technical question with a technical answer, and the answer was available the whole time.

**Write it as a decision, with the evidence, and act on it:**

    DECIDED 21 Nov: the .txt thresholds are normalised to share-of-applicable-checks, not raw counts,
    because t02 and t08 were firing on documents that failed nothing else (CAUSES-TXT.json, 213 rows).
    Re-measured the corpus; 3 documents changed class. Reversible: revert this commit.

**The only thing that is genuinely outside the repository** is a permission or a tool that does not exist:
a Drive authorisation the account owner has not given, an integration that is not connected, a binary that
cannot be installed. For those, **state the exact call, the exact error, and what it blocks** - and then
work on the next thing. Do not sit on it and do not dress it up as a decision.

### And record it so the next run can disagree

**Every decision goes into `BLOCKERS.md` or a `FINDINGS/` file with its evidence and what would overturn
it.** Not for a person - for the next run, which is the only reader you will ever have. A decision with no
record is a decision the next run will make again, differently, and one of the two will be wasted.

**You are the last line. There is no one above you to escalate to.**

---

## BEFORE YOU DO ANYTHING ELSE, LOOK AT WHAT THE LAST RUN DID. INCLUDING WHETHER IT DID ANYTHING.

The user, 21 Nov: *"kya fixer cron khud ko correct nhi kar sakta hai yaar uske paas poora access hai...
isko khud hee khud ko dekhna hoga ki wo kaam kar raha hai ya nhi"*

**You can. Nobody told you to.**

### The first thing you run, before the class, before the engine, before anything

    python3 tools/p2w-bench/gaps.py            # every silence over 5 minutes, per run, with what it was doing
    python3 tools/p2w-bench/status.py          # is the slot clean, or did the last run die holding it
    python3 tools/p2w-bench/health.py          # the pipeline's own verdict

**Read what they say about the run before yours.** If a run shows a gap longer than the slot, or a run
that claimed and then recorded nothing, **that is a finding, and it is yours to act on**:

* a **stale claim** - `round.py --release-fixer --force`, then say in the report that you cleared it
* a **run with no beacon at all** - it never got past the clone. Write it into `BLOCKERS.md`; the next
  run needs to know the failure is above the repository
* **a fire that never happened** - `TIMELINE.jsonl` has a hole wider than the schedule. That is a missed
  slot, and no run can recover it; record it so the gap is visible instead of silent

### The one thing you cannot see, and why

**A run that never starts cannot check anything.** It runs no code, so it leaves no evidence and cannot
report its own death. **And no cron in this pipeline has the `cron` tool** - `BLOCKERS.md` row 2026-11-17
11:40 says so - so a live run cannot list its own runs, cannot see a sibling stuck at `status: running`,
and cannot trigger, pause or resume itself.

**That is not a gap in your access. It is what being a process means.** The only thing that can act on a
dead process is something outside it.

**What you CAN do, and what this section is for: leave enough evidence that the next run knows exactly
what happened and where.** A run that writes a beacon before it starts reading, and a gap in the timeline
when it dies, is a run whose death is diagnosable. A run that writes nothing is a two-hour hole nobody can
explain - and that is what 21 Nov cost: a run from 07:57 that left no claim, no beacon and no commit, was
still marked `running` at 09:54, and silently swallowed the 09:50 fire.

### So beacon early, and beacon often

    python3 tools/p2w-bench/round.py --heartbeat --doing "cloned, reading the brief"

**The clone is the first thing that can hang, and you cannot beacon before it because the tool lives in the
repository you are cloning.** So the moment the clone returns: beacon, before you read anything. Then
beacon before every step that can take minutes - a corpus pass, a build, a Drive round-trip, a sub-agent
wait. The gaps those beacons leave are the only map anyone will have of your run.

### And check yourself while you are running

If you are about to do something that will take more than a few minutes, ask: **if this hangs, will the
next run be able to tell what I was doing?** If the answer is no, beacon first. That is the whole of
self-monitoring that is in your power, and it is worth more than any status line, because it is the only
evidence that survives you.

---

## AND THE ONE THING THAT MADE THIS PIPELINE A FOLLOWER: IT STOPPED WHEN THE PROCEDURE ENDED, NOT WHEN THE WORK DID

The user, 21 Nov: *"yehi sab fixer cron kyun nhi decide karta hai sala sirf chalata hai aur rukta hai
chahe kuch kaam ho ya na ho"*

**That is a fair description of what this brief produced, and the fault is in the brief, not in the run.**

A run read its steps, did them in order, recorded two attempts, wrote an honest report and stopped - even
when nothing had improved, even when the class it was given was a fifth of a bigger one, even when the
three checks it was chasing were one construct that five checks shared. It followed the procedure
perfectly and moved one document. **Every gate passed. The report was accurate. Nothing was wrong except
that no document got closer to 99%.**

### So the run does not end when the steps end. It ends when the work does.

**Before you stop, answer this in one line: what moved?** If the answer is "nothing", you are not finished -
you have used your attempts on the wrong thing, and the evidence to find the right thing is one command
away:

    python3 tools/p2w-bench/classpick.py --leverage

**If two attempts on a class moved nothing, do not report and stop. Change the class, or change the
construct, and spend the rest of the slot on the thing the arithmetic says is worth the most.** The user's
instruction is explicit: *"fixer kisi kisi run me ek bhi documents fix nhi karta aur ek hee attempt karta
hai kuch aisa karo jisse yeh apni poori timings tak poori takat se kaam karta rahe"*.

**Three things are not a reason to stop:**

* **the procedure is finished** - it is a floor, not a ceiling
* **the attempts are used** - "two attempts is the floor" means at least two, not at most two
* **the report is due** - a report of nothing is worse than a report written at the end of a slot that
  spent its last twenty minutes on the class with the highest clean leverage

**A run that ends with 0 documents improved must say, in the report, what it learned about WHY and what
the next run should do instead.** A bare "0 improved" with no next move is the failure mode the user is
describing, and it is the one thing in this brief that costs more than any wrong fix.

---

# THE RUN'S OWN VERDICT. ANSWER THIS BEFORE YOU RELEASE THE SLOT.

The charter says the goal is documents at 99% in Google. **So the only question a run has to answer about
itself is whether the number that measures that goal moved.**

    python3 tools/p2w-bench/report.py | head -20      # the clean count, before and after

**One of three answers, and the run must know which one it is:**

* **The clean count went up.** Name the documents that became clean and the construct that did it. That is
  the whole deliverable, and it is worth more than any number of attempts recorded.
* **A document improved but none became clean.** Say which construct you moved and how far each document
  now is - "three of these four are one check from clean" is a real result and tells the next run exactly
  where to aim.
* **Nothing moved.** Then the run has not finished; it has failed to find the cause, and the honest output
  is what you ruled out. **A run that ends here must leave the next one a shorter list**, not the same one:
  which approaches are now proved wrong, and what you would try if you had another hour.

**A run that reports "0 improved" with no shorter list for the next run has produced nothing, however
accurate its tables.** That is the failure the user described - "sirf chalata hai aur rukta hai" - and it is
the one thing this file cannot check for you.

## And then leave the place better than you found it

Not a tidy desk - a shorter path. One of these, every run, whichever is true:

* a finding in `FINDINGS/` the next run would otherwise have to rediscover
* a tool that removes a guess someone was making by hand
* a check that was lying, fixed and re-measured
* a class that is genuinely unwinnable, parked with the proof, so no run spends a slot on it again
* one document closer to 99%, named

**If none of those is true of your run, the run did not happen.**

---

# A LEAD IS NOT A FAILURE. RECORD IT AS ONE AND THE ROTATION WILL NOT WALK AWAY.

The user, 21 Nov: *"kya rotation ki wajah se kisi ek cheez par kaam karna iske liye muskil hai... koi
improvement nhi hua toh dusra class lekin jo lead mila hai usko chodna padta hoga"*

**They had found a real hole.** The rotation's verdict was `sum(moved)`, so a run that measured a construct
through Google and ran out of slot to implement it read as **zero progress** - and the rotation started
counting towards leaving the class.

That is exactly what happened at 19:10 on 21 Nov. A run measured `w:tblpPr`: a floating table renders its
rule at y=399.5 for 400 asked and costs **0.00 pt of flow**, which unblocks `32_stroke_lines` - 145
documents, 36.3 clean, the largest prize in the tool. The implementation did not land, the run recorded it
as `reverted`, and the rotation saw 0 moved.

**`reverted` means the idea was refuted. That idea was not refuted - it was proved.** The run had done the
hard part and labelled it a failure.

### So there are five outcomes, and the middle one matters most

| outcome | means | rotation |
|---|---|---|
| `kept` | landed, measured, documents moved | stays |
| `partial` | moved some, not finished | stays |
| **`lead`** | **a construct was measured and is ready to emit; nothing landed yet** | **stays, and nothing else starts** |
| `reverted` | tried and refuted by measurement | counts towards rotating |
| `error` | could not be attempted | counts towards rotating |

    python3 tools/p2w-bench/attempt.py --class "<class>" --outcome lead \
        --reason "w:tblpPr measured: rule at y=399.5 for 400 asked, 0.00 pt flow. Emit a floating table
                  per rule. Not implemented yet - the build is the next run's first job."

**A class holding an open lead is not rotated away from, whatever its document count says.** Finish it or
refute it. A measured lead is worth more than a fresh attempt on any other class, because the measuring is
the expensive part and it is already done.

### And the honest corollary

**If you cannot land a lead in your slot, you must still record it** - the finding, the exact construct, and
what is left to do. A lead that dies with your sandbox is the same as no lead at all, and the next run pays
for the measurement again.

**Three attempts died on "the patch is ready and there is no time to build and measure it" in one run on 21
Nov.** That is a run that measured three things and landed none. The build is not the afterthought; on a
slot with a lead in hand, **the build is the slot.**
