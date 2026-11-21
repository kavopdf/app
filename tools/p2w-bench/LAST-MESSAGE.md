# P2W Fixer - Run Report

**21 Nov 2026 · slot 15:58 → running IST · 1h 24m**

> **The fix I proved was already landed by a second fixer while I was proving it.** I converted the
> whole 213-document corpus twice - 213 of 213 `.docx` byte-identical, exactly one `.txt` changed - and
> went to commit: `462353f` had landed the same fix with the same proof at 17:00. My duplicate commit
> was reset away. What this run actually changed is below.

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

## What this run actually changed

| | |
|:--|:--|
| Dead carry-over cleared | **1** — the pBdr rule replacement, refuted three ways |
| Obstacle recorded | **1** — two fixers ran one slot and duplicated 65 minutes |
| Documents improved | **0** — the fix landed from the other run, not this one |

**The carry-over was dead and the gate kept handing it over.** `RULES-PBDR-IMPLEMENTATION-SUPERSEDED-124500-relay.md`
says at 12:45 that "the carry-over is cleared so the gate stops handing it to the next run". It was not
cleared. `HANDOFF.json["next"]` still carried it through 12:45, through the 15:17 run, and through
`462353f` at 17:00 — four consecutive runs opened by reading an instruction three findings had already
refuted. A finding cannot clear a carry-over; only `handoff.py --next` can, and no run had called it.
It is called now, and `pending.py` no longer prints it.

**The duplicate, with numbers.** `round.py --claim-fixer` returned `fixer claimed at 16:16`, exit 0, and
a second run did the work anyway and committed at 17:00. Both converted the corpus twice: 2 x 213
conversions at about 5.8 s each is roughly 42 minutes of conversion spent to produce one commit.
`BLOCKERS.md` carries the row and the two ways out.

**The measurement this run did make, and it is the one worth keeping.** The previous run left 140 of
213 `.docx` compared and named the other 73 as "what would prove this wrong". Closed: HEAD from
`17099ac` and the patched build from the same tree, `ConvertOne` one document per JVM, all 213 each
way — **213 of 213 `word/document.xml` byte-identical, 212 of 213 `.txt` identical**, the one
difference being `one-page-rotated-180-degrees` (8986 -> 9312 bytes, `t02_position` FAIL -> PASS).

**The number that explains a month of "it does not fit in the slot".** A full `.txt` corpus pass is
213 conversions at about 5.8 s serial — **21 minutes** — plus 71 s to re-score. This sandbox has
**2 CPUs and 2 GB of RAM (1 GB free)**, so four JVMs at `-Xmx700m` do not fit and the conversions
cannot be parallelised. It fits in about half a slot, and that is now in `HANDOFF.json["next"]`.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `32_sA-01` | Does the pBdr replacement in FINDINGS/RULES-PBDR-IMP | 15:59 | - | - |
| `t02_B-01` | The 180deg uprightIfPageIsUpsideDown patch (FINDINGS | 15:59 | - | - |

Those two are the **other** run's agents, not this one's. None were deployed here, and the number that
says why: the 15:17 run measured `delegate_task` with `background=true` being run *inside* the turn for
**26.6 minutes** - 86 % of a half-hour slot. This run's first work was a corpus conversion of known
duration and known value, and firing two agents ahead of it would have spent the slot before it began.

## Timing

| | |
|:--|:--|
| Slot window | 15:58 → running · 1h 24m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 20 |
| Longest silence | **44.7 min** — from 16:37:48, after `HEAD rebuilt; converting all 213 to out-head for a byte-for-byte docx ` |
| Silences over 2 min | 7 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | **Two fixers ran the same slot and duplicated 65 minutes of work.** This run claimed at 16:16 (`round.py --cla |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **1h 18m** | `####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **3 min** | `#` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Take 32_stroke_lines from 'no new paragraph'. The pBdr carrier is refuted three ways (RULES-PBDR-IMPLEMENTATION-SUPERSEDED-124500-relay.md): w:pBdr needs a paragraph and a paragraph costs 9.6 pt on this engine, so the carrier IS the displacement. Not yet tried: a table-row bottom border, or a border on the paragraph the page already drew above the rule. Also: a full .txt corpus pass is 21 minutes (213 conversions at ~5.8s serial, 2 CPUs / 1 GB free - it cannot be parallelised) plus 71s to re-score, so it fits in about half a slot.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

