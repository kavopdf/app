# 18_displacement — the check finally prints a DISTANCE, and the row-excess quantum is a RULED-table quantum

**23 Nov 2026 · fixer slot 23:58 → · engine reverted to HEAD after measurement · every Google number
below is a live round trip this slot (ConvertOne → Drive create-as-Google-Doc → export PDF →
`verify_google.py`)** · 2 probe Docs created in `KavoPDF-Verify`, never in the Drive root.

## Why this run started here

`FINDINGS/18_displacement-PARTIAL-SPEND-IS-INERT-AND-COSTS-68-JOURNAL-2315-fixer.md` ended with one
sentence that outranks every other lead in the class:

> `18_displacement` prints a count, not a distance … **Publishing those three numbers is the
> highest-value change available to this class**, and it is an instrument change, not an engine
> change, so it is not blocked by the corpus measure.

`verify_google.py` has computed `med_dy`, `worst_dy` and `med_dx` since the check was rewritten
(`:5653-5655`) and then thrown them away: `checks["18_displacement"] = (0, len(bad_pages), not
bad_pages)`. Every attempt at this class for two weeks has therefore been steering blind — unable to
tell a document 0.5 pt out from one 50 pt out, or a constant offset from an accumulating drift.

## 1 — The instrument (KEPT, committed)

`verify_google.py`: `18_displacement` now carries a fourth element — the detail dict
`{med_dy, worst_dy, med_dx, bad_pages, runs_matched}`. The fourth element is the file's own existing
reported-not-scored channel (it is what `26_text_overlap` uses), so **no check's pass/fail can move**.
`gverify.py --collect` stores it as `displacement` in `gverify/<name>.json`.

Two independent confirmations that the instrument is neutral and correct:

| check | result |
|:--|:--|
| a document compared against **itself** (`72_bank_statement…`, 42/42 expected) | **42/42 PASS**, `med_dy 0.0`, `worst_dy 0.0`, 80 runs matched — the detail cannot invent a fault |
| the live Google render of `72_bank_statement…` | instrument `med_dy **-13.0**`; an **independent** PyMuPDF baseline match over the same two PDFs (not the edited tool) reads `med_dy **-12.9**` — agree to 0.1 pt |

## 2 — The first document the instrument was pointed at

`72_bank_statement_no_rules_right_amounts` — one of the 13 that fail `18_displacement` and nothing
else. Scored **41/42**, failing only `18_displacement`, exactly as the committed table says, so the
engine in the tree reproduces the stored result.

Per-line dy, ordered down the page (source y, dy in pt):

| block | dy |
|:--|:--|
| header block, 5 lines, y 64.5 → 137.9 | **+0.2 … +0.3** — placed exactly |
| table header row, y 169.8 | **-13.0** — a 13.3 pt step in one boundary |
| 17 body rows, y 187.9 → 459.9 | -15.1 → -11.1 — recovering **+0.25 pt per row** |
| footer block, y 488.7 → 807.6 | -9.5 … -9.4 |

So the fault is **two** things, not one: a **13.3 pt step at the table's top**, then a **0.25 pt/row
pitch excess** that partially pays it back. The census's #1 construct is confirmed by dose: the docx
carries exactly one spacer, `w:line="366"` (18.30 pt) `w:before="0"`, and Google charges a
`w:line`-exact box on an `sz=2` mark `2.5873*max(L/240,0.06)` = 3.94 pt — a **14.36 pt shortfall**
predicted, **13.3 pt** measured.

## 3 — Why the engine already knew this and refused to act

`DocxWriter.java:6085-6106` splits the spacer (hairline in `w:line`, the rest in `w:before`, which
Google honours 1:1) but only **where the page has room**, and the room test charges
`rowExcessTw = 15 * pageRowCount`. Traced on `-Dp2w.debugSpacer` (added this run):

```
72_bank_statement…   spacerTw=366 slackTw=558 roomWantTw=346 rowExcessTw=270 rows=18  spendable=false
```

The page has 558 twips of slack and the guard asks 616 — **refused by 58 twips (2.9 pt)**, and a
refused spend is not neutral: it leaves the table the whole 18.3 pt gap too high, which is the 13.3 pt
step.

**The quantum is wrong for this table.** 0.75 pt/row is the same `TABLE_BORDER_TW` the file subtracts
from a *ruled* row — and `:6245` says it in as many words: *"An unruled table draws no rule and keeps
its full pitch."* `72_bank_statement` has **no rules**. Its measured growth is **0.25 pt/row**, three
times smaller than the 0.75 pt the guard charged it.

## 4 — The change, and what it did in Google (LEAD, engine reverted)

`rowExcessTw = (t.ruled ? 15 : 5) * pageRowCount` — 5 twips is the measured 0.25 pt/row. **A ruled
table is untouched**, so every document the guard already spent or refused for a ruled table is
byte-identical.

| | before (HEAD) | after (patched) |
|:--|--:|--:|
| guard decision on `72_bank_statement…` | refused (616 > 558) | **spent** (436 ≤ 558) |
| Google `med_dy` | **-13.0** | **+1.1** |
| Google `worst_dy` | **28.2** | **4.8** |
| Google score | 41/42 | **41/42** — still `18_displacement` |
| page count | 1 | 1 |

The 13.3 pt step is **gone** (med_dy -13.0 → +1.1). What is left is the other half of the fault: 7 runs
at **+3.2 … +4.9 pt** against a tolerance of 2.8–3.0, and their dy grows monotonically down the page —
18 rows × 0.25 pt = 4.5 pt, the pitch excess the instrument measured in §2. So the change fixes the
step and leaves the drift, which is why the check still reads FAIL.

Only `72_bank_statement` flips in the spend decision; `two-tables-stacked-with-no-gap` and
`table-with-no-header-row` are **ruled** (`t.ruled` true, traced: rowExcessTw 195 and 390) and are
correctly untouched. `68_journal_wide_table_spanning` also reads unruled now (rowExcessTw 35) but its
144 pt spacer needs 2,860 twips of 568 and stays refused.

**Engine reverted.** `regress.py --check` refuses any engine change until the corpus is re-measured on
it (`ENGINE CHANGED … An unmeasured change is not a pass`), and a corpus pass is ~40 minutes this run
did not have. Recorded as a `lead`: measured, not landed.

## 5 — The next run starts here

1. **The 0.25 pt/row pitch excess on unruled rows is the whole of what is left** on
   `72_bank_statement`: writing each unruled row 5 twips short of the page's pitch (the mirror of the
   `TABLE_BORDER_TW` subtraction, applied only where no rule is drawn) should take worst_dy 4.9 → ~0.4
   and the document to **42/42**. Build it together with the quantum change above — one corpus pass
   proves both.
2. **Do not re-propose a partial spend of this spacer.** It is inert (2315). Spend it *whole*, which
   is what the guard's `spendable` branch already does, and only where the room test passes.
3. **The instrument is now the first thing to read on this class.** `gverify/<name>.json` carries
   `displacement.med_dy` / `.worst_dy`; a fixer can tell a step from a drift before touching the
   engine. Run `gverify.py` on the other 10 of the 13 before choosing a construct — the step/drift
   split will say whether the quantum fix reaches them.
4. `dy.py` and the new detail now report the same quantity from the same matcher; the independent
   PyMuPDF match in §1 is the cross-check to keep using.
