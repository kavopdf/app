# 39_small_caps_letter_spacing: both of its failures are the reference's, measured

20 Nov 2026, fixer run claimed 00:57, subagent B. The document is charged 2 of 9 checks,
`t01_word_accuracy` and `t12_word_invention`. This finding shows they are one fault seen from
two sides, and that the fault is the scoring reference's tokenisation, not the writer's output.

Everything below is printed from the measurement: engine built from the clone's head,
`ConvertOne` on the corpus PDF, `verify_txt.py` unmodified.

## The two checks, as scored today

    39_small_caps_letter_spacing.txt   9/12 applicable, 7 passed, 3 abstained   FAIL
        t01_word_accuracy          source=100        txt=97.4
        t12_word_invention         source=1281       txt=2

Recomputing the same two comparisons directly (`Counter(_words(src)) - Counter(_words(txt))`):

    SRC tokens: 306   TXT tokens: 302
    t01 LOST, total 8 ......  '0' x2, 'O', 'D', '.', ',', '57', '05'
    t12 INVENTED, total 2 ..  '570', '005'

The eight lost tokens and the two invented tokens are the same six digits and one address
punctuation pair, seen from opposite sides. Character content is identical between the two sides:
the multiset of non-whitespace characters in the source and in the .txt is equal, and so is their
order. Only the word boundaries differ.

## The page's text state, measured

| property | measured |
|---|---|
| pages / MediaBox | 1 / 595.276 x 841.89 pt |
| fonts | 3 Type0 `/Identity-H`: JSXNFF+Liberation Serif Regular, XIEYTO+...Bold, YOHEIF+...Italic |
| `Tc` (char spacing) | **0 operators** in the whole 26 936-byte stream |
| `Tz` (horizontal scale) | **0 operators** |
| `Tw` (word spacing) | 3, on the justified body paragraph only |
| `TJ` arrays | 293 `TJ`, 0 `Tj`; every array holds exactly one glyph; **0 carry a kerning number** |
| small caps | **synthesised**: `N` at 8.00 pt, `O` at 6.24 pt (0.78x), same baseline y = 757.89 |

So the letter spacing is not `Tc`, not `Tz` and not a kerning number. It is baked into the `TD`
x-coordinates of single-glyph `TJ` arrays, with a real space glyph (code `<0003>`, U+0020 through
`/ToUnicode`) drawn between letters.

## Where the boundary is destroyed, with numbers

The failing line, baseline y = 757.89:

    x=340.233  size=8.00  '5'  advance 4.000  drawn gap +1.200
    x=345.433  size=8.00  '7'  advance 4.000  drawn gap +1.200
    x=350.633  size=8.00  '0'  advance 4.000  drawn gap +1.200
    x=355.833  size=8.00  <0003>  SPACE GLYPH - the page's only separator here
    x=359.033  size=8.00  '0'  advance 4.000  drawn gap +1.200
    x=364.233  size=8.00  '0'  advance 4.000  drawn gap +1.200
    x=369.433  size=8.00  '5'  advance 4.000  drawn gap +1.200

Page-wide: 191 space glyphs drawn, 296 spaces in the reference, 593 spaces in the .txt.

The two sides apply different thresholds to the same 1.200 pt gap at 8.00 pt:

* **Writer** - `PdfToWord.textOf()`, `gap > gs * 0.18f` (line ~4308). 0.18 x 8.00 = **1.440 pt >
  1.200 pt, so no space is inserted**. The writer emits only the drawn space glyph and writes
  `570 005`, which is what the page draws (a Mysuru PIN in its grouped form).
* **Reference** - `page.get_text()` splits at the finer 1.200 pt gap and returns `57 0 0 05`.

Side by side, line 3 of the page:

| | |
|---|---|
| page draws | `ESTABLISHED 1886  .  NO. 4, KRISHNARAJA BOULEVARD, MYSURU 570 005` |
| writer's .txt | `... M Y S U R U 570 005` |
| reference | `... M Y S U R U 57 0 0 05` |

The same mechanism explains the address punctuation: source `N O . 4,` / `D ,` against .txt
`N O. 4,` / `D,`.

## The measurement that says do not "fix" this in the writer

A candidate writer patch was built outside the repo tree (repo untouched) that suppresses the gap
rule when the page draws its own space glyphs. It produces plainly the better text file:

    THE MYSORE CHAMBER OF COMMERCE AND INDUSTRY
    ESTABLISHED 1886  .  NO. 4, KRISHNARAJA BOULEVARD, MYSURU 570 005
    NOTICE TO MEMBERS
    ELECTION OF THE MANAGING COMMITTEE
    HEADINGS ON THIS PAGE ARE SET IN SMALL CAPITALS WITH LETTER SPACING

and `verify_txt.py` scores it:

| | t01_word_accuracy | t12_word_invention |
|---|---:|---:|
| unpatched .txt | 97.4 | 2 |
| patched .txt | **58.5** | **22** |

The correct .txt scores 38.9 points lower on `t01` and 20 words higher on `t12` than the wrong one.
The reference reads the small-caps lines letter by letter (`T H E M Y S O R E ...`), so a .txt that
carries real words is charged for every single-letter "source word" it does not reproduce.

**Conclusion: no engine change should be made for `t01` or `t12` on this document.** The writer's
`570 005` is what the page draws; the reference's `57 0 0 05` is not. The honest repair is on the
source side of `verify_txt.py` - a tokenisation that does not split a letter-spaced run at 1.200 pt,
or one that reads the page's drawn space glyphs as the primary boundary and falls back to gaps.

## Not done, and not established

* `verify_txt.py` was **not** edited. The verifier is the instrument and a check is not moved by
  changing the check. This is recorded so the next run does not spend a slot on it.
* A pure "drawn space glyph = word break" reference is **not** a correct repair either: the page
  draws a space glyph between *every* letter of the letter-spaced headings, so that rule welds the
  address correctly and shatters nothing useful (scores 90.0 / 121 on this document). The genuine
  ambiguity is that on a letter-spaced line the drawn space glyphs cannot distinguish a word gap
  from a tracking gap.
* Whether PyMuPDF's split threshold is configurable is not established; its behaviour was measured,
  not its source.
* Whether the same 1.2 pt-at-8 pt collision affects any other document in the corpus was not
  measured corpus-wide.

## Code locations

    writer side     app/src/main/java/com/kavopdf/app/engine/PdfToWord.java  textOf()  ~4308
                    (the gap > gs * 0.18f word-break test; sibling cell rule ~8331)
    reference side  tools/p2w-bench/txt/verify_txt.py  _words() 276, _src_text() 679,
                    t12 comparison ~1266
