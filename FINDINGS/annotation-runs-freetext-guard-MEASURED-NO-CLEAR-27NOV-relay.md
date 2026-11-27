# Annotation `/Contents` hoisted into body text — the guard `annotationContentsOf()` has and `annotationRuns()` never got

**27 Nov 2026, 06:25 IST · fixer run (relay) · built, measured corpus-wide, reverted**

A genuine engine defect, measured before and after, that **clears no document** and is therefore not
committed. The patch is here for the run that wants to pay the 213-document re-measure.

## The defect

`PdfToWord.java` has two functions with the same job, and only one of them was fixed:

* `annotationContentsOf()` (`:2474`) carries the rule since 25 Nov, with its own comment:
  *"ONLY A FREE-TEXT BOX PRINTS ITS /Contents. A note, a comment, a highlight's remark and a stamp's caption
  are METADATA: the reader shows them in a panel, and the page itself prints nothing of them."*
  It skips any annotation whose `/Subtype` is not `FreeText`.
* `annotationRuns()` (`:2456`) — the one whose output is actually appended to `page.blocks` at `:956` — has
  no such test. Every annotation with a non-empty `/Contents` becomes a `Para` with `top = 0`, in the body
  of the document the user opens in Google Docs.

## The change

One line, at `PdfToWord.java:2463` (full diff: `FINDINGS/annotation-runs-freetext-guard-27NOV.patch`, 18
lines with the comment):

```java
if (!"FreeText".equals(ann.getSubtype())) continue;
```

## Measured, on one document first

`600_reviewed_invoice_with_annotations`, converted with `ConvertOne` before and after:

| | before | after |
|:--|:--|:--|
| paragraphs | 14 | **12** |
| `.txt` lines | 74 | **72** |
| `t12_word_invention` (invented chars of 785 source chars) | **83** | **49** |

The two lines that leave the `.txt`, exactly as the 25 Nov comment predicted:

```
Rate for HSN 8536 confirmed with PO.        <- the sticky note
Approved                                    <- the stamp's caption
```

## Measured, corpus-wide

The engine was rebuilt and all 213 documents re-converted (`corpus-convert.py --ensure -j 6`, 4.6 min,
engine `fadda06d2c958f18`), then every `.txt` byte-compared against the corpus at `a4d8fca469bba636`:

* **1 of 213 `.txt` files changed** — `600_reviewed_invoice_with_annotations`, and no other.
* `.txt` clean count: **205 of 213 before, 205 of 213 after**, the same eight documents failing with the
  same check ids. No document got worse; none got better.

`regress.py --check` on the patched tree printed **"docx: no document worse than baseline / txt: no document
worse than baseline / google-safe: no construct Google ignores has spread"** and then **REFUSED**, correctly,
because the engine moved and the tables were measured on the old one:

> `ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tree is fd881781d022a58e`
> `ENGINE CHANGED (txt): table measured on a4d8fca469bba636, the tree is fadda06d2c958f18`
> `An unmeasured change is not a pass. Re-measure, then --stamp.`

## Why it is reverted

**It clears no document.** `600` still fails `t12_word_invention`, at 49 invented characters instead of 83.
Landing it would cost a full 213-document LibreOffice re-measure — the last run paid four ~265 s chunks for
exactly that — to move a number on one document's failing check without turning it green. The charter's test
is *"if this works, which documents become CLEAN?"*, and the honest answer here is none.

It is still a real improvement in fidelity: two paragraphs of text no page prints were in the `.docx` the
user opens. **The next run should land it together with the change that finishes `600`**, so one re-measure
pays for both.

## What is left on `600` after the guard — measured, not guessed

The remaining 49 invented characters are **one FreeText box emitted twice**. `annotationRuns()`'s duplicate
guard at `:957` tests the annotation text against `flat`, the page's content-stream text:

```java
if (flat.contains(ar.text.replaceAll("\\s+", " ").toLowerCase(Locale.ROOT))) continue;
```

On `600` the FreeText *is* in the content stream — `.txt` line 0 and line 70 are byte-identical,
`"Checked against PO 4471. Quantity on line 3 raised from 20 to 25."` — and the guard does not catch it.
Two things the next run should measure, both visible in the code without a build:

1. **`flat` is `pageOwn` and the test is a whole-string substring match.** The annotation text is normalised
   to single spaces and lowercased, but `pageOwn` is the page's own text as *the engine* assembled it, and a
   sentence that the page sets across two paragraphs will never be a contiguous substring of it. The guard
   asks "is this exact sentence somewhere in the page", when the question is "are these words already here".
2. **`drawnByAppearance(apDrawn, v)` is applied to the form values at `:945` and NOT to `annotationRuns`.**
   That is the same asymmetry this file is about, one level down: a FreeText box's `/Contents` and the
   string its `/AP /N` draws are the same words, and the appearance puts them where the reader saw them. The
   form-value loop dedupes on it; the annotation loop does not.

Either is worth about 30 of the 49 remaining characters. The other ~19 are the truncated table amounts in
the right-hand column (`Amou…`, `22,2…`, `3,8…`), which is a different construct and is not in this file.

**And `600` will still fail after either.** 49 − 30 = 19 invented characters. It is a multi-defect document:
finish it as one attempt with all three changes and one re-measure, not three attempts with three.
