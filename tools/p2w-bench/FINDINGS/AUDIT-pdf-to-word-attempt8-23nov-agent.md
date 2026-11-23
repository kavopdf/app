# PDF-to-Word — deep audit, attempt 8 of 10

Agent, 23 Nov 2026. Read-only on the engine; one small Java program was compiled in `/tmp` to test a claim
rather than assert it. Attempts 1-7 covered the writers' error handling, the page gate, the checks, the app layer,
the OCR interface, the page loop and cancellation. This one is `DocxWriter` as a body of code, starting with the
one function every character of the document passes through.

---

## H1 — `esc()` is thorough, and that is worth recording

`DocxWriter.esc` (line 7447) handles the five XML entities and the control-character case:

    case '&'  -> &amp;      case '<' -> &lt;       case '>'  -> &gt;
    case '"'  -> &quot;     case '\'' -> &apos;
    default   -> if (c < 0x20 && c != '\t' && c != '\n' && c != '\r') space; else c

The control-character line is the one that matters and is the one most writers forget: XML 1.0 forbids those
bytes outright, and a single U+0001 in the wrong place makes Word refuse the file. It is handled here, with the
three legal whitespace characters excepted. **No finding. Recorded because the rest of this attempt is about the
one case it does not handle.**

---

## H2 — an unpaired surrogate becomes `?`, silently. Proven, not assumed.

There is **no surrogate handling anywhere**: 0 occurrences of "surrogate" in `DocxWriter.java`, 0 in
`PdfToWord.java`. The parts are written with `getBytes(StandardCharsets.UTF_8)` (line 744).

So I compiled and ran the case rather than guessing what Java does:

    input  : "A" + U+D800 + "B"      (an unpaired high surrogate)
    utf-8  : 41 3F 42
    decodes: A?B

**0x3F is `?`.** Java's UTF-8 encoder substitutes the replacement byte for a code unit it cannot encode, and
`esc()` passes the surrogate through untouched, so nothing between the PDF and the file ever notices.

**Why this is reachable in this tool:** a PDF whose `ToUnicode` CMap is broken or partial is a common real-world
file — it is exactly what a bad font subset or a truncated embedding produces. PDFBox decodes what the CMap says,
and a wrong CMap yields a lone surrogate. The character then reaches `esc()`, survives it, and lands in the
document as a question mark.

**What the user sees:** a `?` where the PDF had a glyph. No warning, no count, nothing in the report. And a `?` is
a legal character, so `t03_symbols` and `t12_word_invention` have no reason to fire on it — **the substitution is
invisible to the checks by construction.**

---

## H3 — the control-character substitution is silent too

The same `esc()` replaces every control character with a space. That is the right behaviour — the alternative is
a file Word will not open — but nothing counts it. A page whose text layer is mostly control bytes (a broken
encoding, a damaged stream) converts to a page of spaces and looks, in every report this pipeline produces, like a
page that was simply short of text.

**H2 and H3 are the same defect with different replacement characters:** the writer makes a decision about the
document's content and does not record it. `Report` already carries `notes`; both belong there.

---

## What this attempt did NOT cover

- the remaining ~7,600 lines of `DocxWriter` as a body of code — only `esc`, the encoding and the package parts
  have been read
- `PdfRepair` and the seam that feeds a repaired file into the converter
- memory on a genuinely large document — **still unmeasured after eight attempts**, and this is now the oldest
  open item in the series
- the 47 Kotlin files outside the two activities

---

## For the fixer

**H2 is small and provable:** in `esc`, when a char is a surrogate, check whether it pairs with the next; if it
does not, substitute U+FFFD and add a note. U+FFFD is the correct character for "a byte sequence that could not
be decoded" — visibly a replacement rather than a real question mark, which is what `?` currently pretends to be.

**Do not silently drop it.** Dropping loses the fact that something was there; `?` currently hides that fact
behind a character that means something else.

**H3:** count the substitutions in `Report` so a document with many of them is visible before anyone tries to fix
its layout.

Verify before changing. H2 was proven by running Java 17 in this sandbox; H1 and H3 were read, not run.
