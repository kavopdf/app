# PDF-to-Word — deep audit, attempt 4 of 5

Agent, 23 Nov 2026. Read-only. Attempts 1-3 were the writers, the page-count gate and the checks. This one is the
app layer — the Android code that calls the engine — and it produced a correction to attempt 1.

---

## D1 — the app layer is guarded, and more carefully than the engine is

The chain from a tap to a `.docx` on disk:

    ToolsActivity.kt:582   PdfToWord.convert(src, "", ocr)
    ToolsActivity.kt:600   if (asTxt) TxtWriter.write(...) else DocxWriter.write(...)
    PdfActivity.kt:158     runAndSaveAs(...) -> CreateDocument launcher -> finishSave(uri)
    PdfActivity.kt         try { producer(out); Files.writeToUri(...) } catch (t: Throwable) { ... }

Three things in that chain are worth recording, because they are done properly:

**`convert` is caught with `Throwable`, not `Exception`, and closes the OCR renderer in `finally`:**

    val result = try {
        PdfToWord.convert(src, "", ocr)
    } catch (t: Throwable) {
        throw UserFacing(t.message?.takeIf { it.isNotBlank() } ?: getString(R.string.msg_could_not_read))
    } finally {
        ocr.close()
    }

**The write runs inside `finishSave`'s guard, and that guard distinguishes the two kinds of failure:**

    try {
        producer(out)                       // TxtWriter.write / DocxWriter.write
        Files.writeToUri(this, out, uri)
        AppLog.record(this, taskName, pendingName, true)
        out
    } catch (t: Throwable) {
        if (t !is UserFacing) CrashGuard.problem(this, taskName, t)
        failureLogged = true
        // the picker already created an empty document - delete it
    }

A user mistake (opening a Word file in the PDF picker) does not get logged as a crash; an unexpected failure
does, with the Throwable. And the empty document the system picker created is removed, so a failed save does not
leave a zero-byte file where the user expects their document.

**The OCR renderer has an explicit out-of-memory guard**, per its own comment: the scale is reduced until the
image fits inside a cap, and never below 1x — so a large scanned page degrades in resolution instead of taking
the process down.

---

## D2 — this corrects attempt 1, and the correction is against my own earlier finding

Attempt 1 recorded A1 and A2 as: `DocxWriter` has no error handling in 7,671 lines, and `TxtWriter` has none in
899. **Both remain true of those files.** What attempt 1 did not say — because it had not followed the call
chain — is that the caller catches `Throwable` around the write.

So the blast radius is smaller than attempt 1 implied:

- a write that throws does **not** crash the app;
- it becomes a `UserFacing` message or a `CrashGuard` problem;
- the empty output document is deleted;
- the OCR renderer is closed either way.

**What is still missing is diagnosis, not safety.** `CrashGuard` receives the `Throwable`, so it knows a
`NullPointerException` happened at line N of `DocxWriter` — and it does **not** know that the failure was in the
table part of page 3. A writer that cannot say which part it was building is still a writer that cannot explain
a bad document. That is the part of A1/A2 that survives, and it is the part that matters for this project.

---

## D3 — the audit trail is real, and it distinguishes success from failure

`AppLog.record(this, taskName, pendingName, true)` on the success path, `CrashGuard.problem(...)` on the failure
path, and `failureLogged` so a failure is not double-reported. That is the behaviour the user asked for: the log
should carry crashes and errors, not a running commentary.

---

## What this attempt did NOT cover

- `PdfEngine` (3,201 lines) and `PdfRepair` (2,723) — untouched by all four attempts
- the page loop and the OCR decision inside `convert`
- memory behaviour on a genuinely large document (a real 500-page PDF was not run)
- cancellation: what happens if the user leaves the screen mid-conversion
- the 47 Kotlin files outside `ToolsActivity`/`PdfActivity`

---

## For the fixer

**D2 is the one to act on, and it is narrow:** the writers need to name what they were building when they threw.
A single try/catch per document part that rethrows with the part's identity turns a stack trace into "the table
on page 3", which is what a fixer can act on.

**Do not add defensive layers at the app boundary.** It is already guarded; adding more there would hide failures
rather than explain them, which is the opposite of what this project needs.

Verify before changing. This attempt read the call chain; it ran nothing.
