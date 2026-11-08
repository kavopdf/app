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

## 8 Nov 2026 — verified, not changed

Re-converted all 208 and re-recorded the baseline to see whether anything had moved.

| field | 6 Nov | 8 Nov |
|---|---|---|
| missing | 133 | 133 |
| extra | 243 | 243 |
| blocks | 0 | 0 |
| nobg | 0 | 0 |
| blank | 0 | 0 |
| pages | 537 | 537 |
| **lines** | **15780** | **15769** |

Six of the seven counts are identical. **`lines` fell by 11**, which is the line-pitch fix
(D-01) merging lines the old constant had split. Eleven lines across 208 documents is a small
number and it is a real change, so it is written down rather than called "identical" - a
record that rounds away the one field that moved is how a ratchet stops ratcheting.

The baseline was still left alone: `gate.py --check` reported no document worse, and a fall in
`lines` with `missing` unchanged means lines were joined, not lost. But the honest statement is
"one field moved and the move is an improvement", not "nothing moved".

What that also proves: the line-pitch fix and the gap-spending guard changed how the documents
LOOK without moving six of these seven counts. A baseline of counts cannot see a line that
moved onto the right baseline; only the position measure can. That is why
`base208-position.json` exists as a second ratchet.

**A measurement defect found while checking this.** `gate.py`'s `pages` count reads 537
against the PDFs' 540, which looks like three documents losing a page. They are not: a section
break written as `<w:type w:val="nextPage"/>` starts a new page in Word, and `gate.py` counts
only `<w:br w:type="page"/>`. Counting both gives 208 documents matching their PDF's page
count exactly, 0 spill and 0 short. The metric under-counts any document that carries a
section break, and it is left as-is for now because the baseline was recorded with it - but
anyone reading `pages 537 vs refpages 540` as three lost pages is reading a counting artifact.

