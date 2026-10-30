#!/usr/bin/env python3
"""Independently verifies text search and hyperlinks by RENDERING the PDFs.

Search hits must sit on real ink in the displayed page; link annotations must
carry the right URI and cover the text they claim to cover.
"""
import os, sys
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
DPI = 150
K = DPI / 72.0

def ink_maps(path):
    d = pymupdf.open(path)
    out = {}
    for i in range(len(d)):
        px = d[i].get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
        out[i + 1] = (np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width) < 140,
                      px.width, px.height)
    return d, out

def frac(maps, page, x, y, w, h):
    m, pw, ph = maps[page]
    a, b = max(0, int(x * K)), max(0, int(y * K))
    c, dd = min(pw, int((x + w) * K)), min(ph, int((y + h) * K))
    return float(m[b:dd, a:c].mean()) if c > a and dd > b else 0.0

ok = True
src = pymupdf.open(os.path.join(W, "search_src.pdf"))
_, maps = ink_maps(os.path.join(W, "search_src.pdf"))
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(W, "search_results.tsv"))]
searches = [(int(f[1]), float(f[2]), float(f[3]), float(f[4]), float(f[5]), f[6])
            for f in rows if f[0] == "SEARCH"]
print(f"  search: {len(searches)} hit(s)")
for (page, x, y, w, h, q) in searches:
    f = frac(maps, page, x, y, w, h)
    ph = maps[page][2] / K
    c = frac(maps, page, x, min(y + 300, ph - h - 10), w, h)
    good = f > 0.10 and c < 0.02
    ok = ok and good
    print(f"    {'PASS' if good else 'FAIL'}  p{page} '{q}' on ink={f*100:5.1f}%  blank={c*100:4.1f}%")

dl = pymupdf.open(os.path.join(W, "search_links.pdf"))
links = 0
for i in range(len(dl)):
    for L in dl[i].get_links():
        links += 1
        r = L["from"]
        px = dl[i].get_pixmap(clip=r, dpi=200, colorspace=pymupdf.csGRAY)
        a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
        f = float((a < 140).mean()) if a.size else 0.0
        good = bool(L.get("uri")) and f > 0.05
        ok = ok and good
        print(f"    {'PASS' if good else 'FAIL'}  p{i+1} {L.get('uri')}  ink under link={f*100:.1f}%")
if links == 0:
    print("    FAIL  no links were added"); ok = False

print("SEARCH + LINKS:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
