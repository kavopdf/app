# The rule carrier works on a real document: 394_map_with_legend 41/42 -> 42/42 in Google

**21 Nov 2026 · relay slot 19:26 · measured through Google Docs, before and after, one document**

## The answer

The floating-table carrier the 18:17 run measured in a synthetic probe **lands on a real document**.
`394_map_with_legend` was **41/42 in Google, failing `32_stroke_lines` alone**, and is **42/42** with the
engine change in `tools/p2w-bench/patches/rule-carrier-tblppr-2008.patch` — same document, same source
PDF, same 42 checks, both numbers measured through Google Docs itself.

The patch is written, compiled, measured, and **not committed**: an engine change may not land without a
full-corpus measurement of the tree (`regress.py --check`), and that measurement does not fit in one slot.
See "Why it is not in the tree" below.

## Before and after, both in Google

| | engine | Google | LibreOffice proxy | `32_stroke_lines` |
|:--|:--|--:|--:|:--|
| before | `7112d76` (recorded in `benchmarks/gverify/`) | **41/42** | 42/42 | 1 rule lost |
| after | patch, uncommitted | **42/42** | 42/42 | 0 lost |

The before number is not re-derived here: it is the committed record in `benchmarks/gverify/394_map_with_legend.json`
(`passed 41, total 42, failed ["32_stroke_lines"], engine 7112d76`). The after number is this run's, from
the Drive round trip described at the end.

## What the patch emits, and the two things the probe did not know

A page rule is a **floating 1x1 table** (`w:tblpPr`, `vertAnchor="margin"`, `horzAnchor="margin"`) whose
one `w:tcBorders` edge is the rule — the construct measured on 21 Nov in
`32_stroke_lines-TBLPPR-ZERO-FLOW-1905-f1x.md`. Two numbers had to be fixed before it worked, and neither
was in the probe:

1. **`w:tblCellMar` must be zeroed, or every rule lands 5.4 pt to the left.** A table with no
   `w:tblCellMar` gets Word's default 0.075 in (108 twips, **5.4 pt**) left inset, and the renderer puts
   the table's left edge — which is the border the carrier draws — that far left of `w:tblpX`. Measured in
   the LibreOffice proxy: the 20 pt rule asked for at x 395.28 rendered at **389.9**, covering **73 %**
   of its own length against `32_stroke_lines`' **80 %** floor, and was reported lost. With the margins
   zeroed it renders at **395.30**. Every other table `DocxWriter` emits already zeroes its margins; the
   carrier had to as well.
2. **The rule predicate must use the instrument's own definition of a rule, not a narrower one.** The
   first build cut off at 2.5 pt and left the document's third rule — a **20 x 3.0 pt legend swatch** — on
   the old anchored-drawing path, which is the path Google drops. Google scored it **41/42** with exactly
   that one rule missing. `verify_google.py`'s `RULE_THIN` is **4.0 pt**; the predicate now matches it.

Neither of these is a Google defect. Both are the engine writing a number the page did not draw.

## The patch

    tools/p2w-bench/patches/rule-carrier-tblppr-2008.patch     186 lines, 169 insertions, one file

| | |
|:--|:--|
| site | `DocxWriter.shape()` — the only function that emits a rule; its only caller is `emitBlock()` |
| dispatch | 12 lines at the top of `shape()`: `if (isRuleShape(s)) { ruleCarrier(sb, s, ctx); return; }` |
| carrier | `RULE_MAX_PT` 4.0, `isRuleShape()`, `ruleCarrier()` |
| call sites changed | none — the dispatch sits behind the existing function |

**The patch in the file is the build that was measured.** Rebuilt from it and compared: the resulting
`word/document.xml` is byte-identical to the `.docx` Google scored 42/42.

## Why it is not in the tree

`regress.py --check` refuses a commit whose engine fingerprint is not the one the corpus tables were
measured on, and the pre-commit hook runs it. Measuring 213 documents with this engine costs **~21 s of
JVM per document** just to convert (measured here: `ConvertOne` on `300_prescription_rx`, 20.8 s), so
**~75 minutes** before any rendering or comparison. That is a slot and a half, from a cold sandbox with no
corpus, no JDK and no build.

So this run did what it could prove and stopped there: the construct is proven on a real document in the
renderer the user opens, and the code that proves it is in the repository as a patch rather than as an
unmeasured engine edit. **The next run that can afford a corpus measurement applies this file in one
step** — it needs no design work, only `git apply`, a rebuild and `benchmarks/gate.py`.

What has to be true for it to be right, and is not yet measured:

* **the other 144 rule-carrying documents.** One document is not a corpus. `regress.py` is the instrument
  that answers this and it has not been run.
* **multi-rule pages.** 46 carriers on one page (`407_id_card_front_back`) is still untested; the probe
  measured one.
* **vertical rules.** Mirrored by construction (row height = length, border on `left`), never measured on a
  document. This document's two vertical marks are not isolated rules, so `32_stroke_lines` did not ask.
* **the `.txt`.** Unchanged by the patch in this document (both builds produce the same `.txt`), but a
  table emits no text, so a rule that used to leave a `U+200B` anchor should now leave nothing at all —
  `05_chars_extra` should get *easier*, and that is an expectation, not a measurement.

## How it was measured

    ConvertOne 394_map_with_legend.pdf -> .docx                     (engine as patched)
    upload -> GOOGLEDRIVE_CREATE_FILE mimeType=application/vnd.google-apps.document
    GOOGLEDRIVE_DOWNLOAD_FILE mime_type=application/pdf             (Google's own layout)
    verify_google.py source.pdf export.pdf --docx built.docx        (the 42 checks)

The two Google Docs this run created were left in place, in `KavoPDF-Test-Outputs`, named
`394_map_with_legend (relay tblpPr probe)` and `... (relay tblpPr v2)` — the non-negotiable says nothing
is ever deleted in the user's Drive, and these are the evidence for the two numbers above. Nothing was
written to the Drive root.
