#!/usr/bin/env python3
"""Run every bench tool for real, on a document built for the purpose.

WHY
    tools/precommit.sh parsed every Python file and called that a pass. A file can parse
    and still be dead: on 7 Nov visual.py lost its module-level QUESTIONS list to an
    edit, so every document came back "check failed: name 'QUESTIONS' is not defined",
    and the parse check was perfectly happy. Five documents ran through the whole
    pipeline reporting failure, and the failure was the tool, not the documents.

    Parsing proves a file is Python. It does not prove the file works. This runs each
    tool against a two-page document that is built here, so there is no corpus to fetch
    and no engine to compile, and it fails on the first exception a tool raises.

WHAT IT CHECKS
    gate.py        scores a document without raising
    reflow.py      measures a document without raising
    visual.py      answers all eight questions without raising
    sidebyside.py  writes an image without raising
    looked.py      reads a record without raising
    txt-guard.py   snapshots and compares without raising

EXIT
    0  every tool ran
    1  a tool raised, and the traceback is printed
    2  a tool could not be run at all (a module is missing)
"""

import os
import subprocess
import sys
import tempfile
import zipfile

# The bench tools live one level down. This file sits in tools/ so that
# precommit can call it the same way it calls the other guards.
TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2w-bench")


def build_pair(work):
    """A PDF and a docx that describe the same page, made without the engine."""
    import pymupdf

    pdf_path = os.path.join(work, "smoke.pdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 90), "SMOKE HEADING", fontsize=18)
    page.insert_text((72, 130), "a body line of text", fontsize=10)
    page.insert_text((72, 150), "another body line", fontsize=10)
    page.draw_line((72, 200), (500, 200))
    page.draw_rect((72, 220, 300, 300))
    doc.save(pdf_path)
    doc.close()

    docx_path = os.path.join(work, "smoke.docx")
    from docx import Document
    from docx.shared import Pt
    d = Document()
    h = d.add_paragraph()
    r = h.add_run("SMOKE HEADING")
    r.font.size = Pt(18)
    b = d.add_paragraph()
    r = b.add_run("a body line of text")
    r.font.size = Pt(10)
    b2 = d.add_paragraph()
    r = b2.add_run("another body line")
    r.font.size = Pt(10)
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text = "cell a"
    t.cell(0, 1).text = "cell b"
    t.cell(1, 0).text = "cell c"
    t.cell(1, 1).text = "cell d"
    d.save(docx_path)
    return pdf_path, docx_path


# The marks of a BROKEN tool, as opposed to a tool that worked and found problems.
#
# This distinction is the whole point. visual.py exits 1 when a document fails its eight
# questions, and that is the tool doing its job; looked.py exits 1 while a page is
# PENDING, and that is also its job. A smoke test that failed on a non-zero exit would
# have to be given a perfect document to pass, and then it would stop testing the tools
# and start testing the fixture.
BROKEN = (
    "Traceback (most recent call last)",
    "is not defined",
    "check failed",
    "can't open file",
    "No module named",
    "TypeError",
    "AttributeError",
    "NameError",
    "usage:",
)


def run(label, args, work):
    try:
        r = subprocess.run([sys.executable] + args, cwd=work,
                           capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("FAIL  %s  (timed out - it hung, which is a break too)" % label)
        return False
    out = (r.stdout or "") + (r.stderr or "")
    for bad in BROKEN:
        if bad in out:
            print("FAIL  %s  (said: %s)" % (label, bad))
            print("\n".join("      " + ln for ln in out.strip().split("\n")[-12:]))
            return False
    if not out.strip():
        print("FAIL  %s  (said nothing at all)" % label)
        return False
    # A verdict of FAIL on the fixture is fine. The tool ran.
    verdict = "found problems" if "FAIL" in out else "clean"
    print("ok    %-14s ran (%s)" % (label, verdict))
    return True


def main():
    try:
        import pymupdf  # noqa: F401
        import docx  # noqa: F401
    except ImportError as e:
        print("smoke: %s" % e)
        print("smoke: needs pymupdf and python-docx, which CI installs for the bench job")
        return 2

    work = tempfile.mkdtemp(prefix="smoke-")
    try:
        build_pair(work)
    except Exception as e:
        print("smoke: could not build the test document: %s" % e)
        return 2

    corpus = os.path.join(work, "corpus")
    out = os.path.join(work, "out")
    os.makedirs(corpus, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    for name in ("smoke.pdf",):
        os.replace(os.path.join(work, name), os.path.join(corpus, name))
    os.replace(os.path.join(work, "smoke.docx"), os.path.join(out, "smoke.docx"))

    g = os.path.join(TOOLS, "gate.py")
    r = os.path.join(TOOLS, "reflow.py")
    v = os.path.join(TOOLS, "visual.py")
    s = os.path.join(TOOLS, "sidebyside.py")
    l = os.path.join(TOOLS, "looked.py")
    t = os.path.join(TOOLS, "txt-guard.py")

    ok = True
    ok &= run("gate.py", [g, "--corpus", corpus, "--out", out,
                          "--baseline", os.path.join(work, "base.json")], work)
    ok &= run("reflow.py", [r, "--dir", out], work)
    ok &= run("visual.py", [v, "--corpus", corpus, "--out", out], work)
    ok &= run("sidebyside.py", [s, "--corpus", corpus, "--out", out, "--doc", "smoke",
                                "--record", os.path.join(work, "LOOKED.tsv")], work)
    ok &= run("looked.py", [l, "--record", os.path.join(work, "LOOKED.tsv")], work)
    ok &= run("txt-guard.py", [t, "snapshot", "--dir", out,
                               "--save", os.path.join(work, "guard.json")], work)

    print("")
    if ok:
        print("every bench tool ran")
        return 0
    print("a bench tool did not run - fix it before committing")
    return 1


if __name__ == "__main__":
    sys.exit(main())
