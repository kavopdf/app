# The cell-before shortfall, and the gate that cannot see it

**Run:** 27 Nov 2026, fixer slot 18:00 IST (claimed 12:30 UTC).
**Class:** `18_displacement` (highest leverage in the table: 52.6 clean documents).
**Outcome:** **lead**, not kept. The engine change is real and reaches the output; the
instrument that would have certified it is blind to it. Patch written, not landed:
`tools/p2w-bench/PATCHES/18-small-dy-cellbefore.patch`.

---

## 1. What was believed

`18_displacement` is worth 52.6 clean documents and 23 documents fail it and nothing else.
A sub-agent's static analysis of the class proposed that a whole sub-population of it is one
arithmetic slip in one branch of `DocxWriter`, and claimed a LibreOffice measurement of
**+4 documents flipping FAIL -> PASS**.

## 2. What was measured

### 2a. The construct is real, and it reaches the output

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, the "raise a slightly-short cell"
branch. The file's own comment eleven lines above states the law:

    before + LINE_BASE * box = LINE_BASE * rowLine

The branch immediately above (`cellBeforeTw = Math.max(0, Math.round(LINE_BASE * (rowLineTw - cellBoxTw)))`)
obeys it. The raise branch below it did not:

    -    cellBeforeTw = rowHeightTw - cellBoxTw;
    +    cellBeforeTw = Math.max(0, Math.round(LINE_BASE * (rowHeightTw - cellBoxTw)));

So the baseline it places sits `(1 - LINE_BASE) = 0.2` of the shortfall **below** the row's foot.

**Measured on the emitted XML, pre-patch vs post-patch, same corpus PDF, engine rebuilt either way:**

| document | attribute | pre | post | move |
|---|---|---|---|---|
| `74_balance_sheet_indented_subitems` | `w:before` (tw) | 170 | 136 | -34 tw = **-1.70 pt** |
| `bus-timetable-station-left-times-right` | `w:before` (tw) | 317 | 254 | -63 tw = **-3.15 pt** |

`w:line` is unchanged (170 and 11 tw), which is the point: only the space above the cell line
moved. This is the arithmetic the sub-agent predicted and it reproduces exactly.

### 2b. LibreOffice does not move. At all.

`screen.py --docs` on **10 documents** (the 4 the sub-agent named as flips, plus 6 controls
chosen because they are the documents the raise branch's scope was written for or against:
`362_price_list_dense`, `402_calendar_month_grid`, `16_right_aligned_amounts_txtpos`,
`320_balance_sheet_statutory`, `balance-sheet-two-columns-of-figures`, `71_invoice_space_aligned_no_rules`).
Fresh conversion, engine-keyed cache discarded on the engine change, all 10 measured:

    share5     identical on 10 of 10
    median_pt  identical on 10 of 10
    p90_pt     identical on 10 of 10

Not "small improvement". **Bit-identical scores.** So the sub-agent's claim of a measured
LibreOffice flip is **refuted by the repository's own instrument on the same documents**.

### 2c. Why 2a and 2b are both true

The largest move available here is 3.15 pt = 6.6 px at 150 DPI, and the smallest is 1.70 pt =
3.5 px. `share5` counts ink more than **5 px** from where the page drew it. A 3.5 px shift is
inside the threshold by construction, and a 6.6 px shift on one line of a page full of ink moves
the *share* by less than the 0.5-point bar `screen.py` calls a move.

`median_pt` is a different question and it also did not move, which means LibreOffice is not
laying the cell text out from `w:before` at all — it is placing the cell line by the table row
geometry. So on this construct **LibreOffice is not a proxy for Google; it is silent.** That is
the same shape as the 25 Nov anchored-box finding and it is worth more than the patch.

## 3. What is now true

1. The branch at `DocxWriter.java` ~:7013 is arithmetically inconsistent with the branch above it
   and with the law written in the file. Measured, in twips, in the emitted XML.
2. **`share5` and `median_pt` cannot see a shift of 3.5 px or less, and LibreOffice does not
   honour `w:before` inside a table cell.** Therefore `regress.py --check` cannot certify *or*
   refute a change of this size or this construct. A run that asks the gate "is this better?"
   on a sub-4px cell shift is asking a question the gate was never built to answer — it will
   answer "no document worse", which is true, and mean nothing.
3. Consequence for the ledger: **the `18_displacement` small-dy population cannot be worked from
   the LibreOffice loop at all.** It needs a Google render per candidate document, which is
   4 Drive calls per document, and a slot that budgets for it.

## 4. What would prove this wrong

- A Google render of `74_balance_sheet_indented_subitems` at HEAD and at this patch, with
  `18_displacement`'s dy read off the Google export. If the patched build's dy(origin) is ~0 and
  HEAD's is ~+1.7 pt, the patch is a real fix and the LibreOffice silence in 2b is the proxy
  failure, not a refutation. **This is the one measurement that settles it and it was not taken
  in this slot.**
- Conversely, if Google also ignores `w:before` inside a cell, the patch is inert and the class's
  small-dy population lives somewhere else entirely.
- A 19th or later document in the corpus whose `document.xml` changes but which is not in the
  18-document population the sub-agent counted (that would mean the branch's scope is wider than
  the census).

## 5. Why it is a lead and not a kept fix

The commit gate refuses an engine change whose table was not re-measured on the new engine, and
correctly so. Re-measuring 212 documents with `benchmarks/p2w.py` is ~12 s per document, ~42
minutes, and this slot had ~20 left after the corpus conversion. Recording the change as kept
without that measurement is the 23 Nov mistake. So the patch is written to
`PATCHES/18-small-dy-cellbefore.patch` and the measurement is what the next run starts from.

**Next run, first thing:** put the patch back, convert `74_balance_sheet_indented_subitems`,
and take the Google render. If it flips, the corpus pass is worth its 42 minutes.

---

## 6. Second measurement, free: the txt "regression" is a denominator, not a document

`gverify.py --plan` re-measured the whole `.txt` half on this run (214 scored, 205 clean, 9 failing,
95.8%) and the ratchet said **"a document got worse"**. It did not. Diffed row by row against
`HEAD:tools/p2w-bench/txt/RANKING-TXT.csv`:

    documents added   : Prakashan_Print_Fidelity_Handbook
    documents removed : none
    documents whose failed_ids changed : none

The corpus grew from 213 to 214. `205/213 = 96.2 %` became `205/214 = 95.8 %` and the failing count
went 8 -> 9 without a single document changing. The new one,
`Prakashan_Print_Fidelity_Handbook`, is 11 applicable / 7 passed / 4 failed / 1 abstained and fails
`t01_word_accuracy t03_symbols t07_symbol_counts t12_word_invention`.

**So the txt ratchet cannot tell a new document from a worse one**, and a run that reads its refusal
as "something regressed" will hunt a regression that does not exist. The correct reading is: one new
document is open on four txt checks, and the txt population is now 214.
