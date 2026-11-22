# 18_displacement: the spacer SPLIT lands 4 documents and costs 2 - REVERTED. It needs the scope guard first.

**Run:** relay/fixer slot 23:10 IST, 22 Nov 2026. **Class:** `18_displacement` (38.7 clean documents,
the largest single check by `classpick.py --leverage`). **Outcome: `reverted`.** The engine change is
not in the tree. Everything measured is below.

## What was done, and what it proved

The 19:00 slot left the spacer SPLIT (`w:before = spacerTw - 20`, `w:line = 20`) as an unlanded
lead because it scored one document - `two-tables-stacked-with-no-gap` - and that document carries a
second term (23 rows whose cell line box Google lays a whole point tall) that no spacer change can
touch. This run applied the same patch and measured it across **all 16 documents that fail
`18_displacement` and nothing else**, which is the set the patch was for.

### LibreOffice: neutral on all 16

`benchmarks/p2w.py measure_doc`, before and after, same corpus: `share5` identical to two decimals on
every one of the 16 (0.00/0.00, 0.03/0.03, 0.27/0.27, 0.53/0.53, 0.57/0.57, 0.61/0.61, 0.77/0.77,
1.04/1.04, 1.55/1.55, 12.09/12.09, 26.88/26.88 and five at 0.00). The `.docx` did change - the
table-top spacer of `two-tables-stacked-with-no-gap` went from `before="0" line="247"` to
`before="227" line="20"` - so this is a construct LibreOffice does not measure and Google does.

**The full corpus was then rebuilt and measured with the patched engine** (213/213 converted,
212/213 scored, `416_many_tiny_pages` exempt) and `regress.py --check` passed: no document worse in
`.docx` or `.txt`, google-safe clean. That is the whole of what the commit gate can see, and it is
not enough.

### Google: four documents pass - and two break

Converted with the patched engine, uploaded to `KavoPDF-Verify`, converted to a Google Doc, exported
as PDF, scored by `verify_google.py --docx` against the source.

| document | before | after patch | matched runs out |
|:--|:--|:--|:--|
| `73_marksheet_subject_marks_grade` | 41/42 | **42/42 PASS** | 60/64 -> 0/64 |
| `41_coloured_headings_white_bg` | 41/42 | **42/42 PASS** | 21/36 -> 0/36 |
| `29_dot_leaders_txtpos` | 41/42 | **42/42 PASS** | -> 0/52 |
| `72_bank_statement_no_rules_right_amounts` | 41/42 | **42/42 PASS** | -> 4/80, all in tolerance |
| `22_invoice_four_columns_txtpos` | 41/42 | 41/42 | 21/71, med -2.76 pt, slope ~0 |
| `16_right_aligned_amounts_txtpos` | 41/42 | 41/42 | 20/64, med -2.45 pt, slope ~0 |
| `mobile-bill` | 46/47, 1 page | **43/47, 2 PAGES** | `01_page_count`, `32_stroke_lines`, `55_orientation_mix` |
| `insurance-policy-schedule` | 46/47, 1 page | **43/47, 2 PAGES** | `01_page_count`, `32_stroke_lines`, `55_orientation_mix` |

## The controlled A/B that decided it

The two cost documents were measured **at the same engine, the same hour, differing only in the
patch**: pre-patch `46/47` and one page each, post-patch `43/47` and two pages each. Not an engine
drift, not a stale baseline - the patch, and nothing else.

Both are exactly-full pages. Spending the gap at its true value removes the ~19.5 pt of slack that
was absorbing Google's row excess, so the page overflows and content is lost. This is the mechanism
`FINDINGS/18_displacement-DITHER-REFUTED-AND-THE-GUARD-THAT-REPLACES-IT-0030-fixer.md` (slot 23:54,
landed while this run was measuring) predicted from the repository's earlier round trips: **the
blocker is scope, not row height.**

So the patch was reverted in full - engine, `RANKING.csv` and the engine stamp back to the pre-patch
commit, `regress.py --check` PASS - and the finding is recorded as a `reverted` with the numbers
attached rather than a `lead` that the next slot would have to rediscover.

## What is now true that was not

1. **The spacer SPLIT is worth 4 documents and costs 2.** +4 clean is the best single-class yield any
   run has measured this round, and it is still a net win *if* the two cost documents can be spared -
   which is what a scope guard does, not what a row fix does.
2. **`two-tables-stacked-with-no-gap` is not the class's representative document** and testing only it
   under-reports the patch by 4. Testing only the 16 solo documents over-reports it by 2, because the
   cost lands on documents that fail 18 *plus* others and were never in the set.
   **The set that matters is not "documents that fail this check alone" - it is "documents this
   construct touches".** That distinction cost this run a push and a revert, and it is the general
   lesson: a spacer is spent on every table page in the corpus, so the blast radius is every document
   with a table on a full page, not the 16 that name the check.
3. **`regress.py --check` cannot see a Google regression that has not been re-verified in Google.**
   It passed on a change that broke two documents from 46/47 to 43/47. The corpus-wide `.docx`
   ratchet is blind to this class by construction, because the whole defect is a construct LibreOffice
   does not measure. A run that changes the spacer must Google-verify the exactly-full pages before
   it commits, and the two named documents are the ones to verify.

## What the next slot should do

Implement the scope guard from the 23:54 finding - apply the gap as `w:before` only when the page's
flow budget still has slack after it - then re-run exactly this experiment: the 16 solo documents, plus
`mobile-bill` and `insurance-policy-schedule` as the guard's own test. If those two stay 46/47 at one
page and the four stay 42/42, that is **+4 clean documents for one build**, and the guard is what
makes the difference between +4 and +2.

Also worth one round trip, not a build: `22_invoice_four_columns_txtpos` and
`16_right_aligned_amounts_txtpos` both still fail with a **constant -2.5 pt step and a fitted slope of
~0** (`dy.py`). That is one term on two documents and it is the same "2.6 pt remains" the 19:00 slot
isolated. It is a second, smaller lever on the same class.
