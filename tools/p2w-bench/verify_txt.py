#!/usr/bin/env python3
"""
verify_txt.py - does the .txt describe the same document as the source PDF?

WHY THIS EXISTS
  The pipeline measures the .docx path and nothing else. 59 checks compare the source
  PDF with the PDF Google exports from our .docx, and the .txt is never opened. So the
  fixer cannot improve it: a defect it cannot see is a defect it cannot fix, and the
  .txt could break outright without a single number moving.

  This is the second verifier. It reads the same source PDF, reads the .txt the engine
  wrote, and answers the things a text file can actually carry:

      text accuracy   the same words, with nothing lost
      position        a line's x survives as its leading spaces
      symbols         the characters a PDF can carry, not just ASCII
      structure       every text line the page drew is still a line of the .txt
      encoding        the file is UTF-8 and carries no replacement character
      symbol counts   each symbol arrives as many times as the page drew it
      line order      the lines arrive in the order the page drew them
      page furniture  one copy of each running head per page it belongs to
      page complete   every page contributes a line
      page breaks     N pages carry N-1 U+000C separators
      word invention  no word the source never drew
      amount columns  money columns stay right-aligned

CONSOLIDATION - 2026-11-15
  Six independent improvements were measured and clean and none of them could land: five
  of them had each claimed the name t08 and all six edited the same three places. This
  file is the one coherent verifier they became, and the order below is the order the
  measurements said they must be applied in:

      1. the two rebuilds   t03_symbols and t06_encoding now read GLYPH TRUTH, and both
                            of them rewrite _src_text(), which three of the additive
                            checks read. Rebuilds first, or the additive checks read a
                            source side that is about to change under them.
      2. t11_page_breaks    adds no line to any .txt; it changes no existing line, so it
                            cannot move any other check's number.
      3. t09_page_furniture
      4. t10_page_completeness
      5. t08_line_order     (was five different checks all called t08; it is the one
                            that becomes the line-order check)
      6. t12_word_invention
      7. t13_amount_columns

  Ids are unique and are not reused: t08_line_order, t09_page_furniture,
  t10_page_completeness, t11_page_breaks, t12_word_invention, t13_amount_columns.

  Two decisions taken before the consolidation, applied here:
    * t05_completeness is RETIRED. Three agents measured it subsumed by t01 - it fails
      0 of 211 documents and it passes a file that carries one word of eighty. It was
      not deleted from history, it is gone from CHECKS, and it no longer pads the
      denominator with a check that cannot fail.
    * t04_structure is DEMOTED, not deleted. It changes verdict on 0 of 844 mutants, so
      it cannot be the primary structure check; t08_line_order is. t04 keeps the one
      question nothing else asks (a ratio of lines), and its result is reported as a
      check and not as the verdict.

  THE DENOMINATOR MOVED, AND THAT IS THE POINT. The old universe was 211 documents x 7
  checks = 1477, of which t03 and t07 were vacuous on 74 documents each - 148 of those
  1477 were checks that judged nothing. Every JSON now carries "applicable" beside
  "total" and every check carries its own "applicable" flag, so a check that judges 19
  documents cannot read like one that judges 211.

THE SOURCE SIDE IS GLYPH TRUTH
  t03 and t06 used to ask their question of page.get_text(), which is the PDF's
  DECLARATION - a /ToUnicode map if there is one, otherwise the /Encoding. A declaration
  is a claim about the glyphs and a claim can be wrong; when it is, the symbol checks are
  the ones that go quiet, because they are the ones whose whole subject is a character
  the declaration did not mention. The rebuild walks the page content and each widget's
  selected appearance stream, reads /BaseFont and /Encoding from the font dictionary, and
  decodes a standard symbol face through the published Annex D table for that face,
  ignoring the declaration. See the note above glyph_truth() for its measured scope on
  this corpus, which is narrower than the rebuild deserves and is stated rather than
  implied.

WHAT IT DOES NOT MEASURE
  Fonts and colours. A .txt has neither, and a number for them would mean nothing.

  The row-per-line format. Whether a table row should arrive as one line or as one line
  per cell is a separate format change with its own ratchet consequence, and this file
  keeps the current format's answer (one line per drawn line).

USAGE
  python3 verify_txt.py <source.pdf> <output.txt>
  python3 verify_txt.py <source.pdf> <output.txt> --json out.json
  python3 verify_txt.py --list-checks

  Exit 0 every applicable check passed, 1 at least one failed, 2 could not run.
"""
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Adobe's published standard encodings, Annex D of PDF 32000-1, as code -> Unicode.
# ---------------------------------------------------------------------------
# Generated from the published table (reportlab's _fontdata_enc_symbol, which IS that
# table) resolved through the Adobe Glyph List, then embedded here so a measurement run
# needs nothing installed that the pod might not have. 0 means the code is unassigned.
#
# ZapfDingbats is absent on purpose: its glyph names are a1..a191, they are not in the
# Adobe Glyph List, and nothing shipped in this environment carries the mapping. A
# ZapfDingbats span therefore falls back to its declaration and is counted as an
# undeclared face rather than decoded through a table guessed at from memory.

SYMBOL_ENCODING = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0x0020, 0x0021, 0x2200, 0x0023, 0x2203, 0x0025, 0x0026, 0x220B,
    0x0028, 0x0029, 0x2217, 0x002B, 0x002C, 0x2212, 0x002E, 0x002F,
    0x0030, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035, 0x0036, 0x0037,
    0x0038, 0x0039, 0x003A, 0x003B, 0x003C, 0x003D, 0x003E, 0x003F,
    0x2245, 0x0391, 0x0392, 0x03A7, 0x2206, 0x0395, 0x03A6, 0x0393,
    0x0397, 0x0399, 0x03D1, 0x039A, 0x039B, 0x039C, 0x039D, 0x039F,
    0x03A0, 0x0398, 0x03A1, 0x03A3, 0x03A4, 0x03A5, 0x03C2, 0x2126,
    0x039E, 0x03A8, 0x0396, 0x005B, 0x2234, 0x005D, 0x22A5, 0x005F,
    0xF8E5, 0x03B1, 0x03B2, 0x03C7, 0x03B4, 0x03B5, 0x03C6, 0x03B3,
    0x03B7, 0x03B9, 0x03D5, 0x03BA, 0x03BB, 0x00B5, 0x03BD, 0x03BF,
    0x03C0, 0x03B8, 0x03C1, 0x03C3, 0x03C4, 0x03C5, 0x03D6, 0x03C9,
    0x03BE, 0x03C8, 0x03B6, 0x007B, 0x007C, 0x007D, 0x223C, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0x20AC, 0x03D2, 0x2032, 0x2264, 0x2044, 0x221E, 0x0192, 0x2663,
    0x2666, 0x2665, 0x2660, 0x2194, 0x2190, 0x2191, 0x2192, 0x2193,
    0x00B0, 0x00B1, 0x2033, 0x2265, 0x00D7, 0x221D, 0x2202, 0x2022,
    0x00F7, 0x2260, 0x2261, 0x2248, 0x2026, 0xF8E6, 0xF8E7, 0x21B5,
    0x2135, 0x2111, 0x211C, 0x2118, 0x2297, 0x2295, 0x2205, 0x2229,
    0x222A, 0x2283, 0x2287, 0x2284, 0x2282, 0x2286, 0x2208, 0x2209,
    0x2220, 0x2207, 0xF6DA, 0xF6D9, 0xF6DB, 0x220F, 0x221A, 0x22C5,
    0x00AC, 0x2227, 0x2228, 0x21D4, 0x21D0, 0x21D1, 0x21D2, 0x21D3,
    0x25CA, 0x2329, 0xF8E8, 0xF8E9, 0xF8EA, 0x2211, 0xF8EB, 0xF8EC,
    0xF8ED, 0xF8EE, 0xF8EF, 0xF8F0, 0xF8F1, 0xF8F2, 0xF8F3, 0xF8F4,
    0, 0x232A, 0x222B, 0x2320, 0xF8F5, 0x2321, 0xF8F6, 0xF8F7,
    0xF8F8, 0xF8F9, 0xF8FA, 0xF8FB, 0xF8FC, 0xF8FD, 0xF8FE, 0,
]

# ---------------------------------------------------------------------------
# The rest of this file
# ---------------------------------------------------------------------------

# How far a line's leading spaces may sit from where its x says it should be. One
# character of slack absorbs the rounding in x/charW without hiding a shifted column.
POS_TOLERANCE = 2

# A page that drew N text lines should arrive as N lines of the .txt, because that is
# what TxtWriter writes: one line per paragraph line, and one line per table cell
# (appendTable - "every line the PDF drew stays a line of its own"). The ratio is
# therefore expected to be exactly 1, and this is only the room the engine's own model
# needs to split or join a drawn line: appendTable splits a cell on "\n", so a cell the
# model re-wrapped arrives as two lines from one drawn line, and a paragraph the model
# joins from several columns arrives as one line from two or more. Measured on the
# densest real document to hand (350_question_paper, 104 drawn lines -> 112 txt lines)
# that drift is 8 %. 1.5 is half again either way - six times the drift actually
# observed - and still catches the fault this check exists for: twenty rows glued onto
# one line is a ratio of 0.02.
MAX_LINE_DRIFT = 1.5

# Words that survive, as a share of the source's words.
MIN_ACCURACY = 98.0

# Where a running head or a page number lives: the top and bottom band of the page, as
# a share of page height. Furniture outside these bands is not furniture - a heading
# that happens to repeat on three pages is a heading.
FURNITURE_BAND = 0.12

# An element has to repeat on this many pages before it is furniture. Two pages is a
# coincidence, and on a two-page document every repeated line would qualify.
FURNITURE_MIN_PAGES = 3

# The page separator the .txt format carries: one U+000C between consecutive pages, so a
# document of N pages carries N-1 of them.
PAGE_BREAK = "\u000c"

# t12 is gated on CHARACTERS, not words, and this is the number. A document of a dozen
# characters - a stamp, a page number on its own - cannot distinguish a word the writer
# invented from a word the source drew, because every token in it is unique and the
# comparison has no population. 200 characters is the smallest size at which the corpus
# has a document whose .txt is faithful to the last word, so the gate is measured rather
# than chosen: below it, this check abstains and says so.
WORD_INVENTION_MIN_CHARS = 200

# An amount column needs this many rows before it is a column rather than three numbers
# that happen to share an edge.
AMOUNT_MIN_ROWS = 3

# An amount, anchored at the end of a line. It must carry a two-decimal tail, which is
# what separates a money column from a column of years, counts or page numbers: "2024"
# at the end of a line is not an amount and must not be aligned like one. Both western
# grouping (1,234,567.89) and Indian grouping (12,34,567.89) are accepted, because the
# corpus is Indian and a lakh separator is not a malformed thousand separator.
AMOUNT_RE = re.compile(
    r"(?:[\u20b9$\u20ac\u00a3\u00a5]\s*)?"
    r"(?:\d{1,3}(?:,\d{3})+|\d{1,2}(?:,\d{2})+,\d{3}|\d+)"
    r"\.\d{2}$")

# The checks, in the order they run. t05_completeness is absent on purpose: three
# independent measurements found it subsumed by t01 (it fails 0 of 211 documents and
# passes a file that carries one word of eighty), so it was retired rather than left in
# to pad the denominator. t04_structure is present but demoted - it changes verdict on 0
# of 844 mutants, so it cannot be the primary structure check and t08_line_order is.
CHECKS = ["t01_word_accuracy", "t02_position", "t03_symbols",
          "t04_structure",
          "t06_encoding", "t07_symbol_counts",
          "t08_line_order", "t09_page_furniture", "t10_page_completeness",
          "t11_page_breaks", "t12_word_invention", "t13_amount_columns"]

# What each check is, for --list-checks and for anyone reading a JSON a year from now.
ABOUT = {
    "t01_word_accuracy": "the source's words survive, 98 % of them",
    "t02_position": "a line's x survives as its leading spaces",
    "t03_symbols": "every character the page DRAWS survives, read from the glyphs",
    "t04_structure": "line count against drawn-line count (demoted, not primary)",
    "t06_encoding": "the bytes decode as the UTF-8 the writer declares",
    "t07_symbol_counts": "each symbol arrives as many times as the page drew it",
    "t08_line_order": "lines arrive in the order the page drew them",
    "t09_page_furniture": "one copy of each running head per page it belongs to",
    "t10_page_completeness": "every page of the source contributes a line",
    "t11_page_breaks": "N pages carry N-1 U+000C separators",
    "t12_word_invention": "the .txt carries no word the source never drew",
    "t13_amount_columns": "amount columns stay right-aligned",
}


# The glyph-truth statistics of the last compare(), for the JSON. Kept beside the
# function that fills it rather than returned, so compare()'s contract stays the one
# every caller and test already uses: {id: (source, txt, passed, applicable)}.
_LAST_TRUTH = {}


def _words(s):
    return re.findall(r"\S+", s or "")


def _strip_punct(w):
    """A word with its surrounding punctuation removed, lowercased.

    The comparison t12 makes is about WORDS, and a writer that moves a comma from the
    end of one token to the start of the next has not invented anything. Case is folded
    for the same reason: a heading set in caps on the page and in sentence case in the
    .txt is a different fault, and t01 already owns it.
    """
    return w.strip(".,;:!?()[]{}\"'\u201c\u201d\u2018\u2019\u00ab\u00bb-").lower()


# ---------------------------------------------------------------------------
# GLYPH TRUTH - the source side, rebuilt
# ---------------------------------------------------------------------------
# t03 and t06 used to ask their question of page.get_text(), which is the PDF's
# DECLARATION: a /ToUnicode map if the file has one, and otherwise the /Encoding. A
# declaration is a claim about the glyphs, and a claim can be wrong. When it is, every
# check downstream inherits the error, and the symbol checks are the ones that go quiet:
# a page that draws a degree sign through a Symbol face whose encoding is declared as
# WinAnsi declares "40C" and draws "40°C", so t03 sees no symbol, judges nothing, and
# reports a clean sheet on a document it never examined.
#
# The rebuild reads the truth instead of the claim:
#
#   * walk the page's content - every span of every glyph, and every widget's selected
#     appearance stream, which is where a filled form's text lives and where
#     get_text() does not look;
#   * read /BaseFont and /Encoding from the font dictionary itself;
#   * when the face is a standard symbol face, decode the code through the published
#     Annex D table for that face, IGNORING the declaration entirely;
#   * otherwise the declaration stands, because for a single-byte encoding the encoding
#     IS the mapping and there is nothing further to read.
#
# MEASURED SCOPE, and it is narrower than the rebuild deserves. On the 211-document
# corpus this changes no character: no document uses a Symbol or ZapfDingbats face, the
# only single-byte fonts are the non-embedded base-14 Type1 faces whose /Encoding and
# declaration already agree, and the Type0 subsets carry stripped cmaps and no glyph
# names, so gid -> Unicode is not recoverable for them at all. The rebuild is therefore
# exercised by the fixture in test_txt_checks.py (a Symbol face declared WinAnsi, which
# the declaration reads as "a b g" and the glyphs read as alpha beta gamma) and by no
# corpus document. That is stated here rather than implied by a green number.
#
# ZapfDingbats is not decoded. Its glyph names are a1..a191, they are not in the Adobe
# Glyph List, and the mapping is not recoverable from anything shipped in this
# environment, so a ZapfDingbats span falls back to its declaration and is counted in
# glyphs_undeclared_face rather than silently guessed at.

# Adobe's published Symbol encoding, Annex D, as code -> Unicode. Generated from the
# published table (reportlab's _fontdata_enc_symbol, which is that table) and the Adobe
# Glyph List, then embedded so this file has no dependency that a measurement run might
# not have installed.
SYMBOL_FACES = ("symbol",)
ZAPF_FACES = ("zapfdingbats",)


def _annex_d(basefont):
    """The Annex D table for a standard symbol face, or None.

    The subset prefix (ABCDEF+Symbol) is stripped: a subset of Symbol is still Symbol,
    and its encoding is still the one Annex D publishes for that face.
    """
    if not basefont:
        return None
    face = re.sub(r"^[A-Z]{6}\+", "", basefont).strip().lower()
    face = re.sub(r"[^a-z]", "", face)
    if face in SYMBOL_FACES or face.startswith("symbol"):
        return SYMBOL_ENCODING
    # ZapfDingbats deliberately not decoded - see the note above.
    return None


def _single_byte_code(ch, encoding):
    """The code a declared character stood for, under a single-byte encoding.

    The glyph walk gives (unicode, gid) per glyph, and gid is a glyph index, not the code
    the content stream used: for the base-14 faces the two differ. The code is what
    Annex D is indexed by, so it has to be recovered, and it is recovered from the
    encoding the font declares - which is the one thing about the declaration that is
    still read, because /Encoding is a statement about CODES and the claim under test is
    about GLYPHS.
    """
    if not ch:
        return None
    codec = {"winansiencoding": "cp1252",
             "macromanencoding": "mac_roman",
             "standardencoding": "latin-1",
             "pdfdocencoding": "latin-1"}.get((encoding or "").strip("/").lower())
    if not codec:
        return None
    try:
        b = ch.encode(codec)
    except (UnicodeEncodeError, LookupError):
        return None
    return b[0] if len(b) == 1 else None


def _font_facts(doc, xref):
    """(basefont, encoding) read from the font dictionary, not from the page's claim."""
    def get(key):
        try:
            kind, val = doc.xref_get_key(xref, key)
        except Exception:
            return ""
        return val if kind in ("name", "string") else ""
    return get("BaseFont"), get("Encoding")


def _ap_stream_text(doc, widget_xref):
    """The text a widget's selected appearance stream draws.

    A filled form field's value is in its appearance stream, not in the page content, and
    get_text() does not read it. The stream carries its own /Resources and its own font,
    so its /BaseFont and /Encoding are read the same way the page's are.
    """
    try:
        kind, ap = doc.xref_get_key(widget_xref, "AP")
    except Exception:
        return ""
    if kind != "dict":
        return ""
    m = re.search(r"/N\s+(\d+)\s+0\s+R", ap or "")
    if not m:
        return ""
    try:
        raw = doc.xref_stream(int(m.group(1)))
    except Exception:
        return ""
    if not raw:
        return ""
    body = raw.decode("latin-1")
    # The stream's own font dictionary: /Resources << /Font << /F1 12 0 R >> >>.
    face = None
    enc = ""
    fm = re.search(r"/Font\s*<<\s*/([A-Za-z0-9]+)\s+(\d+)\s+0\s+R", body)
    if fm:
        face, enc = _font_facts(doc, int(fm.group(2)))
    table = _annex_d(face)
    out = []
    for lit in re.findall(r"\((?:\\.|[^\\()])*\)", body):
        s = _pdf_string_unescape(lit[1:-1])
        for ch in s:
            code = _single_byte_code(ch, enc)
            if table is not None and code is not None and table[code]:
                out.append(chr(table[code]))
            else:
                out.append(ch)
        out.append(" ")
    return "".join(out)


def _pdf_string_unescape(s):
    """The literal-string escapes of PDF 32000-1 7.3.4.2, enough of them to read text."""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        i += 1
        if i >= len(s):
            break
        e = s[i]
        i += 1
        if e in "nrtbf":
            out.append({"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}[e])
        elif e in "()\\":
            out.append(e)
        elif e.isdigit():
            oct_digits = e
            while i < len(s) and len(oct_digits) < 3 and s[i].isdigit():
                oct_digits += s[i]
                i += 1
            out.append(chr(int(oct_digits, 8) & 0xFF))
        elif e == "\n":
            pass
        else:
            out.append(e)
    return "".join(out)


def glyph_truth(path):
    """(text, stats) - the characters the pages DRAW, read from the glyphs.

    stats carries what the rebuild actually got to look at, because a source side that
    could not read a font must not look like a source side that read it and found
    nothing:
        glyphs          characters walked in page content
        declared        characters the declaration supplied (no truth available)
        from_glyphs     characters the Annex D table supplied INSTEAD of the declaration
        widget_glyphs   characters recovered from widget appearance streams
        undeclared_face faces with no table to decode through, by name
    """
    import fitz
    stats = {"glyphs": 0, "declared": 0, "from_glyphs": 0, "widget_glyphs": 0,
             "undeclared_face": [], "structure_fallback": 0}
    d = fitz.open(path)
    pages = []
    try:
        for pg in d:
            pno = pg.number
            fonts = {}
            try:
                for f in d.get_page_fonts(pno):
                    fonts[f[4]] = f
            except Exception:
                pass
            # (resource name -> (basefont, encoding)) read from the dictionary itself.
            facts = {}
            for name, f in fonts.items():
                got = _font_facts(d, f[0])
                # Keyed by the resource name AND by the base font, because a span's
                # "font" is whichever of the two the extractor decided to report, and a
                # lookup that knows only one of them silently finds no table at all -
                # which is how a rebuild like this one passes its own review and decodes
                # nothing.
                facts[name] = got
                base = got[0] or f[3] or ""
                facts[base] = got
                facts[base.lstrip("/")] = got
                facts[re.sub(r"^[A-Z]{6}\+", "", base.lstrip("/"))] = got
            buf = []
            try:
                trace = pg.get_texttrace()
            except Exception:
                trace = []
            try:
                declared_page = pg.get_text()
            except Exception:
                declared_page = ""
            # THE LAYOUT IS THE DECLARATION'S; ONLY THE CHARACTERS ARE THE GLYPHS'.
            #
            # A span's declared text and its glyph-decoded text are the same length - one
            # character per glyph - so each span's text can be located in the page's own
            # text and replaced in place. That keeps every newline, every space and every
            # line break exactly as the declaration had them, which is what stops this
            # rebuild from moving t01: a reconstruction that re-derives the layout can
            # glue two spans and hand t01 a smaller document, and the difference then
            # reads as lost words. Substitution cannot do that. A span whose declared
            # characters cannot be located, or which carries an undefined character the
            # declaration omitted, is left alone and counted.
            out = []
            cursor = 0
            for span in trace:
                base, enc = facts.get((span.get("font") or "").lstrip("/"), ("", ""))
                table = _annex_d(base)
                if table is None and base:
                    face = re.sub(r"^[A-Z]{6}\+", "", base)
                    if re.search(r"dingbat", face, re.I):
                        if face not in stats["undeclared_face"]:
                            stats["undeclared_face"].append(face)
                chars = span.get("chars", ())
                stats["glyphs"] += len(chars)
                stext = "".join(chr(c[0]) for c in chars if c[0])
                if not stext or len(stext) != len(chars):
                    # An undefined character in the span: its declared text is not the
                    # same length as its glyphs, so there is nothing to align against.
                    stats["declared"] += len(chars)
                    continue
                # Forward only. A document that draws a line twice - faux bold is
                # exactly that - has the same span text more than once, and a search
                # that falls back to offset 0 finds the FIRST copy again, appends the
                # decoded text ahead of the cursor and duplicates the line. A span that
                # is not ahead of the cursor is left as the declaration had it.
                idx = declared_page.find(stext, cursor)
                if idx < 0:
                    stats["declared"] += len(chars)
                    continue
                decoded = []
                for ch in chars:
                    ucs = ch[0]
                    d_ch = chr(ucs) if ucs else ""
                    got = d_ch
                    if table is not None:
                        code = _single_byte_code(d_ch, enc)
                        if code is not None and table[code]:
                            got = chr(table[code])
                    decoded.append(got)
                out.append(declared_page[cursor:idx])
                out.append("".join(decoded))
                stats["from_glyphs"] += sum(1 for a, b in zip(decoded, stext) if a != b)
                stats["declared"] += sum(1 for a, b in zip(decoded, stext) if a == b)
                cursor = idx + len(stext)
            out.append(declared_page[cursor:])
            walked = "".join(out)
            # Widget appearance streams: the filled values get_text() never reads.
            try:
                widgets = list(pg.widgets())
            except Exception:
                widgets = []
            for w in widgets:
                t = _ap_stream_text(d, w.xref)
                if t.strip():
                    stats["widget_glyphs"] += len(t)
                    walked += "\n" + t
            pages.append(walked)
    finally:
        d.close()
    return "\n".join(pages), stats


def _src_text(path):
    """The source text, from glyph truth.

    Order here is content order, not reading order. Every consumer of this string asks a
    multiset question - which words, which characters, how many of each - and none of
    them asks where a word sat, so re-sorting it would buy nothing and cost the one
    property this rebuild exists for: that the characters are the ones drawn.
    """
    return glyph_truth(path)[0]


def _src_runs(path):
    """(x, y, text) for every non-empty span, in page order."""
    import fitz
    d = fitz.open(path)
    runs = []
    for pg in d:
        for blk in pg.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                for sp in ln.get("spans", []):
                    t = sp.get("text", "")
                    if t.strip():
                        runs.append((sp["bbox"][0], sp["bbox"][1], t))
    d.close()
    return runs


def _src_line_count(path):
    """How many text lines the page drew - the object the .txt writes one line each.

    A drawn line, not a baseline. Eight cells drawn across one baseline are eight lines
    here and eight lines in the .txt, so counting baselines instead would read a
    faithful transcription as eight times too many lines.
    """
    import fitz
    d = fitz.open(path)
    n = 0
    for pg in d:
        for blk in pg.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                if "".join(sp.get("text", "") for sp in ln.get("spans", [])).strip():
                    n += 1
    d.close()
    return n


def _src_pages(path):
    """One record per page: its drawn lines, in order, with x and the page's height.

    This is the source model the four structure checks share - line order, furniture,
    page completeness and page breaks all ask a question of "which page, which line,
    where". Building it once is also what stops the four of them from disagreeing about
    what a page is.
    """
    import fitz
    d = fitz.open(path)
    pages = []
    for pg in d:
        # The same glyph substitution the text side gets, applied to the drawn lines.
        # Without it a page whose Symbol face is declared as WinAnsi has line text "a b g"
        # while the .txt correctly carries alpha beta gamma, and every structure check
        # then reports the page as missing from a .txt that transcribed it perfectly. The
        # rebuild has to reach the line model too, or it only moves half the source side.
        subs = []
        try:
            fonts = {f[4]: f for f in d.get_page_fonts(pg.number)}
            facts = {}
            for name, f in fonts.items():
                got = _font_facts(d, f[0])
                facts[name] = got
                base = got[0] or f[3] or ""
                facts[base] = got
                facts[base.lstrip("/")] = got
                facts[re.sub(r"^[A-Z]{6}\+", "", base.lstrip("/"))] = got
            for span in pg.get_texttrace():
                base, enc = facts.get((span.get("font") or "").lstrip("/"), ("", ""))
                table = _annex_d(base)
                chars = span.get("chars", ())
                stext = "".join(chr(c[0]) for c in chars if c[0])
                if table is None or not stext or len(stext) != len(chars):
                    continue
                dec = []
                for ch in chars:
                    d_ch = chr(ch[0]) if ch[0] else ""
                    got = d_ch
                    code = _single_byte_code(d_ch, enc)
                    if code is not None and table[code]:
                        got = chr(table[code])
                    dec.append(got)
                dec = "".join(dec)
                if dec != stext:
                    subs.append((stext, dec))
        except Exception:
            subs = []
        lines = []
        for blk in pg.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                t = "".join(sp.get("text", "") for sp in ln.get("spans", []))
                if not t.strip():
                    continue
                x0, y0, x1, y1 = ln["bbox"]
                for _a, _b in subs:
                    if _a in t:
                        t = t.replace(_a, _b)
                lines.append({"text": t.strip(), "x": x0, "y": y0,
                              "right": x1, "size": ln["spans"][0]["size"]
                              if ln.get("spans") else 10.0,
                              # A line drawn on a slanted or vertical baseline has no
                              # reading order to preserve: its "next line down" is a
                              # different place on the page. The order checks skip it
                              # rather than assert an order the page never had.
                              "upright": tuple(ln.get("dir", (1, 0))) == (1, 0)})
        pages.append({"number": pg.number, "height": pg.rect.height,
                      "width": pg.rect.width, "lines": lines})
    d.close()
    return pages


def _txt_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f if l.strip()]


def _txt_bytes(path):
    """(bytes, strict decode error or "") - what the reader above threw away.

    _txt_lines decodes with errors="replace" and is left exactly as it was, because
    every number t01-t05 has ever reported came through it and changing the reader
    would move those numbers without the engine changing. This is the same file read
    again, strictly, for the one check that asks whether the bytes were readable.
    """
    with open(path, "rb") as f:
        raw = f.read()
    try:
        raw.decode("utf-8")
        return raw, ""
    except UnicodeDecodeError as e:
        return raw, "%s at byte %d" % (e.reason, e.start)


def _column(line):
    return len(line) - len(line.lstrip(" "))


def _ruler(runs, lines):
    """Characters per point, fitted from the (x, column) pairs themselves.

    t02 calibrates the ruler and t08 needs the same one: line order is a question about
    (text, column) pairs, and a column is only comparable between the two sides if both
    are read with the same ruler. Returns None when there is nothing to fit.
    """
    by_text = {}
    for ln in lines:
        by_text.setdefault(ln.strip(), []).append(_column(ln))
    pairs = []
    for x, _y, t in runs:
        key = t.strip()
        if by_text.get(key):
            pairs.append((x, by_text[key].pop(0)))
    ratios = sorted(x / col for x, col in pairs if col > 0)
    if not ratios:
        return None, pairs
    return ratios[len(ratios) // 2], pairs


def _furniture_key(text):
    """A furniture element's identity, with its counter folded out.

    A running head that reads "Page 3" on page 3 and "Page 4" on page 4 is ONE element
    that belongs on both pages, not two elements of one copy each. Digits are therefore
    normalised to "#": the check is that the element appears once per page it belongs to,
    and a page number that appears once is exactly right.
    """
    return re.sub(r"\d+", "#", " ".join(text.split()))


def _amount_at_end(line):
    """(start, end) of the amount a line ends with, or None."""
    m = AMOUNT_RE.search(line)
    return (m.start(), m.end()) if m else None


def compare(src_pdf, txt_path):
    """Every check, as {id: (source_value, txt_value, passed, applicable)}."""
    truth_text, truth_stats = glyph_truth(src_pdf)
    _LAST_TRUTH.clear()
    _LAST_TRUTH.update(truth_stats)
    src_text = truth_text
    runs = _src_runs(src_pdf)
    lines = _txt_lines(txt_path)
    txt_text = "\n".join(lines)
    c = {}

    # ---- t01 word accuracy -------------------------------------------------
    # Lost words only. Extra words are a different fault, and counting them here would
    # make one duplicated line look like a document that dropped text. t12 owns them.
    from collections import Counter
    sw, tw = _words(src_text), _words(txt_text)
    if sw:
        lost = sum((Counter(sw) - Counter(tw)).values())
        acc = round(100.0 * (len(sw) - lost) / len(sw), 1)
        c["t01_word_accuracy"] = (100, acc, acc >= MIN_ACCURACY, True)
    else:
        c["t01_word_accuracy"] = (0, 100, True, False)

    # ---- t02 position ------------------------------------------------------
    # Self-calibrating: the character width is derived from the pairs themselves, so the
    # check does not depend on the engine's choice of ruler, only on whether one ruler
    # explains every line. Columns that drift will not fit one.
    mid, pairs = _ruler(runs, lines)
    if len(pairs) >= 3:
        if mid:
            good = sum(1 for x, col in pairs
                       if abs(col - round(x / mid)) <= POS_TOLERANCE)
            share = round(100.0 * good / len(pairs))
            c["t02_position"] = (len(pairs), share, share >= 90, True)
        else:
            # Enough pairs to judge and not one of them at a positive column: every line
            # of the .txt is flat against the margin. That is not a document too short to
            # judge, it is a document whose indentation is gone, and the original check
            # failed it here. Refactoring this into an abstain would have turned the one
            # fault t02 exists for into a silent pass.
            c["t02_position"] = (len(pairs), 0, False, True)
    else:
        # Too few lines to fit a ruler. Nothing to say, so say nothing rather than fail
        # a document for being short.
        c["t02_position"] = (len(pairs), 100, True, False)

    # ---- t03 symbols -------------------------------------------------------
    # Only characters above ASCII, and now only the ones the page DRAWS: the set comes
    # from glyph truth, so a symbol the declaration hid is a symbol this check can see.
    # A symbol the source had and the .txt lost is a real loss; a symbol the .txt gained
    # is not this check's business - t07 counts both directions.
    s_sym = {ch for ch in src_text if ord(ch) > 127}
    t_sym = {ch for ch in txt_text if ord(ch) > 127}
    missing = s_sym - t_sym
    c["t03_symbols"] = (len(s_sym), len(s_sym) - len(missing), not missing,
                        len(s_sym) > 0)

    # ---- t04 structure -----------------------------------------------------
    # DEMOTED. It stays because it is the only check that asks a ratio question, and a
    # ratio catches the one collapse nothing else does - twenty rows glued onto one line
    # with every word and every column intact. But it changes verdict on 0 of 844
    # mutants, so it is not the primary structure check and t08_line_order is. It is
    # reported as a check and not as the verdict.
    # An empty .txt is t10's finding, not this one: a file with no lines has no structure
    # to compare, and restating the emptiness here would put two ids on one fault.
    src_lines = _src_line_count(src_pdf)
    if src_lines and lines:
        drift = round(len(lines) / src_lines, 2)
        c["t04_structure"] = (src_lines, len(lines),
                              1.0 / MAX_LINE_DRIFT <= drift <= MAX_LINE_DRIFT, True)
    else:
        c["t04_structure"] = (src_lines, len(lines), True, False)

    # ---- t06 encoding ------------------------------------------------------
    # The writer declares UTF-8 and this reader reads UTF-8, so the two agree and the
    # file must decode. Three ways a .txt arrives unreadable while the other checks stay
    # green:
    #   * a byte of a multi-byte sequence is lost or flipped. The real production case
    #     is the tail of a truncated write - FileOutputStream is not atomic, and a
    #     process killed mid-write leaves a file that ends inside a character;
    #   * the engine is switched to the platform default charset, which on a non-UTF-8
    #     host writes cp1252 and still looks like text to every editor;
    #   * a BOM, legal UTF-8, which puts an invisible character at the head of the
    #     first line of every .txt.
    # U+FFFD is counted as well as the strict decode: a file that already carries one
    # has the same defect one layer up, where something put "cannot represent this"
    # into the string and the writer then wrote it faithfully.
    #
    # REBUILT: the source side used to be the constant 0, which made the check a claim
    # about the .txt alone wearing a comparison's clothes - it could not say what it had
    # read, so a run that never opened the PDF scored the same as one that did. The
    # source side is now the number of glyphs glyph truth walked, which is non-zero on
    # every document that has any text at all, and the defect count is unchanged. The
    # pair now reads "N characters were read from the glyphs; 0 of them arrived
    # undecodable".
    raw, enc_err = _txt_bytes(txt_path)
    fffd = txt_text.count("\ufffd")
    bom = raw.startswith(b"\xef\xbb\xbf")
    c["t06_encoding"] = (truth_stats["glyphs"],
                         fffd + (1 if bom else 0) + (1 if enc_err else 0),
                         not enc_err and fffd == 0 and not bom,
                         truth_stats["glyphs"] > 0)

    # ---- t07 symbol counts -------------------------------------------------
    # t03 asks whether a symbol survived AT ALL. This asks whether it survived as many
    # times as the page drew it, which is the question a reader of the .txt has: a price
    # list whose rupee sign appears once where the page printed it five times has lost
    # four of them, and a set cannot say so.
    #
    # Two directions, and they are different faults:
    #   lost      a source symbol carried fewer times than the page drew it;
    #   invented  a character in the .txt the page never drew - U+FFFD from a bad
    #             decode, mojibake from a charset mistake, a glyph from a fallback font.
    # The invented direction runs on every document, including the ones whose source
    # carries no non-ASCII at all and on which t03 is vacuous: a .txt cannot invent a
    # character and be right. The reported pair is the total on each side, so the row
    # carries the size of the question - source=6 txt=5 is a loss of one, source=0 txt=0
    # is a document with nothing to lose, and the applicability flag says which.
    s_cnt = {}
    for ch in src_text:
        if ord(ch) > 127:
            s_cnt[ch] = s_cnt.get(ch, 0) + 1
    t_cnt = {}
    for ch in txt_text:
        if ord(ch) > 127:
            t_cnt[ch] = t_cnt.get(ch, 0) + 1
    short = {ch: (n, t_cnt.get(ch, 0)) for ch, n in s_cnt.items()
             if t_cnt.get(ch, 0) < n}
    invented = sorted(ch for ch in t_cnt if ch not in s_cnt)
    c["t07_symbol_counts"] = (sum(s_cnt.values()), sum(t_cnt.values()),
                              not short and not invented,
                              bool(s_cnt) or bool(t_cnt))

    # ---- t08 line order ----------------------------------------------------
    # t02 asks whether a line sits at the right column. It does NOT ask whether the lines
    # arrive in the order the page drew them, because it indexes the .txt by text and
    # pops the first column it finds - a .txt that reads the page backwards satisfies
    # every (text, column) pair it contains.
    #
    # The predicate is the pair, not the text. A document with a repeated header, or a
    # table whose cells repeat ("Yes", "Yes", "Yes"), has the same text many times over,
    # so text alone cannot say which copy is out of place; text together with the column
    # it sits at can, and it is the same pair t02 already calibrated a ruler for.
    #
    # A pair the .txt does not contain at all is not this check's finding - a lost line
    # is t01's, and counting it here would put two ids on one fault. Only pairs that ARE
    # present are ordered, which is why source counts partners rather than source lines.
    src_seq = []
    for pg in _src_pages(src_pdf):
        for ln in pg["lines"]:
            if ln.get("upright", True):
                src_seq.append(ln)
    txt_seq = [(ln.strip(), _column(ln)) for ln in lines]
    # The COLUMN is what decides which pairs are comparable, not just what identifies a
    # line. A form that puts "Invoice Date" at column 11 and "Order Ref" at column 60 is
    # two columns, and a writer may read the right one before returning to the left - a
    # legitimate reading of the page, and the one the engine actually produces. Two lines
    # in the SAME column cannot swap: their vertical order IS the reading order. So the
    # predicate is (text, column) to identify a line and column to scope the comparison.
    #
    # MEASURED: this is what separates a real inversion from the 131 documents a strict
    # whole-page sequence called broken. See the consolidation note in the report.
    txt_seq = [(ln.strip(), _column(ln)) for ln in lines]
    txt_cols = {}
    for idx, (t, col) in enumerate(txt_seq):
        txt_cols.setdefault(t, set()).add(col)
    # A source line is a PARTNER when the .txt carries its text at a column the page's
    # own x agrees with. A line that is not a partner is not this check's finding - a
    # lost line is t01's, and counting it here would put two ids on one fault.
    # ORDER IS ONLY JUDGED WHERE A LINE'S IDENTITY IS UNIQUE.
    #
    # A document repeats lines - a table of "Yes", a running head, a 60-page report whose
    # every page carries the same footer - and the .txt has no page marker to say which
    # copy a line belongs to (t11 is the check that would give it one, and the engine does
    # not write it yet). With two copies on each side, "which copy moved" has no answer,
    # and a check that picks one anyway reports an inversion whenever a copy is merely
    # missing - which is t01's fault, not this one's. So a text that occurs more than once
    # on either side is not ordered by this check; it is counted in the abstention and
    # left to the checks that can see it.
    from collections import Counter as _C
    src_occ = _C(ln["text"] for ln in src_seq)
    txt_occ = _C(t for t, _c in txt_seq)
    # Compare order WITHIN a column, and only for lines whose identity is unique.
    #
    # Within a column, because two columns can legitimately be read in either order - a
    # form's right-hand column before returning to the left is what the engine does and
    # it is a fair reading of the page. Across the whole document, a writer that reads
    # column two first looks like 102 broken documents; measured, that is exactly what a
    # whole-page subsequence reported.
    #
    # Unique identity, because with two copies of a line on each side "which copy moved"
    # has no answer without a page marker in the .txt, and a check that picks one anyway
    # reports an inversion whenever a copy is merely missing - which is t01's fault.
    src_by_col = {}
    txt_by_col = {}
    for idx, (t, col) in enumerate(txt_seq):
        txt_by_col.setdefault(col, []).append(t)
    for ln in src_seq:
        if not mid:
            break
        if src_occ[ln["text"]] != 1 or txt_occ.get(ln["text"], 0) != 1:
            continue
        want = round(ln["x"] / mid)
        bucket = None
        for cand in range(want - POS_TOLERANCE, want + POS_TOLERANCE + 1):
            if cand in txt_by_col and ln["text"] in txt_by_col[cand]:
                bucket = cand
                break
        if bucket is None:
            continue
        src_by_col.setdefault(bucket, []).append(ln["text"])
    import difflib
    partners = 0
    in_order = 0
    for bucket, srcs in src_by_col.items():
        partners += len(srcs)
        # The longest common subsequence, not a cursor walked down the .txt. A cursor
        # advances past a line that is missing and every line after it reads as out of
        # order; a subsequence charges one line for one line.
        sm = difflib.SequenceMatcher(None, srcs, txt_by_col.get(bucket, []),
                                     autojunk=False)
        in_order += sum(b.size for b in sm.get_matching_blocks())
    if partners >= 3:
        c["t08_line_order"] = (partners, in_order, in_order == partners, True)
    else:
        c["t08_line_order"] = (partners, in_order, True, False)

    # ---- t09 page furniture ------------------------------------------------
    # A running head, a footer, a page number: an element that belongs to a page and
    # appears on it. The .txt owes one copy per page it belongs to - not one copy for the
    # document, which is what a writer that de-duplicates repeats produces, and not two,
    # which is what a writer that emits a header once per paragraph produces.
    #
    # Furniture is identified by POSITION as well as repetition: it lives in the top or
    # bottom band of the page. A heading that repeats on four pages is a heading, and
    # this check must not count it.
    pages = _src_pages(src_pdf)
    element_pages = {}
    for pg in pages:
        h = pg["height"] or 1.0
        for ln in pg["lines"]:
            if not (ln["y"] <= h * FURNITURE_BAND
                    or ln["y"] >= h * (1.0 - FURNITURE_BAND)):
                continue
            element_pages.setdefault(_furniture_key(ln["text"]), set()).add(pg["number"])
    elements = {k: v for k, v in element_pages.items()
                if len(v) >= FURNITURE_MIN_PAGES}
    txt_furniture = Counter(_furniture_key(ln.strip()) for ln in lines)
    owed = 0
    present = 0
    for key, pgs in elements.items():
        owed += len(pgs)
        present += min(txt_furniture.get(key, 0), len(pgs))
    c["t09_page_furniture"] = (owed, present, present == owed, owed > 0)

    # ---- t10 page completeness ---------------------------------------------
    # Every page of the source contributes at least one line to the .txt. This is the
    # only check that can see a whole page go missing from the middle of a long document:
    # the words that are left are all correct, the columns are all correct, and the line
    # count of a 60-page file that lost page 30 is 98 % of what it should be - inside
    # t04's drift and inside t01's 98 %. Dropping one page of sixty is a 1.7 % loss, so
    # the accuracy floor is below it by construction.
    #
    # A page that drew nothing owes nothing: an image-only page is not a page the writer
    # failed to write, and counting it would fail every scanned document in the corpus.
    # Contribution is measured in WORDS, not in whole lines. A writer that glues a page's
    # rows onto one line still contributed every word of that page, and a page-level
    # check that demands an exact line has no business calling that page missing - the
    # line structure is t04's question. Half the page's words is the bar: a dropped page
    # contributes none, a re-wrapped or re-ordered page contributes all of them.
    txt_word_count = Counter(_strip_punct(w) for w in _words(txt_text))
    # A page is identified by the words only IT carries. "of", "the" and "text" appear on
    # every page, so a share-of-words test calls a dropped page present whenever its
    # common words survive elsewhere - measured on a 60-page file whose pages share their
    # vocabulary, that test saw nothing at all. The words unique to one page are the ones
    # whose absence means that page is gone. A page that carries no unique word is judged
    # on its words as a whole, and that limitation is written down rather than hidden.
    page_words = []
    for pg in pages:
        page_words.append(set(_strip_punct(w) for w in
                              _words(" ".join(ln["text"] for ln in pg["lines"]))))
    df = Counter()
    for ws in page_words:
        for w in ws:
            df[w] += 1
    owed_pages = 0
    contributed = 0
    for pg, ws in zip(pages, page_words):
        if not pg["lines"]:
            continue
        owed_pages += 1
        if not ws:
            contributed += 1
            continue
        unique = [w for w in ws if df[w] == 1]
        if unique:
            # ONE of the page's own words is enough. The question is whether the page is
            # represented in the .txt at all; how much of it survived is t01's question,
            # and a bar of "most of them" here would fail a page for a word loss and put
            # two ids on one fault. A dropped page has none of its own words, because
            # they exist nowhere else.
            if any(txt_word_count.get(w, 0) for w in unique):
                contributed += 1
        else:
            pw = Counter(_strip_punct(w) for w in
                         _words(" ".join(ln["text"] for ln in pg["lines"])))
            present = sum(min(n, txt_word_count.get(w, 0)) for w, n in pw.items())
            if present * 2 >= sum(pw.values()):
                contributed += 1
    c["t10_page_completeness"] = (owed_pages, contributed,
                                  contributed == owed_pages, owed_pages > 0)

    # ---- t11 page breaks ---------------------------------------------------
    # A document of N pages carries N-1 U+000C separators. A .txt with no separator is
    # not a text file with a cosmetic gap: nothing in it says where a page ended, so a
    # reader cannot tell a two-column page from two pages, and every per-page question
    # has to be answered by re-reading the PDF.
    #
    # MEASURED TODAY: 0 of the 211 documents carry a separator, and 334 boundaries exist
    # to mark. The engine does not emit the mark and TxtWriter.java:86 strips it -
    # replaceAll("[\\u0000-\\u0008\\u000B\\u000C\\u000E-\\u001F]", " ") turns a form feed
    # into a space on the way out - so this check fails every multi-page document until
    # the writer lands the separator. It is a format check with a known-open finding, not
    # a check that is wrong: the ratchet must not count it as passing, and must not
    # silently drop it either.
    n_pages = len(pages)
    # Counted in the RAW file, not in _txt_lines: a separator that sits on a line of its
    # own strips to nothing and the reader above drops it, so counting there would report
    # zero marks on a file that carries every one of them.
    try:
        with open(txt_path, encoding="utf-8", errors="replace") as f:
            marks = f.read().count(PAGE_BREAK)
    except OSError:
        marks = txt_text.count(PAGE_BREAK)
    c["t11_page_breaks"] = (max(n_pages - 1, 0), marks,
                            marks == max(n_pages - 1, 0), n_pages > 1)

    # ---- t12 word invention ------------------------------------------------
    # t01 counts lost words. Nothing counted words the writer ADDED, and the corpus has a
    # real one: 38_faux_bold_italic_synthesised writes its subtitle twice, and every
    # check passes because a duplicated word is not a lost word, the line count moves by
    # one and the columns still fit.
    #
    # The gate is CHARACTERS, not words. A stamp that reads "PAID" has one word, and any
    # comparison over one word is a comparison over nothing: the first OCR difference
    # invents a word and the check condemns a document it cannot judge. Below the gate
    # this check abstains and says so, which is the whole point of publishing applicable
    # beside total.
    #
    # Case and surrounding punctuation are folded: moving a comma is not inventing a
    # word, and t01 already owns the case fault.
    invented_words = 0
    if len(src_text) >= WORD_INVENTION_MIN_CHARS:
        src_w = Counter(_strip_punct(w) for w in _words(src_text))
        txt_w = Counter(_strip_punct(w) for w in _words(txt_text))
        invented_words = sum((txt_w - src_w).values())
    c["t12_word_invention"] = (len(src_text), invented_words,
                               invented_words == 0,
                               len(src_text) >= WORD_INVENTION_MIN_CHARS)

    # ---- t13 amount columns ------------------------------------------------
    # A money column is right-aligned: the digits' RIGHT edge is what lines up, because
    # that is where the decimal point sits and that is how a reader compares 9.50 with
    # 1,240.00. A writer that pads on the left instead produces a column whose left edges
    # line up and whose decimal points do not, and every amount in it has to be re-read
    # digit by digit.
    #
    # Zero tolerance, because the fault is exact: two amounts in one column either end at
    # the same character column or they do not. A tolerance would let a column drift by
    # the amount that makes it unreadable.
    #
    # The unit is the COLUMN, not the line. One number at the end of a line is not a
    # column and cannot be mis-aligned; three or more sharing an edge is a column, and
    # the check reports how many columns there were and how many of them were
    # right-aligned.
    # The SOURCE decides which rows form a right-aligned amount column; the .txt is then
    # judged on exactly those rows. A column of amounts that the page itself left-aligns
    # is not a fault in the .txt, and a check that condemns it is a check measuring the
    # page, not the writer. This is the same split every other check here makes: the
    # source names the population, the .txt is what gets judged.
    src_cols = {}
    if mid:
        for pg in _src_pages(src_pdf):
            for ln in pg["lines"]:
                if not ln.get("upright", True):
                    continue
                span = _amount_at_end(ln["text"])
                if not span:
                    continue
                token = ln["text"][span[0]:span[1]]
                end_col = round(ln["x"] / mid) + span[1]
                src_cols.setdefault(end_col, []).append(token)
    right_src = {k: v for k, v in src_cols.items() if len(v) >= AMOUNT_MIN_ROWS}
    # Where each amount token ended in the .txt. Keyed by the TOKEN and not by the line,
    # because the source's line carries characters the .txt does not - the declaration
    # puts U+0000 in front of a table cell - and a lookup by line text then finds nothing
    # and reports every column as unaligned.
    txt_ends = {}
    for ln in lines:
        span = _amount_at_end(ln)
        if span:
            txt_ends.setdefault(ln[span[0]:span[1]], []).append(span[1])
    consumed = {}
    preserved = 0
    for end_col, tokens in right_src.items():
        ends = []
        ok = True
        for tok in tokens:
            got = txt_ends.get(tok)
            if not got:
                ok = False       # the amount is not in the .txt at all: t01's finding
                break
            ends.append(got[0])
        # Zero tolerance, WITHIN the column: the amounts either end at one character
        # column or they do not. The column's absolute offset is not compared to the
        # source's - the writer's ruler is t02's question and it is a constant shift, not
        # a mis-alignment. What is compared is whether the rows of one column still agree
        # with each other, which is the property a reader uses to compare 9.50 with
        # 1,240.00 and the property a left-padding writer destroys.
        if ok and len(set(ends)) == 1:
            preserved += 1
    c["t13_amount_columns"] = (len(right_src), preserved,
                               preserved == len(right_src), len(right_src) > 0)
    return c


def all_check_ids():
    return list(CHECKS)


def main(argv):
    if "--list-checks" in argv:
        for cid in CHECKS:
            print("%-24s %s" % (cid, ABOUT.get(cid, "")))
        return 0

    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print("usage: verify_txt.py <source.pdf> <output.txt> [--json out.json]")
        return 2
    src, txt = args[0], args[1]
    for p in (src, txt):
        if not os.path.isfile(p):
            print("could not run: no such file: %s" % p)
            return 2

    try:
        checks = compare(src, txt)
    except Exception as e:
        print("could not run: %s" % e)
        return 2

    judged = [cid for cid in CHECKS if checks[cid][3]]
    abstained = [cid for cid in CHECKS if not checks[cid][3]]
    failed = [cid for cid in judged if not checks[cid][2]]
    passed = len(judged) - len(failed)
    # The line says three numbers, not two. "10/12" would let a document that exercised
    # ten of twelve checks read exactly like one that exercised all twelve, and the
    # difference between those two documents is the whole of measurement integrity.
    print("%-40s %d/%d applicable, %d passed, %d abstained  %s"
          % (os.path.basename(txt)[:40], len(judged), len(CHECKS), passed,
             len(abstained), "PASS" if not failed else "FAIL"))
    for cid in failed:
        s, t, _ok, _a = checks[cid]
        print("    %-26s source=%-10s txt=%s" % (cid, s, t))

    if "--json" in argv:
        # The same shape verify_google.py writes, down to the key names. record.py,
        # ratchet.py and classify.py already read "checks" with a "source" and a
        # "render" in each, and a second dialect would mean every one of them needed
        # two code paths. "render" here is the .txt - the name is the one the chain
        # already speaks, not a claim about what kind of file it is.
        out = argv[argv.index("--json") + 1]
        # The run may be told to write into a directory it has not made yet - that is
        # exactly how the .txt half measured nothing for a whole day: restxt/ never existed,
        # so this line raised FileNotFoundError on every document and the half stayed empty.
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

        with open(out, "w", encoding="utf-8") as f:
            json.dump({
                "document": os.path.splitext(os.path.basename(src))[0],
                "source_file": src,
                "render_file": txt,
                "source": src,
                "render": txt,
                # "passed" counts the checks that JUDGED this document and passed.
                # "total" is the size of the verifier, not of this document's
                # examination, and "applicable" is the bridge between them. A document
                # whose checks abstained is not a document that passed them.
                "passed": passed,
                "applicable": len(judged),
                "total": len(CHECKS),
                "abstained": abstained,
                "ok": not failed,
                "failed": sorted(failed),
                "checks": {cid: {"source": checks[cid][0], "render": checks[cid][1],
                                 "ok": bool(checks[cid][2]),
                                 "applicable": bool(checks[cid][3])}
                           for cid in CHECKS},
                # Which checks asked their question on THIS document, and the glyph
                # truth the source side was read through. A source count of 0 is a
                # document that could not exercise the check, and a score that does not
                # say how many of those it contains is a score with a silent denominator.
                "applicability": {cid: bool(checks[cid][3]) for cid in CHECKS},
                "glyph_truth": dict(_LAST_TRUTH),
            }, f, indent=2)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
