# t12 on the two account-opening forms is 127 U+FFFD characters, not a welded `Y`

**25 Nov 2026, fixer slot 22:58.** Two attempts, both measured, both reverted. One finding: the
root cause the previous two runs worked from is not the cause, and the real one is a font-decoding
gap with a one-line trigger and a larger fix behind it.

## What was believed

`FINDINGS/25NOV-CELL-CARRY-GUARD-t12-vs-content-2005.md` (the 20:56 run) diagnosed the three
`t12_word_invention` documents as the carry-on rule at `PdfToWord.java:7904-7908` welding a glyph
onto the previous table cell: `(Authorised signatory)` starts at x=153.46 with the table's right
edge at x=145.0, so the last cell read `(Authorised signatory)Y`. That run's patch fixed the .txt
and broke two other documents, and was reverted. The next run was told to print the glyph.

## What the characters actually are

Measured on the two forms directly, comparing the source PDF's own text layer (`fitz`) with the
engine's `.txt`, on the committed engine:

    Account_Opening_Form_Fillable_filled   src=48936  txt=270609
        surplus (in .txt, not in source) = 127   ALL of them U+FFFD (�)
        missing (in source, not in .txt) = 148   of which Hcircumflex 89, Hstrok 23,
                                                 gbreve 13, hstrok 2  -> exactly 127
    041122-Account_Opening_Form            src=48837  txt=270521
        surplus = 127   ALL U+FFFD
        missing = 143   same four letters, exactly 127

127 for 127, one for one. This is not an invented character: it is **127 characters that arrive as
the Unicode replacement character**, and `t12_word_invention` counts them as a surplus because
U+FFFD is not in the source. The same 127 also drive `t06_encoding`, which fails on the same two
documents — one cause, two checks, and `chars_missing = 131` on the .docx side.

The source text is genuinely those letters: page 1 of `041122` carries `(Oģ)` where the page shows
`(Off)`. The PDF's text layer is itself the scrambled thing, and the check compares against it.

## Why the engine emits U+FFFD

`PdfToWord.java:2501 isJunk(String)` is the gate that decides whether `tp.getUnicode()` is readable,
and only when it says junk does `decodeThroughFont` (`:2513`, the glyph-name path) run. Its test was

    if (c < 0x20 || (c >= 0x7F && c <= 0x9F)) continue;   // control codes
    return false;                                        // everything else is text

`0xFFFD` is neither a control code nor below 0x20, so **the replacement character was taken as
readable text** and the fallback never ran.

The font is `REAQAG+Effra-Regular` as a **Type0 / Identity-H** font (`C2_0`) with no usable
ToUnicode; the WinAnsi `TT0`/`TT1` copies of the same face are fine.

## Attempt 2, measured, and why it did not land

Adding `if (c == '\uFFFD') continue;` to `isJunk` (12 lines) compiles and converts, and the
measurement is unambiguous:

    Account_Opening_Form_Fillable_filled   surplus 127 -> 141   (U+FFFD still 127)
    041122-Account_Opening_Form            surplus 127 -> 141   (U+FFFD still 127)

The fallback now runs and returns the replacement character anyway — `font.toUnicode(code,
GlyphList.getAdobeGlyphList())` has no answer for this font — while 14 real characters appear
elsewhere. Surplus up on both documents: **a document getting worse**, so it does not land.
Reverted; `git diff app/` empty.

## Attempt 1, measured, and why it did not land

Before the characters were counted, the carry-on hypothesis was implemented as the previous run
asked: refuse the carry when the glyph's line will be written as a paragraph anyway (line centre
outside the table box, so the cell copy is a second copy by construction).

    corpus-changed.py --record   after converting all 213 on the patched engine
        1 of 213 documents changed: Account_Opening_Form_Fillable_filled
        (041122 did not change at all - the rule does not fire there)
    txt   RANKING-TXT.csv, 213 rows compared semantically
        0 rows changed, 204 clean before, 204 clean after, 041122 still t06 t09 t12
    docx  Account_Opening_Form_Fillable_filled
        share5 97.62 -> 97.62   chars_missing 131 -> 131   order_share 78.94 -> 78.94

The guard fires, changes bytes, and moves no score. The welded `Y` was never the defect. Reverted.

## The next probe, and it is a number now

The fix has to come from the font, not from the layout. In order:

1. **Print the font's own answer.** At `:2513`, for a Type0 font, print `font.getName()`,
   `tp.getCharacterCodes()`, `font.toUnicode(code)` and `font.getEncoding().getName(code)`. If the
   encoding names the glyphs (`Hcircumflex`, `Hstrok`, `gbreve`, `hstrok`), then the Adobe Glyph
   List is the answer and `decodeThroughFont` is calling the wrong overload.
2. **Read the embedded TrueType cmap by GID.** For an Identity-H font the code IS the glyph id, and
   the embedded face (`getFontDescriptor().getFontFile2()`) has a cmap that maps GID -> Unicode.
   This is what MuPDF does to produce `Ĥ` where we produce `U+FFFD`. It is a real piece of work -
   a cmap subtable parser - and it is the whole fix.
3. **Do not** touch the carry-on rule again for these documents. It is measured dead here.

## The safety result worth keeping

Refusing a carry only when the line's centre lies outside the table box cannot lose a character, by
construction: that line is written as a paragraph. That argument survives; it simply does not apply
to this document. If a future run needs the carry rule narrowed, this is the narrow form to use.
