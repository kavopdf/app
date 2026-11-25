# 25_invisible_text is not dead - it is correctly failing on five documents

The 04:23 run concluded the opposite, in these words:

    "25_invisible_text cannot fail. 0 of 392 real Google exports can trip it after the 24 Nov sheet
     filter; eway-bill and mutual-fund-statement render white-on-white in Google and are recorded PASS."

And it planned the next run around that conclusion: "ship the 25_invisible_text patch - its 43 recorded
failures are a number nobody can currently move."

The store says otherwise. On engine 981ff1fa35e2cf67, five documents FAIL the check, and the check
records both counts, so the failure can be read rather than guessed:

    document                        source   render   verdict
    eway-bill                            0        3   FAIL
    mutual-fund-statement                0        4   FAIL
    bank-statement-5-pages               0        8   FAIL
    gst-invoice-multipage-item-table      0        ?   FAIL
    text-held-twice-shadow-text          8       12   FAIL

`source=0, render=3` is not a document that was already invisible. It is a document with no invisible
run in the original and three in Google's render - Google hid three runs the source showed. That is the
defect the check exists to find, found.

## Why the two claims could both be written in good faith

verify_google.py stores this check as a 3-tuple, `(s_invisible, invisible, invisible <= s_invisible)`,
so the verdict carries `source` and `render` rather than a prose detail. A reader who looks for a
`detail` field finds nothing and can reasonably conclude the check abstained or passed. It did neither:
`ok=False` with `source=0, render=3` is a complete answer sitting in two fields nobody opened.

That is the same shape as every other defect in this directory - the evidence exists and the reading
does not reach it.

## What this changes for the next run

The 43 recorded failures are not a number nobody can move. At least five of them are Google rendering
text invisible that the source showed, which is an engine-side defect with a location, not an instrument
problem. Shipping a patch to a check believed to be dead would have removed the evidence for that.

## Verified, not changed

No instrument was edited. verify_google.py computes and stores this correctly; the correction is to the
reading of it. The five documents and their counts are in benchmarks/gverify/ and can be re-read at any
time with the two field names above.
