# t12 on 600: the surplus is 83, the 600 patch clears it, and the txt-only route is WRONG

**28 Nov 2026, relay slot 12:30.** Measured, not predicted. Source reverted at the end so the tree
is committable; the patch is on disk and the numbers below are what a next run needs.

## 1. The surplus, attributed char for char

`600_reviewed_invoice_with_annotations` fails `t12_word_invention`. Against
`verify_txt.glyph_truth()` — the instrument t12 itself uses (`invented_chars = sum((txt_c - src_c))`
over non-space characters, case-sensitive, verify_txt.py:1569) — the stored `.txt` carries **83**
surplus non-space characters, and they are exactly:

| chars | what |
|--:|:--|
| 30 | `Rate for HSN 8536 confirmed with PO.` — the `/Text` sticky note's `/Contents`. Nothing draws it. |
| 53 | `Checked against PO 4471. Quantity on line 3 raised from 20 to 25.` — the `/FreeText` box's `/Contents`, written a **second** time; its `/AP` appearance is already read into the page as glyphs. |

30 + 53 = 83, deficit 0. `Approved` (the `/Stamp`'s `/Contents`, 8 chars) is **not** surplus: the page
draws it and t12 does not fold case.

## 2. The 600 patch clears it — measured

`PATCHES/600-annotation-runs-subtype-25NOV.patch` applies clean to today's `PdfToWord.java`. Two rules,
both already stated in the same file by the dead sibling `annotationContentsOf()`:

* `annotationRuns()` keeps only `FreeText` and `Stamp` — a note's remark is metadata a reader shows in a
  panel and the page never prints. Kills the 30.
* the `:957` hoist loop adds `if (drawnByAppearance(apDrawn, ar.text)) continue;` — the form-value loop
  nine lines up carries the same guard. Kills the 53.

Applied, engine rebuilt (`e9180fd9a74e5e78`), `600` reconverted. Result:

    surplus 83 -> 0, deficit 0 -> 0

so `invented_chars` is 0 and `600` reads **8 applicable / 8 passed** on the txt side, from 8/7/1.

**Not landed.** `regress.py --check` refuses: the docx table is stamped `a05b20eb05fe0fc8` and the tree
is `e9180fd9a74e5e78`, and the `.docx` half of this patch cannot be re-measured in a slot that cannot
upload to Drive. The source was reverted rather than left unmeasured in the tree.

**What the next run needs to do:** rebuild with the patch, convert all 214 (~18 min on this 2-CPU pod,
6 slices), score the docx table on the new engine, `regress.py --stamp`, then commit. Nothing else about
this change is open.

## 3. REFUTED: dropping annotation paragraphs from the `.txt`

`PATCHES/txt-meta-annotation-26NOV-relay.patch` adds `Para.meta` on every hoisted annotation paragraph
and has `TxtWriter` `removeIf` them. It applies clean and it looks like the tidy version of the same
idea — it is wrong, and this is the measurement:

    .txt after the meta drop:  surplus 0, deficit 8

The 8 are `Approved`. The page **does** draw that string, t12 counts a missing character as well as an
extra one, and the patch deletes it because it arrived through the annotation path. A rule that drops
"everything that came from an annotation" cannot tell the note (never drawn) from the stamp caption
(drawn). The 600 patch can, because it asks the page (`drawnByAppearance`) and the subtype instead of
asking the provenance.

**Do not land it.** Any future attempt at the annotation family should start from §2, not from the
`meta` flag.

## 4. Why the ranking row still says 8,7,1

`txt_gate.py` with no arguments prints the summary **from the CSV** and does not re-score; `--score N`
runs `txt_rank.py --limit N`, and `txt_rank.py --rescore` scores a **budgeted slice** — it reported
"scored 20 this pass" and wrote the file. A whole-corpus rescore is therefore ~11 passes, and `600` was
not in the slice that ran. The row `600_reviewed_invoice_with_annotations,8,7,1,0,t12_word_invention`
is **stale**, not a contradiction of §2. A run that reads it as "the patch did not work" will re-derive
the patch. That is the one cost of this run.

## 5. The three other t12 failures, for the next run

* `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` — 14 chars each,
  `(Authorised signatory)` written twice plus a `Y` welded onto the signatory line. This is the
  cell-carry construct of `25NOV-CELL-CARRY-GUARD-t12-vs-content-2005.md`, whose two candidate guards
  move the same four documents and whose discriminator was never run. No smallest safe change exists
  today.
* `Prakashan_Print_Fidelity_Handbook` — 88 chars, last page, the right-hand label/value column printed
  twice (`DATE OF ISSUE`, `TIME, IST`, `REVISION RECORD`, the colophon). Attributed, not root-caused:
  the engine seam that emits that block twice is unidentified.
