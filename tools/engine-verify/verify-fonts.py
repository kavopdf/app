#!/usr/bin/env python3
"""Confirms the font chosen for a watermark and for custom link text really
lands in the PDF - checked by an independent library reading the font table."""
import os, sys
import pymupdf

W = "/tmp/kavopdf-engine-test"
ok = True
want = [("font_wm_0.pdf", "Helvetica"), ("font_wm_1.pdf", "Helvetica-Bold"),
        ("font_wm_2.pdf", "Times-Roman"), ("font_wm_3.pdf", "Times-Bold"),
        ("font_wm_4.pdf", "Courier"),
        ("font_link_one.pdf", "Times-Roman"), ("font_link_all.pdf", "Courier")]
for name, expected in want:
    p = os.path.join(W, name)
    if not os.path.exists(p):
        print(f"  {name:22s}: missing"); ok = False; continue
    d = pymupdf.open(p)
    names = sorted({f[3] for f in d[0].get_fonts()})
    good = any(expected in n for n in names)
    print(f"  {name:22s}: {expected:14s} -> {names}  {'OK' if good else 'MISSING'}")
    ok = ok and good
print()
print("FONTS:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
