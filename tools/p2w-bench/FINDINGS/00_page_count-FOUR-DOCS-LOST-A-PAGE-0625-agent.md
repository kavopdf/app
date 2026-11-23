# Four documents were scored yesterday and are refused today — they gained a page

**23 Nov 2026 · agent · measured from the committed gverify history**

## What happened

`benchmarks/gverify/` says 25 documents are refused on page count. Three days ago it said 21. The four
that were added were all **scored** before:

| document | was | now | page |
|---|---|---|---|
| `314_tender_rfp_boq` | 41/47 | refused | 2 against a 1-page source |
| `326_itr_computation` | 41/47 | refused | 2 against a 1-page source |
| `353_admit_card` | 39/47 | refused | 2 against a 1-page source |
| `402_calendar_month_grid` | 45/47 | refused | 2 against a 1-page source |

Two landed in `214d9eab` (22 Nov 23:15) and two in `7d956ab5` (23 Nov 02:15).

## Why nothing caught it

`regress.py` compares `{document: count of Google failures}` from the committed results against the working
tree. Both readers open with

    if j.get("status") == "page_count_refused":
        continue

because a refused document has no `failed` list to count. So the transition **scored → refused** is
invisible to every check in that file, and `regress.py --check` prints PASS while four documents that could
be measured on 22 Nov cannot be measured on 23 Nov.

**A document the corpus can no longer measure is worse than one that fails a check.** The failing one can be
fixed. The refused one cannot even be looked at.

## What the fix has to be

The check cannot compare the two dicts — they both skip refused. It has to ask, per document refused in the
tree, what that document was in the previous commit that touched it:

    git log -2 --format=%h -- benchmarks/gverify/<doc>.json
    git show <the older hash>:benchmarks/gverify/<doc>.json

If the older one was `status: ok`, the document has gained a page and the gate must refuse.

**And it must only run when the tree's gverify results differ from HEAD's.** The files are committed state,
so comparing the working tree to history flags a regression that landed commits ago on every single commit,
and a gate that cries about the past is a gate people learn to ignore.

I started that change, could not land it cleanly in the time available, and reverted it rather than leave a
half-edited gate in the tree. **The measurement above is the deliverable; the gate change is the next run's.**

## The other half, which is the real work

Four documents that were 41/47, 41/47, 39/47 and 45/47 are now unmeasurable because the engine put a second
page under them. Whatever moved between 22 Nov and 23 Nov made four one-page documents spill. That is a
regression to find and revert, and it is worth more than the gate change — the gate only tells you it
happened.
