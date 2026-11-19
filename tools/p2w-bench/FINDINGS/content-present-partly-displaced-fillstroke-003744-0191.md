# Can RuleCollector carry the paint operator, so a shading FILL stops being a cell separator?

**Run:** 20 Nov 2026, 00:37 IST. **Class:** `content-present-partly-displaced`.
**Document under test:** `75_merged_header_cell_three_columns` (share@5px 7.62, per `benchmarks/RANKING.csv`).
**Engine:** `app/src/main/java/com/kavopdf/app/engine/` at `6bff144` (tree `77d6cf4`), built with
`tools/p2w-bench/build-engine.sh` (35 s). **No engine code was changed.** One file is committed: this one.

Read first, as the brief required: `FINDINGS/content-present-partly-displaced-mergedheader-130426-4bd9.md`
(the mechanism), `FINDINGS/content-present-partly-displaced-mergedheader-vmerge-192600-c3f1.md` (what
`w:vMerge` did and did not fix), and `FINDINGS/content-present-partly-displaced-fillrule-131500-fixer.md`
(the refused experiment: dropping fill-only rules wholesale, 27.31 -> 46.58).

---

## Short answer to the three questions

1. **Yes - the operator is already in hand, and the provenance is already recorded.** `RuleCollector`
   is a real PDFBox operator engine (`extends PDFGraphicsStreamEngine`, `PdfToWord.java:5720`), not a
   generic path visitor. `appendRectangle` runs *before* the paint operator, and the comment there says
   so, but `resetPath()` snapshots the rule-list sizes (`5797-5800`) and `stampPathRules(stroked)`
   (`6131-6139`) rewrites each rule's stroke at the paint callback, where `S` and `f` are told apart.
   `bandFillStroke()` (`6142-6155`) already returns **null** for a shading fill, so the shading rect's
   four rules already carry `hStrokeAt/vStrokeAt == null`. The distinction exists in the model today.
   What does not exist is a **reader**: `hStrokeAt`/`vStrokeAt` are consulted only at `7462` and `7543`
   to choose a border's *weight*, and the edge list (`1296-1304`) copies geometry with no reference to
   the stroke at all.

2. **At most 25 of the 213 documents can change, and only 1 of the 25 has been measured.** Measured
   without converting the corpus (pymupdf `get_drawings()`, extractor validated against `CENSUS.csv`
   `src_drawings` on 74/74 documents): 690 fill-only non-hairline `re` rectangles corpus-wide, of which
   **446 in 26 documents** sit inside a rule lattice that can hold cells. **25 of those 26 emit at least
   one `<w:tbl>`** from the current engine. So 25 is the ceiling. 13 of the 25 have at least one fill
   edge that no stroked rule supplies, so the rule must bite there. The other 24 are **not measured**.

3. **A narrower rule exists in principle, but the two obvious text witnesses for it are refuted by
   measurement on this corpus.** "Fill contributes no separator; its extent is only a merge licence"
   is expressible and touches just **12 fills in 9 documents** (the fills that have an *open* interior
   boundary - everywhere else a stroked rule already crosses the fill, so nothing can change). Gating
   that licence on "the text inside occupies fewer bands than the rect covers" **false-splits a genuine
   merge** on `table-with-merged-cells` (share5 0.67, header really is span2 + span4). Gating it on
   "no word straddles the boundary" is **vacuous**: 0 of the 12 fills has a word straddling an open
   boundary. So the separator half is safe to state and cheap to screen; the licence half is unproven.

---

## 1. Is the paint operator available where `appendRectangle` is called?

### It is an operator engine, and the callbacks are all there

    PdfToWord.java:5720   private static final class RuleCollector extends PDFGraphicsStreamEngine
    PdfToWord.java:5778   protected void processOperator(Operator operator, List<COSBase> arguments)
    PdfToWord.java:6266   public void appendRectangle(PointF p0, PointF p1, PointF p2, PointF p3)
    PdfToWord.java:6704   public void strokePath()
    PdfToWord.java:6713   public void fillPath(android.graphics.Path.FillType fillType)
    PdfToWord.java:6722   public void fillAndStrokePath(android.graphics.Path.FillType fillType)

`PDFGraphicsStreamEngine` is PDFBox's `PDFStreamEngine` subclass, so `S`, `s`, `f`, `f*`, `B`, `B*`,
`b` all arrive as three callbacks. `RuleCollector` even overrides `processOperator` itself (`5778`),
for `q`/`Q`, which proves the operator stream is being read here and not somewhere generic.

### Why `appendRectangle` cannot answer, in the engine's own words

    PdfToWord.java:6276-6281
      // stroke the page is drawing the path with right now. The width, the colour and
      // the alpha are all in the graphics state at this point, and they are the ones a
      // `S` after this `re` will paint with. (A `re` that is only filled, never stroked,
      // records the fill-only stroke it did not use; see D-22's note in the report - a
      // path's own paint operator is not visible here.)
      float[] stroke = strokeOf();

So at `6281` the engine records a *guess*: the stroking colour in force, which for
`q .9 .92 .96 rg 394 681.89 124 34 re f Q` is whatever stroking colour the page last set - not the
paint the path will actually get.

### ...but the operator arrives two callbacks later, and is already consumed

    PdfToWord.java:5797-5800  (in resetPath)
      // The rule lists' sizes at the start of this path: the rules this path adds are the
      // ones the paint operator will be told about when it arrives.
      pathRulesH = rules.horizontal.size();
      pathRulesV = rules.vertical.size();

    PdfToWord.java:6131-6139
      private void stampPathRules(boolean stroked) {
          float[] stroke = stroked ? strokeOf() : bandFillStroke();
          for (int i = Math.max(0, pathRulesH); i < rules.horizontal.size(); i++) {
              if (i < rules.hStroke.size()) rules.hStroke.set(i, stroke);
          }
          for (int i = Math.max(0, pathRulesV); i < rules.vertical.size(); i++) {
              if (i < rules.vStroke.size()) rules.vStroke.set(i, stroke);
          }
      }

`strokePath()` (`6704`) and `fillAndStrokePath()` (`6722`) call `stampPathRules(true)`; `fillPath()`
(`6713`) calls `stampPathRules(false)`. **That is the paint operator, read at the operator.**

And the fill case is already discriminating:

    PdfToWord.java:6142-6155  bandFillStroke()
      float hgt = pyMax - pyMin, wid = pxMax - pxMin;
      if (hgt <= 1.5f && wid > 2f) return new float[]{Math.max(0.1f, hgt), fill, alpha};
      if (wid <= 1.5f && hgt > 2f) return new float[]{Math.max(0.1f, wid), fill, alpha};
      return null;

A fill-only path that is a **hairline band** keeps a stroke (that is how most generators draw a rule);
any other fill-only path - the header shading, 124 x 34 pt - gets `null`.

### So what is actually missing is one reader, not one piece of information

    PdfToWord.java:1295-1304
      List<Edge> edges = new ArrayList<>();
      for (float[] h : rules.horizontal) {
          float y = pageH > 0 ? pageH - h[0] : h[0];
          edges.add(new Edge(true, h[1], y, h[2], y));
      }
      for (float[] v : rules.vertical) {
          float y0 = pageH > 0 ? pageH - v[2] : v[1];
          float y1 = pageH > 0 ? pageH - v[1] : v[2];
          edges.add(new Edge(false, v[0], y0, v[0], y1));
      }
      List<Table> tables = findTables(edges, glyphs, pageWidth);

Every rule becomes an `Edge` whatever it was painted with. `grep -n "hStrokeAt\|vStrokeAt"` returns
exactly five hits: the two declarations (`5677`, `5682`) and two readers (`7462` in `edgeStroke`,
`7543` in `innerStroke`), both of which use the stroke to pick a border's *weight and colour* and both
of which `continue` on null - i.e. a null-stroke rule is skipped when choosing which weight to write,
but it is still in the lattice.

**That is the whole of the refused experiment.** `fillrule-131500` skipped null-stroke rules while
building `edges` (its numbering: `1275-1285`; today `1296-1304`), and measured 27.31 -> 46.58 and
1 page -> 2. Nothing else had to change, because the operator was never the missing part.

### What the current build actually emits (measured, this run)

`ConvertOne` on the document, then counting `word/document.xml`:

    tables 1   rows 8   cells 44   gridSpan 3   vMerge 4
    row 0  [Depot vMerge] [SCHEDULED span3] ["Fleet held Breakdowns" span2 vMerge]
    row 1  ["" vMerge]   [Services] [Km operated] [Revenue (Rs. lakh)] ["" span2 vMerge]
    row 2  [Yeshwanthpur] [1,842] [6,42,180] [1,284.42] [184] [42]

So `6bff144` did land `w:vMerge` (4 of them: Depot, Fleet held, Breakdowns, and the row-1
continuations), and the **horizontal weld is untouched**: "Fleet held" and "Breakdowns" are still one
`span2` cell with two paragraphs. The defect is exactly where the brief says it is.

---

## 2. How many of the 213 documents would change if a fill-only rectangle contributed NO edge at all?

### Method (no corpus conversion, no engine change)

For every page of every PDF in `/scratch/work/p2w/corpus/` I rebuilt the engine's rule lists from
pymupdf `page.get_drawings()` and applied the engine's own tests, each with the line it comes from:

| step | engine | reproduced as |
|:--|:--|:--|
| a `re` adds 4 edges | `appendRectangle 6282-6290` (H if `width>2`, V if `height>2`) | same thresholds |
| an axis-aligned segment adds 1 | `lineTo 6680-6690` (`<=0.8` off-axis, `>2` long) | same |
| a fill-only path keeps a stroke only when hairline | `bandFillStroke 6142-6155` | exclude `w<=1.5` or `h<=1.5` |
| an edge shorter than 3 pt is dropped | `findTables 8794-8797`, `EDGE_MIN=3f` (`7589`) | same |
| a table needs a lattice | `findTables` needs intersections and cells | connected component of crossing rules with >=3 distinct h and >=3 distinct v lines |

**Extractor validation:** for the 74 documents that carry `src_drawings` in `benchmarks/CENSUS.csv`,
`sum(len(page.get_drawings()))` equals it **74/74 exactly**. The counting instrument reads the same
drawings the pipeline counts.

**One caveat, stated rather than hidden:** `get_drawings()` reports drawing objects, not raw `re`
tokens. For a single-`re` path they are the same thing - one `appendRectangle` call each - and a
closed 4-line axis-aligned path is treated as the engine treats it in `bandFillStroke` (`6145-6147`,
`pLines == 4 && pRects == 0`). A path that mixes `re` with other segments is one drawing object here
and is not separated out; how many of the 690 are such paths is **not measured**.

### The numbers

    documents                                      213   (0 errors)
    fill-only, non-hairline `re` rects with >=1 edge >= 3 pt
                                                   690   in 86 documents
    ... of those, inside a >=3 x >=3 rule lattice  446   in 26 documents
    ... of those, >=1 edge no stroked rule supplies 347  in 13 documents
    ... of those, an OPEN interior column boundary  12   in  9 documents
    ... of those, an OPEN interior row boundary     21   in  9 documents
    ... of the 26 documents, how many emit >=1 <w:tbl> in the .docx
                                                    25   (434 of the 446 fills)

The 26th is `46_chart_coloured_labels_body_text`: 12 in-band fills, **0 tables** in the converted
`.docx`, so its fills are not inside a region the engine turns into a table - my lattice test is a
proxy and over-counts it. That is why the ceiling is 25 and not 26.

**Answer: at most 25 documents can change; 13 of them are the set where a fill supplies a lattice line
nothing else supplies; exactly 1 of them has been measured with the change.** The measurement is
`75_merged_header_cell_three_columns`: 27.31 -> 46.58 share5, 1 page -> 2, `content-present-partly-
displaced` -> `content-missing-partly-replaced` (`fillrule-131500`). **The other 24 are not measured** -
that is the number this census cannot give without converting, and I did not convert it.

### The worst three by number of such fills inside a region the engine turns into a table

Raw count (all 26 documents, table confirmed in the converted `.docx`):

| # | document | in-band fills | load-bearing | `<w:tbl>` | share5 today |
|:-|:--|--:|--:|--:|--:|
| 1 | `305_vaccination_certificate` | 192 | 192 | 1 (12 tr / 24 tc) | 0.00 |
| 2 | `bank-statement-5-pages` | 60 | 0 | 5 | 0.56 |
| 3 | `041122-Account_Opening_Form` | 26 | 26 | 26 | 98.65 |
| 3= | `Account_Opening_Form_Fillable_filled` | 26 | 26 | 26 | 97.62 |

Two honest qualifications, both measured:

* `305_vaccination_certificate`'s 192 fills are **3.6 x 3.6 pt squares** - the modules of a QR code -
  and the "table" the engine builds from them is a 12-row, 2-cell artefact. It is a real fill-only
  rectangle in a real lattice (`22 x 22` module edges, each 3.6 pt so each survives `EDGE_MIN`), but it
  is not shading, and the change would be judged on it for the wrong reason.
* `46_chart_coloured_labels_body_text` has 12 in-band fills and **no table**, so it drops out.

Excluding fills smaller than 4 pt in both directions (dots and QR modules, i.e. shading only) gives:

    fill-only shading rects                        342   in 82 documents
    ... inside a table lattice                     223   in 24 documents
    ... with an edge no stroked rule supplies      124   in 11 documents
    top three: bank-statement-5-pages 60, 041122-Account_Opening_Form 26
               (tie: Account_Opening_Form_Fillable_filled 26), 330_cad_drawing_sheet 15

**The number that should decide whether to spend a corpus pass is 13, not 25.** The 12 documents whose
every fill edge is duplicated by a stroked rule cannot change at the lattice level (`mergeEdges`,
`SNAP_TOL`/`JOIN_TOL = 3f`, is not modelled here, so "cannot" is a lattice-level statement, not a
byte-level one). And of the 13, four are already at 98.65, 97.62, 0.23 and 0.05 - documents whose
tables are currently right, with the fill carrying them.

---

## 3. Is there a narrower rule that keeps the fill's EXTENT as evidence but stops it being a separator?

### The rule, stated so it can be tested

1. **Separator provenance.** An edge is a separator only if it was stroked (`S`, `s`, `B`, `b`) or is a
   hairline fill (`bandFillStroke != null`). A shading fill contributes **no** separator.
2. **Extent as licence.** A shading fill's rectangle licenses a merge over the lattice bands it covers,
   but creates no lattice line. It may *extend* a line the stroked rules already establish elsewhere in
   the same table (on 75 that keeps the fill's bottom edge `y=160`, which the Depot cell outline
   establishes at `x 56..196`), and it may not *create* one (on 75 that refuses `x=456`).
3. **A text witness gates the licence.** Where a boundary is open (no stroked rule crosses the fill at
   that coordinate), the licence is granted only if the text inside the fill does not witness two
   separate runs on either side.

Part 1 and part 2 are cheap and measurable. Part 3 is where the corpus says no.

### Why the population is small

Only **12 fills in 9 documents** have an *open* interior boundary - a boundary inside the fill that no
stroked rule crosses. Everywhere else (434 of the 446 fills) a stroked rule already separates the
columns inside the fill, so the fill's extent cannot license a false merge and parts 1-3 are inert.
That is a strong reason to think the change is cheap to screen:

    75_merged_header_cell_three_columns     2 fills   open x 262,328 (fill 1) and x 456 (fill 2)
    305_vaccination_certificate             3         open x 440.9,444.5 / 491.5,495.1   (no text)
    electricity-bill, eway-bill, gst-invoice-with-qr-code,
    insurance-policy-schedule, mobile-bill  1 each    open x ~528-544                   (no text)
    03_stamp_vertical_90deg                 1         open x 509.2,512.2
    table-with-merged-cells                 1         open x 92.4,225.5,264.4,303.2

### The three candidate text witnesses, and what each measured

**(a) "text occupies fewer bands than the rect covers" - REFUTED as stated.**

Over the whole corpus, 80 fill-only rects span more than one column band (15 documents): 9 have their
text in a single band, 71 have text in two or more. On 75 it works exactly:

| fill | bands | bands its text occupies | words | verdict |
|:--|--:|--:|:--|:--|
| `196..394 x 126..143` (SCHEDULED shading) | 3 | **1** | SCHEDULED | keep the merge - correct, the cell really is span3 |
| `394..518 x 126..160` (the header shading) | 2 | **2** | Fleet / held / Breakdowns | split - correct, two cells |

But on `table-with-merged-cells` (share5 **0.67**, i.e. already right) the header shading
`42.5..552.8 x 90.5..127.3` covers 8 column bands with its text in 7, and the current output is

    row 0  [Region span2] [Headcount by quarter span4] [Annual cost (Rs)] [Remarks]

which is the source's own structure. The band-count test would split "Headcount by quarter" at
`x 225.5, 264.4, 303.2` and "Region" at `92.4` - **four real merges destroyed to fix one false one.**

**(b) "no word straddles the open boundary" - VACUOUS.**

Measured: **0 of the 12** open-boundary fills has any word whose box crosses an open boundary. In
`table-with-merged-cells` "Headcount", "by" and "quarter" each sit wholly inside their own band, just
as "Fleet held" and "Breakdowns" do. The test separates nothing; it would split both.

**(c) gap size against the word space, or per-band text centring - NOT MEASURED.** These are the two
witnesses left, and they are the only ones that distinguish 75 (a 24.7 pt gap between `436.3` and
`461.0` across `x=456`, two labels each centred in its own band) from `table-with-merged-cells` (one
phrase, normal word spaces, centred across bands 2-5 as a whole). I did not measure them, so I will not
claim they work.

### So the honest verdict on question 3

**Yes to the separator half, no to the licence half as currently formulated.** "A shading fill is not a
separator" is a statement the engine's own data already supports (`hStrokeAt == null`), it touches 12
fills in 9 documents, and one document has been measured and got worse (46.58) - which is not evidence
against the rule, it is evidence that the rule must be applied **together** with the licence, because
on 75 the fill is also the only thing closing `y=160` for `x 196..518`. Without part 2 the header row
loses its bottom edge and the table fragments across two pages.

### What would falsify it

1. **A shading-only grid loses its lattice.** A table whose cells are only ever filled, never stroked,
   has no line for part 2 to extend; it would come back with no table, or a worse one. The census names
   the documents to test: `041122-Account_Opening_Form` (26 load-bearing fills, 26 tables, 98.65),
   `Account_Opening_Form_Fillable_filled` (26, 97.62), `330_cad_drawing_sheet` (15, 4.91),
   `343_air_waybill` (13, 0.23), `340_bill_of_lading` (12, 0.07). **If any of those five gets worse, the
   separator half is wrong too and the distinction has to be weaker than stroke-vs-fill.**
2. **A genuine merge whose text occupies as many bands as the rect covers** is split by part 3. This is
   already measured as existing: `table-with-merged-cells` at 0.67. If splitting it moves any ink (it
   changes `gridSpan` 2 -> 1 and 4 -> 1 and therefore the column widths `DocxWriter` computes), part 3
   is wrong as stated.
3. **A document with an open-boundary fill and no text at all** (8 of the 12) changes when the licence is
   withdrawn. If one of `electricity-bill` (1.33), `eway-bill` (0.05), `mobile-bill` (1.55),
   `insurance-policy-schedule` (0.53), `gst-invoice-with-qr-code` (0.07) moves, the no-text default must
   be "keep the merge", not "split".
4. **If `75` does not reach ~0 with parts 1+2+3** then the weld was never (only) the fill: the missing
   `y=160` under Services / Km operated / Revenue would have to be supplied by the lattice-extrapolation
   half, and that half is what the 46.58 measurement says is load-bearing.

---

## Ruled out, with how

| Claim | Test | Result |
|:--|:--|:--|
| the paint operator is unavailable at the rule-recording point | read `RuleCollector`: `5720`, `5778`, `5790-5800`, `6131-6155`, `6704-6727` | **refuted** - it is a `PDFGraphicsStreamEngine`, the operator arrives at `strokePath`/`fillPath`, and `stampPathRules` already stamps `null` for a shading fill |
| the operator information is missing from the model | `grep -n "hStrokeAt\|vStrokeAt"` -> `5677, 5682, 7462, 7543` | **refuted** - it is stored per rule; only `edgeStroke`/`innerStroke` read it, and only for weight |
| the change is a wide blast radius | 213 documents, `get_drawings` census | **refuted** - 446 in-band fills but only 26 documents, 25 with a table, 12 fills with an open boundary in 9 documents |
| the corpus cannot be counted without converting it | `get_drawings` vs `CENSUS.csv src_drawings` | **refuted** - 74/74 exact |
| a fill's extent is never a legitimate merge | 75's `SCHEDULED` shading spans 3 bands and the merge is real | **refuted** - 9 of the 80 multi-band fills have their text in one band, i.e. are real merges |
| the column-band text test in `mergedheader-vmerge-192600` is safe | `table-with-merged-cells`, 8 bands, text in 7, currently 0.67 | **refuted as written** - it would split `Region span2` and `Headcount by quarter span4` |
| the straddle test discriminates | 12 open-boundary fills, words vs boundary boxes | **refuted** - 0 straddles anywhere, including in the false merge and in the two real ones |
| the fix is unnecessary because `6bff144` fixed this document | converted at `6bff144` and counted the XML | **refuted** - 4 `w:vMerge` present, "Fleet held Breakdowns" still one `span2` cell |

## Not measured (stated, not estimated)

* How many of the 25 candidate documents actually change. 1 of 25 is measured.
* Whether `mergeEdges` (`JOIN_TOL = 3f`) makes the 12 "every edge duplicated" documents inert.
* The gap-size and per-band-centring witnesses in 3(c).
* `share@5px` for `75` on this build: `measure_doc` needs a soffice render, which this run did not
  spend. 7.62 is taken from `benchmarks/RANKING.csv`, which is the committed measurement of this engine
  and agrees with `mergedheader-vmerge-192600`.
* Google Docs behaviour of any of this: no Drive call was made.

## Reproducing

    bash tools/p2w-bench/build-engine.sh                     # 35 s, fetches the JDK
    python3 -c "import sys;sys.path.insert(0,'benchmarks');import p2w;p2w.corpus()"
    python3 /scratch/work/fillcensus.py                      # the 690 / 446 / 347 / 12 census
    python3 /scratch/work/texttest.py                        # band-count witness (refuted)
    python3 /scratch/work/straddle.py                        # straddle witness (vacuous)
    # per document: ConvertOne, then count <w:tbl> in word/document.xml
    cd tools/engine-verify && java -Xmx700m -cp "out:libs/aar/classes.jar:libs/aar/assets:\
      libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" ConvertOne <pdf> <outdir>

The three census scripts read `/scratch/work/p2w/corpus/*.pdf` and write
`fillcensus.json`, `fillcensus_shade.json`, `texttest.json`, `straddle.json`.
