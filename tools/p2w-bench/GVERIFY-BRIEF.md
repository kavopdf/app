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

