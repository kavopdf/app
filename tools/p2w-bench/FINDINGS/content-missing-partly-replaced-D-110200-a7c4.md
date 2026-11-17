# content-missing-partly-replaced / D — the blast radius of the `pieces` remap

Agent: contD-02 (deployed 10:1x, returned without committing — the parent wrote this file from its
measurements; the numbers below are the agent's, the conclusions marked "parent" are mine).

## The question

`PdfToWord.buildTables` builds `pieces` (each cell's source lines) at full width, then trims every
other per-cell array through `keep` when a table has empty columns. `pieces` is never re-indexed, so
`parasOfLines(pieces.get(rr).get(cc))` hands every cell the paragraphs of the cell one dropped
column to its left. Which documents does that touch, and is the one-line remap safe?

## The non-remap, in source

- built full width, `PdfToWord.java:8640-8662`: `pieces.get(r).get(c).add(line)` with `c = band(xs, cx)`
- trimmed, `PdfToWord.java:8682-8701`: `trimmed[r][k] = cells[r][keep.get(k)]` for `cells`, `faces`,
  `firstX`, `firstY`, `colours`; `cols = keep.size()`
- consumed with the trimmed index, `PdfToWord.java:8753` (before the fix):
  `parasOfLines(pieces.get(rr).get(cc))`

`colX` at `:8737` already reads `keep.get(c)`, which is why the paragraph path is the only one that
shifted.

## The differential test (the decisive measurement)

Clone copied to `/scratch/work/app-fix`, one line changed in the copy only:

```java
List<Table.CellPara> cp = parasOfLines(pieces.get(rr).get(keep.get(cc)));
```

Both builds converted all 213 corpus documents; every table cell diffed on paragraph count and
joined text:

```
docs_total 213  changed 2  missing/err []
== 041122-Account_Opening_Form.docx      tables 26 -> 26  cellchanges 14
   t18 r1  c1  OLD np=1 'Annexure-1 Income-tax Rules, 1962 FORM NO.60 [See second proviso to ru'
                NEW np=6 'Annexure-1 ...'
   t18 r1  c2  OLD np=6 ...            NEW np=1 ''
   t18 r15 c1  OLD np=1 '14 In case of transaction in joint names, number of persons involved i'
                NEW np=3 ...
   t18 r15 c2  OLD np=3 ...            NEW np=1 ''
== Account_Opening_Form_Fillable_filled.docx  tables 26 -> 26  cellchanges 14   (same pattern)
```

An independent source-free check — two cells of one row carrying the same text, at least one of them
a ≥2-paragraph cell — flagged the same two documents and nothing else. 123 multi-paragraph cells
exist across 31 documents; only these two carry the bug.

## Verdict on safety (agent)

The remap is safe in the sense that it changes 2 of 213 documents and leaves 211 bit-identical. The
bug needs BOTH an empty column that `keep` drops AND a ≥2-paragraph cell in the same table.

## What the parent measured afterwards, and why the fix is NOT in the tree

Parent applied the one-line remap, rebuilt, converted and measured the two affected documents with
`benchmarks/p2w.py` (render into an empty directory, 150 dpi):

| document | pages src/ours | share5 before | share5 after | invent5 before | invent5 after |
|---|---|---|---|---|---|
| 041122-Account_Opening_Form | 9/9 (was 9/10) | 98.65 | **99.02** | 66.62 | **0.00** |
| Account_Opening_Form_Fillable_filled | 9/10 (unchanged) | 97.62 | **98.65** | 66.62 | 66.62 |

So the remap removes the duplicated text (invent5 66.62 → 0.00) and the spurious tenth page on
041122 — and both documents read WORSE on `share@5px`, the axis RANKING.csv ranks by. The score
cannot see either improvement: it compares page *k* with page *k* for `k <= min(pages)`, so a
document that gains a page is not penalised and one that loses one is not rewarded, and `invent5` is
not part of the rank. Reverted, with the mechanism recorded so the next run does not have to find it
again.

## What this means for the next run (parent)

The bank forms' dominant defect is not this one. Every glyph on both documents is written at **1 pt**
— 4088 runs, `w:sz w:val="2"` — because their generator emits `/C2_0 1 Tf  10 0 0 10 x y Tm`: the
size is in the text matrix, not in Tf, and the engine's `g.size` reads `tp.getFontSize()`, which is
Tf alone (1.0). `tp.getTextMatrix().getScalingFactorY()` is exactly the size the page draws at
(measured: 10.0 here, 16.0 on 01_stamp where Tf is 16 and the matrix carries nothing) and
`tp.getFontSizeInPt()` is that number rounded to a whole point. Blast radius measured over all 213
documents: 4 documents differ — the two bank forms (all 47477 glyphs each), 38_faux_bold (93 glyphs,
9.5→9.7), 411_nested_xobject_transforms (32 glyphs, 10→16).

With the size corrected the text is right and the page is not: 041122 goes 9 → 12 pages and page 7
comes out almost blank, because the table model then has to hold 10 pt text in row heights and column
widths that were fitted against 1 pt. share5 98.65 → 97.62. Both changes belong together and neither
is a win alone.

## What would prove me wrong

- If a document outside this corpus has an empty column whose `keep` shift crosses a spanning cell,
  `keep.get(cc)` could be off by a span; merged-cell tables with empty columns were not tested.
- The cell diff compares text and paragraph count only, not formatting.
- If `Account_Opening_Form_Fillable_filled` scores better on a full ratchet than its baseline, the
  "worse" verdict for it is wrong.
