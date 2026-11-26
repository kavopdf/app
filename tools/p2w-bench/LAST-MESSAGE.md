# P2W Fixer - Run Report

**26 Nov 2026 · slot 08:27 → running IST · 1 min**

> Nothing was kept this run. Three things landed: two subagent findings and one measured lead.
> The lead moves 37 documents and is written up, not committed - the gate needs a full Google
> re-measure and the slot ran out before it.

## Progress

| Check-instances passing | **41** of 42 (97.6%) on 1 documents |
| Check-instances still failing | **1** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **47** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **0** of the **1** re-measured on this engine - **207** of the 208 scored are still on an older engine, and **42** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **4** run(s) for the 207 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **5** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - the highest-leverage open check at 54.4 clean documents |

**The Progress block above is the live table, and it is degenerate this run.** A concurrent
gverify pass had re-measured 1 document when the table was built, so "41 of 42 on 1 documents" is
a sample of one, not the corpus. The corpus numbers that did not move are the ones to read:
**47 documents clean**, **205 of 213 clean in the .txt**, **no regressions**.

## The class, and why this one

`classpick.py --leverage` refuses a new class until the pending list is empty, then weights six
checks 3x over the 34 that cannot finish a document. `18_displacement` is worth **54.4 clean
documents** - more than the next three combined - and 25 documents fail *only* it. It was the
choice, and the reason is that number.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 07:21 | **lead** | 0/None | pgMar-top regression root-caused as a DOUBLING on 401; two guards make 401+601 byte-identical (carried over from the previous slot's record) |
| 08:24 | **lead** | 1/25 | spacer->w:before clamp + ruled-only row excess; Google med_dy -13.0->+1.1 on 72_bank, still 41/42 (carried over) |
| 08:39 | **lead** | 0 | **this run's own attempt.** The refused table spacer declares its whole gap as `w:line` and Google delivers 22.9% of it. Patched, measured, written up, not committed. |

## This run's lead: the refused spacer delivers a fifth of what it declares

Two subagent findings, both committed, both needed to get here.

`18_displacement-CLAUSE-NOT-DS-074250-71ae.md` settles the clause question: for all **25** of the
25 documents that fail only `18_displacement`, the clause that fires is **over_tolerance**, and
the `not ds` branch fires on **0**. The class is vertical position; `SETTLED.md` §4c's
run-matching hypothesis is settled against.

`w-line-exact-GOOGLE-CHARGE-075617-f0cc.md` measures the law: Google charges an exact line box of
`L` twips on a faceless `sz=2` mark at **2.74663 × max(L/240, 0.06) pt**, not `L/20` - 17 points,
four faces, residual ≤ 0.0007 pt. The `2.5873` the engine quoted is that law with the wrong font
ratio in it.

Put together: the *refused* branch of the table-spacer emitter writes the whole gap as `w:line`,
so a 2880-twip spacer asks for 144.00 pt and Google draws **32.96** - every row under the table
sits 111.04 pt high. **62 documents, 141 instances.** The guard refuses because the page has no
room for the whole gap; it never charged for the 22.9% the construct was already spending.

The patch hands Google the room the page actually has, as `w:before`, floored at the old
construct's own charge - so a refused spacer can only move the table *towards* the source.

**Measured before/after over all 213 documents**, engine `981ff1fa35e2cf67` → `2c7141b7eeb9a0fe`:

| | |
|:--|--:|
| Documents carrying a refused spacer | 62 |
| Instances compared | 141 |
| Documents that gained gap | **37** |
| Documents unchanged | 24 |
| Documents that lost gap | 1 |
| Largest single-document gain | **+51.04 pt** (`374_org_chart`) |

The one loss, `itr-computation-with-slab-table` at **0.258 pt**, was a real bug in my first floor:
it omitted the law's `0.06` clause and under-stated the old charge for a spacer under 14.4 twips.
Corrected; re-checked arithmetically over the same 141 instances the worst case is **−0.0085 pt**,
which is twip rounding and 176× below the check's 1.5 pt floor.

**Why it is a lead and not a commit.** It moves 37 documents, so `regress.py --check` will not
skip - a `.docx` change that moves the corpus needs the full Google re-measurement. Two corpus
conversions and the two agents used the slot. Nothing is committed but the write-up; the two
hunks and the four-step resume are in the file.

## The txt

| | |
|:--|:--|
| Measured | **1.1 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

**Two deployed, two landed, both committed.**

| Agent | Class | Question | Landed |
|:--|:--|:--|:--|
| A | `18_displacement` | Which clause of the check fires on the 25 solo documents? | **over_tolerance, 25 of 25; `not ds` 0** |
| B | `18_displacement` | Google's exact charge for `w:lineRule="exact"`, and every emitter of it | **2.74663 × max(L/240, 0.06) pt; 12 emitter sites; 202 of 213 documents carry the construct** |

Both were deployed `background=true` in the first ten minutes and registered in `HANDOFF.json`
before this report claimed them. Both returned inline, which a scheduled run does - neither
blocked the run. Agent B's census is the part that predicts future work: `lineRule="exact"` is
emitted at **12 sites**, and three of them - the **post-table carrier** at −3.0845 pt per table
on 10 documents, **empty cell paragraphs** at +0.6824 pt on 46, and **text-box lines** at up to
+28.04 pt on 37 - have never been looked at.

## Timing

| | |
|:--|:--|
| Slot window | 08:27 → running · 1 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 12 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **1 min** | `######################` |

**The header reads 08:27 · 1 min and it is wrong about this run, in a way I can name.** The slot
was claimed at 07:11 and worked until 08:40. At 08:31, pushing after a concurrent gverify run had
already pushed, the rebase conflicted on `RUN.json`; I resolved it with a merge, which took the
remote's `RUN.json` and wiped the claim and the two attempt rows. Re-claiming with
`round.py --claim-fixer` then reset the window to 08:27 and 1 minute. So the live table shows a
one-minute run, 0 attempts and 12 beats. The real run was **89 minutes, 2 attempts, 21 beats**,
and `TIMELINE.jsonl` and `ATTEMPTS.json` in the merge still hold the beats and the lead.

The 21-minute silence is a corpus conversion slice and I did not beacon into it. That is the one
process failure of this run: `pod-prep.sh`'s conversion step beats once and then goes quiet for
four minutes at a time, four times over. A beacon belongs inside that loop.

## Next run

1. Apply the two hunks in `DocxWriter.java` around line 6121 - **refused branch only** - from
   `FINDINGS/18_displacement-REFUSED-SPACER-PARTIAL-SPEND-083900-a7c2.md`.
2. `pod-prep.sh` to conversion-complete, then the full `regress.py --check`.
3. Watch `374_org_chart`, `403_crossword_puzzle`, `23_timetable_grid_txtpos` first - they gain the
   most, so an over-spend shows there as content loss at the page foot.
4. Then take agent B's untouched sites in order of leverage: the post-table carrier (10 docs,
   −3.0845 pt each, a constant, never examined), then empty cell paragraphs (46 docs), then
   text-box lines (37 docs).
5. `18_displacement` will not clear on the spacer alone - 14 of the 25 solo documents carry no
   refused spacer at all. That tail is the next question, and agent A named the discriminating
   test for it: a per-paragraph `dy`, which needs one extra field in the same probe.
