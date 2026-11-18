<!-- RETIRED - see tools/p2w-bench/RETIRED.md. This file describes the check-id pipeline, which the live pipeline does not run. Do not read it as current. -->

# INSTRUMENT — the only commands that measure anything

This file is authoritative. The four briefs (`BASELINE-BRIEF.md`, `CLASSIFIER-BRIEF.md`,
`FIXER-BRIEF.md`, `TOOLBOX.md`) were written for the previous pipeline. Their **method** —
how to form a hypothesis, how to be honest about a failure, how to commit, how not to break
a neighbour — is still the instruction set and still applies.

Their **tool names are not.** `record.py`, `classify.py`, `calibrate.py`, `seed.py`,
`verify_google.py` and `ratchet.py` appear hundreds of times across those briefs and none of
them is the score any more. Following one of them produces a number that looks real and
describes nothing.

Where a brief and this file disagree about **which command to run**, this file wins.

---

## The one measurement

    python3 benchmarks/p2w.py --validate          # ground truth, 14/14, must print GATE PASS
    python3 benchmarks/gate.py --budget 250       # measure the corpus, write RANKING.csv + STATE.json

`p2w.py` is the authority for "how far off is this document". It reports two axes per
document and a derived problem name:

    share@5px     what fraction of source ink has no counterpart within 5 px   -> HOW MUCH
    invent5       what fraction of our ink has no counterpart in the source    -> moved or gone
    max_pt        the furthest displaced ink, in points                        -> outlier only
    text_recall   character recall against the source text                     -> content
    signature     content-loss / displacement / mixed / clean
    problem       one of eight names, see benchmarks/PROBLEM-NAMES.md

**Rank by `share@5px`. Never by `max_pt`** — it is one pixel and it once read 134 pt on a
document whose pages looked nearly identical.

## What each document's number means

    benchmarks/RANKING.csv      one row per document; share5 is the score
    benchmarks/STATE.json       verdict + ratchet + the round the numbers belong to
    benchmarks/PROBLEM-NAMES.md the eight problem names and what each means for a user

## The phase machine

    python3 tools/p2w-bench/round.py --phase            # one bare word: measure|classify|fix|done
    python3 tools/p2w-bench/round.py --claim-<name>     # take the slot before working
    python3 tools/p2w-bench/round.py --release-<name>   # give it back
    python3 tools/p2w-bench/round.py --advance          # measure->classify, classify->fix
    python3 tools/p2w-bench/round.py --close-round      # fix->next round; only from fix
    python3 tools/p2w-bench/round.py                    # human status

The gates decide, not the brief:

    python3 tools/p2w-bench/measure_gate.py     # every row scored, no dups, right round
    python3 tools/p2w-bench/classify_gate.py    # class file covers the measurement

## The class file

    benchmarks/DEFECT-CLASSES.md

That path and no other. It must carry

    Documents measured: **N of M**

and its rows must use exactly `OPEN`, `FIXED`, `PARKED`. Any other word is invisible to
`round.py`, which is worse than `OPEN` because it looks finished.

## Still live, and why

    verify_txt.py    the 12 .txt checks. gate.py runs it as its advisory layer. Do not edit
                     it as a way to make a number improve - a check is the measurement.
    ratchet.py       the APK cron's Gate B, a second opinion behind gate.py's Gate A.
                     Not the score. If A and B disagree, A wins and B is a bug to report.

## Retired as a measurement

    verify_google.py   the 47 docx checks. Advisory: they NAME a defect, they do not SIZE
                       one. All 47 are falsifiable (benchmarks/FALSIFY-47-RESULT.md), which
                       is the floor, not proof they are right.
    record.py          superseded by RANKING.csv and STATE.json
    classify.py        superseded by benchmarks/DEFECT-CLASSES.md
    calibrate.py       superseded by p2w.py --validate
    seed.py            superseded by the committed RANKING.csv baseline
    BASELINE.md        nothing reads it any more; RANKING.csv is the table
    RESULTS.jsonl      nothing writes it any more; STATE.json is the record

## The corpus

    211 synthetic documents from release corpus-v1
    + every PDF in benchmarks/realworld/   (today: 2 nine-page bank forms)

    213 total. measure_gate refuses a corpus smaller than that, so a corpus that failed to
    build cannot read as "everything measured".

Never average the two populations. Synthetic median `share@5px` is 0.3%; the real documents
read 10.3%, and the two worst read 98.7% and 97.6%. Quote both, or quote neither.
