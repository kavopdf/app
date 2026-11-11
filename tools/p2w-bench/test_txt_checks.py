#!/usr/bin/env python3
"""
test_txt_checks.py - does each check in verify_txt.py actually fire, and does it stay
quiet when it should?

WHY THIS EXISTS
  The same reason test_checks.py exists for the .docx verifier: a check that never fails
  is decoration, and a check that always fails condemns every document and hides the real
  defect behind its noise. Both look identical in a report.

  Every case changes exactly ONE thing, so a check that fires can only be the check that
  was meant to fire. The base document is three single-cell rows at three different x -
  one row, one line, one cell - which is the one shape every check agrees on. Each case
  then breaks one of them.

RUN
  python3 test_txt_checks.py          summary
  python3 test_txt_checks.py -v       every case
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_txt

# The base page: three rows, one cell each, at three x. One row is one line and one
# cell, so structure, position and accuracy all hold at once and a case can break one.
BASE = [[(72, "Alpha")], [(140, "Beta")], [(220, "Gamma")]]

# Two cells on one baseline: one row, one line. A writer that gives each cell its own
# line turns three rows into six.
TWO_CELL = [[(72, "Alpha"), (300, "100")],
            [(72, "Beta"), (300, "200")],
            [(72, "Gamma"), (300, "300")]]
CHARW = 6.6   # the ruler the txt below is padded with


def _pdf(path, rows):
    import fitz
    d = fitz.open()
    p = d.new_page(width=595, height=842)
    for ri, row in enumerate(rows):
        y = 100 + ri * 24
        for x, t in row:
            p.insert_text((x, y), t, fontsize=11)
    d.save(path)
    d.close()
    return path


def _render(rows, gap=False):
    """The txt a correct writer would produce: one line per row, indented to its x."""
    out = []
    for row in rows:
        line = ""
        for x, t in row:
            col = round(x / CHARW)
            line = line.ljust(col) + t
        out.append(line)
    return "\n".join(out) + "\n"


def _cells_on_own_lines(rows):
    """Every cell on its own line, still at its own column. The indentation is right
    and the words are right; only the row has been broken up."""
    out = []
    for row in rows:
        for x, t in row:
            out.append(" " * round(x / CHARW) + t)
    return "\n".join(out) + "\n"


def _run(rows, txt_content):
    d = tempfile.mkdtemp(prefix="txtchk-")
    src = _pdf(os.path.join(d, "s.pdf"), rows)
    t = os.path.join(d, "s.txt")
    with open(t, "w", encoding="utf-8") as f:
        f.write(txt_content)
    checks = verify_txt.compare(src, t)
    got = [cid for cid in verify_txt.all_check_ids() if not checks[cid][2]]
    for f in os.listdir(d):
        os.unlink(os.path.join(d, f))
    os.rmdir(d)
    return got


def cases():
    good = _render(BASE)
    out = [
        ("a correct txt passes every check", BASE, good, []),

        # t01 - one word gone, everything else untouched
        ("a lost word fires only t01", BASE, good.replace("Gamma\n", ""),
         ["t01_word_accuracy"]),

        # t02 - the words and the rows are all there, the indentation is not
        ("a flat txt fires only t02", BASE,
         "Alpha\nBeta\nGamma\n", ["t02_position"]),

        # t04 - two cells per row, and the txt gives each cell its own line. The
        # words and their indentation are both right; only the row is gone.
        ("a row split across lines fires only t04", TWO_CELL,
         _cells_on_own_lines(TWO_CELL), ["t04_structure"]),

        # t05 - nothing at all
        ("an empty txt fires t05 and t01", BASE, "", ["t01_word_accuracy",
                                                     "t05_completeness"]),
    ]

    # t03 - a symbol the source carries and the txt drops. Degree and multiply are in
    # the base-14 fonts, so the source PDF really does carry them.
    sym = [[(72, "Temp 40\u00b0C")], [(140, "12 \u00d7 4")], [(220, "Gamma")]]
    sym_good = _render(sym)
    out.append(("symbols kept pass t03", sym, sym_good, []))
    # The degree sign removed, not replaced by a word: the text keeps its word count,
    # so only the symbol check can fire.
    # Removing the degree sign changes "40°C" into "40C", so the word itself is gone
    # too. Both checks are right to fire and the case says so rather than pretending a
    # lost symbol can leave the word untouched.
    out.append(("a lost symbol fires t03 and the word with it", sym,
                sym_good.replace("\u00b0", ""), ["t01_word_accuracy", "t03_symbols"]))
    return out


def main(argv):
    verbose = "-v" in argv
    ok = 0
    fails = []
    all_cases = cases()
    for name, rows, txt, expected in all_cases:
        got = _run(rows, txt)
        good = sorted(got) == sorted(expected)
        if good:
            ok += 1
        else:
            fails.append(name)
        if verbose or not good:
            print("  %-40s %-5s %s" % (name, "PASS" if good else "FAIL",
                                       "" if good else "expected %s, got %s" % (expected, got)))
    print()
    print("%d/%d cases behave as claimed" % (ok, len(all_cases)))
    if fails:
        print()
        print("A check that does not fire on a case built to make it fire is broken.")
        print("A check that fires on a case built to pass marks correct output wrong.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
