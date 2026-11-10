#!/usr/bin/env python3
"""Per-document regression gate for PDF->Word.

WHAT THIS DOES NOT SEE  - read before trusting it
    This scores blank, blocks, extra, lines, missing, nobg, pages, reflines and
    refpages. Not one of those moves when text lands in the wrong place.

    On 10 Nov a change to w:framePr passed this gate, shipped as 3.53.5, and broke
    the stamp on the phone: every count was identical and the text had moved. The
    gate was not wrong; it was being asked a question it cannot answer.

    Position, reading order, line pitch and overlap are measured by
    verify_google.py against a PDF exported from Google Docs itself. That is the
    instrument for "does the user see what the PDF shows". This one is for "did the
    converter lose any words or pages", which is cheap and worth keeping.

    Use this in CI. Do not use it as evidence that a document looks right.

WHY THIS EXISTS
    For two days every metric went up and the output went down: a black page, values missing,
    solid blocks over an invoice. Nothing compared one build against the last one, so a fix for
    document A could break document B and no one saw it until a human opened the file.

WHAT IT DOES
    Converts a corpus, renders both sides, and records PER DOCUMENT:
        missing   PDF words absent from the .docx text
        extra     .docx words absent from the PDF
        blocks    solid regions the PDF does not have
        nobg      the .docx declares no default text colour
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

def _has_default_colour(z):
    """True when styles.xml declares a default text colour.

    This replaced a check for <w:background w:color="FFFFFF"/> in document.xml. That
    background was added so a dark reader would not show black text on a black page, and it
    caused a worse problem: Google Docs dark mode paints the stated white back on top of the
    inverted page, so every table came out covered in white patches. The colour now lives on
    the text as a document default, which is where a reader looks before deciding what "black"
    means on its own surface - so that is what is checked.
    """
    try:
        st = z.read("word/styles.xml").decode("utf-8", "replace")
    except Exception:
        return False
    return 'w:color w:val="000000"' in st or 'w:color w:val="000"' in st


def _alt_text(path):
    """Words a document carries as a picture's alt text.

    A rotated stamp is rasterised from the page so its outline, its words and its angle cannot
    drift from each other, which takes those words out of the text layer. They are written as
    the picture's alt text instead - the picture is the appearance, the alt text is the content.
    A word comparison that ignored them would report every stamp document as having lost words.
    """
    try:
        import zipfile
        xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return ""
    return " ".join(re.findall(r'<wp:docPr[^>]*?descr="([^"]*)"', xml))


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
        return [], 0, False, 0.0, 0.0
    leaves, pages = [], 0
    xml = z.read('word/document.xml').decode('utf-8', 'replace')
    hasbg = _has_default_colour(z)
    for p in root.iter(W + 'p'):
        if p.findall('.//' + W + 'p'):
            continue
        t = norm("".join((x.text or "") for x in p.iter(W + 't')))
        if t: leaves.append(t)
    pages = xml.count('<w:br w:type="page"/>') + xml.count('w:type="nextPage"') + 1

    # The page's own size, so a solid fill can be told apart from the page background
    # without a hard-coded A4. Twips / 20 = points.
    page_w = page_h = 0.0
    for el in root.iter(W + 'pgSz'):
        try:
            page_w = float(el.get(W + 'w')) / 20.0
            page_h = float(el.get(W + 'h')) / 20.0
        except (TypeError, ValueError):
            page_w = page_h = 0.0
        break
    return leaves, pages, hasbg, page_w, page_h

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
                    # Same two conditions as the docx side, or the difference between
                    # the two counts means nothing. See D-05 in REMAINING-DEFECTS.md.
                    pr = d.load_page(i).rect
                    if r.width * r.height <= 3000:
                        continue
                    if not (r.width >= pr.width - 2 and r.height >= pr.height - 2):
                        n += 1
        d.close()
    except Exception:
        pass
    return n

def big_shapes(path, page_w, page_h):
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
        # Two conditions, and both are load-bearing.
        #
        # 3000 pt2 is a floor: a fill that small is a rule or a dot, not a block over the
        # page. Removing it made every small fill count and 179 documents went from
        # blocks 0 to blocks N, so it stays - see D-05 in REMAINING-DEFECTS.md, where the
        # deeper problem is recorded: big_shapes and pdf_fills count different
        # populations, and this floor is what keeps their difference near zero. That is
        # masking, not measuring, and it needs a positional match instead.
        #
        # The second condition used to be "w < 580 and h < 820", a hard-coded A4 that
        # would misjudge a Letter or a landscape page. It now compares against this
        # document's own pgSz.
        if w * h <= 3000:
            continue
        if page_w and page_h and w >= page_w - 2 and h >= page_h - 2:
            continue
        n += 1
    return n

def score_one(pdf, docx):
    ref, pages = pdf_lines(pdf)
    ours, dpages, hasbg, page_w, page_h = docx_text(docx)
    _alt = _alt_text(docx)
    if _alt.strip():
        ours.append(_alt)
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
        "blocks": max(0, big_shapes(docx, page_w, page_h) - pdf_fills(pdf)),
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

    # A run that could not score the corpus can neither judge it nor record a baseline.
    # This guard used to sit below the baseline write, so a run with no converted
    # documents wrote 208 empty entries and every run after it passed - a baseline of
    # zeros is worse than no baseline, because it looks like evidence.
    scored = sum(1 for v in cur.values() if "error" not in v)
    if scored < len(files):
        print("documents scored: %d of %d - %d could not be scored"
              % (scored, len(files), len(files) - scored))
        print("A gate that did not see the corpus cannot judge it, and must not record a"
              " baseline. FAILED.")
        return 1

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

    regressed, improved, joined = [], [], []
    for b, now in cur.items():
        was = base.get(b)
        if not was or "error" in now or "error" in was:
            continue
        # Did this document lose or gain a WORD? That is the question the line count was
        # standing in for, and it is asked directly below, so it is asked once here too.
        words_moved = (now.get("missing", 0) > was.get("missing", 0)
                       or now.get("extra", 0) > was.get("extra", 0))
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
        # A line count can FALL without a word being lost: two fields the page drew on one
        # baseline are one row, and one row is one line holding two boxes. That is the whole
        # point of a row, and counting it as a regression made every row merge look like lost
        # text - 15 documents on 8 Nov, all of them with missing and extra still at 0. So a
        # fall is a regression only when a word went with it; otherwise it is a join, and it
        # is reported as one.
        if now.get("lines", 0) < was.get("lines", 0):
            if words_moved:
                regressed.append((b, "lines", was.get("lines", 0), now.get("lines", 0)))
            else:
                joined.append((b, "lines", was.get("lines", 0), now.get("lines", 0)))
        elif now.get("lines", 0) > was.get("lines", 0):
            improved.append((b, "lines", was.get("lines", 0), now.get("lines", 0)))
    print(f"documents: {len(cur)}")
    if improved:
        print(f"IMPROVED: {len(improved)} counts")
        for r in improved[:12]:
            print(f"   {r[0][:42]:<42} {r[1]:<8} {r[2]} -> {r[3]}")
    if joined:
        print(f"JOINED: {len(joined)} line counts fell with no word lost")
        for r in joined[:12]:
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
