# Baseline history

One row per move of the ratchet in `base208.json`. A ratchet nobody can see is a
ratchet nobody can trust.

## The rule this file records

    Run G2 across the whole corpus BEFORE recording anything.
    Any document worse  -> the fix is reverted and the baseline does not move.
    Every document same or better -> drop --check, record, commit.

So every row below is a state that was no worse than the row above it, on every
document, not on average.

## Moves

| Date | Documents improved | missing | extra | blocks | nobg | blank | pages | lines |
|------|--------------------|---------|-------|--------|------|-------|-------|-------|
| 6 Nov | starting state | 133 | 243 | 0 | 0 | 0 | 537 | 15780 |

The starting state was established by converting all 208 documents twice: once with
the shipped 3.52.1 build and once with the code as it stood, then comparing every
document. The five gate counts were identical and the page count identical; line
count moved by 36 across 208 documents, which the five counts cannot see and which is
why page count and line count are now gate signals too.

`reflines` for the corpus is 17777 and `refpages` is 540 - what the PDFs themselves
hold. The gap to `lines` 15780 is the work: lines the converter is not yet producing.
