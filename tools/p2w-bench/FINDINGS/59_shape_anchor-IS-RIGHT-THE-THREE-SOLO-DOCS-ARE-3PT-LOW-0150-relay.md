# `59_shape_anchor` is not wrong on the three solo documents — they sit 3.2–3.9 pt low, and 18 lets it through

**26 Nov 2026, relay fixer slot 01:25 IST · engine `981ff1fa35e2cf67` · no engine change landed.**
This is a measured lead, not a fix. Every number below is from a live Google round trip made in this
slot, and the check was instrumented to print the per-run offset rather than being trusted.

## Why this was worth measuring

The 24 Nov root-cause file (`DOCS-ROOT-CAUSES-24NOV.md:466-508`) says `59_shape_anchor`'s conviction
logic is wrong and that `_same_object` is dead code. `_same_object` **is** still defined and never
called at HEAD. The inference everyone has been carrying since is that the three documents whose only
failing check is 59 are instrument artefacts and would go clean if the check were fixed:

| document | committed verdict | 59 `source` / `render` |
|---|---|---|
| `351_omr_answer_sheet` | 41/42 | 66 / 59 |
| `48_form_coloured_border_coloured_values` | 41/42 | 24 / 18 |
| `52_one_cm_margin_wide_body` | 41/42 | 18 / 15 |

**That inference is false for all three.**

## Method — Google, not LibreOffice, and the same instrument on both arms

The three `.docx` were staged from `/scratch/work/p2w/out`, uploaded to `KavoPDF-Verify`
(`11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6`) as Google Docs, exported back as PDF and scored with
`verify_google.py` against the corpus source PDF. **The shipped instrument reproduced the committed
verdicts exactly** — 41/42, and the same `source`/`render` counts to the unit — so the renders are
the same renders the store was built from and the comparison below is apples to apples.

Two further documents that **pass** 59 on the same engine were rendered the same way as controls:
`303_discharge_summary` (47/47) and `320_balance_sheet_statutory` (47/47).

A copy of the instrument with one `print` after the `dy` computation was used for the distribution.
The shipped file was not modified.

## What the conviction actually is

Every convicted run on all three documents takes the **same-box** branch (`_same_box` true, the
rectangle reproduced within 2 pt) — no `lost`, no `_box_moved`. The text moved down inside a box that
did not move:

```
351_omr_answer_sheet   '15' dx 1.00 dy 3.20   box 20.0,20.0,575.3,821.9   gbox 19.0,19.0,576.2,823.0
                       '30' / '45' / '60' identical to the above
                       'Signature of candidate'  dx 0.75 dy 3.65
                       'Signature of invigilator' dx 0.65 dy 3.65
52_one_cm_margin       'Dividend declared on member shares' dx 0.62 dy 3.27
                       '12%' dx 0.70 dy 3.27   '14%' dx 0.45 dy 3.27
```

`ANCHOR_TOL_PT` is 3.0, so these are convictions **just over** the line, and that is exactly the kind
of number that looks like an instrument fault. The distribution says it is not.

## The distribution, five documents, same instrument, same renderer

`dy` for every judged same-box run, in points (Google render):

| document | n | median | p90 | max | 59 |
|---|---:|---:|---:|---:|---|
| `351_omr_answer_sheet` | 66 | +1.45 | +2.95 | +3.87 | FAIL |
| `48_form_coloured_border_coloured_values` | 24 | +2.55 | +3.26 | +3.41 | FAIL |
| `52_one_cm_margin_wide_body` | 18 | +0.69 | +3.27 | +3.27 | FAIL |
| `303_discharge_summary` | 22 | -0.16 | +0.34 | +0.34 | pass |
| `320_balance_sheet_statutory` | 64 | -0.40 | -0.39 | +0.74 | pass |

The two populations do not overlap at all: the failing documents' **p90** (+2.95 to +3.27) is above
the passing documents' **max** (+0.74). A systematic renderer offset would put both populations on the
same number — it does not. **These three documents carry a real vertical displacement of 3.2–3.9 pt,
and the check is reporting it correctly.**

## Why nobody has seen it

`18_displacement` sees the same runs and acquits them. Its per-run tolerance is
`clamp(0.35*size, 1.5, 4.5)` pt — for 8 pt text that is 2.8 pt, but its budget is 5 % of **every run
on the page** (hundreds), while 59's budget is 5 % of the **runs it can judge** (18–66 here). On
`351`, 6 of 66 judged runs is 9 %, over 59's budget; the same 6 runs against ~900 page runs is under
1 %, well inside 18's. So 18 passes, 59 fails, and the document is neither.

**`_same_object` is not the answer to these three.** Wiring the dead identity test in would not change
a single one of the convictions above: the boxes already agree within 2 pt, and the offsets are
measured against the *same* rectangle. The fix is engine-side.

## What the engine is doing — the shape of the lead, not a proven cause

`52`'s three convicted runs all sit in one table row, `(28.3, 378.3) → (528.3, 480.3)`, a 102 pt row,
and all three read the same +3.27 pt — the whole row's text is uniformly low inside a row whose own
outline is reproduced. `351`'s are the OMR label column and the two signature lines, +3.2 and +3.65.
Both are *content below something*: a cumulative, one-signed, uniform-per-block offset, not a
per-run scatter.

That is the signature the 0.75 pt row-quantum law (`18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`)
predicts, and it is **not** the construct-B falsification recorded on 25 Nov: there the *spacer* was
already spent and the residual was attributed to row pitch; here no spacer is involved — `52` and
`351` have one section each and 59 judges their text against a box that Google reproduced.

**Not proven, and the next run must not treat it as proven.** The cheapest discriminating test is
one document and one `p2w.dbgSpacer`-style instrumentation of `rowHeightTw` (`DocxWriter.java:6468`,
`:6516`): if the rows above the convicted block are declared at a pitch that is not a multiple of
0.75 pt, the +3.27 is that law and the fix is the declaration; if they are already on the ladder, the
lead is dead and the offset is in `place()`'s `w:before` solve instead.

## What this run did not do

No engine change, no instrument change, nothing committed to `app/` or `verify_google.py`. The corpus
was not re-measured — `regress.py --check` was run on the unchanged tree and passed, which is the only
thing this run can honestly claim about the corpus.

## Attempt 2 — the row declaration is NOT the lever here, and that is measured, not assumed

The first hypothesis the lead suggests is the 0.75 pt quantum law: `52`'s table declares six rows at
`w:trHeight w:val="340" w:hRule="atLeast"` (17.00 pt each), which is not a multiple of 0.75.

**Probe.** The `.docx` was rebuilt byte-for-byte with `w:hRule="atLeast"` switched to `"exact"` on all
six rows and nothing else changed (`/scratch/output/52_exact.docx`, 6 substitutions), uploaded to
`KavoPDF-Verify`, exported and scored.

**Result: Google's render is identical to the twip.**

| render | word baselines in the table band (y0, pt) | 59 |
|---|---|---|
| source PDF | 357.88 · 382.32 · 399.32 · 416.32 · 433.32 · 450.32 · 467.32 | — |
| Google, HEAD `.docx` | 358.35 · 381.70 · 400.11 · 417.36 · 433.45 · 451.86 · 469.86 | FAIL, source=18 render=15 |
| Google, `hRule="exact"` | 358.35 · 381.70 · 400.11 · 417.36 · 433.45 · 451.86 · 469.86 | FAIL, source=18 render=15 |

Not one baseline moved, and the verdict is unchanged to the unit. **`w:trHeight` does not control the
row pitch Google lays on this document.**

**What the pitches say instead.** Source row pitch is 17.00 pt, six times, exactly. Google's is
18.41 · 17.25 · 16.09 · 18.41 · 18.00 — **irregular, row by row, on a table whose six rows are declared
identically.** The rows are content-driven: the cell paragraph is
`w:spacing w:before="262" w:line="12" w:lineRule="exact"` on `w:sz=17` (8.5 pt) text, and Google does
not honour the 0.6 pt `w:line` — it takes the natural line height of the glyphs in that row, which
differs between a row of digits, a row of capitals and a row with descenders. The declared pitch is a
constant; the rendered pitch is a function of the row's own text.

That is a construct Google ignores (`w:line` + `lineRule="exact"` as a *height*, the same law recorded
for the table spacer at `DocxWriter.java:6107-6112`), one level down from where it was being looked
for.

## The next discriminating test — one document, one instrumented field

`52` is the right probe because all three convicted runs are in one row and the pitch series is short
enough to read by eye. The test is: instrument `rowHeightTw` (`DocxWriter.java:6468`, `:6516`) **and**
the cell paragraph's `w:before` / `w:line` emission, convert `52` alone, and check whether the engine
can express a row whose rendered pitch is 17.00 pt in Google without the row's text changing — i.e.
whether `w:trHeight hRule="exact"` at a height the content cannot exceed, or a `w:line` Google honours,
exists at all. If neither does, the honest verdict is that this 3.2 pt residual is **not expressible**
in .docx for Google, and the three documents belong in a written waiver with this measurement behind
them rather than in a fix queue.

## Reproduce

```
python3 tools/p2w-bench/verify_google.py /scratch/work/p2w/corpus/<doc>.pdf <google-export>.pdf \
        --docx /scratch/work/p2w/out/<doc>.docx --json /scratch/work/<doc>.json
```
Renders were made in `KavoPDF-Verify` (`11-mkegjnnIOmVdO7c44nDSgxrw2qkWn6`) and the five probe Docs
were deleted after measurement; nothing was left in the user's Drive.

## Attempt 3 — `w:line` cannot be relaxed either, and that closes the family

If Google ignores `w:line="12" w:lineRule="exact"` as a height and takes the row's natural line
height, the obvious counter-move is to stop asking for an exact line. Rebuilt `52` with all 37
`w:lineRule="exact"` → `"atLeast"` and rendered it in Google.

**Result: the document is destroyed, not improved.**

| render | page count | 59 | 18 | 23 line pitch |
|---|---:|---|---|---|
| source | 1 | — | — | 17.0 |
| Google, HEAD | 1 | FAIL 18/15 | pass | — |
| Google, `lineRule="atLeast"` | **2** | — | source=0 render=1 | **source 17.0 → render 23.0** |

The `.docx`'s whole vertical layout is carried by `w:line exact`; relaxing it re-flows the page onto
two sheets and changes the line pitch by 6 pt. So the construct is load-bearing and cannot be
traded away to buy a uniform row pitch.

**The family is closed for `52`:** `w:trHeight` (atLeast vs exact) makes no difference to Google
(attempt 2), and `w:line` cannot be relaxed at all (attempt 3). Google's row pitch here is a function
of the row's glyphs and no .docx construct this engine can emit fixes it. The remaining honest
question is whether the engine can express a fixed 17.00 pt row at all — and if it cannot, these three
documents belong in a written waiver, with these three probes behind it, rather than in a fourth run's
fix queue.
