# Adversarial review: `recoverUndefinedCids()` (Identity-H / U+FFFD recovery)

Scope: the two hunks in `PdfEngine.diff` only. No corpus measurement, no build, no clone. Line
numbers below are the *new-file* lines computed from the hunk headers (`+1751,14`, `+2108,27`,
`+2548,57`) with the corresponding diff line in brackets, e.g. **PdfToWord.java:2593 [diff L98]**.

Two framing facts before the list:

* The patch is two independent behaviours behind one helper: a **writer** call
  (PdfToWord.java:2128–2131) and a **search-index** call (PdfEngine.java:1757–1761). They do not
  share preconditions, so risks below are tagged **[W]**, **[S]** or **[both]**.
* The rationale in the javadoc (PdfToWord.java:2552–2573) rests on three claims about
  pdfbox-android 2.0.27.0 internals (`PDFont.toUnicode` line 459, line 474,
  `PDType0Font.toUnicode` line 489). **None of that source is in the two files I was given**, so
  those citations are unverified here; the review treats them as assertions the next run should
  confirm, not as established fact. If any one of them is wrong, risks 5 and 7 get worse.

---

## 1. The premise "Identity-H ⇒ code is a character" is false; the patch's own measured codes prove it

**Line:** PdfToWord.java:2593 [diff L98] `sb.append((char) code);` — reached via the guard at
PdfToWord.java:2589 [diff L94]. Justified in the javadoc at PdfToWord.java:2566–2568 [diff L66–68].

**Why it bites.** In a Type0/Identity-* font the code is the **CID**, i.e. a glyph index in that
font's CID ordering — *not* a Unicode code point. CID = code point only when the producer happened
to build the subset so that the two coincide, which is the exception, not the rule. The javadoc
asserts the equation ("Identity-H says the code IS the character identifier, so the code is the
only answer") and then applies it unconditionally to every Identity-* font in 213 documents.

The patch's own evidence contradicts it. The measured CIDs are `<0123>/<0124>/<0126>/<0127>`
(diff L38–39). As Unicode those are `U+0123 ģ`, `U+0124 Ĥ`, `U+0126 Ħ`, `U+0127 ħ` — verified
locally with `unicodedata`: LATIN SMALL LETTER G WITH CEDILLA, LATIN CAPITAL LETTER H WITH
CIRCUMFLEX, LATIN CAPITAL LETTER H WITH STROKE, LATIN SMALL LETTER H WITH STROKE. They are not
ligatures and they are not characters a bank account-opening form draws. So on the *two documents
this patch is supposed to fix*, the 127 glyphs (diff L40) that currently arrive as U+FFFD will
become 127 occurrences of `ģ Ĥ Ħ ħ`. That is a silent wrong-text regression inside the fix's own
happy path — worse for a search index than a visible gap, because the output now looks like real
text.

**Document class.** Any document whose Type0/Identity-* font has a subset with CIDs above ~0x80
that are not Latin-1 — i.e. essentially every PDF with an embedded subset font and at least one
FFFD entry. High-CID subsets (Cyrillic, Devanagari, CJK, Indic, Greek) are the worst: CIDs land in
ranges that decode to arbitrary BMP letters.

**One-line test.** For each font touched, dump the pairs `(cid, toUnicode(cid))` for every non-FFFD
entry in the same CMap and count how many satisfy `toUnicode(cid).equals(String.valueOf((char)cid))`
— if that fraction is not ~1.0 for a given font, the code-as-character assumption is refuted for
that font and its FFFD entries must not be recovered.

---

## 2. One CID, one character: ligature expansion is impossible by construction, so the stated goal is not met

**Line:** PdfToWord.java:2583–2594 [diff L88–99] — the loop appends at most one `char` per code;
there is no branch that can emit two or three characters for one code.

**Why it bites.** The comment at PdfEngine.java:1755–1756 [diff L10–11] states the purpose: "a
search for a word the page draws as a ligature finds nothing, because the index would hold U+FFFD
where the page holds the glyph." A ligature is exactly the case that needs `ffi → "ffi"`. After the
patch, the index holds `ģ` (or whatever the CID decodes to) instead of U+FFFD: the word is still
unfindable, the gap is still there, and the text now *also* carries a wrong letter that will join
the neighbouring word (`Accoģnt`). The patch converts a detectable failure into an undetectable one
while claiming to fix it. A ligature that should expand also breaks the 1 glyph ↔ 1 char invariant
that the rest of the engine relies on (see risk 3).

**Document class.** Bank/insurance forms and any professionally typeset PDF with a subset font —
the exact class the patch targets. Also any document using `fi`/`fl`/`ff`/`ft` ligatures as real
CIDs.

**One-line test.** For every FFFD CID recovered, look the glyph up through
`CIDToGIDMap → descendant font's TrueType cmap` and check whether the GID has *no* single-codepoint
cmap entry but is reachable from a `liga`/`clig` GSUB rule — if so, that CID is a ligature and must
expand to a string, not a char.

---

## 3. The engine path and the writer path now disagree, and can change the index's char count

**Line:** PdfEngine.java:1757–1761 [diff L12–16], specifically `if (again != null) u = again;`
followed by `chars.add(u); pos.add(tp);` at PdfEngine.java:1762–1764 [diff L17–19].

**Why it bites.** Two distinct problems in four lines.

*(a) Divergence.* The writer reaches its `u` through `decodeThroughFont(tp, f0)` and `isJunk()`
(PdfToWord.java:2108–2110 [diff L25–27]) **before** the new block runs; the engine path has neither
— it starts from raw `tp.getUnicode()` and jumps straight to the code-as-character recovery. So for
any glyph where `decodeThroughFont` produces a good answer, the DOCX will contain that answer while
the search index contains `(char) code`. Search and document text disagree, which is precisely the
bug the comment claims to fix. And the writer's own policy is not applied to the new path either:
line 2110 [diff L26] guards with `!isJunk(again)`, line 2130 [diff L47] does **not** — a recovered
string of junk characters is accepted on one path and rejected on the other.

*(b) Char-count alignment.* `chars` and `pos` are parallel lists: one `TextPosition` is registered
against one string. The helper's output length is `codes.length`, not `tp.getUnicode().length()`
and not `1`. Any case where the original unicode was length ≠ `codes.length` (a multi-code
`TextPosition`, or a bfchar destination that is a multi-char string with FFFD embedded) silently
changes the number of searchable characters while `pos` still holds a single `TextPosition` with a
single advance. Every downstream offset/highlight computed from `pos` after that point on the page
shifts. Note the returned string is never checked against `tp.getWidth()`/`getWidthDirAdj()`, so a
1→N recovery puts N characters inside one glyph advance — in the writer that is `g.text = u` with
`g`'s width unchanged (PdfToWord.java:2132–2134 [diff L50–52]), i.e. a DOCX run wider than the space
the glyph occupied, and reflowed line breaks on a nine-page form.

**Document class.** Documents mixing a broken-ToUnicode font with any font that `decodeThroughFont`
handles (most real corpora), and any document where a form field's text is searched after export.

**One-line test.** On each affected page assert `chars` length equals the sum of per-`TextPosition`
expected lengths, and diff the searchable text of each document against its exported DOCX text —
any mismatch outside known-normalised whitespace is a regression.

---

## 4. The control-code guard leaves holes that produce invalid XML, lone surrogates and tofu

**Line:** PdfToWord.java:2589 [diff L94]
`if (code < 0x20 || (code >= 0x7F && code <= 0x9F) || code > 0xFFFF) {`

**Why it bites.** The guard covers C0, DEL+C1 and above-BMP. It does not cover:

| range | what lands in the DOCX | consequence |
|---|---|---|
| `0xD800–0xDFFF` | `(char) code` = **unpaired surrogate** | invalid UTF-16; verified locally that UTF-8 encoding of a lone surrogate yields `?`, and XML serialisation of the DOCX may emit a character Word rejects |
| `0xE000–0xF8FF` | private-use area | renders as tofu, unsearchable, breaks font fallback in Word |
| `0xFDD0–0xFDEF`, `0xFFFE`, `0xFFFF` | Unicode noncharacters | illegal in XML 1.0 — a DOCX that Word "repairs" or refuses |
| `0x2028`, `0x2029` | line/paragraph separator | injected line break in the middle of a word in the .txt half |
| `0xFEFF`, `0x200B–0x200F` | BOM / zero-width / bidi marks | invisible characters that corrupt search tokens and RTL layout |
| `0x20` exactly | space | a ligature glyph becomes a **word separator** — changes tokenisation and, in the .txt path, splits a word |

The javadoc's justification (PdfToWord.java:2570–2572 [diff L73–76]) is "a visible gap the reader can
see is better than a NUL it cannot" — a good instinct applied to the wrong list. CIDs in the PUA and
surrogate ranges are reachable because the code space is whatever the producer wrote, and the
`> 0xFFFF` clause is dead code for Identity-H anyway (2-byte codes can never exceed 0xFFFF), which
suggests the range analysis was done for a different code space than the one the guard admits.

**Document class.** Icon/dingbat/symbol Type0 fonts used for bullets, checkboxes and rules on
forms (PUA), and any font whose subset CIDs run past 0xD800 (large CJK/Indic subsets).

**One-line test.** After recovery, assert every produced `char` satisfies
`Character.isValidCodePoint` **and** `!Character.isSurrogate` **and** `ch >= 0x20` **and** is legal
in XML 1.0 (`ch == 0x9 || ch == 0xA || ch == 0xD || (ch >= 0x20 && ch <= 0xD7FF) || (ch >= 0xE000 && ch <= 0xFFFD)`),
then fail the document if any char is rejected.

---

## 5. The guard is per-`TextPosition`, so codes the CMap never named get invented too

**Line:** PdfToWord.java:2585–2587 [diff L90–92]:
`if (part != null && part.indexOf('\uFFFD') < 0) { sb.append(part); continue; }`

**Why it bites.** The invocation guard (PdfToWord.java:2128 [diff L45], PdfEngine.java:1757
[diff L12]) is "this *position* contains FFFD". Inside the helper, **every** code of that position is
re-decoded. Any code whose `font.toUnicode(code)` returns `null` — no CMap entry at all, which is the
normal PDFBox answer for an unmapped code — falls through to `sb.append((char) code)` at line 2593.
So the patch does not merely repair FFFD codes; once it is triggered on a position it substitutes
code-as-character for unmapped codes as well. `part == null` and `part == U+FFFD` are conflated into
one branch, although they are different statements ("the producer declined" vs "there is no
mapping"). The `part != null` re-append at line 2590 [diff L95] only saves the control-range case.

**Document class.** Fonts with a *partial* `/ToUnicode` (very common: 91 entries in a 300-glyph
subset per diff L62) used in a document that also has at least one FFFD entry — the second half of
the patch's own target document qualifies.

**One-line test.** Instrument the helper to log `(code, part == null, part == FFFD)` for every code
it rewrites; count the `part == null` cases — any non-zero count is over-recovery.

---

## 6. Documents that legitimately contain U+FFFD are destroyed

**Line:** PdfToWord.java:2128 [diff L45] and PdfEngine.java:1757 [diff L12] — the trigger is a bare
`u.indexOf('\uFFFD') >= 0` with no corroboration that the FFFD came from the CMap's bfchar
destination.

**Why it bites.** U+FFFD is a real, printable character. A document that *shows* U+FFFD on purpose —
a Unicode chart, a QA/test sheet for a PDF tool, a spec page, a "missing glyph" placeholder that the
producer encoded deliberately, a form label meaning "unknown" — has a font whose CMap maps a code to
FFFD by design. The patch rewrites that correct text into `(char) code`. Nothing in the trigger
distinguishes "producer could not name the glyph" from "producer named the glyph U+FFFD".

**Document class.** Documentation/spec PDFs, font sample sheets, test fixtures; also any document
whose text already contains FFFD from a *different* font, since the trigger is per-position and the
font check happens afterwards.

**One-line test.** Take the corpus documents whose extracted text contains U+FFFD adjacent to
readable text from the *same* font, and confirm each FFFD code is an entry whose bfchar destination
is literally `FFFD` and whose CID is not plausibly a real codepoint (e.g. it appears in a run of
otherwise-Latin text) — anything else must be left alone.

---

## 7. The guard is circular: it re-asks the same method that produced the FFFD

**Line:** PdfToWord.java:2584 [diff L89] `String part = font.toUnicode(code);`

**Why it bites.** `tp.getUnicode()` was itself produced by `font.toUnicode(...)` inside PDFBox's
stream engine. Calling `font.toUnicode(code)` again is not an independent oracle — it is the same
call. The helper therefore cannot tell apart the three ways a code reaches FFFD: (i) the CMap's
bfchar destination is FFFD (the intended case, asserted for Effra at diff L36–39); (ii) PDFBox's own
fallback synthesised FFFD; (iii) a ligature/embedded-CMap path in PDFBox returned FFFD. The javadoc
argues (ii) away for one font on one document ("PDFBox is not inventing the fallback", diff L63) and
then generalises it to 213 documents, and it does so by citing line numbers I cannot check from the
files provided. If (ii) or (iii) holds anywhere in the corpus, the recovery is applied to a code
PDFBox already tried and rejected, and the output is worse than the FFFD it replaced. Secondary
point: the re-call is also the only way a null-mapping code gets invented (risk 5) — the two failure
modes are the same line.

**Document class.** PDFs from producers that emit a truncated/odd ToUnicode and rely on PDFBox's
embedded-CMap fallback — scanner/OCR pipelines and older Acrobat/Distiller output.

**One-line test.** For each recovered code, read the font's ToUnicode CMap *directly* via
`PDType0Font.getToUnicodeCMap().lookup(code)` (not `toUnicode`) and assert it returns exactly
`"\uFFFD"`; if it returns `null` or something else, the FFFD was synthesised and recovery must not run.

---

## 8. Symbol/dingbat faces turn bullets and checkboxes into body text

**Line:** PdfToWord.java:2593 [diff L98], in combination with the `startsWith("Identity-")` gate at
PdfToWord.java:2579 [diff L84].

**Why it bites.** Icon fonts are Type0/Identity-H by construction and frequently carry no usable
ToUnicode (or an FFFD-filled one). The patch will decode every bullet, checkbox, arrow and rule as
`(char) cid`. In the DOCX that puts PUA or Latin-Extended characters where a drawing was, which
(a) defeats list/numbering detection in the writer, (b) puts junk into the .txt half where the code
was previously a gap the text layer already treated as a separator (diff L75–76), and (c) makes the
document's character count grow with decorative glyphs.

**Document class.** The bank forms themselves (checkbox/rule glyphs), questionnaires, any form with
a Symbol/Wingdings-style Type0 face.

**One-line test.** For every font the helper fires on, report `descendantFont.getBaseFont()` and the
fraction of its CMap entries that are FFFD; a font whose base name matches a known symbol/dingbat
face, or where the FFFD fraction exceeds ~20%, must be skipped.

---

## 9. Structural gaps in the gate itself

**Line:** PdfToWord.java:2577–2581 [diff L82–86], and 2597 [diff L102].

* **No font-type check.** The gate reads `/Encoding` off the raw COS dictionary (line 2577) but never
  asserts `font instanceof PDType0Font`. A simple Type1/TrueType font that happens to carry
  `/Encoding /Identity-H` (illegal but present in the wild) has 1-byte codes; `(char) code` then
  recovers Latin-1 garbage. Add `if (!(font instanceof PDType0Font)) return null;`.
* **`startsWith("Identity-")` is too loose and too tight at once.** It accepts `Identity-V`
  (vertical writing — the recovery is arguably fine but the reading order it lands in is not) and any
  vendor name beginning `Identity-`; and it *rejects* the common case of `/Encoding` being an
  **embedded CMap stream** (`enc instanceof COSName` fails at line 2578), which is a false negative —
  not a regression, but it means the corpus number the next run reports will understate how many
  documents have this defect. Compare the exact names `Identity-H`/`Identity-V`.
* **`catch (Throwable t)`** (line 2597) swallows `OutOfMemoryError`, `StackOverflowError` and any
  `NullPointerException` from a null `font.getCOSObject()`, converting a crash into a silent FFFD.
  Catch `IOException`/`RuntimeException` instead, and count the catches.
* **Cost.** The helper is called once per FFFD-bearing glyph and does a dictionary lookup plus one
  `toUnicode` per code, with no per-font cache. On a document where a whole font is FFFD-mapped that
  is tens of thousands of redundant lookups. Performance only, but it belongs in the same change.

**Document class.** Malformed/hand-built PDFs and large scanned documents.

**One-line test.** Log `font.getClass().getSimpleName()`, the exact `/Encoding` name, and the number
of helper invocations per document; assert every invocation is `PDType0Font` with `/Encoding` exactly
`Identity-H`, and that invocation count is bounded by the FFFD glyph count.

---

## Verdict

**Do not land it as written.** The mechanism is sound in shape — a ToUnicode that answers U+FFFD has
not answered, and Identity-* is the only family where the code is even a candidate answer — but the
central equation the patch relies on (`code == Unicode code point`) is false for the general case and,
on the patch's own measured evidence, false for the two documents it is meant to fix: CIDs
`0x0123–0x0127` decode to `ģ Ĥ Ħ ħ`, so the "fix" replaces 127 visible gaps on nine-page bank forms
with 127 wrong letters, and turns a detectable failure into an undetectable one. It also cannot
achieve its stated goal at all, because a single `char` per CID cannot expand a ligature, so the
search-for-a-ligature bug it was written for survives. Land it only with two named guards, both
required: **(a) a font-level consistency guard** — recover nothing for a given font unless that
font's own non-FFFD CMap entries corroborate `toUnicode(cid) == (char) cid` (and, better, resolve the
glyph through `CIDToGIDMap` + the descendant font's `cmap` and refuse when the GID has no single
codepoint, which is also the only correct answer for ligatures); and **(b) a character-validity
guard** replacing line 2589 — reject surrogates, noncharacters, private-use, U+2028/2029 and U+FEFF,
require XML-1.0 legality, and require the produced string's length to equal the position's expected
length so the `chars`/`pos` index stays aligned. With (a) and (b) plus `instanceof PDType0Font`,
exact `Identity-H`/`Identity-V` matching, a per-code rather than per-position trigger, and the same
`isJunk` precedence in `PdfEngine` that the writer already applies, this becomes a defensible
narrow fix; without them it is a corpus-wide silent-corruption change. Given that a regression on any
of 213 documents is defined as failure, the honest expectation for the patch as written is
*multiple* regressions, and the two target documents are among them.

## Open questions (could not be resolved from the two files provided)

1. Whether `decodeThroughFont` and `isJunk` exist and what they do — I can only see their call sites
   at PdfToWord.java:2108–2110 [diff L25–27], not their bodies.
2. Whether anything downstream keys on U+FFFD (e.g. a "font is broken, take another path" branch, or
   an OCR fallback). Not visible in the diff.
3. Whether `chars`/`pos` in `PdfEngine` are consumed strictly in parallel and how offsets are derived
   from `pos` — the consumer of those lists is outside the diff.
4. The actual pdfbox-android 2.0.27.0 source for `PDFont.toUnicode` (lines 459/474) and
   `PDType0Font.toUnicode` (line 489). Not provided and not fetched, per the read-and-reason
   constraint; risks 5 and 7 are conditional on those citations being accurate.
5. What the Effra glyphs at CIDs 0x0123/0x0124/0x0126/0x0127 actually draw. If they are genuinely
   ligatures, risk 2 is confirmed; if they are something else, the target documents have an
   additional problem the patch does not name.
