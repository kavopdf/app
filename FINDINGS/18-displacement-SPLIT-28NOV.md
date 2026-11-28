# `18_displacement`: the 19 solo documents split into 6 row-accumulation carriers and 13 that are not, and the collectable subset is 0

**28 Nov 2026 · read-only investigation · repo `kavopdf/app` cloned `--depth 1` at HEAD
`bcc0ea0c532e3ccf9813562967aa5ddba7a441da` (2026-11-28 04:25:41 +0000) · engine compiled and all 19
`.docx` built on this pod · no engine file edited, nothing committed, nothing pushed, nothing deleted.**

**The answer, in one paragraph.** The 19 documents that fail `18_displacement` and nothing else are
**all single-page**, and the store keeps no per-page number for them (only `med_dy`, `worst_dy`,
`med_dx`, `bad_pages=[0]`, `runs_matched` — `benchmarks/gverify/*.json`). **Six of them carry a table
of 20+ rows and their stored `|med_dy| / rows` lands inside the per-row excess already measured in
Google (+0.10, +0.13, +0.50 pt/row) — those are table-row accumulation and are uncollectable by the
record's own ten-variant test.** The other **13 do not have the rows to accumulate to tolerance** (12 of them carry ≤ 18 rows; the 13th,
`306_clinical_protocol_synopsis`, carries 20 and its `|med_dy| / rows` is 0.02), and on those the engine's
row geometry is **faithful to the source to the twip** (declared `w:trHeight` equals the source row pitch
on 13 of the 19, and is 0.36-0.52 pt *under* on the other 5 — a deficit that is inert because Google does
not read `w:trHeight`). **11 of the 13 already have
`|med_dy|` inside their own tolerance and fail only the check's 5 % count clause**, at the smallest type
on the page. So the collectable subset of the 19 is **0**, and one specific engine change *is* named
below (§6) — the only construct in the class that is traceable end to end — with its measured expected
effect of **−61.2 pt of `worst_dy` on 1 document and 0 documents collected.**

Every number below came from a file on this pod or a named file in the repo; the artefacts are in §8.

---

## 1. The population, measured

`benchmarks/gverify/*.json` read with `failed == ["18_displacement"]` returns **19**; the store's own
counter agrees:

```
$ python3 tools/p2w-bench/classpick.py --leverage
  18_displacement                47.1
     19  18_displacement
```

All 19 carry one engine stamp, `a05b20eb05fe0fc8`, and `bad_pages == [0]` on all 19, i.e. the failing
page is page 0 and it is the only page. Built at HEAD, all 19 report `pages=1` from `ConvertOne`, and the
source PDFs are 1 page each (`PyMuPDF len(doc)`), so **page count 1 is triple-sourced: source, build,
store.**

**Per-page vertical delta.** The store has no per-page figure — `gverify.py` persists only the check's
`detail` dict, and `verify_google.py` reduces the per-run list in-process. Because every document is one
page, the stored document median *is* the page delta. That is the column `med_dy` below, and it is the
only vertical number the store holds.

## 2. The 19, with the two views that decide the classification

| # | document | pages | largest table (rows) | total rows | source row pitch (pt) | declared `w:trHeight` (pt) | Δ/row | stored `med_dy` | `worst_dy` | runs | tol @ median size | class |
|--:|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|
| 1 | `10_stamp_as_image` | 1 | 7 | 7 | 18.00 | 18.00 | **0.00** | −1.8 | 3.1 | 52 | 2.97 | b |
| 2 | `303_discharge_summary` | 1 | 5 | 5 | 15.00 | 15.00 | **0.00** | +0.9 | 3.1 | 45 | 2.80 | b |
| 3 | `306_clinical_protocol_synopsis` | 1 | 11 | 20 | 17.00 / 14.00 | 16.50 / 14.00 | **−0.50** | −0.4 | 6.6 | 75 | 2.62 | b |
| 4 | `30_mixed_font_sizes_one_baseline_txtpos` | 1 | 6 | 6 | 18.00 | 18.00 | **0.00** | +2.3 | 4.2 | 38 | 3.15 | b |
| 5 | `320_balance_sheet_statutory` | 1 | 16 | 21 | 14.00 / 13.00 | 14.00 / 13.00 | **0.00** | +7.2 | 16.2 | 73 | 2.62 | **a** |
| 6 | `341_shipping_manifest` | 1 | 25 | 25 | 13.00 | 13.00 | **0.00** | +2.4 | 21.4 | 304 | 2.17 | **a** |
| 7 | `35_four_typefaces_one_page` | 1 | 7 | 7 | 19.00 | 19.00 | **0.00** | −2.8 | 3.3 | 52 | 3.15 | b |
| 8 | `403_crossword_puzzle` | 1 | 7 | 7 | 22.00 | 11.00 × 2 paragraphs = 22.00 | **0.00** | −7.7 | 10.6 | 27 | 2.45 | b |
| 9 | `70_magazine_drop_cap_photo_caption` | 1 | **0** | 0 | — | — | — | +2.9 | 3.1 | 24 | 3.22 | b |
| 10 | `71_invoice_space_aligned_no_rules` | 1 | 10 | 14 | 18.00 / 16.00 | 18.00 / 16.00 | **0.00** | +2.9 | 26.3 | 72 | 3.15 | b |
| 11 | `72_bank_statement_no_rules_right_amounts` | 1 | 18 | 18 | 17.00 | 17.00 | **0.00** | −1.0 | 3.5 | 80 | 3.01 | b |
| 12 | `74_balance_sheet_indented_subitems` | 1 | 6 | 10 | 17.00 | 17.00 | **0.00** | +1.5 | 4.6 | 54 | 3.04 | b |
| 13 | `balance-sheet-two-columns-of-figures` | 1 | 11 | 16 | 11.60 | 11.60 | **0.00** | −0.5 | 4.0 | 94 | 2.73 | b |
| 14 | `bus-timetable-station-left-times-right` | 1 | **33** | 33 | 16.40 | 16.40 | **0.00** | +4.2 | 5.9 | 177 | 3.01 | **a** |
| 15 | `eway-bill` | 1 | 11 | **24** | 18.40 | 17.50 / 18.50 (mean 17.9) | **−0.50** | −2.7 | 4.7 | 129 | 2.45 | **a** |
| 16 | `price-list-2col-dense-right-aligned` | 1 | **41** | 41 | 16.40 | 16.40 | **0.00** | +5.8 | 8.8 | 253 | 2.73 | **a** |
| 17 | `table-inside-two-column-page` | 1 | 6 | 7 | 18.40 | 18.00 (mean) | **−0.40** | +8.0 | **69.2** | 64 | 3.11 | b |
| 18 | `table-with-no-header-row` | 1 | **26** | 26 | 18.40 | 17.50 / 18.50 (mean 17.88) | **−0.52** | +0.7 | 4.0 | 215 | 2.59 | **a** |
| 19 | `two-tables-stacked-with-no-gap` | 1 | 13 | 13 | 18.40 | 17.50 / 18.50 / 19.50 (mean 18.04) | **−0.36** | −1.2 | 2.9 | 72 | 2.59 | b |

Sources for each column: **pages** — `PyMuPDF len(fitz.open(corpus/<doc>.pdf))`, `ConvertOne` stdout,
store `bad_pages`. **rows** — counted from `word/document.xml` `<w:tr>` of the `.docx` built at HEAD.
**source row pitch** — `PyMuPDF` line tops on page 0, clustered at 4 pt, mode of gaps ≥ 8 pt (script
`/scratch/work/an/pitch2.py`). **declared** — `w:trHeight w:val`/20 per `<w:tr>`, `hRule="atLeast"` on
every row in the table except the one carrier in `table-inside-two-column-page`. **Δ/row** =
declared − source. **stored `med_dy`/`worst_dy`/runs** — `benchmarks/gverify/<doc>.json`
`displacement`. **tol** = the check's own `clamp(0.35 × size, 1.5, 4.5)`
(`verify_google.py:5863-5864`) at the document's median matched run size, which is the figure the earlier
census used; the check applies it **per run**, at that run's size.

**Two facts fall out of the table and they are the whole result.**

1. **The engine's declared row geometry is faithful.** On **13 of the 19** the declared `w:trHeight`
   equals the source row pitch to 0.00 pt (counting `403_crossword_puzzle`'s two 11.00 pt cell
   paragraphs as its 22.00 pt row, and `70_magazine_drop_cap_photo_caption` as having no table at all);
   on the other **5** it is 0.36-0.52 pt *under*. There is no document where the engine asks for a
   taller row than the page drew. (Earlier drafts of this class hunted for exactly
   that — `FINDINGS/18-displacement-TWO-CONSTRUCTS-27NOV.md` §B predicted `trHeight` 14.0 → 13.0 on
   `320_balance_sheet_statutory`; measured here, `320` declares **14.00 against a 14.00 source pitch**,
   so that lever is not available on it.)
2. **Row count does not order the displacement.** `r(|med_dy|, total table rows)` over the 19 = **0.08**.
   `bus-timetable` has 33 rows and `worst_dy` 5.9; `table-inside-two-column-page` has 7 rows and
   `worst_dy` 69.2. So "table-row accumulation" is not a description of the class — it is a description
   of a subset, and the subset has to be found by arithmetic, not by the presence of a table.

## 3. The split, and the arithmetic that draws it

A row-accumulation mechanism can only explain a document if its rows are numerous enough for the measured
per-row excess to reach the check's tolerance. The excess is measured **in Google**, on three documents,
by `FINDINGS/TABLE-ROW-PITCH-IS-FLOORED-BY-GOOGLE-8-VARIANTS-28NOV-fixer.md`:

| document | rows | type | source pitch | Google pitch | excess/row | accumulated |
|:--|--:|--:|--:|--:|--:|--:|
| `price-list-2col-dense-right-aligned` | 40 | 8 pt | 16.40 | 16.50 | **+0.10** | **+8.28** |
| `table-with-no-header-row` | 30 | 8 pt | 18.40 | 18.53 | **+0.13** | **+3.92** |
| `341_shipping_manifest` | 24 | 6 pt | 13.00 | 13.50 | **+0.50** | **+9.24** |

At the mildest measured rate (+0.10 pt/row) the excess reaches the smallest tolerance in this population
(2.17 pt on `341`) at row 22; at 2.59-3.15 pt it needs 26-32 rows. **So a document needs ≥ 20 rows before
accumulation is even arithmetically able to fail it.** Six of the seven documents with ≥ 20 total rows
also have `|med_dy| / rows` inside the measured 0.10-0.50 band:

| document | total rows | `\|med_dy\| / rows` | inside 0.10-0.50? |
|:--|--:|--:|:--|
| `341_shipping_manifest` | 25 | 0.096 | yes (measured +0.50/row directly) |
| `bus-timetable-station-left-times-right` | 33 | 0.127 | yes |
| `price-list-2col-dense-right-aligned` | 41 | 0.141 | yes (measured +0.10/row directly) |
| `eway-bill` | 24 | 0.113 | yes |
| `320_balance_sheet_statutory` | 21 | 0.343 | yes (top of the band) |
| `table-with-no-header-row` | 26 | 0.027 | yes (measured +0.13/row directly; the median is dragged by the non-table runs) |
| `306_clinical_protocol_synopsis` | 20 | 0.020 | **no** |

**Group (a) — dense-table row accumulation: 6 documents** — `320_balance_sheet_statutory`,
`341_shipping_manifest`, `bus-timetable-station-left-times-right`, `eway-bill`,
`price-list-2col-dense-right-aligned`, `table-with-no-header-row`.

**Group (b) — everything else: 13 documents** — `10_stamp_as_image`, `303_discharge_summary`,
`306_clinical_protocol_synopsis`, `30_mixed_font_sizes_one_baseline_txtpos`,
`35_four_typefaces_one_page`, `403_crossword_puzzle`, `70_magazine_drop_cap_photo_caption`,
`71_invoice_space_aligned_no_rules`, `72_bank_statement_no_rules_right_amounts`,
`74_balance_sheet_indented_subitems`, `balance-sheet-two-columns-of-figures`,
`table-inside-two-column-page`, `two-tables-stacked-with-no-gap`.

The brief expected group (b) to be "only 3-7 documents". **Measured, it is 13**, and the reason is that
the row-count arithmetic excludes six dense documents rather than fifteen: **12 of the 13 carry ≤ 18
rows**, where the largest measured excess (0.50 pt/row) accumulates to ≤ 9 pt only if every row is at
that rate, and at the typical 0.10 pt/row to ≤ 1.8 pt — **below the smallest tolerance on the page**. The
thirteenth, `306_clinical_protocol_synopsis`, does carry 20 rows and is excluded on its **per-row figure
(0.02)**, not on its count.

## 4. Group (a): why it is uncollectable, and the two independent proofs

1. **The declarations are inert in Google, measured ten ways on three documents**
   (`TABLE-ROW-PITCH-IS-FLOORED-BY-GOOGLE-8-VARIANTS-28NOV-fixer.md`): `w:trHeight` ±5 tw renders
   identically to the shipped file (v3/v4); reducing `w:before` by 0.20-0.50 pt/row renders identically
   (v5, and `341` with `before −10 tw`); the cell paragraph mark's size is inert (v7); `w:line="0"` is
   read as single spacing and makes it worse (v8: pitch 16.50 → 22.47). **The one variant that moves the
   pitch is an increase** (v6, `before +20 tw`: 16.50 → 17.11). There is no downward lever.
2. **The engine is already asking for the source's own pitch.** Measured above: `price-list` 16.40
   declared against 16.40 source, `bus-timetable` 16.40 against 16.40, `341` 13.00 against 13.00,
   `320` 14.00 against 14.00. And the cell's `w:before + w:line` is the row height to the twip
   (`18d-WLINE-GOOGLE-MEASURED-AGENT-28NOV.md` §1: `before="368" + line="12"` = 380 tw = 19.00 pt =
   `35_four_typefaces_one_page`'s source pitch exactly).

Both directions are therefore closed: the engine cannot ask for less (the 5 documents where it already
asks 0.4-0.5 pt/row less show no corresponding displacement — `table-with-no-header-row` declares 13.4 pt
shorter than the page and measures **+0.7**), and Google will not deliver less.

**One correction to group (a)'s arithmetic, stated rather than smoothed.** `341_shipping_manifest`'s
`worst_dy` is 21.4 against a measured accumulation of +9.24 — a **19.0 pt** gap between its median (2.4)
and its tail. Its median is accumulation; its tail is not. So group (a) is not uniformly "accumulation to
the last row": on `341` the accumulation is the median term and something localised is the tail term,
and the tail alone would fail the document (21.4 / 2.1 = 10.2 × tolerance).

## 5. Group (b): the three views, per document

The three views are: **(1)** the source PDF (`PyMuPDF`, line tops / fonts / sizes), **(2)** the engine's
`word/document.xml` unzipped from the `.docx` built at HEAD, **(3)** what Google does with it — which for
this class is *only* the stored `med_dy`/`worst_dy`/`bad_pages` plus the two committed Google
measurements (`35_four_typefaces_one_page`'s per-row ramp, and the three dense-table pitch pairs). No
per-run Google data exists for these 13 and none can be produced from this task (§7).

### 5.1 What view 2 says about all 13: the geometry is right, and the row heights are inert

Declared pitch equals source pitch to 0.00 pt on **9 of the 13** (`10_stamp`, `303`, `30_mixed`,
`35_four`, `71_invoice`, `72_bank`, `74`, `balance-sheet-2col`, and `403_crossword_puzzle` at 2 × 11.00);
`70_magazine_drop_cap_photo_caption` has no table; and on the remaining three it is 0.36-0.50 pt *under*
(`306` −0.50, `table-inside` −0.40, `two-tables` −0.36). `403_crossword_puzzle` is the interesting
one: the page draws its twelve numbers at **22.00 pt** pitch and the engine declares **11.00 pt rows with
two 11.00 pt cell paragraphs each** — **22.00 pt per row, exact.** So even the document that looks like a
pitch mismatch is exact once the cell's paragraph count is read.

### 5.2 The clause each of the 13 fails on

`verify_google.py:5891-5895` fails a page on any of three clauses: `n_out > max(2, ceil(0.05·n))`
(count), `n_out == len(ds)` (block move), or `max(|dy|/tol) > 2.0` (tail). With `|med_dy|` and
`worst_dy` stored and the per-run tolerance derived from the source's own type sizes, the only clause a
document *can* fail on is fixed:

| document | `\|med_dy\|` vs tol@median | `worst_dy` / tol@median | clause that must fire |
|:--|:--|:--|:--|
| `10_stamp_as_image` | 1.8 < 2.97 | 1.04 | **count** (≥4 of 52 runs out at 8.0 pt, tol 2.80) |
| `303_discharge_summary` | 0.9 < 2.80 | 1.11 | **count** (12 of 45 runs are ≤ 2.7 pt type) |
| `306_clinical_protocol_synopsis` | 0.4 < 2.62 | **2.52** | **tail** (one run 6.6 pt out at 7.5 pt, tol 2.62) |
| `30_mixed_font_sizes_one_baseline_txtpos` | 2.3 < 3.15 | 1.33 | **count** |
| `35_four_typefaces_one_page` | 2.8 < 3.15 | 1.05 | **count** |
| `403_crossword_puzzle` | **7.7 > 2.45** | 4.33 | **median** (and tail) |
| `70_magazine_drop_cap_photo_caption` | 2.9 < 3.22 | 0.96 | **count** (≥3 of 24 runs at 7.5 pt, tol 2.62) |
| `71_invoice_space_aligned_no_rules` | 2.9 < 3.15 | **8.3** | **tail** (one run 26.3 pt out at 8.0 pt, tol 2.80) |
| `72_bank_statement_no_rules_right_amounts` | 1.0 < 3.01 | 1.16 | **count** |
| `74_balance_sheet_indented_subitems` | 1.5 < 3.04 | 1.51 | **count** |
| `balance-sheet-two-columns-of-figures` | 0.5 < 2.73 | 1.47 | **count** |
| `table-inside-two-column-page` | **8.0 > 3.11** | **22.2** | **median** (and tail) |
| `two-tables-stacked-with-no-gap` | 1.2 < 2.59 | 1.12 | **count** |

**11 of the 13 fail only the 5 % count clause.** Their medians are inside tolerance; the failure is a
handful of runs between 1 × and 2 × their own tolerance. That is a *spread*, not a shift, and the
distinction matters: no single engine constant can close a spread.

### 5.3 The two documents in group (b) that are not count-clause failures

**`table-inside-two-column-page` — the one construct in the class that is traceable end to end.**
This is the only document of the 19 whose displacement has an identifiable engine object behind it, and
it takes all three views to see it:

* **View 1 (source, `PyMuPDF`):** a two-column page, A4. Left column 17 body lines from y=109.47 to
  476.27; right column carries a caption at y=102.08 and a 6-row table whose row tops are **122.17,
  140.57, 158.97, 177.37, 195.77, 214.17 — pitch 18.40 pt**, then text to y=476.27; the footer line
  "Technical note DEG/2026/14 · page 1 of 1 Page 1 of 1" at **y=811.41**, 6.4 pt.
* **View 2 (`word/document.xml`):** the whole two-column block is emitted as **one table with one row and
  two cells**, `w:trHeight w:val="7353" w:hRule="exact"` — **367.65 pt of exact row height** — with the
  left column's paragraphs in cell 1 and the right column's in cell 2; the footer follows as a flow
  paragraph with `w:before="5069"` (253.45 pt) and `w:line="9"` (0.45 pt). No `w:footerReference`
  anywhere in the package. The emitter is `DocxWriter.java:2286-2301`, and its own comment records why
  it is `exact`: *"hRule=\"atLeast\" -> 2 pages, hRule=\"exact\" -> 1 page, all 41 lines present."*
* **View 3 (Google, stored):** `med_dy` **+8.0**, `worst_dy` **69.2**, 64 runs, `bad_pages [0]`. The gap
  between the median and the tail is **61.2 pt** — and the only object in this document that is not
  laid row-by-row is the 367.65 pt carrier row. The one render I could make on this pod at all (the
  LibreOffice proxy, §7) puts its worst run at **y=811.41 — the footer**, displaced −87.3 pt: the
  carrier's height error is inherited by everything after it, including the footer, and the check
  charges it at the footer's 6.4 pt tolerance (2.24 pt) as **30.9 × tolerance**, which fires the tail
  clause on a single run.

I am calling this an inference, not a per-run measurement: it is the only block in the document, the
document is the only one of the 19 that has such a block, and the tail is 61.2 pt above a median that is
itself only 8.0. It is falsifiable by one Google render with the carrier changed (§6).

**`403_crossword_puzzle` — the median itself is out, and the mechanism is not in the row geometry.**
The page draws twelve 5 pt numbers at 22.00 pt pitch (y = 115.20 → 335.20); the engine's seven rows are
exact (2 × 11.00 = 22.00, §5.1). Google measures **−7.7 median** (the built numbers sit *higher* than the
source drew them) with a **2.9 pt** spread, so this is a rigid shift of the grid, not accumulation: at
0.10-0.50 pt/row seven rows can produce at most 3.5 pt. The engine's own placement model for a cell is
`before + LINE_BASE × line` = 10.5 + 0.8 × 0.5 = **10.9 pt below the slot top**, while the source draws a
5 pt glyph's baseline about 3.8 pt below its cell top — a 7.1 pt disagreement in the direction Google
measures. **That is a hypothesis with an arithmetic, not a measurement**: it needs one Google render to
confirm which side is wrong, and the `LINE_BASE` family has already been refuted once on other documents
(`18dA-03`, §4).

### 5.4 The page footer: present in all 13, measured *not* to be the cause — and the one exception that is

**The page footer is a flow paragraph, not a footer part**: `footerReference` count is **0** in every one
of the 19 (`word/document.xml`), and the footer is written as the last body paragraph with a large
`w:before` — `71_invoice` `before="5587"` (279.35 pt), `70_magazine` `4507` (225.35), `table-inside`
`5069` (253.45), `341` `191` (9.55 pt, after the summary line's `3918`) — and a sub-glyph exact line box
(`w:line` 8-12 tw = 0.40-0.60 pt for 6.4-7.5 pt type).

It is tempting to call that the defect, and on the two documents where it can be checked it is not one:
**the gap is arithmetically exact.** `71_invoice`: the page's footer sits at y=798.76 and the engine's
279.35 pt gap implies a model content-bottom of **519.41 pt**, which is the `Authorised Signatory` line's
own bottom. `70_magazine`: 225.35 pt against a last body line at 572.87 implies **573.86**. `341`: the
195.9 pt gap in front of the summary line implies a model table bottom of **364.06 pt**, and the table's
own declared height is 25 × 13.00 = 325 pt. The footer's `w:before` is therefore *computed from the
content the engine believes it emitted*, and any displacement it shows in Google is **inherited** from
the flow above it. So the footer cannot be the engine change.

**One exception, and it points at §6.** On `table-inside-two-column-page` the footer's 253.45 pt gap
follows the **carrier row**, not a paragraph, and implies a model block-bottom of **557.96 pt**, where the
page's two-column text actually ends at **476.27 pt** — the engine believes its carrier row's bottom is
**81.7 pt** lower than the page drew it. The carrier's declared height (367.65 pt) is itself right for the
block (476.27 − 108.67 = 367.6), so the disagreement is in the block's *model position*, not its height,
and it is the same order as the 69.2 pt tail Google measures and the 87.3 pt the LibreOffice proxy shows.
This is the second independent reason to look at the carrier, and it is still an inference: the median is
only +8.0 pt, so the engine's model and the render disagree and one render would settle it.

## 6. The one engine change, and its expected point effect

The instruction is to name one change that would fix group (b). **The honest answer is that no single
engine change clears group (b), and the measurement that says so is §5.2: 11 of the 13 fail only the
5 % count clause with their medians inside tolerance — a spread that no constant can close — and the
other two fail on medians of −7.7 and +8.0 pt whose sign and size the record's declaration families
(`w:trHeight`, `w:before`, `w:line`, `w:hRule`, the row rung, `LINE_BASE`, the spacer spend) have each
already been measured and refuted** (`18dA-03` §4; `18D-CENSUS-19-AND-THE-GAP-LAW` §4-5;
`TABLE-ROW-PITCH-IS-FLOORED-BY-GOOGLE-8-VARIANTS` §5).

What *can* be named is the one construct with a measured object and a measured tail — the two-column
layout carrier:

> **File** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, the multi-column layout emitter at
> **lines 2286-2301**. **Condition** the branch that emits a two-column page block as a one-row,
> two-cell table — `sb.append("<w:tr><w:trPr><w:cantSplit/>").append("<w:trHeight w:val=\"").append(rowTw)
> .append("\" w:hRule=\"exact\"/></w:trPr>")`. **Change** write the row with **no `w:trHeight` element at
> all** (auto row height, content-driven) instead of `rowTw` = **7353 tw (367.65 pt) `exact`** on
> `table-inside-two-column-page`. Every other declaration in the row stays as it is; the cells' own
> `w:before + w:line` already sum to the column block's height to the twip, which is why the row does not
> need a declared height.

**Expected point effect, from the arithmetic and not from a render:** the 367.65 pt fixed box becomes one
content-driven row, so Google's per-row excess applies **once** (0.10-0.50 pt) instead of to a 367.65 pt
box whose delivered height differs from the ask by the amount the tail shows. The measured quantity at
stake is exactly `worst_dy − |med_dy|` on that document = **69.2 − 8.0 = 61.2 pt**; the expected effect is
**`worst_dy` 69.2 → ≤ 8.0 (a 61.2 pt improvement) on 1 document, and CLEAN 0 of 19**, because the
document's median of **+8.0 pt is already 2.6 × its 3.11 pt tolerance** and this change does not touch
it. It also carries a known risk: the comment at `:2293-2294` records that the `atLeast` form of this
same row put the document on **2 pages**, so the change must be re-measured for page count, and a
2-page render fails `18_displacement` more expensively than 1 page does.

**And §5.4 says the change is necessary but may not be sufficient on its own**, which is why it is stated
with its falsification test rather than as a fix: the footer's gap implies the engine's model of the block
is 81.7 pt low, and if the render agrees with that model then removing the declared height moves the
block's *height* without moving its *top*. The measurement that decides which of the two the 69.2 pt tail
is — one Google render of this one document — is the whole of the next run's job on this class.

**What would falsify §6:** a Google render of `table-inside-two-column-page` with the `w:trHeight`
removed that comes back with `worst_dy` still ≈ 69.2 (the carrier is not the block), or with the document
on 2 pages (the change is not shippable).

**And the negative, stated as the result it is:** the collectable subset of `18_displacement`'s 19 solo
documents is **0**. Group (a)'s 6 are renderer behaviour that ten variants of declaration could not move;
group (b)'s 13 are a count-clause spread at the smallest type on the page plus two localised tails, on
documents whose declared geometry matches the page to 0.00-0.52 pt per row. The next run should not
spend itself on a declaration for this class.

## 7. What could not be measured, and why

| wanted | status | why |
|:--|:--|:--|
| per-run or per-page Google `dy` for the 19 | **not measured, not storable** | `gverify.py:494-499` persists only the check's `detail` dict; `verify_google.py` reduces the per-run list in-process. No per-run `dy` exists for any document in the store. |
| a fresh Google render of any of the 19 | **not possible from this task** | every Drive write tool takes an `s3key` minted by the platform `upload` action, which a delegated task cannot reach; reproduced with the exact errors in `18d-WLINE-GOOGLE-MEASURED-AGENT-28NOV.md` §3. This run did not re-attempt it. |
| a LibreOffice proxy for the per-line structure | **measured, and shown invalid for this class** | built and rendered all 19 through `soffice` and matched source↔render lines in order (`/scratch/work/an/rows.py`). Against the stored Google medians: **r = −0.162**, **7 of 19 sign flips**, mean absolute difference **4.09 pt**, max **15.67 pt** (`table-inside-two-column-page`: LO −7.67, Google **+8.0**; `table-with-no-header-row`: LO −5.88, Google **+0.7**). No LO number is used as evidence in §3-§6. |
| per-row Google `dy` | exists for **2 of the 19** | `35_four_typefaces_one_page`: −1.96 → −3.71, a straight **−0.25 pt/row** on a 19.00 pt pitch, Google laying 18.75 (`18d-WLINE-GOOGLE-MEASURED` §5, `18D-CENSUS` §3.3). The three dense-table pitch pairs in §3. The other 17 need a Drive round trip. |
| whether my `.docx` are the bytes the store scored | **not verifiable from this repo** | the package carries the conversion timestamp (two conversions differ at zip byte 11 while `word/document.xml` is sha256-identical), and `benchmarks/DOCX-HASHES.json` predates the store's engine. §2's view-2 numbers describe the bytes this engine emits at `bcc0ea0`, not a proven copy of the bytes scored. |

## 8. Provenance

| artefact | what it is |
|:--|:--|
| `/scratch/work/CS` | `git clone --depth 1 https://github.com/kavopdf/app`, HEAD `bcc0ea0c532e3ccf9813562967aa5ddba7a441da`, 2026-11-28 04:25:41 +0000 |
| `bash tools/p2w-bench/pod-prep.sh` | corpus 214 PDFs (0 missing), JDK 17, pdfbox-android 2.0.27.0 + BouncyCastle 1.72, stubs, engine compiled (`out/ConvertOne.class`) |
| `/scratch/work/p2w/out/*.docx` | the 19, built by `ConvertOne` at `bcc0ea0`; every one `pages=1` |
| `/scratch/work/an/docxview.py` | tables / rows / `w:trHeight` / `w:rFonts` / `w:sz` / page-break count per document |
| `/scratch/work/an/pitch2.py` | source row pitch (PyMuPDF, rows clustered at 4 pt) against declared `w:trHeight` |
| `/scratch/work/an/adv2.py` | declared row advance `max(trHeight, cell line + cell margins)`; `tblCellMar` and `tcMar` are **0** on all 19 |
| `/scratch/work/an/rows.py` → `rows.json` | the LibreOffice proxy measurement (source↔render line matching by `difflib` on text in reading order) |
| `/scratch/work/an/final.py` → `final.json` | the §2 table's tolerances, clause analysis and accumulation bounds |
| `/scratch/work/an/top.py`, `/scratch/work/an/flow.py` | first-line placement and declared-flow-vs-source-y probes; both **abandoned** as invalid (the first body paragraph is often a spacer before a table, and cell paragraphs do not align 1:1 with source lines). No number from either appears above. |
| files read | `benchmarks/gverify/*.json` (all 214), `tools/p2w-bench/verify_google.py` (`:5863-5864`, `:5887-5895`, `:5921`, `:5961`), `classpick.py --leverage`, `FINDINGS/18-displacement-TWO-CONSTRUCTS-27NOV.md`, `FINDINGS/18D-CENSUS-19-AND-THE-GAP-LAW-AGENT-28NOV.md`, `FINDINGS/18dA-03-ASCENT-NOT-DISPLACEMENT-MEASURED-27NOV-relay.md`, `FINDINGS/18d-WLINE-GOOGLE-MEASURED-AGENT-28NOV.md`, `FINDINGS/TABLE-ROW-PITCH-IS-FLOORED-BY-GOOGLE-8-VARIANTS-28NOV-fixer.md`, `FINDINGS/18prize-01-18-DISPLACEMENT-PRIZE-CENSUS-28NOV-agent.md`, `benchmarks/DISP-TABLE.csv`, `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (`:54`, `:58`, `:113`, `:220`, `:2286-2301`, `:6324-6437`) |

**Ledger.** No engine file edited; nothing committed, pushed or deleted; everything written under
`/scratch/work` and `/scratch/output`. One side effect, recorded rather than hidden: `classpick.py
--leverage` invokes `pending.py`, which appends two `beat` lines to `tools/p2w-bench/TIMELINE.jsonl`; that
append was reverted with `git checkout -- tools/p2w-bench/TIMELINE.jsonl` and `git status --porcelain` is
now empty.

---

## Open questions

1. **Which run is the tail on `341` (21.4), `71_invoice` (26.3), `320` (16.2) and `table-inside` (69.2)?**
   Not answerable from the store, which keeps no per-run `dy`. A single Google render of one of these
   with the runs dumped would decide whether the tail is the footer, the last table row, or a block —
   and therefore whether §6's carrier change is the right one for `table-inside` or whether the real
   object is the 253.45 pt `w:before` gap in front of its footer.
2. **Is `table-inside-two-column-page`'s 367.65 pt carrier row shippable without the `w:trHeight`?**
   `DocxWriter.java:2293-2294` records that `atLeast` split it onto 2 pages, but "no `w:trHeight` at all"
   was never tried and is not the same declaration.
3. **Which snapshot is canonical for the class count** — the store at HEAD says 19 (`classpick.py
   --leverage` agrees); `18prize-01-…-CENSUS-28NOV-agent.md` says 18, missing `341_shipping_manifest`,
   whose record was rewritten at 2026-11-28 00:00:25. This file censuses all 19 and names the difference
   rather than picking one.
