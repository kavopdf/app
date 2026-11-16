# Verification - is the data the fixer receives accurate?

Not a gate run. The gates said READY. These are invariants checked directly against the
data, because a gate that passes is only as good as the checks it happens to contain.

## Baseline: 8 of 8 invariants pass

    PASS  213 rows
    PASS  no duplicate documents
    PASS  212 scored + 1 unmeasured
    PASS  share1 >= 2 >= 3 >= 5 >= 10 for every row
    PASS  median_pt <= p90_pt <= max_pt
    PASS  every problem is one of the 9 names
    PASS  share5 in 0..100
    PASS  text_recall in 0..100

The two that matter most are the monotonic ones. A larger tolerance can never match less
ink, so `share1 >= share5 >= share10` must hold for every document; and a median can never
exceed a p90, nor a p90 a max. A single corrupted or mis-sorted row breaks one of them.
None do. The measurement is internally consistent.

Text recall is a median of 100.0 % and **zero documents fall under 90 %**. That is worth
stating plainly: the engine gets the words right almost everywhere. What it gets wrong is
where the ink sits, which is exactly what the position axis measures.

## Classifier: the grouping is right, the file was not

The counts are correct - the summary table matches the actual distribution exactly:

    none 120 | missing-nothing-in-place 30 | missing-partly-replaced 16
    wholly-displaced 15 | partly-displaced 12 | partly-lost 11
    lost-and-displaced 7 | single-element-far-out 1     = 212

But the file itself had three defects:

**1. Two documents listed twice.** `041122-Account_Opening_Form` and
`Account_Opening_Form_Fillable_filled` each appeared in two different tables. 215 rows for
213 unique documents.

**2. Three different table shapes.** 92 rows with 11 pipes, 122 with 9, one with 7. A
reader - human or fixer - has to guess what each column means in each block.

**3. An unmeasured document marked OPEN.** `416_many_tiny_pages` is exempted in
EXEMPT.json, and the class file listed it OPEN anyway.

**The consequence, measured:** `round.py open_classes()` counts every row that says OPEN
and reported **94** when there are **92** defective documents. The round-close gate was
counting two phantoms. A fixer reading the file would see the same document in two tables
with different column meanings.

## What is now enforced, in code

`classify_gate.py` refuses a class file that:

  * lists any document more than once
  * has more than one table shape
  * omits a scored document
  * lists a document that was never scored (that one must be PARKED with a reason)
  * has a header whose N or M does not match RANKING.csv

Run against the file the 16 Nov classifier produced, it now fails with all three reasons
named. That is the point: the checks live in the gate, not in a sentence a run may or may
not follow.

## Honest limits

**The classifier's grouping was never wrong.** Every count matched, no document was
invented, no class was mislabelled. What was wrong was the file's shape and its duplicate
rows - a presentation defect that had a real consequence for the round-close gate.

**Baseline's numbers are internally consistent, not independently re-measured.** The
invariants prove the table is coherent and cannot have been shuffled or corrupted. They do
not prove `share@5px` is the true displacement of every document - that is what the 14/14
ground-truth gate does, and what the ratchet does against the committed baseline.

**Neither check says anything about whether the defects are FIXABLE.** That is the fixer's
question and it has not started.
