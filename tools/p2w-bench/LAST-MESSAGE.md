# P2W Fixer - Run Report

**21 Nov 2026 · slot 13:54 → running IST · 56 min**

> **38_faux_bold_italic_synthesised** improved — 2.00 → 0.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 3 attempt(s), 2 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **21** files in 7 commit(s) from `a396617` — ATTEMPTS.json, CLASS-HISTORY.jsonl, ENGINE-STAMP.json, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, RANKING-TXT-BASELINE.csv, RANKING-TXT.csv, REPORT.md, RESTAMP-TXT.jsonl, ROTATION.json, ROUND.json, RUN-HISTORY.json, RUN- |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:42 | **kept** | 1/5 | clip-off: 411_nested_xobject_transforms t01 90.0->100.0, 12_stamp_across_page_break t12 also clean; corpus 186->188, 0 regressions |
| 14:42 | **kept** | 1/5 | doubled draw, both sides: 38_faux_bold_italic_synthesised fully clean (t01+t07 dropped); corpus 188->189, 0 regressions, 1 of 213 txt changed, 213 docx content identical |
| 14:49 | **reverted** | 0/3 | DUPLICATE, not a second fix. The relay claimed the slot at 14:11 and picked the same lead the :50 run landed at 14:21 (d2ea491, TEXT_MEDIABOX_CLIP). Found on the push: the commit was already on main. |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **189** (88.7%) |
| Failing at least one check | **24** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |


## The relay's slot

The claim was 27 min stale and the last run had died holding it - `status.py` said LIKELY DEAD, `health.py` said a run is still marked running but has not beaconed. Claimed at 14:11, released at the end.

**Two leads, one of them already done.** This run picked `t01_word_accuracy`, re-derived the MediaBox clip lead from `FINDINGS/411-nested-xobject-matrix-1940.md`, and measured it on 211 documents: 2 rows differ, both improved, none worse. On push it found the `:50` run had landed the identical line at 14:21. No credit taken - the 411 and 12_stamp movement is `d2ea491`'s. The independent second measurement is the value, because two builds and two harnesses agreeing is what makes the number believable.

**What that commit left stale, and this run repaired.** `d2ea491` rewrote two rows of `RANKING-TXT.csv` and stopped. `DEFECT-CLASSES-TXT.md` - the file `classpick.py` and `round.py` actually read - still said `t01_word_accuracy` 5 documents, `t12_word_invention` 9, 25 failing. Regenerated from the committed ranking: 3, 8, 24. A round could not have closed on the old table, and the next run would have been sent back to 411.

**Two writer changes killed by measurement**, so no run pays for them again: `39_small_caps_letter_spacing` `gs = g.sizePt` -> `g.size` takes it 97.4 -> 78.8; `38_faux_bold_italic_synthesised` dedupe window 40 -> 200 takes it 98.0 -> 93.0. The position-aware dedupe that did clear 38 is the version the agent called defensible - span-identical *and* position-identical - and it is the one that landed.

## The lead worth carrying

`39`'s hand-corrected `.txt`, the file a reader would produce, scores 58.2 where the broken one scores 97.4. The reference rewards the wrong file by about 39 points, because `get_text()`'s gap heuristic shatters a real word gap (570 005 arrives as 57 0 0 05) while the page draws a genuine space glyph at x = 355.8. Same shape as the clip: a MuPDF heuristic standing in for what the page draws. **Derive the source word boundaries from the drawn space glyphs in `get_texttrace()`, not from `get_text()`.** Not built - bigger than one line, needs the whole corpus.

## A gate hole, written up not fixed

`regress.py --check` passed an instrument edit with `scope of the change: nothing` and `txt: not re-measured`. The gate's fingerprint tracks the ENGINE; the verifier's own body is not in it. So a change to `verify_txt.py` lands without the gate asking for a measurement. It cost nothing today - both runs measured all 213 by hand - and it will cost something the first time a run edits a check and does not.


## Timing

| | |
|:--|:--|
| Slot window | 13:54 → running · 56 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 28 |
| Longest silence | **20.4 min** — from 13:54:18, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **`stage.py` can never print `measure-google` again, so the results with no engine stamp will never be re-meas |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **38 min** | `###############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **7 min** | `###` |
| other - not attributed to a tool | **9 min** | `####` |
