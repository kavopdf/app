# Two instruments were counting files and calling them measurements

**25 Nov 2026, fixer slot 09:13. Measured before and after in one clone, engine `85b8735f` / fingerprint
`981ff1fa35e2cf67`.**

## The defect, in one sentence

`stage.py:measured()` and `health.py:compute()` both counted the `.json` files in `benchmarks/gverify/` and
called the count "measured through Google". 213 files exist; **82 carry the engine on HEAD**. So the stage
read `fix` and the watchdog read `done 213 of 213` while 131 results described an engine two commits old.

This is the same defect `gverify._done()` was written to end on 21 Nov (`gverify.py:154-168`: "A FILE ON DISK
IS NOT A MEASUREMENT"), and `--plan` has used it since. Two instruments, two answers, one question - which is
how the 22 Nov "0 verified" report happened.

## Before and after

| instrument | before | after |
|:--|:--|:--|
| `stage.py` | `stage: fix` / `measured: 213 through Google (191 scored, 22 refused)` | `stage: measure-google (changed from fix)` / `measured: 82 through Google (60 scored, 22 refused)` |
| `health.py` measure-google | `done 213 of 213` | `moving 82 of 213` |
| `health.py` matrix | `done 213 of 82` (once the Google count moved) | `done 213 of 213` |

`gverify._done()` returns 82 at this engine; of those 82, 22 are `page_count_refused`, which `_done()`
already treats as done, so `stage.py` reports 60 scored and 22 refused.

## The matrix row was a second, latent bug

`matrix`'s `of` was the **Google** count. The moment the Google count became engine-aware, the line printed
`done 213 of 82` - a fraction greater than one, the same class of nonsense as the "213 of 212" the file's own
header warns about. The matrix is a LibreOffice render of every document in the corpus, so the corpus is what
it is measured against: `of: total`, `done` when `lo >= total`.

## Why this is worth a run even though no document moved

`classpick.py` refuses a new class while the pending list is non-empty, and four of the pending items were
the ledger disagreeing with itself about whether a measurement existed. The stage a run is told to work in
was wrong by 131 documents. That is not progress toward 99 %, but it is the instrument that says whether
progress happened, and it was reporting a finished measurement over a stale table.

## What would overturn this

A result in `benchmarks/gverify/` whose `engine` field is empty and which was nevertheless taken on HEAD - the
abbreviation guard at `gverify.py:185-194` accepts `e == now`, `now.startswith(e)` and `e.startswith(now)`, so
an empty stamp counts as *not* done by design. The honest cost of the fix is that the count is 82, not 213,
and the next gverify pass moves it.
