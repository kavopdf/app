# P2W Fixer - Run Report

**24 Nov 2026 · slot 08:18 → running IST · 2 min**

> **`60_text_column_right_edge` is not a layout class, and four of its five single-check documents
> cannot be fixed by anything the engine writes.** They are **42/42 in LibreOffice** and fail only in
> Google, because the source PDF is set in **DejaVu**, Google has no DejaVu, and the substitute it
> picks is **4.8 % wider** - which re-breaks page 0 of `302_radiology_report` from 33 lines to 35 and
> moves a column's right edge by **28.6 pt**. Naming a face Google has moves the fault into
> LibreOffice instead; **embedding the face in the `.docx` is ignored by Google**, measured.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **34** of the **186** re-measured on this engine - **4** of the 190 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 08:05 | **lead** | 0 | `60_text_column_right_edge`. All five documents that fail only it were converted on this engine and scored against their own source with the unmodified checker: **302, 313, 316 and 321 are 42/42 in LibreOffice**; only `79_inr_indian_digit_grouping_table` fails in both renderers. The class is two disjoint halves, not one. |
| 08:14 | **lead** | 0 | The Google half, three live round trips on `302_radiology_report`. As built: 41/42, fails 60. Its export carries **Calibri, Verdana, ArialMT** where the source and our `.docx` both say **DejaVuSans/DejaVuSerif**; page 0 is 35 lines against the source's 33 and the first line is 270.00 pt against 257.62. Naming Verdana/Georgia instead: LibreOffice falls back to Noto, first line 227.63 pt, the render stops being the source's face. Embedding both faces in the package: Google's export is the **same** three substituted families and the same 35 lines, 81,521 bytes against 81,526 - **the embedded face is not read**. |
| 08:20 | **lead** | 0 | `18_displacement`, two agents, both committed to `FINDINGS/`. A 14-document guard census: **5 of the 14 already spend their table-top spacer and still fail**, so the page-height guard is not why the spacer is unspent; the unruled-row-excess patch is LibreOffice-invariant (identical sha256 rasters) and buys 3.93 pt of a 13.0 pt displacement - **it cleans nothing**. An instrument audit: the verdict is a per-page **count** beyond `clamp(0.35*size, 1.5, 4.5)` pt, not `med_dy`; a rigid uniform shift of a real page by 2.0 pt fails it while one line overlapping another by 5.16 pt passes. |

## What was decided, and why

**The class was `60_text_column_right_edge`, taken on the only question that matters: which documents
become CLEAN.** Five documents fail *only* it, so all five were one check from done. Four of them are
now known to be unfixable by any construct the engine can emit, and that is a **`Google cannot do it`**
verdict with two probes behind it rather than a guess. The fifth, `79`, has a real engine defect -
page 0, column left 132.3 pt, source right edge 289.97 pt against the render's **149.70 pt** - and it
is reproducible in LibreOffice, so the next run can iterate it without a Drive round trip.

`18_displacement` was **not** worked as an engine change. The 04:52 and 05:59 findings already measured
the row-half patch and refuted it on the proxy bar (`362` 0.03 → 0.04 share@5), and the guard census
this run removes the last reason to think the spacer half is guard-blocked. Both halves are behind a
full corpus pass and neither has a construct that both renderers accept.

## The txt

| | |
|:--|:--|
| Measured | **23 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-05` | is the page-height guard why no table-top spacer is  | 08:20 | - | - |
| `60_tB-01` | is 60 or 18 reading the paper instead of the defect  | 08:20 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 08:18 → running · 2 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 8 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **1 min** | `############` |
| report - the report and the chain | **1 min** | `##########` |
## What the next run should do

1. **Take `79_inr_indian_digit_grouping_table`.** It is the only document in this class with an engine
   defect and it fails in **both** renderers, so it can be worked without a Drive round trip. Its
   failing column is named above. It is one document from CLEAN.
2. **Do not work 302, 313, 316 or 321 as a layout class.** The engine's columns are the source's
   columns to 0.2 pt in LibreOffice and the `.docx` names the source's own face. The residual belongs
   to `53_embedded_faces`, which currently PASSES them. If `60` is to stop convicting a re-break fully
   explained by a face the renderer does not have, that must be written as a rule about
   extent-versus-substitution and re-measured on the whole class - **not loosened for four documents.**
3. **`18_displacement`'s instrument question is now the live one**, not the construct. `18`'s own
   comment says it is "calibrated against what a user SEES"; agent B's control shows a 5.16 pt ink
   overlap passing and an invisible uniform shift failing. That is a check measuring the paper, and it
   is the same shape as `25_invisible_text`, which took 5 documents to 42/42 last run.
