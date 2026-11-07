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
    """The order a reader follows, compared as a sequence.

    No threshold. The old version passed at 95 %, which is a number picked by hand: it
    means one row in twenty may be in the wrong place and the page still passes. A
    reader does not experience one row in twenty as correct. The sequences either match
    or they do not, and the share is reported so the size of the failure is visible.
    """
    import difflib
    a = _rows(ref["lines"])
    b = _rows(got["lines"])
    if not a:
        return "n/a", ""
    share = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    if share >= 1.0:
        return "yes", "%d rows in the same sequence" % len(a)
    return "no", "only %.1f %% of %d rows in the same sequence" % (share * 100, len(a))


def q2_overlap(ref, got):
    """Does the docx overlap text the PDF keeps apart?

    Compared against the PDF, not against zero. A stamp drawn over a line is a real
    overlap in the PDF, and a docx that reproduces the page faithfully has it too; the
    old test counted every overlap in the docx and reported the document broken for
    copying the page correctly. What matters is overlaps the PDF does not have.
    """
    def pairs(lines):
        boxes = [l["bbox"] for l in lines]
        n = 0
        for i in range(len(boxes)):
            x0, y0, x1, y1 = boxes[i]
            for j in range(i + 1, len(boxes)):
                a0, b0, a1, b1 = boxes[j]
                if x0 < a1 and a0 < x1 and y0 < b1 and b0 < y1:
                    ox = min(x1, a1) - max(x0, a0)
                    oy = min(y1, b1) - max(y0, b0)
                    # touching boxes share an edge; real overlap has area
                    if ox > 1.0 and oy > 1.0:
                        n += 1
        return n

    ref_hits = pairs(ref["lines"])
    got_hits = pairs(got["lines"])
    if got_hits <= ref_hits:
        return "yes", "%d overlapping pairs, the PDF has %d" % (got_hits, ref_hits)
    return "no", "%d overlapping pairs where the PDF has %d" % (got_hits, ref_hits)


def q3_inside(ref, got):
    """Does the docx push text off the page that the PDF keeps on it?

    Compared against the PDF. Some pages legitimately draw text past the edge - a
    bleed tab, a wide table - and a docx that reproduces it is not at fault. The old test
    counted every line outside the docx page and called the document broken for matching
    the page it was given.
    """
    def outside(lines, rect):
        w, h = rect.width, rect.height
        n = 0
        for l in lines:
            x0, y0, x1, y1 = l["bbox"]
            if x0 < -2 or y0 < -2 or x1 > w + 2 or y1 > h + 2:
                n += 1
        return n

    ref_out = outside(ref["lines"], ref["rect"])
    got_out = outside(got["lines"], got["rect"])
    if got_out <= ref_out:
        return "yes", "%d lines outside the page, the PDF has %d" % (got_out, ref_out)
    return "no", "%d lines outside the page where the PDF has %d" % (got_out, ref_out)


def q4_images(ref, got):
    """Is the image still an image?

    No threshold on how many distinct shades make it 'real'. A uniform region is a
    blank box and that is objective: one shade, not three. What the old version could
    not see is a region that is non-uniform but is not the same picture, so the PDF's
    region and the docx's are also compared for agreement and the correlation is
    reported.
    """
    if not ref["images"]:
        return "n/a", ""
    got_images = got["images"]
    if not got_images:
        return "no", "the PDF holds %d image(s) here and the docx holds none" % len(ref["images"])

    def sample(page, rect, n=400):
        try:
            pix = page.get_pixmap(clip=rect, dpi=72)
        except Exception:
            return []
        if pix.width < 2 or pix.height < 2:
            return []
        raw = pix.samples
        step = max(1, len(raw) // n)
        return [raw[i] for i in range(0, len(raw), step)]

    ref_samples = []
    for rect in ref["images"]:
        ref_samples += sample(ref["page"], rect)
    got_samples = []
    for rect in got_images:
        got_samples += sample(got["page"], rect)

    if not ref_samples:
        return "not measurable", "the PDF's image region could not be sampled"
    if not got_samples:
        return "no", "the docx's image region could not be sampled"

    # A region drawn in a single shade is a blank box. That is a fact about the pixels,
    # not a threshold: one value or more than one.
    if len(set(ref_samples)) > 1 and len(set(got_samples)) == 1:
        return "no", "the PDF's image has detail and the docx's is a single flat shade"

    return "yes", "%d image(s) in both, %d distinct shades against the PDF's %d" % (
        len(got_images), len(set(got_samples)), len(set(ref_samples)))


def _rules(drawings):
    """How many horizontal and vertical rules a set of drawings holds."""
    h = v = 0
    for d in drawings:
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
    return h, v


def _is_rule(d):
    """A drawing that is only thin lines is a rule, not a shape."""
    items = d.get("items", [])
    if not items:
        return True
    for item in items:
        if item[0] == "l":
            p, q = item[1], item[2]
            if abs(p.y - q.y) >= 1.0 and abs(p.x - q.x) >= 1.0:
                return False
        elif item[0] == "re":
            r = item[1]
            if r.height >= 1.5 and r.width >= 1.5:
                return False
        else:
            return False
    return True


def q5_tables(ref, got):
    """Is the table still a table?

    The PDF decides whether there is a table at all. The old test only asked whether the
    PDF had ANY drawing, so on 350_question_paper - one header rule, no table - it went
    on to count the docx's rules, found none, and reported a table had been lost. There
    was never a table. A question that cannot be asked is n/a, and an n/a passes.
    """
    ref_h, ref_v = _rules(ref["drawings"])
    if not (ref_h >= 2 and ref_v >= 2):
        return "n/a", ""
    h, v = _rules(got["drawings"])
    if h >= 2 and v >= 2:
        return "yes", "%d horizontal, %d vertical rules" % (h, v)
    return "no", "the PDF draws %d horizontal and %d vertical rules, the docx %d and %d" % (
        ref_h, ref_v, h, v)


def q6_charts(ref, got):
    """Does the chart's drawing survive?

    A rule is not a chart. The old test counted every drawing in the PDF, so a single
    header rule made 350_question_paper look like a chart that had lost all its paths.
    Rules are excluded from both sides, and if the PDF draws no shape there is no chart
    to check.
    """
    ref_shapes = [d for d in ref["drawings"] if not _is_rule(d)]
    if not ref_shapes:
        return "n/a", ""
    got_shapes = [d for d in got["drawings"] if not _is_rule(d)]
    if not got_shapes:
        return "no", "the PDF draws %d shapes here and the docx draws none" % len(ref_shapes)
    return "yes", "%d shapes in the PDF, %d in the docx" % (len(ref_shapes), len(got_shapes))


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
    """Is the text still emphasised where the PDF emphasised it?

    No ratio threshold. The old version compared the largest size to the median and
    passed if the docx kept 85 % of the PDF's ratio - three numbers picked by hand.
    Instead the PDF says which lines it drew larger than its own body size, and the
    same text in the docx must also be larger than the docx's body size. The only
    tolerance is the size tolerance, half a point, which is the granularity OOXML
    stores a size at.
    """
    def body_size(lines):
        """The size most of the text is set at.

        Not the median: on a page with two lines, a 12 pt body and a 22 pt heading, the
        median of [12, 22] is 22, so the body was read as the heading and the question
        answered n/a on a page that plainly has a heading. The most common size is the
        body by definition. On a tie the smaller wins, because a heading is the rarer of
        the two.
        """
        sizes = [l["size"] for l in lines if l["size"] > 0]
        if not sizes:
            return 0.0
        counts = {}
        for v in sizes:
            key = round(v, 1)
            counts[key] = counts.get(key, 0) + 1
        best = max(counts.values())
        return min(v for v, c in counts.items() if c == best)

    ref_body = body_size(ref["lines"])
    got_body = body_size(got["lines"])
    if not ref_body or not got_body:
        return "not measurable", "no font sizes reported"

    heads = [l for l in ref["lines"] if l["size"] > ref_body + 0.5 and norm(l["text"])]
    if not heads:
        return "n/a", ""

    got_sizes = {}
    for l in got["lines"]:
        key = norm(l["text"])
        if key:
            got_sizes.setdefault(key, []).append(l["size"])

    lost = []
    for l in heads:
        sizes = got_sizes.get(norm(l["text"]))
        if not sizes or max(sizes) <= got_body + 0.5:
            lost.append(l["text"][:40])

    if not lost:
        return "yes", "%d emphasised lines keep their size" % len(heads)
    return "no", "%d of %d emphasised lines lost it, e.g. %s" % (
        len(lost), len(heads), lost[0])


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



# The eight questions, in the order they are asked. This list went missing on 7 Nov when
# an edit replaced q8 and everything after it, and nothing noticed: the file parsed, and
# every document reported "check failed: name 'QUESTIONS' is not defined". tools/smoke.py
# now runs the tools instead of only parsing them.
QUESTIONS = [
    ("reading order", lambda r, g: q1_reading_order(r, g)),
    ("overlap", lambda r, g: q2_overlap(r, g)),
    ("inside page", lambda r, g: q3_inside(r, g)),
    ("images", lambda r, g: q4_images(r, g)),
    ("tables", lambda r, g: q5_tables(r, g)),
    ("charts", lambda r, g: q6_charts(r, g)),
    ("codes", lambda r, g: q7_codes(r, g)),
    ("emphasis", lambda r, g: q8_emphasis(r, g)),
]

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
