# The annotation /Contents hoist has a second door - measured, patched, not landed

**25 Nov 2026, relay fixer slot 17:16 IST. Engine 981ff1fa35e2cf67 + one uncommitted edit.**

## The construct

`PdfToWord.pageText()` hoists annotation words onto the page when the page already has a text layer,
through two loops that sit six lines apart:

* the form-value loop (`formValuesOf`, ~line 942) already carried the guard
  `if (drawnByAppearance(apDrawn, v)) continue;`
* the annotation loop (`annotationRuns(pdPage)`, ~line 956) did **not**.

So an annotation whose `/Contents` is *also* drawn by its own `/AP /N` appearance was written twice:
once where the appearance puts it, once hoisted as an 11 pt black paragraph at the top of the page.

## Measurement - before and after, one document, same reader

`600_reviewed_invoice_with_annotations`:

| | before | after |
|---|--:|--:|
| `verify_txt.py` t12_word_invention, invented characters | **83** | **30** |
| paragraphs written | 14 | 13 |
| verdict | FAIL | FAIL |

Commands:

    python3 tools/p2w-bench/verify_txt.py /scratch/work/p2w/corpus/600_reviewed_invoice_with_annotations.pdf /scratch/work/p2w/out/600_reviewed_invoice_with_annotations.txt
    # -> t12_word_invention source=785 txt=83
    # apply the guard, javac the engine, ConvertOne the one document
    python3 tools/p2w-bench/verify_txt.py ... /scratch/work/probe1/600_reviewed_invoice_with_annotations.txt
    # -> t12_word_invention source=785 txt=30

This reproduces the pending note's prediction (20 tokens/83 chars -> 7 tokens/30 chars) exactly.

## What the residual 30 characters are - and why the guard did not reach them

The 30 remaining invented characters are exactly the free-text comment's own words:

    Rate for HSN 8536 confirmed with PO.     (4+3+3+4+9+4+2+1 = 30 non-space characters)

That is a `/FreeText` annotation. Its `/Contents` is hoisted as a body line at the top of the `.txt`,
so its appearance stream did **not** satisfy `drawnByAppearance(apDrawn, text)` - the guard is not
reaching this annotation's appearance at all. Either `readAnnotationAppearances()` does not read a
`/FreeText`'s `/AP /N` into `apDrawn`, or the appearance draws the string in a form the whitespace
normalisation does not match. **That is the next measurement, and it is the one that makes this
document clean**, not this guard.

## Why it is a patch file and not a commit

The edit is in `app/src/main/java/.../PdfToWord.java`, so it moves the engine fingerprint. A moved
fingerprint needs a full-corpus re-measure (docx and txt, 213 documents) before the commit gate will
accept it, and this slot had ~20 minutes left when the measurement finished. It moves no document to
CLEAN on its own: 600 still fails t12 at 30 characters. Landing an engine-wide re-measure for a
document that does not become clean is the wrong trade; the patch is saved at
`tools/p2w-bench/patches/annotation-contents-hoist-guard.diff` with the measurement above, ready for a
slot that can afford the ratchet.

The rule this leaves behind, stated without a class name: **when two adjacent loops read the same
words from two sources, a guard added to one of them must be added to both, and the measurement must
name which source the remaining difference came from.** The census that found the first door did not
look for a second.
