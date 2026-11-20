# t01_word_accuracy - the U+FFFD is the CMap's own answer, and the fix is one guard

Run: fixer, 21:57-23:05 IST 20 Nov 2026. Class taken: t01_word_accuracy (carry-over, per HANDOFF.md).
Status: **proven on two documents on the .txt axis, engine change REVERTED unmeasured at corpus scale.**
The patch is in `FINDINGS/fffd-cmap-destination-2300-fixer.patch` and applies cleanly to `e5268fe`.

## The mechanism, with evidence

The 127 tokens of U+FFFD in `041122-Account_Opening_Form` are not a missing CMap and not a
failed `bfchar` parse. They are the CMap's **destination** value.

    REAQAG+Effra-Regular  /ToUnicode obj 117: 91 well-formed beginbfchar entries,
                          four of them <0123> <FFFD>  <0124> <FFFD>  <0126> <FFFD>  <0127> <FFFD>
    WWLUSW+Effra-Medium   adds <0124>/<0126> -> FFFD
    IWIJEY+Effra-Bold     adds <0124> -> FFFD

pdfbox-android 2.0.27.0 returns that value verbatim: `PDFont.toUnicode` at PDFont.java:474
returns the CMap's mapping, and `PDType0Font.toUnicode` returns at PDType0Font.java:489-492
before its own embedded-cmap fallback can run. A non-null mapping is authoritative.

The engine then trusts it. `PdfToWord.GlyphCollector.processTextPosition` line 2101
(`String u = tp.getUnicode();`) takes U+FFFD as the page's word, and `isJunk()` at line 2501
returns false for U+FFFD, so the existing re-decode fallback at lines 2107-2110
(`decodeThroughFont`) never fires.

Identity-H says the code **is** the CID, so the code is the only handle the font still gives.
That is also what PDFBox already does for an Identity font with no /ToUnicode at all
(PDFont.java:459), so the two cases should agree instead of the second one winning on a
technicality.

## The patch (two hunks, one helper)

- `PdfToWord.recoverUndefinedCids(TextPosition, PDFont)` - new static helper, ~50 lines with
  its docstring. Returns null unless `/Encoding` is a COSName starting `Identity-`, unless the
  character code currently maps to U+FFFD, and unless the recovered string differs. Control
  codes (< 0x20, 0x7F-0x9F) keep their U+FFFD: a visible gap beats a NUL the reader cannot see.
- `PdfToWord.processTextPosition` - after the existing `decodeThroughFont` fallback, call the
  helper when the string still carries U+FFFD.
- `PdfEngine` (position/search index, line ~1753) - the same recovery, so a search for a word
  the page draws as a ligature does not miss it because the index holds U+FFFD.

No document id appears anywhere in it. The condition is the font's structure.

## What was measured

Engine built from the patched tree (`tools/p2w-bench/build-engine.sh`, compiles clean, ecj
0 errors), then both documents converted with `ConvertOne` and scored with
`tools/p2w-bench/verify_txt.py` - the live .txt check, not a proxy:

    document                                   before (RANKING-TXT baseline)      after
    041122-Account_Opening_Form                7 of 10 failing                    3 of 10 failing
      failing: t01,t03,t06,t07,t08,t09,t12       -> t08, t09, t12 only
    Account_Opening_Form_Fillable_filled       7 of 10 failing                    3 of 10 failing
      failing: t01,t03,t06,t07,t08,t09,t12       -> t08, t09, t12 only

    U+FFFD in our .txt: 127 and 127 before -> 0 and 0 after, both documents.

So one change closes four checks on each document: t01_word_accuracy, t03_symbols,
t06_encoding, t07_symbol_counts. Both documents leave the t01 class.

## What was NOT measured, and why

The docx corpus pass did not run. `screen.py --docs` on these two documents could not get past
prerender in three consecutive 295 s calls: soffice takes about 80 s to start and these are
nine-page forms, so the call limit is spent before a single document is scored. The .txt sweep
(`restamp_txt.py --run`) needs `/scratch/work/p2w/out`, which only `p2w.py` populates, and
`p2w.py --budget` would have needed four or five more calls.

Because `benchmarks/RANKING.csv` and `STATE-TXT.json` were not regenerated, the class file still
carries these rows OPEN and the engine change has no kept attempt behind it. It was therefore
reverted at the end of the run rather than left in the tree - an unmeasured engine change must
not ship.

## What the next run should do - this is a full-slot job, and it is the whole remaining win

1. Apply `FINDINGS/fffd-cmap-destination-2300-fixer.patch` (applies clean to `e5268fe`).
2. Run `python3 benchmarks/p2w.py --budget 250` repeatedly until it says complete. This
   populates `/scratch/work/p2w/out` with .docx **and** .txt for all 213, and gives the docx
   ratchet in the same pass - the patch moves the docx fingerprint, so that pass is required
   either way.
3. `restamp_txt.py --run` then `--apply`, then `classrow.py --write`. Expect t01 7 open -> 5,
   and t03/t06/t07 to move with it.
4. `regress.py --check` before any commit.

Only these two of the 124 PDFs in the tree have `<FFFD>` in a /ToUnicode, so the blast radius on
the corpus is bounded - but the docx ratchet is what proves it, not that census.

## Ruled out

- A missing /ToUnicode CMap: every Effra face carries one.
- A malformed CMap: 91 well-formed beginbfchar entries, one per CID.
- PDFBox inventing a fallback: it returns the CMap's own destination value.
- The writer: `TxtWriter`/`DocxWriter` receive the U+FFFD already formed.
- The control-character fix of 21:49 (already landed, `_words` splitting) - that is a different
  mechanism and it is why the class went 10 -> 7 open before this.

## A second agent read the patch adversarially and says do not land it as written

Recorded 23:25 by a review agent that saw only the diff, in
`FINDINGS/fffd-cmap-destination-PATCH-REVIEW-2325.md`. Its objection is the strongest thing
in this run and the next run must answer it before the patch goes anywhere:

- `sb.append((char) code)` turns the CID into a code point. The CIDs measured here are
  0x0123/0x0124/0x0126/0x0127, which are the characters g-with-cedilla, H-circumflex,
  H-stroke and h-stroke. A bank form does not draw those. If the page really draws a
  ligature or a special glyph and the CMap declines to name it, this writes 127 wrong
  letters into the document - and wrong text that looks like text is worse than a visible
  U+FFFD, because nothing downstream can tell.
- One CID becomes exactly one char, so a CID that should expand to two characters cannot.
- The PdfEngine call site has neither `decodeThroughFont` nor `isJunk` precedence, so the
  search index and the exported .docx can hold different text for the same glyph - the
  divergence the patch's own comment claims to remove.

**And the review is right that the measurement above cannot settle it.** t01_word_accuracy
passes because our .txt now agrees with the source extraction, and the source extraction is
pymupdf, which resolves an Identity font the same way. Two extractors making the same
assumption agree with each other whether or not the assumption is true. The check moved; the
question did not.

The test that settles it costs one page, and it is STEP 4c - look at it. Render page 1 of
041122-Account_Opening_Form at 150 DPI, crop where the 127 glyphs sit, and read the letters
with an eye. If the page draws a ligature, the patch is wrong and the answer is the
CIDToGIDMap plus the descendant font's own cmap, not the CID as a code point. If the page
draws exactly what the CID names, the patch is right and the review's first risk is closed.

Until that is done this patch must not be landed, whatever the .txt number says.
