# 47_margins — diagnosis of `40_devanagari_shaping_font` (share5 10.48) and `76_devanagari_table` (7.91)

**Verdict in one line:** neither document has a horizontal margin or indent defect. On both pages the left ink
anchor and every table column line are within **0.1–0.8 pt** of the source, and no rigid shift in x (or in y)
improves the score — shifting actually makes it worse. **79 % (doc 40) and 95 % (doc 76) of the "far" ink is the
table's own 1-pixel rules**, which our render draws in the same place with the same 0.5 pt stroke but which
rasterise just above the instrument's ink threshold. The small remainder in doc 40 is a **4–5 % narrower
Devanagari line width** (glyph advance / shaping), which moves the *right end* of each long line ~20 pt left.
No horizontal indent change can fix either document.

---

## 1. Where the numbers came from

`benchmarks/RANKING.csv` (213 rows) — the two rows in full:

| document | rank | signature | problem | share1 | share2 | share3 | **share5** | share10 | median_pt | p90_pt | max_pt | text_recall | chars_missing | worst_page | pages |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `76_devanagari_table` | 198 | mixed | **content-partly-lost** | 14.50 | 8.90 | 8.22 | **7.91** | 5.53 | 3.84 | 14.88 | 15.36 | 100.00 | 0 | 1 | 1 |
| `40_devanagari_shaping_font` | 199 | mixed | **content-partly-lost** | 26.79 | 16.62 | 13.50 | **10.48** | 7.89 | 1.92 | 14.88 | 24.00 | 100.00 | 0 | 1 | 1 |

Two facts here already contradict the brief's framing, and they matter for the class decision:

* **`RANKING.csv` does not put either document in a class called `47_margins`.** Its `problem` column labels both
  `content-partly-lost`. `47_margins` is a *verifier check id* (`tools/p2w-bench/verify_google.py`, block starting
  line 3960), not a `problem` value — `problem` values in this CSV are `none`,
  `content-present-partly-displaced`, `content-missing-partly-replaced`, `content-present-wholly-displaced`,
  `content-missing-nothing-in-its-place`, `content-partly-lost`, `content-partly-lost-and-displaced`.
* **"the rest of the class sits near zero" is only half true.** Of the 213 documents, **26 fail `47_margins`**
  (`benchmarks/gverify/*.json`), and they are bimodal: 12 sit at share5 ≤ 1.82 and 14 sit well above it. These two
  are 4th and 5th worst of the 26 — behind `600_reviewed_invoice_with_annotations` (62.46),
  `360_restaurant_menu` (34.43) and `77_arabic_rtl_document` (11.89). The class is not a tight near-zero
  cluster with two outliers; it is a near-zero cluster of 12 plus 14 documents that fail `47_margins` while
  carrying a *different, larger* defect.

`benchmarks/CENSUS.csv` in this checkout is **header-only (0 data rows)** — there is no census row for either
document to read. The census signal columns (`signal`, `dx_pt`, `dy_pt`, `explains`, `moved_gt20`) are therefore
not available here, and nothing in this report is derived from them.

## 2. How the pages were obtained

The brief's invocation does not exist: `python3 benchmarks/p2w.py --help` offers only
`--budget / --status / --validate / --diagnose N / --force`. `diagnose(n)` takes no `--doc`; it walks the top *n*
rows of an existing ranking and, for each, renders `corpus/<doc>.pdf` and `out/<doc>.docx` to
`/scratch/work/p2w/diag/<doc>__p<worst_page>__src.png` and `__ours.png` at 150 DPI. It needs the corpus, a built
engine and a populated `out/` directory, none of which existed in the sandbox.

So the same two render steps were reproduced directly:

1. Corpus PDFs from release `corpus-v1` of `kavopdf/app` (`gh release download corpus-v1 -p '*.zip'`) → 211 PDFs,
   including both targets.
2. Engine built from the repository head with `tools/p2w-bench/build-engine.sh` (fetches a JDK 17 and
   pdfbox-android; 36 s compile).
3. `ConvertOne <pdf> /scratch/work/p2w/out` — one document per JVM, as `p2w.py` insists — giving the `.docx`.
4. `soffice --headless --convert-to pdf` on each `.docx`, then 150 DPI PNGs of page 1 of both source and render,
   identical to what `diagnose()` writes.

**Reproduction check** (my render vs the ranking, same page):

| document | RANKING share5 | my share5 | RANKING max_pt | my max_pt |
|---|---|---|---|---|
| `40_devanagari_shaping_font` | 10.48 | **10.77** | 24.00 | **24.00** |
| `76_devanagari_table` | 7.91 | **7.97** | 15.36 | **15.36** |

share5 reproduces to 0.3 / 0.06 of a point and `max_pt` exactly, so this render is the one being scored.
(`median_pt`/`p90_pt` are **not** comparable: `p2w.py` reports those "from the worst window" of its chunked pass,
not over the whole page — my whole-page values are 0.48/3.04 and 0.00/0.96. share5 and max are page-level and do
match.)

No repository file was modified, and `benchmarks/gate.py` was not run.

---

## 3. `40_devanagari_shaping_font` — page 1 (the document has 1 page)

**Measured share@5: 10.48 (RANKING) / 10.77 (re-measured). Worst page: 1.**

### What the pages actually look like

Placed side by side the two pages are, to the eye, the same document: same centred three-line masthead, same
left margin, same two-column table with the same seven horizontal rules and three vertical rules in the same
places, same six table rows, same footer with the grey rule. Nothing is indented differently, nothing has slid
sideways or up, no text is missing and no glyph is replaced by a box.

The one difference visible at 1:1 is at the **right-hand end of the three long paragraph lines** (the paragraph
beginning "यह प्रमाणित किया जाता है कि …"). In the 4× crop of x 460–545 pt, y 182–240 pt, the source shows the
line tail ending flush at about 539 pt; in our render the same words ("… के मान्यता प्राप्त") sit visibly further
left and end at about 519 pt. The glyph shapes themselves are correct — conjuncts and matras are formed properly,
the same Noto Sans Devanagari face is used on both sides.

### The measurement, decomposed

| test | result |
|---|---|
| best **x-only** rigid shift of the render | +1 px (+0.5 pt) → share5 10.73 (no gain) |
| best **y-only** rigid shift | +1 px (+0.5 pt) → share5 10.97 (worse) |
| best **2-D** shift (FFT cross-correlation peak) | (+0.5 pt, +0.5 pt) → share5 10.94 (**worse than doing nothing**) |
| left ink anchor, body lines | source 56.80 pt → ours 56.90 pt (**+0.10 pt**), identical on every body line |
| left ink anchor, table | source 51.3 pt → ours 51.3 pt |
| table rules (8 horizontal + 3 vertical) | same y/x within **0.7 pt** (max 293.6 → 294.3), same 0.5 pt stroke, same 0–100 % black |
| ink x-span of the page | source 106–1121 px → ours 106–1110 px |
| source ink px / render ink px | 33 845 / 30 495 |
| far ink (>5 px) on table-rule rows | **2 864 of 3 644 px = 79 %** |
| **share5 with rule rows excluded** | **3.05 %** |
| character content (text layer) | 741 chars source, 741 chars render, **identical** |

The far ink clusters are thin 1-px slivers sitting *exactly on the rule coordinates* — e.g. a 968-px cluster at
y 350.9–355.2 spanning x 63.8–532.3, which is the bottom rule at y = 353.0; and column-width segments at
y ≈ 293.6 and 308.4. The pixel values explain why:

```
source rule y=293.6pt -> px 612, column x=400:  rows 610..614 = [255, 0, 238, 255, 255]   -> ink (<68)
our    rule y=294.3pt -> px 613, column x=400:  rows 610..614 = [255, 255, 118, 118, 255] -> NOT ink (>=68)
```

A 0.5 pt rule at 150 DPI is 1.04 px wide. In the source its centre lands so that one pixel row carries almost all
the coverage (value 0). In our render the rule is 0.4 pt lower, so its coverage splits across two rows
(118 / 118). Both are visible black hairlines — the crop proves they look the same — but neither of our rows is
below the instrument's `INK = 68` threshold, so **the rule contributes no ink at all to the distance transform**,
and every source rule pixel is then scored as ink sitting up to 100 px from the nearest glyph.

**The residual 3.05 %** is at the line ends, and it is a width error, not a position error:

| line (y, pt) | source width | source x1 | render x1 | Δ | Δ as % of line |
|---|---|---|---|---|---|
| 190.3 | 359.7 | 538.6 | 518.7 | **−19.90 pt** | −5.5 % |
| 206.8 | 481.7 | 538.5 | 517.7 | **−20.80 pt** | −4.3 % |
| 381.5 | 481.1 | 537.9 | 514.0 | **−23.89 pt** | −5.0 % |
| 223.3 (short line) | 165.0 | 221.8 | 221.9 | +0.10 pt | +0.1 % |

Every one of these lines starts at 56.8/56.9 pt and ends 20–24 pt short: the shortfall accumulates *through* the
line, which is what a per-glyph advance difference looks like and is not what any indent looks like. One span is
also set at 10.50 pt where the source has 11.00 pt (`प्रमाण पत्र संख्या: केटीबी/…`), which is why this document
also fails `34a_span_size_match`, and its line ends 5.7 pt short at the same place.

### Verdict for doc 40

* The ink is **not** shifted horizontally: the left anchor is out by 0.1 pt and the best x-shift is +0.5 pt.
* The ink is **not** shifted vertically: body line y-positions match to 0.00 pt, table rows to +0.4 pt.
* The glyphs are **not** substituted and none are missing: 741 characters on both sides, same face, correct
  conjuncts. What differs is the **advance width** — our Devanagari line runs 4–5 % narrow.
* **A horizontal indent change cannot fix this.** Indenting the paragraph moves the left edge, which is currently
  correct to 0.1 pt, and leaves the 20 pt right-end shortfall exactly where it is. The only horizontal "fix"
  that would move the line ends is widening the text (letter-spacing / character scaling / a face with the
  source's metrics), and the dominant 79 % of the score is not text at all.

---

## 4. `76_devanagari_table` — page 1 (the document has 1 page)

**Measured share@5: 7.91 (RANKING) / 7.97 (re-measured). Worst page: 1.**

### What the pages actually look like

Again the two pages are the same document: five-line heading block, a five-column, six-row fee table, three
paragraphs below it, and the signature block. Table columns line up with each other across the two images, the
rules are in the same places, the cells hold the same text at the same size. The 4× crop of one column
(x 236–350 pt, y 246–272 pt) is the cleanest evidence: the header cell, the rule under it, the row below with
"१२", and both vertical rules are in the **same pixel positions** in source and render.

The only difference at all is inside the cells: our cell text sits about **1.3 pt lower** than the source's
(e.g. the "१" of row 1 at y 259.40 source, 260.70 render; the header row +0.5 pt). That is a vertical, sub-2 pt
effect and is below the 5 px (2.4 pt) tolerance.

### The measurement, decomposed

| test | result |
|---|---|
| best x-shift / y-shift / 2-D shift | **0 px in every axis** — the correlation peak is at the origin |
| left ink anchor | source 62.50 pt → ours 62.60 pt (**+0.10 pt**) |
| table column rules (x) | source 151.1 / 245.2 / 339.3 / 433.4 / 527.5 → ours 151.3 / 245.3 / 339.2 / 433.2 / 528.3 — **≤ 0.8 pt** |
| table row rules (y) | source 243.3 / 258.1 / 287.3 / 302.2 / 317.0 / 331.9 / 347.4 → ours 243.3 / 258.3 / 287.3 / 302.3 / 317.3 / 332.3 / 347.3 — **≤ 0.4 pt** |
| far ink (>5 px) on table-rule rows | **2 739 of 2 891 px = 95 %** |
| **share5 with rule rows excluded** | **0.52 %** |
| character content (text layer) | 752 chars source, 752 chars render, **identical** |

The far-ink map is unambiguous: 2 860 of the 2 891 far pixels fall in one horizontal band, y ≈ 252–336 pt, i.e.
the table; and the clusters are column-width, 1-px-tall slivers at exactly the rule y-values (255.8–260.2,
314.9–319.2, 329.8–334.1, each split into the three column segments between the vertical rules). Same mechanism
as doc 40, verified the same way:

```
source rule y=258.1pt -> px 538, x=400:  rows 536..540 = [255, 16, 238, 255, 255]   -> ink
our    rule y=258.3pt -> px 538, x=400:  rows 536..540 = [255, 118, 118, 255, 255] -> NOT ink
```

**Table column widths are not the defect.** This was one of the four candidate causes named in the brief; it is
ruled out by direct measurement. Our vertical rules sit within 0.2–0.8 pt of the source's (151.1→151.3,
245.2→245.3, 339.3→339.2, 433.4→433.2), i.e. column widths are within 1 pt of the source's, and the source's
five column starts (62.5 / 156.6 / 250.7 / 344.8 / 438.9 pt) reappear in the render at 63.1 / 157.2 / 251.3 /
345.4 / 439.5 — a uniform **+0.6 pt** table inset, not a width change.

### Verdict for doc 76

* No horizontal displacement at all: the best x-shift is 0 px and the left anchor is out by 0.1 pt.
* No table column-width error: columns are within 1 pt.
* No glyph or content difference: 752 characters on both sides, same face.
* The score is **95 % table rules failing the ink threshold**, and 0.52 % everything else (residual is the
  1.3 pt lower cell text, which is vertical and below tolerance).
* **A horizontal indent change cannot fix this** — there is nothing horizontal to change. Neither can a column-
  width change. The only levers are the rule's rasterised weight / sub-pixel position, or the instrument's
  threshold and DPI.

---

## 5. What this means for the class

1. **Neither document is a margin/indent case.** Both are dominated by the same mechanism: a 0.5 pt table rule
   that our render places 0.2–0.7 pt from where the source places it, which at 150 DPI tips a 1-px line from
   value 0–50 (ink) to value 118–170 (not ink). Because a rule is ~470 pt long, each one contributes 180–500
   "far" pixels, and a page with 7–9 rules carries 2 700–2 900 of them. Removing the rule rows takes
   `76_devanagari_table` from **7.97 % to 0.52 %** and `40_devanagari_shaping_font` from **10.77 % to 3.05 %**.
2. **The class's own horizontal instrument agrees.** `benchmarks/gverify-lo/*.json` — the LibreOffice-side run of
   the same 47 checks — records `47_margins: {'source': 0.0, 'render': 1, 'ok': True}` for doc 40 and
   `{'source': 0.0, 'render': 0, 'ok': True}` for doc 76. The check that owns x reports a 0.0 pt worst-page median
   displacement on both. (The Google-side run in `benchmarks/gverify/` fails it — see the note in
   `verify_google.py` at the merged-run clause, which names `40_devanagari`, `76_devanagari_table`,
   `21_form_labels`, `64_newspaper` and `magazine-2col` as the five documents that a merged-run exclusion would
   take to a pass. That clause is judging run pairs whose x comes from the render's own glyph boxes, and on
   Devanagari a 4–5 % advance-width difference between source and render is exactly what makes such pairs
   disagree — again a shaping/width effect, not an indent.)
3. **So the class cannot be "won" by a margin change, and these two documents cannot be won by one either.**
   The 12 near-zero members are plausibly the genuine leading-space-indent cases the class was built for. These
   two, and the other 12 above-zero members, fail for other reasons: rule rasterisation (both docs here), glyph
   advance width (doc 40), and whatever their own dominant defect is (`content-missing-partly-replaced` for
   `600_reviewed_invoice_with_annotations` and `360_restaurant_menu`).

### What would actually move these two scores

* **Both:** make the rule rasterise as ink at 150 DPI — nudge the rule so its 0.5 pt stroke centres on a pixel
  row (a sub-0.5 pt vertical adjustment of the table's row heights/rule offsets), or draw rules at ≥0.75 pt, or
  measure at 300 DPI where a 0.5 pt rule is 2 px and cannot fall between rows. This is worth ~7.5 and ~9.5
  share5 points respectively — i.e. all of doc 76's gap and most of doc 40's.
* **Doc 40 only:** the 4–5 % narrow Devanagari line. That is a shaping/advance question (the same 11 pt Noto
  Sans Devanagari face, 741 identical characters, lines 20 pt short at the right end, one span set at 10.5 pt
  instead of 11 pt). It is worth the residual 3.05 %.

---

## 6. Reproducing this

```bash
# corpus + engine + render (all inside the sandbox, no repo edits)
gh release download corpus-v1 --repo kavopdf/app -p '*.zip' -O /scratch/work/p2w/x/
unzip -oq /scratch/work/p2w/x/*.zip -d /scratch/work/p2w/x/ex
cp /scratch/work/p2w/x/ex/{40_devanagari_shaping_font,76_devanagari_table}.pdf /scratch/work/p2w/corpus/
cd /scratch/work/CS && bash tools/p2w-bench/build-engine.sh
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/40_devanagari_shaping_font.pdf /scratch/work/p2w/out
cd /scratch/work/p2w/out && soffice --headless --convert-to pdf --outdir ../tmp *.docx
```

Diagnostic PNGs at 150 DPI (identical to what `p2w.py --diagnose` writes) were produced at
`/scratch/work/p2w/diag/<doc>__p1__src.png`, `<doc>__p1__ours.png`, plus 4× crops
`76__rule_{src,ours}.png` and `40__lineend_{src,ours}.png`. The measurement and decomposition scripts are
`/scratch/work/measure.py` (sweep, rigid-shift search, per-line extents, span positions) and
`/scratch/work/farink.py` (far-ink clustering and span pairing).

## 7. Caveats

* The engine here is `kavopdf/app` at the head of `main` today, not the exact build that produced
  `RANKING.csv`. share5 reproduces to 0.29 (doc 40) and 0.06 (doc 76) of a point and `max_pt` exactly, so the
  diagnosis rests on a render equivalent to the scored one, but the numbers are not bit-identical.
* `benchmarks/CENSUS.csv` is empty (header only) in this checkout, so no census row was read for either document.
* My render is LibreOffice's; the `47_margins` class is defined against Google Docs. The pixel-level findings
  (rule rasterisation, advance width) are properties of the `.docx` + renderer pair, and the LO-side verifier
  JSON independently reports `47_margins` passing with a 0.0 pt median, which is consistent with them.
* I did not run `verify_google.py` or `gate.py`, so the exact `(worst_med, worst_tail)` tuple the check would
  report on the Google side is **not measured here** — only the LO-side tuple (0.0 pt, ≤1 pair) from the
  committed `gverify-lo` JSON.
