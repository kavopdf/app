# P2W Fixer - Run Report

**21 Nov 2026 · slot 21:11 → running IST** — class `32_stroke_lines`, taken on the open lead.

> **No engine change was kept, and the reason is a measurement, not a shortage of time.** The lead
> was priced: the carrier patch two runs wrote is worth **one** document of the 192 Google scores,
> and as it stands it puts floating tables into documents that have no rules at all and moves a
> paragraph 122 pt. Both numbers were measured in this sandbox this slot, before and after, and
> both are committed with the patch reverted.

## What this run actually changed

| | |
|:--|:--|
| Corpus in the sandbox | **213 of 213**, from the `corpus-v1` release assets, in 6 minutes |
| Engine built | yes, 37 s |
| Commits pushed | 3 — a FINDINGS file and two new tools |
| Engine commits | **none** — see below |
| Documents made clean | 0 |

**The wall two runs hit is gone.** `regress.py` refuses any docx engine change whose table was not
measured on that engine, and the corpus is not in the repository, so every run ended with an
unlandable patch. The corpus is four release assets and five PDFs that travel in the repo.
`tools/p2w-bench/corpus-fetch.sh` now does it and refuses if any of the 213 is missing. `p2w.py
--budget` is a *time* budget and manages ~26 documents per 250 s, so a full pass is ~33 minutes of
wall clock across several commands — a known number now instead of a guess.

## What the census found

Every page of every corpus PDF, read with the instrument's own rule definition
(`verify_google._rules`, imported, not re-implemented):

| | |
|:--|--:|
| documents drawing no rule on any page | **53** |
| documents with at least one rule | **160** |
| … busiest page holds at most one | **14** |
| … busiest page holds two or more | **146** |
| rules counted across the corpus | **1170** |

Crossed with the committed Google results: **35** documents fail only within `{05_chars_extra,
18_displacement, 32_stroke_lines}`. **32** of them carry rules, and **31 of those 32 have two or more
rules on a page**. The floating-table carrier that is already written and measured on
`394_map_with_legend` places one table per page and stacks every later one, so it can make at most
**one** of them clean. The row-per-rule construct is the precondition for the lead, not an
optimisation of it.

## What the second measurement falsified

Built the patched engine, converted six documents, byte-compared against HEAD, reverted.

| document | rules (instrument) | `w:tblpPr` the patch emits |
|:--|--:|--:|
| `305_vaccination_certificate` | **0** | **20** |
| `303_discharge_summary` | **0** | **15** |
| `77_arabic_rtl_document` | **0** | **4** |
| `80_gstin_pan_cin_ifsc_table` | 0 | 2 |
| `76_devanagari_table` | 0 | 0 |
| `15_stamp_on_scanned_page` | **0** | 0 |

`isRuleShape` has no isolation test; the instrument's `_rules` has one (`RULE_GAP` 3 pt). So the
carrier takes every table grid line drawn as a thin fill — and the carrier stacks. On
`303_discharge_summary` the same paragraph's `w:spacing w:before` also went **6740 → 4291 twips**:
the carrier is not zero-flow there, and the `.txt` is byte-identical on all three, so no `.txt` check
would have seen it. The narrow predicate is the next build, before the row construct.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 0 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `-` |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Why the class was taken

`classpick.py` suggested `32_stroke_lines` because it holds an open lead, and `--leverage` prices the
class at 36.3 clean documents. I took it on that arithmetic and then tested the arithmetic itself:
the 36.3 is reachable only through a carrier that handles multiple rules per page, and 31 of the 32
candidate documents need exactly that. The lead was worth taking; the patch that carries it was not.

## What the next run should do

1. **Narrow `isRuleShape` to the instrument's definition** — thin face ≤ 4.0 pt, long face ≥ 10 pt,
   and not touching another stroke within 3 pt. Re-convert the six documents above and confirm
   `tblpPr` counts fall to the census's rule counts. That is one build and six conversions, ~5 min.
2. **Probe `w:hRule="exact"` on a floating-table row through Google** before building rows: three
   rows, 40 pt gaps, read the three border y's out of the export. If exact is not honoured every
   rule after the first drifts by the empty cell's line box.
3. **Then build one table per page with rules as rows**, and measure the 31.

Do not land `rule-carrier-tblppr-2008.patch`. It is worth one document and it changes 146.

## Subagents

One agent, on the carrier design. It could not read the repo — its sandbox had no clone and no
`/scratch/input`, and it said so instead of inventing line numbers, which is the useful part. Its
OOXML element ordering and its list of unmeasured questions are in this run's reasoning; the design
detail it produced that this run verified independently is the `w:sz` eighths-of-a-point rule and
the `w:tblCellMar` 5.4 pt inset, which matches the landed finding.

## Timing

| | |
|:--|:--|
| Slot window | 21:11 → running · 11 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 7 |
| Longest silence | **4.4 min** — from 21:11:30, after `gaps.py: reading the timeline` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **4 min** | `#########` |
| measure or build - a conversion, screen or compile writes no beacon | **0 min** | `##` |
| report - the report and the chain | **0 min** | `##` |
| other - not attributed to a tool | **5 min** | `##########` |

