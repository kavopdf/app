# Two-column documents at 5 px: the ink is MOVED, not lost — and in one of them a nested table is
# emitted correctly but the flow after it is anchored to the table's TOP

Run: 20 Nov 2026, ~07:00–07:10 IST. Engine built from the repository head by
`tools/p2w-bench/build-engine.sh` (35 s), corpus rebuilt from the `corpus-v1` release
(213 PDFs), `scipy` installed **before** any measurement (`INSTRUMENT_MODE = "scipy"`, exact
EDT). Read-only: no engine file was edited, nothing committed, nothing pushed.

Documents:

    table-inside-two-column-page     share@5 38.11   max_pt 82.08   1 page
    itr-computation-with-slab-table  share@5 42.33   max_pt 15.36   1 page

Both are classed `content-partly-lost-and-displaced` in `benchmarks/DEFECT-CLASSES.md`
(rows 36 and 47, both `OPEN`).

---

## The answer in one paragraph

**Neither document has lost any ink.** Every character is present — `text_recall 100.00`,
`chars_src == chars_ours` (2109/2109 and 1675/1675), 409/409 and 304/304 source words matched
to one of ours, 0 unmatched — and the entire `share@5px` deficit is recovered by a large enough
tolerance: **100 % of it by 96 pt on `table-inside-two-column-page` and by 19.2 pt on
`itr-computation-with-slab-table`.** What the metric is measuring in both cases is a *local*
displacement that the 5 px (2.4 pt) radius cannot see:

* `table-inside-two-column-page` — the right column's caption and its three body paragraphs
  (78.4 % of the lost ink) are **115.43 pt too low**, and the nested table above them (17.6 %) is
  **9.7 pt too high**. The cause is in the emitted XML and is unambiguous: the first paragraph
  after the nested table is written with **`w:before="2600"` (130 pt)** where the page drew
  **4.2 pt**, because the flow position after a nested table is anchored to the nested table's
  **top edge (102.2 pt) instead of its bottom edge (221.4 pt)**.
* `itr-computation-with-slab-table` — every table row is laid out at its own `w:trHeight`, which
  is **351 or 370 twips against the page's uniform 368 twips (18.4 pt)**. The shortfall is
  ~0.5 pt a row and accumulates down the page: **dy = −0.97 pt at row 2, −6.27 at row 9,
  −14.31 pt at the last row.** Nothing is missing; the page is compressed vertically by 14.3 pt.

The defect-class name is wrong for both documents. `content-partly-lost-and-displaced` is derived
from `invent5 > 0.7 * share5` on a sweep that stops at 10 px; both documents read `invent5 ≈
share5` (37.35 vs 38.11 and 41.10 vs 42.33) — the mirror image of loss, i.e. **wholly
displaced** ink. Extending the same sweep to 20/40/96 pt shows 0.00 % remaining.

---

## Setup, and the instrument checked against the published table

    git clone https://github.com/kavopdf/app /scratch/work/CS
    pip install scipy pymupdf
    bash tools/install-gate.sh          # PASS - nothing got worse, table matches engine 26d4a5451cadc765
    bash tools/p2w-bench/build-engine.sh # engine built - ConvertAll ready (35s)
    python3 -c "import p2w; print(p2w.corpus())"   # 213

Corpus path used by `benchmarks/p2w.py`: `/scratch/work/p2w/corpus` (`ROOT="/scratch/work/p2w"`,
`CORPUS=ROOT+"/corpus"`). The two source PDFs are there.

Conversion and rendering — `ConvertOne` (one document per JVM, as `docx()` in `p2w.py`
requires), then `soffice --headless --convert-to pdf`:

    java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
         ConvertOne /scratch/work/p2w/corpus/<doc>.pdf /scratch/work/out2
    soffice --headless --norestore --convert-to pdf --outdir /scratch/work/pre <doc>.docx

Then `p2w.py`'s own `position()` and `invention()` re-run on those two files, with the sweep
extended to 20 px (identical code, one extra tolerance):

```
table-inside-two-column-page
  position:  {"state":"compared","shares":{"1":62.45,"2":50.76,"3":45.62,"5":38.11,"10":29.13,"20":22.14},
              "median_pt":3.84,"p90_pt":64.32,"max_pt":82.08,"n":28856,"n_ours":27304}
  invention: {"shares":{"1":61.89,"2":50.39,"3":45.25,"5":37.35,"10":26.73,"20":20.47},
              "max_pt":115.2,"n":27304}
  content:   {"chars_src":2109,"chars_ours":2109,"recall":100.0,"missing":0}
itr-computation-with-slab-table
  position:  {"state":"compared","shares":{"1":64.93,"2":56.21,"3":52.2,"5":42.33,"10":27.4,"20":7.85},
              "median_pt":4.32,"p90_pt":11.04,"max_pt":15.36,"n":29209,"n_ours":26384}
  invention: {"shares":{"1":62.53,"2":54.77,"3":50.96,"5":41.1,"10":22.46,"20":4.18},
              "max_pt":15.36,"n":26384}
  content:   {"chars_src":1675,"chars_ours":1675,"recall":100.0,"missing":0}
```

Every published number is reproduced exactly: 62.45 / 50.76 / 45.62 / 38.11 / 29.13 and
64.93 / 56.21 / 52.20 / 42.33 / 27.40. This is the same measurement, not a lookalike.

One instrument detail that matters for every share quoted below: `p2w.edt()` returns
`distance_transform_edt(~mask).astype(np.int32)`, so distances are **floored** — `d > 5` means
"6 px or more". A first pass of my own scripts used the float distance and read 40.22 % at 5 px
instead of 38.11 %; the int32 form is used everywhere below, so every share here equals the
published one.

---

## Q1 — Absent, or present but moved?

### The numbers, per document

| | `table-inside-two-column-page` | `itr-computation-with-slab-table` |
|---|---|---|
| share@1 px | 62.45 | 64.93 |
| share@2 px | 50.76 | 56.21 |
| share@3 px | 45.62 | 52.20 |
| **share@5 px** | **38.11** | **42.33** |
| share@10 px | 29.13 | 27.40 |
| share@20 px | 22.14 | 7.85 |
| share@40 px (19.2 pt) | 19.15 | **0.00** |
| share@120 px (57.6 pt) | 9.06 | 0.00 |
| share@160 px (76.8 pt) | 1.18 | 0.00 |
| share@200 px (96 pt) | **0.00** | 0.00 |
| invent@5 px | 37.35 | 41.10 |
| invent@10 / @20 px | 26.73 / 20.47 | 22.46 / 4.18 |
| invent max_pt | 115.20 | 15.36 |

(The first five rows are `benchmarks/RANKING.csv`; @20/@40/@120/@160/@200 are the same
`position()` with the sweep extended, and @1/@5/@10/@20 of that extension reproduce the CSV to
the hundredth.)

### How much of the deficit 10 px and 20 px recover

| | deficit @5 px | recovered @10 px | recovered @20 px | still lost @20 px |
|---|---|---|---|---|
| `table-inside-two-column-page` | 10 996 px | 2 591 px = **23.6 %** | 4 606 px = **41.9 %** | 22.14 % of source ink (6 390 px) |
| `itr-computation-with-slab-table` | 12 363 px | 4 359 px = **35.3 %** | 10 069 px = **81.4 %** | 7.85 % (2 294 px) |

The two curves are different shapes and they say different things:

* `itr-…-slab-table` is a **falling** curve — 42.33 → 27.40 → 7.85 → **0.00 at 40 px**. Ink that
  a wider tolerance recovers entirely is ink that was **put somewhere else**. Nothing is absent.
* `table-…-two-column-page` is a **two-slope** curve: 23.6 % of the deficit goes in the first
  10 px (the right edge of every right-column line, ~11 pt short), then it flattens
  (22.14 → 19.15 → 9.06) and only collapses at 96 pt, where the 115.43 pt block displacement
  comes back into range. **0.00 % at 200 px** — there is no ink on that page with no counterpart
  anywhere on our page.

### `invent5` — the mirror statistic

`invention()` in `benchmarks/p2w.py` (our ink with no source ink within the radius):

* `table-inside-two-column-page`: invent@5 **37.35** against share@5 **38.11** — ratio 0.98.
* `itr-computation-with-slab-table`: invent@5 **41.10** against share@5 **42.33** — ratio 0.97.

Loss and invention of the same size, pixel for pixel, is the signature of **displacement**: for
every place the page has ink and we do not, we have ink where the page does not. `invent max_pt`
is 115.2 pt on the first document — the same 115.43 pt as the block shift measured under Q2, which
is the second, independent confirmation of that number.

### What `max_pt` does not mean here

`max_pt` 82.08 on `table-inside-two-column-page` is *not* the displacement. The displaced block
moved **115.43 pt**, but the distance transform measures to the *nearest* our-ink pixel, and the
block's own neighbouring lines (18.4 pt pitch) and the paragraph above it supply ink at 82 pt.
The published `max_pt` understates this defect by 33 pt. On `itr-…-slab-table` `max_pt` 15.36 is
the honest number: it is the accumulated row drift at the foot of the page.

---

## Q2 — Which ink, where

Method exactly as `tools/p2w-bench/FINDINGS/content-partly-lost-SPAN-162250-a999.md`: rebuild
`position()`, take the **argmax of the distance transform over source ink**, convert px → pt,
then read the source word under that pixel with pymupdf `get_text("words")`.

### `table-inside-two-column-page`, page 1 (596 × 842 pt)

    argmax source-ink pixel: px(912,604)  pt(437.76,289.92)  dist 82.43 pt
    source word under it: 'bands'   full line: 'bands themselves. A spanning'

* Region: **right-hand column, middle of the page** (y 290 of 842 = 34 % down; x 438 of 596).
* What it is: **body text**, the third line of the paragraph that begins *"We therefore model the
  page as a sequence of horizontal bands…"*. Not the table, not a rule.

Ink census over the page, as % of each region's source ink that is > 5 px from any of our ink:

| region (pt) | ink px | @5 | @10 | @20 | @40 | @120 | @160 |
|---|---|---|---|---|---|---|---|
| header band (0–70) | 1 099 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| left column body (x 40–300, y 70–500) | 11 583 | 3.87 | 2.81 | 0.59 | 0.00 | 0.00 | 0.00 |
| right column: the nested table (x 300–560, y 100–230) | 2 698 | **71.57** | 57.04 | 0.00 | 0.00 | 0.00 | 0.00 |
| right column: below the table (x 300–560, y 230–500) | 12 757 | **67.55** | 51.27 | 49.56 | 43.33 | 20.48 | 2.67 |
| footer (y 700–842) | 0 | — | — | — | — | — | — |
| whole page | 28 856 | 38.11 | 29.13 | 22.14 | 19.15 | 9.06 | 1.18 |

Attribution of the 10 996 px @5 px deficit: **8 617 px (78.4 %) from the right column below the
table**, **1 931 px (17.6 %) from the nested table**, **448 px (4.1 %) from the left column**.

Block-level geometry (blocks matched by their first 25 characters; `dx0`/`dy` in pt):

| source block | source rect | our rect | dx0 | dy | dW |
|---|---|---|---|---|---|
| masthead `TECHNICAL NOTE · DEG/2026/14 …` | (45.4, 49.9, 549.9, 56.9) | (45.5, 46.6, 545.2, 57.6) | +0.15 | −3.32 | −4.88 |
| title | (45.4, 68.0, 354.9, 83.0) | (45.5, 67.4, 354.7, 82.4) | +0.15 | −0.58 | −0.33 |
| left column ¶2 | (45.4, 185.3, 289.2, 265.0) | (45.5, 185.2, 279.9, 264.5) | +0.15 | −0.07 | −9.47 |
| table row `Metric Weight Baseline Current` | (309.1, 122.2, 529.9, 129.4) | (309.9, 113.1, 529.8, 120.1) | +0.76 | **−9.07** | −0.86 |
| table row `Merged cell recall 0.10 61.8 72.4` | (309.1, 214.2, 529.9, 221.4) | (309.9, 205.1, 530.2, 212.1) | +0.76 | **−9.07** | −0.50 |
| caption `Weights sum to 1.00. Baseline is the build…` | (306.1, 232.6, 473.1, 239.4) | (306.2, 348.1, 465.7, 354.6) | +0.06 | **+115.53** | −7.49 |
| ¶ `We therefore model the page as a sequence…` | (306.1, 253.9, 550.0, 321.8) | (306.2, 369.3, 538.9, 436.8) | +0.06 | **+115.43** | −11.14 |
| ¶ `Error analysis shows three recurring patterns…` | (306.1, 329.7, 550.0, 409.4) | (306.2, 445.1, 538.6, 524.4) | +0.06 | **+115.43** | −11.43 |
| ¶ `The approach has an obvious cost: band boundaries…` | (306.1, 417.3, 550.0, 485.2) | (306.2, 532.7, 540.8, 600.2) | +0.06 | **+115.43** | −9.24 |
| footer line | (45.4, 811.4, 549.9, 817.8) | (45.5, 811.6, 547.9, 817.6) | +0.15 | +0.19 | −2.15 |

So: **horizontal placement is right (dx0 +0.06 … +0.76 pt everywhere), vertical placement is
wrong in exactly two places** — the nested table −9.07 pt, and everything after it **+115.43 pt**
to the tenth of a point. The `dW` column is a third, smaller defect: every right-column block is
9–11 pt narrower than the page drew it (−4.6 % on a 244 pt line), which is the half-point size
floor (8.9 pt → 8.5 pt, −4.5 %), not missing word spacing — the page is ragged-right here.

The table's **rules are present and displaced, not missing**:

    src : 7 horizontal rules at y = 117.35 135.75 154.15 172.55 190.95 209.35 227.75 (pitch 18.40)
    ours: 7 horizontal rules at y = 107.65 126.85 144.65 163.65 181.65 199.65 218.65 (pitch 17.8-19.2)
    verticals: src 5 at x = 306.14 391.18 430.87 481.89 532.91
               ours 5 at x = 306.40 391.30 431.40 482.30 533.40

### `itr-computation-with-slab-table`, page 1 (596 × 842 pt)

    argmax source-ink pixel: px(331,1753)  pt(158.88,841.44)  dist 15.79 pt
    source word under it: '(refundable)'   full line: '(refundable) 13,427.20'

* Region: **bottom edge of the page**, last row of the third table (`Balance tax payable /
  (refundable)`), left column of that row. It is **a table cell's text**, not a rule.

Word-level drift, matched word by word (`dy` negative = our word is higher than the page's),
banded by the source y:

| source y band | words | dy median | dy p5…p95 | words with \|dy\| > 2 pt |
|---|---|---|---|---|
| 0–84 | 34 | −1.48 | −1.62 … −0.21 | 0 |
| 84–168 | 37 | −0.16 | −1.12 … +0.09 | 0 |
| 168–253 | 32 | −1.22 | −1.97 … −0.17 | 0 |
| 253–337 | 29 | −2.67 | −3.42 … −2.37 | 29 |
| 337–421 | 23 | −3.97 | −4.87 … −3.47 | 23 |
| 421–505 | 28 | −6.27 | −7.27 … −5.37 | 28 |
| 505–589 | 17 | −8.67 | −7.77 … −7.77 | 17 |
| 589–674 | 28 | −10.57 | −11.47 … −9.57 | 28 |
| 674–758 | 30 | −11.51 | −12.02 … −11.01 | 30 |
| 758–842 | 46 | −12.41 | −14.31 … −7.71 | 46 |

`dx` median −0.11 pt (p5 −6.60, p95 +0.65): **the page is displaced vertically only, and the
displacement grows monotonically with y** — a pure row-height accumulation, not a block move and
not a page shift. Region census:

| region (pt) | ink px | @5 | @10 | @20 | @40 |
|---|---|---|---|---|---|
| header band (0–70) | 2 894 | 0.00 | 0.00 | 0.00 | 0.00 |
| assessee block (70–140) | 4 111 | 0.00 | 0.00 | 0.00 | 0.00 |
| Table 1, slab rates (145–295) | 4 485 | 1.67 | 0.00 | 0.00 | 0.00 |
| Table 2, upper half (295–560) | 8 065 | 53.63 | 23.01 | 0.00 | 0.00 |
| Table 2, lower half (560–690) | 3 010 | **99.97** | 84.15 | 9.10 | 0.00 |
| Table 3 + footer (690–842) | 6 644 | **74.56** | 54.41 | 30.40 | 0.00 |
| whole page | 29 209 | 42.33 | 27.40 | 7.85 | 0.00 |

The table **rules** are all there too: 44 horizontal rules on the page, 43 in our render (the one
without a counterpart is the 969.15 pt rule that lies outside the page box), at an alternating
17.5/18.5 pt pitch instead of the page's uniform 18.4:

    src : 71.35 138.35 160.35 178.75 197.15 215.55 233.95 … 885.15 969.15   (pitch 18.40 throughout)
    ours: 70.85 109.40 120.40 138.15 159.75 178.45 195.75 214.25 231.85 …  (pitch 17.5 / 18.5 alternating)

---

## Q3 — `table-inside-two-column-page`: is the nested table emitted at all?

**Yes. Completely, correctly nested, with every cell and every character, and not one duplicate.**
The problem is entirely what happens *after* it.

    w:tbl: 2   w:tr: 7   w:tc: 26   w:trHeight: 7   w:tblpPr: 0   w:drawing: 4   w:txbxContent: 4

`document.xml` body children: `p, p, p, p, tbl, p, p, p, p, sectPr`.

* **TABLE 1** — the two-column *layout* table: `w:tblW 10999` (= 549.95 pt, the full text width),
  `w:tblInd 907`, **1 row, 2 cells, `w:trHeight 9815` `w:hRule="exact"`** (= 490.75 pt). Cell 1
  holds the left column's 13 line-paragraphs; cell 2 holds the content table and the right
  column's 20 paragraphs.
* **TABLE 2** — the nested content table, `nested_in_tbl=True`, `w:tblW 4540` (= 227 pt),
  `w:tblInd 0`, `w:tblStyle KavoTable`, single 9B9B9B borders, **6 rows × 4 cells = 24 cells,
  0 empty**:

```
row: ['Metric', 'Weight', 'Baseline', 'Current']
row: ['Cell text exact', '0.35', '96.4', '97.1']
row: ['Cell position', '0.25', '91.2', '94.8']
row: ['Row boundary', '0.20', '88.6', '93.2']
row: ['Header detection', '0.10', '94.0', '95.5']
row: ['Merged cell recall', '0.10', '61.8', '72.4']
```

Compared word by word against the PDF's own text in the table's rectangle
(300,100)–(560,232):

    docx table words: 46 tokens,  empty cells: 0
    docx-only (invented / duplicated): Counter()      <- nothing
    pdf-only  (dropped)              : Counter({'Table':1,'1':1,'Metric':1,'weights':1,
                                              'and':1,'results':1,'per':1,'cent':1})

The only "pdf-only" words are the table's **caption** `Table 1. Metric weights and results (per
cent).`, which is a body paragraph in the source and is emitted as a body paragraph (an anchored
line at x 306), not a cell. So: **no cell is empty, no cell is dropped, no cell is duplicated,
and no character is missing.** The rules are emitted as real `w:tblBorders` and render.

**And the table's declared geometry proves where the damage is.** The layout row's written height
is exactly the sum of what its cell writes:

    cell-2 before+line sum = 7595 tw;  nested trHeights = 2220 tw;  total = 9815 tw = 490.75 pt
    written w:trHeight = 9815 tw = 490.75 pt          <- the writer's own arithmetic, to the twip
    with the 2600 tw gap removed: 360.75 pt           <- against the page's 383.1 pt columns band

and the paragraph that carries the bogus gap is visible in the cell XML, in document order:

```
CELL 2 children: ['tbl', 'p', 'p', 'p', ... ]
  NESTED TABLE row 1..6: trHeight=380/360 atLeast, 4 cells each
  p  before=0    line=80  rule=exact :: ''                       <- the 4 pt table carrier
  p  before=2600 line=9   rule=exact :: 'Weights sum to 1.00. Baseline is the build of 12 August 2026'
  p  before=446  line=12  rule=exact :: 'We therefore model the page as a sequence of horizontal band'
  ...
```

`2600 twips = 130 pt`. The page draws **4.2 pt** between the table's bottom rule (221.4 + rule)
and that caption's box top. The caption and the three paragraphs under it therefore land
**115.43 pt** low — 130 pt of `w:before` less the 9.07 pt the table above them sits high, less
the 4-5 pt the page actually had. This one number explains 78.4 % of the document's deficit and
also inflates the layout row by 130 pt (490.75 written against 383.1 drawn).

**Where does 130 pt come from?** From the flow position the paragraph is spaced against. The
caption's box top is 232.2 pt; the gap written is 130 pt; so the flow position the writer used was
**102.2 pt** — the nested table's **top edge** (= the layout row's top), not its bottom edge
(221.4 pt). Two independent confirmations:

* the shift of the four blocks after the table is **+115.43 pt** = 111.0 pt (the nested table's
  declared height, 2220 twips) + 4.4 pt (the real gap) — i.e. the paragraphs were placed as if
  the table occupied no height at all;
* `invent max_pt` = **115.2 pt** — our ink sits 115.2 pt from the source's, measured by the
  instrument, from the other side.

---

## Q4 — The code path

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`.

### `table-inside-two-column-page` — the flow anchor after a table (lines 6775–6795)

The content table is emitted inside the layout table's cell (`ctx.inColumn == true`), and the
function that writes it ends by telling the flow where the table ended:

```java
6775    float rowBottomPt = t.bottom;
6776    if (!Float.isNaN(lastRowTopPagePt) && lastRowHeightTw > 0) {
6777        rowBottomPt = lastRowTopPagePt + lastRowHeightTw / (float) TWIPS_PER_PT;
6778    } else {
6779        rowBottomPt = t.bottom
6780                + Math.max(0, lastRowHeightTw - lastRowContentTw) / (float) TWIPS_PER_PT;
6781    }
6782    ctx.lastBaseline = rowBottomPt;
6783    ctx.lastSize = 0f;
6786    ctx.lastLinePt = 0f;
6789    if (ctx.inColumn) ctx.cenCellFlowY++;
6790    else cenSetY(ctx, rowBottomPt + (carrier ? carrierTw / (float) TWIPS_PER_PT : 0f), false, "table-bottom");
6792    ctx.flowY = rowBottomPt
6793            + (carrier ? carrierTw / (float) TWIPS_PER_PT : 0f);
```

Measured: the value this block hands on is **102.2 pt** — the nested table's top edge — where the
table's last row's box bottom is **221.4 pt**. `lastRowTopPagePt` is assigned only inside
`if (exactRows)` (`:6242` declares it `NaN`, `:6249` assigns it from `rowEdge[r]`), and for this nested table it is `NaN`, so control
falls to the `t.bottom` fallback at `:6775/:6779`. `t.bottom` for this nested table is its own
top. Both `ctx.lastBaseline` (`:6782`) and `ctx.flowY` (`:6792`) then hold a position 119 pt too
high, and every block placed from them is 119 pt too high — the paragraphs inside the cell are
spaced by the gap they measure to that position.

The consumer is the paragraph emitter:

```java
4245    } else if (pitch > 0f) {
4252        float extra = pitch - (1f - LINE_BASE) * ctx.lastLinePt - LINE_BASE * linePt;
4256            beforeTw = (int) Math.round(extra * TWIPS_PER_PT);      // 130.4 pt -> 2600 twips
...
4275    int absBeforeTw = 0;
4300    if (ctx.flowY >= 0f) {
4301        absBeforeTw = (int) Math.max(0L,
4302                Math.round(Math.min(absTop - ctx.flowY, gapCapTw(ctx) / TWIPS_PER_PT) * TWIPS_PER_PT));
```

`pitch = 232.6 − 102.2 = 130.4 pt`, `extra = 130.1 pt`, `beforeTw = 2600` — the number in the XML.
`ctx.inColumn` also disables both escape hatches that exist for the page flow: the anchor rule at
`:4337` (`ZERO_GAP_ANCHOR && !ctx.inColumn`) and the over-cap anchor at `:4259`
(`!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx)`). Inside a cell a 130 pt gap is written
as 130 pt of `w:before` by design; the defect is that the gap itself was measured from the wrong
edge.

And the same number then inflates the row, because `flowTwOf` (`:2160-2195`) sums every
`w:before` and `w:line` in the cell and the nested table's `w:trHeight`s, giving the layout row its
`w:hRule="exact"` height at `:2114`:

    7595 (cell paragraphs' before+line, including the 2600) + 2220 (nested trHeights) = 9815 twips

So a single wrong anchor is responsible for both the 115.43 pt shift **and** the layout row being
130 pt too tall.

### `itr-computation-with-slab-table` — the row height (lines 6182 and 6271–6273)

```java
6182            int rowHeightTw = Math.max(rowTwHere, rowLineTw);
...
6270            inner.append("<w:tr>");
6271            if (rowTwHere > 0) {
6272                inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw)
6273                     .append("\" w:hRule=\"atLeast\"/><w:cantSplit/></w:trPr>");
```

and the cell paragraph that cannot rescue it, `cellParaXml` (`:6874-6879`):

```java
6878                .append(spacing(beforeTw, boxTw, sz, autoCellBoxes(), false));
```

which for every cell of these tables writes **`w:line="10" w:lineRule="exact"`** (0.5 pt) — the
cell's own line box is a hairline, so `w:trHeight` is the only thing that can set the row's
height. Measured: the render's row pitches are **17.5 / 18.5 / 17.6 …**, i.e. exactly the
`w:trHeight` values **351 / 370** twips written for the rows, against the page's uniform
**368 twips (18.4 pt)**. `rowHeightTw` is 17 twips short on one row in two and 2 twips over on
the other, so each pair of rows loses 15 twips and the deficit accumulates:

    row 1  dy −0.07      row 6  dy −5.37      row 12 dy −9.17
    row 2  dy −0.97      row 9  dy −7.77      row 20 dy −14.31

Because 5 px is 2.4 pt, the first two rows are inside the tolerance and every row from the third
down is outside it — which is exactly the shape of the table above (0 % loss to y 253, 100 % loss
by y 491).

**What I did not verify here:** the arithmetic that turns a uniform 368-twip page pitch into the
alternating 351/370. The two candidates inside `:6086-6182` are `rowTwHere` (the page's own
`rowEdge` pitch when `exactRows`, else the table's average `rowTw` from `:5940`) and the
`contentTwHere = rowTwHere - ruleTwHere` that feeds `rowLineTw`. I did not instrument
`PdfToWord.Table.rowEdge[]` to see which one produced 351, and the source comment at `:6108-6112`
("on electricity-bill's 18.4 pt rows (0.5 pt rules) that turned an 18.0/19.0 alternation into
17.5/18.5") says the engine already knows this alternation exists and had it measured once. The
*mechanism* above (row laid out at `w:trHeight` because the cell line box is a 0.5 pt hairline) is
verified by the render; the *origin of 351* is not.

---

## Q5 — What I ruled out, and the measurement that ruled it out

**Ruled out: any content loss or deletion.**
`content()` on both documents: `text_recall 100.00`, `chars_missing 0`, `chars_src == chars_ours`
(2109 = 2109; 1675 = 1675). Word matching: **409 of 409** source words found on
`table-inside-two-column-page`, **304 of 304** on `itr-…-slab-table`, 0 unmatched on either.

**Ruled out: absent ink.** The tolerance sweep reaches 0.00 % — at 40 px (19.2 pt) for
`itr-…-slab-table`, at 200 px (96 pt) for `table-…-two-column-page`. If ink were missing, some
share would survive every tolerance. It does not, on either document. (The 1.18 % that survives
76.8 pt on the first document is 340 px, and it is one line —
`natural top-to-bottom order of the bands themselves. A spanning`, x 340.8–548.6, y 283.7–295.2 —
whose nearest counterpart is 115 pt away because the block it belongs to moved; it goes to 0.00 %
at 96 pt.)

**Ruled out: the nested table being dropped, flattened, emptied or duplicated.**
`w:tbl` = 2, the content table is a real `<w:tbl>` nested in a `<w:tc>`, 6 rows × 4 cells, **0
empty cells**, docx-only word multiset empty, rules emitted as `w:tblBorders` and drawn (7 of 7
horizontal, 5 of 5 vertical, at the right x).

**Ruled out: font substitution / glyph advance widths.** Width per em of the same words in both
renders (matched word by word, `(x1−x0)/(y1−y0)`):

| document | src width/em | our width/em | ratio | n |
|---|---|---|---|---|
| `table-inside-two-column-page` | 2.1670 | 2.2150 | **1.0000** | 383 |
| `itr-computation-with-slab-table` | 2.6670 | 2.6620 | **0.9986** | 214 |

The faces are metric-compatible to 0.14 %, so no displacement here is a font-metrics effect. What
*is* a size effect is visible separately: the rendered sizes are floored to the half point
(8.9 → 8.5, 7.2 → 7.0, `halfPointsDown`), which is exactly the −4.5 % `dW` on the right column of
the first document — a real but *separate* 9–11 pt horizontal tail defect, and it cannot produce a
115 pt vertical move.

**Ruled out: a page-level shift, rotation, or wrong page size.** Masthead `dy −3.32`, title
`dy −0.58`, footer `dy +0.19`, left column `dy −0.07`, `dx0 +0.15` — on `table-…-two-column-page`
the frame of the page is where the page put it. On `itr-…-slab-table` the header band is at
`dy −1.48 … −0.21` and `dx −1.56`. Both renders are 1241 × 1754 px = 596 × 842 pt, the same as
the source; `/Rotate` is forced to 0 on both sides by `p2w.render()`.

**Ruled out: the instrument.** `share@1/2/3/5/10` reproduce `benchmarks/RANKING.csv` to the
hundredth on both documents (62.45 / 50.76 / 45.62 / 38.11 / 29.13 and 64.93 / 56.21 / 52.20 /
42.33 / 27.40) with `scipy` present (`INSTRUMENT_MODE = "scipy"`), so these are the published
numbers and not a re-measurement of something else. I also confirmed the int32 truncation in
`p2w.edt()` is what makes 5 px read 38.11 rather than 40.22 — a float-distance variant of the same
code disagrees by 2.1 points, so every share quoted here uses the int32 form.

**Ruled out: the layout row's `hRule="exact"` clipping the right column.** The row is written
490.75 pt tall and its content ends at 600.2 pt against a row bottom of 592.85 pt — a 7 pt
overflow, not a clip; all 21 blocks in that cell are present in the render and all their words
match. The row is too tall *because* of the bogus gap (it is charged into `flowTwOf`), not the
other way round.

**Ruled out: a two-column-specific defect on `itr-…-slab-table`.** That document has no columns —
it is a single-column form. Its drift is a row-height accumulation, and it appears in the same
form in every table on the page (Table 1 −2.87 pt at its last row, Table 2 −11.47, Table 3
−14.31), i.e. it scales with the number of rows above, not with any column structure.

---

## What I did not verify

1. **The exact expression that produces `w:trHeight` 351 on `itr-…-slab-table`.** I read
   `:6086-6182` and named the two candidates; I did not instrument `PdfToWord.Table.rowEdge[]`,
   `rowTw` or `contentTwHere` to see which one is 17 twips short. The rendered consequence is
   measured; the arithmetic that causes it is inferred from the emitted values.
2. **Why the nested table's `t.bottom` is its own top** on `table-…-two-column-page` (102.2 pt
   instead of 221.4 pt). I measured the flow position the writer used (from the 2600-twip gap and
   the caption's box top, two ways), and read that `lastRowTopPagePt` is only assigned under
   `exactRows`, so the `t.bottom` fallback at `:6775/:6779` is what ran. I did not print
   `t.bottom` itself; the claim "`t.bottom` is the table's top" is the reading that fits, not a
   direct observation.
3. **A fix, or any statement about what a fix would do to the corpus.** Nothing here was built or
   measured as a patch. Two candidate changes fall out of the measurements — anchor the post-table
   flow to the last row's box bottom inside a cell, and write `w:trHeight` at the page's own pitch
   with the cell's `w:line` carrying the content — and neither is built, measured or claimed.
4. **Whether the other nested-table documents share this defect.** `401_trifold_brochure` and
   `350_question_paper` are named in the source comments as the other two documents that nest. I
   did not measure them.
5. **`python3 benchmarks/p2w.py --diagnose 3` was not run as written.** `diagnose()` calls
   `rank()`, and `DIST` (`/scratch/work/p2w/dist2`) is empty on a fresh sandbox, so `rank()` would
   write `RANKING.partial.csv` into `/scratch/output` — a side effect I did not want to leave in
   the deliverable directory. I reproduced exactly what it does (the same `conv()` render, the same
   150 DPI, `set_rotation(0)`) with pymupdf and wrote the four PNGs to `/scratch/work/diag`, then
   viewed them:

       /scratch/work/diag/table-inside-two-column-page__p1__src.png  …__p1__ours.png
       /scratch/work/diag/itr-computation-with-slab-table__p1__src.png …__p1__ours.png

   The images show what the numbers say: on the first document the right column's caption and
   three paragraphs sit ~115 pt below where the page has them, with the table itself in place; on
   the second the two pages look almost identical, with the rows progressively higher toward the
   foot.

---

## Housekeeping

Two files in the clone show as modified and I did not edit either: `tools/p2w-bench/TRACE.md`
(two rows appended by `build-engine.sh` when I ran it: `20 Nov 06:58 | ? | build-engine |
started` / `06:59 | engine built in 35s`) and `tools/p2w-bench/RUN-LOG.md` (one 12 Nov line
removed by the repo's own tooling during `install-gate.sh`). Nothing was staged, committed or
pushed. The corpus zips `p2w.py` downloads to `/scratch/output/_cache` were moved out of the
deliverable directory to `/scratch/work/p2w-cache-zips`.

## Commands run (outputs quoted above)

```
git clone https://github.com/kavopdf/app /scratch/work/CS
pip install scipy pymupdf
bash tools/install-gate.sh
bash tools/p2w-bench/build-engine.sh
python3 -c "import p2w; print(p2w.corpus())"            # 213
java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/<doc>.pdf /scratch/work/out2
soffice --headless --norestore --convert-to pdf --outdir /scratch/work/pre <doc>.docx
python3 /scratch/work/measure.py     # p2w.position() + p2w.invention() + p2w.content(), sweep to 20 px
python3 /scratch/work/where.py       # distance-transform argmax, source word under it, 12x12 region grid
python3 /scratch/work/region.py      # per-region share@1/5/10/20/40/120/160 and deficit recovery
python3 /scratch/work/blocks.py      # block-level dx0/dy/dW, matched by block text
python3 /scratch/work/words.py       # word-level dx/dy, matched by word text + nearest position
python3 /scratch/work/checks.py      # width-per-em, nested-table cell text vs PDF text, row-height sum
```

All scripts are in `/scratch/work/`; the converted `.docx`/`.txt` are in `/scratch/work/out2`,
the soffice renders in `/scratch/work/pre`, the diagnostic PNGs in `/scratch/work/diag`. No engine
file was modified; `git status` in `/scratch/work/CS` is clean.
