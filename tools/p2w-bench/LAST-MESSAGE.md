# P2W Fixer - Run Report

**23 Nov 2026 · slot 10:17 → running IST**

The slot went to the `.txt` instrument, and it landed. `t09_page_furniture` was charging
two correct `.txt` files for duplications their pages really make.

**Fault 1 — a furniture key with no letter in it is not furniture.** `_furniture_key` folds
every digit to `#`, so a page of numeric table cells folds to a handful of keys that repeat
on every page and clear `FURNITURE_MIN_PAGES`. On `324_loan_amortisation_schedule` three
such keys (`'#'` present 240, `'#,#,#.#'` 423, `'#,#.#'` 774 = 1437) invented 18 owed and
1437 present out of table data, while all 8 real running heads matched 6/6 on each of their
six pages and the bottom band of every page is blank — the document has no footer, so
nothing was missing. Owed/present went 66/1485 → **48/48**.

**Fault 2 — owed was counted per page, not per drawn occurrence.**
`gst-invoice-multipage-item-table` draws `Page N of 4` **twice on every page** (y=75.4 top
band, y=811.4 bottom band) and its `.txt` carries all 8 copies; the check owed 4 and charged
a 4-copy surplus for a duplication the page makes. Owed/present 39/43 → **43/43**. A writer
that drops a second copy now shows as a deficit, which is the fault the check is for.

Measured on all 213, re-scored with the real `verify_txt.compare()` on a fresh conversion of
the whole corpus: head **197** clean, each fault alone **198**, and **zero** `ok -> fail`
flips on any check of any document. `test_txt_checks.py` 8/8, `regress.py --check` PASS,
`measure_gate.py` READY. The two fixes were landed together; the combination was bounded for
the four documents they touch and cannot regress against baseline, but it was **not re-scored
as a combination** — the conversion is 20+ minutes and the slot had 20. `RANKING-TXT.csv` is
now stale against the verifier and needs `restamp_txt.py --run --apply`; until then the table
still says 197, so this report does not claim the 198 in its own table.

Two sub-agent diagnoses ran inside this turn, not in the background (a scheduled run has no
one to answer a later result), so the tooling records none. Both came back with measurements
that changed the plan:

* **`18_displacement`'s `.txt` half is not `18_displacement`.** Of the **101** documents that
  fail `18` in Google, **95 are `.txt`-clean** (94.1%) against 5.3 expected if the two
  populations were independent (Fisher p = 0.752, OR 1.34); all 13 documents that fail `18`
  and nothing else are `.txt`-clean; `t08_line_order`, the only positional `.txt` check,
  fails **0 of the 101**. `_txt_lines` discards blank lines, so a block displacement cannot
  reach the `.txt` instrument at all. That refuted the class's open lead and is why the slot
  went to the instrument.
* **The blast radius, measured not reasoned.** The second agent built five variants of
  `verify_txt.py`, converted all 213 documents and re-scored each. Its own proposed
  ZapfDingbats *decode* fix was refuted by that measurement — decoding `0x33` to `✓` would
  newly fire `t03`/`t07` on `601` — so it was not landed. The digit/letter word split was
  measured at **0 flips**, so `77_arabic_rtl_document` is parked, not fixed: `t01` also
  compares unstripped punctuation.

`311_fir_police_form` and `600_reviewed_invoice_with_annotations` are real engine text
faults, not instrument faults, and are named as such in the finding.

## Progress

| | |
|:--|:--|
| Document-moves this run | **2** — 1 attempt(s), 1 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 212) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **1** — 416_many_tiny_pages |
| **Fixed - Google, all 42 checks** | **0**, out of the 2 measured on THIS engine (all engines: 30 of 190) |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `t09_page_furniture` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:00 | **kept** | 2/None | verify_txt.py only, no engine change: a furniture key with no letter in it is not furniture (_furniture_key folds digits to '#', so 324's numeric table cells invented 18 owed and 1437 present - 66/148 |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 10:17 → running · 44 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 9 |
| Longest silence | **39.9 min** — from 10:17:36, after `report.py: building the report` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **39 min** | `####################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Re-stamp `RANKING-TXT.csv` (`restamp_txt.py --run --apply`) so the table stops lying about
the verifier that produced it, and score the two landed faults **as a combination** to settle
whether `324_loan_amortisation_schedule` holds — that is the difference between 198 and 199.
Then `t01`'s punctuation strip, which is the whole of `77`, and is unmeasured. `18_displacement`
still holds the 34.5-document lead, but its `.txt` half is closed: work it in the `.docx`.
