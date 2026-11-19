# content-present-partly-displaced / sub-px — the 43.87 is share@1px, and the 1.55 is a run size truncated to half a point

Run: 20 Nov 2026, 04:11 IST. Engine: repo HEAD `2be77ee`, built with `tools/p2w-bench/build-engine.sh`,
tree left clean apart from this file. Instrument: `benchmarks/p2w.py`'s own `position()`, `edt()`,
`_pix()` and `PT` (DPI 150), `ConvertOne` for the .docx, `soffice` once per document for the render,
`pymupdf` for the page geometry and the .docx XML for the emitted values.

## The answer in one sentence

**The pair `43.87 | 1.55` in `benchmarks/DEFECT-CLASSES.md` is not `(share@5px, max_pt)` — it is
`(share@1px, share@5px)`, written into the wrong two columns by `classrow.py` — and the real
residual on these pages is a run size truncated to whole half-points (`6.8 pt -> 6.5 pt`), which
shrinks every glyph advance by 4.5 % while `w:ind` pins the line's left edge, so words slide left in
proportion to their distance from the start of their line. That is hypothesis (c), a font-metric
difference inside lines, and it is the only one of the three that survives arithmetic.**

## 1. The premise, checked first — the table is the defect

`43.87 %` of ink beyond 5 px with `max_pt 1.55` cannot both be true, and not because of anything
on the page. In `position()` (`benchmarks/p2w.py:372-385`) `share@N` and `max_pt` are computed from
the **same** distance array:

```python
d,_=edt(om,sm.shape)                                   # 376
shares={t:round(float((sm&(d>t)).sum())/n*100,2) for t in SWEEP}   # 378
dv=d[un]  where  un=sm&(d>1)                           # 377, 383
max_pt=round(float(dv.max())*PT,2)                     # 385
```

`dv` is a superset of the pixels counted by `share@5px`, so **whenever `share@5px > 0`,
`max_pt >= 5 px = 2.400 pt`.** That is a hard invariant of the instrument, and `RANKING.csv`
satisfies it on every row: 0 of 212 rows have `share5 > 0` with `max_pt < 2.4`.

`benchmarks/DEFECT-CLASSES.md` violates it on **47 of its 212 rows**. So the two numbers in that
table are not `(share5, max_pt)`.

They are `(share1, share5)`. The RANKING row for `mobile-bill` is

```
160,mobile-bill,displacement,content-present-partly-displaced,
    43.87,23.00,6.99,1.55,0.32,1.4,1.92,16.80,100.00,0,1,1,,0,86.80,99.32,100.00
    share1 2     3     5    10   med  p90  max
```

`43.87` is `share1`, `1.55` is `share5`, `16.80` is `max_pt`. `electricity-bill` is the same:
`share1 46.85`, `share5 1.33`, `max_pt 14.40`.

**Where it is written.** `tools/p2w-bench/classrow.py:206-207`:

```python
newrow = "| %s | `%s` | %s | %.2f | %.2f | %s | %s | %s |" % (
    c[0], doc, c[2], s1, s5, c[5], new_status, new_note)
```

The header is `| # | document | problem | share5 | max_pt | worst_page | status | note |`, and the
row is written with `s1` in the `share5` slot and `s5` in the `max_pt` slot. `load_rank()`
(`classrow.py:60`) returns `(share1, share5, problem)` and **never reads `max_pt` at all**, so no
number in the `max_pt` column of a rewritten row can be a `max_pt`.

This predicts exactly which rows are wrong, and the prediction holds: the `problem == "none"`
branch (`classrow.py:172-186`) appends the line **unchanged**, so those rows keep the hand-written
`(share5, max_pt)`; every other row is rebuilt by line 206 with `(share1, share5)`.

| `problem` in the class file | rows reading `(share5, max_pt)` | rows reading `(share1, share5)` | neither |
|---|---|---|---|
| `none` | **116** | 4 | 10 |
| all other problems (80 rows) | 1 | **78** | 6 |

The one "other" that reads `(share5, max_pt)` is `415_inline_images` at `0.00 | 0.00`, where both
readings coincide. The 16 "neither" rows are FIXED rows still carrying the numbers they were fixed
with (`411_nested_xobject_transforms` reads `48.64 | 31.05` while RANKING now says `share1 5.01,
share5 0.00, max_pt 1.44`) — a separate, already-documented staleness, not this bug.

**Consequence for the question as asked.** "About 44 % of the source ink has no counterpart within
5 px" is false: 44 % has no counterpart within **1 px (0.48 pt)**. And "the worst single outlier is
under 2 pt" is also false: the worst outlier is **16.80 pt** (`mobile-bill`) and **14.40 pt**
(`electricity-bill`). Neither of the question's two figures is what its label says.

## 2. The instrument's pixel, from the code

`benchmarks/p2w.py:72` — `INK=68; DPI=150; PT=72.0/DPI`. So

```
1 px = 0.480 pt      2 px = 0.960 pt      3 px = 1.440 pt
5 px = 2.400 pt     10 px = 4.800 pt
```

Pages are rasterised at `fitz.Matrix(DPI/72, DPI/72)` = 2.0833 px/pt (`p2w.py:176`, `712`), and
`edt()` is an exact Euclidean transform, so a distance of *n* px is *n* × 0.480 pt.

**This alone decides the question's three options.** 5 px is 2.400 pt, which is **larger than 2 pt**.
So option (a) — "a uniform sub-2 pt offset that is over 5 px" — is arithmetically impossible: an
offset under 2 pt cannot be more than 2.4 pt. Option (b), a re-wrap, is excluded by measurement
(§4: same word count, same line count, every line start within 0.08 pt). Only (c) remains, and §5
shows it is (c).

## 3. The measured distribution, per page

Reproduced with `position()` on the converted `.docx` rendered by `soffice`; it reproduces the
published RANKING row to the digit, which is the check that this run is measuring the same thing.

| | `mobile-bill` p1 | `electricity-bill` p1 |
|---|---|---|
| source ink px / our ink px | 24 567 / 22 531 | 20 444 / 19 031 |
| share@1px | **43.87** | **46.85** |
| share@2px | 23.00 | 22.07 |
| share@3px | 6.99 | 7.32 |
| share@5px | **1.55** | **1.33** |
| share@10px | 0.32 | 0.31 |
| median_pt / p90_pt / max_pt (as the instrument reports them) | 1.44 / 1.92 / **16.80** | 0.96 / 1.92 / **14.40** |

The instrument's `median/p90/max` are taken over `d > 1` only (`p2w.py:377`), so they describe the
*conditional* tail. Over **all** source ink the distribution is:

| distance | `mobile-bill` | `electricity-bill` |
|---|---|---|
| 0 px | 27.4 % | 17.8 % |
| 1 px (0.480 pt) | 28.8 % | 35.3 % |
| 2 px (0.960 pt) | 20.9 % | 24.8 % |
| 3 px (1.440 pt) | 16.0 % | 14.7 % |
| 4 px (1.920 pt) | 3.8 % | 4.5 % |
| 5 px (2.400 pt) | 1.7 % | 1.5 % |
| 6–11 px | 1.4 % | 1.0 % |
| ≥ 12 px | 0.21 % (51 px) | 0.24 % (49 px) |
| **median / p90 / p99 / max, all ink** | **0.480 / 1.440 / 3.360 / 16.800 pt** | **0.480 / 1.440 / 2.880 / 14.400 pt** |

**Read the shape.** Median 1 px, p90 3 px, 92 % of ink inside 4 px, and a thin tail of 0.2 % beyond
12 px. That is **not** a re-wrap (median 1–2 px with a long fat tail) and **not** a 4–6 px uniform
shift (median would be 4–6 px). It is a tight 1-px-mode distribution with a thin, long tail — two
mechanisms, one small and everywhere, one rare and large.

Splitting the ink by what the page drew it as (span bboxes inside the three `find_tables()` regions
versus outside):

| region | share of ink | >1px | >2px | >3px | >5px | max |
|---|---|---|---|---|---|---|
| `mobile-bill` in-table text | 55.3 % | 47.1 | 22.2 | 10.4 | 2.2 | 8.64 pt |
| `mobile-bill` flow text | 19.5 % | 26.7 | 12.4 | 6.2 | 1.7 | **16.80 pt** |
| `mobile-bill` rules, QR, other drawings | 25.3 % | 50.0 | 32.8 | **0.0** | **0.0** | **1.92 pt** |
| `electricity-bill` in-table text | 62.9 % | 45.7 | 19.8 | 9.1 | 1.4 | 8.64 pt |
| `electricity-bill` flow text | 16.8 % | 49.4 | 25.7 | 9.3 | 2.8 | **14.40 pt** |
| `electricity-bill` drawings | 20.3 % | 48.2 | 26.0 | **0.0** | **0.0** | **1.92 pt** |

**The rules and the QR code — ink with no glyph advances at all — never exceed 1.92 pt (4 px).**
That is the ceiling of the vertical component: it is real (it puts ~50 % of rule ink over 1 px, which
is most of the 43.87), and by itself it can never produce a single pixel over 5 px. Every pixel
beyond 5 px, and the whole 16.80 pt maximum, is **text**, and it is text only in the horizontal axis.

## 4. Line starts hold; word positions inside the line do not

The emitted `.docx` reproduces the page's line breaks exactly — this is the measurement that rules
out re-wrap:

| | `mobile-bill` | `electricity-bill` |
|---|---|---|
| source words / our words | 279 / 279 | 294 / 294 |
| source lines / our lines | 32 / 32 | 32 / 32 |
| words matched to a source word | 279 (100 %) | 294 (100 %) |
| paragraphs / `<w:tbl>` emitted | 8 / 3 | 8 / 3 (page draws 3 tables) |

**Line starts, horizontal.** Every flow paragraph is emitted with `w:ind w:left="850"` = 42.50 pt;
the page draws it at 42.52 pt and the render puts it at 42.60 pt — **+0.08 pt, the same on all 18
flow spans**. In-table words start at **+0.58 pt**, also constant (the cell inset), on all 94/102
in-table spans. No line start drifts: the set of observed line-start offsets is
`{0.08, 0.14, 0.58}` on `mobile-bill` and `{0.08, 0.10, 0.13, 0.58}` on `electricity-bill`.

**Line starts, vertical** (span baselines, source → ours): `-0.02, +0.48, +0.88, +0.98, +1.38,
+1.48, +1.52, +1.88` pt — the ladder already measured in
`content-missing-nothing-in-its-place-B-103610-346a.md`, unchanged, capped at **1.88 pt < 4 px**.

**Words inside a line: they compress, and the compression is exactly the font size.**

For every flow line, our width / source width equals our emitted size / the size the page drew:

| line (source y) | page size | our size | `w:sz` | size ratio | source width | our width | width ratio |
|---|---|---|---|---|---|---|---|
| `Table 1. Usage summary` (182.52) | 6.80 | 6.50 | 13 | 0.9559 | 79.74 | 76.17 | 0.9552 |
| `Table 2. Bill details` (349.72) | 6.80 | 6.50 | 13 | 0.9559 | 61.23 | 58.48 | 0.9551 |
| `Amount in words: …` (570.12) | 7.20 | 7.00 | 14 | 0.9722 | 206.43 | 200.33 | 0.9705 |
| `SAC 998413 · This is a tax invoice …` (583.12) | 6.80 | 6.50 | 13 | 0.9559 | 343.94 | 328.74 | 0.9558 |
| `For assistance call 198 …` (596.12) | 6.60 | 6.50 | 13 | 0.9848 | 252.81 | 248.94 | 0.9847 |
| `Vistara Telecom · +91 98200 44112 · …` (816.38) | 6.40 | 6.00 | 12 | 0.9375 | 200.11 | 187.28 | 0.9359 |

Six lines, six agreements to three decimals. The mechanism is closed by one number: the last word of
the `SAC` line, `banking.`, sits at source x0 = 360.80 with the line starting at 42.52. A pure
size-ratio compression predicts `-(1 - 0.9559) × (360.80 - 42.52) = -14.19 pt`; the render measures
**-14.00 pt**. Word-width sums and inter-word gaps shrink together (0.9549 and 0.9620 on that line),
and per-word width ratios are 0.947–0.958 with no outlier — so this is not the space glyph and not
letter spacing, it is every advance, which is what a size change does and only a size change does.

The same thing inside table cells, smaller because a cell's words are pinned by a tab stop and only
their own advance width can shrink: in-table lines measure 0.997–0.9998 of source width, with the
residual reaching 8.64 pt on the longest cell string (`Flat 402, Shree Residency, Chakan, Pune
410501`).

**So: line starts are accurate to 0.08 pt horizontally and 1.88 pt vertically; word positions inside
a line drift up to 14 pt horizontally. The error is inside the line, and it grows with x.**

## 5. The code path

**What decides a line's start** — `DocxWriter.flowFromBox`
(`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:4154`): the x becomes `w:ind w:left`
(`:4164`, `leftTw = Math.round(b.x * TWIPS_PER_PT)`), the gap to the previous line becomes
`w:spacing w:before` via `spacing(...)` (`:3536`). In a table row, `DocxWriter.flowRow`
(`DocxWriter.java:3308`) puts each field at a `w:tab` stop at its measured x (`:3529-3532`).
**This path is correct** — 0.08 pt of x error, ≤ 1.88 pt of y error — and it produces the sub-2 pt
component that caps at 1.92 pt.

**What decides the x of a word inside a line** — nothing positions it. In a flow paragraph a word's x
is the sum of the advance widths of everything before it, and the advance widths are the face's
advances **at the emitted size**. That size is decided in `DocxWriter.runXml`
(`DocxWriter.java:4475`; the four-argument overload writes the size at **`:4504`**):

```java
int half = halfPointsDown(run.sizePt);           // DocxWriter.java:4504
if (half > 0) {
    sb.append("<w:sz w:val=\"").append(Math.min(3276, Math.max(2, half))).append("\"/>");
```

and `halfPointsDown` (`DocxWriter.java:6959-6962`):

```java
private static int halfPointsDown(float sizePt) {
    if (!(sizePt > 0f)) return 20;
    return Math.max(2, (int) Math.floor(sizePt * 2f));
}
```

`Math.floor(sizePt * 2f)` — **truncation to whole half-points, always down**. Measured on the emitted
XML: 13.00→26, 10.00→20, 7.40→14, 7.20→14, 6.80→13, 6.60→13, 6.40→12. Every size that is not already
a multiple of 0.5 pt loses up to 0.5 pt, and at these sizes 0.5 pt is 4.4–7.8 % of the type.

The size going *in* is right, so this is not an upstream measurement problem: `PdfToWord.java:2130`
sets `g.sizePt = tp.getFontSizeInPt()`, `:2136` multiplies by the CTM scale, `:2308` by `sy` — and the
page's own content stream on `mobile-bill` says `BT 1 0 0 1 42.51969 258.7701 Tm /F3+0 6.8 Tf …`, i.e.
6.8 pt at an identity text matrix. 6.8 in, `floor(13.6) = 13` out, 6.5 emitted.

**Which one produces this signature: `halfPointsDown`, reached through `runXml`.** The line-start
path (`flowFromBox` / `flowRow`) is what makes the error visible rather than cancelling it — because
the left edge is pinned and the size is not, the whole deficit is expressed as horizontal drift that
accumulates along the line.

The truncation is **deliberate and documented** (`DocxWriter.java:6950-6958`): rounding *up* made a
substitute face wider than the page's and re-wrapped `362_price_list_dense`. So the mechanism is not
"a rounding bug to flip"; a repair has to restore the line's measure (the deficit is exactly
`1 - floor(2s)/2s` of the line length, and `stretchTw` at `DocxWriter.java:4434` already computes a
letter spacing for the *justified* case) rather than change the direction of the rounding.

## 6. The mechanism, and what it predicts

**A page whose body type is drawn at a size that is not a whole half-point loses up to 0.5 pt of type
size at emission; because glyph advances scale with the size while `w:ind` pins the line's left edge,
every word slides left in proportion to its distance from the start of its line, and the ink of the
longest lines ends up 8–17 pt from where the page drew it while every line still starts where the
page started it.**

The prediction is testable from the source PDFs alone, with no conversion — a document is in this
class because of the truncation only if its characters are drawn at sizes that are not multiples of
0.5 pt. Measured on the 18 OPEN `content-present-partly-displaced` documents and a 20-document sample
of the `share5 = 0.00` clean rows:

| group | draws text at a non-half-point size | count |
|---|---|---|
| the 18 OPEN class documents | 54 %–98 % of characters (15 of 18) | 15 |
| the clean sample (`share5 = 0.00`) | **0.0 %** of characters (18 of 20) | 18 |

`mobile-bill` 98.3 % (7.4/7.2/6.4/6.8 pt), `electricity-bill` 96.0 % (7.2/7.4/6.8/6.6),
`very-long-single-column-table` 95.8 % (7.4), `table-of-contents-dot-leaders` 95.0 % (10.4/9.4),
`64_newspaper_uneven_columns_ad_boxes` 87.0 % (8.4), `price-list-right-aligned-amounts` 87.3 % (8.3).
On the clean side: `56_table_indented_from_margin` 0.0 % (9.5/8.5/8.0), `19_hanging_indent_txtpos`
0.0 % (10.0/8.0), `314_tender_rfp_boq` 0.0 % (7.5/9.0/8.0) — all whole or half points.

The three class documents the prediction **excludes** are `75_merged_header_cell_three_columns`,
`374_org_chart` and `330_cad_drawing_sheet`, all at 0.0 % non-half-point sizes; their displacement is
something else and this mechanism does not explain them. The two clean documents it **wrongly
includes** are `325_demat_holdings_statement` (62 % at 7.2 pt) and `335_msds_safety_data_sheet`
(9 %), where the non-half-point text must be short enough or pinned enough that the deficit stays
under 5 px.

So: **this class is, for 15 of its 18 OPEN members, the documents set at 6.4–10.4 pt type with a
fractional point in it; the corpus's clean tail is the documents set at 7.5, 8.0, 8.5, 9.0, 10.0 pt.**
That is why the class boundary looks arbitrary — it is a type-size accident, not a layout property.

## 7. What I ruled out, and how

* **A block displacement of the page (option a).** The question's own arithmetic: 5 px = 2.400 pt, so
  a sub-2 pt offset cannot exceed 5 px. Measured: rule and QR ink, which has no advances to scale,
  never exceeds **1.92 pt** and is 0.0 % beyond 3 px on both pages. There is no 5 px displacement
  anywhere on either page.
* **A re-wrap (option b).** Word counts identical (279/279, 294/294), line counts identical (32/32),
  every line start within 0.08 pt, and the emitted `.docx` has 8 paragraphs and the page's 3 tables.
  Nothing re-wrapped.
* **The space glyph or letter spacing.** Per-word width ratios 0.947–0.958 across a line and
  inter-word gaps 0.962 — a narrower space would move the gaps and not the words; the words moved.
  No `w:spacing` letter-spacing is emitted on any of these paragraphs (checked in `document.xml`).
* **A face substitution.** Both PDFs name `LiberationSans` on both sides (`mobile-bill` source spans
  `AAAAAA+LiberationSans`, our render `LiberationSans`). The width ratio equals the *size* ratio, not
  a face's width ratio — a substitution would not track the size so exactly.
* **The `run-size-from-sizePt-not-Tf` patch mechanism.** That patch takes the run size from the wrong
  input. Here the input is right (`6.8 Tf`, identity `Tm`, `g.sizePt` 6.8) and the loss is entirely in
  `halfPointsDown` afterwards. Same *symptom*, different line of code — do not read this as a reason
  to re-try that patch.
* **`median_pt`/`p90_pt`/`max_pt` as published.** They are conditional on `d > 1` (`p2w.py:377`), so
  they describe only the tail; the true all-ink median on both pages is **0.480 pt**, not 1.44/0.96.
* **The vertical ladder.** Not re-opened: it is `content-missing-nothing-in-its-place-B-103610-346a.md`'s
  uncharged table bottom rule, still live and unchanged (rungs `-0.02/+0.48/+0.88/+0.98/+1.38/+1.48/
  +1.52/+1.88`), and it is capped at 4 px so it cannot be the `share@5px` figure.
* **`--diagnose 3`.** As written it diagnoses the **top three** rows of `RANKING.csv`
  (`p2w.py:1162`, `r[:3]`), which are `041122-Account_Opening_Form`,
  `Account_Opening_Form_Fillable_filled` and `one-page-rotated-180-degrees` — it does not produce
  `mobile-bill` or `electricity-bill` images. The four PNGs for this finding were written by the same
  instrument's `_pix()` at `DPI = 150` into `/scratch/work/diag/<doc>__p1__{src,ours}.png`, and both
  pairs were viewed: same line breaks, same word positions, a visible downward drift of the tables and
  the sentences ending 8–14 pt early — which is the measurement in §4 seen by eye.

## 8. Provenance

* Engine: repo HEAD `2be77ee`, `bash tools/p2w-bench/build-engine.sh` (34 s), `ConvertOne` once per
  document, one document per JVM as `p2w.py:docx()` requires.
* Corpus: `benchmarks/p2w.py`'s `corpus()` — 213 PDFs from the `corpus-v1` release zips.
* Numbers: `benchmarks/p2w.py`'s own `position()`, `edt()`, `_pix()`, `pad()`, `PT` — not a
  reimplementation. `position()` reproduces the published RANKING row for both documents exactly
  (`43.87/1.55/1.44/1.92/16.80` and `46.85/1.33/0.96/1.92/14.40`), which is the check that this run
  measures what the table measured.
* Geometry: `pymupdf` `get_text("words")` / `get_text("dict")` on the source PDF and on the
  `soffice` render of the converted `.docx`; `find_tables()` for the table regions.
* Emitted values: `word/document.xml` of the converted `.docx` (`w:sz`, `w:ind`, `w:spacing`, `w:tabs`).
* No engine change, no build of a candidate, no corpus measurement. `app/src/main/java` unmodified;
  `git status` clean apart from this file.
