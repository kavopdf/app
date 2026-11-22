# Row/line pitch in the 16 single-page `18_displacement` documents

Engine: `kavopdf/app` at HEAD `4afa0975c5e287191ad8f40fd547c541b4460926`.
Build: `bash tools/p2w-bench/build-engine.sh` (engine built in 35 s, no compile errors).
Corpus: `bash tools/p2w-bench/corpus-fetch.sh` → 213 PDFs, 0 missing.
Conversion: `ConvertOne` from `tools/engine-verify` (the command in the brief), output parsed from
`word/document.xml`. Source pitch measured with PyMuPDF 2.1 (`pymupdf` 1.28.6): the y of
`line["spans"][0]["origin"]` for every non-blank line, clustered at 1.2 pt, successive differences.

No tracked file was modified. Nothing was uploaded, pushed or deleted.

All 16 convert to `pages=1` with **0** `<w:br w:type="page"/>` and `w:pgSz w:h="16838"` (841.9 pt),
`w:pgMar top=0 bottom=0`. The engine's own accounting of each page is 796.0–817.2 pt of flow, i.e.
25–46 pt of slack, which is why none of them breaks.

---

## 1. The pitch construct each document uses

Fifteen of the sixteen have a table; `31_times_body_arial_headings` has **none** (its pitch is the
paragraph pitch). Every table is the *grid* path, and every one of its rows is written

    <w:trHeight w:val="N" w:hRule="atLeast"/>          DocxWriter.java:6318-6320

— `atLeast`, never `exact`. The `hRule="exact"` form exists only on the layout-column path
(`DocxWriter.java:2159-2161`, `int rowTw` at 2144-2145), which none of these 16 takes.

Inside a cell the pitch is split in two: `w:before` carries the distance from the row's top edge to
the baseline, and `w:line` carries a **hairline** box of 0.069 em (`HAIRLINE_EM`, `DocxWriter.java:107`;
`hairlinePt()`, 3886-3886; written by the cell emitters at 6507-6514 and 5203). A cell the page drew
on several lines instead gets `w:line = rowLineTw`, the row's own pitch (6195, 6204).

Every one of the 91–264 paragraphs in each document carries an explicit `w:spacing` — **0** fall
back to `docDefaults`' `w:after="120"` (`word/styles.xml`), so the default 6 pt after-space is not in
play anywhere.

| document | table rows | trHeight range (pt) | hRule | cell `w:line` (pt) | cell `w:before` (pt) | spacer above table (pt) |
|---|---:|---|---|---|---|---:|
| 16_right_aligned_amounts_txtpos | 13 | 19.0 | atLeast | 0.05, 0.6, 9.5 | 7.6, 14.7 | 4.65 |
| 22_invoice_four_columns_txtpos | 16 | 18.0–19.0 | atLeast | 0.6, 0.65, 9.0, 9.5 | 7.2, 7.6, 13.9, 14.7 | 6.65, 10.75 |
| 29_dot_leaders_txtpos | 5 | 18.0–20.0 | atLeast | 0.65, 10.0 | 8.0, 13.9, 15.5 | 15.85 |
| 31_times_body_arial_headings | **0 (no table)** | — | — | — | body `w:line` 0.05–0.65, `w:before` 0.0–175.3 | — |
| 362_price_list_dense | 29 | 8.4–12.0 | atLeast | 0.05, 0.4, 0.5 | 6.4, 9.2 | 15.2 |
| 41_coloured_headings_white_bg | 12 | 18.0 | atLeast | 0.65, 9.0 | 7.2, 13.9 | 3.5, 3.45, 3.45 |
| 68_journal_wide_table_spanning | 7 | 19.0 | atLeast | 0.55 | 14.75 | **144.0 (capped)** |
| 71_invoice_space_aligned_no_rules | 14 | 16.0–18.0 | atLeast | 0.6, 8.0, 9.0 | 6.4, 7.2, 12.3, 13.9 | none |
| 72_bank_statement_no_rules_right_amounts | 18 | 17.0–18.0 | atLeast | 0.05, 0.6, 8.5 | 6.8, 13.9 | 18.3 |
| 73_marksheet_subject_marks_grade | 9 | 19.0–20.0 | atLeast | 0.6, 10.0 | 8.0, 14.7 | 16.7 |
| balance-sheet-two-columns-of-figures | 16 | 11.6–16.0 | atLeast | 0.05, 0.45, 0.5, 0.55 | 8.85–12.45 | 12.6 |
| bus-timetable-station-left-times-right | 33 | 16.4 | atLeast | 0.45, 0.55, 0.6 | 12.65, 12.7, 12.75 | 6.35 |
| insurance-policy-schedule | 22 | 18.0–19.0 | atLeast | 0.05, 0.5 | 9.3–10.5 | 14.4, 6.4, 6.0 |
| mobile-bill | 24 | 18.0–19.0 | atLeast | 0.5 | 9.5–10.5 | 12.4, 6.4, 6.2 |
| table-with-no-header-row | 26 | 18.0–19.0 | atLeast | 0.5 | 9.7–10.5 | 12.35 |
| two-tables-stacked-with-no-gap | 13 | 18.0–20.0 | atLeast | 1.5–9.0 | 2.9–9.65 | 12.35 |

The "spacer above table" column is the engine's own `<w:p>` carrying
`w:line = gap, w:lineRule="exact", w:sz w:val="2"` — `DocxWriter.java:5869-5881`. It is the only
construct in these documents that carries a *gap* rather than a row.

---

## 2. Emitted row heights against the source's own row pitch

Source pitch = median successive baseline difference inside the table body (the longest run of
pitch values in 6–40 pt; the footer line at y≈805.9 is excluded). Emitted pitch = median
`w:trHeight`/20 over the document's rows.

| document | rows | median emitted (pt) | median source (pt) | **diff (pt)** | source spread (pt) | emitted distinct (pt) |
|---|---:|---:|---:|---:|---|---|
| 16_right_aligned_amounts_txtpos | 13 | 19.00 | 19.00 | **0.00** | 13.0–33.0 | 19.0 |
| 22_invoice_four_columns_txtpos | 16 | 19.00 | 19.00 | **0.00** | 13.0–36.0 | 18.0, 19.0 |
| 29_dot_leaders_txtpos | 5 | 18.00 | 18.00 | **0.00** | 18.0–20.0 | 18.0, 20.0 |
| 31_times_body_arial_headings | 0 | 16.60 (line) | 16.58 (line) | **+0.02** | 16.58–17.03 | — |
| 362_price_list_dense | 29 | 8.40 | 8.40 | **0.00** | 8.4–12.0 | 8.4, 12.0 |
| 41_coloured_headings_white_bg | 12 | 18.00 | 18.00 | **0.00** | 14.0–40.0 | 18.0 |
| 68_journal_wide_table_spanning | 7 | 19.00 | 19.00 | **0.00** | 19.0 | 19.0 |
| 71_invoice_space_aligned_no_rules | 14 | 18.00 | 18.00 | **0.00** | 9.0–36.0 | 16.0, 18.0 |
| 72_bank_statement_no_rules_right_amounts | 18 | 17.00 | 17.00 | **0.00** | 14.0–32.0 | 17.0, 18.0 |
| 73_marksheet_subject_marks_grade | 9 | 19.00 | 19.00 | **0.00** | 16.0–34.0 | 19.0, 20.0 |
| balance-sheet-two-columns-of-figures | 16 | 11.60 | 11.70 | **−0.10** | 10.0–26.0 | 11.6, 12.0, 16.0 |
| bus-timetable-station-left-times-right | 33 | 16.40 | 16.40 | **0.00** | 16.4 (32 rows) | 16.4 |
| insurance-policy-schedule | 22 | 18.00 | 18.40 | **−0.40** | 18.4 (24 rows) | 18.0, 19.0 |
| mobile-bill | 24 | 18.00 | 18.40 | **−0.40** | 18.4 | 18.0, 19.0 |
| table-with-no-header-row | 26 | 18.00 | 18.40 | **−0.40** | 18.4 | 18.0, 19.0 |
| two-tables-stacked-with-no-gap | 13 | 18.00 | 18.40 | **−0.40** | 18.4 | 18.0, 19.0, 20.0 |

Notes on the two rows that need one:
* `29_dot_leaders_txtpos` — the only table is the four-line totals block at y 412/430/448/466/486
  (pitch 18/18/18/20); the 22.0 pt pitch in the body of that page is dot-leader **prose**, not a
  table. Emitted 18/18/18/20/20 → 0.00.
* `31_times_body_arial_headings` — no table. Its prose pitch is 16.58 pt in the source
  (151.06/167.64/184.23 and 441.06/457.64/474.23/490.81) and 16.60 pt in the emitted `w:before +
  w:line` paragraphs: +0.02 pt.

**The emitted row pitch is the source's row pitch.** It is exact on 11 of 15 table documents, 0.10 pt
short on one, and 0.40 pt short on the four documents drawn at 18.4 pt. Those four are the
`floor(18.4·k)` pattern written a whole point at a time (rows 18.0/19.0 alternating; cumulative
18/36/55/73/92/110/128/147/165/184/… = `floor(18.4k)` exactly), which is worth −0.8 pt over 22 rows.

---

## 3. The one code path that decides that pitch

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, method `table(...)`:

| line | what it decides |
|---|---|
| 5986 | `int rowTw = round(extentPt / rowCount * 20)` — the **average** pitch, used when the page's own row edges are unknown |
| 6031-6032 | `float[] rowEdge = t.rowEdge; boolean exactRows = rowEdge != null && rowEdge.length == t.rows.size()+1;` |
| 6131-6138 | `rowTwHere` = `round((rowEdge[r+1]-rowEdge[r]) * 20)` — the per-row pitch when `exactRows` |
| 6149 | `ruleTwHere` — the border the row pays, `(szAbove+szBelow)*20/16` |
| 6163-6168 | `contentTwHere` / `cellLineHere` / `naturalLineHere` |
| 6195, 6204 | `baseLineTw`, then `rowLineTw` = the row's pitch (or `min(pitch,200)` for a multi-line cell) |
| 6208-6216 | `rowLineTw` raised to the type-size floor `sz*1.25*20` |
| **6228** | **`int rowHeightTw = Math.max(rowTwHere, rowLineTw);`** — the number that is written |
| 6318-6320 | `<w:trHeight w:val="rowHeightTw" w:hRule="atLeast"/>` |
| 6502, 6507-6514 | the cell's own box: `EMPTY_CELL_LINE_TW` (396) or `rowLineTw`, else `hairlinePt(sz)` |

**Which constant or clamp would have to change, and by how much.** Nothing in this chain is wrong
against the source: `rowHeightTw` already lands on the page's pitch to within 0.4 pt. There are only
two constants in the vertical path that are measurably off:

1. **The row pitch needs no correction to match the source, and one to match a Google render.** If
   the caller's measurement holds (Google renders a row 2–3.6 % taller than the pitch it is given),
   the correction is a factor on line 6228:
   `rowHeightTw = (int) Math.round(Math.max(rowTwHere, rowLineTw) * 0.9785)` — i.e. **−2.2 %,
   −8 twips on a 19.0 pt row, −7 on 18.0, −7 on 16.4, −4 on 8.4**. Per document that is 1.9–11.7 pt
   off the foot of the table (table in §4). Four of the sixteen are already written at 0.978 of the
   source pitch by accident (18.0 against 18.4) and would not move.
2. **The 2880-twip clamp on the table spacer** (`DocxWriter.java:5852` and `5866`,
   `Math.min(2880L, …)`) — 144.0 pt. `68_journal_wide_table_spanning` is clamped by it: the page's
   last prose baseline is y=193.13 and the table's top edge is 356.40 − 0.8·19.0 = 341.20, a gap of
   **148.07 pt = 2961 twips**. The clamp would have to rise from 2880 to **2961 (+81 twips, +4.05 pt)**
   for that document, and the cap is hit by exactly that one document.

---

## 4. Ranked candidate causes, with the twips/pt each contributes

Magnitudes below are computed from the emitted `word/document.xml` of each of the 16, not estimated.

### C1 — the row pitch itself is written at 100 % of the source pitch, and Google charges 2–3.6 % more per row
Code path: `DocxWriter.java:6228` → `6318-6320`.
Contribution: `0.022 × pitch` per row — 0.42 pt/row at 19.0 (8 tw), 0.39 at 18.0 (8 tw), 0.35 at 16.4
(7 tw), 0.18 at 8.4 (4 tw). Per table: 1.9 pt (29_dot_leaders) to 11.7 pt (bus-timetable, 33 rows).
Accumulates monotonically down the table, which is the "drifts progressively" shape.
**Caveat, and it is a real one:** the 2–3.6 % is the caller's Google measurement. I could not
reproduce it here (no Google render is available in this sandbox) and the repo's *own* measured
advance model (`tools/p2w-bench/REMAINING-DEFECTS.md`, "The model, measured") says the opposite for
a `w:trHeight`-held row: Google honours the row's declared height and the only per-line error is
`0.069·size − w:line/20` (see C4). So C1 rests on the caller's premise, not on my measurement.

### C2 — the gap above the table is a `w:line` on a 1 pt paragraph mark, and Google reads `w:line` as a multiple
Code path: `DocxWriter.java:5869-5881` (the spacer `<w:p>`), value from `5852`/`5866`.
Google's measured rule is `advance = w:before + (w:line/240)·lineHeight(face,size)`
(`REMAINING-DEFECTS.md:88-101`), so a spacer written as `w:line` is not a height at all. With the
1 pt mark the spacer is charged 0.137× its written value; with the inherited 11 pt default it is
charged 1.118×. Either way this is the **largest single vertical term in the corpus**:

| document | spacer(s) written (pt) | Google @1 pt mark (pt) | delta | Google @11 pt mark (pt) | delta |
|---|---:|---:|---:|---:|---:|
| 68_journal_wide_table_spanning | 144.0 | 13.74 | **−130.3** | 160.9 | **+16.9** |
| insurance-policy-schedule | 26.8 | 2.56 | −24.2 | 29.9 | +3.2 |
| mobile-bill | 25.0 | 2.39 | −22.6 | 27.9 | +2.9 |
| 72_bank_statement_no_rules_right_amounts | 18.3 | 1.75 | −16.6 | 20.4 | +2.2 |
| 22_invoice_four_columns_txtpos | 17.4 | 1.66 | −15.7 | 19.4 | +2.1 |
| 73_marksheet_subject_marks_grade | 16.7 | 1.59 | −15.1 | 18.7 | +2.0 |
| 29_dot_leaders_txtpos | 15.85 | 1.51 | −14.3 | 17.7 | +1.9 |
| 362_price_list_dense | 15.2 | 1.45 | −13.8 | 17.0 | +1.8 |
| balance-sheet-two-columns-of-figures | 12.6 | 1.20 | −11.4 | 14.1 | +1.5 |
| table-with-no-header-row | 12.35 | 1.18 | −11.2 | 13.8 | +1.5 |
| two-tables-stacked-with-no-gap | 12.35 | 1.18 | −11.2 | 13.8 | +1.5 |
| 41_coloured_headings_white_bg | 10.4 | 0.99 | −9.4 | 11.6 | +1.2 |
| bus-timetable-station-left-times-right | 6.35 | 0.61 | −5.7 | 7.1 | +0.8 |
| 16_right_aligned_amounts_txtpos | 4.65 | 0.44 | −4.2 | 5.2 | +0.6 |
| 71_invoice_space_aligned_no_rules | none | — | 0.0 | — | 0.0 |
| 31_times_body_arial_headings | none | — | 0.0 | — | 0.0 |

Which reading applies is **not measured**: the probe that produced the model moved the *run* size and
never an empty paragraph's mark. This is the single most valuable next measurement.

### C3 — the 2880-twip (144 pt) cap on that spacer
Code path: `DocxWriter.java:5852`, `5866` (`Math.min(2880L, …)`).
Contribution: `68_journal_wide_table_spanning` is short by **4.05 pt (81 twips)** — measured, not
inferred (§3.2). Every other document is under the cap.

### C4 — the hairline line box is charged 0.069 em by Google, and it is written as `0.069 em` rounded to a twip
Code path: `HAIRLINE_EM` (`107`), `hairlinePt()` (`3886`, `min(0.069·size, 0.6485)`), emitters `5203`,
`6507-6514`.
Contribution per line = `0.069·size − w:line/20`, always ≥ 0, so it always lengthens the page:
**+0.021 pt** on a 9 pt / 12 twip line, **+0.037** on 8.5 pt / 11 twip, **+0.57 pt** on a `w:line="1"`
paragraph (1 twip). Summed over each document: **+0.12 to +1.84 pt** (`31_times` +1.59,
`29_dot_leaders` +0.77, `bus-timetable` +0.88 — the last has 36 one-twip paragraphs). This is the
only mechanism here whose sign matches "Google renders taller", and it is one to two orders of
magnitude too small to explain a 4.3 pt median.

### C5 — a cell the page drew on several lines gets `w:line` = the row's pitch, which Google charges at 0.86×
Code path: `6195` (`baseLineTw`), `6204` (`rowLineTw`), `6507-6514` (`boxHere`).
Contribution: on a 9.5 pt box at 9 pt, Google charges `(190/240)·1.145·9 = 8.16 pt` instead of 9.5 →
**−1.34 pt per line**; per document **−8.3 to −106.0 pt** (72_bank −106.0 over 66 such paragraphs,
two-tables −41.5 over 25, 22_invoice −57.0 over 44).
**But it is absorbed**: the row is held by `w:trHeight … atLeast`, and the tallest cell's content is
still below it in every row of all 16 documents (minimum slack **1.50 pt**, maximum 7.69 pt; **0 rows
grow**). So this moves the text *up inside its row*, not the page. It is a `20_within_10pt` cause,
not an `18_displacement` cause.

### C6 — the average-pitch fallback flattens uneven rows
Code path: `5986` (`rowTw = extentPt/rowCount`), used when `6032`'s `exactRows` is false.
Contribution: the table's total height is preserved by construction (sum of rows = extent), so the
error is a sawtooth with **zero net drift** and a large local error:
`16_right_aligned_amounts_txtpos` writes 19.0 pt for all 13 rows against a source spread of
**13.0–33.0 pt** (local error −6.0/+14.0 pt); `41_coloured_headings_white_bg` 18.0 vs 14.0–40.0;
`22_invoice_four_columns_txtpos` 18.0/19.0 vs 13.0–36.0; `71_invoice_space_aligned_no_rules` 16.0/18.0
vs 9.0–36.0. This is the right size to explain a dy spread of −12.8/+2.9 pt, but not a *median* dy of
−4.3.

### C7 — the rule a row pays
Code path: `6149` (`ruleTwHere`), row box `max(trHeight, content+rule)` (`6073`).
Contribution: **0.00 pt** in all 16. Twelve tables draw no border at all (`w:tblBorders` all `nil`);
the four that do (`insurance-policy-schedule`, `mobile-bill`, `table-with-no-header-row`,
`two-tables-stacked-with-no-gap`, `w:sz="4"` = 0.5 pt) never have content+rule above `trHeight`.
Eliminated.

### C8 — `atLeast` vs `exact` on the row height
Contribution: **0.00 pt** for these 16, for the same reason as C7 — no row's content reaches its
floor. `atLeast` is a live risk only for a row whose cell content is taller than the pitch, which is
0 of 257 rows here. Eliminated for this set (it is the reason the 15 documents cannot be fixed by
switching to `exact`: that would clip nothing and move nothing).

### C9 — the default `w:after="120"` (6 pt) in `docDefaults`
Eliminated with evidence: `word/styles.xml` does set `w:after="120"`, but **0 of the 91–264
paragraphs** in each document omit `w:spacing`, so nothing inherits it.

---

## 5. Which of the 16 would be expected to become clean

Cleanliness is **not measured** here — no Google render was available. What follows is which
documents each change would move, and by how much.

**If C1 (row pitch × 0.9785 at `DocxWriter.java:6228`) were the one change:**

| changes | documents | shift at the foot of the table |
|---|---|---|
| yes | 16_right_aligned_amounts_txtpos | −5.3 pt |
| yes | 22_invoice_four_columns_txtpos | −6.5 pt |
| yes | 29_dot_leaders_txtpos | −1.9 pt |
| yes | 362_price_list_dense | −5.2 pt |
| yes | 41_coloured_headings_white_bg | −4.7 pt |
| yes | 68_journal_wide_table_spanning | −2.9 pt |
| yes | 71_invoice_space_aligned_no_rules | −5.4 pt |
| yes | 72_bank_statement_no_rules_right_amounts | −6.6 pt |
| yes | 73_marksheet_subject_marks_grade | −3.7 pt |
| yes | balance-sheet-two-columns-of-figures | −2.4 pt |
| yes | bus-timetable-station-left-times-right | −11.7 pt |
| **no** | insurance-policy-schedule | 0.0 — already at 0.978 of the source (18.0 vs 18.4) |
| **no** | mobile-bill | 0.0 — same |
| **no** | table-with-no-header-row | 0.0 — same |
| **no** | two-tables-stacked-with-no-gap | 0.0 — same |
| **no** | 31_times_body_arial_headings | 0.0 — **no table at all**; its pitch is a paragraph pitch and the factor would not touch it |

So C1 would be expected to change 11 of the 16 and to leave 5 untouched — including the only
document in the set with no table, whose failure therefore cannot be a row-pitch failure at all.

**If C2/C3 (the table spacer) were the one change:** 14 of 16 move (4.2–130.3 pt as tabulated);
`71_invoice_space_aligned_no_rules` and `31_times_body_arial_headings` have no spacer and would not
move by a twip.

**If C6 (per-row edges instead of the average) were the one change:** the 6 documents whose source
rows are uneven move a lot locally and zero at the table's foot — 16_right_aligned (13.0–33.0),
22_invoice (13.0–36.0), 41_coloured (14.0–40.0), 71_invoice (9.0–36.0), 73_marksheet (16.0–34.0),
362_price (8.4–12.0). The other 10 are already even grids and would not move.

---

## 6. What is not measured

* The Google render itself. Every per-document figure in §4 C1 is the caller's 2–3.6 % premise
  applied to my measured emitted pitch; C2's two columns are the two readings of the repo's own
  measured model and **the probe that would settle which applies has not been run** (an empty
  paragraph, `w:sz=2`, `w:line=2880`, `w:lineRule="exact"`, through Drive).
* Whether any of these documents actually *passes* after any of the changes. No `gverify` round was
  run.
* The 0.40 pt alternation in the four 18.4 pt documents (§2) is measured but its origin inside
  `PdfToWord` was not traced to a line; the emitted cumulative edges are `floor(18.4k)`, which is a
  whole-point quantisation of the row edges, and I did not find the statement that does it.
