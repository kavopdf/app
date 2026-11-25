# The lead outcome swallowed 28 documents of real movement

## Measured from the ledger

    leads recorded:                          69
    leads whose attempt DID move documents:   9
    documents moved but recorded as lead:    28
      32_stroke_lines                   14
      04_chars_missing                  11
      18_displacement                    1
      content-present-partly-displaced   1
      t12_word_invention                 1

04_chars_missing is the clearest case: eleven attempts, every one recorded as `lead`, and eleven documents
moved between them. Real improvement, none of it credited.

## Why it happened

When the engine or an instrument carried uncommitted changes, add() zeroed the moved count and rewrote the
outcome to `lead`. The reason is sound - a measurement of code that exists only in a sandbox is not a
measurement of the repo - but the effect was that a run which genuinely improved documents was recorded as
having improved nothing.

The ledger then told the rotation a story that was not true: eighteen attempts on 18_displacement that moved
nothing, when one of them moved a document; eleven on 04_chars_missing that moved eleven. A class that is
producing looks identical to a class that is not.

## What was changed today, and what it does not fix

A dirty-tree measurement now returns 2 without recording an attempt at all, so the ledger cannot fill with
leads that mean nothing. That is the correct discipline - commit what you measured, then record it - but it
does not recover the 28 documents already lost, and it makes the loss permanent for any future run that
measures a dirty tree: the movement is not credited, and unlike before it is not even visible in the history.

## The fix that is still needed

A lead whose attempt moved documents should be re-recordable as `kept` once the commit lands. Two ways, and
the second is better:

1. When `--moved N --outcome kept` is refused for a dirty tree, keep the number in the row as
   `pending_moved` with the reason, so the history shows what was measured even though it is not credited.
2. On the next run, if the tree is clean and the same class is attempted again, the pending number is
   re-measured rather than re-derived - which is what happens naturally if the fixer simply re-runs.

Option 1 costs one field and makes the loss visible. Option 2 is the honest one but needs the run to
remember.

## The deeper pattern this belongs to

This is the fourth time today that a real quantity was rendered as a zero by the pipeline: a failed read as
0 fixed, an absent engine as 0 stale, an unmeasured attempt as 0 moved, and now a dirty-tree measurement as
0 improved. Every one made work look like no work, and every one made the fixer's own report argue against
continuing.
