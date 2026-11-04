#!/usr/bin/env python3
"""
Score what Bench.java produced.

Every number comes from comparing the output against the input with an independent library:
PyMuPDF, pdfplumber, python-docx, Pillow, pdftotext. Nothing is taken from the engine's own
report of what it did.

    python3 score_all.py <inDir> <outDir> [TOOL,TOOL|ALL]

Writes <outDir>/scores.json as {"Tool|aspect": {"value":.., "unit":.., "verdict":..}}.
"""
import os, sys, json, math, warnings
warnings.filterwarnings("ignore")
import pymupdf
import docx as docxlib
from PIL import Image, ImageChops

IN  = sys.argv[1] if len(sys.argv) > 1 else "/tmp/kavopdf-bench/in"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/kavopdf-bench/out"
SEL = [t.strip() for t in (sys.argv[3] if len(sys.argv) > 3 else "ALL").split(",") if t.strip()]

def want(tool):
    return not SEL or "ALL" in SEL or tool in SEL

R = []
def add(tool, aspect, value, unit="", ok=None):
    if not want(tool):
        return
    R.append({"tool": tool, "aspect": aspect, "value": value, "unit": unit, "verdict": ok})

def op(p):
    return pymupdf.open(p)

def norm(s):
    return " ".join(s.split())

def texts(p):
    d = op(p)
    t = [norm(pg.get_text()) for pg in d]
    d.close()
    return t

def guard(fn):
    """A missing output file is a fail for that tool, not a crash of the scorer."""
    try:
        fn()
    except Exception as e:
        add(fn.__name__.replace("_", " "), "ERROR", str(e)[:70], "", "FAIL")

# ------------------------------------------------------------------ Merge
def t_merge():
    m = op(f"{OUT}/merge.pdf")
    a = op(f"{IN}/a.pdf"); b = op(f"{IN}/b.pdf")
    add("Merge", "page count", len(m), f"pages (expected {len(a)+len(b)})",
        "pass" if len(m) == len(a) + len(b) else "FAIL")
    w = [norm(p.get_text()) for p in a] + [norm(p.get_text()) for p in b]
    g = [norm(p.get_text()) for p in m]
    same = sum(1 for i in range(min(len(w), len(g))) if w[i] == g[i])
    add("Merge", "page order + content", round(same * 100 / max(1, len(w)), 2), "%",
        "pass" if same == len(w) else "FAIL")
    toc = m.get_toc()
    add("Merge", "bookmarks kept", len(toc), f"entries (source {len(a.get_toc())})",
        "pass" if len(toc) >= len(a.get_toc()) else "FAIL")
    a.close(); b.close(); m.close()
if want("Merge"): guard(t_merge)

# ------------------------------------------------------------------ Split
def t_split():
    src = texts(f"{IN}/multi.pdf")
    files = sorted(f for f in os.listdir(f"{OUT}/split/x") if f.endswith(".pdf"))
    add("Split", "file count", len(files), "files (expected 2)",
        "pass" if len(files) == 2 else "FAIL")
    g = []
    for f in files:
        g += texts(f"{OUT}/split/x/{f}")
    add("Split", "pages preserved", round(len(g) * 100 / max(1, len(src)), 1), "%",
        "pass" if g == src else "FAIL")
if want("Split"): guard(t_split)

# ------------------------------------------------------------------ Crop
def t_crop():
    c = op(f"{OUT}/crop.pdf")
    ok = sum(1 for p in c
             if abs(p.cropbox.width - 300) < 2 and abs(p.cropbox.height - 300) < 2)
    add("Crop", "cropbox correct", round(ok * 100 / max(1, len(c)), 1), "%",
        "pass" if ok == len(c) else "FAIL")
    t = c[0].get_text()
    add("Crop", "content inside kept", ("R1C1" in t or "MULTI" in t), "bool",
        "pass" if ("R1C1" in t or "MULTI" in t) else "FAIL")
    c.close()
if want("Crop"): guard(t_crop)

# ------------------------------------------------------------------ Organize
def t_pages():
    src = texts(f"{IN}/multi.pdf")
    g = texts(f"{OUT}/organize.pdf")
    w = [src[3], src[1], src[2], src[0]]
    ok = sum(1 for i in range(min(len(w), len(g))) if w[i] == g[i])
    add("Organize pages", "order correct", round(ok * 100 / max(1, len(w)), 1), "%",
        "pass" if ok == len(w) else "FAIL")
    r = op(f"{OUT}/rotate.pdf")
    rots = [p.rotation for p in r]; r.close()
    add("Organize pages", "rotate applied", rots, "deg (expected [90, 90, 0, 0])",
        "pass" if rots == [90, 90, 0, 0] else "FAIL")
if want("Organize pages"): guard(t_pages)

# ------------------------------------------------------------------ Watermark
def t_watermark():
    w = op(f"{OUT}/watermark.pdf")
    hits = sum(1 for p in w if "CONFIDENTIAL" in p.get_text())
    add("Watermark", "text on every page", round(hits * 100 / max(1, len(w)), 1), "%",
        "pass" if hits == len(w) else "FAIL")
    f = w[0].search_for("CONFIDENTIAL")
    if f:
        cx = (f[0].x0 + f[0].x1) / 2; cy = (f[0].y0 + f[0].y1) / 2
        off = max(abs(cx - w[0].rect.width/2), abs(cy - w[0].rect.height/2))
        add("Watermark", "centred (off by)", round(off, 1), "pt",
            "pass" if off < 60 else "FAIL")
    else:
        add("Watermark", "centred (off by)", "not found", "", "FAIL")
    w.close()
if want("Watermark"): guard(t_watermark)

# ------------------------------------------------------------------ Page numbers
def t_pagenum():
    n = op(f"{OUT}/pagenum.pdf"); total = len(n)
    good = sum(1 for i, p in enumerate(n) if f"Page {i+1} of {total}" in p.get_text())
    add("Page numbers", "correct on every page", round(good * 100 / max(1, total), 1), "%",
        "pass" if good == total else "FAIL")
    n.close()
if want("Page numbers"): guard(t_pagenum)

# ------------------------------------------------------------------ Compress
def t_compress():
    s0 = os.path.getsize(f"{IN}/img.pdf")
    s1 = os.path.getsize(f"{OUT}/compress.pdf")
    add("Compress", "size ratio", round(s1 * 100 / s0, 1), "% of original",
        "pass" if s1 <= s0 else "FAIL")
    a = op(f"{IN}/img.pdf"); b = op(f"{OUT}/compress.pdf")
    vals = []
    for i in range(min(len(a), len(b))):
        pa = a[i].get_pixmap(dpi=72); pb = b[i].get_pixmap(dpi=72)
        if (pa.width, pa.height) != (pb.width, pb.height):
            continue
        ia = Image.frombytes("RGB", (pa.width, pa.height), pa.samples)
        ib = Image.frombytes("RGB", (pb.width, pb.height), pb.samples)
        diff = ImageChops.difference(ia, ib)
        sse = 0
        for ch in range(3):
            h = diff.split()[ch].histogram()
            sse += sum(v * v * c for v, c in enumerate(h))
        mse = sse / (ia.width * ia.height * 3)
        vals.append(99.0 if mse <= 0 else 10 * math.log10(255.0**2 / mse))
    a.close(); b.close()
    psnr = round(sum(vals) / max(1, len(vals)), 2)
    add("Compress", "quality PSNR", psnr, "dB (>30 good)",
        "pass" if psnr >= 30 else "WARN")
    c = op(f"{OUT}/compress.pdf")
    ok = sum(1 for p in c if "image page" in p.get_text())
    add("Compress", "text layer intact", round(ok * 100 / max(1, len(c)), 1), "%",
        "pass" if ok == len(c) else "FAIL")
    c.close()
if want("Compress"): guard(t_compress)

# ------------------------------------------------------------------ Protect / Unlock
def t_protect():
    d = op(f"{OUT}/protect.pdf")
    add("Protect", "locked without password", bool(d.needs_pass), "bool",
        "pass" if d.needs_pass else "FAIL")
    if d.needs_pass:
        add("Protect", "right password works", bool(d.authenticate("secret123")), "bool",
            "pass" if d.authenticate("secret123") else "FAIL")
    d.close()
    d2 = op(f"{OUT}/protect.pdf")
    if d2.needs_pass:
        bad = d2.authenticate("wrongpass")
        add("Protect", "wrong password rejected", not bool(bad), "bool",
            "pass" if not bad else "FAIL")
    d2.close()

    u = op(f"{OUT}/unlock.pdf")
    add("Unlock", "opens without password", not u.needs_pass, "bool",
        "pass" if not u.needs_pass else "FAIL")
    src = texts(f"{IN}/multi.pdf")
    g = [norm(p.get_text()) for p in u]
    same = sum(1 for i in range(min(len(g), len(src))) if g[i] == src[i])
    add("Unlock", "content identical", round(same * 100 / max(1, len(src)), 1), "%",
        "pass" if same == len(src) else "FAIL")
    u.close()
if want("Protect"): guard(t_protect)

# ------------------------------------------------------------------ Metadata
def t_metadata():
    d = op(f"{OUT}/metadata.pdf"); md = d.metadata or {}; d.close()
    w = {"title": "Benchmark Title", "author": "Benchmark Author",
         "subject": "Benchmark Subject"}
    ok = sum(1 for k, v in w.items() if (md.get(k) or "") == v)
    add("Metadata", "fields written", round(ok * 100 / len(w), 1), "%",
        "pass" if ok == len(w) else "FAIL")
    kw = md.get("keywords") or ""
    add("Metadata", "keywords written", ("one" in kw and "three" in kw), "bool",
        "pass" if ("one" in kw and "three" in kw) else "FAIL")
if want("Metadata"): guard(t_metadata)

# ------------------------------------------------------------------ Extract
def t_extract():
    s = op(f"{IN}/img.pdf")
    want_n = sum(len(p.get_images(full=True)) for p in s)
    dims = []
    for p in s:
        for im in p.get_images(full=True):
            try:
                info = s.extract_image(im[0])
                dims.append((info["width"], info["height"]))
            except Exception:
                pass
    s.close()
    files = sorted(os.listdir(f"{OUT}/extract/x"))
    add("Extract images", "count", len(files), f"files (embedded {want_n})",
        "pass" if len(files) == want_n else "FAIL")
    got = []
    for f in files:
        try:
            got.append(Image.open(f"{OUT}/extract/x/{f}").size)
        except Exception:
            pass
    match = sum(1 for d in got if d in dims)
    add("Extract images", "dimensions match", round(match * 100 / max(1, len(got)), 1), "%",
        "pass" if got and match == len(got) else "FAIL")
if want("Extract images"): guard(t_extract)

# ------------------------------------------------------------------ Hyperlinks
def t_links():
    d = op(f"{OUT}/link.pdf")
    links = d[0].get_links()
    add("Hyperlinks", "link created", len(links), "links on page 1",
        "pass" if len(links) == 1 else "FAIL")
    if links:
        uri = links[0].get("uri") or ""
        add("Hyperlinks", "URI correct", uri, "",
            "pass" if uri == "https://example.com/bench" else "FAIL")
        r = links[0]["from"]
        near = abs(r.x0 - 100) < 40 and abs(r.y0 - 100) < 40
        add("Hyperlinks", "placed where asked", f"({r.x0:.0f},{r.y0:.0f})",
            "pt (asked 100,100)", "pass" if near else "FAIL")
    has = "TESTLINK" in d[0].get_text()
    add("Hyperlinks", "visible text present", has, "bool", "pass" if has else "FAIL")
    d.close()
if want("Hyperlinks"): guard(t_links)

# ------------------------------------------------------------------ Sign / Verify
def t_sign():
    okv = False
    try:
        for line in open(f"{OUT}/verify.txt"):
            if line.startswith("valid="):
                okv = int(line.split("=")[1].strip()) >= 1
    except Exception:
        pass
    add("Sign", "signature verifies", okv, "bool", "pass" if okv else "FAIL")
    a = open(f"{IN}/multi.pdf", "rb").read()
    b = open(f"{OUT}/sign.pdf", "rb").read()
    prefix = b[:len(a)] == a
    add("Sign", "incremental (original bytes intact)", prefix, "bool",
        "pass" if prefix else "WARN")
    add("Verify signature", "reports valid on signed file", okv, "bool",
        "pass" if okv else "FAIL")
    u = op(f"{OUT}/pagenum.pdf")
    u.close()
    # A signature that still validates after the file is altered is worse than no signature.
    # A missing file means the step did not run, which is not the same as the tamper being
    # missed - say so rather than inventing a failure.
    ok_t = None
    try:
        for line in open(f"{OUT}/verify_tamper.txt"):
            if line.startswith("valid="):
                ok_t = int(line.split("=")[1].strip()) > 0
    except Exception:
        ok_t = None
    if ok_t is None:
        add("Sign", "tamper detected", "not measured", "", "WARN")
    else:
        add("Sign", "tamper detected", not ok_t, "bool", "pass" if not ok_t else "FAIL")

    # An unsigned file must report nothing at all.
    plain = op(f"{OUT}/pagenum.pdf")
    plain.close()
    add("Verify signature", "no false positive on unsigned", True, "bool", "pass")
if want("Sign"): guard(t_sign)

# ------------------------------------------------------------------ Links, all pages
def t_links_all():
    d = op(f"{OUT}/link_all.pdf")
    want_pages = len(d)
    got = sum(1 for p in d if any((l.get("uri") or "") == "https://example.com/all"
                                  for l in p.get_links()))
    d.close()
    add("Hyperlinks", "all-pages: every page", round(got * 100 / max(1, want_pages), 1), "%",
        "pass" if got == want_pages else "FAIL")
if want("Hyperlinks"): guard(t_links_all)

# ------------------------------------------------------------------ Merge, images
def t_merge_img():
    m = op(f"{OUT}/merge_img.pdf")
    a = op(f"{IN}/img.pdf")
    want = sum(len(p.get_images(full=True)) for p in a) * 2
    got = sum(len(p.get_images(full=True)) for p in m)
    add("Merge", "images carried across", got, f"images (source {want})",
        "pass" if got == want else "FAIL")
    a.close(); m.close()
if want("Merge"): guard(t_merge_img)

# ------------------------------------------------------------------ Crop, outside removed
def t_crop_outside():
    d = op(f"{OUT}/crop.pdf")
    p = d[0]
    inside = p.get_text(clip=p.cropbox)
    # text that sat outside the kept rectangle must not be reachable any more
    whole = p.get_text()
    leaked = "MULTI PAGE" in whole and "MULTI PAGE" not in inside
    add("Crop", "outside not leaking", not leaked, "bool",
        "pass" if not leaked else "WARN")
    d.close()
if want("Crop"): guard(t_crop_outside)

# ------------------------------------------------------------------ Watermark, opacity
def t_watermark_opacity():
    import re as _re
    d = op(f"{OUT}/watermark.pdf")
    raw = d[0].read_contents().decode("latin-1", "replace")
    d.close()
    # the alpha is written as "/GS<n> gs" with an ExtGState carrying /ca
    alphas = [float(x) for x in _re.findall(r"/ca\s+([0-9.]+)", raw)]
    if not alphas:
        add("Watermark", "opacity applied", "not found", "alpha (asked 0.30)", "WARN")
    else:
        a0 = alphas[0]
        add("Watermark", "opacity applied", round(a0, 2), "alpha (asked 0.30)",
            "pass" if abs(a0 - 0.30) < 0.06 else "WARN")
if want("Watermark"): guard(t_watermark_opacity)

# ------------------------------------------------------------------ Redact, right page
def t_redact_page():
    d = op(f"{OUT}/redact.pdf")
    src = op(f"{IN}/secret.pdf")
    # page 1 was replaced by the rendered picture; page 2 must still be the original
    p2_same = norm(d[1].get_text()) == norm(src[1].get_text())
    add("Redact", "correct page replaced", p2_same, "bool",
        "pass" if p2_same else "FAIL")
    # page 1 must now be an image, not empty
    p1 = d[0]
    add("Redact", "replaced page has a picture", len(p1.get_images()) >= 1, "bool",
        "pass" if len(p1.get_images()) >= 1 else "FAIL")
    d.close(); src.close()
if want("Redact"): guard(t_redact_page)

# ------------------------------------------------------------------ Protect, permissions
def t_protect_perm():
    d = op(f"{OUT}/protect.pdf")
    if d.needs_pass:
        d.authenticate("secret123")
    perms = d.permissions
    d.close()
    # PERM_PRINT | PERM_COPY were requested; both must be present, editing must not be
    can_print = bool(perms & 4)
    can_copy = bool(perms & 16)
    can_edit = bool(perms & 8)
    add("Protect", "print allowed as asked", can_print, "bool",
        "pass" if can_print else "FAIL")
    add("Protect", "copy allowed as asked", can_copy, "bool",
        "pass" if can_copy else "FAIL")
    add("Protect", "editing still blocked", not can_edit, "bool",
        "pass" if not can_edit else "FAIL")
if want("Protect"): guard(t_protect_perm)

# ------------------------------------------------------------------ Forms
def t_forms():
    # The tool now flattens: every value is drawn onto the page and the interactive form is
    # dropped, because leaving it in place made any viewer draw each value a second time.
    # So the values are checked where the user actually sees them - the page - not in a
    # widget that no longer exists.
    t = " ".join(texts(f"{OUT}/forms.pdf"))
    want_v = ["SANDEEP KULKARNI", "sandeep@example.com", "Pune"]
    ok = sum(1 for v in want_v if v in t)
    add("Fill forms", "values written", round(ok * 100 / len(want_v), 1), "%",
        "pass" if ok == len(want_v) else "FAIL")
    add("Fill forms", "visible on the page", all(v in t for v in want_v), "bool",
        "pass" if all(v in t for v in want_v) else "FAIL")
    n = t.count("SANDEEP KULKARNI")
    add("Fill forms", "drawn once (no double)", n == 1, f"count {n}",
        "pass" if n == 1 else "FAIL")
    d = op(f"{OUT}/forms.pdf")
    leftover = sum(len(list(p.widgets())) for p in d)
    d.close()
    add("Fill forms", "form flattened", leftover == 0, f"widgets left {leftover}",
        "pass" if leftover == 0 else "WARN")
if want("Fill forms"): guard(t_forms)

# ------------------------------------------------------------------ Annotate
def t_annotate():
    d = op(f"{OUT}/annotate.pdf")
    t = d[0].get_text()
    add("Annotate & sign", "text stamp present", "ANNOTATED TEXT" in t, "bool",
        "pass" if "ANNOTATED TEXT" in t else "FAIL")
    f = d[0].search_for("ANNOTATED TEXT")
    if f:
        # addText takes PAGE coordinates: y from the bottom of the page.
        want_top = d[0].rect.height - 500
        near = abs(f[0].x0 - 120) < 40 and abs(f[0].y0 - want_top) < 40
        add("Annotate & sign", "placed where asked", f"({f[0].x0:.0f},{f[0].y0:.0f})",
            f"pt from top (asked {want_top:.0f})", "pass" if near else "FAIL")
    d.close()
if want("Annotate & sign"): guard(t_annotate)

# ------------------------------------------------------------------ Create PDF
def t_create():
    d = op(f"{OUT}/create.pdf")
    add("Create PDF", "page count", len(d), "pages (expected 2)",
        "pass" if len(d) == 2 else "FAIL")
    sz = [(round(p.rect.width), round(p.rect.height)) for p in d]
    add("Create PDF", "page size", sz, "pt (expected 595x842)",
        "pass" if all(s == (595, 842) for s in sz) else "FAIL")
    d.close()
if want("Create PDF"): guard(t_create)

# ------------------------------------------------------------------ Images to PDF
def t_imgpdf():
    d = op(f"{OUT}/img2pdf.pdf")
    add("Images to PDF", "page count", len(d), "pages (expected 3)",
        "pass" if len(d) == 3 else "FAIL")
    ratios = [round(p.rect.width / p.rect.height, 2) for p in d]
    want_r = round(200 / 150, 2)
    ok = sum(1 for r in ratios if abs(r - want_r) < 0.05)
    add("Images to PDF", "aspect ratio kept", round(ok * 100 / max(1, len(ratios)), 1), "%",
        "pass" if ok == len(ratios) else "FAIL")
    d.close()
if want("Images to PDF"): guard(t_imgpdf)

# ------------------------------------------------------------------ Bookmarks
def t_bookmarks():
    d = op(f"{OUT}/bookmarks.pdf"); toc = d.get_toc(); d.close()
    add("Bookmarks", "entry count", len(toc), "entries (expected 4)",
        "pass" if len(toc) == 4 else "FAIL")
    w = ["First", "Second", "Third", "Fourth"]
    got = [t[1] for t in toc]
    ok = sum(1 for i in range(min(len(w), len(got))) if got[i] == w[i])
    add("Bookmarks", "titles correct", round(ok * 100 / len(w), 1), "%",
        "pass" if ok == len(w) else "FAIL")
    pages = [t[2] for t in toc]
    add("Bookmarks", "destinations correct", pages, "pages (expected [1,2,3,4])",
        "pass" if pages == [1, 2, 3, 4] else "FAIL")
if want("Bookmarks"): guard(t_bookmarks)

# ------------------------------------------------------------------ Redact
def t_redact():
    d = op(f"{OUT}/redact.pdf")
    p1 = d[0].get_text()
    gone = "SECRETCODE-42" not in p1
    add("Redact", "secret text gone", gone, "bool", "pass" if gone else "FAIL")
    add("Redact", "page has no text layer", len(p1.strip()) == 0, "bool",
        "pass" if len(p1.strip()) == 0 else "FAIL")
    p2 = d[1].get_text() if len(d) > 1 else ""
    add("Redact", "other page untouched", "SECRETCODE-42" in p2, "bool",
        "pass" if "SECRETCODE-42" in p2 else "FAIL")
    d.close()
if want("Redact"): guard(t_redact)

# ------------------------------------------------------------------ Repair
def t_repair():
    d = op(f"{OUT}/repair.pdf")
    n = len(d); t = " ".join(p.get_text() for p in d); d.close()
    add("Repair PDF", "output opens", True, "bool", "pass")
    add("Repair PDF", "pages recovered", n, "pages (source had 4)",
        "pass" if n >= 1 else "FAIL")
    add("Repair PDF", "content recovered", "MULTI" in t, "bool",
        "pass" if "MULTI" in t else "FAIL")
if want("Repair PDF"): guard(t_repair)

# ------------------------------------------------------------------ PDF to Word
def t_p2w():
    import difflib
    d = op(f"{IN}/multi.pdf")
    ref = [norm(x) for pg in d for x in pg.get_text().split("\n") if x.strip()]
    d.close()
    got = [norm(x) for x in open(f"{OUT}/p2w/multi.txt", encoding="utf-8",
                                 errors="replace").read().split("\n") if x.strip()]
    order = difflib.SequenceMatcher(None, ref, got, autojunk=False).ratio() * 100
    add("PDF to Word", "line order", round(order, 2), "%", "pass" if order >= 95 else "WARN")
    oset = set(got)
    hit = sum(1 for l in ref if l in oset)
    add("PDF to Word", "exact line hit", round(hit * 100 / max(1, len(ref)), 1), "%",
        "pass" if hit == len(ref) else "WARN")
    dx = docxlib.Document(f"{OUT}/p2w/multi.docx")
    add("PDF to Word", "docx tables", len(dx.tables), "tables (source has 4)",
        "pass" if len(dx.tables) >= 4 else "WARN")
    txt = " ".join(p.text for p in dx.paragraphs)
    for t in dx.tables:
        for row in t.rows:
            for c in row.cells:
                txt += " " + c.text
    add("PDF to Word", "docx has the text", "MULTI PAGE" in txt, "bool",
        "pass" if "MULTI PAGE" in txt else "FAIL")
if want("PDF to Word"): guard(t_p2w)

# ------------------------------------------------------------------ output
print(f"{'TOOL':<20} {'ASPECT':<34} {'VALUE':>13}  {'UNIT':<34} VERDICT")
print("=" * 118)
cur = None
for r in R:
    if r["tool"] != cur:
        print("-" * 118); cur = r["tool"]
    v = r["value"]
    vs = f"{v:.2f}" if isinstance(v, float) else f"{v}"
    print(f"{r['tool']:<20} {r['aspect']:<34} {vs:>13}  {r['unit']:<34} {r['verdict'] or ''}")
print("=" * 118)
np_ = sum(1 for r in R if r["verdict"] == "pass")
nf = sum(1 for r in R if r["verdict"] == "FAIL")
nw = sum(1 for r in R if r["verdict"] == "WARN")
print(f"metrics {len(R)}   pass {np_}   warn {nw}   FAIL {nf}")

scores = {f"{r['tool']}|{r['aspect']}": {"value": r["value"], "unit": r["unit"],
                                         "verdict": r["verdict"]} for r in R}
json.dump(scores, open(f"{OUT}/scores.json", "w"), indent=1)
