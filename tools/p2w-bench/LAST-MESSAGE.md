# P2W Fixer - Run Report

```

> No document moved this run. One attempt, recorded `lead`, with the measurement the class has
> never had - and one real bug in the pipeline's own accounting, fixed.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt, 0 kept |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **27** of the **123** re-measured on this engine - **67** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 67 outstanding |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## Why this class, and not the one the table suggested

I did not take the class the rotation offered. Two agents were deployed in the first ten minutes and
one of them recomputed, from `benchmarks/gverify/*.json` over the 190 documents that carry a check
list, out of 213, **which single failing check is the last blocker** on each document - the charter's own question,
"if this works, which documents become CLEAN?":

| check | documents where it is the SOLE failure |
|:--|--:|
| `18_displacement` | **13** |
| `60_text_column_right_edge` | 4 |
| `25_invisible_text` | 3 |
| `32_stroke_lines` | 2 |
| `59_shape_anchor` | 2 |
| every other check | 1 at most |

26 documents fail exactly one check and half of those fail only this one. So the class was taken on that
measurement, not on the class file's ordering. The second agent tested a recorded claim about
`04_chars_missing` ("fully explained by anchored text boxes on 9 documents") and **refuted it**: the
construct is real and reaches 54 of 65, but no document fails `04` alone, so fixing it cleans nothing
on its own.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 02:08 | **lead** | 0/13 | Four live Google round trips give the distances this class has never had: `med_dy` -2.8 / -3.0 / -6.7 / -13.0 pt, `worst_dy` 5.4 / 4.9 / 10.0 / 28.2, `med_dx` -0.2..+0.2, `bad_pages` [0] on all four. Run-by-run profiles show a lost table-gap step at every block top (-4.1 to -8.8 pt) exactly cancelled by a +0.75 pt/row ramp, so the page total is right and its distribution is wrong. |

## What is now known that was not known this morning

`verify_google.py` computes `med_dy`, `worst_dy`, `med_dx` for `18_displacement` and no stored record
carried one, so **twenty attempts at this class were steering blind** - a fixer could not tell a
document 0.5 pt out from one 50 pt out. Four documents measured live in Google this slot:

| document | `med_dy` | `worst_dy` | `med_dx` | bad pages |
|:--|--:|--:|--:|:--|
| `362_price_list_dense` | -2.8 | 5.4 | -0.2 | [0] |
| `bus-timetable-station-left-times-right` | -3.0 | 4.9 | +0.2 | [0] |
| `mobile-bill` | -6.7 | 10.0 | -0.1 | [0] |
| `72_bank_statement_no_rules_right_amounts` | -13.0 | 28.2 | -0.1 | [0] |

Three facts follow, and none were in the record. `med_dx` is zero on all four, so the class is a
**vertical** defect and any attempt that moves x is measuring the wrong axis. One page is out on every
document and it is page 0. And the residual spans a factor of 4.6, so no single constant serves both
ends - against a tolerance of 2.59 pt at 7.4 pt type, two documents are 0.4 pt outside it and one is
five times outside.

The shape is the part that matters. On `mobile-bill` the profile loses the gap at every table's block
top (-8.76, -4.19, -4.08 pt) and gains 0.75 pt back on every table row, so `dy` returns to zero at the
footer: 24 rows at 0.75 pt is 18 pt of ramp against 17.0 pt of step. **That is one defect with two
symptoms**, and it is why each half has been refuted alone - spending the spacer without removing the
row excess overflows the page, which is exactly what `DocxWriter`'s own guard records, and the row
declaration change alone leaves the step uncompensated. The untried move is the pair: deliver the gap
through the first-row cell `w:before` (measured 1:1 by Google, 66 probes, error 0.000000 pt) and reduce
`w:trHeight` by the same per-row amount, so the table's total height is unchanged. `362_price_list_dense`
has a ramp and no step, so it falsifies the pair on its own.

## The pipeline bug this run found and fixed

`round.py --claim-fixer` resets `RUN.json` for the new run, and that reset was being undone by the next
command in the documented setup order: `git checkout -- tools/p2w-bench/` restores `RUN.json` from HEAD,
which is the **previous** run's ledger. Measured on this slot - the claim printed "fixer claimed at
01:56" and `RUN.json` still read `started 00:56, attempts 2, agents ["18_dA-01","04_cB-01"]`. The report's
own header was written from those fields, and the release guard reads the same file to decide whether a
run deployed an agent and made an attempt. **Every run in the ledger has been mis-dated by one slot.**

A heartbeat now repairs it: a `RUN.json` that predates the claim cannot describe this run, so it is
re-opened at the claim's own timestamp. It fires once per claim (a `window_for_claim` stamp), so a claim
that moves forward does not wipe a live ledger. Verified both ways: it resets a stale ledger to the
claim time, and it leaves the ledger untouched when the claim has not changed.

## The gates are not what stopped this run

Checked before blaming the slot, as the brief asks: `regress.py --check` **PASS** (no document worse in
either format, table matches this engine) and `measure_gate.py` **READY** (212/212 scored, engine ==
tree). The pipeline is not blocked. What stopped the attempt from landing is arithmetic of the slot: the
pair above is an engine change, and `regress.py --check` refuses an engine commit until all 212
documents are re-measured - about forty minutes - which does not fit beside the measurement itself.
So the four documents are converted and staged in `/scratch/work/p2w/out`, and the next run pays for the
measurement, not the setup.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

Two deployed, both landed, both with a finding committed.

* **A - which single failing Google check, if fixed, makes the most documents CLEAN.** Answered:
  `18_displacement`, sole failure on 13 documents. `FINDINGS/18_displacement-SOLE-FAILURE-13-DOCS-0120-agentA.md`
* **B - is the `04_chars_missing` multiset fully explained by anchored text boxes on 9 documents.**
  Refuted as stated: 54 of 65, and no document fails `04` alone. `FINDINGS/04_chars_missing-TXBX-CLAIM-REFUTED-54of65-0120-agentB.md`

## Pending

The gate listed 90 items at claim and 80 at release. Eight were closed with evidence - six agents
deployed 730-884 minutes ago with no file in `FINDINGS/` naming their id (dead with their runs), and two
duplicate registrations this run made itself. The five `[ratchet]` items are very likely stale:
`benchmarks/STATE.json`, `RANKING.csv` and the engine last changed in the **same commit** `b7699196`,
and both gates pass on this tree - but stamping a ratchet nobody ran is a false ledger entry, so the
close is one corpus pass, not five stamps. That is written into the handoff.

## Timing

| | |
|:--|:--|
| Slot window | 02:08 → 02:09 · 1h 13m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 64 |
| Longest silence | **24.4 min** — from 00:56:37, after `pending.py: reading the pending gate` |
| Silences over 2 min | 8 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **3 min** | `#` |
| fix - diagnose and change the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **34 min** | `##########` |
| record - attempt, handoff, class rows | **4 min** | `#` |
| report - the report and the chain | **14 min** | `####` |
| other - not attributed to a tool | **13 min** | `####` |

## Next run

1. `18_displacement` is measured and staged. The pair is (first-row cell `w:before` carries the table
   gap) + (`w:trHeight` declared less by the same per-row amount). `362_price_list_dense` is the
   falsifier: it has a ramp and no step, so the row half must move it and the spacer half must not.
2. The five `[ratchet]` items close with **one** corpus pass, not five stamps. The evidence they are
   stale is in the handoff.
3. The remaining ~75 pending items are `[blocker]` rows that say "this needs a decision, not a patch".
   They are not a reason to sit still, and they are not yours.
