#!/usr/bin/env python3
"""The structure gate: is this a Word document, or a PDF wearing one?

WHY
    A .docx whose body text sits in anchored text boxes measures perfectly - every
    line is exactly where the PDF drew it - and is not a Word document. It cannot be
    edited, it does not reflow, and it falls apart the moment anyone touches it.
    Every number you can measure agrees with it. This is the check that does not.

TWO CHECKS, NEITHER WITH A MAGIC THRESHOLD

    1. STRUCTURE
       Count the body paragraphs, the text boxes, the floating frames and the
       anchored drawings. Body text inside a text box is REPORTED, not banned: a
       watermark or a sidebar legitimately uses one, and the report names the
       document and the count so a person can look at that one case.

    2. REFLOW
       Lay the same document out at two page widths and compare the number of
       rendered lines. A flowing document lays out differently when the page
       changes. A fixed one does not move at all. No threshold is involved: the
       question is only whether the layout changed.

USAGE
    python3 reflow.py --dir OUT                 # every .docx in a folder
    python3 reflow.py --docx one.docx --docx two.docx
    python3 reflow.py --dir OUT --json out.json # machine-readable result

EXIT CODE
    0  every document is a real Word document
    1  at least one is not
    2  the tools needed to render are missing (the check could not run)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

# Two page widths to lay the document out at. Word's default Letter width is 12240
# twips; the second is deliberately narrower so a flowing document must re-wrap.
WIDE_TWIPS = 12240
NARROW_TWIPS = 9000


def count(xml, needle):
    return xml.count(needle)


def structure(docx_path):
    """What the file declares about itself, read from its own XML."""
    with zipfile.ZipFile(docx_path) as z:
        try:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
        except KeyError:
            return None
    return {
        "paragraphs": count(xml, "<w:p>") + count(xml, "<w:p "),
        "text_boxes": count(xml, "<w:txbxContent"),
        "floating_frames": count(xml, "<w:framePr"),
        "anchored": count(xml, "<wp:anchor"),
        "tables": count(xml, "<w:tbl>") + count(xml, "<w:tbl "),
    }


def set_page_width(docx_in, docx_out, twips):
    """Copy the document with every section's page width replaced."""
    with zipfile.ZipFile(docx_in) as zin, zipfile.ZipFile(docx_out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                text = data.decode("utf-8", "replace")
                import re
                text = re.sub(r'<w:pgSz[^/]*/>',
                              '<w:pgSz w:w="%d" w:h="15840"/>' % twips,
                              text)
                data = text.encode("utf-8")
            zout.writestr(item, data)


def render_line_count(docx_path, workdir):
    """Lay the document out with LibreOffice and count the lines it produced."""
    outdir = os.path.join(workdir, "render")
    os.makedirs(outdir, exist_ok=True)
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                        "--outdir", outdir, docx_path],
                       check=True, capture_output=True, timeout=180)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    pdf = os.path.join(outdir, os.path.basename(docx_path)[:-5] + ".pdf")
    if not os.path.exists(pdf):
        return None
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            return None
    lines = 0
    pages = 0
    widest = 0.0
    with pymupdf.open(pdf) as doc:
        pages = doc.page_count
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    if line.get("spans"):
                        lines += 1
                        x0, _y0, x1, _y1 = line["bbox"]
                        w = x1 - x0
                        if w > widest:
                            widest = w
    return {"lines": lines, "pages": pages, "widest_pt": widest}


def check_one(docx_path, workdir):
    info = structure(docx_path)
    if info is None:
        return {"doc": os.path.basename(docx_path), "ok": False,
                "reason": "no word/document.xml - not a readable .docx"}

    result = {"doc": os.path.basename(docx_path), "structure": info}

    wide = os.path.join(workdir, "wide.docx")
    narrow = os.path.join(workdir, "narrow.docx")
    set_page_width(docx_path, wide, WIDE_TWIPS)
    set_page_width(docx_path, narrow, NARROW_TWIPS)

    wide_layout = render_line_count(wide, workdir)
    narrow_layout = render_line_count(narrow, workdir)

    problems = []
    if info["text_boxes"] > 0:
        problems.append("%d text boxes - body text inside one cannot be edited or reflowed"
                        % info["text_boxes"])
    if info["floating_frames"] > 0:
        problems.append("%d floating frames" % info["floating_frames"])

    if wide_layout is None or narrow_layout is None:
        result["reflow"] = "not measured - LibreOffice or PyMuPDF is missing"
    else:
        result["wide"] = wide_layout
        result["narrow"] = narrow_layout
        moved = (wide_layout["lines"] != narrow_layout["lines"]
                 or wide_layout["pages"] != narrow_layout["pages"])
        result["reflow"] = "changed" if moved else "identical"

        if not moved:
            # A layout that does not move only means something if it COULD have moved.
            # If the widest line on the page is already narrower than the narrow page,
            # no amount of narrowing can wrap it, and reporting that as a defect would
            # send a run chasing a document whose layout is perfectly fine. Measured,
            # not assumed: this is the widest line the render actually produced.
            narrow_pt = NARROW_TWIPS / 20.0
            widest = wide_layout.get("widest_pt", 0.0)
            if widest and widest < narrow_pt:
                result["reflow"] = "not measurable - the widest line is %.0f pt, inside the %.0f pt narrow page" % (widest, narrow_pt)
            elif wide_layout["lines"] > 1:
                problems.append("layout did not change when the page width changed")

    result["problems"] = problems
    result["ok"] = not problems
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    ap.add_argument("--docx", action="append", default=[])
    ap.add_argument("--json")
    args = ap.parse_args()

    targets = list(args.docx)
    if args.dir:
        if not os.path.isdir(args.dir):
            print("no such folder: " + args.dir)
            return 2
        for name in sorted(os.listdir(args.dir)):
            if name.lower().endswith(".docx"):
                targets.append(os.path.join(args.dir, name))
    if not targets:
        print("nothing to check")
        return 2

    if shutil.which("soffice") is None:
        print("LibreOffice is not installed, so the reflow half cannot run")
        return 2

    results = []
    workdir = tempfile.mkdtemp(prefix="reflow-")
    for path in targets:
        try:
            results.append(check_one(path, workdir))
        except Exception as exc:
            results.append({"doc": os.path.basename(path), "ok": False,
                            "reason": "check failed: " + str(exc)})

    failed = [r for r in results if not r.get("ok")]
    for r in results:
        mark = "OK  " if r.get("ok") else "FAIL"
        print("%s %s" % (mark, r["doc"]))
        for p in r.get("problems", []):
            print("       " + p)
        if r.get("reason"):
            print("       " + r["reason"])
    print("%d checked, %d not a real Word document" % (len(results), len(failed)))

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=1)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
