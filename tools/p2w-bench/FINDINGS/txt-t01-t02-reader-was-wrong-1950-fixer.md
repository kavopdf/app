# txt t01/t02: the reader was wrong twice — 205 → 208 of 214 clean, 0 worse

**27 Nov 2026, fixer slot 19:15.** Two defects in `tools/p2w-bench/verify_txt.py`, one measurement
each, both landed in the same commit because they touch the same instrument and were re-stamped
together.

## What moved

| | before | after |
|:--|--:|--:|
| .txt clean | 205 of 214 | **208 of 214 (97.2%)** |
| .txt failing | 9 | 6 |
| newly clean | — | 3 |
| newly failing | — | **0** |

Cleared: `39_small_caps_letter_spacing` (t01 97.4 → 100), `74_balance_sheet_indented_subitems`
(t02 80 → 96), `77_arabic_rtl_document` (t01 92.1 → 100).

## Defect 1 — t01 charged "lost text" when no character was lost

`t01_word_accuracy` counts tokens present in the source and missing from the .txt. It compared
`Counter(words)` and charged every difference as lost text. But a word boundary is exactly where
two extractors are allowed to disagree: `_strip_punct` in the same file says so in its own note.

Measured on the two documents it failed:
- `39_small_caps_letter_spacing` draws `M Y S U R U 57 0 0 05`; the .txt has `M Y S U R U 570 005`.
  The extractor breaks at 0.15 em of letter spacing, the writer at 0.18; this document sits between.
- `77_arabic_rtl_document` draws the digit fused to the Arabic word in visual order (`:التاريخ5`);
  the .txt separates them.

Both were charged 8 lost tokens and both have a **zero character deficit** — every non-space
character the page drew is in the .txt. The fix: if `Counter(src_chars) - Counter(txt_chars)` is
empty, no text was lost, so the lost count is 0. Falsifiability is unchanged — a .txt that drops a
word drops its characters, so the deficit is non-zero and the word is still charged (the
`test_txt_checks.py` "a word is missing" fixture still passes, 8/8).

## Defect 2 — t02 read the span's bbox left edge, not the ink

`_src_runs` returned `sp["bbox"][0]`. A page can encode a line's indentation **inside** the run: the
run starts with spaces, so the bbox left edge is the first *space*, and the first character a reader
sees is further right.

`74_balance_sheet_indented_subitems`, every subitem row at bbox x0 = 56.00:

```
'        (a)  Share capital'        ink at 73.40
'                 General reserve'  ink at 92.98
```

The .txt pads those rows to columns 14 and 18 — exactly what the ink says at charW 5.06, and exactly
what the model's own `cellX` records (73.4 / 92.98 with `colX[0]` = 56.0). The check paired
(56.0, 14) and (56.0, 18) with a ruler fitted on x = 56.0 → 11 and called the document 80 %.

Fix: on upright LTR runs with a **lead of 8 or more spaces** and no RTL character, use the first
inked glyph's x from `rawdict`.

### The threshold was measured, not chosen — and the first answer was wrong

A sub-agent proposed `lead >= 4` and reported that at 4 both `383_api_docs_page` and
`392_statistical_console_output` were "back at 100". **That was false**, and the paired A/B caught it:

| threshold | cleared | 383 t02 | 392 t02 |
|:--|:--|--:|--:|
| lead >= 4 | same 3 | 100 → 96 | 100 → **90** (exactly on the threshold) |
| lead >= 8 | same 3 | 100 → 100 | 100 → 95 |

`lead >= 8` is strictly better: it clears the same three documents, costs nothing, and leaves 392 a
margin instead of none. 74's indents are 8 and 17 spaces; 77's clear is the t01 arm, not this one.

## How it was proved (three sources, none of them the tool I edited)

1. **Paired A/B, one process, both instruments** — `/tmp/vt_head.py` vs the patched module, same
   `.txt`, same PDF, all 214 documents: 9 failing → 6 failing, 3 cleared, **0 new failures**.
2. **`restamp_txt.py`**, the repo's own re-score tool, run blind after the patch: *"214 scored | 3
   documents newly clean, 0 newly failing, 211 unchanged"* — the same three documents.
3. **`test_txt_checks.py`** 8/8, and `txt_gate.py --gate`: `214 scored | 208 clean | 6 failing`,
   `docx untouched: benchmarks/RANKING.csv is 939f50e6323a846b`.

## What it does NOT do

The remaining 6 are engine faults, not reader faults, and were not attempted:
`041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` (t06/t09/t12),
`600_reviewed_invoice_with_annotations` (t12), `601_fillable_admission_form` (t01),
`305_vaccination_certificate` (t08), `Prakashan_Print_Fidelity_Handbook` (t01/t03/t07/t12).

**Known lead, not fixed:** `392_statistical_console_output` now sits at t02 = 95 where it was 100.
It passes, and it passed at 90 under the rejected threshold, but the ink-x rule costs it margin it
did not have to lose. Narrowing the rule to table rows only is untested and may recover it.

**The instrument sha moved** (`… → 72ff003db5871587`), so every .txt mark taken before this commit
is stale by construction. That is why the full re-stamp was run in the same commit rather than
carried as a waiver.
