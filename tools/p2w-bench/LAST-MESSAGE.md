# P2W Fixer - Run Report

**22 Nov 2026 · slot 08:16 → running IST · 16 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **23**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `18_displacement` |
| Committed | **13** files in 3 commit(s) from `091b271` — 18_displacement-SPACER-REFUTED-0900-f1x.md, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSAGE.md, REPORT.md, ROUND.json, RUN-LOG.md, RUN.json, SETTLED.md, TIMELINE.jsonl, TRACE.md, screen.py |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 08:26 | **reverted** | 1/16 | table-top spacer w:line -> w:before + hairline: 1 of 16 moved (68_journal 12.09->11.24), none worse. REFUTED as the cause: RANKING.csv gives 68_journal max_pt 8.64, not the -114.8 the lead assumed; af |

## Why the lead died, and what replaces it

The 07:14 run left one instruction: the gap above a table is written as `w:line` on a 1 pt mark, and
Google reads `w:line` as a *multiple* of the face's line height, so a 144 pt spacer renders as
13.74 pt. Both halves of that are true, and the fix for it is real - `w:before` is the one vertical
length Google honours exactly, and the engine's own `ctx.flowTw` and `cenSetY` already charged the
full spacer. I wrote it as `w:before` with the box cut to a hairline, confirmed the XML in the emitted
document rather than assuming it, and screened all sixteen through Google. One moved, by 0.85 points.
The bar is four.

The reason is that the premise was already contradicted by the table the lead was reading. Every one
of the sixteen has `max_pt` between 1.44 and 17.76 pt; `68_journal_wide_table_spanning` is 8.64, and
the -114.8 pt figure came from a FINDINGS measurement that disagrees with `RANKING.csv` by a factor of
thirteen. A 130 pt spacer loss cannot produce a render whose largest error is 8.64 pt, and the render
after the change is the same document, line for line.

## The lead I formed and had to retract inside the same run

Fourteen of the sixteen read `median_pt` 0.96 or 1.44, and at 150 DPI a pixel is 0.48 pt, so I read
that as the whole page being two or three pixels out uniformly - one constant, not sixteen
constructs. A second agent was sent to find the constant and came back with the opposite answer, and
the code agrees with it: `benchmarks/p2w.py` computes `p50(dv) * 0.48` over `dv = d[sm & (d > 1)]`
where `d` is an INTEGER distance transform. Pixels at distance 0 or 1 are excluded, so the smallest
number the statistic can print is 2 px = 0.96 pt. **0.96 is the floor of the instrument, not a
measurement.** It is also self-contradicting as a cause: `18_displacement`'s tolerance floor is 1.5 pt,
so a real 0.96 pt offset would pass.

## The live question, which is the opposite one

Six of the sixteen - `22_invoice_four_columns_txtpos`, `41_coloured_headings_white_bg`,
`73_marksheet_subject_marks_grade`, `16_right_aligned_amounts_txtpos`, `29_dot_leaders_txtpos`,
`72_bank_statement_no_rules_right_amounts` - have `max_pt` 1.44 to 2.40 and `share5` 0.00, and
`18_displacement` fails them anyway. Reading the check settles how that is possible. Its tolerance
`clamp(0.35 * size, 1.5, 4.5)` is never below 1.5 pt, so a page with nothing more than 1.5 pt out has
`n_out` 0 and `worst_here` under 1, and neither the budget nor the tail clause can fire. The only
branch left is `if not ds: bad_pages.append(pg)` - upright text on the page and none of it matched.

So for at least two of the six, the fault is more likely run matching than vertical position, and no
vertical constant will ever fix it. That is stated with its caveat in the finding: the ink measure and
the check's run-dy are not the same quantity, so it is not airtight. What is airtight is that the ink
metric is structurally blind to that branch. **The test needs no build**: run `verify_google.py --json`
on one of the six and read which clause fired.

`71_invoice_space_aligned_no_rules` is genuinely displaced (share@5 26.88, `median_pt` 3.84, no table
spacer at all) and is a separate question.

## The bug that was worth more than the attempt

`screen.py` set `p2w.REPO` after importing `benchmarks/p2w.py`, but that module computes
`ENGINE_SRC = os.environ.get("P2W_ENGINE_SRC") or REPO` at module level, from
`/scratch/work/p2w/repo`. On a pod with no previous run that directory does not exist, so every
conversion died on `ClassNotFoundException` in under a second, nothing reached `dist/`, and the tool
printed "PARTIAL - 0 of 16 measured. Call again" for ever. The identical command with
`P2W_ENGINE_SRC` set converted and measured 16 of 16. This is the worst shape a bug can have here: it
does not report that it could not run, it reports that the idea did nothing - and the brief's next
line tells the run to revert. Any run on a fresh pod has been judging its ideas against a screen that
never ran. Fixed, and verified without an environment variable: 0 of 2 measured before, 2 of 2 after.


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
| `18_dA-03` | independently re-derive the sixteen and the spacer p | 08:31 | 03:01 | 0 min |
| `18_dB-02` | what places a page's first baseline, and is median_p | 08:31 | 03:01 | 0 min |

## Timing

| | |
|:--|:--|
| Slot window | 08:16 → running · 16 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **3.5 min** — from 08:16:26, after `gaps.py: reading the timeline` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **3 min** | `#####` |
| screen - the class's own documents | **0 min** | `#` |
| record - attempt, handoff, class rows | **1 min** | `##` |
| report - the report and the chain | **4 min** | `######` |
| other - not attributed to a tool | **5 min** | `########` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

Before building anything for 18_displacement, read which clause of the check fired: verify_google.py --json on one of 22_invoice_four_columns_txtpos / 41_coloured_headings_white_bg / 73_marksheet_subject_marks_grade / 16_right_aligned_amounts_txtpos / 29_dot_leaders_txtpos / 72_bank_statement_no_rules_right_amounts. All six have max_pt 1.44-2.40 and share5 0.00, under the check's 1.5 pt tolerance floor, so they can only be failing through 'if not ds' - upright text with no matched run - which is run matching or reading order, not vertical position. That test needs no build and decides whether the class is real. Do not rebuild the table-top spacer and do not believe the -114.8 pt figure: both refuted in SETTLED.md (68_journal max_pt is 8.64, and the w:before build moved 1 of 16 by 0.85). Do not read median_pt 0.96 as an offset either - it is the floor of the instrument (p2w.py filters the integer EDT to d>1). 71_invoice_space_aligned_no_rules (share@5 26.88, median_pt 3.84, no spacer) is genuinely displaced and a separate question. Also settled: screen.py was measuring NOTHING on a fresh pod (ENGINE_SRC frozen at import) - fixed; a screen reporting '0 of N measured' is a tool failure, not evidence.

> **1 item(s) parked** — each carries what was tried and what would re-open it; see the top of `HANDOFF.md`.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
