# Prediction, written before the measurement (27 Nov, fixer)

Document: `362_price_list_dense`. One page. Currently 41/42 in Google, failing only
`18_displacement`: 257 matched runs, 181 out, dy = -6.19 - 0.01475*y, rms 0.51 pt, span 6.81 pt.

Evidence: the document is a 28-row table, every row `w:trHeight w:val="168" w:hRule="atLeast"`
(8.4 pt = the source's measured row pitch, 27 deltas of 8.4 pt). Every cell paragraph asks
`w:before="128" w:line="8" w:lineRule="exact"` = 136 tw = **6.8 pt**, which is 32 tw (1.6 pt)
short of the row it sits in.

Hypothesis: Google lays the row from the paragraph's own height, not from `w:trHeight` (the repo
already records "Google ignores trHeight"). So every row lands ~0.25 pt short, and 27 rows
accumulate 6.81 pt down the page - which is exactly the measured span.

Probe: `w:before` 128 -> 160 on those paragraphs only, so before+line = 168 tw = the row height.

PREDICTION: dy span falls from 6.81 pt to under 1.5 pt, n_out falls from 181 to <= 13 (the page's
budget), and `18_displacement` passes - the document becomes 42/42.

REFUTED IF: n_out stays above 13, or the drift keeps its slope, or any other check starts failing.

## Second document, same construct, different shape (16_right_aligned_amounts_txtpos)

13 rows, `w:trHeight=380`, cell paragraphs `w:before=342 w:line=0` = 342 tw - a deficit of
38 tw (1.9 pt) per row. Currently 41/42, failing only `18_displacement`: 64 runs, 7 out
(budget 4), dy = -2.48 - 0.00681*y, span 3.95 pt.

PREDICTION: `w:before` 342 -> 380 makes n_out fall from 7 to <= 4 and `18_displacement` pass.
REFUTED IF: n_out stays above 4, or the slope is unchanged.
