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

## What the residual 30 characters are - and who owns them

The page carries seven annotations (raw `/Annots`, read with PyMuPDF):

| xref | /Subtype | /Contents | /AP /N |
|---|---|---|---|
| 78 | Highlight | - | draws the band |
| 80 | Underline | - | draws the rule |
| 82 | StrikeOut | - | draws the rule |
| **84** | **Text** (sticky note) | **"Rate for HSN 8536 confirmed with PO."** | **an icon** |
| 85 | Popup | - | none |
| **87** | **FreeText** | "Checked against PO 4471. Quantity on line 3 raised from 20 t..." | **draws the text** |
| **89** | **Stamp** | "Approved" | draws "APPROVED" |

The 30 remaining invented characters are exactly xref 84, the sticky note:
`RateforHSN8536confirmedwithPO.` = 4+3+3+4+9+4+2+1 = **30**.

That is not an engine defect and no engine guard can reach it. A `/Text` note's appearance is an
**icon**; the words exist only in `/Contents`. The engine is right to carry them (the .docx side has
`50_annotation_text` asking for exactly that string), and `verify_txt.py`'s source side is built from
**glyph truth**, which cannot see a string that was never drawn. So the .txt is charged for words the
source side refuses to count.

**The fix therefore belongs in the instrument, not the engine:** the txt source side should add each
annotation's `/Contents` to its source character multiset - the strings the engine is required to
emit - before `t12_word_invention` compares. That is an instrument edit, it does not move the engine
fingerprint, and it does not need the 213-document docx ratchet. **It does need its own measurement**
(a txt re-measure over the corpus, because relaxing a source side can hide a real invention
elsewhere), and this slot ended before that could be run honestly.

What the guard DID remove (83 -> 30, i.e. 53 characters) is xref 87, the `/FreeText`: its appearance
draws the same words the hoist was writing at the top of the page. So the guard is correct and
measured; it is simply not the whole of this document's failure.

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
