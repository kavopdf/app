# P2W Fixer - Run Report

**20 Nov 2026 · slot 13:54 → running IST · 1h 18m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 3 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `47_margins` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:35 | **reverted** | 0/26 | anchorBox/lineParagraph: anchor at Box.inkX and strip the leading ASCII spaces, so a space-led anchored line's indent is a position instead of n space-advances of the rendering face. Measured reach by |
| 15:07 | **reverted** | 0/26 | g.size from getFontSize() (exact) instead of getFontSizeInPt() (rounded), gated OFF monospaced faces. The gate fires on 360 (8.5/8.0 DejaVuSerif) and not on 392 (6.6/6.0 DejaVuSansMono). Measured: 360 34.43 -> 34.43, 365 0.02 -> 0.02, 07_stamp_over_table 1.82 -> 1.82, 21_form_labels 0.00 -> 0.00 - a |
| 15:08 | **reverted** | 0/26 | CORRECTED 15:25 - the claim this row was first recorded with was wrong. The 'ungated' build turned out to be a NO-OP: the line it changed is semantically identical to HEAD's, so the docx it produced is HEAD's docx. What was read as '392 1.61 -> 0.06' is therefore HEAD's own score, not the patch's, a |

## What this run established

The class was being attacked from the wrong end, and nobody had counted. Every writer traced over all
26 documents of `47_margins`:

| construct | writer it reaches | documents | of 26 |
|:--|:--|--:|--:|
| leading-space indent | `flowFromBox` | 380, 383, 392 | 3 |
| leading-space indent | `anchorBox` | none - no anchored line in the class opens with a space | 0 |
| centred-line extent pin | `flowFromBox` | 07, 76, 317, 318, 404 | 5 |

The two sets do not overlap and the bar is 7, so neither construct, nor both, can keep an attempt on
this class. The handoff said to extend the space construct "to the table-cell emitter, where 40/77/78's
space-led lines live" - 40, 77 and 78 have no space-led line at all, and the cell emitters already
trim. That direction is closed.

Two committed leads are wrong and are now corrected in `SETTLED.md`. `run-size-from-sizePt-not-Tf` does
not take `360_restaurant_menu` from 34.43 to 1.31 - it moves it 0.25 - and it does not cost
`392_statistical_console_output` 12 points; 392 does not move at all. Worse, the tables do not describe
this engine: a pristine build scores 392 at 0.06 with 42 of 42 checks PASS, where `RANKING.csv` carries
1.61 and both gverify tables carry a `47_margins` FAIL. This class is at most 25 documents, and the
next run must measure against a fresh render.

I also caught myself: my first reading of that lead attributed 392's 0.06 to a patch that turned out to
be a no-op - the line I changed differed only by parentheses. The attempt record is corrected in place
rather than left standing.

The instrument now says where. `verify_google.py --detail` prints the two lists 47's verdict was
computed from and then threw away: `360_restaurant_menu`'s body column lands 12 pt left of the source's
(52 against 40) and nine runs are 11.9 pt out; `39_small_caps_letter_spacing` has 40 runs out, worst
48.3. That is what the next run has to aim at.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **179** (84.0%) |
| Failing at least one check | **34** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `47_mA-01` | which code path emits a table-cell line, and how a c | 14:02 | 08:37 | 4 min |
| `47_mB-01` | why 40_devanagari_shaping_font and 76_devanagari_tab | 14:02 | 08:46 | 13 min |

## Timing

| | |
|:--|:--|
| Slot window | 13:54 → running · 1h 18m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 33 |
| Longest silence | **28.3 min** — from 14:39:38, after `attempt 2 built: exact glyph size gated off monospaced faces` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | **This watchdog run has no `cron` tool**, so a paused or zombie cron cannot be moved by automation - a person  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 07m** | `###################` |
| record - attempt, handoff, class rows | **9 min** | `###` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

47_margins: re-measure the class against a fresh render, not the tables - 392_statistical_console_output already reads 0.06 and passes all 42 checks on this engine while RANKING.csv says 1.61 and both gverify tables say 47_margins FAIL, so the class is at most 25 documents. Then pull the thread FINDINGS/47_margins-REACH-140500.md leaves open: 360_restaurant_menu's body column was 12 pt left (source 52, render 40) and 9 runs are still 11.9 pt out; the leading-space indent and the centred-line constructs are both capped under the 25% bar and must not be retried.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
