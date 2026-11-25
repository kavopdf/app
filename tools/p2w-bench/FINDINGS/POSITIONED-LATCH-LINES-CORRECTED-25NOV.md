# The positioned latch: three reads confirmed, but the line range in the 02:20 report is wrong

The 02:20 relay report makes the most important correction anyone has made to the brief this week:

    "The brief calls the 120 pt gapCapTw threshold 'the largest engine defect anyone has found' at
    ~166 document-failures. Measured over all 213: the cap carries 1,469 characters; the page-local
    latch ctx.positioned (DocxWriter.java:3126-3144, read in exactly three places, all in para())
    carries 24,920 characters over 655 lines."

The structural claim is right and worth checking, so it was checked against HEAD.

## What is true

`ctx.positioned` is READ in exactly three places, and all three are in `para()`:

    3140    if (p.pinned && !anyRotated && !ctx.positioned)
    3150    if (ctx.positioned && !anyRotated)
    3168    if (ctx.positioned || containerOf(ctx.curShapes, b) != null)

Three reads, one method. Confirmed.

## What is wrong

The line range. The report says 3126-3144. That covers the first read and nothing else - 3150 and 3168
are outside it. Anyone told to look at 3126-3144 for "where the latch is read" will find one of the
three sites and conclude the other two do not exist, which is exactly the shape of mistake this file
exists to prevent.

The range is 3140-3168.

## What the report does not mention at all

There are six WRITE sites, and they matter more than the reads for the argument being made:

    3595    ctx.positioned = true
    3619    ctx.positioned = true
    3688    if (PAGE_POSITION_ON_ANCHOR) ctx.positioned = true
    4478    ctx.positioned = true
    4512    ctx.positioned = true
    4612    if (PAGE_POSITION_ON_ANCHOR) ctx.positioned = true

Two of the six are behind `PAGE_POSITION_ON_ANCHOR`, which is the flag the report's own probe disabled
with -Dp2w.pagepos=0. The other four are unconditional. So `-Dp2w.pagepos=0` turns the latch off on
some paths and leaves it on for the rest, which is worth knowing before anyone concludes from that probe
that the latch is neutral.

There are also four unconditional resets to false (1154, 1270, 2235, 2312).

## Not changed

The engine was not touched. This is a correction to a line reference, so the next run reads the right
code rather than a range that hides two thirds of it.
