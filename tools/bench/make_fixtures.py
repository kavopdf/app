#!/usr/bin/env python3
"""
Build the benchmark fixtures.

Every fixture is made by PyMuPDF, not by KavoPDF. That matters: the reference a metric is
judged against must never come from the thing being measured.

    python3 tools/bench/make_fixtures.py <dir>
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
import pymupdf

def build(OUT):
    os.makedirs(OUT, exist_ok=True)

    # multi.pdf - 4 pages, body text + a ruled 3x3 table + an image on every page.
    # Used by crop, organize, rotate, watermark, page numbers, annotate, bookmarks,
    # pdf-to-word and repair.
    d = pymupdf.open()
    for pno in range(4):
        p = d.new_page(width=595, height=842)
        p.insert_text((60, 70), f"MULTI PAGE {pno+1}", fontsize=22, fontname="helv")
        for i in range(3):
            p.insert_text((60, 110 + i*17), f"Line {i} of body text on this page.", fontsize=11)
        x0, y0, w, h = 60, 190, 460, 90
        for i in range(4):
            p.draw_line((x0, y0 + i*h/3), (x0 + w, y0 + i*h/3))
            p.draw_line((x0 + i*w/3, y0), (x0 + i*w/3, y0 + h))
        for r in range(3):
            for c in range(3):
                p.insert_text((x0 + c*w/3 + 8, y0 + r*h/3 + 18), f"R{r+1}C{c+1}", fontsize=9)
        pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 120, 80), 0)
        pix.clear_with(200 + pno*10)
        p.insert_image(pymupdf.Rect(60, 320, 180, 400), pixmap=pix)
    d.save(os.path.join(OUT, "multi.pdf")); d.close()

    # a.pdf (2p) and b.pdf (3p), one carrying a bookmark - merge
    for name, n, tag in [("a", 2, "AAA"), ("b", 3, "BBB")]:
        d = pymupdf.open()
        for i in range(n):
            p = d.new_page(width=595, height=842)
            p.insert_text((60, 80), f"{tag} PAGE {i+1}", fontsize=24, fontname="helv")
            p.insert_text((60, 120), f"content of {tag} page {i+1}", fontsize=12)
        d.set_toc([[1, f"{tag} first", 1]])
        d.save(os.path.join(OUT, f"{name}.pdf")); d.close()

    # img.pdf - one large image per page - compress, extract images
    d = pymupdf.open()
    for i, col in enumerate([(220, 80, 80), (80, 160, 220), (90, 190, 120)]):
        p = d.new_page(width=595, height=842)
        pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 300, 200), 0)
        pix.clear_with(col[0]*65536 + col[1]*256 + col[2])
        p.insert_image(pymupdf.Rect(60, 60, 535, 380), pixmap=pix)
        p.insert_text((60, 420), f"image page {i+1}", fontsize=12)
    d.save(os.path.join(OUT, "img.pdf")); d.close()

    # form.pdf - three text fields - fill forms
    d = pymupdf.open()
    p = d.new_page(width=595, height=842)
    p.insert_text((60, 70), "APPLICATION FORM", fontsize=18, fontname="helv")
    for nm, x, y in [("name", 60, 110), ("email", 60, 160), ("city", 60, 210)]:
        p.insert_text((x, y - 6), nm.upper(), fontsize=8)
        w = pymupdf.Widget()
        w.field_name = nm
        w.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
        w.rect = pymupdf.Rect(x, y, x + 300, y + 22)
        p.add_widget(w)
    d.save(os.path.join(OUT, "form.pdf")); d.close()

    # rot.pdf - the same page at rotation 0, 90 and 180 - hyperlinks
    d = pymupdf.open()
    for rot in (0, 90, 180):
        p = d.new_page(width=595, height=842)
        p.insert_text((72, 72), f"ROT {rot} TOP LEFT", fontsize=12, fontname="helv")
        p.insert_text((72, 800), f"ROT {rot} BOTTOM", fontsize=12, fontname="helv")
        p.set_rotation(rot)
    d.save(os.path.join(OUT, "rot.pdf")); d.close()

    # secret.pdf - the same secret on two pages - redact
    d = pymupdf.open()
    for i in range(2):
        p = d.new_page(width=595, height=842)
        p.insert_text((60, 70), "PUBLIC HEADER", fontsize=16, fontname="helv")
        p.insert_text((60, 110), "SECRETCODE-42 appears on this page.", fontsize=12)
        p.insert_text((60, 140), f"page {i+1} ordinary text", fontsize=12)
    d.save(os.path.join(OUT, "secret.pdf")); d.close()

    # page1.png - secret.pdf page 1 rendered by PyMuPDF. The redact painter hands this
    # back, so "the text is gone" is judged against a picture we did not produce.
    d = pymupdf.open(os.path.join(OUT, "secret.pdf"))
    d[0].get_pixmap(dpi=144).save(os.path.join(OUT, "page1.png"))
    d.close()

    print("fixtures written to " + OUT)

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "/tmp/kavopdf-bench/in")
