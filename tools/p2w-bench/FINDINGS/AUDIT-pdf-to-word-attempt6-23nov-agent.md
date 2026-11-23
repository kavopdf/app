# PDF-to-Word — deep audit, attempt 6 of 10

Agent, 23 Nov 2026. Read-only. Attempts 1-5 covered the writers, the page gate, the checks, the app layer and the
OCR interface. This one is the page loop and how one bad page is handled.

**Note on scope first:** `PdfEngine` (3,201 lines) is *not* part of PDF-to-Word. Its surface is `isEncrypted`,
`needsPassword`, `cropPages`, `pageCount`, `pageSizes`, `stampDisplayRasters`, `merge`, `keepPages` — the other
tools. PDF-to-Word reads with PDFBox inside `PdfToWord` itself. Attempts 7-10 should not spend time there.

---

## F1 — one corrupt page loses the whole document, and the message blames the file

The page loop, in full:

    for (int i = 0; i < count; i++) {
        Page read = readPage(doc, i, hook, result.report);
        mergeClusterTails(read);
        result.pages.add(read);
    }

**No `try` inside the loop.** And `readPage` has exactly **one** `catch` in its whole body — the OCR hook swallow
in F2. So these calls are unguarded:

    PDPage pdPage = doc.getPage(index);
    PDRectangle box = pdPage.getMediaBox();
    List<Glyph> glyphs = glyphsOf(doc, index);

A 200-page PDF with one damaged page is not an unusual file — it is the ordinary shape of a file that came out of
a scanner, an email gateway or a merge tool. When PDFBox throws on that page:

1. the exception leaves `readPage`, leaves the loop, leaves `convert`;
2. `ToolsActivity` catches it with `catch (Throwable)` and shows `msg_could_not_read`;
3. **the user is told the file could not be read — after waiting for 199 pages that were read fine.**

Nothing is written, because the write happens after `convert` returns. So the failure is total, and the message
describes the wrong thing: not "page 147 is damaged", but "could not read".

**The code already knows how to survive a page it cannot use** — `skippedPages` and a note per page exist
precisely for that. The loop just never gives a page the chance to be skipped.

---

## F2 — `catch (Throwable ignored)` loses the cause and makes the note name the wrong one

    String ocrText = null;
    if (!readAnnotations && hook != null) {
        try {
            ocrText = hook.text(index);
        } catch (Throwable ignored) {
        }
    }

When OCR throws, control falls through to:

    report.skippedPages++;
    report.notes.add("page " + (index + 1)
            + " has no text layer and was not OCR'd - it comes out empty");

**That note is wrong for this path.** "Has no text layer" describes a PDF with nothing to read. What actually
happened is that OCR was attempted and failed — an out-of-memory, a corrupt embedded image, a page the OCR engine
could not open. The user reads the note, concludes the PDF is fine and the tool did not try, and has no way to
learn otherwise.

And `ignored` means the `Throwable` is discarded. `CrashGuard` never sees it, the report never records it, so
**nothing anywhere can say why OCR failed on that page.** This is the same shape as attempt 4's finding — the app
boundary is guarded, but the guard explains nothing.

**The fix is small and does not change behaviour:** catch, record the throwable's type and message into
`report.notes` (or a new counter), and let the note say "OCR failed on page N: OutOfMemoryError" instead of "has
no text layer".

---

## F3 — what is still unmeasured after six attempts

Named so attempts 7-10 do not repeat it:

- **memory on a genuinely large document.** No attempt has run a real 500-page PDF. `convert` holds every page's
  glyphs and blocks in one `Result` before anything is written, so peak memory scales with page count × content.
  This is a claim to test, not a finding.
- **cancellation.** What happens if the user leaves the screen mid-conversion — nothing in the loop checks.
- **`DocxWriter`'s 7,671 lines** as a body of code — only its error handling has been looked at.
- **`PdfRepair`** — outside PDF-to-Word, but it is what feeds a damaged file into the converter, so the seam
  between them matters.
- **the 47 Kotlin files** outside `ToolsActivity`/`PdfActivity`.

---

## For the fixer

**F1 is the one with user-visible cost:** a single damaged page should not cost 199 good ones. The loop needs a
per-page guard that records the page as skipped — the reporting machinery for exactly that already exists.

**F2 is nearly free and makes F1 diagnosable:** stop discarding the throwable, and stop calling an OCR failure "no
text layer".

**Do not add a guard that silently continues** — attempt 4 showed the codebase already has one boundary that
swallows without explaining. A second would make a damaged file look like a clean one.

Verify before changing. This attempt read code; it ran nothing.
