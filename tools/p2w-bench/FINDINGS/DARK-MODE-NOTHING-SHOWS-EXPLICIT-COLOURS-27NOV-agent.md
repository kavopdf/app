# Nothing shows in Google Docs dark mode, and the cause is that not one colour is automatic

The user reported that our `.docx` is invisible in Google Docs dark mode while iLovePDF's, converted from the same
content, shows normally. **It is not a black-on-black accident and it is not the images** - the user was clear that
text, lines and many other things all disappear.

## Measured on the 10-page tool output

    runs                    1,622
    explicit w:color        1,045   -> 64 percent
    w:color="auto"              0   -> not one
    no w:color at all         577

    #1A1A1A  x565   luminance  26.0   near black
    #12314F  x125   luminance  43.2   dark navy
    #A3232E  x 67   luminance  74.5   dark red
    #3A4653  x 39   luminance  67.9
    #26303C  x 26   luminance  46.4

    border colours: #000000 x55, luminance 0.0

## The mechanism

**Google Docs dark mode inverts *automatic* colours. An explicit colour is treated as a choice the author made,
and it is left alone.**

**This document has no automatic colour anywhere.** Every run that carries a colour carries a dark one, because
that is what the PDF had. So dark mode leaves all 1,045 of them dark, on a background it has just turned dark, and
the text is not dimmed - it is gone.

**The borders are `#000000`.** Same mechanism, same result, and that is the "lines" half of what the user saw.

**iLovePDF's output shows because its text carries automatic colour, which dark mode inverts to light.** Same
content, same viewer, opposite result, and the difference is one attribute.

## Why this is a real defect and not a viewer quirk

A document that renders in light mode and vanishes in dark mode is broken for every user who has dark mode on,
which is a large and growing share. **The content is there, the text layer is intact, every text-based check
passes - and the reader sees an empty page.** That is the same failure shape as the invisible banner text found
earlier in this work: present, correct, unreadable.

## The fix, and it is not "make everything auto"

**Removing the colour would be wrong** - a coloured heading, a red total, a grey rule are part of the document and
losing them is a fidelity failure. The two requirements are in tension and must be resolved deliberately:

- **Near-black text that carries no meaning should be automatic**, so dark mode inverts it. `#1A1A1A` at luminance
  26 is doing no work that "black" would not do.
- **Colour that carries meaning** - the red of a total, the navy of a heading - **should keep its value** and accept
  that dark mode will not invert it, because inverting it would change the document.
- **Rules and borders** at `#000000` are the strongest case for automatic: a rule is a rule, and its colour carries
  nothing.

**No threshold has been measured and none should be guessed.** What is established is the cause; the boundary
between "meaningful colour" and "incidental near-black" is a product decision that needs the corpus to settle.

## Not measured

**I cannot test Google Docs dark mode** - there is no UI in this environment, and a LibreOffice render would not
answer the question, as this work has already learned once today at the cost of a wrong finding.

**What is measured is the attribute inventory above.** The mechanism is a well-known behaviour of the viewer, and
the inventory shows this document is maximally exposed to it: zero automatic colours across 1,622 runs.
