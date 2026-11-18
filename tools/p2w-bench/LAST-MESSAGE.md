# P2W Fixer — Run Report

**18 Nov 2026 · session 16:52 → 17:31 IST · 0h 39m**

> The one change this bench still called live was re-measured and does not exist on this engine; the
> three documents the ratchet had never compared are now two measured and one proved unmeasurable by
> construction.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt, 0 kept |
| Documents improved, round total | 3 of 212 |
| Corpus improvement vs 15 Nov | **+8.24%** — mean 6.15 → 5.64 |
| Regressions | **none** |
| Exempt, not measured | **1** — `416_many_tiny_pages` |
| Classes solved | 0 of 6 clear — 6 classes still have an OPEN document |
| Working on | `content-missing-partly-replaced` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 17:00 | **reverted** | 0/16 | `run-size-from-sizePt-not-Tf` applied clean to `7a95b1c`, built, screened on 4 documents: `360_restaurant_menu` **34.43 → 34.43** (the 96% gain SETTLED records does not reproduce), `392_statistical_console_output` 1.61 → **13.94**, `itr-computation-with-slab-table` and `320_balance_sheet_statutory` unchanged. SCREEN FAIL — dead on this engine, not gated-able |

Two more ideas were carried in from the handoff and were already refuted before this run started, so
neither was re-run: the anchor rule never fires (`FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md`)
and the cell-baseline fallback measured worse at 16:23.

## Subagents

*None deployed this run.* Both questions the slot had were single measurements of one document each,
not sweeps, and one of them turned out to be a one-command refutation.

## Timing

| | |
|:--|:--|
| Session | 16:52 → 17:31 · **0h 39m** |
| Slot window | 16:52 → 17:31 · 39 min |
| Before the claim | 0 min — clone up to date, engine built on the first call |
| Tool beats | 15 |
| Longest silence | **18.4 min** — from 17:00, after `classrow.py` — two full corpus passes converting 86 of 213 documents, one JVM each |
| Silences over 2 min | 2 |
| Obstacles | 2 written this run · 0 need a human |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup — claim, housekeeping, reading the gate | **5 min** | `####` |
| fix — diagnose and change the engine | **8 min** | `#######` |
| measure — convert and measure the corpus | **19 min** | `###############` |
| record — attempt, handoff, class rows | **7 min** | `######` |

## Best results, round to date

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `itr-computation-with-slab-table` | 68.82 | 50.80 | -18.02 |
| `newsletter-3col-header-footer` | 3.45 | 3.13 | -0.32 |

This run added nothing to this table. Its two new measurements are not improvements, they are the
first numbers ever taken: `77_arabic_rtl_document` **11.89** and
`79_inr_indian_digit_grouping_table` **0.74**, both single pages.

## Next run

`416_many_tiny_pages` first and alone. Its docx needs ~250 s in soffice (it succeeds, it is not
broken) and its 300 pages need ~280 s to compare, against a 292 s command — and `measure_doc_chunked`
does not cache a partial window, so it restarts at page 1 and dies every run. Seed
`pre/416_many_tiny_pages.pdf.src` with the docx's `size:mtime` stamp and give it one whole call, or
add per-window caching under `dist2/<doc>.w<N>.json`, which is the real fix.

Proved wrong already, so do not repeat it: the run-size patch (34.43 → 34.43 here, and 392 breaks),
the anchor rule, and the cell-baseline fallback. `content-partly-lost-and-displaced` is down to
`itr-computation-with-slab-table` at 50.80, and of its three listed defects only the third — the
footer emitted as a ROW of table 3 between rows the page draws around it — is still standing; it is a
row-ordering question in `DocxWriter.table()`, not a flow one.

`chain.py --after-release` **STOPPED**: three runs in a row with no kept and no partial attempt. That
is the circuit breaker, not bad luck — the next run should clear the measurement obstacle above
before it tries a fourth idea on the same class.
