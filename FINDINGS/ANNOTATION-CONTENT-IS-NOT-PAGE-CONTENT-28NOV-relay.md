# PDF annotation `/Contents` are written into the `.txt` — 1 document, and it is the one that fails

**28 Nov 2026, relay slot 11:25.** Fixer run, after the `TxtWriter` hoist lead turned out to be already
landed by the 11:00 slot.

## The measurement

`600_reviewed_invoice_with_annotations` is 7 of 8, failing only `t12_word_invention`. Its `.txt` opens
with three lines that are nowhere on the page:

```
Rate for HSN 8536 confirmed with PO.
Checked against PO 4471. Quantity on line 3 raised from 20 to 25.
Approved
```

They are annotation `/Contents` (three review comments), not page content: `pymupdf`'s `page.get_text()`
returns 776 characters for the page and does not contain any of them; the writer's output does. So the
`.txt` describes a document the user cannot see — text no reader of the page draws, which is exactly
what `t12_word_invention` exists to catch.

## The census, which is what makes it a small fix

Over all 214 corpus PDFs, counting documents with at least one annotation carrying a non-empty
`/Contents`: **1 document** — `600_reviewed_invoice_with_annotations` (3 annotations, all 3 present in
its `.txt`). Every other PDF in the corpus has none.

So the blast radius of dropping annotation text is **one document**, and it is the document that
becomes clean. Expected: `600` 7/8 → 8/8, corpus `.txt` 209 → 210 of 214.

## Why it is not landed

`pdfbox-android` 2.0.27's `PDFTextStripper` exposes no annotation hook. `javap` on
`libs/aar/classes.jar` lists `processPages`, `processPage`, `writePage`, `writePageStart`, `writePageEnd`
and no `processAnnotation`, so the annotation text is reaching the model by a path the subclass cannot
intercept at that seam. `PdfToWord.GlyphCollector` already overrides `processPage` for its own page box;
the next run should find where annotation appearances enter and either skip the annotation
sub-dictionary or filter glyphs whose source is an annotation's `/AP` stream.

## What would overturn this

A second corpus document whose `.txt` carries annotation `/Contents` that the page also draws — then the
filter would remove text the page shows. The census above says there is none today; it is 214 PDFs and
one pass of `pymupdf`, so re-running it costs a minute.
