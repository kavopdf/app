# READ THIS FIRST — the fifteen-attempt PDF-to-Word audit, 23 Nov 2026

Fifteen files in this folder (`AUDIT-pdf-to-word-attempt{1..15}-23nov-agent.md`) are one audit by the agent. This
page is the index: what each found, in what order to read them, and **three places where the audit corrected
itself and a run must not repeat the mistake.**

**Two older files sit beside them and overlap.** `AUDIT-pdf-to-word-deep-23nov-agent.md` and
`AUDIT-pdf-to-word-deep-2nd-pass-23nov-agent.md` are from an earlier pass on the same day. The second one already
recorded *"No memory guard on the PDF-to-Word path"* and mentions silent swallows. **Attempts 9 and 10 below add
the specific mechanism to that (the `Picture.png` `byte[]` and the missing `MemoryUsageSetting`); attempts 1 and 4
largely restate it.** The agent did not search this folder before starting, which is the same mistake it made with
`TXT-FALSIFIABILITY.md` earlier — so read those two files before treating 1, 4, 6, 9 or 10 as new.

Read this page, then the three files marked **[mechanism]**. The rest are context.

---

## The numbers a run needs before it starts

    190 scored documents · 160 failing (84%) · 30 clean
    23 refused on page count and never examined at all

    documents failing 18_displacement           : 100
    documents failing 04_chars_missing          :  65
    documents failing 60_text_column_right_edge :  56
    documents failing 25_invisible_text         :  48

    union of 04 + 25 + 60                       : 122 of 160 failing = 76%

**Three checks are three-quarters of every failure, and they are three separate defects** (pairwise overlap
16 / 14 / 24, all three only 7). Fixing one leaves most of the others untouched.

---

## TWO CORRECTIONS — do not repeat these

**1. Tables are not a problem.** The audit said for three attempts that "62 documents fail checks 62-66". Wrong.
**62 is the number of documents that RUN the table checks; twelve failures exist in total** (66: 4, 62: 3, 63: 3,
64: 1, 65: 1). About a 4% failure rate — the best-performing area in the corpus. **Do not spend a run on tables.**
If a class list ranks the table checks high, it was built on the same misreading and should be rebuilt from the
`failed` lists, not from `total`.

**2. Fills are not the missing-character mechanism.** The old rule dropped 402 fills in 87 documents; that was
measured, and `isPageColour` now drops only fills within `PAGE_TOL` of the paper. Re-examining fill drops is
finished work.

**3. Almost all of this audit repeats work that already exists here, and only ONE attempt is new.** Checked by
grepping this folder for each finding's subject:

    attempt 5  OcrHook returns a String          ONLY my files mention OcrHook   <- new
    attempt 11 BREAK_WHEN_UNFITTABLE / overrun   4 existing findings already       <- repeat
               (18_displacement-ROWHEIGHT-CODE-MAP-142000-agentA,
                itr-slab-the-squeeze-is-not-the-defect-1645, and two more)
    attempt 13 the census / rewind               already known and used           <- repeat
               (18_displacement-CENSUS-AND-TWO-INSTRUMENT-FAULTS-0015-relay)
    attempt 14 the 04/25 mechanism               already measured, 127 docs       <- repeat
               (04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent)
    attempts 1,4 writers / app layer             already in AUDIT-...-deep-2nd-pass <- repeat

**And the existing findings are better: `TXBX-IS-RASTERISED` measured 127 documents re-converted with their
`word/document.xml` read directly. This audit read source and ran almost nothing.**

So: read attempt 5, and read `TXBX-IS-RASTERISED` and `CENSUS-AND-TWO-INSTRUMENT-FAULTS` instead of attempts 13
and 14. The rest of this folder is context, not new work.

---

## The three findings with a mechanism

**[mechanism] attempt 5 — `OcrHook` returns a `String`.** No boxes, no baselines, no size. Four sites in
`PdfToWord` (950, 962, 980, 1006) then place every OCR paragraph at `p.top = 0` in a hard-coded 11 pt. Scanned
documents cannot honour "text at its correct position" because the position was never passed in. `WordOcr` already
renders each page and the boxes exist in its pipeline.

**[mechanism] attempt 11 — the extra page is a deliberate trade, and it is not counted.** The fitter's third
outcome (`room < ascent`) keeps the line at its true height and lets the page overrun; `BREAK_WHEN_UNFITTABLE =
false` is hard-coded. Correct choice, but `ctx.fitted++` counts only the second outcome and **nothing counts the
overrun** — so a document that overran looks identical to one that did not.

**[mechanism] attempt 9 + 10 — memory, twice.** Every page's image is held as a full PNG `byte[]` in
`Picture.png` until `DocxWriter.write` runs (after `convert` returns). And `PDDocument.load` is called with no
`MemoryUsageSetting`, so PDFBox holds the whole parsed document too. `PdfRepair` already does both correctly:
`setupTempFileOnly()` and `setLenient`. **Copy the call that exists three files away.**

---

## The two measurement flags that are already built and switched off

    -Dp2w.debugFlow        per page: flowTw, budgetTw, overTw          (attempt 11)
    -Dp2w.census=<file>    per page: rewind, rewindWorst, rewindWho    (attempt 13)

**`rewind` is displacement, counted per page, in points, with the name of the writer that caused it.** The
`one-positioner-per-page` invariant is stated twice in prose and enforced nowhere; this census is the only thing
that measures it. **`18_displacement` is 100 documents and this is its measurement. Nothing in `p2w-bench` or
`benchmarks` passes either flag.**

There are **30 `p2w.*` properties** in total, several of them tunables rather than diagnostics. None is documented
anywhere a run reads.

---

## What has no mechanism yet — read the check before hunting the writer

    18_displacement            100   the census above is the way in
    60_text_column_right_edge   56   the check's definition was never reached
    25_invisible_text           48   counts TWO causes under one id: text the colour of its
                                     fill, and text outside the page. Split it before fixing it.
    05_chars_extra              43   no mechanism found; the check may count duplicates, not
                                     inventions — read its definition first

---

## The order to read the rest

    attempt 1   writers' error handling — corrected by 4
    attempt 2   the page-count gate: 23 documents never examined, not just unscored
    attempt 3   all 47 checks are falsifiable; the proof is in /scratch/saved, not the repo
    attempt 4   the app layer is guarded properly; the writers cannot say WHAT they were building
    attempt 6   one corrupt page costs the whole document; 16 silent swallows, 2 on the text path
    attempt 7   cancellation: the scope is right, nothing inside convert cooperates
    attempt 8   an unpaired surrogate becomes '?', proven by running Java
    attempt 12  the tables correction (above)
    attempt 14  14 of 16 stamp documents lose characters; text inside a graphic is the pattern
    attempt 15  the 76% number (above)

---

## What this audit did NOT do

**It read code. It ran almost nothing** — one Java program for the surrogate test, and nothing on a device, because
there is no Android runtime in the sandbox.

So: the mechanisms above are read from source and are certain. **Every claim about runtime behaviour — how much a
page overran, which writer rewinds, whether a stamp's text reaches `w:t` or becomes an image — needs one device
run to confirm.** The flags to do it are listed above and already exist.

Roughly a fifth of the ~25,000 relevant lines was read. `DocxWriter`'s anchor (4741), styles (4941) and three other
sections were never opened; `PdfRepair`'s body and 45 of 47 Kotlin files were not read at all.
