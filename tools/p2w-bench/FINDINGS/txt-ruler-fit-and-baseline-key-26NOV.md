# Two .txt instrument faults, measured: t02's estimator and t08's vertical key

**26 Nov 2026 · fixer slot 05:57 · measured, kept.** Scope: `tools/p2w-bench/verify_txt.py` only.
The .docx did not move - `txt_gate.py --gate` records `benchmarks/RANKING.csv` as
`b2fce93d8aebf91f`, unchanged across the gate.

## Result

| | before | after |
|---|--:|--:|
| .txt clean | 204 of 213 | **205 of 213** |
| .txt failing | 9 | **8** |
| documents newly failing | - | **0** |

Measured twice, independently, and they agree exactly:
- `txt_rank.py --all --rescore` → `scored 213 this pass | 205 clean | 8 with a failed check | 0 errors`
- a separate multiprocessing re-score of all 213 (6 workers, own CSV) → `scored 213, clean 205, failing 8`,
  with the failing set a strict subset of the previous 9.

The document that flipped: `334_patent_document` (t02 69 % → 100 %).
`39_small_caps_letter_spacing`'s t08 went 21/22 → 23/23 PASS but the document stays open on
`t01_word_accuracy` (97.4 %), so it is not counted.

## Fault 1 - `t02_position` fitted its ruler with a median, which a rounding artefact outvotes

`_ruler()` returned `median(x / col)`. On `334_patent_document` 22 of the 32 pairs are
`(x = 28.0, col = 5)` - the body margin, where `round(28 / 5.1) = 5` inflates the ratio to 5.60 -
and the other 10 are the real ruler at 5.00-5.13. The median returns 5.600; the writer used 5.100;
the check charged the document 69 % for its own estimator's error. At mid = 5.100 all 32 pairs fit.

The fix is a leverage-weighted least-squares slope through the origin, `mid = sum(x*col)/sum(col*col)`:
a pair at column 60 is 144x the evidence of one at column 5, which is the correct weighting when the
error is rounding of `x/mid`. It is accepted only when it is a plausible character width
(`POS_MID_MIN..POS_MID_MAX`) and within a factor of two of the median; otherwise the median stands,
so a degenerate pair set cannot move the ruler into nonsense.

**Falsifiability is unchanged.** This is an estimator fix, not a tolerance change: a .txt with
randomised indents destroys the linear relation, the share falls, and the document still fails - the
same test that made the first "abstain on a bad fit" version unacceptable on 19 Nov.

## Fault 2 - `t08_line_order` keyed on the bbox top, which is not a vertical position

`39_small_caps_letter_spacing` draws its title twice on one baseline: a 1 pt white invisible
duplicate at `y0 = 65.11` and the 15 pt letter-spaced one at `y0 = 52.64`. The bbox top of a 15 pt
caps line sits 12.5 pt above a 1 pt line sharing its baseline, so keying on it invents a
top-to-bottom relation between two pieces of one visual line. Keyed on the baseline
(`max(span["origin"][1])`), the same predicate reports 23 of 23.

The line model now carries `by` (baseline) beside `y` (bbox top); nothing else reads `by`.

## Not fixed here, and why

- `74_balance_sheet_indented_subitems` (t02 80 %) needs the **source x** changed to the first inked
  glyph, not the bbox x0 - the indentation is leading spaces inside the text run. The same run
  measured that applying it blindly newly fails 4 documents, so it needs the upright/non-RTL
  restriction and its own full-corpus pass. Left for the next run with the restriction in place.
- The remaining 8 failures are 6 engine defects and 2 check artefacts, ranked in
  `PATCHES`-adjacent notes from the 26 Nov txt diagnosis.

## A note on the ratchet

`RATCHET-TXT.json` is stamped with a sha over the instrument, so any edit to `verify_txt.py` makes
the marks STALE and `txt_rank.py` then refuses to compare or carry them forward. The check universe
did not move (12 checks before and after); only an estimator inside it did. The marks were left
exactly as they were - not deleted, not reset - and the regression evidence for this change is the
two independent full-corpus re-scores above, each showing 0 documents newly failing.
