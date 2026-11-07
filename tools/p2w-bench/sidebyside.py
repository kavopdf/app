#!/usr/bin/env python3
"""The visual check that is actually looked at.

WHY
    visual.py answers the eight questions from extracted data - text, boxes, pixel
    variance, rule counts. That is measurement, and it is necessary, but it is not
    looking at the page. A document can pass all eight and still be obviously wrong to
    a person: a heading in the wrong colour, a table squeezed into half its width, a
    logo where the signature should be. None of those is a box that overlaps.

    So this renders the same page twice at 130 dpi and puts them next to each other,
    with a third panel showing where the pixels differ. The agent then LOOKS at it.

WHAT IT WRITES
    <outdir>/<document>/page-01.png, page-02.png, ...
        PDF | DOCX side by side, labelled, with a difference panel on the right.

USAGE
    python3 sidebyside.py --corpus DIR --out DIR --doc 300_prescription_rx
    python3 sidebyside.py --corpus DIR --out DIR --doc 300_prescription_rx --pages 1,3
    python3 sidebyside.py --corpus DIR --out DIR --doc 300_prescription_rx --all-pages

    Then view the PNGs and answer the eight questions by looking at them.

EXIT
    0  the images were written
    1  a side could not be rendered
    2  the check could not run (LibreOffice, PyMuPDF or Pillow missing)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

DPI = 130


def render_docx(docx_path, workdir):
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                        "--outdir", workdir, docx_path],
                       check=True, capture_output=True, timeout=300)
    except Exception:
        return None
    pdf = os.path.join(workdir, os.path.basename(docx_path)[:-5] + ".pdf")
    return pdf if os.path.exists(pdf) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--doc", required=True, help="document base name, without .pdf")
    ap.add_argument("--pages", default="", help="1,3,5 - default is every page")
    ap.add_argument("--all-pages", action="store_true")
    ap.add_argument("--dpi", type=int, default=DPI)
    args = ap.parse_args()

    if shutil.which("soffice") is None:
        print("LibreOffice is not installed, so the docx side cannot be rendered")
        return 2
    try:
        import pymupdf
    except ImportError:
        print("PyMuPDF is not installed")
        return 2
    try:
        from PIL import Image, ImageDraw, ImageChops
    except ImportError:
        print("Pillow is not installed")
        return 2

    pdf_path = os.path.join(args.corpus, args.doc + ".pdf")
    docx_path = os.path.join(args.out, args.doc + ".docx")
    if not os.path.isfile(pdf_path):
        print("no such PDF: " + pdf_path)
        return 1
    if not os.path.isfile(docx_path):
        print("no such docx: " + docx_path)
        return 1

    workdir = tempfile.mkdtemp(prefix="sbs-")
    rendered = render_docx(docx_path, workdir)
    if not rendered:
        print("could not render the docx")
        return 1

    dest = os.path.join(args.outdir if hasattr(args, "outdir") else args.out, args.doc)
    os.makedirs(dest, exist_ok=True)

    with pymupdf.open(pdf_path) as ref, pymupdf.open(rendered) as got:
        n = max(ref.page_count, got.page_count)
        wanted = list(range(n))
        if args.pages and not args.all_pages:
            try:
                wanted = [int(p) - 1 for p in args.pages.split(",") if p.strip()]
            except ValueError:
                print("--pages wants numbers like 1,3,5")
                return 1

        written = 0
        for i in wanted:
            if i < 0 or i >= n:
                continue
            left = ref[i].get_pixmap(dpi=args.dpi) if i < ref.page_count else None
            right = got[i].get_pixmap(dpi=args.dpi) if i < got.page_count else None

            imgs = []
            for pix, label in ((left, "PDF"), (right, "DOCX")):
                if pix is None:
                    # a page the other side does not have is itself the finding
                    img = Image.new("RGB", (800, 200), (255, 230, 230))
                    ImageDraw.Draw(img).text((20, 90), label + ": page missing", fill=(150, 0, 0))
                else:
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                imgs.append(img)

            w = max(imgs[0].width, imgs[1].width)
            h = max(imgs[0].height, imgs[1].height)
            for k in range(2):
                if imgs[k].size != (w, h):
                    canvas = Image.new("RGB", (w, h), (250, 250, 250))
                    canvas.paste(imgs[k], (0, 0))
                    imgs[k] = canvas

            # difference panel: where the two pages disagree, in red on the PDF's grey
            diff = ImageChops.difference(imgs[0].convert("RGB"), imgs[1].convert("RGB")).convert("L")
            diff = diff.point(lambda v: 255 if v > 48 else 0)
            panel = imgs[0].convert("RGB").point(lambda v: v // 3)
            panel.paste((255, 0, 0), mask=diff)

            pad, head = 8, 26
            total_w = w * 3 + pad * 4
            total_h = h + head + pad * 2
            sheet = Image.new("RGB", (total_w, total_h), (255, 255, 255))
            d = ImageDraw.Draw(sheet)
            for idx, (img, label) in enumerate(((imgs[0], "PDF"),
                                                (imgs[1], "DOCX"),
                                                (panel, "DIFFERENCE (red = differs)"))):
                x = pad + idx * (w + pad)
                d.text((x + 4, 8), "%s  page %d of %d" % (label, i + 1, n), fill=(0, 0, 0))
                sheet.paste(img, (x, head))

            name = os.path.join(dest, "page-%02d.png" % (i + 1))
            sheet.save(name)
            written += 1

        print("wrote %d image(s) to %s" % (written, dest))
        if ref.page_count != got.page_count:
            print("NOTE: %d pages in the PDF, %d in the render - a page is missing"
                  % (ref.page_count, got.page_count))
        print("")
        print("Now view them and answer the eight questions by looking:")
        for f in sorted(os.listdir(dest))[:5]:
            print("   " + os.path.join(dest, f))
        return 0


if __name__ == "__main__":
    sys.exit(main())
