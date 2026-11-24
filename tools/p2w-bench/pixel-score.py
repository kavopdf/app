#!/usr/bin/env python3
"""pixel-score.py - how closely does the render look like the original, in pixels?

WHY THIS EXISTS. Every number this pipeline has produced is a boolean check: `verify_google.py`
asks 42-47 yes/no questions and the report counts how many said yes. That is not the question the
product is judged on. A document can fail one check - a 2 pt line moved, a font substituted - and
still be a 98 % visual match, which is what "99 % visual match in Google's render" means. Nothing
in the tree measured that: `visual.py` compares line boxes and text runs, `visual_score.py` reports
dy in points, `compare_strokes.py` compares stroke widths. All of them compare STRUCTURE. None of
them compares the picture.

WHAT IT COMPUTES. Two numbers per page, both from the rasterised page:

    ink_iou   intersection over union of the two pages' ink masks. The one that behaves like a
              reader: a sideways page scores near 0, a page whose lines moved scores high.
    ssim      mean structural similarity (skimage, grayscale). Punishes a page that has the right
              amount of ink in the wrong arrangement.
    agree     1 - mean(|a-b|)/255 over every pixel. Included because it is the blunt number people
              expect, and NOT to be trusted on a sparse page: a deliberately 90-degree-rotated
              page scored 95.6 % on it, because both pages are mostly white. See compare_arrays.
    agree_ink the same over the pixels where either page has ink.

Both are computed on the SAME pixel grid: both PDFs are rasterised at one DPI, so a page rendered
at the same physical size lands on the same grid and a shifted line is a real difference.

THE THREE THINGS THAT MAKE A PIXEL SCORE MEANINGLESS, AND WHAT THIS DOES ABOUT EACH.

  page count    A render with more pages than the source is not a worse match, it is a different
                document. It is reported as a DEFECT, the pages are NOT padded with blanks, and only
                the pages that exist in both are scored. `--strict` refuses to score at all.
  page size     Two pages of different physical size cannot share a grid. The larger size becomes the
                canvas, both pages are placed at its top-left corner, and the size delta is recorded
                as a defect. Scoring them anyway is right - a page reflowed to A4 from Letter IS a
                worse visual match - but the reader must know the grid was padded, not shared.
  rotation      `page.rotation` (/Rotate) is compared. PyMuPDF applies it when rasterising, so a
                source at /Rotate 90 and a render at /Rotate 0 come out in different orientations and
                score near zero for a reason that is not a layout error. Recorded as a defect, and
                with `--unrotate` the render is turned to the source's orientation so the two can be
                compared on content. Without the flag the number is reported as it is.

WHAT IT DOES NOT DO. It does not obtain the render. A Google render is three Drive API calls that
cannot run in this process - see grender.py - so the caller supplies the exported PDF. `--corpus`
reads whatever renders are in the given directory and reports which documents have none, rather than
silently scoring a subset.

USAGE

    python3 pixel-score.py --score <src.pdf> <render.pdf> [--dpi 150] [--json out.json]
    python3 pixel-score.py --corpus /scratch/work/p2w/corpus --renders /scratch/work/p2w/grender
    python3 pixel-score.py --corpus ... --renders ... --json all.json --csv all.csv

Exit codes: 0 scored, 2 could not read a file, 4 page counts differ (with --strict).

MEASURED 24 Nov 2026, engine b7699196, 6 documents: see the table this prints. The number that
matters is that it is not 100 for any document, and the worst page is not always page 1.
"""
import argparse
import csv
import glob
import json
import os
import sys

DEFAULT_DPI = 150
# A page size delta below this is the same page measured twice, not a reflow. 1 pt = 1/72 inch.
SIZE_TOL_PT = 0.5
# Above this, a page-size difference is a reflow rather than Google rounding A4 up to 596 pt.
ROUND_TOL_PT = 2.0


def _fitz():
    import fitz
    return fitz


def render_page(doc, i, dpi):
    """One page as an 8-bit grayscale numpy array, plus its geometry.

    get_pixmap honours /Rotate, so the array is what a reader sees, not what the content stream
    says. That is the right thing to compare: the question is what the page looks like.
    """
    pg = doc[i]
    fitz = _fitz()
    pm = pg.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
    import numpy as np
    # `colorspace` is a request, not a promise: some builds hand back 3 channels whatever is asked
    # for, and reshaping by height*width then dies with "cannot reshape array of size N into shape
    # (h,w)" - which is how the first run lost all six documents. Reshape by the pixmap's OWN
    # channel count and stride, then take the first channel.
    buf = np.frombuffer(pm.samples, dtype=np.uint8)
    buf = buf[:pm.height * pm.stride].reshape(pm.height, pm.stride)
    arr = buf[:, :pm.width * pm.n].reshape(pm.height, pm.width, pm.n)[:, :, 0]
    return arr, {"page": i + 1,
                 "rotation": int(pg.rotation or 0),
                 "w_pt": round(pg.rect.width, 2),
                 "h_pt": round(pg.rect.height, 2)}


def to_canvas(a, b, shape):
    """Put two arrays on one grid at the top-left, without resampling either.

    NO SCALING. Resampling one page to the other's size would turn "the page is the wrong size"
    into a small blur difference, which is exactly the fault we are trying to see.
    """
    import numpy as np
    h, w = shape
    out = []
    for x in (a, b):
        c = np.full((h, w), 255, dtype=np.uint8)
        c[:min(h, x.shape[0]), :min(w, x.shape[1])] = x[:h, :w]
        out.append(c)
    return out[0], out[1]


INK_LEVEL = 240  # below this a pixel is ink; above it is paper


def compare_arrays(a, b):
    """Four numbers, because the plain one lies on a sparse page.

    `agree` is the share of ALL pixels that match, and a document page is mostly blank. Measured
    24 Nov on a page deliberately turned 90 degrees against its render: `agree` still said 95.6 %
    because the two pages share several hundred thousand white pixels and the canvas padding is
    white too. A number that calls a sideways page a 95 % match cannot be the headline.

    So ink is measured on its own:

        ink_iou   intersection over union of the ink masks, as they are. This measures
                  REGISTRATION, not fidelity: at 150 dpi a text stroke is 1-2 px wide, so a half-pixel
                  shift drops it to 20 %. Measured: a page rotated 90 deg scores 1.8 %, identical
                  files score 100 %, and a good render still scores 13-54 %. Useful as a detector,
                  useless as a score.
        ink_iou_d1 the same after dilating both masks by one pixel, which is the tolerance a
                  reader actually has for a 150 dpi raster. Measured on the same pairs: rotated
                  page 3.6 %, identical 100 %, real renders 17-88 %. THIS is the ink number to
                  read - it falls off a cliff when the layout is wrong and barely moves when the
                  page is merely re-rasterised.
        agree_ink 1 - mean(|a-b|)/255 over the pixels where EITHER page has ink. Punishes a
                  grey-for-black substitution that an IoU forgives.
    """
    import numpy as np
    ai, bi = a.astype(np.int16), b.astype(np.int16)
    agree = 1.0 - float(np.abs(ai - bi).mean()) / 255.0
    ma, mb = a < INK_LEVEL, b < INK_LEVEL
    union = int((ma | mb).sum())
    inter = int((ma & mb).sum())
    iou = (inter / union) if union else 1.0
    if union:
        agree_ink = 1.0 - float(np.abs(ai - bi)[ma | mb].mean()) / 255.0
    else:
        agree_ink = 1.0
    iou_d1 = iou
    try:
        from scipy.ndimage import binary_dilation
        k = np.ones((3, 3), bool)
        u1 = int((binary_dilation(ma, k) | binary_dilation(mb, k)).sum())
        i1 = int((binary_dilation(ma, k) & binary_dilation(mb, k)).sum())
        iou_d1 = (i1 / u1) if u1 else 1.0
    except Exception:
        pass
    try:
        from skimage.metrics import structural_similarity as ssim
        s = round(float(ssim(a, b, data_range=255)) * 100.0, 2)
    except Exception:
        s = None
    return {"agree": round(agree * 100.0, 2), "ssim": s,
            "ink_iou": round(iou * 100.0, 2), "ink_iou_d1": round(iou_d1 * 100.0, 2),
            "agree_ink": round(agree_ink * 100.0, 2),
            "ink_px": [int(ma.sum()), int(mb.sum())]}


def best_offset(a, b, radius=8):
    """The translation that makes the two pages agree best, in pixels.

    Reported only when asked for. A page that is 3 px out scores badly on an unaligned comparison
    and that is CORRECT - a 3 px shift at 150 dpi is half a millimetre and a reader sees it - but a
    reader also wants to know whether the page is shifted or wrong. The offset says which.
    """
    import numpy as np
    best = (None, -1.0)
    h, w = a.shape
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            ys1, ys2 = max(0, dy), max(0, -dy)
            xs1, xs2 = max(0, dx), max(0, -dx)
            hh, ww = h - abs(dy), w - abs(dx)
            if hh <= 0 or ww <= 0:
                continue
            s1 = a[ys1:ys1 + hh, xs1:xs1 + ww]
            s2 = b[ys2:ys2 + hh, xs2:xs2 + ww]
            agree = 1.0 - float(np.abs(s1.astype(np.int16) - s2.astype(np.int16)).mean()) / 255.0
            if agree > best[1]:
                best = ((dx, dy), agree)
    return best[0], round(best[1] * 100.0, 2)


def score(src_pdf, render_pdf, dpi=DEFAULT_DPI, unrotate=False, align=False):
    """Score one pair. Returns the record; never raises on a defect, only on unreadable files."""
    fitz = _fitz()
    import numpy as np
    rec = {"source": os.path.basename(src_pdf), "render": os.path.basename(render_pdf),
           "dpi": dpi, "defects": [], "pages": []}
    with fitz.open(src_pdf) as s, fitz.open(render_pdf) as r:
        ns, nr = len(s), len(r)
        rec["pages_source"] = ns
        rec["pages_render"] = nr
        if ns != nr:
            rec["defects"].append({"kind": "page_count", "source": ns, "render": nr,
                                   "note": "scored on the %d page(s) both have; not padded"
                                           % min(ns, nr)})
        n = min(ns, nr)
        for i in range(n):
            a, ga = render_page(s, i, dpi)
            b, gb = render_page(r, i, dpi)
            pg = {"page": i + 1, "source": ga, "render": gb}
            if ga["rotation"] != gb["rotation"]:
                pg["defects"] = pg.get("defects", []) + ["rotation %d vs %d"
                                                        % (ga["rotation"], gb["rotation"])]
                if unrotate:
                    # turn the render so its orientation matches the source's, then re-read it
                    delta = (ga["rotation"] - gb["rotation"]) % 360
                    if delta == 90:
                        b = np.rot90(b, k=-1)
                    elif delta == 180:
                        b = np.rot90(b, k=2)
                    elif delta == 270:
                        b = np.rot90(b, k=1)
                    pg["unrotated"] = delta
            dw, dh = abs(ga["w_pt"] - gb["w_pt"]), abs(ga["h_pt"] - gb["h_pt"])
            if dw > SIZE_TOL_PT or dh > SIZE_TOL_PT:
                # ROUNDING IS NOT A REFLOW. Every Google export measured here comes back 596.0 x
                # 842.0 pt against the source's 595.3 x 841.9 - A4 with the fraction rounded up, a
                # 0.7 pt difference that is one pixel of canvas at 150 dpi. Calling that a defect on
                # all 213 documents would bury the reflows that matter, so the two are separated:
                # under 2 pt is recorded and named as rounding, over it is a size defect.
                kind = "page size rounding" if max(dw, dh) < ROUND_TOL_PT else "page size"
                pg["defects"] = pg.get("defects", []) + [
                    "%s %.1fx%.1f vs %.1fx%.1f pt" % (kind, ga["w_pt"], ga["h_pt"],
                                                      gb["w_pt"], gb["h_pt"])]
            if a.shape != b.shape:
                shape = (max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1]))
                pg["canvas_padded"] = [list(a.shape), list(b.shape), list(shape)]
                a, b = to_canvas(a, b, shape)
            # NOT `s` - that is the source document handle opened above, and overwriting it made
            # page 2 of every multi-page document die with "'float' object is not subscriptable".
            # Only the two-page and four-page documents hit it, so a one-page smoke test passed.
            pg.update(compare_arrays(a, b))
            if align:
                off, ag = best_offset(a, b)
                pg["best_offset_px"], pg["agree_at_offset"] = list(off), ag
            rec["pages"].append(pg)
    ok = [p for p in rec["pages"] if p.get("ssim") is not None]
    for k in ("agree", "agree_ink", "ink_iou", "ink_iou_d1"):
        rec[k + "_mean"] = (round(sum(p[k] for p in rec["pages"]) / len(rec["pages"]), 2)
                            if rec["pages"] else None)
    if ok:
        worst = min(ok, key=lambda p: p["ssim"])
        rec["ssim_mean"] = round(sum(p["ssim"] for p in ok) / len(ok), 2)
        rec["ssim_worst"] = worst["ssim"]
        rec["worst_page"] = worst["page"]
        # the worst page by ink overlap as well - on a sparse document the two disagree, and the
        # reader needs to know which page to open
        wi = min(ok, key=lambda p: p["ink_iou"])
        rec["ink_iou_worst"] = wi["ink_iou"]
        rec["worst_page_by_ink"] = wi["page"]
    else:
        rec["ssim_mean"] = rec["ssim_worst"] = rec["worst_page"] = None
        rec["ink_iou_worst"] = rec["worst_page_by_ink"] = None
        rec["defects"].append({"kind": "no_ssim", "note": "skimage unavailable; agree only"})
    return rec


def one(src, render, a):
    if not os.path.exists(src):
        print("no such source: %s" % src)
        return 2
    if not os.path.exists(render):
        print("no such render: %s" % render)
        return 2
    rec = score(src, render, a.dpi, a.unrotate, a.align)
    if a.json:
        json.dump(rec, open(a.json, "w"), indent=1)
    print_report([rec])
    if a.strict and rec["pages_source"] != rec["pages_render"]:
        return 4
    return 0


def print_report(recs):
    print("  %-38s %-5s %-8s %-7s %-8s %-6s %s"
          % ("document", "pages", "ink1%", "ssim%", "agree%", "worst", "defects"))
    for r in recs:
        d = []
        for x in r["defects"]:
            d.append(x["kind"] if isinstance(x, dict) else x)
        for p in r["pages"]:
            for x in (p.get("defects") or []):
                k = x.split(" ")[0] + (" " + x.split(" ")[1] if x.startswith("page size") else "")
                if k not in d:
                    d.append(k)
        print("  %-38s %-5s %-8s %-7s %-8s %-6s %s"
              % (r["source"][:38],
                 "%d/%d" % (r["pages_source"], r["pages_render"]),
                 r["ink_iou_d1_mean"], r["ssim_mean"], r["agree_mean"], r["worst_page"],
                 "; ".join(d[:4]) or "-"))


def corpus(corpus_dir, render_dir, a):
    """Score every document that has a render, and say which have none."""
    srcs = {os.path.basename(p)[:-4]: p for p in glob.glob(os.path.join(corpus_dir, "*.pdf"))}
    rends = {os.path.basename(p)[:-4]: p for p in glob.glob(os.path.join(render_dir, "*.pdf"))}
    names = sorted(srcs)
    have = [n for n in names if n in rends]
    missing = [n for n in names if n not in rends]
    recs, errs = [], []
    for n in have:
        try:
            recs.append(score(srcs[n], rends[n], a.dpi, a.unrotate, a.align))
        except Exception as e:
            errs.append({"name": n, "error": str(e)[:200]})
    print("  %d corpus document(s), %d with a render, %d without"
          % (len(names), len(have), len(missing)))
    if missing:
        print("  NO RENDER, NOT SCORED (this is the caller's Drive export step, not a failure here):")
        print("    " + ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else ""))
    if recs:
        print("")
        print_report(recs)
        print("")
        for key, label in (("ink_iou_d1_mean", "ink_iou_d1"), ("ssim_mean", "ssim"),
                           ("agree_mean", "agree"), ("agree_ink_mean", "agree_ink")):
            m = sorted(r[key] for r in recs if r.get(key) is not None)
            if not m:
                continue
            print("  %-10s mean %6.2f  median %6.2f  min %6.2f  max %6.2f   at/above 99%%: %d of %d"
                  % (label, sum(m) / len(m), m[len(m) // 2], m[0], m[-1],
                     sum(1 for x in m if x >= 99.0), len(m)))
    if a.json:
        json.dump({"documents": recs, "no_render": missing, "errors": errs},
                  open(a.json, "w"), indent=1)
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["document", "pages_source", "pages_render", "ink_iou_d1_pct", "ssim_pct",
                        "agree_pct", "agree_ink_pct", "ink_iou_pct", "ssim_worst", "worst_page",
                        "defects"])
            for r in recs:
                w.writerow([r["source"][:-4], r["pages_source"], r["pages_render"],
                            r["ink_iou_d1_mean"], r["ssim_mean"], r["agree_mean"],
                            r["agree_ink_mean"], r["ink_iou_mean"], r["ssim_worst"],
                            r["worst_page"], "; ".join(str(x) for x in r["defects"])])
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--score", nargs=2, metavar=("SRC", "RENDER"))
    ap.add_argument("--corpus")
    ap.add_argument("--renders")
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    ap.add_argument("--json")
    ap.add_argument("--csv")
    ap.add_argument("--unrotate", action="store_true",
                    help="turn a rotated render to the source's orientation before scoring")
    ap.add_argument("--align", action="store_true",
                    help="also report the best translation and the score at it (does not replace the score)")
    ap.add_argument("--strict", action="store_true", help="exit 4 if the page counts differ")
    a = ap.parse_args(argv)
    if a.score:
        return one(a.score[0], a.score[1], a)
    if a.corpus:
        if not a.renders:
            ap.error("--corpus needs --renders")
        return corpus(a.corpus, a.renders, a)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
