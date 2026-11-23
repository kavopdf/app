# Deep audit of the PDF-to-Word tool — 23 Nov 2026

**Read-only. Nothing in this file was acted on. Every claim below is a line of code or a measurement, and each
one says how to check it.**

The user asked for an advanced deep audit: what is right, what is not, verified, and no blind fixing. This is
that audit. The four architectural gaps are in
`ARCHITECTURAL-GAPS-font-embedding-numbering-footnotes-0923-agent.md` and are not repeated here except where
this audit found something new about them.

---

## A. What is right — verified, no action

These are the things that are easy to get wrong and are not wrong here. Each was checked in the source.

| | evidence | why it matters |
|---|---|---|
| Text is never rendered as an image | `renderTextAsImage` / `textAsPicture`: **0** | LibreOffice's PDF-to-Word produces a page made of text boxes — 0% editable paragraphs in an independent 11-document test. A picture of text is the worst possible output. |
| Runs are coalesced by style | `coalesceRuns()` at PdfToWord:5482 merges adjacent runs with the same bold/italic/colour/size/face | One run per glyph would make typing inside a word produce a new run per character. This is the single biggest editing-quality decision in the writer and it is right. |
| Paragraphs group lines | `Para.lines` holds the PDF's drawn lines; the docx path reads `runs` | The alternative — one paragraph per line — breaks editing completely. |
| Headings carry `w:pStyle` | DocxWriter:3748 `Heading1..3` | Acrobat's own "Retain flowing text" mode loses heading styles, per Adobe's user forum and an accessibility write-up. |
| Merged cells | `w:vMerge` (5), `w:gridSpan` (2) | A merged header cell is a structural fact; most converters flatten it. |
| Overflowing values do not wrap | `w:noWrap`, DocxWriter:6624 | On `343_air_waybill`, "12" runs from 67.46 pt in a column ending at 76 — a word processor's default wraps it and the row arrives as "1" over "2". |
| Rows do not split across pages | `w:cantSplit` | |
| Page box is the PDF's own | `w:sectPr` with the media box, DocxWriter:1303 | Without it a landscape page comes out portrait and every x is measured against a width the page never had. |
| Images are counted, not swallowed | `imageDropped()` at PdfToWord:6485 | This used to be `catch (Throwable ignored)` and a full-corpus run dropped a picture in 15 documents with no word anywhere. Now counted, described, retried at lower resolution. |
| Multi-column is a table, not `w:cols` — deliberately | DocxWriter:1506, with the measurement | `w:cols` gave `63_three_column_brochure` 100% of lines within 3 pt and **13% reading order**. The table is the measured choice, not an oversight. |

**None of these needs touching. They are the reason this tool is not in the category of the ones it is
compared to.**

---

## B. Verified issues — genuine, with severity

### B1. One bad page kills the whole document. **Severity: high.**

    // PdfToWord.java:830
    for (int i = 0; i < count; i++) {
        Page read = readPage(doc, i, hook, result.report);   // <- not wrapped
        mergeClusterTails(read);
        result.pages.add(read);
    }

`readPage` is not inside a try/catch. It calls `glyphsOf`, `rulesOf` and PDFBox internals, any of which can
throw on a malformed page. If page 7 of 100 throws, pages 1–6 are discarded, 8–100 are never read, and the
user gets nothing.

**It does not crash** — `ToolsActivity.kt:582` wraps the call in `catch (t: Throwable)` and raises
`UserFacing`, so the user sees "could not read" instead of a stack trace. So this is not a stability bug.

**But it is the opposite of the behaviour asked for.** The requirement is that a heavy corrupted PDF is
handled like butter. Today one bad page means total loss.

**The infrastructure for the right behaviour already exists**: `report.skippedPages` (PdfToWord:749) is
incremented at :1013 for a page with no text, and `ToolsActivity` already reports it
(`word_no_text_pages`). A page-level catch that increments the same counter and continues is the whole fix.

**How to verify:** take a corpus PDF, corrupt one page's content stream (truncate it), convert. Today: error.
After: every other page converted, one skipped page named.

### B2. Report notes are truncated with no marker. **Severity: medium.**

    // PdfToWord.java:920
    if (report.notes.size() < 200) report.notes.add(...);
    // PdfToWord.java:6616
    if (rules.imageNotes.size() < 40) rules.imageNotes.add(note);

The 201st note is dropped silently. The **counts** are not capped — `imagesFailed` and `imagesRecovered` stay
accurate — so the number a report prints is right and the detail list under it is short without saying so.

A user reading 200 image failures cannot tell whether there were 200 or 2,000.

**Fix:** when the cap is reached, add one final note — `"and N more not listed"` — or record the true count
beside the list. Small, safe, no engine behaviour changes.

### B3. An OCR failure is reported as "no text layer". **Severity: low.**

    // PdfToWord.java:993
    try {
        ocrText = hook.text(index);
    } catch (Throwable ignored) {
    }

If the OCR hook throws — an out-of-memory on a large page, a native failure — the exception vanishes and the
page falls through to the "no text layer" note. The user is told the page had no text when in fact the text
was there and recognition failed. That sends them looking at the wrong problem.

**Fix:** carry the exception's message into the note. One line.

### B4. The four architectural gaps.

Font embedding (199 of 213 documents), `numbering.xml`, `headerReference`, `footnotes.xml` — measured and
specified in the companion file. Not repeated here.

---

## C. The finding that matters more than B1–B4 — the measurement cannot see structure

**This is the root cause of all four gaps being invisible, and it is worth more than any single fix.**

The suite defines **50 named checks** and applies 42, 44 or 47 of them per document depending on what the page contains. Not one of them examines the OOXML structure of the output:

    numPr              0 references in verify_google.py
    headerReference    0    footerReference  0
    fontTable          0    embedRegular     0
    footnoteReference  0    abstractNum      0

Every check compares the **render** against the **source**: is the text there, is it at the right x and y, is
it the right colour and size, does the table's geometry match, are the images at the right dpi. That is a
sound primary measure — the user's rule is that Google's render is the truth, and it is.

**But a document can render perfectly and still be uneditable.** A list drawn as indented paragraphs renders
identically to a real list. A header repeated as body text renders identically to a header part. A font named
but not embedded renders identically — on the machine that has the font.

So the pipeline measures **appearance** and the user's goal is **appearance + editing + completeness**. Two of
the three goals have no check at all.

**Three checks that do read the `.docx` look at the wrong thing, and they are the reason the gaps survive:**

| check | what it says it measures | what it actually measures |
|---|---|---|
| `53_embedded_faces` | embedded faces | the font **family** the docx names, bucketed by reader-family. A document naming `Times New Roman` where the source drew `Liberation Serif` passes — and neither is embedded. |
| `38_list_markers` | list markers | whether the marker **text** survived, not whether the paragraph carries a `w:numPr` that resolves in `numbering.xml` |
| `44_header_footer` | header and footer | whether the band's **text** survived, not whether it landed in a `w:hdr` part referenced from `w:sectPr` |

**What this costs.** A run reads `classpick.py`, takes the biggest class, and the four gaps rank 6, 2, unknown
and unknown. They are invisible not because they are small but because nothing measures them.

**What would close it.** Not a rewrite. Three checks whose pass condition is structural:

1. `67_font_embedded` — for each face the docx names and the source used, is there a `w:font` with
   `w:embedRegular` and a `.odttf` part that resolves?
2. `68_list_structure` — does every paragraph carrying a list marker carry a `w:numPr` whose `w:numId`
   resolves in `numbering.xml`?
3. `69_header_part` — is every repeating band line inside a header/footer part referenced from `w:sectPr`?

**These were deliberately not added.** `verify_google.py` is the instrument every number in this pipeline rests
on; a 43rd check changes the catalogue, leaves every existing `gverify` result one check short, and forces a
full re-measure. That blast radius is the fixer's call to make, not this audit's — but it should be made
knowingly, because until it is, the four gaps cannot appear in any number.

---

## D. What to hand the fixer

1. **B1 is the first thing to fix**, and not because it is the highest severity — because it is the smallest
   change with the clearest proof: `report.skippedPages` already exists, `ToolsActivity` already reports it,
   and the only missing piece is a try/catch inside the loop.
2. **B2 and B3 are one-liners** in the same pass.
3. **B4 is specified** in the companion file, ordered with the two cheap editing defects first.
4. **C is a decision, not a task.** Three structural checks would make the four gaps visible; the cost is a
   full re-measure. If the fixer wants the gaps in the rotation, that is the price.

---

## How this audit was done, so it can be repeated or falsified

Read, not guessed:

- `catch (... ignored)` counted per file: PdfRepair 30, PdfToWord 18, PdfEngine 15, NormStore 2, SoftMaskAlpha 2
- every `catch` in PdfToWord read in place, to see whether it can drop content
- the `convert` loop and its caller in `ToolsActivity.kt` read in full
- `verify_google.py` searched for structural OOXML terms: numPr, headerReference, fontTable,
  footnoteReference — all zero
- the three checks that read the `.docx` read in full, with their pass conditions
- `coalesceRuns`, `runsOf`, `w:cols` reasoning, `w:noWrap`, `w:cantSplit`, `sectPr` read in place

**Not covered by this audit**, and worth a later pass: memory behaviour on a 1,000-page document (every page is
held in `result.pages`), `PdfRepair`'s 30 swallowed exceptions (a different tool), and `TxtWriter` (899 lines,
not read here).
