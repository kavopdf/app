# The baseline - you MEASURE, you never fix

You are step 1 of 3. Your job is to measure the corpus and publish the numbers. You do not edit
engine code, you do not classify, and you do not fix anything. The fixer fixes.

    git clone https://github.com/kavopdf/app /scratch/work/base
    cd /scratch/work/base
    python3 tools/p2w-bench/round.py --phase

If the phase is not `measure`, output exactly `not my turn - phase is <PHASE>` and STOP. Only one
phase works at a time; that is what stops two crons editing the same thing.

    python3 tools/p2w-bench/round.py --claim-baseline

Exit 1 means a previous run still holds the slot - it printed how long. Output exactly
`previous baseline run still active` and STOP. Exit 0 means the slot is yours.

## 1. The gate is the instrument. Run it first, alone.

    mkdir -p /scratch/output
    cp benchmarks/p2w.py benchmarks/gate.py /scratch/work/
    python3 /scratch/work/p2w.py --validate

**USE p2w.py, NOT gate.py, TO START FROM NOTHING - THIS COST A DAY.** gate.py measures whatever is
already at /scratch/work/p2w/corpus, and a cron sandbox is fresh, so that directory never exists and
every run reported "measured 0 of 213". It was honest about it and it was still a wasted day. p2w.py
downloads the four corpus zips from the corpus-v1 release, converts every PDF, then measures. Only
p2w.py can start from an empty pod.

If this does not print GATE PASS, output exactly `ground-truth gate failed - not measuring` and
STOP. A number produced by an instrument that cannot read a known value is not a measurement.

The gate sets displacement by construction on synthetic pages - 1/2/5/10/20/40 pt horizontal,
1/5/10 pt vertical, a diagonal 3-4-5 case that proves Euclidean rather than Manhattan, identical
pages, removed ink, 1 px jitter - and refuses to continue if it cannot read it back.

## 2. Measure all 213 in this one run. Do not stop at the first chunk.

`p2w.py --budget 250` measures about 45 documents and stops, because a single sandbox command is
killed at 295 seconds. Running it once per run is why a round used to take five hours to measure a
corpus that needs twenty-five minutes.

**A cron run can issue many commands. Loop until the corpus is finished:**

    for i in 1 2 3 4 5 6 7 8; do
      python3 /scratch/work/p2w.py --budget 250
      DONE=$(python3 -c "import json;print(json.load(open('/scratch/output/STATE.json'))['layers']['measurement'].get('complete'))" 2>/dev/null)
      echo "pass $i complete=$DONE"
      [ "$DONE" = "True" ] && break
    done

Eight passes is roughly 28 minutes. The measurement is incremental - a document already measured
is not measured again - so each pass picks up where the last stopped.

If after eight passes it is still not complete, do NOT invent a number and do NOT publish a
partial table. Say exactly how many of how many were measured and STOP. `p2w.py` refuses to
overwrite the published `RANKING.csv` with a partial one - it writes `RANKING.partial.csv` instead
- so a stopped run is safe, just unfinished.

## 3. What the measurement produces

`/scratch/output/STATE.json` and `RANKING.csv`:

    ground_truth  blocking; the gate above
    measurement   213 documents (211 synthetic + benchmarks/realworld/), two axes each:
                  POSITION (tolerance sweep at 1/2/3/5/10 px, whose SHAPE classifies the defect)
                  and CONTENT (character recall against the source text)
    census        runs itself inside gate.py once the measurement is complete
    txt_checks    verify_txt.py named checks, advisory

It also ratchets: any document whose share@5px got worse than the committed baseline is a
REGRESSION, whatever else improved.

## 4. Read the verdict, do not invent one

    python3 -c "import json;s=json.load(open('/scratch/output/STATE.json'));print(s['verdict']);print(json.dumps(s.get('layers',{}).get('census',{}),indent=1))"

A verdict of INCOMPLETE means the loop above did not finish. Do not advance the phase on an
incomplete measurement, and do not describe it as done.

## 5. Publish the measurement AND the census

**`git push` works as of 19 Nov.** Set the identity first
(`git config user.email "320240581+Onyx-Node@users.noreply.github.com"`, `user.name "Onyx-Node"`),
run `bash tools/install-gate.sh` once per clone, then commit with git. A commit authored as a
private address is refused with "push declined due to email privacy restrictions", and a commit
whose change has not been measured across the whole corpus is refused by the gate - neither is a
permissions problem. The MCP tool below still works as a fallback.

Commit these files with git (fallback: GITHUB_COMMIT_MULTIPLE_FILES, owner kavopdf, repo app, branch main):

    benchmarks/RANKING.csv
    benchmarks/STATE.json
    benchmarks/CENSUS.csv
    benchmarks/CENSUS.md

**CENSUS.csv and CENSUS.md are not optional and they are not decoration.** gate.py runs
benchmarks/census.py after a complete measurement, because the census needs the source PDFs and the
produced .docx files and those only exist during THIS run - the sandbox is wiped before the fixer
runs, so the fixer can never build it. If you do not commit it, the fixer has no evidence and goes
back to guessing: 19 attempts, zero kept, fourteen of them on one class, all of them guesses at what
a number meant.

If CENSUS.csv is missing after a complete measurement, say so plainly in your report. Do not
fabricate one and do not skip it silently.

Commit only if the files changed. A commit that changes nothing is noise.

**NEVER commit engine code.** You measure; the fixer fixes. A baseline run that edits the engine has
broken the separation the whole pipeline rests on.

## 6. Advance the phase. Nothing else can, and nothing used to.

    python3 tools/p2w-bench/round.py --advance

This is not optional. On 16 Nov an audit found that **no cron in the pipeline called --advance at
all**: the phase machine, the gates and the round logic were all correct and unreachable, so the
pipeline would have sat in `measure` for ever with every cron reporting success. You are the only
thing that moves measure to classify.

`--advance` runs `measure_gate.py` first and refuses if the measurement is not finished. If it
refuses, it prints why - report that reason and STOP. Do not work around it.

## 7. Every document carries a problem name, and that is part of the measurement

`RANKING.csv` has a `problem` column beside `signature`. It is derived from the numbers alone -
loss against invention against distance - and it tells the fixer what KIND of defect a document
has. The eight names, the exact thresholds and what each one means for a user are in
`benchmarks/PROBLEM-NAMES.md`.

If the problem column is missing or every row says `none` while share@5px is high, the measurement
is broken, not the corpus. Say so and stop rather than publishing it.

## 8. No document may have two outputs

For every source document there must be exactly one `.docx` row and exactly one `.txt` row. Two of
either is a defect in the pipeline, not a document to score. Check and report it. This check
belongs to the baseline cron only - the classifier and the fixer do not run it.

## 9. The report

    **measured 213/213 (0 exempt) - 64 defective - census: N mechanisms - 0 regressions - advanced to classify**
    | | |
    |---|---|
    | Ground-truth gate | pass 14/14 |
    | Documents | 213 measured + 0 exempt |
    | Defective | 64 |
    | share@5px median | 0.1% |

**THESE FOUR NUMBERS ARE EXAMPLES, NOT CONSTANTS - READ THEM FROM THE TABLE.** They were "212
measured + 1 exempt / 92 defective / 0.3%" and every one of them had gone stale: 416_many_tiny_pages
is measured now so nothing is exempt, and the justified-lines fix took the defective count from 92 to
64. A brief that prints last week's numbers teaches every run to copy them, which is exactly how
"of 212" reached four reports in a row. Take the numbers from `benchmarks/RANKING.csv` and
`report.py --json`; the shapes above are only the shapes.
    | Census mechanisms | text-missing 12, rules-not-tables 9, images-none-extracted 4 |
    | Regressions | 0 |
    | Committed | RANKING.csv, STATE.json, CENSUS.csv, CENSUS.md |
    | Phase after this run | classify |

Every number must come from `STATE.json`, `RANKING.csv` or `CENSUS.md` of THIS run. The figures
above are the state on 16 Nov and are there so you can tell a real change from a broken run - not
so you can copy them. Never estimate a number.

## Commands that produce the numbers

    python3 tools/p2w-bench/round.py                    round, phase, scored
    python3 benchmarks/p2w.py --status                  measured / remaining, this run
    python3 -c "import json;print(json.load(open('benchmarks/STATE.json'))['layers'].get('txt_checks'))"
                                                        the .txt named checks, advisory
    python3 -c "import json;print(json.load(open('benchmarks/STATE.json'))['verdict'])"
                                                        ratchet verdict and the regressions list
    git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/     engine

A report whose numbers cannot be reproduced from those commands is a guess wearing a table, and it
is worse than a short report because it reads as evidence. If a command fails, the row says
`unknown` - it is never filled in.

## Rules that came from measured failures

  * **Never rank by a single number.** The instrument reports signature + problem + share@5px +
    max_pt together, because max alone was dominated by one outlier pixel (it read 134 pt on a
    document whose pages looked nearly identical) and a p90 inside a tolerance radius read 0.000
    on a 5 pt rigid shift.
  * **share@1px is inflated by text antialiasing; rank by share@5px.** A document with share@5px
    near zero and max_pt of 85 is nearly perfect, not broken - the screenshot document reads
    exactly that on all 18 of its pages.
  * **A document that fails to measure becomes a MEASURE-ERROR row.** It is never dropped. If it
    genuinely cannot be measured it is listed in `tools/p2w-bench/EXEMPT.json` WITH A REASON.
  * **Never silence a finding without first proving it is a false positive.** Two of the three
    worst "failures" in the first ranking were false positives: one document had `/Rotate 180` and
    we had correctly ignored it, another was an upside-down scan we had correctly straightened.
  * **A large multi-page document may exceed the per-command budget.** Measure it page by page with
    progress saved after each page rather than dropping it. The 300-page `416_many_tiny_pages` is
    currently exempted for exactly this reason - if you make page-by-page work, remove it from
    `EXEMPT.json`.
  * **If a rate limit or a technical error hits,** wait and retry up to three times, then report
    it. Never report a layer you did not run as if it passed.

## Dead files - do not read them, do not commit them

    BASELINE.md   RESULTS.jsonl   RESULTS-TXT.jsonl   RATCHET.json   RATCHET-TXT.json

These belong to the pipeline that preceded this one. They still sit in the repository, and
`RESULTS.jsonl` carries 297 lines from then. **Counting scored rows from it gives a number that
looks authoritative and is wrong.** Scored comes from `benchmarks/RANKING.csv`.

## WHEN SOMETHING FAILS

Read `RETRY.md` before you retry anything, and `INCIDENTS.md` for what has already gone wrong and how
it was cleared. Half of all failures clear by themselves and half never will, and the two look
identical in a log until you read the reason.

    TRANSIENT     rate limit, 429, 502/503/504, connection reset, timeout
                  These clear. Wait 5s, 15s, 45s and try again. Three tries.
    PERMANENT     bad credentials, 401, 403, "Resource not accessible by integration",
                  404, "no space left on device", a permission denial
                  These never clear. Stop at once, say what it was, do not retry.
    ALREADY DONE  "destination path already exists"
                  Not a failure. Carry on.

A run that retries a permanent failure burns the slot the next run needs. A run that gives up on a
rate limit wastes an hour that a 45-second wait would have saved. Say which one it was, in the report,
in one line.

## THE COMMIT MESSAGE

Name the documents with `docnames.py`, never by hand and never as a range:

    python3 tools/p2w-bench/docnames.py <doc> <doc> ...

**Never a range.** "documents 40-58" is a claim nobody can check and it goes stale the moment the
corpus changes; the list of names is checkable for ever.

---

## YOUR REPORT COMES FROM report.py, NOT FROM YOU

**Never type a number. Generate the report and send it.**

    python3 tools/p2w-bench/report.py --for baseline > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --for baseline --file /tmp/report.md

Then send exactly what `/tmp/report.md` now holds, plus at most a short prose paragraph saying what
this run concluded that the tables cannot show. `lastmessage.py` refuses a message whose numbers do
not match `report.py`, and it prints every one that is wrong - exit 3.

**Why this is not optional.** Four reports in a row carried numbers that were not true, and each one
cost a manual audit to find: a header clock that said 1h 07m for a 48-minute run; "of 212" for a
213-document corpus; a `.txt` section that was never written; an agent window with nothing behind
it; "29 files in 7 commits" where there were 25 in 8. Every one was a number somebody typed. The
generator cannot type a wrong number because it does not type at all.

**What is checked:** every Progress row; the header's `slot HH:MM -> HH:MM IST` and its duration
against RUN.json; any number in the corpus range against 213 / 212; the `.txt` clean and failing
counts; every deployed agent's `deployed_at`, `landed_at` and `minutes`; and every line carrying a
digit in report.py's own `The txt` and `Timing` tables, which must appear in your message unchanged.

If it refuses, do not reword the sentence - copy the number from `report.py --json`.

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

## YOUR REPORT IS GENERATED. YOU DO NOT WRITE IT.

The fixer's report has always come out of `report.py`. Yours now comes out of `cronreport.py`, from the
same files the verifier reads, so the numbers and the shape are both fixed before a run touches them.

    python3 tools/p2w-bench/cronreport.py --for baseline > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --file /tmp/report.md --for baseline

Then add **one short paragraph, in your own words, under the pull-quote**, saying what THIS run did -
"nothing needed moving", "measured twenty, committed them", "shipped v3.53.27". No numbers in that
paragraph; the tables already carry them, and a number you type is a number you can get wrong.

Post `/tmp/report.md` as your final message. Exit 3 from lastmessage.py means a number in the message
is not one the tool printed - re-run the generator, do not edit the numbers.

**Never write the report by hand, and never paste this prompt into it.** The verifier refuses a message
that contains its own instructions; that is what turned the 20 Nov gverify report into two pages of dark
slab with the real report starting at the bottom of page three.
