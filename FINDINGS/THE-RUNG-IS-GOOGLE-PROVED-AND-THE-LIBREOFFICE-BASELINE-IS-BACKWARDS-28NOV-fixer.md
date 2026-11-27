# The rung is Google-proved. Reverting it costs both clean sheets. The 15 Nov baseline prefers the worse document.

**28 Nov 2026, fixer slot 04:00 IST.** Engine in the tree: `a05b20eb05fe0fc8`, byte-identical to HEAD at
the end of this run (`git status app/` clean). Class attempted: `63_table_rows` / `commit_gate`.
Nothing committed to the engine.

## The question this run was handed, and its answer

The 03:18 run left one measurement undone and said so plainly:

> "If the two documents stay clean with the rung off, the constant is pure cost and should go, and the
> gate unblocks by itself. If either one loses its clean sheet, the rung is right and the gate is
> charging a Google-proved construct to a renderer nobody opens."

**Measured, both directions, Google, this run. Neither document stays clean.**

| document | rung = 10 (HEAD) | rung = 0 (this run) |
|:--|:--|:--|
| `mobile-bill` | **47/47**, 0 failing | **46/47**, fails `18_displacement` |
| `electricity-bill` | **47/47**, 0 failing | **46/47**, fails `18_displacement` |

The rung = 10 side is the committed result on `a05b20eb` (27 Nov 14:45–14:46). The rung = 0 side is
this run: `ROW_RUNG_UNDER_TW = 0`, engine rebuilt, both documents converted with `ConvertOne`, uploaded
to the KavoPDF-Verify folder as Google Docs, exported as PDF by Drive, scored by `gverify.py --collect`.
Both probe documents were deleted afterwards; nothing is left in Drive.

**So `ROW_RUNG_UNDER_TW = 10` is right, and reverting it is a Google regression on 2 of 2 documents.**

## What that does to the plan the last two runs were building

The 03:18 run's arithmetic is sound and its conclusion is wrong. It is true that against the 15 Nov
LibreOffice baseline, `rung = 0` takes the refusal count from **84 to 57** - recomputed here from
`FINDINGS/RANKING-rung0-FULL-CORPUS-28NOV.csv`, 28 released, 2 cost. It is also true that the revert
reproduces digit for digit: eight documents screened on this pod on the current tree reproduced
`benchmarks/RANKING.csv` **8 of 8**, then on the rung = 0 build reproduced the rung0 CSV **7 of 8**
(the eighth, `77_arabic_rtl_document`, came back unchanged at 11.57 where the CSV records 11.89 - under
its baseline either way, so no verdict moves).

But the two documents the revert "releases" most spectacularly are `mobile-bill` 30.09 -> 1.55 and
`electricity-bill` 36.78 -> 1.33, and in Google those are the two documents the revert **breaks**.

| | LibreOffice share5 | Google |
|:--|:--|:--|
| rung = 10 | 30.09 / 36.78 (worse than baseline) | **47/47 / 47/47** |
| rung = 0 | 1.55 / 1.33 (better than baseline) | **46/47 / 46/47** |

**The 15 Nov LibreOffice baseline is not merely noisy here. On the two documents where it can be
cross-checked against Google, it prefers the version Google marks down.** A plan to "get `main` back
under the bar" by landing the rung revert would have made 28 documents look better in a renderer the
user does not open, and would have taken two documents the user opens from clean to failing.

That is the third non-negotiable doing its job - `regress.py --check` refused the revert - and it is
also why the gate cannot be re-based to the current engine before this was measured.

## The 84, decomposed, because the shape decides what to do next

`share5` is the share of source ink more than 5 px from any render ink; larger is worse; the charter's
own bar for DONE is `share5 <= 1.0` (99 %). Compared with `regress.py`'s rule, absolute, tol 1e-9.

| group | documents | what it means |
|:--|--:|:--|
| **A. Google-clean today** on the engine in the tree | **10** | passes every applicable Google check (47/47 or 42/42), refused anyway |
| **B. baseline row is internally impossible** | **4** | baseline `share5 = 0.00` while its own `max_pt > 2.4` - unreachable by construction |
| **C. already at the charter's 99 % bar** | **13** | current `share5 <= 1.0`, refused by a gate that never reads the bar |
| **union A ∪ B ∪ C** | **23** | not damage the charter recognises |
| **D. a genuine loss** | **61** | worth arguing about |

Group A, all measured on `a05b20eb` between 11:56 and 14:46 on 27 Nov:

| document | baseline | today | Google |
|:--|--:|--:|:--|
| `electricity-bill` | 16.24 | 36.78 | **47/47** |
| `mobile-bill` | 18.48 | 30.09 | **47/47** |
| `insurance-policy-schedule` | 13.29 | 22.66 | **47/47** |
| `73_marksheet_subject_marks_grade` | 0.00 | 7.95 | **42/42** |
| `33_sans_nondefault_body` | 4.49 | 10.73 | **42/42** |
| `36_embedded_subset_font` | 0.00 | 4.91 | **42/42** |
| `16_right_aligned_amounts_txtpos` | 0.00 | 3.83 | **42/42** |
| `41_coloured_headings_white_bg` | 0.00 | 2.16 | **42/42** |
| `29_dot_leaders_txtpos` | 0.00 | 0.89 | **42/42** |
| `362_price_list_dense` | 0.03 | 0.82 | **42/42** |

The charter defines done as "every Google check that applies to it passes". These ten meet it and are
refused. `regress.py` already grants the principle in one direction - a LibreOffice regression is
ALLOWED when Google improved on the same document - and that branch cannot fire here, because these
documents did not *improve* in Google, they were already clean. The gate has no way to say "this
document is done; a proxy score cannot make it undone."

Group B, all four inside the 84: `56_table_indented_from_margin`, `02_stamp_rotated_15deg_upleft`,
`323_credit_card_statement`, `403_crossword_puzzle`. A baseline of `0.00` is two-decimal rounding of a
handful of pixels - its own `max_pt` is 2.88-3.36 - so any measurement at all reads as a regression.

## What the next run should do, in order

1. **Do not land the rung revert.** It is refuted in Google on 2 of 2 documents. The 28 it "releases"
   are a proxy artifact; the two that can be checked say the proxy is pointing the wrong way.
2. **Do not re-base the gate to the current engine to make it pass.** That would ratify 61 genuine
   losses on the strength of a yardstick that has just been shown to prefer the worse document.
3. The 23 in A ∪ B ∪ C are the only part of the 84 that needs no engine change at all. Ten of them
   are at the charter's own definition of done. If the gate is to keep refusing them, the reason has
   to be written down somewhere, because it is not the charter's reason - and the two-branch fix
   (a document at the 99 % bar, and a document that passes every Google check on the current engine)
   is a gate change that releases exactly those documents and nothing else.
4. The 61 genuine losses are a fixer's class table, and the largest single one is `18_displacement`:
   `FINDINGS/18-DISPLACEMENT-PRIZE-CENSUS-28NOV.md` counts 18 documents whose only failing Google
   check it is.

**The gate is still unsatisfiable at HEAD** - `measure_gate.py` prints READY, 213/213 scored, and
`regress.py --check` still exits 1 with 84 refusals - so no engine change can be recorded as kept until
it is. That is the finding, not an excuse, and the two measurements above are what the next run needs
in order not to walk into the same wall from the other side.
