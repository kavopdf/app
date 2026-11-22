# 18_displacement — the table-top spacer is REFUTED as the cause of the 16 solo documents

22 Nov, slot 08:16 → · class `18_displacement` · outcome **reverted**, 1 of 16 moved, best drop 0.85

The 07:14 run left one instruction: the gap above a table is written as `w:line` on a 1 pt mark,
Google reads `w:line` as a multiple of the face's line height, so `68_journal_wide_table_spanning`'s
144.0 pt spacer may render as 13.74 pt, and one Drive probe would settle it.

**It was built, it was measured, and the premise was already contradicted by the table the run was
reading.** Both halves are recorded here so neither is paid for twice.

---

## 1. The construct was real, and the fix is the right fix for that construct

`DocxWriter.java:5869` wrote the gap above a table as

    <w:p><w:pPr><w:snapToGrid w:val="0"/>
      <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0" w:after="0"
                 w:line="2880" w:lineRule="exact"/>
      <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>

Google renders `w:line` as `(w:line / 240) * lineHeight(face, size)` — measured through Drive on
purpose-built probes and recorded in `REMAINING-DEFECTS.md` (class `20_within_10pt`, re-measured
12 Nov, three probes differing only in how one 12 pt advance is written). So 2880 twips on a
`w:sz=2` mark is 12 × 1.145 = **13.74 pt, not 144 pt**. `w:before` is the one vertical length Google
reads as a length: 20/40/80/120/160 pt all came back exact, and with the box cut to a hairline the
advance is `before + 0.069 * size`, font-independent.

The engine's own bookkeeping already charged the full `spacerTw` (`ctx.flowTw += spacerTw`,
`cenSetY(flowTopPt + spacerTw / TWIPS_PER_PT)`). Only the emitted paragraph told Google a smaller
number. So the change was to write the gap as `w:before` with the box cut to `w:line="1"`:

    <w:spacing ... w:before="2880" w:after="0" w:line="1" w:lineRule="exact"/>

Confirmed in the emitted document, not assumed: `word/document.xml` of the screened
`68_journal_wide_table_spanning.docx` carries `w:before="2880" ... w:line="1" w:lineRule="exact"`.
The paragraph immediately above it already uses the same model (`w:before="204" w:line="12"`), so
the page body had been converted and the table spacer was the last path still on `w:line`.

## 2. What it measured — 1 of 16, and the one by 0.85

Sixteen documents screened through Google on the patched engine (`screen.py --docs`, engine
`462353f9+b10039bbc4`), none worse:

| document | before | after | change |
|:--|--:|--:|--:|
| `68_journal_wide_table_spanning` | 12.09 | 11.24 | −0.85 |
| the other 15 | — | — | **unchanged** |

The bar is `max(2, 25 % of 16)` = 4 documents. One moved. Reverted.

**The reason it did nothing is that the table did not move.** The measured displacement of
`68_journal` after the change is median 1.92 pt, p90 3.84 pt, max **8.64 pt** — identical, to the
hundredth, to its row in `benchmarks/RANKING.csv`. A spacer that had been charged 13.74 pt instead
of 144 pt would put every line below the table at dy ≈ −130 pt. Nothing in the render is 130 pt
from where it belongs.

## 3. Why the premise was already refuted before it was built

`RANKING.csv` carries `max_pt` for every document. For the sixteen it is **1.44 to 17.76 pt**:

| document | share@5 | median pt | p90 pt | max pt |
|:--|--:|--:|--:|--:|
| `31_times_body_arial_headings` | 1.04 | 0.96 | 1.92 | 17.76 |
| `mobile-bill` | 1.55 | 1.44 | 1.92 | 16.80 |
| `bus-timetable-station-left-times-right` | 0.27 | 0.96 | 1.92 | 12.96 |
| `table-with-no-header-row` | 0.61 | 0.96 | 1.92 | 11.52 |
| `71_invoice_space_aligned_no_rules` | 26.88 | 3.84 | 6.24 | 9.12 |
| `68_journal_wide_table_spanning` | 12.09 | 1.92 | 3.84 | 8.64 |
| `insurance-policy-schedule` | 0.53 | 0.96 | 1.92 | 8.64 |
| `balance-sheet-two-columns-of-figures` | 0.57 | 0.96 | 1.92 | 5.76 |
| `two-tables-stacked-with-no-gap` | 0.77 | 0.96 | 1.92 | 5.28 |
| `362_price_list_dense` | 0.03 | 0.96 | 1.92 | 3.36 |
| `16_right_aligned_amounts_txtpos` | 0.00 | 0.96 | 1.44 | 2.40 |
| `29_dot_leaders_txtpos` | 0.00 | 0.96 | 1.44 | 2.40 |
| `72_bank_statement_no_rules_right_amounts` | 0.00 | 0.96 | 1.44 | 2.40 |
| `22_invoice_four_columns_txtpos` | 0.00 | 0.96 | 1.44 | 1.44 |
| `41_coloured_headings_white_bg` | 0.00 | 0.96 | 1.44 | 1.44 |
| `73_marksheet_subject_marks_grade` | 0.00 | 0.96 | 0.96 | 1.44 |

The −114.8 pt figure the lead was built on comes from a FINDINGS measurement of `68_journal` at
HEAD. `RANKING.csv` gives that same document `max_pt` 8.64. **Two records of one document disagree
by a factor of thirteen**, and the table is the one the gate and the ratchet treat as truth. The
spacer is a real construct with a real defect; it is not what fails these sixteen.

## 4. The `median_pt` 0.96 is the STATISTIC'S FLOOR, not a two-pixel page offset

The first reading of the table above was that fourteen of the sixteen sit at `median_pt` 0.96 or 1.44,
that one pixel is 0.48 pt at 150 DPI, and therefore the whole page is offset by two or three pixels
uniformly — one constant, not sixteen constructs. **That reading is wrong, and the code says so.**

`benchmarks/p2w.py`, `position()`:

    d,_ = edt(om, sm.shape)      # distance_transform_edt(...).astype(np.int32)  - INTEGER pixels
    un  = sm & (d > 1)           # every pixel at distance 0 or 1 is EXCLUDED
    dv  = d[un]
    median_pt = round(float(np.percentile(dv,50)) * PT, 2)     # PT = 72/150 = 0.48

`dv` holds integers and is filtered to `d > 1`, so the smallest value it can ever contain is 2, and
**`median_pt` can never print below 0.96**. 0.96 is the floor of the statistic. It is also the worst
page's value, not a page average. Reading it as "the page is two pixels out" is reading the
instrument's own quantisation as a measurement.

It is self-contradicting on its own terms as well: `18_displacement`'s tolerance is
`clamp(0.35 * size, 1.5, 4.5)` pt, so a genuine uniform 0.96 pt offset is *inside the floor and would
pass*. A number below the check's own floor cannot be the reason the check fails.

**What the sixteen actually are, then, is still open — but it is a tail, not a shift.** `p90_pt` runs
1.44 to 6.24 and `max_pt` 1.44 to 17.76: three to thirty-seven pixels, on a minority of the ink, not
two pixels on all of it.

## 4b. Six of the sixteen are under the check's own floor — the two instruments disagree

This is the sharpest thing in the run and it is a question, not an answer. These six have an ink
displacement that cannot fail a 1.5 pt tolerance:

| document | share@5 | p90 pt | max pt |
|:--|--:|--:|--:|
| `22_invoice_four_columns_txtpos` | 0.00 | 1.44 | 1.44 |
| `41_coloured_headings_white_bg` | 0.00 | 1.44 | 1.44 |
| `73_marksheet_subject_marks_grade` | 0.00 | 0.96 | 1.44 |
| `16_right_aligned_amounts_txtpos` | 0.00 | 1.44 | 2.40 |
| `29_dot_leaders_txtpos` | 0.00 | 1.44 | 2.40 |
| `72_bank_statement_no_rules_right_amounts` | 0.00 | 1.44 | 2.40 |

`18_displacement` fails them, and `RANKING.csv` says the largest ink displacement anywhere on the page
is 1.44–2.40 pt, under the 1.5 pt floor for every face size. **The two instruments are measuring
different quantities.** Either the check's dy is not the ranking's dy, or the check's population is
not the ranking's population. Until that is settled, "displacement" is unproven for six of the
sixteen and nothing should be built for them — the 18.6 clean documents the class is worth may be
partly an artefact of the check, not of the engine.

`71_invoice_space_aligned_no_rules` is the opposite case and a different question: share@5 26.88 with
`median_pt` 3.84 — genuinely displaced, and no table spacer at all.

## 5. A tool bug found on the way — screen.py measured nothing on a fresh pod

`screen.py` set `p2w.REPO` after importing `benchmarks/p2w.py`, but `p2w.py` computes
`ENGINE_SRC = os.environ.get("P2W_ENGINE_SRC") or REPO` **at module level**, from
`ROOT + "/repo"`. On a pod with no previous run that directory does not exist, so every `ConvertOne`
was invoked with a classpath under it, died on `ClassNotFoundException` in under a second, and
nothing reached `dist/`. The tool then printed

    PARTIAL - 0 of 16 measured. Call again; the cache carries over.

for ever. Measured: the identical command with `P2W_ENGINE_SRC` set converted and measured 16 of 16.

This is the most expensive shape a bug can have here — it does not say it could not run, it says the
idea did nothing, and the brief's next line tells the run to revert. Fixed in `screen.py` by setting
`p2w.ENGINE_SRC = REPO` beside `p2w.REPO`, and verified: 0 of 2 measured before, 2 of 2 after, with
no environment variable.

## 6. Provenance of every number above

- 16 documents, and the fact that they are exactly those failing only `18_displacement`: counted
  from `benchmarks/gverify/*.json`, `failed == ["18_displacement"]`, 213 files read.
- before/after and all `*_pt` columns: `benchmarks/RANKING.csv` and
  `/scratch/work/p2w/screen-out/dist/68_journal_wide_table_spanning.json` (engine `462353f9+b10039bbc4`).
- the `w:line` model: `REMAINING-DEFECTS.md`, class `20_within_10pt`, §"The model, measured".
- the emitted XML: `word/document.xml` of the screened `.docx`, read directly.
- the engine change was reverted with `git checkout -- app/src/.../DocxWriter.java`; `git status`
  shows no engine file modified.
