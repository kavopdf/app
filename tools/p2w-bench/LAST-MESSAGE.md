# P2W Fixer - Run Report

**21 Nov 2026 · slot 03:57 → 04:36 IST · 39 min**

> No engine change was kept this run. The patch is measured, the blast radius is proved over all 213 documents, and the gate refuses an unmeasured engine - so what landed is the patch, the finding, and a census, not a tree change.
>
> The slot was reclaimed, not claimed. The 03:36 run committed its report and died holding the claim: 20 minutes since its last beacon against a 10 minute stale limit. `round.py --claim-fixer` read "last activity 0 min ago" because the mandatory `git checkout -- tools/p2w-bench/` rewrites TIMELINE.jsonl and refreshes the very mtime the staleness check reads. The true last event in that file is 03:36:40.
>
> The class was not my choice. classpick.py printed `t01_word_accuracy`, 5 documents, and pending.py agreed: its first row is the carry-over, and it names this class.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 2 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:36 | **partial** | 1/5 | A WIDGET'S APPEARANCE STREAM IS WHERE A TICK LIVES. `readAnnotationAppearances()` skipped every `PDAnnotationWidget` on a comment saying its appearance was already painted by `paintField` - and there is no `paintField` in the file, so the skip was the loss, not a guard. Walking `/AP /N` resolved through `/AS` takes 601 from 37/42 to 42/42 docx checks on the same tree, same run. |

### The mechanism, and the proof

`601_fillable_admission_form` loses three tokens: `3`, `3` and `General`. The two `3`s are ZapfDingbats code 0x33 - a checkmark - drawn in checkbox appearance streams (xrefs 51 and 57) as `BT 0 g .9 1.7999992 Td /ZaDb 9 Tf (3) Tj ET`. `PDFTextStripper` walks page content streams only, so nothing reached the .docx and the form came out with two blank boxes where it was answered.

The patch stops skipping widgets, resolves `/N` through `/AS` because a checkbox's `/N` is `<< /Off 49 0 R /Yes 51 0 R >>` and `/Off` is the blank one, and leaves an unfilled `() Tj` emitting nothing.

### Same tree, same run, both sides built

| document | before | after |
|:--|--:|--:|
| `601_fillable_admission_form` docx checks | 37/42 FAIL | **42/42 PASS** |
| `601_fillable_admission_form` t01 | 96.4 | 98.8 |
| `Account_Opening_Form_Fillable_filled` docx checks | 21/47 | 25/47 |

Five checks move on 601 and all five move the right way: `04_chars_missing` 0/2 → 0/0, `18_displacement` 0/1 → 0/0, `51_field_values` 3/0 → 3/3, `53_embedded_faces` 2/1 → 2/2, `59_shape_anchor` 3/0 → 3/3. Both builds were made with build-engine.sh and both were scored inside this run, so neither side is a stale row.

On the Account form seven checks fix and **two newly fail**: `42_justification_edges` 0/3 → 22/6 and `63_table_rows` 23/0 → 24/1. The matched population also goes 272 → 803, so the reading is a denominator effect rather than new bad layout - an inference, not a measurement. That document is the gate for this patch.

### The blast radius, over all 213 documents

A census of every page annotation and every appearance stream: 563 pages, 363 widgets, 145 of those 363 whose selected `/N` carries text operators, **17 that emit characters, in 2 documents**, and **0** whose text is already in the page text layer. 210 documents have no annotations at all. Only the 7 ticks are unreachable today; the other 10 strings equal the widget's `/V` and are already reachable, so the patch emits each once. A walk over all annotations would add a third document, `600_reviewed_invoice_with_annotations`.

`page.annots()` returns no widgets at all in PyMuPDF - the first pass reported a false "no blast radius" until it was switched to `page.widgets()`.

### Why t01 does not reach 100 on 601, and it is the instrument

`verify_txt._ap_stream_text()` has no Annex D table for ZapfDingbats by explicit decision, so it counts a tick as the ASCII digit `3`. Then `glyph_truth()` double-counts the text field: pymupdf's `page.get_text()` **already synthesises the widget appearance** - on 601 it returns `General` and two `3`s while no page content stream in the file contains `General` at all, all 33 `/Contents` xrefs scanned - and `glyph_truth()` appends `_ap_stream_text()` on top. A faithful engine therefore cannot reach 100 %. The variant that does reach 100 % duplicates `General` and costs 601 five docx checks. **The correct fix is instrument-side and a fixer may not make it.**

### Why it did not land

`p2w.py` builds the engine from `origin main`, not from a working tree, so the corpus cannot be measured until the patch is pushed - and `regress.py --check` refuses an engine whose fingerprint is not the table's. The patch is `FINDINGS/widget-ap-glyph-walk-0436-f1x.patch` and it forward-applies to `ada9ce9`. Google was not measured: nothing landed, so no gate decision depended on it, and the slot went to the census and the two-build measurement.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

Two agents, both before the run's own attempt.

1. Explore - a census of every widget appearance stream across all 213 documents. It found the corpus is not in the repository (four release zips), fetched them, and returned 17 widgets in 2 documents with the trap named: 10 of the 17 equal `/V` and would be duplicated by a naive walk, and 128 of the 145 widgets that carry text operators emit the empty string. That census is why the patch is 36 lines and not a rewrite.
2. general-purpose - implemented the glyph walk in its own clone and measured both documents both ways. It found the missing `paintField`, the `/AS` state dictionary, and the instrument's double count. Its patch is the one applied here; its numbers reproduced exactly when I built and scored both sides myself.

Both returned inside the turn - a scheduled run has no one to answer later - so neither was waited on.

## Timing

| | |
|:--|:--|
| Slot window | 03:57 → 04:36 · 39 min |
| Before the claim | 4 min - clone, install-gate, brief |
| Tool beats | 28 |
| Longest silence | **30.0 min** — from 03:57:32, after `pending.py: reading the pending gate` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **7 min** | `####` |
| measure or build - a conversion, screen or compile writes no beacon | **30 min** | `#################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |

## Next run

Push `FINDINGS/widget-ap-glyph-walk-0436-f1x.patch` and measure it corpus-wide - the blast radius is 2 documents, so the ratchet is cheap. Then measure 601 through Drive before and after, because Google is the authority and this run only has LibreOffice. Watch the Account form's two new failures.

Do not chase t01 to 100 % on 601 from the engine. The residual is `verify_txt` counting `General` twice, and a person has to decide that, the same way the 01:43 row asks for a decision on the .txt side.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
