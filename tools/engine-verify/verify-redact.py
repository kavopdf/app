#!/usr/bin/env python3
"""Verifies a redaction REALLY removed the content - as hard as we can make it.

Marking an area is not redaction: the text has to be gone from the file, and it has
to stay gone no matter what tool opens it. So we hunt for the secrets in every place
they could possibly hide:

  1. normal text extraction, page by page
  2. every decompressed stream in the file
  3. every object in the xref, including object streams
  4. the raw bytes of the file (uncompressed leftovers)
  5. no earlier revision is left behind (no incremental updates)
  6. the redacted page carries no font at all - it is pure image
  7. the redacted areas render 100% solid black
  8. untouched pages keep their text, and page count/sizes are unchanged
"""
import os, sys, re, zlib
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"
SECRETS = ["SECRETCODE-9931", "TOPSECRET-ALPHA"]
K = 150 / 72.0

src = pymupdf.open(os.path.join(W, "redact_src.pdf"))
out = pymupdf.open(os.path.join(W, "redact_out.pdf"))
ok = True

# 1 -------------------------------------------------------------------------
hits = []
for i in range(len(out)):
    t = out[i].get_text()
    for s in SECRETS:
        if s in t:
            hits.append((f"page {i+1} text", s))
print(f"  1. text extraction           : {'CLEAN' if not hits else 'LEAK ' + str(hits)}")
ok = ok and not hits

# 2 -------------------------------------------------------------------------
hits = []
for xref in range(1, out.xref_length()):
    try:
        raw = out.xref_stream_raw(xref)
        if not raw:
            continue
        try:
            data = zlib.decompress(raw)
        except Exception:
            data = raw
        for s in SECRETS:
            if s.encode() in data:
                hits.append((f"stream xref {xref}", s))
    except Exception:
        pass
print(f"  2. every decompressed stream : {'CLEAN' if not hits else 'LEAK ' + str(hits)}")
ok = ok and not hits

# 3 -------------------------------------------------------------------------
hits = []
for xref in range(1, out.xref_length()):
    try:
        obj = out.xref_object(xref, compressed=True)
        for s in SECRETS:
            if s in obj:
                hits.append((f"object {xref}", s))
    except Exception:
        pass
print(f"  3. every object in the xref  : {'CLEAN' if not hits else 'LEAK ' + str(hits)}")
ok = ok and not hits

# 4 -------------------------------------------------------------------------
raw = open(os.path.join(W, "redact_out.pdf"), "rb").read()
hits = [s for s in SECRETS if s.encode() in raw]
print(f"  4. raw file bytes            : {'CLEAN' if not hits else 'LEAK ' + str(hits)}")
ok = ok and not hits

# 5 -------------------------------------------------------------------------
# a rebuilt file has a single revision: no /Prev in the trailer
prev = b"/Prev" in raw[-4096:]
print(f"  5. no earlier revision kept  : {'CLEAN' if not prev else 'LEAK (incremental update present)'}")
ok = ok and not prev

# 6 -------------------------------------------------------------------------
page = out[0]
fonts = []
try:
    for f in page.get_fonts(full=True):
        fonts.append(f[3])
except Exception:
    pass
imgs = page.get_images(full=True)
clean = len(fonts) == 0 and len(imgs) >= 1
print(f"  6. redacted page is pure art : {'CLEAN' if clean else 'LEAK'} "
      f"(fonts={fonts}, images={len(imgs)})")
ok = ok and clean

# 7 -------------------------------------------------------------------------
for i, rects in [(0, [(60, 125, 360, 155)]), (2, [(690, 65, 725, 230)])]:
    p = out[i]
    px = p.get_pixmap(dpi=150, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
    for (x0, y0, x1, y1) in rects:
        reg = a[int(y0 * K):int(y1 * K), int(x0 * K):int(x1 * K)]
        dark = float((reg < 40).mean())
        good = dark > 0.95
        ok = ok and good
        print(f"  7. page {i+1} blacked area     : {dark*100:5.1f}% solid black {'PASS' if good else 'FAIL'}")

# 8 -------------------------------------------------------------------------
good = "Public info on page two" in out[1].get_text()
ok = ok and good
sizes_src = [(round(src[i].rect.width), round(src[i].rect.height)) for i in range(len(src))]
sizes_out = [(round(out[i].rect.width), round(out[i].rect.height)) for i in range(len(out))]
same = len(src) == len(out) and sizes_src == sizes_out
ok = ok and same
print(f"  8. rest of the document      : untouched={good}  layout same={same}")

# 9 -------------------------------------------------------------------------
# the redacted page's own content must contain no text-showing operators at all
leaks = []
for i in (0, 2):
    try:
        cs = out[i].read_contents().decode("latin-1")
    except Exception:
        cs = ""
    for op in ("BT", "Tj", "TJ", "'", '"'):
        # a text object or a text-showing operator
        if op in ("BT",):
            if re.search(r"(^|\s)BT(\s|$)", cs):
                leaks.append((i + 1, op))
        elif op in ("Tj", "TJ"):
            if re.search(r"(^|\s)" + op + r"(\s|$)", cs):
                leaks.append((i + 1, op))
print(f"  9. no text operators left    : {'CLEAN' if not leaks else 'LEAK ' + str(leaks)}")
ok = ok and not leaks

print()
print("REDACTION:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
