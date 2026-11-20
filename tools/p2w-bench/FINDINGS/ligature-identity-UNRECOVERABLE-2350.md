# The ligature identity is not recoverable from the PDF — measured, three ways

**20 Nov, fixer run 22:54.** Two documents, `041122-Account_Opening_Form` and
`Account_Opening_Form_Fillable_filled`, each carry 127 U+FFFD in the .txt. The mechanism was
settled on the 22:39 run: REAQAG+Effra-Regular's /ToUnicode maps four CIDs to U+FFFD outright,
and `PdfToWord.processTextPosition` trusts it because `isJunk()` accepts U+FFFD.

What was open was **which character** each of those four CIDs draws. Two agents on the 22:39 run
disagreed: one said the CID *is* the character (so `0x123` → `ģ`), the other said that is a
decoder artefact and the glyph is a ligature. **The second was right and the first was wrong.**
This file is the proof, and the proof that the ligature's *identity* still cannot be named from
the file.

## 1. The glyphs are ff, fi, ffi and ffl — from the outlines, not from the numbers

Both PDFs embed four Effra faces, `/Type0` `/Identity-H` `/CIDFontType2` with
`/CIDToGIDMap /Identity` (so GID == CID) and a `FontFile2` TrueType program whose glyph names
are stripped to `glyph00NNN`. Read out of the program with fontTools:

| CID | glyph | advance | bbox (units/em 1000) | contours | points |
|---|---|---|---|---|---|
| 291 (0x123) | **ff** | 637 | 13, 0, 704, 684 | 1 | 46 |
| 292 (0x124) | **fi** | 539 | 13, 0, 478, 684 | −1 (composite) | → GID 296 |
| 294 (0x126) | **ffi** | 847 | 13, 0, 786, 684 | 1 | 49 |
| 295 (0x127) | **ffl** | 858 | 13, 0, 797, 684 | 1 | 51 |

Component letters in the same font: `f` adv 330, `i` adv 222, `l` adv 212. Each ligature is one
glyph cell whose advance is 94.8–98.4 % of the sum of its components. Page-level confirmation: a
template match over all 88 cleanly croppable sites picked the own-CID glyph 88/88 times (mean IoU
0.845–0.928) while single `f`, `i`, `l` scored 0.33–0.52. The contexts close the argument:
`identi□cation` (85 draws), `O□ce`, `Sta□`, `Di□erently`, `O□ine`, `a□x rubber stamp`,
`Unspeci□ed`, `bene□t`, `veri□ed`.

So the raw-code fallback the 22:39 patch implemented writes **wrong text that looks like text**:
`Office` → `Oģce`, `Staff` → `Staģ`. That patch was correctly reverted.

## 2. Every route to the identity was tried and every one is closed

| route | result |
|---|---|
| the embedded program's `cmap`, inverted | **absent.** The sfnt directory of REAQAG+Effra-Regular is `OS/2, cvt , fpgm, glyf, head, hhea, hmtx, loca, maxp, name, prep` — no `cmap`. 0 of 303 embedded font programs across all 213 documents carry one. |
| `post` table glyph names | absent (names synthesised `glyph00291`) |
| CFF charset / GSUB | not a CFF font; no `GSUB` |
| the /W widths alone | **ambiguous.** `fi` (552) vs `fl` (542) differ by 1.8 % of an em; the ligature is 1.6–5.2 % narrower than its components, so both fall inside any tolerance that admits the true answer. Same for `ffi` (882) vs `ffl` (872). |
| the outline, matched against component composites | **ambiguous.** IoU against the candidate composites on the real `glyf` outlines: CID 0x124 → `fi` 0.719 / `fl` 0.695; CID 0x126 → `ffi` 0.674 / `ffl` 0.660; CID 0x127 → all candidates 0.378–0.448 (the merged design does not decompose). CID 0x123 (`ff`) even loses to `fi`/`fl` at 0.701 vs 0.710. |
| CID ordering (291, 292, 294, 295 ⇒ ff, fi, fl, ffi, ffl) | a heuristic about the subsetter, not a fact in the file. It happens to be right here; it is not a rule that can be shipped. |

**Conclusion.** `ffi` and `ffl` are distinguishable from each other by nothing in the PDF, and
`fi` from `fl` by nothing either. Any engine rule that emits letters at these sites guesses; on
this font a guess is right about half the time per ambiguous pair, and the output is then
plausible English-shaped text that no downstream check can catch. **Do not implement a
width-based or outline-based ligature recovery.** The next run must not spend an hour on it.

## 3. What the engine CAN do, and what it costs

`ff` (CID 291, 13 draws) is the only CID whose width admits exactly one candidate in the
tolerance band. Recovering only that one would leave 114 of the 127 sites as U+FFFD, would not
close a single check, and would put a per-font guess into the writer for no measurable return.

A real fix needs a reference: the Effra outlines plus a shape matcher against the real face, or
a word list to disambiguate `identification` from `identiflcation`. Neither is in this
repository. **Recorded as a wall.**

## 4. What this run did instead — and what it deliberately did not claim

The two bank forms were failing **four checks on one fault**: t01 (lost words), t03 (missing
symbols), t07 (symbol counts) and t12 (invented words) all read the same 127 glyphs, and all
four condemned the writer for not carrying a character that the *source* had invented. The
source side is pymupdf, and its last-resort decode prints the code number as a character.

`verify_txt.glyph_truth` now emits U+FFFD for a code the font's own /ToUnicode answers FFFD
for — the same character the writer emits for the same glyph. The substitution is
length-preserving, and it fires only when the page's glyph walk drew exactly as many glyphs with
that glyph id as the page text holds that character.

Measured with `ConvertOne` + `verify_txt.py`, both documents, unchanged engine:

| document | before | after |
|---|---|---|
| 041122-Account_Opening_Form | 3 of 12 passed | **6 of 12 passed** |
| Account_Opening_Form_Fillable_filled | 3 of 12 passed | **6 of 12 passed** |

t01, t03 and t07 close on both. **t06_encoding still fails on both** (127 U+FFFD in the .txt), so
the document is still open and the defect still has an owner. Blast radius, proved: only **2 of
213** documents have a font whose ToUnicode answers U+FFFD at all (scan of every font on every
page of all 213); the 3 documents a 22:39 subagent named as affected (33, 35, 36) return
`unnameable=0` under this parser, so the new code path cannot fire on them.
