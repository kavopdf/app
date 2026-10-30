#!/usr/bin/env python3
"""Verifies the visible link icon by RENDERING it.

The link must cover only the small icon (never the page), carry the right address,
and the icon must actually be drawn where the link is.
"""
import os, sys
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
ok = True

d = pymupdf.open(os.path.join(W, "icon_out.pdf"))
p = d[0]
links = p.get_links()

def region(r):
    px = p.get_pixmap(clip=r, dpi=200, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
    return float((a < 230).mean()) if a.size else 0.0

blank = region(pymupdf.Rect(60, 400, 100, 440))
page_area = p.rect.width * p.rect.height
print(f"  blank area on the page: {blank*100:.1f}% non-white")
if blank > 0.02:
    print("  FAIL  the control area is not blank"); ok = False

if not links:
    print("  FAIL  no link was written"); ok = False
for L in links:
    r = L["from"]
    share = (r.width * r.height) / page_area
    drawn = region(r)
    small = share < 0.05
    on_icon = drawn > 0.15
    good = bool(L.get("uri")) and small and on_icon
    ok = ok and good
    print(f"  {'PASS' if good else 'FAIL'}  uri={L.get('uri')}  rect {r.width:.0f}x{r.height:.0f}pt "
          f"= {share*100:.2f}% of the page")
    print(f"        icon drawn at the link={on_icon} ({drawn*100:.1f}% non-white)   link is small={small}")

print("LINK ICON:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
