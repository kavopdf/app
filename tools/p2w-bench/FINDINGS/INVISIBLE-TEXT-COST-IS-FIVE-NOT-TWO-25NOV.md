# The invisible-text fix landed and works; the cost it reports is 2 documents, the corpus says 5

The 04:56 run fixed the check that could not fail, and the diagnosis is exactly right:

    "It measured its background with get_drawings(), and on a Google export that returns exactly one
     fill per page - the page-sized sheet Google paints itself. `behind` was None on every run of every
     page, so the check returned 0 across 392 exports. It was not a strict check that happened to pass;
     it was a check that could not fail."

Verified in HEAD: the pixel-ring method is in (BG_RING_PT 0.5, the 12 px / 1.5 pt growth cap, the
abstain-unless-one-colour-covers-90% rule). The check now runs on all 213 and fails on 5.

## The correction

The report states the cost as two documents:

    "On 34 real exports: 35 of 37 unchanged, 2 fail - mutual-fund-statement (0->4) and eway-bill
     (0->3), both white-on-white table headers, both confirmed by eye."

That is a 34-export sample. Over the full corpus the check fails five:

    eway-bill                        source=0  render=3
    mutual-fund-statement            source=0  render=4
    bank-statement-5-pages           source=0  render=8
    gst-invoice-multipage-item-table source=0  render=?
    text-held-twice-shadow-text      source=8  render=12

So the honest cost is 5 documents leaving the clean count, not 2. The report's own framing - "those two
documents were counted clean before" - understates it by three, and those three are the same defect, not
a different one.

## Why this matters more than a count

The three the sample missed are the largest render counts in the set: 8 and 12. A sampling radius chosen
on two documents with 3 and 4 runs would not have been tested against a page carrying twelve, and the
report itself flags that risk for the cap knob ("21 of the 23 documents the cap changes have no position
measurement") without applying the same standard here.

## Verified, not changed

No instrument edited. The check is correct and now falsifiable, which is the whole gain. The next run
should re-read the five rather than the two, and confirm the ring radius holds at render=12 before the
result is treated as settled.
