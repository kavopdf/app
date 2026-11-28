# Fixer report - 2026-11-28 11:59

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 11:59 → running IST · 10 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - .txt age: measured 6.7 h ago vs nothing re-measures it on a schedule; subagents: 1 deployed vs no FINDINGS filename carries 18dA18_displacem - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> **The lead was a measurement somebody else had already made, and my job was to land it or refute it.** The previous run built a `TxtWriter` change, measured it, wrote both hunks into `FINDINGS/TXT-SPLITS-A-LETTER-SPACED-LINE-INTO-ONE-LINE-PER-GLYPH-28NOV-relay.md`, and ran out of slot before it could commit. It named its own overturning condition: *a corpus re-conversion in which a document other than 305 moves, or in which any document's pass count falls*. I ran exactly that test. It passed.
>
> **The class is `t08_line_order`, and the reason is the document, not the class.** `305_vaccination_certificate` was 6 of 7 and one page, and the single failing check was line order 32 against a source 33. The page draws a letter-spaced seal whose glyphs sit on baselines that are not horizontal, so the seal paragraph carries no `lineY` at all; the model appends it last in `page.blocks`, after a footer at y = 781.9, while its own `top` is y = 270.9. I did not pick this class because it looked easy or because the rotation said so — the rotation said `18_displacement`. I picked it because a measured, already-built change was sitting one commit away from a clean document, and a lead that has been measured outranks a class that has not.
>
> **I audited the patch before I trusted it, and the audit found the relay file wrong in three places.** A sub-agent read the two hunks against HEAD: hunk 1 was not a diff at all (it printed the new method and *described* the rename in prose, so applied literally it produces two methods named `pageOrder` and does not compile), the guard is `if (ly > 0f) lastY = ly;` — a test on the current line's baseline, not on `lastY` — and `Para.top` is in the wrong frame for a 180°-turned line, which is why `pageOrderByColumn` orders by `paraTop()` and the hoist cannot. I applied the corrected diff, not the relay's.
>
> **Then the run hit a defect that would have made it report "my patch did nothing".** The first corpus pass converted 165 documents, printed `DONE - 214 documents converted`, and left `305`'s `.txt` at the pre-patch answer: `FAIL, t08 32 vs 33`. The cause is not the patch. `corpus-convert.py` keys the corpus cache on `engine_sources(fmt="docx")`, and that fingerprint **excludes `TxtWriter.java`** — correctly, for a `.docx` cache — so a change to `TxtWriter.java` is invisible to `corpus-slice.py`, which saw 49 documents it had built at 05:29 on the unpatched engine and declared the corpus current. The 49 include the one document the patch is for. A single-document `ConvertOne` probe had already said `PASS` from the same tree; the corpus said `FAIL`; the difference was which files the cache had decided were current, not the engine. I added `corpus-slice.py --force`, which re-converts every document whose `.txt` mtime predates the newest `engine/*.java` and resumes by file time so it still slices. It said `49 of 214 .txt predate the newest engine source`, one 265 s slice converted all 49 with 0 failures, and `305` then verified `PASS` from the corpus output.
>
> **The measurement, and it is deliberately not the gate's.** `restamp_txt.py --apply` writes `RANKING-TXT.csv` *and* `RANKING-TXT-BASELINE.csv` from the same new results, and `regress.py` compares those two files — so after an `--apply` that comparison is new-against-new and cannot fail whatever the change did. The gate's line `txt: no document worse than baseline` is therefore not evidence for a `.txt` change made in the same run. I copied the store to `/scratch/work/` before the re-stamp and diffed it myself:
>
> before: 214 docs, 208 clean
> after : 214 docs, 209 clean
> improved: 1   worsened: 0
> BETTER 305_vaccination_certificate  (7, 6, 1, t08_line_order) -> (7, 7, 0, '')
>
> **The `.docx` claim is a measurement too, not an argument.** `scope.py` did not know `pageOrder`, so it would have fallen back to `both` and demanded a 54-minute `.docx` re-measure. I added `TxtWriter.pageOrder`, `pageOrderByColumn` and `hoistLastPara` as `txt` — `pageOrder` is private static with exactly one caller, `TxtWriter.java:95`, inside `write()`, and `DocxWriter` never calls it. Then I checked it rather than asserting it: the 49 `.docx` this engine rebuilt are byte-identical to the 49 they replaced, 49 of 49, by `sha256sum -c`. `regress.py --check` answers `docx: out of scope`, `txt: no document worse than baseline`, `google-safe: no construct Google ignores has spread`, `PASS`.
>
> **What is not proven, and it is the next run's first question.** The audit's sharpest objection stands: the hoist moves a ring or a stamp from the end of the file into the middle of the body on 27 pages of 27 documents, and for a *circular* seal `top` is the topmost glyph of the circle, not the seal's reading start — so ~40 single-character lines now sit inside the body text. `t04` and `t08` cannot see this; neither tests contiguity. `0 worsened` is a statement about checks, and it is not the same statement as `no document reads worse`. That is a reader question, and no check in `verify_txt.py` asks it.
>
> **What would overturn this.** A document whose `.txt` now reads worse to a person, on the 26 non-305 pages the hoist touches — in which case the hoist narrows to paragraphs with no `lineY` **and** a `top` inside the page's text band, rather than to any last paragraph. The second overturning condition is the one I ran and it held: 0 documents fell in pass count.

## The txt

| | |
|:--|:--|
| Measured | **6.7 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
| Scored | **214** of 214 |
| Clean - every applicable check passes | **209** (97.7%) |
| Failing at least one check | **5** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `18dA18_displacement-01` | engine | 12:09 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 11:59 → running · 10 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 3 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

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
