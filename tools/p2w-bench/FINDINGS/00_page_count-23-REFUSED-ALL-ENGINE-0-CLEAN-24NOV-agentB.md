# 00_page_count — the 23 not-scored documents: one mechanism, three code paths, and a prize of 5, not 23

**24 Nov 2026.** Analysis slot. Question asked: for the 23 documents whose page count does not match the
source, what is the mechanism, and how many are engine defects vs instrument defects?

**What this run could and could not measure.** The pod has no `java` and no `gradle` (checked: neither
binary exists, no prebuilt `PdfToWord.class`), so **no `.docx` was generated and no Google round trip was
run here**. Every number below is either (a) measured in this pod off the source PDFs, (b) read out of
`benchmarks/gverify/*.json`, `benchmarks/gverify-lo/*.json` and `benchmarks/RANKING.csv`, or (c) quoted
from a `FINDINGS/` file with the file named. Anything modelled is labelled modelled.

## 1. The filter, stated exactly

`gverify.py:326-336`. After the Google export comes back, the gate is a page-count comparison and nothing
else:

```
want, got = _pages(src), _pages(tmp)
if want > 0 and got > 0 and got != want:
    os.remove(tmp)
    _write(name, {"name": name, "status": "page_count_refused", "pages": got, "want": want, ...})
    return 4
```

`report.py:1275` prints the survivors as the row *"Not scored - page count did not match"*. The check
that never ran is `01_page_count` (`verify_google.py:4648`, `src.page_count == gd.page_count`); the class
name in `classpick.py` is `00_page_count`. **A refusal is not one failing check — it is all 47 checks
skipped.** `gverify.py` also `os.remove`s the exported PDF, so the evidence of *what the extra page
carries* is deleted at the moment it is produced.

## 2. The 23, with both renderers and the direction

Sources: `want`/`pages` from `benchmarks/gverify/*.json` (Google); our render's page count from
`benchmarks/gverify-lo/*.json` → `checks.01_page_count.render` (LibreOffice, i.e. the local proxy — the
best render count in the store, since no `.docx` can be built here); slack and shape counts measured in
this pod off the source PDF's page 1 with PyMuPDF.

| document | src pages | our pages (proxy) | Google pages | direction | check failed | p1 slack (pt) | shapes on p1 | other checks failing in the proxy |
|---|---:|---:|---:|---:|---|---:|---:|---|
| `041122-Account_Opening_Form` | 9 | 10 | **14** | +5 | `01_page_count` | -1.5 | 646 | 19 other checks (04_chars_missing, 05_chars_extra, 10_font_sizes, …) |
| `Account_Opening_Form_Fillable_filled` | 9 | 11 | **14** | +5 | `01_page_count` | -1.5 | 646 | 25 other checks (04_chars_missing, 05_chars_extra, 10_font_sizes, …) |
| `405_sheet_music_lyrics` | 1 | 1 | **2** | +1 | `01_page_count` | 76.4 | 144 | **none - 42/42 in the proxy** |
| `333_datasheet_spec_tables` | 1 | 1 | **2** | +1 | `01_page_count` | 68.4 | 132 | `66_table_cell_width` |
| `326_itr_computation` | 1 | 1 | **2** | +1 | `01_page_count` | 60.0 | 288 | `63_table_rows` |
| `305_vaccination_certificate` | 1 | 1 | **2** | +1 | `01_page_count` | 58.4 | 225 | `17_matched_runs`, `59_shape_anchor` |
| `314_tender_rfp_boq` | 1 | 1 | **2** | +1 | `01_page_count` | 58.3 | 79 | `63_table_rows` |
| `320_balance_sheet_statutory` | 1 | 1 | **2** | +1 | `01_page_count` | 58.3 | 80 | **none - 47/47 in the proxy** |
| `403_crossword_puzzle` | 1 | 1 | **2** | +1 | `01_page_count` | 48.4 | 169 | `14_filled_shapes` |
| `353_admit_card` | 1 | 1 | **2** | +1 | `01_page_count` | 48.3 | 273 | **none - 47/47 in the proxy** |
| `402_calendar_month_grid` | 1 | 1 | **2** | +1 | `01_page_count` | 44.3 | 48 | **none - 47/47 in the proxy** |
| `361_product_catalogue_grid` | 1 | 1 | **2** | +1 | `01_page_count` | 38.4 | 85 | **none - 42/42 in the proxy** |
| `05_round_company_seal_curved_text` | 1 | 1 | **2** | +1 | `01_page_count` | 34.3 | 7 | **none - 42/42 in the proxy** |
| `390_wide_data_appendix` | 1 | 1 | **2** | +1 | `01_page_count` | 32.6 | 400 | `66_table_cell_width` |
| `price-list-2col-dense-right-aligned` | 1 | 1 | **2** | +1 | `01_page_count` | 29.7 | 85 | **none - 42/42 in the proxy** |
| `bank-statement-horizontal-rules-only` | 1 | 1 | **2** | +1 | `01_page_count` | 24.1 | 39 | **none - 42/42 in the proxy** |
| `boq-horizontal-rules-only` | 1 | 1 | **2** | +1 | `01_page_count` | 24.1 | 33 | **none - 42/42 in the proxy** |
| `351_omr_answer_sheet` | 1 | 1 | **2** | +1 | `01_page_count` | 20.0 | 381 | **none - 42/42 in the proxy** |
| `341_shipping_manifest` | 1 | 1 | **2** | +1 | `01_page_count` | 18.6 | 301 | **none - 47/47 in the proxy** |
| `60_page_border` | 1 | 1 | **2** | +1 | `01_page_count` | 18.5 | 15 | `17_matched_runs` |
| `332_bom_on_drawing` | 1 | 1 | **2** | +1 | `01_page_count` | 10.0 | 58 | **none - 47/47 in the proxy** |
| `350_question_paper` | 1 | 1 | **2** | +1 | `01_page_count` | 4.6 | 1 | **none - 42/42 in the proxy** |
| `401_trifold_brochure` | 1 | 1 | **2** | +1 | `01_page_count` | 0.0 | 198 | **none - 42/42 in the proxy** |

**Direction is one-sided and that is the first finding.** 21 of 23 drew **one page too many**, 2 drew
**five too many**, and **0 drew too few**. There is no document in this population where the render lost
a page. Every mechanism below is therefore an *additive* flow cost, not a loss — which is why "a table
that breaks across pages" and "a footer that adds a page" in the usual sense do not apply: on the 21
one-page documents there is no page 2 in the source to break onto.

**Every one of the 23 is measured on a retired engine.** The 23 Google refusals carry no `engine` key and
no `at` timestamp at all; the 23 proxy verdicts carry `462353f` (19), `98be7c3c` (2), `7112d76` (2) or
nothing. **Zero of 23 has a verdict — Google or proxy — on the engine in the tree (`b7699196`).** The
whole class is stale by construction, and that is an instrument fact, not a mechanism.

## 3. What the record already proved, so this file does not re-prove it

Three constructs have been proposed and measured for this class. All three are real; none of them is the
whole class:

| claim | where | status |
|---|---|---|
| one carrier paragraph per anchored shape, ~0.83 pt each, Google does not honour `w:line="1" exact` | `00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md` | **true where it occurs**, and **already fixed at HEAD** (`flushShapes()`); but 18 of 22 refused documents had **zero** drawing-only paragraphs (`00_page_count-REFUSALS-ARE-GOOGLE-RASTERISATION-1640-relay.md`), so it cannot be the class |
| the `<wp:inline>` picture in a `pPr`-less paragraph | `00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md` | **refuted for the class**: 0 `<wp:inline>` in all 23 emitted files; `350` has 70 paragraphs of text and one 539.3 x 0.7 pt rule |
| Google bills the flow for page-positioned floating shapes | `…-REFUSALS-ARE-GOOGLE-RASTERISATION-1640-relay.md` | **proven by a controlled probe**: `60_page_border`, same 689 characters, same LibreOffice page count — 62 `wp:anchor` shapes → **2 Google pages**; 0 shapes + `w:pgBorders` → **1 Google page** |

And the two measurements that bound the constant:

- **Per shape.** `PAGE-COUNT-IS-THE-ANCHORS-NOT-THE-ROWS-2200-fixer.md` computed, for each document, the
  slack divided by the anchor count — the size of box Google must be charging per shape to spill the
  page: **0.10 to 0.96 pt, median 0.57**, over 19 documents. It also measured the four components the
  class was assumed to be (row growth, table-top spacer, wrap under a substitute face, paragraph
  spacing) at **0.00 pt on 16 of the 21, negative on 6, +0.11 on one**.
- **Per paragraph.** The carrier merge landed and was measured in Google twice: `301_lab_report_panel`
  108 drawing-only paragraphs → 0, **2 pages → 1, 39/42** (`…-SHAPE-RUNS-NOT-PARAGRAPHS-LANDED-0730-fixer.md`);
  `361_product_catalogue_grid` 124 paragraphs → 40, **2 pages → 1, 41/42** (`…-MERGE-LANDED-1120-fixer.md`).
  LibreOffice moved on neither.

**The decisive counter-measurement is one line in `00_page_count-MERGE-IN-COLUMN-PAGE-MEASURED-IN-GOOGLE.md:47`:**
the same merge, applied to `401_trifold_brochure`, leaves it at **2 pages**. So the carrier paragraph is
one of two costs, and the second one survives the merge.

## 4. The mechanism, per group, and what is on the page that causes it

### M1 — a genuine one-line text overflow (1 document: `350_question_paper`)

Page 1 of the source opened (rendered at 110 dpi, this pod): a full A4 of exam questions, 3090
characters, ending `9a. … Discuss 1NF, 2NF and 3NF with relation / schemas.` The last wrapped line
`schemas.` sits at **y = 837.3 pt on an 841.9 pt page — 4.6 pt of slack**, the tightest in the class.
The document carries **one** shape on the page (a header rule) and 104 text lines.

This is the only document in the 23 where the extra page carries real text, and it is measured, not
inferred: the Google probe in the 1640 relay read **8 characters on page 2 — `schemas.`**. The engine's
flow overflowed by roughly one line and Google put it on sheet 2.

This is also the one document where the mechanism the `350` agent finding charged is **wrong**: it
predicted a page-tall `<wp:inline>` picture in a `pPr`-less paragraph. The emitted file has 0 inline
pictures and 70 paragraphs; the page is a text page. `probe-350.java.patch` must not be applied.

### M2 — page furniture emitted as N floating shapes (1 document measured: `60_page_border`)

Page 1 of the source opened: a certificate — title block, name, two signature blocks, a circular
"SEAL 2025" stamp, and a **decorative double-line border with four corner motifs**. The border's bottom
edge sits at **y = 823.4 pt, 18.5 pt of slack**; the page draws **15 vector drawings** in the PDF and the
emitted `.docx` carries **62 `wp:anchor`** shapes for them (each border side, each rule of the double
line, each corner motif is its own shape).

What the extra page carries, measured by the 1640 probe: **0 characters and 16 rasterised images.** The
text all stays on page 1; page 2 is the same page with the bottom of its frame on it. LibreOffice scores
this document **41/42** (only `17_matched_runs`), which is what "refused, not measured" costs.

### M3 — the flow cost of N anchored shapes on a page with almost no slack (19 documents)

This is the class. The pattern is mechanical and it is visible in the table's last two columns:

| | |
|---|---|
| shapes on page 1 | **7 to 646** (median 132 over the 21 one-page documents) |
| page-1 slack | **0.0 to 76.4 pt**, median **34.3**; 8 of 21 have less than 25 pt |
| text on the extra page | **not measured for 20 of the 23** — see §7 |
| ink outside the sheet | **none** on the 21; the two bank forms are the exception (§M4) |

The geometry is what makes them fragile. Page 1 of `401_trifold_brochure` opened: a landscape A4 tri-fold
with a **full-height navy panel** (its bottom edge is exactly the page height — **0.0 pt of slack**), two
dotted fold lines running the full height, a QR code, and 198 drawings. Any additive charge at all opens
sheet 2, which is why this is the one document the carrier merge did not fix. Page 1 of
`390_wide_data_appendix` carries **400 drawings of which 380 are hairlines** — a ruled grid whose every
rule is its own floating shape.

So the mechanism is one construct — **the page's own geometry is emitted as N independent
page-positioned floating shapes, and Google charges the flow for them while LibreOffice charges
nothing** — and the difference between M2 and M3 is only whether the shapes are furniture or content.

### M4 — the two bank forms: geometry past the paper, wrong in both renderers (2 documents)

`041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled`, 9 source pages each, **14 in
Google**, and **10 and 11 in LibreOffice**. These are the only two where the proxy is also wrong, so they
are a pagination fault, not a Google-only charge. Measured on the source here:

- page 1 carries **646 drawings** and 3604 characters; the page frame's bottom edge is at
  **y = 843.4 pt on an 841.9 pt page — 1.5 pt below the paper**, on **all nine pages**;
- the emitted `.docx` anchors a picture at **cy = 842.1 pt on a 841.9 pt sheet**
  (`…-THE-PROXY-IS-BLIND-TO-21-OF-23-0206.md`).

Page 9 of the source opened: an account-opening form with a table whose last row and a signature box sit
within 30 pt of the foot, plus the same full-page frame. A frame taller than the sheet plus a table at the
foot is a pagination fault the engine should have caught and did not.

## 5. Engine or instrument — verdict per group, and the exact code a fix touches

| group | documents | verdict | construct |
|---|---:|---|---|
| M1 one-line overflow | 1 | **engine** | flow budget overrun at a page that is 4.6 pt from full |
| M2 furniture as shapes | 1 measured, same construct in M3 | **engine** | N floating shapes billed to the flow |
| M3 shapes billed to the flow | 19 | **engine** | N floating shapes billed to the flow |
| M4 frame past the paper | 2 | **engine** | a 842.1 pt anchor on a 841.9 pt sheet |
| **total** | **23** | **23 engine, 0 instrument** | |

**0 of the 23 is an instrument artefact of the comparison.** The one candidate — "it counts a trailing
blank page" — was tested and fails: `60_page_border`'s second page is not blank, it carries 16 rasterised
pieces of the page's own frame. A user opening that Google Doc sees two pages where the source has one,
with the bottom of the border on the second. That is the defect, fairly counted.

### Where a fix would touch

**The page-break decision is blind to the construct by construction.**
`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`

| site | line | what it decides |
|---|---|---|
| `pageFits(PdfToWord.Page page, float ph)` | **3846** | the only whole-page height measure in the writer. It collects `outlines` from `page.blocks` (3855-3857) and then **skips every box whose `containerOf(outlines, b) != null`** (3884), plus every `p.pinned` line and every `b.rotated` box. A page that is only furniture therefore measures as **empty** and `pageFits` returns true. Its return value is `ctx.spendGaps` (1144), which in turn decides how the whole page is laid |
| `spacingTw(CharSequence xml)` | **449** | the budget measure the guard reads. It sums exactly three token kinds — `w:before`, `w:line`, `w:trHeight` (481, 488). A bare shape run carries none of them, so `writtenTw` is short of what Google bills on every shape-dense page |
| budget guard | 1191-1310 | `writtenTw > pageBudgetTw` (1210), `fitReserveTw` = 96 twips (1293), `shaveToFit` (1301, defined 510). All downstream of the two measures above, so all blind in the same way |
| `shape()` → `shapeRun()` → `flushShapes()` | **2923 / 2956 / 2936** | one carrier paragraph per page — **already merged**, landed 23 Nov. The `.docx` comment at 2948-2955 states the law: Google "rasterises the shape, keeps the paragraph, and bills the paragraph the line box of its own `sz=2` run — about 0.83 pt" |
| `anchorShape(...)` | **5565 / 5580** | still emits **one `<w:p>` per anchored text box** (the stamp / rotated-label / `anchorBox()` path). This is the un-merged half of the carrier construct |
| `columnPage(...)` → `emitBlock()` | **1763** | the table/column pass, the path the merge patch had to reach twice |
| `breakPage()` / `<w:br w:type="page"/>` / `sectPrXml()` | 666 / 670, 1113 / 2389, 2402 | where a page actually ends — the consumer of `pageFits`, not the cause |

The single sentence a fixer needs: **`pageFits()` at `DocxWriter.java:3846` charges a page-positioned
floating shape nothing, so the engine believes a page of page-furniture fits while Google overflows it by
0.10-0.96 pt per shape.** Either charge the shapes in `pageFits`/`spacingTw` (so the engine's own break
decision sees them) or stop emitting N of them (merge — landed for the body path, not for
`anchorShape()` and not for `columnPage()`'s cells).

### The instrument defects that are real, but change no page count

These are worth fixing and none of them makes a document pass:

1. **The refusal is undated and unstamped.** `gverify.py:333` writes `pages`/`want` only — no `engine`,
   no `at`. The 190 scored verdicts carry `engine`; the 23 refused ones do not, so the class cannot be
   aged against the tree and is in fact **entirely on retired engines** (§2).
2. **The evidence is deleted.** `os.remove(tmp)` on the refusal line throws away the only artefact that
   says what the extra page contains. Two hand-built Drive probes had to rediscover it.
3. **A refusal hides a near-clean document.** `361` is 41/42 in Google once the page count is right;
   `60_page_border` is 41/42 in the proxy. Both read as a single "not scored" row.
4. **The proxy cannot see the construct at all** — 21 of 23 are the correct page count in LibreOffice —
   so the corpus pass, `gate.py`, `regress.py` and the ratchet are all blind to it. `…-MERGE-LANDED` says
   it plainly: "Documents whose `share@5px` moved: 0" while Google moved a page.
5. **The proxy verdicts for the 23 are mixed-total** — 11 measured on 42 checks, 12 on 47 — so 9 of the
   14 that look clean were never offered checks 43-47 (the charter's own warning, with a number on it).

## 6. The prize, honestly counted

`classpick.py --leverage` prices `00_page_count` at **23.0 clean documents**. That number assumes all 23
become clean. They do not.

**Measured in Google: 0 of 23.** Not one of the 23 has a single Google check result — the refusal skips
all 47. Exactly **one** of the 23 has ever been re-measured in Google after a page-count fix:
`361_product_catalogue_grid`, **41/42, failing `25_invisible_text`** (render=2). One check short of clean.

**Bounded by the LibreOffice proxy** (all applicable checks passing in `benchmarks/gverify-lo/`):

| state in the proxy | documents | which |
|---|---:|---|
| clean on **47 of 47** | **5** | `320`, `332`, `341`, `353`, `402` |
| clean on **42 of 42** — never offered checks 43-47 | 9 | `05_round`, `350`, `351`, `361`, `401`, `405`, `bank-statement`, `boq`, `price-list` |
| 1-2 other checks failing | 7 | `305` (2), `314`, `326`, `333`, `390`, `403`, `60` (1 each) |
| 20+ other checks failing | 2 | `041122` (19 others, 20 with the page count), `Account_Opening_Form_Fillable_filled` (25, 26 with it) |

So, in order of how much the number can be trusted:

| statement | count |
|---|---:|
| documents that would go CLEAN on measured Google evidence | **0** |
| documents with any Google measurement after a page-count fix | **1** (`361`, at 41/42) |
| documents that pass every check the proxy gave them | **14** |
| documents that pass **all 47** checks the proxy can give | **5** |
| documents the leverage table assumes | 23 |

**The honest prize is 5, with 14 as the absolute ceiling, and 0 as what has been demonstrated.** A
document with one other failing check does not become clean; 7 of the 23 already have 1-2, and the two
bank forms have 20 and 26.

## 7. What one run would settle, and it is one measurement

The record has a page-2 census for **2 of the 23** (`60_page_border`: 0 chars, 16 images; `350`: 8 chars).
The other 21 have never had their second page opened. That single artefact — export the refused PDF and
keep it instead of `os.remove`ing it — decides between M2 and M3 per document and measures the per-shape
constant directly instead of bounding it.

The cheapest falsifiable sequence:

1. **`60_page_border`** — the 1640 probe already proved 62 shapes → 2 pages and 0 shapes → 1 page. The
   open question there is only whether Google draws the `w:pgBorders` replacement; check for ink near all
   four edges, not just the page count.
2. **`350_question_paper`** — one line over. A fix that gives the page 5 pt of slack settles it; it is
   also the one document where the answer cannot be shapes.
3. **`401_trifold_brochure`** — 0.0 pt of slack, 198 drawings, and the only document proved to survive
   the carrier merge at 2 pages. It is the discriminator between "merge more" and "charge the shapes".
4. **Re-measure the 23.** They are all on retired engines; the merge has landed since. Until that run,
   "23 refused" is a claim about 23 Nov, not about the tree.

## Reproduce

```
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
bash tools/p2w-bench/corpus-fetch.sh                     # 213 PDFs, ~40 s
python3 - <<'EOF'   # the 23 and both renderers
import json, glob
for f in sorted(glob.glob('benchmarks/gverify/*.json')):
    d = json.load(open(f))
    if d.get('status') == 'page_count_refused':
        lo = json.load(open('benchmarks/gverify-lo/%s.json' % d['name']))
        print(d['name'], d['want'], d['pages'], lo['checks']['01_page_count']['render'])
EOF
```

Page 1 of any document: `pymupdf` → `page.get_drawings()`, `page.get_text("dict")`, bottom-most ink
against `page.rect.height`; render at 110 dpi with `get_pixmap(dpi=110)`.

## Not stated / not established

- The page-2 content of 21 of the 23. Measured for `60_page_border` and `350_question_paper` only.
- The exact per-shape charge. The record bounds it at **0.10-0.96 pt (median 0.57)** by the spill
  arithmetic; it has never been read off a Google export.
- Whether Google charges per *shape* or per *paragraph holding shapes*. The two laws both have a
  controlled probe behind them (`301`/`361` for paragraphs, `60_page_border` for shapes) and `401`
  surviving the merge says the paragraph law is not sufficient. This file does not claim to have settled
  which is primary.
- No `.docx` was built in this pod (no JVM), so every "our render" number in §2 is LibreOffice's, read
  from the store, on a retired engine.
