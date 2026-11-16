# run-size-from-sizePt-not-Tf

**Status: measured, NOT KEPT. The engine is reverted; this patch is not applied.**

Applied on 16 Nov by the fixer, measured on the class's own two documents, then reverted
because the class did not pass and the full 213-document ratchet was not run in that slot.

## The bug

Every `Run` inside a text box carried the raw `Tf` operand as its point size, not the size
the glyph was actually drawn at.

A PDF can put its scale in the TEXT MATRIX instead of the `Tf` operand:

    /TT0 1 Tf                 <- the size operand is 1
    6 0 0 6 71.3 493.7 Tm     <- the real scale is 6

PDFBox then reports `getFontSize() = 1.000` and `getFontSizeInPt() = 6.000`. The engine read
the first. `runsOf()` and the paragraph/ring paths built `new Run(..., first.size, ...)`
from `Glyph.size`, never `Glyph.sizePt`.

The `.docx` for `041122-Account_Opening_Form` carried **4088 runs, all at `w:sz w:val="2"`**
- 1 pt - and the LibreOffice render was boxes with no words at all.

**Why 211 synthetic documents never showed it:** on every document where `Tf` carries the
size, `getFontSize()` and `getFontSizeInPt()` are equal. A form PDF is exactly the shape
that separates them. The corpus could not see this defect until the real-world set was added.

## What it changes

Two call sites, both `new Run(...)` constructions, to prefer `lead.sizePt` when it is
positive and fall back to the computed size otherwise:

    app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
      @@ -3993   runsOf() ring path
      @@ -5102   paragraph path

Plus the accessor and comment that explain why the two sizes differ.

## What it measured

    document                              before    after
    041122-Account_Opening_Form
      pages 1-6 mean share@5              82.1 % -> 18.3 %
      p1                                  40.0   ->  9.4
      p3                                  92.9   -> 10.6
      p4                                  87.1   -> 20.4
      p5                                  97.0   -> 15.5
      p6                                  96.8   ->  1.6
      worst page                          98.65  -> 94.92
    Account_Opening_Form_Fillable_filled
      worst page                          97.62  -> 90.31
      mean over 9 pages                          72.5

No page of `041122` got worse.

## Why it was not kept

Two reasons, both honest:

1. **The class does not pass.** The worst page is still 94.92 %@5.
2. **The full 213-document ratchet was not run in that slot.** This patch touches every run
   in every text box, so it can move every document in the corpus. Keeping it on a two-document
   measurement would be exactly the kind of unverified change the ratchet exists to stop.

## How to use it

    cd /scratch/work/base            # or any clean clone
    git apply --check tools/p2w-bench/patches/run-size-from-sizePt-not-Tf.patch
    git apply        tools/p2w-bench/patches/run-size-from-sizePt-not-Tf.patch

Verified on 16 Nov: **it applies cleanly** to the committed engine.

Then, in this order:

1. **Run the ratchet across all 213 documents.** Not the class's two. This patch moves text
   size everywhere, and a size change moves every line box, so the blast radius is the corpus.
2. **Then fix the page spill** - it is the class's remaining real cause. With the text at its
   true 6 pt, `041122` still emits 10 pages against the source's 9 and the fillable form 11:
   source page 7 overflows, everything after shifts one page, and pages 7-9 read 74-95 %@5
   purely because page *i* is compared against page *i*. Fix the spill and the same documents
   should fall from ~90 %@5 into the pages 1-6 range.

**Do not re-derive the size bug.** It is solved and evidenced above.
