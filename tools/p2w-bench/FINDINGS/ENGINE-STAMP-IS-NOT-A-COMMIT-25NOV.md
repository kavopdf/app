# The Google scoreboard read zero because it compared a commit with a hash

**25 Nov 2026, fixer slot 10:56 IST.** Instrument fix, kept. The truth was in the store the whole time.

---

## The defect

`report.py` printed, on every run for at least two consecutive slots:

> **Fixed - Google, every applicable check** | **could not be read** - 0 of 212 scored were read as
> current, which is a failed read and not a measurement.

Nothing was wrong with the store. `google_fixed()` compares two different quantities with `==`:

| | |
|:--|:--|
| the store's stamp (`benchmarks/gverify/*.json`, 213 rows) | `engine = "981ff1fa35e2cf67"` - 16 hex, `sha256(name + bytes of every app/.../engine/*.java)[:16]`, written by `gvbatch.py:26,76` |
| `report.py:engine_now()` at HEAD | `git log -1 --format=%h -- app/.../engine/` -> `"85b8735f"` - an 8-char git abbreviation |
| the comparison, `report.py:460` | `if (j.get("engine") or "") == now:` - exact string equality |

Two quantities, two lengths, so it matched nothing and reported zero. `gverify.py:194` had already
been fixed for exactly this (`_e == now or now.startswith(_e) or _e.startswith(now)`), but its
`_engine_now()` still answered `%h`, so `_done()` returned 1 (the single page-count refusal) and
`plan()` said "1 of 213 documents have a Google result; 212 to go" - an hourly cron re-measuring all
212 for ever. That is starvation in the other direction, and it is why the store never looked fresh.

`classify_google.py:34` carried the same defect and printed it into the class table every run:

> **HEAD is `85b8735f` and 0 of the 212 Google results were measured on it**; the rest came from
> `981ff1fa35e2cf67` (212). Re-measure before treating any row as the current behaviour.

Every run that read that line was told to distrust the only Google measurement it had.

## The measurement, before and after

Same tree, same store, only the instrument differing.

| | before | after |
|:--|:--|:--|
| `report.py` "Fixed - Google" | **could not be read** - 0 of 212 current | **42** of the **212** re-measured on this engine (213 after `b559f2ac` landed) |
| `report.py --json` | `google_fixed_current=0` | `google_fixed_current=42, google_scored_current=212, google_refused=1` |
| `classify_google.py --print` header | "0 of the 212 ... measured on it; re-measure" | "Every result above was measured on engine `981ff1fa35e2cf67`, the engine in the tree." |

## The population, proved three ways that do not share code

1. **The store.** All 213 files in `benchmarks/gverify/`: every row carries `engine =
   981ff1fa35e2cf67` and `render = google`; 42 of them carry `failed = []`. (At the time of the
   measurement it was 212 scored plus one `status: page_count_refused`; the 213th verdict - document
   600, 37 of 44, failing `18_displacement` among others - landed from another run's commit
   `b559f2ac` at 06:10 UTC, and it is stamped on the same engine.)
2. **The tree.** `regress.engine_fingerprint()` on this clone returns `981ff1fa35e2cf67` for the txt
   fingerprint (all `.java`) - the same value the store is stamped with. `corpus-slice.py` wrote the
   same value into the corpus stamp after converting all 213 documents.
3. **The commit that wrote the store.** `9165bf25` (25 Nov 05:14) states its own numbers: "on current
   engine: 212 (one page-count refusal)", "clean: 42 of 212". The scoreboard contradicted the commit
   that produced its own data.

So **42 of 213 documents pass every applicable Google check on this engine** - not 0, and not the
"6 clean of 192 scored" the FIXER-BRIEF charter still carries. The charter line is stale; it is not
edited here because it is the user's text, but no run should plan against it again.

## What this changes for the pipeline

* The scoreboard's Google row is now a number, so a fixer can see whether a fix moved a document in
  the renderer the user opens, instead of only in LibreOffice.
* `gverify.py plan()` now sees 212 measured documents, so the :20 cron stops re-measuring the whole
  corpus hourly and can spend its 60-document budget on documents whose engine has actually moved.
* `DEFECT-CLASSES-GOOGLE.md` will say the engine coverage truthfully on its next regeneration. That
  file was **not** regenerated here: `classify_google.py --check` says it is already STALE on its rows
  (41 rows differ) for reasons that predate this change, and absorbing that drift should be a
  deliberate pass, not a side effect of an instrument fix. Recorded, not touched.

## Residual, same defect, not patched

`verify_google.py:6394` (`_engine_head()` -> `%h`) stamps NEW verdicts with a commit abbreviation
while the existing 212 carry the source hash. Until it is aligned, a freshly measured document will
carry a different kind of stamp from the rest of the store and will not count as current. This is the
next instrument fix, and it needs one Google round trip to prove, which this pod cannot do (no Drive
render path from here).

## What would falsify this

A verdict row whose `engine` equals the source hash while its `.docx` was produced by a different
engine - i.e. stamps rewritten without re-measuring. The corpus stamp written by `corpus-slice.py` in
this run (`{'engine': '981ff1fa35e2cf67', 'documents': 213}`) is the independent check that the tree
that converted the 213 documents is the tree the 212 verdicts are keyed on.

## Gate state after the change

```
regress.py --check   PASS - nothing got worse in both formats, and the table matches this engine
                     (corpus built here: 213 converted, stamp 981ff1fa35e2cf67, 0 failed)
measure_gate.py      READY - every document measured (docx 212/212 scored, 1 exempt)
google-safe.py       no construct Google ignores has spread
```
