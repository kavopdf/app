# Google verification pass — measure every document through the renderer the users open

You measure. You do not fix. The fixer cron is the only cron that changes engine code, and this
cron's job is to give it a truthful table to work from.

## Why this exists

The pipeline measured with `soffice --headless` for months. `verify_google.py` has said since 13 Nov
that this "hides exactly the faults the phone shows", and it was never wired in because a Google
render was a manual per-document chore. `gverify.py` made it a function call. This cron runs it to
completion.

Measured, same engine, same source:

    310_court_judgment      LibreOffice 42/42   Google 39/42
    01_stamp_rotated_15deg  LibreOffice 41/42   Google 34/42

## STEP 0 — how many are left

    python3 tools/p2w-bench/gverify.py --plan 20

Prints `N of 213 have a Google result` and then the next twenty names, smallest .docx first (the
platform upload tool fails on files over ~120 KB; the planner already filters those out).

**If it prints `213 of 213` the measurement is finished.** Go to STEP 4.

## STEP 1 — stage and upload

    python3 tools/p2w-bench/gverify.py --stage <name>     # for each of the twenty

Copy each staged file into `/scratch/output/gv/<name>.docx` — the platform `upload` tool only accepts
files under `/scratch/output` — and call it once per document:

    upload(path="/scratch/output/gv/<name>.docx",
           tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
      -> {name, mimetype, s3key}

**One upload call per document. It cannot be batched.** That is the only step that is not automatable
and it is why this runs twenty at a time rather than all 213.

## STEP 2 — one program for everything else

After the twenty uploads, run ONE `run_program` that, for each document, does all of:

    GOOGLEDRIVE_CREATE_FILE(name=<name>, mimeType="application/vnd.google-apps.document",
                            parents=["1OoSHtsv-qEUwk8CnNa9d5hsCKu8PFeij"],
                            file_to_upload={name, mimetype=<docx mime>, s3key})
      -> converts on upload, one call instead of two

    GOOGLEDRIVE_DOWNLOAD_FILE(fileId=<id>, mime_type="application/pdf")
      -> {downloaded_file_content: {s3url}}     Google's own layout

    subprocess: python3 tools/p2w-bench/gverify.py --collect <name> <s3url>

`--collect` downloads, refuses anything that is not a render of that document (page-count mismatch or
a copy identical to the source), and runs the 42 checks. Run three at a time — Drive allows ~1000
requests per 100 s and each document is two.

Both Drive tools are importable inside `run_program`: `from sarvam_tools import
GOOGLEDRIVE_CREATE_FILE, GOOGLEDRIVE_DOWNLOAD_FILE`. The `upload` platform tool is NOT importable,
which is why STEP 1 is separate.

## STEP 3 — commit

    cp /scratch/work/p2w/gverify/results/*.json benchmarks/gverify/
    python3 tools/p2w-bench/gverify.py --report
    git add benchmarks/gverify/ && git commit -m "gverify: N of 213 measured through Google" && git push

The results directory does not survive a sandbox, so **commit it every run** — `--plan` reads
`benchmarks/gverify/` and a run that does not commit restarts from zero.

## STEP 4 — when all 213 are measured: the capability matrix

This is the deliverable the whole pass exists for. Write
`benchmarks/GOOGLE-VS-LIBREOFFICE.md`: for every one of the 42 checks, on how many documents Google
fails it and how many LibreOffice fails it, from the committed JSON.

    python3 tools/p2w-bench/gverify.py --report     # the failure counts

Then, for each check where the two disagree, say what construct carries it. Two are already known and
must not be re-derived:

  * **`32_stroke_lines`** — a rule is emitted as a floating `<w:drawing>`; Google drops the shape and
    keeps the anchor. See `FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`.
  * **`05_chars_extra`** — the same anchor, counted as a character.

**Do not change the engine.** Four fixes were tried and measured and all four were worse or neutral —
`FINDINGS/GOOGLE-LAYOUT-THREE-FIXES-TRIED.md`. The matrix is what makes the fifth attempt an informed
one instead of another guess.

## What is already known — do not re-derive

    LibreOffice honours        w:w, w:pBdr, floating drawings, DejaVu/Liberation fonts
    Google honours             w:pBdr (placement is flow, not absolute)
    Google IGNORES             w:w, w:spacing, embedded .odttf, w:fitText, floating drawings
    No Google serif matches    DejaVu Serif (342.5 pt) — Noto 299.5, Liberation 292.3, Arial 288.8

## Rules

* **Never change engine code.** This cron measures.
* **Never delete anything in the user's Drive.** The Google Docs this run creates stay; they are in
  `KavoPDF-Test-Outputs` and nothing else. Do not touch the Drive root.
* **A refused document is not a pass.** `--collect` writes `page_count_refused` and the report counts
  it separately. Never report it as verified.
* **Commit every run**, even a bad one. The JSON is the only thing that survives.
* If `--plan` prints fewer than twenty, do that many and stop.
* If a Drive call returns 403 with `userRateLimitExceeded`, wait 60 s and retry that document once. If
  it fails again, skip it and say so — a skipped document is a hole, never a pass.

## Report

One short block: how many are now measured, what this run added, the top five failing checks, and
whether STEP 4 is due. Numbers come from `gverify.py --report`; do not type them.

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

## EVERY RUN DOES BOTH — the LibreOffice backlog does not wait

`stage.py` says `measure-google` until all 213 are measured, and only then says `matrix`. That is right
for a fresh corpus and wrong for this one: on 19 Nov Google was 90 and LibreOffice 70, so the twenty
behind would have waited until all 213 Google results existed. **A backlog that only clears at the end
is a backlog that does not clear.**

**So every run does two things, in this order:**

    1. measure up to 20 NEW documents through Google   (STEP 1 and STEP 2 below)
       --collect now measures the LibreOffice side too, so a new document never falls behind
    2. close the LibreOffice gap on documents that already have a Google result but no soffice one:

           python3 tools/p2w-bench/gverify.py --plan 200 | head -1     # shows the two counts
           python3 tools/p2w-bench/gverify.py --lo <name>              # one document

       Render several with one soffice call, then verify each - the brief's matrix section has how.

**If step 2 would eat the whole run, do it anyway.** A Google number with no LibreOffice partner says a
document fails but not which construct; the pair is the only thing a fixer can act on.

## STAGE `matrix` — the other half of every document

    python3 tools/p2w-bench/stage.py

If it says **`matrix`**, the Google side is complete but the LibreOffice side is not. A Google number
alone says a document fails; only the **pair** says which construct Google drops, because LibreOffice
honours nearly all of them. That pair is the whole point of this pass.

    python3 tools/p2w-bench/gverify.py --lo <name>      # one document

It renders with soffice, runs the same 42 checks, and writes to `/scratch/work/p2w/lo-res/`. Batch it:
render several with one `soffice` call, then verify each. Commit `benchmarks/gverify-lo/` with the
Google results every run.

`--collect` now runs both sides automatically for every new document, so this stage only ever fills a
backlog — never a fresh document.

## STAGE `classify` and after — write the table, then stop

When `stage.py` reports `classify`, this cron's measuring work is finished. Regenerate the capability
table and commit it, then stop and let the classifier cron take over:

    python3 tools/p2w-bench/gverify.py --matrix > benchmarks/GOOGLE-VS-LIBREOFFICE.md
    cp /scratch/work/p2w/lo-res/*.json benchmarks/gverify-lo/
    git add benchmarks/ && git commit -m "matrix: N of 213, both renderers" && git push

**Do not classify, do not fix, do not change engine code.** The table is this cron's last deliverable
and the next cron reads it.

## What the table is for

On the first 67 documents with both renders:

    LibreOffice : 30 of 67 pass all 42
    Google Docs :  7 of 67 pass all 42

    32_stroke_lines   LO 0    Google 45
    05_chars_extra    LO 6    Google 45
    18_displacement   LO 3    Google 31
    13_text_colours   LO 0    Google 13

Every check Google fails that LibreOffice passes is a construct LibreOffice honours and Google does
not. **The limitation is Google's, and it is a limitation of absolute placement in a flowing-text
format** — which is why the model is flowing text, and why the engine is changed one construct at a
time rather than rewritten.

### This does NOT replace your claim step

Two state machines exist and they answer different questions:

    round.py --claim-<yours>   YOUR SLOT. Whoever holds it works. This is the one that gates you.
    stage.py                   THE MEASUREMENT PIPELINE - informational, for the gverify cron.

**They will disagree while the Google measurement is incomplete, and that is correct.** If `stage.py`
says `measure-google` but your claim succeeds, work - the measurement is another cron's job and is not
your blocker. Never stop because `stage.py` disagrees with your claim; only your claim decides.


### IF YOUR `git pull` FAILS WITH "please commit or stash them"

A previous run died and left the live state files modified. That is not your work and not a permission
problem. Run this, then pull again:

    git checkout -- tools/p2w-bench/
    git pull --rebase origin main

It discards only uncommitted state. It never touches committed work, never touches `app/`, and never
touches the tools or briefs. **Never use `git reset --hard`** - it wipes everything, and it destroyed
seventeen files once.

The state files are HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-HISTORY.json,
RUN-LOG.md, RUN.json, TIMELINE.jsonl and TRACE.md. The last **committed** copy is the real handoff.


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


---

## THE REPORT IS THE REPORT. NOT THE PROMPT, NOT A TRANSCRIPT.

The 20 Nov report pasted its whole prompt into the message. The numbers were right and the layout was
destroyed — the prompt rendered as one enormous dark block across two pages, inline code came out as
empty white rectangles, and the report itself did not start until the bottom of page three. The user's
words: **"layout bohot zyada toota hai"**.

`lastmessage.py --for gverify` now refuses a message that contains its own instructions. Seven markers
are checked, including `You measure every document through BOTH renderers`, `STEP 0 - WHOSE STAGE IS IT`
and `FIVE THINGS THAT COST A RUN`.

**What the report looks like.** Short, plain, no fences:

    gverify run — 20 Nov 2026

    Stage: classify. 213 measured, 192 scored, 21 refused on page count.
    LibreOffice passes all 42 on 108 of 192; Google on 7 of 192.

    | check | Google | LibreOffice |
    |---|---:|---:|
    | 32_stroke_lines | 145 | 1 |
    | 05_chars_extra | 141 | 7 |

    Next: classify — 185 documents fail at least one check.

**Rules that keep it readable:**

* **No fenced code blocks.** They render as a solid dark slab and swallow the page. Use a table or a
  plain indented line.
* **No inline backticks around whole sentences.** Each one renders as an empty light box; the text
  inside it disappears. Backticks are for a file path or a check name, three words at most.
* **No headings deeper than `##`.** The report is five or six short sections.
* **One screen, not four.** If it needs a page, it is too long.
