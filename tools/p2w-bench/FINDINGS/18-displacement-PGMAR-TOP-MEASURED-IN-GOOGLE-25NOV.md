# 18_displacement: the page-top gap is dropped by Google at a page break, and `w:pgMar w:top` keeps it

**Run:** fixer, 25 Nov 23:56 IST · **Engine measured:** `771234e164611275` (tree = HEAD + the patch below)
**Verdict:** MECHANISM PROVEN IN GOOGLE on 4 documents. **Not committed**: the corpus was not re-measured
on this engine inside the slot, so `regress.py --check` refuses, correctly. Patch is in
`patches/18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch`.

## The mechanism

A page's top gap is emitted as `w:spacing w:before` on the first paragraph of the sheet
(`DocxWriter.java:4753`, `:3823`; the gap is computed at `:4490`, `:3600`). Google Docs **drops
space-before at the top of a page**. So page 0, which is not preceded by a break, keeps its gap, and
every continuation page lands high by it. That is why `18_displacement`'s median equals the page-first
gap, one sign, continuation pages only.

`w:pgMar w:top` is honoured at a page top by Google. Measured 22 Nov on `bank-statement-5-pages`:
pages 1-4 went from -59.5 pt to -4.3 pt, page count unchanged at 5.

**The patch** sets `w:pgMar w:top` to the document's page-first gap `G` (twips) and subtracts `G` from
every page-first paragraph's `w:before`, floored at 0. `flowTw`, `budgetTw`, `resync` and `fitPage` are
untouched, so the engine's page-breaking decisions do not move: only the bytes change.

## Measured, Google, before vs after

Before = `benchmarks/gverify/<doc>.json` at HEAD (engine `981ff1fa35e2cf67`). After = a fresh Google
render of the patched `.docx`, exported from Drive and scored by `gvbatch.py` on engine `771234e164611275`.

| document | before | after | moved | failing after |
|---|---|---|---|---|
| `412_page_labels_roman` | 40/42 | **42/42** | +2, **CLEAN** | — |
| `602_bookmarked_annual_report` | 38/42 | **41/42** | +3 | `52_outline` |
| `bank-statement-5-pages` | 42/47 | **46/47** | +4 | `18_displacement` |
| `324_loan_amortisation_schedule` | 44/47 | **46/47** | +2 | `18_displacement` |

**Nothing got worse.** Not one check that passed before fails after, on any of the four. `27_text_off_page`
was fixed on all four (the gap was pushing text off the page bottom), `04_chars_missing`,
`25_invisible_text`, `44_header_footer` and `59_shape_anchor` were fixed on the documents that had them.

## The residual, measured with `dy.py` on the same renders

- `412` — dy **+2.2 to +2.5 pt on every page, page 0 through 4**. Uniform. No per-page drift remains; the
  residual is a constant 2.3 pt and it passes.
- `bank-statement-5-pages` — dy **-11.25 pt, identical on page 0 and on every continuation page**. A
  constant offset that does not depend on the page break is not the page-top gap: it is inside the table
  (row height / cell top inset). Page 3 additionally reads -28.90 pt on one row.
- `324_loan_amortisation_schedule` — dy **+357.83 pt on all 6 pages including page 0**, on the run
  `38,620.00`, which occurs six times in the document. Uniform on page 0 means it is not displacement;
  it is the matcher pairing a run with the wrong occurrence.

**So the class splits in three, and only the first part is now closed:**

1. page-top gap dropped at a page break — **fixed** by this patch (uniform per-page dy is gone).
2. table-internal vertical offset — `bank-statement-5-pages` residual -11.25 pt on every page.
3. `18_displacement`'s matcher pairing a repeated run with the wrong occurrence — `324`, 357.83 pt,
   present on page 0 too.

## Why it was not committed

`regress.py --check` on this tree: *"ENGINE CHANGED (docx): table measured on 9e2b3e4d7869ea86, the tree
is 771234e164611275. An unmeasured change is not a pass."* The patch changes bytes in **197 of 213**
documents (every document whose pages carry a top gap), and 197 documents were not re-measured in
Google inside this slot. Four documents is enough to prove the mechanism and to show it does not
regress those four; it is not enough to authorise a 197-document change.

## What the next run does with it

    git apply tools/p2w-bench/patches/18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch
    python3 tools/p2w-bench/corpus-slice.py            # repeat until DONE (213 docs, ~11 s each)
    bash tools/p2w-bench/refresh-all.sh                # Google: publish, convert, render, score
    python3 tools/p2w-bench/regress.py --check && bash tools/commit-gate.sh

Known identity break to watch: `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled`
carry page-first gaps of `[767, 686, 696, 686, 686, 0, 696, 1100]` twips — five distinct values, one of
them 0. `G` is the minimum, so the page written with `before=0` cannot give up `G` and that page keeps its
2.2 pt break. Excluding those two, the identity `pgMar + before_after == before_before` holds exactly on
**211 of 213** documents, every page break, to the twip.
