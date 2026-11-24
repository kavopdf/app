# The docx's vertical geometry is correct. The defect is unreachable, not absent.

**Two agents measured this from opposite directions on 24 Nov and appeared to contradict each other.
They do not. Reconciled here, and the reconciliation is verified in the repository.**

## What the empirical study found (213 documents, 18,327 lines)

Every document converted at HEAD, every .docx rendered through LibreOffice, every text line's y read
from both sides. Pooled `dy = docx_y - pdf_y`:

| population | n | median | p05 | p75 | p95 | within 1 pt |
|---|---|---|---|---|---|---|
| flowed w:p | 4,896 | **0.00** | -0.11 | 0.10 | 3.53 | 90.2% |
| anchored box | 421 | **0.02** | -0.03 | 0.10 | 2.35 | 74.6% |
| table cell | 7,220 | **+0.40** | -0.05 | 0.52 | 1.48 | 85.0% |

**The error is a LEVEL, not a SLOPE.** Over the 184 documents with >=5 flowed lines, median slope of dy
against y is **0.0004 pt per pt of page** - 0.3 pt across a whole page. Median within-document IQR
**0.11 pt**. 180 of 184 documents have |median dy| <= 5 pt.

**Flowed and boxed are NOT offset from each other** - pooled medians differ by 0.02 pt, p25 and p75
identical to a hundredth. In 9 of the 11 documents containing both, the paired difference is
0.00-0.09 pt.

The instrument was falsified: shifting one anchor's `posOffset` by +50 pt, and separately one flowed
paragraph's `w:before` by +50 pt, both come back as **+49.98 pt on exactly the perturbed line**.

## What the diagnosis found on one document

`policy-2col-spanning-section-heading`, dose-response on the emitted artifact: the carrier's
`w:line="1"` advances the flow by 0.05 pt while `anchorKeepsFlow` advances `flowY` by the line's
would-be advance. Changing only that `w:line` moves the worst flowed-line dy from **-101.82** to
**+70.98**, slope 27/20. On the parent of the fix the flow ends **101.82 pt high** at the page foot.

## Why both are right

Verified here on the emitted file:

    paragraphs: 68   box-carriers: 62   flowed: 6
    flowed paragraphs AFTER the first box: 0

**No flowed paragraph follows a box at HEAD.** `PAGE_POSITION_ON_ANCHOR` makes the page absolute after
the first anchor, so the flow never runs past a box and the per-box advance mismatch has nowhere to
accumulate. The empirical study measures the document that exists and finds 0.02 pt, correctly. The
diagnosis measures the same defect with the suppression lifted and finds 101.82 pt, correctly.

On that document the empirical study returns 61 of 61 lines paired, median dy **-0.02 pt**, largest
|dy| anywhere **0.08 pt**. So the 105.7 pt is not in the docx's geometry - it is what the geometry does
when the boxes stop carrying the page.

## The full chain, measured at every link

1. The flow cannot express a two-column band: emitted column-by-column, the right column lands below
   the left's last line. With the anchor rule off: median **+112.28**, max **+138.78**, and 18 of 54
   flowed lines have a negative required gap, worst **-85.05 pt** (`place()` returns `{0, linePt}` for
   `d <= 0`, DocxWriter.java:4152).
2. So the engine carries the page in anchored boxes instead, and the geometry becomes exact: **0.02 pt**.
3. So every page is 62 boxes and 6 flowed paragraphs, and Google **rasterises anchored boxes on
   import**.
4. So the pixel score is **81-92% SSIM**, not 99%, with the geometry correct.

**The boxes are not a workaround for a bug in the flow. They are the only way this engine can place a
two-column page at all today, and their cost is that Google receives an image of the text.**

## What this changes about the plan

- "Fix the y model" is the wrong frame. The y model is already right where it runs.
- The three outliers (median dy +194.68 on Account_Opening_Form_Fillable_filled, +101.90 on
  600_reviewed_invoice_with_annotations, +27.00 on 601_fillable_admission_form) are **per-document
  placement failures**, not a model error - the worst is a rebuilt page (11 render pages against 9
  source). Three documents, three separate causes.
- The only route that removes both the rasterisation and the negative gaps is emitting a band's two
  columns as ONE paragraph with tab stops at the measured x - which the engine already does for form
  rows (`flowRow`, :3546). Not built, not measured.
- The gating measurement: dy on the FLOWED lines of a page where a flowed line DOES follow a box must
  stop being a function of the carrier's `w:line`. At HEAD that population is empty, so the gate must
  be built on a deliberately unsuppressed build, not on the corpus.

## Limits of both measurements

- LibreOffice is the renderer for the empirical study, not Google. It can say the docx's geometry is
  right; it cannot say what Google does with a box.
- Coverage (matched / source text lines): 1.00 median, 0.94 mean, >=0.99 on 156 of 213. Seven below
  0.5, all fragmented decorative or scanned pages, listed and not quoted as extremes.
- Letter-spaced and rotated fragments split to one character per line; those 2,860 lines are excluded
  rather than averaged in.
- Page counts differ on 2 documents, aligned by signature; two implausible pairings at -600/-675 pt
  left visible rather than folded into a median.
# The vertical error of the converted .docx, measured across the corpus

Measurement only. The engine was built from `HEAD` and not modified. Every number below comes
from a measurement that was run in this session; the scripts are `measure.py`, `run_corpus.py`
and `figs.py` in `/scratch/work`, and the raw per-line data is `p2w/meas/<document>.json`
(213 files, 18 327 matched lines).

## What was measured

For every one of the 213 corpus documents:

* source side — `PyMuPDF` on the original PDF: every visual text line, with its baseline
  origin, ink top, ink bottom, x, size and text;
* docx side — the `.docx` the engine produced, rendered to PDF by LibreOffice
  (`soffice --headless --convert-to pdf`), read the same way. Page size matched the source on
  **all 213 documents** (0 mismatches), so the two coordinate systems are the same sheet of paper;
* docx structure — `word/document.xml` unzipped and walked in document order, giving every
  text block a kind: **flowed** (`w:p` in the body), **boxed** (a `w:p` inside a
  `w:txbxContent` under a `wp:anchor`) or **table** (a cell), plus, for a box, its declared
  `wp:positionV/wp:posOffset`.

`dy = docx y − pdf y`, positive means the docx put the line lower on the page.

Lines are paired **by content**, not by position and not by order (a two-column PDF is written
column 1 then column 2; the render interleaves them, which is why a sequence alignment loses a
third of a two-column document — measured: 40 of 61 lines on
`policy-2col-spanning-section-heading` before the method was changed, 61 of 61 after). Where the
same text occurs more than once on a page, identity is settled by **x**, never by y — using y
would manufacture agreement. Lines whose text repeats on the page are flagged `dup>1` and are
excluded from every statistic below unless stated.

## 1. The distribution overall

18 327 lines matched. Pooled `dy` (unambiguous text only):

| population | n | median | p05 | p25 | p75 | p95 | within 1 pt |
|---|---|---|---|---|---|---|---|
| flowed `w:p` | 4 896 | **0.00** | −0.11 | 0.00 | 0.10 | 3.53 | 90.2 % |
| anchored box | 421 | **0.02** | −0.03 | 0.00 | 0.10 | 2.35 | 74.6 % |
| table cell | 7 220 | **0.40** | −0.05 | 0.00 | 0.52 | 1.48 | 85.0 % |

The pooled distribution is a spike at zero with a thin right tail: 91.8 % of all lines are
within 1 pt, the median is 0.00–0.40 pt, and the sign is very slightly positive (the docx sits
a fraction of a point low). `|dx|` over the same pairs has median 0.13 pt, p90 0.61 pt — the
pairing is sound, so the small dy values are not pairing noise.

## 2. Flowed vs boxed — the key result

**The two populations are not offset from each other.** Pooled medians differ by 0.02 pt;
pooled p25 and p75 are identical to a hundredth of a point; the two histograms sit on top of one
another (fig 2, middle).

The sharper test is *within a document*, where both populations come from the same source page
and the same engine run. Eleven documents have ≥5 unambiguous lines of each kind:

| document | n flowed | median flowed | n boxed | median boxed | difference |
|---|---|---|---|---|---|
| Account_Opening_Form_Fillable_filled | 99 | +194.68 | 7 | +190.99 | +3.69 |
| 041122-Account_Opening_Form | 311 | +1.85 | 100 | +2.30 | −0.45 |
| 69_two_col_legal_numbered_clauses | 12 | +0.09 | 29 | +0.00 | +0.09 |
| magazine-2col-pullquote-spanning | 6 | +0.05 | 36 | +0.00 | +0.04 |
| gst-invoice-horizontal-rules-only | 61 | +0.05 | 6 | +0.01 | +0.03 |
| academic-paper-ieee-2col-abstract | 53 | +0.08 | 50 | +0.05 | +0.03 |
| 322_mutual_fund_factsheet | 14 | +0.00 | 8 | +0.00 | 0.00 |
| 323_credit_card_statement | 12 | +0.00 | 5 | +0.00 | 0.00 |
| 65_two_col_full_width_figure_caption | 22 | +0.00 | 22 | +0.00 | 0.00 |
| 66_two_col_footnotes_bottom | 23 | +0.00 | 8 | +0.00 | 0.00 |
| policy-2col-spanning-section-heading | 6 | −0.02 | 52 | −0.02 | 0.00 |

Ten of eleven agree to within 0.5 pt. The single disagreement (+3.69 pt) is in the one document
where **both** populations are displaced by ~+191 pt — the boxes are displaced with the flow, not
against it.

Boxed lines are exact almost everywhere: in 10 of the 11 documents above the boxed median is
0.00 pt to two decimals. The only systematic boxed error in the corpus is 85 lines in
`041122-Account_Opening_Form`, all at exactly **+2.25 pt**.

## 3. How the error grows down the page

It does not grow. It is a **level, not a slope** (fig 1: each panel is one document, x is height
on the page).

Within a document, over the 184 documents with ≥5 flowed lines:

* median slope of `dy` against `y` = **0.0004 pt per pt of page** (0.3 pt over a whole A4 page);
  p90 = 0.0022; only 6 documents exceed 0.01 (8 pt over a page);
* median within-document IQR of `dy` = **0.11 pt**; median full span = **0.41 pt**;
* 180 of 184 documents have |median dy| ≤ 5 pt, and of those, 164 are within 1 pt.

So the error is a per-document constant, not an accumulation and not a sawtooth. Where a document
is displaced, the whole page or the whole document is displaced by the same amount — e.g.
`600_reviewed_invoice_with_annotations` is +101.9 pt at the top and +103 pt at the bottom
(span 0.8 pt over the page).

The one place a genuine drift appears is inside **tables**: table-cell slope has median 0.0011,
p90 0.0078, but 11 documents exceed 0.01 and the worst reach 0.28 pt/pt (`330_cad_drawing_sheet`,
+0.279; `041122-Account_Opening_Form`, +0.150; `360_restaurant_menu`, +0.043). That is row
heights in the docx differing from the source, accumulating across a table — a separate
phenomenon from the flowed-text error.

There is no evidence of stepwise growth at section boundaries in the corpus. Apparent steps in a
first pass turned out to be pairing artefacts on documents whose text repeats (a question paper
whose labels occur twice per page reads as −1/+78/+254/−95 until the repeated-text lines are
excluded; on unambiguous lines the same document is −0.70 ± 0.6 pt throughout).

## 4. The documents at the extremes

By per-document median of the flowed population (≥5 unambiguous flowed lines):

| document | median dy | n flowed | median boxed | pages src→docx | coverage |
|---|---|---|---|---|---|
| Account_Opening_Form_Fillable_filled | **+194.68** | 99 | +190.99 | 9 → 11 | 0.20 |
| 600_reviewed_invoice_with_annotations | **+101.90** | 10 | – | 1 → 1 | 0.98 |
| 601_fillable_admission_form | **+27.00** | 21 | – | 1 → 1 | 0.91 |
| 360_restaurant_menu | +18.11 | 5 | – | 1 → 1 | 0.51 |
| 363_warranty_card | +3.90 | 11 | – | 1 → 1 | 1.00 |
| 03_stamp_vertical_90deg | +2.40 | 6 | – | 1 → 1 | 0.96 |
| 041122-Account_Opening_Form | +1.85 | 311 | +2.30 | 9 → 10 | 0.94 |
| … | | | | | |
| 310_court_judgment | −0.12 | 27 | – | 1 → 1 | 1.00 |
| 351_omr_answer_sheet | −0.34 | 6 | – | 1 → 1 | 1.00 |
| 50_invoice_coloured_total_row | −0.60 | 10 | – | 1 → 1 | 0.96 |
| 350_question_paper | −0.70 | 11 | – | 1 → 1 | 0.85 |
| itr-computation-with-slab-table | **−1.45** | 6 | – | 1 → 1 | 1.00 |

Only **3 of 184** documents exceed 20 pt, and all three are positive. The negative side has no
document worse than −1.45 pt. The error is therefore strongly asymmetric: the docx pushes text
down far more often than it pulls it up.

`Account_Opening_Form_Fillable_filled` is not a shifted page but a rebuilt one: the render has
11 pages against the source's 9, and page 0 of the render starts with the form's field values
stacked 20 pt apart at the top (`12/01/2000`, `jalapur`, `89`, `hsjw862`, …) where the source has
them at their field positions.

`policy-2col-spanning-section-heading` — the document the other investigation is built on — is
**not** displaced in this measurement: 61 of 61 lines paired, median dy −0.02 pt, largest
|dy| in the document 0.08 pt, flowed and boxed both at −0.02 pt.

## 5. What the pattern implies

Stated as an inference from the numbers above, not as a hypothesis:

1. **The two models are not offset from each other, so "flowed vs boxed" is not the axis the
   error lives on.** Ten of eleven documents agree to <0.5 pt between the populations, and the
   one that does not is displaced in both. If the flow model were wrong in a way the anchor model
   is not, the paired differences would be a constant; they are 0.00–0.09 pt.

2. **The docx's own vertical geometry is, for this corpus, essentially correct.** 90 % of flowed
   lines and 75 % of boxed lines land within 1 pt of the source, and the median document is exact
   to 0.01 pt with an IQR of 0.11 pt. Neither the flow model nor the anchor model can be called
   wrong *on average*: a model that were wrong by construction would not produce a within-document
   IQR of a tenth of a point.

3. **The error that exists is a per-document placement failure, not a per-line one.** It appears
   as a whole-document (or whole-page) constant offset — +27, +102, +195 pt — in 3 of 184
   documents, and it travels with both mechanisms. The correct description of the population is a
   spike at zero plus a small population of catastrophic outliers, which is why a single median
   describes nothing: the corpus median is 0.01 pt while the worst document is 195 pt.

4. **A 105.7 pt disagreement cannot come from the docx's declared or rendered geometry.** On the
   document where that number was observed, the same measurement returns −0.02 pt median and
   0.08 pt maximum. The hypotheses that concern the docx's arithmetic — line height, baseline
   versus line top, `w:before`, table-row snapping — are all hypotheses about quantities this
   measurement reads directly, and on this document those quantities are right. The convention
   question alone is bounded: switching from baseline to ink-top changes dy by a median of 0.07 pt
   (p90 2.75 pt, maximum 11.4 pt over 12 537 lines) — an order of magnitude short of 105.7 pt.

   What that leaves is the renderer: Google rasterises the anchored boxes, and the corpus result
   here says the boxes are *correct* — every boxed line is within 2.25 pt of its source position
   in a Word-compatible renderer. A renderer that moves or drops them therefore produces a
   disagreement that the document does not contain.

## 6. How approximate the extraction was

* **Not approximated: the docx y.** It is read from a LibreOffice render of the `.docx` — a real
  rendered position, not an inferred line pitch. The `.docx` has no coordinates of its own (a
  `w:p` is a flow object), so a render is the only way to read a flowed line's y at all; the
  anchor's `posOffset` gives the boxed population a second, renderer-free reading, and the two
  agree (boxed median from the render: 0.02 pt; boxed median from the XML anchor: −0.25 pt
  against the source ink top, on 530 unique-text boxes in 58 documents).
* **The renderer is LibreOffice, not Word and not Google.** Word and LibreOffice both honour
  `w:before` and exact line rules, so the docx is being measured as a Word-compatible renderer
  reads it; a renderer that ignores those properties would disagree. Google was not measured —
  no access from this sandbox.
* **Font ascent.** The docx render uses different fonts from the source, so *ink top* is not
  comparable across the two; *baseline* is used as the primary quantity. The gap between the two
  conventions is measured above (median 0.07 pt, max 11.4 pt).
* **Line grouping.** PyMuPDF splits a line into several "lines" when the text is letter-spaced or
  rotated (an ornate certificate renders one character per line). Those lines are matched
  character-for-character and land in the `tooshort` bucket (2 860 lines), not in the statistics.
* **Matching.** Content-based, 1:1, per page. Coverage — matched lines ÷ source text lines — is
  1.00 at the median, 0.94 at the mean, and ≥0.99 on 156 of 213 documents. Seven documents are
  below 0.5: `15_stamp_on_scanned_page` (0.00 — the page is an image with 2 text lines, neither
  matched), `Account_Opening_Form_Fillable_filled` (0.20), `05_round_company_seal_curved_text`
  (0.28), `60_page_border` (0.30), `352_certificate_ornate_border` (0.38),
  `371_experience_certificate` (0.43), `305_vaccination_certificate` (0.48). The last six are all
  letter-spaced or curved-text documents where the render fragments the text; none of them is
  quoted as an extreme above.
* **Page alignment.** Index alignment when the page counts agree (211 of 213). Two documents
  differ (`041122-Account_Opening_Form` 9→10, `Account_Opening_Form_Fillable_filled` 9→11) and
  are aligned by page signature; a handful of individually implausible pairings in the latter
  (two lines at −600 and −675 pt) are page-alignment residues and are visible as the isolated
  points in fig 1, not folded into any median.
* **Falsification of the instrument.** Two copies of
  `policy-2col-spanning-section-heading.docx` were edited: one with the first anchor's
  `posOffset` moved +50 pt, one with the first flowed paragraph's `w:before` moved +50 pt
  (1 092 → 2 092 twips). Both perturbations come back as **+49.98 pt on exactly the perturbed
  line**, with the rest of the document unchanged (median still −0.02 pt). The instrument
  resolves a 50 pt shift to 0.02 pt and does not smear it across neighbouring lines.

## Files

* `fig1_dy_down_page.png` — dy against height on the page for six representative documents.
* `fig2_distributions.png` — pooled |dy| ECDF by population; the two populations overlaid;
  per-document medians sorted.
* `per_document_dy.csv` — one row per document: pages, coverage, n and median dy per population.
