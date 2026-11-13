#!/usr/bin/env python3
"""
test_checks.py - does each check in verify_google.py actually fire?

WHY THIS EXISTS
  A check that never fails is not a check, it is decoration. A check that always
  fails is worse: it condemns every document and hides the real defect behind its
  noise. Both look identical in a report, and both were present in this file on
  10 Nov - five checks failed a document against itself, and nobody had noticed
  because nobody had ever run the verifier on two copies of the same file.

  So every check is tested here twice: once on a pair that differs in exactly the
  way it claims to measure, and once on a pair that differs in no relevant way.
  A check that cannot tell those two apart is broken regardless of how reasonable
  its code looks.

HOW IT WORKS
  Each case builds two small PDFs from scratch with PyMuPDF, so the difference is
  known exactly. compare() is called directly - no Drive, no network, no corpus.

  expect   the check must appear in `failed`
  allow    the check must NOT appear in `failed`
  either   the check must behave consistently but its verdict is not asserted
           (used where a synthetic document cannot isolate the property)

USAGE
  python3 tools/p2w-bench/test_checks.py            # run everything
  python3 tools/p2w-bench/test_checks.py -v         # show every case
"""
import os
import sys
import tempfile
import zipfile
import warnings

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import fitz
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)

import verify_google as V


# ---------------------------------------------------------------------------
# builders - every document is made from nothing, so its properties are exact
# ---------------------------------------------------------------------------
def page(doc, w=595, h=842):
    return doc.new_page(width=w, height=h)


def text(p, x, y, s, size=11, colour=(0, 0, 0), font="helv"):
    p.insert_text((x, y), s, fontsize=size, color=colour, fontname=font)


def table(p, x0, y0, cols, rows, cw=80, rh=24):
    """Draw a bordered grid - strokes only, no fill, like a real invoice table."""
    for r in range(rows + 1):
        y = y0 + r * rh
        p.draw_line((x0, y), (x0 + cols * cw, y), color=(0, 0, 0), width=1)
    for c in range(cols + 1):
        x = x0 + c * cw
        p.draw_line((x, y0), (x, y0 + rows * rh), color=(0, 0, 0), width=1)


def simple(path, body):
    doc = fitz.open()
    body(page(doc))
    doc.save(path)
    doc.close()


def docx_faces_doc(path, face):
    """A minimal .docx that declares one face on one run - all 53 reads."""
    NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    z.writestr("word/document.xml",
               '<w:document xmlns:w="%s"><w:body><w:p><w:r><w:rPr>'
               '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/></w:rPr>'
               '<w:t>Invoice number 12345</w:t></w:r></w:p></w:body></w:document>'
               % (NS, face, face, face))
    z.writestr("word/styles.xml",
               '<w:styles xmlns:w="%s"><w:docDefaults><w:rPrDefault><w:rPr>'
               '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr></w:rPrDefault>'
               '</w:docDefaults></w:styles>' % NS)
    z.close()



def run(verbose=False):
    tmp = tempfile.mkdtemp(prefix="chk-")
    results = []
    for case in cases():
        name, src_b, gd_b, expect, allow = case[:5]
        docx_face = case[5] if len(case) > 5 else None
        a = os.path.join(tmp, "a.pdf")
        b = os.path.join(tmp, "b.pdf")
        simple(a, src_b)
        simple(b, gd_b)
        docx = None
        if docx_face:
            docx = os.path.join(tmp, "a.docx")
            docx_faces_doc(docx, docx_face)
        try:
            res = V.compare(a, b, docx)
        except Exception as exc:
            results.append((name, "ERROR", "compare raised: %s" % exc, []))
            continue
        failed = set(res["failed"])
        ok = True
        why = []
        for e in expect:
            if e not in failed:
                ok = False
                why.append("%s did not fire" % e)
        if allow == "all":
            if failed:
                ok = False
                why.append("nothing should fail, but %s did" % ", ".join(sorted(failed)))
        results.append((name, "PASS" if ok else "FAIL", "; ".join(why), sorted(failed)))

    width = max(len(r[0]) for r in results) + 2
    bad = 0
    for name, verdict, why, failed in results:
        if verdict != "PASS":
            bad += 1
        if verbose or verdict != "PASS":
            print("%-*s %-6s %s" % (width, name, verdict, why))
    print("\n%d/%d cases behave as claimed" % (len(results) - bad, len(results)))
    if bad:
        print("\nA check that does not fire on a case built to make it fire is broken.")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(run(verbose="-v" in sys.argv))
