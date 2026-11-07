# Visual score — one row per document

The 09:00 digest reads this file. It counts the PASS rows to answer "how many documents
are completely done, out of 208", and it works out the remaining days from the dates.

A document is PASS only when every page was looked at, every finding was verified against
the PDF, and no verified finding is left open. Processing a document is not passing it.

Rows are appended, never edited: if a document appears more than once, the LAST row is the
truth.

| Date | Document | Verdict | Why |
|------|----------|---------|-----|
| 2026-11-07 | 79_inr_indian_digit_grouping_table | PASS | table, amounts and Indian digit grouping all match |
| 2026-11-07 | 300_prescription_rx | PASS | QR identical, table and header match, 2.3 % of pixels differ |
| 2026-11-07 | 303_discharge_summary | FAIL | breaks:WARNING SIGNS, moved:Resident Medical Officer (193.6 pt) |
| 2026-11-07 | 350_question_paper | FAIL | wraps:Write SQL queries, count:[08] 17 vs 13, pagecount 2 vs 1 |
| 2026-11-07 | 01_stamp_rotated_15deg_upright | FAIL | stamp position, 2 text boxes (G3) |
| 2026-11-07 | 64_newspaper_uneven_columns_ad_boxes | FAIL | reading order 7.1 %, 5 pages against the PDF's 1 |

## What this file is not

It is not a summary of batches, and it is not a place to record that a batch ran. Only a
document that has been through all seventeen steps and holds no open verified finding goes
in here as PASS. The counts above are the four documents examined by hand on 7 Nov while
the pipeline was being built; the corpus work starts from here.

## Why the dates matter

The digest computes the rate as PASS documents divided by the days between the first PASS
row and today, then divides what is left by that rate. With fewer than two days of history
it says "not enough data yet" instead of a number, because a rate from one day is not a
rate.
