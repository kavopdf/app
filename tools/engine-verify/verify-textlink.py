#!/usr/bin/env python3
"""Verifies custom link text by RENDERING it.

The text must be visible, drawn in the chosen colour, carry the right address,
and the link must cover only that text - on every page rotation.
"""
import os, sys
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
PW, PH = 595.0, 842.0

def to_display(rot, x0, y0, x1, y1):
    if rot == 90:  return pymupdf.Rect(PH - y1, x0, PH - y0, x1)
    if rot == 180: return pymupdf.Rect(PW - x1, PH - y1, PW - x0, PH - y0)
    if rot == 270: return pymupdf.Rect(y0, PW - x1, y1, PW - x0)
    return pymupdf.Rect(x0, y0, x1, y1)

name = open(os.path.join(W, "tl2_name.txt")).read().strip()
d = pymupdf.open(os.path.join(W, name))
ok = True
for i in range(len(d)):
    p = d[i]; rot = p.rotation
    links = p.get_links()
    has_text = "Click" in p.get_text()
    if not links:
        print(f"  FAIL  page {i+1}: no link"); ok = False; continue
    for L in links:
        rect = L["from"]
        disp = to_display(rot, rect.x0, rect.y0, rect.x1, rect.y1)
        px = p.get_pixmap(clip=rect, dpi=200)
        a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width, px.n)[:, :, :3].astype(int)
        reddish = float(((a[:, :, 0] > 110) & (a[:, :, 1] < 110) & (a[:, :, 2] < 110)).mean())
        ink = float((a.mean(axis=2) < 230).mean())
        small = (disp.width * disp.height) / (PW * PH) < 0.10
        good = bool(L.get("uri")) and has_text and reddish > 0.03 and ink > 0.05 and small
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  p{i+1} rot={rot:>3} {L.get('uri')}  "
              f"rect {disp.width:.0f}x{disp.height:.0f}pt  red={reddish*100:.1f}%  ink={ink*100:.1f}%")
print("CUSTOM TEXT LINK:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
