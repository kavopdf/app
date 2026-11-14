#!/usr/bin/env python3
"""
verify_txt.py - does the .txt describe the same document as the source PDF?

WHY THIS EXISTS
  The pipeline measures the .docx path and nothing else. 59 checks compare the source
  PDF with the PDF Google exports from our .docx, and the .txt is never opened. So the
  fixer cannot improve it: a defect it cannot see is a defect it cannot fix, and the
  .txt could break outright without a single number moving.

  This is the second verifier. It reads the same source PDF, reads the .txt the engine
  wrote, and answers the four things a text file can actually carry:

      text accuracy   the same words, with nothing lost
      position        a line's x survives as its leading spaces
      symbols         the characters a PDF can carry, not just ASCII
      structure       every text line the page drew is still a line of the .txt
      encoding        the file is UTF-8 and carries no replacement character
      symbol counts   each symbol arrives as many times as the page drew it

  THE LAST TWO EXIST BECAUSE THE FIRST FIVE COULD NOT SEE A BROKEN FILE.
  TxtWriter.java:91 writes the bytes with
  clean.getBytes(StandardCharsets.UTF_8), so the .txt is declared UTF-8. This reader
  opens it with errors="replace", which means an invalid byte never raises: it becomes
  U+FFFD and every check then runs on the repaired string. Measured on the 211-document
  corpus, a .txt with one byte flipped out of its UTF-8 sequence still scores 5/5 on 159
  documents, and a .txt whose last multi-byte character is cut in half - a write that
  died one byte short - still scores 5/5 on 28 of the 137 documents that carry any
  non-ASCII at all. t06 is the assertion that closes that hole.

  And t03 compares SETS. A set cannot see a symbol the page drew five times and the
  .txt carries once: 38_faux_bold_italic_synthesised draws two em dashes and the .txt
  carries one, and t03 passes because the em dash is still in the set. t07 counts.

  The last one is a line count on both sides, not a row count against a line count.
  A .txt has no rows: TxtWriter writes one line per drawn text line, so eight cells
  drawn across one baseline arrive as eight lines. Counting baselines on the source
  side and lines on the .txt side measured two different objects and called the
  engine's own format an eightfold inflation.

  It writes nothing and changes nothing. The .docx path is measured by verify_google.py
  and is not touched by this file - a regression in one must not be able to hide behind
  a good score in the other.

WHAT IT DOES NOT MEASURE
  Fonts and colours. A .txt has neither, and a number for them would mean nothing.

USAGE
  python3 verify_txt.py <source.pdf> <output.txt>
  python3 verify_txt.py <source.pdf> <output.txt> --json out.json
  python3 verify_txt.py --list-checks

  Exit 0 every check passed, 1 at least one failed, 2 could not run.
"""
import json
import os
import re
import sys

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

CHECKS = ["t01_word_accuracy", "t02_position", "t03_symbols",
          "t04_structure", "t05_completeness",
          "t06_encoding", "t07_symbol_counts"]


def _words(s):
    return re.findall(r"\S+", s or "")


def _src_text(path):
    import fitz
    d = fitz.open(path)
    out = [pg.get_text() for pg in d]
    d.close()
    return "\n".join(out)


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


def compare(src_pdf, txt_path):
    """Every check, as {id: (source_value, txt_value, passed)}."""
    src_text = _src_text(src_pdf)
    runs = _src_runs(src_pdf)
    lines = _txt_lines(txt_path)
    txt_text = "\n".join(lines)
    c = {}

    # ---- t01 word accuracy -------------------------------------------------
    # Lost words only. Extra words are a different fault, and counting them here would
    # make one duplicated line look like a document that dropped text.
    from collections import Counter
    sw, tw = _words(src_text), _words(txt_text)
    if sw:
        lost = sum((Counter(sw) - Counter(tw)).values())
        acc = round(100.0 * (len(sw) - lost) / len(sw), 1)
        c["t01_word_accuracy"] = (100, acc, acc >= MIN_ACCURACY)
    else:
        c["t01_word_accuracy"] = (0, 100, True)

    # ---- t02 position ------------------------------------------------------
    # Self-calibrating: the character width is derived from the pairs themselves, so the
    # check does not depend on the engine's choice of ruler, only on whether one ruler
    # explains every line. Columns that drift will not fit one.
    by_text = {}
    for ln in lines:
        by_text.setdefault(ln.strip(), []).append(_column(ln))
    pairs = []
    for x, _y, t in runs:
        key = t.strip()
        if by_text.get(key):
            pairs.append((x, by_text[key].pop(0)))
    if len(pairs) >= 3:
        ratios = sorted(x / col for x, col in pairs if col > 0)
        if ratios:
            mid = ratios[len(ratios) // 2]
            good = sum(1 for x, col in pairs if abs(col - round(x / mid)) <= POS_TOLERANCE)
            share = round(100.0 * good / len(pairs))
            c["t02_position"] = (len(pairs), share, share >= 90)
        else:
            c["t02_position"] = (len(pairs), 0, False)
    else:
        # Too few lines to fit a ruler. Nothing to say, so say nothing rather than fail
        # a document for being short.
        c["t02_position"] = (len(pairs), 100, True)

    # ---- t03 symbols -------------------------------------------------------
    # Only characters above ASCII. A symbol the source had and the .txt lost is a real
    # loss; a symbol the .txt gained is not this check's business.
    s_sym = {ch for ch in src_text if ord(ch) > 127}
    t_sym = {ch for ch in txt_text if ord(ch) > 127}
    missing = s_sym - t_sym
    c["t03_symbols"] = (len(s_sym), len(s_sym) - len(missing), not missing)

    # ---- t04 structure -----------------------------------------------------
    # The same object on both sides: a drawn text line of the page against a line of the
    # .txt. A row of the page is not that object - a row is a y, and the .txt carries no
    # y for a table row, so a row cannot be counted in it at all.
    # An empty .txt is t05's finding, not this one: a file with no lines has no structure
    # to compare, and restating the emptiness here would put two ids on one fault.
    src_lines = _src_line_count(src_pdf)
    if src_lines and lines:
        drift = round(len(lines) / src_lines, 2)
        c["t04_structure"] = (src_lines, len(lines),
                              1.0 / MAX_LINE_DRIFT <= drift <= MAX_LINE_DRIFT)
    else:
        c["t04_structure"] = (src_lines, len(lines), True)

    # ---- t05 completeness --------------------------------------------------
    # A PDF with text must produce a .txt with text. A scanned page whose OCR ran and
    # produced nothing is a defect, not an empty document.
    c["t05_completeness"] = (len(src_text.strip()), len(txt_text.strip()),
                             len(src_text.strip()) == 0 or len(txt_text.strip()) > 0)

    # ---- t06 encoding ------------------------------------------------------
    # The writer declares UTF-8 and this reader reads UTF-8, so the two agree and the
    # file must decode. Three ways a .txt arrives unreadable while t01-t05 stay green:
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
    raw, enc_err = _txt_bytes(txt_path)
    fffd = txt_text.count("\ufffd")
    bom = raw.startswith(b"\xef\xbb\xbf")
    c["t06_encoding"] = (0, fffd + (1 if bom else 0) + (1 if enc_err else 0),
                         not enc_err and fffd == 0 and not bom)

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
    # The invented direction runs on every document, including the 74 of 211 whose
    # source carries no non-ASCII at all and on which t03 is vacuous: a .txt cannot
    # invent a character and be right. The reported pair is the total on each side, so
    # the row carries the size of the question - source=6 txt=5 is a loss of one,
    # source=0 txt=0 is a document with nothing to lose.
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
                              not short and not invented)
    return c


def all_check_ids():
    return list(CHECKS)


def main(argv):
    if "--list-checks" in argv:
        for cid in CHECKS:
            print(cid)
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

    failed = [c for c in CHECKS if not checks[c][2]]
    passed = len(CHECKS) - len(failed)
    print("%-40s %d/%d %s" % (os.path.basename(txt)[:40], passed, len(CHECKS),
                              "PASS" if not failed else "FAIL"))
    for cid in failed:
        s, t, _ = checks[cid]
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
                "passed": passed,
                "total": len(CHECKS),
                "ok": not failed,
                "failed": sorted(failed),
                "checks": {cid: {"source": checks[cid][0], "render": checks[cid][1],
                                 "ok": bool(checks[cid][2])} for cid in CHECKS},
                # Which checks asked their question on THIS document. A source count of
                # 0 is a document that could not exercise the check, and a score that
                # does not say how many of those it contains is a score with a silent
                # denominator - the fault t03 has carried on 74 of 211.
                "applicability": {
                    "t03_symbols": checks["t03_symbols"][0] > 0,
                    "t07_symbol_counts_counted": checks["t07_symbol_counts"][0] > 0,
                },
            }, f, indent=2)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
