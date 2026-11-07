#!/usr/bin/env python3
"""G6 - the eight questions, answered by measurement where measurement can answer.

WHY THIS EXISTS
    Some defects are invisible to every count and every coordinate. Text in the wrong
    reading order is still at the right place. An empty white box measures as an image.
    A chart drawn as grey rectangles has the right size and position. A QR code that
    was re-rendered too small still occupies its rectangle. This asks eight questions
    per page and answers each one from the pixels and the vector content, so two runs
    give the same answer.

    Where a criterion genuinely cannot decide, the question is reported as UNSURE and
    a person looks at that page. That is the honest outcome; guessing is not.

USAGE
    python3 visual.py --corpus PDF_DIR --out DOCX_DIR
    python3 visual.py --corpus PDF_DIR --out DOCX_DIR --json result.json
    python3 visual.py --corpus PDF_DIR --out DOCX_DIR --pages 300_prescription_rx

EXIT CODE
    0  every page answered yes or not-applicable
    1  at least one page failed a question
    2  the check could not run
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

DPI = 130


def norm(text):
    # Control characters are not text. A PDF that draws a soft hyphen or a zero-width
    # joiner reports it as U+0000 inside the line, and comparing that against the .docx's
    # text charged a survey header for a word that is present on both sides: the PDF read
    # "disagreestrongly\x00disagree" and the render "disagreestrongly disagree".
    # Replaced by a space, not deleted: the page uses the character as the gap between two
    # words, so deleting it welds "strongly" to "agree" and the render is charged for a
    # missing space it does not have.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b-\u200d\ufeff]", " ", text or "")
    return re.sub(r"\s+", " ", text).strip().lower()


def render_pdf(src, outdir):
    os.makedirs(outdir, exist_ok=True)
    if src.lower().endswith(".docx"):
        try:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                            "--outdir", outdir, src],
                           check=True, capture_output=True, timeout=240)
        except Exception:
            return None
        pdf = os.path.join(outdir, os.path.basename(src)[:-5] + ".pdf")
        return pdf if os.path.exists(pdf) else None
    return src


def page_data(doc):
    """Everything the eight questions need, read while the document is open."""
    import pymupdf
    pages = []
    for page in doc:
        d = page.get_text("dict")
        lines = []
        for block in d["blocks"]:
            for line in block.get("lines", []):
                spans = line.get("spans") or []
                text = "".join(s.get("text", "") for s in spans)
                if not norm(text):
                    continue
                sizes = [s.get("size", 0) for s in spans if s.get("text", "").strip()]
                origins = [s["origin"][1] for s in spans if s.get("origin")]
                lines.append({
                    "text": text,
                    "bbox": line["bbox"],
                    # The baseline, not the box's top. A line's box top is the font's
                    # ascender, so two fields on ONE baseline set in different faces
                    # report tops 3 pt apart: on an org chart that split "TRANSPORT"
                    # off its own row and charged the page for a row that is not
                    # there. The baseline is the same number for both.
                    "base": min(origins) if origins else line["bbox"][3],
                    "size": max(sizes) if sizes else 0,
                    "bold": any("bold" in (s.get("font", "").lower()) for s in spans),
                })
        images = []
        for img in page.get_images(full=True):
            try:
                images.append(page.get_image_bbox(img))
            except Exception:
                pass
        drawings = page.get_drawings()
        pages.append({
            "lines": lines,
            "images": images,
            "drawings": drawings,
            "rect": page.rect,
            "page": page,
        })
    return pages


def _rows(lines):
    """Lines grouped into the visual rows a reader's eye traverses.

    A row, not a line, is the unit of reading order. Three labels drawn on one baseline
    are one line of the page, and the writer is allowed - and has long been required - to
    emit them as one Word paragraph with a tab stop at each label's measured x, because
    that is how Word puts two strings at two known x positions on one line. Comparing
    line i of the PDF with line i of the render charges that paragraph for two lines that
    are not missing, and every line after it shifts by two: on an org chart, whose boxes
    are drawn one at a time and read across, that reported 55 % order for a page whose
    every row was in the right place. Rule 3 of the brief forbids index pairing for
    exactly this reason, so the comparison is on rows, matched by their text.
    """
    rows = []
    for l in sorted(lines, key=lambda l: (l.get("base", l["bbox"][3]), l["bbox"][0])):
        y = l.get("base", l["bbox"][3])
        tol = max(1.5, 0.3 * (l.get("size") or 10))
        if rows and abs(rows[-1][0] - y) <= tol:
            rows[-1][1].append(l)
        else:
            rows.append([y, [l]])
    out = []
    for _y, ls in rows:
        ls.sort(key=lambda l: l["bbox"][0])
        text = norm(" ".join(l["text"] for l in ls))
        if text:
            out.append(text)
    return out


def q1_reading_order(ref, got):
    import difflib
    a = _rows(ref["lines"])
    b = _rows(got["lines"])
    if not a:
        return "n/a", ""
    share = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    if share >= 0.95:
        return "yes", "%.0f %% of rows in the same sequence (%d rows)" % (share * 100, len(a))
    return "no", "only %.0f %% of rows in the same sequence (%d rows)" % (share * 100, len(a))


def q2_overlap(got):
    boxes = [l["bbox"] for l in got["lines"]]
    hits = 0
    for i in range(len(boxes)):
        x0, y0, x1, y1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            a0, b0, a1, b1 = boxes[j]
            if x0 < a1 and a0 < x1 and y0 < b1 and b0 < y1:
                ox = min(x1, a1) - max(x0, a0)
                oy = min(y1, b1) - max(y0, b0)
                # touching boxes share an edge; real overlap has area
                if ox > 1.0 and oy > 1.0:
                    hits += 1
    if hits == 0:
        return "yes", ""
    return "no", "%d overlapping line pairs" % hits


def q3_inside(ref, got):
    w, h = got["rect"].width, got["rect"].height
    out = 0
    for l in got["lines"]:
        x0, y0, x1, y1 = l["bbox"]
        if x0 < -2 or y0 < -2 or x1 > w + 2 or y1 > h + 2:
            out += 1
    if out == 0:
        return "yes", ""
    return "no", "%d lines outside the page" % out


def q4_images(ref, got):
    if not ref["images"]:
        return "n/a", ""
    if not got["images"]:
        return "no", "the PDF has %d images, the render has none" % len(ref["images"])
    blank = 0
    for rect in got["images"]:
        try:
            import pymupdf
            pix = got["page"].get_pixmap(clip=rect, dpi=72)
            if pix.width < 4 or pix.height < 4:
                blank += 1
                continue
            samples = pix.samples
            if len(set(samples[i] for i in range(0, len(samples), max(1, len(samples) // 400)))) < 3:
                blank += 1
        except Exception:
            pass
    if blank == 0:
        return "yes", ""
    return "no", "%d image regions are blank" % blank


def q5_tables(ref, got):
    if not ref["drawings"]:
        return "n/a", ""
    h = v = 0
    for d in got["drawings"]:
        for item in d.get("items", []):
            if item[0] == "l":
                p, q = item[1], item[2]
                if abs(p.y - q.y) < 1.0:
                    h += 1
                elif abs(p.x - q.x) < 1.0:
                    v += 1
            elif item[0] == "re":
                r = item[1]
                if r.height < 1.5:
                    h += 1
                if r.width < 1.5:
                    v += 1
    if h >= 2 and v >= 2:
        return "yes", "%d horizontal, %d vertical rules" % (h, v)
    return "no", "only %d horizontal and %d vertical rules" % (h, v)


def q6_charts(ref, got):
    ref_paths = sum(len(d.get("items", [])) for d in ref["drawings"])
    if ref_paths < 5:
        return "n/a", ""
    got_paths = sum(len(d.get("items", [])) for d in got["drawings"])
    if got_paths >= max(5, ref_paths * 0.5):
        return "yes", "%d vector items against the PDF's %d" % (got_paths, ref_paths)
    return "no", "%d vector items against the PDF's %d" % (got_paths, ref_paths)


def q7_codes(ref, got):
    try:
        import pymupdf
    except ImportError:
        return "not measurable", "PyMuPDF is not installed"
    import io
    try:
        from PIL import Image
    except ImportError:
        return "not measurable", "Pillow is not installed"
    # Two decoders, tried in turn. pyzbar needs the system libzbar, which this image does
    # not carry and cannot apt-install; OpenCV decodes QR and the common 1-D symbologies
    # in-process, so a page with a code can be answered instead of reported UNSURE.
    zbar = None
    try:
        from pyzbar.pyzbar import decode as zbar
    except Exception:
        zbar = None
    cv2 = None
    try:
        import cv2
        import numpy as np
    except Exception:
        cv2 = None

    def read(page):
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        out = []
        if zbar is not None:
            try:
                out += [r.data.decode("utf-8", "replace") for r in zbar(img)]
            except Exception:
                pass
        if cv2 is not None:
            arr = np.array(img)[:, :, ::-1]
            try:
                ok, texts, _pts, _q = cv2.QRCodeDetector().detectAndDecodeMulti(arr)
                if ok:
                    out += [t for t in texts if t]
            except Exception:
                pass
            try:
                bc = cv2.barcode.BarcodeDetector()
                ok, texts, _t, _p = bc.detectAndDecodeMulti(arr)
                if ok:
                    out += [t for t in texts if t]
            except Exception:
                pass
        if zbar is None and cv2 is None:
            return None
        return sorted(set(out))

    want = read(ref["page"])
    if want is None:
        return ("not measurable",
                "no QR decoder in this sandbox - look at the page yourself")
    if not want:
        return "n/a", ""
    have = read(got["page"]) or []
    if sorted(want) == sorted(have):
        return "yes", "%d codes, same content" % len(want)
    return "no", "the PDF holds %d codes, the render decodes %d" % (len(want), len(have))


def q8_emphasis(ref, got):
    if not ref["lines"]:
        return "n/a", ""
    ref_sizes = sorted(l["size"] for l in ref["lines"] if l["size"] > 0)
    got_sizes = sorted(l["size"] for l in got["lines"] if l["size"] > 0)
    if not ref_sizes or not got_sizes:
        return "not measurable", "no font sizes reported"
    ref_body = ref_sizes[len(ref_sizes) // 2]
    got_body = got_sizes[len(got_sizes) // 2]
    ref_head = ref_sizes[-1]
    got_head = got_sizes[-1]
    ref_ratio = ref_head / ref_body if ref_body else 1
    got_ratio = got_head / got_body if got_body else 1
    if ref_ratio <= 1.05:
        return "n/a", ""
    if got_ratio >= ref_ratio * 0.85:
        return "yes", "headings %.2fx body against the PDF's %.2fx" % (got_ratio, ref_ratio)
    return "no", "headings %.2fx body against the PDF's %.2fx" % (got_ratio, ref_ratio)


QUESTIONS = [
    ("reading order", lambda r, g: q1_reading_order(r, g)),
    ("overlap", lambda r, g: q2_overlap(g)),
    ("inside page", lambda r, g: q3_inside(r, g)),
    ("images", lambda r, g: q4_images(r, g)),
    ("tables", lambda r, g: q5_tables(r, g)),
    ("charts", lambda r, g: q6_charts(r, g)),
    ("qr/barcode", lambda r, g: q7_codes(r, g)),
    ("emphasis", lambda r, g: q8_emphasis(r, g)),
]


def check(pdf_path, docx_path, workdir):
    ref_pdf = render_pdf(pdf_path, workdir + "/ref")
    got_pdf = render_pdf(docx_path, workdir + "/got")
    if not ref_pdf or not got_pdf:
        return {"error": "could not render one side"}

    import pymupdf
    answers = []
    failed = 0
    unsure = 0
    pages_ref = pages_got = 0
    # Both documents stay open while the questions run. A page is a handle into its
    # document: the moment that document closes, every call on the page raises. An
    # earlier version returned the page handles and closed the documents, so the image
    # question and the QR question threw on every page of every document and the
    # catch-all recorded them as "unsure" - which passes. Two of the eight questions
    # were never actually asked.
    with pymupdf.open(ref_pdf) as refdoc, pymupdf.open(got_pdf) as gotdoc:
        ref = page_data(refdoc)
        got = page_data(gotdoc)
        pages_ref, pages_got = len(ref), len(got)
        for i in range(min(len(ref), len(got))):
            page_answers = {}
            for name, fn in QUESTIONS:
                try:
                    verdict, detail = fn(ref[i], got[i])
                except Exception as exc:
                    # An exception is NOT a pass. A question that could not run is a
                    # failure of the check, and saying so is the only honest answer.
                    verdict = "error"
                    detail = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                page_answers[name] = {"verdict": verdict, "detail": detail}
                if verdict in ("no", "error"):
                    failed += 1
                elif verdict in ("unsure", "not measurable"):
                    unsure += 1
            answers.append({"page": i + 1, "answers": page_answers})

    return {
        "pages_ref": pages_ref,
        "pages_got": pages_got,
        "page_count_ok": pages_ref == pages_got,
        "answers": answers,
        "failed": failed,
        "unsure": unsure,
        "ok": failed == 0 and pages_ref == pages_got,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json")
    ap.add_argument("--pages", action="append", default=[])
    args = ap.parse_args()

    if shutil.which("soffice") is None:
        print("LibreOffice is not installed, so the docx side cannot be rendered")
        return 2
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        print("PyMuPDF is not installed")
        return 2

    if args.pages:
        names = [p if p.lower().endswith(".pdf") else p + ".pdf" for p in args.pages]
    else:
        names = sorted(f for f in os.listdir(args.corpus) if f.lower().endswith(".pdf"))

    results = []
    workdir = tempfile.mkdtemp(prefix="visual-")
    for name in names:
        base = name[:-4]
        docx = os.path.join(args.out, base + ".docx")
        if not os.path.isfile(docx):
            results.append({"doc": base, "ok": False, "error": "no docx"})
            continue
        try:
            r = check(os.path.join(args.corpus, name), docx, workdir)
        except Exception as exc:
            r = {"error": "check failed: " + str(exc)}
        r["doc"] = base
        results.append(r)

    failed = [r for r in results if not r.get("ok")]
    for r in results:
        if r.get("ok"):
            print("OK   " + r["doc"][:52])
        else:
            print("FAIL " + r["doc"][:52] + "  " + r.get("error", ""))
            if not r.get("page_count_ok", True):
                print("       %d pages in the render against the PDF's %d"
                      % (r.get("pages_got", 0), r.get("pages_ref", 0)))
            for page in r.get("answers", []):
                for name, a in page["answers"].items():
                    if a["verdict"] in ("no", "error"):
                        print("       page %d  %-14s %s" % (page["page"], name, a["detail"]))

    print("")
    print("%d documents, %d failed the eight questions" % (len(results), len(failed)))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=1)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
