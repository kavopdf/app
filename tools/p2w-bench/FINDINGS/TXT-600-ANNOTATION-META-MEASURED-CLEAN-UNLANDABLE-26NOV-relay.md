# The .txt carries annotation text it must not — 600 goes CLEAN, and the change cannot be landed in one slot

**26 Nov 2026 · relay fixer, 04:27 slot · engine `d85db0a9822ddb54` at HEAD · patch in
`PATCHES/txt-meta-annotation-26NOV-relay.patch`**

## The defect, measured

`600_reviewed_invoice_with_annotations` failed exactly one .txt check, `t12_word_invention`, with
**83 invented characters** — and the characters are the page's *annotations*, not its text:

    annots on the page: Text(0) 'Rate for HSN 8536 confirmed with PO.'
                        FreeText(2) 'Checked against PO 4471. Quantity on line 3 raised from 20 to 25.'
                        Stamp(13) 'Approved'

`PdfToWord.annotationRuns()` appends every annotation's words as a paragraph so the **.docx** can carry
them (`50_annotation_text` asks for the string), and `TxtWriter` then writes those same paragraphs as
body text. A note and a stamp caption are panel content: the page prints nothing of them, so a .txt
that carries them invents text the source never drew.

## The change

`Para.meta` — a flag set on the paragraphs the annotation loop appends — and one line at the top of
`TxtWriter`'s page loop:

    page.blocks.removeIf(b -> b instanceof PdfToWord.Para && ((PdfToWord.Para) b).meta);

It is .txt-only by construction: every caller writes the .docx **first** and calls `writeTxt` last
(`ReadingOrder.java:24-30`, and `ConvertAll` in `tools/engine-verify`), so the .docx bytes are on disk
before the filter runs.

## The measurement, before and after

| | before | after |
|:--|--:|--:|
| `600_reviewed_invoice_with_annotations` | 8/12 applicable, 7 passed, **FAIL** (`t12` 83) | 8/12 applicable, **8 passed, PASS** |
| `word/document.xml`, 600 / 041122 / 601 | — | **byte-identical** (sha256 compared, all three) |
| `041122-Account_Opening_Form` | FAIL (`t06` 127, `t09`, `t12` 14) | unchanged |
| `601_fillable_admission_form` | FAIL (`t01` 97.6) | unchanged |

Predicted corpus effect: **204 → 205 of 213 .txt clean**. Not measured across the corpus, because the
gate needs the .docx table re-measured too (below), and that is what refused the change.

## Why it is not committed

`regress.py --check` refuses on an unmeasured engine, and an engine change moves the fingerprint of
**every** engine file, so `scope.py` says `docx, txt` — even for a change that provably cannot move a
.docx byte. Re-measuring the .docx table needs `benchmarks/p2w.py` over 212 documents, and that does not
finish in this pod (see `BLOCKERS.md`, "the .docx table cannot be re-scored inside a slot"). So the
patch is written, measured on the documents it names, and left for a slot that can pay the 45 minutes.

## What a landing run must do

1. apply `PATCHES/txt-meta-annotation-26NOV-relay.patch`
2. `bash tools/p2w-bench/build-engine.sh`
3. `python3 benchmarks/p2w.py --budget 250` until `remaining 0` (expect the table to be unchanged:
   `word/document.xml` is byte-identical on every document the patch touches)
4. `python3 tools/p2w-bench/txt_rank.py` (or `txt_gate.py --score 213`) for the .txt table
5. `regress.py --stamp`, then `regress.py --check` must PASS
