# CORRECTED: the "live" hash is the check universe, not a fourth engine identity

This file previously claimed that `live : 36b7913c98da (12 checks)` was a fourth derivation of the engine
and that it disagreed with the tree. That was wrong, and the correction matters more than the original.

## What was actually true

The line is not printed by gverify.py at all. It is txt_rank.py:256:

    print("      live  : %s (%d checks)" % (live_sha or "unknown", len(ids)))

and live_sha comes from `_universe()`, which hashes the set of check ids verify_txt.py offers. `(12 checks)`
in the same line was the tell - 12 is a count of checks, not of files or documents, so the value beside it
is a check-set fingerprint.

It is a different question from the engine, and it is a legitimate one: `marks_universe != live_sha` is how
the tool notices that the checks themselves changed and the old marks no longer describe the same
instrument. Comparing it to 981ff1fa35e2cf67 was never the right comparison.

## Why this correction is worth writing down

The finding was produced the way every real defect this session was found - by spotting a hash that did not
match. This time the hash was answering a different question, so the match was never owed. Two lessons:

1. A hash with no label is not evidence. `live` says nothing about what was hashed; the `(12 checks)`
   beside it did, and I read past it.
2. The correction is the same discipline as the original: verify before claiming. I had the evidence in
   front of me and mis-assigned it.

## Verified

    _engine_now()  gverify.py:141  reads /scratch/work/p2w/.stamp first  -> 981ff1fa35e2cf67  CORRECT
    live_sha       txt_rank.py:195 from _universe(), hash of check ids   -> 36b7913c98da        CORRECT

Neither is broken. No change was made.
