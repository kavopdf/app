# The cell carry-on guard clears t12 on two documents and costs real characters on two others

**25 Nov 2026, fixer slot 20:56-22:26 IST. Engine change built, measured on all four documents whose
bytes it moved, and REVERTED. Nothing is committed to `app/`.**

## What was proposed

`t12_word_invention` fails three documents. Two of them are the same form:

   041122-Account_Opening_Form            14 invented characters
   Account_Opening_Form_Fillable_filled   14 invented characters
   600_reviewed_invoice_with_annotations  83 invented characters

The check (`verify_txt.py:1441-1452`) is a **character multiset difference**: `txt − src` over every
non-whitespace character, no token, no case folding. One surplus `Y` is a failure.

For the two forms the surplus is one `Y`, and the cause is a **welding artifact** in
`PdfToWord.java:7904-7908` (`tableFromCells`). The carry-on rule pulls a glyph into the previous cell
when it sits within `max(9 pt, 1.1 × size)` of the previous glyph's end, **with no check that the glyph
still belongs to the table at all**. On `041122-Account_Opening_Form` the date-field row
`D D M M Y Y Y Y` is the last cell, the phrase `(Authorised signatory)` begins at x=153.46, and the
table's right edge is x=145.0 — its centre is outside every cell so the hit test misses it, and every
following glyph chains on. The last cell's text becomes `(Authorised signatory)Y`.

## What was built and measured

One clause on the carry-on condition, two variants:

| variant | condition added | files changed |
|---|---|---|
| **broad** | `g.x <= group.get(prevCell)[2] + 2f` — the glyph must still start inside the cell it is carried into | `PdfToWord.java` |
| **narrow** | `g.x <= group.get(ncells - 1)[2] + 2f` — the glyph must still be inside the table | `PdfToWord.java` |

Both compiled clean and converted all 213 documents (`corpus-slice.py`, engine `0399b504809b1879`).

**Scope: the change moved 4 of 213 documents' bytes**, from `corpus-changed.py --record`/`--list` —
the two forms, plus `itr-computation-with-slab-table` and `mutual-fund-statement`. The other 209 are
byte-identical, so their scores cannot have moved.

### txt — measured, better, and kept in the numbers

`txt_rank.py --all`, 213 scored, compared against the committed `RANKING-TXT.csv`:

| | before | after |
|:--|--:|--:|
| documents clean (every applicable check) | 204 | **204** |
| documents failing t12 | **3** | **1** |
| documents worse | — | **0** |
| documents better | — | **2** |

    041122-Account_Opening_Form           t06 t09 t12  ->  t06 t09
    Account_Opening_Form_Fillable_filled  t06 t09 t12  ->  t06 t09

Both documents still fail `t06_encoding` and `t09_page_furniture`, so **no document became clean** —
the count stays 204 of 213. The t12 construct is real and the patch clears it exactly as predicted.

### docx — measured, and the reason this does not land

`benchmarks/p2w.py:measure_doc` on the four changed documents, against their committed
`RANKING.csv` rows:

| document | share@5px | max_pt | text_recall | chars_missing | order_share |
|:--|:--|:--|:--|:--|:--|
| `041122-Account_Opening_Form` | 98.65 → 98.65 | 937.92 → 937.92 | 99.68 → 99.68 | 127 → 127 | 79.11 → 79.11 |
| `Account_Opening_Form_Fillable_filled` | 97.62 → 97.62 | 358.08 → 358.08 | 99.67 → 99.67 | 131 → 131 | 78.94 → 78.94 |
| `itr-computation-with-slab-table` | **42.33 → 43.01** | **15.36 → 14.40** | **100.00 → 99.88** | **0 → 2** | 95.50 → 95.50 |
| `mutual-fund-statement` | 0.21 → 0.21 | 5.76 → 5.76 | **100.00 → 99.91** | **0 → 3** | **99.49 → 99.36** |

The two forms are visually untouched — the invented `Y` was never printed by the source, so removing
it moves no ink. That is the good half.

The other two are a **content regression**: `itr-computation-with-slab-table` loses 2 characters and
`mutual-fund-statement` loses 3, both from a baseline of `chars_missing = 0`, and
`mutual-fund-statement`'s `order_share` falls 0.13. Those glyphs were legitimately carried into a cell
and the guard moved them out of it. A document at `chars_missing = 0` going to 3 is worse by the
project's own rule, so **the change does not land** — non-negotiable 3.

## The narrowing that was tried and did not help

The obvious containment was to block the carry only past the **table's** right edge rather than the
cell's, leaving intra-table overflow carries alone. It is the same four documents and it measured
**identical numbers to the broad guard** — so the characters lost on `itr` and `mutual-fund` are also
carried from beyond the table's right edge. The carry-out-of-table behaviour is load-bearing for those
two documents; it is not separable from the t12 fix by geometry alone.

## What this rules out, and what is left

**Ruled out:** the carry-on distance test is not the discriminator. Both `g.x <= cell.right + 2` and
`g.x <= table.right + 2` produce the same four-document set and the same verdict, so the glyphs on
`itr` and `mutual-fund` sit beyond the table edge exactly like the `(Authorised signatory)` glyphs do.

**The remaining discriminator is the glyph's own semantics, not its position.** The `Y` on the forms is
part of a *date-field glyph run* (`D D M M Y Y Y Y`) whose other members are already in that cell, and
the phrase welded after it is a *different text line at a different baseline offset*. The characters
lost on `itr`/`mutual-fund` are plausibly the same line of the same cell continuing. A next run should
print, for each of the four documents, the exact glyph that changes cell and its `(x, y, size, text)`
plus the text already in the destination cell — that is a two-minute probe and it decides between
"same text line" and "different text line" without another full build.

**`600_reviewed_invoice_with_annotations` is not fixed by this and must not be.** Its 83 invented
characters are the annotation `/Contents` hoist at `PdfToWord.java:956-961`, and the fix that clears
them is to filter `annotationRuns` through `annotationContentsOf` (`:2475`, currently **dead code with
no call site**). That fix was specified and measured on this document, and **rejected here**: the
comment at `PdfToWord.java:2352-2356` records that `50_annotation_text` — a *Google* check — asks for
an annotation's `/Contents` string exactly, and that suppressing the hoist deletes the only copy of
`Approved`. So the txt check and the Google check disagree about whether a note's and a stamp's
`/Contents` belong in the document. **That is a measurement conflict to resolve, not a patch to land**:
the next run should read `50_annotation_text` on this document in Google before touching `:956`.

## The two patches, verbatim, so this is not re-derived

Broad (the one measured here), at `PdfToWord.java:7904`:

```java
if (hit < 0 && prevCell >= 0 && Math.abs(g.y - prevY) <= 0.5f
        && g.x >= prevRight - 1f
        && g.x <= group.get(prevCell)[2] + 2f                 // broad: cell's own right edge
        && g.x - prevRight <= Math.max(9f, Math.max(g.size, prevSize) * 1.1f)) {
    hit = prevCell;
}
```

Narrow: replace `group.get(prevCell)[2]` with `group.get(ncells - 1)[2]`.

Both are reverted from the tree; `git diff app/` is empty.
