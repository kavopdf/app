# Fixer report - 2026-11-28 11:59

```
# P2W Fixer - Run Report

**28 Nov 2026 · slot 11:59 → 12:15 IST · 16 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **3 disagreement(s)** - kept change: 2 code commit(s) in this window, first: blockers: the drive upload path needs an s3key,  vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; .txt age: measured 6.8 h ago vs nothing re-measures it on a schedule; subagents: 1 deployed vs no FINDINGS filename carries 18dA18_displacem - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
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
| Working on | `-` - taken from the pending list (64 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> **I landed a change that was already landed, found out at the rebase, and threw my copy away rather
> than double-count it.** The `TxtWriter` hoist fix (`305_vaccination_certificate`, `t08` 33/32 →
> 33/33) was built, measured and named as a next step by the 09:16 slot; I re-derived it from that
> finding, rebuilt the engine, rebuilt the whole 214-document corpus and re-scored it, and got exactly
> the number that finding predicted: **1 newly clean, 0 newly failing, 213 unchanged**, `.txt` clean
> **208 → 209 of 214**. Then `git push` was refused, and the rebase showed the 11:00 slot had already
> committed the same two hunks and the same 209. My commits were discarded (`git reset --hard
> origin/main`) so the ledger does not carry the same document twice. **What this run adds is a
> reproduction, not a fix** — and the cost of the duplicate is the finding below.
>
> **Why the duplicate was possible, measured.** At 11:19 my clone was at `de7d5acf` and `git pull`
> said `Already up to date`; the 11:00 slot pushed its landing at 11:19-11:25, after my clone. Nothing
> in the brief or in `LAST-MESSAGE.md` told a run that a *different* slot's commit was in flight, and
> the claim I took at 11:25 was on a tree that did not have it. A run that claims a slot should
> `git fetch` **after** the claim, not before — the claim is the moment the lock is taken, and the tree
> it protects is the one at that moment.

## The txt

| | |
|:--|:--|
| Measured | **6.8 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
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
| Slot window | 11:59 → 12:15 · 16 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 8 |
| Longest silence | **6.0 min** — from 12:09:51, after `lastmessage.py: running report.py for the numbers` |
| Silences over 2 min | 1 |
| Obstacles | 1 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | cannot reach drive for a NEW engine output: the upload call needs an s3key the sandbox cannot mint, so GOOGLED |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **6 min** | `######################` |
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

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
