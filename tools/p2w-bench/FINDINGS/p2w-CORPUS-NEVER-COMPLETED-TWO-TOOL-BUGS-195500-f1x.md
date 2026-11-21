# The corpus pass could never complete, and `RANKING.csv` was never written by `p2w.py` at all

**21 Nov 2026, 19:55 IST, fixer.** Two defects in `benchmarks/p2w.py`, both silent, both in the path
every engine patch has to go through. Fixed, and each proved by a number that changed.

This is the answer to a question that has been open for days: *why does a full corpus pass never end
in a `RANKING.csv`?* It was not slowness and it was not the corpus. It was a `KeyError` and a missing
file.

## Defect 1 - `rank()` crashes on the progress file the same function writes

`measure()` keeps a resumable window for a document over 80 pages in `DIST/<doc>.partial.json`:

    {"first": 120, "merged": {...}}

That is a progress note. It has no `doc` key. `rank()` read every `DIST/*.json` and did
`seen[d['doc']] = d`, so it raised `KeyError: 'doc'` on
`416_many_tiny_pages.partial.json` - **after** the whole corpus had been measured.

Measured this run, 13:58:

    [13:58:13] chunk 1: measured 211 of 212
    Traceback (most recent call last):
      File "/scratch/work/p2w.py", line 1400, in main
        docx(end); run(end); r=rank(); status()
      File "/scratch/work/p2w.py", line 1257, in rank
        else: seen[d['doc']]=d
    KeyError: 'doc'

The pass was complete. The traceback killed the run before the table was written, so the run looked
like a run that did nothing - and the engine patch it was measuring stayed unlandable.

**Fix:** `results()` returns `DIST/*.json` minus `*.partial.json`, and the three readers of `DIST`
(`rank()`, the `done=` count in `run()`, `status()`) use it.

## Defect 2 - `EXEMPT.json` was read from one hard-coded path, and the brief puts the script elsewhere

    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "p2w-bench", "EXEMPT.json")

That resolves correctly only when `p2w.py` runs from `benchmarks/` inside a clone. `FIXER-BRIEF.md`
instructs every run to `cp benchmarks/p2w.py /scratch/work/` and run it from there, where the path is
`/scratch/tools/p2w-bench/EXEMPT.json` and does not exist. The `except` returned an empty set, silently.

So `want` counted `416_many_tiny_pages`, which `EXEMPT.json` excludes **by design** because 300 pages
cannot be measured inside one command. `have` could never reach `want`, `complete` was never true, and
the tool wrote `RANKING.partial.csv` on every run of its life. Measured before the fix:

    corpus 211/211  docx 211/211  measured 210/211  remaining 1
      PARTIAL: 210 of 211 measured - the published RANKING.csv is untouched

210 measured, one exempt, and the tool still called the corpus unfinished.

**Fix:** `_exempt_paths()` is the same list-of-places shape as `_realworld_dirs()`, which already
solved exactly this problem for `benchmarks/realworld/`: beside the script, in `REPO`, in
`ENGINE_SRC`, then beside the script in `tools/`. A miss now logs a WARNING instead of returning an
empty set. `status()` uses the same denominator, so `remaining` can reach 0.

After both fixes, on the same corpus and the same engine:

    corpus 211/211  docx 211/211  measured 210/210  remaining 0
    /scratch/output/RANKING.csv   211 lines  (header + 210 documents)

## Why this matters more than the patch it blocked

`regress.py --check` refuses any commit whose table is not measured on the tree's engine. The only
tool that measures the tree is `p2w.py`. While `p2w.py` could not write `RANKING.csv`, **no engine
patch could ever be gated**, and every run that tried one either shipped it unmeasured or reverted a
good patch for want of a measurement. `patches/47-margins-cell-border-inset.patch` had been sitting
measured on nine documents and unlanded since 03:45 for exactly this reason.

## The cell-border patch is REFUTED at corpus scale - do not re-apply it as written

With the corpus pass working, the patch (`47_margins-CELL-BORDER-PAID-TWICE-034500-f1x.md`) was
measured on all 210 documents instead of nine.

| | nine-document sample (03:45) | 210-document pass (this run) |
|---|---|---|
| `404_sudoku_grid` share@5 | 0.27 -> 0.00 | **0.27 -> 0.00** |
| documents improved | 2 | 4 |
| documents **worse** | 0 | **24** |
| mean share@5 | - | 2.810 -> 2.823 |

`regress.py --check` on the real table:

    docx: 24 REGRESSION(S)
      bank-statement-5-pages                  0.56 -> 0.60
      gst-invoice-multipage-item-table        0.40 -> 0.54
      purchase-order                          0.90 -> 0.93
      two-tables-stacked-with-no-gap          0.77 -> 1.07
      64_newspaper_uneven_columns_ad_boxes    3.46 -> 3.61
      text-held-twice-shadow-text             30.29 -> 30.41
      insurance-policy-schedule               0.53 -> 0.64
      table-with-no-header-row                0.61 -> 0.86   (+41 % relative)
      ...

The nine-document sample was not wrong about `404_sudoku_grid`; it was too small. Every document it
picked was one where the rule is thick (2 pt, `w:sz=16`). The 24 that got worse are tables whose left
rule is thin or absent, where subtracting the full border moves the text off a position the renderer
had already placed correctly.

**Not landed. Reverted.** The engine is back at the committed state.

**What would settle it, for the next run:** subtract only where the writer's rule is thick enough that
a renderer insets by it - `sz >= 8` (1.0 pt) is the boundary the 404 measurement supports and the
regressions contradict below. That is a hypothesis, not a measurement: it needs the same 210-document
pass, and the number to beat is `4 improved / 24 worse` becoming `2+ improved / 0 worse`.

## A third, smaller lie, not fixed

`regress.py --check` reports this commit as `scope of the change: txt` because `scope.py` attributes
by method name and cannot see that `benchmarks/p2w.py` is a measurement tool, not the engine. It
cannot move either format. The gate is right to pass; the sentence is wrong. Left standing, recorded
here, because a wording change should not ride along with a measurement.
