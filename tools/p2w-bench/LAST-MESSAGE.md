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

Measured on all 213. Each fault alone re-scored at **198** clean with **zero** `ok -> fail`
flips on any check of any document; the two were then landed together and the combination was
scored on the whole corpus — corpus fetched, engine built from this tree, all 213 converted:

    213 scored | 2 documents newly clean, 0 newly failing, 211 unchanged
      NEWLY CLEAN: 324_loan_amortisation_schedule, gst-invoice-multipage-item-table

`restamp_txt.py --apply` wrote the table at **199 clean (93.4%)**, up from 197, with 0 newly
failing. `test_txt_checks.py` 8/8, `regress.py --check` PASS for both formats,
`measure_gate.py` READY.

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
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-02` | what makes a single-page dense table drift in Google | 07:36 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 10:17 → running · 1h 10m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Longest silence | **39.9 min** — from 10:17:36, after `report.py: building the report` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **39 min** | `############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **27 min** | `########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

`t01`'s punctuation strip: `77_arabic_rtl_document` loses no character (its date is bidi
reordered, not lost) but `t01` compares unstripped punctuation, so the digit/letter split alone
measured **0 flips**. Applying the punctuation strip to both sides is the whole of that
document and is **unmeasured** — the corpus and engine are now on the pod, so it is one
`restamp_txt.py --run` away. The remaining 12 `.txt` failures are: 2 real engine text faults
(`311`, `600`), 2 ZapfDingbats documents that need **opposite** treatments and are parked with
the evidence, and the date-box `t09` keys on `041122` and the filled form (owed 12 against
present 125). `18_displacement` still holds the 34.5-document lead, but its `.txt` half is
closed: work it in the `.docx`.
