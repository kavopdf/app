# Fixer report - 2026-11-27 09:28

```
# P2W Fixer - Run Report

**27 Nov 2026 · slot 09:28 → running IST · 15 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| Check-instances passing | **2621** of 2805 (93.4%) on 64 documents |
| Check-instances still failing | **184** |
| Kept attempts vs documents clean | **16** classes with a kept attempt, **54** documents clean - a kept attempt is progress inside a class, not a finished document |
| Visual match, Google render | **4** at 99%+ SSIM, **10** at 95%+, median 84.1% over 213 scored |
| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - attempts: RUN.json counter 2 vs ATTEMPTS.json history 1 |
| Document-moves this run | **0** — 2 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **13** of the **64** re-measured on this engine - **141** of the 205 scored are still on an older engine, and **33** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **3** run(s) for the 141 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **8** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 40 clear — 40 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (56 still open), not a new class |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 09:42 | **lead** | 0/None | w:pBdr in the cell paragraph refuted in LibreOffice: the rule lands on the paragraph box (3.9 pt high for bottom, 10.45 pt low for top), not on the row edge; HEAD already reproduces the page's rules e |

## Why nothing moved, in this run's own words

> > **Nothing moved because the change this run was handed had never been measured where it counts. The
> > 09:13 run's own recommendation was that `w:pBdr` on the cell paragraph "cannot be refused by the
> > proxy" - it measures 15.00 pt in LibreOffice. This run built it three ways and it is refused by the
> > proxy on the first document it was told to prove it on, because 15.00 pt was the PITCH between the
> > new rules and nobody had asked where the rules were.**
> >
> > ## 1. What was inherited, and what it was worth
> >
> > `classpick.py --leverage` still puts `18_displacement` first. The 09:13 run left one thing: a
> > three-variant probe in which `w:pBdr/w:bottom` on the cell paragraph read 15.00 in Google and 15.00
> > in LibreOffice where `tblBorders/insideH` and `tcBorders/bottom` both read 15.75. Its conclusion -
> > *"B is the exception: it measures 15.00 in LibreOffice, so it cannot be refused by the proxy"* - is
> > the reason this run spent its slot on it instead of picking a new class. It was worth checking,
> > because it is the first construct in 105 attempts on this class that claimed to reconcile both
> > renderers.
> >
> > ## 2. What was built, and what happened in the first ten minutes of measurement
> >
> > Three builds behind `-Dp2w.pbdr=true` (patch kept in `FINDINGS/`, 87 lines, engine reverted after):
> > `w:pBdr/w:bottom` on every cell paragraph but the last row with `insideH` dropped; `w:pBdr/w:top`
> > with the table's top dropped; and the bottom form plus `w:after` sized so the paragraph box reaches
> > the row's bottom edge.
> >
> > `303_discharge_summary` is the document the 09:13 run named as the first proof target. Its source
> > PDF draws five ruled rows as five **stroked rectangles** at 273.38, 288.38, 303.38, 318.38, 333.37,
> > 348.37 - pitch 15.00, x 28.0 to 538.0. **The unmodified engine already reproduces that exactly in
> > LibreOffice**: 273.2, 288.2, 303.2, 318.2, 333.2, 348.2. There is nothing wrong with this document in
> > the proxy; its defect is Google-only, so any change to it is pure proxy risk.
> >
> > | build | LibreOffice rule y | verdict |
> > |:--|:--|:--|
> > | source | 273.38, 288.38, 303.38, 318.38, 333.37, 348.37 | - |
> > | HEAD | 273.2, 288.2, 303.2, 318.2, 333.2, 348.2 | **exact** |
> > | bottom | 273.2, **284.5**, 288.4, **299.2**, **314.2**, **329.2**, 348.2 | 5 rules where the page draws 4, the pBdr ones 3.9 pt high |
> > | top | 273.35, **283.7**, 288.4, **298.7**, **313.7**, **328.7**, 343.7, 348.2 | 8 rules, the pBdr ones 10.45 pt low |
> > | bottom + `w:after` | ... 284.5, 288.4, 299.9, 315.2, 330.6, **350.0** | rules still 3.9 pt high **and** the table grew 1.8 pt |
> >
> > Cell text is byte-identical in all four builds. Nothing here is a text problem.
> >
> > ## 3. Why the probe could not see it - the correction this run exists to leave behind
> >
> > A paragraph border is drawn on the **paragraph's box**, not on the row. The corpus cell paragraph is
> > `w:spacing w:before=209 w:line=11 exact` inside a `trHeight` of 15.00, so its top edge sits 10.45 pt
> > below the row's top and its bottom edge 3.9 pt above the row's bottom. Both builds put the rule on
> > one of those edges, which is exactly where the page does not draw it.
> >
> > **And the probe measured pitch, not position.** Three rules at 15.00, 15.00, 15.00 read "pitch
> > 15.00" whether they sit on the row boundaries or 3.9 pt above every one of them - a uniform offset
> > has zero pitch error. The probe's own Google table shows the tell and passes over it: variant B's
> > rule ys are 237.50, 252.50, 267.50, 282.50, 297.50, four pitches of exactly 15.00, and it never asks
> > where the first one is relative to the row it belongs to.
> >
> > **The method, stated without naming a class: when a construct moves a RULE, measure the rule's
> > absolute y against the page's rule, not the pitch between rules.** Pitch is a difference and is
> > blind to a constant. Two constructs in this class now have a right pitch and a wrong origin, and the
> > 22 Nov build of this same patch was diagnosed as a *text placement* problem when it was the same
> > placement problem seen from the other end.
> >
> > ## 4. Why no Google call was made, and why that is not a shortcut
> >
> > The charter's rule 3 - no document gets worse - is decided by `regress.py --check`, which is
> > LibreOffice. All three builds regress it on the document the lead named. A Google round trip would
> > have cost five minutes and could not have made a refused change committable, and the 09:13 Google
> > numbers are not contradicted by this run: a Google pitch of 15.00 for the bottom form is entirely
> > consistent with a rule 3.9 pt above the row boundary.
> >
> > The blast radius is the reason this had to be measured first rather than discovered in a corpus pass:
> > on the 213 built `.docx` at HEAD, **177 `insideH` rules across 77 documents** would have moved.
> >
> > ## 5. What is now true that was not this morning
> >
> > `w:pBdr` in the corpus's cell paragraph cannot carry the row rule in either edge, and `w:after`
> > cannot make it - the row grows before the border arrives, because `trHeight` is `atLeast` and the
> > renderer takes `max(trHeight, content + after)`. What would still work is a table whose cell
> > paragraph's box **is** the row's box (`before=0`, `line = trHeight` exact, no `after`); that document
> > has not been looked for. The patch, the finding and the four measurements are in `FINDINGS/` for the
> > run that looks.

### The run before this one said

> **No document moved because the engine change was never built — the 66 minutes went to a cold pod
> (19 min), a delegate_task call the platform ran inline instead of in the background (24 min), and one probe
> measurement (20 min). What the run produced instead is a construct the repository has recorded as
> impossible since 03:01 today.**
>
> ## 1. What the run was for
>
> `classpick.py --leverage` puts `18_displacement` at **54.4 clean documents**, more than the next three
> checks combined, and 28 documents fail that check and nothing else. Two root-cause files already
> existed. The 03:01 IST run today had proved the law — **Google lays a ruled row at `trHeight + 0.75 pt`,
> LibreOffice at `trHeight`** — over seven variants, and concluded:
>
> > There is no value of `trHeight` for which both renderers produce 15.00.
>
> It named the only escape in its own text — *"the horizontal rules have to leave the table (drawn as
> shapes or as paragraph rules that are not charged)"* — and never tested `w:pBdr`.
>
> ## 2. The measurement, which is the whole of the value this run adds
>
> One probe `.docx`, three variants, five rows each, every row `trHeight 300 atLeast` (15.00 pt), every
> cell paragraph the corpus construct (`before=209 line=11 exact`), 7 pt text.
>
> | horizontal rule carried by | LibreOffice pitch | **Google pitch** |
> |:--|--:|--:|
> | `w:tblBorders` + `insideH` (control) | 15.00 | **15.75** |
> | **`w:pBdr/w:bottom` on the cell paragraph** | **15.00** | **15.00** |
> | `w:tcBorders/w:bottom` (repeat of V9) | 15.00 | **15.75** |
>
> Both known-failing constructs land on 15.75 and the untested one on 15.00, so this is not a probe
> artefact. The rule is still drawn — five vector rules in each export — so the row height was not bought
> by losing the line, and Google's 1.00 pt stroke sits in exactly the same relation to LibreOffice's
> 0.35 pt as the control's table borders do.
>
> **Why it is worth more than its four documents.** The 03:01 finding's central warning was that a change
> correct in Google is *guaranteed* to look like a regression in LibreOffice, which `regress.py --check`
> gates on — that is why 98 attempts against this class died. This construct reads 15.00 in LibreOffice
> too. It cannot be refused by the proxy.
>
> **The two gaps I did not clear, so the next run does not inherit a trap.** The rule is inset by the cell
> margin (6 pt in the probe, which did not zero `w:tblCellMar`; the corpus's ruled tables do zero it,
> untested) and it is split at the column boundary where the original PDF's rule is continuous. And
> `w:pBdr` gives no `insideV`, so a table that draws column rules loses them unless a second construct
> carries them — all four documents this reaches carry `insideV`.
>
> ## 3. Why the attempt was not reached
>
> **24 minutes to a sub-agent that the platform ran inline.** `delegate_task(background=true)` came back
> after 1440 s with `"note": "Ran inside this turn, not in the background (an unattended run has no one to
> answer later)"`. The run before this one lost 27 minutes the same way. In a cron slot `delegate_task` is
> not a background tool, and the brief's "deploy sub-tasks in the first ten minutes, never wait" cannot be
> honoured by asking for `background=true`. That is a fact about the platform, not a judgement call.
>
> **19 minutes to a cold pod**, which is real work but not the goal: `corpus-fetch.sh` (213 PDFs, 0
> missing), `pod-prep.sh` (JDK, libs, engine, then 53 of 160 conversions in 207 s), and `corpus-slice.py`
> three times (53 in 182 s, 53 in 269 s, 1 in 7 s) until the stamp was written for engine
> `d28ca7516c3f9165`. `install-gate.sh` cannot finish inside one 300 s call; that is the whole of the
> "gate refuses everything" story, and this is the second run to say so.
>
> **The gate is not what refused this run.** `regress.py --check` exits 0 on the unmodified tree —
> docx: no document worse than baseline; txt: no document worse than baseline; google-safe: no construct
> Google ignores has spread.
>
> ## 4. What is ready for the next run
>
> The engine change is specified, not written, in
> `FINDINGS/18-displacement-PBDR-CARRIES-THE-RULE-AND-ROW-PITCH-RECONCILES-27NOV-fixer.md`: emit
> `insideH` as `w:pBdr/w:bottom` on every cell paragraph but the last row, drop `insideH` from
> `w:tblBorders`, leave `trHeight` and `insideV` untouched so it is one rule whose effect is measurable in
> isolation. Prove it on `303_discharge_summary` (measured at +2.80 pt on its last row by the 03:01 run),
> then `320_balance_sheet_statutory` for a different table shape, then the full `regress.py --check`.
> A warm pod and a PASSing gate are already in place.
>
>
> # Why nothing moved
>
> **Nothing moved because 27 of this slot's 90 minutes went to two agents that ran inline instead of in the
> background, and 10 more went to a cold pod. The engine change this run intended to build was never started.
> That is a scheduling failure of mine, and it is the whole of the answer.**
>
> ## 1. What the run was for, and what it found instead
>
> `classpick.py --leverage` refused a new class (35 pending items) and `pending.py`'s first item said to read
> `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` before anything. Doing that, the highest-leverage check with a live
> cause was `60_text_column_right_edge` (23.5 in the mixed-engine store, **5 over the 61 current-engine rows**).
>
> Before touching it I ran `install-gate.sh`, as the prompt says to. **It timed out at 300 s.** That is the
> first fact of the run, and it turned out to be the whole story.
>
> ## 2. The gate was not refusing a change. It was refusing a pod.
>
> On an unmodified HEAD tree `regress.py --check` refuses with four different messages, in sequence, and none
> of them is about the code:
>
> ```
> corpus : could not be built (1)      -> no corpus PDFs found - run corpus-fetch.sh first
> no java on PATH and no JAVA_HOME     -> run jdk-fetch.sh
> ClassNotFoundException: ConvertAll    -> engine classes never compiled
> PASS
> ```
>
> `pod-prep.sh` exists to install exactly those in exactly that order, and `install-gate.sh` calls it — which
> is why `install-gate.sh` cannot finish inside one 300 s call. Once the pod is warm:
>
> ```
> corpus-fetch.sh          213 PDFs, 212 scored, 0 missing
> pod-prep.sh              [1..6/6] warm, then 53 converted, 79 to go
> corpus-slice.py          53 converted in 242 s, 26 to go
> corpus-slice.py          26 converted in 130 s, DONE, stamp a4d8fca469bba636
> regress.py --check       PASS, exit 0
> ```
>
> **Three calls and about ten minutes from cold, thirteen seconds once warm.** Runs have been reporting this
> gate as the reason nothing lands; the gate was reporting a missing corpus, a missing JDK and missing classes.
> That is the correction, and it is in `FINDINGS/GATE-PREREQUISITES-ARE-THE-REAL-BLOCKER-27NOV-fixer.md` with
> the exact commands and their output.
>
> ## 3. The two agents: right answers, wrong mode
>
> Both were dispatched with `background=true` and both came back **inside this turn** ("an unattended run has
> no one to answer later"). 202 s and 1427 s. The second one alone was 24 minutes.
>
> Their findings are real and are committed:
>
> * **`60_text_column_right_edge` is settled.** The engine never writes a body line's right extent
> (`DocxWriter.java:4444`, `int rightTw = 0;`, no `w:jc` at `:4672-4675`), so the column edge is whatever
> advance the renderer's resolved face gives the string. Three engine fixes are already refuted by
> measurement: the right indent, the `w:jc="distribute"` pin (refuted in Google: 41/42 → 39/42, 28 lines
> wrapped), and the `w:rPr/w:spacing` advance carry (on `google_safe.py`'s IGNORED list, so the gate refuses
> it). The one construct that survives is a **right tab stop at the source line's own edge**, which
> `flowRow` already emits at `:3805-3809` — a position, not an advance, so it is face-independent and
> absolute in both renderers. Ceiling: **5 CLEAN documents**, not 23.5, because 55 of the 61 are held by
> other checks too.
> * **The gate diagnosis** above, which also produced two instrument defects recorded as proposals and
> deliberately not committed: `regress.py:636` labels every `google_safe.py` return-3 as "no .docx output
> directory" when the other cause is a corpus/mark size mismatch, and a docx-scoped commit can land with
> google-safe disclosed as skipped and the gate still exiting 0. Neither could be A/B measured on this pod
> without moving the 213-document output directory, so both stayed proposals, per non-negotiable 2.
>
> ## 4. What the next run should do first
>
> 1. `bash tools/p2w-bench/corpus-fetch.sh` then `bash tools/p2w-bench/pod-prep.sh` then `corpus-slice.py`
> until `DONE`, **before** `install-gate.sh`. Three calls, ~10 min. Do not read a timeout here as a refusal.
> 2. Build the right-tab construct in `flowFromBox` (`DocxWriter.java:4438`, schema position after `w:pStyle`,
> before `w:snapToGrid`) and move the last word behind `<w:tab/>`.
> 3. Test it on **`302_radiology_report` only** first. The prediction is falsifiable and already written down:
> source edge 543.74, today's Google edge ≤ 503.06, so the edge must travel right by ≥ 40.68 pt and land on
> **543.74 ± 1.0**, with `60` reading `(0,0,True)` and the document going **41/42 → 42/42**. Negative
> control: `purchase-order` must still read **+102.98** — that is an instrument artefact at
> `verify_google.py:2692`, a line moved 0.12 pt across a 10 pt bucket, and it must not change.
>
> ## 5. What I would do differently
>
> Deploy the agents, then **work in the same turn while they run** — or do not deploy them. In an unattended
> run they do not run in the background, and 27 minutes of a 90-minute slot is a third of the run spent
> waiting for two files I could have written myself from `FINDINGS/`. The gate prerequisites come first and
> cost ten minutes; the attempt is what the other eighty are for.
>
>
> **Two documents went from 46/47 to 47/47 in Google this run: `mobile-bill` and `electricity-bill`.**
> Both were failing one check, `18_displacement`, and nothing else. This section is why, and what the
> four measurements behind it cost.
>
>
> The last run's hand-off said "fix the rows and the anchor in one patch" and named `writtenRowsTw` /
> `lastRowHeightTw` as the consumer still charging the pre-patch heights. It is not. `writtenRowsTw` is
> floored at `pitchTwHere`, which equals the row's own pitch, so a row declared below its pitch is charged
> the same either way; and `rowBottomPt` is built from the page's own `lastRowTopPagePt`, not from the
> flow. There was nothing there to fix, and the attempt spent on it came back empty.
>
>
> Four copies of `mobile-bill`'s .docx differing only in `w:trHeight`, exported through Drive. The page's
> own row pitch is 18.40 pt:
>
> | declared twips | Google lays | against the page |
> |---|---|---|
> | 340 | 18.15 pt | -0.25 |
> | **350** | **18.40 pt** | **0.00** |
> | 360 (HEAD) | 19.15 pt | +0.75 |
> | 380 | 19.90 pt | +1.50 |
>
> Ten twips off the declaration is 0.75 pt off the laid row, and HEAD is 0.75 pt too tall on every row of
> both tables.
>
>
> Minus ten twips on every `w:trHeight`, measured in Google on five documents that were one check from
> clean: four did not move at all, and `price-list-2col-dense-right-aligned` went 41/42 to **40/42** by
> turning `46_text_crossing_rule` 0 to 2. A row whose text sits at its foot has no height to give:
> shorten it and the rule the page drew moves up through the text. The construct needs a gate, not a
> constant.
>
>
> Measured against the source's own baselines: `mobile-bill`'s caption-to-first-row gap is 16.40 pt on the
> page and 12.19 pt in the render; `electricity-bill`'s is 16.40 pt and 12.20 pt. Two different tables, two
> different declared gaps, **the same 4.2 pt short** - a construct, not a page. One-knob calibration on
> `electricity-bill`: `w:before` plus 180 twips moves the page **+8.7 pt** (about 1:1), `w:line` plus 180
> twips moves it **+2.06 pt** (about 23 %). The engine already knew this and already splits the gap, but it
> clamped the split to the page's remaining room, and on these pages the room is 0, so nothing was spent.
>
> The clamp is now a fraction. On `mobile-bill`, rung and gap together:
>
> | variant | median dy | 18_displacement |
> |---|---|---|
> | rung only, none of the gap spent | -9.65 | FAIL |
> | 60 % spent | -0.99 | FAIL |
> | **70 % spent** | **+0.49** | **PASS** |
> | 100 % spent | +4.70 | FAIL |
>
>
> Three constants and two lines in `DocxWriter.table`: `ROW_RUNG_UNDER_TW = 10`, `FOOT_ROOM_MIN_TW = 100`
> (the gate that keeps `price-list-2col` byte-identical - its `word/document.xml` hash is unchanged), and
> `SPACER_SPEND_FRAC = 0.70`. `regress.py --check` passes on engine `74a152e7` in both formats,
> google-safe clean, no document worse than baseline.
>
> The limit, stated plainly: this is a corpus-wide change and it was measured in Google on five documents.
> LibreOffice says nothing got worse on all 212, and the change moves a gap between two properties whose
> sum is unchanged, so a reader that honours both lays the page it always laid - but Google is the truth
> and only five were put through it. The gverify cron has 203 documents to re-measure on this engine;
> those runs are what turns "not worse" into evidence.
>
>
> - `18_displacement` is still failed by 105 documents and 25 of them fail nothing else. The same pair is
> the probe for that list - start with the ones whose `med_dy` is already small:
> `303_discharge_summary` (-0.2), `table-with-no-header-row` (-0.5), `402_calendar_month_grid` (1.4).
> - `74_balance_sheet_indented_subitems` does not move under this change and is not a table case: all 12 of
> its out-of-tolerance runs are positive (+3.2 to +4.3) and include `Page 1` and the signature block.
> - The 70 % fraction is measured on two documents. If a document regresses under it, the fraction is the
> knob to turn - and the way to find the right value for a page is the one-knob probe in section 4, not a
> corpus pass.
> - The self-check's one disagreement is the attempts counter (RUN.json 2 against one history row), not a
> second attempt.
>
>
>
>
> # Why nothing moved
>
> **Nothing moved because 27 of this slot's 90 minutes went to two agents that ran inline instead of in the
> background, and 10 more went to a cold pod. The engine change this run intended to build was never started.
> That is a scheduling failure of mine, and it is the whole of the answer.**
>
> ## 1. What the run was for, and what it found instead
>
> `classpick.py --leverage` refused a new class (35 pending items) and `pending.py`'s first item said to read
> `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` before anything. Doing that, the highest-leverage check with a live
> cause was `60_text_column_right_edge` (23.5 in the mixed-engine store, **5 over the 61 current-engine rows**).
>
> Before touching it I ran `install-gate.sh`, as the prompt says to. **It timed out at 300 s.** That is the
> first fact of the run, and it turned out to be the whole story.
>
> ## 2. The gate was not refusing a change. It was refusing a pod.
>
> On an unmodified HEAD tree `regress.py --check` refuses with four different messages, in sequence, and none
> of them is about the code:
>
> ```
> corpus : could not be built (1)      -> no corpus PDFs found - run corpus-fetch.sh first
> no java on PATH and no JAVA_HOME     -> run jdk-fetch.sh
> ClassNotFoundException: ConvertAll    -> engine classes never compiled
> PASS
> ```
>
> `pod-prep.sh` exists to install exactly those in exactly that order, and `install-gate.sh` calls it — which
> is why `install-gate.sh` cannot finish inside one 300 s call. Once the pod is warm:
>
> ```
> corpus-fetch.sh          213 PDFs, 212 scored, 0 missing
> pod-prep.sh              [1..6/6] warm, then 53 converted, 79 to go
> corpus-slice.py          53 converted in 242 s, 26 to go
> corpus-slice.py          26 converted in 130 s, DONE, stamp a4d8fca469bba636
> regress.py --check       PASS, exit 0
> ```
>
> **Three calls and about ten minutes from cold, thirteen seconds once warm.** Runs have been reporting this
> gate as the reason nothing lands; the gate was reporting a missing corpus, a missing JDK and missing classes.
> That is the correction, and it is in `FINDINGS/GATE-PREREQUISITES-ARE-THE-REAL-BLOCKER-27NOV-fixer.md` with
> the exact commands and their output.
>
> ## 3. The two agents: right answers, wrong mode
>
> Both were dispatched with `background=true` and both came back **inside this turn** ("an unattended run has
> no one to answer later"). 202 s and 1427 s. The second one alone was 24 minutes.
>
> Their findings are real and are committed:
>
> * **`60_text_column_right_edge` is settled.** The engine never writes a body line's right extent
> (`DocxWriter.java:4444`, `int rightTw = 0;`, no `w:jc` at `:4672-4675`), so the column edge is whatever
> advance the renderer's resolved face gives the string. Three engine fixes are already refuted by
> measurement: the right indent, the `w:jc="distribute"` pin (refuted in Google: 41/42 → 39/42, 28 lines
> wrapped), and the `w:rPr/w:spacing` advance carry (on `google_safe.py`'s IGNORED list, so the gate refuses
> it). The one construct that survives is a **right tab stop at the source line's own edge**, which
> `flowRow` already emits at `:3805-3809` — a position, not an advance, so it is face-independent and
> absolute in both renderers. Ceiling: **5 CLEAN documents**, not 23.5, because 55 of the 61 are held by
> other checks too.
> * **The gate diagnosis** above, which also produced two instrument defects recorded as proposals and
> deliberately not committed: `regress.py:636` labels every `google_safe.py` return-3 as "no .docx output
> directory" when the other cause is a corpus/mark size mismatch, and a docx-scoped commit can land with
> google-safe disclosed as skipped and the gate still exiting 0. Neither could be A/B measured on this pod
> without moving the 213-document output directory, so both stayed proposals, per non-negotiable 2.
>
> ## 4. What the next run should do first
>
> 1. `bash tools/p2w-bench/corpus-fetch.sh` then `bash tools/p2w-bench/pod-prep.sh` then `corpus-slice.py`
> until `DONE`, **before** `install-gate.sh`. Three calls, ~10 min. Do not read a timeout here as a refusal.
> 2. Build the right-tab construct in `flowFromBox` (`DocxWriter.java:4438`, schema position after `w:pStyle`,
> before `w:snapToGrid`) and move the last word behind `<w:tab/>`.
> 3. Test it on **`302_radiology_report` only** first. The prediction is falsifiable and already written down:
> source edge 543.74, today's Google edge ≤ 503.06, so the edge must travel right by ≥ 40.68 pt and land on
> **543.74 ± 1.0**, with `60` reading `(0,0,True)` and the document going **41/42 → 42/42**. Negative
> control: `purchase-order` must still read **+102.98** — that is an instrument artefact at
> `verify_google.py:2692`, a line moved 0.12 pt across a 10 pt bucket, and it must not change.
>
> ## 5. What I would do differently
>
> Deploy the agents, then **work in the same turn while they run** — or do not deploy them. In an unattended
> run they do not run in the background, and 27 minutes of a 90-minute slot is a third of the run spent
> waiting for two files I could have written myself from `FINDINGS/`. The gate prerequisites come first and
> cost ten minutes; the attempt is what the other eighty are for.
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
>
> Accounts share 18% of their significant words - a different account (the cut is 50%).
>
> Accounts share 33% of their significant words - a different account (the cut is 50%).
>
> Accounts share 18% of their significant words - a different account (the cut is 50%).

Accounts share 17% of their significant words - a different account (the cut is 50%).

## The txt

| | |
|:--|:--|
| Measured | **33 min ago** |
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
| Slot window | 09:28 → running · 15 min |
| Before the claim | not recorded - no session_start in ROUND.json to measure the gap from; round.py --heartbeat does write a beat before the claim |
| Tool beats | 29 |
| Longest silence | **4.5 min** — from 09:33:07, after `corpus-slice: 48 of 53 converted` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **1 min** | `#` |
| build - compiling the engine | **8 min** | `############` |
| record - attempt, handoff, class rows | **0 min** | `#` |
| report - the report and the chain | **1 min** | `##` |
| other - not attributed to a tool | **4 min** | `######` |

The unattributed row is 3 distinct beat(s) that matched no phase. They said:

- `relay: finishing baseline corpus conversion (pre-change engine)`
- `relay: pBdr construct refuted in LibreOffice, writing finding`
- `18_displacement -> lead`
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## Next run

READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 33 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 39 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 39 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 38 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 37 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 36 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 34 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 35 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 32 item(s) you can close - run pending.py and take them in its order before the class below. READ FIRST: FINDINGS/DOCS-ROOT-CAUSES-24NOV.md and FINDINGS/TXT-ROOT-CAUSES-18-AGENTS-24NOV.md - every open class root-caused, with the measurement that proves it. CORPUS: regress.py --check now builds the converted corpus itself (corpus-slice.py, 240 s a slice - a COLD pod needs TWO gate calls, the first fills one slice and ends at the 290 s ceiling, the second finishes and writes the stamp) - do not convert by hand, and do not skip the gate because "no .docx output directory" was ever the reason it could not run. PENDING FIRST: 31 item(s) you can close - run pending.py and take them in its order before the class below.

---
*Every number read from ROUND.json, RUN.json, ATTEMPTS.json, HANDOFF.json, BLOCKERS.md, TIMELINE.jsonl, benchmarks/RANKING.csv and benchmarks/RANKING-BASELINE.csv. Never remembered, never estimated.*

```

Written by report.py from committed files only. Every number above is read from
ROUND.json, RUN.json, ATTEMPTS.json, benchmarks/DEFECT-CLASSES.md, benchmarks/RANKING.csv
and benchmarks/RANKING-BASELINE.csv - never remembered, never estimated.
