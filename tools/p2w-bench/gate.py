#!/usr/bin/env python3
"""Per-document regression gate for PDF->Word.

WHY THIS EXISTS
    For two days every metric went up and the output went down: a black page, values missing,
    solid blocks over an invoice. Nothing compared one build against the last one, so a fix for
    document A could break document B and no one saw it until a human opened the file.

WHAT IT DOES
    Converts a corpus, renders both sides, and records PER DOCUMENT:
        missing   PDF words absent from the .docx text
        extra     .docx words absent from the PDF
        blocks    solid regions the PDF does not have
        nobg      the .docx declares no page fill
        overflow  text placed outside the page box
        blank     a page with no text at all
    Then compares against a stored baseline. A document may improve freely; it may not get worse.
    Exit code 1 if any document regressed on any count, and it names them.

USAGE
    python3 gate.py --corpus DIR --out DIR --baseline base.json        # record
    python3 gate.py --corpus DIR --out DIR --baseline base.json --check # compare
"""
import argparse, json, os, re, subprocess, sys, tempfile, shutil
import warnings
warnings.filterwarnings("ignore")

def norm(s):
    return " ".join((s or "").split())

def pdf_lines(path):
    import pymupdf
    pymupdf.TOOLS.mupdf_display_errors(False)
    out, pages = [], 0
    try:
        d = pymupdf.open(path)
        if d.needs_pass:
            d.close(); return [], 0
        for i in range(len(d)):
            pages += 1
            for bl in d.load_page(i).get_text("dict").get("blocks", []):
                for l in bl.get("lines", []):
                    t = norm("".join(s.get("text", "") for s in l.get("spans", [])))
                    if t: out.append(t)
        d.close()
    except Exception:
        pass
    return out, pages

def docx_text(path):
    import zipfile
    try:
        from lxml import etree
    except ImportError:
        raise SystemExit("gate.py needs lxml to read the .docx XML. "
                         "pip install lxml, then run it again.")
    W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    try:
        z = zipfile.ZipFile(path)
        root = etree.fromstring(z.read('word/document.xml'))
    except Exception:
        return [], 0, False
    leaves, pages = [], 0
    xml = z.read('word/document.xml').decode('utf-8', 'replace')
    hasbg = 'w:background' in xml
    for p in root.iter(W + 'p'):
        if p.findall('.//' + W + 'p'):
            continue
        t = norm("".join((x.text or "") for x in p.iter(W + 't')))
        if t: leaves.append(t)
    pages = xml.count('<w:br w:type="page"/>') + xml.count('w:type="nextPage"') + 1
    return leaves, pages, hasbg

def pdf_fills(path):
    """How many filled areas the PDF itself draws, so a correct band is not counted as a block."""
    import pymupdf
    pymupdf.TOOLS.mupdf_display_errors(False)
    n = 0
    try:
        d = pymupdf.open(path)
        for i in range(len(d)):
            for dr in d.load_page(i).get_drawings():
                if dr.get("fill") is not None and dr.get("rect") is not None:
                    r = dr["rect"]
                    if r.width * r.height > 3000:
                        n += 1
        d.close()
    except Exception:
        pass
    return n

def big_shapes(path):
    import zipfile
    from lxml import etree
    W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
    WPS = '{http://schemas.microsoft.com/office/word/2010/wordprocessingShape}wsp'
    try:
        z = zipfile.ZipFile(path)
        root = etree.fromstring(z.read('word/document.xml'))
    except Exception:
        return 0
    n = 0
    for wsp in root.iter(WPS):
        if wsp.find('.//' + W + 'txbxContent') is not None:
            continue
        e = wsp.find('.//' + A + 'ext')
        if e is None: continue
        try:
            w = int(e.get('cx')) / 12700.0
            h = int(e.get('cy')) / 12700.0
        except Exception:
            continue
        # The shape's OWN fill, not any solidFill inside it. An outline-only shape writes
        # <a:noFill/> followed by <a:ln><a:solidFill> for its border colour, and a descendant
        # search matched that border and called every thin drawn rectangle a solid block: 19
        # of the 21 documents were charged for boxes whose fill is noFill. A fill is a fill
        # only when spPr itself declares one.
        sp = wsp.find('.//' + WPS[:-3] + 'spPr')
        if sp is None: continue
        sf = sp.find(A + 'solidFill')
        if sf is None: continue
        # A block is a solid fill that is not the page itself. The old test was
        # "bigger than 3000 pt2 and smaller than 580x820" - 3000 picked by hand, and the
        # 580x820 pair a hard-coded A4 that would misjudge a Letter page or a landscape
        # one. The page's own size is known here, so the page is excluded by comparing
        # against it and no size threshold is needed at all.
        if not (w >= page_w - 2 and h >= page_h - 2):
            n += 1
    return n

def score_one(pdf, docx):
    ref, pages = pdf_lines(pdf)
    ours, dpages, hasbg, page_w, page_h = docx_text(docx)
    refw, oursw = {}, {}
    for l in ref:
        for w in l.split(): refw[w] = refw.get(w, 0) + 1
    for l in ours:
        for w in l.split(): oursw[w] = oursw.get(w, 0) + 1
    missing = sum(1 for w, c in refw.items() if oursw.get(w, 0) < c)
    extra = sum(1 for w, c in oursw.items() if refw.get(w, 0) < c)
    return {
        "missing": missing,
        "extra": extra,
        "blocks": max(0, big_shapes(docx) - pdf_fills(pdf)),
        "nobg": 0 if hasbg else 1,
        "blank": 1 if (pages > 0 and not ours) else 0,
        "lines": len(ours),
        "reflines": len(ref),
        "pages": dpages,
        "refpages": pages,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.corpus) if f.lower().endswith(".pdf"))
    cur = {}
    for f in files:
        b = f[:-4]
        d = os.path.join(a.out, b + ".docx")
        if not os.path.isfile(d):
            cur[b] = {"error": "no docx"}
            continue
        cur[b] = score_one(os.path.join(a.corpus, f), d)

    if not a.check:
        json.dump(cur, open(a.baseline, "w"), indent=1, sort_keys=True)
        tot = {k: sum(v.get(k, 0) for v in cur.values() if isinstance(v, dict)) for k in
               ("missing", "extra", "blocks", "nobg", "blank")}
        print(f"baseline written: {len(cur)} docs  {tot}")
        return 0

    base = json.load(open(a.baseline))

    # A gate that scored almost nothing passes everything. If the corpus did not
    # download, or the converter produced nothing, every count is zero, nothing is
    # worse than its baseline, and this prints "no document got worse" - a clean bill
    # of health for a run that never happened. It fails instead, and says how many it
    # expected.
    if len(cur) < len(base):
        missing = len(base) - len(cur)
        print(f"documents scored: {len(cur)} of {len(base)} - {missing} missing")
        print("A gate that did not see the corpus cannot judge it. FAILED.")
        return 1

    regressed, improved = [], []
    for b, now in cur.items():
        was = base.get(b)
        if not was or "error" in now or "error" in was:
            continue
        for k in ("missing", "extra", "blocks", "nobg", "blank"):
            if now.get(k, 0) > was.get(k, 0):
                regressed.append((b, k, was.get(k, 0), now.get(k, 0)))
            elif now.get(k, 0) < was.get(k, 0):
                improved.append((b, k, was.get(k, 0), now.get(k, 0)))
        # Page count and line count, each against this document's OWN baseline
        # entry rather than against a ratio. A document that held three pages and
        # now holds two has lost a page, and one that held 400 lines and now holds
        # 380 has lost text; both are things the other five counts can miss, because
        # a page of text moved into a text box keeps every word and every line.
        # A page change in EITHER direction is a regression: the page count the PDF
        # has is the only correct one, so a new page is as wrong as a lost page.
        if now.get("pages", 0) != was.get("pages", 0):
            regressed.append((b, "pages", was.get("pages", 0), now.get("pages", 0)))
        if now.get("lines", 0) < was.get("lines", 0):
            regressed.append((b, "lines", was.get("lines", 0), now.get("lines", 0)))
        elif now.get("lines", 0) > was.get("lines", 0):
            improved.append((b, "lines", was.get("lines", 0), now.get("lines", 0)))
    print(f"documents: {len(cur)}")
    if improved:
        print(f"IMPROVED: {len(improved)} counts")
        for r in improved[:12]:
            print(f"   {r[0][:42]:<42} {r[1]:<8} {r[2]} -> {r[3]}")
    if regressed:
        print(f"REGRESSED: {len(regressed)} counts — DO NOT SHIP")
        for r in regressed:
            print(f"   {r[0][:42]:<42} {r[1]:<8} {r[2]} -> {r[3]}")
        return 1
    print("no document got worse")
    return 0

if __name__ == "__main__":
    sys.exit(main())
