# P2W Fixer - Run Report

**20 Nov 2026 · slot 03:53 → running IST · 20 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.44%** — mean 6.15 → 3.72 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed to 99%** | **32** of 213 — the rest are still off |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-present-partly-displaced` |
| Committed | **15** files in 2 commit(s) from `319035a` — ...artly-displaced-rules-cannot-flow-044000-f1x.md, ATTEMPTS.json, BLOCKERS.md, CLASS-HISTORY.jsonl, DEFECT-CLASSES.md, HANDOFF.json, HANDOFF.md, ROUND.json, RUN-LOG.md, RUN.json, TIMELINE.jsonl, TRACE.md, classrow-colum |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:03 | **error** | 0/23 | no fix was built or measured, on purpose: the pBdr rule change cannot work until a rule is written before the text below it. PdfToWord.attachShapes appends shapes to page.blocks AFTER the paragraphs ( |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **167** (78.4%) |
| Failing at least one check | **46** |
| Most common failure | `t13_amount_columns` - 18 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `contA-06` | after rules become w:pBdr, which construct still emi | 03:54 | 22:34 | 10 min |
| `contB-06` | mobile-bill share5 43.87 and electricity-bill 46.85  | 03:54 | 22:43 | 19 min |

## Timing

| | |
|:--|:--|
| Slot window | 03:53 → running · 20 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 27 |
| Longest silence | **9.5 min** — from 03:54:06, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 2 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **18 min** | `####################` |
| record - attempt, handoff, class rows | **2 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

## What the tables cannot show

No engine change was kept, and that is the finding rather than an accident. The largest class in the
corpus is rules: a horizontal rule is emitted as a floating drawing that Google Docs drops, and Google
fails the stroke-line check on dozens of documents that LibreOffice fails on none of. The `w:pBdr`
repair for it is written and was measured on 19 Nov; this run established that it **cannot work as
written**, and the reason is structural, not a wrong formula. `PdfToWord.attachShapes` appends every
shape to the page's block list *after* the paragraphs, and `DocxWriter.pageXml` writes that list in
order, so a rule is always written when the flow has already run to the foot of the page — and a
paragraph border can only be placed forward. That is what put both borders at y 807 on 19 Nov instead
of at the two ys the page drew, and it is why the change would be a LibreOffice regression: the drawing
path pins the rule absolutely and LibreOffice draws it correctly today. The precondition is that shapes
must be written in top order among the page's blocks; `FINDINGS/content-present-partly-displaced-rules-
cannot-flow-044000-f1x.md` has the exact change and the numbers behind it.

Two subagents landed findings. The first closed the open question in the handoff — there is no third
construct emitting the zero-width-space anchor: no Java line writes that character, and none of the
corpus `.docx` files contains one; it is Google's own placeholder for a drawing it refused. The second
found that the numbers describing this class were unreadable because the class file's two numeric
columns were swapped, and went on to name the real residual on the pages it examined.

Four tool defects were found and repaired, each verified by re-running the tool and comparing: the
liveness report took its ages from file timestamps, which a fresh clone resets, so every stage read as
zero hours old and the stall alarm could never fire; its attempt counter read the ledger's Indian
timestamps as if they were pod-local, putting every attempt five and a half hours in the future; the
class-file writer put the one-pixel share in the five-pixel column and the five-pixel share in the
outlier column, on every row it had ever written; and the report dated itself in UTC while every other
stamp in the file is IST. Two blocker rows were closed on the evidence. The one that remains needs a
person at the platform console and cannot be cleared from inside a run.
