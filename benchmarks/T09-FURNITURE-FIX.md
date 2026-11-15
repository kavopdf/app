# t09_page_furniture could not fail, and why

## The symptom

A falsifiability test duplicated every running head three times on every page of
`412_page_labels_roman`. The check still passed. Three different mutations, all
passed. It looked like the check was blind.

## The cause, one line

    present += min(txt_furniture.get(key, 0), len(pgs))

`min()` caps `present` at `owed`. So `present` could never exceed `owed`, and the
predicate `present == owed` held whenever there were AT LEAST enough copies. The
check could only ever see MISSING furniture, never DUPLICATED furniture.

Its stated meaning is: "one copy of each running head per page it belongs to."
That is a two-sided claim. The implementation was one-sided. The cap was the bug.

## The fix

    present += txt_furniture.get(key, 0)

One line. `present` can now exceed `owed`.

## Verified

On `412_page_labels_roman`, where the check previously passed:

| mutation | owed | present | verdict |
|---|---|---|---|
| none (baseline) | 10 | 10 | pass |
| every line duplicated 2x | 10 | **20** | **fail** |
| every line duplicated 3x | 10 | **30** | **fail** |

The check now detects duplicates. With this, all 12 .txt checks are proven able
to fail: 12 of 12.

## What the fix immediately found

Run across every corpus document where t09 applies, after the fix:

    8 applicable documents:  6 pass, 2 fail

    324_loan_amortisation_schedule    owed 66    present 1485
    gst-invoice-multipage-item-table  owed 39    present  43

`324_loan_amortisation_schedule` emits its running head **1485 times where it
owes 66** -- 22 times too many. The `min()` cap hid this completely: `present`
was pinned at 66 and the document read as perfect.

That is the point of a falsifiability test. The check was not merely unable to
fail; it was actively reporting a 22x duplication as correct.

## Regression check

The 6 documents that passed before still pass. The fix does not manufacture
failures. The 2 that now fail are failing for a reason visible in the numbers.

## Standing rule, unchanged

A check that cannot fail is a bug in the check, not a pass. This one was found
by duplicating a running head and watching nothing happen.
