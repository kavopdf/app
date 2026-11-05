#!/usr/bin/env python3
"""Font / colour / position fidelity, read out of the .docx's TEXT BOXES.

python-docx cannot see text-box content, and the converter puts every PDF line in a text
box, so tools/bench/score_fidelity.py reads no runs at all on this engine's output and its
font/colour numbers are meaningless here. This reads the XML with lxml instead.

    python3 fidelity2.py PDFDIR OUTDIR [--json J]

  fonts      per document: |PDF families n docx families| / |PDF families|, summed
  colours    the same over non-black colours
  position   each text box's anchor (x,y) against the PDF line it carries; % within 1 pt,
             median error in twips (1 pt = 20 twips)
"""
import os, sys, json, re, statistics, warnings
warnings.filterwarnings("ignore")
import pymupdf
import zipfile
from lxml import etree

PDF_DIR, OUT_DIR = sys.argv[1], sys.argv[2]
J = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
EMU = 12700.0


def norm(s):
    return " ".join((s or "").split())


def family(f):
    f = (f or "").split("+")[-1]
    f = re.sub(r"[^A-Za-z]", "", f)
    for known in ["TimesNewRoman", "Arial", "Helvetica", "Calibri", "Cambria", "Georgia",
                  "Garamond", "CourierNew", "Courier", "Verdana", "Tahoma", "Segoe",
                  "Roboto", "Consolas", "LiberationSerif", "LiberationSans",
                  "DejaVuSans", "DejaVuSerif", "Noto", "Symbol"]:
        if known.lower() in f.lower():
            return known
    return f[:20] if f else ""


def has_nested(el):
    for sub in el.iter("{%s}p" % W):
        if sub is not el:
            return True
    return False


def docx_runs(path):
    """(font family, colour int, anchor box) for every run inside a text box leaf."""
    out = []
    try:
        z = zipfile.ZipFile(path)
        root = etree.fromstring(z.read("word/document.xml"))
    except Exception:
        return out
    for el in root.iter("{%s}p" % W):
        if has_nested(el):
            continue
        anc = el.getparent()
        anchor = None
        while anc is not None:
            ln = etree.QName(anc).localname
            if ln == "anchor":
                anchor = anc
                break
            anc = anc.getparent()
        box = None
        if anchor is not None:
            x = y = 0.0
            for tag in ("positionH", "positionV"):
                node = anchor.find("{%s}%s" % (WP, tag))
                if node is None:
                    continue
                off = node.find("{%s}posOffset" % WP)
                v = float(off.text) / EMU if (off is not None and off.text) else 0.0
                if tag == "positionH":
                    x = v
                else:
                    y = v
            box = (x, y)
        for r in el.iter("{%s}r" % W):
            rPr = r.find("{%s}rPr" % W)
            fam = None
            col = None
            if rPr is not None:
                f = rPr.find("{%s}rFonts" % W)
                if f is not None:
                    fam = family(f.get("{%s}ascii" % W) or f.get("{%s}hAnsi" % W))
                c = rPr.find("{%s}color" % W)
                if c is not None:
                    v = c.get("{%s}val" % W)
                    if v and re.fullmatch(r"[0-9A-Fa-f]{6}", v):
                        col = int(v, 16)
            txt = norm("".join(t.text or "" for t in r.iter("{%s}t" % W)))
            if txt:
                out.append({"text": txt, "font": fam, "color": col, "box": box})
    return out


def pdf_spans(path):
    out = []
    d = pymupdf.open(path)
    for pno in range(d.page_count):
        for blk in d[pno].get_text("dict").get("blocks", []):
            for line in blk.get("lines", []):
                for sp in line.get("spans", []):
                    t = norm(sp.get("text"))
                    if not t:
                        continue
                    out.append({"text": t, "font": family(sp.get("font")),
                                "color": sp.get("color", 0),
                                "bbox": sp["bbox"], "page": pno})
    d.close()
    return out


tot_pf = tot_fh = tot_pc = tot_ch = 0
tot_lines = 0
tot_within = 0
errs = []
per = {}

for f in sorted(os.listdir(PDF_DIR)):
    if not f.lower().endswith(".pdf"):
        continue
    base = f[:-4]
    dp = os.path.join(OUT_DIR, base + ".docx")
    if not os.path.isfile(dp):
        continue
    spans = pdf_spans(os.path.join(PDF_DIR, f))
    runs = docx_runs(dp)
    pf = {s["font"] for s in spans if s["font"]}
    df = {r["font"] for r in runs if r["font"]}
    pc = {s["color"] for s in spans if s["color"] not in (0, None)}
    dc = {r["color"] for r in runs if r["color"] is not None}
    tot_pf += len(pf)
    tot_fh += len(pf & df)
    tot_pc += len(pc)
    tot_ch += len(pc & dc)
    per[base] = {"fonts": "%d/%d" % (len(pf & df), len(pf)),
                 "colours": "%d/%d" % (len(pc & dc), len(pc)),
                 "fonts_missed": sorted(pf - df), "colours_missed": sorted(pc - dc)}

    # position: match each text box to the PDF line holding its text, on its page order
    d = pymupdf.open(os.path.join(PDF_DIR, f))
    pages = []
    for pno in range(d.page_count):
        pl = []
        for blk in d[pno].get_text("dict").get("blocks", []):
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                t = norm("".join(sp["text"] for sp in ln["spans"]))
                if t:
                    pl.append((t.replace(" ", ""), ln["bbox"]))
        pages.append(pl)
    d.close()
    boxes = [r for r in runs if r["box"]]
    for r in boxes:
        if not r["box"]:
            continue
        sq = r["text"].replace(" ", "")
        best = None
        for pl in pages:
            for t, bbox in pl:
                if t == sq:
                    best = bbox
                    break
            if best:
                break
        if not best:
            continue
        dx = abs(r["box"][0] - best[0])
        dy = abs(r["box"][1] - best[1])
        err = max(dx, dy)
        tot_lines += 1
        errs.append(err)
        if err <= 1.0:
            tot_within += 1

res = {
    "fonts": tot_fh * 100.0 / max(1, tot_pf),
    "colours": tot_ch * 100.0 / max(1, tot_pc),
    "position": tot_within * 100.0 / max(1, tot_lines),
    "position median twips": statistics.median(errs) * 20 if errs else 0,
    "position lines": tot_lines,
}
print("  fonts      %.2f%%  (%d/%d)" % (res["fonts"], tot_fh, tot_pf))
print("  colours    %.2f%%  (%d/%d)" % (res["colours"], tot_ch, tot_pc))
print("  position   %.2f%% within 1 pt, median %.0f twips over %d boxes"
      % (res["position"], res["position median twips"], tot_lines))
if J:
    json.dump({"summary": res, "per_doc": per}, open(J, "w"), indent=1)
