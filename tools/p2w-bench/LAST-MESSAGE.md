# P2W Fixer - Run Report

**21 Nov 2026 · slot 13:54 → running IST · 51 min**

> **38_faux_bold_italic_synthesised** improved — 2.00 → 0.00. Corpus ratchet clean across 213 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 2 attempt(s), 2 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **21** files in 5 commit(s) from `f702b40` — ATTEMPTS.json, CLASS-HISTORY.jsonl, ENGINE-STAMP.json, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, RANKING-TXT-BASELINE.csv, RANKING-TXT.csv, REPORT.md, RESTAMP-TXT.jsonl, ROTATION.json, ROUND.json, RUN-HISTORY.json, RUN- |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:42 | **kept** | 1/5 | clip-off: 411_nested_xobject_transforms t01 90.0->100.0, 12_stamp_across_page_break t12 also clean; corpus 186->188, 0 regressions |
| 14:42 | **kept** | 1/5 | doubled draw, both sides: 38_faux_bold_italic_synthesised fully clean (t01+t07 dropped); corpus 188->189, 0 regressions, 1 of 213 txt changed, 213 docx content identical |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **189** (88.7%) |
| Failing at least one check | **24** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t01lostwords-01` | which words each of the five documents loses, and wh | 13:57 | 14:06 | 9 min |
| `t01blastradius-01` | which of 213 documents change verdict under the two  | 13:57 | 14:08 | 11 min |

## Timing

| | |
|:--|:--|
| Slot window | 13:54 → running · 51 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 27 |
| Longest silence | **20.4 min** — from 13:54:18, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **`stage.py` can never print `measure-google` again, so the results with no engine stamp will never be re-meas |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **38 min** | `################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **2 min** | `#` |
| other - not attributed to a tool | **9 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## What the .txt work was, and why the .docx table is right to be still

The class was `t01_word_accuracy` (5 documents). Two attempts, both kept, and both were
source-side or writer-side faults rather than a converter that could not draw:

* **The check clipped the page to the media box.** `get_text()` with its default flags drops
  a line drawn even slightly outside the media box from the SOURCE word list, so the writer
  was charged for a word it had faithfully emitted. On `411_nested_xobject_transforms` a
  rotated heading at y = -2.5..-16.4 survived as the two stray characters S and O.
* **A line drawn more than once at one place is one line** - and both sides got it wrong.
  Faux bold draws the same string two or three times at an identical bounding box; the writer
  built two paragraphs from the overlapping draws, and the check counted every copy. Fixed
  together, because each half alone was a wash: the check alone moved the fault to `t12`, the
  writer alone gained nothing while the check still charged it.

The `.docx` table did not move, and that is the correct answer, not an omission. `scope.py`
named `TxtWriter.write` and `TxtWriter.appendPara` - scope `txt`. Proved rather than trusted:
the whole corpus converted to `.docx` on the patched tree and on HEAD, every zip member
compared - 213 of 213 identical, 0 differing.

## Next run

`t01_word_accuracy` is down to three documents and none of them is a clipping or a doubling
fault. `FINDINGS/t01-doubled-draw-both-sides-142100.md` carries the measurement for each:

* `39_small_caps_letter_spacing` and `77_arabic_rtl_document` are **word-boundary
  disagreements** between PyMuPDF and PDFBox, in opposite directions. Both already fail `t12`
  too, which is the signature of segmentation rather than missing content. A segmentation
  change moves both t01 and t12 on every RTL and letter-spaced document and needs its own
  blast radius before it lands.
* `601_fillable_admission_form` is the only genuine writer-side loss left: the two ticks exist
  only in widget `/AP` streams and PDFBox never walks appearances. That is a `convert()` change
  - scope BOTH - so it needs the `.docx` score measured, not just its bytes proved.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
