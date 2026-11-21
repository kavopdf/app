# The U+FFFD patch is rejected: the four Effra CIDs are ff / fi / ffi / ffl, and `chr(CID)` writes the wrong letters

**21 Nov, relay/fixer run 13:18-13:40.** Class taken: `t01_word_accuracy`. Two agents deployed in
the first ten minutes, both answered, and their files are in this directory:

    t01_word_accuracy-FFFD-FONT-TRUTH-075328-b3e7.md    the font program, read
    t01_word_accuracy-FFFD-VISUAL-READ-132642-0f4c.md   the rendered page, read with an eye
    crops/*.png                                          the eight crops the second agent read

This file is the verdict on the open question that `FFFD-CMAP-2300-fixer.md` left standing at
23:25, and the reason `fffd-cmap-destination-2300-fixer.patch` must not be applied.

## Asked

`FFFD-CMAP-2300-fixer.md` ended with an unanswered objection from a review agent: the patch
resolves an unnameable CID by `sb.append((char) code)`, so CID 0x0123 becomes `ģ`. If the page
draws a ligature there, the patch writes 127 wrong letters into a bank form. The finding named
the test that settles it — render page 1 at 150 DPI, crop the sites, and read the letters. It
was never done. It is done here.

## Claim, and the verdict

**Claim: `chr(0x0123)` = `ģ` is the wrong character. The four CIDs draw the ligatures
ff / fi / ffi / ffl, so the patch writes wrong text that looks like text.**

**Verdict: the claim is CORRECT and the patch is WRONG.** Three independent lines of evidence,
none of which trusts the other two:

### 1. The font program has no glyph that could be `ģ`

`REAQAG+Effra-Regular` is Type0 / Identity-H / CIDFontType2, `/CIDToGIDMap /Identity`, so CID ==
GID. Its FontFile2 sfnt directory is `OS/2, cvt , fpgm, glyf, head, hhea, hmtx, loca, maxp, name,
prep` — **no `cmap`, no `post`**, so there is no Unicode→glyph mapping and no glyph name to read.
What the program does say:

* all four glyphs have **yMin = 0**; `g` has yMin = −212 and no glyph in all 1225 descends below
  −250, so a cedilla **cannot exist** in this program;
* the tallest glyph in the font is `.notdef` at yMax = 750; all four are yMax = 684 (the `f`
  ascender), so a circumflex at ~847 **cannot exist** either;
* advances: 637 vs f+f = 660, 539 vs f+i = 552, 847 vs f+f+i = 882, 858 vs f+f+l = 872.

### 2. The outlines match the ligatures, best-candidate

Component unions fitted exhaustively: CID 0x0123 → **ff 0.9707** (fi 0.7112); 0x0124 → **fi
0.8873** (ff 0.7486); 0x0126 → **ffi 0.9200** (ffl 0.8829); 0x0127 → **ffl 0.9366** (ffi 0.9214).
The i-dot separates ffi from ffl structurally: 0x0126 has a detached dot, 0x0127 is continuous
ink 0→684.

This is weaker evidence than it looks and must not be shipped as a rule — `ligature-identity-
UNRECOVERABLE-2350.md` already measured ffi/ffl and fi/fl as ambiguous at this tolerance, and
that conclusion stands. It is used here only as corroboration.

### 3. The rendered page, read with an eye — decisive

Pages 1 and 2 of `041122-Account_Opening_Form` rendered at 300 DPI, cropped at eight
well-separated sites, upscaled 3x, and read (crops in `crops/`):

| CID | extractor says | the page visibly draws |
|:--|:--|:--|
| U+0123 | `Staģ`, `Diģerently abled`, `Oģ` | **Staff**, **Differently abled**, (**Off**) |
| U+0124 | `Ĥll up`, `QualiĤcation`, `veriĤed`, `Ĥnancial` | **fill**, **Qualification**, **verification**, **Financial** |
| U+0126 | `aĦx`, `Registered OĦce`, `OĦcial Name` | **affix**, Registered **Office**, **Official** Name |
| U+0127 | `Oħine` | **Offline** |

Every one of the 38 sites on pages 1-2 yields a real English word as a ligature and nonsense as
an accented letter. I re-read two of the crops myself; `gistered Office` and `ii. Differently ab`
are unmistakable.

## The number, measured on this tree

`pymupdf` over the nine pages of `041122-Account_Opening_Form`, counting the four code points
directly (not the patch, not verify_txt):

    ģ U+0123   13 sites   must be ff    26 letters
    Ĥ U+0124   89 sites   must be fi   178 letters
    Ħ U+0126   23 sites   must be ffi   69 letters
    ħ U+0127    2 sites   must be ffl    6 letters
    ---------------------------------------------------
    127 wrong characters standing where 279 correct letters belong

Fonts: Effra-Regular 121, Effra-Medium 4, Effra-Bold 2. U+FFFD in `get_text()`: **0** — the
extractor's last-resort decode prints the code number as a character, which is the other half of
the defect.

## Why the patch's own measurement passed anyway

`FFFD-CMAP-2300-fixer.md` measured t01 7-of-10 → 3-of-10 failing and called it proof. It is not.
t01 compares our `.txt` against the **source extraction**, and the source extraction is pymupdf,
which resolves an Identity font the same way the patch does. Two extractors making the same wrong
assumption agree with each other whether or not the assumption is true. **The check moved; the
question did not** — the review agent's objection, now confirmed by the page itself.

## Ruled out

* a missing /ToUnicode — every Effra face carries one, 91 well-formed bfchar entries;
* a malformed CMap — the FFFD is the CMap's own **destination** value, deliberately;
* the CID being the character — the font program cannot draw `ģ` or `Ĥ` at all (yMin/yMax);
* the width rule as a shippable fix — fi 552 vs fl 542 is 1.8 % of an em, ambiguous, per
  `ligature-identity-UNRECOVERABLE-2350.md`, which this file does not overturn.

## Status: rejected. The patch stays out of the tree.

`fffd-cmap-destination-2300-fixer.patch` is renamed `...-REJECTED.patch` and carries a banner. It
must not be applied. What the next run needs is a **measured table** — (BaseFont, CID) → replacement
string, derived from a rendered-page read as above, not from widths or outlines — and it needs
`verify_txt.glyph_truth` to apply the same table, because the reference is wrong in the same way.
That is a two-sided change and the instrument half is the wall recorded in `BLOCKERS.md` at
01:43. It is not this slot's to decide.

## What this run did NOT establish

The live `RANKING-TXT.csv` names **six** documents failing t01 — 391, 39, 411, 601, 77, 79 — and
the two bank forms are not among them: t01, t03 and t07 already closed on both at 22:54 via
`glyph_truth` emitting U+FFFD, and t06 is the only check still open on them. So the FFFD defect
costs t01 **nothing today**; this work removes a trap, it does not move a document. 391 and 79
appearing back on the list is a live-table-versus-finding discrepancy this run could not measure
(the corpus conversion needs `/scratch/work/p2w/out`, which no tool on this slot could build in
time). **The next run measures those two first.**
