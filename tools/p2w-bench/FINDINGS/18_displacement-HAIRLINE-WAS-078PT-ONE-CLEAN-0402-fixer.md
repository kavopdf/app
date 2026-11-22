# 18_displacement — the hairline was 0.78 pt of gap Google never drew, and one document is clean: `22_invoice_four_columns` 41/42 → 42/42

**23 Nov 2026 · fixer slot 02:57 IST · class `18_displacement` (35.7 clean documents by
`classpick.py --leverage`, the largest single check) · engine change in `DocxWriter.emitTable` ·
outcome: `kept`, 1 document to 42/42 in Google · corpus 212/212 re-measured, 0 worse ·
every Google number below from a round trip made in this slot**

## Why this construct, and not the suggestion

`classpick.py` suggested `t08_line_order` (2 documents, .txt). The leverage table says
`18_displacement` is worth **35.7 clean documents**, `32_stroke_lines` 23.3, and 13 documents
fail `18_displacement` and nothing else. The previous slot landed the spacer scope guard and left
two open questions in `HANDOFF.json next`; this slot took the first of them — the constant
residual on `22_invoice` and `16_right_aligned` — because a constant is the only kind of error in
this construct that can be removed without touching the guard.

## The change

The gap between flowing text and a table is written as an empty spacer paragraph, and since the
guard landed it is split: a hairline in `w:line`, the remainder in `w:before`.

The hairline was **20 twips**, credited as 1.00 pt of the gap. Google does not lay `w:line` that
way. The repo's own sweep says `w:line` exact on an `sz=2` mark lays
`2.5873 * max(L/240, 0.06)` pt — **0.2156 pt at L=20**. So twenty twips of gap were declared, a
fifth of a point delivered, and every table under a split spacer sat **0.7844 pt high** in Google.
A constant, identical on every document, because the construct is identical.

    int spacerHairTw = 20;   ->   int spacerHairTw = 1;

At L=1 the same law lays 0.1552 pt against 0.05 pt credited, so the error goes from **−0.78 pt to
+0.10 pt**, and `before + line` still equals the gap to the twip — LibreOffice and Word see the
page they always saw.

**The guard's room test is now keyed to a fixed 20, not to the hairline, and that is half the
change.** With the test keyed to the hairline, `22_invoice`'s *second* spacer flips from spent
(`before=195 line=20`) to refused (`before=0 line=215`) — Google then lays 2.32 pt of a 10.75 pt
gap and that table moves 7.65 pt, decided by a constant that has nothing to do with the page's
room. The test and the running charge (`ctx.spacerSplitTw`) therefore stay exactly what they were
at hair=20; only the emission moves. Every document the guard refuses is byte-identical to the
engine before this change, and no document changes side of the guard.

## Measured in Google, before and after, same hour, differing only in the patch

Converted with `ConvertOne` from the same corpus PDF, uploaded to `KavoPDF-Verify`, copied as a
Google Doc, exported as PDF, scored by `verify_google.py --docx` against the source. All four
probe documents were deleted from Drive afterwards.

| document | build | Google | failing check |
|:--|:--|:--|:--|
| `22_invoice_four_columns_txtpos` | base (hair=20) | **41/42** | `18_displacement` render=1 |
| `22_invoice_four_columns_txtpos` | patched (hair=1) | **42/42 PASS** | — |
| `16_right_aligned_amounts_txtpos` | base | 41/42 | `18_displacement` render=1 |
| `16_right_aligned_amounts_txtpos` | patched | **41/42** | `18_displacement` render=1 |

`22` was measured on **both** builds in this slot, an hour apart from nothing, so the move is not a
margin reading carried over from another run. `16` did not move: it is the same constant, but its
one displaced block sits outside the 3.15 pt tolerance at 9 pt for a second reason this patch does
not address (below).

## Prediction against result

Written down before the round trips, then compared:

| predicted | measured |
|:--|:--|
| 22 → 42/42 | 42/42 |
| 16 → 42/42 | **41/42** — wrong |
| LibreOffice 42/42 on both builds for both documents | 42/42 on all four |
| no document's `share@5px` moves corpus-wide | **0 of 213 changed** |

## What this slot could not close

`16` fails for a reason this patch does not touch. The arithmetic that brackets it (see
`FINDINGS/18_displacement-RESIDUAL-2.5PT-ARITHMETIC-0355-fixer.md`) is: the hairline was −0.78 pt,
and a second constant sits in the **cell paragraph's line box** — declared 7.60 + 9.50 = 17.10 pt,
laid 7.60 + 8.193 = **15.793 pt**, a **−1.307 pt per row** term identical on both documents.
Removing that means inflating the cell's declared `w:line`, which moves the text inside the row in
LibreOffice (the row height is `atLeast 19 pt` and absorbs the height, not the position). It is the
next lever on this class and it is a separate measurement.

## What the corpus says

- 213 documents converted with the patched engine, 212 measured (`416_many_tiny_pages` is exempt:
  300 pages, no per-command budget can walk it).
- `gate.py`: **no regressions against baseline**, `RANKING.csv` published, `measure_gate` READY.
- `share@5px` changed on **0 of 213** documents. That is the prediction, not a disappointment: the
  patch moves 0.05 pt in the LibreOffice proxy and the score is taken at a 5 px tolerance.
- `.txt` re-scored: **213 scored, 213 unchanged**. `TxtWriter` is untouched.

## The table-coverage defect found on the way

`gate.py` publishes `RANKING.csv` from what it measured, and it **dropped the exempt document's
row**. `measure_gate.py` then read "212/212 scored, 1 exempt" as *not ready* — it wants the row to
exist even when the document is exempt, which is what the committed table has always had
(`213,416_many_tiny_pages,exempt,exempt,...`). The row is restored here as the same unscored
exempt marker. A run that publishes a table without it silently shrinks the corpus the whole
pipeline is judged on. Recorded in `BLOCKERS.md`.
