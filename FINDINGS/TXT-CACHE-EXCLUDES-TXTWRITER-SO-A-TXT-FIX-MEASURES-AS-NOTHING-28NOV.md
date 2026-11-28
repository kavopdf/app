# THE CORPUS CACHE CANNOT SEE A `TxtWriter.java` CHANGE, SO A .txt FIX MEASURES AS NOTHING

**28 Nov 2026, fixer run 11:00-12:30.** Found while landing the `.txt` hoist, and it is the reason
that hoist had not landed in the run that built it.

## The defect

`corpus-convert.py` keys the corpus cache on `engine_sources(fmt="docx")`, and that function
**excludes `TxtWriter.java`** on purpose:

    DOCX_EXCLUDES = ("TxtWriter.java",)          # corpus-convert.py:136

The reason is written in the file and is correct *for the .docx*: the cache holds `.docx` files, and
`TxtWriter` cannot move a `.docx` byte. What it also does is make a change to `TxtWriter.java`
invisible to `corpus-slice.py`. The slice looks at 214 documents, decides every one of them is
current, converts nothing, and prints:

    DONE - 214 documents converted, stamp written for engine a05b20eb05fe0fc8

which is true and is not the same statement as "the corpus is this tree's output".

## What it did to this run, exactly

| at | what | effect |
|--:|:--|:--|
| 05:29 | a timed-out `install-gate.sh` left 49 `.docx`+`.txt` from the **unpatched** engine | 49 stale documents on disk |
| 05:39 | the `TxtWriter` patch applied and `javac` rebuilt `out/ConvertAll.class` | tree is the new engine; cache key unchanged |
| 05:47-05:57 | `corpus-slice.py` converted the 165 it thought were missing | 214/214 "converted", **49 still old** |
| — | `verify_txt.py` on `305_vaccination_certificate` from the corpus output | **FAIL, t08 32 vs 33** — the pre-patch answer |

A single-document probe (`ConvertOne`) had already said PASS. The corpus said FAIL, on the same
document, from the same tree. The difference was not the engine, it was which 49 files the cache
had decided were current.

**A run that hits this and does not diagnose it reports that its patch did nothing**, which is the
shape of the last three runs on this class.

## The fix, in the tool

`corpus-slice.py --force` re-converts every document whose `.txt` mtime predates the newest
`engine/*.java`. It resumes by file time rather than by a bookkeeping file, so it slices the same
way a cold build does: each call converts the stale ones, the next call sees fewer.

Measured on this run: `--force --status` said **49 of 214 .txt predate the newest engine source**,
one 265 s slice converted all 49 with 0 failures, and `305` then verified **PASS (7/12 applicable,
7 passed)** from the corpus output.

## The rule this produces, stated without naming a class

> **A cache whose key excludes a file cannot measure a change to that file.** Before believing a
> corpus-wide number after an engine edit, check that the cache key actually moved — and if the
> edit is in a file the key excludes, force the rebuild rather than trusting the "DONE".

## A second, separate hole found at the same time

`restamp_txt.py --apply` writes **both** `RANKING-TXT.csv` and `RANKING-TXT-BASELINE.csv` from the
same new results. `regress.py`'s `.txt` regression check compares those two files. After an
`--apply`, that comparison is new-against-new and **cannot fail**, whatever the change did.

So the gate's "txt: no document worse than baseline" is not evidence for a `.txt` change made in
the same run. This run did not rely on it: it copied `RANKING-TXT.csv` to `/scratch/work/` before
the re-stamp and diffed the store itself.

    before: 214 docs, 208 clean
    after : 214 docs, 209 clean
    improved: 1   worsened: 0
      BETTER 305_vaccination_certificate  (7, 6, 1, t08_line_order) -> (7, 7, 0, '')

That diff, not the gate line, is the measurement that this change is safe. The baseline file is
the ratchet and a ratchet that is re-cut every time it is read is not a ratchet.
