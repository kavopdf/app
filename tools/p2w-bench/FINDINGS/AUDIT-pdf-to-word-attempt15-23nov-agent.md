# PDF-to-Word — deep audit, attempt 15 of 15

Agent, 23 Nov 2026. Read-only. The last of fifteen. The target was `60_text_column_right_edge` (56 documents) and
`25_invisible_text` (48). It ended up producing the single most useful number in the series.

---

## O1 — `25_invisible_text` counts two different defects under one id

The counter (810-827):

    invisible = off_page = 0
    for p in doc:
        fills = fill_rects(p)
        for r in runs(p):
            for f in fills:
                if f["rect"].contains(Point(r["x"] + 1, r["y"] + 1)):
                    if colour_close(text_colour, f["fill"], 0.08):
                        invisible += 1        <- text the colour of the fill behind it
                    break
            if r["x"] < -1 or r["y"] < -1 or r["x1"] > W + 1 or r["y1"] > H + 1:
                off_page += 1                 <- text outside the page

**One check, two unrelated causes:** text that cannot be seen because it is the colour of what is behind it, and
text that cannot be seen because it left the sheet. A document can fail for either reason and the id says neither.

**The docstring records that this check used to fail documents against themselves** — white text on a white band,
a watermark — and that seven of 208 documents did exactly that before the measurement was taken from the source
too. So the check has a history of being wrong in this direction and has been narrowed once.

**For the fixer: split the id.** Two causes in one verdict means a fix for one cannot be seen as progress, and a
document that fails for `off_page` reads as a colour problem.

---

## O2 — the three biggest classes are largely independent, so they are three defects, not one

    documents failing 25_invisible_text         : 48
    documents failing 04_chars_missing          : 65
    documents failing 60_text_column_right_edge : 56

    pairwise overlap:  25 & 04 = 16      25 & 60 = 14      04 & 60 = 24
    all three      :  7

**Only seven documents fail all three, and the largest pairwise overlap is 24 of 65.** These are not aliases of one
underlying problem: a run that fixes character loss will leave most of the invisible-text documents untouched, and
vice versa.

---

## O3 — and together they are 76% of everything that is wrong

    scored documents             : 190
    documents with any failure   : 160   (84%)
    documents clean              :  30
    union of the three classes   : 122   (76% of all failing)

**Three checks cover three-quarters of the corpus's failures.** That is the number this whole audit was looking
for, and it was never stated in any report I have seen across fifteen attempts.

**It also reframes the work.** The corpus is not failing 42 different ways. It is failing three ways, mostly, and
the other 39 checks account for the remaining quarter.

---

## O4 — what I could not establish

**I did not find the writer-side mechanism for either class.** For `25_invisible_text` the plausible route is a
fill that is dropped while the text on it is kept — but the code explicitly protects dark bands
(`"A dark band carries white text … and must not stay dark in light mode"`), so the route is a band the writer
does not recognise as a band at all, and I could not name which.

**For `60_text_column_right_edge` I have nothing.** It is 56 documents and I did not reach its definition.

**Saying this is the honest close.** Fifteen attempts have produced mechanisms for the page count (K3/K4), the
memory (I1/J2), the OCR position (E1) and the stamp characters (N2). They have not produced one for these two, and
a run that starts from this file should read the checks' own definitions before hunting the writer.

---

## The fifteen attempts, in one table

| # | area | what it established |
|---|---|---|
| 1 | writers | no error handling inside `DocxWriter`/`TxtWriter` — corrected by 4 |
| 2 | page gate | 21 documents +1 page; the gate hides 41 other checks from 23 documents |
| 3 | checks | all 47 falsifiable, and the proof is not in the repo |
| 4 | app layer | guarded properly; the writers cannot say *what* they were building |
| 5 | OCR | **position is lost at the interface — `OcrHook` returns a String** |
| 6 | page loop | one corrupt page costs the document; 16 silent swallows, 2 on the text path |
| 7 | cancellation | the scope is right, nothing inside `convert` cooperates |
| 8 | escaping | an unpaired surrogate becomes `?`, proven by running Java |
| 9 | memory | every page image held as a PNG `byte[]` until the write |
| 10 | seam | `PdfRepair` loads leniently and spills to disk; `PdfToWord` does neither |
| 11 | document body | the extra page is `BREAK_WHEN_UNFITTABLE = false`, and not counted |
| 12 | tables | **I had it backwards — 62 documents run the table checks, 12 fail** |
| 13 | positioner | the one-positioner invariant is prose; its measurement (`rewind`) is off |
| 14 | characters | 14 of 16 stamp documents lose characters; text inside a graphic is the pattern |
| 15 | invisible text | **three classes are 76% of all failures, and they are independent** |

**The through-line, stated once:** this tool is not short of guards, checks or reports. It is short of the
information it needs to do its own job — a writer that cannot name the part it was building, a gate that cannot
say what else was wrong, a verdict that cannot say which check passed, an OCR hook that cannot say where the text
was, and an invariant whose only measurement is switched off.
