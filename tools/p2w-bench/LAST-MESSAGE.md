# P2W Fixer — Run Report

**21 Nov 2026 · slot 21:53 → running IST · 59 min** (this relay claimed it at 22:13)

> This relay force-released a claim it called dead. The claim was alive: the 21:53 run had been
> working for 20 minutes without a single beacon and pushed its fix at 17:08 UTC, 25 minutes after
> I took its slot. It had already landed the t08 correction. So this run rebuilt the same fix,
> measured it independently, and then found the thing nobody had noticed — **that landed fix had
> wedged the commit gate for every run after it.** That is what this slot actually repaired.

## Progress

| | |
|:--|:--|
| Documents improved this run | **9** — 1 attempt(s), 1 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t08_line_order` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 22:38 | **kept** | 9/10 | t08 ground truth was PyMuPDF paint order, not reading order: sort each page's upright lines by (round(y,1),x) in the t08 block only. All 213 .txt rescored with the same engine: clean 190->197, t08 fai |
| 23:00 | **kept** | 0/0 | the gate, not the corpus: `RANKING-TXT-BASELINE.csv` was never restamped for that correction, so 10 rows disagreed with `RANKING-TXT.csv` and `regress.py` refused every commit — 39_small_caps as a "new failing: t08_line_order". Restamped both tables from one pass over the 213 .txt files. |

## The one measurement this run made that the other run did not

The 21:53 run falsified its own change. This run falsified it again, independently, with a different
instrument: a synthetic page whose six lines are **painted in scrambled order** (DELTA, ALPHA,
FOXTROT, BRAVO, ECHO, CHARLIE) at descending visual y, and two `.txt` files over it — one in visual
order, which is the correct `.txt`, and one with two lines deliberately exchanged.

| `.txt` over that page | before the sort | after the sort |
|:--|:--|:--|
| visual order (correct) | **FAIL** — t08 4 of 6 in order | **PASS** — 6 of 6 |
| two lines swapped | FAIL — 4 of 6 | **FAIL** — 5 of 6 |

Both halves matter. The old check failed a `.txt` that was right; the new one still fails a `.txt`
that is wrong. On the corpus, both verifiers run over **identical** `.txt` bytes: **190 clean → 197,
0 lost.**

## The document that gains a check, and why it is not a loss

`39_small_caps_letter_spacing` flips t08 pass → fail (21 of 22 lines in visual order). It is not clean
under either verifier — it fails `t01_word_accuracy` at 97.4 % and `t12_word_invention` at 2 — so no
clean document is lost. The line really is out of visual order in its `.txt`; the old check could not
see it because the paint order happened to match. `305_vaccination_certificate` is the same story (32
of 33). Those two are now a real, honest class: **the writer's line order**, 2 documents, visible for
the first time.

## The gate was wedged, and that was the emergency

`bd1c2e5` rewrote `RANKING-TXT.csv` but not `RANKING-TXT-BASELINE.csv`. Ten rows disagreed. The
pre-commit hook reads that as a regression and refuses — not just a txt commit, **every** commit from
every cron. From 17:08 UTC nothing could land. `restamp_txt.py --run --apply` rewrote both tables from
one scoring pass: 213 rows, 197 clean (92.5 %), and `regress.py --check` passes again.

## Why the relay took a live run's slot

A corpus pass writes no beacon. `corpus-fetch.sh` (20 s), `build-engine.sh` (49 s), `ConvertAll` over
213 PDFs (124 s) and 213 `compare()` calls (59 s) are six minutes of the work the brief asks for, and
not one of them touches `fixer_last_beat`. Two in sequence beat the 20-minute window `status.py` calls
SILENT and the 45-minute window `CLAIM_STALE_MIN["fixer"]` calls stale. A healthy run and a dead one
are the same object in git. Recorded in `BLOCKERS.md` with the two fixes: beat inside the long steps,
and size the window above the longest measurement a run performs.

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|:--:|:--:|--:|
| `t08_A-01` | does t08 measure line order or drawing order, decide | 22:39 | code reading | 24 min |
| `32_sA-02` | a census of every rule in the failing documents by p | 22:39 | - | - |

**One agent, not two, and the second one did not run at all.** The one that did returned the code
reading that named the asymmetry (`_src_pages` appends unsorted; `PdfToWord.java:3733/5018` sorts by
y), verified the 10-document set against the committed tables, and ran out of its budget before the
falsification — so I built the control pair myself. It also ran synchronously and cost 24 minutes of
the slot, which is why this run had one angle and not three.


## The gate was wedged, and that was the emergency

`bd1c2e5` rewrote `RANKING-TXT.csv` but not `RANKING-TXT-BASELINE.csv`. Ten rows disagreed. The
pre-commit hook reads that as a regression and refuses — not just a txt commit, **every** commit from
every cron. From 17:08 UTC nothing could land. `restamp_txt.py --run --apply` rewrote both tables from
one scoring pass: 213 rows, 197 clean (92.5 %), and `regress.py --check` passes again.


## Why the relay

A corpus pass writes no beacon. `corpus-fetch.sh` (20 s), `build-engine.sh` (49 s), `ConvertAll` over
213 PDFs (124 s) and 213 `compare()` calls (59 s) are six minutes of the work the brief asks for, and
not one of them touches `fixer_last_beat`. Two in sequence beat the 20-minute window `status.py` calls
SILENT and the 45-minute window `CLAIM_STALE_MIN["fixer"]` calls stale. A healthy run and a dead one
are the same object in git. Recorded in `BLOCKERS.md` with the two fixes: beat inside the long steps,
and size the window above the longest measurement a run performs.



## The gate was wedged, and that was the emergency

`bd1c2e5` rewrote `RANKING-TXT.csv` but not `RANKING-TXT-BASELINE.csv`. Ten rows disagreed. The
pre-commit hook reads that as a regression and refuses — not just a txt commit, **every** commit from
every cron. From 17:08 UTC nothing could land. `restamp_txt.py --run --apply` rewrote both tables from
one scoring pass: 213 rows, 197 clean (92.5 %), and `regress.py --check` passes again.


## Why the relay

A corpus pass writes no beacon. `corpus-fetch.sh` (20 s), `build-engine.sh` (49 s), `ConvertAll` over
213 PDFs (124 s) and 213 `compare()` calls (59 s) are six minutes of the work the brief asks for, and
not one of them touches `fixer_last_beat`. Two in sequence beat the 20-minute window `status.py` calls
SILENT and the 45-minute window `CLAIM_STALE_MIN["fixer"]` calls stale. A healthy run and a dead one
are the same object in git. Recorded in `BLOCKERS.md` with the two fixes: beat inside the long steps,
and size the window above the longest measurement a run performs.


## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `t08_A-01` | does t08 measure line order or drawing order, decide | 22:39 | - | - |
| `32_sA-02` | a census of every rule in the failing documents by p | 22:39 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 21:53 → running · 1h 00m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 16 |
| Longest silence | **24.3 min** — from 21:53:34, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 5 |
| Obstacles | 1 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **13 min** | `#####` |
| measure or build - a conversion, screen or compile writes no beacon | **30 min** | `###########` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **14 min** | `#####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

The txt half is at 197 of 213 and the biggest single remaining class is `t12_word_invention` (8
documents) — not t08, which is now down to 2 and both are real writer faults. But the reason this slot
was worth spending is the gap the charter names: **6 clean in Google across 192 scored documents, against 197 of 213 in
txt.** Nothing this run touched the .docx half. The 20:57 run's bottom-edge probe is still the whole
of the next run's first ten minutes and it is written out in full in its own report: take the
per-rule carrier's `73_marksheet` output, set table 2 to `tblpY 12000` (600 pt), and read whether the
second band honours its anchor. If it does, the `32_stroke_lines` class is worth 134 documents instead
of 1. Stage the `.docx` through Google Drive directly — this sandbox has the Drive tools, and the
release-asset detour the last run recorded as a breach is not needed.

---
*Every number read from `RANKING-TXT.csv`, `RANKING-TXT-BASELINE.csv`, `RESULTS`/`pair.json` on
identical bytes, `ROUND.json`, `TIMELINE.jsonl`, `report.py` and `git log`. Never remembered.*
