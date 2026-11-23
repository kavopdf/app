# PDF-to-Word — deep audit, attempt 5 of 5

Agent, 23 Nov 2026. Read-only. Attempts 1-4 were the writers, the page-count gate, the checks and the app layer.
This one is the OCR path, and it found the root cause of a whole class of documents that cannot reach 99%.

---

## E1 — the OCR hook returns text without position, so position is lost at the interface

    public interface OcrHook {
        /** Text recognised on the given 0-based page, or null if it could not be read. */
        String text(int pageIndex) throws Exception;
    }

**A `String`.** No bounding boxes, no baselines, no font size. The engine is handed the words and told nothing
about where they were.

Everything downstream follows from that. Four places in `PdfToWord` receive text that arrived without
coordinates, and all four do the only thing they can:

    950   Para p = new Para(); p.runs.add(new Run(v, false, false, 11f));  p.top = 0;
    962   Para p = new Para(); p.runs.add(ar);                            p.top = 0;
    980   Para p = new Para(); p.runs.add(new Run(t.replaceAll(...), false, false, 11f)); p.top = 0;
    1006  Para p = new Para(); p.runs.add(new Run(t.replaceAll(...), false, false, 11f)); p.top = 0;

**`p.top = 0` on every one, and `11f` hard-coded as the font size.**

So on a scanned page the recognised text does not flow down the page in the shape it had. **Every paragraph is
placed at y = 0**, in 11 pt, and the page's real content — a photograph of text — is what the reader sees behind
it.

This is the defect the user names first, every time: *"ek ek text agar apne sahi position par hoga toh character
apne app sahi position par aa jaayega"*. For scanned documents the tool cannot honour it, and not because of a
tuning value — because the position was never passed in.

---

## E2 — a page with no text layer and no OCR is reported, not silently lost

    1013  report.skippedPages++;
          report.notes.add("page " + (index + 1)
                  + " has no text layer and was not OCR'd - it comes out empty");

The page is counted and the note names it. `ToolsActivity` turns `skippedPages` into a user-visible reason rather
than a generic failure. That is the right shape: a page that could not be read is a fact the user is told, not a
gap they discover later.

**What this audit did not prove:** whether the page's picture is still attached by the `attachPictures` call that
follows. The note says the page "comes out empty", which implies the picture does not carry it — but the note is
written by the same author who placed the call, and the call does run. **This needs one document and two minutes
to settle, and it decides whether a failed OCR loses the page or merely loses its text.** Flagged rather than
guessed.

---

## E3 — the OCR text is also flattened to one paragraph per blank-line block

    1006  for (String block : ocrText.split("\\n\\s*\\n")) { ... p.runs.add(new Run(t.replaceAll("\\s*\\n\\s*", " "), ...)) }

Two or more newlines make a paragraph; every other newline inside the block becomes a space. So a table
recognised by OCR arrives as one paragraph of words with its columns replaced by spaces, and the table structure
is gone before the table detector ever sees it.

**This is not a separate bug — it is E1 seen from the other end.** With boxes, the table would be recoverable;
with a string, it cannot be.

---

## E4 — what a correct fix looks like, and why it is not a tweak

`OcrHook` has one caller-visible method and one implementation (`WordOcr` in `ToolsActivity`, which already runs
`PdfRenderer` and an OCR pass per page). The Android OCR surface it uses returns recognised text **with bounding
boxes** — the boxes exist in the pipeline and are thrown away at this interface.

So the fix is:

1. `OcrHook` returns positioned text — a list of lines, each with its box and a size — instead of a `String`.
2. The four `p.top = 0` sites place each line at its own top and set its run size from the box height.
3. The table detector then receives geometry it can work with, which is E3 falling out for free.

**This is the largest single change any of the five attempts has found**, and it is the one that decides whether
scanned documents can ever be scored honestly — because until it lands, every scanned document is measured
against a layout the tool did not attempt to reproduce.

---

## Five attempts, and what they add up to

| # | area | the finding that matters |
|---|---|---|
| 1 | writers | no error handling inside `DocxWriter`/`TxtWriter` — corrected in 4 |
| 2 | page gate | 21 documents are one page too long, and the gate hides all 41 other checks |
| 3 | the checks | all 47 are falsifiable, and the proof is not in the repo |
| 4 | app layer | guarded properly; the writers cannot say *what* they were building |
| 5 | OCR | **position is lost at the interface — `OcrHook` returns a String** |

**The pattern across all five:** the tool is not short of guards, checks or reports. It is short of one thing —
the information needed to do the job. `DocxWriter` cannot say which part failed. The page gate cannot say what
else was wrong. The verdict cannot say which check passed. And `OcrHook` cannot say where the text was.

**For the fixer:** E4 is the work. E1/E3 are the same defect. E2 needs one document to settle. Attempts 1-4 are
in `FINDINGS/AUDIT-pdf-to-word-attempt{1,2,3,4}-23nov-agent.md`.

Verify before changing. All five attempts read code; none ran the engine.
