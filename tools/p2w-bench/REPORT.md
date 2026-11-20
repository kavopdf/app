# Fixer report - 2026-11-20 22:54

```
# P2W Fixer - Run Report

**20 Nov 2026 · slot 22:54 → running IST · 27 min**

> **041122-Account_Opening_Form** improved — 7.00 → 4.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **2** — 1 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **19** files in 1 commit(s) from `0580c1b` — ATTEMPTS.json, BLOCKERS.md, CAUSES-TXT.json, CENSUS-TXT.csv, CLASS-HISTORY.jsonl, DEFECT-CLASSES-TXT.md, HANDOFF.json, HANDOFF.md, RANKING-TXT-BASELINE.csv, RANKING-TXT.csv, RESTAMP-TXT.jsonl, ROUND.json, RUN-LOG.md, RUN |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:16 | **kept** | 2/7 | SOURCE-SIDE HONESTY for a code the font itself cannot name. The two bank forms fail 7 of 10 checks each; 4 of those 7 were the same fault counted four times. pymupdf's /ToUnicode fallback prints the C |

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
| Slot window | 22:54 → running · 27 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 18 |
| Longest silence | **11.3 min** — from 22:54:44, after `attempt.py: recording an attempt` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | the ligature identity at Effra CIDs 0x123/0x124/0x126/0x127 is not in the file: no cmap table in any embedded  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **10 min** | `########` |
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `#########` |
| record - attempt, handoff, class rows | **4 min** | `###` |
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

The 127 U+FFFD on the two bank forms are SETTLED on both sides: the glyphs are ff/fi/ffi/ffl, read from the FontFile2 outlines, and the ligature IDENTITY is not in the file - no cmap in any of 303 embedded programs, no glyph names, no GSUB, and both the /W widths and the glyf outlines leave ffi vs ffl and fi vs fl ambiguous. FINDINGS/ligature-identity-UNRECOVERABLE-2350.md has the numbers; do not rebuild a width or outline matcher. What is left for those two documents is t06_encoding (127 U+FFFD in the .txt), t08_line_order (40 of 461 out of order) and t09_page_furniture (197 where 21 are owed) - the .docx/.txt writer, not the font. t01_word_accuracy now holds 5 documents: 38_faux_bold_italic_synthesised, 39_small_caps_letter_spacing, 411_nested_xobject_transforms, 601_fillable_admission_form and 77_arabic_rtl_document. Two of those five is the bar. 38 loses the SECOND draw of its title - the source carries 'PROJECT REPORT - CIVIL' twice because faux bold strokes the fill, and our .txt carries it once, which is right; that is a source-side duplicate, and the 21:46 attempt that collapsed identical spans was REJECTED, so it needs a different construct. 411 loses 'S' and 'O': pymupdf and PDFBox disagree about a nested form's /Matrix and the rotated line runs off the page (y to -16.4). 601 loses two ZapfDingbats checkmarks that PDFBox never delivers - they are drawn in a widget appearance stream, and the source calls a tick '3', so both sides need the same fix or neither is honest.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
