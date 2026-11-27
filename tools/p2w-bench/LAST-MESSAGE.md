# P2W Fixer - Run Report

**27 Nov 2026 · slot 07:03 → running IST · 0 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **7788** of 8247 (94.4%) on 190 documents |
| Check-instances still failing | **459** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **55** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 0 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
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
| Working on | `-` - taken from the pending list (55 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## Why nothing moved, in this run's own words

*(not written. This run did not put its reasoning in `/tmp/why-nothing-moved.md`, so the only answer to "why did nothing move" is the table above - and a table of attempts is not a diagnosis. That absence is itself the finding.)*

### The run before this one said

> # Why nothing moved
>
> **Nothing moved because the change is a real trade, and this run measured the trade properly instead of
> the number that had been used to close it.**
>
> ## 1. The class, and why it was the right one
>
> `classpick.py` suggested `05_chars_extra` (0.8 clean documents, on a carried-over lead). `pending.py` then
> refused it: 33 items a fixer can close, take them in order. I took `18_displacement` — the pending list's
> own carried item, and the leverage table's top row at **53.2 clean documents**, with 27 documents failing it
> and nothing else.
>
> ## 2. Attempt one: the rung pair, re-measured in Google from this pod
>
> The last run left one instruction: *diff `document.xml` in full on mobile-bill, not just the `trHeight`
> values.* Done. Then the pair was re-applied with both switches and measured end to end through my own
> probe path (upload → Drive converts to a Google Doc → export PDF → `verify_google.py`):
>
> ```
> mobile-bill  HEAD (rungTw=0)         41/42  worst_dy  9.2  med_dy  -6.0
> mobile-bill  half A (rungTw=15)      41/42  worst_dy 66.7  med_dy -10.7
> ```
>
> Both numbers from the last run reproduce exactly. The control is real: `rungTw=0` on the patched tree is
> **byte-identical to HEAD** (`word/document.xml` sha256 `e162166f81c9d2d5`, and the `.txt` too).
>
> ## 3. What the full diff actually showed, and the correction it forces
>
> The last run recorded the change as **five rows, 2.5 pt**, and built a puzzle on it — "a 2.5 pt row change
> produced a 56.7 pt page movement, so the movement is not coming from the row heights at all." That count is
> wrong. Every `w:trHeight` in order:
>
> ```
> head  : 360 360 380 360 380 | 360 360 380 360 380 | 360 360 380 360 380 | ...
> halfA : 350 350 370 350 380 | 350 350 370 350 380 | 350 350 370 350 370 | ...
> ```
>
> **18 of 24 rows, not 5.** 18 × 0.5 pt = 9 pt, plus 1 pt of `w:before` — and the measured page movement is
> **−10.3 pt**. The movement is the row heights, at exactly the size they were changed. The puzzle was a
> miscount, and a run that believed it would have spent a slot hunting a phantom.
>
> ## 4. The number the revert was taken on is inflated 6× by its own aligner
>
> `worst_dy` reports 66.7. Pairing the two renders by exact text in an independent tool (PyMuPDF, not the
> harness), **all 115 runs match and none moves more than 10.3 pt**. A figure 6× the largest real movement
> cannot be one run's displacement; it is a pair whose two members are different text — mobile-bill carries
> `0.00` five times and `—` and `Unlimited` four times each, so after a uniform 10 pt shift a run can be
> matched to the next occurrence of the same string 60 pt away.
>
> `worst_dy` is reported and never scored (`verify_google.py:5897`). On checks this change is **one clean,
> zero worse**: 303_discharge_summary 46/47 → **47/47**, mobile-bill 46/47 → 46/47, same check failing both
> times.
>
> ## 5. So why is it still not landable
>
> Because the revert was right for the wrong reason, and the right reason is the one that matters. Median
> displacement on mobile-bill goes **−6.0 → −10.7 pt**. That is a document 4.7 pt further from its original
> than it already was, on a corpus whose goal is 99 % match. No check can see it. **The gate cannot protect
> this class, so a fixer has to.**
>
> ## 6. Attempt two: the pitch floor. Measured, and it changes nothing.
>
> Hypothesis: `mustTw` (the content floor) is short, so raise it to the measured row pitch —
> `mustTw = max(rowLineTw + ruleTwHere, pitchTwHere)`. **Result: a byte-identical declaration set**
> (`350 350 370 350 380`, same as before the guard). Reverted.
>
> The per-row dump explains why, and it is the run's most useful output:
>
> ```
> r=0 want=360 must=360 decl=350 laid=360 rule=10 line=350 pitch=360
> r=2 want=380 must=380 decl=370 laid=375 rule=10 line=370 pitch=380
> r=3 want=365 must=360 decl=350 laid=360 rule=10 line=350 pitch=360
> ```
>
> `must` already equals `pitch`, so the guard is a no-op by construction. And the patch is
> **self-consistent and correct by the law**: declared 350 + rule 10 = 360, on the 15 rung, and 360 is
> exactly the source pitch. HEAD declared 360 and so lays 370 — half a point too tall, 18 times. The engine's
> own model says the patched file is the better one and Google disagrees. **That gap is the question, and it
> is about Google's row layout, not about this patch.**
>
> ## 7. The next run's first test, and it is four files
>
> Two hand-made docx, one row each, declared 350 and 360 twips, identical content, exported through Drive. If
> one lays 10 twips shorter than the other, the law holds and the guard must come from somewhere else. If
> both lay the same height, Google is laying at content and every declaration below the content floor is
> inert — which would mean the rung law measured on 12 documents does not generalise, and that is worth
> knowing before another slot is spent on it.
>
> ## 8. The other thing this run fixed, which is worth more than the document it did not
>
> `pending.py` printed item 1 as **26,417 bytes — the same carry-over paragraph 42 times**, one copy per run,
> the only difference the number in "PENDING FIRST: N item(s)". Item 1 is the first thing the brief tells a
> run to read, so an unreadable item 1 is how every run came to skip the pending list and take a class
> instead. The duplication is in `HANDOFF.json["next"]`, which every run appends its own refusal to, and
> `pending.py` printed it verbatim with no bound and no de-duplication — while already containing exactly
> that collapse for `blocker` items, one `kind` test away.
>
> Fixed as presentation only: item 1 is now **628 bytes**, the queue is still **53 items**, the 33/20
> actionable/decision split is unchanged, and items 2–53 are byte-identical. Verified on the real repo, not a
> fixture: 50,707 bytes of stdout → 25,169.
>
> ## 9. For the next run: what is in the commit, and why the self-check flags it
>
> The commit `d041c80` is **findings plus one instrument fix plus the run's own tool state**. The engine
> source is untouched — `git checkout -- app/src/main/java/.../DocxWriter.java` after the second attempt, and
> the gate reports `a4d8fca469bba636`, docx, no document worse than baseline. The attempt is recorded as
> `--outcome lead --moved 0`, because no document moved.
>
> The self-check reads "3 code commit(s) in this window … ATTEMPTS.json has no kept record" and warns that the
> next run will read the class as parked. **It is not parked.** `18_displacement` is open with 27 documents
> failing it alone, and the rung pair is a measured lead, not a closed question — §7 is the test that decides
> it. The two things that are closed and must not be redone: the "5 rows / 2.5 pt / the movement is not the
> row heights" framing, which is a miscount (§3), and the pitch-floor guard, which is a no-op by construction
> (§6).
>
> The attempts counter also reads 2 against 1 history record; the extra row is a `none`-class record from this
> run's own bookkeeping, not a second attempt.
>
> ## 10. The four-file test was run before the slot closed, and it settles the premise
>
> Two hand-made docx, identical but for `w:trHeight` 350 vs 360, exported through Drive:
> **350 → Google lays 18.00 pt; 360 → Google lays 18.75 pt.** A 10-twip declaration moves the layout 15 twips,
> so the rung is real, it is 0.75 pt wide, and the patch's direction is correct. On mobile-bill the source
> pitch is 18.00 pt, which is exactly what declaring 350 lays — so **HEAD's table is 0.75 pt too tall on 18
> rows, 13.5 pt in total**, and the −10.3 pt movement is that error going away less the 2 pt of spacing the
> patch adds back.
>
> That leaves one place to look, and it is not the row heights: **whatever was compensating for the 13.5 pt is
> still charging the pre-patch heights.** The flow anchor after the table (`writtenRowsTw` /
> `lastRowHeightTw`) is that consumer. The next run should fix the rows and the anchor in one patch.
>
>
> # Why nothing moved
>
> **Nothing moved because the change is a real trade, and this run measured the trade properly instead of
> the number that had been used to close it.**
>
> ## 1. The class, and why it was the right one
>
> `classpick.py` suggested `05_chars_extra` (0.8 clean documents, on a carried-over lead). `pending.py` then
> refused it: 33 items a fixer can close, take them in order. I took `18_displacement` — the pending list's
> own carried item, and the leverage table's top row at **53.2 clean documents**, with 27 documents failing it
> and nothing else.
>
> ## 2. Attempt one: the rung pair, re-measured in Google from this pod
>
> The last run left one instruction: *diff `document.xml` in full on mobile-bill, not just the `trHeight`
> values.* Done. Then the pair was re-applied with both switches and measured end to end through my own
> probe path (upload → Drive converts to a Google Doc → export PDF → `verify_google.py`):
>
> ```
> mobile-bill  HEAD (rungTw=0)         41/42  worst_dy  9.2  med_dy  -6.0
> mobile-bill  half A (rungTw=15)      41/42  worst_dy 66.7  med_dy -10.7
> ```
>
> Both numbers from the last run reproduce exactly. The control is real: `rungTw=0` on the patched tree is
> **byte-identical to HEAD** (`word/document.xml` sha256 `e162166f81c9d2d5`, and the `.txt` too).
>
> ## 3. What the full diff actually showed, and the correction it forces
>
> The last run recorded the change as **five rows, 2.5 pt**, and built a puzzle on it — "a 2.5 pt row change
> produced a 56.7 pt page movement, so the movement is not coming from the row heights at all." That count is
> wrong. Every `w:trHeight` in order:
>
> ```
> head  : 360 360 380 360 380 | 360 360 380 360 380 | 360 360 380 360 380 | ...
> halfA : 350 350 370 350 380 | 350 350 370 350 380 | 350 350 370 350 370 | ...
> ```
>
> **18 of 24 rows, not 5.** 18 × 0.5 pt = 9 pt, plus 1 pt of `w:before` — and the measured page movement is
> **−10.3 pt**. The movement is the row heights, at exactly the size they were changed. The puzzle was a
> miscount, and a run that believed it would have spent a slot hunting a phantom.
>
> ## 4. The number the revert was taken on is inflated 6× by its own aligner
>
> `worst_dy` reports 66.7. Pairing the two renders by exact text in an independent tool (PyMuPDF, not the
> harness), **all 115 runs match and none moves more than 10.3 pt**. A figure 6× the largest real movement
> cannot be one run's displacement; it is a pair whose two members are different text — mobile-bill carries
> `0.00` five times and `—` and `Unlimited` four times each, so after a uniform 10 pt shift a run can be
> matched to the next occurrence of the same string 60 pt away.
>
> `worst_dy` is reported and never scored (`verify_google.py:5897`). On checks this change is **one clean,
> zero worse**: 303_discharge_summary 46/47 → **47/47**, mobile-bill 46/47 → 46/47, same check failing both
> times.
>
> ## 5. So why is it still not landable
>
> Because the revert was right for the wrong reason, and the right reason is the one that matters. Median
> displacement on mobile-bill goes **−6.0 → −10.7 pt**. That is a document 4.7 pt further from its original
> than it already was, on a corpus whose goal is 99 % match. No check can see it. **The gate cannot protect
> this class, so a fixer has to.**
>
> ## 6. Attempt two: the pitch floor. Measured, and it changes nothing.
>
> Hypothesis: `mustTw` (the content floor) is short, so raise it to the measured row pitch —
> `mustTw = max(rowLineTw + ruleTwHere, pitchTwHere)`. **Result: a byte-identical declaration set**
> (`350 350 370 350 380`, same as before the guard). Reverted.
>
> The per-row dump explains why, and it is the run's most useful output:
>
> ```
> r=0 want=360 must=360 decl=350 laid=360 rule=10 line=350 pitch=360
> r=2 want=380 must=380 decl=370 laid=375 rule=10 line=370 pitch=380
> r=3 want=365 must=360 decl=350 laid=360 rule=10 line=350 pitch=360
> ```
>
> `must` already equals `pitch`, so the guard is a no-op by construction. And the patch is
> **self-consistent and correct by the law**: declared 350 + rule 10 = 360, on the 15 rung, and 360 is
> exactly the source pitch. HEAD declared 360 and so lays 370 — half a point too tall, 18 times. The engine's
> own model says the patched file is the better one and Google disagrees. **That gap is the question, and it
> is about Google's row layout, not about this patch.**
>
> ## 7. The next run's first test, and it is four files
>
> Two hand-made docx, one row each, declared 350 and 360 twips, identical content, exported through Drive. If
> one lays 10 twips shorter than the other, the law holds and the guard must come from somewhere else. If
> both lay the same height, Google is laying at content and every declaration below the content floor is
> inert — which would mean the rung law measured on 12 documents does not generalise, and that is worth
> knowing before another slot is spent on it.
>
> ## 8. The other thing this run fixed, which is worth more than the document it did not
>
> `pending.py` printed item 1 as **26,417 bytes — the same carry-over paragraph 42 times**, one copy per run,
> the only difference the number in "PENDING FIRST: N item(s)". Item 1 is the first thing the brief tells a
> run to read, so an unreadable item 1 is how every run came to skip the pending list and take a class
> instead. The duplication is in `HANDOFF.json["next"]`, which every run appends its own refusal to, and
> `pending.py` printed it verbatim with no bound and no de-duplication — while already containing exactly
> that collapse for `blocker` items, one `kind` test away.
>
> Fixed as presentation only: item 1 is now **628 bytes**, the queue is still **53 items**, the 33/20
> actionable/decision split is unchanged, and items 2–53 are byte-identical. Verified on the real repo, not a
> fixture: 50,707 bytes of stdout → 25,169.
>
> ## 9. For the next run: what is in the commit, and why the self-check flags it
>
> The commit `d041c80` is **findings plus one instrument fix plus the run's own tool state**. The engine
> source is untouched — `git checkout -- app/src/main/java/.../DocxWriter.java` after the second attempt, and
> the gate reports `a4d8fca469bba636`, docx, no document worse than baseline. The attempt is recorded as
> `--outcome lead --moved 0`, because no document moved.
>
> The self-check reads "3 code commit(s) in this window … ATTEMPTS.json has no kept record" and warns that the
> next run will read the class as parked. **It is not parked.** `18_displacement` is open with 27 documents
> failing it alone, and the rung pair is a measured lead, not a closed question — §7 is the test that decides
> it. The two things that are closed and must not be redone: the "5 rows / 2.5 pt / the movement is not the
> row heights" framing, which is a miscount (§3), and the pitch-floor guard, which is a no-op by construction
> (§6).
>
> The attempts counter also reads 2 against 1 history record; the extra row is a `none`-class record from this
> run's own bookkeeping, not a second attempt.
>
> ## 10. The four-file test was run before the slot closed, and it settles the premise
>
> Two hand-made docx, identical but for `w:trHeight` 350 vs 360, exported through Drive:
> **350 → Google lays 18.00 pt; 360 → Google lays 18.75 pt.** A 10-twip declaration moves the layout 15 twips,
> so the rung is real, it is 0.75 pt wide, and the patch's direction is correct. On mobile-bill the source
> pitch is 18.00 pt, which is exactly what declaring 350 lays — so **HEAD's table is 0.75 pt too tall on 18
> rows, 13.5 pt in total**, and the −10.3 pt movement is that error going away less the 2 pt of spacing the
> patch adds back.
>
> That leaves one place to look, and it is not the row heights: **whatever was compensating for the 13.5 pt is
> still charging the pre-patch heights.** The flow anchor after the table (`writtenRowsTw` /
> `lastRowHeightTw`) is that consumer. The next run should fix the rows and the anchor in one patch.
>
>
> # Why nothing moved
>
> **Nothing moved because the change is a real trade, and this run measured the trade properly instead of
> the number that had been used to close it.**
>
> ## 1. The class, and why it was the right one
>
> `classpick.py` suggested `05_chars_extra` (0.8 clean documents, on a carried-over lead). `pending.py` then
> refused it: 33 items a fixer can close, take them in order. I took `18_displacement` — the pending list's
> own carried item, and the leverage table's top row at **53.2 clean documents**, with 27 documents failing it
> and nothing else.
>
> ## 2. Attempt one: the rung pair, re-measured in Google from this pod
>
> The last run left one instruction: *diff `document.xml` in full on mobile-bill, not just the `trHeight`
> values.* Done. Then the pair was re-applied with both switches and measured end to end through my own
> probe path (upload → Drive converts to a Google Doc → export PDF → `verify_google.py`):
>
> ```
> mobile-bill  HEAD (rungTw=0)         41/42  worst_dy  9.2  med_dy  -6.0
> mobile-bill  half A (rungTw=15)      41/42  worst_dy 66.7  med_dy -10.7
> ```
>
> Both numbers from the last run reproduce exactly. The control is real: `rungTw=0` on the patched tree is
> **byte-identical to HEAD** (`word/document.xml` sha256 `e162166f81c9d2d5`, and the `.txt` too).
>
> ## 3. What the full diff actually showed, and the correction it forces
>
> The last run recorded the change as **five rows, 2.5 pt**, and built a puzzle on it — "a 2.5 pt row change
> produced a 56.7 pt page movement, so the movement is not coming from the row heights at all." That count is
> wrong. Every `w:trHeight` in order:
>
> ```
> head  : 360 360 380 360 380 | 360 360 380 360 380 | 360 360 380 360 380 | ...
> halfA : 350 350 370 350 380 | 350 350 370 350 380 | 350 350 370 350 370 | ...
> ```
>
> **18 of 24 rows, not 5.** 18 × 0.5 pt = 9 pt, plus 1 pt of `w:before` — and the measured page movement is
> **−10.3 pt**. The movement is the row heights, at exactly the size they were changed. The puzzle was a
> miscount, and a run that believed it would have spent a slot hunting a phantom.
>
> ## 4. The number the revert was taken on is inflated 6× by its own aligner
>
> `worst_dy` reports 66.7. Pairing the two renders by exact text in an independent tool (PyMuPDF, not the
> harness), **all 115 runs match and none moves more than 10.3 pt**. A figure 6× the largest real movement
> cannot be one run's displacement; it is a pair whose two members are different text — mobile-bill carries
> `0.00` five times and `—` and `Unlimited` four times each, so after a uniform 10 pt shift a run can be
> matched to the next occurrence of the same string 60 pt away.
>
> `worst_dy` is reported and never scored (`verify_google.py:5897`). On checks this change is **one clean,
> zero worse**: 303_discharge_summary 46/47 → **47/47**, mobile-bill 46/47 → 46/47, same check failing both
> times.
>
> ## 5. So why is it still not landable
>
> Because the revert was right for the wrong reason, and the right reason is the one that matters. Median
> displacement on mobile-bill goes **−6.0 → −10.7 pt**. That is a document 4.7 pt further from its original
> than it already was, on a corpus whose goal is 99 % match. No check can see it. **The gate cannot protect
> this class, so a fixer has to.**
>
> ## 6. Attempt two: the pitch floor. Measured, and it changes nothing.
>
> Hypothesis: `mustTw` (the content floor) is short, so raise it to the measured row pitch —
> `mustTw = max(rowLineTw + ruleTwHere, pitchTwHere)`. **Result: a byte-identical declaration set**
> (`350 350 370 350 380`, same as before the guard). Reverted.
>
> The per-row dump explains why, and it is the run's most useful output:
>
> ```
> r=0 want=360 must=360 decl=350 laid=360 rule=10 line=350 pitch=360
> r=2 want=380 must=380 decl=370 laid=375 rule=10 line=370 pitch=380
> r=3 want=365 must=360 decl=350 laid=360 rule=10 line=350 pitch=360
> ```
>
> `must` already equals `pitch`, so the guard is a no-op by construction. And the patch is
> **self-consistent and correct by the law**: declared 350 + rule 10 = 360, on the 15 rung, and 360 is
> exactly the source pitch. HEAD declared 360 and so lays 370 — half a point too tall, 18 times. The engine's
> own model says the patched file is the better one and Google disagrees. **That gap is the question, and it
> is about Google's row layout, not about this patch.**
>
> ## 7. The next run's first test, and it is four files
>
> Two hand-made docx, one row each, declared 350 and 360 twips, identical content, exported through Drive. If
> one lays 10 twips shorter than the other, the law holds and the guard must come from somewhere else. If
> both lay the same height, Google is laying at content and every declaration below the content floor is
> inert — which would mean the rung law measured on 12 documents does not generalise, and that is worth
> knowing before another slot is spent on it.
>
> ## 8. The other thing this run fixed, which is worth more than the document it did not
>
> `pending.py` printed item 1 as **26,417 bytes — the same carry-over paragraph 42 times**, one copy per run,
> the only difference the number in "PENDING FIRST: N item(s)". Item 1 is the first thing the brief tells a
> run to read, so an unreadable item 1 is how every run came to skip the pending list and take a class
> instead. The duplication is in `HANDOFF.json["next"]`, which every run appends its own refusal to, and
> `pending.py` printed it verbatim with no bound and no de-duplication — while already containing exactly
> that collapse for `blocker` items, one `kind` test away.
>
> Fixed as presentation only: item 1 is now **628 bytes**, the queue is still **53 items**, the 33/20
> actionable/decision split is unchanged, and items 2–53 are byte-identical. Verified on the real repo, not a
> fixture: 50,707 bytes of stdout → 25,169.
>
> ## 9. For the next run: what is in the commit, and why the self-check flags it
>
> The commit `d041c80` is **findings plus one instrument fix plus the run's own tool state**. The engine
> source is untouched — `git checkout -- app/src/main/java/.../DocxWriter.java` after the second attempt, and
> the gate reports `a4d8fca469bba636`, docx, no document worse than baseline. The attempt is recorded as
> `--outcome lead --moved 0`, because no document moved.
>
> The self-check reads "3 code commit(s) in this window … ATTEMPTS.json has no kept record" and warns that the
> next run will read the class as parked. **It is not parked.** `18_displacement` is open with 27 documents
> failing it alone, and the rung pair is a measured lead, not a closed question — §7 is the test that decides
> it. The two things that are closed and must not be redone: the "5 rows / 2.5 pt / the movement is not the
> row heights" framing, which is a miscount (§3), and the pitch-floor guard, which is a no-op by construction
> (§6).
>
> The attempts counter also reads 2 against 1 history record; the extra row is a `none`-class record from this
> run's own bookkeeping, not a second attempt.
>
>
>
>
> **Three attempts, no document landed, and the class is now smaller than when the run started.**
>
> **1. The class, and why it was not the tool's suggestion.** `classpick.py` suggested
> `t09_page_furniture` on an open lead. A sub-agent spent the first minutes refuting that lead: the
> .docx half of t09 is already landed at all four code sites and its one surviving candidate can only
> shrink a firing set whose members already pass. I took `18_displacement` instead — 18 of 61 scored
> rows on the current engine, and 27 documents fail it alone.
>
> **2. Attempt one: the row rung as a pair. It fixed one document and wrecked two, so it was reverted.**
> The relay's prediction held exactly where it fired: `303_discharge_summary` 46/47 → **47/47** in
> Google, its footer moving the predicted 1.10 pt. But mobile-bill went worst_dy 9.2 → **65.9** and
> electricity-bill 28.5 → **47.8**. One clean against two worse is a trade and rule three refuses it.
>
> **3. The control that makes the number believable.** The patch carries `-Dp2w.rungTw=0` as an identity
> switch, so the same tree converts mobile-bill two ways: 9.2 with it off, 65.9 with it on. That one
> round trip is the difference between a measurement and a story.
>
> **4. Attempt two: the .txt reader drops every page separator — and fixing it moves nothing.** This
> was the run's best find and it did not survive contact with the corpus. `verify_txt.py`'s `_txt_lines`
> filters `if l.strip()`, and a line holding only `U+000C` is whitespace to Python, so every multi-page
> `.txt` was read as one segment. Patched to keep the separator, re-scored all 213 documents: **12
> failing check-instances before, 12 after, 0 worse, 0 better.** The patch is kept because it is
> correct, and it is now known to unblock nothing on its own — which corrects the t09 lead's premise
> ("blocked on an aligner plus a full .txt re-measure") in a way no future run has to rediscover.
>
> **5. Attempt three: the bisect, and it moves the blame.** Splitting the rung patch with
> `-Dp2w.rungCharge=0` (declare the rung, charge the old expression) reproduces **both** the fix and the
> regression: 303 47/47 and mobile-bill 66.7. So the charge — the half the relay said was the missing
> one — is not the culprit; the declaration is. And that is a puzzle worth handing on: on mobile-bill
> the declaration moved five rows by 0.5 pt each, upward, and the page moved 57.5 pt downward. The
> declaration is reaching something beyond row height, most likely whether Google lays a row at its
> declaration or at its content.
>
> **What the next run should not redo.** The pair as a whole; the content-driven guard; the per-table
> kill switch; the bisect; the t09 .docx half; the reader patch. All six are measured and written down.
>
> **Instruments.** The Google after-side works from this pod (`upload` → `CREATE_FILE` → `EXPORT` →
> `--collect`, with the file copied to `/scratch/output` first). Thirteen probe documents were created
> this run and all thirteen were deleted from the verify folder. The gate passes on the reverted tree:
> `a4d8fca469bba636`, docx — no document worse than baseline.
>
> **The one self-check disagreement, stated rather than hidden.** It says: four code commits in this
> window and no kept record. The code commit it is pointing at is `verify_txt.py` — the reader patch
> from attempt two, which changed no document's score (12 failing checks before, 12 after). `attempt.py`
> refuses to record it as `kept` ("a kept fix must have moved a document"), and it is right to; so the
> two rules cannot both be satisfied by a change that lands and moves nothing. It is recorded as a
> `lead` with its measurement, and the patch and its numbers are in
> `FINDINGS/TXT-READER-DROPS-THE-PAGE-SEPARATOR-27NOV-fixer.md` so the next run finds it by reading the
> finding, not by trusting a ledger row.
>
>
> **A trade was refused, and two instruments were found to be lying.** Three things happened, in this order.
>
> **1. The class I picked, and why it was not the tool's suggestion.** `classpick.py` suggested
> `t09_page_furniture` on the strength of an open lead. A sub-agent spent the first minutes of this run
> on that lead and came back with a refutation: the .docx half of t09 is already landed at all four
> code sites, and the one surviving candidate can only shrink a firing set whose members already pass.
> I took `18_displacement` instead: on the current engine it is 18 of 61 scored rows, and the shape
> census puts 27 documents on `18_displacement` alone, 15 more on it plus `60_text_column_right_edge`.
> The reason is in the report, not the tool.
>
> **2. The attempt: the row rung as a pair. 303_discharge_summary went 46/47 → 47/47 in Google and
> was not kept, because two other documents got worse.** The relay's prediction held exactly where it
> fired — the footer on 303 moved 1.10 pt, as predicted, and the document is now 47/47. But
> mobile-bill went worst_dy 9.2 → 65.9 and electricity-bill 28.5 → 47.8, both measured in Google. A
> document that goes clean while two get worse is a trade, and rule three refuses it, so the engine was
> reverted and the attempt recorded as a lead.
>
> **3. The regression is real, and I proved it rather than assuming it.** The patch carries
> `-Dp2w.rungTw=0` as an identity switch, so the same tree converts mobile-bill two ways. With the
> switch off, Google reads 9.2 — the committed baseline exactly. With it on, 65.9. That control cost one
> Drive round trip and it is the only reason the number in the table can be believed at all.
>
> **What the failure narrowed, which is the part worth carrying forward.** Two guards were built and
> neither removed the regression: a content-driven guard (rows whose content exceeds the declaration
> keep their old height and charge) and a per-table kill switch. The numbers barely moved. And the
> declarations themselves cannot explain 57 pt: the patch changed five rows on mobile-bill by 0.5 pt
> each, upward. So the movement is not coming from row heights at all — it is coming from what the flow
> after the table is charged, i.e. half B. **The next run should split the two halves behind two
> properties and measure mobile-bill and electricity-bill with each alone: four round trips, and it
> decides whether the rung law is one rule or two.**
>
> **Two instruments were caught lying, and both are worth more than the document.**
>
> - `verify_txt.py:939` filters `if l.strip()`, and a line holding only a form feed is whitespace in
> Python — so the reader drops every page separator the writer carefully emits (`TxtWriter.java:86`,
> `"\f\n"`, on its own line, by measurement). **Every .txt check in this pipeline is computed on a
> single segment for a multi-page document.** The t09 lead was recorded in the ledger as blocked on
> "an aligner plus a full 213-document .txt re-measure"; it is blocked on six lines of reader, and on
> the full .txt re-measure that any honest fix to the reader owes.
> - The Google after-side works from this pod: `upload` → `CREATE_FILE` → `EXPORT` → `--collect`, with
> the file copied to `/scratch/output` first. Eleven probe documents were created this run and all
> eleven were deleted from the verify folder at the end of it.
>
> **Not done, and not claimed.** No document is newly clean in the committed tree. The two FINDINGS
> files carry the measurements; the three relay reports are in `FINDINGS/` with a header saying which
> of their claims I checked myself and which I did not. The gate passes on the reverted tree
> (`a4d8fca469bba636`, docx: no document worse than baseline).
>
>
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
>
> Accounts share 11% of their significant words - a different account (the cut is 50%).
>
> Accounts share 42% of their significant words - a different account (the cut is 50%).
>
> Accounts share 25% of their significant words - a different account (the cut is 50%).
>
> Accounts share 53% of their significant words - **the same blocker, named twice** (the cut is 50%).
>
> Accounts share 57% of their significant words - **the same blocker, named twice** (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **4.1 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **205** (96.2%) |
| Failing at least one check | **8** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 3 documents |

## Subagents

*None deployed this run.*

## Timing

| | |
|:--|:--|
| Slot window | 07:03 → running · 0 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 6 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 39 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 39 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*
