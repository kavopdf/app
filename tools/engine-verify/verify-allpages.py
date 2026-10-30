#!/usr/bin/env python3
"""Verifies 'same link on every page' by RENDERING.

The icon / text must appear at the SAME spot on the displayed page, on every page,
including a rotated one.
"""
import os, sys
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
K = 150 / 72.0
ok = True

for fname, label, (ex, ey), (ew, eh) in [
    ("ap_out.pdf",  "icon on all pages", (380, 90),  (40, 40)),
    ("ap_out2.pdf", "text on all pages", (120, 500), (86, 30)),
]:
    d = pymupdf.open(os.path.join(W, fname))
    print(f"  {label}: {len(d)} pages")
    for i in range(len(d)):
        p = d[i]
        px = p.get_pixmap(dpi=150, colorspace=pymupdf.csGRAY)
        a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
        reg = a[int(ey * K):int((ey + eh) * K), int(ex * K):int((ex + ew) * K)]
        frac = float((reg < 230).mean()) if reg.size else 0.0
        # control: same box, pushed down but kept inside THIS page (rotated pages differ)
        page_h = px.height / K
        cy = min(ey + 300, page_h - eh - 10)
        ctrl = a[int(cy * K):int((cy + eh) * K), int(ex * K):int((ex + ew) * K)]
        cfrac = float((ctrl < 230).mean()) if ctrl.size else 1.0
        good = frac > 0.15 and cfrac < 0.02
        ok = ok and good
        print(f"    {'PASS' if good else 'FAIL'}  page {i+1} rot={p.rotation:>3}  "
              f"drawn at ({ex},{ey})={frac*100:5.1f}%  elsewhere={cfrac*100:4.1f}%")

print("ALL PAGES:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
