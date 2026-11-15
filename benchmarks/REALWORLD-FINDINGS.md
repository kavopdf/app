# Real-world documents: the synthetic corpus was hiding a large failure

The 211-document corpus is synthetic. It scores median `share@5px` **0.3 %**,
with 120 of 211 clean. On nine real documents taken from this project's own
uploads, the same instrument on the same engine reads:

    median share@5px   10.3 %      (34x worse)
    worst              98.7 %
    clean (<1 %)       3 of 9      (33 %, against 57 % synthetic)
    text recall        all >= 99.7 %

## The ranking

| # | document | problem | share@5px | max_pt | text | pages |
|---|---|---|---|---|---|---|
| 1 | 041122-Account_Opening_Form | content-missing-partly-replaced | **98.7 %** | **937.9** | 99.7 % | 9 |
| 2 | Account_Opening_Form_Fillable_filled | content-missing-partly-replaced | **97.6 %** | **358.1** | 99.7 % | 9 |
| 3 | property-tax-receipt | content-missing-nothing-in-its-place | 10.8 % | 55.7 | 100 % | 1 |
| 4 | admit-card | content-missing-nothing-in-its-place | 10.7 % | 57.1 | 100 % | 1 |
| 5 | delivery-challan | content-missing-nothing-in-its-place | 10.3 % | 39.8 | 100 % | 1 |
| 6 | gst-invoice-3line-items | content-missing-nothing-in-its-place | 7.2 % | 20.2 | 100 % | 1 |
| 7 | 350_question_paper | none | 0.1 % | 16.8 | 100 % | 1 |
| 8 | 300_prescription_rx | none | 0.1 % | 21.6 | 100 % | 1 |
| 9 | 311_fir_police_form | none | 0.0 % | 2.4 | 100 % | 1 |

## What this means, stated plainly

**The words come through. The layout does not.** Text recall is 99.7-100 % on
every real document -- nothing is being lost from the text. But on the two
nine-page bank forms, 98 % of the ink sits where the source did not put it, and
the furthest mark is 937.9 pt from home. That is 33 cm: larger than the page.

**A synthetic corpus cannot prove real-world fidelity, and this is the proof.**
Before this run the honest summary was "median 0.3 %, 120 clean". That sentence
was true of the corpus and misleading about the product. The same engine, same
instrument, same day, reads 34x worse on documents a user would actually open.

## Why the synthetic corpus missed it

Every synthetic document in the 211 is single-page or a small multi-page table.
The two worst real documents are **nine-page forms** with repeated field grids.
The corpus has no nine-page form. It also has no scanned multi-page document:
`Screenshot_20261029_143058_KavoPDF_searchable` (2.2 MB) was excluded from this
run because a single measurement exceeded the sandbox's per-command budget, and
that exclusion is itself a coverage note, not a pass.

## What to do with this

1. These nine documents belong in the corpus, as a separate real-world set so
   the synthetic baseline stays comparable. They are now `REALWORLD-RANKING.csv`.
2. The 9-page form failure is the highest-value defect in the whole project:
   it is the largest measured error anywhere, it affects a document type users
   open constantly, and the synthetic corpus cannot see it.
3. Never quote the synthetic median as if it described the product. Quote both.
