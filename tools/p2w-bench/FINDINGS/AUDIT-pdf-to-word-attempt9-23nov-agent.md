# PDF-to-Word — deep audit, attempt 9 of 10

Agent, 23 Nov 2026. Read-only. This is the memory question, open since attempt 1 and named as still-unmeasured in
attempts 6, 7 and 8. **It is answered, and the answer is structural.**

---

## I1 — every image on every page is held as a full PNG until the document is written

    DocxWriter.java:2520   public static final class Picture {
    DocxWriter.java:2521       public final byte[] png;        <- the whole encoded image

    PdfToWord.java:6010        DocxWriter.Picture pic = new DocxWriter.Picture(png, 0f, 0f, wpt, hpt);
    PdfToWord.java:6013        rules.pictures.add(pic);
    PdfToWord.java:6476        DocxWriter.Picture pic = new DocxWriter.Picture(png, 0f, 0f, ...);
    PdfToWord.java:6482        rules.pictures.add(pic);

    PdfToWord.java:6747        for (DocxWriter.Picture pic : rules.pictures) { ... page.blocks.add(pic); }
    PdfToWord.java:7275        out.pictures.addAll(collector.rules.pictures);

**The bytes are not streamed, not spilled to a temp file, and not released per page.** `rules.pictures` collects
them for the whole run, each page's `blocks` references the same object, and they live until `DocxWriter.write`
runs — which is *after* `convert` has returned, i.e. after the last page has been read.

**So the peak is reached at the very end of the conversion, and it is proportional to the total image content of
the document.**

**What that means for the file that matters most:** a scanned PDF is *one image per page by definition*. A
500-page scan at ~2 MB of PNG per page is ~1 GB of `byte[]` on the heap. An Android process on a mid-range phone
gets a few hundred MB. The conversion reads all 500 pages, holds every image, and then dies when the writer
starts.

**The user's experience is the worst version of this failure:** they wait for the entire conversion, and then it
fails — with `catch (Throwable)` at the app boundary turning an `OutOfMemoryError` into
`msg_could_not_read`, which names the wrong cause (the file was read fine; there was no room to write it).

---

## I2 — text is not the problem, and this is worth saying because it is where the memory *should* have been

The per-page structures are lighter than they look and are not retained across pages:

- `Glyph` has 12 fields (~96 bytes plus its two strings) but glyphs are built per page inside `readPage` and are
  not kept in `Result`;
- `Para` and `Run` are retained for every page, but a page of 40 paragraphs × 3 runs is ~24 KB, so 500 pages is
  ~12 MB.

**So the memory profile of a text document is fine.** The problem is images, and only images.

---

## I3 — the fix is the same one the OCR interface needs

`Picture.png` is a `byte[]` because `DocxWriter.write` has to put it into the `.docx` ZIP at the end. That is a
real constraint, not laziness — the ZIP is assembled once.

But it does not have to be held as bytes. Three options, cheapest first:

1. **Spill to a temp file per image and hold the `File`.** The writer reads it back when zipping. Peak memory
   becomes one image, not N. This is the smallest change and needs no format change.
2. **Write the ZIP entry as each image is produced** — i.e. stream the package instead of assembling it. Correct,
   and a much larger change to `DocxWriter`.
3. **Re-encode at a lower resolution when the document is large.** Loses fidelity — the opposite of what this
   project wants — so it is a last resort, not a first.

**Option 1 is the one to try first**, and it can be regression-checked cheaply: the `.docx` bytes should be
identical, because the same PNG goes into the same ZIP entry. Only the storage location changes.

---

## I4 — a claim this attempt did NOT test

The 1 GB figure above is arithmetic from the code path, not a measurement. **No 500-page scanned PDF was run
through the engine in this sandbox** — there is no Android runtime here, and the engine depends on
`android.graphics.Bitmap` for `encodePng`.

**What is measured:** the retention path (the `byte[]` is reachable from `Result` until write), and that `encodePng`
produces a `byte[]` per image. What is inferred: the size for a large scan. **The inference is stated as such.**

**To settle it, the fixer needs one measurement:** convert a 100-page scanned PDF on a device and read
`Debug.getNativeHeapAllocatedSize()` / `Runtime.totalMemory()` at the end of `convert`. If it is near the app's
heap limit, I1 is confirmed in size as well as in structure.

---

## For the fixer

**I1 is the finding; I3 option 1 is the edit.** Spill image bytes to temp files, hold `File` instead of `byte[]`,
delete them after the ZIP is written. Regression check: the produced `.docx` must be byte-identical on a document
whose images all fit comfortably — if it is, the change is safe for every document.

**Do not lower image resolution to save memory.** This project's whole point is fidelity; trading pixels for heap
would fix the crash and break the product.

Verify before changing. I1/I2/I3 were read from code; I4 says plainly what was not run.
