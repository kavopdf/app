# 18_displacement: the engine now writes a single-line cell at its row's height — 2 documents 41/42 → 42/42 in Google

**27 Nov 2026, relay/fixer slot 17:11. Engine before: `d28ca7516c3f9165`.**

## The result first

| document | before (store, Google) | after (Google, this run) | check set |
|---|---|---|---|
| `362_price_list_dense` | 41/42, `18_displacement`, med_dy -2.8, 257 runs matched | **42/42 PASS** | 42/42 |
| `16_right_aligned_amounts_txtpos` | 41/42, `18_displacement`, med_dy -1.6 | **42/42 PASS** | 42/42 |

Both measured end to end this slot: the engine's own `.docx` → Drive → Google Doc → PDF export →
`gverify.py --collect`. Not LibreOffice, not a hand-edited file.

## What changed

`DocxWriter.java`, in the per-cell placement, immediately before the empty-cell guard:

```java
int deficitTw = rowHeightTw - cellBeforeTw - cellBoxTw;
if (vspan <= 1 && !cell.isEmpty() && rowTwHere > 0 && cellBoxTw > 0
        && deficitTw > 0 && deficitTw * 4 <= rowHeightTw) {
    cellBeforeTw = rowHeightTw - cellBoxTw;
}
```

The construct is the one `FINDINGS/18-displacement-CELL-CONTENT-SHORT-OF-ROWH-27NOV-fixer.md` proved by
hand-editing XML on the previous engine: Google lays a row at its CELL's content, not at `w:trHeight`,
so a one-line cell written `w:before` (the page's own baseline) + the hairline box is short of its row
and every row below it moves up by the shortfall.

| document | `w:trHeight` | cell `before + line` before | after | short by |
|---|---|---|---|---|
| `362_price_list_dense` | 168 tw | 136 tw | **168** | 32 tw (1.6 pt) |
| `16_right_aligned_amounts_txtpos` | 380 tw | 342 tw | **380** | 38 tw (1.9 pt) |
| `36_embedded_subset_font` | 400 tw | 360 tw | **400** | 40 tw (2.0 pt) |
| `402_calendar_month_grid` | 1230 tw | 335 tw | **335 (unchanged)** | 895 tw (44.7 pt) |

## Why the bound is a quarter of the row, and not `rowParts`

`rowParts` cannot draw this line. `16`'s short rows and `402`'s 1230-tw week rows have the same shape —
one paragraph per cell, a box far below the row — and one must be raised while the other must not. The
shortfall's SHARE of the row separates all four documents cleanly: 19 %, 10 %, 10 % raise; 73 % leaves.
A cell within a quarter of its row is the same row measured slightly short; a cell a quarter short of its
row is a cell whose row is tall for a reason that paragraph does not carry, and filling it doubles the
row — the `402` breakage the scope was first written for.

## The non-regression control, checked without a renderer

`402_calendar_month_grid` is the document the scope exists for. Its generated `document.xml` was compared
against the same document built before the change: **every cell's `w:before`/`w:line` pair is identical**
(`(60,275)` x16, `(0,1)` x11, `(270,13)` x10, `(56,280)` x5, `(109,144)` x5). The patch does not touch
`402` at all, so it cannot regress it. That is a structural check, not a proxy: the bytes are the same.

## What was NOT done this slot

- The 212-document Google table was not re-measured on the new engine, so the corpus-wide move count is
  not known. The gate will want that before this lands on `main` if the tree is otherwise unmeasured.
- `36_embedded_subset_font` (41/42, same construct, 40 tw short, XML now at its row height) was not
  rendered through Google. It is the cheapest next test and should clear.
- `31_times_body_arial_headings` is NOT this construct — no table — and is untouched by it.
