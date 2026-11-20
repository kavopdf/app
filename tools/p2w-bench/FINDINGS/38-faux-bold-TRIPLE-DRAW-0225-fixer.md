# 38_faux_bold_italic_synthesised: the page draws its two headings three times, and the reference counts them twice

21 Nov 2026, fixer run claimed 00:57, third attempt. Measured with pymupdf 2.1 over the corpus
rebuilt from the corpus-v1 release (213 PDFs). No engine change.

This document is charged 2 of 9 checks, `t01_word_accuracy` and `t07_symbol_counts`. The carried
note from 20 Nov said the source carries `PROJECT REPORT - CIVIL` twice and our .txt carries it
once "which is correct". That is close, and the real shape is worse than the note.

## What the page actually draws

`get_texttrace()` on page 1, spans at the same baseline:

| render mode | x | y | size | text |
|---:|---:|---:|---:|---|
| 0 (fill) | 56.0 | 99.54 | 13.0 | `PROJECT REPORT - CIVIL` |
| 0 (fill) | 56.0 | 99.54 | 13.0 | `PROJECT REPORT - CIVIL` |
| 1 (stroke) | 56.0 | 99.54 | 13.0 | `PROJECT REPORT - CIVIL` |
| 0 (fill) | 56.0 | 119.15 | 11.0 | `Study of self-compacting concrete using ...` |
| 0 (fill) | 56.0 | 119.15 | 11.0 | `Study of self-compacting concrete using ...` |
| 1 (stroke) | 56.0 | 119.15 | 11.0 | `Study of self-compacting concrete using ...` |

Three draws of each line at the identical position, same font, same size: two fills and one
stroke. That is the faux-bold idiom - the page has no bold face, so it paints the line twice and
strokes it once to thicken it.

## What the reference counts

    page.get_text() words ......................... 201
    words with identical-position spans collapsed .. 186

So the reference reads the two fill copies and counts each of those two lines twice: 15 words that
the page means once. That is exactly the `t01` charge on a 99 % threshold - 186 of 201 is 92.5 % -
and it is the `t07_symbol_counts` charge too, because the em dash in `PROJECT REPORT - CIVIL` is
counted twice as well.

## The .txt is not the fault

A Word file that carries every faux-bold heading twice is a broken file. The writer emits each line
once, which is what the page means, and the reference charges it for the copies. This is the same
family as `411_nested_xobject_transforms` (a reference that invents tokens the page did not mean)
and the opposite of `39_small_caps_letter_spacing` (a reference that invents boundaries): in all
three the writer is right and the source side of the check is counting something a reader would
not.

The .txt side of this document was not re-measured this run - it needs the engine build and a
conversion, and the two agents used the slot's build time. What is measured here is the reference
side, which is the half that decides the check.

## Corpus-wide: the rule fires on this document and nowhere else

Every page of all 213 PDFs was walked for spans whose text and position are identical to another
span's (0.1 pt tolerance on both axes):

| | |
|---|---:|
| documents with identical-position duplicate spans | **1** of 213 |
| the document | `38_faux_bold_italic_synthesised` |
| duplicate span sites on it | 2 (one per faux-bold heading) |
| words the duplicates add to the source count | 28 raw, 15 as `get_text()` reads it |

So a "same place, same string" dedupe on the source side is a rule with a measured blast radius of
one document, which is the whole reason it is worth proposing.

## Proposal, not applied

`verify_txt.py` is the instrument and a fixer does not move a number by editing the check, so this
is written up rather than built. The shape: when two spans carry the same text at the same
position (0.1 pt), the source side should count it once - and the corpus measurement above says
nothing else in the 213 changes if it does. It belongs in the same decision as the clip-flag
proposal in `INSTRUMENT-PROPOSAL-clip-flag-NOT-APPLIED-0210-fixer.md`: one sanctioned correction to
the source side, one corpus-wide restamp, both documents cleared together.

With `411` (clip flag) and this one (dedupe), four of the five `t01` documents have a measured
cause and three of the four are the reference's.
