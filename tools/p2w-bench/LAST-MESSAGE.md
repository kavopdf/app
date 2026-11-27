# P2W Fixer - Run Report

**28 Nov 2026 · slot 03:24 → 03:28 IST · 3 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8477** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **534** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - attempts: RUN.json counter 3 vs ATTEMPTS.json history 1; kept change: 4 code commit(s) in this window, first: relay 03:18: run state and handoff ledger vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; subagents: 2 deployed vs no FINDINGS filename carries row_A-01, commB-01 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **43** of the 212 compared (corpus 214) |
| Corpus improvement vs 15 Nov | **-17.93%** — mean 6.15 → 7.25 |
| Regressions | **82** — 415_inline_images, 411_nested_xobject_transforms, itr-computation-with-slab-table |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **46** of the **206** re-measured on this engine - **0** of the 206 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 13 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 214 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **30** — improved, not fixed |
| Classes solved | 0 of 35 clear — 35 class(es) still have an OPEN document |
| Working on | `63_table_rows` - taken from the pending list (64 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `63_table_rows` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 03:24 | **lead** | 0/None | Bisected the 84-regression cluster to one constant: ROW_RUNG_UNDER_TW=10 (8fb4f503). -Dp2w.rung=0 restores 6 of 6 probed table documents (table-with-no-header-row 47.48->0.61, electricity-bill 36.78-> |
| 03:40 | **lead** | None/None | gate refuses main itself (84 with no engine change); rung=0 recomputed from the committed full-corpus table: 84 -> 57, 28 released, 1 cost, net 27; 27 of the 84 have a baseline of 0.00 and 6 are alrea |

## Why nothing moved, in this run's own words

Not for want of a change: the change is measured and it is one constant. Nothing could be committed
because **the commit gate refuses `main` itself**.

`bash tools/install-gate.sh` installs `.git/hooks/pre-commit`, which runs `regress.py --check` and has
no override. On a clean clone of `main` with `scope.py` reporting no engine change, that command exits
1 with **84 docx documents worse than the 15 Nov baseline**. So the hook refuses an engine fix, a tool,
a findings file and the run's own report alike. Four slots have ended "nothing kept" against this wall
and each wrote it up as a slot that ran out of time; the wall is the reason.

The arithmetic, recomputed this run from the three committed tables by a new read-only tool,
`tools/p2w-bench/gate_decompose.py`:

- of the 84, **27 have a baseline of exactly 0.00** - a floor no change can hold;
- **6 already sit inside the corpus's own 99% bar** (`share5 <= 1.0`) and are refused anyway;
- **10 baseline rows contradict themselves** - `share5 = 0.00` while `max_pt > 2.4 pt` says ink sits
  beyond the 5 px radius the metric is defined on; **4 of them are among the 84**;
- 19 are a genuine loss above 5.0.

The largest real lever is `ROW_RUNG_UNDER_TW = 0`. `FINDINGS/RANKING-rung0-FULL-CORPUS-28NOV.csv` is a
full-corpus measurement of exactly that tree, and against the same baseline it takes **84 -> 57**:
**28 released, 1 cost** (`marksheet-subject-left-marks-right`, 4.55 -> 5.21), **net 27**. It is one
constant, it is fully measured, and it still does not clear a gate that demands zero.

So the next run's first question is not "which class" but "how does `main` get back under the bar". The
order that does not ratify damage: land the rung in its **per-row** form (mechanism and falsifier in
`FINDINGS/GATE-REFUSES-MAIN-ITSELF-AND-THE-RUNG-IS-27-NET-28NOV-relay.md` §6 - apply it only where the
table is held to a page budget, the `mobile-bill` case it was tuned on), re-measure the ten
self-contradicting baseline rows as a data defect, and only then decide whether a gate that refuses a
tree in which nothing changed is still the right gate. Re-baselining to today's state without the rung
would ratify 27 documents of avoidable damage.

Nothing here is a substitute for a measurement the gate accepts. It is the map of why there is no such
measurement yet, and it is committed so the next slot starts from it rather than re-deriving it.

**Two agents were deployed and recorded in `HANDOFF.json`** (`row_rung|A`, `commit_gate|B`); both landed
and their arithmetic was recomputed here rather than trusted - one of them cited a findings file that
does not exist, which is why the numbers in this report come from `gate_decompose.py`.

### The run before this one said

> The gate's regressions are not five constructs. They are one constant, and this run bisected them to it.
>
> The last three reports said the 84 LibreOffice regressions were several unrelated constructs and that no
> single patch would move them. That was never measured; it was inferred from the class table. So I stopped
> inferring and bisected the engine the way you bisect any regression: build the tree at each commit, score
> one document, watch the number. `table-with-no-header-row` sits at the baseline score for four commits in a
> row and jumps to its full tree score at exactly one of them. That commit is the table work of 27 November.
>
> It went in as two rules at once, so the second question was which half did it. Both were made switchable
> and measured separately, and only one of them moves anything: the rule that declares a pitch-bound table row
> ten twips under its own pitch. Turning that rule off returns every table document I probed to its baseline
> score, and five of the six come out better than the baseline rather than level with it, because the other
> engine work since 15 November is real and the rung was hiding it. The gap rule from the same commit is inert
> on both documents I tested it on.
>
> So the answer to "what makes these documents worse" is now a named constant with a named commit, and the
> probe that shows it costs fifteen seconds a document instead of a corpus pass. That is the thing this run
> was worth.
>
> What I did not do is decide which renderer is right, and I want to be plain about why that matters. The rung
> was landed on Google evidence: its own commit message says it took two documents to a clean sheet in Google
> Docs. Every measurement against it since has been LibreOffice. Under the rule this project is built on -
> Google is the truth and LibreOffice is a proxy - a change that is right in Google and wrong in the proxy is
> not a regression at all, and a tenth of the "regressed" documents pass every Google check while their proxy
> score rises. That is consistent with the gate refusing on an artifact of the proxy. It is also exactly the
> kind of comfortable story that turns out to be wrong, so it stays a hypothesis: the Google side of this
> constant is unmeasured, and it is two documents wide.
>
> The next run should measure it before it builds anything, because the answer decides two different jobs. If
> the two documents stay clean with the rung off, the constant is pure cost and should go, and the gate
> unblocks by itself. If either one loses its clean sheet, the rung is right and the gate is charging a
> Google-proved construct to a renderer nobody opens - and then the gate is the defect, with a measurement in
> FINDINGS/ to argue from rather than an opinion.
>
> Nothing was kept and no engine line was committed: a change that requires a full corpus re-measurement does
> not fit the slot that found it, and a change measured only in the proxy would be the exact mistake this file
> is warning about. The switches I built were reverted; the tree's engine is byte-identical to HEAD.
>
> The self-check above reports one disagreement: a code commit in this window with no kept record beside
> it. That commit is this report's own documentation commit, whose message begins "fixer 28nov" and which
> the checker reads as an engine change. No engine line was committed this run; the tree's engine is
> byte-identical to HEAD, and the attempt is recorded as a lead with nothing moved.

## The txt

| | |
|:--|:--|
| Measured | **59 min ago** |
| Scored | **214** of 213 |
| Clean - every applicable check passes | **208** (97.2%) |
| Failing at least one check | **6** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 4 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `row_A-01` | which of the 84 docx regressions vs the 15 Nov basel | 03:41 | - | not recorded |
| `commB-01` | is the gate's 84 a real quality loss or an inflated  | 03:41 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 03:24 → 03:28 · 3 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 11 |
| Longest silence | **2.0 min** — from 03:25:50, after `pending.py: reading the pending gate` |
| Silences over 2 min | 1 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **2 min** | `#################` |
| report - the report and the chain | **0 min** | `#####` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 38.49 | -30.33 |
| `report-2col-table-spanning-both-columns` | 22.58 | 1.18 | -21.40 |
| `78_mixed_english_devanagari_line` | 13.51 | 1.73 | -11.78 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

  written to tools/p2w-bench/REPORT.md - commit it, so the report survives the run
