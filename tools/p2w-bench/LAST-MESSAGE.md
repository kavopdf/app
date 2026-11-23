# Fixer report - 2026-11-23 04:56

```
# P2W Fixer - Run Report

**23 Nov 2026 · slot 04:56 → 05:13 IST · 16 min**

> No change was kept this run. The numbers below say what was tried.


> **A second fixer slot ran concurrently and overwrote this run's record.** The table below is
> report.py's, generated from ROUND.json/RUN.json as they now stand (the 04:56 slot). This relay's
> own slot ran 02:13 → 00:40 UTC; what it did is in **This relay's slot** below. It changed no
> document, so every number in the table is the same for both.

## This relay's slot (02:13 → 00:40 UTC)

**The construct I built was already on main.** A concurrent run landed the same spacer split at
04:56 with a better guard — "the page has room" — and the rebase said so. I dropped my engine patch
and kept the measurement and the instrument fix.

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:33 | **reverted** | 0 | spacer split, guard = nil-border carrier and gap<=20pt, measured across all 213: 65 documents better, 3 worse (363_warranty_card 10.58->11.13, price-list-right-aligned-amounts 1.79->1.90, 03_stamp_vertical_90deg 16.98->17.50). regress.py refused. |
| 23:54 | **lead** | 0 | the same split narrowed by two clauses - spend the gap only where it was MEASURED from the page's flow position, and only on a page with no floating shape at all - passes regress.py with nothing worse in either format and keeps all six documents the split fixes. Dropped at the rebase: main already carries this construct. |

### What landed (`d5b6edc7`)

`_soffice_warm()` ran `soffice.bin --version`, which short-circuits **before** LibreOffice's profile
is initialised. On a fresh pod the first document launch then exits 81 with no PDF and no message:
`measured 0 of 212`, four runs in a row, `pre/` empty while 213 .docx existed. Three clean-HOME
experiments through the real `soffice_pdf()` path: `--version` leaves the profile absent and the first
convert fails; `mkdir` of the profile directory alone changes nothing (rc=81 either way);
`--headless --norestore --terminate_after_init` populates it in 0.6 s and the first convert converts.
**This was the gate, not a construct** - runs that stood aside reading "measured 0" were blocked by a
missing directory, not by policy.

### The census, which is the lead

Instrumented at the exact statement the gate reads, all 213 documents:

| | |
|:--|:--|
| Reachable (nil-border table, gap ≤ 20 pt) | **50** |
| Of those, failing Google | **46** |
| Of those, exactly one check short, and it is `18_displacement` | **9** |
| Of those, already 42/42 (must not break) | **1** — 74_balance_sheet_indented_subitems |

Six of the nine are already at 42/42 in Google under the split the 01:14 slot measured. Three were
never measured in Google: `362_price_list_dense`, `balance-sheet-two-columns-of-figures`,
`bus-timetable-station-left-right`. Three round trips close the class.

### Parked, with the evidence to re-open

`_engine_stamp()` hashes `ENGINE_SRC`, but the invalidation runs where `ENGINE_SRC` resolved to
`/scratch/work/p2w/repo` while the measurement was of `P2W_ENGINE_SRC`. The stamp written therefore
describes another tree, the next call computes the real one, and `rm -rf`s `DOCX`/`DIST`/`PRE` — it
cost this slot two full 213-document reconversions. Not fixed: what the stamp should describe (the
tree measured, or the commit measured) is a decision. Evidence:
`FINDINGS/18_displacement-CENSUS-AND-TWO-INSTRUMENT-FAULTS-0015-relay.md`.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **28**, out of the 190 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:09 | **lead** | 0/23 | corrected: see FINDINGS/00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md - the cost is the empty paragraph (~0.83 pt), not an inline image |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `00_pA-01` | from the committed gverify JSONs and CENSUS.csv, how | 05:13 | 23:43 | 0 min |
| `00_pB-01` | re-measure every claim of the page-count finding fro | 05:13 | 23:43 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 04:56 → 05:13 · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 27 |
| Longest silence | **9.1 min** — from 05:00:24, after `agent B landed: 12 docs fail 18_displacement alone; fetching corpus` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **9 min** | `############` |
| record - attempt, handoff, class rows | **5 min** | `#######` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **1 min** | `##` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Three Google round trips close `18_displacement`: `362_price_list_dense`,
`balance-sheet-two-columns-of-figures`, `bus-timetable-station-left-right`, on the engine as it
stands, against their committed Google scores. If all three reach 42/42 the class is solved; if one
does not, its failing check names the next construct. Do not rebuild the corpus to ask it - the
construct is committed and the proxy cannot see it.

Before any long measurement, check `pre/` is filling. `measured 0 of 212` is a missing LibreOffice
profile, not a policy block, and the fix is in `benchmarks/p2w.py` as of `d5b6edc7`.

> **1 item parked** — the engine stamp names the wrong tree; it wipes a local tree's own corpus. See
> the top of `HANDOFF.md` and the FINDINGS file above for what would re-open it.
