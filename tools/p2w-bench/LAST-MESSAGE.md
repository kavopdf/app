# Fixer report - 2026-11-20 23:19

**20 Nov 2026 · slot 22:54 → running IST · 27 min**

> Two documents moved, and the thing that had eaten three runs is now closed on both sides: the
> glyphs are ligatures, and their identity is not in the file. What this run bought is the four
> checks that were all counting one fault, and a wall with a proof behind it.

## Progress

| | |
|:--|:--|
| Documents improved this run | **2** — 1 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **19** files in 1 commit(s) from `0580c1b` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:16 | **kept** | 2/7 | A code the font itself answers U+FFFD for was being counted as four separate faults against the writer |

## The finding: the ligature is real, and its identity is not in the file

Both bank forms carry 127 U+FFFD. Two agents on the 22:39 run disagreed about what those glyphs
are, and one of them was wrong. Read out of the embedded FontFile2 programs, the four CIDs are
ff, fi, ffi and ffl: advances 637, 539, 847, 858 against component letters f 330, i 222, l 212,
every one a single glyph cell 94.8–98.4 % of the sum of its letters, and every one inside a word
that only closes with a ligature - `identi□cation` 85 times, `O□ce`, `Sta□`, `O□ine`,
`a□x rubber stamp`. A template match over 88 croppable sites picked the own-CID glyph 88 of 88.

So the 22:39 patch that recovered the code as a character was writing `Oģce` for `Office`, and
it was right to be reverted. The replacement idea - fall back to the embedded font's own cmap -
is dead too: not one of the embedded font programs across the corpus carries a cmap table at all.

And the identity cannot be recovered by any other route, which is the part worth keeping:

| route | result |
|:--|:--|
| /W widths alone | fi 552 vs fl 542, ffi 882 vs ffl 872 - both inside the 1.6–5.2 % compression band |
| the glyf outlines, matched against component composites | fi 0.719 vs fl 0.695; ffi 0.674 vs ffl 0.660; ffl's own CID 0x127 scores 0.378–0.448 against everything |
| glyph names, post, GSUB, CFF charset | all stripped or absent |

ffi and ffl are distinguishable from each other by nothing in these files. Any engine rule here
guesses, and a guess produces English-shaped text no downstream check can catch. That is written
up in FINDINGS/ligature-identity-UNRECOVERABLE-2350.md and recorded as a blocker, so the next run
does not spend an hour rebuilding a matcher.

## What was landed instead

The two bank forms were failing **four checks on one fault**. The source side is pymupdf, and its
last-resort decode prints the code number as a character, so Effra's CIDs arrive in the source
text as U+0123, U+0124, U+0126, U+0127. t01\_word\_accuracy, t03\_symbols, t07\_symbol\_counts and
t12\_word\_invention each condemned the writer for not carrying a letter the page never drew.

`glyph_truth` now emits U+FFFD for a code the font's own /ToUnicode answers FFFD for - the same
character the writer emits for the same glyph. The substitution is length-preserving, so every
newline and space the declaration put down stays where it was, and it fires only when the page's
glyph walk drew exactly as many glyphs of that id as the page text holds that character.

Measured with ConvertOne and verify\_txt.py on an unchanged engine:

| Document | Before | After |
|:--|:--|:--|
| 041122-Account\_Opening\_Form | 3 of 12 passed | 6 of 12 passed |
| Account\_Opening\_Form\_Fillable\_filled | 3 of 12 passed | 6 of 12 passed |

t01, t03 and t07 close on both. **t06\_encoding still fails on both** - the 127 U+FFFD are still in
the .txt and still have an owner - so this is not a claim that the conversion is fixed. The corpus
ratchet over 213 documents says 2 newly clean, 0 newly failing, 211 unchanged, and a scan of every
font on every page of all 213 finds only these two documents with a font that answers U+FFFD, so
the new path cannot fire anywhere else.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t01_A-01` | is the U+FFFD glyph a ligature or a single letter, read from the outlines and the rendered page | 23:20 | 23:20 | 0 min |
| `t01_B-01` | how many of the 213 a cmap-based recovery would reach, and does any program carry a cmap | 23:20 | 23:20 | 0 min |

They ran inline and returned in the same turn, so their records were written when they landed
rather than when they started - the Deployed column is the ledger's clock, not theirs.

The first answered the question that decided the run: ligature, with the outlines and a contact
sheet. The second killed the fallback that looked most likely to work: no cmap table in any embedded font program, so the recovery cannot be built at all on this corpus. It also corrected the
first on reach - it found 5 documents with FFFD destinations, and my own scan with the parser
that actually ships finds 2, which is the number the guard fires on.

## Timing

| | |
|:--|:--|
| Slot window | 22:54 → running · 27 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 18 |
| Longest silence | **11.3 min** — from 22:54:44, after `attempt.py: recording an attempt` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | the ligature identity at Effra CIDs 0x123/0x124/0x126/0x127 is not in the file: no cmap table in any embedded  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **10 min** | `########` |
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `#########` |
| record - attempt, handoff, class rows | **4 min** | `###` |
| report - the report and the chain | **1 min** | `#` |

## Next run

t01\_word\_accuracy now holds 5 documents, and two of those five is the bar. The two bank forms
have left the class; what is left on them is t06\_encoding, t08\_line\_order and t09\_page\_furniture,
which is the writer and not the font.

Of the five, 38\_faux\_bold\_italic\_synthesised loses the SECOND draw of its title - the source
carries `PROJECT REPORT - CIVIL` twice because faux bold strokes the fill, and our .txt carries it
once, which is correct. That is a source-side duplicate and the 21:46 attempt at collapsing
identical spans was rejected, so it needs a different construct. 411\_nested\_xobject\_transforms
loses `S` and `O` because pymupdf and PDFBox disagree about a nested form's matrix and the rotated
line runs off the page. 601\_fillable\_admission\_form loses two ZapfDingbats checkmarks that
PDFBox never delivers - they are drawn in a widget appearance stream - and the source calls a tick
`3`, so both sides need the same fix or neither is honest.
