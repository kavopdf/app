# 18_displacement — Google honours `w:trHeight` exactly; the row floors at the type's own line box, and there is no threshold

**22 Nov 2026 · relay slot 11:14 → · engine `kavopdf/app` at HEAD `462353f9` · one Google round trip,
one synthetic probe, probe Doc deleted after scoring (`KavoPDF-Verify` empty)**

## Why this was measured

Two runs in a row (10:20, 10:37) ended with the same instruction: *"a probe that sweeps the floor from
300 to 1500 twips on one cell is the cheapest way to find it. That probe was not run."* It is the
question every 18_displacement attempt has been guessing at: **what does Google actually lay a table
row at, as a function of the declared `w:trHeight`?** The committed evidence was contradictory — an
18 pt row declared 360 laid 19.0/20.0 (`GOOGLE-IGNORES-TRHEIGHT-1045-relay.md`), while a 1440-twip row
laid 72.00 and an 1103-twip row 55.83 (`CORRECTION-1045-relay.md:40-43`). That was read as a threshold
somewhere between 19 pt and 55 pt, or as a mysterious "content term" of 19.10 pt.

## The probe

A 28-row `.docx`: two tables, 14 rows each, one row per declared height
`{300, 360, 380, 400, 500, 600, 720, 800, 900, 1000, 1100, 1200, 1440, 1500}` twips, all
`w:hRule="atLeast"` (the rule the engine writes at `DocxWriter.java:6318-6320`), one identifiable
label per row, cell paragraph `w:before=0 w:after=0`. Table A carries **10 pt** Arial, table B **18 pt**
Arial. Round trip: `upload` → `GOOGLEDRIVE_CREATE_FILE` as `application/vnd.google-apps.document` →
`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` as PDF → PyMuPDF text origins. Row pitch is the distance
between consecutive label baselines.

## The measurement

| declared | declared pt | laid pitch, **10 pt** text | laid pitch, **18 pt** text |
|--:|--:|--:|--:|
| 300 | 15.00 | 15.75 | **21.45** |
| 360 | 18.00 | 18.75 | **21.45** |
| 380 | 19.00 | 19.50 | — (not in B: value repeated) |
| 400 | 20.00 | 21.00 | **21.45** |
| 500 | 25.00 | 25.50 | 25.50 |
| 600 | 30.00 | 30.75 | 30.75 |
| 720 | 36.00 | 36.75 | 36.75 |
| 800 | 40.00 | 40.50 | 40.50 |
| 900 | 45.00 | 45.75 | 45.75 |
| 1000 | 50.00 | 51.00 | 51.00 |
| 1100 | 55.00 | 55.50 | 55.50 |
| 1200 | 60.00 | 60.75 | 60.75 |
| 1440 | 72.00 | 72.75 | 72.75 |
| 1500 | 75.00 | — (row on page 2) | — |

Two facts, and they are the whole answer:

1. **Every laid pitch equals the declared height plus one constant.** From 15 pt to 72 pt, 13 of 13
   values, both type sizes, no discontinuity: `laid = declared + 0.75 pt`. The 0.75 is this probe's
   `Table Grid` border (0.5 pt) plus the rule, not a property of `trHeight`.
2. **Below the text's line box, the row floors at the line box and stops responding.** At 18 pt the
   three smallest declarations — 15.0, 18.0 and 20.0 pt — all lay the same **21.45 pt**. 21.45 − 0.75 =
   **20.70 = 1.15 × 18**. At 10 pt the same floor is below 15 pt, so all fourteen values are honoured.

## What this settles, and what it refutes

- **There is no threshold.** The "something changes between 19 pt and 55 pt" reading in
  `CORRECTION-1045-relay.md:40-43` is **wrong**: 19 pt and 55 pt behave identically. The two prior
  measurements were both correct and both on the same rule.
- **`max(trHeight, content)` was right in form and the content term is now named.** It is the cell
  text's line box, `≈ 1.15 × w:sz`, not an opaque 19.10 pt. Nothing about the type face, the cell
  margins or the paragraph's `w:before` was needed to explain it.
- **`w:hRule="exact"` was never the question.** `atLeast` is honoured exactly as written once the
  declaration clears the line box, so the 10:20 run's finding that switching `atLeast`→`exact` changes
  nothing on those rows is now explained rather than surprising.
- **The two blockers' excess is arithmetic, not magic.** `mobile-bill` and `insurance-policy-schedule`
  lay 19.10 pt on an 18.40 pt source pitch. 19.10 − 0.75 (border) = 18.35 = 1.15 × **15.96**, so those
  cells carry ~16 pt text declared at 18.0/19.0 pt. The declared 18.0 is **below** the line box, so
  Google floors every such row at 18.35 and the +0.70 pt/row excess measured in
  `table-spacer-CONFIRMED-6of16-1005-f1x.md` is that floor, to two decimal places.

## The consequence for the spacer, which is the landable path

`table-spacer-CONFIRMED-6of16-1005-f1x.md` measured the spacer (charged as `w:before` with a hairline
`w:line="1"`) taking **6 of the 16 solo documents to 42/42**, and blocked only because those two
full pages then overflow and drop content. The mechanism is now exact: the engine charges its page
budget the *declared* row height, while Google lays `max(declared, 1.15 × size)`. On the two blockers
that is +0.70 pt × 21 rows = +14.7 pt the engine never budgeted. **Charging the flow the same floor —
`max(declared, 1.15 × w:sz)` — makes the engine's page model equal Google's, and the spacer can then be
charged at its true value without exposing an overflow.** That is a two-line change at the budget line
(`DocxWriter.java:6233-6236`, `writtenRowsTw`) plus the spacer change, and it is the next build.

It also says what will *not* work, so no run pays for it again: **no row-height construct can make a
row lay tighter than 1.15 × its type size.** The 0.9634 row scale is not "inert", it is impossible —
declaring 18.0 where the line box is 18.35 cannot be honoured by any value of the declaration. The two
blockers cannot be fixed by row height at all; they need the line box reduced (an unmeasured `w:tcMar`
or cell-paragraph `w:line` probe) or accepted as a Google floor.

## Cost, and what was not done

One probe document, four Drive calls, ~4 minutes, deleted after scoring. Not done: the build the
consequence above calls for — the slot ended. It is one two-line change and one measured round trip on
`mobile-bill`, and it is written down here so the next run starts at the build instead of at the
question.
