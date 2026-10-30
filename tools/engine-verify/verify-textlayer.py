#!/usr/bin/env python3
"""Independently verifies the OCR text layer by RENDERING the PDFs.

  measure : renders the source pages and writes the ink line boxes (stand-in for OCR)
  check   : confirms the output is searchable, invisible, and that the placed text
            sits exactly where the ink is - for every page rotation.
"""
import os, sys, tempfile
import numpy as np
import pymupdf

W = "/tmp/kavopdf-engine-test"   # same dir the JVM uses
DPI = int(os.environ.get("TL_DPI", "110"))
K = DPI / 72.0
PW, PH = 595.0, 842.0

def display_to_ink_frame(rot, x0, y0, x1, y1):
    """get_text() gives unrotated page coords; rendering is in the displayed frame."""
    if rot == 90:  return pymupdf.Rect(PH - y1, x0, PH - y0, x1)
    if rot == 180: return pymupdf.Rect(PW - x1, PH - y1, PW - x0, PH - y0)
    if rot == 270: return pymupdf.Rect(y0, PW - x1, y1, PW - x0)
    return pymupdf.Rect(x0, y0, x1, y1)

def measure():
    d = pymupdf.open(os.path.join(W, "tl_src.pdf"))
    out = []
    for i in range(len(d)):
        p = d[i]
        pix = p.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        rows = np.where((a < 140).any(axis=1))[0]
        if len(rows) == 0:
            continue
        # group contiguous ink rows into lines
        groups, start, prev = [], rows[0], rows[0]
        for r in rows[1:]:
            if r - prev > 6:
                groups.append((start, prev)); start = r
            prev = r
        groups.append((start, prev))
        for (y0, y1) in groups:
            band = a[y0:y1 + 1]
            cols = np.where(band.any(axis=0))[0]
            x0, x1 = cols[0], cols[-1]
            out.append(f"{i+1}\t{pix.width}\t{pix.height}\t{x0:.1f}\t{y0:.1f}\t"
                       f"{x1-x0:.1f}\t{y1-y0:.1f}\tline {i+1}-{len(groups)}")
    open(os.path.join(W, "tl_words.tsv"), "w").write("\n".join(out))
    print(f"  measured {len(out)} ink lines across {len(d)} pages")
    return 0

def check():
    d = pymupdf.open(os.path.join(W, "tl_out.pdf"))
    src = pymupdf.open(os.path.join(W, "tl_src.pdf"))
    ok = True
    for i in range(len(d)):
        p = d[i]; r = p.rotation
        ws = p.get_text("words")
        txt = p.get_text().strip()
        raw = b"".join(d.xref_stream(x) for x in p.get_contents()).decode("latin-1")
        invisible = "3 Tr" in raw
        fr, ct = [], []
        for w in ws:
            b = display_to_ink_frame(r, w[0], w[1], w[2], w[3])
            fr.append(_ink(p, b))
            ct.append(_ink(p, pymupdf.Rect(b.x0, b.y0 + 120, b.x1, b.y1 + 120)))
        avg = sum(fr) / len(fr) if fr else 0.0
        cavg = sum(ct) / len(ct) if ct else 0.0
        searchable = len(ws) >= 6 and "Searchable" in txt and "Amount" in txt
        placed = avg > 0.05 and avg > cavg * 2
        # the page must render exactly as it did before
        a = src[i].get_pixmap(dpi=40).samples
        b = p.get_pixmap(dpi=40).samples
        same = sum(1 for k in range(min(len(a), len(b))) if abs(a[k] - b[k]) > 8) < len(a) * 0.002
        good = invisible and searchable and placed and same
        ok = ok and good
        print(f"  page {i+1} rot={r:>3}  searchable={searchable} invisible={invisible} "
              f"on-ink={avg*100:.1f}% (control {cavg*100:.1f}%) unchanged={same}  {'PASS' if good else 'FAIL'}")
    print("TEXT LAYER:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

def _ink(page, rect, dpi=220):
    px = page.get_pixmap(clip=rect, dpi=dpi, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
    return float((a < 140).mean()) if a.size else 0.0

sys.exit(measure() if sys.argv[1] == "measure" else check())
