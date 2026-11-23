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

## 5 — The second lead, built and REFUTED in the same slot

§4 leaves 7 runs at +3.2 … +4.9 pt, growing monotonically down the page. Measured directly from the
Google export's own text layer, the **baseline pitch is 17.25 pt for 16 consecutive rows** against the
page's 17.00, so the drift looked like 5 twips of row height and the obvious fix was to write each
unruled row 5 twips short.

Built it (`rowTwHere - 5` where `!t.ruled`), and measured it three ways:

| | HEAD + quantum | + rows 5 twips short |
|:--|--:|--:|
| Google `med_dy` | **+1.1** | **-4.2** |
| Google `worst_dy` | **4.8** | **8.7** |
| Google score | 41/42 | 41/42 |
| LibreOffice score | **42/42** | **41/42** — `18_displacement`, med_dy -1.1 |
| LibreOffice `23_line_pitch` | 17.0 / 17.0 | 16.8 / 17.0 |

**Refuted, and it costs a document in LibreOffice.** Shortening the row made Google *worse*, not
better, which says Google is already honouring `w:trHeight` (340 twips laid as 17.0) and the 17.25 pt
**text** pitch is produced INSIDE the cell — the cell paragraph's own line advance
(`w:before="278" w:line="12" exact`, `sz=17`) — not by the row box. Shortening the row therefore moved
the whole table up by 18 × 0.25 pt and left the drift intact: med_dy +1.1 → -4.2 is exactly the 5.3 pt
of row height removed.

So the residual is a **cell-line** fault, which is the census's construct #2 ("the cell's own line
box, `:6892` — no run has yet converted into a clean document"), and it is not reachable by the row
height. `23_line_pitch` is the check that constrains it: LO reads the page's 17.0 and the render's 16.8,
so any row-height route pays the LO check to buy the Google one.

## 6 — The corpus pass did not fit, and that is the measured reason

Landing the §4 change needs `regress.py --check` to see a corpus measured on the new engine
(`ENGINE CHANGED … An unmeasured change is not a pass`). `benchmarks/p2w.py --force` was run with scipy
installed: **33 documents in 250 s, then 7 in the next 250 s** — 43 s a document on this pod, i.e.
**~2.5 hours for 213**, against the 40 minutes the brief budgets. That is a fact about this run's pod,
not about the change, and it is why the engine is reverted rather than landed. The next run should
check the rate before committing to a pass.

## 7 — The next run starts here

1. **The quantum change in §4 is proven and small — re-apply it and land it with the corpus pass**:
   `rowExcessTw = (t.ruled ? 15 : 5) * ctx.pageRowCount` at `DocxWriter.java:6093`. It is byte-identical
   for every ruled table, LO-neutral (42/42 on the document measured), and worth **med_dy -13.0 →
   +1.1** on a real Google render.
2. **Do not shorten unruled rows.** §5 refuted it and it costs LO `18_displacement`.
3. **The residual is the cell's line advance inside an unruled row.** On
   `72_bank_statement` the cell paragraph is `w:before="278" w:line="12" exact` on an `sz=17` run
   inside a 340-twip row, and Google advances 17.25 pt a row where the page drew 17.00. That is the
   whole of what is left on this document, and it is ~4.9 pt against a 2.8 pt tolerance.
4. **The instrument is now the first thing to read on this class.** `gverify/<name>.json` carries
   `displacement.med_dy` / `.worst_dy`; a fixer can tell a step from a drift before touching the
   engine. Run `gverify.py` on the other 10 of the 13 before choosing a construct — the step/drift
   split will say whether the quantum fix reaches them.
5. `dy.py` and the new detail report the same quantity from the same matcher; the independent PyMuPDF
   match in §1 is the cross-check to keep using.

## 8 — Two more solo documents measured with the new instrument

The instrument's first real job is to tell the next run which of the 13 the spacer construct can reach.
Two more, converted on the **HEAD** engine (no changes) and scored on a live Google round trip:

| document | Google | `med_dy` | `worst_dy` | spacer in the docx? |
|:--|:--|--:|--:|:--|
| `72_bank_statement_no_rules_right_amounts` | 41/42 | **-13.0** | **28.2** | yes — 18.30 pt, `w:before="0"` |
| `71_invoice_space_aligned_no_rules` | 41/42 | **+1.1** | **6.7** | **no spacer at all** |
| `table-with-no-header-row` | 46/47 | **-0.5** | **9.0** | yes — 12.35 pt, ruled, guard correctly refuses |

Two things follow, and both are new:

1. **The spacer is not the class's construct.** `71_invoice_space_aligned_no_rules` carries no
   table-gap spacer and still fails `18_displacement`; `table-with-no-header-row`'s spacer is refused
   by the room test and the document is 46/47 with `med_dy -0.5`. So the §4 change reaches
   `72_bank_statement` and the other documents shaped like it, and **nothing else**. The census's
   "53 of the 100" is presence, not causation — on this evidence the causal set is smaller.
2. **What is left on all three is LOCALISED, not a page-wide offset.** Once the step is removed,
   `med_dy` sits at |1.1| pt or better on every document measured, while `worst_dy` stays 4.8–9.0. A
   median that good with a tail that bad is a handful of runs, not a block — which points at
   individual cells and rows, not at the flow or the page. The next run should read `worst_dy` first
   and find *which runs*, not re-measure the page.

That is the shape of the remaining prize on this class: small, localised, and visible only now that the
check prints a distance.
