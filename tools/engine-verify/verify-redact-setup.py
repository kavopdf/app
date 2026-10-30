#!/usr/bin/env python3
"""Builds the redaction fixture: a 3 page PDF with two secrets, plus the rendered
page images and the areas to blacken (standing in for the app's Canvas)."""
import os
import pymupdf

W = "/tmp/kavopdf-engine-test"
os.makedirs(W, exist_ok=True)
DPI = 150
K = DPI / 72.0

d = pymupdf.open()
p = d.new_page(width=595, height=842)
p.insert_text((72, 700), "SECRETCODE-9931 confidential", fontsize=14)
p.insert_text((72, 740), "Public info on page one", fontsize=14)
p2 = d.new_page(width=595, height=842)
p2.insert_text((72, 700), "Public info on page two", fontsize=14)
p3 = d.new_page(width=595, height=842)
p3.set_rotation(90)
p3.insert_text((72, 700), "TOPSECRET-ALPHA hidden", fontsize=14)
p3.insert_text((72, 740), "Public rotated page", fontsize=14)
d.save(os.path.join(W, "redact_src.pdf"))
d.close()

spec = []
for pno, rects in [(1, [(60, 125, 360, 155)]), (3, [(690, 65, 725, 230)])]:
    doc = pymupdf.open(os.path.join(W, "redact_src.pdf"))
    pix = doc[pno - 1].get_pixmap(dpi=DPI)
    png = os.path.join(W, f"redact_p{pno}.png")
    pix.save(png)
    doc.close()
    row = [str(pno), png, str(K)]
    for r in rects:
        row += [str(v) for v in r]
    spec.append("\t".join(row))
open(os.path.join(W, "redact_spec.tsv"), "w").write("\n".join(spec))
print("redaction fixture ready")
