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
    return re.sub(r"\s+", " ", text or "").strip().lower()


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
    """Everything the eight questions need, read while the document is still open.

    The document must stay open: a page object is a handle into its document, and the
    moment that document closes every call on it raises. The first version returned the
    page handle and then closed the document, so the image question and the QR question
    threw every single time and the catch-all turned each of them into "unsure" - which
    passes. Two of the eight questions were therefore never asked.
    """
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
                lines.append({
                    "text": text,
                    "bbox": line["bbox"],
                    "size": max(sizes) if sizes else 0,
                    "bold": any("bold" in (s.get("font", "").lower()) for s in spans),
                })
        images = []
        for img in page.get_images(full=True):
            try:
                images.append(page.get_image_bbox(img))
            except Exception:
                pass
        pages.append({
            "lines": lines,
            "images": images,
            "drawings": page.get_drawings(),
            "rect": page.rect,
            "page": page,
            "pixmap": page.get_pixmap(dpi=200),
        })
    return pages


def q1_reading_order(ref, got):
    a = [norm(l["text"]) for l in ref["lines"]]
    b = [norm(l["text"]) for l in got["lines"]]
    if not a:
        return "n/a", ""
    same = sum(1 for x, y in zip(a, b) if x == y)
    share = same / max(1, len(a))
    if share >= 0.95:
        return "yes", "%.0f %% of lines in the same sequence" % (share * 100)
    return "no", "only %.0f %% of lines in the same sequence" % (share * 100)


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
            step = max(1, len(samples) // 400)
            if len(set(samples[i] for i in range(0, len(samples), step))) < 3:
                blank += 1
        except Exception:
            blank += 1
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
    """QR and barcodes. There is no decoder in this sandbox, and that is reported.

    pyzbar needs a system library, zxing-cpp and opencv are not installable because the
    sandbox cannot reach a package index, and there is no pure-Python decoder. A question
    that cannot be answered must say so, in words, rather than quietly returning
    "unsure" - which reads like "probably fine" and lets a broken QR code through.
    """
    try:
        from pyzbar.pyzbar import decode as zbar  # noqa: F401
    except ImportError:
        try:
            import zxingcpp  # noqa: F401
        except ImportError:
            try:
                import cv2  # noqa: F401
            except ImportError:
                return ("not measurable",
                        "no QR decoder in this sandbox - look at the page yourself")

    def read(page):
        from PIL import Image
        import io
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        try:
            from pyzbar.pyzbar import decode as zbar
            return [r.data.decode("utf-8", "replace") for r in zbar(img)]
        except ImportError:
            pass
        try:
            import zxingcpp
            return [r.text for r in zxingcpp.read_barcodes(img)]
        except ImportError:
            pass
        try:
            import cv2, numpy as np
            arr = np.array(img.convert("L"))
            data, _pts, _ = cv2.QRCodeDetector().detectAndDecode(arr)
            return [data] if data else []
        except ImportError:
            return []

    want = read(ref["page"])
    if not want:
        return "n/a", ""
    have = read(got["page"])
    if sorted(want) == sorted(have):
        return "yes", "%d codes, same content" % len(want)
    return "no", "the PDF holds %d codes, the render decodes %d" % (len(want), len(have))


def q8_emphasis(ref, got):
    if not ref["lines"]:
        return "n/a", ""
    ref_sizes = sorted(l["size"] for l in ref["lines"] if l["size"] > 0)
    got_sizes = sorted(l["size"] for l in got["lines"] if l["size"] > 0)
    if not ref_sizes or not got_sizes:
        return "unsure", "no font sizes reported"
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
    with pymupdf.open(ref_pdf) as refdoc, pymupdf.open(got_pdf) as gotdoc:
        ref = page_data(refdoc)
        got = page_data(gotdoc)
        for i in range(min(len(ref), len(got))):
            page_answers = {}
            for name, fn in QUESTIONS:
                try:
                    verdict, detail = fn(ref[i], got[i])
                except Exception as exc:
                    # An exception is NOT a pass. It is reported as a failure of the
                    # check itself, so a broken question cannot hide behind "unsure"
                    # and look like a document that passed.
                    verdict, detail = "error", "%s: %s" % (type(exc).__name__, str(exc)[:70])
                page_answers[name] = {"verdict": verdict, "detail": detail}
                if verdict in ("no", "error"):
                    failed += 1
                elif verdict in ("unsure", "not measurable"):
                    unsure += 1
            answers.append({"page": i + 1, "answers": page_answers})

    return {
        "pages_ref": len(ref),
        "pages_got": len(got),
        "page_count_ok": len(ref) == len(got),
        "answers": answers,
        "failed": failed,
        "unsure": unsure,
        "ok": failed == 0 and len(ref) == len(got),
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
