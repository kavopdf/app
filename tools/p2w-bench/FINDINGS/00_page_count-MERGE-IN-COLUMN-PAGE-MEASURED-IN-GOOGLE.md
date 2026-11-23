# 00_page_count — the merge that was missing is the one inside a column page, and it is MEASURED IN GOOGLE

**Run:** 23 Nov 2026, fixer slot claimed 04:47 UTC.
**Status:** measured, NOT landed. The patch is committed beside this file as
`00_page_count-MERGE-SHAPE-PARAGRAPHS.patch`. It applies cleanly to HEAD (`git apply --check`, verified).

## What was already true at HEAD, and what this corrects

The 0530 finding said "merge the drawing-only paragraphs of a page into ONE
(`DocxWriter.shape()`)" as the next lever. That is only half right.

`pageBody()` **already** writes every shape as a bare run appended to the page's last paragraph, with a
single orphan carrier paragraph per page. That landed earlier on 23 Nov. So a re-implementation in
`shape()` is a no-op for every document that goes through `pageBody()` — which is why 301, 375, 341,
390, 403, 405, 351, 333, 305, 60, 314, 320, 326, 332, price-list, bank-statement and boq already had
exactly one shape-only paragraph and already render 1 page.

The path that was still un-merged is `shape()` reached through `emitBlock()` **from inside the
table/column pass** (`columnPage()`, lines 2062 / 2203 / 2271). There it still wrote one paragraph per
shape. That is the 21 documents this patch changes.

## The change

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, +47/−5:

| location | change |
|---|---|
| `Ctx` | new `shapeCarrier` StringBuilder |
| `shape()` | appends `shapeRun(...)` to the carrier instead of wrapping it in `<w:p>` |
| `flushShapes()` (new) | writes the carrier as ONE `<w:p>` with `SHAPE_PARA_PPR`, then clears it |
| `pageBody()` | clears the carrier on entry (the budget guard writes a page up to 3×) and flushes at both exits |
| `columnPage()` | a cell whose only block was a shape still gets a paragraph |

Geometry is untouched: every drawing keeps its `wp:positionH/V relativeFrom="page"` + `wrapNone`, so the
anchor never consults its paragraph. Verified: drawing count and every drawing's (x, y, extent, docPr id)
identical in all 21 changed documents.

## The measurement — Google, not LibreOffice

Rendered through Drive exactly as `gverify.py` does (upload → `GOOGLEDRIVE_CREATE_FILE` as
`application/vnd.google-apps.document` in `KavoPDF-Test-Outputs` → `GOOGLEDRIVE_DOWNLOAD_FILE` as PDF →
page count with PyMuPDF). Before arm = HEAD engine, after arm = HEAD + this patch, both converted in the
same sandbox with `tools/p2w-bench/build-engine.sh`.

| document | source pages | HEAD | + patch | 42 checks (Google, after) |
|---|--:|--:|--:|:--|
| `361_product_catalogue_grid` | 1 | **2** (refused by gverify) | **1** | 41/42 — only `25_invisible_text` (render=2) |
| `401_trifold_brochure` | 1 | 2 | 2 | still refused |

`361` was one of the 23 documents gverify refuses to score. It is now scorable and 41/42.
`401` was predicted to be a coin flip by the 0530 finding (0 pt of free space, full-bleed landscape
trifold); it is a coin flip that came up short — 20 × 0.83 = 16.6 pt saved against ~0 pt of slack.

## What did NOT change (and why that is not a failure)

- LibreOffice page count: identical on all 21 changed documents, and all 42 checks return the same
  verdict. LibreOffice honours `w:line="1"` exact; Google does not. This is precisely the case the
  charter says to distrust the proxy for.
- The `.txt`: byte-identical on 213/213. Re-scored with `restamp_txt.py --run` → "213 scored, 0 documents
  newly clean, 0 newly failing, 213 unchanged".
- `.docx` `document.xml`: byte-identical on 192/213; 21 changed, all of them fewer paragraphs
  (361: 124 → 40 paragraphs, 91 drawings either way).

## Why it is not landed

The commit gate needs BOTH tables re-measured on the new engine:

    ENGINE CHANGED (docx): table measured on 4a607e4b793fb348, the tree is 3e7f7c4475343a35
    ENGINE CHANGED (txt):  table measured on d20930229132b191, the tree is b97d8172ce642eb0

The `.txt` half was re-measured in 47 s (`restamp_txt.py --run --budget 240`, resumable, 213 scored).
The `.docx` half is `benchmarks/gate.py --budget 250`, which did **not** finish inside one 290 s call —
it produced no output and wrote neither `RANKING.csv` nor `STATE.json`. That is the whole of the gap: the
measurement outlives the call limit, not the evidence.

**Next run, in this order:** apply the patch → `build-engine.sh` → `python3 benchmarks/gate.py --budget 250`
across two or three calls until `RANKING.csv` and `STATE.json` are rewritten → commit engine + table
together → `regress.py --stamp` → commit the stamp → `regress.py --check` → push.
`regress.py --stamp` refuses until the table is committed at or after the engine, so the engine and its
table must be in the SAME commit; stamping first is impossible by design.

## Probes spent, do not repeat

Google A/B on two documents, 4 Drive documents created in `KavoPDF-Test-Outputs` (names `gv/b361…`,
`gv/a361…`, `gv/b401…`, `gv/a401…`). Nothing deleted, nothing written to the Drive root.

`GOOGLEDRIVE_DOWNLOAD_FILE` does **not** return `downloaded_file_content.s3url` any more — it returns
`artifacts[0].workspace_path`, a local path. `gverify.py --collect` expects an s3url, so it cannot be
called with what the tool hands back today; the page count and the 42 checks were therefore run directly
(`verify_google.py <src> <render> --docx <docx>`). That mismatch is itself a defect in the instrument and
is worth fixing before the next gverify run.
