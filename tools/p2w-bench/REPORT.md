# Fixer report - 2026-11-26 18:57

```
# P2W Fixer - Run Report

**26 Nov 2026 · slot 18:57 → 19:45 IST · 47 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **5829** of 6153 (94.7%) on 142 documents |
| Check-instances still failing | **324** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **53** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **4 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1; kept change: 5 code commit(s) in this window, first: release fixer slot 26 Nov vs ATTEMPTS.json has no kept record in the window - the next run will read the class as parked and never find this change; .txt age: measured 8.7 h ago vs nothing re-measures it on a schedule |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+40.32%** — mean 6.15 → 3.67 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **142** re-measured on this engine - **65** of the 207 scored are still on an older engine, and **5** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **2** run(s) for the 65 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **6** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (54 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 19:42 | **lead** | 0/None | three arms of the table-gap spacer room guard measured first-hand in Google on 7 documents (42 renders). FULL clears 403_crossword_puzzle 41/42 -> 42/42 at med_dy -0.6 but drives worst_dy to 29-34 pt |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> The class was `18_displacement`, and the reason is a number, not a preference: `classpick.py --leverage`
> puts it first at **53.2 clean documents**, four times the next check. The picker refused a *new* class (51
> pending items), so the work came from the pending list — item 1 is the carry-over, and 18_displacement is
> where the carry-over points.
>
> An agent in the first ten minutes root-caused the construct and produced a patch: the room guard that decides
> how much of a table-gap spacer goes into `w:before` charges the unspent remainder at one twip per twip, while
> Google draws only 0.2156 of a twip carried by `w:line`. It predicted `403_crossword_puzzle` at `med_dy −2.2`
> and **42/42 CLEAN**.
>
> I measured it instead of believing it. Real Google Doc, real PDF export, `verify_google.compare()`:
> **−0.9 pt, still 41/42.** The median moved 10 points; the verdict did not, because the check fails on its
> tail clause (`n_out > max(2, 5% of runs)`), not on its median. That is the second time in two days a modelled
> "CLEAN" has been caught by measuring it.
>
> So the run stopped modelling and started sweeping. Three arms of the same guard — HEAD, HALF the refused
> remainder, FULL spend — built and rendered through the identical path on the same seven documents: **42
> Google renders, every number first-hand.**
>
> | arm | finishes a document? | cost |
> |---|---|---|
> | FULL | **yes — 403 at 42/42, med_dy −0.6** | worst_dy 29–34 pt on three bills |
> | HALF | no | worst_dy *reduced* on six of seven; two-tables worse by 1.1 pt |
>
> FULL is the only arm that completes a document and it is refused by non-negotiable 3: three documents end up
> 30 pt further from their original than they started. HALF is strictly better on six and marginally worse on
> one, and completes nothing — so it is a lead, not a fix, and the engine stays at HEAD.
>
> **What the sweep bought the next run** is the shape of the residue. With HALF the median lands at −0.1, −0.1,
> +0.8 on the three bills — dead on — and the check still fails, on the tail, at worst 7.5–8.9 pt. A spacer
> spend error is a constant offset. What is left is per-run variation. **The class's next mechanism is the tail,
> and it is a different defect from the one this run measured.** That is worth more than a patch that clears one
> document and wrecks three.
>
> The gate is refused, and it is the gate: `regress.py --check` reports `RANKING.csv` measured on docx engine
> `a4de7df896875a39` while this tree fingerprints `7e0de1abdeb221ae` — the 10:46 commit `aa496ebe` moved the
> page-top gap and the table has not been re-measured since. `docx: no document worse than baseline` passes; the
> refusal is "unmeasured engine", not a regression. The corpus build that would stamp it is pod-local and no
> later run inherits it, so it was not spent. The pre-commit hook is not installed for the same reason
> (`install-gate.sh` runs that build before it writes the hook), so the FINDINGS file landed unguarded — it adds
> documentation and no engine code, so no document can have moved.
>
>
> **The class was `44_header_footer`, and the reason is the picker's, not mine to invent.** `classpick.py` suggested it on one record: *"running foot is a row: flowRow anchors it past gapCapTw, Google drops the box text entirely. footBand change measured in | next run: the .txt half"*. It refused a new class outright — 35 pending items must be closed first — so the work had to come from the pending list, and this was the pending item with a stated next step. `classpick.py --leverage` still puts `18_displacement` first at 53.2 clean documents; the picker's refusal, not the leverage number, is what kept this run off it.
>
>
> The recorded finding ends by naming `flowFromBox` as the untouched second anchor site and calls it "worth more documents than this one". It is not a site at HEAD. `flowFromBox` has two oversized-gap anchors (the `afterTablePt` edge gap at DocxWriter.java:4625–4642 and the pitch gap at 4657–4678) and both already carry `!inFootBand(ctx, b.y)` through the helper at 420–425; it landed in `85b8735f` on 25 Nov, after the finding was written. The ablation is the proof:
>
> | build | 27 | 55 | 61 | 67 |
> |:--|:--|:--|:--|:--|
> | HEAD (four sites guarded) | txbx 0, anchor 0 | 0, 0 | 0, 0 | 0, 0 |
> | only the `flowFromBox` guards removed | 0, 0 | 0, 0 | 0, 0 | 0, 0 |
> | whole foot-band patch reverted | 4, 2 | 4, 2 | 4, 2 | 4, 2 |
>
> Row 2 is byte-identical to row 1 on those four and on a 12-document box-carrying sample, so the boxes come from `flowRow` — already guarded — and the "4 text boxes each" figure belongs to the writer before `85b8735f`. Compared at `word/document.xml`, because the `.docx` bytes are not deterministic: two runs of the same engine differ in bytes on 12/12 documents.
>
>
> The `.txt` half is nearly clean already. The live store `tools/p2w-bench/txt/RANKING-TXT.csv` (213 documents, engine stamp `a4d8fca469bba636`) has 8 documents failing anything, and both documents the footBand change fixed in Google — `27_two_column_left_short_txtpos` and `46_chart_coloured_labels_body_text` — read 9/9, 0 failed. There was nothing to carry over.
>
> `t09_page_furniture` is the only page-furniture check in the `.txt` set and it fails on exactly two documents, the same form twice. Re-measured live this run — both PDFs converted with `ConvertOne` on the engine compiled from HEAD (9 pages each), scored with `verify_txt.py`:
>
> | document | source (owed) | txt (present) |
> |:--|--:|--:|
> | `041122-Account_Opening_Form` | 29 | 125 |
> | `Account_Opening_Form_Fillable_filled` | 29 | 125 |
>
> Both returned `10/12 applicable, 7 passed, 2 abstained FAIL` with `t09 source=29 txt=125`, identical to the stored row, so the row is current. The owed keys are four — `Y` 12, `D` 8, `M` 6, `Date` 3 — and the first three are the date box of the form, which the page draws as eight separate one-glyph lines on one baseline. The `.txt` carries 247 single-character lines: the date box is the first eight, and the rest are letter-spaced words split into one-character lines that then match the same furniture keys, because `t09` restricts its *source* side to the top/bottom band and compares against a *whole-file* count on the `.txt` side.
>
>
> Whether the 125 is a `TxtWriter` line-assembly defect or a `t09` asymmetry is not decided, and the number alone cannot decide it. A crude band approximation — first and last six non-blank lines of each `.txt` page — returned 11 present against 29 owed, which is neither number, so it decides nothing; it is recorded so the next run does not repeat it. The census that would decide it is cheap and is written into the finding: for each of the 247 single-character lines, ask whether `_src_pages` says the page drew that glyph on its own line.
>
>
> The gate was run, and it is what refused — not the slot. `regress.py --check` exits REFUSED with `docx: no document worse than baseline` and `txt: not re-measured - the tree is the engine the table was measured on (a4d8fca469bba636)`, because `measure_gate.py` reports `RANKING.csv` measured on docx engine `a4de7df896875a39` while this pod's tree fingerprints `7e0de1abdeb221ae`: NOT READY. No document got worse; the engine has not been measured on this tree. The corpus build that would stamp it is pod-local — `pod-prep.sh` reported 165 of 213 documents still to convert, at 53 per 240-second slice — and no later run inherits it, so it was not spent. The pre-commit hook was not installed either, because `install-gate.sh` runs that same build before it writes the hook; the two FINDINGS files therefore landed in `b1a934f7` unguarded. They add documentation and no engine code, so no document can have moved, but the refusal is recorded in `BLOCKERS.md` rather than left implicit.
>
>
> 1. The single-character census on `041122-Account_Opening_Form`: 247 lines, each classified against the drawn line `_src_pages` says it came from. That decides writer versus instrument.
> 2. If the writer: fix `TxtWriter`'s line assembly and let `t04_structure` be the independent check that line counts elsewhere did not move.
> 3. If the check: restrict `t09`'s `txt_furniture` to the band the source side already uses, and re-measure the whole 213-document `.txt` table before and after, because the number moves on any document that draws a single letter.
> 4. `18_displacement` is still the largest single lever at 53.2 clean documents, and 35 pending items are what stand in front of it. Closing pending items is the way to it.
>
>
> **The page-top gap was carried by the one construct Google throws away.** Every page after the first took its whole top offset from `w:spacing w:before` on the first paragraph after a page break, and Google discards space-before at a page top. Moving that gap into the section's `w:pgMar w:top` took bank-statement-5-pages from 42/47 to 46/47 and gst-invoice-multipage-item-table from 42/47 to 45/47 in real Google renders. One attempt, kept, pushed as `aa496eb`.
>
>
> `classpick.py --leverage` puts `18_displacement` first at 51.9 clean documents, and 23 documents fail it alone - the largest single-check shape in the corpus. `classpick.py` refused a new class (32 pending items), so the class came from the pending list, which is what "Working on `-`" above records.
>
> The agents were pointed at the two halves the previous run had already separated: 17 page-scale, 38 block, 58 line. The previous run had refuted the table-row explanation, so the page-scale half was the unclaimed ground.
>
>
> `sectionTopTw`/`pageFirstBeforeTw` read the page-top term off the model; it goes into the section's `w:pgMar w:top`, and the page-first paragraph is written `w:before="0"`. `flowTw`, `budgetTw` and the emitters' accounting are untouched - only the bytes change. The committed `.docx` writes `w:pgMar w:top="1103"` (55.15 pt) on bank-statement-5-pages and `1023` on gst-invoice, with `w:before="0"` on the page-first paragraph - read out of the file, which is the independent check that the patch applied at all.
>
>
> | document | before | after | med_dy | worst_dy |
> |:--|:--|:--|:--|:--|
> | bank-statement-5-pages | 42/47 | **46/47** | -55.0 → **-1.8** | 355.4 → **28.7** |
> | gst-invoice-multipage-item-table | 42/47 | **45/47** | -52.1 → **-2.3** | 168.3 → **7.5** |
>
> Seven check-instances cleared: `25_invisible_text`, `27_text_off_page`, `44_header_footer`, `59_shape_anchor` on the first; `25`, `27`, `44` on the second. Both documents read 42/47 before this change, so the extra passes are the change and not a re-measurement artefact. No document got worse.
>
>
> Both agents reported refutations with numbers, and both matter more than the fix:
>
> - **The page-scale half is not one construct.** 8 of the 17 are single-page documents with no page break in their `document.xml` at all, worst_dy 105-230 pt. A page-top carrier cannot reach them.
> - **"Google delivers 5-10 pt of an exact line height" is wrong.** It charges `2.5873 x max(L/240, 0.06)` pt of an exact line box - 21.6 % of the declared height, proportional. Calibrated to 2.8 pt and 0.5 pt on two Google-measured documents. A proportional charge cannot be fudged with a constant.
> - Three of the 8 single-page documents carry no empty spacer at all; their displacement has the opposite sign and is explained by annotation paragraphs emitted with no `w:spacing`, inheriting a heading style's before/after.
> - Row growth under a wider substitute face: r² = 0.022. A cross-document `med_dy` law: r = 0.49. Neither is the cause.
>
> Both findings are committed: `FINDINGS/18-displacement-PAGE-SCALE-IS-THE-DROPPED-PAGE-TOP-26NOV-explore.md` and `FINDINGS/18-displacement-SINGLE-PAGE-SPACER-MEASURED-26NOV-explore.md`.
>
>
> `regress.py --check`, after all 213 documents were re-converted on the new engine:
>
> - `docx: no document worse than baseline` - the whole corpus, not a sample.
> - `google-safe: no construct Google ignores has spread` - the gate that exists to catch exactly this kind of change passed it.
> - `REFUSED` - not for a regression, but because `benchmarks/RANKING.csv` has not been re-measured on engine `025fe9deda5ac7b1`. `measure_gate.py` agrees: `NOT READY`.
>
> That refusal is correct and is not bypassed here. The one command left is `python3 benchmarks/p2w.py --force`, which fetches `origin/main` (now carrying this change) and re-scores all 213 documents on it; then `regress.py --stamp` passes. It is a ~20-minute pass and did not fit after the corpus conversion. Until it runs, "91 of 94 on 2 documents" is the honest state: only the two documents this run Google-verified are scored on the engine in the tree.
>
>
> The agents could not reach Google - the Drive write path needs the platform `upload` staging key, which a sub-agent does not have. Every "after" number they produced was LibreOffice, and LibreOffice is blind to this construct: it renders the unpatched file 47/47 PASS. The Google numbers in the table above are the parent run's own, made with `upload` → `GOOGLEDRIVE_CREATE_FILE` → export → `gverify.py --collect`, which is why they are the only ones this report claims.
>
>
> Three claims landed inside this run's slot: `baseline` at 15:07, a fixer at 15:10 (this run), and another at 15:50 which reset `RUN.json` - hence the self-check disagreement and `Document-moves this run: 0` while `attempt.py` recorded attempt 88 as kept with 2 moved. The attempt ledger in `ATTEMPTS.json` is the durable record; the run window is not. The push needed a cherry-pick onto `origin/main` because the state files conflicted on rebase, and the other claims' state commits were left alone rather than overwritten.
>
> Accounts share 19% of their significant words - a different account (the cut is 50%).
>
> Accounts share 19% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **8.7 h ago** - nothing re-measures this on a schedule; run `txt_gate.py --score 60` |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `--he-01` | --help | 19:43 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 18:57 → 19:45 · 47 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 33 |
| Longest silence | **16.2 min** — from 18:58:31, after `pending.py: reading the pending gate` |
| Silences over 2 min | 6 |
| Obstacles | 0 cleared · 1 parked, with the evidence to re-open them |
| Still a wall | `regress.py --check` refused every commit: `ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tre |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| build - compiling the engine | **0 min** | `#` |
| fix - diagnose and change the engine | **3 min** | `#` |
| measure or build - a conversion, screen or compile writes no beacon | **28 min** | `##############` |
| record - attempt, handoff, class rows | **4 min** | `##` |
| report - the report and the chain | **2 min** | `#` |
| other - not attributed to a tool | **7 min** | `####` |

The unattributed row is 8 distinct beat(s) that matched no phase. They said:

- `gate install timed out, checking phase`
- `building patched engine`
- `building HEAD engine for the honest before`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
