# The table gap is `w:before`, the row rung is 10 twips, and the row must have room under its text

**27 Nov 2026, fixer slot 07:03.** Measured in Google end to end (upload → Drive converts to a
Google Doc → export PDF → `verify_google.py`, and independently with PyMuPDF for the per-run dy).

Outcome: `mobile-bill` **46/47 → 47/47** and `electricity-bill` **46/47 → 47/47**, both recorded
in `benchmarks/gverify/`. Nothing worse: `price-list-2col-dense-right-aligned` is **byte-identical**
to the previous engine (`word/document.xml` sha256 equal), and `regress.py --check` passes at corpus
scale on the new engine (docx and txt, "no document worse than baseline", google-safe clean).

---

## 1. What the last run left, and what was wrong with it

The carried instruction was: *"fix the rows and the anchor in one patch"* — declare `w:trHeight` one
rung under the page's pitch and fix `writtenRowsTw` / `lastRowHeightTw` so the flow does not charge
the pre-patch heights.

**The anchor is not the consumer.** `writtenRowsTw` is floored at `pitchTwHere` (= `rowTwHere`), so a
row declared below its own pitch is charged the pitch either way; and `rowBottomPt` is built from the
page's own `lastRowTopPagePt`, not from the flow. There is nothing there to fix. The instruction was
aimed at the wrong variable, and the numbers below say where the error actually lives.

## 2. The rung, measured four ways on one document

`mobile-bill`'s page pitch is **18.40 pt**. Four copies of the generated .docx differing only in
`w:trHeight` were exported through Drive:

| declared twips | Google lays | vs page |
|---|---|---|
| 340 | 18.15 pt | −0.25 |
| **350** | **18.40 pt** | **0.00** |
| 360 (HEAD) | 19.15 pt | +0.75 |
| 380 | 19.90 pt | +1.50 |

So ten twips off the declaration is 0.75 pt off the laid row, and HEAD is 0.75 pt too tall on every
row of both tables. (This also corrects the 22 Nov constant "Google lays a ruled row 0.75 pt taller
than the declaration": with HEAD's declaration it is **1.15 pt** taller, 19.15 against 18.00.)

## 3. The rung alone is not a fix, and it is not safe on every row

`-10 twips` on **every** `w:trHeight`, measured in Google on five documents that were one check from
clean:

| document | HEAD | −10 every row |
|---|---|---|
| 16_right_aligned_amounts_txtpos | 41/42 | 41/42 |
| 74_balance_sheet_indented_subitems | 41/42 | 41/42 |
| electricity-bill | 41/42 | 41/42 |
| table-with-no-header-row | 41/42 | 41/42 |
| price-list-2col-dense-right-aligned | 41/42 | **40/42** (`46_text_crossing_rule` 0→2) |

Four documents do not move and one loses a check. **A row whose text sits at its foot has no height
to give: shorten it and the rule the page drew moves up through the text.** That is the whole of the
regression, and it is why the construct needs a gate, not a constant.

## 4. The gap above a table is the bigger error, and it is a Google-vs-LibreOffice construct

The engine already knows Google draws an exact `w:line` on an empty paragraph at ~21.6 % and
`w:before` at 1:1, and already splits the gap — but the split is clamped by a **room** test, and on
these pages the room is 0, so nothing is spent and the table sits high. Measured deficit, two
documents, independently:

| | caption → first row baseline | declared gap | short by |
|---|---|---|---|
| mobile-bill, source | 16.40 pt | — | — |
| mobile-bill, HEAD | 12.19 pt | 128 tw | 4.21 pt |
| electricity-bill, source | 16.40 pt | — | — |
| electricity-bill, HEAD | 12.20 pt | 233 tw | 4.20 pt |

Two different tables, two different declared gaps, the same **4.2 pt** short — it is the construct,
not the page. One-knob calibration on `electricity-bill`:

* `w:before` +180 twips → the page moves **+8.7 pt** (≈1:1)
* `w:line` +180 twips → the page moves **+2.06 pt** (≈23 %)

The clamp was replaced by a **fraction**: 70 % of the gap into `w:before`, the rest left in
`w:line`, so `before + line` still equals the spacer to the twip and LibreOffice/Word lay the page
they always laid. Measured on `mobile-bill`, rung + gap together:

| variant | med dy | 18_displacement |
|---|---|---|
| rung only (0 % spent) | −9.65 | FAIL |
| 60 % spent | −0.99 | FAIL |
| **70 % spent** | **+0.49** | **PASS** |
| 100 % spent | +4.70 | FAIL |

## 5. What was landed

Two constants and two lines in `DocxWriter.table`:

1. **`ROW_RUNG_UNDER_TW = 10`** — a row whose pitch binds declares ten twips under its own pitch.
2. **`FOOT_ROOM_MIN_TW = 100`** — and only when its lowest baseline leaves at least 100 twips
   (5 pt) of the row below it. This is the gate that keeps `price-list-2col` byte-identical.
3. **`SPACER_SPEND_FRAC = 0.70`** — the spacer split spends 70 % of the gap in `w:before` instead
   of clamping to the page's remaining room.

`mobile-bill` and `electricity-bill` go 46/47 → **47/47**; the other three sampled documents are
unchanged or byte-identical; the corpus gate passes in both formats.

## 6. For the next run

* `18_displacement` is still failed by **105** documents and **25** of them fail nothing else. The
  next probe is the same pair on that list — start with the ones whose `med_dy` is small
  (`303_discharge_summary` −0.2, `table-with-no-header-row` −0.5, `402_calendar_month_grid` 1.4).
* `74_balance_sheet_indented_subitems` does **not** move under this change: its 12 out-of-tolerance
  runs are all **positive** (+3.2 to +4.3) and include `Page 1` and the signature block — that is
  page furniture and a bottom-half shift, not a table. Do not spend a slot on it as a table case.
* The 70 % fraction is measured on two documents. If a document regresses under it, the fraction is
  the knob to turn, not the gate — and the way to find the right value for a page is the same
  one-knob probe used in §4, not a corpus pass.
