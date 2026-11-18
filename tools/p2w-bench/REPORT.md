# Fixer report - 2026-11-18 15:29

```
# P2W Fixer — Run Report

**18 Nov 2026 · 14:50 → 15:29 IST · 38 min**

> **415_inline_images** fixed — 89.04 → 0.00. Corpus ratchet clean across 212 documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **1** — 2 attempt(s), 1 kept |
| Documents improved, round total | 2 of 212 |
| Corpus improvement vs 15 Nov | **+6.85%** — mean 6.15 → 5.73 |
| Regressions | **none** |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `content-partly-lost-and-displaced` |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Run time | 38 min |
| Tool beats | 16 |
| Longest silence | **37.0 min** — from 14:52:00, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 need a human |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `newsletter-3col-header-footer` | 3.45 | 3.13 | -0.32 |

## Next run

Finish itr-computation-with-slab-table (50.80). Its remaining 22 pt of overrun is the running footer, which the page draws at y=811 INSIDE table 3's band while the flow can only place it after the table's clipped bottom at 841, so the page still squeezes at f=0.974 and every row drifts -0.45 pt. The anchor rule is already described in DocxWriter's zero-gap branch (~line 4235): the comment says a line the page drew above the flow's position is anchored at its own y, but the code only counts it and writes before=0. Implement that, re-screen this document (screen.py --docs itr-computation-with-slab-table). Second: finish the three documents the ratchet could not measure - 416_many_tiny_pages (300 pages, needs ~5 calls of measure_doc_chunked), 77_arabic_rtl_document and 79_inr_indian_digit_grouping_table (soffice 'no render', re-run them). Third: this class cannot be closed by attempt.py's bar (6 of 7 already under 5.0) - BLOCKERS.md 14:50, a human decision.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
