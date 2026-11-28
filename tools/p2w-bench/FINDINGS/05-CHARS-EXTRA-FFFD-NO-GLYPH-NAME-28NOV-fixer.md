# The U+FFFD ligatures carry no recoverable glyph name: the font has no `post` names and no `cmap`

**28 Nov 2026, fixer slot 08:24 IST. Measured with PDFBox-android 2.0.27.0, the engine's own reader, on
`041122-Account_Opening_Form`. This closes the recovery path that
`NO-FFFD-THE-LIGATURES-ARE-NOT-MAPPED-25NOV.md` proposed ("fall back to the glyph name — PDFBox exposes
it per glyph"). It does not, for this document.**

## What was measured

A probe (`tools/engine-verify/GlyphProbe2.java`, this run) walks every `TextPosition` whose unicode holds
`U+FFFD` and asks the font what it still knows about the code:

| font | code | `toUnicode(code, AGL)` | `toUnicode(code)` | glyph id | `post` table | `post` name | `cmap` table |
|:--|:--|:--|:--|--:|:--|:--|:--|
| REAQAG+Effra-Regular | 0x123 | U+FFFD | U+FFFD | 291 | absent (format null) | null | **absent** |
| REAQAG+Effra-Regular | 0x124 | U+FFFD | U+FFFD | 292 | absent | null | absent |
| REAQAG+Effra-Regular | 0x126 | U+FFFD | U+FFFD | 294 | absent | null | absent |
| REAQAG+Effra-Regular | 0x127 | U+FFFD | U+FFFD | 295 | absent | null | absent |
| WWLUSW+Effra-Medium | 0x124 / 0x126 | U+FFFD | U+FFFD | 292 / 294 | absent | null | absent |
| IWIJEY+Effra-Bold | 0x124 | U+FFFD | U+FFFD | 292 | absent | null | absent |

And the `/ToUnicode` CMap of the Type0 font (xref 117 of the source PDF) says so itself:

    90 beginbfchar
    <0123> <FFFD>
    <0124> <FFFD>
    <0126> <FFFD>
    <0127> <FFFD>

## What is now true

1. **The producer wrote the replacement character.** This is not a decode failure in our reader and not
   a glyph-name lookup we forgot to make: the PDF's own `/ToUnicode` maps these four codes to `U+FFFD`.
2. **The glyph name is not recoverable from the font.** The embedded subsets carry no `post` table
   (`getPostScript()` returns a table whose format is unset and whose `getName(gid)` is null) and **no
   `cmap` table at all** — `TrueTypeFont.getUnicodeCmap()` throws "does not contain a 'cmap' table". So
   neither the name→AGL route nor the unicode-cmap inversion the 25 Nov finding proposed can answer here.
   `font.getEncoding()` is null (Identity-H), so there is no `Differences` name either.
3. **The four codes are stable per face** (0x123/0x124/0x126/0x127 in Regular, 0x124/0x126 in Medium and
   Bold), which is what makes a per-document or per-face guess tempting and what makes it a guess.

## The only route left, and why it was not taken

The glyphs are `fi`/`ff`/`ffi`/`fl` substitutions. With no name and no cmap, the remaining signal is
**geometry**: a ligature's advance width is ≈ the sum of its components' widths, and the components are
in the same font. That is an inference, not a lookup — it would write "fi" where the page wrote a glyph
whose identity the PDF declines to state, and it can be wrong (`ff` vs `fi` differ by ~0.1 em in most
serif faces).

It is a legitimate candidate for a run with a slot to spend, and it is falsifiable in one document: take
the 127 occurrences, compare each ligature's `w` against `w(f)+w(i)`, `w(f)+w(f)`, `w(f)+w(f)+w(i)`,
`w(f)+w(l)` from the same font's ASCII glyphs, and check the assignment is unique on every one. If any
occurrence is ambiguous, the route is a guess and the class is a Google-side finding, not a fix.

## MEASURED 28 Nov 08:5x, same slot - the geometric route is a guess too

A second agent measured it (`05-CHARS-EXTRA-FFFD-GEOMETRY-IS-A-GUESS-28NOV-agent.md`): the four codes'
advance widths are 0.6370, 0.5390, 0.8470, 0.8580 em, and this font's ligatures run **0.013–0.048 em
narrower** than the sum of their components — 1.3 to 4.8 times the 0.010 em that separates `fi` from
`fl`. **0 of 127 occurrences resolve uniquely** at ±0.02 em; 87 are ambiguous and 40 have no candidate.
The 89 occurrences of `0x124` (70 % of the document) land nearest to `fl` while the glyph is `fi`.
Signal smaller than noise, so a width heuristic would write the wrong word 70 % of the time.

**So this class is closed as far as the PDF's own data goes: the producer wrote `U+FFFD`, and neither a
glyph name, a cmap, nor the geometry can recover the character.** What is left is a rendering-and-OCR
route, which is out of scope for this engine. The two documents stay open and their `.txt` stays wrong;
that is a finding, not a pending fix.

What would prove this wrong: a `/ToUnicode` in a later revision of the same form that maps these codes to
real characters, a font revision carrying a `post` table, or a width measurement that separates `fi`
from `fl` in this face — none of which the shipped bytes offer.
