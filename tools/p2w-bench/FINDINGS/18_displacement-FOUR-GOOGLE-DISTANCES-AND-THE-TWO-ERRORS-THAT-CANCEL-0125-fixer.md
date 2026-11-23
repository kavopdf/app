# 18_displacement — four live Google measurements, and the two errors that cancel

**24 Nov 2026 · fixer slot 00:56 IST · engine built from HEAD (`b7699196`) in this sandbox · corpus
fetched whole (213/213) · every Google number below is a live round trip
(`ConvertOne` → Drive upload → copy-as-Google-Doc → export PDF → `verify_google.py --json`) · every
probe Doc and its uploaded .docx deleted after scoring; nothing left in the Drive root**

## Why these four documents

`18_displacement` is the largest clean-document step in the corpus and it is not close. Recomputed this
slot from `benchmarks/gverify/*.json` over the 190 documents that carry a check list
(`FINDINGS/18_displacement-SOLE-FAILURE-13-DOCS-0120-agentA.md`):

| check | documents where it is the SOLE failure |
|:--|--:|
| `18_displacement` | **13** |
| `60_text_column_right_edge` | 4 |
| `25_invisible_text` | 3 |
| `32_stroke_lines` | 2 |
| `59_shape_anchor` | 2 |
| every other check | ≤ 1 |

26 of 190 documents fail exactly one check, and half of them fail only this one. So the class was taken
on that measurement, not on the class table's ordering.

## The numbers

`verify_google.py` computes `med_dy`, `worst_dy`, `med_dx`, `bad_pages` for this check and has thrown
them away since 13 Nov. `gverify.py --collect` now stores them as `displacement` in the record
(`gverify.py:298-303`), but no record in `benchmarks/gverify/` carries one yet, so **the distance this
class is steering by did not exist for any of these documents.** Four were measured this slot:

| document | runs matched | `med_dy` | `worst_dy` | `med_dx` | bad pages | verify_google |
|:--|--:|--:|--:|--:|--:|:--|
| `mobile-bill` | 112 | **-6.7** | 10.0 | -0.1 | [0] | 41/42, 18 only |
| `72_bank_statement_no_rules_right_amounts` | 80 | **-13.0** | 28.2 | -0.1 | [0] | 41/42, 18 only |
| `362_price_list_dense` | 257 | **-2.8** | 5.4 | -0.2 | [0] | 41/42, 18 only |
| `bus-timetable-station-left-times-right` | 177 | **-3.0** | 4.9 | +0.2 | [0] | 41/42, 18 only |

Three things follow immediately, and none of them were in the record:

1. **`med_dx` is zero on all four (-0.2 to +0.2 pt).** The whole class, on these documents, is a
   VERTICAL defect. Any attempt that moves x is measuring the wrong axis.
2. **One page is out on every document, and it is page 0.** `bad_pages` is `[0]` four times over. These
   are not multi-page drift problems.
3. **The residual is not one magnitude.** `med_dy` runs from -2.8 to -13.0 pt, a factor of 4.6, and the
   tolerance at 7.4 pt type is `clamp(0.35*size, 1.5, 4.5)` = 2.59 pt. `362_price_list_dense` and
   `bus-timetable` are 0.4 pt outside it; `72_bank_statement` is 5x outside. A single constant cannot
   serve both ends, which is what `18_displacement-SEVEN-LO-ONE-CHECK-DOCS-ARE-SEVEN-MECHANISMS-0630`
   says and this table now shows as a distance.

## The shape, which is the part that matters

Each document was then paired run-by-run against its source (`/scratch/work/prof.py`, text+page match,
dy = render baseline - source baseline) and printed against source y:

    mobile-bill            dy  +0.09 at the title, -8.41 at the first body line, -0.60 at the footer
    362_price_list_dense   dy  +0.08 at the first row,  -4.02 at the last line, monotone
    bus-timetable          dy  +0.03 at the title, -4.05 at the table's first row, -0.46 at the footer
    72_bank_statement      med -13.0, worst 28.2

On `mobile-bill` the profile has two features and they are the whole story:

| where | dy before | dy after | change |
|:--|--:|--:|--:|
| after the title, before the first table's body | +0.35 | **-8.41** | **-8.76** |
| after `Table 1. Usage summary`, at the table's first row | -5.11 | **-9.30** | **-4.19** |
| after `Table 2. Bill detail`, at the table's first row | -4.05 | **-8.13** | **-4.08** |
| inside a table, per row (source pitch 18.40 pt) | | | **+0.75 per row** |
| at the footer | | | -0.60 |

So: **every table's gap is lost at the block top (a step down of 4-9 pt), and every table row is laid
0.75 pt too tall (a ramp back up).** Twenty-four rows at 0.75 pt is 18 pt of ramp against 17.0 pt of
step. The page's total height is therefore right — `dy` returns to 0 at the footer — and its
distribution is wrong.

**That is one defect with two symptoms, not two defects**, and it is why each half has been refuted
alone. Spending the spacer without removing the row excess overflows the page (that is exactly what
`DocxWriter.table()`'s guard at `:6074-6107` records: "spending the gap unguarded took mobile-bill and
insurance-policy-schedule from 46/47 on one page to 43/47 on two"). Removing the row excess without
spending the spacer leaves the step uncompensated. `mobile-bill` and `insurance-policy-schedule` are the
two documents the guard refuses, and they are refused precisely because their rows are carrying the
gap the spacer did not deliver.

The two constructs are the two already ranked in `18_displacement-CONSTRUCT-RANKING-agent-2310.md`:
#1 the table-gap spacer (`w:line` + `lineRule="exact"` on an `w:sz=2` mark, which Google charges
21.6 % of) and #2 the row height (`w:trHeight w:hRule="atLeast"` laid 0.75-1.15 pt taller than
declared, `18_displacement-ROW-PITCH-LAW-135800-relay.md`). **They have only ever been attempted
separately, and separately each one makes the page worse.**

## What this predicts, and what would prove it wrong

Prediction: a change that (a) delivers each table's gap through a property Google honours 1:1 — the
first-row cell `w:before`, measured at 66 probes with error 0.000000 pt in
`FINDINGS/18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md` — and (b) reduces the declared
`w:trHeight` by the same amount per row, so the table's total height is unchanged, moves `med_dy`
toward zero on all four without moving the page count.

What would prove it wrong: a document where the step and the ramp do not cancel — `362_price_list_dense`
has a monotone ramp with no step at all (its only step is +3.0 pt at one heading), so (b) alone must
move it and (a) must not touch it. If (b) alone leaves `362`'s `med_dy` where it is, the row-excess half
of the pair is not the mechanism and this note is wrong.

**Not measured this slot, and why:** the pair needs an engine change, and `regress.py --check` refuses
an engine commit until the whole corpus is re-measured (212 documents, ~40 min). The slot ran out of
room for the ratchet, not for the idea. The four documents above are converted and staged in
`/scratch/work/p2w/out` so the next run can measure the pair without paying the conversion again.

## Instrument status

`gverify.py --collect` already stores `displacement` (`:298-303`); no stored record has one. The `:20`
gverify cron re-measures up to 60 documents a run, so within two runs every scored document will carry
`med_dy`/`worst_dy`/`med_dx` and this class will no longer be steered blind. Nothing needed writing.
