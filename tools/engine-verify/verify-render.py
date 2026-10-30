#!/usr/bin/env python3
"""Independently verifies rotation-aware overlay placement by RENDERING the
output PDFs and checking pixel colours with PyMuPDF."""
import os, sys, tempfile
try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

base = "/tmp/kavopdf-engine-test"
ok = True
for deg in (90, 180, 270):
    path = os.path.join(base, f"stamped{deg}.pdf")
    if not os.path.exists(path):
        print(f"  FAIL  missing {path}")
        ok = False
        continue
    doc = pymupdf.open(path)
    page = doc[0]
    pix = page.get_pixmap(dpi=72)
    w, h = pix.width, pix.height
    tl = pix.pixel(int(w * 0.10), int(h * 0.10))
    tr = pix.pixel(int(w * 0.90), int(h * 0.10))
    bl = pix.pixel(int(w * 0.10), int(h * 0.90))
    br = pix.pixel(int(w * 0.90), int(h * 0.90))
    good = tl == (0, 0, 255) and tr == (255, 255, 255) and bl == (255, 255, 255) and br == (255, 255, 255)
    print(f"  {'PASS' if good else 'FAIL'}  overlay lands correctly on a {deg}-rotated page "
          f"(rot={page.rotation}, {w}x{h})")
    ok = ok and good

# crop: page 1 cropped to the top-left red quadrant, page 2 untouched
crop_path = os.path.join(base, "cropped.pdf")
if os.path.exists(crop_path):
    doc = pymupdf.open(crop_path)
    p1, p2 = doc[0], doc[1]
    pix = p1.get_pixmap(dpi=72)
    tl = pix.pixel(int(pix.width * 0.2), int(pix.height * 0.2))
    c1 = abs(p1.rect.width - 297.5) < 3 and abs(p1.rect.height - 421) < 3
    c2 = tl[0] > 150 and tl[2] < 100
    c3 = abs(p2.rect.width - 595) < 3
    print(f"  {'PASS' if c1 else 'FAIL'}  crop shrinks page 1 to the selected region")
    print(f"  {'PASS' if c2 else 'FAIL'}  cropped page shows only the selected content")
    print(f"  {'PASS' if c3 else 'FAIL'}  crop leaves other pages untouched")
    ok = ok and c1 and c2 and c3
else:
    print("  FAIL  missing cropped.pdf")
    ok = False

sys.exit(0 if ok else 1)
