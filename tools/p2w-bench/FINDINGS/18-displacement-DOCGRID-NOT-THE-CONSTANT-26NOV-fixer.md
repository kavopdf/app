# The 2.65 pt page constant is not the document grid either

**26 Nov 2026, fixer slot 10:54.** One document, one construct, measured in Google.

## What I believed

`31_times_body_arial_headings` carries every run on its single page at a **uniform +2.65 pt** (sd 0.71,
n = 29) that does not scale with the type - see
`18-displacement-TEN-SOLO-DOCS-AND-THE-HAIRLINE-REFUTED-26NOV-fixer.md`. A constant added to every line
of a page, independent of size, is a page-level term. The section carries
`<w:docGrid w:linePitch="360"/>` - an 18 pt document grid - and Google is known to apply a document
grid where Word does not. If Google snapped each line into the grid, every line would move by the same
amount and the amount would be the same for every type size. That is the signature exactly.

## What I measured

The construct is one element in `word/document.xml`, so it was tested without touching the engine: the
emitted `.docx` was unzipped, `<w:docGrid w:linePitch="360"/>` removed from the only `w:sectPr`,
rezip­ped, and put through the same Drive convert/export/`gverify.py --collect` as the unmodified file.

| | with `w:docGrid` | docGrid removed |
|:--|--:|--:|
| Google checks | 41/42 | 41/42 |
| failing | `18_displacement` | `18_displacement` |
| med_dy | 2.6 | **2.6** |
| worst_dy | 3.5 | **3.5** |
| runs matched | 29 | 29 |
| export md5 | 8a002ed5… | 1db1a76d… (different bytes, so the change did reach Google) |

**Identical to 0.1 pt on both statistics.** The grid is not the constant.

## What is now true

1. `w:docGrid` can be eliminated as the cause of the page-level constant. Do not spend a run on it.
2. Three candidates are now refuted by measurement (page geometry, the docGrid, `lineRule=auto`) and
   one by arithmetic (`LINE_BASE`, because the offset does not scale with size). What is left of the
   page-top family is the **first paragraph's own box** - `w:before="1230"` (61.5 pt) with a
   `w:line="13"` exact box - which is worth 0.18 pt of the 2.65 on the engine's own numbers, so the
   constant is not fully explained by any of them and the next run should not assume it is a
   construct at all.
3. The next step I would take is the one I did not: pair the source PDF and the export **per page
   origin** - `page.rect.y0` and the first block's top on both - on three or four of the ten solo
   documents, and see whether the constant is the same number across documents. If it is one number
   corpus-wide, it is a page-origin term and it is worth 8 documents; if it differs per document, it
   is not one defect and the ten should be worked separately.

## The ledger was restored

`benchmarks/gverify/31_times_body_arial_headings.json` was overwritten by the probe and re-collected
from the unmodified build's export afterwards: 41/42, `18_displacement`, med_dy 2.6, worst_dy 3.5,
engine `a4d8fca469bba636` - identical to before the experiment except the timestamp. The Google Doc the
probe created in the verify folder was deleted and the staged copy under `/scratch/output` removed.
