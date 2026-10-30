#!/usr/bin/env python3
"""Verifies the text used for tap-to-copy: every word box must sit on real ink,
and the page text must match what is on the page."""
import os, sys
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
K = 150 / 72.0
d = pymupdf.open(os.path.join(W, "copy_src.pdf"))
p = d[0]
px = p.get_pixmap(dpi=150, colorspace=pymupdf.csGRAY)
ink = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width) < 140

ok = True
n = 0
for line in open(os.path.join(W, "copy_out.tsv")):
    f = line.rstrip("\n").split("\t")
    if f[0] == "WORD":
        x, y, w, h = float(f[2]), float(f[3]), float(f[4]), float(f[5])
        frac = float(ink[int(y * K):int((y + h) * K), int(x * K):int((x + w) * K)].mean())
        n += 1
        good = frac > 0.10
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  '{f[6]}' ink={frac*100:5.1f}%")
    elif f[0] == "PAGETEXT":
        text = f[1]
        want = "Hello world from KavoPDF|second line of text"
        good = text == want
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  page text: '{text}'")
print(f"  {n} word box(es) checked")
print("COPY TEXT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
