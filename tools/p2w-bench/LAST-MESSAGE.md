**22 Nov 2026 · relay slot 01:16 → running IST · 27 min**

> The carrier fix handed over at 01:02 is **right on 2 documents and destroys 59**. Measured, not
> argued: built the engine with the patch, rebuilt all 213 `.docx`, read the XML back. The patch
> turns **4595** shapes into floating carriers across **183** documents - and **3608 of those are
> 8-twip vertical table-cell separators**, not rules. `375_attendance_register` goes from 1 table
> and 13 rows to **443 tables and 455 rows**. A one-line guard - a rule is horizontal - restores
> `324`, `341` and `375` to **byte-identical with HEAD** while keeping `17`'s 2 carriers and
> `bank-statement`'s 39. Patch saved; the remaining 987 carriers are unmeasured in Google.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 01:43 | **lead** | 0 | The carrier patch, corpus-wide. 4595 carriers in 183 of 213 documents; `375` 1 table/13 rows/456 drawings → **443 tables/455 rows/14 drawings**, `341` 1/25/301 → **276/300/26**, `324` 6/246/1483 → **1236/1476/253**. Character counts unchanged in all three, so no existing check sees it. |

## The class I chose, and why

I did not choose a class - I finished the one the previous slot was one build away from. It left
`17` and `53` at 42/42 in Google with one empty block after each carrier, and it left the reason
it did not land: the full-corpus re-measurement. That measurement is the only thing standing
between 18 documents and clean, so it was the slot.

It cost the slot, and it bought the answer: the construct as patched cannot land, and now we know
exactly why and exactly how much it needs narrowing.

## The cause, in one line

```java
float lo = Math.min(s.wPt, s.hPt), hi = Math.max(s.wPt, s.hPt);
return lo <= RULE_MAX_PT && hi > 2f && hi >= lo * 4f;
```

Symmetric. A cell's **vertical** separator is 0.4 pt wide and a row tall: one side under 4 pt, the
other more than four times longer. It passes. `ruleCarrier` writes it as a floating 1x1 table
8 twips wide. Read out of the carriers the patch actually wrote: real rules are **9666** twips
(`17`) and **10091** (`bank-statement`); every destructive one is **8**.

Corpus split: **987 horizontal carriers in 160 documents, 3608 vertical in 59, 23 documents that
are verticals-only and are now left alone.**

## Falsification

Prediction written to `/scratch/work/PREDICTION.txt` **before** the guarded build:
*"324/341/375 become byte-identical to HEAD; 17 keeps 2; bank-statement keeps 39. If any of the
three still differs, the vertical diagnosis is wrong."*

| test | expected | measured |
|:--|:--|:--|
| `324` guarded vs HEAD | identical | **identical** |
| `341` guarded vs HEAD | identical | **identical** |
| `375` guarded vs HEAD | identical | **identical** |
| `17` guarded carriers | 2 | **2** |
| `bank-statement` guarded carriers | 39 | **39** |

Read with `zipfile` + `re` on `word/document.xml`, not with the tool I edited.

## What I did not land, and why

`regress.py --check` passes on the reverted tree (`PASS - nothing got worse in the .txt only, and
the table matches this engine`). The engine is at HEAD. The change ships as
`patches/rule-carrier-horizontal-only-2008.patch`, 211 lines, applies clean to the pristine tree,
and **supersedes** `rule-carrier-followed-by-block-2008.patch`.

It is not landed because a 160-document construct change needs the full corpus measured, and that
is 85 minutes of `soffice`, not the 25 the last handoff guessed: **11 documents per 280-second
budget**, 213 documents, 18 passes. That number is the real blocker on this class and on every
class behind it, and it is worth a slot of its own.

## Two things the next run needs

1. `patches/rule-carrier-per-rule-2008.patch` and `patches/rule-carrier-tblppr-2008.patch` are
   **byte-identical** (md5 `8473b14274c0aa827432895733cbba7f`), and both conflict with
   `followed-by-block-2008` on the same hunk. LAST-MESSAGE.md's "apply `per-rule` then
   `followed-by-block`" fails `git apply`. Only one of the three can ever land.
2. The 987 horizontal carriers still need a Google export on a document where the rule is a
   **table's own row border** rather than a standalone line. The guard removes the destruction; it
   does not yet show a horizontal carrier is harmless there.

## Subagents

One, at 01:47, in the first ten minutes.

**`Patch scope analysis`** read the three patches and the writer source and returned the facts this
slot was built on: the patch touches only `DocxWriter.shape()` behind a per-shape guard, documents
with no rule shape are byte-identical, the following block is a **1-twip exact line** rather than a
full line, and the three patches conflict. The last two changed the plan - I applied one patch
instead of two, and I went looking for over-fire instead of assuming a zero-flow block was safe.

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
| Slot window | 01:16 → running · 27 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 13 |
| Longest silence | **10.6 min** — from 01:18:37, after `relay: patch scope read - followed-by-block is a superset, applying th` |
| Silences over 2 min | 4 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **1 min** | `##` |
| measure or build - a conversion, screen or compile writes no beacon | **22 min** | `##################` |
| report - the report and the chain | **2 min** | `##` |
