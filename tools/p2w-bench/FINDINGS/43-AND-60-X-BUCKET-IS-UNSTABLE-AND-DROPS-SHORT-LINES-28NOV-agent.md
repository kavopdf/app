# The x-position check buckets by round(midpoint) and drops every line under 10 pt

**Located from the 28 Nov 09:55 fixer report, which measured the overcharge but did not name the line:**
"the instrument over-charges through a hard 10 pt left-edge bucket - purchase-order charged +103.36 pt where the
page's widest line moved +2.79 pt."

## Where it is

`tools/p2w-bench/verify_google.py`, in the line collector that feeds `43_within_10pt_x` and `60_text_column_right_edge`:

    lx0 = min(_p0[0], _p1[0]) + _cx
    lx1 = max(_p0[0], _p1[0]) + _cx
    if lx1 - lx0 < 10:
        continue

**Every line narrower than 10 pt is dropped before any comparison.** A single word, a number in a column, a short
label, a date - none of them are seen by this check at all.

And twenty lines above it, the code's own comment names the second half of the problem:

    # this check buckets a line by round(midpoint) and takes the MODE, and a
    # constant shift moves every midpoint across a rounding boundary, so the
    # mode - and therefore the bucket of 7 lines - changed on a document that had
    # not moved (newsletter-3col-header-footer read 0 -> 6 contradicted pairs).

## The two defects, stated plainly

1. **A hard 10 pt width floor makes short lines invisible.** A document whose columns are made of short cells -
   an invoice's amounts, a form's values - is judged on the long lines only, and the check reports a number that
   does not describe the page.
2. **`round(midpoint)` is a 1 pt bucket, and the check takes the MODE of those buckets.** A line whose midpoint
   sits at 100.4 rounds to 100; the same line moved 0.2 pt to 100.6 rounds to 101. **A shift far below any
   tolerance can move a line into a different bucket and flip which bucket is the mode**, so the check can report
   a large movement on a document that barely moved - which is the +103.36 against a real +2.79.

**The comment at 3709 already records this happening on `newsletter-3col-header-footer`, where the check read 0
against 6 contradicted pairs on a document that had not moved. That was written up as a reason to keep the centre
subtraction, not as a reason to stop bucketing by a rounded midpoint.**

## Why this was NOT changed, and what must happen first

**This collector feeds the x-position judgement for every document in the corpus.** A change here re-scores
everything, and a wrong change corrupts the number the whole pipeline steers by.

**The +103.36 was not reproduced.** What is established is the location and the mechanism, not the arithmetic.
**Today's lesson, learned four times: a change made without reproducing the number it claims to fix is a guess.**

**Before touching it:**

- **Reproduce the purchase-order reading.** Run the check on `purchase-order` with the source PDF and the current
  render, print `lx0`, `lx1` and `round(midpoint)` for every line on the page, and show which bucket the mode
  landed on in each. **The claim to test is that the mode bucket moved while the lines did not.**
- **Then measure what the fix does to the corpus.** Changing the bucket width or dropping the mode changes
  `43` and `60` on all 213 documents, so it needs a full re-measure before and after, and `regress.py --check`
  must pass.
- **A stable replacement, if one is wanted:** compare the same line's position across source and render instead of
  bucketing by a rounded midpoint and taking a mode. The pair already exists in `pairs`; the bucket throws that
  pairing away. **That is a design change and it is not a one-line edit.**

## The size of what this is hiding

`60_text_column_right_edge` is charged on 59 documents in Google against 18 in LibreOffice - **a 41-document gap
between two renderers on the same check**, which is the signature of an instrument problem rather than an engine
one. And `43_within_10pt_x` is charged on 13 with 7 documents.

**If the bucket is unstable, part of that 59 is the instrument, not the documents.** That is why this is worth a
slot to settle rather than a patch to guess at.
