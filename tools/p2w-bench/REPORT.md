# Fixer report - 2026-11-28 14:35

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 14:35 → running IST · 13 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - kept change: 1 code commit(s) in this window, first: t12_word_invention: both annotation doors must b vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; run window: RUN.json says this run began at 14:35 vs TIMELINE.jsonl records the claim at 13:53, so the window was reset and the duration is short |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (63 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 14:35 | **lead** | 0/None | both annotation guards together take 600_reviewed_invoice_with_annotations t12 from 83 invented chars to 0 (FAIL->PASS); each guard alone leaves 49/30 and was previously recorded as NO CLEAR; change i |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

>
>
> The slot did not land a document because the lead it inherited was measured on an incomplete
> instrument, and the complete one refuses it.
>
> I took the lead the last run handed over: the source PDFs are drawn in DejaVu, the engine declares
> DejaVu, Google Docs has no DejaVu, so it substitutes something ~13% narrower and every line stops
> short of the column. Declare Verdana instead and the edge lands. The last run proved that on two
> documents and recorded `42 of 42`.
>
> It is right about the edge and it is wrong about the document. I put the mapping in the engine
> (`dejaVuFace`, which normalises all six spellings of the family the corpus uses - a `BASE14` entry
> catches `DejaVuSans-Bold` and misses `DejaVu-Sans` entirely, and left 32 runs of
> `33_sans_nondefault_body` in `DejaVu Sans Book`), and measured twelve documents through the real
> Drive round trip, five targets and seven controls.
>
> `60` passes on all five targets. `53_embedded_faces` fails on all twelve. So 313 goes 41/42 -> 41/42
> with a different check failing, and five documents that were clean stop being clean - two of them
> losing `46_text_crossing_rule` and `59_shape_anchor` as well, because Verdana is inside `60`'s
> one-word slack but still wide enough to push a line across a rule.
>
> That is not a near miss, it is the check's own rule. `SAME_FACE` forgives a rename only when the two
> faces are metric-identical, and says so in as many words: "a serif as a sans, a sans as a serif,
> anything as DejaVu. Those stay losses." `dejavuserif -> verdana` breaks it twice. Google Docs has no
> serif as wide as DejaVu Serif - Georgia, the widest it offers, is 11% short and still fails `60` - so
> on a DejaVu Serif document `60` and `53` cannot both pass. Not "did not this time": cannot, by the
> instrument's own definition. The class is not fixable by a font rename and should stop being chased.
>
> So the most useful thing this run produced is a refutation, and the second most useful is that it
> could measure at all. Three runs lost their `.docx` work to "the upload needs an s3key". It does not:
> `upload` -> `s3key` -> `CREATE_FILE` works from a local file, and `UPLOAD_FROM_URL` works for a batch
> inside one `run_program`. Twelve documents took one program call and four minutes. Both routes are
> written into VERIFY-GOOGLE.md so no run pays that tax again.
>
> With the loop working I could then ask the question neither previous run asked: which of the 59
> documents failing `60` are actually font-limited? Thirty-two. The other twenty-seven take their
> column edge from a line drawn in Liberation Sans or Liberation Serif - families the engine already
> maps to metric-identical faces - so their edge is not a substitution artefact at all. Twenty-seven
> documents had been invisible inside a class counted as one problem.
>
> And what they do is the opposite of the story. I built `edgeprobe.py` to print the numbers `60`
> compares, and cross-checked it to the digit against the previous run's own recorded
> `477.66 vs 538.63, tolerance 48`. On five of the twenty-seven, every column on the page lands within
> a couple of points of the source except one, and that one runs 77 to 161 pt PAST it. `gst-invoice-3line-items`
> is 161.18 pt over on a 112 pt source column - a 2.4x widening. That is a lost table cell width or a
> lost wrap in `PdfToWord`, not a narrow face and not a tolerance miss, and it is visible in `w:tcW`
> without any renderer at all.
>
> What I would have done with another thirty minutes, in order: open `gst-invoice-3line-items`'s
> `w:tcW` against its source column and see why a 112 pt column arrived at 273 pt - a 2.4x widening has
> one likely cause and it is cheap to name; then the same on `purchase-order` (+103.36) and
> `delivery-challan` (+77.21), to see whether it is one cause or three; then the `far >= 2` safety net
> in `edgeprobe.py`, which is the reason `marksheet-subject-left-marks-right` and
> `very-long-single-column-table` pass every column and still fail the check, and is one function.
>
> None of that is blocked. It is what the clock cost.

## The txt

| | |
|:--|:--|
| Measured | **1.0 h ago** |
| Scored | **214** of 214 |
| Clean - every applicable check passes | **209** (97.7%) |
| Failing at least one check | **5** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 14:35 → running · 13 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 16 |
| Longest silence | **8.7 min** — from 14:35:53, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **4 min** | `########` |
| measure or build - a conversion, screen or compile writes no beacon | **8 min** | `##############` |
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
