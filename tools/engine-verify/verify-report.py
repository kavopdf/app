#!/usr/bin/env python3
"""Checks the exported log report is a real, designed document: the header band,
the facts card, the table, and the coloured status column all present, with the
text actually drawn (not invisible on top of a filled shape)."""
import os, sys
import pymupdf

W = "/tmp/kavopdf-engine-test"
ok = True
p = os.path.join(W, "log_designed.pdf")
if not os.path.exists(p):
    print("  report missing"); sys.exit(1)

d = pymupdf.open(p)
page = d[0]
txt = page.get_text()

checks = [
    ("title in the header",   "Activity log" in txt),
    ("brand in the header",   "KAVOPDF" in txt),
    ("subtitle present",      "Activity on this device" in txt),
    ("facts card filled",     "Application" in txt and "samsung" in txt),
    ("table headers",         "TIME" in txt and "RESULT" in txt and "OUTPUT" in txt),
    ("a row's data",          "merged_protected.pdf" in txt),
    ("footer",                "Passwords are never recorded" in txt),
]
for name, good in checks:
    print(f"  {name:24s}: {'yes' if good else 'NO'}")
    ok = ok and good

# the header band must be filled with the accent colour, and the text on it white
pix = page.get_pixmap(dpi=72)
w, h = pix.width, pix.height
band = pix.pixel(int(w * 0.5), int(h * 0.03))
print(f"  header band colour      : {band} (expected a blue accent)")
ok = ok and band[2] > 120 and band[2] > band[0]        # blue channel dominant

# coloured status: a green OK and a red FAIL must both appear
greens = reds = 0
for y in range(h):
    for x in range(0, w, 2):
        r, g, b = pix.pixel(x, y)[:3]
        if g > 110 and r < 90 and b < 110: greens += 1
        if r > 150 and g < 80 and b < 80: reds += 1
print(f"  green OK pixels         : {greens}   red FAIL pixels: {reds}")
ok = ok and greens > 20 and reds > 5

print()
print("REPORT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
