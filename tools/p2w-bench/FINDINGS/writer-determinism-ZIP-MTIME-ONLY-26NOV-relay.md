# The writer is deterministic in content and not in bytes — every difference is the ZIP entry mtime

**26 Nov 2026, relay slot 14:18. Agent R-01, 18 documents, same engine `a4d8fca469bba636`.**

Two conversions of one PDF never produce the same sha256. They do produce the same `word/document.xml`,
`word/settings.xml`, `word/styles.xml`, `docProps/core.xml`, `word/_rels/document.xml.rels` and — where
present — `word/media/image1.png`. Not one byte of any part differs, on any of the 18 documents tested
(merged-cell table, annotated invoice, offer letter, 5-page bank statement, QR invoice, Devanagari table,
Arabic RTL, 2-page Form 16, comic page, XObject reuse, softmask, inline images, stamp-as-image,
16-tiny-pages, wide spanning table, and others).

The only differing bytes are the 2-byte DOS **time** field of each ZIP entry, in both the local header
(offset 10) and the central directory (offset 12): 18 positions in an 6 889-byte file, 36 in the
others. `0x48f5` = 09:07:42 and `0x48fc` = 09:07:56 — the wall clock second each entry was written,
truncated to the 2-second DOS grid. Zeroing only those fields makes the files bit-for-bit equal.
Two processes started inside the same 2-second bucket produce identical hashes; four back-to-back runs
crossing bucket boundaries produce four different ones.

Cause, from the source: `DocxWriter.write()` uses `new ZipOutputStream(...)` and
`zip.putNextEntry(new ZipEntry(name))` (`DocxWriter.java:758`, `:767`). `java.util.zip.ZipEntry`
defaults its time to `System.currentTimeMillis()` and the engine never calls `setTime` or
`setLastModifiedTime`. `PdfEngine.java:1050` `c.setTime(...)` is PDF metadata parsing, unrelated.

**What this means for the pipeline, and it is the whole reason to write it down:** any check that
compares two `.docx` by hash, or that reports "the file changed" from a hash, will always say changed
and will never say *what* changed. `benchmarks/DOCX-HASHES.json` and `DOCX-CHANGED.json` are that kind
of instrument. A byte-identity assertion must normalise the ZIP time fields first, or compare the XML
parts. Nothing needs to change in the engine for this: content determinism is what the corpus compares,
and it holds.
