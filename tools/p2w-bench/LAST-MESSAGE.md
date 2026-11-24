# Fixer report - 2026-11-24 18:28

```
# P2W Fixer - Run Report

**24 Nov 2026 · slot 18:28 → running IST · 5 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - subagents: 2 deployed vs no FINDINGS file for 60ed60_text_colu, pc2300_page_coun |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **35** of the **187** re-measured on this engine - **4** of the 191 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `00_page_count` - taken from the pending list (26 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 18:28 | **lead** | 0/23 | Recorded as a lead, not a fix: the class's 23 refusals are all engine (the page's furniture as N page-positioned shapes, Google charges 0.10-0.96 pt per shape) but zero of them can go clean - a refusa |
| 18:30 | **lead** | 0/23 | Second measurement this slot, live in Google through the fixed recorder: 60_page_border still 2 vs 1 on b7699196 with page 2 holding 0 words / 1 drawing / 16 images (the page's own border, rasterised |

## The txt

| | |
|:--|:--|
| Measured | **41 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `60ed60_text_column_right_edge-01` | is the right edge the engine's or the face's | 18:27 | 18:40 | 13 min |
| `pc2300_page_count-01` | what is on the extra page of the 23 refusals | 18:27 | 18:40 | 13 min |

## Timing

| | |
|:--|:--|
| Slot window | 18:28 → running · 5 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 59 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **3 min** | `###############` |
| report - the report and the chain | **1 min** | `####` |
| other - not attributed to a tool | **1 min** | `####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## The two classes this run gave a verdict, and why neither is a fix

| class | leverage claimed | what the measurement says | reachable by an engine change |
|:--|--:|:--|:--|
| `60_text_column_right_edge` | 19.8 | the edge moves by `k x (line width)` where `k` is the ratio of two faces' advance widths - the `.docx` states no right edge at all. 4 of the 5 sole-failure documents declare DejaVu, which Google does not have; 1 is the check reading the widest extractor line. **0 engine defects.** | no |
| `00_page_count` | 23.0 | 23 of 23 are engine (the page's furniture emitted as 7-646 page-positioned shapes; Google charges 0.10-0.96 pt per shape, LibreOffice nothing), but **0 would go clean** - not one carries a single Google check, and the LibreOffice proxy bounds the prize at 14, honestly 5. | yes, worth 5 |

Both are in `FINDINGS/`, with the measurement that proves each.

## What was changed, and how it was proved

`gverify.py --collect`'s page-count branch did `os.remove(tmp)` on the export and then wrote its own dict
instead of going through `_write`. Read off the committed store before the change: **23 refusals, 21 with
no engine stamp, keys exactly `[name, status, pages, want]`**. So "23 refused" was a claim about 23 Nov,
not about the engine in the tree, and the one thing that decides engine-vs-instrument - what the extra
page holds - was deleted by the code recording it.

After: the export is kept as `<name>.refused.pdf`, the record goes through `_write` so it carries
`engine`, `checks` and `at`, and it carries `extra_pages` (per page: words, chars, drawings, images) and
`export`. Proved on one synthetic refusal and then on a real one: `60_page_border`'s record now reads
`engine b7699196`, `checks 369550-1795522931`, `extra_pages [{page 2, words 0, drawings 1, images 16}]`.
No verdict changes on its own - a refusal is still a refusal.

## What the gate did, and what it could not do

`regress.py --check` was run and **did not finish**: it timed out at 285 s with no output, because it
tries to build the converted corpus and a cold pod needs the ~38 min conversion. The corpus itself was
fetched (213 PDFs, 212 scored, 0 missing). This is a gate that cannot be run inside one tool call on a
cold pod, not a gate that refused the change - and the change touches no engine file, so no document's
render moved.

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 28 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 28 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-convert.py --ensure) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 28 item(s) you can close - run pending.py and take them in its order before the class below. Re-measure the 23 page-count refusals in Google with the new recorder - the census now says whether the extra page holds anything, which is the difference between an engine defect and a counter. Then the 18_displacement pair: the spacer split is already in HEAD behind the room guard; the blocker is measured at +0.70 pt/row on w:trHeight hRule=atLeast (factor 0.9634), and it must land in the same attempt or mobile-bill and insurance-policy-schedule lose content.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
