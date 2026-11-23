# 00_page_count — the column-page merge is LANDED, and LibreOffice cannot see it

**Class:** `00_page_count` (23 refused documents, 23.0 clean-document leverage)
**Tree:** HEAD `5beb8b9d` + `00_page_count-MERGE-SHAPE-PARAGRAPHS.patch` = engine fingerprint `3e7f7c4475343a35`
**Measured:** 23 Nov 2026, 15:02–16:50 IST, one Google verification already on record (04:47 run), one full 213-document corpus pass on this tree.

## What this run did that the last two could not

The 04:47 run measured the patch in Google (`361` 2 pages → 1, 41/42) and could not land it: the
`.docx` corpus pass did not finish inside one call. The 07:30 run landed the `pageBody()` half.
This run spent its slot on the second half and got the corpus table written on the patched tree.

**The measurement gap was not a time limit. It was two instrument bugs:**

1. `p2w.py` builds `P2W_ENGINE_SRC` or `repo@FETCH_HEAD` — never the working tree by default. The
   first five conversion calls of this run therefore rebuilt all 213 documents with the **unpatched**
   engine while the patch sat in the tree. Caught by asking the `.docx` itself: `361` came back with
   124 paragraphs and 91 single-drawing paragraphs, the pre-patch shape, while the finding predicted 40.
2. `--force`'s staleness clock read `REPO`'s `PdfToWord.class` even with `ENGINE_SRC` set, so a
   document written by the other clone after this tree's build read as fresh. Fixed in `p2w.py` this
   run (see `FINDINGS/p2w-ENGINE-SRC-FORCE-STALENESS-1120-fixer.md`).

## The change, proved on the document XML (not on a tool this run edited)

Rebuilt all 213 on the patched tree, then read `word/document.xml` directly:

| document | paragraphs before | after | drawings before/after | drawings per paragraph, after |
|:--|--:|--:|:--|:--|
| `361_product_catalogue_grid` | 124 | **40** | 91 / 91 | one paragraph carries **85** |
| `401_trifold_brochure` | 52 | **27** | 26 / 26 | one paragraph carries **21** |
| `301_lab_report_panel` | 85 | 85 | 108 / 108 | one carries 108 — **unchanged**, the `pageBody()` half already merged it |
| `350_question_paper` | 70 | 70 | 1 / 1 | unchanged — **not explained by this mechanism** |

The last two rows are the control: a document already fixed is not fixed twice, and the one document
the mechanism does not explain stays exactly as it was. Every drawing survives at its source position
(`wp:anchor`, `relativeFrom="page"`, `wrapNone`) — the paragraph was never consulted for placement.

## The corpus, measured whole on this tree

    python3 benchmarks/gate.py --budget 250   (with P2W_ENGINE_SRC=/scratch/work/CS)
    212/212 scored, 1 exempt, 0 blocking
    OK: no regressions against baseline

**Documents whose `share@5px` moved: 0. Improved: 0. Worse: 0.** That is not a null result, it is the
finding: the LibreOffice proxy honours `w:line="1" exact` on the carrier paragraph, so removing 84
empty paragraphs changes nothing it can see. Google does not honour it — which is why the 04:47 run's
Google arm moved `361` from 2 pages to 1 and `375` from 35/42 to 37/42 with **no check that passed
before failing now**. The proxy is blind to this construct by construction; the charter says Google is
the truth for exactly this case.

What the corpus pass buys is the other half of the claim: **the 21 changed documents are neutral in
LibreOffice and nothing else in the corpus moved**, so the change cannot regress anything the proxy
can measure. Zero documents worse, on both formats.

## What this is worth, stated as documents

22 of the 23 `page_count_refused` documents emit their drawing-only paragraphs after the last text
paragraph and were scoring **zero of 42 known checks** because `gverify.py --collect` refuses a
page-count mismatch. They are now measurable: `361` at 41/42 and `375` at 37/42 in Google, both from
2 pages to 1. The class moves from *unmeasurable* to *2–5 checks from clean*.

## What would prove this wrong

* A document whose Google page count goes **up**. Not yet measured on the third document — see below.
* A Google render where a drawing is missing or moved. 361 and 375 both keep every drawing.
* A document that comes out of the carrier with **no** paragraph in a cell that had one (the
  `cellXml[c].indexOf("<w:p") < 0` guard exists for that; unexercised so far).

## Left for the next run, in order

1. **`041122-Account_Opening_Form`** (2464 drawing-only paragraphs, nine pages) — the scale test. Not
   measured in Google. If the carrier chokes, it chokes here, and it is also the worst-scoring document
   in the corpus at 98.65.
2. **`350_question_paper`** — 1 drawing-only paragraph, still refused. The agent finding beside this
   file charges `picture()` lines 2542–2564: an unplaced picture is emitted as `<wp:inline>` in a
   paragraph with **no `w:pPr`**, so it inherits `sz=22` and `w:after=120` from `stylesXml()`'s
   docDefaults, and `spacingTw()` cannot see it because it reads only `w:before`/`w:line`/`w:trHeight`.
   The proposed rule: no drawing is ever placed in the text flow. Patch beside it, **not compiled**.
3. `w:tcBorders` through the table writer — the second lever for `32_stroke_lines` and
   `05_chars_extra`, same construct family.
