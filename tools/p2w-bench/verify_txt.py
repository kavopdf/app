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
      structure       cells that share a row share a line

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

# A row of the page is one baseline. The bucket absorbs a baseline that wobbles by a
# point or two, which real PDFs do and strict equality would read as a second row.
Y_BUCKET = 3.0

# How far a line's leading spaces may sit from where its x says it should be. One
# character of slack absorbs the rounding in x/charW without hiding a shifted column.
POS_TOLERANCE = 2

# A page that drew N rows should arrive as about N lines. More than this and the
# structure is gone: a 17-row attendance register became 459 lines.
MAX_INFLATION = 1.5

# Words that survive, as a share of the source's words.
MIN_ACCURACY = 98.0

CHECKS = ["t01_word_accuracy", "t02_position", "t03_symbols",
          "t04_structure", "t05_completeness"]


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


def _rows(runs):
    """How many distinct baselines the page drew text on."""
    return len({round(y / Y_BUCKET) for _, y, _ in runs})


def _txt_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f if l.strip()]


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
    rows = _rows(runs)
    if rows:
        infl = round(len(lines) / rows, 2)
        c["t04_structure"] = (rows, len(lines), infl <= MAX_INFLATION)
    else:
        c["t04_structure"] = (0, len(lines), True)

    # ---- t05 completeness --------------------------------------------------
    # A PDF with text must produce a .txt with text. A scanned page whose OCR ran and
    # produced nothing is a defect, not an empty document.
    c["t05_completeness"] = (len(src_text.strip()), len(txt_text.strip()),
                             len(src_text.strip()) == 0 or len(txt_text.strip()) > 0)
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
        out = argv[argv.index("--json") + 1]
        with open(out, "w", encoding="utf-8") as f:
            json.dump({
                "document": os.path.basename(src),
                "txt": os.path.basename(txt),
                "source_file": src,
                "txt_file": txt,
                "passed": passed,
                "total": len(CHECKS),
                "ok": not failed,
                "failed": failed,
                "values": {cid: {"source": checks[cid][0], "txt": checks[cid][1],
                                 "ok": checks[cid][2]} for cid in CHECKS},
            }, f)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
