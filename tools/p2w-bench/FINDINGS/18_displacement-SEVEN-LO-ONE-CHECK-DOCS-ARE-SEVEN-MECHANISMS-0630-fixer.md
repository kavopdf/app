# 18_displacement — the seven documents that are ONE check from clean in the measurable renderer, and the fact that they are seven mechanisms, not one

**23 Nov 2026 · fixer slot 05:58 → 06:35 IST · engine `98be7c3c` · every number below is a local
measurement on this pod, reproduced in this run**

## Why this run went here

`classpick.py --leverage` prices `18_displacement` at **34.2 clean documents**, the largest single
step in the table. The Google census is only 58 of 213 documents on the current engine, so a fixer
that aims at the Google table aims at a corpus that is 73 % unmeasured. The LibreOffice table is
complete (`measure_gate.py`: **212/213 scored, 1 exempt, 0 blocking, READY**), so the population this
run worked is the one the proxy can actually see.

    documents failing 18_displacement in LibreOffice, current engine   22
    of those, failing NOTHING ELSE (one check from clean)               7

## The seven, with their measured per-run displacement

`dy.py` on the source PDF and the LibreOffice render of each document, current engine, rebuilt this
run. `tol` is the check's own `min(max(0.35*size,1.5),4.5)`.

| document | score | n_out/n | dy profile | mechanism |
|:--|:--|:--|:--|:--|
| `330_cad_drawing_sheet` | 46/47 | 32/40 | min −51.56, p25 −39.56, med −3.15 | a block **39.6 pt high**, plus one run at −51.6 |
| `363_warranty_card` | 41/42 | 7/30 | med −0.23, block at **+3.58…+3.72** | one block (7.0–7.5 pt text) sits **+3.7 pt low**, rest of page correct |
| `64_newspaper_uneven_columns_ad_boxes` | 41/42 | 14/77 | med +2.07, worst **+4.34** | whole page ~+2.0, body text 8.4 pt at **+4.1** |
| `71_invoice_space_aligned_no_rules` | 41/42 | 29/72 | table rows uniformly **+9.52**, `Total` **+24.42** | the table's top is placed **9.5 pt low**; its own pitch is exact |
| `balance-sheet-two-columns-of-figures` | 41/42 | **6/94** | everything ≤0.40 except the header row at **+3.69 / +3.63** | the **first row of a table** places its cell text 3.7 pt low; rows 2+ are correct |
| `newsletter-3col-header-footer` | 41/42 | 8/129 | med −0.24, one KPI band at **+6.46**, 13 pt at +4.46 | localised to one stat strip |
| `table-inside-two-column-page` | 46/47 | 44/64 | table cell text uniformly **−9.06** | a table block displaced **−9.1 pt as a whole** |

**Seven documents, seven mechanisms.** Three are whole-block placement offsets (330, 71, table-inside),
three are a single localised band (363, balance-sheet, newsletter), one is a page-wide small offset
(64). There is no single construct here. This is the same conclusion `18_displacement-ELEVEN-NON-RULED-
IS-THREE-FAULTS-CENSUS-2354-fixer.md` reached for the eleven, one population further on.

## The controlled experiment: `w:trHeight` is inert on a table's FIRST row, `w:before` is 1:1

`balance-sheet-two-columns-of-figures` is the crispest of the seven: **6 of 94 runs out**, all of them
the first table row, everything else within 0.40 pt. Its first row is emitted as

    <w:tr> <w:trPr><w:trHeight w:val="320" w:hRule="atLeast"/><w:cantSplit/></w:trPr>
      <w:tc>… <w:spacing w:before="248" w:after="0" w:line="10" w:lineRule="exact"/> …

Three variants, each rebuilt from the same .docx by editing that one attribute, each rendered through
LibreOffice and scored by `dy.py` against the same source PDF:

| variant | `w:trHeight` row 0 | row 0 `w:before` | header row dy | n_out / 94 | span |
|:--|--:|--:|--:|--:|--:|
| committed | 320 (16.00 pt) | 248 (12.40 pt) | **+3.69** | 6 | 4.18 |
| A | **240 (12.00 pt)** | 248 | **+3.69 — unchanged** | **89** | 6.96 |
| B | **200 (10.00 pt)** | 248 | **+3.69 — unchanged** | **89** | 6.96 |
| C | 320 | **174 (8.70 pt)** | **+0.40 max** | **0** | **0.89** |

Two things fall out, and both are worth more than the document:

1. **`w:trHeight` on the first row moves every row BELOW it and none of the text in it.** Variants A and
   B left the header row at +3.69 to the hundredth while taking the median of the whole page from
   +0.10 to −3.00. The first row's top is the table's top, so its own height cannot move its own text.
   **Any future attempt to fix a table's first row by adjusting `w:trHeight` is aimed at the wrong
   attribute** — and 89 of 94 runs go wrong when it is tried.
2. **`w:before` on a cell paragraph is laid 1:1.** The measured error is **+3.69 pt** and the
   correction that clears it is **−74 twips = −3.70 pt**. That is a dose–response of slope 1 on the
   first and only point, which is what makes it a usable term rather than a coincidence.

Variant C takes `balance-sheet-two-columns-of-figures` from **6 runs out to 0**, span 4.18 → 0.89, i.e.
41/42 → **42/42 in LibreOffice**. That is a measured clean document.

## What this run did NOT establish, and why it was not committed

**The 74 twips is measured, not derived.** The engine computes 248 tw where 174 is right, and the
source says why it should be 174:

    table's top rule            101.35 pt
    'EQUITY AND LIABILITIES'     109.61 pt   ->  8.26 pt below the table top
    engine wrote                248 tw = 12.40 pt   ->  over-computes by 4.14 pt

but the same arithmetic does **not** hold on row 2 of the same table, where the engine's value is
already right: `Equity share capital` sits 5.95 pt below its row top and the engine writes 8.85 pt
(+0.40 pt of error, inside tolerance). So the engine's constant is ~2.90 pt on row 2 and ~4.14 pt on
row 0, and **a rule that fits one fits neither.** A −74 twip edit guarded by "first row of a table"
would be a fudge: the corpus carries 100+ documents with tables and `regress.py --check` would be the
only thing standing between that fudge and a corpus-wide regression. It was not written.

**The first row of a table is not the only shape.** Variants A and B show the first row's height is
currently declared **2.0 pt short of the source** (16.00 declared against an 18.00 pt source band,
rules at 101.35 and 119.35). Whether the engine's `w:before` error on row 0 is a *consequence* of that
short row — the row model using a 16.0 pt band where the page drew 18.0 — is the single most likely
explanation and is **untested**. It is the next experiment, and it is one build and one LibreOffice
render, not a Google round trip: **declare the first row at the source band and see whether 248 becomes
correct on its own.** If it does, the construct is the row-height model and not the spacing at all, and
it generalises to 71 and table-inside-two-column-page, which are whole-block offsets of the same kind.

## What the proxy cannot decide here

`18_displacement` is the one check where the two renderers have already been shown to disagree on this
class: `31_times_body_arial_headings` is **42/42 in LibreOffice** (`benchmarks/gverify-lo/`) and
**41/42 in Google, `18_displacement` alone** (`benchmarks/gverify/`, engine `98be7c3c`). So a document
made clean in the proxy is not a document made clean in Google, and every fix above needs a round trip
before it counts. That is the correct order — the proxy finds the construct cheaply, Google certifies
it — but it means **this run's 42/42 is a lead, not a clean document.**

## Reproduction

    bash tools/p2w-bench/corpus-fetch.sh
    bash tools/p2w-bench/build-engine.sh
    cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
        ConvertOne /scratch/work/p2w/corpus/<doc>.pdf /scratch/work/p2w/out
    soffice --headless --convert-to pdf --outdir /tmp/lo /scratch/work/p2w/out/<doc>.docx
    python3 tools/p2w-bench/dy.py /scratch/work/p2w/corpus/<doc>.pdf /tmp/lo/<doc>.pdf

The variant harness is the 30-line `exp.py` described in the table above: unzip the .docx, rewrite
`w:trHeight` or `w:before` in row 0 of the first `<w:tbl>`, rezip, render, score. No engine source was
changed and nothing in `app/` is dirty.
