# `--collect` deleted the export it was refusing, so 21 of the 23 refusals say nothing about the tree

**24 Nov 2026, fixer slot 17:54.** Engine built in-sandbox (42 s), corpus fetched (213 PDFs), one
document converted and one refusal recorded end to end through the shipped `collect()`.

## What was believed

That a page-count refusal is a fact about the document: "this one drew the wrong number of pages". The
report prints it as `Not scored - page count did not match: 23 of the 213 gverify saw`, and the brief
calls it "a defect, not a pass". So the 23 were treated as 23 known engine defects waiting for a fix.

## What was measured

The recorder, not the document. `gverify.py --collect` had two faults in the same branch:

1. **`os.remove(tmp)` in the refusal branch.** The export was deleted before anything could read it, so
   the one piece of evidence that decides *engine or instrument* - what the extra page actually holds -
   was destroyed by the code that recorded it. 21 of the 23 were recorded as "one page too many" with no
   record of whether that page carried the page's own borders or nothing at all.

2. **The refusal wrote its own dict instead of going through `_write`.** The committed store, read
   directly:

   ```
   refusals in benchmarks/gverify/        : 23
   with no engine stamp                   : 21
   union of keys                          : ['engine', 'name', 'pages', 'status', 'want']
   ```

   So "23 refused" was a claim about 23 Nov, not about the engine in the tree: no `engine`, no `at`, no
   `checks` stamp on 21 of them, and nothing that could ever be counted as a current measurement. The
   report's own line ("4 of the 190 scored are still on an older engine") never saw them, because a
   refusal is not scored at all.

## What is now true

The refusal goes through `_write` and carries `engine`, `checks` and `at` like every other record, plus
two new fields: `extra_pages` (per extra page: words, chars, drawings, images) and `export` (the kept
file). The export is written to `<name>.refused.pdf` in the gverify working directory instead of being
deleted. Measured on one real document with a synthetic second page:

```
source 1 page(s), export 2 page(s)
REFUSED: 01_stamp_rotated_15deg_upright rendered to 2 page(s), the source has 1
  page 2: 0 word(s), 0 drawing(s), 0 image(s)  <- EMPTY: a counter, not a sheet
  export kept: /tmp/gv-probe/gd/01_stamp_rotated_15deg_upright.refused.pdf
keys: ['at', 'checks', 'engine', 'export', 'extra_pages', 'name', 'pages', 'status', 'want']
engine: b7699196 | checks: 369550-1795522931 | at: 2026-11-24T12:47:34
extra_pages: [{"page": 2, "words": 0, "chars": 0, "drawings": 0, "images": 0}]
```

Before the change the same probe wrote `name, status, pages, want, at` and no export survived. The census
is written into the record, not left in `/scratch/work`, because the record is committed and the scratch
directory is not.

## What it does not claim

No verdict changed. A refusal is still a refusal, `status` is still `page_count_refused`, and nothing in
`matrix()`, `report.py` or `measure_gate` reads the new fields yet - they are evidence for the next run,
not a number in this one. The next gverify pass over those 23 documents is what turns the census into a
measurement; until it runs, the 21 unstamped refusals stay stale, which is the honest state.

## What would prove this wrong

A refusal recorded after this change that comes back with `engine` missing, or an export that is not on
disk, or a page-2 census that disagrees with `pdftotext -f 2 -l 2` on the same file. Any of the three
means the recorder is still lying and this finding is wrong.
