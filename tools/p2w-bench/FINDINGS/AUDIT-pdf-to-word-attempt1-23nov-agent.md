# PDF-to-Word — deep audit, attempt 1 of 5

Agent, 23 Nov 2026. Read-only: nothing in the engine was changed. Every item below was checked in the code
before it was written here; the line numbers are where the evidence is.

Scope of this attempt: error handling and silent failure in the three writers. Attempts 2-5 will cover the
conversion pipeline, the checks themselves, the measurement path, and the app layer.

---

## A1 — `DocxWriter` has no error handling at all, and its two `catch` blocks are for debug sinks

`DocxWriter.java` is **7,671 lines** and produces the entire `.docx`. It contains two `catch` clauses:

    4272:  } catch (Exception e) { CENSUS_OUT = null; }
    4281:  } catch (Exception e) { TRACE_OUT = null; }

Both null out an optional debug output. **Neither guards document writing.** There is no try/catch around the
XML generation, the ZIP assembly, or the relationship parts.

So any `RuntimeException` during a `.docx` write — a null part, an index past a runs array, a malformed colour
string — leaves `write()` with no partial file, no message saying which part failed, and no record that it
happened. The caller sees an exception with whatever stack the JVM gives it.

**Why this matters more than it looks:** the docs side is the weak half of this tool (30 of 190 clean). When a
document comes out wrong, this is the code that produced it, and it cannot say what it did. The `.txt` writer is
899 lines and has *zero* catch blocks — see A2.

**Not verified:** what the app layer does with the exception. `DocxWriter.write` has no caller inside the engine
package; `ReadingOrder.java` documents the intended chain (`PdfToWord.convert` → `DocxWriter.write`) only in a
comment. Finding the real caller is attempt 2.

---

## A2 — `PdfToWord.writeTxt` is a bare passthrough and `TxtWriter` catches nothing

    public static void writeTxt(Result result, File out) throws IOException {
        TxtWriter.write(result, out);
    }

`TxtWriter` has **0 `catch` blocks in 899 lines**. Its only guard is a null check on entry:

    60:  if (result == null || out == null) throw new IOException("nothing to write");

Everything after that — table geometry, column detection, the indent arithmetic — runs unguarded. A
`NumberFormatException` or an out-of-bounds index inside the padding logic propagates out of `writeTxt` as a
`RuntimeException`, which the method's `throws IOException` signature does not even advertise to a caller.

**The asymmetry is the finding.** The `.txt` path is 93% clean and the `.docx` path is 16%. The clean path is the
one with no error handling; the weak path is the one with 10,016 lines and 40 catches. Whatever is protecting
`.txt` quality, it is not defensive code.

---

## A3 — the indent clamp is silent

    45:   private static final int MAX_INDENT = 400;
    769:  if (c > MAX_INDENT) return MAX_INDENT;

A line whose computed indent exceeds 400 is clamped to 400 and nothing records it. The comment says this is
"well past the width of any real page", so on a well-formed PDF it never fires — which is exactly why it is
worth flagging: if it *does* fire, the cause is a malformed coordinate, and the output silently carries a wrong
indent instead of saying so. A clamp is a decision the tool makes about the document; it should leave a trace.

---

## A4 — the `writeTxt` contract is documented wrongly

`PdfToWord.java`, above `writeTxt`:

> *"table rows as `cell | cell`"*

`TxtWriter` emits **no pipe characters anywhere** — `grep` for a pipe separator returns 0. Table rows are built
by padding with leading spaces (`int pad = column(lx, charW);` at line 534), which is what the Option A spec
asks for: rows on one line, columns aligned by spaces.

**The code is right and the comment is wrong.** Low severity on its own, but this comment is the first thing a
reader — human or agent — meets when looking for how tables are written, and it describes a format the tool does
not produce. It sent this audit looking for a pipe-separated path that does not exist.

---

## What this attempt did NOT cover

Named so the next attempt does not repeat it:

- the conversion pipeline itself (`convert`, page loop, OCR path)
- the 23 page-count refusals — 11% of the corpus that is never scored
- the 42 checks: whether each measures what it says
- memory and time limits on a large document
- the app layer and the Android entry points
- `PdfEngine` (3,201 lines) and `PdfRepair` (2,723 lines)

---

## For the fixer

Each item above is a claim with a line number. **Verify before changing anything** — this audit read the code,
it did not run it. A1 and A2 are the ones with real blast radius: a writer that cannot report its own failure is
how a document arrives wrong with nothing in the log.
