# The four architectural gaps — what they are, how to close them, and why they are not in the class table

**Measured 23 Nov 2026 by the agent. Nothing here is fixed. This is the specification the fixer works from.**

The user asked whether the tool uses the best techniques for a 100% on-device constraint. The technique family
is right — glyph-level extraction, geometry, hand-written flowing OOXML, no ML, no network. Three specific
capabilities are missing, and **all three are fixable offline with no model, no internet and no new
dependency.** None of them is a class the rotation will ever reach on its own, and the reason for each is
different. That reason is the most important part of this file.

---

## Gap 1 — fonts are named, never embedded. 199 of 213 documents are affected.

### The measurement

Every `.docx` this engine writes names its fonts and embeds none:

    word/fontTable.xml       0 of 28 sampled docx
    getFontFile / FontFile2  0 references in the engine
    .odttf (obfuscated font) 0 references

Across the corpus, the faces the documents actually use:

    Effra              1191 runs    commercial, on no phone
    Times New Roman    1056 runs    universal
    Arial               321 runs    universal
    Effra-Medium         45 runs    commercial
    NotoSansDevanagari    4 runs    not on most phones
    Webdings              2 runs    symbol

And across all 213 source PDFs:

    documents using ONLY universal families   14
    documents with a non-universal family    199

Liberation Serif/Bold, DejaVu Sans, Liberation Sans — Linux faces. Android ships Roboto and Noto; Windows
ships Arial and Times. None of those are the face the PDF drew.

### Why this matters more than any class in the table

The requirement is **text position exactly as the PDF**. Position is decided by glyph advance widths, and
advance widths belong to the face. Name a face the reader does not have and the reader substitutes one whose
widths differ; every line reflows and the x of everything after the first word moves.

**The engine already knows this and compensates numerically.** DocxWriter models the substitute face's line
height ("a MULTIPLE OF THE SUBSTITUTE FACE'S LINE HEIGHT with a floor at 0.069 em", "the reader's own single
line height, in em, for the face it substitutes"). That is sophisticated and it is why vertical drift is
survivable. But compensation is not reproduction: the widths still differ, and `18_displacement` — 101
documents in Google, the largest class in the corpus, 23 attempts and every one a `lead` — is the shape of
that residual.

**A fixer that treats `18_displacement` as pure geometry may be treating a font problem with geometry.**

### How to close it

Three steps, all inside the engine, all offline:

1. **Read the font program.** PDFBox gives it: `PDFont.getFontDescriptor().getFontFile()` (Type1),
   `getFontFile2()` (TrueType), `getFontFile3()` (CFF/OpenType). The corpus is almost entirely TrueType and
   Type0, so `FontFile2` is the path that matters.
2. **Obfuscate it the way OOXML requires.** Word embeds fonts as `.odttf` in `word/fonts/`: the first 32
   bytes are XORed with the 16-byte GUID taken from the font's part name, repeated twice. The algorithm is
   in ECMA-376 Part 1 §17.8.1. It is twenty lines and it is the only non-obvious step.
3. **Declare it.** Write `word/fontTable.xml`, add the part to `[Content_Types].xml` and
   `word/_rels/document.xml.rels`, and in `styles.xml` point the face at it:

        <w:font w:name="Effra">
          <w:embedRegular r:id="rIdFont1" w:fontKey="{GUID}"/>
        </w:font>

**Do it as a subset, not the whole face.** PDFBox exposes the embedded program, which for most PDFs is
already a subset; if it is not, subset with the glyphs the page actually used. Budget 20–50 KB per face.
`Effra` appears in 1191 runs across the sample and would be the first face worth carrying.

**What to measure before and after.** Pick three documents that use `Effra` and fail `18_displacement`, run
one live Google round trip each with and without embedding, and compare `n_out` and the `dy` profile. If
embedding moves them, it is the construct; if it does not, the finding is that substitution is not the
residual and `18_displacement` really is geometry. **Either answer is worth the slot**, because 23 attempts
have been spent without establishing which.

---

## Gap 2 — a list is detected, then written as an indent. No `numbering.xml`.

### The measurement

    isListMarker()      exists, detects "1." "(a)" "iv" "•"
    p.indent            exists, holds nesting depth
    word/numbering.xml  0 references
    w:numId             0 references
    w:abstractNum       0 references
    DocxWriter:4596     if (p.indent > 0) → <w:ind w:left="p.indent * 420"/>

So a numbered list becomes a paragraph with a left indent. In Word that is not a list: it does not renumber,
it does not nest, it does not survive an edit, and Google Docs shows it as body text.

`38_list_markers` is a class in the table with **2 documents** — because the check measures whether the
marker text survived, not whether the list is a list. The real population is every document with a list in
it.

### How to close it

1. Emit `word/numbering.xml` with one `w:abstractNum` per list kind (bullet, decimal, lowerLetter,
   lowerRoman) and one `w:num` pointing at each.
2. Register it in `[Content_Types].xml` and `document.xml.rels`.
3. On a paragraph the engine already believes is a list item, write
   `<w:numPr><w:ilvl w:val="N"/><w:numId w:val="K"/></w:numPr>` and **drop the synthetic `w:ind`** — the
   numbering definition carries the indent.
4. Keep `w:ind` only for indentation that is not a list.

The detection already exists. This is writing, not inferring — which is why it is the cheapest of the three.

**What to measure.** `38_list_markers` should go from 2 documents to every document with a list, and the
pass condition should be "the paragraph carries a `w:numPr` whose `w:numId` resolves in `numbering.xml`",
not "the marker text is present".

---

## Gap 3 — footnotes and the outline are absent.

### The measurement

    w:footnote            0 references
    word/footnotes.xml    not written
    w:bookmarkStart       0 references
    w:fldSimple           0 references
    TOC                   0 references
    w:sdt                 0 references

A footnote marker becomes ordinary superscript body text and the note at the foot of the page becomes an
ordinary paragraph at the end of the body. In a 200-page document that is a structural loss: the note is no
longer attached to anything.

`52_outline` is the class that would catch the bookmark half.

### How to close it

1. **Pair the marker with the note.** A footnote is a small superscript run in the body whose number matches
   a short run at the foot of the same page, below the last body line and above the page furniture. The
   engine already finds the foot of the page for `44_header_footer`; the same geometry answers this.
2. Write `word/footnotes.xml` with one `w:footnote` per pair, register the part, and replace the body
   superscript with `<w:footnoteReference w:id="N"/>`.
3. **Outline.** Emit `<w:bookmarkStart w:name="_Toc..."/>` around every paragraph the engine already marks as
   a heading (`p.heading > 0`), and a `TOC` field at the front. The heading levels exist; this is bookkeeping.

This is the hardest of the three because the pairing is geometry, and it is the one that can wait.

---

## Gap 4 — a header is body text repeated on every page, not a header part.

### The measurement

    w:hdr             0 references
    w:ftr             0 references
    w:headerReference 0 references
    w:titlePg         0 references
    header1.xml       not written
    footer1.xml       not written

There is no notion of a repeating element anywhere in the engine — no `pageFurniture`, no `runningHead`, no
`repeat`. A page's top band and bottom band are read as ordinary paragraphs like any other, so a 200-page
report carries 200 literal copies of its own header.

`44_header_footer` is a class in the table, and it measures whether the band's text survived into the
`.docx` — not whether it became a header. So the structure is lost and the check does not look for it, the
same shape as gaps 1 and 2.

### Why it costs the user two things

**Completeness.** A header that is body text is not a header: it does not repeat, it does not survive an edit
on page 1, and it is not what the document says it is. If the user changes the company name, they change it
200 times.

**Editing.** In a real document the header is edited once and appears everywhere. Here the user must find
every copy, and the moment a paragraph is added the header drifts out of its band.

### How to close it

1. **Find the repeating lines.** A line is page furniture when the same text, at the same y band and the same
   x, appears on three or more pages. The engine already knows every line's x, y and text — this is a
   counting pass over the page list, not new geometry.
2. **Split them out.** Write `word/header1.xml` and `word/footer1.xml`, reference them from `w:sectPr` with
   `w:headerReference` / `w:footerReference`, and set `w:titlePg` where page 1 differs (most invoices and
   letters draw their first page differently).
3. **Take them out of the body**, and give the section a top and bottom margin that leaves room for the
   header and footer — otherwise the body text and the header will overlap.

**Page numbers are the interesting case.** A footer that says "Page 3" on page 3 is not repeating text, it is
a field. Emit `PAGE` and `NUMPAGES` fields where the digits are, so the number stays right when the document
is edited — a literal "3" becomes wrong the moment a page is inserted.

### What to measure

`44_header_footer` should ask whether the band element landed in a header part referenced from `w:sectPr`,
not whether its text is present. Before: every document with a header fails the structural question. After:
it passes, and the body gets shorter by one copy of the header per page.

---

## The order to take them

| | gap | documents affected | risk of the change | do it |
|---|---|---|---|---|
| 1 | font embedding | **199 of 213** | medium — binary payload, obfuscation | **first** |
| 2 | `numbering.xml` | every document with a list | low — pure writing | second |
| 3 | header/footer parts | every document with a header | medium — a counting pass and a margin | third |
| 4 | footnotes + outline | every document with a note | high — geometry pairing | fourth |

**Gaps 2 and 3 are the cheap ones and both are editing defects**, which is half the user's goal. Take them
when the class you are on has gone quiet, before spending another slot on a lead that has not moved.

**Gap 1 first, and not because it is the largest number — because it may be the answer to the class you are
already stuck on.** If embedding three `Effra` documents moves `18_displacement`, you have found the construct
behind 101 documents. If it does not, you have eliminated it, which is worth as much after 23 attempts.

---

## What was NOT done, and why

The agent did not touch the engine and did not add a check. Two reasons:

1. **`verify_google.py` is the instrument every number in this pipeline rests on.** Adding a 43rd check
   changes the catalogue, leaves every existing `gverify` result short of it, and forces a full re-measure.
   That is a blast radius the pipeline does not need while it is finally running.
2. **The engine is the fixer's to change**, by the standing arrangement.

What was done is the measurement above, in this file, and a pointer to it from `FIXER-BRIEF.md` so that a run
reading the brief meets it before it picks a class.
