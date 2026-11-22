# 18_displacement — Google does not lay a table row at its `w:trHeight`

**22 Nov 2026, relay slot 10:20. All numbers below measured this run, in Google, on the real
renderer. Nothing here is inferred from LibreOffice.**

Five engine builds and five Google round-trips. Four constructs refuted with a PDF or a read-back to
show it; one construct measured to work and blocked on a second question. The engine is back at HEAD.

---

## The measurement loop that made this cheap

The 09:51 run spent nine Drive calls on three documents and reported the cost as an obstacle. It is
not: one document is **four calls and about ninety seconds** —

    upload(path, tool_slug=GOOGLEDRIVE_CREATE_FILE, toolkit=googledrive)   -> s3key
    GOOGLEDRIVE_CREATE_FILE(mimeType=google-apps.document, parents=[KavoPDF-Verify])
    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId, "application/pdf")    -> /scratch/downloads/composio/<name>.pdf
    verify_google.py <source.pdf> <export.pdf> --docx <docx>

Two facts that cost the last run time and are not obvious:

- **`upload` refuses a path under `/scratch/work`.** It must be a saved file: copy the probe to
  `/scratch/output/<name>.docx` first, or the call fails with "is not a saved file".
- **`KavoPDF-Verify` is folder id `11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6`.** `GOOGLEDRIVE_FIND_FOLDER`
  returns 170 KB of JSON to say so; resolve it once and paste the id.

The loop reproduced the committed result exactly — mobile-bill 46/47, `18_displacement` alone — which
is the control that says the loop is measuring what the table says it measures.

---

## 1. `w:hRule="exact"` is inert. REFUTED.

The 09:51 report's instruction was to make the floor bind. Emitter B (`DocxWriter.java:6318`) writes
`hRule="atLeast"` unconditionally. Built: `exact` whenever `rowHeightTw <= rowTwHere` (the floor is
what the row needs, so the content cannot be clipped), `atLeast` otherwise.

mobile-bill in Google, rule positions off the exported page:

| | rule gaps, rows 0-13 |
|:--|:--|
| HEAD, `atLeast` | 18.0, 19.0, 20.0, 18.0, 20.0, 18.0, 18.0, 19.0, 20.0, 18.0, 20.0, 19.0, 18.0, 20.0 |
| `exact` where the floor binds | **identical, element for element** |

All 24 rows came out `exact` and the PDF did not move a rule. Google normalises `exact` back to
`atLeast` on import — read back from Google's own `.docx` export of the same document, which carries
`<w:trHeight w:val="360" w:hRule="atLeast"/>` for rows we wrote `exact`.

## 2. `w:before` does not enter the row's height in Google. REFUTED.

The engine places cell text with `before` = 163-210 twips (8.2-10.5 pt) plus a hairline box. If
Google charged `before + box` against the floor, cutting `before` would stop the growth.

Built a cap (`GOOGLE_BOX_EM = 1.33`, before ≤ rowHeight − 1.33·size), which took mobile-bill's
`before` from 190-210 to 163-188 twips. Google's rule gaps: **identical to HEAD, all 26 of them.**

A synthetic probe says the same thing directly. One table, floor 360, 13 rows, `w:before` 100 → 340
twips in 20-twip steps (5.0 → 17.0 pt, a 12 pt range):

    every row laid 19.0 pt.  w:before moved the text inside the row and never the row.

## 3. The floor is not what Google lays, even though Google keeps it.

Read back from Google's `.docx` export of mobile-bill: `w:trHeight w:val="360"` / `"380"`,
`hRule="atLeast"`, and `w:before="163"`/`"183"`/`"188"` — **exactly what we wrote.** Google's model
has our numbers. Its PDF lays 18.0/19.0/20.0 on the same rows, and lays a row written 380 at 18.0.
So `trHeight` is a number Google stores and does not honour as a height.

Also in that read-back, the construct Google *does* replace:

    written:  <w:spacing w:before="163" w:line="10" w:lineRule="exact"/>
    Google:   <w:spacing w:before="163" w:line="14.399999999999999" w:lineRule="auto"/>

**The hairline box is discarded.** `w:line` = 0.069 em (0.48 pt at 7 pt) is below whatever Google
accepts as a line box, and it substitutes ~14.4 pt at `lineRule="auto"`. That is the construct this
engine leans on for every single-line table cell in the corpus, and it is a construct Google ignores —
which `google_safe.py` does not list (it lists only `w:position`). **That list has a gap.**

## 4. The construct that works. MEASURED, then blocked on a different question.

Synthetic probe, one table, floors 360/360/380 (the `floor(18.4k)` sawtooth), eleven rows, cell
written `w:before="0"` and `w:line = <the row's own height>` `lineRule="exact"`:

    laid: 18.00, 18.00, 18.75, 18.00, 18.00, 18.75, 18.00, 18.00, 18.75, 18.00, 18.00

**The floor is reproduced.** Average 18.25 against the page's 18.40 — 0.15 pt a row, 1.65 pt over
eleven rows, inside `18_displacement`'s 2.52 pt tolerance. `vAlign` (top/center/bottom) does not
change the height: all three variants laid the same sawtooth.

Why it cannot be landed as it stands: a box the height of the row puts the baseline at `LINE_BASE` =
0.8 of the row, and mobile-bill draws its cell text at **0.5** of the row (source baseline 9.2 pt
below the row's top edge on an 18.4 pt pitch). `w:vAlign="center"` is the only construct that lifts a
single line inside a row without also being a height, so it was built with the box:

- mobile-bill LibreOffice **47/47 → 45/47** (`18_displacement`, and `59_shape_anchor` 101 → 0)
- insurance-policy-schedule **47/47 → 46/47** (`18_displacement`)
- 68_journal unchanged at 40/42

A LibreOffice regression is a refusal, so it was reverted unmeasured in Google. **That is the one
thing this run did not find out: whether the box-at-pitch + centre pair fixes mobile-bill in Google
even though it costs LibreOffice.** The Google side was not measured; do not assume either way.

---

## What the next build has to solve, stated as arithmetic

For a single-line cell on a row whose floor binds, the three numbers cannot all be satisfied by one
paragraph:

| wanted | value |
|:--|:--|
| row height | the floor (360/360/380 tw) |
| baseline below the row's top | 0.5 × pitch = 184 tw (9.2 pt) |
| box, because Google honours nothing smaller | = the row's height, 360 tw |

`before + 0.8 × box = 184` with `before + box = 360` has no solution (it needs `box = 880 tw`,
taller than the row). **So the row height and the baseline cannot both come from one paragraph's
`spacing`.** Either the vertical position comes from a construct that is not a height
(`w:vAlign`, `w:tcMar`, a border-less spacer row), or the pitch has to be reached from the row and
`trHeight` has to be made to bind — and (1) and (3) say it cannot.

The one variant not tried: **`w:vAlign="center"` with `w:before` left as it is and the box at the
pitch minus `before`** — no. That is `before + box = pitch`, which table D of the probe measured to
lay the same sawtooth, and it puts the baseline at `before + 0.8·box`, which for `before = 184 − 0.8·360
< 0` is out of range. Recorded so the next run does not re-derive it.

The other variant not tried, and the cheapest: **`w:tcMar` top margin on the cell** to lift the text
inside a box at the pitch. `tcMar` is a margin, not a height, so Google should honour it the way it
honours `before` without charging it to the row — but `before` is also a margin and Google did not
charge *it* either, so the question is whether `tcMar` moves the text at all. **One probe answers it.**

## Blast radius, if a construct is found

16 documents fail `18_displacement` and nothing else; `classpick.py --leverage` prices the check at
**38.7 clean documents**. The three documents used here are the whole test set for the first build
because all three fail only this check:

    68_journal_wide_table_spanning   Google 41/42   LO 40/42   both failures: 18_displacement, 59_shape_anchor
    insurance-policy-schedule        Google 46/47   LO 47/47   only failure: 18_displacement
    mobile-bill                      Google 46/47   LO 47/47   only failure: 18_displacement

---

## The instrument, checked

`verify_google.py` on the HEAD export of mobile-bill returns 46/47 with `18_displacement` — the same
verdict as the committed `benchmarks/gverify/mobile-bill.json`. That agreement is why the negative
results above are trustworthy: the loop reproduces the recorded number before it is used to judge a
change.

Every Google PDF this run produced is described by its rule positions in this file. The probe
documents were deleted from `KavoPDF-Verify`; nothing else in the Drive was touched.
