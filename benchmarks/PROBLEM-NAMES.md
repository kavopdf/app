# What each document's problem is called, and why

The ranking used to report a size. It now reports a name as well, and the name
is derived from the numbers -- not from anyone's judgement, and not from
opening a rendered image.

## The two axes that produce it

    share@5px    what fraction of source ink has no counterpart within 5 px
    invent5      what fraction of our ink has no counterpart in the source
    max_pt       the furthest displaced ink, in points

Loss and invention together say whether content MOVED or is MISSING:

    loss high, invention near zero   -> nothing was put in its place -> MISSING
    loss high, invention high        -> the content moved             -> MOVED
    loss high, invention partly high -> both

## The eight names

| name | condition | what it means for the user |
|---|---|---|
| `none` | share@5px < 1% | nothing wrong |
| `content-missing-nothing-in-its-place` | loss high, invention < 2% | content is GONE. The worst kind: nothing can be recovered by reformatting. |
| `content-missing-partly-replaced` | loss high, invention 2-70% | content gone, something else in its place |
| `content-partly-lost` | loss high, invention > 70% of loss | some content gone, the rest displaced |
| `content-partly-lost-and-displaced` | both, neither dominant | two defects on one page |
| `content-present-wholly-displaced` | loss ~= invention | everything is there, all of it moved |
| `content-present-partly-displaced` | loss ~= invention, partial | most is right, part moved |
| `single-element-far-out` | share@5px < 8% and max_pt > 30 | one small thing (a stamp, a seal) is far from where it belongs |
| `unmeasured` | the document failed to measure | fix the measurement before judging the document |

## What the current corpus says

    120  none
     30  content-missing-nothing-in-its-place
     15  content-present-wholly-displaced
     14  content-missing-partly-replaced
     12  content-present-partly-displaced
     11  content-partly-lost
      7  content-partly-lost-and-displaced
      1  single-element-far-out

## Worked examples, read straight off RANKING.csv

    415_inline_images        89.0%@5  inv  0.0%  max 153.1  text 100%
      -> content-missing-nothing-in-its-place
      Nothing was put where the four bars were. The image is absent, not moved.
      This is the only true deletion in the corpus.

    one-page-rotated-180     81.6%@5  inv 78.8%  max 177.6  text 100%
      -> content-missing-partly-replaced
      The source is an upside-down SCAN; our output is typeset text. The scan's
      ink was replaced by glyphs. Text recall is 100%, so nothing was lost --
      the ink changed medium. Do not read this as an ink defect.

    itr-computation          68.8%@5  inv 65.2%  max 133.9  text 100%
      -> content-partly-lost-and-displaced
      Content present, geometry systematically off. Table rules and column
      edges sit a few px out across the page.

    75_merged_header_cell    27.6%@5  inv 31.1%  max  21.6  text 100%
      -> content-present-wholly-displaced
      Loss and invention are equal: every mark is there, all of it moved.

    07_stamp_over_table       2.6%@5  inv  2.2%  max  66.2  text 100%
      -> single-element-far-out
      97% of the page is right. One stamp is 2.3 cm from where it belongs.

## What this does NOT tell you

It names the KIND of defect and sizes it. It does not say WHY the engine did
it -- "inline images are not extracted" came from looking at a rendered pair
(`p2w.py --diagnose`), not from these numbers. The name narrows the search;
the fixer still has to find the cause.
