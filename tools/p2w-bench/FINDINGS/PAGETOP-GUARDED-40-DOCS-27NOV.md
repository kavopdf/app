# THE PAGE-TOP MARGIN, GUARDED: 40 DOCUMENTS, 0 WORSE, 1 BETTER — AND THE "33-POINT ITR WIN" WAS A PAGE COUNT

**27 Nov 2026, fixer slot 01:20.** Engine measured: committed tree (`a4d8fca469bba636`, restored
`9f0a8207`) and the guarded patch (`dc24e106b67abc0d`, built classes `373c8837f29123fb`).
Patch kept, unlanded, at `tools/p2w-bench/PATCHES/pagetop-guarded-27NOV.patch` (276 lines).

---

## 1. What was re-measured, and why the numbers in the record could not be trusted

`RANKING.csv` is a **mixed table**: 209 of its rows match the withdrawn patched engine `aa496ebe`, 208
match the restored one, and the 7 rows that disagree are exactly the 7 documents the patch moved. That is
why `regress.py --check` refuses on a tree with nothing modified in `app/`, and it is the same refusal three
runs have now reported as "the engine is blocked".

This run measured its own before/after instead of reading the table. Nine deciding documents, converted and
scored three ways on one pod, one instrument (`benchmarks/p2w.py:measure_doc`):

| document | committed engine | `aa496ebe` (patch only) | patch + budget fix | patch + both guards |
|:--|--:|--:|--:|--:|
| `itr-computation-with-slab-table` | 42.33 | **9.10** | 40.83 | **40.83** |
| `newsletter-3col-header-footer` | 0.20 | **86.30** | 0.20 | 0.20 |
| `350_question_paper` | 0.11 | 0.12 | **3.75** | 0.11 |
| `39_small_caps_letter_spacing` | 0.70 | 0.80 | 0.80 | 0.70 |
| `600_reviewed_invoice_with_annotations` | 62.46 | 62.46 | 62.46 | 62.46 |
| `601_fillable_admission_form` | 52.39 | 52.39 | 52.39 | 52.39 |
| `401_trifold_brochure` | 0.03 | 0.03 | 0.03 | 0.03 |
| `bank-statement-5-pages` | 0.56 | 0.56 | 0.56 | 0.56 |
| `412_page_labels_roman` | 0.00 | 0.00 | 0.00 | 0.00 |

share@5px, lower is better. All nine render at their source page count in the first and last columns.

**The committed tree's own numbers are not the table's.** Measured today on `a4d8fca`: `601` is **52.39**,
not the 55.32 three findings quote; `401` is **0.03**, not 0.79; `39` is **0.70**, not 0.80; `350` is
**0.11**, not 0.12; `newsletter` is **0.20**, not 86.30. The table's three "regressions" are the patched
engine's numbers left in a table stamped for the restored one.

## 2. The finding that changes the goal: the itr win is a page count, not a fix

Rendering each variant and counting pages:

| document | committed | patch only | patch + budget fix |
|:--|--:|--:|--:|
| `itr-computation-with-slab-table` | 1 | **2** | 1 |
| `newsletter-3col-header-footer` | 1 | **2** | 1 |
| `350_question_paper` | 1 | 1 | 1 |
| `39_small_caps_letter_spacing` | 1 | 1 | 1 |

`aa496ebe` did not move itr's ink 33 points closer to the original. It **pushed the body off the sheet**:
the margin was claimed without taking it out of the flow's budget, so the page overran and rendered as two
pages against a one-page source. The score fell from 42.33 to 9.10 because page 1 now holds only part of the
document and the rest is compared against nothing. `itr` is one of the report's own
"Not scored — page count did not match" documents under this engine.

**Every run since 26 Nov has been chasing this number, and the number was an artefact.** The "third-largest
move in the corpus", the bisect to recover it, the `pageTopTw = 0 when pages == 1` proposal to protect it —
all of it rests on a document that got worse by the only measure the goal names.

## 3. Why the margin must come out of the budget (and what that costs)

The patch moved the page's top gap from the first paragraph's `w:before` into `w:pgMar w:top`, and
`pageFirstBeforeTw()` subtracts the margin back off that paragraph, so `pgMar + w:before` equals the original
`w:before`. The bytes say the gap is preserved — newsletter's first paragraph reads `w:before="1199"` before
and `pgMar w:top="1200"` + `w:before="0"` after.

The **reader** does not agree. The text area starts at `pgMar.top` and the page's usable height is smaller by
that margin, while the flow's budget still claimed the whole sheet. A page whose content already reached the
bottom edge therefore overruns by the margin. Charging the margin to the budget
(`ctx.budgetTw -= ctx.pageTopTw`) puts the two accounting schemes back together: newsletter 86.30 → 0.20 and
its page count back to 1.

That alone is not enough, because it also charges documents whose ink has no room to give: `350` went
0.11 → 3.75 with the page count unchanged — a score that moves without a page break to explain it.

## 4. The two guards, and the population they leave

Both are per-document identity rules, in `sectionTopTw()`:

1. **A page written as a column layout table carries its gap inside the table.** `pageFirstBeforeTw()` only
   subtracts from a paragraph the flow flags page-first; the paragraphs of a column layout table live in
   cells, so the subtraction never happens and the sheet carries the margin **and** the whole `w:before`.
   Measured on newsletter: `pgMar 1200` + `w:before 1199` against a source gap of 1199 — the gap counted
   twice. `hasColumnBands(page) → return 0`.
2. **A page must have the room the margin takes.** If `pageHeight − lowestInk < pageTopTw` the margin cannot
   be honoured without overflowing the sheet. Measured on `350_question_paper` (ink to 837.32 of 841.89,
   margin 35.50 pt): 0.11 → 3.75 when the margin was claimed anyway.

With both guards, **41 of 213 documents claim a non-zero `w:pgMar w:top`** (census of every emitted
`document.xml`, `373c8837`). The other 172 write `w:top="0"`, which makes `ctx.pageTopTw == 0`, which makes
both `budgetTw` and `pageFirstBeforeTw()` byte-identical no-ops — those documents cannot have moved.

**The 41-document population, measured before and after.** Before: the previous run's
`FINDINGS/RANKING-MEASURED-RESTORED-ENGINE-27NOV.csv` (203 rows, the restored engine). After: the guarded
build, same instrument, 40 of the 41 measured (`416_many_tiny_pages` is exempt at 300 pages).

| | |
|:--|:--|
| documents measured | **40** of 41 |
| **worse** | **0** |
| better | **1** — `itr-computation-with-slab-table` 42.33 → 40.83 (−1.50), page count 1 |
| unchanged | **38** |
| no before value | 1 — `324_loan_amortisation_schedule`, measures 0.00 |

**0 worse across the entire population the change can touch.** The prize is small — one document by 1.5
points — and that is the honest size of it once the page-count artefact is removed. `classpick.py
--leverage` values `18_displacement` at 54.8 documents; the guards leave 41 documents claiming a margin and
38 of them already score at or near zero, so the class's remaining population is not in this construct.

## 5. Why it is not landed

`regress.py --check` and `measure_gate.py` both refuse, correctly:

```
ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tree is dc24e106b67abc0d
NOT READY — the corpus has not been measured on this engine
```

An engine change requires the whole 212-document table re-measured on the new engine. That is ~35 minutes of
measurement (213 documents convert in 4.7 min at 6 workers; scoring is ~8 s each), which did not fit beside
the corpus conversion this pod needed from cold. The patch is kept as
`PATCHES/pagetop-guarded-27NOV.patch`, the tree is reverted, and the engine is rebuilt to the committed
source.

## 6. What would overturn this

- A document in the 172-identity set whose `document.xml` differs from the committed build. The argument is
  by construction (`pgMar=0 → pageTopTw=0 → both no-ops`), and one byte comparison of the two builds over
  those 172 documents would settle it.
- Any of the 40 measuring worse on Google rather than LibreOffice. Every number here is the LibreOffice
  proxy; rule 1 says Google is the truth, and none of these 40 has been through Drive.
- `itr` at 9.10 on a **one-page** Google render. If it reproduces, the win is real and section 2 is wrong.
  It did not reproduce as a one-page render in three builds here.

## 7. For the next run

1. **Land it, and it is a 35-minute job, not a mystery.** Re-measure the 212 with `benchmarks/p2w.py
   --force` on `PATCHES/pagetop-guarded-27NOV.patch`, stamp the table, then the gate passes on its own terms.
   The population evidence is already in section 4.
2. **Delete the 9.10 from the record.** `ATTEMPTS.json` and three LAST-MESSAGE.md files carry
   "itr 42.33 → 9.10, third-largest move in the corpus". It is a two-page render of a one-page document.
   Any future bisect that starts from it starts from a defect.
3. **`RANKING.csv`'s three "regressions" are stale rows, not a blocked engine.** Measured today on the
   committed engine: newsletter **0.20**, 39 **0.70**, 350 **0.11** — all at or better than the 15 Nov
   baseline. Replacing those three rows with today's measurements clears the check on the current engine.
