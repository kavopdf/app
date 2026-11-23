# PDF-to-Word — deep audit, attempt 10 of 10

Agent, 23 Nov 2026. Read-only. The seam between `PdfRepair` and `PdfToWord` — the two tools that have to hand a
damaged file to each other, and do not. This attempt also closes the second half of attempt 9's memory finding.

---

## J1 — the converter loads strictly; the repair tool loads leniently

The same PDFBox, in the same repository, used two different ways:

    PdfRepair.java:2029   parser.setLenient(lenient);
    PdfRepair.java:2219   PDDocument.load(out, password == null ? "" : password,
                              MemoryUsageSetting.setupTempFileOnly());

    PdfToWord.java:823    try (PDDocument doc = PDDocument.load(pdf, password == null ? "" : password)) {

**No leniency flag on the converter.** PDFBox's default parse rejects structures that `setLenient(true)` accepts —
a wrong `/Length`, an out-of-order xref, a stream whose declared size is short. Those are exactly the defects the
Repair tool exists to fix, and the Repair tool can open the file while the converter cannot.

**And the two are not connected.** `PdfRepair` appears in `ToolsActivity` only inside `Action.REPAIR`
(lines 203, 614, 871). The Word path at line 582 calls `PdfToWord.convert(src, ...)` on the file the user picked,
with no repair pass and no leniency.

**So the user experience is:** pick a slightly damaged PDF → "could not read this file" → and the message does not
say that the Repair tool, one screen away, would fix it. The tool that can read the file is the one the user was
not told to use.

---

## J2 — the converter holds the whole parsed PDF in memory, and the repair tool does not

    PdfToWord:823    PDDocument.load(pdf, password)                       <- no MemoryUsageSetting
    PdfRepair:2219   PDDocument.load(out, password, setupTempFileOnly())  <- spills to a temp file

`MemoryUsageSetting.setupTempFileOnly()` makes PDFBox keep the parsed document on disk and read it back as
needed. Without it, PDFBox keeps **every page object, every content stream and every embedded resource of the
whole document** on the heap for the lifetime of the `PDDocument` — which in `convert` is the entire run.

**This is the other half of attempt 9.** That attempt found every page's image held as a full PNG `byte[]` until
the writer runs. This one finds the parsed PDF itself held the same way. **A large document therefore pays twice:**
once for PDFBox's in-memory parse, once for the PNG bytes the converter produces from it.

**And again, the correct call is already written in this codebase**, three lines long, in `PdfRepair`.

---

## J3 — what this says about the five attempts before it

Attempts 1-9 each found one place where the tool could not say what it was doing. This attempt finds the same
pattern in a different form: **the tool already knows how to do the hard part.** `PdfRepair` has leniency, temp-file
spill and a diagnosis pass. `PdfToWord` has none of the three, and it is the tool that reads more files.

That is not a missing capability. It is a capability that exists in the same package and was not carried across
the seam.

---

## What this attempt did NOT cover, after ten

- the remaining ~7,600 lines of `DocxWriter` — only `esc`, the encoding, the package parts and `Picture` were read
- the 47 Kotlin files outside `ToolsActivity` / `PdfActivity`
- `PdfRepair`'s own body (2,723 lines) — only its loader was compared
- **a real large-document run** — attempts 9 and 10 both describe memory structurally; neither ran a 500-page
  file, and there is no Android runtime in this sandbox to run one
- the `pixdiff` pixel comparison path

---

## For the fixer

**J1 and J2 are one edit each, and both are copies of a call that already exists in `PdfRepair`:**

    PDDocument.load(pdf, password, MemoryUsageSetting.setupTempFileOnly())

and, where the file fails to load, a lenient retry before reporting failure. Neither changes what the converter
does with a good file — **so both are regression-checkable by converting a clean document and comparing the
`.docx` byte for byte.**

**And the message matters as much as the code:** if a file still cannot be read after a lenient attempt, say so
and point at Repair. A user who is told "could not read" when the app has a tool that fixes exactly that has been
told the wrong thing.

Verify before changing. All three findings were read from code; nothing was run.
