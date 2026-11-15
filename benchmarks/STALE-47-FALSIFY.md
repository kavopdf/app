# The 47-check falsifiability harness no longer runs

`tools/p2w-bench/falsify.py` is the tool that produced the "66 % of
verify_google passes could not have failed" figure. It does not run against the
current `verify_google.py`:

    AttributeError: module 'verify_google' has no attribute 'set_universe'
    (falsify.py:1060, universe = V.set_universe())

`falsify.py` is 1193 lines and calls an API that has since been removed from
the verifier it tests. So the 66 % figure is a measurement of an EARLIER
version of the 47 checks. It is not a statement about today's code, and it must
not be quoted as one.

## What this changes

`benchmarks/LAYER-POLICY.md` cites 66 % as the reason the 47 checks are
advisory. That reasoning still holds on its own terms -- a named check sizes
nothing, and the .txt half was independently measured at 11 of 12 proven able
to fail -- but the specific number is stale. Two honest options:

1. repair `falsify.py` to the current verifier API and re-measure, or
2. drop the number from the policy and keep only the structural argument.

Option 1 is better and is the remaining work. Until it is done, the policy
should be read as "the 47 checks are advisory because a named check does not
size a defect", without leaning on a figure nobody can currently reproduce.

## Why this is written down rather than quietly fixed

A stale number that keeps being cited is exactly the failure mode this whole
exercise exists to remove: a figure that was true once, is repeated because it
sounds authoritative, and is never re-checked. The number is retired from use
the moment it cannot be reproduced, not the moment someone notices.

## The remaining work on the 47 checks

* repair `falsify.py` against the current `verify_google.py` API, or replace it
  with a mutation harness in the shape of `TXT-FALSIFIABILITY.md`
* re-measure all 47
* for each check that cannot fail: fix its predicate or delete it
* only then may any of the 47 be quoted as evidence
