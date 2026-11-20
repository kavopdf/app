# Fixer report - 2026-11-20 22:54

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 22:54 → running IST · 29 min**

> **041122-Account_Opening_Form** improved — 7.00 → 4.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **2** — 2 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **21** files in 2 commit(s) from `952d58e` — ATTEMPTS.json, BLOCKERS.md, CAUSES-TXT.json, CENSUS-TXT.csv, CLASS-HISTORY.jsonl, DEFECT-CLASSES-TXT.md, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, RANKING-TXT-BASELINE.csv, RANKING-TXT.csv, REPORT.md, RESTAMP-TXT.jsonl, |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:16 | **kept** | 2/7 | SOURCE-SIDE HONESTY for a code the font itself cannot name. The two bank forms fail 7 of 10 checks each; 4 of those 7 were the same fault counted four times. pymupdf's /ToUnicode fallback prints the C |
| 23:23 | **reverted** | 0/5 | SECOND ATTEMPT, measurement only, no code changed. 601_fillable_admission_form loses exactly three tokens - '3', '3' and 'General'. The two '3's are ticked checkboxes: the page's /Resources name only |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t01_A-01` | is the U+FFFD glyph a ligature or a single letter, r | 23:20 | 17:50 | 0 min |
| `t01_B-01` | how many of the 213 documents a cmap-based recovery  | 23:20 | 17:50 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 22:54 → running · 29 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **11.3 min** — from 22:54:44, after `attempt.py: recording an attempt` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | the ligature identity at Effra CIDs 0x123/0x124/0x126/0x127 is not in the file: no cmap table in any embedded  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **10 min** | `########` |
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `########` |
| record - attempt, handoff, class rows | **4 min** | `###` |
| report - the report and the chain | **3 min** | `###` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

t01_word_accuracy holds 5 documents and two of those five is the bar. Two of them now have a measured, named cause and a fix shape, so start there rather than re-diagnosing. (1) 601_fillable_admission_form loses exactly three tokens and two of them are ticked checkboxes drawn in widget appearance streams as 'BT /ZaDb 9 Tf (3) Tj ET' - PDFBox never processes annotation appearance streams, so the engine emits nothing, which is real content loss on a filled form. FINDINGS/601-tick-is-a-widget-appearance-2342.md has the xrefs; the engine side is a glyph walk over each widget's /AP /N, the shape formValuesOf/widgetValue already have, and the instrument side already reads that stream in _ap_stream_text - both sides must call a /ZaDb glyph a tick or neither is honest. (2) 38_faux_bold_italic_synthesised loses the SECOND draw of its title because faux bold strokes the fill and the source carries 'PROJECT REPORT - CIVIL' twice while our .txt carries it once, which is correct; the 21:46 attempt that collapsed identical spans was REJECTED, so it needs a different construct. (3) 411_nested_xobject_transforms loses 'S' and 'O' - pymupdf and PDFBox disagree about a nested form's matrix and the rotated line runs off the page to y=-16.4. The two bank forms have LEFT this class; what is left on them is t06_encoding, t08_line_order and t09_page_furniture, which is the writer and not the font. Do not rebuild a ligature matcher: FINDINGS/ligature-identity-UNRECOVERABLE-2350.md proves the identity is not in the file.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
