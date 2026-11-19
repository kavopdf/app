# 041122 — the worst document, and why its score cannot be trusted

`041122-Account_Opening_Form` sits at **share@5px 98.65** — the worst in the corpus, and one of the
two documents the fixer's prompt names as "the two that need the agent's owner". It is 9 pages, a
bank account-opening form, 7448 words.

**Its measurement truth is wrong.** That is the finding, and it comes before any fix.

## The ligature the truth gets wrong

The page draws "Please **fill** up in BLOCK letters only". Two readers disagree about it:

| reader | what it returns |
|:--|:--|
| PyMuPDF — the `glyph_truth` this pipeline scores against | `Ĥll` |
| the engine, into the `.docx` | `�ll` (U+FFFD) |
| the page itself | `fill` |

Thirteen occurrences. **Neither side reads `fi`.** So `t01_word_accuracy` compares `Ĥll` against `�ll`,
finds no match, and charges the document for a word neither reader got right — and no change to the
engine can make that comparison pass, because the string being compared is not the string on the page.

`Ĥ` is U+0124, LATIN CAPITAL LETTER H WITH CIRCUMFLEX — the codepoint a broken single-byte mapping
lands on when `fi` (U+FB01) is truncated to its low byte `0x24`-ish range. It is not a character the
page contains.

## What was tried, and why it did not work

`PdfToWord.processTextPosition` already has a fallback: when `isJunk(u)` is true it re-decodes through
the font with `decodeThroughFont()`. **`isJunk()` cannot see U+FFFD** — 0xFFFD is above every range
that function rejects, so the replacement character came back as a perfectly good character and the
fallback never ran.

Adding `hasReplacement()` to that test made the fallback run. **It changed nothing:**

    screen.py --docs 041122-Account_Opening_Form
    1 measured, 1 same, 0 better, 0 worse

`decodeThroughFont()` asks the font for a glyph name, and this font has none for that code. The
fallback returns null, the original U+FFFD is kept, and the output is byte-identical. **The change was
reverted** — an inert patch is a patch that costs a review and buys nothing.

## What would actually fix it

**A ligature table, applied where a decode fails and the advance width says the glyph is two
characters wide.** U+FB01 `ﬁ` → `fi`, U+FB02 `ﬂ` → `fl`, U+FB00 `ﬀ` → `ff`, U+FB03 `ﬃ` → `ffi`,
U+FB04 `ﬄ` → `ffl`. But this page's glyph does not decode to U+FB01 either — it decodes to nothing —
so the table has to be driven by the glyph's **width against the font's own `fi` advance**, not by a
codepoint.

**And the truth has to be fixed first**, or the fix cannot be scored: `glyph_truth` reads the same
broken mapping. Whatever repairs the engine must repair the reference too, or a correct `fi` will be
measured against a wrong `Ĥll` and score worse than the defect.

## The other half of the 98.65

The score is not only this. The census calls the document `lost-text 0.57 — 928 of 1255 lines out`,
and the text is not lost at all:

    docx paragraphs only     5043 words
    docx paragraphs + tables 7801 words
    the PDF                  7448 words

**Every word is present and it is inside tables.** The document is a form: labels and their boxes are
one grid, and the writer puts the grid in `w:tbl`. What the measurement sees as 928 misplaced lines is
a structure that differs from the page's own line order, not text that went missing.

`zeroGap=110, zeroGapWorst=34.3` on this document says the same thing from the other side: 110
paragraphs sit flush against the one above them.

**So 041122 is two problems, and neither is "the engine lost the text":** a ligature the reference
reader gets wrong, and a form grid whose row order does not match the page's drawing order.
