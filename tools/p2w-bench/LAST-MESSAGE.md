# P2W Fixer - Run Report

**25 Nov 2026 · slot 23:37 → running IST · 4 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8702** of 9320 (93.4%) on 213 documents |
| Check-instances still failing | **618** |
| Kept attempts vs documents clean | **15** classes with a kept attempt, **42** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 0 vs ATTEMPTS.json history 2 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (20 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |
| Committed | **14** files in 1 commit(s) from `7528a43` — ATTEMPTS.json.bak, CLASS-HISTORY.jsonl, HANDOFF-ARCHIVE.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, RANKING-TXT.csv, REPORT.md, ROUND.json, RUN-HISTORY.json, RUN-LOG.md, RUN.json, TIMELINE.jsonl, TRACE.md |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:37 | **lead** | 0/None | carry-on guard keyed on whether the line gets a paragraph copy: changed 1 of 213 docx, moved no score (txt 0 rows changed, docx share5 97.62->97.62); reverted. Welded-Y diagnosis disproved. |
| 23:37 | **lead** | 0/None | isJunk() treats U+FFFD as readable so decodeThroughFont never runs; adding it to the junk set made .txt surplus 127->141 on both forms; reverted. Real cause is a Type0 Identity-H font with no ToUnicod |


## The measurement, and what it killed

`t12_word_invention` failed 3 documents at the start of this slot. Two are the same form
(`041122-Account_Opening_Form`, `Account_Opening_Form_Fillable_filled`), and the 20:56 run had
diagnosed them as a **welded `Y`**: the carry-on rule at `PdfToWord.java:7904-7908` pulling
`(Authorised signatory)` out of the paragraph and into the last table cell, because the label
starts at x=153.46 and the table's right edge is at x=145.0. This run was told to print the glyph
and narrow the rule.

**Attempt 1 did exactly that**, in its narrow form: refuse the carry only when the glyph's own line
will be written as a paragraph anyway (line centre outside the table box), so the cell copy would
be a second copy by construction and refusing it cannot lose a character. It compiles, it converts,
and `corpus-changed.py --record` says it touched **1 document of 213**
(`Account_Opening_Form_Fillable_filled` - the rule does not even fire on `041122`). The scores:

| | before | after |
|:--|--:|--:|
| txt, 213 rows compared semantically | 204 clean | **204 clean**, 0 rows changed |
| `Account_Opening_Form_Fillable_filled` share@5px | 97.62 | **97.62** |
| its `chars_missing` | 131 | **131** |
| its `order_share` | 78.94 | **78.94** |

The guard fires, changes bytes, and moves nothing. Reverted.

**Attempt 2 counted the characters instead of trusting the diagnosis**, and the diagnosis is wrong.
Comparing the source PDF's own text layer with the engine's `.txt` on the committed engine:

| document | surplus in .txt | missing from .txt |
|:--|:--|:--|
| `Account_Opening_Form_Fillable_filled` | **127, all of them U+FFFD** | 127 = Hcircumflex 89 + Hstrok 23 + gbreve 13 + hstrok 2 |
| `041122-Account_Opening_Form` | **127, all of them U+FFFD** | 127, the same four letters |

127 for 127, one for one. Nothing is invented: **127 characters arrive as the Unicode replacement
character**, and `t12` counts a replacement character as a surplus because the source contains none.
The same 127 drive `t06_encoding`, which fails on the same two documents - one cause, two checks,
and `chars_missing = 131` on the .docx side.

The trigger is one line. `isJunk()` at `PdfToWord.java:2501` decides whether `tp.getUnicode()` is
readable, and only then does the glyph-name fallback `decodeThroughFont` (`:2513`) run. Its test is
"below 0x20, or 0x7F-0x9F, is a control code; everything else is text". `0xFFFD` is neither, so the
replacement character was taken as readable and the fallback never ran. The font is
`REAQAG+Effra-Regular` as a **Type0 / Identity-H** font with no usable ToUnicode; the WinAnsi
`TT0`/`TT1` copies of the same face decode fine.

Adding `if (c == '\uFFFD') continue;` compiles and converts, and **makes it worse**: the fallback
now runs and returns the replacement character anyway, while 14 real characters appear elsewhere -
surplus **127 -> 141** on both forms. A document getting worse, so it does not land. Reverted;
`git diff app/` is empty.

## What the next run should do

The fix has to come from the font, not from the layout.
`FINDINGS/25NOV-T12-IS-U-FFFD-NOT-A-WELDED-Y.md` has the numbers and the order of probes. Short
version: print `font.getEncoding().getName(code)` and `tp.getCharacterCodes()` for a Type0 glyph;
if the encoding names the glyphs, `decodeThroughFont` is calling the wrong overload. If it does not,
the answer is the embedded TrueType **cmap read by GID** - for Identity-H the code *is* the glyph
id, and MuPDF gets `Hcircumflex` from exactly that table. That is a cmap subtable parser and it is
the whole fix.

**Do not touch the carry-on rule for these documents again.** It is measured dead here. The narrow
form is kept in the finding because it cannot lose a character by construction, so it is the right
shape if a future class needs it.

`18_displacement` is still the largest lever in the corpus - **54.8** clean documents - and the
second agent returned a pre-registered prediction for it: Google charges a ruled row's rule **on top
of** `w:trHeight` while LibreOffice charges it inside (1.115 pt of growth per row in Google against
0.130 in LibreOffice, over 52 and 75 measured rows), and the row-pitch hypothesis the last run was
handed is dead - a 9-arm Google probe already laid cell `w:line` at 15.00 on all 16 rows. That is
the next run's class, and it is a number, not a guess.

## The txt

| | |
|:--|:--|
| Measured | **21 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **204** (95.8%) |
| Failing at least one check | **9** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 23:37 → running · 5 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 22 |
| Longest silence | **4.2 min** — from 23:37:47, after `gate + commit` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| other - not attributed to a tool | **4 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |


## The corpus, checked

The corpus was rebuilt on the reverted tree and **0 of 213** documents differ from the committed
`DOCX-HASHES.json`. That is the independent proof both reverts are complete, and it is not the tool
that made the change.

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 12 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 13 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 11 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 9 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 10 item(s) you can close - run pending.py and take them in its order before the class below. classpick --leverage picks the class; six checks can make a document clean (18_displacement 25, 60_text_column_right_edge 6, 47_margins 3, 59_shape_anchor 3, 32_stroke_lines 2, 17_matched_runs 1) and they are weighted 3x over the 34 that cannot. Read pending.py first, then take the class it gives.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
