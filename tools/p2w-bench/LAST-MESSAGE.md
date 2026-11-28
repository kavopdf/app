# P2W Fixer - Run Report

**28 Nov 2026 · slot 08:24 → running IST · 43 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - attempts: RUN.json counter 5 vs ATTEMPTS.json history 4; kept change: 2 code commit(s) in this window, first: findings: the U+FFFD geometry route is a guess t vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; subagents: 2 deployed vs no FINDINGS filename carries 18_dA-02, 05_cB-01 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 5 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **48** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (62 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 08:54 | **lead** | 0/None | The 25 Nov recovery path for the 127 U+FFFD ligatures ('fall back to the glyph name - PDFBox exposes it') is refuted by measurement with the engine's own reader: for 041122-Account_Opening_Form the fo |
| 08:54 | **lead** | 0/None | Google-side baseline measured for 35_four_typefaces_one_page (the gap the 05:54 run named): dy -1.96..-3.71, so Google does NOT preserve the cell baseline and the w:line patch's 'zero move' premise is |
| 08:56 | **lead** | 0/None | The falsifier named in the first attempt was run: five Google builds of 35_four_typefaces_one_page (trHeight atLeast/exact 380/377, cell w:line natural, cell w:before 373). Google's row height is a QU |
| 09:06 | **lead** | 0/None | Swept the falsifier: cell w:before 368/370/371/373 twips in Google. Pitch laid = 18.75, 19.24, 19.29, 19.39 against a source 19.00. There is a 0.49 pt discontinuity between 368 and 370 twips and 19.00 |

## Why nothing moved, in this run's own words

> > **The decision, and its reason.** `classpick.py` suggested `05_chars_extra` (an open lead) and the
> > previous run left `18_displacement` with a named next step and one gap: *"there is no Google export of
> > `35_four_typefaces_one_page` anywhere in the repo, so the Google side of every number is the recorded
> > verdict, not a measurement I took."* I closed that gap first, because it decided whether the named
> > patch was worth building at all.
> >
> > **The patch was refuted before it was built, which is the cheapest thing that happened.** The 05:54
> > lead predicted "a zero move in Google if and only if Google already preserves the baseline". Google
> > does not: −1.96 pt on the first row, −3.71 on the seventh, one-signed. LibreOffice moves the same cells
> > **+3.70 the other way**. Two renderers, opposite signs: any validation done in `soffice` in this class
> > is worthless, and the lead's premise was false.
> >
> > **Then I asked what else could hold the pitch, and measured it in Google instead of arguing.** Five
> > builds of the same document, one attribute apart each time: `trHeight` 380 `atLeast` (shipped), 380
> > `exact`, 377 `exact`, the cell's `w:line` set to its natural box, and the cell's `w:before` moved 5
> > twips. The rows came back at **18.75, 19.14, 19.14, 20.90, 19.39** against a source pitch of 19.00.
> > Google lays `atLeast` rows at *content* height — below the floor it was given — and it **quantises**:
> > 5 twips of `before` moved the row 0.64 pt, and 380 vs 377 exact landed on the same row. There is no
> > value you can compute that lands on 19.00. That is why this class has survived every attempt: the
> > `.docx` cannot express the target and the renderer steps over it.
> >
> > **The second class was closed the same way, from the other side.** `05_chars_extra`'s open lead said
> > the 127 `U+FFFD` ligatures could be recovered from the glyph name, "PDFBox exposes it per glyph". With
> > the engine's own reader: no `post` table, no `cmap` table, no encoding name, and the PDF's own
> > `/ToUnicode` maps `0x123/0x124/0x126/0x127` to `<FFFD>` by the producer's hand. The name is not there
> > to fall back to. The only route left is geometric (a ligature's advance width against its components'),
> > which is an inference — and a second agent measured it in the same slot: 0 of 127 occurrences resolve
> > uniquely, and the 89 that make up 70 % of the document land nearest to the wrong ligature. So that
> > class is closed from the PDF's own data, not parked waiting for a patch.
> >
> > **Why nothing landed, stated plainly.** Both results are *refutations of a named next step*, not
> > engine fixes, and a refutation cannot be committed as a change: there is nothing to change. The one
> > change that was in reach — a cell-spacing patch — is exactly what the five probes measured as
> > unfixable by numbers. Landing an engine change also needs the full re-measure (16 min convert plus the
> > render and score), and this slot spent its first 25 minutes on a delegated Google measurement that
> > returned inside the turn rather than in the background.
> >
> > **What I leave behind, and what would overturn it.** Three findings with the raw measurements, four
> > reproducible probe builds, and a new probe tool (`GlyphProbe2.java`) that answers "what does this font
> > still know about this glyph" in one command. The next run should not spend a slot on `w:line`/`w:before`
> > arithmetic in table cells, nor on a glyph-name fallback for `U+FFFD`. What would overturn the first: a
> > `before` in the 368–373 twip band whose Google export lays 19.00 on all seven rows. What would overturn
> > the second: a revision of the form whose `/ToUnicode` maps those codes to real characters.

## The txt

| | |
|:--|:--|
| Measured | **3.7 h ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18_dA-02` | take a real Google export of 35_four_typefaces_one_p | 08:56 | - | - |
| `05_cB-01` | test whether the U+FFFD ligature glyphs resolve by a | 09:05 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 08:24 → running · 43 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 39 |
| Longest silence | **16.4 min** — from 08:27:14, after `claimed; deploying agents, then pod-prep` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **5 min** | `###` |
| build - compiling the engine | **3 min** | `##` |
| fix - diagnose and change the engine | **3 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **24 min** | `#############` |
| record - attempt, handoff, class rows | **2 min** | `#` |
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

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
