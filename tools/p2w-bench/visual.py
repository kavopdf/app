#!/usr/bin/env python3
"""
visual.py - a per-page visual comparator for the PDF to Word engine.

The twelve classes in detect.py read the .docx as XML: they can tell that a paragraph is
missing or a shape is absent, but they cannot tell that the page came out black, or that a
solid slab was painted over the invoice. This tool renders both sides and looks at the
pixels.

    PDF page  --PyMuPDF, 100 dpi-->  PNG
    .docx     --LibreOffice--> PDF --PyMuPDF, 100 dpi-->  PNG

Both rasters are aligned on page size and compared page by page. Four classes:

    INK_MISSING   share of the PDF's dark pixels with no dark pixel in the docx within a
                  small radius. Text, or a rule, that never arrived.
    INK_EXTRA     share of the docx's dark pixels with no dark pixel in the PDF within the
                  same radius. A block, band or shape that should not be there.
    BLOCK         a contiguous docx region of one colour, over 2000 pt2, where the PDF has
                  a different colour. Two sub-kinds, both literally that:
                    BLOCK fill   a flat region of the rendered page that the PDF does not
                                 have (a slab, a band, a painted-over area)
                    BLOCK shape  a wps shape in the .docx whose own paint does not match
                                 the PDF - an axis-aligned rect emitted where the PDF
                                 draws something else (the stamp-slab defect)
    BACKGROUND    the docx page's modal colour differs from the PDF page's, or the page
                  declares no fill at all, so the viewer's own surface shows through it
                  (the black-screen defect)

Every page is printed, with numbers, whether or not it fires. A single score is exactly
what let four broken builds ship.

Usage
    python3 visual.py --pdf <dir> --docx <dir> [--report FILE] [--json FILE]
                      [--only NAME] [--lo-dir DIR] [--dpi 100] [--keep-png DIR]

The .docx files are converted in batches by one LibreOffice process; --lo-dir reuses a
previous conversion so a re-measurement does not pay for it again.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
from PIL import Image, ImageFilter

try:
    import pymupdf as fitz
except ImportError:  # older wheels
    import fitz

# --------------------------------------------------------------------------- thresholds
DPI = 100
PX_PER_PT = DPI / 72.0

# A pixel is "dark" when its luminance is below this. Red 191,13,13 is 66, so stamps and
# coloured headings count; the light greys the engine uses for bands (229,234,244 = 232)
# do not.
DARK_LUMA = 128

# Two dark pixels are "the same ink" if they are within this many pixels of each other.
# 3 px at 100 dpi is 2.2 pt - enough to absorb the sub-2 pt baseline drift LibreOffice
# introduces when it substitutes a font, and far too little to hide a missing line.
INK_RADIUS_PX = 3

# A page fires INK_MISSING / INK_EXTRA when this share of its own dark pixels is unmatched.
INK_PCT = 1.0

BLOCK_MIN_PT2 = 2000.0     # the size a region must reach to be a block, not ink
BLOCK_DCOL = 40            # per-channel difference that counts as "a different colour"
BLOCK_DIFF_SHARE = 0.25    # the PDF must have this much more off-colour than the docx
BLOCK_INSET_PT = 2.0       # ignore a block's own edge: 2 pt of drift is not a defect
BLOCK_SHAPE_HIT = 0.50     # share of a shape's own paint that must disagree with the PDF
BLOCK_FRAME_DOCX = 0.80    # a frame the docx draws covers this much of its box
BLOCK_FRAME_PDF = 0.35     # ...and the PDF has almost nothing there
MATCH_SLOP_PX = 0          # 0 keeps a one-pixel glyph stroke from being absorbed
BACKGROUND_DCOL = 24       # per-channel difference on the page surface

# A colour component smaller than this share of the page is not considered as a slab.
BLOCK_MIN_PAGE_SHARE = 0.002

EMU_PER_PT = 12700.0


# ------------------------------------------------------------------------------- helpers
def luma(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def to_array(pix):
    a = np.frombuffer(pix.samples, dtype=np.uint8)
    a = a.reshape(pix.height, pix.width, pix.n)
    return a[:, :, :3].astype(np.int16)


def render_pdf_pages(path, dpi=DPI):
    """Every page of a PDF as an (h, w, 3) array."""
    doc = fitz.open(path)
    out = []
    try:
        for page in doc:
            out.append(to_array(page.get_pixmap(dpi=dpi)))
    finally:
        doc.close()
    return out


def modal_colour(arr):
    """The most common colour of an image, as an (r, g, b) tuple."""
    flat = arr.reshape(-1, 3)
    key = (flat[:, 0].astype(np.int32) << 16) | (flat[:, 1].astype(np.int32) << 8) | flat[:, 2]
    vals, counts = np.unique(key, return_counts=True)
    v = int(vals[int(counts.argmax())])
    return ((v >> 16) & 255, (v >> 8) & 255, v & 255)


def hexs(rgb):
    if rgb is None:
        return "none"
    return "#%02X%02X%02X" % tuple(int(c) for c in rgb)


def dcol(a, b):
    """Largest per-channel difference between two colours."""
    return max(abs(int(a[i]) - int(b[i])) for i in range(3))


def pad_to(arr, h, w, fill):
    """Grow an image to (h, w) at its top-left corner, filling with `fill`."""
    if arr.shape[0] == h and arr.shape[1] == w:
        return arr
    out = np.empty((h, w, 3), dtype=np.int16)
    out[:, :] = fill
    out[:arr.shape[0], :arr.shape[1]] = arr
    return out


def dilate(mask, radius):
    """Binary dilation by a (2r+1)^2 square, via PIL so it stays in C."""
    if radius <= 0:
        return mask
    im = Image.fromarray((mask * 255).astype(np.uint8))
    im = im.filter(ImageFilter.MaxFilter(2 * radius + 1))
    return np.asarray(im) > 0


def label_components(mask):
    """Connected components (4-neighbour) of a boolean mask.

    Run-length encoding plus union-find: linear in the number of runs, no scipy needed.
    Returns (labels, count) with labels 0 = background.
    """
    h, w = mask.shape
    parent = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    labels = np.zeros((h, w), dtype=np.int32)
    prev_runs = []
    next_id = 0
    for y in range(h):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.nonzero(d == 1)[0]
        ends = np.nonzero(d == -1)[0]
        runs = []
        for s, e in zip(starts, ends):
            rid = next_id
            next_id += 1
            parent.append(rid)
            labels[y, s:e] = rid + 1
            runs.append((s, e, rid))
        # union with the runs of the previous row that overlap
        for s, e, rid in runs:
            for ps, pe, prid in prev_runs:
                if ps < e and s < pe:
                    union(rid, prid)
        prev_runs = runs

    if next_id == 0:
        return labels, 0
    roots = {}
    for i in range(next_id):
        r = find(i)
        if r not in roots:
            roots[r] = len(roots) + 1
    remap = np.zeros(next_id + 1, dtype=np.int32)
    for i in range(next_id):
        remap[i + 1] = roots[find(i)]
    labels = remap[labels]
    return labels, len(roots)


# ------------------------------------------------------------------------ docx reading
def docx_page_fill(docx_path):
    """The colour the .docx declares for the page, or None when it declares none."""
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    m = re.search(r'<w:background\b[^>]*w:color="([0-9A-Fa-f]{6})"', xml)
    if m:
        v = m.group(1)
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    m = re.search(r'<w:background\b', xml)
    if m:
        return None  # declared but with no colour: same as undeclared
    return None


def docx_shapes(docx_path):
    """Every drawing in the .docx that paints something, with its page-relative box.

    Each entry: dict(x, y, w, h in pt, fill=rgb or None, line=rgb or None, linew=pt)
    """
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    out = []
    for m in re.finditer(r"<w:drawing>(.*?)</w:drawing>", xml, re.S):
        d = m.group(1)
        ph = re.search(r'<wp:positionH relativeFrom="page"><wp:posOffset>(-?\d+)</wp:posOffset>', d)
        pv = re.search(r'<wp:positionV relativeFrom="page"><wp:posOffset>(-?\d+)</wp:posOffset>', d)
        ext = re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"', d)
        if not (ph and pv and ext):
            continue
        wps = re.search(r"<wps:wsp>(.*?)</wps:wsp>", d, re.S)
        fill = line = None
        linew = 0.0
        if wps:
            s = wps.group(1)
            sppr = s.split("<wps:txbx")[0]
            ln_m = re.search(r"<a:ln\b([^>]*)>(.*?)</a:ln>", sppr, re.S)
            body = sppr
            if ln_m:
                body = sppr[: ln_m.start()]
                lw = re.search(r'w="(\d+)"', ln_m.group(1))
                linew = int(lw.group(1)) / EMU_PER_PT if lw else 0.75
                lc = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', ln_m.group(2))
                if lc and "<a:noFill/>" not in ln_m.group(2):
                    line = tuple(int(lc.group(1)[i:i + 2], 16) for i in (0, 2, 4))
            fc = re.search(r'<a:solidFill><a:srgbClr val="([0-9A-Fa-f]{6})"', body)
            if fc and "<a:noFill/>" not in body:
                v = fc.group(1)
                fill = (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
        if fill is None and line is None:
            continue
        out.append(dict(
            x=int(ph.group(1)) / EMU_PER_PT,
            y=int(pv.group(1)) / EMU_PER_PT,
            w=int(ext.group(1)) / EMU_PER_PT,
            h=int(ext.group(2)) / EMU_PER_PT,
            fill=fill, line=line, linew=linew,
        ))
    return out


# ----------------------------------------------------------------- LibreOffice plumbing
def docx_to_pdf(docx_paths, outdir, batch=18):
    """Convert .docx to .pdf with one LibreOffice process per batch."""
    os.makedirs(outdir, exist_ok=True)
    todo = []
    for p in docx_paths:
        stem = os.path.splitext(os.path.basename(p))[0]
        target = os.path.join(outdir, stem + ".pdf")
        if not (os.path.exists(target) and os.path.getsize(target) > 0):
            todo.append(p)
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        cmd = ["soffice", "--headless", "--norestore", "--convert-to", "pdf",
               "--outdir", outdir] + chunk
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=280)
        if r.returncode != 0:
            sys.stderr.write("  libreoffice batch %d failed: %s\n" % (i, r.stderr[-400:]))
    return {os.path.splitext(os.path.basename(p))[0]: os.path.join(
        outdir, os.path.splitext(os.path.basename(p))[0] + ".pdf") for p in docx_paths}


# ------------------------------------------------------------------------- the analysis
def page_report(pdf_arr, docx_arr, page_no, pdf_rect, docx_rect, shapes, declared_fill):
    """Compare one page. Returns a dict of findings, all in points."""
    # --- align on page size -------------------------------------------------------
    fill_pdf = modal_colour(pdf_arr)
    fill_docx = modal_colour(docx_arr)
    h = max(pdf_arr.shape[0], docx_arr.shape[0])
    w = max(pdf_arr.shape[1], docx_arr.shape[1])
    a = pad_to(pdf_arr, h, w, fill_pdf)
    b = pad_to(docx_arr, h, w, fill_docx)

    rec = dict(page=page_no, pdf_pt=[round(pdf_rect[0], 1), round(pdf_rect[1], 1)],
               docx_pt=[round(docx_rect[0], 1), round(docx_rect[1], 1)],
               size_delta_pt=[round(abs(pdf_rect[0] - docx_rect[0]), 1),
                              round(abs(pdf_rect[1] - docx_rect[1]), 1)],
               pdf_modal=list(fill_pdf), docx_modal=list(fill_docx),
               declared_fill=list(declared_fill) if declared_fill else None,
               findings=[])

    # --- INK_MISSING / INK_EXTRA --------------------------------------------------
    dark_pdf = luma(a) < DARK_LUMA
    dark_docx = luma(b) < DARK_LUMA
    npdf, ndocx = int(dark_pdf.sum()), int(dark_docx.sum())

    if npdf:
        covered = dilate(dark_docx, INK_RADIUS_PX)[dark_pdf]
        miss = int((~covered).sum())
        miss_pct = 100.0 * miss / npdf
        rec["ink_missing_pct"] = round(miss_pct, 2)
        rec["ink_missing_px"] = [miss, npdf]
        if miss_pct >= INK_PCT:
            ys, xs = np.nonzero(dark_pdf & ~dilate(dark_docx, INK_RADIUS_PX))
            rec["findings"].append(dict(
                cls="INK_MISSING", pct=round(miss_pct, 2),
                at=_box_pt(xs, ys),
                detail="%d of %d dark PDF px have no docx ink within %.0f px"
                       % (miss, npdf, INK_RADIUS_PX)))
    else:
        rec["ink_missing_pct"] = 0.0
        rec["ink_missing_px"] = [0, 0]

    if ndocx:
        covered = dilate(dark_pdf, INK_RADIUS_PX)[dark_docx]
        extra = int((~covered).sum())
        extra_pct = 100.0 * extra / ndocx
        rec["ink_extra_pct"] = round(extra_pct, 2)
        rec["ink_extra_px"] = [extra, ndocx]
        if extra_pct >= INK_PCT:
            ys, xs = np.nonzero(dark_docx & ~dilate(dark_pdf, INK_RADIUS_PX))
            rec["findings"].append(dict(
                cls="INK_EXTRA", pct=round(extra_pct, 2),
                at=_box_pt(xs, ys),
                detail="%d of %d dark DOCX px have no PDF ink within %.0f px"
                       % (extra, ndocx, INK_RADIUS_PX)))
    else:
        rec["ink_extra_pct"] = 0.0
        rec["ink_extra_px"] = [0, 0]

    # --- BLOCK, kind 1: a flat region of the rendered page -------------------------
    rec["blocks"] = _flat_blocks(a, b, fill_docx)

    # --- BLOCK, kind 2: a wps shape whose own paint disagrees with the PDF ---------
    rec["blocks"] += _shape_blocks(a, b, shapes, fill_pdf, fill_docx)

    for blk in rec["blocks"]:
        rec["findings"].append(dict(cls="BLOCK", pct=None, at=blk["at"], detail=blk["detail"]))

    # --- BACKGROUND ----------------------------------------------------------------
    bg = _background(a, b, fill_pdf, fill_docx, declared_fill)
    rec["background"] = bg
    if bg["fired"]:
        rec["findings"].append(dict(cls="BACKGROUND", pct=None, at="page",
                                    detail=bg["detail"]))
    return rec


def _box_pt(xs, ys):
    return [round(float(xs.min()) / PX_PER_PT, 1), round(float(ys.min()) / PX_PER_PT, 1),
            round(float(xs.max()) / PX_PER_PT, 1), round(float(ys.max()) / PX_PER_PT, 1)]


def _flat_blocks(pdf_arr, docx_arr, page_fill):
    """Flat regions of the docx page that the PDF does not have.

    Quantise both to a coarse palette, take connected components of each docx colour,
    and keep the ones over BLOCK_MIN_PT2 whose PDF pixels are materially more off-colour
    than the docx's own are. Comparing "how much off-colour" rather than the modal colour
    is what keeps a text box - white behind black glyphs on both sides - from firing.
    """
    found = []
    h, w, _ = docx_arr.shape
    # work at quarter resolution: 1 cell = 2.88 pt, so 2000 pt2 = 241 cells
    small = np.asarray(Image.fromarray(docx_arr.astype(np.uint8)).resize(
        (max(1, w // 4), max(1, h // 4)), Image.BOX)).astype(np.int16)
    sh, sw, _ = small.shape
    q = (small // 24) * 24                       # 11 levels per channel
    key = (q[:, :, 0].astype(np.int32) << 16) | (q[:, :, 1].astype(np.int32) << 8) | q[:, :, 2]
    vals, counts = np.unique(key, return_counts=True)
    min_cells = max(2, int(BLOCK_MIN_PAGE_SHARE * sh * sw))
    order = np.argsort(counts)[::-1]

    for idx in order:
        if counts[idx] < min_cells:
            break
        mask = key == vals[idx]
        labels, n = label_components(mask)
        if n == 0:
            continue
        for comp in range(1, n + 1):
            ys, xs = np.nonzero(labels == comp)
            if len(xs) < 6:
                continue
            x0, x1 = int(xs.min()) * 4, int(xs.max() + 1) * 4
            y0, y1 = int(ys.min()) * 4, int(ys.max() + 1) * 4
            x1, y1 = min(x1, w), min(y1, h)
            area_pt2 = ((x1 - x0) / PX_PER_PT) * ((y1 - y0) / PX_PER_PT)
            if area_pt2 < BLOCK_MIN_PT2:
                continue
            # the page surface is not a block
            if (x1 - x0) * (y1 - y0) > 0.25 * w * h and dcol(page_fill, _cell_colour(small, xs, ys)) <= BLOCK_DCOL:
                continue
            # Inset by BLOCK_INSET_PT so a table rule or a band edge sitting a point or
            # two off does not make a matching region look different.
            i = int(round(BLOCK_INSET_PT * PX_PER_PT))
            ix0, iy0, ix1, iy1 = x0 + i, y0 + i, x1 - i, y1 - i
            if ix1 - ix0 < 8 or iy1 - iy0 < 8:
                ix0, iy0, ix1, iy1 = x0, y0, x1, y1
            reg_d = docx_arr[iy0:iy1, ix0:ix1].reshape(-1, 3)
            reg_p = pdf_arr[iy0:iy1, ix0:ix1].reshape(-1, 3)
            if len(reg_d) == 0:
                continue
            c_d = modal_colour(reg_d.reshape(1, -1, 3))
            c_p = modal_colour(reg_p.reshape(1, -1, 3))
            off_d = float((np.abs(reg_d - np.array(c_d)).max(axis=1) > BLOCK_DCOL).mean())
            # The PDF side is allowed MATCH_SLOP_PX of drift before a pixel counts as
            # off-colour, so a band drawn one point lower is not called a defect.
            close_p = (np.abs(pdf_arr[iy0:iy1, ix0:ix1] - np.array(c_d)).max(axis=2)
                       <= BLOCK_DCOL)
            off_p = float((~dilate(close_p, MATCH_SLOP_PX)).mean())
            if dcol(c_d, c_p) > BLOCK_DCOL or (off_p - off_d) > BLOCK_DIFF_SHARE:
                found.append(dict(
                    kind="fill",
                    at=[round(x0 / PX_PER_PT, 1), round(y0 / PX_PER_PT, 1),
                        round(x1 / PX_PER_PT, 1), round(y1 / PX_PER_PT, 1)],
                    area_pt2=round(area_pt2),
                    docx=hexs(c_d), pdf=hexs(c_p),
                    detail="flat %s region %.0fx%.0f pt (%d pt2) at (%.0f,%.0f); "
                           "PDF is %s there, and %.0f%% of the PDF inside it is neither"
                           % (hexs(c_d), (x1 - x0) / PX_PER_PT, (y1 - y0) / PX_PER_PT,
                              area_pt2, x0 / PX_PER_PT, y0 / PX_PER_PT, hexs(c_p),
                              off_p * 100)))
    return found


def _cell_colour(small, xs, ys):
    px = small[ys, xs]
    return tuple(int(v) for v in np.median(px, axis=0))


def _ring_coverage(arr, box, bg, t):
    """Share of a rectangle's four edges that carry ink.

    Measured the same way on both rasters, so a frame drawn on one side and absent on the
    other is a straight comparison. A sub-point wps line renders at ~50% coverage and is
    still ink; that is why the test is "differs from the page surface", not "matches the
    declared colour".
    """
    x0, y0, x1, y1 = box
    reg = arr[y0:y1, x0:x1]
    ink = np.abs(reg - np.array(bg)).max(axis=2) > BLOCK_DCOL
    if ink.size == 0:
        return 0.0
    top = ink[:t, :].any(axis=0)
    bot = ink[-t:, :].any(axis=0)
    lef = ink[:, :t].any(axis=1)
    rig = ink[:, -t:].any(axis=1)
    return float((top.mean() + bot.mean() + lef.mean() + rig.mean()) / 4.0)


def _shape_blocks(pdf_arr, docx_arr, shapes, page_fill_pdf, page_fill_docx):
    """A wps shape over BLOCK_MIN_PT2 whose paint the PDF does not have.

    A rotated rectangle cannot be an axis-aligned wps rect: emitting its bounding box
    paints a straight red frame (or a slab) where the PDF draws a diamond. Either way it
    is one colour over more than 2000 pt2, and the PDF has a different colour under it.

      fill  the interior is compared: the share of PDF pixels that are not the fill colour
      line  the frame is compared: how much of the box's four edges carry ink on each side
    """
    found = []
    for s in shapes:
        area = s["w"] * s["h"]
        if area < BLOCK_MIN_PT2:
            continue
        x0 = int(round(s["x"] * PX_PER_PT))
        y0 = int(round(s["y"] * PX_PER_PT))
        x1 = int(round((s["x"] + s["w"]) * PX_PER_PT))
        y1 = int(round((s["y"] + s["h"]) * PX_PER_PT))
        if x1 <= x0 or y1 <= y0 or x0 < 0 or y0 < 0:
            continue
        if y1 > min(docx_arr.shape[0], pdf_arr.shape[0]) or x1 > min(docx_arr.shape[1], pdf_arr.shape[1]):
            continue
        box = (x0, y0, x1, y1)
        detail = None

        if s["fill"] is not None:
            i = int(round(BLOCK_INSET_PT * PX_PER_PT))
            reg_p = pdf_arr[y0 + i:y1 - i, x0 + i:x1 - i].reshape(-1, 3)
            if len(reg_p):
                off = float((np.abs(reg_p - np.array(s["fill"])).max(axis=1)
                             > BLOCK_DCOL).mean())
                if off >= BLOCK_SHAPE_HIT:
                    detail = ("fill %s %.0fx%.0f pt (%d pt2) at (%.0f,%.0f); %.0f%% of the "
                              "PDF inside it is %s"
                              % (hexs(s["fill"]), s["w"], s["h"], area, s["x"], s["y"],
                                 off * 100, hexs(modal_colour(reg_p.reshape(1, -1, 3)))))
        if detail is None and s["line"] is not None:
            t = max(2, int(round(s["linew"] * PX_PER_PT)) + 1)
            cov_d = _ring_coverage(docx_arr, box, page_fill_docx, t)
            cov_p = _ring_coverage(pdf_arr, box, page_fill_pdf, t)
            if cov_d >= BLOCK_FRAME_DOCX and cov_p <= BLOCK_FRAME_PDF:
                detail = ("frame %s %.0fx%.0f pt (%d pt2) at (%.0f,%.0f); the docx draws an "
                          "edge along %.0f%% of its box, the PDF along %.0f%%"
                          % (hexs(s["line"]), s["w"], s["h"], area, s["x"], s["y"],
                             cov_d * 100, cov_p * 100))
        if detail:
            found.append(dict(kind="shape",
                              at=[round(x0 / PX_PER_PT, 1), round(y0 / PX_PER_PT, 1),
                                  round(x1 / PX_PER_PT, 1), round(y1 / PX_PER_PT, 1)],
                              area_pt2=round(area), docx=hexs(s["fill"] or s["line"]),
                              pdf=None, detail=detail))
    return found


def _background(pdf_arr, docx_arr, fill_pdf, fill_docx, declared):
    """Does the docx page surface match the PDF page surface?"""
    detail = ""
    fired = False
    if declared is None:
        fired = True
        detail = ("no page fill declared - the viewer's own surface shows through, so a "
                  "dark theme turns a %s page into a black one" % hexs(fill_pdf))
    else:
        if dcol(declared, fill_pdf) > BACKGROUND_DCOL:
            fired = True
            detail = "declared %s, PDF page is %s" % (hexs(declared), hexs(fill_pdf))
        elif dcol(fill_docx, fill_pdf) > BACKGROUND_DCOL:
            fired = True
            detail = "rendered %s, PDF page is %s" % (hexs(fill_docx), hexs(fill_pdf))
    return dict(fired=fired, declared=hexs(declared), pdf=hexs(fill_pdf),
                rendered=hexs(fill_docx), detail=detail)


# --------------------------------------------------------------------------------- main
def analyse_document(pdf_path, docx_path, lo_pdf_path, dpi=DPI):
    pdf_pages = render_pdf_pages(pdf_path, dpi)
    docx_pages = render_pdf_pages(lo_pdf_path, dpi)
    declared = docx_page_fill(docx_path)
    shapes = docx_shapes(docx_path)

    pdoc = fitz.open(pdf_path)
    dd = fitz.open(lo_pdf_path)
    precs = [(p.rect.width, p.rect.height) for p in pdoc]
    drecs = [(p.rect.width, p.rect.height) for p in dd]
    pdoc.close()
    dd.close()

    pages = []
    n = max(len(pdf_pages), len(docx_pages))
    for i in range(n):
        if i >= len(pdf_pages) or i >= len(docx_pages):
            pages.append(dict(page=i + 1, findings=[dict(
                cls="PAGE_MISSING", pct=None, at="page",
                detail="PDF has %d pages, docx has %d" % (len(pdf_pages), len(docx_pages)))],
                pdf_modal=None, docx_modal=None, blocks=[],
                ink_missing_pct=None, ink_extra_pct=None, background=None))
            continue
        pages.append(page_report(pdf_pages[i], docx_pages[i], i + 1,
                                 precs[i], drecs[i], shapes, declared))
    return dict(document=os.path.basename(pdf_path), pages=pages,
                pdf_pages=len(pdf_pages), docx_pages=len(docx_pages),
                declared_fill=list(declared) if declared else None)


CLASSES = ["INK_MISSING", "INK_EXTRA", "BLOCK", "BACKGROUND", "PAGE_MISSING"]


def write_report(docs, fh, title="visual comparator"):
    totals = {c: [0, 0] for c in CLASSES}   # [pages fired, documents fired]
    fh.write("%s\n" % title)
    fh.write("%s\n" % ("=" * len(title)))
    fh.write("PDF rendered with PyMuPDF at %d dpi; .docx rendered by LibreOffice to PDF\n"
             "and rasterised at the same %d dpi. Both sides aligned on page size.\n\n"
             % (DPI, DPI))

    for d in docs:
        fired = {}
        for p in d["pages"]:
            for f in p["findings"]:
                fired.setdefault(f["cls"], []).append(p["page"])
        mark = "  " if not fired else ">>"
        fh.write("%s %s   pdf %dp / docx %dp%s\n" % (
            mark, d["document"], d["pdf_pages"], d["docx_pages"],
            "" if not fired else "   " + "  ".join(
                "%s x%d" % (c, len(v)) for c, v in sorted(fired.items()))))
        for p in d["pages"]:
            fh.write("     page %-3d %s  " % (
                p["page"],
                "%.0fx%.0fpt" % tuple(p["pdf_pt"]) if p.get("pdf_pt") else "n/a"))
            if p.get("ink_missing_pct") is not None:
                fh.write("ink_missing %5.2f%%   ink_extra %5.2f%%   "
                         % (p["ink_missing_pct"], p["ink_extra_pct"]))
            if p.get("background"):
                fh.write("bg %s%s" % (
                    "OK " if not p["background"]["fired"] else "!! ",
                    p["background"]["declared"]))
            fh.write("\n")
            for f in p["findings"]:
                fh.write("       %-13s %s\n" % (f["cls"], f["detail"]))
        for c in fired:
            totals[c][1] += 1
        for p in d["pages"]:
            for c in {f["cls"] for f in p["findings"]}:
                totals[c][0] += 1

    fh.write("\n%s\n" % ("-" * 78))
    fh.write("PER-CLASS TOTALS over %d documents\n" % len(docs))
    fh.write("%-14s %10s %10s\n" % ("class", "pages", "documents"))
    for c in CLASSES:
        fh.write("%-14s %10d %10d\n" % (c, totals[c][0], totals[c][1]))
    return totals


def main(argv=None):
    global DPI, PX_PER_PT
    ap = argparse.ArgumentParser(description="Render the PDF and the .docx and compare them.")
    ap.add_argument("--pdf", required=True, help="folder of source PDFs")
    ap.add_argument("--docx", required=True, help="folder of .docx produced from them")
    ap.add_argument("--report", default=None, help="write the report here (default stdout)")
    ap.add_argument("--json", default=None, help="also write the findings as JSON")
    ap.add_argument("--only", default=None, help="one document stem, or a comma list")
    ap.add_argument("--lo-dir", default=None, help="cache folder for LibreOffice PDFs")
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--png-dir", default=None, help="write page PNGs here for eyeballing")
    args = ap.parse_args(argv)

    DPI = args.dpi
    PX_PER_PT = DPI / 72.0

    pdfs = sorted(f for f in os.listdir(args.pdf) if f.lower().endswith(".pdf"))
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        pdfs = [f for f in pdfs if os.path.splitext(f)[0] in want]
    pairs = []
    missing = []
    for f in pdfs:
        stem = os.path.splitext(f)[0]
        docx = os.path.join(args.docx, stem + ".docx")
        if os.path.exists(docx):
            pairs.append((os.path.join(args.pdf, f), docx))
        else:
            missing.append(stem)
    if missing:
        sys.stderr.write("no .docx for %d documents: %s\n"
                         % (len(missing), ", ".join(missing[:5])))
    if not pairs:
        sys.stderr.write("nothing to compare\n")
        return 2

    tmp = args.lo_dir or tempfile.mkdtemp(prefix="p2w-visual-")
    lo = docx_to_pdf([p for _, p in pairs], tmp)

    docs = []
    for pdf_path, docx_path in pairs:
        stem = os.path.splitext(os.path.basename(docx_path))[0]
        lo_pdf = lo[stem]
        if not (os.path.exists(lo_pdf) and os.path.getsize(lo_pdf) > 0):
            sys.stderr.write("  libreoffice produced nothing for %s\n" % stem)
            continue
        if args.png_dir:
            os.makedirs(args.png_dir, exist_ok=True)
            for tag, path in (("pdf", pdf_path), ("docx", lo_pdf)):
                for i, arr in enumerate(render_pdf_pages(path)):
                    Image.fromarray(arr.astype(np.uint8)).save(
                        os.path.join(args.png_dir, "%s_%s_p%d.png" % (stem, tag, i + 1)))
        docs.append(analyse_document(pdf_path, docx_path, lo_pdf))

    out = open(args.report, "w") if args.report else sys.stdout
    try:
        write_report(docs, out)
    finally:
        if args.report:
            out.close()
            sys.stderr.write("report -> %s\n" % args.report)

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(docs, fh, indent=1)
        sys.stderr.write("json   -> %s\n" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
