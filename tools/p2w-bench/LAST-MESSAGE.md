# P2W Fixer - Run Report

**21 Nov 2026 · slot 12:12 → running IST · 36 min**

> No change was kept this run. The numbers below say what was tried.

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
| Committed | **20** files in 4 commit(s) from `8206f46` — ...-PBDR-IMPLEMENTATION-SUPERSEDED-124500-relay.md, ...troke_lines-A-pbdr-verification-124000-relay.md, ...troke_lines-B-rule-flow-neutral-124500-relay.md, ATTEMPTS.json, BLOCKERS.md, CLASS-HISTORY.jsonl, HANDOFF.json, H |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 12:46 | **error** | 0/37 | pBdr carrier construct refuted before a build: three findings (044000 shape emitted after flow, 055000 flush-by-top turns 18_displacement PASS->FAIL, 065000 carrier costs 9.6 pt whatever it contains) |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `32_sA-01` | Verify the pBdr implementation in FINDINGS/RULES-PBD | 12:14 | 07:10 | 26 min |
| `32_sB-02` | From the source PDFs, count horizontal hairline rule | 12:14 | 07:10 | 26 min |

## Timing

| | |
|:--|:--|
| Slot window | 12:12 → running · 36 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **24.6 min** — from 12:14:42, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 3 |
| Obstacles | 1 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | `_done()` in gverify.py counts a document as measured only when its result carries the CURRENT engine stamp (` |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **0 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **24 min** | `###############` |
| record - attempt, handoff, class rows | **5 min** | `###` |
| report - the report and the chain | **6 min** | `####` |
## What this run did

Two things, both proved with a number, neither of them an engine change. The class `classpick.py`
names is `47_margins`, and it was not started: the gate's first item was a carry-over that three of
our own findings had already refuted, and clearing it was worth more than a fourth attempt at it.

### 1. The pBdr carry-over is closed, not parked

Every run since 19 Nov opened with "land `RULES-PBDR-IMPLEMENTATION.md`, it predicts 124 documents
cleared". It is refuted three ways by measurements already in `FINDINGS/`, and today's two subagents
re-derived the same answers independently:

* the carrier paragraph costs **9.6 pt of flow whatever it contains** - border, inert element, no
  run, any `w:line` (065000);
* the flush-by-top precondition was built and turned `18_displacement` **PASS -> FAIL** (055000);
* a shape is appended to `page.blocks` **after** the page's paragraphs, so `s.topPt > ctx.flowY` is
  never true and the `w:before` gap is never computed (044000).

Re-checked in the tree today: `ruleAsBorder`/`w:pBdr` **do not exist** in the engine; every symbol the
snippet needs does; and the 065000 guard is **unsatisfiable by construction** - `flowFromBox` gives a
left-aligned paragraph `rightTw = 0`, so its right-edge test demands the rule reach the paper edge,
and **0 of 2136** corpus rules pass both edges. The ceiling is the hook, not the guard: 3 of 39 rules
on the document made entirely of rules. Any future attempt must start from **no new paragraph**.

### 2. Two checks that could never fail, now able to

`health.py` held its thresholds in **seconds** while every age it computes is in **hours**, so four
of five stages could not read `stopped`. Measured on the live tree: `txt` read **moving at 13.2 h**
against a 12 h intent; it now reads **stopped**, and `--stalled` went from `STOPPED: fix` to
`STOPPED: fix, txt`. A guard refuses any threshold over 48, tested by putting `12 * HOUR` back -
exit 3, "it is seconds, and it can never fire". `classify` gained a `superseded` state so a table
newer than the results it summarises is not a false alarm; the branch was proved to fire.

`lastmessage.py` wrote `LAST-MESSAGE.md` for **every** caller, so a watchdog pass replaced the
fixer's committed message with a watchdog table (it happened on 20 Nov). It now gives the fixer that
file and every other cron `LAST-MESSAGE-<cron>.md`; a real write through `--for health` created its
own file and left the fixer's **byte-identical**.

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
