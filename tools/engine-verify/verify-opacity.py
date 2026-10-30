#!/usr/bin/env python3
"""Verifies the link opacity by RENDERING: 40% must be visibly lighter than 100%,
for both the icon and custom text."""
import os, sys
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
name = open(os.path.join(W, "op_name.txt")).read().strip()
d = pymupdf.open(os.path.join(W, name))

def sample(i):
    p = d[i]
    links = p.get_links()
    if not links:
        return None
    r = links[0]["from"]
    px = p.get_pixmap(clip=r, dpi=200)
    a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width, px.n)[:, :, :3].astype(float)
    m = a.mean(axis=2) < 250
    sel = a[m] if m.any() else a.reshape(-1, 3)
    return float((sel.max(axis=1) - sel.min(axis=1)).mean())

labels = ["text 100%", "text 40%", "icon 100%", "icon 40%"]
vals = [sample(i) for i in range(4)]
for lab, v in zip(labels, vals):
    print(f"  {lab:<10} saturation {v:.0f}" if v is not None else f"  {lab:<10} no link")

ok = True
for a, b, what in [(0, 1, "text"), (2, 3, "icon")]:
    if vals[a] is None or vals[b] is None:
        print(f"  FAIL  {what}: missing link"); ok = False; continue
    lighter = vals[b] < vals[a] * 0.75
    ok = ok and lighter
    print(f"  {'PASS' if lighter else 'FAIL'}  {what}: 40% is lighter than 100% ({vals[a]:.0f} -> {vals[b]:.0f})")

print("OPACITY:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
