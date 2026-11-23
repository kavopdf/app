# P2W Fixer - Run Report

**23 Nov 2026 · slot 19:57 → running IST · 48 min**

> One attempt, measured in Google before and after, refuted. Two agents landed with findings. Nothing kept: the construct that looked like it would turn documents clean buys nothing in the renderer the user opens and costs LibreOffice 30-36 share@5.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| **Fixed - Google, every applicable check** | **13** of the **63** re-measured on this engine - **127** of the 190 scored are still on an older engine |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

The class was chosen because it is the largest prize in `classpick.py --leverage` (18_displacement, 34.5 in clean documents) and because the previous run left a measured lead: `patches/18-spacer-before-rowpitch-rowrule.patch` was recorded at 2 documents CLEAN in Google but never ratcheted.

**Attempt 1 (20:44, reverted, 0/16).** Agent B's construct — `w:trHeight = pitch − 20 tw` plus a cell bottom margin — applied to the engine, built, and taken through four live Google round trips.

| document | HEAD | HEAD + construct | failed check |
|:--|--:|--:|:--|
| table-with-no-header-row | 46/47 | 46/47 | `18_displacement` |
| mobile-bill | 46/47 | 46/47 | `18_displacement` |

The construct reached the output (26 rows at `w:trHeight 348`, `w:tcMar bottom 154`), so this is Google not honouring the prediction, not a dead code path. Independent PyMuPDF geometry on the same exports says why:

| render | first line dy | ramp across the table | rule pitches | table span |
|:--|--:|--:|:--|--:|
| source PDF | — | — | 18.40 uniform | 478 pt |
| Google, HEAD | −10.16 pt | 16.25 pt | 18.0 / 19.0 / 20.0 | 495 pt |
| Google, HEAD + construct | −10.16 pt | 8.38 pt | 18.0 / 19.0 | 482 pt |

The row construct halves the drift and still fails, because **the first line of the block is 10.16 pt high in both renders** and mobile-bill starts at −15.75 pt. What check 18 still charges is a per-document offset at the top of the block, which no row-height number can move. The construct also costs LibreOffice 30-36 share@5 on four documents (agent A and agent B, independently). Reverted; no engine change landed.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed |
|:--|:--|--:|:--|
| `18A-01` | is the LO regression on the spacer+trHeight patch a real layout change or a proxy artefact | 20:15 | `FINDINGS/18_displacement-LO-PROXY-VERDICT-2013-agentA.md` |
| `18B-01` | is there a construct that gives Google the row pitch without changing what LibreOffice draws | 20:44 | `FINDINGS/18_displacement-TRHEIGHT-CROSS-RENDERER-1506-agentB.md` |

Agent A settled the proxy question: the LibreOffice 30-36 is a real 20-26 pt table compression (the `w:trHeight` half of the patch), not a soffice artefact, and its independent line check agrees with share@5. Agent B found the one construct that lays 18.40 pt on all 26 rows in LibreOffice and named its cost — which my round trips then showed buys nothing in Google.

## Next run

Stop spending attempts on row pitch. The measured residual on `table-with-no-header-row` is a −10.16 pt offset at the top of the block (mobile-bill −15.75 pt), identical with and without the row construct. The leading paragraph carries its vertical position in `w:spacing w:before="1040"` with `w:line="13" w:lineRule="exact"`, and the Google column of `GVERIFY-BRIEF.md` lists `w:spacing` as ignored. Build one variant that carries the same position without `w:spacing` (an exact-height empty paragraph, or `w:ind`/`w:framePr`), round trip the same document, and read the first line's dy. It is −10.16 now; if it does not move, the carrier is not the spacing and this lead is dead. Then repeat on mobile-bill before anything is committed, because a per-document offset is not a construct.

Also open: the two agents' findings are committed, the `18_displacement` class now has 40 recorded attempts, and `patches/18-spacer-before-rowpitch-rowrule.patch` should not be applied to HEAD — it no longer applies (HEAD carries a guarded spacer split) and its row half is the part that costs LibreOffice.

## Timing

| | |
|:--|:--|
| Slot window | 19:57 → running · 48 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **23.8 min** — from 20:15:19, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **42 min** | `###################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **4 min** | `##` |

> The 23.8 min silence is the two agents: a scheduled run returns them inline, and the second one
> ran to its 22-minute budget. It is the run's only silence and it is why both findings exist.
