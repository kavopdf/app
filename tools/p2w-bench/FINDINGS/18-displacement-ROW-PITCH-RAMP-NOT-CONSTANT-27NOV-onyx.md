# 18_displacement — on `table-with-no-header-row` the charge is a per-row RAMP, and `worst_dy` is a pairing artefact

**27 Nov 2026 · slot 16:06 · fixer `Onyx-Node` · diagnosis + measurement, no engine change kept.**

Engine `d28ca7516c3f9165` (the engine every stored row for this document carries). Converted with
`ConvertOne` at HEAD, rendered with `soffice --headless`, scored with `verify_google.py` itself.
Every number below is **measured in this slot** on the LibreOffice proxy, which for this document is
the renderer that reproduces the recorded Google verdict (`46/47`, `18_displacement` the only failure).

## 1. The reproduction

    ConvertOne corpus/table-with-no-header-row.pdf -> probe/   7 s, pages=1 paragraphs=5
    soffice --convert-to pdf                                    -> probe/table-with-no-header-row.pdf
    verify_google.py corpus.pdf probe.pdf --docx probe.docx     41/42 FAIL, 18_displacement

Recorded Google row: `46/47`, `med_dy -0.5`, `worst_dy 9.0`, 215 runs.
Measured LibreOffice here: `41/42`, `med_dy -4.9`, `worst_dy 101.4`, 215 runs.
The run count is identical, so the two renders are pairing the same population.

## 2. The page's own row grid, source against render

Both PDFs carry 32 text rows on page 1. Their baselines:

| row | source y | render y | dy |
|--:|--:|--:|--:|
| 3 | −329.6 | −328.9 | +0.7 |
| 4 | −311.2 | −311.0 | +0.2 |
| 8 | −237.6 | −239.4 | −1.8 |
| 12 | −164.0 | −167.8 | −3.8 |
| 16 | −90.4 | −96.2 | −5.8 |
| 20 | −16.8 | −24.6 | −7.8 |
| 24 | 56.8 | 47.0 | −9.8 |
| 28 | 130.4 | 118.6 | −11.8 |
| 29 | 150.5 | 138.5 | −12.0 |

**Pitch: source 18.4 pt, render 17.9 pt, on 26 consecutive gaps.** The declared `w:trHeight` on this
document is 360/380 tw = 18.0/19.0 pt, which `FINDINGS/18_displacement-trheight-175237-ab3f.md` already
established is the page's own pitch to 0.00 pt. The renderer lays 17.9 against a 18.4 declaration.

So the charge on this document is a **linear ramp of 0.44 pt per row, 0.7 → 12.0 pt over 27 rows**,
not a constant offset. `med_dy` (−4.9) is simply the value at the middle of the ramp; it has no
independent meaning.

## 3. `worst_dy 101.4` is not a displacement — it is the assignment

The largest pair in this render:

    d=101.4  src_ry=130.4  ren_ry=29.1  size=7.4  'Diesel'

Source row 130.4 is row 28 of the grid. Render y 29.1 is row 23. The same source row's other cells
pair as follows: `312`/`2,640` → 100.7 (row 27), `Surat`/`Chakan`/`8,302`/`30-10-2026` → 118.6 (row 28).
**One source row's cells are claimed by three different render rows, 5.5 rows apart at the widest.**

That is the greedy assignment in `verify_google.py:5626-5645` claiming the nearest *unused* occurrence
of a normalised string. On a header-less table of short numeric cells the same string occurs many
times, so when one occurrence is already taken the next-nearest wins — and the distance it wins at is
5.5 rows of pitch, which the check then reports as a 101 pt displacement.

`worst_dy` feeds the tail clause (`worst_here > TAIL_FACTOR = 2.0`, `:5872`), so a pairing artefact can
fail a page on its own. On this document the page fails on the **count** clause anyway (the ramp puts
most of the 26 rows past `_tol(7.4) = 2.59`), so the artefact changes no verdict here. **It is a hazard
to the fits, not to this verdict**: prior work in this class fitted corrections to `worst_dy` by
document (`18-displacement-TWO-CONSTRUCTS-27NOV.md`: "320 predicts 21×1.0 = 21.0 vs worst_dy 19.4").
If `worst_dy` can carry a 5.5-row pairing error, those fits were fitting noise.

## 4. What this changes for the next run

1. **Read `med_dy` and `worst_dy` as a ramp, not an offset, for any table document.** The recorded
   detail carries no per-row data, so the ramp is invisible in the store — this is the same gap
   `FINDINGS/18_displacement-PARTIAL-SPEND-IS-INERT...` named and it is still open.
2. **Do not fit a correction to `worst_dy` alone.** It needs the pairing checked first. A cheap
   guard: a pair whose `|dy|` exceeds 2× the page's own row pitch is more likely a mis-pair than a
   displacement, and should be counted separately rather than scored.
3. **The lever for this document is the row's laid pitch (18.4 → 17.9), not the declaration** (already
   exact) and not `LINE_BASE` (its whole lever is `0.8 × hairlinePt(size)` ≤ 0.52 pt, 20× too small).
   `FINDINGS/18_displacement-TRHEIGHT-HONOURED-LINEBOX-FLOOR-1130-relay.md` is the prior work at that
   site; nothing here overturns it.

## 5. Not measured, and why

The ramp was confirmed in **one** renderer on **one** document. Doing it for the 15-document small-dy
cluster needs a render of each, and the Google render of each needs a Drive round trip — there is no
cached Google export on the pod (`/scratch/work/p2w/gverify/gd` is empty, and `/scratch/work` does not
survive a run). That is the standing blocker for this class and it is why 57 attempts have steered by
`med_dy` alone.
