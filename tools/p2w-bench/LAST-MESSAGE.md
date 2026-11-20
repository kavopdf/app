
  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
# P2W Fixer - Run Report

**20 Nov 2026 · slot 17:59 → running IST · 1h 32m**

> **itr-computation-with-slab-table** improved — 2.00 → 1.00. Corpus ratchet clean across 213 documents.

## What this run changed

The engine now measures a figure where its own line was drawn instead of from the welded cell box
that contains it, and `t13_amount_columns` is closed: no document fails it any more, where one did.

That one was `itr-computation-with-slab-table`, and the previous run had written it off as table
geometry needing a .docx measurement. It was a welded cell. A table cell's box is the x of its FIRST
drawn line, and on that document the cell holds the running head Page 1 of 1 above the figure
10,000.00 - three ruler columns apart. Measured from the box the figure landed one column right of
the six others in its own column. The per-line model already carried the figure's own x, so the
writer now reads it there, and uses that line's own base as the floor for where the figure starts;
keeping the box as the floor is what made the first version of this change move nothing.

The whole corpus was re-converted with the new engine and every row re-scored: one newly clean, none
newly failing, everything else unchanged, and the published ranking moved by a single line.
`regress.py --check` passes on the .txt scope.

Two things the next run should not have to rediscover, both written into FINDINGS. First, the class
table was a whole engine behind and claimed six documents on this class when five already passed,
because `classify_txt.py` had not been run after the last keep. Second, `p2w.py` measures origin's
head rather than the working tree, so a local edit has to be converted with `ConvertOne` out of the
clone or the measurement describes a different engine than the one being changed.

## The second attempt: t12 is not one construct

`t12_word_invention` was the next class the rotation handed over, and no engine change landed on it,
because the census showed it is not a single fault. Its documents split across annotation content the
source side cannot read, duplication across a page break, a welded cell in the .docx model, RTL
ordering, curved text arriving as single letters, and letter-spaced caps.

Three of them are the instrument's own artifact: the PDF text layer carries U+0000 as a zero-width
separator, the verifier splits words on non-whitespace so that NUL glues itself to the neighbouring
token, and its punctuation strip does not remove it - so the clean word the writer emitted is counted
as invented. Treating NUL as whitespace on the source side would clear those three and harm nothing.
The verifier was not touched: it is the instrument, and the finding is recorded instead.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 4 attempt(s), 1 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t12_word_invention` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 18:00 | **reverted** | 0/6 | claimed. .txt half. 6 documents still fail t13 per DEFECT-CLASSES-TXT: 22_invoice_four_columns_txtpos, 29_dot_leaders_txtpos, 74_balance_sheet_indented_subitems, balance-sheet-two-columns-of-figures, |
| 19:24 | **kept** | 1/0 | KEPT - the class is CLOSED, not parked: 0 of 213 documents fail t13_amount_columns (was 1). itr-computation-with-slab-table was not table geometry as the previous run concluded, it was a WELDED CELL: |
| 19:27 | **reverted** | 0/12 | claimed (second attempt, same slot). t12_word_invention, 12 documents, the biggest .txt class after t13 closed. Plan: read the check, census the invented tokens per document, group by mechanism (furni |
| 19:29 | **reverted** | 0/12 | NO ENGINE CHANGE LANDED - a measured census, which is the result. t12_word_invention is NOT one construct: the twelve documents carry at least five different faults. 21 of the words on 600_reviewed_in |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **182** (85.4%) |
| Failing at least one check | **31** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t13column census-01` | which of the six t13 documents still fail at head, t | 18:01 | 18:10 | 9 min |
| `t13itr weld fix-01` | implement and measure the TxtWriter change that clea | 18:11 | 18:34 | 23 min |

## Timing

| | |
|:--|:--|
| Slot window | 17:59 → running · 1h 32m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 25 |
| Longest silence | **55.3 min** — from 18:28:39, after `report.py: building the report` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 4 need a human |
| Still a wall | The fixer run 15:55-17:12 released its slot and its report was committed at 17:24 IST; `RUN-LOG.md` has no cla |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **58 min** | `##############` |
| record - attempt, handoff, class rows | **5 min** | `#` |
| report - the report and the chain | **29 min** | `#######` |
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
