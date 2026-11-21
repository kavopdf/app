# The rule carrier DRAWS in Google — and two floating tables stack under the first

**21 Nov 2026 · relay/fixer slot 19:58 · measured through Google Docs on
`73_marksheet_subject_marks_grade`, three exports, one per variant · engine reverted**

## Why this was measured

`classpick.py --leverage` prices `32_stroke_lines` at 36.3 clean documents, `05_chars_extra` at 35.0
and `18_displacement` at 28.6, and the three travel together on 51 documents. The last run closed
the placement blocker: a floating table (`w:tblpPr`) is honoured by Google and costs 0.00 pt of
flow. This run built that carrier into the engine and took it to the renderer.

## What was built

`DocxWriter.ruleCarrier()` — a hairline shape (a 0.4–1.5 pt rule, drawn either as a stroke **or as
a thin filled rectangle**) leaves the writer as a one-cell floating table: `w:tblpPr` at the page's
own x/y, `w:tblW`/`w:tblGrid` at the rule's length, `w:tblLayout fixed`, one `w:trHeight w:val="1"
w:hRule="exact"` row, and a `w:tcBorders` bottom edge at the rule's weight and colour. The patch is
`FINDINGS/32_stroke_lines-FLOATING-CARRIER-DRAWS-BUT-STACKS-2050-f1x.patch`; the engine was
reverted, nothing is in the tree.

The measurement that made the build possible, and which the previous finding did not have: **on
this corpus a rule is usually a FILL, not a stroke.** Both rules on `73_marksheet` leave the writer
as a filled 483 × 0.9 pt rectangle with `a:ln noFill` and `lineRgb = -1`. A carrier gated on
"has a stroke colour" would have skipped every rule on the document the class was opened on.

## The measurement

Three variants of the same document, same engine, uploaded to `KavoPDF-Verify`, converted to a
Google Doc, exported back as PDF, and scored with `verify_google.py` against the source PDF.

| variant | rules drawn in the Google export | `05_chars_extra` | `18_displacement` | `32_stroke_lines` | verdict |
|:--|:--|--:|--:|--:|:--|
| **before** — floating `wp:anchor` drawing | **0 of 2** | 2 | 1 | 1 | 39/42 FAIL |
| **A** — floating table, `tblpPr` | **2 of 2, both at y 83.5 / 84.5** | 2 | 1 | 1 | 39/42 FAIL |
| **B** — A + `w:tblOverlap w:val="overlap"` | 2, same two y | 2 | 1 | 1 | 39/42 FAIL |
| **C** — A with `tblpPr` removed (inline) | 2, at y 792.5 / 793.5, **x 0 → 483** | 2 | 1 | 1 | 39/42 FAIL |

Source rules, for the record: y = 84.0 (0.9 pt, `0F1F52`) and y = 793.89 (0.5 pt, `BFBFBF`),
x 56.0 → 539.28 on both.

## Four things settled

1. **A cell border IS drawn by Google where a floating drawing is not.** Before: 0 rules. After:
   2 rules, at the requested weight and colour. This is the first time the corpus has seen Google
   draw a rule the engine emitted.
2. **Only the FIRST floating table in a document is placed at its `w:tblpY`.** Rule 1 asked for
   83.6 pt and was drawn at 83.5 pt — exact. Rule 2 asked for 793.6 pt and was drawn at **84.5 pt**,
   one rule-thickness below rule 1. Two `w:tblpPr` tables in one document do not stack vertically;
   the second is placed against the first. So a per-rule carrier can carry exactly one rule per
   page, and `32_stroke_lines` still reads `render=1` of 2.
3. **`w:tblOverlap w:val="overlap"` does not change that** — variant B is byte-different and
   render-identical to A.
4. **An inline carrier cannot be placed in x.** Variant C dropped `tblpPr`: both rules moved to the
   end of the flow (y ≈ 793) and their left edge went to **x = 0**, not the requested 56 pt —
   `w:tblInd` inside a table with `w:tblLayout fixed` does not survive the conversion here. The
   inline route is therefore not a fallback.

## The extra character is NOT a property of tables

A four-case probe (`A1` paragraph, normal table with text, normal table with an empty cell,
floating table with an empty cell) rendered through Google carried **0** `U+200B` and 0 extra
characters. So a table — floating or not — does not itself cost a character. On `73_marksheet` the
render carries exactly **2** `U+200B`, one after `Examinations` and one after `marksheet`, i.e. at
the two points where the carrier band overlaps running text. The working hypothesis, **not yet
measured**: Google emits the `U+200B` when text WRAPS around the floating band, not when a table is
merely present. If that is right, a carrier placed in white space costs no character at all, and
`05_chars_extra` clears with it.

## What this costs, and what the next run should do

`73_marksheet` reads 39/42 before and after: the carrier changes the render (0 → 2 rules drawn) and
moves no verdict, so **nothing landed**. It is a lead, and it is a narrower one than it was:

* **One floating table per page, all of that page's rules as rows of it.** Rows inside one table
  do stack, so `tblpY` = the first rule's y and each row's exact height = the gap to the next rule
  puts every rule at its own y with one `tblpPr` — and one band, one wrap region, one `U+200B` at
  worst instead of one per rule.
* **Place the band in white space where the page has white space.** The ZWSP hypothesis says a
  carrier that does not overlap text costs nothing; that is one probe (a rule drawn through a
  paragraph vs between two) and it decides `05_chars_extra` for the whole class.
* **Do not retry** the per-rule floating table (stacks, measured), the inline table (loses x,
  measured), or `tblOverlap` (no effect, measured).

## How to repeat it

    bash tools/p2w-bench/build-engine.sh
    # ConvertOne <pdf> <outdir> with the patched tree
    upload -> GOOGLEDRIVE_CREATE_FILE(mimeType=application/vnd.google-apps.document,
              parents=["KavoPDF-Verify folder"], file_to_upload={s3key})
    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId, mimeType="application/pdf")
    python3 tools/p2w-bench/verify_google.py <source.pdf> <export>.pdf --docx <built>.docx --json <out>.json

    Then read the drawn segments directly, which is what caught the stacking:
    fitz.open(export).get_drawings() -> items of type "l", y of each.
