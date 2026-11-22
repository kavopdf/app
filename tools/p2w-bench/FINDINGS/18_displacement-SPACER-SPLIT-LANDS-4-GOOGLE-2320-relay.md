# 18_displacement: the spacer SPLIT lands 4 documents in Google - it was a lead, not a dead end

**Run:** relay/fixer slot 23:10 IST, 22 Nov 2026. **Class:** `18_displacement` (worth 38.7 clean
documents, the largest single check by `classpick.py --leverage`).

## What this run did

The 19:00 slot measured the spacer SPLIT (`w:before = spacerTw - 20`, `w:line = 20`) as
LibreOffice-neutral and 8.7 of 11.3 pt better in Google on `two-tables-stacked-with-no-gap`, and
recorded it as a lead because that one document stayed 46/47. **The 19:00 slot tested the split on
the hardest document and stopped.** That is the right place to prove a construct and the wrong place
to measure its yield: `two-tables-stacked-with-no-gap` carries a second term (23 rows of
`w:trHeight` that Google lays a whole point tall) which no spacer change can touch.

So this run took the same patch, applied it unchanged (`git apply --include=DocxWriter.java` on
`FINDINGS/18_displacement-SPACER-SPLIT-LO-NEUTRAL-STEP-11.3to2.6-1900-f1x.patch`), and measured it
across **all 16 documents that fail `18_displacement` and nothing else** - every one of them 41/42 or
46/47, i.e. one check from clean.

## LibreOffice: neutral on all 16, not just on one

`benchmarks/p2w.py measure_doc`, before and after the patch, same corpus, same engine otherwise:

| document | share5 before | share5 after |
|:--|--:|--:|
| 16_right_aligned_amounts_txtpos | 0.00 | 0.00 |
| 22_invoice_four_columns_txtpos | 0.00 | 0.00 |
| 29_dot_leaders_txtpos | 0.00 | 0.00 |
| 31_times_body_arial_headings | 1.04 | 1.04 |
| 362_price_list_dense | 0.03 | 0.03 |
| 41_coloured_headings_white_bg | 0.00 | 0.00 |
| 68_journal_wide_table_spanning | 12.09 | 12.09 |
| 71_invoice_space_aligned_no_rules | 26.88 | 26.88 |
| 72_bank_statement_no_rules_right_amounts | 0.00 | 0.00 |
| 73_marksheet_subject_marks_grade | 0.00 | 0.00 |
| balance-sheet-two-columns-of-figures | 0.57 | 0.57 |
| bus-timetable-station-left-times-right | 0.27 | 0.27 |
| insurance-policy-schedule | 0.53 | 0.53 |
| mobile-bill | 1.55 | 1.55 |
| table-with-no-header-row | 0.61 | 0.61 |
| two-tables-stacked-with-no-gap | 0.77 | 0.77 |

Bit-identical to two decimal places on every one. The `.docx` did change (the table-top spacer of
`two-tables-stacked-with-no-gap` went from `before="0" line="247"` to `before="227" line="20"`), so
this is a construct LibreOffice does not measure and Google does - exactly the asymmetry the split
was built for.

## Google: four documents are now 42/42

Each one converted with the patched engine, uploaded to `KavoPDF-Verify`, converted to a Google Doc,
exported as PDF, and scored by `verify_google.py --docx` against the source PDF.

| document | before (stored gverify) | after | n_out of matched runs |
|:--|:--|:--|:--|
| `73_marksheet_subject_marks_grade` | 41/42, fails 18 | **42/42 PASS** | 60/64 -> 0/64 |
| `41_coloured_headings_white_bg` | 41/42, fails 18 | **42/42 PASS** | 21/36 -> 0/36 |
| `29_dot_leaders_txtpos` | 41/42, fails 18 | **42/42 PASS** | -> 0/52 |
| `72_bank_statement_no_rules_right_amounts` | 41/42, fails 18 | **42/42 PASS** | -> 4/80, all within tolerance |
| `22_invoice_four_columns_txtpos` | 41/42, fails 18 | 41/42, fails 18 | 21/71, med -2.76 pt |
| `16_right_aligned_amounts_txtpos` | 41/42, fails 18 | 41/42, fails 18 | 20/64, med -2.45 pt |

`dy.py` on the two that still fail shows the shape of what is left: a uniform `med -2.5 pt` offset
with a fitted slope near zero, i.e. **a constant step of about 2.5 pt, not drift**. That is the same
quantity the 19:00 slot left behind as "2.6 pt remains (the empty paragraph's own line box, one
point, plus rounding)" on `two-tables-stacked-with-no-gap`. The two failures are one more spacer
term away, and they are the same term on both documents - a candidate for the next slot, not a new
class.

## What is now true that was not

1. **The spacer split is a fix, not a lead.** It takes 4 of the 16 solo-`18_displacement` documents
   to 42/42 in Google with no LibreOffice movement anywhere in the set. The 19:00 slot's own
   conclusion - "the patch lands no document" - was true of the one document it scored and false of
   the class.
2. **`two-tables-stacked-with-no-gap` is not the class's representative document.** It is the only
   one of the 16 with a many-row table, and its residual is a `w:trHeight` term that the other 15 do
   not carry. Proving a construct there is right; sizing its yield there is not.
3. **The remaining 2.5 pt step is a single term shared by `22_invoice_four_columns_txtpos` and
   `16_right_aligned_amounts_txtpos`.** Two independent documents, the same fitted offset, slope ~0.

What would prove this wrong: a Google round trip on the other ten solo-18 documents showing they
still fail `18_displacement` with an offset larger than the 2.5 pt step - that would mean the split
is one of several terms on those documents and the four passes were the easy ones.

## The full corpus, and the gate

The patch may not land without `regress.py --check`, and that needs the whole corpus measured
against this engine. It was rebuilt and measured here: 213/213 converted with the patched engine,
212/213 scored (416_many_tiny_pages is exempt by `EXEMPT.json`), written to
`benchmarks/RANKING.csv`.

    docx: no document worse than baseline
    txt : no document worse than baseline
    google-safe : no construct Google ignores has spread
    PASS - nothing got worse in both formats, and the table matches this engine.

**The `.txt` side is untouched by construction, and here is the proof rather than the claim.** The
patch is in `DocxWriter`, and the `.txt` is written by `TxtWriter` from the same `PdfToWord.Result`,
so no `.txt` byte can depend on it. Checked rather than argued: all 16 documents of the measured set
were converted before and after the patch and `cmp` reports **16 of 16 `.txt` identical**. The
engine stamp is shared by both formats, so `regress.py --stamp` was run to record that the table
describes this tree; `RANKING-TXT.csv` itself was not rewritten, because the verifier did not change
and only the stamp was stale.

## Where the next slot should start

`22_invoice_four_columns_txtpos` and `16_right_aligned_amounts_txtpos` both fail with a **constant
-2.5 pt step and a fitted slope of ~0** (`dy.py`). That is one term, on two documents, and it is the
same "2.6 pt remains" the 19:00 slot isolated on `two-tables-stacked-with-no-gap`. The empty spacer
paragraph's own line box is one point of it. A split that puts the *whole* gap in `w:before` and
zeroes `w:line` - the 08:56 attempt - is now worth re-testing **on these two documents**, because the
reason it was rejected (mobile-bill's LibreOffice regression) came from a renderer that honours both
attributes, and on a 1 pt hairline the LO movement is 1 pt, not the whole gap. That is a hypothesis
for the next slot, not a measurement made here.
