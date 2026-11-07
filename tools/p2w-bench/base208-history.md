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

## 7 Nov — the measurement was repaired, and the baseline re-recorded with it

    Trigger   the eight hand-picked thresholds in the visual gates were replaced, and
              the colour test moved from Euclidean RGB distance under 24 to CIE76
              delta-E under 3.
    Result    base208.json:  identical on every field. The block test still uses the
              3000 pt2 floor, so no count moved.
              base208-position.json:  re-recorded. The aggregates came out the same to
              one decimal - position 11.7, size 99.2, name 93.1, colour 98.9 - but 45
              per-document fields moved, and a baseline recorded with a measurement that
              no longer exists reports regressions that are not there.

    Before    position 11.7 %   size 99.2 %   name 93.1 %   colour 98.9 %
    After     position 11.7 %   size 99.2 %   name 93.1 %   colour 98.9 %

Why this row exists even though the numbers did not move: a baseline is only meaningful
against the measurement that produced it. Changing the formula and keeping the old file
would have been the quiet kind of drift this file is here to make impossible.
