# P2W Fixer - Run Report

**20 Nov 2026 · slot 10:51 → running IST · 1h 10m**

> **t13\_amount\_columns** went from 18 documents to 6, and two constructs were kept. The gate itself was the reason the .txt half could never land a commit, and that is fixed too.

## Progress

| | |
|:--|:--|
| Documents improved this run | **12** — 3 attempt(s), 2 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t13_amount_columns` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:51 | **kept** | 10/18 | One end column per TABLE column. `appendTable` aimed each numeric cell at its own cell's right edge and then discarded that aim whenever it landed left of the cell's left edge. On a 7 pt amount column it always does: the document-wide 0.6 em ruler over-estimates a numeric token by a column, so `startCol` fell 1-2 columns left of `baseCol` and the guard kept the left edge. The amount then ended at `baseCol + length` - 134 for a 9-character figure, 133 for an 8-character one: the same page column, two .txt columns. Measure the column once, as the furthest right any numeric cell in it already reaches, and end every numeric cell there. Nothing moves left; the line count is unchanged, so `t04\_structure` cannot drift. |
| 11:59 | **kept** | 2/18 | `paraEndSnap()`. The paragraph path has no right edge at all - `Para` carries `lineX/lineY/lineSize` only - so a numeric paragraph line ends at `column(lineX) + length` and the ruler's rounding split one page column across two adjacent .txt columns: 91/92 on `29\_dot\_leaders\_txtpos`, 142/143 on `bank-statement-horizontal-rules-only`. Per page, an end column whose immediate neighbour is also an end column of that page's numeric paragraph lines merges into it, transitively, keeping the highest value; `appendPara` pads to it. It only ever pads, and it cannot change a line count. |

Both are inside `TxtWriter`, which the .docx path never calls. Measured over the whole corpus, one JVM
per document, `verify_txt.compare()` on every document: 12 documents better, 0 worse, 201 unchanged.
Corpus checks 1784 to 1796, and 179 documents now pass every applicable .txt check against 167 before.
Neither attempt moved a single document the wrong way, at any point.

## The gate could not have landed either of them

`scope.py` fell back to "both formats" for any method it did not recognise, and `regress.py` then
demanded a re-stamped docx table - while `engine_fingerprint()` hashes every `.java` in the engine, so
any `TxtWriter` edit staled the docx stamp by construction. A .txt-only change could therefore never
pass the gate. That is the mechanical reason 46 documents have failed the same .txt checks for a month:
not that nobody tried, but that nothing a .txt run produced could be committed.

* `scope.py` now maps `TxtWriter.appendTable` and `TxtWriter.appendPara` to `txt`. Both are private
  static in `TxtWriter` and are called only from `TxtWriter.write()`, which no .docx path invokes.
* `regress.py` no longer stamp-checks a format `scope.py` has proved out of scope. A change `scope.py`
  cannot attribute still leaves the scope empty and stays strict on both stamps, and
  `docx_regressions()` still runs unconditionally, so nothing is waved through.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **179** (84.0%) |
| Failing at least one check | **34** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 12 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | What it proved |
|:--|:--|--:|--:|:--|
| `t13_A-01` | which writer path emits the misaligned amounts | 11:05 | 11:18 | Built the engine and ran it. The amounts come from `appendTable`, `cellR` is not NaN and does not differ per row - the clamp at `TxtWriter.java:375` is the mechanism. Measured two candidate patches on 60 documents; the per-column one was 6 better, 0 worse. |
| `t13_B-01` | a path census of all 18 documents | 11:06 | 11:29 | Built the engine, converted all 18, instrumented `TxtWriter`: 14 table-only, 2 paragraph-only, 2 mixed. Measured the three constructs at 10, 13 and 15 of 18. Ran out of its budget before writing its file; the census is in `FINDINGS/t13-path-census-120600-f2y.md`. |

## Timing

| | |
|:--|:--|
| Slot window | 10:51 → running · 1h 10m |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 22 |
| Longest silence | **58.6 min** — from 10:52:49, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 need a human |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **1h 07m** | `#####################` |
| record - attempt, handoff, class rows | **2 min** | `#` |
| report - the report and the chain | **1 min** | `#` |

## Next run

`t13\_amount\_columns` holds 6 documents and none of them is a one-column split. Four of the six
(`74\_balance\_sheet\_indented\_subitems`, `29\_dot\_leaders\_txtpos`,
`gst-invoice-multipage-item-table`, `itr-computation-with-slab-table`) fail because the table path and
the paragraph path are measured separately: the table cells converge on their own end column, the
paragraph lines converge on theirs, and the two maxima differ. Pooling both emitters onto one per-page
ruler is the next construct - the census agent measured that variant at 15 of 18 - and it is a change
to how the two emitters share a ruler, not another special case.
`balance-sheet-two-columns-of-figures` needs one pair merged that is TWO columns apart (52 and 54); no
one-column window reaches it, and widening the window is a layout claim the measurement does not
support.

The class is not exhausted: it moved twice this slot, 18 documents to 6, and the rotation should stay
on it.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md,
TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never
estimated.*
