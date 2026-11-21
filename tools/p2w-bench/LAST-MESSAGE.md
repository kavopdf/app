**22 Nov 2026 · fixer slot 01:00 -> running IST · 47 min**

> **The corpus pass finished and the tool deleted it.** 213 docx converted and 212 measured in 35
> minutes; one command later `_invalidate_if_engine_changed` ran `rm -rf` over all of it, because
> `ENGINE-STAMP` said `unknown` and the guard reads that as a *different* engine. That is why the
> `32_stroke_lines` carrier fix has ended in a lead four slots running — not the construct, not the
> 25 minutes, but the finish line. The guard is now fixed and measured. **The next slot that runs
> the pass keeps the pass.**

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 19:42 | **measured** | 0 | The carrier patch applies clean on HEAD and `rule-carrier-followed-by-block-2008.patch` **is a superset** of `rule-carrier-per-rule-2008.patch` — same hunk headers, same target blob `4ead19d..5405e26`. The 00:15 handoff's "apply both" fails on the second. One patch, not two. |
| 19:56 | **measured** | 0 | Conversion: 213 of 213 docx in 4 slices at 3.68 / 3.54 / 4.70 / 4.47 s per document. `--budget` split diagnosed by the subagent (conversion eats the whole budget) is real but is not what stopped the last slot. |
| 20:17 | **measured** | 0 | Measurement: 212 of 212, `PASS COMPLETE`. `rank()` returned 212 rows. The pass was done. |
| 20:16 | **refuted** | 0 | `gate.py` then wiped it: `engine changed unknown -> 462353f - discarding docx and measurements built on unknown`. `dist2` 212 → 0, `out` 213 → 0, between two commands. |
| 20:17 | **fix, measured** | 0 | Guard narrowed to `was != "unknown" and now != "unknown"`. Probe: stamp `unknown` + 2 dist2 files → **2 survive** (before: 0). Stamp `deadbee` + 2 files → **0 survive**. A real engine change still wipes. |

## The class I chose, and why

`32_stroke_lines`, and not because `classpick.py` printed it. It is the only class in the repository
where construct, code and failure signature are all written down, and this slot was the first with
evidence that the *pass itself* was the blocker rather than the construct. Four slots have now
carried this patch to a complete measurement; none has kept it. The arithmetic is unchanged: the
carrier is the largest class left, `w:drawing` is on 197 of 213 documents, and two documents are
already proven 40/42 → 42/42 through Google.

What this slot adds is that the reason was never the code.

## Why it is a lead and not landed

The measurement was destroyed at 20:16 and there was no second 35 minutes. The engine is reverted to
HEAD; the patch is unchanged in `patches/` and the tree is clean. `regress.py --check` passes —
nothing worse in the `.txt`, the table matches the engine.

The guard fix is committed because it is a *tool* change with a before-and-after measurement, and
because leaving it out guarantees the next slot repeats this exact loss.

## Falsification

The prediction was written before each test.

| test | expected | measured |
|:--|:--|:--|
| patch applies to HEAD | clean, or a rejected hunk | **clean**; superset of the carrier patch confirmed by hunk header |
| conversion rate | ~3.7 s/doc (repo-recorded) | **3.54–4.70 s/doc** across 4 slices |
| measurement completes | 212 of 212 in ~15 min | **212 of 212**, `PASS COMPLETE` |
| stamp `unknown` + populated `dist2` | files deleted (that is the bug) | **0 of 2 survive** |
| same, after the guard | 2 of 2 survive | **2 of 2 survive** |
| stamp `deadbee` (a real change), after the guard | still wiped | **0 of 2 survive** |

The direction that could have refuted the fix — that narrowing the guard also disarms it — was
tested directly and did not: a genuine engine change still discards the cache.

## Subagents

Two, deployed inside the first ten minutes.

**`gate-runtime`** read the whole build → convert → render → measure → rank chain and found the two
things that made this slot possible: that `--budget` is consumed entirely by conversion on an
unconverted corpus (which is the previous slot's `39 of 213 docx, 0 measured` symptom exactly), and
that `_invalidate_if_engine_changed` keys on a commit hash and so is blind to an uncommitted patch.
Its recommendation to use batched `ConvertAll` for the pass is **wrong and I did not take it** —
`ConvertAll` carries state between documents (392 scored share5 1.61 alone against 28.39 in a full
batch). It is sound only as a differential of two engines over one batch.

**`falsify-32`** went to the `gverify` JSON rather than the prose and found that the denominators are
not 42 everywhere — 43 documents are scored out of 47 and 2 out of 44, and 21 carry
`page_count_refused` with no check list at all. Any sentence of the form "42/42" is only meaningful
for the 42-scored set. It also showed `394_map_with_legend` at **41/42 in Google**, not the 42/42 the
00:15 handoff quotes — that figure was a LibreOffice number used as a Google prediction.

## Next run

1. `git apply tools/p2w-bench/patches/rule-carrier-followed-by-block-2008.patch` — this one only.
2. `bash tools/p2w-bench/build-engine.sh`
3. Drive the pass with a script that validates once, then loops `docx(deadline)` and `run(deadline)`
   — not `p2w.py main()`, which pays a 50 s engine rebuild and a 5 s re-validation on **every**
   invocation (7 minutes of a 35-minute pass). 4 slices to convert, 5 to measure.
4. `rank()`, then `regress.py --check`, `regress.py --stamp`, commit. **Do not run `gate.py` between
   `rank()` and `--stamp`** until this fix is on `main` and the stamped tree is the tree
   `P2W_ENGINE_SRC` names.
5. Re-measure the sixteen `{05, 32}` documents through Google. Predicted 42/42; two are already
   proven.

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
| Working on | `32_stroke_lines` — the carrier, held open by the pass, not by the code |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 01:00 → running · 48 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 15 |
| Longest silence | **13.3 min** — from 01:12:41, after `corpus pass: converting (driver skips per-call rebuild)` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **3 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **41 min** | `###################` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **0 min** | `#` |
| other - not attributed to a tool | **1 min** | `#` |
