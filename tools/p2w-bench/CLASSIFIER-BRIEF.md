# The classifier - you SORT the measurements, nothing more

You are step 2 of 3. You do not fix and you do not measure. You group and rank what the baseline
already measured.

    git clone https://github.com/kavopdf/app /scratch/work/cls
    cd /scratch/work/cls
    python3 tools/p2w-bench/round.py --phase

If the phase is not `classify`, output exactly `not my turn - phase is <PHASE>` and STOP. Do not
read anything else.

    python3 tools/p2w-bench/round.py --claim-classifier

Exit 1 means a previous run still holds the slot. Output exactly `previous classifier run still
active` and STOP. Exit 0 means the slot is yours.

## 1. The classification is already in the data. Do not invent one.

The instrument writes `signature` and `problem` for every document. They are derived mechanically -
`signature` from the SHAPE of the tolerance sweep, `problem` from loss against invention against
distance. Neither is an opinion and neither is yours to overrule. Your job is to GROUP and RANK
them.

    signature: flat curve -> content-loss (ink ABSENT); falling -> displacement (ink MOVED);
               both high -> mixed; share@5px below 1% -> clean
    problem  : content-missing-nothing-in-its-place, content-missing-partly-replaced,
               content-partly-lost, content-partly-lost-and-displaced,
               content-present-wholly-displaced, content-present-partly-displaced,
               single-element-far-out, none, unmeasured

The exact thresholds for each name are in `benchmarks/PROBLEM-NAMES.md`.

    python3 - <<'PY'
import csv, collections
rows=list(csv.DictReader(open('benchmarks/RANKING.csv')))
sc=[r for r in rows if (r.get('share5') or '').strip().replace('.','').isdigit()]
print('scored', len(sc), 'of', len(rows))
for p,n in collections.Counter(r['problem'] for r in sc).most_common():
    print(f"  {p:42s} {n}")
PY

## 2. Rank by damage, not by count

  1. content-missing-nothing-in-its-place   content GONE, nothing in its place (worst)
  2. content-missing-partly-replaced        gone, something else in its place
  3. content-partly-lost-and-displaced      two defects on one page
  4. content-partly-lost                    some gone, rest displaced
  5. content-present-wholly-displaced       everything there, all of it moved
  6. content-present-partly-displaced       most right, part moved
  7. single-element-far-out                 one small thing (a stamp, a seal) far away

Do not rank by `max_pt` - one outlier pixel dominated it (134 pt on a document whose pages looked
nearly identical). Rank by share@5px, and put the class with the MOST DOCUMENTS first, because one
mechanism fixed once clears every document under it.

## 3. Write benchmarks/DEFECT-CLASSES.md. Exactly one table. This is enforced.

**On 16 Nov the file this step produced had 3 different table shapes (92 rows with 11 pipes, 122
with 9, one with 7) and listed the two bank forms TWICE. round.py counts every row that says OPEN,
so it reported 94 classes when there were 92 defective documents - the round-close gate was
counting two phantoms, and a fixer reading the file saw the same document in two tables with
different column meanings.**

`classify_gate.py` now refuses a file that has duplicates, more than one table shape, a missing
document, or an extra one. So write it right the first time:

    # Defect classes - round <N>

    Documents measured: **N of M**

    | signature | problem | documents |
    |---|---|---|
    | content-loss | content-missing-nothing-in-its-place | 30 |
    | ... one row per problem name ... |

    ## Documents

    | # | document | problem | share5 | max_pt | worst_page | status | note |
    |---|---|---|---|---|---|---|---|
    | 1 | `415_inline_images` | content-missing-nothing-in-its-place | 89.04 | 153.12 | 1 | OPEN | - |
    | ... one row per document ... |

Rules the gate checks mechanically:

  * `N` = number of documents in `RANKING.csv` with a real share5. `M` = the total number of ROWS
    in `RANKING.csv` - not the same number, because an exempted document is a row with no score.
    Count both from the CSV; do not assume they are equal.
  * **ONE table of documents.** Same number of columns in every row. No per-class tables.
  * **Every scored document appears EXACTLY ONCE.** No duplicates, no omissions.
  * **A document that was not scored must be PARKED with the reason, never OPEN.**
    `416_many_tiny_pages` is exempted in `tools/p2w-bench/EXEMPT.json` - write it PARKED and say
    why, or the round waits for a measurement that will never exist.
  * Status is exactly `OPEN`, `FIXED` or `PARKED`. Any other word is invisible to round.py.
  * `none` documents are `FIXED` (there is nothing to do), not OPEN.

**`git push` works as of 19 Nov.** Set the identity first
(`git config user.email "320240581+Onyx-Node@users.noreply.github.com"`, `user.name "Onyx-Node"`),
run `bash tools/install-gate.sh` once per clone, then commit with git. A commit authored as a
private address is refused with "push declined due to email privacy restrictions", and a commit
whose change has not been measured across the whole corpus is refused by the gate - neither is a
permissions problem. The MCP tool below still works as a fallback.

Commit these files with git (fallback: GITHUB_COMMIT_MULTIPLE_FILES, owner kavopdf, repo app, branch main): Commit only if it
changed.

## 4. Advance the phase. Nothing else can, and nothing used to.

    python3 tools/p2w-bench/round.py --advance

This is not optional. On 16 Nov an audit found that **no cron in the pipeline called --advance at
all**: the phase machine, the gates and the round logic were all correct and unreachable, so the
pipeline sat in `classify` with every cron reporting success. You are the only thing that moves
classify to fix, and until you do, the fixer refuses to work.

`--advance` runs `classify_gate.py` first. If it refuses it prints why - fix that reason and try
again once. If it still refuses, report the reason and STOP. Do not work around it and do not
hand-edit the gate.

Never edit engine code. Never edit `benchmarks/RANKING.csv` - that is the baseline's output and the
only record of what was measured. Never run `classify.py`; it is retired.

If a rate limit or technical error hits, wait and retry up to three times, then report it.

## 5. The report

    **18 partly-displaced - 13 partly-replaced - 12 wholly-displaced - 149 clean - 64 OPEN -> advanced to fix**
    | class | docs | worst | damage |
    |---|---|---|---|
    | content-present-partly-displaced | 18 | (from RANKING.csv) | high |
    | content-missing-partly-replaced | 13 | (from RANKING.csv) | highest |
    | content-present-wholly-displaced | 12 | (from RANKING.csv) | high |
    | clean | 149 | - | none |

**THE SHAPE IS THE INSTRUCTION; THE NUMBERS ARE NOT.** This table read "30 / 16 / 15 / 120 / 94" and
every figure had moved: the justified-lines fix took the open count from 94 to 64 and the clean
count from 120 to 149. Build the table from `benchmarks/RANKING.csv` and `DEFECT-CLASSES.md` every
run - a brief that prints last week's census teaches the run to copy it, and a copied census is a
report nobody can trust.
    | Phase after this run | fix |

Every number must come from `RANKING.csv` of THIS run. The figures above are the state on 16 Nov
and are there so you can tell a real change from a broken run - not so you can copy them. Never
estimate a number.

## Dead files - do not read them, do not commit them

    BASELINE.md   RESULTS.jsonl   RESULTS-TXT.jsonl   RATCHET.json   RATCHET-TXT.json

These belong to the pipeline that preceded this one. The current measurement is
`benchmarks/RANKING.csv`; the current class file is `benchmarks/DEFECT-CLASSES.md`.

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

---

## YOUR REPORT COMES FROM report.py, NOT FROM YOU

**Never type a number. Generate the report and send it.**

    python3 tools/p2w-bench/report.py --for classifier > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --for classifier --file /tmp/report.md

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


---

## BOTH FORMATS GET CLASSES

The corpus has two halves and they fail differently. A class table built only from the `.docx` results
tells the fixer nothing about the 47 documents whose `.txt` fails a check, and those documents stay
failing for as long as the table ignores them.

    python3 tools/p2w-bench/health.py                    # both halves, one view
    python3 tools/p2w-bench/txt/RANKING-TXT.csv          # per-document .txt checks
    python3 tools/p2w-bench/txt/DEFECT-CLASSES-TXT.md    # the .txt classes

`DEFECT-CLASSES.md` carries the `.docx` classes; the `.txt` classes live beside it in
`txt/DEFECT-CLASSES-TXT.md`. **Both are regenerated every run.** A run that updates one and not the
other has classified half the corpus and reported it as the corpus.

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

## THE CLASSES ARE LIBREOFFICE'S. GOOGLE'S ARE BIGGER AND INVISIBLE.

`benchmarks/DEFECT-CLASSES.md` says in its own header: *"Grouped and ranked from
`benchmarks/RANKING.csv` only"*. RANKING.csv is a soffice render. So every class the fixer is offered
describes a renderer no user opens, and the checks that actually fail in Google appear in no class at
all. Measured 19 Nov on 84 documents with both renders:

    32_stroke_lines   LibreOffice  0    Google 53      <- no class mentions it
    05_chars_extra    LibreOffice  6    Google 54      <- no class mentions it
    18_displacement   LibreOffice  4    Google 46      <- no class mentions it

LibreOffice fails `32_stroke_lines` on **zero** documents. Google fails it on 53. A classifier reading
RANKING.csv alone can never produce a class for it, and the fixer can never be sent to fix it.

### Both halves, every run

    benchmarks/DEFECT-CLASSES.md        the .docx classes, from RANKING.csv          (as now)
    tools/p2w-bench/txt/DEFECT-CLASSES-TXT.md   the .txt classes                     (as now)
    benchmarks/DEFECT-CLASSES-GOOGLE.md  NEW - from benchmarks/gverify/ and gverify-lo/

The third file groups the **42 checks** through both renderers and ranks by the gap:

    python3 tools/p2w-bench/gverify.py --matrix

Its "Where they disagree" table is already the ranking - `google fails` minus `libreoffice fails`, the
checks that are Google's alone. Turn each into a class with the documents that fail it and the
construct it names:

    | signature | problem | google | libreoffice | documents |
    |---|---|---:|---:|---|
    | rules-as-drawings | 32_stroke_lines + 05_chars_extra | 53 | 0 | <names> |

**A class where LibreOffice fails zero and Google fails fifty is the highest-value class in the
repository**, because it is invisible to every other measurement and it is the reason the users see a
broken document while the gate says it passes.

`FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` already names the construct for the first of them.
Read it before writing the class so the fixer is not sent to rediscover it.

---

## YOUR REPORT IS GENERATED. YOU DO NOT WRITE IT.

The fixer's report has always come out of `report.py`. Yours now comes out of `cronreport.py`, from the
same files the verifier reads, so the numbers and the shape are both fixed before a run touches them.

    python3 tools/p2w-bench/cronreport.py --for classifier > /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --file /tmp/report.md --for classifier

Then add **one short paragraph, in your own words, under the pull-quote**, saying what THIS run did -
"nothing needed moving", "measured twenty, committed them", "shipped v3.53.27". No numbers in that
paragraph; the tables already carry them, and a number you type is a number you can get wrong.

Post `/tmp/report.md` as your final message. Exit 3 from lastmessage.py means a number in the message
is not one the tool printed - re-run the generator, do not edit the numbers.

**Never write the report by hand, and never paste this prompt into it.** The verifier refuses a message
that contains its own instructions; that is what turned the 20 Nov gverify report into two pages of dark
slab with the real report starting at the bottom of page three.
