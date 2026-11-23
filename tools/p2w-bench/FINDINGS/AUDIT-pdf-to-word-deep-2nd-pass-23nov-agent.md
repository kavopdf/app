# Deep audit, second pass — 23 Nov 2026

**Read-only. Nothing acted on. This pass covers what the first audit explicitly did not: `DocxWriter`'s
failure modes, `TxtWriter`, the app layer, memory, thread safety, and the checks' own pass conditions.**

The first audit (`AUDIT-pdf-to-word-deep-23nov-agent.md`) covered the engine's extraction path, the page loop
and the instrument's blind spot. This one hunts a different class of defect: the one that produces a **false
pass** — a bug that hides a defect rather than showing it.

---

## What this pass CLEARED — five false alarms, each verified safe

These looked like bugs from a scan and are not. Recorded so nobody re-opens them.

### 1. XML escaping — 43 `<w:t` writes but only 9 `esc()` calls

The count looks alarming and the conclusion is wrong. Every write that carries document text goes through
`esc()`:

    DocxWriter:4695   .append(esc(run.text))
    DocxWriter:6930   .append(esc(parts[q]))
    DocxWriter:7170   .append(esc(parts[q]))

The other `<w:t` writes are literal spaces — `<w:t xml:space="preserve"> </w:t>` — which cannot need escaping.
`esc()` at :7405 handles `&`, `<` and the rest. **A document containing `&` or `<` does not corrupt the docx.**

### 2. `TxtWriter` writes straight to the target, no temp-and-rename

`TxtWriter:125` opens `new FileOutputStream(out)` and writes. A failed write would leave a truncated `.txt`
that looks complete — the one format where truncation is undetectable, because a truncated `.docx` still fails
to open (no central directory) but a truncated `.txt` just looks short.

**It is safe because of where `out` points.** `PdfActivity.kt:121` makes it a cache file:

    val out = trackCacheFile(Files.newFile(this, pendingName))
    ...
    producer(out)                        // writes the cache file
    Files.writeToUri(this, out, uri)     // only then copies to the user's Uri

A failed write never touches the user's chosen file, and the failure is caught and reported. **No change
needed.**

### 3. Thread safety

- No mutable static state in `PdfToWord` or `DocxWriter` — every static field is `final`.
- `runTask` (`PdfActivity.kt:520`) runs the work inside `withContext(Dispatchers.IO)`, catches `Throwable`,
  records it through `CrashGuard`, and shows a toast. No main-thread work, no ANR.

### 4. Resource leaks

Every place a stream is opened uses try-with-resources: `DocxWriter:722-723` (the zip and its output),
`PdfRepair` 4 sites, `PdfSigner` 2, `PdfEngine` 78 `try (` blocks. Nothing to fix.

### 5. Checks that pass with `(0, 0, True)`

`35_rotation:3129` and `37_super_subscript:3307` pass when the source has nothing of that kind to preserve.
That is correct — there is nothing to measure. And `37` explicitly **fails** with a message when the source
*does* carry script runs and the `.docx` was not given. The distinction between "nothing to measure" and
"could not measure" is made properly in both.

---

## New finding N1. No memory guard on the PDF-to-Word path. **Severity: medium.**

`PdfRepair` has one:

    // PdfRepair.java:1179
    private static long freeHeapBytes() {
        Runtime rt = Runtime.getRuntime();
        long max = rt.maxMemory();
        long used = rt.totalMemory() - rt.freeMemory();
        return Math.max(0L, max - used);
    }

`PdfToWord` and `DocxWriter` have **zero** references to `maxMemory`, `freeMemory` or any size check:

    PdfToWord.java   maxMemory: 0
    DocxWriter.java  maxMemory: 0

And `PdfToWord.convert` holds every page at once — `result.pages.add(read)` at :833, with `Page` carrying every
glyph, line, paragraph, table and image of that page.

The corpus is 1–9 pages, so this never shows up there. A user converting a 300-page scanned report — the case
the app exists for — reaches the heap ceiling, `OutOfMemoryError` propagates, `ToolsActivity.kt:582` catches it
as `Throwable`, and the user gets "could not read" after minutes of work. **Same failure shape as B1 in the
first audit: no crash, total loss.**

`android:largeHeap="true"` is set (manifest:39), which raises the ceiling and does not remove it.

**How to verify before changing:** convert a long document (200+ pages, or the `pdf_repair_100` corpus
repeated) on a device and watch `Runtime.getRuntime().totalMemory()` across pages. If it climbs without
bound, the finding is confirmed. **Do not add a guard on the assumption** — measure the curve first, because a
guard that refuses a file the app can actually convert is worse than no guard.

---

## New finding N2. Three checks pass when `--docx` is missing. **Severity: low — latent, not active.**

    // verify_google.py:1590
    c["50_annotation_text"] = (len(s_at), 0, True)
    // verify_google.py:2006
    c["53_embedded_faces"] = (len(s_fa), 0, True)
    // and 54_image_dpi

Each prints a note to stderr and then **passes**. The comment on 50 says the run "must be visible as such
rather than passing silently" — and then sets `ok = True`, so from the JSON's point of view it did not fail.

**Checked whether this is active:** it is not. Both callers pass `--docx` —

    gverify.py:180   src, pdf, "--docx", docx, "--json", out_json
    gverify.py:230   src, pdf, "--docx", docx, "--json", out_json

So today every measurement carries the docx and these three checks measure something real. The risk is a
**future** caller that forgets the flag: three checks pass, the document scores higher than it is, and nothing
in the result says so. That is the exact shape of a false pass, and it is worth closing while it is still
latent rather than after it has inflated a ranking.

**The fix is a decision, not a mechanical change:** either those three checks report `ok = False` with
`measured = False` when the docx is absent, or the JSON carries a top-level `"docx": null` flag that
`gverify.py` refuses to score. The first is a one-line change per check and would make any forgotten flag
visible as a failure instead of a pass.

---

## Carried forward from the first audit, unchanged

- **B1, high** — `PdfToWord:830` calls `readPage` in the page loop with no try/catch. One bad page discards
  the whole document. `report.skippedPages` already exists and is already reported; the fix is a catch that
  increments it.
- **B2, medium** — notes capped at 200, `imageNotes` at 40, no "and N more" marker.
- **B3, low** — an OCR exception is swallowed and reported as "no text layer".
- **C, the instrument cannot see structure** — 50 named checks, 42–47 applied, and `numPr`,
  `headerReference`, `footerReference`, `fontTable`, `embedRegular`, `footnoteReference`, `abstractNum` are all
  zero. The four architectural gaps cannot appear in any number until that changes.

---

## The order to take them

| | finding | severity | cost of the fix | verify first |
|---|---|---|---|---|
| 1 | B1 page exception | high | one catch in a loop | corrupt one page, convert, see total loss |
| 2 | B2 note caps | medium | two one-liners | a document with >200 notes |
| 3 | B3 OCR message | low | one line | force the hook to throw |
| 4 | N2 missing `--docx` | low, latent | three one-liners | run verify_google without --docx, see three passes |
| 5 | N1 memory | medium | a guard, or a streaming rewrite | measure the heap curve on a long document |

**Every one of these is smaller than the four architectural gaps and every one is verifiable in a single
conversion.** Take them in this order, because each one either prevents a total loss or closes a false pass,
and neither costs a measurement round.

---

## The protocol the fixer must follow on each of these

The user's instruction, and it applies to every item above:

1. **Verify the finding is real before touching code.** Reproduce it. A finding in this file is a claim, not a
   fact — the reproduction is the fact.
2. **Change one thing.**
3. **Run the regression check on the whole corpus** — `regress.py --check` and `measure_gate.py`. A change
   that improves one document and worsens another is not a fix.
4. **Commit only after 3 passes.** A change that is not committed does not exist and must not be counted.
5. **If the finding does not reproduce, say so and do not change anything.** A false finding recorded as
   fixed is worse than an unfixed true one, because it stops anyone looking again.

---

## How this pass was done, so it can be repeated

Searched and read in place: every `catch (... ignored)` in `PdfToWord` (18) read to see whether it can drop
content; `esc()` and every `<w:t` write in `DocxWriter`; `TxtWriter`'s write path and its control-character
strip; `PdfActivity.runTask`, `finishSave`, `runAndSaveAs` and the producer/cache/Uri flow;
`AndroidManifest` for `largeHeap`; `PdfRepair.freeHeapBytes` and whether `PdfToWord` has its equivalent; static
fields in both writers; every check that returns `True` with a zero measured count, and each one's reason; both
`verify_google.py` invocations in `gverify.py`.

**Still not covered, and honestly worth a third pass:** `PdfEngine` (3,201 lines, 15 swallowed exceptions),
`PdfRepair` (2,723 lines, 30 swallowed exceptions) — both are different tools with their own audit — and a
runtime memory profile, which needs a device rather than a reading.
