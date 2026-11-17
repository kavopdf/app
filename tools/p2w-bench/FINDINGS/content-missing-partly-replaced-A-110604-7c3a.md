# content-missing-partly-replaced / A - does DocxWriter consume `Table.paras` for the welded cell?

Asked: for `041122-Account_Opening_Form.pdf` page 7, row 2, cell 2 of the one big table, does
       `DocxWriter` consume `Table.paras` (the per-line `CellPara` list built by `parasOfLines`)?
       If not, which code decides how many `w:p` are emitted inside that cell and what `w:ind`
       they carry?

Engine at HEAD `e2ed77322f752b4930420cea32e6480395bacaa0` (branch main). Engine sources NOT
modified: the repo clone was used read-only, instrumentation was compiled from a **copy** of the
engine under `/scratch/work/instr/src` (same pattern the earlier finding used). Read-only
investigation plus this file.

---

## Answer in one paragraph

`DocxWriter` **does** consume `t.paras` - and it is consumed for the cell *beside* this one. The
branch is `if (cps.size() >= 2)` on `t.parasAt(r, c)` (`DocxWriter.java:6380-6381`); when it is
taken the writer emits one `w:p` per `CellPara` via `cellParaXml` and `continue`s past the
string path (`:6411-6418`). For **row 2 cell 2 that list is empty at HEAD**, so the writer falls
through to the welded-string path, whose paragraph count is decided by
`String[] cellLines = cell.split("\n", -1)` (`:6437`) and whose indent is `insetTw`
(`:6440`, written at `:6445`). The welded string for this cell contains **no `"\n"`** (the weld
at `PdfToWord.java:8652-8653` joins with a space), so the split yields exactly ONE element, ONE
`w:p`, carrying `w:ind w:left="9452"` = `insetTw` from `t.cellX`. `t.paras` is empty for that
cell not because `parasOfLines` fails but because the per-cell line list `pieces` is never
re-indexed through the empty-column trim (`PdfToWord.java:8682-8703` rebinds `cells`, `faces`,
`firstX`, `firstY`, `colours` - not `pieces`; not `sizes` either), so the loop at `:8751-8755`
reads `pieces[r][c]` with a TRIMMED column index against an UNTRIMMED list and hands the six
`CellPara`s to the cell one column to the right.

Measured, not inferred: the six paragraphs are in the file, in the wrong cell -
`r1 c2 nparas=6` (456-twip sliver), `r1 c1 nparas=1` with the welded text and `w:ind 9452`.

---

## 1. Where DocxWriter emits a cell's paragraphs, and the exact choosing condition

| what | file:line |
|---|---|
| the cell's welded string is read | `DocxWriter.java:6132` `String cell = c < row.size() ? row.get(c) : "";` |
| the cell's inset is computed once | `DocxWriter.java:6145` `int insetTw = insetTw(t, r, c, x0, edgeTw[c]);` |
| **the model's paragraphs are fetched** | `DocxWriter.java:6380` `java.util.List<PdfToWord.Table.CellPara> cps = t.parasAt(r, c);` |
| **the condition** | `DocxWriter.java:6381` `if (cps.size() >= 2) {` |
| paras branch: one `w:p` per `CellPara` | `DocxWriter.java:6401-6412` (loop at `:6401`), emit call `:6411` `cellParaXml(inner, cp, beforeTw, boxTw, pInset, cellSz);` |
| paras branch leaves before the string path | `DocxWriter.java:6417-6418` `c += span; continue;` |
| **string branch: paragraph count** | `DocxWriter.java:6437` `String[] cellLines = cell.split("\n", -1);` |
| string branch: per-line indent | `DocxWriter.java:6440` `int lineInset = li == 0 ? insetTw : 0;` |
| string branch: the `w:ind` | `DocxWriter.java:6445` `if (lineInset > 0) inner.append("<w:ind w:left=\"").append(lineInset).append("\"/>");` |
| string branch: the `w:p` and its spacing | `DocxWriter.java:6442-6444` |

So the choice is exactly: **`t.parasAt(r, c).size() >= 2` -> N `w:p` from `t.paras`;
otherwise -> `cell.split("\n", -1).length` `w:p` from the welded string, indented by `insetTw` on
the first (here: only) paragraph.** There is no third path for a table cell.

Measured on the emitted file (engine built from HEAD, `java ConvertAll` on the single PDF,
`word/document.xml` split on `<w:br w:type="page"/>`, page 7's only table, `tblGrid` 363 / 10636
/ 456 twips, 24 rows):

```
row 1 (0-based) trPr <w:trHeight w:val="1682" w:hRule="atLeast"/><w:cantSplit/>
  c0 nparas=1  ind=109    '1'                                    <- next row shown for scale
  c1 nparas=1  ind=9452   'Annexure-1 Income-tax Rules, 1962 FORM NO.60 [See second proviso
                           to rule 114B] Form for declaration ... rule 114B'   <- WELDED CELL
  c2 nparas=6  ind=None   'Annexure-1' | 'Income-tax Rules, 1962' | 'FORM NO.60' | ...
                           tcPr carries <w:vAlign w:val="top"/>    <- the paras branch's own marker
```

`w:vAlign w:val="top"` is written only inside the `cps.size() >= 2` branch
(`DocxWriter.java:6400`), so cell 3 of that row proves the branch ran and that
`t.paras` was consumed - for the wrong cell. The welded cell's raw XML (single `w:p`, no
`w:br`, no newline in the text):

```
<w:tc><w:tcPr><w:tcW w:w="10636" w:type="dxa"/></w:tcPr><w:p><w:pPr>
  <w:pStyle w:val="TableText"/><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0" w:after="0"
             w:line="200" w:lineRule="exact"/><w:ind w:left="9452"/></w:pPr>
  <w:r><w:rPr><w:rFonts w:ascii="Effra" .../><w:b/><w:color w:val="2A2076"/></w:rPr>
  <w:t xml:space="preserve">Annexure-1 Income-tax Rules, 1962 FORM NO.60 ...</w:t></w:r></w:p></w:tc>
```

`w:p` count 1, `w:br` count 0, no newline character in the run text - i.e. `cell.split("\n",-1)`
returned one element.

## 2. Why `parasOfLines`' output does not reach that cell

`parasOfLines` is not the failing part:

* `PdfToWord.java:7998` signature; `:8000` `if (ls == null || ls.size() < 2) return none;`;
  `:8026` `if (out.size() < 2) return none;` - it needs two lines on two baselines.
* attach guard: `PdfToWord.java:8753-8754`
  `List<Table.CellPara> cp = parasOfLines(pieces.get(rr).get(cc)); if (cp.size() >= 2) t.paras.get(rr).get(cc).addAll(cp);`
* `t.paras` is allocated with the TRIMMED column count by `t.shapeParas(rows, cols)` at
  `PdfToWord.java:8750` (`Table#shapeParas`, `:365-372`).

The desync, all inside `buildTables`' ruled-grid pass:

* `pieces` is filled with the ORIGINAL column index: `PdfToWord.java:8640-8651`
  (allocated `cols` wide at `:8640-8645`, `pieces.get(r).get(c).add(line);` at `:8651`).
* the weld into one string, same loop: `PdfToWord.java:8652-8653`
  `cells[r][c] = cells[r][c] == null ? line.text.trim() : cells[r][c] + " " + line.text.trim();`
  - a SPACE, never a newline.
* `keep` is built at `PdfToWord.java:8672-8680`; when `keep.size() < cols` (`:8682`) exactly five
  per-cell arrays are re-indexed through `keep` and rebound - `cells`, `faces`, `firstX`,
  `firstY`, `colours` (`:8697-8701`) - and `cols = keep.size()` (`:8702`). **`pieces` is not
  remapped and not rebound**, and `sizes` is not either (see observation 3 below; `:8736`
  reads `sizes[r][c]` with the trimmed `c`).
* `colX` *is* remapped (`:8719-8722` `int src = c < keep.size() ? keep.get(c) : c;`), which is
  why the widths and `w:ind` are right while the paragraphs are not.

For this table the trim drops one column: `keep == [1, 2, 3]`, `cols` 4 -> 3, `pieces` still 4
wide. Trimmed cell 1 is original column 2, but the loop reads `pieces[1][1]`, which is the empty
original column 1.

Measured (instrumented copy, printing `pieces.get(rr).get(cc)` = "piecesHere",
`pieces.get(rr).get(keep.get(cc))` = "piecesOwn", and `t.paras` after the attach):

```
DBGTRIM top=0.0 rows=24 colsAfter=3 keep=[1, 2, 3] piecesWidth=4
DBGCELL r1 c0 origCol=1 piecesHere=0 piecesOwn=0 parasOfLines=0 cellX=NaN      welded=
DBGCELL r1 c1 origCol=2 piecesHere=0 piecesOwn=6 parasOfLines=0 cellX=513.5645 welded=Annexure-1 Income-tax Rules, 1962 FORM N
DBGCELL r1 c1 t.paras=0
DBGCELL r1 c2 origCol=3 piecesHere=6 piecesOwn=0 parasOfLines=6 cellX=NaN      welded=
DBGCELL r1 c2 t.paras=6
```

(printed twice per page - `buildTables` runs on `rawLines` and again on `lines`,
`PdfToWord.java:1016` and `:1270`; only one table reaches the .docx.)

So: `parasOfLines` would return 6 for this cell's six lines (it does, for the array entry one
column to the right), and the `cp.size() >= 2` guard would pass - the list is simply looked up
in the wrong place. `cellX[1][1] = 513.5645` is the welded cell's own first-line x and is
correctly carried, which is why the indent is right and only the paragraph split is missing.

## 3. The exact code that turns `t.cellX` into `w:ind`, and what governs the wrap width

```
DocxWriter.java:6851  private static int insetTw(PdfToWord.Table t, int r, int c, float x0, long edgeTw) {
DocxWriter.java:6852      if (r >= t.cellX.size()) return 0;
DocxWriter.java:6854      List<Float> xs = t.cellX.get(r);
DocxWriter.java:6855      if (c >= xs.size()) return 0;
DocxWriter.java:6856      Float textX = xs.get(c);
DocxWriter.java:6857      if (textX == null || textX.isNaN()) return 0;
DocxWriter.java:6858      double leftPt = x0 + edgeTw / TWIPS_PER_PT;
DocxWriter.java:6859      int tw = (int) Math.round((textX - leftPt) * TWIPS_PER_PT);
DocxWriter.java:6860      return Math.max(0, tw);
```

Callers:
* string/welded path: `DocxWriter.java:6145` (computed once per cell), used at `:6440`
  (`lineInset = li == 0 ? insetTw : 0`) and written at `:6445`.
* paras path: `DocxWriter.java:6409-6410` - `pInset = cp.indentPt` when the `CellPara` measured
  one, else `insetTw`; written inside `cellParaXml` at `DocxWriter.java:6702`
  `if (insetTw > 0) inner.append("<w:ind w:left=\"").append(insetTw).append("\"/>");`

`t.cellX` is filled at `PdfToWord.java:8661` (`firstX[r][c] = visibleX(line.glyphs, line.x)`, on
the FIRST line only - `if (Float.isNaN(firstX[r][c]))`), carried per row at `:8746` (`t.cellX.add(rowXs)`), and read back
by the writer through `Table#cellX` only - nothing else writes a cell indent.

**Is the welded paragraph's wrap width governed by that `w:ind` alone? Yes, for this cell.** In
the emitted file the only width terms are:

* `w:tblW 11455`, `w:tblInd 456`, `w:tblLayout w:type="fixed"` (`DocxWriter.java:2021-2023`) and
  `w:tblCellMar` with all four margins `0` (`DocxWriter.java:2024-2027`);
* the cell's `w:tcW 10636` - no `w:tcMar` on the cell;
* the paragraph's `w:ind w:left="9452"`; `w:spacing ... w:line="200" w:lineRule="exact"`;
* the `TableText` style carries only `spacing before/after 0` and `sz 20` - **no `w:ind`**.

So usable width = 10636 - 9452 = 1184 twips = 59.2 pt of a 531.8 pt cell. The `w:line="200"`
(10 pt exact) comes from the row pitch, not from the cell: `cellSz` is `NaN` for this cell
(`DocxWriter.java:6266-6267` reads `t.sizes` - see observation 3) so both `cellSz > 0f` branches
are skipped and `cellBoxTw` stays at `rowLineTw` (`DocxWriter.java:6290-6297`).

Measured in the render (LibreOffice, this .docx): that one paragraph lays out as **28 lines at
10.0 pt, first baseline y 23.4, last 293.4, pitch 10.0 = 280 pt of content** in a row whose
`w:trHeight` is 1682 twips = **84.1 pt**. Note this corrects the handoff's "27 lines / 270 pt":
the count is 28 and the content height 280 pt (all 28 line starts are at x0 = 513.9, the same x
as the welded paragraph's first line - the whole block starts at the right place and then wraps
into a 59.2 pt column). The rendered file is **10 pages against the source's 9**.

## 4. What I ruled out, and what would prove me wrong

Ruled out, each with the observation that excludes it:

* **(a) "DocxWriter ignores `t.paras`."** False. `DocxWriter.java:6380-6418` takes
  `t.parasAt(r, c)` and, at `size() >= 2`, emits one `w:p` per `CellPara` and `continue`s. Cell 3
  of row 2 in the shipped .docx is six `w:p` with `<w:vAlign w:val="top"/>` (written only in
  that branch, `:6400`) and per-line `w:before` 0 / 246 / 216 / 216 ... that only `cellParaXml`
  can produce. `parasAt` itself (`PdfToWord.java:346-353`) is a plain bounds-checked getter.
* **(b) "`parasOfLines` returns < 2 for this cell."** False. Instrumented: `parasOfLines=6` for
  `pieces[1][2]`, the welded cell's own column. The guard at `:8000`/`:8026` is not the block.
* **(c) "`band()`/column assignment lost or misrouted the six lines."** False. `pieces[1][2]`
  holds exactly 6 lines and `cells[1][2]` holds the same six welded, so the lines were assigned
  to the right original column; the error is downstream, in which `pieces` entry the attach loop
  reads.
* **(d) "The writer's one-`w:p`-per-`\n` code is what splits a welded cell."** It cannot fire
  here: `cell.split("\n", -1)` at `:6437` yields one element for this cell (measured: 1 `w:p`,
  0 `w:br`, no newline in the text). This confirms the previous attempt's own report that the
  change was a no-op on this document - it was a no-op because the weld uses spaces
  (`PdfToWord.java:8653`), not because the writer ignores lines.
* **(e) "Something else sets the indent."** No `w:tcMar`, `w:tblCellMar` all zero
  (`DocxWriter.java:2024-2027`), `w:tblLayout` fixed, `TableText` has no `w:ind`; the only
  indent in the cell is `:6445` from `insetTw` (`:6851`).
* **Not the fit guard / `shaveToFit` / `w:cantSplit` question.** Out of scope here; the row
  height (`w:trHeight 1682`, `w:cantSplit`, `DocxWriter.java:6123-6124`) is written before the
  cell content and is unchanged by anything in this file.

Evidence that would prove me wrong:

* If a HEAD run printed `t.paras[r1][c1] == 6` (or the shipped cell 2 carried >1 `w:p`), then
  the paras path *does* reach this cell and the `pieces`/`keep` desync is not the operative
  cause. Measured: `t.paras=0` and 1 `w:p`.
* If `keep` were the identity for this table (`colsBeforeTrim == colsAfterTrim`, i.e. no trim),
  there would be no index shift. Measured `colsAfter=3` from 4, `keep=[1,2,3]`, `piecesWidth=4`.
* If `pieces[1][2]` held 0 lines while the six sat in `pieces[1][3]`, then `band()` really did
  misroute the lines and this file is wrong. Measured the opposite (`piecesOwn=6` at origCol 2).
* If the cell's `w:ind` were not 9452, or `w:tblCellMar`/`w:tcMar`/style carried a non-zero
  width term, then the wrap width would not be `ind` alone. Measured: 9452, all margins 0, style
  has no ind.

---

## Side observations (measured, outside the question - do not treat as conclusions)

1. **The wrap count is 28 lines / 280 pt, not 27 / 270** (render, this run). Same mechanism, one
   more line.
2. **`sizes` is a third un-remapped per-cell array.** The trim rebinds only
   `cells/faces/firstX/firstY/colours` (`PdfToWord.java:8697-8701`) but `:8736` reads
   `sizes[r][c]` with the trimmed `c`. Measured: `sizes[1][1]=NaN`, `sizes[1][2]=1.0`, so
   `cellSz` is `NaN` for the welded cell (`DocxWriter.java:6266-6267`) - which is why its
   `w:p` carries **no `w:sz`** and takes `TableText`'s 10 pt, and why its box fell back to the
   row pitch (`:6290-6297`).
3. **Every `CellPara` in this document carries `size = 1.0`, `indentPt = NaN`** (instrumented:
   `DBGCP r1 c2 sz=1.0/NaN` x6). The six paragraphs therefore come out as
   `<w:sz w:val="2"/>` with `w:line="24"` (`cellParaXml`, `DocxWriter.java:6698-6721`) - 1 pt
   text - which is what the render shows at x0 573.1. `sizeOf` (`PdfToWord.java:7869-7877`)
   returns 1.0 because the glyphs themselves measure 1.0 here.
4. **The whole document is emitted at 1 pt at HEAD**, which is bigger than the cell question:
   all 4088 `<w:sz>` elements in `word/document.xml` are `w:val="2"`, and the LibreOffice render
   of the .docx has 46,926 characters at size 1.0 pt against a source whose sizes are 6.0-10.0
   (e.g. the page-1 heading `ACCOUNT OPENING FORM ...` renders with bbox height 1.0 pt). The
   same is true of the only other corpus PDF in this clone
   (`Account_Opening_Form_Fillable_filled.pdf`: 4088 x `sz 2`). I did **not** investigate the
   cause and am not claiming one - the plausible reading is a text-size/CTM-scale defect in the
   glyph-size path, and it should be checked on a fresh run before anything is built on it.
   Consequence for a `pieces` remap: remapping alone would move the six paragraphs into cell 2
   but they would still be 1 pt, because `cp.size` is 1.0 independently of the column shift.

## How this was measured (reproducible, engine untouched)

```
git clone https://github.com/kavopdf/app.git /scratch/work/fix      # HEAD e2ed773
cd /scratch/work/fix && bash tools/p2w-bench/build-engine.sh        # fetches JDK + PDFBox, builds (37 s)
cp benchmarks/realworld/041122-Account_Opening_Form.pdf /scratch/work/one/
E=/scratch/work/fix/tools/engine-verify
CP="$E/out:$E/libs/aar/classes.jar:$E/libs/aar/assets:$E/libs/bcprov.jar:$E/libs/bcpkix.jar:$E/libs/bcutil.jar"
cd $E && java -Xmx700m -cp "$CP" ConvertAll /scratch/work/one /scratch/work/one-out
# -> 041122-Account_Opening_Form  pages=9  paragraphs=480  (docx 157442 bytes)
unzip -p /scratch/work/one-out/041122-Account_Opening_Form.docx word/document.xml
soffice --headless --convert-to pdf ...                             # -> 10 pages
```

Instrumentation: a copy of `app/src/main/java/com/kavopdf/app/engine` under
`/scratch/work/instr/src` plus `tools/engine-verify/{stubs,ConvertAll.java}`, three
`System.out.println` probes added to the copy only (after the trim at `:8702`, and inside the
attach loop at `:8751-8755`). The repo tree at `/scratch/work/fix` was never edited; the only
file this run writes to the repo is this FINDINGS file.

Confidence: high for questions 1-3 (read at file:line, observed in the shipped .docx, and the
`pieces` desync observed in an instrumented run). Observation 4 is measured but unexplained.
