# P2W Fixer — Run Report

**18 Nov 2026 · slot 14:50 → 15:29 IST · 38 min**

> **1 document(s)** improved this run, but the run did not commit benchmarks/RANKING.csv, so the report cannot name them.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 2 attempt(s), 1 kept |
| Documents improved, round total | 3 of 212 |
| Corpus improvement vs 15 Nov | **+8.24%** — mean 6.15 → 5.64 |
| Regressions | **none** |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost-and-displaced` |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Session | 13:50 → 15:29 · **1h 39m** |
| Slot window | 14:50 → 15:29 · 38 min |
| Before the claim | 1h 01m - pod setup, cloning and retries |
| Tool beats | 16 |
| Longest silence | **37.0 min** — from 14:52:00, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 10 cleared · 1 need a human |
| Still a wall | The document is 33.6 pt high on every line and its own model of the page said so: `need=18160 twips` against ` |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 50.80 | -18.02 |
| `newsletter-3col-header-footer` | 3.45 | 3.13 | -0.32 |

## Next run

Finish itr-computation-with-slab-table (50.80). Its remaining 22 pt of overrun is the running footer, which the page draws at y=811 INSIDE table 3's band while the flow can only place it after the table's clipped bottom at 841, so the page still squeezes at f=0.974 and every row drifts -0.45 pt. The anchor rule is already described in DocxWriter's zero-gap branch (~line 4235): the comment says a line the page drew above the flow's position is anchored at its own y, but the code only counts it and writes before=0. Implement that, re-screen this document (screen.py --docs itr-computation-with-slab-table). Second: finish the three documents the ratchet could not measure - 416_many_tiny_pages (300 pages, needs ~5 calls of measure_doc_chunked), 77_arabic_rtl_document and 79_inr_indian_digit_grouping_table (soffice 'no render', re-run them). Third: this class CAN now be closed - attempt.py takes --best-drop and keeps an attempt when one document moved >= 5.0 share points (5d3965a), so the 18.02-point fix on itr-computation-with-slab-table counts even though only 1 of 7 moved. Pass --best-drop when you record it.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
