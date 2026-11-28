# P2W Fixer - Run Report

**28 Nov 2026 · slot 11:59 → running IST · 10 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **8480** of 9011 (94.1%) on 213 documents |
| Check-instances still failing | **531** |
| Kept attempts vs documents clean | **17** classes with a kept attempt, **56** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - .txt age: measured 6.7 h ago vs nothing re-measures it on a schedule; subagents: 1 deployed vs no FINDINGS filename carries 18dA18_displacem - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
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
| Working on | `-` - taken from the pending list (63 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

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

## Two measurements this run leaves behind

**1. A `DONE` from `corpus-slice.py` is not a fact about the files, and here it was wrong by 42.**
After the engine rebuild, `corpus-slice.py` printed `DONE - 214 documents converted, stamp written for
engine a05b20eb05fe0fc8` — and 42 of the 214 `.docx`/`.txt` pairs in the cache were still older than
the build, `305` among them, still failing `t08` 32/33. The same document converted by `ConvertOne` from
the same engine, in the same minute, passed. The 42 were rebuilt by hand (6 workers, 42 converted, 0
failed), and only then did the corpus agree with the single-document probe. The 11:00 slot's report
names the cause: the cache is keyed on a fingerprint that excludes `TxtWriter.java`, so a `.txt` fix is
invisible to the slicer. **This run's contribution is the count: 42 of 214, and a stamp that claimed
214.** A run that trusts `DONE` stamps a corpus it did not build.

**2. `600_reviewed_invoice_with_annotations` fails `t12_word_invention` on PDF annotation text.** Its
`.txt` opens with three lines the page never draws — `Rate for HSN 8536 confirmed with PO.`, `Checked
against PO 4471. Quantity on line 3 raised from 20 to 25.`, `Approved` — because they are annotation
`/Contents`, not page content (`pymupdf`'s `get_text()` does not see them; the writer does). A census
over all 214 corpus PDFs: **exactly 1 document carries annotation text, and it is this one, and it is
the one that fails.** The blast radius of dropping it is therefore one document, and it is the document
that becomes clean. **Not landed:** `pdfbox-android` 2.0.27's `PDFTextStripper` exposes no
`processAnnotation` hook (`javap` shows `processPages`, `processPage`, `writePage`, `writePageStart`,
`writePageEnd` and nothing for annotations), so suppressing it is a real change to the collector, not a
one-line filter — and it was 72 minutes into the slot. Written up in
`FINDINGS/ANNOTATION-CONTENT-IS-NOT-PAGE-CONTENT-28NOV-relay.md`.

## The agent, and the class it refuted

**One agent, not two, and the number is 20.3 minutes.** An unattended run's sub-agent returns inline, and
the first one took 1215 s. A second would have cost another 20 of a 90-minute slot, and the slot was
worth more spent landing a measured lead. The brief allows this with the number.

It went at `18_displacement`, the rotation's own class and the largest prize in the leverage table
(47.1 clean documents), and it **refuted the mechanism the brief records**:

* `shift = 0.961 × gap − 0.58` is a *loss* fit taken at an older engine. Inverted, it asks for more loss.
* `w:line` exact delivers **0.223** of the gap, not 0.961 (`403_crossword_puzzle`, 4 Google renders,
  max residual 0.21 pt).
* `w:before` is 1:1 on page 0 and **0.000** on pages 1-4 (`412_page_labels_roman`): Google drops it
  after a page break, which is what the brief said, and no engine arithmetic can put it back.
* The residue is per-line drift, not a gap: `p403-claimfix` moves `med_dy` −7.7 → −7.5, verdict
  **41/42, fails**.

**Documents that become clean from a gap transform: 0.** A patch exists and is off by default
(`DocxWriter.googleGapTw`, flag `-Dp2w.googlegap=1`, `document.xml` byte-identical with the flag off);
it is not in the tree because its own measurement says it cleans nothing.

## The txt

| | |
|:--|:--|
| Measured | **6.7 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
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
| Slot window | 11:59 → running · 10 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 3 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |
