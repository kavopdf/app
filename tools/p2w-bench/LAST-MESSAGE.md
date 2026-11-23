# P2W Fixer - Run Report

**24 Nov 2026 · slot 03:30 → running IST**

## Progress

| | |
|:--|:--|
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **27** of the **123** re-measured on this engine - **67** of the 190 scored are still on an older engine, and **30** were clean there |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 67 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **23** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 03:30 → running · 27 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 9 |
| Longest silence | **7.9 min** — from 03:30:35, after `retrying corpus pass with checkpointing` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **7 min** | `######` |
| report - the report and the chain | **10 min** | `########` |
| other - not attributed to a tool | **8 min** | `#######` |

## The class I picked, and why

`18_displacement`. Not because the tool printed it, and not because the last run picked it: because
`classpick.py --leverage` puts it at the top of the corpus at 34.7 clean documents, and because the last
run left a named, testable lead on it. I spent the slot testing that lead rather than inheriting it.

## What the last run's lead actually was

The previous run's FIRST MOVE was `trHeight = max(content, line-15)` on rows where `line > content`.
**It selects 0 rows across all 222 rows those 13 documents carry** and moves LibreOffice by +0.00 pt on all three
of `362_price_list_dense`, `mobile-bill` and `table-with-no-header-row`. It was a no-op, and its safety
argument ("LibreOffice lays max(trHeight, line) = line") is false on this emitter, where a single-line
cell carries a hairline `w:line` of 8–12 twips so LibreOffice lays the declared `trHeight`.

Its row half was also refuted by the document it was derived from: `362_price_list_dense` has all six
`tblBorders` at `w:val="nil"`, so it draws no rule and pays no row excess — **0.00 pt, not the 21.75 pt
the lead claimed** — and the record's own `worst_dy` on that document is 5.4, which no 21.75 pt
displacement can hide inside. The quantum is not flat either: `laid = 0.75*(round(declared/0.75)+1)`,
so 360 tw is +0.75 but 380 tw is +0.50.

The spacer half survives, on a four-point dose–response: 144.00 → 112.90 predicted against 114.28
measured, 16.70 → 13.09 against 12.85, 6.35 → 4.98 against 4.90. Within 1.9 % at three magnitudes
spanning 23×. It is unfixed for one reason only: the guard's room test.

## What I found instead, and left as a patch

**The spacer guard charges 0.75 pt per row for a rule an unruled table does not draw.** The row excess
is the rule's — this file already says so where the row height is written: *"An unruled table draws no
rule and keeps its full pitch."* The guard charges it to every row on the page anyway, so a table whose
six sides are all `w:val="nil"` is charged for a rule it does not have. Measured on this corpus:
`68_journal_wide_table_spanning` 7 rows, `72_bank_statement_no_rules_right_amounts` 18,
`bus-timetable-station-left-times-right` 33 — all three all-six-nil, all three refused a gap they had
the room for.

The patch charges the page's **ruled** rows only. Measured before and after on all 13 solo documents:
`document.xml` changed on **2 of 13**, every other member **0 of 13**, every `.txt` **0 of 13** — and the
two that changed moved the gap from `w:line` into `w:before` with the sum preserved to the twip
(366 → 365+1, 127 → 126+1). Both branches of the guard emit the same `w:before + w:line` total, so the
change **cannot move a LibreOffice or Word render of any document**; it can only change what Google
draws. It is worth 3.93 pt on `72_bank` and 1.37 pt on `bus-timetable` against displacements of 13.0 and
3.0 — so **neither document becomes clean. It is a lead, not a win**, and it is recorded as one.

It is a patch and not a commit because `regress.py --check` refuses an unmeasured engine and the corpus
pass does not fit in a slot. Numbers below.

## The bigger thing the second agent found, and it is not what the class was assumed to be

`00_page_count` is worth 23 clean documents and 23 documents are currently unscorable for it. Of those
23, **21 are one-page sources that Google lays on two**. I had the four usual components decomposed and
measured, and all four are zero: row heights **0.00 pt** over 391 `trHeight` rows (minimum clearance
+2.95 pt, the floor never binds); the spacer is **negative on six** documents (it buys Google room);
text wrapping under Google's substitute face **0.00 pt** — the substitute is narrower, not wider, and
removes wraps on three documents; paragraph spacing **0.00 by construction**.

What is left is **7,939 `wp:anchor` and 0 `wp:inline`**. LibreOffice charges an anchored shape nothing
in the flow; Google rasterises it and keeps a box. Median **0.57 pt per anchor**, range 0.10–0.96 — a
sub-point box, invisible in LibreOffice and fatal in Google. `351_omr_answer_sheet` spills at 0.10 pt
per anchor over 381 anchors; `390_wide_data_appendix` at 0.11 over 400.

The cheapest real unit is `332_bom_on_drawing`: **35 of its 58 anchors are redundant** — the table
already declares `insideV single sz=3` and the engine emits each of the 35 vertical row rules again as
its own floating anchor. Removing a rule the table's own borders already draw changes the visible table
in neither renderer. Written up in
`FINDINGS/PAGE-COUNT-IS-THE-ANCHORS-NOT-THE-ROWS-2200-fixer.md`.

## The obstacle, and it is the gate

Nothing engine-side could be committed this slot, and the reason is mechanical, not analytical:

| step | measured |
|:--|:--|
| corpus conversion on a fresh pod | 213 docx in 6 sandbox calls, ~14 min |
| corpus measurement | 24 documents per 245 s call |
| measurement still outstanding | 188 of 212 |
| calls to finish | 8 more, ~33 min |

`regress.py --check` on the changed tree: `ENGINE CHANGED (docx): table measured on 3e7f7c4475343a35,
the tree is 3e656727d8a12797`. It has no override. So **a 90-minute slot cannot host the pass that
would let it commit**, and the pass is not resumable across pods: `/scratch/work` does not survive, so
every run starts at `docx 0/213, measured 0/212`. The pass needs to be its own cron, or `p2w.py` needs
to checkpoint to something that survives a pod.

That is why this run is 6 sandbox calls of corpus pass and still 188 short: I started it at minute 40
because the class investigation came first. The pending list said to start the slot with it. It was
right.

## What the next run should do

1. **Apply `FINDINGS/18-guard-unruled-row-excess-2200.patch`** once a corpus table exists, and confirm
   the 2-of-13 `document.xml` diff reproduces.
2. **`332_bom_on_drawing` anchor de-duplication** — 35 redundant vertical rule anchors, Google-only,
   LibreOffice-identical. One build, one Drive round trip, and it fixes the per-shape constant for the
   whole `00_page_count` class.
3. **Do not** charge the spacer to the page-count class first: on `332`, `341`, `390`, `403` and the two
   bank forms it is currently worth −11.53 to −538.95 pt in Google's favour.
4. **The two bank forms are not the page-count class** — 9-page sources already 10 and 11 pages in
   LibreOffice, fault is an 842.1 pt picture on an 841.89 pt sheet. They belong with `18_displacement`.
5. **Do not trust `tools/p2w-bench/RANKING-TXT.csv`.** It holds 64 failing documents; the live table at
   `tools/p2w-bench/txt/RANKING-TXT.csv` holds 14. `report.py` reads the live one first and falls back
   to the stale one, so a missing live file silently republishes a wrong .txt number.

## Subagents

Two, both given a real problem with the document and the success condition named.

| Agent | Problem | Returned |
|:--|:--|:--|
| `18_displacement` mechanism | Which half explains each of the 13 solo documents, and is the last run's first move real | Per-document table for all 13; the first move is a no-op, selecting no row at all; the row half is refuted on its own document; the spacer half survives a 4-point dose–response |
| `00_page_count` overflow | Why 21 one-page documents lay on two, decomposed by construct | All four assumed components 0.00 pt; 7,939 anchors and 0 inline; median 0.57 pt per anchor; the redundant-anchor unit on `332_bom_on_drawing` |
