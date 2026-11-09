#!/usr/bin/env python3
"""Compare the strokes the PDF draws against the table borders the .docx emits.

For every document:
  * the PDF side is read with PyMuPDF page.get_drawings(): every stroked axis-aligned
    segment (a `l` item) and every edge of a stroked `re`, plus every FILLED band no more
    than 1.5 pt thick (the way most generators draw a hairline). Each gives a rule with a
    width in points, a colour and a stroke opacity.
  * the .docx side is read from word/document.xml: every w:tblBorders side whose w:val is
    "single", with its w:sz (eighths of a point) and w:color.

A side matches when its width is within WIDTH_TOL pt of a drawn rule in the same document
and its colour is within COLOUR_TOL per channel of that rule's colour blended toward white
by the rule's own opacity (a table border has no opacity, so a faint rule must be written as
a lighter colour - see D-22).

Usage: compare_strokes.py <corpusdir> <outdir> [--json out.json]
"""
import json
import os
import re
import sys
import zipfile

WIDTH_TOL = 0.4          # pt; w:sz is in eighths (0.125 pt) and a drawn rule may be rounded
COLOUR_TOL = 24          # per channel, 0..255
SIDES = ["top", "left", "bottom", "right", "insideH", "insideV"]


def blend(rgb, alpha):
    """The colour a faint rule has to be written as: blended toward the white page."""
    if alpha is None or alpha >= 0.999:
        return rgb
    return tuple(int(round(c * alpha + 255 * (1 - alpha))) for c in rgb)


def drawn_rules(path):
    """Every horizontal/vertical rule the PDF draws: (width_pt, r, g, b, alpha)."""
    import pymupdf
    pymupdf.TOOLS.mupdf_display_errors(False)
    out = []
    try:
        doc = pymupdf.open(path)
    except Exception:
        return out

    def rgb_of(c):
        if c is None:
            return None
        if len(c) == 1:
            c = (c[0], c[0], c[0])
        if len(c) == 3:
            return tuple(int(round(max(0.0, min(1.0, v)) * 255)) for v in c)
        return None

    for pno in range(len(doc)):
        try:
            page = doc.load_page(pno)
            drawings = page.get_drawings()
        except Exception:
            continue
        for d in drawings:
            w = d.get("width")
            col = rgb_of(d.get("color"))
            alpha = d.get("stroke_opacity")
            if d.get("type") in ("s", "fs") and col is not None and w is not None:
                w = max(0.05, float(w))
                for item in d.get("items", []):
                    kind = item[0]
                    if kind == "l":
                        p1, p2 = item[1], item[2]
                        dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                        if dy <= 0.8 and dx > 2:
                            out.append((w,) + col + (alpha, "h"))
                        elif dx <= 0.8 and dy > 2:
                            out.append((w,) + col + (alpha, "v"))
                    elif kind == "re":
                        r = item[1]
                        if r.width > 2:
                            out.append((w,) + col + (alpha, "h"))
                            out.append((w,) + col + (alpha, "h"))
                        if r.height > 2:
                            out.append((w,) + col + (alpha, "v"))
                            out.append((w,) + col + (alpha, "v"))
            # A hairline drawn as a filled band: the band's thickness IS the weight.
            fill = rgb_of(d.get("fill"))
            if fill is not None and d.get("type") in ("f", "fs"):
                r = d.get("rect")
                if r is None:
                    continue
                falpha = d.get("fill_opacity")
                if r.height <= 1.5 and r.width > 2:
                    out.append((max(0.05, r.height),) + fill + (falpha, "h"))
                elif r.width <= 1.5 and r.height > 2:
                    out.append((max(0.05, r.width),) + fill + (falpha, "v"))
    doc.close()
    return out


BORDER_BLOCK = re.compile(r"<w:tblBorders>(.*?)</w:tblBorders>", re.S)
SIDE_EL = re.compile(r"<w:(top|left|bottom|right|insideH|insideV)\b([^/>]*)/>")


def emitted_borders(docx_path):
    """Every drawn table border side the .docx emits: (side, sz, 'RRGGBB')."""
    out = []
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return out
    for block in BORDER_BLOCK.findall(xml):
        for side, attrs in SIDE_EL.findall(block):
            val = re.search(r'w:val="([^"]*)"', attrs)
            if not val or val.group(1) != "single":
                continue
            sz = re.search(r'w:sz="(\d+)"', attrs)
            colour = re.search(r'w:color="([0-9A-Fa-f]{6})"', attrs)
            out.append((side, int(sz.group(1)) if sz else 0,
                        (colour.group(1) if colour else "000000").upper()))
    return out


def orientation(side):
    """insideH/top/bottom are rules that run across the page; the others run down it."""
    return "h" if side in ("top", "bottom", "insideH") else "v"


def match(emitted, drawn):
    """Split the emitted sides into matched / stroke-mismatched / page-drew-none.

    A side whose weight and colour match a drawn rule is MATCHED. A side that does not match
    but for which the page draws rules of the same orientation somewhere is a STROKE mismatch -
    the writer put a weight or a colour there that the page does not use, which is D-22 itself.
    A side for which the page draws no rule of that orientation at all is a different defect
    (the writer claims a side the page never drew) and is counted separately, because no
    weight could ever match it.
    """
    matched, stroke_miss, undrawn = 0, [], []
    for side, sz, colour in emitted:
        wpt = sz / 8.0
        want = tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))
        same = [r for r in drawn if r[5] == orientation(side)]
        hit = False
        for rule in same:
            if abs(rule[0] - wpt) > WIDTH_TOL:
                continue
            expect = blend(rule[1:4], rule[4])
            if max(abs(expect[i] - want[i]) for i in range(3)) <= COLOUR_TOL:
                hit = True
                break
        if hit:
            matched += 1
        elif same:
            stroke_miss.append((side, sz, colour))
        else:
            undrawn.append((side, sz, colour))
    return matched, stroke_miss, undrawn


def main():
    corpus, outdir = sys.argv[1], sys.argv[2]
    dump = None
    if "--json" in sys.argv:
        dump = sys.argv[sys.argv.index("--json") + 1]
    docs = sorted(f for f in os.listdir(corpus) if f.lower().endswith(".pdf"))
    per_doc = {}
    total_e = total_m = total_undrawn = 0
    with_borders = 0
    for f in docs:
        stem = f[:-4]
        docx = os.path.join(outdir, stem + ".docx")
        if not os.path.exists(docx):
            continue
        emitted = emitted_borders(docx)
        if not emitted:
            continue
        with_borders += 1
        drawn = drawn_rules(os.path.join(corpus, f))
        m, misses, undrawn = match(emitted, drawn)
        scored = len(emitted) - len(undrawn)
        per_doc[stem] = {"emitted": len(emitted), "matched": m,
                         "undrawn": len(undrawn),
                         "share": (m / scored) if scored else 0.0,
                         "misses": misses[:12]}
        total_e += scored
        total_m += m
        total_undrawn += len(undrawn)
    share = (total_m / total_e) if total_e else 0.0
    print("documents with borders: %d" % with_borders)
    print("emitted border sides:   %d" % (total_e + total_undrawn))
    print("  of which the page draws no rule of that orientation: %d" % total_undrawn)
    print("  scored (a rule of that orientation exists):        %d" % total_e)
    print("matched to a drawn PDF rule: %d (%.1f%% of scored)" % (total_m, 100 * share))
    worst = sorted(per_doc.items(), key=lambda kv: kv[1]["share"])[:6]
    print("worst documents:")
    for k, v in worst:
        print("  %-52s %3d/%3d  %5.1f%%  (undrawn %d)" %
              (k[:52], v["matched"], v["emitted"], 100 * v["share"], v["undrawn"]))
    if dump:
        json.dump({"share": share, "emitted": total_e, "matched": total_m,
                   "undrawn": total_undrawn, "docs": per_doc}, open(dump, "w"), indent=1)


if __name__ == "__main__":
    main()
