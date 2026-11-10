# TOOLBOX — how to use every tool in this pipeline

One section per tool: the exact command, what it prints, what it returns, what it
writes, and what it must not be used for. Read only the sections your cron needs.

Every flag here is checked against the code by `toolbox_check.py`. If this file and
the code ever disagree, the check fails — a stale interface reference is worse than
none, because it teaches a cron to call something that no longer exists.

Common to every tool below: run from the repository root, and `git push` does not
work in this environment. Commit with `GITHUB_COMMIT_MULTIPLE_FILES`.

---

## verify_google.py — the measurement

**Used by:** baseline. **Not used by:** classifier, fixer (it reads recorded
numbers instead), APK.

```
python3 tools/p2w-bench/verify_google.py <source.pdf> <google-export.pdf> [--json out.json]
python3 tools/p2w-bench/verify_google.py --list-checks
```

Prints one line per document, then one line per failing check:

```
300_prescription_rx.pdf                40/58 FAIL
    01_page_count                source=1        render=2
    20_within_10pt               source=100      render=20
```

`--json out.json` adds every check with its source and render value, plus
`document`, `source_file`, `render_file`, `passed`, `total`, `ok`, `failed`.

`--list-checks` prints the 58 check ids, one per line. Use this when you need the
denominator — never write a total from memory.

Exit codes: **0** every check passed, **1** at least one failed, **2** could not run
(a missing or unreadable PDF).

The denominator is whatever `total` the script reports. It has been 31, then 50,
then 58. Never hardcode it.

Deterministic: the same pair twice gives byte-identical output, so a changed result
means the document changed, not the measurement.

---

## record.py — keep the numbers so nobody measures twice

**Used by:** baseline (writes), fixer (reads). **Not used by:** classifier, APK.

```
python3 tools/p2w-bench/record.py res/*.json --round <n> --engine <hash>
python3 tools/p2w-bench/record.py --show <document>
python3 tools/p2w-bench/record.py --show <document> --check <id>
```

Writes `RESULTS.jsonl`, one line per document per round per engine. Re-running the
same document for the same round and engine replaces its line instead of adding a
second one.

`--show` prints what the baseline already measured:

```
round 1  engine 2a68de6  31/58  18 failing
    20_within_10pt             source=100        render=62         FAIL
```

This is how the fixer sees how far off and in which direction, without pushing the
document through Drive again. Exit **0** found, **1** no record.

---

## ratchet.py — the regression rule

**Used by:** all four. Baseline runs it after measuring, classifier runs `--check`,
fixer runs it before committing, APK runs `--check` before publishing.

```
python3 tools/p2w-bench/ratchet.py            # update marks, fail on regression
python3 tools/p2w-bench/ratchet.py --check    # same, but never raise a mark
```

Prints a four-line summary and any regressed documents:

```
ratchet
  documents scored this run : 20 of 208 rows
  high-water marks held     : 20
  new documents, first mark : 0
  REGRESSED: 1 document(s) below their best ever score
      04_stamp_180deg_upside_down        44/58 was 46/58  (-2)
  FAIL - the bar fell
```

Exit **0** the bar held or rose, **1** something fell, **2** could not run.

It holds, per document, the best score ever reached AND the set of failing checks at
that point. Two things count as a regression: the score falling, and a check that
used to pass now failing — even when the score is unchanged. It compares only
checks that existed at both marks, and a mark taken by a smaller verifier does not
bind a larger one. Do not try to out-think it and do not edit `RATCHET.json` by hand.

---

## round.py — whose turn it is

**Used by:** all four.

```
python3 tools/p2w-bench/round.py                 # status
python3 tools/p2w-bench/round.py --phase         # prints exactly: measure | classify | fix | done
python3 tools/p2w-bench/round.py --advance       # measure -> classify -> fix
python3 tools/p2w-bench/round.py --close-round   # archive, empty scores, next round or done
python3 tools/p2w-bench/round.py --claim-fixer   # 0 = go, 1 = another run is working
python3 tools/p2w-bench/round.py --release-fixer
python3 tools/p2w-bench/round.py --apk-status    # 0 = may ship, 1 = no (prints why)
python3 tools/p2w-bench/round.py --mark-apk-shipped <version>
python3 tools/p2w-bench/round.py --force-round <n>   # set the round by hand; recovery only
```

`--phase` prints one bare word. Compare it, do not parse the status output.

Status prints:

```
round 1 of 3   phase: measure
  documents scored : 20 of 208
  open classes     : 0
  next             : baseline runs until 208 of 208 are scored
```

`--close-round` archives `BASELINE.md` as `ROUND-<n>.md`, `ATTEMPTS.json` as
`ATTEMPTS-round-<n>.json`, empties every score, clears the fixer claim and the
shipped mark, and moves the phase. It survives a missing BASELINE.md.

The fixer claim expires after 100 minutes on its own, so a run that dies cannot
block the next one. Always `--release-fixer` when you finish, even on failure.

---

## classify.py — separate and rank the defects

**Used by:** classifier (writes), fixer (reads and records attempts).

```
python3 tools/p2w-bench/classify.py
python3 tools/p2w-bench/classify.py --subclusters "<exact class name>"
python3 tools/p2w-bench/classify.py --attempt "<exact class name>" --outcome kept|improved|reverted|error
python3 tools/p2w-bench/classify.py --top <n>        # how many classes the table lists
```

Writes `DEFECT-CLASSES.md` and `ATTEMPTS.json`. Prints:

```
documents measured : 20
checks firing      : 35
classes (data-driven): 28
  47_margins                          20 docs  OPEN
  53_embedded_faces                   20 docs  OPEN
```

Classes are named after the check that touches the most documents. There are no
hand-written names, and adding one is a mistake: a friendly label written before
the data was seen sends the fixer after the wrong cause.

A check that fails on almost every document is its own class, because it cannot
discriminate between causes. A class bigger than six checks is re-split at a
stricter threshold until the parts can name one cause each.

`--subclusters` splits one class by the checks its documents also fail:

```
class '47_margins' - 20 documents, 32 outside checks

   16 docs  with 19_worst_dy
    3 docs  with 09_font_names
```

Copy the class name exactly as printed, including the `(+N)` suffix. If it says no
class matches, run `classify.py` first and copy from the output.

Attempt outcomes: `kept` (target passes on at least half, nothing worse),
`improved` (moved on at least a third, nothing worse, day restarts up to 3 times),
`reverted`, `error`. Limits: one day per class, 12 attempts, 3 requeues.

---

## hypothesis.py — what earlier attempts already ruled out

**Used by:** fixer only.

```
python3 tools/p2w-bench/hypothesis.py --show "<exact class name>"
python3 tools/p2w-bench/hypothesis.py --next "<exact class name>"
python3 tools/p2w-bench/hypothesis.py --add "<exact class name>" "<theory>" \
        --result ruled-out|confirmed|untested --evidence "<the numbers>"
```

Writes `HYPOTHESES.md`, one section per class. `--next` prints only the untested
theories; when nothing is left it says so and tells you to form a new one.

A duplicate hypothesis is refused rather than recorded twice. RULED OUT entries each
cost a calibration run — do not re-test one without new evidence, and if you do, say
what changed.

---

## calibrate.py — is this a renderer limit or an engine bug?

**Used by:** fixer only.

Builds the smallest docx that isolates one variable in three variants, sends each
through Drive, and measures what comes back. This is how you tell "Google will not
do this" from "our engine writes the wrong thing". It is not optional before an
`unfixable` verdict — 89 rows were once closed on an untested assumption and all
had to be reopened.

---

## google-gate.sh — how much was measured on this engine

**Used by:** APK.

```
bash tools/p2w-bench/google-gate.sh
```

Prints the engine hash, how many documents are in the table, how many were measured
at all, and how many on the current engine. Exit **0** pass, **1** fail.

If it reports nothing measured on the current engine, say so plainly: the APK is
then unverified by Google. Do not quietly publish.

---

## precommit.sh — build and sanity before any commit

**Used by:** fixer, APK.

```
bash tools/precommit.sh --no-corpus     # fast; what the crons use
bash tools/precommit.sh                 # also runs the corpus
bash tools/precommit.sh --all           # every tier, including the corpus
```

Exit **0** pass, non-zero fail. Must exit 0 before a commit is allowed.

---

## reset_round.py — back to round 1 with nothing measured

**Used by:** a human, or the agent on request. Never by a cron.

```
python3 tools/p2w-bench/reset_round.py          # dry run, changes nothing
python3 tools/p2w-bench/reset_round.py --yes    # do it
```

Archives everything under `archive/reset-<timestamp>/` first, then clears
`BASELINE.md` scores, `RATCHET.json`, `ATTEMPTS.json`, `RESULTS.jsonl`, regenerates
`DEFECT-CLASSES.md` and sets `ROUND.json` to round 1, phase measure. Then it re-counts
and exits **1** if anything survived. A reset is a new attempt, not a deletion.

---

## The files these tools share

| File | Written by | Read by | Meaning |
|---|---|---|---|
| `BASELINE.md` | baseline, fixer | all | one row per document: score, verdict, failing checks, engine, date |
| `RATCHET.json` | ratchet.py | ratchet.py | best ever score + the failing set at that point |
| `RESULTS.jsonl` | record.py | record.py | per-check source vs render, per round, per engine |
| `ROUND.json` | round.py | all | round, phase, fixer claim, shipped mark |
| `DEFECT-CLASSES.md` | classify.py | fixer | ranked classes with status |
| `ATTEMPTS.json` | classify.py | fixer | attempts, requeues, outcomes per class |
| `HYPOTHESES.md` | hypothesis.py | fixer | what was ruled out, per class |
| `REMAINING-DEFECTS.md` | fixer | human | what is genuinely unfixable, with numbers |
| `ROUND-<n>.md` | round.py | human | the archived scores of a finished round |

`BASELINE.md` rows are exactly six columns. Never rebuild the file from a fetched
string — that deleted 119 rows on 10 Nov. Edit it in the local clone.
