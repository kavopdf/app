# Route (c) — a two-column band as one tabbed paragraph per baseline

**Branch:** `proto/col-rows-tabs` (commit `736011e`), cut from `main` at `8d5a3eb`.
Not merged, not pushed. `main` is untouched.
**Patch:** `route-c-col-rows.patch` (308 insertions, 6 deletions, one file).

**Verdict: route (c) works on the document that motivated it and does not break
pagination anywhere in the corpus. It is a real win, and a narrower one than the
brief hoped for.**

---

## 1. What changed — file and function

One file: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`.

The mechanism is `flowRow` (≈ line 3546), unchanged. Route (c) is a *front end* that
gives `flowRow` something to write: it re-cuts a page's block list so that one
paragraph exists per baseline, holding that baseline's boxes from both columns.
`para()` then sees a multi-box paragraph on one baseline, `isRow()` returns true, and
the existing `flowRow` writes it as one paragraph with a `w:tab` per column at the
measured x.

New code, all private static, all in `DocxWriter`:

| symbol | what it does |
|---|---|
| `COLUMN_ROWS` / `p2w.colrows` | the flag, **on by default**; `-Dp2w.colrows=false` gives the exact "before" from the same binary |
| `COLUMN_ROW_TOL` (2.0 pt) | how far apart two boxes may be and still be one row |
| `columnRowBlocks(page, pw)` | returns the page's block list with each *run* of column lines re-cut. Never edits `page.blocks` — the budget guard writes a page several times and every pass must see the same document |
| `columnLineHome(block, edge, n)` | is this block one line of one column. Box extent, not the column tag (a masthead can carry the last band's tag) |
| `taggedColumnEdges(page, pw)` | the column left edges, median per band from the column pass's own tags |
| `columnRowsOfRun(out, blocks, from, to)` | the run, flattened to boxes, sorted by (y, x), grouped by baseline |
| `copyBoxAt(box, y)` | one field of a row, copied onto the row's baseline (boxes are shared with the document, so they are copied, not edited) |
| `textLen(box)` | the row-baseline heuristic (see §5) |

Hook point: one line in `pageBody()` (≈ 1363), immediately after `columnPage()`
refuses:

```java
if (columnPage(sb, page, ctx, pw)) { ...; return; }
java.util.List<Object> blocks = columnRowBlocks(page, pw);
```

and the emit loop iterates `blocks` instead of `page.blocks`.

**Why this is the right hook.** A page that `columnPage()` accepts is already written
as a fixed-geometry layout table — no anchored boxes, nothing for route (c) to do.
Route (c) is for the pages `columnPage()` *refuses*, which are exactly the pages that
fall back to one anchored text box per line. On `policy-2col-spanning-section-heading`
the refusal is `straddles-gutter`: a full-width section heading sits *between* the
column bands, which is the one shape a single table cannot describe and a flow of rows
can.

---

## 2. Before / after, per document

`txb` = `<w:txbxContent>` (anchored **text boxes** — the construct Google rasterises).
`pg` = pages in the rendered PDF. `dy` = baseline (span origin) of the rendered line
minus the source PDF's, matched by text. `neg` = lines the engine wrote with
`w:before=0` because the page put them above the running flow (`DocxWriter.Stats.zeroGap`),
i.e. lines that needed a **negative gap**.

Rendered with LibreOffice (`soffice --headless --convert-to pdf`), source read with
PyMuPDF. Google's own render was **not** obtained in this run (no Drive round-trip was
available in the sandbox) — see §6.

### `policy-2col-spanning-section-heading` — the target document

| | before | after |
|---|---|---|
| pages (source 1) | 1 | **1** |
| anchored text boxes | 62 | **2** |
| `wp:anchor` (incl. shapes) | 65 | 5 |
| paragraphs | 130 | 44 |
| tab runs in body | 1 | 27 |
| median \|dy\| | 0.02 pt | 0.02 pt |
| max \|dy\| | 0.08 pt | **0.02 pt** |
| negative-gap lines | 1 (worst 13.40 pt) | **0** |
| lines matched / source lines | 61 / 61 | 61 / 61 |

The two boxes left are the running footer's two fields and the folio — a genuine row
that the page drew at 805 pt, 160 pt below the last body line, and which the gap cap
refuses to spend (unchanged behaviour, and the reason it is anchored rather than
tabbed).

### `69_two_col_legal_numbered_clauses` — second two-column document

| | before | after |
|---|---|---|
| pages (source 1) | 1 | **1** |
| anchored text boxes | 36 | **7** |
| `wp:anchor` | 39 | 10 |
| paragraphs | 84 | 45 |
| median \|dy\| | 0.03 pt | 0.28 pt |
| max \|dy\| | 0.70 pt | 1.72 pt |
| negative-gap lines | 2 (worst 15.39 pt) | **0** |

Position cost here, and it is real: this document's two columns are **not on shared
baselines** (left 156.90 / 167.13 / 177.35 against right 162.61 / 172.84 / 183.06 — a
5.7 pt offset), and a row is one paragraph, which has one baseline. Where the model
puts two fields within `COLUMN_ROW_TOL` of each other but not exactly together, the
row lands on the topmost and the other field moves by that difference: worst 1.72 pt,
median 0.28 pt. Still under the repo's own `TOL_Y_PT = 3.0`, and under 1 pt for every
line but one.

### `66_two_col_footnotes_bottom` — third two-column document

| | before | after |
|---|---|---|
| pages (source 1) | 1 | **1** |
| anchored text boxes | 8 | 8 |
| paragraphs | 38 | 31 |
| tab runs in body | 1 | 8 |
| median \|dy\| | 0.04 pt | 0.03 pt |
| max \|dy\| | 0.66 pt | **0.15 pt** |
| negative-gap lines | 7 (worst 0.52 pt) | **0** |

The band converts (8 tab rows, 7 paragraphs gone, every negative gap gone, max dy
0.66 → 0.15 pt) but the box count does not fall, because all 8 remaining boxes are
the three footnotes, the sign-off block and the running footer — all of them *below*
the columns, all legitimately positioned rather than flowed.

### Two more, for completeness

| document | txb | pages | median \|dy\| | max \|dy\| |
|---|---|---|---|---|
| `magazine-2col-pullquote-spanning` | 37 → 37 | 1 → 1 | 0.03 → 0.03 | 0.55 → **0.08** |
| `65_two_col_full_width_figure_caption` | 25 → 25 | 1 → 1 | 0.04 → 0.03 | 0.66 → **0.18** |

Both converted part of their band (max dy collapses) without losing a box, because
their anchors are the figure's shapes and chart labels, not text boxes.

### Corpus totals (213 documents, same binary, flag off vs on)

| | before | after |
|---|---|---|
| `<w:txbxContent>` | 1037 | **836** (−201) |
| `wp:anchor` (google_safe `--predict`) | 13211 | **13010** (−201) |
| `w:spacing-letter` (google_safe `--predict`) | 300 | 276 |
| documents whose `document.xml` changed | — | 20 of 213 |

`google_safe.py --predict` output, 213 documents, before → after:
`w:drawing` / `wp:anchor` 197 documents, 13211 → 13010 instances;
`w:before-any` 21579 → 21197; `w:spacing-letter` 300 → 276.
(The `w:spacing-letter` fall is a side effect: a merged row goes out with `align=0`
and `flowRow` does not pass the justification stretch, so 24 justified lines lose a
`w:spacing` they had. dx is unchanged on every document, so nothing moved.)

---

## 3. Did pagination hold?

**Yes — on every document whose bytes changed.**

- 20 of 213 documents changed. The other 193 are byte-identical in `word/document.xml`,
  so their rendered PDF is identical by construction and cannot re-paginate.
- All 20 were rendered before and after and their page counts compared:

```
041122-Account_Opening_Form              10 -> 10
Account_Opening_Form_Fillable_filled     11 -> 11
12_stamp_across_page_break                2 ->  2
311_fir_police_form                       1 ->  1
331_pid_diagram                           1 ->  1
343_air_waybill                           1 ->  1
400_comic_page_speech_bubbles             1 ->  1
65_two_col_full_width_figure_caption      1 ->  1
66_two_col_footnotes_bottom               1 ->  1
69_two_col_legal_numbered_clauses         1 ->  1
80_gstin_pan_cin_ifsc_table               1 ->  1
bank-statement-horizontal-rules-only      1 ->  1
bus-timetable-station-left-times-right    1 ->  1
gst-invoice-horizontal-rules-only         1 ->  1
magazine-2col-pullquote-spanning          1 ->  1
marksheet-subject-left-marks-right        1 ->  1
policy-2col-spanning-section-heading      1 ->  1
purchase-order                            1 ->  1
report-2col-table-spanning-both-columns   1 ->  1
table-of-contents-dot-leaders             1 ->  1
```

**pagination changed on 0 of 20.**

This is the result the brief was most worried about, and it did not happen. The
reason is visible in the trace: on `policy-2col` every row is placed with a *real,
positive* `w:before` — 371, 245, 245, 245 … twips, i.e. exactly one pitch — and the
page's total flow after the last body line is 643.22 pt on an 841.89 pt sheet, 198 pt
short of the paper. There is no room problem to have. The failure mode the diagnosis
agent hit ("writing real advance into the page increases its height") is real but it
belongs to pages whose columns are *stacked* — `columnPage()`'s refusal set is
precisely the pages where they are not.

Also checked: no text was lost or duplicated. The word-multiset of the rendered PDF
against the source PDF is identical before and after on every changed document
(`wordΔ` column of the run table is the same in both modes).

---

## 4. What failed, with the measurement

Route (c) did not fail. Two things did, and both are worth carrying forward.

### 4a. The construct loses text when the gutter is not a gutter — measured, then guarded

The first build of the pass took the clearance between two fields on trust. A tab stop
that lands inside the text before it is skipped for the next one, and the field that
should have gone there **wraps** — and a flowed line is written with a hairline
`w:lineRule="exact"` box, so the wrapped field is clipped to nothing and vanishes.
Measured on the first build:

- `table-of-contents-dot-leaders`: rendered lines 45 → 41. The page numbers **108** and
  **141** disappeared from the render (both fields were still present in the .docx —
  the loss was in the layout, not the write).
- `price-list-right-aligned-amounts`: rendered lines 163 → 161. The footer field
  "For orders: sales@kastura.in · +91 20 4890 2211" disappeared.

Fix: a row is only worth tabbing when the gap between two fields is at least **one em
of the type before it plus 1 pt** (the same clearance `flowRow` applies when it pushes
a stop right). Below that the boxes keep the paragraphs they came from. After the
guard both documents are byte-identical to the "before" render and neither is in the
changed set at all.

This is the single most important finding about the construct: **it is safe only where
the columns are far apart.** A form row or a dot-leader line has no gutter and must
never be routed through it. The guard is what makes the pass safe on a 213-document
corpus; without it, 2 of 213 documents lose text.

### 4b. A justified line arrives as one box per word — measured, then excluded

`policy-2col`'s "Absence without approved leave for more than three" is a justified
line whose inter-word gaps the page stretched, so the model carries it as **8 boxes on
one baseline**. The first build re-cut them into 8 paragraphs (the clearance guard
correctly refusing to tab between two words), each with `w:before=0`, charging
7 × 0.65 pt to the flow — which is what turned `zeroGap` from 0 into 7 on this
document. It rendered correctly (494.20 pt in both modes) only because LibreOffice
collapses an exact line box; that is luck, not design.

Fix: a group of boxes that is **one whole paragraph** is emitted as that paragraph,
untouched, and left to `flowRow` — which is what the writer did before this patch.
After the fix `zeroGap` on `policy-2col` is **0** and the paragraph count is 44.

### 4c. What route (c) does not reach (not a failure, a scope statement)

- **Nine corpus documents that are genuinely two-column are already written as layout
  tables** by `columnPage()` and never enter this path (`-Dp2w.debugCols` shows no
  refusal on their pages): `62_two_col_newsletter_pull_quote` (2 boxes),
  `61_two_col_abstract_spanning` (2), `67_two_col_with_sidebar` (2),
  `54_two_column_body_full_width_header_footer` (2), `27_two_column_left_short_txtpos`
  (5), `20_numbered_list_separate_column_txtpos` (9), `63_three_column_brochure` (7),
  `annual-review-2col-uneven-columns` (3), `newspaper-2col-fullwidth-headline` (1).
  There is almost nothing there to win.
- **`price-list-2col-dense-right-aligned`** carries 85 boxes but refuses with
  `no-colleft 1/1` — the column pass never declared it two-column, so the pass does
  not apply. That document is the largest remaining pool of anchored text boxes on a
  two-column-looking page and route (c) cannot reach it without a column-detection fix.
- **`journal-2col-with-footnotes`** refuses with `straddles-gutter` but already carries
  0 text boxes — it flows correctly today and has nothing to convert.
- **`17_three_column_widths_txtpos`** refuses with `not-columns` and carries 2 boxes.
- **`academic-paper-ieee-2col-abstract` (51 boxes) and `magazine-2col-pullquote-spanning`
  (37)** are not converted, because the page enters `ctx.positioned` mode (a gap wider
  than `GAP_CAP_TW`), after which `para()` anchors every line regardless of what the
  block list says. Measured with `-Dp2w.census`: `anchorPos` = 50 of 51 anchors on
  academic page 1 and 36 of 37 on magazine. That mode is set by a wide gap earlier on
  the page, not by route (c), and changing when it is set is a separate, much larger
  change.
- **`65_two_col_full_width_figure_caption`'s** remaining 25 text boxes are the chart's
  own tick labels, series labels and legend — a figure, not a column band — and the
  other 49 of its 74 `wp:anchor`s are the chart's drawn shapes. The band itself does
  convert: paragraphs 71 → 66, tab runs 1 → 6, max |dy| 0.66 → 0.18 pt.

---

## 5. Judgement: is it worth continuing?

**Yes, but as a scoped landing, not as the thing that replaces anchored boxes
corpus-wide.**

For it:
- It removes the anchored box from the *exact* page class the brief named, and it
  removes 62 of 65 on `policy-2col-spanning-section-heading` with the page's position
  **improving** (max |dy| 0.08 → 0.02 pt) and its page count unchanged.
- The two negative-gap lines the engine could not express on that document are gone,
  and the flow's sequence now equals the page's y sequence by construction — the
  property the whole route was argued from, and it holds.
- It costs nothing where it does not apply: 193 of 213 documents are byte-identical,
  20 changed, 0 re-paginated, 0 lost a word.
- The construct is `flowRow`'s own, already in the product, already Google-safe by
  construction (real body text, no drawing). Nothing new is asked of any renderer.
- It is one flag away from off (`-Dp2w.colrows=false`), so it can land dark.

Against:
- The corpus-wide yield is **−201 boxes out of 1037**, and 62 of those are one
  document. Route (c) is not the general answer to anchored boxes; `columnPage()`'s
  layout table already covers most two-column pages, and the `ctx.positioned` mode is
  what stands between the remaining ~90 boxes and the flow.
- On a document whose columns are not baseline-aligned (`69_two_col`) it makes the
  worst line **worse**, 0.70 → 1.72 pt. That is the construct's honest cost: a row is
  one paragraph and a paragraph has one baseline. It is under tolerance, but a
  ratchet on `max |dy|` would refuse it.
- The construct is fragile in a way that is invisible in the XML: the text-loss in §4a
  left both fields in the .docx and only the *render* lost them. Any landing of this
  needs the clearance guard and a render-level text check, not an XML check.

**Recommended next step if this is pursued:** the highest-value follow-on is not more
column work — it is `ctx.positioned`. Route (c) proves that a column band can be
flowed, which means the wide-gap rule that flips a page into anchored mode is now
over-firing on column pages. Relaxing it *for pages whose column bands are written as
rows* would take `academic-paper-ieee-2col-abstract` (51 boxes) and
`magazine-2col-pullquote-spanning` (37) out of anchored mode, which is a bigger prize
than everything route (c) has already delivered. That is a separate patch and it was
not attempted here.

**Not measured, and named so it is not assumed:**
- Google Docs' own render (SSIM / pixel score). The sandbox had no Drive round-trip, so
  every number above is a LibreOffice render. The brief's premise — that Google
  rasterises anchored boxes — is taken from the repo's own findings, not re-measured
  here. The construct-count census is the proxy that says the Google verdict *can*
  have moved; it does not say it has.
- The repo's full pre-commit corpus regression (`regress.py --check`), which needs a
  Google render for every document.
- Writer independence was checked on 40 of 213 documents, not all: `PASS`, every .txt
  byte-identical with and without the .docx write.

---

## 6. How to reproduce

```bash
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/app
cd /scratch/work/app && git fetch origin proto/col-rows-tabs && git checkout proto/col-rows-tabs
bash tools/p2w-bench/corpus-fetch.sh          # 213 PDFs
bash tools/p2w-bench/build-engine.sh

# before / after from the SAME binary
java ... -Dp2w.colrows=false ConvertAll  ...  # -> out-before
java ... -Dp2w.colrows=true  ConvertAll  ...  # -> out-after

soffice --headless --convert-to pdf --outdir rp-after out-after/*.docx
python3 tools/p2w-bench/google_safe.py --predict
```
