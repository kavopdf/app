# Google lays a declared table row at the next 0.75 pt rung

Measured 26 Nov 2026 on a real Google render of `72_bank_statement_no_rules_right_amounts`
(engine `a4d8fca469bba636`, after the spacer->`w:before` clamp).

## The measurement

Declared row height 17.00 pt. Google draws 17.25 pt. That is `ceil(h / 0.75) * 0.75`, and the
effect is cumulative down the table: 18 rows x +0.25 pt puts the foot of the table +3.50 pt below
where the PDF drew it, against a 3.01 pt tolerance.

After the spacer patch the same document reads `med_dy = +1.1, worst_dy = 4.8` (was `-13.0 / 28.2`).
The residue is this rung, not the gap.

## What this implies for the engine

Only multiples of 0.75 pt are drawable. A row whose target height is not a multiple of 0.75 cannot
be hit exactly; the error must be *distributed* rather than accumulated. The candidate is a running
accumulator: for each row, declare a value whose ceiling lands on the nearest reachable multiple of
the *cumulative* target, so the residual never exceeds 0.375 pt at any row and never sums.

## What would refute it

A patched document whose Google `worst_dy` does not fall below 3.0 pt with the rung compensated.
Do not implement it before that render exists.
