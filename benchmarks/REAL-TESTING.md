# Real testing, start to the end of round 3

Not a dry run with fabricated files. The real instrument, the real corpus, the real gates,
and the real phase machine. Everything below was found by running it.

## Bugs found and fixed

### 1. The corpus was 211, and the gate expected 213 - a permanent deadlock

`corpus()` looked for `realworld/` beside the script. The baseline cron copies only
`p2w.py` and `gate.py` into `/scratch/work`, so the directory never came along: the corpus
built to 211. `measure_gate`, which runs from the clone where `benchmarks/realworld/` does
exist, expected 213. 211 < 213 is a gate that refuses for ever, so the pipeline would have
stopped at measure on its first run with every cron reporting success.

Fixed: `_realworld_dirs()` searches beside the script, then in the repo the script clones
for the engine, then in a `benchmarks/` directory beside the script. Verified: corpus 213,
GATE PASS, both bank forms present.

### 2. A timed-out run deleted the baseline

`--budget` is a time limit, so a run can stop after 13 documents of 213. `rank()` wrote
whatever it had to `RANKING.csv`, replacing the committed table with 13 rows - and
`gate.py` then reported **"OK: no regressions"**, because the 200 documents it never
looked at could not regress.

Fixed: a partial run writes `RANKING.partial.csv` and leaves the published table alone.
Verified during the real measurement: at 212 of 213 it printed
`PARTIAL: 212 of 213 measured - writing RANKING.partial.csv, the published RANKING.csv is untouched`.

### 3. `gate.py` could not find `ROUND.json`, so the round stamp was always None

It resolved `dirname(__file__)/../tools/p2w-bench/ROUND.json`, which from `/scratch/work`
is `/tools/p2w-bench/ROUND.json`. `measure_gate` refuses a measurement whose round stamp
does not match the machine's, so round 1 could never advance either.

Fixed: `_find_round_json()` searches three places. Verified: `round: 1` instead of `None`.

### 4. The verdict called an incomplete measurement clean

Fixed: `INCOMPLETE` now outranks every comparison except a failed ground-truth gate.
Verified: `INCOMPLETE: measured 20 of 213 documents - run again with more budget before
trusting any comparison`.

### 5. `verify_txt.py --help` exits 2, and the failure was recorded as "available"

A smoke test whose failure was written down as a pass. Fixed to use `--list-checks` and to
report `BROKEN` honestly.

### 6. A future-dated claim locked the slot for ever

`age = (now - started)/60` goes negative when a timestamp is in the future - clock skew, a
hand-edited `ROUND.json`, a timezone mistake - and `age < limit` is then true for ever. The
slot reads as busy permanently and the cron stands aside on every run. Found by testing
`claim()` with a far-future timestamp.

Fixed: `claim_age_min()` treats a timestamp more than five minutes in the future as stale.
Used by both `claim()` and `release()`. Verified: now 0.0, 45 min ago 45.0, far future 1e9,
no claim None.

### 7. `classify_gate` compared N against M - so one exemption broke it

The class file's header reads `Documents measured: **212 of 213**`: 212 scored, 213 in the
corpus. The gate compared the header's M against the **scored** count, so any corpus with
one exempted document failed for ever - and it printed "classify again", which could never
help, because classifying again cannot change how many documents were measured.

Fixed: `scored_docs()` returns `(scored, total)` and the two are checked separately.
Verified: `212 scored of 213 rows, class file covers 212 of 213 - READY`.

### 8. Rounds 2 and 3 were fake - the class file survived the round boundary

`--close-round` blanked `BASELINE.md` but left `DEFECT-CLASSES.md` untouched. The fixer
marks a class FIXED when its number improves, so the next round inherited a file that
already said everything was FIXED: `--close-round` found no OPEN row and the round closed
instantly having done nothing. Three such rounds reach `done`, and the app ships on one
round of work dressed as three.

Fixed: `--close-round` blanks every class file, so the classifier must write a fresh
classification from the new measurement, and `classify_gate` refuses to advance until it
has. A round cannot reach fix, let alone close, without a class list built for that round.

## Real walk, all three rounds

    start phase: measure
      round 1 closed -> phase measure, round 2
      round 2 closed -> phase measure, round 3
      round 3 closed -> phase done

    FINAL: round 3 of 3, phase done
    APK may ship: YES

Driven by the real `RANKING.csv` (213 documents), the real exemption, and a class file
generated from the real measurements - not fabricated.

## Real measurement, all 213 documents

    213 rows, 212 scored, 1 MEASURE-ERROR (exempted with a reason)

    content-missing-nothing-in-its-place   30
    content-missing-partly-replaced        16
    content-present-wholly-displaced       15
    content-present-partly-displaced       12
    content-partly-lost                    11
    content-partly-lost-and-displaced       7
    single-element-far-out                  1
    none                                  120
    unmeasured                              1

`416_many_tiny_pages` (300 pages) is the unmeasured one: a whole-document measurement
exceeds the per-command budget, so the run is killed mid-document and no result is
written. Exempted with that reason recorded rather than dropped. **The real fix is
resumable page-by-page measurement - the same fix the nine-page forms need.**

## Function tests

39 checks across `problem_name` (all 8 branches), `signature` (all 4), `invention` (mirror
of position), `content` (recall), `corpus`, `rows`, `class_files`, `open_classes`,
`claim`/`release` including the stale window, `measure_gate.state`/`expected_docs`/
`round_stamp`, and `classify_gate.scored_docs`/`header_count`.

    39 passed, 0 failed

Two failures along the way were my own test's expectations, not the code: a curve of
60/45/40 is `content-loss` (it barely falls), and `scored_docs()` legitimately changed
signature when N and M were separated.

## A mistake I made and had to fix

My first walk script used `open(f, "w").write(open(f).read().replace(...))`. Python opens
`"w"` and truncates **before** the read, so it emptied the class file and the walk failed
for a reason that had nothing to do with the pipeline. Read first, then write.
