# P2W Fixer - Run Report

**21 Nov 2026 · slot 07:58 → running IST · 2h 44m**

> The carry-over was measured three ways and the gate refuses it on one document - and the reason three previous runs could not measure anything at all is now fixed and on main.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |

## The thing that was actually broken

Three runs in a row ended with the same sentence: the corpus can only be measured on an engine that is already pushed, and the commit gate refuses an engine whose table was not measured on it. Each rule is right alone; together they made every engine patch uncommittable, and that is why the widget patch sat measured on two documents and unlanded since 04:36.

`p2w.py` now takes `P2W_ENGINE_SRC=<clone>` and builds from that tree instead of forcing `origin main`. Unset, nothing changes. The gate is untouched.

Two more, both measured and both fixed in the same commit:

- `measure_doc_chunked` reported where it had got to and then threw the windows away, and `run()` never saved them. `416_many_tiny_pages` is 300 pages and alphabetically first, so every pass re-measured its first 60 pages and stopped. Six consecutive 290 s passes this run each ended on it at `measured 114 of 213`. Progress is now kept in `dist2/<name>.partial.json` and the queue runs shortest document first. 114 → 212 of 213 in four passes.
- The exempt-set filter in `run()` now exists, so a future exemption is honoured by the loop that measures, not only by the counter that ranks.

## What was tried, and why it did not land

| variant | 601 share@5px | Account form share@5px |
|:--|--:|--:|
| pristine HEAD | 52.39 | 97.62 |
| full widget walk | **0.00** | 98.65 |
| state dictionaries only | 51.28 | 98.65 |
| plain streams only | 0.25 | 98.06 |

Same tree, same render path, pristine HEAD built and scored beside each variant in this run. `601_fillable_admission_form` goes from the worst document in the corpus to a perfect page, and its docx checks go 38/42 → 42/42. `Account_Opening_Form_Fillable_filled` goes up 1.03, in every variant that emits widget text at all, and the gate refuses one document worse.

It is not a layout regression: that form is 97.62 - 97.6 % of its ink already more than 5 px from where the page drew it - so any correct ink added to it is also displaced, and share@5px is a fraction of source ink. Its matched population triples (`17_matched_runs` 272 → 803) and its docx checks go 19/42 → 23/42 on the same document. But the gate cannot tell that from a page that got worse, which is what it is for. A fixer may not authorise the trade.

Corpus-wide, on the patched tree: 205 documents scored to the hundredth identical to the published table, 0 worse, 1 better. An annotation census over all 213 found exactly 3 documents carrying any annotation, so 210 are unreachable by any version of this patch. Engine reverted; attempt 14 recorded.

**A person decides one of three:** authorise the trade, give share@5px a companion axis that separates "more ink, some of it far" from "the same ink, further", or keep the walk out. It is row one of `BLOCKERS.md` and `FINDINGS/widget-walk-REFUSED-BY-ONE-DOCUMENT-1050-f1x.md` carries all four numbers, so no run needs to re-derive them.

## Two agents, both landed

**The 47\_margins `.txt` half does not exist.** `verify_txt.py` has 12 check ids and `47_margins` is not one of them; the `.txt` analogue is `t02_position`, holding 5 documents, not 14. Four of the five are the instrument - a text-pairing collision in the verifier on two, a bbox-versus-ink reading on one, a ruler 9 % coarse on one - and one is a real two-line engine defect: a page turned 180° whose glyphs are not flagged `rotated`, so the guard bails and every line lands mirrored. Measured over 213: that document 50 % → 100 %, 1 document of 213 changed, three named regression candidates all byte-identical. Not landed: the docx side of that patch was not measured and the gate scopes a `PdfToWord` change to both formats.

**The 127 U+FFFD sites on the bank form are ligatures.** Eight sites inspected at 600 DPI, all four CIDs, all three faces: ff, fi, ffi and ffl. So `fffd-cmap-destination-2300-fixer.patch` must not be applied - it appends one character per CID and would write a wrong letter at 127 places in a document that is visibly correct today. The identity is still not recoverable from the file (no `cmap` in any embedded program, `/ToUnicode` answers U+FFFD), so the choice between Effra outlines and a word list is a person's.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## What the next run should do first

Build the `t02_position` two-line fix from `FINDINGS/47_margins-TXT-HALF-IS-T02-1055-f1x.md` and measure **both** formats - it is the only engine defect left in that half, it is measured at 1 document of 213 moved, and `P2W_ENGINE_SRC` now makes the corpus measurement possible before the push rather than after it.

## Timing

| | |
|:--|:--|
| Slot window | 07:58 → running · 2h 44m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 17 |
| Longest silence | **119.2 min** — from 08:40:45, after `attempt.py: recording an attempt` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | The walk fixes 601 completely - share@5px 52.39 -> 0.00 and docx checks 38/42 -> 42/42 - and it moves Account_ |

The 119-minute silence is the two subagents. They run inside the fixer's turn here, not in the
background, so nothing writes a beacon while they work and `gaps.py` reads it as a dead run. Both
landed with their findings; the measure is the instrument's, not the run's.

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2h 41m** | `######################` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **0 min** | `#` |

## Committed

`c6eb970` - measure: the corpus can be measured on an unpushed tree, and 416 can resume. Three tooling fixes, four findings, one blocker row, no engine change.
