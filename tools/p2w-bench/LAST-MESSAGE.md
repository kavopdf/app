**21 Nov 2026 · slot 22:56 → running IST · 18 min**

> I spent this slot answering a question nobody had asked, and the answer is that the largest
> class in the corpus is measured by an instrument that cannot see the thing it is measuring.
> Check 32 scores a rule **LOST when Google drew it**. I proved that in both directions on
> Google's own exports, and then proved that fixing it still does not make one document clean -
> so it is a correction and a lead, not a fix, and I have not landed it.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 23:13 | **lead** | 0/192 | CHECK BLIND TO PICTURES, measured both ways. _rule_segments() (verify_google.py:1082) walks get_drawings() only; Google exports every anchored shape as a raster image, so a rule it drew reads as zero |

## The class I chose, and why

I did not take the tool's suggestion. `classpick.py` said `t08_line_order`, worth about 10 clean
documents, whose `.txt` half already moved 9. I took `32_stroke_lines` for the arithmetic in
`classpick.py --leverage`: it is worth **36.3 clean documents**, the largest single figure in the
corpus, and it travels with `05_chars_extra` (35.0) and `18_displacement` (28.6) as **one construct** -
41 of the 192 scored documents fail *nothing but* those three checks. One fix there is 41 documents.
It is also the class with six attempts and zero movement, which by the brief's own standard is the
reason to look harder at it rather than the reason to leave.

## Why nothing landed

Because the fix I found is not a fix. Two documents fail nothing but `32_stroke_lines`:
`394_map_with_legend` and `407_id_card_front_back`. I converted both with the current engine, put them
through Google Docs, exported them and scored them with check 32's own predicate. Making the check see
picture-drawn rules recovers **1 of the 3 rules on `394`** and **18 of the 46 on `407`** (its vertical ones, drawn as
15.0 x 1.5 pt raster strips at exactly the source x positions). Both still fail. The brief is explicit:
if nothing becomes clean, it cannot be a fix. So it is recorded as a lead with the patch on disk.

## The one measurement this run made that nobody had made

Six previous attempts argued about **which construct** to emit, because the class table said Google
drops the rules. It does not. Uploaded one at a time to Google Docs and measured from the export:

| construct | asked | Google drew | error | chars added | body text moved |
|:--|--:|--:|--:|--:|--:|
| the engine's own carrier paragraph | y = 140.0 | **139.88** | **-0.12 pt** | 0 | 0.69 pt |
| the same anchor inside a body paragraph | y = 140.0 | **139.88** | **-0.12 pt** | 0 | **0.00 pt** |
| floating table, `tcBorders/bottom` | y = 140.0 | 140.50 | +0.50 pt | 0 | 0.00 pt |
| `w:pBdr` on an empty paragraph | y = 140.0 | 141.50 | +1.50 pt | 0 | **+19.91 pt** |
| `w:pgBorders` | y = 140.0 | not drawn | - | 0 | 0.00 pt |

Google honours the engine's existing construct to a tenth of a point. `w:pgBorders` is the only one it
drops, and `w:pBdr` costs 19.91 pt of flow - the same per-carrier cost the 17:39 refutation measured,
which is why that path has died twice.

## The lead that outlives the run

The isolated rule draws perfectly on a clean page. The same construct draws **1 of its 3** on `394` and
**0 of 28 horizontals** on `407`. `394` carries 25 images on one page; `407` carries 41. The variable
that separates the probe from the corpus is **how crowded the page is, not the construct** - a
hypothesis no previous attempt has tested, because every one of them was changing the XML.

Cheap test for the next run: N copies of the same anchored rule on one page, N = 1, 2, 4, 8, 16, 32,
one export, find where Google stops placing them. If there is a threshold, the fix is to stop emitting
one anchored object per rule, not to change what a rule is made of.

## The instrument defect, and why it is not landed

`_rule_segments()` (`verify_google.py:1082`) walks `get_drawings()` and nothing else. The file already
says in capitals, above `_strokes()`, that Google's export has no vector paths at all and that
`_stroke_pictures()` fixes the render side - and `_strokes()` calls it. `_rule_segments()` was written
later, is the path check 32 actually uses, and never calls it. The two return different shapes
(`{rect,width,colour}` against `{o,perp,a,b,t,col}`), which is why they were never merged; merging them
naively raises `KeyError: 't'`. The patch that maps one into the other is
`patches/rule-segments-see-pictures.patch`.

It is not applied. It can only turn lost to matched, so it can never make a document worse, but the size
of the flip across 192 Google documents is **unmeasured**, and changing a check on an unmeasured corpus
is how a tool ends up passing everything. A corpus pass measures that column first; then it is a
one-line switch.

## Falsification, in both directions

Ten probe `.docx` were uploaded to Google Docs and exported. `rule-base` asks for no rule at all;
`rule-v6_pgborder` uses `w:pgBorders`, which Google drops. Those are the negatives.

| Google export | construct | BEFORE | AFTER | must be |
|:--|:--|:--|:--|:--|
| `rule-base` | no rule in the docx | 0 matched / **1 lost** | 0 matched / **1 lost** | stays LOST |
| `rule-v6_pgborder` | `w:pgBorders` | 0 matched / **1 lost** | 0 matched / **1 lost** | stays LOST |
| `rule-v1_drawing` | the engine's own carrier | 0 matched / 1 lost | **1 matched / 0 lost** | becomes MATCHED |
| `rule-v1b_inline` | anchor in a body paragraph | 0 matched / 1 lost | **1 matched / 0 lost** | becomes MATCHED |
| `rule-v3_tblppr` | floating table border | 1 matched / 0 lost | 1 matched / 0 lost | unchanged |
| `rule-v2_pbdr` | `w:pBdr/w:bottom` | 1 matched / 0 lost | 1 matched / 0 lost | unchanged |

Both negatives held and both positives gained: the change invents no rule where there is none and does
not paper over a rule Google genuinely lost.

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
|:--|:--|:--:|:--:|:--|
| `rule-census` | which construct Google actually draws, at what y, with what cost | 22:58 | **the construct table above**, 10 Google round trips | 12 min |

**One agent, not two.** The second would have been the `t08` `.docx` half, and I did not send it
because the leverage arithmetic put `32_stroke_lines` at 36.3 against `t08`'s 10. The census agent
returned inside the turn, so it cost nothing in waiting - but it also means this run has one angle,
and the crowding hypothesis it produced is untested.


## Timing

| | |
|:--|:--|
| Slot window | 22:56 → running · 18 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 11 |
| Longest silence | **14.4 min** — from 22:56:17, after `pending.py: reading the pending gate` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **16 min** | `###################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| other - not attributed to a tool | **1 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Judge the t08 verifier question before touching the engine: is t08_line_order measuring line order or drawing order? FINDINGS/t08_line_order-DRAWING-ORDER-1740.md has the numbers (10 of 10 rows clear when only our own line sequence is put into drawing order). The agent's proposed one-line sort of _src_pages is NOT obviously right - it would compare sorted-vs-sorted. Decide with a falsification: construct a .txt whose lines are deliberately swapped in y and confirm t08 still fires after the change. Then take t01_word_accuracy's .docx half or 32_stroke_lines' cell-border construct.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
