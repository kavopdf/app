# fixer 21 Nov 12:20 - t01_word_accuracy: 601's last lost word was the instrument, not the engine

The table below is `report.py`'s own verdict on the committed state. This run's live state files were
reset at 12:02 by the `git checkout -- tools/p2w-bench/` that the rebase needed, so the timing rows
describe the committed 07:58 record and not this slot; every number I claim is measured inline in the
sections after it, with the tool that produced it.

# P2W Fixer - Run Report

**21 Nov 2026 · slot 07:58 → 10:45 IST · 2h 47m**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 10:39 | **reverted** | 0/213 | Carry-over measured, all three variants, corpus-wide: full widget-AP walk 601 52.39 -> 0.00 share@5px and 38/42 -> 42/42 docx checks, but Account_Opening_Form_Fillable_filled 97.62 -> 98.65 (+1.03) in |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 07:58 → 10:45 · 2h 47m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **119.2 min** — from 08:40:45, after `attempt.py: recording an attempt` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | The walk fixes 601 completely - share@5px 52.39 -> 0.00 and docx checks 38/42 -> 42/42 - and it moves Account_ |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2h 41m** | `#####################` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **2 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*


Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.

## This slot, in one paragraph

Claimed 10:02, released 12:20. Two tool fixes landed (`747e401`, gate PASS, pushed), one engine patch
measured and saved but not committed, and one broken tool fixed on the way.

## What I measured

| what | before | after | how it was measured |
|---|---:|---:|---|
| `p2w.py --force` rebuilt per 275 s call | 75, 75, 75 | 75, 149, 205, 211 | the tool's own log, six calls |
| 601 t01, unpatched engine | 96.4 | - | `verify_txt.py` on a ConvertOne output |
| 601 t01, widget /AP /N walk | 96.4 | 98.8 | same, patched build |
| 601 t01, walk plus the glyph\_truth guard | 96.4 | 100.0 - 7/7 PASS | same |
| clean documents, old verifier | - | 186 | 211 .txt scored twice, engine held fixed |
| clean documents, new verifier | 186 | 187 | same files, only the verifier changing |
| documents newly failing | - | 0 | document-by-document failed sets |
| failed-set differences vs the committed txt table | - | 0 across 211 documents | `txt/RANKING-TXT.csv` as an independent source |
| docx measured with the patched engine | - | 114 documents measured | `p2w/dist2` |

## What landed

`747e401`. Two tool fixes, no engine change.

`benchmarks/p2w.py` - `--force` was not resumable. `_need()` answered True for every document, so every
call rebuilt the same first 75 and the corpus could never be rebuilt inside a slot; the brief's "repeat
until the corpus is complete" was an instruction no run could follow. A document is now stale only when
it is older than the engine class file that must write it. Measured: 75, 75, 75 before; 75, 149, 205,
211 after.

`tools/p2w-bench/verify_txt.py` - the truth counted one word twice. `glyph_truth()` appended every
widget's `/AP` text even when the page's own content stream already drew it. On 601 the page draws
"General" at (258.0, 244.9) and one widget's appearance draws it again, so the .txt's single correct
copy read as a lost word: 82 of 83 against a 99% threshold, on a document that loses nothing. The guard
appends a widget's text only when it is not already there. Across 211 documents exactly one changed and
no document's failed set grew.

`tools/p2w-bench/report.py` - `subagents()` did `set()` over `RUN.json`'s `agents`, which is now a list
of records, so report.py died with `unhashable type: 'dict'` and took `lastmessage.py`'s number-checker
with it. Fixed to read the id out of a record.

## What did not land, and why

The engine half - the widget `/AP /N` walk that supplies 601's two tick glyphs - is measured and saved
whole at `FINDINGS/widget-AP-walk-PLUS-WHITESPACE-GUARD-1145-f1x.patch`. It takes 601 to 98.8 alone and
to 100.0 with the guard, adds no construct `google_safe.py` flags, and changes no document's failed set
across all 211 on the .txt half. The gate refuses it, correctly: an engine change needs the docx half
re-measured and 114 documents were measured when the slot ran out.

It would also have been wrong to land it. The 07:58 run's own carry-over measured the same walk in
docx terms and reverted it: 601 52.39 -> 0.00 share@5px and 38/42 -> 42/42 checks, but
`Account_Opening_Form_Fillable_filled` 97.62 -> 98.65, one document worse. My patch adds a whitespace
guard that the earlier variant did not have, and the .txt half shows no movement on that document - but
the docx half of it is unmeasured, and one document worse is the rule.

Its known .txt cost is in the finding: 601 goes from 51 lines to 188 because each appearance glyph
enters `TxtWriter`'s gap model. The next attempt should keep those glyphs out of the pitch model the way
the ring-glyph path already does at `PdfToWord.java` line 4155.

## A check that cannot pass

With a measured corpus in `/scratch/work/p2w/out`, `regress.py --check` refuses every tree:
`w:drawing: 195 documents carry it, the mark is 28`. The mark was recorded on a 28-document corpus, so
`google_safe.py --corpus --check` fails as soon as a real corpus exists. I did not raise the mark - that
would set the ceiling to whatever the engine already emits. It is in `BLOCKERS.md`, and this commit
passed only because no output directory was in the tree at commit time, which is the wrong reason.

## What the next run should do

Finish the docx half of the engine measurement - the conversion is done, 114 are measured, 97 remain and
`--force` now resumes - and check the account form before keeping the walk. Then 601 is the first
document to leave t01\_word\_accuracy since 20 Nov.
