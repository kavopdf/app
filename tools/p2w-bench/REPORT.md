# Fixer report - 2026-11-28 10:28

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 10:28 → running IST · 11 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 3 vs ATTEMPTS.json history 2; kept change: 3 code commit(s) in this window, first: FINDINGS: 60-P falsified in Google - w:jc=distri vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change |
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `60_text_column_right_edge` - taken from the pending list (64 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `60_text_column_right_edge` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 10:33 | **lead** | 0/None | Google-measured on 313_power_of_attorney (fails only 60). The font-name lever was measured in Google for the first time: HEAD renders ArialMT at max right edge 480.14 against a source 538.63; Georgia |
| 10:33 | **lead** | 0/None | 60-P falsified in Google in one round trip, which the 1900-fixer finding's section 6 item 2 asked for: w:jc=distribute plus a per-line right indent (w:ind right=1133, pinning the measure to the source |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> **The decision, and its reason.** `classpick.py` suggested `t09_page_furniture` on a lead whose own FINDINGS file refutes its `.docx` half and asks for the `.txt` half. I took it because the `.txt` gate passes at HEAD and a `.txt`-scoped change is the only kind this pipeline can commit today: the docx half is frozen behind 84 documents of debt and a 54-minute re-measure.
>
> **The gate is not what blocks this pipeline, and I measured that rather than assuming it.** `regress.py --check` at HEAD prints `PASS` — `docx: no document got worse`, the 84 worse-than-baseline documents are "frozen, not forgiven", `txt: no document worse than baseline`. What blocks an engine change is the re-measure behind it, not the gate.
>
> **I took a lead, and then proved it wrong with a build.** `305_vaccination_certificate` fails `t08_line_order` 32 of 33 and is one page. Its `.txt` has 85 lines, 47 of them single characters, because the page draws its seal letter by letter. I read that as `TxtWriter` splitting a line the `.docx` merges — `word/document.xml` does carry `NATIONAL IMMUNISATION REGISTRY` as one string — and had the merge built. It took `t08` to 34/34 and broke `t04_structure` at 85/42, drift 0.49 against a 1.5 floor, and it dropped the seal's inter-word spaces. Then the decisive number: `_src_line_count` says the page draws **85** lines and **47** of them are one character, and the `.txt` carried exactly 85 with 47. **The writer was faithful and my reading was wrong.** The merge changes which check the document fails; it does not clean it.
>
> **So I built the thing the refutation pointed at, and it works.** The seal paragraph has no `lineY` at all (its glyphs sit on baselines that are not horizontal), so the model appends it last in `page.blocks` — after a footer at y = 781.9 — although its own `top` is y = 270.9. Ordering that paragraph by `top`, and merging nothing, takes 305 to `7/12 applicable, 7 passed, PASS`: `t04` 85/85 unchanged, `t08` 33/32 → 33/33, 85 lines and 47 single-character lines preserved, 30 blanks, 3384 bytes. I ran `verify_txt.py` on that output myself. A probe over all 214 PDFs says the hoist fires on 27 pages of 27 documents; 187 of 214 `.txt` are byte-identical, the other 26 are unchanged on `t04`, `t08` and pass count, and **305 is the only document that moves**.
>
> **Why it is not in the tree, stated plainly.** The build finished at 90+ minutes into the slot. Landing it needs the engine rebuilt on the pod, a full 213-document `.txt` re-conversion and a re-stamped `RANKING-TXT.csv`, and the gate refuses without that stamp. Both hunks are written verbatim into `FINDINGS/TXT-SPLITS-A-LETTER-SPACED-LINE-INTO-ONE-LINE-PER-GLYPH-28NOV-relay.md`, with the one-line `lastY > 0` guard that stops the hoist inserting ten blank lines, and the measured before/after for each.
>
> **What would overturn it.** A corpus re-conversion in which a document other than 305 moves, or in which any document's pass count falls. That is the measurement the next slot must run before it commits — everything up to it is done.

## The txt

| | |
|:--|:--|
| Measured | **5.2 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 10:28 → running · 11 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 10 |
| Longest silence | **5.2 min** — from 10:34:16, after `lastmessage.py: running report.py for the numbers` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| report - the report and the chain | **5 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
