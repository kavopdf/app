# content-present-partly-displaced - a fill-only shading rectangle is a cell edge, and dropping it is worse

**Run:** 19 Nov 2026, slot 18:00 IST. **Class:** `content-present-partly-displaced`, 18 OPEN documents.
**Document:** `75_merged_header_cell_three_columns`, share@5px 27.31, max 22.08 pt.

## The hypothesis this tested

The subagent's finding (`content-present-partly-displaced-mergedheader-130426-4bd9.md`) says the
table's cells are cut from the page's drawing primitives rather than its row lattice, and that
`RuleCollector.appendRectangle` keeps all four sides of every `re` whether it is stroked or merely
filled. On this page the shaded header band `394 681.89 124 34 re f` is the only closed rectangle in
header row 1, so `tableFromCells` read it as a merge (`spanC=2`), and the shaded band plus the row
below it became one two-row cell (`spanR=2`, which nothing reads).

The reading of the code is right. `stampPathRules(false)` already gives every rule added by a
fill-only path the stroke from `bandFillStroke()`, which is **null** for anything that is not a
hairline band. `edgeStroke()` (`PdfToWord:7441`) and `innerStroke()` (`:7522`) both read null as
"not drawn on the page". The loop that builds the table's `Edge` list did not.

## The change

`PdfToWord:1275-1285` - skip a rule whose `hStrokeAt(i)` / `vStrokeAt(i)` is null when building
`edges`, so a fill-only shading rectangle cannot close a cell. Built (46 s), no compile error.

## What it measured

    before   share5 27.31   max 22.08   problem content-present-partly-displaced   1 page
    after    share5 46.58   max 48.96   problem content-missing-partly-replaced    2 pages

**Worse in every axis, and the table splits across two pages.** Reverted; the tree is clean at
`4147d54`.

## Why it is worse - the part that matters

The shading band's four sides are not spurious. On this page the separator that would close
header row 1 (`x=456`) is only drawn from `y=143` down, and the `y=160` rule under
Services / Km operated / Revenue is never drawn at all. The filled band is therefore the **only**
thing that closes those cells. Removing it does not remove a false merge - it removes the table's
structure, the ruled pass finds nothing, and the row pass builds a different, larger table that
overflows the page.

So the engine's use of a fill as a cell edge is load-bearing and cannot simply be switched off.
`bandFillStroke()` already distinguishes a hairline fill from a shading fill, and that distinction
is correct for *painting* the rule - but it is the wrong distinction for *closing* a cell.

## The fix this points at, with the numbers

Neither half alone works:

1. **Cells from the lattice, with the rectangle as evidence of a merge.** The row and column bands
   exist independently of the shading; the shaded rectangle should mark that a cell spans the bands
   it covers, not define the cell.
2. **`w:vMerge`.** `spanR` is computed at `PdfToWord:7950` and **read by nothing** (`grep -rn spanR`
   returns the declaration, a comment and the write). `DocxWriter` consumes `spanC` only, which is
   why the .docx carries 3 `w:gridSpan` and 0 `w:vMerge` for a table whose source merges three cells
   vertically across two header rows. That is the half that explains the vertical damage: each data
   row's numbers are emitted in the row above its depot name, every word in the body 22.07 pt low,
   and one cell 61.20 pt out horizontally.

Doing (2) alone is the cheaper first attempt and is worth one screen: it cannot make the table
smaller, and a document with vertically merged header cells is exactly what it is for.

## Ruled out by measurement, this run

| Claim | Test | Result |
|:--|:--|:--|
| dropping fill-only rules fixes the merge | build + measure `75_merged_header_cell_three_columns` | **refuted**: 27.31 -> 46.58, 1 -> 2 pages |
| the .docx is missing `w:gridSpan` | count in `word/document.xml` | refuted - 3 present |
| the header occupies the wrong number of rows | `w:trHeight` count | refuted - 8 rows, matching the source's 2 + 6 |
| the defect is LibreOffice's | the fault is visible in `document.xml` before rendering | refuted |
| the whole class is one mechanism | see below | refuted |

## The class is not one mechanism - measured, per document

Sampled with a word-box alignment against the rendered output (dx/dy of every matched word):

| Document | share5 | What is actually wrong |
|:--|--:|:--|
| `75_merged_header_cell_three_columns` | 27.31 | two header columns welded, rows shifted by one; body 22.07 pt low |
| `bank-statement-horizontal-rules-only` | 6.89 | every word correct at the top (+0.03 pt at y108) and +5.77 pt at y421; source row pitch exactly 18.4 pt, ours 18.74 - a constant ~0.34 pt per positioned row that accumulates down the page |
| `374_org_chart` | 5.92 | top of the page -0.18 pt; the bottom box row +4.48 pt and the footer +2.91 pt |
| `payslip-label-left-amount-right` | 5.59 | a block of rows a constant -3.45 pt high; right-aligned amounts out by 3-13 pt horizontally |

Three different mechanisms in four documents. A single patch cannot clear this class, and the
brief's rule - take the class with the most documents because one mechanism fixed once clears every
document under it - does not hold for this one.

## What would prove this note wrong

A change that drops fill-only rules and still keeps `75_merged_header_cell_three_columns` at one page
and below 27.31. That would mean the page has another closing rule I have not found.
