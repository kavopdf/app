#!/usr/bin/env python3
"""census.py - what was lost, and where. Evidence, not a score.

WHY THIS EXISTS

The fixer was given a number and a name: `415_inline_images, 89.04 %@5, content-loss,
max 153 pt, 1 page`. From that it had to guess the MECHANISM, then write a patch, then
measure. ATTEMPTS.json records the result: 19 attempts over four classes, zero kept,
fourteen of them on one class. It was not failing at patching - it was guessing at what
to patch.

A pixel score cannot tell you that four images are missing. A structural diff can.

WHAT IT MEASURES

For every document the ranking calls defective, count what the SOURCE holds and what the
OUTPUT holds, element type by element type:

    images       raster images in the source pages   vs   inline pictures in the docx
    rules        drawn lines/rects in the source     vs   table cells in the docx
    text         characters in the source            vs   characters in the docx
    annotations  annotation objects in the source    vs   (reported, not compared)

and which page carries the worst displacement, so a reader can open that page and look.

THE SIGNAL IS A HYPOTHESIS, NOT A PROOF

The counts are facts. The `signal` column is a candidate mechanism derived from them, and
it is deliberately conservative: it fires only when the evidence is unambiguous (source
has images, output has none). Everything else says `none-identified` rather than inventing
a cause. A wrong mechanism is worse than no mechanism, because it sends the fixer after a
patch that cannot work.

    python3 benchmarks/census.py --corpus /scratch/work/p2w/corpus \
                                 --out /scratch/work/p2w/out \
                                 --ranking benchmarks/RANKING.csv

Writes benchmarks/CENSUS.csv (one row per defective document) and benchmarks/CENSUS.md
(the same grouped by signal, which is the part that tells you which mechanism to fix first).
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict


def src_facts(pdf_path):
    """Per-page element counts from the source PDF."""
    import pymupdf
    out = {"pages": 0, "chars": 0, "images": 0, "images_any": 0, "drawings": 0,
           "annots": 0, "page_chars": {}, "page_images": {}, "page_drawings": {}}
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        out["error"] = str(e)[:120]
        return out
    out["pages"] = len(doc)
    for i, page in enumerate(doc):
        try:
            text = page.get_text("text") or ""
            # get_images() returns XObject images only. INLINE images - the BI ... ID ...
            # EI operators - are not XObjects and are not returned, so a document made
            # entirely of inline images reported src_images 0. 415_inline_images is exactly
            # that document: the census said "source has no images, output has one", which
            # is backwards and points the fixer at the wrong mechanism for the class named
            # after it. get_image_info() reports what is actually DRAWN on the page,
            # inline images included.
            n_img = len(page.get_images(full=True))
            try:
                n_any = len(page.get_image_info())
            except Exception:
                n_any = n_img
            n_draw = len(page.get_drawings())
            n_ann = 0
            try:
                n_ann = len(list(page.annots() or []))
            except Exception:
                pass
            out["chars"] += len(text)
            out["images"] += n_img
            out["images_any"] += max(n_img, n_any)
            out["drawings"] += n_draw
            out["annots"] += n_ann
            out["page_chars"][i + 1] = len(text)
            out["page_images"][i + 1] = n_img
            out["page_drawings"][i + 1] = n_draw
        except Exception:
            continue
    try:
        doc.close()
    except Exception:
        pass
    return out


def docx_facts(docx_path):
    """Element counts from the produced .docx."""
    out = {"chars": 0, "images": 0, "tables": 0, "cells": 0, "paragraphs": 0}
    try:
        import docx
        d = docx.Document(docx_path)
    except Exception as e:
        out["error"] = str(e)[:120]
        return out
    try:
        for p in d.paragraphs:
            out["paragraphs"] += 1
            out["chars"] += len(p.text or "")
        for t in d.tables:
            out["tables"] += 1
            for row in t.rows:
                out["cells"] += len(row.cells)
                for c in row.cells:
                    out["chars"] += len(c.text or "")
        # inline pictures live in the document part's relationships
        try:
            from docx.oxml.ns import qn
            out["images"] = len(d.element.body.findall(".//" + qn("pic:pic")))
        except Exception:
            out["images"] = -1
    except Exception as e:
        out["error"] = str(e)[:120]
    return out


def _instrument():
    """p2w's own renderer, so the census compares with the same instrument.

    Imported lazily and tolerated failing: the census is useful without it (the element
    counts still stand) and must never take the run down because a sibling module moved.
    """
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2w.py")
    if not os.path.exists(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location("p2w_for_census", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception:
        return None


def displacement_vector(pdf_path, docx_path, tmpdir, inst):
    """Where the ink WENT, in points - the rigid shift that explains the page.

    The census counts what is MISSING. Most defects are not missing, they are MOVED: the
    two nine-page bank forms keep 99.6 % of their characters and their image and still
    read 98.7 %@5 with a 937 pt outlier. Nothing was lost; everything is in the wrong
    place. A count cannot say that. A shift can.

    WHY NOT NEAREST-NEIGHBOUR. The first version matched every source ink pixel to its
    closest output ink pixel and took the median offset. Tested on a block moved +10 right
    and +6 down, it answered +6, +2: a solid block's pixels all map to the nearest EDGE of
    the output block, not to their own counterpart, so the answer collapses toward the
    middle. It was wrong by 40 % and looked plausible, which is the worst kind.

    Cross-correlation answers the question actually being asked - what single translation
    makes these two ink masks line up - and on the same test it returns exactly +10, +6.
    Verified on +10/+6, on -12/+3, and on an unshifted pair which returns 0, 0.

    dx > 0 means the output ink sits to the RIGHT of the source, dy > 0 means BELOW it
    (image coordinates, so down the page). A large shift with a high `explains` is an
    offset or margin bug: one origin is wrong and every element inherits it. A small shift
    with low `explains` is a layout bug: elements disagree with each other and no single
    translation fixes the page. `moved_gt20` is the share of ink still more than 20 pt from
    any output ink AFTER the shift is applied - the part the shift does not explain.
    """
    if inst is None:
        return None
    try:
        import numpy as np
        from scipy.ndimage import distance_transform_edt as edt
        from scipy.signal import fftconvolve
    except Exception:
        return None
    try:
        sp = inst.render(pdf_path)
        pdf = inst.conv(docx_path, tmpdir)
        if not pdf:
            return None
        op = inst.render(pdf)
    except Exception:
        return None
    PT, INK = inst.PT, inst.INK
    shifts, explains, residuals = [], [], []
    for i in range(min(len(sp), len(op))):
        src, our = sp[i], op[i]
        H = max(src.shape[0], our.shape[0]); W = max(src.shape[1], our.shape[1])
        s_pad = np.full((H, W), 255, np.uint8); s_pad[:src.shape[0], :src.shape[1]] = src
        o_pad = np.full((H, W), 255, np.uint8); o_pad[:our.shape[0], :our.shape[1]] = our
        sm = s_pad < INK
        om = o_pad < INK
        if not sm.any() or not om.any():
            continue
        f = sm.astype(np.float32); g = om.astype(np.float32)
        corr = fftconvolve(g, f[::-1, ::-1], mode="same")
        py, px = np.unravel_index(np.argmax(corr), corr.shape)
        dy, dx = int(py) - H // 2, int(px) - W // 2
        base = float(corr[H // 2, W // 2]); peak = float(corr[py, px])
        ink = float(sm.sum())
        shifts.append((dx, dy, ink))
        # how much of the overlap this one translation accounts for
        explains.append(max(0.0, (peak - base)) / max(1.0, ink) * 100)
        # residual: source ink shifted by (dx,dy), still far from any output ink
        sh = np.roll(np.roll(sm, dy, axis=0), dx, axis=1)
        d = edt(~om)
        far = d[sh] > (20 / PT)
        residuals.append(float(far.mean()) * 100 if sh.any() else 0.0)
    if not shifts:
        return None
    tw = sum(w for _, _, w in shifts) or 1.0
    return dict(
        dx_pt=round(sum(d * w for d, _, w in shifts) / tw * PT, 1),
        dy_pt=round(sum(y * w for _, y, w in shifts) / tw * PT, 1),
        explains=round(float(np.mean(explains)), 0),
        moved_gt20=round(float(np.mean(residuals)), 0),
    )


def signal_for(s, d):
    """The candidate mechanism. Conservative on purpose - see the module docstring."""
    if s.get("error") or d.get("error"):
        return "unreadable"
    si, di = s.get("images_any", s["images"]), d["images"]
    if si > 0 and di == 0:
        return "images-none-extracted"
    if si >= 2 and 0 < di < si * 0.5:
        return "images-mostly-missing"
    if s["chars"] > 200 and d["chars"] < s["chars"] * 0.85:
        return "text-missing"
    if s["drawings"] >= 20 and d["cells"] == 0:
        return "rules-not-tables"
    if s["annots"] > 0 and s["chars"] > 0:
        return "annotations-present"
    return "none-identified"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="/scratch/work/p2w/corpus")
    ap.add_argument("--out", default="/scratch/work/p2w/out")
    ap.add_argument("--ranking", default="benchmarks/RANKING.csv")
    ap.add_argument("--limit", type=int, default=0, help="only the N worst documents")
    ap.add_argument("--csv", default="")
    ap.add_argument("--md", default="")
    ap.add_argument("--disp-limit", type=int, default=30,
                    help="how many of the worst documents get the expensive "
                         "displacement-vector pass; 0 disables it")
    a = ap.parse_args(argv[1:])

    # The output belongs beside the ranking it describes, NOT beside whatever directory
    # the caller happened to be in. gate.py runs the census from the repo root while the
    # ranking is written to /scratch/output, and a cwd-relative path made os.makedirs
    # fail with the census already half-done - the 16 Nov run recorded "exit1" while
    # still writing valid files, which is the worst of both.
    _rd = os.path.dirname(os.path.abspath(a.ranking)) or "."
    a.csv = a.csv or os.path.join(_rd, "CENSUS.csv")
    a.md = a.md or os.path.join(_rd, "CENSUS.md")

    rows = []
    with open(a.ranking, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            p = (r.get("problem") or "").strip()
            if p in ("", "none", "unmeasured"):
                continue
            try:
                r["_s5"] = float(r.get("share5") or "")
            except ValueError:
                continue
            rows.append(r)
    rows.sort(key=lambda r: -r["_s5"])
    if a.limit:
        rows = rows[:a.limit]

    cols = ["document", "problem", "share5", "max_pt", "worst_page", "pages",
            "src_chars", "docx_chars", "src_images", "docx_images",
            "src_drawings", "docx_tables", "docx_cells", "src_annots", "src_images_any",
            "signal",
            "dx_pt", "dy_pt", "explains", "moved_gt20"]
    inst = _instrument() if a.disp_limit else None
    tmpdir = None
    if inst is not None:
        import tempfile
        tmpdir = tempfile.mkdtemp(prefix="census-")
        if inst is None:
            print("  displacement vector unavailable - p2w.py could not be loaded")

    out_rows = []
    for _rank, r in enumerate(rows):
        doc = r["document"]
        sp = os.path.join(a.corpus, doc + ".pdf")
        dp = os.path.join(a.out, doc + ".docx")
        if not os.path.exists(sp) or not os.path.exists(dp):
            continue
        s, d = src_facts(sp), docx_facts(dp)
        out_rows.append({
            "document": doc, "problem": r.get("problem", ""), "share5": r.get("share5", ""),
            "max_pt": r.get("max_pt", ""), "worst_page": r.get("worst_page", ""),
            "pages": s.get("pages", ""),
            "src_chars": s.get("chars", ""), "docx_chars": d.get("chars", ""),
            "src_images": s.get("images", ""), "docx_images": d.get("images", ""),
            "src_images_any": s.get("images_any", ""),
            "src_drawings": s.get("drawings", ""), "docx_tables": d.get("tables", ""),
            "docx_cells": d.get("cells", ""), "src_annots": s.get("annots", ""),
            "signal": signal_for(s, d),
            "dx_pt": "", "dy_pt": "", "explains": "", "moved_gt20": "",
        })
        # The vector is expensive (a LibreOffice round-trip per document), so only the
        # worst ones get it. They are the ones the fixer will look at first anyway.
        if inst is not None and _rank < a.disp_limit:
            v = displacement_vector(sp, dp, tmpdir, inst)
            if v:
                out_rows[-1].update(v)

    os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
    with open(a.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    by = defaultdict(list)
    for r in out_rows:
        by[r["signal"]].append(r)
    order = ["images-none-extracted", "images-mostly-missing", "rules-not-tables",
             "text-missing", "annotations-present", "none-identified", "unreadable"]

    md = ["# Census - what was lost, and where", "",
          "Every document the ranking calls defective, with what the SOURCE holds beside",
          "what the OUTPUT holds. The counts are facts. The `signal` is a candidate",
          "mechanism and it is deliberately conservative: it fires only when the evidence",
          "is unambiguous. `none-identified` means the counts do not point at one cause,",
          "and that is a real answer - a wrong mechanism sends the fixer after a patch",
          "that cannot work.", "",
          "**%d defective documents censused.**" % len(out_rows), "",
          "| signal | documents | total share@5 | worst document |",
          "|---|---|---|---|"]
    for sig in order:
        g = by.get(sig)
        if not g:
            continue
        worst = max(g, key=lambda r: float(r["share5"]))
        md.append("| %s | %d | %.1f%% | %s %.1f%%@5 p%s |"
                  % (sig, len(g), sum(float(r["share5"]) for r in g),
                     worst["document"][:34], float(worst["share5"]), worst["worst_page"]))
    vec = [r for r in out_rows if r.get("dx_pt") != ""]
    if vec:
        md += ["", "## Where the ink went, in points", "",
               "`dx` positive = the output ink sits right of the source; `dy` positive = below it.",
               "A whole page shifted one way is an offset or margin bug. Signs scattered is a",
               "layout bug. `moved_gt20` is the share of ink that moved more than 20 pt.", "",
               "| document | share@5 | dx | dy | explains | still >20pt |",
               "|---|---|---|---|---|---|"]
        for r in vec:
            md.append("| %s | %s | %s | %s | %s | %s%% |"
                      % (r["document"][:34], r["share5"], r["dx_pt"], r["dy_pt"],
                         r["explains"], r["moved_gt20"]))
        md.append("")

    md.append("")
    for sig in order:
        g = by.get(sig)
        if not g:
            continue
        md += ["## %s (%d documents)" % (sig, len(g)), "",
               "| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |",
               "|---|---|---|---|---|---|---|---|---|"]
        for r in g[:25]:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                      % (r["document"][:34], r["share5"], r["worst_page"],
                         r["src_images"], r["docx_images"], r["src_chars"],
                         r["docx_chars"], r["src_drawings"], r["docx_cells"]))
        if len(g) > 25:
            md.append("| ... %d more | | | | | | | | |" % (len(g) - 25))
        md.append("")
    with open(a.md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("censused %d defective documents" % len(out_rows))
    for sig in order:
        if by.get(sig):
            print("  %-24s %d" % (sig, len(by[sig])))
    print("wrote %s and %s" % (a.csv, a.md))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
