# The pBdr rule fix: built, measured, reverted — it works and it is not enough

Follows `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`, which established that a horizontal rule is
emitted as a floating `<w:drawing>` and that Google drops it, leaving a `U+200B` anchor behind.

## The change

`ruleAsBorder()` in `DocxWriter.shape()`, nine lines: when `isHairline(s)` and the shape is wider than
it is tall, emit a one-twip paragraph carrying

    <w:pBdr><w:bottom w:val="single" w:sz="<width*8>" w:space="0" w:color="<rgb>"/></w:pBdr>
    <w:ind w:left="<x*20>" w:right="<(pageWidth - x - w)*20>" w:firstLine="0"/>
    <w:spacing w:before="0" w:after="0" w:line="1" w:lineRule="exact"/>

with a single space in the run, because a paragraph with no run is dropped by some readers along with
its border, and a space is whitespace so it does not count against `05_chars_extra`.

`w:pBdr` was verified against Google before the change was written: a minimal .docx with one bottom
border renders the rule in both LibreOffice and Google.

## Measured through Google on 18_centred_heading_left_body_txtpos

| | rules drawn | rules lost | U+200B | verdict |
|---|---:|---:|---:|---|
| before (drawing) | 0 | 2 of 2 | 1 | 40/42, 05 and 32 both FAIL |
| after (pBdr) | **2** | 1 of 2 | 1 | 40/42, 05 and 32 both FAIL |

The construct is right: both converted rules are drawn by Google, where before neither was.

## Why it is not enough, and what is left

One rule is still lost and a `U+200B` survives at x=291 y=797 - near the foot of the page. The two
rules this change converted are not the source of it. There is a third construct down there emitting
the same anchor, and it has to be found before the class closes.

## Why it is not committed

The gate wants the whole corpus measured with the engine as it stands, and that is 213 renders, which
did not fit in the turn. Reverted rather than shipped unmeasured. Nine lines; rebuild in a minute from
the description above.

## Order of work

1. Find the construct at y=797 that still emits a U+200B and loses a rule.
2. Land `ruleAsBorder` once (1) is understood, with the full-corpus gate, so the class closes in one
   commit rather than half of it.
