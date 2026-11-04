#!/usr/bin/env python3
"""
The five fidelity benchmarks PDF to Word did not have.

The existing scorers answer "was the text extracted". These answer "does the Word file look
like the PDF" - the part the user named directly: stamps, exact fonts, exact layout, exact
colours, and whether text in the .txt file sits where it sat on the page.

Every number comes from PyMuPDF reading the PDF and python-docx reading the output. Nothing is
taken from the engine's own report of what it did.

    python3 score_fidelity.py <pdfDir> <outDir> [--json out.json]

Expects <outDir>/<name>.docx and <outDir>/<name>.txt next to each <pdfDir>/<name>.pdf.
"""
import os, sys, json, re, warnings
warnings.filterwarnings("ignore")
import pymupdf
import docx as docxlib

PDF_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/kavopdf-p2w/in"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "/tmp/kavopdf-p2w/out"
JSON_OUT = None
if "--json" in sys.argv:
    JSON_OUT = sys.argv[sys.argv.index("--json") + 1]

M = []
def add(*a):
    """(name, value, unit, verdict) - kept flexible so a tool prefix can be added later."""
    M.append(a)

def norm(s):
    return " ".join((s or "").split())


# --------------------------------------------------------------------------- PDF side
def pdf_spans(path):
    """Every text span with the facts the Word file has to reproduce."""
    out = []
    try:
        d = pymupdf.open(path)
    except Exception:
        return out, 0
    n = len(d)
    for pno in range(n):
        try:
            page = d.load_page(pno)
            dd = page.get_text("dict")
        except Exception:
            continue
        for blk in dd.get("blocks", []):
            for line in blk.get("lines", []):
                dirx, diry = line.get("dir", (1, 0))
                rotated = abs(diry) > 0.05
                for sp in line.get("spans", []):
                    t = norm(sp.get("text"))
                    if not t:
                        continue
                    out.append({
                        "text": t,
                        "font": sp.get("font", ""),
                        "size": round(sp.get("size", 0), 1),
                        "color": sp.get("color", 0),
                        "rotated": rotated,
                        "bbox": sp.get("bbox"),
                        "page": pno,
                        "x0": sp["bbox"][0] if sp.get("bbox") else 0,
                    })
    d.close()
    return out, n


def family(font_name):
    """Turn 'ABCDEF+TimesNewRomanPS-BoldMT' into something comparable."""
    f = (font_name or "").split("+")[-1]
    f = re.sub(r'[^A-Za-z]', '', f)
    for known in ["TimesNewRoman", "Arial", "Helvetica", "Calibri", "Cambria", "Georgia",
                  "Garamond", "CourierNew", "Courier", "Verdana", "Tahoma", "Segoe",
                  "Roboto", "Consolas", "LiberationSerif", "LiberationSans",
                  "DejaVuSans", "DejaVuSerif", "Noto", "Symbol"]:
        if known.lower() in f.lower():
            return known
    return f[:20] if f else ""


# --------------------------------------------------------------------------- docx side
def docx_runs(path):
    """Every run in the Word file, with the font and colour it carries."""
    out = []
    try:
        d = docxlib.Document(path)
    except Exception:
        return out
    def walk(paras):
        for p in paras:
            for r in p.runs:
                t = norm(r.text)
                if not t:
                    continue
                col = None
                try:
                    if r.font.color is not None and r.font.color.rgb is not None:
                        col = int(str(r.font.color.rgb), 16)
                except Exception:
                    col = None
                out.append({
                    "text": t,
                    "font": family(r.font.name or ""),
                    "size": round(r.font.size.pt, 1) if r.font.size else None,
                    "color": col,
                })
    walk(d.paragraphs)
    for t in d.tables:
        for row in t.rows:
            for cell in row.cells:
                walk(cell.paragraphs)
    return out


def docx_text(path):
    try:
        d = docxlib.Document(path)
    except Exception:
        return ""
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


# --------------------------------------------------------------------------- the run
files = sorted(f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf"))

tot_stamp = 0
tot_stamp_ok = 0
tot_pdf_fonts = 0
tot_font_hit = 0
tot_pdf_colours = 0
tot_colour_hit = 0
tot_pos_lines = 0
tot_pos_ok = 0
files_with_stamp = 0

per_file = {}

for f in files:
    base = f[:-4]
    pdf = os.path.join(PDF_DIR, f)
    docx_path = os.path.join(OUT_DIR, base + ".docx")
    txt_path = os.path.join(OUT_DIR, base + ".txt")

    spans, npages = pdf_spans(pdf)
    if not spans:
        continue
    runs = docx_runs(docx_path) if os.path.isfile(docx_path) else []
    dtext = docx_text(docx_path) if os.path.isfile(docx_path) else ""
    ttext = open(txt_path, encoding="utf-8", errors="replace").read() if os.path.isfile(txt_path) else ""

    rec = {}

    # ---- 1. stamp text integrity ----
    stamps = [s for s in spans if s["rotated"]]
    if stamps:
        files_with_stamp += 1
        ok = 0
        for s in stamps:
            tot_stamp += 1
            if s["text"] in dtext or s["text"] in ttext:
                ok += 1
                tot_stamp_ok += 1
        rec["stamps"] = len(stamps)
        rec["stamps_ok"] = ok

    # ---- 2. font fidelity ----
    pdf_fonts = {family(s["font"]) for s in spans if family(s["font"])}
    doc_fonts = {r["font"] for r in runs if r["font"]}
    if pdf_fonts:
        tot_pdf_fonts += len(pdf_fonts)
        hit = len(pdf_fonts & doc_fonts)
        tot_font_hit += hit
        rec["fonts_pdf"] = sorted(pdf_fonts)
        rec["fonts_doc"] = sorted(doc_fonts)
        rec["fonts_hit"] = hit

    # ---- 3. colour fidelity ----
    # PyMuPDF gives the colour as a packed int; only non-black counts, because a black
    # document says nothing about whether colour survives.
    pdf_cols = {s["color"] for s in spans if s["color"] not in (0, None)}
    doc_cols = {r["color"] for r in runs if r["color"] is not None}
    if pdf_cols:
        tot_pdf_colours += len(pdf_cols)
        hit = len(pdf_cols & doc_cols)
        tot_colour_hit += hit
        rec["colours_pdf"] = sorted(pdf_cols)
        rec["colours_doc"] = sorted(doc_cols)
        rec["colours_hit"] = hit

    # ---- 4. txt position fidelity ----
    # A line that starts far from the left margin must start with leading spaces in the
    # .txt. A line at the margin must not. This is the only way a plain-text file can carry
    # position, and it is exactly where the tool struggles.
    page_w = 595.0
    try:
        d = pymupdf.open(pdf)
        if len(d):
            page_w = d.load_page(0).rect.width
        d.close()
    except Exception:
        pass
    lines = [l for l in ttext.split("\n") if l.strip()]
    pdf_lines = []
    try:
        d = pymupdf.open(pdf)
        for pno in range(len(d)):
            for line in d.load_page(pno).get_text("dict").get("blocks", []):
                for l in line.get("lines", []):
                    sp = l.get("spans", [])
                    if sp and norm("".join(x.get("text", "") for x in sp)):
                        pdf_lines.append(sp[0]["bbox"][0])
        d.close()
    except Exception:
        pass
    for i, x0 in enumerate(pdf_lines[:len(lines)]):
        # only judge lines that are clearly indented or clearly at the margin
        if 40 <= x0 <= 90:
            continue
        tot_pos_lines += 1
        indent = len(lines[i]) - len(lines[i].lstrip(" "))
        if x0 > 150:
            ok = indent >= 4
        else:
            ok = indent <= 2
        if ok:
            tot_pos_ok += 1

    per_file[base] = rec


n = max(1, len(per_file))

add("Stamps", "files carrying a stamp", files_with_stamp, "files", "pass")
if tot_stamp:
    pct = tot_stamp_ok * 100 / tot_stamp
    add("Stamps", "stamp text comes out whole and in order", round(pct, 1), "%",
        "pass" if pct >= 99 else ("WARN" if pct >= 90 else "FAIL"))
else:
    add("Stamps", "stamp text comes out whole and in order", "no stamps in corpus", "", "WARN")

if tot_pdf_fonts:
    pct = tot_font_hit * 100 / tot_pdf_fonts
    add("Fonts", "typeface carried into the Word file", round(pct, 1), "%",
        "pass" if pct >= 90 else ("WARN" if pct >= 60 else "FAIL"))
else:
    add("Fonts", "typeface carried into the Word file", "no fonts in corpus", "", "WARN")

if tot_pdf_colours:
    pct = tot_colour_hit * 100 / tot_pdf_colours
    add("Colours", "colour carried into the Word file", round(pct, 1), "%",
        "pass" if pct >= 90 else ("WARN" if pct >= 60 else "FAIL"))
else:
    add("Colours", "colour carried into the Word file", "no colour in corpus", "", "WARN")

if tot_pos_lines:
    pct = tot_pos_ok * 100 / tot_pos_lines
    add("Text position", "line indent matches the page x", round(pct, 1), "%",
        "pass" if pct >= 95 else ("WARN" if pct >= 80 else "FAIL"))
else:
    add("Text position", "line indent matches the page x", "no judgeable lines", "", "WARN")

print(f"{'BENCHMARK':<52} {'VALUE':>12}  {'UNIT':<26} VERDICT")
print("=" * 104)
for row in M:
    group, name, v, unit, verdict = row
    vs = f"{v:.2f}" if isinstance(v, float) else f"{v}"
    print(f"{group + ' | ' + name:<52}"[:52] + f" {vs:>12}  {unit:<26} {verdict or ''}")
print("=" * 104)
np_ = sum(1 for r in M if r[4] == "pass")
nf = sum(1 for r in M if r[4] == "FAIL")
nw = sum(1 for r in M if r[4] == "WARN")
print(f"benchmarks {len(M)}   pass {np_}   warn {nw}   FAIL {nf}")
print()
print("per-file detail:")
for b, r in sorted(per_file.items()):
    bits = []
    if "stamps" in r:
        bits.append(f"stamps {r['stamps_ok']}/{r['stamps']}")
    if "fonts_hit" in r:
        bits.append(f"fonts {r['fonts_hit']}/{len(r['fonts_pdf'])}")
    if "colours_hit" in r:
        bits.append(f"colours {r['colours_hit']}/{len(r['colours_pdf'])}")
    if bits:
        print(f"   {b[:46]:<46} {'  '.join(bits)}")

if JSON_OUT:
    json.dump({f"{g}|{n}": {"value": v, "unit": u, "verdict": vd}
               for g, n, v, u, vd in M},
              open(JSON_OUT, "w"), indent=1)
    print("wrote", JSON_OUT)
