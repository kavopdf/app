# P2W Fixer - Run Report

**27 Nov 2026 · slot 05:50 → running IST · 1 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **7788** of 8247 (94.4%) on 190 documents |
| Check-instances still failing | **459** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **55** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **2 disagreement(s)** - run window: RUN.json says this run began at 05:50 vs TIMELINE.jsonl records the claim at 05:13, so the window was reset and the duration is short; subagents: 2 deployed vs no FINDINGS filename carries Expl-02 - the work may be on disk under a topic name, and the next run cannot find it by id; rename it with the id first |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **189** re-measured on this engine - **16** of the 205 scored are still on an older engine, and **5** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 16 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (54 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 05:49 | **reverted** | 0/None | declare the row's laid height net of the rule on the 15-twip rung; Google before/after on 303 and 16_right_aligned: 46/47 and 41/42 in both arms, med_dy unchanged, worst_dy 4.1->3.8. The 0.75pt law is |
| 05:49 | **lead** | 0/None | annotationRuns() lacks the FreeText guard annotationContentsOf() has; 600 t12 83->49 invented chars, 1 of 213 .txt changed, txt clean 205 before and after, gate PASSes on worse/Google-safe then REFUSE |
| 05:50 | **reverted** | 0/None | t01 on the whitespace-stripped character multiset at zero tolerance: measured over all 213 .txt, clears 39 and 77 but fails 6 documents, 205 -> 201 clean. 99 percent char recall would additionally sil |

## Why nothing moved, in this run's own words

> All three attempts died on the same test the charter asks before every attempt: *if this works, which
> documents become CLEAN?*
>
> - **The rung rule (attempt 1)** answered 10 and the Google measurement said 0 of its own 2 worked
>   examples. The finding's model classified both rows `trHeight`-bound; on `303_discharge_summary` the
>   engine's own type floor (307 twips) is above the declared pitch (300), so the declaration was never the
>   number the renderer used. The patch moved the declaration and the render moved by 0.3 pt of worst_dy.
> - **The t01 character unit (attempt 2)** answered 2 and the measurement found 6 documents it would break.
>   The argument that justified it — "strictly weaker, so it can only clear documents" — is true of t12's
>   *surplus* and false of a zero-tolerance *deficit*, because the token count is a 99 % ratio and the
>   character deficit is an absolute. That claim was sitting in the source as a comment, and it is now
>   corrected in `FINDINGS/t01-CHARACTER-UNIT-REFUTED-205-TO-201-27NOV-relay.md`.
> - **The annotation FreeText guard (attempt 3)** answered 0 and was measured anyway, because it fixes a
>   real fidelity defect: two paragraphs of text no page prints were in the `.docx` the user opens. It moved
>   `600`'s invented characters from 83 to 49 and cleared nothing, so it was not landed and the 213-document
>   re-measure was not spent on it.
>
> None of this was blocked by a tool or by the gate. `regress.py --check` passes on the tree as it stands;
> on the patched tree it printed *no document worse than baseline* for both the `.docx` and the `.txt` and
> *no construct Google ignores has spread*, and refused only because the engine had moved without its tables
> being re-measured — which is the gate doing its job. What stopped these three was their own numbers.
>
> The pattern worth carrying forward: the last three runs have each spent a slot on a construct that the
> model said would clear documents and the renderer said would not. The model is being trusted one step too
> far. What is missing is not another patch in `DocxWriter.java` or `PdfToWord.java` — it is a Google
> measurement of the documents a change *hurts*, taken **before** the change is built. Attempt 2 is the
> shape that should be the default: it patched nothing, ran in one minute, and settled a construct that
> would otherwise have cost a whole run.

### The run before this one said

> I chose `18_displacement` because it is the largest class by leverage and because the run before this one had
> left a two-document Google probe saying this exact change takes documents to 42/42. What I did not have, and
> what the run before this one also did not have, is a Google measurement of the documents the change hurts.
> The proxy says 91 of them. Both statements can be true at once - LibreOffice honours `w:trHeight`, so the row
> was already right there and this only moves the baseline down inside it; a renderer that lays the cell needs
> the move. That is a collision between the instrument and the renderer the user opens, and no amount of
> further patching in `DocxWriter.java` settles it: what is missing is Google numbers for the same 204
> documents, not a better patch.
>
> So the honest result of this slot is one construct eliminated by measurement, one patch preserved with its
> numbers, and the corpus warm on the next engine it is applied to.
>
>
> The commit gate is open again, and two documents were taken to 42/42 in Google by changing four characters
> of XML each. Neither is landed: the engine change needs the 212-document table re-measured on the new
> engine, and that pass did not fit the slot.
>
> That pass did fit this slot - 213/213 converted in four slices, 204 of 212 measured in four chunks - and it
> is what refused the change. The finding that run says it wrote,
> `FINDINGS/18-displacement-CELL-CONTENT-SHORT-OF-ROWH-27NOV-fixer.md`, is **not in the repository**: the
> report claims it, `git log -- FINDINGS/` has no commit for it, and `ls FINDINGS/` does not list it. The
> probe's exports were on that pod only. That gap is why this run had to re-derive the mechanism from the code
> instead of from the numbers.

Accounts share 14% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **2.9 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `Expl-01` | Explore:docx construct ranking by documents-cleared  | 05:51 | - | - |
| `Expl-02` | Explore:txt failure root cause (8 docs, 12 check-ins | 05:51 | - | - |

## Timing

| | |
|:--|:--|
| Slot window | 05:50 → running · 1 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 17 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| record - attempt, handoff, class rows | **0 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |


## Next run

1. **`600_reviewed_invoice_with_annotations` is three defects, not one.** After the FreeText guard it still
   carries 49 invented characters: about 30 are its FreeText emitted **twice** (the duplicate guard at
   `PdfToWord.java:957` does a whole-sentence substring match against `pageOwn` and never applies
   `drawnByAppearance`, which the form-value loop at `:945` does), and about 19 are truncated table amounts.
   Do all three in one attempt with one re-measure, not three.
2. **`303`'s real defect is `rowHeightTw = max(rowTwHere, rowLineTw)` using the clamped `rowLineTw`**, so the
   engine declares a row shorter than the line box it says the row needs. Not the rung, never measured.
3. **Do not rebuild the rung rule as a clean-maker.** Measured and refused on its own two worked examples;
   the 41-line patch is in `FINDINGS/18-displacement-RUNG-DECLARATION-27NOV.patch` for the run that wants
   the other eight documents it claimed.
4. **`t01`'s two documents are an engine word-boundary defect, not an instrument one.** `textOf()` splits at
   0.18 em where the source splits at 0.15 em — that is why `39`'s `570005` comes out `57 0 0 05`.
5. **The pod is warm on the tree's own engine**: 213 of 213 converted at `a4d8fca469bba636`, cache stamp
   matches, `regress.py --check` passes.

Two agents were deployed before any work: one ranked every docx construct by the documents it would clear
(and named the rung rule first), one root-caused the txt failures. The txt agent's top recommendation is
exactly what attempt 2 refuted — the refutation is worth more than the recommendation was.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
