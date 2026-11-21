# How the five crons divide the work, and why the model is flowing text

## The decision: a .docx is flowing text

Settled 19 Nov. A Word document is a flow of paragraphs that a reader lays out. It is not a canvas of
absolutely-positioned boxes, and the engine has been writing it as one - zero page margins, every line
placed by an absolute indent, every rule a floating drawing at an absolute y.

That works in LibreOffice because LibreOffice honours every one of those constructs. Google Docs, which
is what the users open, honours almost none of them, and four measured attempts to patch the constructs
one at a time all made the score worse:

    rules as w:pBdr                        40/42 -> 40/42   construct right, placement wrong
    w:pgMar + indents                      40/42 -> 32/42   worse
    w:pgMar + indents + spacing + offsets  40/42 -> 34/42   worse
    font metrics                           40/42 -> worse

So the model is flowing text, which is also what Acrobat Pro and iLovePDF produce: paragraphs with
styles, tables with cell borders, rules as paragraph borders, positions carried by indents and spacing
rather than by absolute offsets. The measured capability table is in
`benchmarks/GOOGLE-VS-LIBREOFFICE.md`.

**The engine is NOT rewritten.** Rewriting a converter that already produces 42/42 in one renderer, to
chase another, loses everything that works and cannot be verified in one step. The model is changed
one construct at a time, each with a measurement before and after, and each document that improves is
worth keeping whether or not the next one does.

## The five crons, in order, and what each may touch

    :20  gverify    measure 20 documents through Google.        engine: NO   results: YES
    :00  baseline   measure the whole corpus through soffice.   engine: NO   RANKING: YES
    :40  classifier group the failures into classes.            engine: NO   classes: YES
    :50  fixer      change ONE construct, measure, keep or revert.  engine: YES  nothing else
    22:00 apk       ship once, when every stage is done.        engine: NO   releases: YES

**One cron may change engine code. That is the fixer.** The other four exist so that the fixer never has
to guess what to fix and never has to prove its own work.

## The one file they all read

    python3 tools/p2w-bench/stage.py

It computes the stage from the results on disk - never from a label, never from a list written down:

    measure-google   Google has a result for fewer than all documents
    classify         results exist and the class table is older than them
    fix              classes exist and some document still fails a check
    ship             every document passes all 42

`--set <stage>` refuses when the evidence disagrees. A run cannot advance the pipeline by asserting it
has; it advances by leaving results behind.

**Every cron starts with `stage.py` and does only what its stage says.** If a run finds the stage is not
its own, it says so in one line and stops. That is not a wasted slot - it is the coordination working.

## What a fixer run does, in order, every time

**`round.py` decides the turn, not `stage.py`.** `stage.py` belongs to the gverify cron and tracks a
different question - which measurement is behind. While the Google measurement is incomplete the two
disagree by design, and that is not a blocker.

1. `round.py --phase` - is it `fix`? If not, say so and stop. **Not `stage.py`.**
2. `round.py --claim-fixer` - take the slot, or stop if another run holds it.
3. `classpick.py` - it prints the class and the reason. **That is the class.** It ranks by how many
   documents each one costs in GOOGLE and rotates; it is not the same thing as "whichever check
   `gverify.py --report` lists first", which is why this line used to say that and was wrong.
4. **Read `FINDINGS/` first.** Everything already measured is in there. Re-deriving one of them is the
   most expensive thing a run can do.
5. Change ONE construct. Not a refactor, not a rewrite, not two constructs because they look related.

## What is settled - and what re-opens it

These were measured, not argued. They stay unless a measurement contradicts them.

* **The renderer is Google Docs.** LibreOffice is a fast local proxy that hides the faults the phone
  shows. Measured 21 Nov on the full corpus: LibreOffice passes 122 of 213, Google passes 7 of the 192
  it can score. (This line said "23 and 7 on the same 50 documents" until 21 Nov - true when it was
  written, stale by then. **The numbers in a settled decision age like everything else.**)
* **The model is flowing text.**
* **No engine rewrite.** One construct, one measurement, one commit.
* **Nothing changes without a measurement before and after.**
* **`share@5px` is not a cross-renderer measure.** Use the 42 checks.
* **A refused document is not a pass.**

**"Settled" means settled until the evidence changes, not settled for ever.** If a measurement
contradicts one of these, that is not re-litigating - that is the pipeline learning. Write the
contradiction into `BLOCKERS.md` with the measurement, act on the measurement, and say in the report that
a settled decision moved and why. **What is not allowed is re-arguing one of these from opinion.**

## When something is blocked

Not every wall is a code problem, and almost none of them needs a person. **Decide, record, continue.**

A run that stops to wait has ended the work: the next run starts from the same question with less
context. So take the reversible decision on the evidence you have, write it into `BLOCKERS.md` with that
evidence and what would overturn it, and carry on with the next thing. The only wall that genuinely
stops a run is a permission or a tool that does not exist - and even then, state the exact call and the
exact error, then work on something else this slot.
---

## STARTING A RUN WHEN THE LAST ONE DIED

A run that dies mid-way leaves the live state files modified and uncommitted. The next run's
`git pull --rebase` then refuses with `error: please commit or stash them`, and that run stops before it
has done anything. **This is the most common way a run does nothing, and it looks like a permissions
problem.**

The state files are:

    tools/p2w-bench/{HANDOFF.json,HANDOFF.md,LAST-MESSAGE.md,REPORT.md,ROUND.json,
                     RUN-HISTORY.json,RUN-LOG.md,RUN.json,TIMELINE.jsonl,TRACE.md}

They are written by whichever run is live. A dirty one means a run died, not that there is work to
preserve - the last **committed** copy is the real handoff.

**Every run starts with this, before anything else:**

    cd <your clone>
    git checkout -- tools/p2w-bench/   # discard a dead run's half-written state
    git pull --rebase origin main

`git checkout --` on that directory discards only uncommitted state. It never touches committed work,
never touches `app/`, and never touches the tools or briefs. **Never use `git reset --hard`** - that
discards everything, and it wiped seventeen files once.

If the checkout itself fails because a file is unreadable, `git clean -fd tools/p2w-bench/` after it.

**Then** claim your slot and work. A run that starts by resetting state is a run that can always start.
