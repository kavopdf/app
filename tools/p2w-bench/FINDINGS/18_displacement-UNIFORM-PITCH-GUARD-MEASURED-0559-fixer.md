# The uniform-pitch guard, built and measured: the target itself is a proxy regression

**Measured 24 Nov 2026, fixer slot 05:59.** This is the follow-up the 04:52 finding asked for.
It builds the pre-pass, answers the guard question with a corpus-wide census, and measures the
result. **Conclusion: the fix cannot land under the current bar, and no guard can change that** -
the document the fix exists for regresses in the LibreOffice proxy by +0.01 share@5, and the bar
for "not worse" is zero movement.

---

## 1. The patch, built

`FINDINGS/18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch` applies to
`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` and compiles (javac 17, 35 s).

A true pre-pass over the rows is **not possible**: `rowHeightTw` depends on `recutTopPt`, which is
a running sum of the row heights above it and feeds `cellParasTw(...)`, so a pre-pass would have
to duplicate the whole row body and re-derive a recurrence from heights it has not written. The
patch therefore buffers: each row's `w:trHeight` value and its offset in the table's `StringBuilder`
are recorded as the row is emitted, and after the last row the digits are rewritten **back to
front**, so no recorded offset shifts.

Nothing but the digits changes. `rowHeightTw` itself is untouched, so `writtenRowsTw`, the flow
charge, `lastRowHeightTw` and the anchor after the table are bit-identical. `hRule` stays
`"atLeast"`. The `hRule="exact"` path at line 2257 is not touched.

The snap is the finding's, with one deliberate departure:

```
cumTw += rowHeightTw[r];
outTw  = (r == last) ? totalInTw - doneTw : 15 * Math.round(cumTw / 15.0f) - doneTw;
```

The last row is written as the remainder, **so `sum(out) == sum(in)` exactly**. The 04:52 finding's
array sums to 4950 from a source that sums to 4944; that +6 twips would have moved the table's own
bottom edge. This version does not, and the last row (174 twips) absorbs the remainder instead.

## 2. It reproduces the measured Google-winning distribution

`362_price_list_dense`, converted on the built engine, `.docx` `word/document.xml` read back:

| | `w:trHeight` (atLeast) | n | sum |
|---|---|---:|---:|
| before | `[240, 168 x 28]` | 29 | 4944 |
| after | `[240, 165, 165, 180, 165, 165, 165, 165, 180, ... 174]` | 29 | **4944** |

That is the finding's `[240, 165, 165, 180, ...]` - the distribution that measured **42/42 in
Google** - with a total that does not move. `electricity-bill` and `330_cad_drawing_sheet` were
converted the same way and compared part by part.

## 3. The guard question, answered with a census

The 04:52 finding proposed "the table's row heights are uniform" and left it unmeasured. Built as a
pre-pass it needs a whole-row census anyway, so the census was run directly: **211 baseline `.docx`
converted (3.5 s each, all 211), every `<w:tbl>`'s `atLeast` heights read back**, and the guard
evaluated on the values the engine really emits.

| guard | rule | documents it fires on |
|---|---|---:|
| **A** (shipped in the patch) | one fractional height repeating >= 3 times; whole-pixel rows anywhere | **85 of 211** |
| **B** (line grid) | as A, plus every whole-pixel row is a contiguous header or footer | **54 of 211** |
| old, refuted | `ruleTwHere == 0` | 17 documents worse |

The literal "all rows equal" test the 04:52 finding proposed **skips the target**: `362` is a 240
twip header over 28 rows of 168. Guard A was written for that reason.

Guard B exists because of `electricity-bill`, whose rows are `360, 360, 380, 360, 380, ...` - one
fractional height (380) repeating seven times, so guard A fires on it, but it is not a pitch: two
heights interleaved. Guard B excludes it. `330_cad_drawing_sheet` (`240, 260, 220, 240, 260, 300
...`, two fractional heights) is excluded by both, and its `.docx` is **byte-identical** between
the two engines - so the 04:52 cost table's `330_cad 4.91 -> 5.22` does not exist under either
guard.

## 4. The measurement that decides it

LibreOffice proxy, `p2w.py`'s own instrument (`measure_doc`), same engine tree, same corpus,
run twice per document to prove determinism:

| document | guard | share@5 before | share@5 after | verdict |
|---|:--:|---:|---:|---|
| `362_price_list_dense` | A, B | 0.03 | **0.04** | **worse** |
| `electricity-bill` | A only | 1.33 | **1.40** | **worse** |
| `16_right_aligned_amounts_txtpos` | A, B | 0.00 | 0.00 | unchanged |
| `351_omr_answer_sheet` | A, B | 0.00 | 0.00 | unchanged |
| `341_shipping_manifest` | A, B | 0.00 | 0.00 | unchanged |
| `390_wide_data_appendix` | A, B | 0.03 | 0.03 | unchanged |
| `320_balance_sheet_statutory` | A, B | 0.00 | 0.00 | unchanged |
| `323_credit_card_statement` | A, B | 0.00 | 0.00 | unchanged |
| `375_attendance_register` | A, B | 0.01 | 0.01 | unchanged |
| `324_loan_amortisation_schedule` (6 tables, 246 rows) | A, B | 0.00 | 0.00 | unchanged |
| `03_stamp_vertical_90deg` | A, B | 16.98 | **17.20** | **worse** |
| `68_journal_wide_table_spanning` | A, B | 12.09 | **12.34** | **worse** |

**Twelve documents measured, eight unchanged at share@5 and four worse.** The largest table in the
corpus - 246 rows across six tables - does not move at all, so the cost does not grow with the row
count, which is exactly what a cumulative snap is for. The four that move are
the target itself (+0.01) and three documents that are already displaced by 12-17 share points; the
seven that do not move are the ones that are clean. A 12-document sample is not the corpus, and it
is not offered as one - it is the reason the next step is a decision about the bar and not another
guard.

Repeated: `362` reads 0.03 on the baseline engine and 0.04 on the patched one, **both times**. It
is not noise. `max_pt` goes 3.36 -> 3.84 while `p90_pt` goes 1.92 -> 1.44 and `share@3` goes
2.03 -> 1.99 - the shape of a redistribution: most rows land closer, the worst one lands further.

**`362_price_list_dense` is the one document this whole class exists for, and it is a proxy
regression under both guards.** The largest cost found anywhere is +0.25 share@5, on a document
whose share@5 is 12.09. `regress.py` refuses any rise in share@5, so the patch is refused
by the gate on its own target, before any other document is considered.

## 5. Why no guard can fix this

The redistribution is forced. Google truncates each row to a whole pixel, so the only row heights
that render correctly are whole pixels, and the only way to hold the cumulative position is to
mix 11 px and 12 px rows - `168` twips can never be kept. On a period-5 cycle the emitted heights
are `165, 165, 165, 165, 180`, which is the minimum possible movement: four rows 0.15 pt short and
one 0.6 pt long. LibreOffice places `168` correctly, so **every** such row is a loss there. The
cost is not a guard problem; it is the definition of the fix.

That is the second question the 04:52 finding raised, and this run answers it with a number
instead of an argument: **the proxy and Google disagree on this construct, and the gate listens to
the proxy.** Either `18_displacement` tolerates one pixel of accumulated quantisation per page, or
every table document with a fractional row pitch is permanently unfixable and the class should be
closed rather than worked again.

## 6. What the next run should do - and not do

1. **Do not rebuild this patch.** It is in `18_displacement-UNIFORM-PITCH-SNAP-0559-fixer.patch`,
   it compiles, and it produces the Google-winning distribution with the total preserved.
2. **Do not look for a better guard.** Section 5 says the target itself moves; a guard can only
   shrink the cost, never reach zero.
3. **The decision to make is about the bar.** Concretely: `regress.py` compares `share5` at two
   decimals, and 0.03 -> 0.04 on a document whose `max_pt` is 3.36 pt is a change in a statistic
   whose own tolerance elsewhere is `clamp(0.35*size, 1.5, 4.5)` pt. A waiver for a **measured
   Google gain with a bounded proxy cost** - or a `share5` floor below which a movement is not a
   regression - unblocks this class and 53 others' worth of table documents with it.
4. If the decision is "no waiver", close `18_displacement` and spend the slot on a class whose
   renderers agree. Working it again will produce this same finding.
