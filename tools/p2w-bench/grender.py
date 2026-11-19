#!/usr/bin/env python3
"""grender.py - render a .docx through Google Docs, the renderer the users actually open.

WHY THIS EXISTS. The pipeline renders with `soffice --headless`. LibreOffice has DejaVu Serif,
Liberation Serif and Liberation Sans installed, so it draws every one of these PDFs in the face they
were set in. Google Docs has none of them. It substitutes, and a substitute face has different
advances, so the line is a different width and everything downstream of it moves.

Measured 19 Nov on two documents, same engine, same source:

    310_court_judgment      LibreOffice  1.39 %    Google Docs  16.28 %
    01_stamp_rotated_15deg  LibreOffice  2.09 %    Google Docs  14.14 %

That is not a rounding difference. `verify_google.py` has said so since 13 Nov - "verify_visual.py
renders through LibreOffice, which honours constructs Google Docs does not, so it hides exactly the
faults the phone shows" - and the pipeline went on measuring with soffice because a Google render was
a manual, per-document chore. This file makes it a function call.

HOW THE RENDER IS OBTAINED. There is no Google renderer you can install. Drive converts an uploaded
.docx to a Google Doc, and a Google Doc exports as a PDF that Google laid out itself:

    upload the .docx  ->  copy it as application/vnd.google-apps.document  ->  export that as PDF

Those three steps are Drive API calls, so they cannot run inside this process. `grender.py` does the
local half - staging, fetching the returned PDF, verifying it is a real PDF of the right page count -
and takes the three ids on the command line. The caller supplies them:

    python3 grender.py --stage  <file.docx>              # prints the path to upload
    python3 grender.py --fetch  <export-url> <src.pdf> <out.pdf>
    python3 grender.py --check  <src.pdf> <google.pdf>   # is this a usable render?

`--fetch` verifies before it writes: a PDF whose page count differs from the source is not a render
of that document, and a file that is not a PDF at all is an error page with a 200 status.

WHAT IT DOES NOT DO, AND WHY THAT MATTERS. It does not decide whether the render is GOOD. That is
`verify_google.py`'s job and it already exists. This file only guarantees that the bytes on disk are
Google's own layout of the document in question, so that a score computed from them means something.
"""
import argparse, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = "/scratch/work/p2w/grender"


def pages(pdf):
    try:
        import fitz
        with fitz.open(pdf) as d:
            return len(d)
    except Exception:
        return -1


def stage(docx):
    """Copy a .docx somewhere stable and print the path a caller should upload."""
    if not os.path.exists(docx):
        print("no such file: %s" % docx)
        return 2
    os.makedirs(CACHE, exist_ok=True)
    dst = os.path.join(CACHE, os.path.basename(docx))
    shutil.copy(docx, dst)
    print(dst)
    return 0


def fetch(url, src, out):
    """Download the exported PDF and refuse it if it is not a render of `src`."""
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    tmp = out + ".part"
    r = subprocess.run(["curl", "-sL", "--max-time", "120", url, "-o", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        print("download failed: %s" % (r.stderr or r.stdout)[:200])
        return 2
    with open(tmp, "rb") as f:
        head = f.read(5)
    if head != b"%PDF-":
        # A 200 with an HTML body is how Drive reports "this is not a Google Doc".
        with open(tmp, "rb") as f:
            body = f.read(300)
        os.remove(tmp)
        print("not a PDF - first bytes %r. The export did not produce a document." % body[:80])
        return 3
    want = pages(src)
    got = pages(tmp)
    if want > 0 and got > 0 and got != want:
        # NOT A REFUSAL TO BE CLEVER. A render with a different page count is a different document:
        # Google reflowed it, or the export returned a cached copy of something else. Scoring it
        # against `src` would produce a number that looks like a layout error and is not one.
        os.replace(tmp, out)
        print("page count %d, source has %d - kept for inspection, do not score it" % (got, want))
        return 4
    os.replace(tmp, out)
    print("%s  %d page(s)" % (out, got))
    return 0


def check(src, gd):
    """Is `gd` a usable Google render of `src`?"""
    if not os.path.exists(gd):
        print("MISSING %s" % gd)
        return 2
    a, b = pages(src), pages(gd)
    if a <= 0 or b <= 0:
        print("unreadable: source %d pages, render %d pages" % (a, b))
        return 2
    if a != b:
        print("PAGE COUNT %d vs %d - this is not a render of that document" % (b, a))
        return 3
    # A render that is byte-identical to the source was never rendered - Drive handed the file back.
    with open(src, "rb") as f1, open(gd, "rb") as f2:
        if f1.read() == f2.read():
            print("IDENTICAL to the source - this file was never rendered by Google")
            return 4
    print("ok - %d page(s), a distinct document" % b)
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage"); ap.add_argument("--fetch", nargs=3)
    ap.add_argument("--check", nargs=2)
    a = ap.parse_args(argv)
    if a.stage:  return stage(a.stage)
    if a.fetch:  return fetch(*a.fetch)
    if a.check:  return check(*a.check)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
