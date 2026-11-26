# P2W Fixer - Run Report

**26 Nov 2026 · slot 08:27 → 09:23 IST · 55 min**

> No change was kept this run. Two things landed: the commit gate is unblocked, and the lead the
> last run handed me is closed as wrong. Both are committed and pushed.

## Progress

| Check-instances passing | **2530** of 2706 (93.5%) on 62 documents |
| Check-instances still failing | **176** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **47** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **14** of the **62** re-measured on this engine - **146** of the 208 scored are still on an older engine, and **28** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **3** run(s) for the 146 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **5** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - the rotation's own choice, and the class this run closed a lead inside |

## The class, and why this one

`18_displacement` is the largest open class and was already the rotation's pick. This run did not
choose a new class: the previous run left a measured lead with a four-step resume, and step 1 was an
engine patch. Checking that patch was the whole of the run's value, and the answer was no.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:27 | **lead** | 0/19 | refused-spacer lead closed: already committed in 9f0a8207; the requested hunk is +0.592pt Google / -1355.5pt LibreOffice over the 19 remaining documents, so it is a regression with no Google effect |

## The lead I was handed, and why it is closed

`FINDINGS/18_displacement-REFUSED-SPACER-PARTIAL-SPEND-083900-a7c2.md` asked the next run to apply
two hunks to the **refused** branch of the table-spacer emitter, and reported that as **62 documents,
141 instances, 37 documents gaining gap, largest +51.04 pt**.

Three measurements say do not apply it.

**The 37-document gain is already committed.** `git show 9f0a8207` - committed 02:54:47 UTC, fifteen
minutes *before* that finding was written - contains the spendable-branch change line for line
(`roomTw`, `spendTw = Math.min(wantTw, roomTw)`, `w:before="spendTw" w:line="spacerTw - spendTw"`).
The finding's `before` engine `981ff1fa35e2cf67` is the tree before that commit and its `after`
engine `2c7141b7eeb9a0fe` is the tree after it. It measured the right thing and credited the wrong
change.

**The population it asks you to patch has shrunk from 62 documents to 19.** Census on the corpus as
converted at HEAD (engine `a4d8fca469bba636`, 213 documents), reading the emitter's own shape out of
`word/document.xml`:

| shape | instances | documents |
|:--|--:|--:|
| spendable - `w:before="spendTw" w:line="1"` | 117 | 85 |
| refused - `w:before="0" w:line="spacerTw"` | 64 | 19 |

`9f0a8207` moved 43 of the 62 documents out of the refused branch.

**On those 19 the hunk is self-cancelling.** It sets `floorTw` to the old construct's own Google
charge converted back to twips and emits `before = floorTw - 3, line = 1`, so the Google charge is
`floorTw/20` to four decimals - which is exactly what Google already draws. Over all 64 remaining
instances:

| | now | with the hunk | delta |
|:--|--:|--:|--:|
| Google draws | 402.3 pt | 402.8 pt | **+0.592 pt over 19 documents** |
| LibreOffice / Word draw | 1757.5 pt | 401.9 pt | **−1355.5 pt** |

Largest single-instance Google change **0.0392 pt** - 38× below the check's own 1.5 pt tolerance, so
it cannot turn one failing document into a passing one. Largest single-instance LibreOffice loss
**111.0 pt**; `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` lose **511.0 pt**
each across 17 spacers. Word and LibreOffice honour `lineRule="exact"` at the full `L/20`; the patch
replaces a full-gap declaration with a 22.9 % one. That is non-negotiable 3 broken on 19 documents
for a Google effect below the floor.

Written up in `FINDINGS/18_displacement-REFUSED-BRANCH-IS-NOT-A-GAIN-26NOV-relay.md`.

## The gate was blocked, and unblocking it was the work

`regress.py --check` would not finish: `git commit` hung for over 180 s twice, and a direct
`regress.py --check` ran 4 m 21 s with 13 s of user time and produced nothing. The cause was not the
check - it was `corpus-slice.py` inside it, converting a corpus that was **115 documents short**.
`corpus-slice.py` finished the remaining 18 in 132 s, and the gate then ran in **25.8 s**:

    docx: no document worse than baseline
    txt : no document worse than baseline
    google-safe : no construct Google ignores has spread
    PASS - nothing got worse in both formats, and the table matches this engine.

Both commits this run passed that gate. The corpus is now converted at `a4d8fca469bba636`, all 213
documents, and the next run starts with a warm gate rather than a 20-minute conversion.

## The txt

| | |
|:--|:--|
| Measured | **2 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

**One deployed, one landed, committed and pushed.**

| Agent | Class | Question | Landed |
|:--|:--|:--|:--|
| A | `18_displacement` | What construct displaces the 14 solo documents that carry no refused spacer? | **yes** - `18-displacement-SOLO-TAIL-26NOV-onyx-node.md` |

Its answer changes what the class is. The 14 are **`w:trHeight w:hRule="atLeast"` re-laid by Google on
a 0.75 pt ladder**, and the branch is decided by whether the table is ruled:

    ruled   (w:insideH single):  laid = 0.75 * ( round(D/0.75) + 1 )     <- gains a whole rung
    unruled (w:insideH nil):     laid = 0.75 *   round(D/0.75)           <- snaps to nearest

Fitted on 13 measured `(declared, laid)` points: **10 exact, median residual 0.00 pt, rms 0.25 pt**.
Document-level: predicted row drift vs measured over 11 documents, **rms residual 2.10 pt, max 4.42
pt, sign correct on 10 of 11**; `320_balance_sheet_statutory` +18.50 predicted / **+17.00 measured**.
The branch rule is 10 for 10 with no counter-example - and it independently confirms the premise
`9f0a8207` committed (charge the 0.75 pt row excess only to ruled tables).

**The consequence for the next run:** `18_displacement`'s solo tail is not a spacer defect at all.
The fix is to declare a row height the ladder already lands on, and the refused-spacer patch moves
**none** of these 14.

**Only one agent was deployed, and the reason is a process failure.** I asked for two in the first ten
minutes. Agent A ran **inline, not in the background** - a scheduled run has nobody to answer later,
so `delegate_task` blocks - and it held the slot for **38.7 minutes**, which is the run's longest
silence and the reason a watchdog released the claim. Deploying a second agent would have blocked for
another twenty and left nothing for the engine work. One agent that lands a law beats two that
return after the slot is gone.

## Timing

| | |
|:--|:--|
| Slot window | 08:27 → 09:23 · 55 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 18 |
| Longest silence | **38.7 min** — from 08:35:19, after `heartbeat before any claim: gverify: converting corpus slices, then me` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **49 min** | `####################` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| other - not attributed to a tool | **3 min** | `##` |

The 38.7-minute silence is mine to own. `delegate_task` with `background=true` returned inline, and
I did not know it would until it did. A run that deploys a subagent must assume it blocks and beacon
first - or not deploy one.

## Where the run's value is

0 documents moved, and the honest reading of that is: this run found out that the last one was wrong
before spending a slot proving it. The refused-spacer lead would have cost a full corpus conversion,
a Google re-measure and 19 LibreOffice regressions to deliver +0.59 pt. It is now closed with the
arithmetic and the commit that already did the work, and the class's real mechanism - the 0.75 pt row
ladder - is named and measured for the first time.

## Next run

1. **Do not apply the refused-spacer hunks.** They are closed; read
   `FINDINGS/18_displacement-REFUSED-BRANCH-IS-NOT-A-GAIN-26NOV-relay.md` first.
2. Take the row ladder: `DocxWriter.java`'s `w:trHeight` emitter should declare a value the 0.75 pt
   ladder already lands on - `0.75 * round(D/0.75)` for an unruled table and
   `0.75 * (round(D/0.75) + 1)` for a ruled one, declared as the rung itself so Google's re-lay is
   the identity. Prove it on `320_balance_sheet_statutory` (+17.00 pt measured drift) and
   `16_right_aligned_amounts_txtpos` (−3.95 pt) before writing it for the class.
3. The corpus is converted and the gate is warm at `a4d8fca469bba636` - a conversion from here is
   only the slice the change actually moves.
4. `18_displacement`'s remaining tail after the ladder is the per-line `w:line` box on the 2 documents
   with no table at all, which agent A measured but did not fit a law to.
