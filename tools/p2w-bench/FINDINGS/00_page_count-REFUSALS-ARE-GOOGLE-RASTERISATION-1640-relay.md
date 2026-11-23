# 00_page_count — the 23 refusals are Google rasterising page-positioned shapes, not carrier paragraphs

**Measured 23 Nov 2026, 15:45–16:40 IST, fixer slot 15:16, engine HEAD `1ba51d99`.**
Probe documents created by this run were deleted from Drive after each export; nothing was left in
`KavoPDF-Verify` (`11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6`) or in the Drive root.

## What was carried in

`FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md` said, and the 13:20 report repeated
as "NEXT LEVER": Google keeps the empty paragraph that carries a page-positioned floating shape, that
paragraph costs ~0.83 pt of flow, 108 of them on `301_lab_report_panel` = 89.9 pt against 44.5 pt of free
page, and merging them into one paragraph saves 107 × 0.83 = 88.8 pt.

## Refuted, in three measurements

### 1. The carrier paragraphs are gone from the tree — 18 of the 22 have none

Converted all 23 `page_count_refused` documents from the `corpus-v1` release with `ConvertOne` on HEAD
(`tools/engine-verify/`, one JVM per document). Counted `<w:p>` containing a `<w:drawing>` and no `<w:t>`
in `word/document.xml`:

| drawing-only paragraphs on HEAD | documents |
|---:|---|
| 0 | **18** |
| 2 | `041122-Account_Opening_Form` |
| 21 | `401_trifold_brochure` |
| 91 | `361_product_catalogue_grid` |

`ConvertOne` could not finish `041122-Account_Opening_Form` inside 90 s, so it was counted from the
already-converted `.docx`; the other 22 were converted this run. The 2 464 drawing-only paragraphs the
0530 finding cites are not in this tree.

### 2. LibreOffice renders the correct page count on 21 of the 22

`soffice --headless --convert-to pdf`, page count against the source PDF:

- **21 of 22 match the source exactly** (`05_round_company_seal_curved_text`, `305_vaccination_certificate`,
  `314_tender_rfp_boq`, `320_balance_sheet_statutory`, `326_itr_computation`, `332_bom_on_drawing`,
  `333_datasheet_spec_tables`, `341_shipping_manifest`, `350_question_paper`, `351_omr_answer_sheet`,
  `353_admit_card`, `361_product_catalogue_grid`, `390_wide_data_appendix`, `401_trifold_brochure`,
  `402_calendar_month_grid`, `403_crossword_puzzle`, `405_sheet_music_lyrics`, `60_page_border`,
  `bank-statement-horizontal-rules-only`, `boq-horizontal-rules-only`,
  `price-list-2col-dense-right-aligned`).
- **1 does not**: `041122-Account_Opening_Form` 9 pages source → 10 in LibreOffice.

So `00_page_count`'s "fixed-in-LO-only 23" column is real: these documents are **correct in the proxy and
wrong only in Google**. The page count is not a shared defect.

### 3. Three Google probes on HEAD — the shapes are rasterised, and 16 of them land on page 2

Uploaded to `KavoPDF-Verify`, converted on import, exported back as PDF, deleted. Page counts read from
the export with PyMuPDF.

| probe | source pages | LibreOffice | **Google** | page 2 text | page 1 images | page 2 images |
|---|---:|---:|---:|---:|---:|---:|
| `60_page_border` (as HEAD writes it) | 1 | 1 | **2** | **0 chars** | 46 | 16 |
| `350_question_paper` (as HEAD writes it) | 1 | 1 | **2** | 8 chars (`schemas.`) | 0 | 1 |
| `60_page_border` + one trailing empty `<w:p>` | 1 | 1 | **2** | 0 chars | — | — |

`60_page_border`'s `.docx` carries **62 `wp:anchor`**, every one of them `wrapNone`, `behindDoc="1"`,
`simplePos="0"`. Google turns them into **62 rasterised images spread 46 / 16 across two pages**, and
draws the page-border rectangle on both pages. The text all stays on page 1: page 2 is a blank page with
a border on it. LibreOffice draws the same 62 shapes on one page and scores the document **41/42**
(only `17_matched_runs` fails) — a document that is refused, not measured, purely because of the extra
page.

`350_question_paper` is a different family: page 2 carries 8 real characters, so it is a genuine one-line
overflow, not a blank page. Its `.docx` has **1** anchor. The two documents need different fixes and the
class name hides that.

## What this refutes

- **Carrier paragraphs are not the cause.** 18 of 22 have none, and the document that best exhibits the
  fault (`60_page_border`) has none.
- **"Google needs a trailing paragraph after a floating shape."** Adding one changes nothing: 2 pages
  before, 2 pages after, page 2 still empty. Measured, not argued.
- **The 0.83 pt/paragraph figure cannot be applied here.** It was measured on shapes, on a document with
  108 drawing-only paragraphs; the documents that actually refuse have 0–91 and 18 of them have zero.

## What is left to test — the next run's lever, with a falsifiable prediction

The fault is that a document's page furniture is emitted as **N independent floating shapes**. Google
rasterises each one and lays them out in flow; the ones that do not fit open a new page. The prediction
that would confirm it: **replace the 62 shapes of `60_page_border` with one shape (or with `w:pgBorders`,
a section property with no flow cost at all) and Google renders 1 page.**

That is cheap to test with one probe and it is the shape of the fix for every border/frame document. It
was not implemented this run: it is an engine change in `DocxWriter` that must be measured in Google
before and after, and the slot's remaining minutes went to the measurement above.

Also worth one probe each, because they are separate mechanisms and the class hides it:
`401_trifold_brochure` (21 drawing-only paragraphs, landscape) and `361_product_catalogue_grid`
(91 drawing-only paragraphs, via the column path — the unlanded patch agent A found this run).


## 4. The prediction held: 62 shapes -> 2 pages, `w:pgBorders` -> 1 page

Built one variant of `60_page_border`'s `.docx` in place — removed every run carrying a `<w:drawing>` (all
62, every one `wrapNone`/`behindDoc="1"`) and added a real `w:pgBorders` (single, `sz=8`, `space=24`,
`offsetFrom="page"`) to the first `sectPr`. Text untouched. LibreOffice: 1 page, 673 chars. Then the same
Google round trip — upload, convert on import, export, delete:

| variant | LibreOffice | **Google pages** | page 1 chars | page 1 images | page 1 drawings |
|---|---:|---:|---:|---:|---:|
| HEAD: 62 `wp:anchor` shapes | 1 | **2** | 689 | **46** | 1 |
| 0 shapes + `w:pgBorders` | 1 | **1** | **689** | **0** | 1 |

The page count follows the **number of page-positioned floating shapes**, and nothing else: same text, same
689 characters, same LibreOffice page count, one page in Google instead of two. This is the mechanism, and
it is not the carrier paragraph.

**What this probe does not establish, and the next run must.** The only drawing in *either* export is a
single rect at `[0.0, 0.0, 595.5, 842.2]` — the full page — in both the 2-page and the 1-page variant. So
this probe does **not** show that Google draws the `w:pgBorders` frame. If Google silently drops it, the
page count is fixed and the page border is lost, which is a document getting worse, not better. `pgBorders`
is not in `google_safe.py`'s "Google ignores" catalogue (`w:framePr`, `w:w`/`w:spacing`, `.odttf` faces,
floating `<w:drawing>` rules), but absence from that list is not evidence that Google honours it.

The falsifiable next test is therefore narrow and cheap: render the `pgBorders` variant in Google and check
that ink exists near all four page edges (four line segments at ~24 twips inset), not just that the page
count is 1. If the frame is dropped, the fallback is one *composite* shape per page edge instead of 62
segments — the count is the thing that matters, and 4 is not 62.

## Two agent findings carried alongside

- `FINDINGS/00_page_count-COLUMN-PAGE-MERGE-1615-agent.md` + `.patch` — the column-page shape merge.
  The handoff's proposed re-implementation in `shape()` is a no-op at HEAD (`pageBody()` already joins
  shapes as runs); the live gap is `columnPage()` → `emitBlock()`. Patch compiles; `<w:p>` 40 → 29 on a
  synthetic two-column page with all 12 anchors identical; **not measured in Google, not applied.**
- `FINDINGS/00_page_count-ANCHORSHAPE-CARRIERS-1615-agent.md` + `.patch` — collapsing `anchorShape()`'s
  per-anchor paragraphs (1 037 of the corpus's 1 319 drawing-only paragraphs, across 61 documents).
  920 paragraph marks removed on 38 documents; all 213 documents keep every anchor attribute, offset and
  order; re-splitting reproduces the old `document.xml` byte for byte in 211/213. LibreOffice page count
  unchanged on all 38, 33/38 pixel-identical. **Not measured in Google, not applied** — it buys 45.7 pt
  of the engine's flow model corpus-wide and no document becomes CLEAN on that evidence alone.

## Reproduce

```
gh release download corpus-v1 --repo kavopdf/app -p '*.zip' -D x/ && for z in x/*.zip; do unzip -oq "$z" -d corpus; done
bash tools/p2w-bench/build-engine.sh
# per document, one JVM each:
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
    ConvertOne <source.pdf> /scratch/work/p2w/docx
soffice --headless --convert-to pdf --outdir lo docx/<name>.docx      # page count vs source
# Google: CREATE_FILE(mimeType=google-apps.document, parents=[KavoPDF-Verify]) -> EXPORT pdf -> DELETE_FILE
```
