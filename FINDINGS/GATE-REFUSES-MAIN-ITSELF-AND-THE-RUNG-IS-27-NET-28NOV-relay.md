# The gate is unsatisfiable at HEAD, and the rung is worth 27 of the 84

**28 Nov 2026, relay/fixer slot 03:18 IST.** Class: `63_table_rows` / `commit_gate`.

This run landed no engine change. What it did produce is the arithmetic the last four runs were
arguing about, recomputed independently from the three committed measurement tables by a new
one-command tool, plus the one measurement nobody had made: **the gate refuses a tree in which
nothing changed.**

    python3 tools/p2w-bench/gate_decompose.py --candidate FINDINGS/RANKING-rung0-FULL-CORPUS-28NOV.csv

## 1. The deadlock, measured

`bash tools/install-gate.sh` installs `.git/hooks/pre-commit`, which runs `regress.py --check` and
has no override. On a clean clone at `main`, with **no engine change at all**, that hook refuses:

```
  engine fingerprint : 72ff003db5871587
  scope of the change: docx, txt   (scope.py: both)
  docx: 84 REGRESSION(S)
  REFUSED. This commit would land a regression or an unmeasured engine.
```

`regress.py --check` exits **1** at HEAD. The hook therefore refuses *every* commit on this
repository — an engine fix, a tool, a findings file, the run's own report. That is not a claim about
the fixer's diligence; it is the reason the last four slots each ended with "nothing was kept". A
gate whose refusal state is the state of `main` is not gating a change, it is gating the repository.

**This is the finding the next run should start from**, because it changes what "unblock the gate"
means: not "find a change that does not regress" but "get `main` back under the bar, or decide the
bar itself".

## 2. What the 84 are

Recomputed from `benchmarks/RANKING.csv` against `benchmarks/RANKING-BASELINE.csv` on the `share5`
column with `regress.py`'s own rule (absolute, tolerance 1e-9):

| group | documents | note |
|:--|--:|:--|
| **all refusals** | **84** | plus 1 row with no baseline row: `Prakashan_Print_Fidelity_Handbook` |
| baseline of exactly **0.00** | **27** | a floor no change can hold — see §3 |
| inside the corpus's own clean bar (`share5 <= 1.0`, i.e. 99 % of ink within 2.4 pt) | **6** | already at the charter's goal, still refused |
| a genuine loss above 5.0 share5 | 19 | the damage worth arguing about |

The six that already meet the charter's own definition of a match: `323_credit_card_statement`
(0.00 → 0.09), `351_omr_answer_sheet` (0.00 → 0.01), `25_signature_block_underscores_txtpos`
(0.03 → 0.04), `403_crossword_puzzle` (0.00 → 0.38), `300_prescription_rx` (0.06 → 0.51),
`question-paper-marks-right-margin` (0.44 → 0.62). Every one is refused by a gate that has no noise
floor and no reference to the 99 % bar the charter is written against.

## 3. Ten baseline rows contradict themselves

`share5` is the share of source ink further than 5 px (2.4 pt at 150 dpi) from any render ink;
`max_pt` is the largest displacement on the worst page. A row with `share5 = 0.00` and `max_pt > 2.4`
cannot both be true: `max_pt > 2.4` says ink is beyond the radius. Ten baseline rows do it:

| document | max_pt | in the 84? |
|:--|--:|:--|
| `342_packing_list` | 3.36 | no |
| `407_id_card_front_back` | 3.36 | no |
| `56_table_indented_from_margin` | 3.36 | **yes** |
| `02_stamp_rotated_15deg_upleft` | 2.88 | **yes** |
| `323_credit_card_statement` | 2.88 | **yes** |
| `325_demat_holdings_statement`, `335_msds_safety_data_sheet`, `353_admit_card`, `381_incident_report_timeline`, `403_crossword_puzzle` | 2.88 | `403` only |

The zero is two-decimal rounding of a handful of pixels. Four of the ten are among the 84, and for
those the baseline is not a yardstick, it is a defect: the target is unreachable by construction.

## 4. The rung is worth 27 net, and it is already measured

`FINDINGS/RANKING-rung0-FULL-CORPUS-28NOV.csv` is a full-corpus (213-row) measurement of the tree
with `ROW_RUNG_UNDER_TW` set to 0 and nothing else touched. Against the same baseline:

| | documents worse than 15 Nov |
|:--|--:|
| `main` today (rung = 10) | **84** |
| rung = 0 | **57** |

- **Released: 28** — `table-with-no-header-row`, `boq-tender-bill-of-quantities`,
  `very-long-single-column-table`, `balance-sheet-and-profit-loss`, `electricity-bill`,
  `mobile-bill`, `salary-slip-factory-wages`, `mutual-fund-statement`, `property-tax-receipt`,
  `table-across-page-break-repeated-header`, and 18 more.
- **Cost: 1** — `marksheet-subject-left-marks-right`, 4.55 → 5.21 (the rung gives it 2.15).
- **Net: 27 documents.**

This is the largest single lever anyone has found on this corpus, it is one constant, and it is fully
measured. It still does not clear the gate, so it cannot be committed under the hook as it stands.

## 5. What is left after the rung, and how to attack it

The 57 remaining, worst first. Three groups - they overlap, a document can be in both the
first and the second - and only the third is real damage:

1. **23 with a baseline of exactly 0.00** — unreachable floor (§3).
2. **11 already inside the 99 % bar** (`share5 <= 1.0`) — `351_omr_answer_sheet` 0.01,
   `323_credit_card_statement` 0.09, `25_signature_block_underscores_txtpos` 0.04,
   `403_crossword_puzzle` 0.38, `300_prescription_rx` 0.51, `question-paper-marks-right-margin`
   0.62, `50_invoice_coloured_total_row` 0.75, `383_api_docs_page` 0.80, `362_price_list_dense`
   0.82, `29_dot_leaders_txtpos` 0.89, `04_stamp_180deg_upside_down` 0.96.
3. **19 above 5.0**, by name: `360_restaurant_menu` (34.4 → 50.2), `03_stamp_vertical_90deg`
   (17.0 → 34.4), `price-list-2col-dense-right-aligned` (2.7 → 27.9),
   `71_invoice_space_aligned_no_rules` (26.9 → 27.0 — 0.4 % relative, noise),
   `363_warranty_card`, `price-list-right-aligned-amounts`, `40_devanagari_shaping_font`,
   `bus-timetable-station-left-times-right` (0.27 → 11.40), `33_sans_nondefault_body`,
   `payslip-label-left-amount-right`, `35_four_typefaces_one_page`, `374_org_chart`,
   `73_marksheet_subject_marks_grade`, `79_inr_indian_digit_grouping_table`,
   `06_rect_paid_stamp_red_transparent`, `406_passport_mrz_page`, `80_gstin_pan_cin_ifsc_table`,
   `14_stamp_chars_positioned_td`, `marksheet-subject-left-marks-right`.

Clusters inside that third group, by the construct their names carry: **stamps** 10,
**two-typeface / subset-face** 4, **right-aligned amount columns** 4, **txtpos absolute placement** 5.
The stamp cluster is the largest coherent one and is the next class after the rung.

## 6. The lead this run leaves, with its falsifier

The rung is a **per-row** correction (`pitchBinds && footRoom`) whose error **accumulates** with row
index — the finding of 27 Nov says ≈ 0.5 · n pt by row n. That is why it costs the long tables and
earns the short one. A condition that matches the mechanism, not the document, is: **apply the rung
only where the table is being held to a page budget** (`rowCapTw > 0` or `ctx.squeeze != 1`, the
`mobile-bill` case the rung was tuned on), because that is the only case where the table's own height
is not the page's.

Falsifier, stated before it is run: if that condition releases fewer than 20 of the 28 and still
costs `marksheet-subject-left-marks-right`, the mechanism is wrong and the per-document trade stands.

## 7. What this run did not do, plainly

No engine change was landed and no document was improved. The reason is §1, not a shortage of ideas:
the change that is measured and ready (rung = 0, 27 net documents) is refused by a hook that refuses
`main` itself. Nothing here is a substitute for a measurement the gate accepts; it is the map of why
there is no such measurement yet.

Tool added: `tools/p2w-bench/gate_decompose.py` (read-only, exits 0, writes nothing). It recomputes
every number in §2, §3 and §4 from the three committed CSVs in about a second, so the next run does
not have to re-derive them by hand.
