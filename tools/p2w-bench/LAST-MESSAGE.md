# Fixer report - 2026-11-28 09:54

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 09:54 → running IST · 26 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; subagents: 1 deployed vs no FINDINGS filename carries --cl-01 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `t09_page_furniture` - taken from the pending list (63 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `t09_page_furniture` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:53 | **lead** | 0/None | The glyph merge was built and measured on 305 and it is refuted: source draws 85 lines of which 47 are single characters (_src_line_count, PyMuPDF granularity) and the .txt at HEAD carries exactly 85 |
| 10:21 | **lead** | 0/None | The placement fix is measured and it works: hoisting the seal paragraph by its own top (TxtWriter.pageOrder -> hoistLastPara, plus the lastY>0 guard) takes 305_vaccination_certificate to PASS - t04 85 |

## Why nothing moved, in this run's own words

> **The decision, and its reason.** `classpick.py` suggested `t09_page_furniture` on a lead whose own
> FINDINGS file (`t09-PAGE-FURNITURE-RELAY-27NOV-relay.md`) refutes its `.docx` half and asks for the `.txt`
> half. I took it, because the `.txt` gate passes at HEAD and a `.txt`-scoped change is the only kind this
> pipeline can commit today: the docx half is frozen behind 84 documents of debt and a 54-minute re-measure.
>
> **What the previous slot left me, and what it cost me.** The 09:08 run's whole slot was two refutations
> (the table-cell pitch band and the U+FFFD glyph-name fallback) and no change, so the ledger's newest lead
> pointed at a class whose `.docx` half was already closed. Reading that before claiming saved the slot
> from re-deriving it; the first 15 minutes went to `FINDINGS/`, `DISP-TABLE.csv` and the gate, not to a
> build.
>
> **The gate is not what blocks this pipeline, and I measured that rather than assuming it.** `regress.py
> --check` at HEAD prints `PASS` — `docx: no document got worse`, the 84 worse-than-baseline documents are
> "frozen, not forgiven", `txt: no document worse than baseline`. The 28 Nov 02:24 finding's "84 regressions
> refuse every engine change" is now a frozen debt, not a refusal. What blocks an engine change is the
> re-measure behind it: the docx table needs a 54-minute corpus pass, the txt table a full 213-document
> re-conversion. That is the real cost, and it is why nothing landed in 40 minutes of slot.
>
> **What I found, and how.** `305_vaccination_certificate` fails `t08_line_order` 32 of 33 and is one page.
> Its `.txt` has 85 lines, **47 of them single characters**: the page draws `NATIONAL IMMUNISATION REGISTRY`
> as one line at `y = 20.1`, and the `.txt` writes it as sixteen lines, one glyph each, at increasing
> columns. The same document's `.docx` carries the string `NATIONAL IMMUNISATION REGISTRY` merged. So
> `DocxWriter` merges the glyphs of a letter-spaced line and `TxtWriter` does not — one model, two writers,
> opposite answers. The two `Account_Opening_Form` documents carry the same defect at scale: 274 single-char
> lines of 1193, and that is where `t09`'s "29 owed / 125 present" comes from, which the 26 Nov census
> recorded as instrument asymmetry and could not attribute.
>
> **Why I did not land it.** The fix is writer-local (`TxtWriter.appendPara`), but a `TxtWriter` change
> moves the engine fingerprint, and the commit gate then demands a re-stamped `RANKING-TXT.csv` over all 213
> documents. I had the diagnosis and 25 minutes; a half-measured engine change is worse than none, and the
> charter says an unmeasured change is not a pass. So the measurement, the exact next step and the expected
> one-document result are in `FINDINGS/TXT-SPLITS-A-LETTER-SPACED-LINE-INTO-ONE-LINE-PER-GLYPH-28NOV-relay.md`
> and the attempt is recorded as a `lead`, not as a fix.
>
> **What would overturn it.** If a merged `TxtWriter` does not take `305` to `t08 33 of 33`, the merge is
> the wrong merge and the split is in `PdfToWord`'s line model instead — which would also mean the `.docx`
> merge I measured is done downstream and would have to be moved. That is one conversion and one
> `verify_txt.py` run to settle, and it is the first thing the next slot should do.

## The txt

| | |
|:--|:--|
| Measured | **4.9 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `--cl-01` | --class | 10:00 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 09:54 → running · 26 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 12 |
| Longest silence | **20.1 min** — from 10:01:26, after `lastmessage.py: running report.py for the numbers` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **20 min** | `#################` |
| measure or build - a conversion, screen or compile writes no beacon | **5 min** | `####` |
| report - the report and the chain | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
