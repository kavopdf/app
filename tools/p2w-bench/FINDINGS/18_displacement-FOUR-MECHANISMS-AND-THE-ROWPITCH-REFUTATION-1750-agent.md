# GOOGLE MOVES TEXT — what the displacement actually is, on which construct, in how many documents

**23 Nov 2026 · measurement run · repo `kavopdf/app` cloned to `/scratch/work/CS` · engine built from
that clone with `tools/p2w-bench/build-engine.sh` (38 s) · corpus fetched whole (`corpus-v1`, 213/213
PDFs) · all 213 converted with `ConvertAll` · no commit, no push, no engine change**

---

## 0. First, a correction about the data the brief described

The brief says *"`benchmarks/gverify/*.json` holds the Google render of each document (per-check
verdicts **and text positions**)"*. It does not. I read all 213 files: the key set is exactly
`name, status, engine, rc, passed, total, failed, pages, want` (and on 8 files
`engine_fingerprint, export_sha256, measured, method`). There are **no positions and no per-check
`checks` block**. `gverify-lo/*.json` is richer (`checks` with counts, plus a `47_margins` detail) but
it also carries **no run positions** — `18_displacement` appears there as `{"source": 0, "render": 0}`,
two integers. No `.docx` and no exported Google PDF is in the repository either (`find -name '*.pdf'`
finds 5 source PDFs and fixtures only).

So a per-run Google `dy`/`dx` histogram cannot be *read* from this repo. What I did instead, and what
each number below rests on:

| layer | source | status |
|:--|:--|:--|
| Google verdicts, 190 scored documents | `benchmarks/gverify/*.json` | read |
| LibreOffice verdicts, 190 | `benchmarks/gverify-lo/*.json` | read |
| the **construct census** (anchored shape / framePr / table / textbox / columns / spacer / page break) over all 190 | **measured this run** on the 190 `.docx` this clone emits | measured |
| per-page `w:before` after every page break, per-document row excess | **measured this run** from those `.docx` | measured |
| the **displacement histogram** | the live Google round trips already recorded in `tools/p2w-bench/FINDINGS/` (35 page/document medians with provenance), re-tabulated here | recorded, attributed per row |
| the LibreOffice control (per-run `dy`, 101 documents, 12,308 pairs) | **measured this run**, soffice + `verify_google.py`'s own matcher | measured |
| predicted `dy` for all 101 | the two laws the repo has measured (spacer × 0.78; page-top gap × 1.0), applied to the `.docx` this clone emits | derived, labelled |

Every table below says which of these it is. I did not drive Google: no credentials, and the binary
ingress paths are blocked in this pod (recorded in `18_displacement-PAGE-SHIFT-CENSUS-1015-agent.md`
§"Not measured").

---

## 1. Population, recomputed from the JSONs (not from the class table)

    213 JSON files;  190 carry per-check verdicts;  190 have a LibreOffice twin
    101 fail 18_displacement in Google          (the class table says 101 ✓)
     20 fail 18_displacement in LibreOffice     (the class table says 20 ✓)
     18 of the 101 fail it in both renderers    → 83 are Google-only
     30 pass all 42 checks in Google            (the class table says 30 ✓)

The class table's "fixed-in-LO-only 81" and my 83 differ by 2 documents: the table counts
`fixed-in-LO-only` against its own open/fail arithmetic, I count `fail-G-and-pass-LO` directly. The
difference does not move any conclusion below.

**The class is therefore two populations, and they are not the same question:**

* **83 documents** are displaced in Google and placed correctly by LibreOffice on the same `.docx`.
  That is the renderer reading our construct differently. This is the population the brief asks about.
* **18 documents** are displaced in both. Those are engine placement errors (the engine put the text
  in the wrong place), not a Google construct. They are counted separately below and should not be
  chased with a Google-shaped fix.

---

## 2. The displacement histogram

### 2.1 What one displacement looks like

`18_displacement` is **vertical only**: `dy = render_ry − src_ry`, tolerance
`clamp(0.35·size, 1.5, 4.5)` pt, page fails when `n_out > max(2, ceil(0.05·n))` or every run is out or
one run is beyond `2×tol` (`verify_google.py:5723-5754`). There is a separate horizontal check
(`43_within_10pt_x`); **no recorded Google measurement in this repo carries a `dx`**, so the horizontal
component of this class is *not stated* by any evidence I have. Everything measured is `dy`, and
`dy < 0` means the text is drawn **higher on the page than the source put it**.

The shape, from the 28-page probe in `18_displacement-dy-shape-101323-4fa7.md` (live Google, the
check's own pairing code): on every page `dy` fits `dy = a + b·y` with **residual sd 0.0–5.5 pt** while
`|a|` is tens of points. So a page is displaced **as a block**, not per run: SCATTER was 0 of 28 pages,
FIRST-LINE/HEADER-OFFSET 0 of 28. `|dy|` is **constant in points, not proportional to type size** —
on `bank-statement-5-pages` p1 a 6.0 pt line and a 13.0 pt line both move −56 pt
(Pearson(|dy|, size) −0.68…+0.16 across the 28 pages). That is the signature of a *length* being
dropped, not of a font metric.

### 2.2 Histogram of the measured Google displacement

35 page-level or document-level medians, all from live Google round trips recorded in `FINDINGS/`
(the 28 per-page medians of `dy-shape`, plus `68_journal`, `73_marksheet`, `41_coloured`,
`362_price_list_dense` as-emitted, `16_right_aligned`, `31_times`, `72_bank` from
`table-spacer-CONFIRMED-1005` / `ELEVEN-NON-RULED-2354`).

    |median dy| (pt)   n   ####################################   which
    ----------------------------------------------------------------------------------------
     0 –  2            3   ###                                    16(+0.2), 71(+1.06), 72(+1.18)
     2 –  5            6   ######                                 41(−4.13), 370, 52, bank p0,
                                                                  362(−2.78 post-fix), +2.62(31)
     5 – 10            2   ##                                     302(−8.9), gst p0(−8.6)
    10 – 20            9   #########                              324 p0(−14.1) + p1–p5(−19.4),
                                                                  324 p6(−13.8), 362(−13.59),
                                                                  73(−12.85)
    20 – 40            0                                           ← the gap
    40 – 50            1   #                                      table-across p1(−48.5)
    50 – 70           13   #############                          602 ×2(−67.6), academic(−60.2),
                                                                  bank ×4(−56.9…−57.1), vlsct ×2,
                                                                  gst ×3, table-across p2
    70 –120            1   #                                      68_journal(−114.28)

    median |dy| of the 35 = 33.9 pt;  21 of 35 are ≥ 40 pt;  32 of 35 are negative (up the page)

**This is bimodal, with an empty bin at 20–40 pt.** Two clusters: a small-offset cluster (11 of 35,
|dy| < 20 pt) and a large one (14 of 35, |dy| 48.5–67.6 pt, plus 68_journal at −114). A distribution
with a hole in it is the strongest single piece of evidence in this report: **the large cluster is one
construct with a narrow natural range, and it is not a continuum of "Google being a bit different".**

The 48.5–67.6 pt band is not a coincidence and it is not a quantum of layout: it is **the page's own top
gap**, and it is a different number in every document (55.15 in `bank-statement`, 69.50 in `602`,
59.65 in `academic-paper`, 51.15 in `gst-invoice`, 49.15 in `table-across`). The band is the *range of
top gaps* in the corpus, not a fixed step. The single fixed quantum in this class is elsewhere — see
§3.3.

### 2.3 Direction and block boundary — which runs move

From `68_journal_wide_table_spanning` (live Google, `table-spacer-CONFIRMED-1005`): runs **above** the
table spacer read **+0.09 pt**, every run **below** it reads **−114.3 to −115.0 pt**. 61 of 74 runs out.
One boundary, everything under it moves, nothing above it moves. The same boundary is visible on
`302_radiology` (header 3 runs −1.6…−2.8, table and footer −8.9…−9.9 — the *header* is the part that
did not move) and on `gst-invoice` p1 (−52.1 header → −65.8 table head → −56.9 foot).

**So "which runs moved" is answerable structurally and generally: every run below the construct.** The
class is a block displacement of the flow, anchored at the construct.

### 2.4 The whole set, predicted (derived, not measured)

Applying the two measured laws to the `.docx` this clone emits gives, over the 101:

    predicted |dy|       n
    0 –  2 pt           39
    2 –  5 pt            7
    5 – 10 pt            7
    10 – 25 pt          25
    25 – 60 pt          14
    60+ pt               9
    median              9.6 pt

39 of the 101 are predicted under the check's own 4.5 pt ceiling — i.e. the class is *not* 101 uniform
failures; about a third of it is a small residual and about half is a block move of 10 pt or more.

---

## 3. Is the displaced text placed explicitly, or is it flow text Google re-flowed?

**Flow text. Overwhelmingly, and this is not close.**

Measured over the 101 failing documents, from their own `word/document.xml` (this run):

| carrier | characters | share |
|:--|--:|--:|
| inside `<w:tbl>` (table cell flow) | 93,326 | 44.8 % |
| inside `<w:txbxContent>` (an anchored shape's text box — *explicit* placement) | 4,764 | **2.3 %** |
| plain body paragraphs (flow) | 110,230 | 52.9 % |

**97.7 % of the text in these documents is flow.** And the engine does not use the two constructs that
would make it explicit placement:

| construct | documents emitting it (of 190) |
|:--|--:|
| `<w:framePr>` (a text frame — explicit position) | **0** |
| `<w:cols w:num="2">` or any multi-column section | **0** |
| `<w:drawing>` with `<wp:anchor>` | 174 |
| `<w:txbxContent>` (text inside an anchored shape) | 54 |

Anchored shapes are ubiquitous (174 of 190, including 26 of the 30 clean documents) but they carry
**rules, images and stamps**, not body text: 2.3 % of characters. They are not where the displacement
lives, and §4 shows they do not discriminate at all.

The mechanism is the same statement from the other side: the construct that moves the text is an
**empty paragraph carrying a gap** (or a gap on the page's first paragraph). Nothing in this class is
"we put it at x=120 and Google put it at x=0". It is "we wrote a vertical gap in a property Google
does not read as a length, and Google laid the flow without it".

**Consequence for the fix, stated plainly:** the answer is *not* "place it differently" (there is
nothing to place — 0 `w:framePr`, and `google_safe.py` records `w:framePr`, `w:drawing`, `wp:anchor`
and `w:position` as constructs Google ignores anyway). It is **"stop expressing vertical distance in a
property Google does not honour as a length"**, which is a one-property change per construct.

---

## 4. The construct census: failing (101) vs clean (30)

Presence of each construct in the `.docx` this clone emits, cross-tabulated against the recorded Google
verdict. **All counts measured this run.**

| construct present | fails 18 (n=101) | clean (n=30) | fail-rate vs clean-rate | verdict |
|:--|--:|--:|:--|:--|
| `w:pgMar w:top="0"` | 101 | 30 | 1.00 vs 1.00 | universal, **no information** |
| any `<wp:anchor>` | 94 | 26 | 0.93 vs 0.87 | **no discrimination** |
| any `<wps:wsp>` | 94 | 25 | 0.93 vs 0.83 | no discrimination |
| any `<w:tbl>` | 90 | 10 | 0.89 vs 0.33 | weak |
| `w:trHeight … hRule="atLeast"` | 88 | 8 | 0.87 vs 0.27 | weak |
| `<w:framePr>` | 0 | 0 | — | **engine never emits it** |
| `<w:cols w:num>1>` | 0 | 0 | — | **engine never emits it** |
| any `<w:txbxContent>` | 23 | **0** | 0.23 vs 0.00 | **perfect specificity, 23 % coverage** |
| any `<w:br w:type="page"/>` | 16 | **0** | 0.16 vs 0.00 | **perfect specificity, 16 % coverage** |
| **a spacer paragraph carrying ≥ 2 pt in `w:line`** | **53** | **0** | **0.52 vs 0.00** | **the discriminator** |

Three constructs are present in **zero** clean documents and in 71 of the 101 failing ones. Their
union covers **71 of 101 failing and 0 of 30 clean**:

    53  spacer in w:line (≥2 pt)          — 0 clean
    16  page break (gap on the next page's first paragraph)  — 0 clean
    23  textbox                          — 0 clean
    ---- overlap: 21 documents carry two of the three
    union 71 / 101 failing,  0 / 30 clean
    residual 30 failing documents carry none of the three (and 30 clean carry none either)

That is the split the brief asked for, and it is clean: **no clean document in the corpus carries any of
the three constructs.** The 30 residual failures are not "the same thing but smaller"; they are a
population the three constructs do not touch.

### 4.1 The spacer is bimodal in the documents themselves

`w:line` value of the largest spacer paragraph, in points:

    0.05 pt (a 1-twip hairline = no gap)   48 failing   30 clean
    0.5 – 2.0 pt                            0 failing    0 clean     ← nothing here
    2.0 – 5.0 pt                            9 failing    0 clean
    5.0 – 10 pt                            10 failing    0 clean
    10 – 20 pt                             25 failing    0 clean
    20 – 50 pt                              5 failing    0 clean
    50 – 144 pt                             4 failing    0 clean

The engine writes either no spacer or a real one; **every document with a real gap fails in Google and
no document without one does**, except the 30 residual. At HEAD the emission is already guarded: the gap
is split into `w:before` (which Google honours 1:1) **only where the page has room**, and the refused
case falls back to the whole gap in `w:line` (`DocxWriter.java:6097-6103`). The 53 documents are
**exactly the refusals.**

### 4.2 Dose-response, which is the part that identifies the construct rather than correlating with it

The fraction Google buys of a `w:line="G"` exact gap on a 1 pt mark is ~22 %, so the loss is ~0.78·G.
Measured, live Google, four documents spanning a factor of 41 in the written value:

| document | gap written (pt) | 0.78 × written | measured median `dy` |
|:--|--:|--:|--:|
| `41_coloured_headings_white_bg` | 3.50 | −2.7 | **−4.13** |
| `73_marksheet_subject_marks_grade` | 16.70 | −13.0 | **−12.85** |
| `362_price_list_dense` | 13.80 | −10.8 | **−13.59** |
| `68_journal_wide_table_spanning` | 144.0 (capped; page draws 148.07) | −112.3 | **−114.28** |

and the same paragraph rewritten as `w:before` instead of `w:line`:

| document | as emitted | as `w:before` |
|:--|--:|--:|
| `362_price_list_dense` | −13.59 | **−2.78** |
| `68_journal_wide_table_spanning` | −114.28 | **−3.08** |

That is a dose-response with the sign, the magnitude **and the block boundary** all matching, and a
one-property intervention that removes it. This is not a correlation.

### 4.3 The page-break construct, validated across 8 documents

The engine carries a page's top gap as `w:before` on the first paragraph after `<w:br w:type="page"/>`.
Google **drops it entirely** at the top of a page (controlled probe: 55.15 pt asked → **0.33 pt**
rendered; LibreOffice 56.80). I extracted that `w:before` from the `.docx` this clone emits and compared
it to the recorded live-Google page `dy`:

| document | my HEAD docx: gap after break (pt) | recorded Google page dy (pt) | residual |
|:--|--:|--:|--:|
| `one-page-rotated-180-degrees` p2 | 54.85 | −56.20 | −1.4 |
| `bank-statement-5-pages` p1–p4 | 55.15 | −56.9, −57.1, −57.1, −57.1 | −1.9 |
| `602_bookmarked_annual_report` p1–p2 | 69.50 | −67.6, −67.6 | +1.9 |
| `academic-paper-ieee-2col-abstract` p1 | 59.65 | −60.2 | −0.6 |
| `very-long-single-column-table` p1–p2 | 60.50 | −58.4, −60.4 | +1.1 |
| `table-across-page-break…` p1–p2 | 49.15 | −48.5, −54.2 | −2.2 |
| `324_loan_amortisation_schedule` p1 | 11.50 | −19.4 | −7.9 |
| `gst-invoice-multipage-item-table` p1–p3 | 51.15 | −61.8, −61.0, −64.3 | −11.2 |

Six of eight land within ±2.2 pt; the two larger residuals are documents where a table-head step or a
row-pitch term rides on top. **The page's own top gap is the number, not a constant** — which is why the
band looks like 48–70 pt and why no single "quantum" explains it.

---

## 5. How many mechanisms, and how many documents each

Exclusive assignment, priority spacer → textbox → page break (a document counts once):

| # | mechanism | construct, in one line | documents | of which Google-only | worst measured/predicted |
|--:|:--|:--|--:|--:|--:|
| **M1** | **table-gap spacer spent in `w:line`** | empty `<w:p>` whose whole height is `w:line="G" lineRule="exact"` under a 1 pt mark; Google buys ~22 % of G | **53** | 43 | −114.3 (68_journal, measured) |
| **M2** | **page-top gap carried as `w:before` after a page break** | first paragraph after `<w:br type="page"/>` carries the gap in `w:before`; Google drops it at a page top | **7** exclusive (**16** carry a break) | 16 | −67.6 (602, measured) |
| **M3** | **text placed inside an anchored shape's text box** | `<wp:anchor>` + `<w:txbxContent>`; 10 of the 23 also fail `59_shape_anchor` | **11** exclusive (**23** carry textboxes) | 20 | not measured per-run |
| **M4** | **table row pitch / row growth** — *not one construct* | `w:trHeight hRule="atLeast"` rows laid by Google on a 0.75 pt ladder, +1 quantum, so every row is 0.75–1.5 pt taller than declared and the error accumulates down the table; plus first-row cell `w:before`, plus block placement offsets | **30** | 22 | 8 of the 30 also fail in LibreOffice |
| | | | **101** | **83** | |

Overlap, measured: 12 documents carry a spacer **and** a textbox, 7 carry a spacer **and** a page break,
2 carry a page break **and** a textbox; 21 carry two of the three and none carries all three. The
per-mechanism columns above therefore sum to more than 101 — the exclusive column does not.

Notes that matter:

* **M1 and M2 are two arms of one design decision** (a vertical gap carried in paragraph spacing) but
  they are **two different renderer behaviours** and need **two different fixes**. M2's fix is measured
  (below); M1's fix is implemented and blocked.
* **M4 is genuinely several mechanisms.** The repo has already separated it once
  (`ELEVEN-NON-RULED-2354`: group A spacer 6, group B row growth 2, group C placement 3) and once more
  (`SEVEN-LO-ONE-CHECK-0630`: seven documents, seven mechanisms — three whole-block placement offsets,
  three localised bands, one page-wide small offset). My census reproduces that: 27 of the 30 carry a
  table with `atLeast` rows, median 8 rows, median row excess **6.5 pt**, and 8 of the 30 fail in
  LibreOffice too, i.e. they are engine placement errors rather than Google reading errors.
* **M3 is "explicit placement"** — the only mechanism in the class that is. It is 11 documents, 11 % of
  the class, and 10 of those 23 documents also fail `59_shape_anchor`, which suggests the text moves
  with the shape's frame and is better attacked as a shape-anchor problem than as a displacement one.

---

## 6. Per-document worst displacement, and the worst offenders

Predicted `dy` for all 101 from the two laws applied to the `.docx` this clone emits
(`max(0.78 × spacer, gap-after-break)`), with the recorded Google number where one exists:

| document | predicted | measured (Google) | spacer pt | gap after break | rows / row excess | LO worst |
|:--|--:|--:|--:|--:|--:|--:|
| `330_cad_drawing_sheet` | −112.3 | — | 144.0 (capped) | – | 12 / 8.8 | 51.6 |
| `360_restaurant_menu` | −112.3 | — | 144.0 (capped) | – | 12 / 11.0 | 31.7 |
| `68_journal_wide_table_spanning` | −112.3 | **−114.28** | 144.0 (capped) | – | 7 / 3.5 | 3.4 |
| `416_many_tiny_pages` | −89.5 | — | 0.05 | **89.5** | 0 / 0 | 4.4 |
| `57_centred_title_page_left_body_pages` | −69.5 | — | 0.05 | **69.5** | 0 / 0 | 1.6 |
| `602_bookmarked_annual_report` | −69.5 | **−67.6** | 0.05 | **69.5** | 0 / 0 | 4.1 |
| `412_page_labels_roman` | −61.4 | — | 0.05 | **61.4** | 0 / 0 | 3.8 |
| `417_rotate180_and_mirrored` | −61.4 | — | 0.05 | **61.4** | 13 / 8.1 | 4.3 |
| `very-long-single-column-table` | −60.5 | **−59.4** | 11.8 | **60.5** | 99 / 64.2 | 1.0 |
| `academic-paper-ieee-2col-abstract` | −59.6 | **−60.2** | 0.05 | **59.6** | 6 / 3.8 | 1.4 |
| `374_org_chart` | −58.3 | — | 74.8 | – | 3 / 2.5 | 4.5 |
| `bank-statement-5-pages` | −55.1 | **−57.0** | 16.2 | **55.1** | 125 / 81.2 | 1.0 |
| `one-page-rotated-180-degrees` | −54.9 | **−56.2** | 0.05 | **54.9** | 13 / 8.1 | 1.0 |
| `balance-sheet-and-profit-loss` | −52.0 | — | 6.4 | **52.0** | 47 / 30.8 | 0.9 |
| `gst-invoice-multipage-item-table` | −51.1 | **−62.4** | 20.3 | **51.1** | 42 / 27.5 | 2.0 |
| `form16-part-b` | −50.0 | — | 8.3 | **50.0** | 31 / 20.2 | 1.8 |
| `mutual-fund-statement` | −49.1 | — | 6.2 | **49.1** | 31 / 20.2 | 1.5 |
| `table-across-page-break-repeated-header` | −49.1 | **−51.4** | 12.2 | **49.1** | 45 / 29.5 | 1.0 |
| `25_signature_block_underscores_txtpos` | −48.9 | — | 62.6 | – | 10 / 8.5 | 4.0 |
| `58_header_rule_footer_rule` | −47.5 | — | 0.05 | **47.5** | 0 / 0 | 1.1 |

**The largest absolute displacements in the class are the three documents whose spacer hits the engine's
2880-twip cap** (144 pt written, ~112 pt lost). `68_journal` is measured at −114.28 and is the worst
measured displacement in the class; the two others are predicted at the same value and have never been
through Google on HEAD.

**LibreOffice control, measured this run on the same 101 `.docx`:** 12,308 matched pairs, **556 out of
tolerance (4.5 %)**; worst per-document |dy| median **1.58 pt**, p75 2.74, p90 4.38, and only 10
documents above the 4.5 pt ceiling: `330_cad` 51.6, `360_restaurant_menu` 31.7, `71_invoice_space_aligned`
24.4, `itr-computation` 14.3, `75_merged_header_cell` 12.3, `table-inside-two-column-page` 9.1,
`03_stamp_vertical_90deg` 6.3, `374_org_chart` 4.5, `600_reviewed_invoice` 127.9 and
`601_fillable_admission` 229.8 (the last two are annotation/field artifacts). **The same bytes are placed correctly by a renderer that reads these properties as lengths.**
That is the whole case: nothing in our placement is wrong; one property is being read differently.

---

## 7. What to change in `app/`, ranked

All line numbers are this clone's HEAD. File: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`.

### Rank 1 — M2, page-top gap: `sectPrXml` / the page-break emitter. **Measured fix exists, 16 documents.**

`DocxWriter.java:4466` and `:4543` (`topGap = b.y − LINE_BASE·linePt`) put a page's top gap into
`w:before` on the first paragraph after a page break. Google renders **0.33 pt of 55.15**. The
controlled probe (`page-top-before-DROPPED-105000`) measured what Google *does* honour for a length at a
page top: **a 1×1 table row with `w:trHeight w:val="G" w:hRule="exact"` → 55.83 pt of 55.15 asked**
(0.68 pt short, versus 0.33 pt for `w:before`). Two options, in order of evidence:

1. **carry the page-top gap as a 1×1 `w:trHeight hRule="exact"` row** before the page's first paragraph.
   Measured in Google and in LibreOffice (56.80 / 55.83). Cost: an extra table per page break, and it
   interacts with `60_text_column_right_edge` (a 1-cell table spans the text column).
2. put the gap in `w:pgMar w:top` on a per-page section (`sectPrXml` at `:2389/:2402`, where `w:top="0"`
   is the hard-coded literal at `:2411`). This is what `PAGE-SHIFT-CENSUS-1015` recommends, and it is
   **untested in Google** — the probe tested `w:before`, `w:line`, and `w:trHeight`, not `w:pgMar`.

Expected reach: 16 documents carry a page break and all 16 fail; the 7 with no other construct go clean,
the other 9 lose their largest term (their page-1 residual remains).

### Rank 2 — M1, the refused table spacer: `emitTable`, the `spacerTw > 0` branch. **53 documents, fix implemented and blocked.**

The guarded split at `:6089-6103` spends the gap as `w:before` only when
`ctx.spacerSplitTw + (spacerTw−20) + 15·pageRowCount ≤ slack`; otherwise it writes the whole gap back
into `w:line` and Google drops 78 % of it. **The refusal is not a rendering question, it is an
arithmetic one: the guard reserves `15 · pageRowCount` twips for row growth that the guard itself
predicts.** The single highest-value change is therefore not to the spacer arm at all but to make that
reservation unnecessary — see Rank 3 — or to charge the row excess at its measured value rather than at
the flat 0.75 pt/row.

**Do not re-try** (both refuted by live Google measurement, see §8): partial spend, and any change to
the spacer that leaves it in `w:line`.

Expected reach if unblocked: 53 documents carry a refused spacer; the recorded probe on 16 of them took
6 to 42/42 and a later probe took `mobile-bill` and `table-with-no-header-row` to 47/47, so the realistic
prize is 6–10 documents plus the removal of the 112 pt outlier on three documents.

### Rank 3 — M4, row pitch: `emitTable` row emission (`w:trHeight`, ~`:6228`/`:6318`). **30 documents, and it is the blocker for Rank 2.**

The measured law (`ROW-GROWTH-075`, 11 independent points) is
`laid = 0.75·(round(declared/0.75) + 1)` pt — Google snaps the declaration to a 0.75 pt ladder and adds
one quantum. Consequences, both measured:

* a declared 18.00 lays 18.75, a declared 19.00 lays 19.50 — so **every row is 0.75–1.5 pt taller than
  we asked for**, and the excess accumulates: median 6.5 pt over the 30 residual documents, 81 pt over
  `bank-statement-5-pages`, 64 pt over `very-long-single-column-table`;
* declaring the source pitch (18.40) with `exact` lays **19.50** and adds `23_line_pitch` — the document
  gets worse (`ROW-PITCH-LAW`, three builds, three round trips);
* declaring `source pitch − 0.75` with `exact` lays 18.00 for a source 18.40 — the best achievable, and
  **still 0.40 pt/row**, which is 5.2 pt over 13 rows and still fails.

**The honest statement: this mechanism has a floor.** Laid pitches are only multiples of 0.75 pt, so a
source pitch that is not on the ladder cannot be matched, and no declaration fixes it. The fix that
*does* exist is to declare the rung below (`d = 0.75·round(P/0.75) − 0.75`) so the error is ≤0.375 pt
and always in the same direction instead of 0.75–1.5 pt; that reduces the accumulation by roughly 2×
and frees the `15·rowCount` twips the Rank-2 guard is withholding. It will not take the 30 to clean.

### Rank 4 — M3, text inside anchored shapes: `anchorShape` (see `anchorClamped`, `:180`). **11 documents.**

Text inside `<w:txbxContent>` moves with the shape's frame, and 10 of the 23 textbox documents also fail
`59_shape_anchor`. Treat this with the shape-anchor class, not here: the displacement is a symptom of the
enclosing rectangle being placed differently, and a displacement-shaped patch will not move it.

### Rank 5 — the 18 engine-side documents.

18 of the 101 fail in both renderers. No Google construct will reach them. They are placement errors in
`flowFromBox`/`flowTopPt` and belong to whoever owns the LibreOffice table.

---

## 8. What is already refuted — do not spend a run on these

Every item below is a live Google measurement recorded in `FINDINGS/`, not an opinion:

| idea | status | where |
|:--|:--|:--|
| **dither** on `w:trHeight` (alternate ±0.75 to average the pitch) | refuted — inert in Google, a 0.75 pt/row regression in LibreOffice | `DITHER-REFUTED-0030`, `WAIVER-EXISTS-174500` |
| **partial spend** of the spacer (`min(want, slack)` in `w:before`, rest in `w:line`) | refuted — `68_journal` 41→40 and it breaks `59_shape_anchor` | `PARTIAL-SPEND-REGRESSES-GOOGLE-1428` |
| the gap belongs in **`w:pgMar w:top`** and page-1 text moves with it | refuted — Pearson(before, page-1 dy) = +0.078 over 0–141.5 pt, slope +0.011 | `PAGE-SHIFT-CENSUS-1015` |
| **`hRule="exact"` at the source pitch** pins the row | refuted — declared 18.40 lays 19.50 and adds `23_line_pitch` | `ROW-PITCH-LAW-135800` |
| the class is **rule count** (≤4 rules) | refuted — `16_right_aligned` draws 17 rules and `balance-sheet` 5 | `ELEVEN-NON-RULED-2354` |
| the displacement is **proportional to font size** | refuted — flat across 6–13 pt on one page | `dy-shape-101323` |
| the displacement is **scatter** | refuted — `dy = a + b·y`, residual sd 0–5.5 pt on 28 pages | `dy-shape-101323` |
| a **LibreOffice-side** fault | refuted — same `.docx`, `n_out = 0` on all 28 pages, and 4.5 % of runs this run over 101 documents | `dy-shape-101323`, this run |
| "the spacer is refuted" (`SPACER-REFUTED-0900`) | **itself refuted** — that screen rendered with soffice, which honours `w:line` as a length, so it could not see the change | `table-spacer-CONFIRMED-1005` |

---

## 9. What would change my mind

* **A clean document carrying a real spacer or a page break.** None of the 30 does; if one appeared the
  perfect-specificity claim in §4 is dead.
* **A Google render of any of the 53 spacer documents on HEAD showing `dy` far from `−0.78 × spacer`.**
  The law is 4 points of dose-response plus 2 intervention pairs; a document at −20 with a 60 pt spacer
  would break it.
* **A page-break document whose page 2 does not move by its own top gap** (the 8-document table in §4.3,
  residual ≤2.2 pt on six).
* **`w:pgMar w:top` measured in Google** — that would move Rank 1 from option 2 to option 1. It has
  never been probed.
* **The 30 residual splitting differently** — they are the part of this class I have counted but not
  explained, and the repo already contains two contradictory statements about the row declaration
  (`ROW-GROWTH-075`'s ladder law, which makes the declaration causal, versus `GOOGLE-IGNORES-TRHEIGHT`'s
  "the declaration is inert"). I did not resolve that contradiction; Rank 3 rests on the ladder law,
  which has 11 points behind it, and the resolution is a one-document probe.

---

## 10. Open questions

* **No Google render of the 53 spacer documents exists on HEAD**, so their `dy` is derived, not measured.
  The 6-document and 4-document probes were run on earlier builds.
* **`dx` is not stated anywhere** for this class. The check is vertical only; no recorded measurement
  carries a horizontal component.
* **M4's internal split** (how many of the 30 are row growth, how many first-row `w:before`, how many
  block placement) cannot be settled from the JSONs — it needs a per-run `dy` from Google on those 30,
  which this pod cannot obtain.

---

## 11. Reproduction

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
gh release download corpus-v1 --repo kavopdf/app --pattern '*' -D /scratch/work/cache
# unpack flat into /scratch/work/corpus, add benchmarks/corpus-extra + benchmarks/realworld
bash /scratch/work/CS/tools/p2w-bench/build-engine.sh          # 38 s, fetches its own JDK
cd /scratch/work/CS/tools/engine-verify && java -Xmx700m -cp \
  "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
  ConvertAll /scratch/work/corpus /scratch/work/docx            # 213/213, 0 failed
```

Scripts written for this run (in `/scratch/work`): `census_struct.py` (construct census, writes
`struct.csv`), `pages.py` (per-page `w:before` after each break, row excess), `lo_dy.py` (soffice render
+ per-run `dy`/`dx` via `verify_google`'s own `pairs`).

No commit, no push, no engine change. 0 Google Docs created — this run had no Drive credentials and
every Google number here is quoted from `FINDINGS/` with its file named.
