# P2W Fixer - Run Report

**20 Nov 2026 · slot 20:58 → running IST · 1h 25m**

> **391_survey_questionnaire_grid** improved — 2.00 → 0.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **3** — 4 attempt(s), 2 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **23** files in 5 commit(s) from `e5268fe` — ATTEMPTS.json, CAUSES-TXT.json, CENSUS-TXT.csv, CLASS-HISTORY.jsonl, DEFECT-CLASSES-TXT.md, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, RANKING-TXT-BASELINE.csv, RANKING-TXT.csv, REPORT.md, RESTAMP-TXT.jsonl, ROTATION.jso |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 20:59 | **reverted** | 0/10 | claimed. t01_word_accuracy (.txt half, 10 documents). Failing: 041122-Account_Opening_Form, Account_Opening_Form_Fillable_filled, 38_faux_bold_italic_synthesised, 391_survey_questionnaire_grid, 39_sma |
| 21:22 | **kept** | 3/10 | CONTROL-CHAR TOKENISATION in verify_txt.py _words(). A PDF that declares U+0000 for a glyph with no Unicode of its own (a space between two words, a bullet, an empty MRZ cell) had its source words wel |
| 21:46 | **reverted** | 0/10 | SECOND ATTEMPT, both repairs on the source side of verify_txt.py, both restamped over 213 documents. (1) REJECTED: collapse a consecutive trace span whose text and bbox match the previous one within 0 |
| 21:49 | **kept** | 0/10 | CORPUS RATCHET for the control-character fix, not a new idea. All 213 documents were re-converted with this tree's engine and re-scored with the changed verifier (restamp_txt.py --run --force, 213 sco |

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
| `t01_verifier-tokenisation-01` | Does verify_txt.py's t01 tokenisation charge a corre | 21:02 | 21:20 | 18 min |
| `t01_writer-word-drop-01` | Which construct in TxtWriter.java/PdfToWord.java dro | 21:02 | 21:13 | 11 min |

## Timing

| | |
|:--|:--|
| Slot window | 20:58 → running · 1h 25m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 41 |
| Longest silence | **35.0 min** — from 21:49:36, after `report.py: building the report` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 2 need a human |
| Still a wall | **It is not - it is stalled at classify, and `health.py` cannot say so.** `stage.py` names `classify` as the s |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **28 min** | `#######` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **36 min** | `#########` |
| other - not attributed to a tool | **15 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

t01_word_accuracy, 7 open after this run. The engine /ToUnicode fix is the whole remaining win and it needs a full slot: 041122-Account_Opening_Form and Account_Opening_Form_Fillable_filled each carry 127 tokens of U+FFFD where the source declares U+0124/U+0126/U+0123, from REAQAG+Effra-Regular (Type0/Identity-H). Fixing it reads 99.95 and 99.76 - two documents - and it moves the docx fingerprint, so budget the 213-document docx re-measure with it. Land the widget /AP de-duplication from FINDINGS/t01_word_accuracy-REDRAW-AND-WIDGET-2155.md in the same attempt, not before it: on its own it is 601 96.4 -> 97.6 and nothing passes. Do NOT retry the redraw suppression - it is a t01/t12 trade, 0 newly clean and 1 newly failing, and the two lines it has to separate have identical trace bboxes.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
