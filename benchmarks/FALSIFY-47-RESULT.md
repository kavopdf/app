# The 47 docx checks: all of them can fail

`falsify.py` had been broken against the current verifier -- it called
`verify_google.set_universe()`, which no longer exists:

    AttributeError: module 'verify_google' has no attribute 'set_universe'

Because of that, the figure "66 % of verify_google passes could not have failed"
had been sitting in the policy as if it described today's code. It did not. It
described an earlier version, and it could not be reproduced.

## The repair, two calls

`set_universe()` was replaced by `all_check_ids()`, which is the function that
now does the same job: it discovers the universe by running the verifier on two
empty documents rather than reading a hard-coded list, so adding a check updates
the universe automatically and a stale list cannot hide a regression.

    patched 2 call(s): set_universe -> all_check_ids
    universe size: 47

## The result

    41 mutations, each aimed at specific checks of a real corpus document
    41 of 41 fired their target
     0 missed
     0 errors
    47 distinct checks targeted, 47 fired at least once, 0 never fired

**Every one of the 47 docx checks can fail.** On this evidence none of them
needs deleting for being unfalsifiable.

## What this changes, and what it does not

**It retires the 66 % figure completely.** Not because the checks got better,
but because the number was never about this code. `STALE-47-FALSIFY.md` recorded
that it could not be reproduced; this is the reproduction, and it says the
opposite.

**It does not make the 47 checks the primary signal.** They are still advisory,
for the reason that never depended on any percentage: a named check tells you a
defect exists but not how large it is. `share@5px` sizes a document; `01_page_count`
does not. That argument stands on its own and is now the only one used.

**It does not mean the checks are correct.** Falsifiable is not the same as
right. A check can fire on every mutation aimed at it and still measure the
wrong thing, or fire too eagerly on documents that are fine. What has been
proven here is narrower and exact: each check responds when its input is broken.

## Reproducing it

    cd tools/p2w-bench
    python3 falsify.py --corpus <dir with the 7 base PDFs> \
                       --docx   <dir with their .docx>     \
                       --render <dir with their PDF renders> \
                       --out out.json --md out.md

The 7 base documents are named in `BASES` at the top of `falsify.py`. All seven
must be present in all three directories or the run stops with
"missing <path>" -- which is what it did before this was sorted out.

## Still open

Falsifiable is the floor, not the ceiling. The next question about these 47 is
not "can it fail" but "does it fail on the right things" -- a precision question
that needs documents known to be correct, not mutations known to be wrong.
