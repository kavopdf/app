# 18_displacement: the spacer gap SPLIT, not moved - LO-neutral, and it removes 8.7 of 11.3 pt

**Run:** fixer slot 19:00 IST, 22 Nov 2026. **Class:** `18_displacement` (124 of 169 failing
documents; 16 fail it and nothing else).

## What was wrong with the 08:56 attempt, and why this one is different

The 08:56 slot moved the whole table gap from `w:spacing/@w:line` to `w:spacing/@w:before`.
Google does not deliver `w:line` on the empty spacer paragraph; it does deliver `w:before`. But a
renderer that honours BOTH then sees `before + line`, i.e. a taller paragraph - that is the
`mobile-bill` 1.55 -> 1.74 regression, and `regress.py --check` was right to refuse it.

**A split keeps the sum.** `spacerTw` is the gap the page drew. Emit

    w:spacing w:before="spacerTw - 20" w:line="20" w:lineRule="exact"

with the `w:sz w:val="2"` (1 pt) paragraph mark the spacer already carries. A renderer that
honours both attributes lays `(spacerTw-20) + 20 = spacerTw` - **identical**. A renderer that
ignores `w:line` but honours `w:before` - which is what Google measured as - gets the gap.

## Measured

Engine `462353f9+a6c98c1451` (HEAD + the patch, `FINDINGS/18_displacement-SPACER-SPLIT-LO-NEUTRAL-STEP-11.3to2.6-1900-f1x.patch`).

| | before | after | verdict |
|:--|--:|--:|:--|
| `mobile-bill` LibreOffice, `share1` (`benchmarks/p2w.py measure_doc`) | 43.87 | **43.87** | LO-NEUTRAL |
| `mobile-bill` LibreOffice, `share5` (the number the 08:56 attempt moved to 1.74) | 1.55 | **1.55** | LO-NEUTRAL |
| `two-tables-stacked-with-no-gap` table top, Google | 80.1 pt | **88.8 pt** | source 91.4 pt |
| step error, Google | 11.3 pt | **2.6 pt** | **-8.7 pt removed** |
| `two-tables-stacked-with-no-gap` Google verdict | 46/47 | 46/47 | unchanged |

The prediction written before the run was "LO signature unchanged to 2 dp; the Google step
collapses". The first half held exactly. The second half held to 77 %: 8.7 of the 11.3 pt went,
2.6 pt remains (the empty paragraph's own line box, one point, plus rounding).

## Why it lands no document, and what the next slot must do

`two-tables-stacked-with-no-gap` stays 46/47 because `18_displacement` has a SECOND term that this
patch does not touch: `w:trHeight="360"` (18.0 pt) plus a 0.5 pt insideH border is laid by Google as
**19.0 pt** per row, against a source pitch of 18.4 pt. 23 rows accumulate 13.8 pt of drift.

So: step + drift together is the construct, not the step alone. The drift lever is
`w:trHeight/@w:val` - 352 tw lays 18, 360 tw lays 19 (whole-point rounding), so 18.4 pt is not
reachable by one declaration; error-diffused 352/360 is the candidate, and it is the piece that must
be measured against LibreOffice before anything is committed, because 352 makes LO lay 17.6.

## Recorded as a lead, not a fix

The patch is not committed: `regress.py --check` needs a full-corpus measurement and this slot ran
out. The patch is in this directory, one build away, with both halves of the prediction already
measured.
