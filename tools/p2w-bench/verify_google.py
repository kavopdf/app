#!/usr/bin/env python3
"""
verify_google.py - compare a Google-Docs-rendered PDF against the source PDF.

WHY THIS EXISTS
  Every earlier instrument lied. gate.py scores words, blocks, overflow, lines and
  pages, and none of those move when w:framePr is ignored or a header band lands at
  the wrong y. verify_visual.py renders through LibreOffice, which honours constructs
  Google Docs does not, so it hides exactly the faults the phone shows. Three separate
  fixes shipped "clean" and broke on the device.

  This one compares the PDF that Google Docs itself exports. If a word lands at the
  left margin in Docs, it lands there in this export too.

USAGE
  python3 verify_google.py <source.pdf> <google-export.pdf> [--docx <engine.docx>] [--json out.json]

EXIT
  0 = all checks pass, 1 = one or more failed, 2 = could not run

THRESHOLDS (a document passes only if every one holds)
  completeness  every count and every style attribute matches the source
  position      ONE displacement standard, one check, three clauses (18_displacement):
                on every page the number of upright runs further than
                clamp(0.35*size, 1.5, 4.5) pt from their source baseline must not exceed
                max(2, ceil(0.05*n)); no page may have every run out; and no single upright
                run may be more than twice its own tolerance out. Order > 95 %
  visual        no invisible text, no text-on-text, no page overflow, no extra page
"""
import os, sys, json, re, collections, statistics, difflib, math, zipfile
import xml.etree.ElementTree as ET

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def runs(page, page_no=0):
    """Every text span on a page, with the attributes we compare."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                t = sp.get("text", "")
                if not t.strip():
                    continue
                out.append({
                    "page": page_no,
                    "text": t,
                    "x": round(sp["bbox"][0], 2),
                    "y": round(sp["bbox"][1], 2),
                    "x1": round(sp["bbox"][2], 2),
                    "y1": round(sp["bbox"][3], 2),
                    "size": round(sp["size"], 1),
                    "font": sp.get("font", ""),
                    "colour": sp.get("color", 0),
                    "weight": ("b" if (sp.get("flags", 0) & 16) else "") +
                              ("i" if (sp.get("flags", 0) & 2) else ""),
                })
    return out


def norm_font(f):
    """Strip the subset prefix and the foundry suffix, so ABCDEF+Arial,Bold == Arial Bold."""
    f = re.sub(r"^[A-Z]{6}\+", "", f or "")
    f = f.replace(",", " ").replace("-", " ").replace("_", " ")
    return " ".join(f.split()).lower()


_STYLE_WORDS = {"bold", "bolditalic", "boldoblique", "italic", "oblique", "regular",
                "roman", "normal", "book", "semibold", "demibold"}
_PS_SUFFIX = ("psmt", "mt", "ps")


def face_name(f):
    """The FAMILY a face name belongs to, with its style stripped off.

    09_font_names counts distinct names, so "liberation sans" and "liberation sans bold" were
    two names to it while the render writes bold once, as a run property. A correct conversion
    therefore produced FEWER names and failed: constructed on 13 Nov with five style variants of
    two families against two families with bold as a flag, the document scored 58/59 and 09 was
    the ONLY failing check - 03/04/05 clean, 53 2/2, 34c 100/100, 47 extents identical.

    This strips a token from a name. It never maps a name onto a different name, so 09 still
    makes no substitution claim - that is 53's job and SAME_FACE is not consulted here. It also
    picks up the MT/PSMT/PS suffixes and the comma form that norm_font does not.
    """
    toks = norm_font(f).split()
    while toks:
        last = toks[-1]
        for suf in _PS_SUFFIX:
            if last.endswith(suf) and len(last) > len(suf):
                last = last[:-len(suf)]
                break
        if last != toks[-1]:
            toks[-1] = last
            continue
        if last in _STYLE_WORDS:
            toks.pop()
            continue
        break
    return " ".join(toks) or norm_font(f)


def order_score(s_seq, g_seq):
    """The share of source words that appear in the render IN ORDER.

    The old measure zipped the two sequences and counted equal positions, which is a SHIFT
    detector, not an order detector: one inserted word at the front moved every source word
    against its neighbour and scored 0, while the same word inserted at the END scored 100 -
    three verdicts for one edit, decided only by where it landed. Measured on 13 Nov across
    nine constructed pairs.

    SequenceMatcher on the word lists scores the longest matching blocks IN ORDER, so an
    insertion costs the inserted word rather than the whole tail, and a swap still costs.
    autojunk=False is not optional: past 200 items the default heuristic junkifies any word
    occurring in more than 1 % of the sequence, which on a 500-word page is every "the", and
    the score then depends on length rather than on the difference.
    """
    if not s_seq:
        return 100
    sm = difflib.SequenceMatcher(None, s_seq, g_seq, autojunk=False)
    return round(100.0 * sum(b.size for b in sm.get_matching_blocks()) / len(s_seq))


def norm_word(w):
    """Digits and punctuation kept; whitespace, C0 controls and case dropped.

    The C0 strip is not cosmetic. Six documents in the corpus carry U+0000 in their text
    layer and the tokeniser kept it, so 'agree' in the render could never equal '\x00agree'
    in the source: 22 tokens that no reader can see were being counted as lost words.
    """
    return re.sub(r"[\s\u00a0\x00-\x1f]+", "", w).lower()


def norm_text(t):
    """The comparison unit, as characters: whitespace, C0 controls and case dropped."""
    return re.sub(r"[\s\u00a0\x00-\x1f]+", "", t).lower()


def fill_rects(page):
    """Filled rectangles - used to find text sitting on a same-colour fill."""
    out = []
    for d in page.get_drawings():
        r = d["rect"]
        if d.get("fill") and r.width > 2 and r.height > 2:
            out.append({"rect": r, "fill": d["fill"]})
    return out


def colour_close(a, b, tol=0.06):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


# ---- perceptual colour, added for 34b --------------------------------------
# A span's colour arrives as ONE 24-bit int, and that int encodes the colour
# SPACE as much as the colour. PyMuPDF converts on the way out, so the same
# visual black arrives differently depending on how the producer painted it.
# Measured 13 Nov, two pages carrying identical black text, one drawn with
# color=(0,0,0,1) and one with color=(0,0,0):
#     'CMYK black' 0x231f20      'RGB black' 0x0
# 34b compared those ints for equality, so a visually identical document scored
# 0 % - the check was measuring the encoder, not the colour.
#
# colour_close() is not enough. It is a per-channel absolute difference: 0.137
# for that black pair against its default tolerance of 0.06, so it still scores
# 0 %. Widening the tolerance to 0.15 would blind the check everywhere to a
# change nobody can miss (0.15 of a light grey is 38 levels of 255), and the
# same absolute difference is not the same perceived difference at both ends of
# the scale: 35/255 is invisible beside black and glaring beside white.
#
# So: CIELAB with CIEDE2000, plus one explicit rule for the black point, because
# the colour space cannot be recovered per span. page.get_texttrace() reports
# colorspace 3 for BOTH pages above - it hands back converted RGB and the
# original CMYK is gone - and nothing in the text API says which operator
# painted a span.
#
# The rule is deliberately narrow, so that it fixes the encoding defect without
# going blind near black. Two colours match as "the same black" only when all of
#   - both are neutral (chroma <= 12),
#   - both are dark (L* <= 13, which is where the CMYK image sits: L* 12.2),
#   - and AT LEAST ONE of them is MuPDF's image of device CMYK K=100 %,
#     measured on this build as 0x231f20 (+/- 3 of 255).
# So #000000 against 0x231f20 passes, while #000000 against #1c1c1c (dE00 6.15)
# and against #333333 (dE00 13.4) still fire - the check does not lose its
# near-black sensitivity to buy this. What it does not cover is the same
# mismatch for a NON-neutral CMYK colour (a CMYK red arriving as its RGB
# equivalent), which would need the paint operator and is out of reach here.
# The constant is empirical and named as such: if a future MuPDF changes its
# CMYK profile, this rule stops matching and the CMYK/RGB pair fires again -
# visible as a false failure, not as a silent pass.
CMYK_BLACK = 0x231f20
BLACK_L = 13.0
BLACK_C = 12.0
BLACK_NEAR = 3         # of 255, so a rounding difference still matches
COLOUR_DE = 6.0        # CIEDE2000; ~5 is "clearly visible" in graphic arts


def _rgb01(v):
    """The 24-bit span colour as three 0..1 floats."""
    return ((v >> 16) & 255) / 255.0, ((v >> 8) & 255) / 255.0, (v & 255) / 255.0


def _lab(rgb):
    """sRGB -> CIELAB, D65 white."""
    def lin(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(x) for x in rgb)
    X = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    Y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    Z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1.0 / 3.0) if t > 216.0 / 24389.0 else (841.0 / 108.0) * t + 4.0 / 29.0
    fx, fy, fz = f(X), f(Y), f(Z)
    return 116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)


def _de00(c1, c2):
    """CIEDE2000 difference. Checked against the 34 reference pairs of
    Sharma/Wu/Dalal (2005): worst absolute error 1e-4, i.e. float noise."""
    L1, a1, b1 = c1
    L2, a2, b2 = c2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cb = (C1 + C2) / 2.0
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25.0 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0 if C1p else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0 if C2p else 0.0
    dLp = L2 - L1
    dCp = C2p - C1p
    if not C1p or not C2p:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180.0:
        dhp = h2p - h1p
    elif h2p - h1p > 180.0:
        dhp = h2p - h1p - 360.0
    else:
        dhp = h2p - h1p + 360.0
    dHp = 2.0 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2.0))
    Lbp = (L1 + L2) / 2.0
    Cbp = (C1p + C2p) / 2.0
    if not C1p or not C2p:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180.0:
        hbp = (h1p + h2p) / 2.0
    elif h1p + h2p < 360.0:
        hbp = (h1p + h2p + 360.0) / 2.0
    else:
        hbp = (h1p + h2p - 360.0) / 2.0
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30.0))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6.0))
         - 0.20 * math.cos(math.radians(4 * hbp - 63.0)))
    dTh = 30.0 * math.exp(-(((hbp - 275.0) / 25.0) ** 2))
    Rc = 2.0 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25.0 ** 7))
    Sl = 1 + (0.015 * (Lbp - 50.0) ** 2) / math.sqrt(20 + (Lbp - 50.0) ** 2)
    Sc = 1 + 0.045 * Cbp
    Sh = 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dTh)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


def _is_cmyk_black(v):
    """Is this int MuPDF's image of device CMYK 0/0/0/1?"""
    return all(abs(x - y) <= BLACK_NEAR / 255.0
               for x, y in zip(_rgb01(v), _rgb01(CMYK_BLACK)))


def colour_same(a, b):
    """True when two packed span colours are the same COLOUR, not the same int."""
    if a == b:
        return True
    la, lb = _lab(_rgb01(a)), _lab(_rgb01(b))
    if (la[0] <= BLACK_L and lb[0] <= BLACK_L
            and math.hypot(la[1], la[2]) <= BLACK_C
            and math.hypot(lb[1], lb[2]) <= BLACK_C
            and (_is_cmyk_black(a) or _is_cmyk_black(b))):
        return True
    return _de00(la, lb) <= COLOUR_DE


# ----------------------------------------------------------------------------
# the 31 checks
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# checks 32-48: the ones the first 31 did not make
#
# Added after an audit asked what the side-by-side comparison actually catches.
# It caught position well and everything else shallowly: fonts and colours were
# compared as SETS rather than per span, images and links as COUNTS rather than
# by position or target, and stroked lines - every table border in the corpus -
# were not read at all, because the only drawing attribute looked at was fill.
#
# The proof was one file: 80_gstin_pan_cin_ifsc_table has 0 filled shapes and 7
# stroked lines. A table whose borders are the only thing defining its structure
# was invisible to the verifier.
# ----------------------------------------------------------------------------
import difflib


def _shapes(page):
    """Everything on the page that can anchor text: drawn outlines and placed images.

    A stamp is an outline with text inside it. The outline is a vector path, not
    text, so every existing position check looks straight past it - they compare
    text to text, and a stamp whose outline slid twenty points away while its text
    stayed put passes all of them. That is the failure this check exists for.

    Images count as anchors too, because a converter is allowed to draw an outline
    as an image; what matters is that the text still sits in the same place
    relative to whatever encloses it.
    """
    out = []
    hs, vs = [], []          # thin rules, kept so an outline drawn as four
    for d in page.get_drawings():   # separate line paths can be rebuilt
        r = d["rect"]
        if r.width >= 8 and r.height >= 8:
            out.append(r)
        elif r.width >= 8 and r.height < 8:
            hs.append(r)     # a horizontal rule (also a filled hairline)
        elif r.height >= 8 and r.width < 8:
            vs.append(r)     # a vertical rule
    # Two rules that are adjacent in y, with a vertical rule standing at each end, are
    # one closed face of the page's drawing - the same shape whether it arrived as one
    # rect, as four line paths, or as four filled hairlines. Without this an outline
    # drawn as lines is not a shape at all (a horizontal line is 0 pt tall), so the
    # text inside it looks unanchored and the check cannot see the frame it is about.
    hs.sort(key=lambda r: r.y0)
    for a, b in zip(hs, hs[1:]):
        if b.y0 - a.y0 < 8:
            continue
        x0, x1 = min(a.x0, b.x0), max(a.x1, b.x1)
        if x1 - x0 < 8:
            continue
        if (any(abs(v.x0 - x0) <= 2 and v.y0 <= a.y0 + 2 and v.y1 >= b.y0 - 2 for v in vs)
                and any(abs(v.x1 - x1) <= 2 and v.y0 <= a.y0 + 2 and v.y1 >= b.y0 - 2 for v in vs)):
            out.append(fitz.Rect(x0, a.y0, x1, b.y0))
    try:
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                if r.width >= 8 and r.height >= 8:
                    out.append(r)
    except Exception:
        pass
    return out


def _anchors(page, rs):
    """For each run: where its centre sits inside the smallest shape containing it,
    AND which shape that was.

    Returns None for a run with no shape around it, else (fx, fy, rect) where fx/fy
    are fractions of the shape and rect is the shape itself. The rect is returned
    because the fraction alone is not comparable between two documents: "the smallest
    shape containing the centre" is an answer about a SET of boxes, and two producers
    that draw the same table with different primitives give different sets (a cell
    rect per cell on one side, one assembled face per band on the other), so the
    fraction is then measured against a different object and reads as movement when
    nothing moved. 59 compares the rect before it trusts the fraction.
    """
    shapes = _shapes(page)
    out = []
    for r in rs:
        cx, cy = (r["x"] + r["x1"]) / 2.0, (r["y"] + r["y1"]) / 2.0
        best, best_key = None, None
        for sh in shapes:
            # fitz.Rect is x0/y0/x1/y1, not x/y - the run dicts use x/y, which is
            # what made this crash on its first run.
            if sh.x0 <= cx <= sh.x1 and sh.y0 <= cy <= sh.y1:
                # A tie on AREA is broken by geometry, not by draw order. min() with a
                # strict < kept whichever shape get_drawings() happened to yield first,
                # and two producers need not agree on that order - the same defect
                # 47_margins had when statistics.mode returned the first of a tie.
                # Constructed (break59.py M3b): two boxes of equal area both holding the
                # text centre, drawn in the opposite order on the render side. Nothing
                # moved and 59 failed the page.
                key = (sh.width * sh.height, sh.width, sh.height, sh.y0, sh.x0)
                if best_key is None or key < best_key:
                    best, best_key = sh, key
        if best is None:
            out.append(None)
        else:
            out.append(((cx - best.x0) / max(1e-6, best.width),
                        (cy - best.y0) / max(1e-6, best.height), best))
    return out


def _anchor(page, rs):
    """Fractions only - the shape's identity is dropped. Use _anchors for 59."""
    return [None if a is None else (a[0], a[1]) for a in _anchors(page, rs)]


def _clipped_count(doc):
    """Text clipped at the page edge, measured the same way for either document.

    28 compared the RENDER's clipped count to a hard-coded 0 and never looked at the
    source, so a document that legitimately sets text at the page edge - a border, a
    footer rule, a full-bleed header, a stamp that runs to the trim - failed against
    ITSELF. That is the identical bug 25, 26 and 27 had (see the docstring below about
    seven of 208 documents failing their own copy), and 62a1792 converted those three and
    left this one.

    Measured on 13 Nov: three spans at x < 1 fail this check against a byte-identical
    copy, because the threshold is max(2, len(g_runs)//50) and 3 > 2 on a nine-span page.
    """
    n = 0
    for p in doc:
        W, H = p.rect.width, p.rect.height
        for r in runs(p):
            if r["x"] < 1 or r["x1"] > W - 1:
                n += 1
    return n


def _visual_counts(doc):
    """Invisible text and off-page text, measured the same way for either document.

    25 and 27 used to count these in the render alone and compare to zero, which
    meant a document that genuinely has text matching its background - white on
    white, a watermark, text on a coloured band - failed against ITSELF. Seven of
    the 208 corpus documents did exactly that. The measurement is now taken from
    the source too, so only text that BECAME invisible or left the page counts as
    a defect. Same bug as 26_text_overlap, same fix.
    """
    invisible = off_page = 0
    for p in doc:
        W, H = p.rect.width, p.rect.height
        fills = fill_rects(p)
        rs = runs(p)
        for r in rs:
            for f in fills:
                fr = f["rect"]
                if fr.contains(fitz.Point(r["x"] + 1, r["y"] + 1)):
                    tr = (((r["colour"] >> 16) & 255) / 255.0,
                          ((r["colour"] >> 8) & 255) / 255.0,
                          (r["colour"] & 255) / 255.0)
                    if colour_close(tr, f["fill"], 0.08):
                        invisible += 1
                    break
            if r["x"] < -1 or r["y"] < -1 or r["x1"] > W + 1 or r["y1"] > H + 1:
                off_page += 1
    return invisible, off_page


def _strokes(page):
    """Rules: stroked paths AND thin filled bands, measured the same way.

    This used to skip every drawing whose `color` is None, which is every FILLED path. A rule
    drawn as a 0.8 pt filled rect counted as nothing - and that is exactly how our own engine
    draws a standalone rule: DocxWriter.shape() writes a filled rect with <a:ln><a:noFill/>.
    The check could not see the engine's own legitimate output and reported the rule as lost.

    Proven by construction on 13 Nov with 14 hand-written PDFs differing only in how the same
    seven rules were drawn: seven stroked paths read 7, the same seven as one path with seven
    subpaths read 1, and the same seven as filled 0.8 pt rects read 0 - the SAME answer as a
    render with no rules at all. Loss and drawing style were indistinguishable, and 94 of the
    137 failing rows read render == 0 (RESULTS.jsonl, one row per document, re-counted 13 Nov).

    AND THE RENDER SIDE HAS NO VECTOR PATHS AT ALL (13 Nov, second finding). Google Docs
    exports every anchored shape in the .docx as one raster image: on 207 of the 211 corpus
    documents the render's 08_image_count equals the .docx <w:drawing> count exactly, and
    the median difference is zero. A rule the engine emitted perfectly still reads 0 here,
    because get_drawings() returns vector paths and a picture is not one. So the band test
    below fixes the DOCX side only; _stroke_pictures() fixes the render side.

    The 1.5 pt / 2 pt test is not new: PdfToWord.bandFillStroke() uses exactly it ("a fill-only
    path that is a thin band IS a hairline, which is how most generators draw a rule"), and so
    does compare_strokes.py. Only this file lacked it.
    """
    out = []
    for d in page.get_drawings():
        r = d["rect"]
        col = d.get("color")
        if col is None:
            fill = d.get("fill")
            if fill is None:
                continue
            h, w = r.height, r.width
            if h <= 1.5 and w > 2:
                out.append({"rect": r, "width": round(h, 2), "colour": fill})
            elif w <= 1.5 and h > 2:
                out.append({"rect": r, "width": round(w, 2), "colour": fill})
            continue
        out.append({"rect": r, "width": round(d.get("width") or 0, 2), "colour": col})
    out.extend(_stroke_pictures(page))
    return out


# A rule that arrived as a picture, not a path.
#
# Google Docs renders each anchored shape as one image, so on the render side a rule is a
# thin band of pixels and nothing else. This is the same 1.5 pt / 2 pt band test _strokes()
# applies to fills, plus a pixel test: a blank placeholder - and the engine writes one for
# every light rule whose fill it suppressed - is thin and has no ink, and must not count as
# a rule that survived.
_INK_CACHE = {}


def _picture_has_ink(page, xref, rect):
    """True when the picture actually has dark pixels in it.

    A pixel counts as ink when it is not fully transparent and not white. 0.94 is the same
    "close enough to white to be the page" bound 25_invisible_text uses for colour.
    """
    if not xref:
        return False
    key = (page.number, xref)
    if key in _INK_CACHE:
        return _INK_CACHE[key]
    ok = False
    try:
        pix = fitz.Pixmap(page.parent, xref)
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        samp = pix.samples
        n = pix.n
        step = max(1, (pix.width * pix.height) // 20000)
        seen = ink = 0
        for i in range(0, pix.width * pix.height, step):
            o = i * n
            a = samp[o + 3] if pix.alpha else 255
            seen += 1
            if a <= 16:
                continue
            lum = (samp[o] * 0.299 + samp[o + 1] * 0.587 + samp[o + 2] * 0.114) / 255.0
            if lum < 0.94:
                ink += 1
        ok = seen > 0 and ink >= max(1, int(seen * 0.30))
    except Exception:
        ok = False
    _INK_CACHE[key] = ok
    return ok


def _stroke_pictures(page):
    """Rules the renderer drew as pictures: thin band, and ink in it."""
    out = []
    try:
        infos = page.get_image_info(xrefs=True)
    except Exception:
        return out
    for info in infos:
        r = fitz.Rect(info["bbox"])
        h, w = r.height, r.width
        if h <= 1.5 and w > 2:
            thin = h
        elif w <= 1.5 and h > 2:
            thin = w
        else:
            continue
        if not _picture_has_ink(page, info.get("xref"), r):
            continue
        out.append({"rect": r, "width": round(thin, 2), "colour": None})
    return out


def _span_flags(sp):
    """PyMuPDF: bit0 superscript, bit1 italic, bit4 bold."""
    f = sp.get("flags", 0)
    return {"sup": bool(f & 1), "ital": bool(f & 2), "bold": bool(f & 16)}


# ----------------------------------------------------------------------------
# checks 49-56: the things nothing measured at all
#
# Added after asking what a conversion can get wrong that none of the first 48
# checks would notice. Each of these is a real failure mode that would pass
# silently today.
# ----------------------------------------------------------------------------


EMU_PER_PT = 12700.0


def docx_image_dpi(path):
    """Median dpi of the pictures a .docx embeds, over the size it places them at.

    The engine's own resolution decision, and the only place it is observable. Google's
    PDF export re-rasterises every picture to its own target (48, 72 or 96 dpi at the
    placement size - measured, see 54_image_dpi), so the density in the export says what
    Google chose, not what the engine wrote. The .docx says what the engine wrote:
    word/media holds the bytes, and the wp:extent beside each r:embed is the size the
    picture is drawn at, so px / (extent_pt / 72) is the embedded density.

    Returns None when the file cannot be read as a .docx, so the caller can say the
    measurement did not happen instead of reporting a zero as a result.
    """
    try:
        import zipfile, io
        with zipfile.ZipFile(path) as z:
            doc = z.read("word/document.xml").decode("utf-8", "replace")
            rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
            targets = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
            pat = re.compile(r'<wp:extent[^>]*cx="(\d+)"[^>]*cy="(\d+)"|r:embed="([^"]+)"')
            vals = []
            pending = None
            for m in pat.finditer(doc):
                if m.group(1):
                    pending = (int(m.group(1)) / EMU_PER_PT, int(m.group(2)) / EMU_PER_PT)
                elif m.group(3) and pending:
                    name = "word/" + targets.get(m.group(3), "").replace("../", "")
                    try:
                        w_px = fitz.Pixmap(z.read(name)).width
                    except Exception:
                        pending = None
                        continue
                    w_pt = max(1.0, pending[0])
                    vals.append(w_px / (w_pt / 72.0))
                    pending = None
            vals.sort()
            return round(vals[len(vals) // 2]) if vals else 0
    except Exception:
        return None


def extra_checks2(src, gd, docx_path=None):
    """Return checks 49-56. Independent of the text runs."""
    c = {}

    # ---- 49 page size ------------------------------------------------------
    # The one that can move everything. If Google Docs exports Letter where the
    # PDF was A4, every coordinate on every page is wrong by a few percent and
    # the position checks would blame the engine for a page-size mismatch.
    def sizes(doc):
        return [(round(p.rect.width, 1), round(p.rect.height, 1)) for p in doc]

    s_sz, g_sz = sizes(src), sizes(gd)
    same = sum(1 for a, b in zip(s_sz, g_sz) if abs(a[0] - b[0]) <= 1.5 and abs(a[1] - b[1]) <= 1.5)
    c["49_page_size"] = (len(s_sz), same, s_sz and same == min(len(s_sz), len(g_sz)))

    # ---- 50 annotations ----------------------------------------------------
    # Links are counted elsewhere; sticky notes, highlights and free text are not.
    def annots(doc):
        n = 0
        for p in doc:
            n += sum(1 for a in p.annots() if a.type[1] not in ("Link", "Widget"))
        return n

    s_a, g_a = annots(src), annots(gd)
    c["50_annotations"] = (s_a, g_a, s_a == 0 or g_a >= max(1, int(s_a * 0.9)))

    # ---- 51 form fields ----------------------------------------------------
    def fields(doc):
        n = 0
        for p in doc:
            n += sum(1 for w in p.widgets())
        return n

    s_f, g_f = fields(src), fields(gd)
    c["51_form_fields"] = (s_f, g_f, s_f == 0 or g_f >= max(1, int(s_f * 0.9)))

    # ---- 52 outline / bookmarks -------------------------------------------
    def outline(doc):
        try:
            return len(doc.get_toc())
        except Exception:
            return 0

    s_o, g_o = outline(src), outline(gd)
    c["52_outline"] = (s_o, g_o, s_o == 0 or g_o >= max(1, int(s_o * 0.9)))

    # ---- 53 embedded font names -------------------------------------------
    # 09_font_names counts distinct faces and allows the count to fall by 20 %; it never
    # asks WHICH face went. This asks, for every family the source PDF DRAWS WITH, whether
    # the converted document still puts that text in that family - which is what decides
    # whether the metrics, the glyph coverage and the look survive.
    #
    # MEASURED ON THE .DOCX, NOT ON THE RENDER. Until 13 Nov this compared the source
    # against the PDF the renderer exports, and that is the wrong side of the pipeline. The
    # engine's own decision is written into the .docx: DocxWriter.runXml writes w:rFonts
    # w:ascii for every run that has a face (DocxWriter.java:3108-3112) and w:b/w:i carry
    # the style. Everything else - Google's substitution, LibreOffice's fontconfig, whether
    # the machine has Liberation installed - is somebody else's decision, and a check that
    # reads it cannot be moved by a fix to the engine. Measured on this corpus, 13 Nov: the
    # render-side 53 fired on 1 of 3 documents under an engine change that removed EVERY
    # face (DocxWriter writing one constant family, engine rebuilt, corpus re-converted and
    # re-rendered); this one fires on 3 of 3. Same correction, same reasoning, as 54.
    #
    # WHAT "THE SAME FAMILY" MEANS. Names cannot be compared raw: a PDF names a face two
    # ways ("Liberation Sans Bold", "LiberationSans-Bold"), carries a subset tag
    # ("KLGWYD+Liberation Sans Bold") and a foundry suffix ("ArialMT",
    # "TimesNewRomanPSMT"), and PyMuPDF truncates span["font"] to 24 characters. Style is
    # not family - bold is w:b - and the fourteen standard faces are mapped to the names a
    # reader has, exactly as DocxWriter.BASE14 does. What is NOT forgiven is one family
    # arriving as another: a serif as a sans is a loss and stays a loss.
    SAME_FACE = {
        # ONLY THE RENAMES THE ENGINE ITSELF PERFORMS. DocxWriter.BASE14 maps
        # times->Times New Roman, helvetica->Arial, courier->Courier New, deliberately and
        # correctly - no reader has a face called "Helvetica", and the three are
        # metric-compatible with their PostScript originals by design. Those three are the
        # whole table, because they are the whole of what the engine substitutes.
        #
        # The four buckets this table used to carry (liberationsans->arial,
        # dejavusans->verdana, dejavuserif->timesnewroman, dejavusansmono->couriernew) were
        # added because GOOGLE substitutes, and they are what made a real loss invisible:
        # measured 13 Nov on 350_question_paper, a .docx that names DejaVu Serif where the
        # source drew Times New Roman reads 2 of 2 kept under the buckets and 1 of 2 here.
        # On the .docx side the engine does not substitute, so the buckets can only hide a
        # loss. Dropping them changes NO document's verdict on this corpus: 6 either way.
        "helvetica": "arial", "helveticaps": "arial", "arialps": "arial",
        "times": "timesnewroman", "timesroman": "timesnewroman",
        "timesnew": "timesnewroman", "timesnewromanps": "timesnewroman",
        "courier": "couriernew", "courierps": "couriernew",
        "couriernewps": "couriernew",
        # THE FOUR THE ENGINE ITSELF PERFORMS, and they were missing. DocxWriter.BASE14 maps
        # Liberation Sans / Serif / Mono onto Arial / Times New Roman / Courier New
        # (DocxWriter.java:4796-4801, 5a09931 on 13 Nov 15:47) because Google Docs has no
        # Liberation and substitutes a serif with a sans. This table refused that rename, so
        # 53 read every Liberation document as a lost family: MEASURED on the 211-document
        # corpus against the .docx HEAD's engine writes, 129 documents fail 53 without these
        # four lines and 6 with them - and the 6 are exactly the six this check's own comment
        # names (364_event_ticket, 600_reviewed_invoice_with_annotations,
        # 601_fillable_admission_form, payslip-label-left-amount-right,
        # price-list-right-aligned-amounts, salary-slip-corporate).
        #
        # This is the narrow version of the bucket this table used to carry. The old
        # liberation->arial bucket was removed on 13 Nov because it hid a real loss on
        # 350_question_paper: a .docx naming DejaVu Serif where the source drew Times New
        # Roman. That case is not this one - DejaVu is not what the engine substitutes, and
        # nothing here maps DejaVu.
        "liberationsans": "arial", "liberationserif": "timesnewroman",
        "liberationmono": "couriernew",
    }

    def family(name):
        # The comma form ("Arial,Bold") is a real PDF naming style and DocxWriter's own suffix
        # list already carries ",Bold"/",Italic"/",BoldItalic". Turned into a space here so the
        # space-form strip below catches it - doing it at the end left "arialbold", a name no
        # family has.
        n = (name or "").split("+")[-1].strip().lower().replace(",", " ")
        # THE TWO STRIPS HAVE TO ITERATE. "MT"/"PSMT"/"PS" and the style word can
        # arrive in EITHER order, and all three of these are legal and appear in real
        # exports:
        #     Arial-BoldMT              family, style, PS      (what Word writes)
        #     TimesNewRomanPS-BoldMT    family, PS, style, PS   (Google's bold export)
        #     ArialMT-Bold              family, PS, style      (the other legal order)
        # One PS pass then one style pass resolves the first two and leaves the third
        # as "arialmt": the PS suffix is still attached when the style strip runs, and
        # the style is still attached when the PS strip runs. Measured on the published
        # corpus on 13 Nov against a copy of each source PDF whose faces were renamed
        # to Google's export spelling and nothing else changed (word boxes identical to
        # 0.000 pt): under the "ArialMT-Bold" order 153 of 199 documents lost at least
        # one face that was still on the page, and 1 read kept=0. Under the
        # "Arial-BoldMT" order 13 of 205 lost one, all of them the DejaVu Sans Mono
        # entry now added above. Iterating to a fixed point resolves every order and
        # cannot over-strip: each pass removes at most one suffix and stops when none
        # applies.
        #
        # "-roman" and "-normal" are in DocxWriter's own suffix list
        # (DocxWriter.java:4656-4659) and were missing here, so "Times-Roman" - the
        # PostScript name of a base-14 face - came out as "times-roman" and matched
        # nothing.
        _PS = ("psmt", "mt", "ps")
        _STYLE = ("-bolditalic", "-boldoblique", "-bold", "-italic", "-oblique",
                  "-regular", "-roman", "-normal",
                  " bold italic", " bold oblique", " italic", " oblique", " bold",
                  " regular", " normal", " book")
        # A TRUNCATED STYLE TOKEN. Some producers cap a /BaseFont name at 23 characters
        # and cut the style word in half; "NotoSansDevanagari-Regul",
        # "Liberation Serif Bold It" and "LiberationSerif-BoldItal" are all in the
        # published corpus. A trailing token that is a PROPER PREFIX of a style word and
        # at least two characters long is that truncation, not a family name, so it comes
        # off too. Two characters is the floor because "It" and "Bo" are already
        # unambiguous while a single letter could belong to a real family name.
        _STYLE_WORD = ("bolditalic", "boldoblique", "italic", "oblique", "regular",
                       "roman", "normal", "bold", "book")

        def _strip_once(n):
            for suf in _PS:
                if n.endswith(suf) and len(n) > len(suf):
                    return n[:-len(suf)]
            for suf in _STYLE:
                if n.endswith(suf):
                    return n[:-len(suf)]
            for sep in ("-", " "):
                head, _, tail = n.rpartition(sep)
                if head and len(tail) >= 2:
                    for w in _STYLE_WORD:
                        if len(w) > len(tail) and w.startswith(tail):
                            return head
            return n

        # Both sides go through this, so a name that cannot be reduced is still
        # compared as itself - the check never invents an equivalence.
        while True:
            shorter = _strip_once(n)
            if shorter == n:
                break
            n = shorter
        # The keys above are written space-free ("liberationsans"), because the hyphen form
        # "LiberationSans-Bold" collapses to that once the style suffix is gone. The space
        # form collapses to "liberation sans" instead and misses the table entirely, so the
        # internal space has to go too. Families carry no meaningful space for this
        # comparison and both sides are normalised identically, so this stays symmetric.
        # The comma form ("Arial,Bold") is a real PDF naming style and DocxWriter's own
        # suffix list already carries ",Bold"/",Italic"/",BoldItalic". This side did not.
        n = n.replace(",", "").replace(" ", "")
        return SAME_FACE.get(n, n)

    def faces(doc):
        """The families this PDF actually DRAWS with, and how many characters each carries.

        p.get_fonts() returns the page's /Resources /Font dictionary: every face the page
        COULD use, including one no glyph ever touches, including faces inherited from a
        shared Resources on the Pages node (so every page reports every font in the
        document), and including fonts reached only through a Form XObject. Measured on two
        real corpus PDFs on 13 Nov, both carry a bare "Helvetica" in their resources and draw
        it in zero spans.

        That made the two sides of this check different measurements: the source side was
        "families declared somewhere on a page", the other was "families actually used". A
        document could fail on a face nothing was drawn in, and no engine change could ever
        fix it because there was nothing to fix.

        Characters, not a set, because "present" is not the question. A family carried by one
        stray run out of three hundred is a family that did not survive; the weight is what
        tells those apart. See SHARE_FLOOR below for the measured cut.
        """
        out = collections.Counter()
        for p in doc:
            drawn = False
            try:
                blocks = p.get_text("dict").get("blocks", [])
            except Exception:
                blocks = []
            for b in blocks:
                for line in b.get("lines", []):
                    for span in line.get("spans", []):
                        t = span.get("text", "")
                        if not t.strip():
                            continue
                        fam = family(span.get("font"))
                        if fam:
                            out[fam] += len(t)
                            drawn = True
            if not drawn:
                # An image-only page has resources and no spans. Fall back to the dictionary
                # so such a page is not silently read as "no fonts, therefore fine". Weight 0:
                # a family that is only declared has to be carried, but it must not inflate a
                # share it never had.
                for f in p.get_fonts():
                    fam = family(f[3])
                    if fam:
                        out[fam] += 0
        return out

    def docx_faces(path):
        """family -> characters carried by the runs of the engine's .docx that DECLARE it.

        The .docx is a zip: word/document.xml holds the runs, word/styles.xml the styles and
        the document defaults. A run's face resolves in the order a reader resolves it - its
        own w:rPr/w:rFonts, then its paragraph style (following w:basedOn), then
        w:docDefaults. DocxWriter writes w:rFonts on every run that has a face
        (DocxWriter.java:3108) and Calibri in docDefaults (DocxWriter.java:4853), so a run
        that resolves to the default is a run the engine could not name - counted, and
        counted as a loss, because Calibri is not the face the source drew.

        Text in tables and in text boxes is included: they are runs like any other, and
        "table cells carry their typeface" is a defect this corpus already had.
        """
        NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

        def qn(tag):
            return NS + tag

        z = zipfile.ZipFile(path)
        styles = ET.fromstring(z.read("word/styles.xml"))
        default = None
        for rf in styles.iter(qn("rFonts")):
            if rf.get(qn("ascii")):
                default = rf.get(qn("ascii"))
                break
        style_face, based = {}, {}
        for st in styles.findall(qn("style")):
            sid = st.get(qn("styleId"))
            rf = st.find(".//" + qn("rPr") + "/" + qn("rFonts"))
            if rf is not None and rf.get(qn("ascii")):
                style_face[sid] = rf.get(qn("ascii"))
            bo = st.find(qn("basedOn"))
            if bo is not None:
                based[sid] = bo.get(qn("val"))

        def from_style(sid, depth=0):
            if sid in style_face:
                return style_face[sid]
            if sid in based and depth < 5:
                return from_style(based[sid], depth + 1)
            return None

        body = ET.fromstring(z.read("word/document.xml"))
        out = collections.Counter()
        for p in body.iter(qn("p")):
            psid = None
            ppr = p.find(qn("pPr"))
            if ppr is not None and ppr.find(qn("pStyle")) is not None:
                psid = ppr.find(qn("pStyle")).get(qn("val"))
            for r in p.findall(qn("r")):
                text = "".join(t.text or "" for t in r.findall(qn("t")))
                if not text.strip():
                    continue
                face = None
                rpr = r.find(qn("rPr"))
                if rpr is not None and rpr.find(qn("rFonts")) is not None:
                    face = rpr.find(qn("rFonts")).get(qn("ascii"))
                if not face:
                    face = from_style(psid) if psid else None
                out[family(face or default or "Calibri")] += len(text)
        return out

    # HOW MUCH OF A FAMILY HAS TO SURVIVE. Measured over the 211 documents on 13 Nov, per
    # (document, family) pair, as the ratio of the family's share of characters in the .docx
    # to its share of characters in the PDF - share, not count, so that text the engine drops
    # outright (03/04's question, not this one) does not fire this check as well.
    #   372 pairs in all. 365 sit at 0.86 or above; the median is 1.000.
    #   6 sit at 0.06 or below, and 4 of those are 0.000 - the family is not named at all:
    #     dejavusansmono on 364_event_ticket (the ticket code arrives proportional),
    #     timesnewroman on 600_reviewed_invoice_with_annotations ("APPROVED" is dropped
    #       with the face, so 03/04 fire there too - that one is a shared signal),
    #     zapfdingbats on 601_fillable_admission_form (a checkbox glyph),
    #     dejavusans on price-list-right-aligned-amounts (38 rupee signs);
    #     the two partial ones, 0.040 and 0.059, are the rupee sign on
    #     payslip-label-left-amount-right and salary-slip-corporate - the character is still
    #     in the .docx, in Liberation Sans, so no text check fires and this is the only
    #     check that sees it.
    #   1 sits at exactly 0.500 (4 characters of dejavusans in newsletter-3col-header-footer).
    # The band between 0.06 and 0.50 is EMPTY - not one pair in 372 lands in it. Any floor
    # from 0.07 to 0.49 fails the same 6 documents (measured at 0.07, 0.10, 0.15, 0.20,
    # 0.25, 0.30, 0.40 and 0.49; every one gives 6). 0.25 is chosen because it is inside
    # that band and at least 4.2x from either edge - 4.2x above the highest observed loss,
    # 2x below the lowest observed survivor - so it is not a knife edge on a data point, and
    # a new document has to be wrong by more than a factor of four to move it.
    SHARE_FLOOR = 0.25

    s_fa = faces(src)
    d_fa = docx_faces(docx_path) if docx_path else None
    if d_fa is None:
        # No .docx to read. The render answers a different question - it is the exporter's
        # substitution, not the engine's decision - so it cannot fail this check. Say so on
        # stderr rather than passing silently, because a run that forgets --docx measures
        # nothing here and should be visible as such. Same rule as 54.
        print("53_embedded_faces: no .docx given, faces unmeasured (the render carries %d of "
              "%d source families, which is the renderer's choice, not the engine's)"
              % (len(set(s_fa) & set(faces(gd))), len(s_fa)), file=sys.stderr)
        c["53_embedded_faces"] = (len(s_fa), 0, True)
    else:
        s_tot = sum(s_fa.values()) or 1
        d_tot = sum(d_fa.values()) or 1
        lost = []
        for fam, chars in s_fa.items():
            want = chars / s_tot
            got = d_fa.get(fam, 0) / d_tot
            # A family the source only DECLARES (weight 0) has no share to lose; it only has
            # to be present - and `faces` keeps such a family only when the page drew nothing
            # at all, where the dictionary is the only evidence there is.
            ratio = (got / want) if want else (1.0 if got else 0.0)
            if ratio < SHARE_FLOOR:
                lost.append((fam, round(ratio, 3), chars))
        kept = len(s_fa) - len(lost)
        if lost:
            print("53_embedded_faces: %s" % ", ".join(
                "%s kept %.0f%% of %d chars" % (f, r * 100, ch) for f, r, ch in lost),
                file=sys.stderr)
        c["53_embedded_faces"] = (len(s_fa), kept, len(s_fa) == 0 or not lost)

    # ---- 54 image resolution ----------------------------------------------
    # 08 counts images and 48 measures area; neither notices a 300 dpi logo
    # arriving as a 40 dpi smear.
    #
    # MEASURED ON THE .DOCX, NOT ON GOOGLE'S EXPORT. This check used to compare the
    # original's pixel density against the density in the PDF Google exports, and that
    # number is Google's, not the engine's. Over the 216 measured documents the recorded
    # render density takes only three values - 96 on 154 of them, 72 on 31, 48 on 3 - while
    # the source densities run 152..665; 753 px in the source implies 210 px in the render,
    # and 480 px implies 35. The engine embeds the native grid (PdfToWord.collectImage
    # lifts pdImage.getImage() at full size and DocxWriter writes those bytes beside a
    # wp:extent taken from the page placement), so nothing the engine writes survives the
    # export: the render density is the exporter's tier x the placement width, and the
    # check therefore asks "is the source below Google's ceiling". Passing it is a step
    # function of the SOURCE density alone - every document above 160 dpi fails, every one
    # at or below 152 passes except 393_spectrum_peak_table (152 against a 72 tier) - and
    # 12 documents fail permanently with no .docx change able to clear them, because
    # embedding more pixels cannot lift the export above its tier.
    # What the engine does control is what it puts in the .docx: word/media holds the bytes
    # and wp:extent the size, so px / (extent_pt / 72) is the engine's own resolution
    # decision. That is what this check now reads, from --docx.
    def img_dpi(doc):
        vals = []
        for p in doc:
            for im in p.get_image_info():
                w_px = im.get("width") or 0
                b = im["bbox"]
                w_pt = max(1.0, b[2] - b[0])
                if w_px and w_pt:
                    vals.append(w_px / (w_pt / 72.0))
        vals.sort()
        return round(vals[len(vals) // 2]) if vals else 0

    s_d, g_d = img_dpi(src), img_dpi(gd)
    d_d = docx_image_dpi(docx_path) if docx_path else None
    if d_d is None:
        # No .docx to read. Google's number answers a different question, so it cannot
        # fail this check - but say so on stderr rather than passing silently, because a
        # run that forgets --docx measures nothing here and should be visible as such.
        if s_d:
            print("54_image_dpi: no .docx given, resolution unmeasured (render reads %s dpi, "
                  "which is Google's export, not the engine's)" % g_d, file=sys.stderr)
        c["54_image_dpi"] = (s_d, 0, True)
    else:
        c["54_image_dpi"] = (s_d, d_d, s_d == 0 or d_d >= s_d * 0.6)

    # ---- 55 page count per size -------------------------------------------
    # A mixed-orientation document that comes out all one size is wrong even if
    # the page COUNT matches.
    def orientation_mix(doc):
        land = sum(1 for p in doc if p.rect.width > p.rect.height)
        return (land, len(doc) - land)

    s_om, g_om = orientation_mix(src), orientation_mix(gd)
    c["55_orientation_mix"] = (s_om, g_om, s_om == g_om)

    # ---- 56 text direction: DROPPED 13 Nov ---------------------------------
    # The check read `line.dir` and counted lines with dir[0] < 0, on the stated
    # premise that an RTL line reports a negative direction. It does not, and it
    # cannot: `dir` is the unit vector of the BASELINE, i.e. rotation. Measured
    # over the whole 211-document corpus on 13 Nov:
    #   - dir[0] < 0 occurs on 115 lines in 10 documents, and every one of them
    #     is a page rotated 180 degrees (04_stamp_180deg_upside_down,
    #     one-page-rotated-180-degrees 61 lines, 417_rotate180_and_mirrored,
    #     ...). That is 35_rotation's subject, not direction.
    #   - the corpus's only Arabic document, 77_arabic_rtl_document, reports
    #     dir = (1.0, 0.0) on every one of its 25 lines. The check read 0 there,
    #     so it passed on the one document it exists for.
    # Direction is not recoverable from the text API at all, so there is nothing
    # to fix. The three candidates were tested and each is blind:
    #   - `dir`: above. `wmode` is 0 for horizontal text and does not distinguish
    #     left-to-right from right-to-left.
    #   - character origins: a right-to-left run should have descending x. On
    #     77_arabic 25 runs descend and every other corpus document has no RTL
    #     character at all - but the signal is produced by MuPDF's bidi
    #     reordering, not by the page. Rewriting that document's content stream
    #     with every glyph run reversed (a direction-lost render, visually
    #     mirrored Arabic) still measures 25/25, because extraction is always
    #     reordered into logical order. The signal reads the same on a correct
    #     document and on a mirrored one, so it is not a direction test.
    #   - the content stream's own operator order is the only place the draw
    #     order survives, and a producer may draw glyphs in any order without
    #     changing direction, so it cannot be compared between two producers.
    # And the defect the check was written for is not lost with it: a mirrored
    # RTL render changes the extracted WORD ORDER, which 03/04/05/22 already
    # compare. Measured on the mirrored copy of 77_arabic: 03_word_count 105 ->
    # 103, 04_words_missing 91, 05_words_extra 89, 22_reading_order 100 -> 0.
    # (45_char_accuracy does not fire there and should not: the character
    # multiset is identical, only the order changed.)
    # Precedent: 02_text_run_count was dropped the same way and for the same
    # reason - a check whose only signal is another check's subject is a
    # liability, and the corpus numbers are cleaner without it.

    # ---- 59 shape anchor ---------------------------------------------------
    # Does text stay in the same place inside the outline that encloses it?
    #
    # REDEFINED 13 Nov - the old form was 123 documents, uninvestigated, and it is not
    # one defect. As it stood it compared each run's centre AS A FRACTION OF ITS
    # SMALLEST ENCLOSING SHAPE against ANCHOR_TOL = 0.12 and failed the document if a
    # single run was out. Both halves of that are wrong on this corpus, and measured:
    #
    #  1. The fraction's unit is the shape's own size, so the tolerance in points is
    #     0.12 x the box, and it is a different number on every run. Constructed
    #     (/scratch/work/probe): a 40 pt box passes at 4 pt and fails at 5; a 12 pt box
    #     passes at 1 pt and fails at 2. A table row is 12-20 pt, so the check fires at
    #     1.4-2.4 pt - under 18_displacement's own FLOOR (1.5 pt), a third of its cap
    #     (4.5 pt), and with no allowance of any kind.
    #  2. "Smallest shape containing the centre" is not the same OBJECT on the two
    #     sides. A table the page drew as one rect per cell comes back as a grid of
    #     rules, and _shapes assembles the widest pair of horizontal rules into ONE face
    #     per band - so a cell's run is re-based from an 80 pt box onto a 320 pt one.
    #     Constructed, 16 cells over 4 columns: 12 of 16 runs fail with every character
    #     on both sides at the same coordinates and no line anywhere out of place.
    #
    # What is left when those two are removed is the defect the check was written for,
    # so it is now judged only where it can be judged, in points:
    #   lost      the text is in the render and NO shape encloses it - the outline went
    #             (the rotated-CTM drop, PdfToWord.java:4231, is the known source)
    #   unjudged  the render's enclosing box is a different object; the fraction would
    #             be measured against the wrong rectangle, so it is not compared
    #   moved     the SAME box on both sides, and the text sits > ANCHOR_TOL_PT off it
    # A page fails on the same budget 18_displacement uses, not on one stray run.
    ANCHOR_TOL_PT = 3.0        # points, not a fraction of whatever box encloses the run
    ANCHOR_RECT_TOL = 2.0      # pt; the two boxes are the same object within this
    ANCHOR_BUDGET = 5          # per cent of the page's judged runs, as 18 uses
    lost, moved, unjudged, anchored = 0, 0, 0, 0
    anchor_bad_pages = []

    def _match(r, gruns, by, used):
        """The unused render runs whose text is r's - whole, or as adjacent pieces.

        The render is free to reorder spans (draw order is not reading order) and 02
        already declares that GAINING runs is legal, so pairing source run i with
        render run i compares two unrelated runs whenever either happens. Match on the
        text instead; index order then cannot decide the answer. A split - "Beta" into
        "Be" + "ta" - leaves no exact match, so fall back to joining unused runs on the
        same baseline while the join stays a prefix of the source text.
        """
        want = norm_word(r["text"])
        free = [j for j in by.get(want, []) if j not in used]
        if free:
            return [min(free, key=lambda j: abs(gruns[j]["y"] - r["y"]) +
                                            abs(gruns[j]["x"] - r["x"]))]
        near = [j for j in range(len(gruns))
                if j not in used and abs(gruns[j]["y"] - r["y"]) <= 1.0
                and gruns[j]["x"] >= r["x"] - 1.0]
        near.sort(key=lambda j: gruns[j]["x"])
        for k0 in range(min(3, len(near))):
            joined, span = "", [near[k0]]
            joined = norm_word(gruns[near[k0]]["text"])
            k = k0
            while want.startswith(joined) and k + 1 < len(near):
                k += 1
                span.append(near[k])
                joined += norm_word(gruns[near[k]]["text"])
                if joined == want:
                    return span
        return []

    def _same_box(a, b):
        return (abs(a.x0 - b.x0) <= ANCHOR_RECT_TOL and abs(a.y0 - b.y0) <= ANCHOR_RECT_TOL
                and abs(a.x1 - b.x1) <= ANCHOR_RECT_TOL and abs(a.y1 - b.y1) <= ANCHOR_RECT_TOL)

    def _class_count(a, shapes):
        """How many shapes in `shapes` have a's size within ANCHOR_RECT_TOL."""
        return sum(1 for s in shapes
                   if abs(s.width - a.width) <= ANCHOR_RECT_TOL
                   and abs(s.height - a.height) <= ANCHOR_RECT_TOL)

    def _box_moved(a, gshapes, sshapes):
        """The source box, reproduced at its own SIZE somewhere else on the page.

        This is the difference the check turns on, and it cannot be read off the run's
        own enclosing shape: a box that slid 55 pt off its text and a table cell that
        came back as a band BOTH leave the run enclosed by a rectangle that is not the
        source's. What separates them is whether the source's rectangle still exists as
        a shape of the same size. If it does, the outline moved and the text did not -
        the defect. If it does not, the page was drawn with different primitives and
        this run is not evidence either way.

        SIZE ALONE IS NOT ENOUGH, and that was the residual risk the author of this
        check named. One shape of a given size anywhere on the page satisfied the test,
        and a uniform table is nothing but shapes of one size: a 3x3 table drawn as nine
        80x24 cell rects has NINE boxes of the size every cell is measured against, so a
        render that draws that table as a rule grid finds one 80x24 box elsewhere on the
        page and calls every cell moved. Constructed (break59.py M1): nine cells, text at
        identical coordinates on both sides, one unrelated 80x24 signature box on the
        page - 59 failed the document. Remove that one box and the same page reads 0/0
        (M1b). What distinguishes the two is not whether the size occurs but whether the
        page still has AS MANY of them: a moved box leaves its size class the size it
        was, a re-primitivised table destroys it.
        """
        if _class_count(a, gshapes) == 0:
            return False
        return _class_count(a, gshapes) >= _class_count(a, sshapes)

    for si in range(min(src.page_count, gd.page_count)):
        sp, gp = src[si], gd[si]
        sruns, gruns = runs(sp), runs(gp)
        sa, ga = _anchors(sp, sruns), _anchors(gp, gruns)
        gshapes = _shapes(gp)
        sshapes = _shapes(sp)                   # for the size-class population test
        by = collections.defaultdict(list)      # text -> render run indices
        for j, g in enumerate(gruns):
            by[norm_word(g["text"])].append(j)
        used = set()
        n_judged = n_out = hard_out = 0
        for i, a in enumerate(sa):
            if a is None:
                continue          # nothing enclosed it in the source either
            sb = a[2]
            sx = (sruns[i]["x"] + sruns[i]["x1"]) / 2.0
            sy = (sruns[i]["y"] + sruns[i]["y1"]) / 2.0
            js = _match(sruns[i], gruns, by, used)
            if not js:
                lost += 1         # its text is not in the render at all
                n_judged += 1
                n_out += 1
                continue
            used.update(js)
            bs = [ga[j] for j in js if ga[j] is not None]
            gx = sum(gruns[j]["x"] + gruns[j]["x1"] for j in js) / (2.0 * len(js))
            gy = sum(gruns[j]["y"] + gruns[j]["y1"] for j in js) / (2.0 * len(js))
            if not bs:
                # NO BOX ENCLOSES THE TEXT. That is two different events and this check
                # scored both as `lost`: the outline went, or the outline is still on the
                # page at its own size and the text is outside it. The second is exactly
                # the defect the check was written for, and scoring it `lost` was the
                # only reason it ever reached the page - under the page budget, and two
                # of them at a time are free (break59.py M6a: 2 of 40 boxes slid 30 pt
                # clear of their text and the page passed with `lost`=2, budget 2).
                # A run that has left its own surviving box outright cannot be a
                # re-primitivisation artifact, so it is also beyond the budget.
                if _box_moved(sb, gshapes, sshapes):
                    moved += 1
                    n_judged += 1
                    n_out += 1
                    hard_out += 1
                else:
                    lost += 1
                    n_judged += 1
                    n_out += 1
                continue
            gb = bs[0][2]
            dx = (gx - gb.x0) - (sx - sb.x0)
            dy = (gy - gb.y0) - (sy - sb.y0)
            if _same_box(sb, gb) or (abs(dx) <= ANCHOR_TOL_PT and abs(dy) <= ANCHOR_TOL_PT):
                # SAME BOX, or a different box with the text in the same place inside
                # it. The second case is not a hole: the box's identity was only ever a
                # proxy for "is this the same object", and the relation this check
                # exists to measure is the text's place INSIDE its outline. A proxy that
                # is asked directly gives the right answer three ways where the old code
                # gave a wrong one or none:
                #  - a box that moved WITH its text (a reflowed table) was called moved
                #    although the relation is untouched (break59.py M7, 9 of 9 runs).
                #    18_displacement owns that displacement; 60 already had this exact
                #    fix applied today for the same reason (A6).
                #  - a box that grew 2-3 pt fell outside ANCHOR_RECT_TOL and the run was
                #    silently unjudged - a hole exactly as wide as the gap between the
                #    box tolerance (2.0) and the displacement tolerance (3.0), so the
                #    anchor was held to a stricter standard than the thing it anchors
                #    (M2a: 3 pt growth, text unmoved, 59 reads 0/0 and nothing else
                #    fires; M2a2: the same at 1.5 pt is judged).
                #  - a table drawn one rect per cell on the source and as a rule grid on
                #    the render kept the relation and lost the box, and fired only because
                #    some unrelated box on the page happened to have the cell's size (M1:
                #    9 cells, text at identical coordinates, page failed; M1b: the same
                #    page without that one box reads 0/0 and passes).
                n_judged += 1
                if abs(dx) > ANCHOR_TOL_PT or abs(dy) > ANCHOR_TOL_PT:
                    moved += 1    # same place in the box? no - and the box is the same
                    n_out += 1
                else:
                    anchored += 1
                continue
            if _box_moved(sb, gshapes, sshapes):
                moved += 1        # the outline is on the page, somewhere else
                n_judged += 1
                n_out += 1
            else:
                # A different rectangle encloses it, the text sits somewhere else inside
                # it, and the source's rectangle is nowhere on the page - a cell rect
                # that came back as a band, a band that came back as the page. The
                # fraction is not comparable, and this run is not evidence either way.
                unjudged += 1
            continue
        if n_judged and (n_out > max(2, -(-n_judged * ANCHOR_BUDGET // 100))
                         or n_out == n_judged or hard_out):
            anchor_bad_pages.append(si)
    # source = the runs this could decide, render = how many of those still sit in the
    # same place inside the SAME box. A raw drift count would read as "source=1
    # render=1" for one good run and one bad run alike.
    # unjudged is IN the source count. A page whose boxes were all re-primitivised
    # judged nothing, and (0, 0, True) is indistinguishable from a page with no boxes
    # at all - the silence of M1b read as a pass and as a clean 0/0. Now it reads 0 of 9.
    c["59_shape_anchor"] = (anchored + lost + moved + unjudged, anchored, not anchor_bad_pages)
    if unjudged:
        # Never silent: on a document whose boxes are drawn with different primitives on
        # the two sides this check decides very little, and that must be visible as the
        # number it is rather than as a pass.
        print("59_shape_anchor: %d anchored run(s) unjudged - the render's enclosing box "
              "is a different rectangle from the source's" % unjudged, file=sys.stderr)

    # ---- 60 text column right edge -----------------------------------------
    # NOTHING MEASURED THIS BEFORE. 43_within_10pt_x compares a span's x - its LEFT edge -
    # so a line that starts in the right place and runs 30 pt past the column is invisible
    # to it. 27_text_off_page fires only beyond the PAPER. And the engine's own residual
    # lives exactly in the gap between the two: the .docx carries w:pgMar right="0"
    # (DocxWriter.java:1610) and w:ind ... right="0" (DocxWriter.java:2607), so a
    # left-aligned paragraph has no right constraint at all and its text area is the whole
    # 595 pt paper while the source's column ended at 539. 57 documents in the corpus
    # overrun the right edge and 52 of them still pass 45_char_accuracy - the text is not
    # garbled, it is unwrapped.
    #
    # The old 47 did see maxx, but on page 1 only, and on 136 of 211 documents a masthead or
    # a full-width rule pins it, which is why a right column 30 pt too narrow passed.
    #
    # Measured per page over the BODY lines: the ink lines that start at the page's modal
    # left edge, outside the header/footer bands. For left-aligned, centred and right-aligned
    # body text alike the longest of those lines ends at the column's right edge, so the max
    # of their right edges is the column edge. Two ways to fail:
    #   overrun   the render's column edge is more than RIGHT_OVERRUN past the source's -
    #             text is running into the margin the source kept;
    #   underrun  the render's column edge is more than RIGHT_UNDERRUN short of it - the
    #             column is narrower than the source's. Only judged on a page with at least
    #             FULL_PAGE_LINES body lines, because on a short page max(right) is
    #             raggedness, not a column edge, and a two-line page cannot tell them apart.
    # FOUR FIXES TO THE FIRST VERSION OF THIS CHECK, each measured on the corpus.
    #
    # (a) IT JUDGED ONE COLUMN AND CALLED IT THE PAGE. The modal left edge is a minority
    #     on most pages: 157 of 545 pages hold less than half their ink in it, and 111
    #     have two left-edge clusters of >=15 %. Everything outside it was unmeasured.
    #     Constructed: 39 of 51 lines on 56_table_indented_from_margin and 23 of 26 on
    #     331_pid_diagram widened 25-30 % with every left edge untouched - both checks
    #     said pass. Every column is now measured, not just the modal one.
    # (b) THE 10-BODY-LINE FLOOR COUNTED THE WRONG THING. The comment says "body lines";
    #     the code compared len(col), the lines in the MODAL CLUSTER, which is one column
    #     of a two-column page. 344 of 545 pages (63 %) are below it and 27 of those have
    #     >=10 body lines on the page. The floor also produced a discontinuity: the same
    #     38 %-narrow column fires on 401_trifold_brochure (cluster 10) and passes on
    #     343_air_waybill (cluster 9). The floor is replaced by a RESOLUTION test on the
    #     source's own edge, which is what the floor was trying to express: if the two
    #     longest source lines agree on the edge within RIGHT_UNDERRUN, the edge is known
    #     to within the tolerance and the comparison means something.
    # (c) max(right) IS A ONE-LINE STATISTIC AND ITS NOISE IS THE TOLERANCE. The gap
    #     between the longest and second-longest body line is >6 pt on 150 of 542 judged
    #     pages (28 %) and >8 pt on 144 (27 %): one line breaking differently - which is
    #     all a different engine's line breaking is - moves the judged edge past the
    #     tolerance. Measured: redrawing 11 lines where they already were, in a
    #     substituted face, fired over=1. The edge is now the 90th percentile of the
    #     column's right edges and a single line can no longer decide the verdict.
    # (d) THE BANDS WERE A FRACTION OF THE PAGE AND NOTHING ELSE. 159 of 545 pages have
    #     body-column lines inside them; on 18 pages the widest body line is one of them,
    #     by up to 206 pt, and on 320_balance_sheet_statutory moving the page 8 pt
    #     vertically - a dy defect, not an x one - flips this check. A line in a band is
    #     now kept when its left edge belongs to a column that continues outside the band.
    BAND = 0.06             # header / footer band, as a fraction of page height
    RIGHT_OVERRUN = 6.0
    RIGHT_UNDERRUN = 8.0
    COL_MIN_LINES = 3       # a left-edge cluster is a column if it holds this many lines
    COL_MIN_SHARE = 0.05    # ... or this share of the page's body lines, if larger
    EDGE_PCT = 0.9          # the column edge is this percentile of its right edges
    EDGE_MIN_LINES = 5      # below this many lines the percentile is the max anyway
    SLACK_CAP = 24.0        # the tolerance never grows past this, however ragged the page

    def page_lines(page):
        ls = []
        for blk in page.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                if not "".join(sp.get("text", "") for sp in ln.get("spans", [])).strip():
                    continue
                ls.append(ln["bbox"])
        return ls

    def columns(page):
        """[(left edge, [line bboxes]), ...] - every column on the page.

        The bands are dropped ALWAYS, not only when enough mid-page lines survive. A
        fallback to "every line" re-admitted the masthead this check exists to ignore:
        measured on 15_stamp_on_scanned_page, a page whose text layer is two lines and a
        masthead, the fallback took the masthead's right edge as the column's and fired.
        A band line is kept when it starts at the left edge of a column that continues
        outside the band - that is a body line the fraction cut off, not a masthead.
        """
        ls = page_lines(page)
        if not ls:
            return []
        H = page.rect.height
        inside = [b for b in ls if b[1] >= BAND * H and b[3] <= H - BAND * H]
        band = [b for b in ls if not (b[1] >= BAND * H and b[3] <= H - BAND * H)]
        if not inside:
            return []
        need = max(COL_MIN_LINES, int(COL_MIN_SHARE * len(inside)))
        groups = []
        for b in sorted(inside, key=lambda b: b[0]):
            if groups and b[0] - groups[-1][0][0] <= 10:
                groups[-1].append(b)
            else:
                groups.append([b])
        out = []
        for g in groups:
            if len(g) < need:
                continue
            a = g[0][0]
            out.append((a, g + [b for b in band if abs(b[0] - a) <= 10]))
        return out

    def edge(col):
        """(the column's right edge, how precisely that page can state it).

        max() was a one-line statistic: its sensitivity to a single line breaking
        differently is the gap between the longest and second-longest line, which is
        larger than the 6 pt tolerance on 28 % of the corpus's pages. A percentile over
        the same lines is the same number on both sides of the comparison, so the
        systematic shortfall of a ragged column cancels.

        The second number is that percentile's OWN resolution - the distance between the
        order statistics on either side of it, capped. A re-break can move the k-th value
        by at most that much, so it is the largest movement that is not evidence of a
        defect, and the tolerance has to include it. This replaces the 10-line floor: the
        floor was an attempt to ask "is this page's edge measurable", and this answers it
        per column instead of per page, on every column, including the short ones.
        """
        v = sorted(b[2] for b in col)
        if len(v) < EDGE_MIN_LINES:
            return v[-1], min(SLACK_CAP, v[-1] - v[0]) if len(v) > 1 else 0.0
        k = min(len(v) - 1, int(round(EDGE_PCT * (len(v) - 1))))
        lo, hi = max(0, k - 1), min(len(v) - 1, k + 1)
        return v[k], min(SLACK_CAP, v[hi] - v[lo])

    over = under = 0
    for i in range(min(src.page_count, gd.page_count)):
        sc, gc = columns(src[i]), columns(gd[i])
        if not sc or not gc:
            continue
        for a, s_col in sc:
            hit = [(abs(a - b2), c2) for b2, c2 in gc if abs(a - b2) <= 10]
            if not hit:
                continue                      # the column is gone: 04/05 own that
            g_col = min(hit, key=lambda t: t[0])[1]
            (rs, slack), rg = edge(s_col), edge(g_col)[0]
            # The percentile is the single-line defence and it is implicit, so it is worth
            # stating: on a 19-line column the p90 is the 3rd-longest line, so one line
            # breaking differently does not move it. A max would be moved by exactly the
            # longest/second-longest gap, which is 6 pt or more on 28 % of pages.
            if rg > rs + RIGHT_OVERRUN + slack:
                over += 1
                break
            if rg < rs - RIGHT_UNDERRUN - slack:
                under += 1
                break
        # Safety net for ink that is not in any column: a diagram's labels, a table's
        # cells, a caption set at its own left edge. 23 of 26 lines on 331_pid_diagram
        # widened 30 % were invisible because no cluster of 3 lines held them. Two lines
        # running far past the source's own widest line is not line breaking.
        s_max = max((b[2] for b in page_lines(src[i])), default=0)
        far = sum(1 for b in page_lines(gd[i]) if b[2] > s_max + 3 * RIGHT_OVERRUN)
        if far >= 2 and not over:
            over += 1
    # source = pages whose column overruns the source's, render = pages whose column is
    # narrower than the source's. A raw total would read the same for one of each.
    c["60_text_column_right_edge"] = (over, under, over == 0 and under == 0)

    return c


def extra_checks(src, gd, s_runs, g_runs, pairs):
    """Return checks 32-48. pairs is [(source_run, render_run), ...] already matched."""
    c = {}

    # ---- 32 stroke lines ---------------------------------------------------
    def stroke_stats(doc):
        n, widths = 0, []
        for p in doc:
            for st in _strokes(p):
                n += 1
                if st["width"]:
                    widths.append(st["width"])
        widths.sort()
        med = widths[len(widths) // 2] if widths else 0
        return n, round(med, 2)

    s_n, s_w = stroke_stats(src)
    g_n, g_w = stroke_stats(gd)
    c["32_stroke_lines"] = (s_n, g_n, s_n == 0 or g_n >= max(1, int(s_n * 0.8)))

    # ---- 33 RETIRED 13 Nov: it was 46 with a 2 pt inset ---------------------
    # 33 and 46 were the same question twice. Both walked every span, both kept the same
    # strokes (`_strokes(p)` filtered to rect.height <= 2.5), both required the rule to sit
    # inside the span's box vertically (r.y0 > y0 + 1.5 and r.y0 < y1 - 1.5), both counted
    # one hit per span with `break`, and both judged the render against the source with the
    # identical allowance `g <= s + s // 5`. The only difference was 2 pt on each end of the
    # horizontal test - 33 wanted r.x0 < x1 - 2 and r.x1 > x0 + 2, 46 accepts any overlap.
    # 33's hits are therefore a strict SUBSET of 46's, span for span.
    #
    # Measured on the 208-document run of engine 2a68de6 (RESULTS.jsonl): 33 and 46 report
    # the SAME source and render count on all 208 documents and the same verdict on all 208.
    # The 2 pt inset never bites, because no corpus document carries a rule that overlaps a
    # span by less than 2 pt. Retiring 33 changes no verdict anywhere (union of 32/33/46 is
    # 136 of 208 documents with or without it), which is the whole point: it was costing a
    # vote in a 57-check universe and buying nothing.
    #
    # Constructed 13 Nov (work/discrim.py, run against this file's own extra_checks): a 0.5 pt
    # stroked rule through a word reads 33 fail / 46 fail, and the same rule drawn as a 0.8 pt
    # filled band - the way DocxWriter.shape() draws a standalone rule - also reads fail/fail,
    # so the two shared the `_strokes` amendment as well. A rule overlapping a span's right
    # edge by 1 pt reads 33 pass / 46 fail, which is the only behaviour 33 lacks. A source
    # carrying six such 1 pt touches and a render that adds one true crossing reads
    # 33 fail / 46 pass, which is the only verdict 33 reached alone - and it reaches it
    # because its own allowance divides by the smaller count (s_bot // 5 = 0 against
    # s_c // 5 = 1), not because it saw anything 46 did not.
    #
    # 46 is the survivor, and it must keep all five of these or the question stops being
    # asked: the per-span walk with `break` (one hit per span, not per rule), the
    # rect.height <= 2.5 filter on `_strokes` output (so a box, a 4 pt band and a vertical
    # rule stay out), the vertical-interior test (so an underline at the baseline stays out -
    # that is 36_underline_rules' question), the source-relative verdict `g <= s + s // 5`
    # (a document that legitimately prints a rule across text must not fail against itself),
    # and the `_strokes` dependency itself (a filled 0.8 pt band IS a rule).
    #
    # Cost accepted: with no inset, 46 counts a rule that overlaps a span box by 1 pt, which
    # may be side bearing rather than glyph. The corpus does not contain that case (0 of 208
    # documents differ between the two geometries), so the inset was never calibrated; it is
    # recorded here as a known looseness rather than carried as a second check.


    # ---- 34 per-span style -------------------------------------------------
    # Size, colour and weight of each matched span, not just how many distinct
    # values exist somewhere in the document.
    ok_size = ok_col = ok_weight = 0
    for s_sp, g_sp in pairs:
        if abs(s_sp["size"] - g_sp["size"]) <= 0.6:
            ok_size += 1
        if colour_same(s_sp["colour"], g_sp["colour"]):
            ok_col += 1
        if s_sp["weight"] == g_sp["weight"]:
            ok_weight += 1
    tot = max(1, len(pairs))
    none = not pairs
    c["34a_span_size_match"] = (100, 0 if none else round(100 * ok_size / tot),
                                none or ok_size >= tot * 0.85)
    c["34b_span_colour_match"] = (100, 0 if none else round(100 * ok_col / tot),
                                  none or ok_col >= tot * 0.85)
    c["34c_span_weight_match"] = (100, 0 if none else round(100 * ok_weight / tot),
                                  none or ok_weight >= tot * 0.85)

    # ---- 35 rotation -------------------------------------------------------
    def rotated(doc):
        n = 0
        for p in doc:
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    d = ln.get("dir", (1, 0))
                    if abs(d[1]) > 0.02 or d[0] < 0.98:
                        n += 1
        return n

    s_r = rotated(src)
    g_r = rotated(gd)
    c["35_rotation"] = (s_r, g_r, s_r == 0 or g_r >= max(1, int(s_r * 0.6)))

    # ---- 36 underline / strike --------------------------------------------
    # No underline flag in the text model, so count thin strokes sitting just
    # under a baseline - an approximation, and named as one.
    def rules_under_text(doc):
        n = 0
        for p in doc:
            lines = [s for s in _strokes(p) if s["rect"].height <= 2.5]
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        if not sp.get("text", "").strip():
                            continue
                        x0, y0, x1, y1 = sp["bbox"]
                        for st in lines:
                            r = st["rect"]
                            if y1 - 2.5 <= r.y0 <= y1 + 2.5 and r.x0 < x1 and r.x1 > x0:
                                n += 1
                                break
        return n

    s_u = rules_under_text(src)
    g_u = rules_under_text(gd)
    c["36_underline_rules"] = (s_u, g_u, g_u >= max(1, int(s_u * 0.7)) if s_u else True)

    # ---- 37 super / subscript ---------------------------------------------
    # The old version counted the superscript FLAG BIT and nothing else. PyMuPDF
    # has no subscript bit, so on a document whose only script text is subscript
    # it read 0 on the source side and the check passed unconditionally.
    # Measured 13 Nov over the 211-document corpus: spans with flags & 1 exist in
    # 3 documents, 5 spans, all superscript (journal-2col-with-footnotes 3,
    # academic-paper-ieee-2col-abstract 1, 400_comic_page_speech_bubbles 1) - and
    # a subscript run exists NOWHERE in the corpus. The subscript half of this
    # check had never once been exercised.
    #
    # A script run is detected by BASELINE OFFSET instead, which covers both
    # directions. The numbers below are measured, not chosen:
    #   - the corpus's only genuine script text is 3 footnote markers in
    #     journal-2col-with-footnotes.pdf: 7.1 pt in an 8.9 pt line, 0.50 em
    #     above the line's dominant baseline;
    #   - Word's own default for vertAlign is a 58 % size at a 33 % offset, so a
    #     correct conversion of a Word subscript lands at 0.33 em and 0.58 size;
    #   - same-line baseline noise among FULL-SIZE spans reaches 0.30 em
    #     (academic-paper-ieee-2col-abstract "Abstract-", 0.302), which is why the
    #     size test is not optional: a script run is also SMALLER than its line;
    #   - a small text object sitting on a lower baseline reaches 0.73 em
    #     (400_comic_page_speech_bubbles "SUPERVISOR", 6.0 pt in a 7.5 pt line).
    #     That is not a script run, so the offset needs a ceiling.
    # Hence: size <= 85 % of the line's largest span AND offset within
    # [0.15, 0.60] em of the line's dominant size. 0.15 clears the noise, 0.60
    # brackets both conventions (0.33 Word, 0.50 corpus) and stays under 0.73.
    # The trade-off is explicit: a render that used a > 0.60 em offset where the
    # source used 0.50 would be counted on one side only, which is why the
    # ceiling is set above the corpus's measured maximum rather than at it.
    SCRIPT_SIZE = 0.85
    SCRIPT_LO, SCRIPT_HI = 0.15, 0.60

    def scripts(doc):
        """(subscript runs, superscript runs), by baseline offset."""
        sub = sup = 0
        for p in doc:
            for blk in p.get_text("rawdict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    info = []
                    for sp in ln.get("spans", []):
                        ys = [ch["origin"][1] for ch in sp.get("chars", [])
                              if ch["c"].strip()]
                        if ys:
                            info.append((sp, sorted(ys)[len(ys) // 2], len(ys)))
                    if len(info) < 2:
                        continue
                    # the line's own baseline: the char-weighted median, so a
                    # line of one big word plus a footnote marker is measured
                    # against the word and not against the midpoint.
                    total = sum(n for _, _, n in info)
                    acc, dom = 0, None
                    for _, y, n in sorted(info, key=lambda t: t[1]):
                        acc += n
                        if acc >= total / 2.0:
                            dom = y
                            break
                    big = max((sp.get("size") or 0) for sp, _, _ in info) or 1.0
                    for sp, y, _ in info:
                        size = sp.get("size") or 0
                        if size > SCRIPT_SIZE * big:
                            continue
                        r = (y - dom) / big
                        if SCRIPT_LO <= r <= SCRIPT_HI:
                            sub += 1
                        elif -SCRIPT_HI <= r <= -SCRIPT_LO:
                            sup += 1
        return sub, sup

    s_sc, g_sc = scripts(src), scripts(gd)
    c["37_super_subscript"] = (s_sc, g_sc, all(
        sv == 0 or gv >= max(1, int(sv * 0.9)) for sv, gv in zip(s_sc, g_sc)))

    # ---- 38 list markers ---------------------------------------------------
    # Two defects, both measured on 13 Nov:
    #   - the trailing space had to be inside the SAME span, so a render that
    #     emits "1." and "First item" as separate spans never counted. That is
    #     not an exotic render, it is the corpus's own shape: all ten markers of
    #     69_two_col_legal_numbered_clauses.pdf sit in their own span, and the
    #     old check read 0 on it - and 0 on any render of it, so a ten-item list
    #     could lose every marker and still pass.
    #   - t[1:3] in (". ", ") ") can never match a two-digit marker: "10." gives
    #     "0.", so the tenth item of every list was invisible on BOTH sides.
    #     Old count on that document: 0. Ten-item list, ten items, zero markers.
    # The test is now on the stripped span text alone - digits plus "."/")"
    # followed by end-of-span or a space, or a bullet glyph.
    NUM_MARK = re.compile(r"^\d{1,4}[.)](?:\s|$)")

    def markers(doc):
        n = 0
        for p in doc:
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        t = sp.get("text", "").strip()
                        if not t:
                            continue
                        if t[0] in "\u2022\u25cf\u25aa\u2023\u2043-*\u00b7" or \
                                NUM_MARK.match(t):
                            n += 1
                            break
        return n

    s_m, g_m = markers(src), markers(gd)
    c["38_list_markers"] = (s_m, g_m, s_m == 0 or g_m >= max(1, int(s_m * 0.9)))

    # ---- 39 image position -------------------------------------------------
    # A DISTANCE TEST, WITH THE PAGE IN THE KEY. The old body quantised each box to an
    # 8 pt bin (round(x/8), round(y/8)) and intersected the two sets, which is not a
    # tolerance - it is a membership test whose tolerance is 4 pt in the middle of a bin
    # and 0 pt on the boundary. A box sitting at x = 52.0 (x/8 = 6.5) is exactly on one:
    # 407_id_card_front_back fails after a 0.1 pt shift, 11_stamp_with_signature_image
    # (y = 420.000, y/8 = 52.5) fails after 0.1 pt too, and on the 15 corpus documents
    # that carry an image a uniform 0.1 pt move fails 2 of them and a 1 pt move fails 5 -
    # all with every image where it belongs. set() also dropped a count whenever two
    # pictures shared a bin, and the key carried no page, so a picture moved from page 1
    # to page 2 at the same coordinates passed. Nearest one-to-one match within 4 pt per
    # axis keeps the old tolerance and removes the cliff.
    IMG_POS_TOL = 4.0

    def img_boxes(doc):
        boxes = []
        for i, p in enumerate(doc):
            for im in p.get_image_info():
                b = im["bbox"]
                boxes.append((i, b[0], b[1]))
        return boxes

    s_ib, g_ib = img_boxes(src), img_boxes(gd)
    if not s_ib:
        c["39_image_position"] = (0, len(g_ib), True)
    else:
        used = set()
        common = 0
        for (pg, x, y) in s_ib:
            best = None
            for j, (gp, gx, gy) in enumerate(g_ib):
                if j in used or gp != pg:
                    continue
                if abs(gx - x) <= IMG_POS_TOL and abs(gy - y) <= IMG_POS_TOL:
                    dist = abs(gx - x) + abs(gy - y)
                    if best is None or dist < best[0]:
                        best = (dist, j)
            if best is not None:
                used.add(best[1])
                common += 1
        c["39_image_position"] = (len(s_ib), common,
                                  common >= max(1, -(-len(s_ib) * 3 // 5)))

    # ---- 40 link targets ---------------------------------------------------
    def link_targets(doc):
        out = set()
        for p in doc:
            for l in p.get_links():
                if l.get("uri"):
                    out.add(l["uri"])
        return out

    s_l, g_l = link_targets(src), link_targets(gd)
    c["40_link_targets"] = (len(s_l), len(s_l & g_l), s_l == g_l or (not s_l))

    # ---- 41 block spacing --------------------------------------------------
    def block_gaps(doc):
        gaps = []
        for p in doc[:1]:
            ys = sorted({round(b["bbox"][1], 1) for b in p.get_text("dict")["blocks"]
                         if b.get("type") == 0})
            gaps += [round(b - a, 1) for a, b in zip(ys, ys[1:]) if 1 < b - a < 300]
        gaps.sort()
        return gaps[len(gaps) // 2] if gaps else 0

    s_bg, g_bg = block_gaps(src), block_gaps(gd)
    c["41_block_spacing"] = (s_bg, g_bg, s_bg == 0 or abs(g_bg - s_bg) <= 3.0)

    # ---- 42 alignment ------------------------------------------------------
    def align_mix(doc):
        # The block bbox is the union of its own lines, so the widest line of EVERY block
        # satisfies lx0 - bx0 < 4 and was counted as 'left'. Every block therefore
        # contributed a 'left' by construction: on the 211-document corpus 5925 of 5925
        # blocks did, left was 72% of all lines and centre 2%. A fully centred document
        # read left, never centre.
        # A line is only left-aligned relative to the COLUMN it sits in, not to a box
        # drawn round itself, so the reference is the page's text margin. The widest line
        # of a centred block still spans the column and is indistinguishable from flush
        # left, but the narrower lines now read centre and the mix is centre-dominated.
        left = right = centre = 0
        for p in doc:
            blks = [b for b in p.get_text("dict")["blocks"] if b.get("type") == 0]
            if not blks:
                continue
            le = statistics.mode([round(b["bbox"][0]) for b in blks])
            re_ = statistics.mode([round(b["bbox"][2]) for b in blks])
            if re_ - le < 10:
                continue
            for blk in blks:
                for ln in blk.get("lines", []):
                    lx0, _, lx1, _ = ln["bbox"]
                    if lx1 - lx0 < 10:
                        continue
                    if abs(lx0 - le) < 4:
                        left += 1
                    elif abs(re_ - lx1) < 4:
                        right += 1
                    elif abs((lx0 + lx1) / 2 - (le + re_) / 2) < 6:
                        centre += 1
        return (left, right, centre)

    s_al, g_al = align_mix(src), align_mix(gd)
    same = sum(min(a, b) for a, b in zip(s_al, g_al))
    tot_al = max(1, sum(s_al))
    c["42_alignment_mix"] = (sum(s_al), same,
                             sum(s_al) == 0 or same >= tot_al * 0.7)

    # ---- 43 horizontal placement ------------------------------------------
    # The old 21_median_dx only looked at the median, which hides a whole column
    # shifted. This asks how many spans are horizontally close, span by span.
    near_x = sum(1 for s_sp, g_sp in pairs if abs(g_sp["x"] - s_sp["x"]) <= 10)
    tot_p = max(1, len(pairs))
    c["43_within_10pt_x"] = (100, round(100 * near_x / tot_p),
                             (not pairs) or near_x >= tot_p * 0.9)

    # ---- 44 header / footer ------------------------------------------------
    def edge_text(doc):
        # Returns the band TEXT, not a count. Widening the band to 0.11/0.89 fixed the 1 pt
        # footer shift but pulled 116 real body blocks into the header count on the corpus
        # (82 of 211 documents, 90% of them not repeated headers - table headers, section
        # headings, the second and third body line), which both dilutes the check and moves
        # its boundary into the densest region of the page. Counting text instead: a footer
        # that moves 1 pt is the same string, a footer that is dropped is a different one,
        # and body text in the band appears on both sides and cancels out.
        out = []
        for p in doc:
            H = p.rect.height
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                y = blk["bbox"][1]
                if y < H * 0.10 or y > H * 0.90:
                    t = " ".join("".join(sp["text"] for ln in blk.get("lines", [])
                                         for sp in ln["spans"]).split())
                    if t:
                        out.append(t)
        return out

    def _present(t, pool):
        if t in pool:
            return True
        return any(difflib.SequenceMatcher(None, t, q).ratio() >= 0.9 or t in q for q in pool)

    s_e, g_e = edge_text(src), edge_text(gd)
    # Every band string in the source must still be in the render. A 1 pt shift keeps every
    # string, so the original defect passes; a dropped header loses its string, so the check
    # still fires; a body block that happens to sit in the band is present on both sides.
    # The 0.9 ratio was kept out of this on purpose: with s_e=2 it tolerated one of the two
    # headers being lost, which is the dilution the widening introduced.
    missing = [t for t in s_e if not _present(t, g_e)]
    c["44_header_footer"] = (len(s_e), len(s_e) - len(missing), not missing)

    # ---- 45 character accuracy --------------------------------------------
    s_txt = "".join(s_sp["text"] for s_sp in s_runs)
    g_txt = "".join(g_sp["text"] for g_sp in g_runs)
    # The glyph stream: every span's text, all whitespace removed.
    #
    # Two defects, both proved on 13 Nov. quick_ratio() is the MULTISET intersection of the two
    # strings, so it is a hard upper bound on ratio() and cannot see reordering at any scale -
    # reversing every run on every page left it reading 100 on 208 of 208 corpus documents.
    # And the old comparison joined span texts with no separator after `runs()` dropped
    # whitespace-only spans, so a render that emits the space as its own span read 95 on text
    # that had not changed. A span boundary can fall anywhere, including mid-word, so no join
    # character can be correct: the separator belongs to the extractor, not to the document.
    # Removing whitespace from both sides makes the check invariant to every cut - measured min
    # 100 across the mid-word split of all 18263 spans in 208 documents - and a dropped space is
    # still caught, by 03/04, which compare the word multiset.
    #
    # SequenceMatcher with autojunk=False, not the default: past 200 characters the heuristic
    # discards any character that is more than 1 % of the sequence, which makes the score depend
    # on length rather than on the difference. This is the same idiom verify.py and visual.py
    # already use for text.
    def _glyphs(rs):
        return re.sub(r"[\s\u00a0]+", "", "".join(r["text"] for r in rs))

    s_cs, g_cs = _glyphs(s_runs), _glyphs(g_runs)
    ratio = round(100 * difflib.SequenceMatcher(None, s_cs, g_cs, autojunk=False).ratio())
    c["45_char_accuracy"] = (100, ratio, ratio >= 97)

    # ---- 46 text crossing a rule (per span) --------------------------------
    def spans_crossing(doc):
        n = 0
        for p in doc:
            lines = [s for s in _strokes(p) if s["rect"].height <= 2.5]
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        if not sp.get("text", "").strip():
                            continue
                        x0, y0, x1, y1 = sp["bbox"]
                        for st in lines:
                            r = st["rect"]
                            if r.y0 > y0 + 1.5 and r.y0 < y1 - 1.5 and r.x0 < x1 and r.x1 > x0:
                                n += 1
                                break
        return n

    s_c, g_c = spans_crossing(src), spans_crossing(gd)
    c["46_text_crossing_rule"] = (s_c, g_c, g_c <= s_c + s_c // 5)

    # ---- 47 margins: the body column's left margin, page by page ------------
    # WHAT THIS USED TO MEASURE. Four numbers: the ink bounding box of PAGE 1, compared on
    # all four edges with a 12 pt tolerance. That is not a margin. Measured on the 211
    # sources (prove-47.py census): on 202 of them the page-1 ink box sits further out than
    # the body column by more than this check's own tolerance on at least one edge - a
    # header pins miny on 178 (median 31 pt), a footer maxy on 156 (median 232 pt), a
    # masthead or a full-width rule maxx on 136 (median 91 pt), marginal ink minx on 47.
    # On the median document the number called "the right margin" is 91 pt outside the body
    # column before anything has gone wrong, and 12 pt is 25 % of the median 48 pt margin.
    # So an unrelated stamp or header decides the verdict: adding a masthead, a rule and a
    # page number without touching the body failed this check on 40 of 40 documents.
    #
    # WHAT IT MEASURES NOW. The horizontal position of the body column, on EVERY page, in
    # the two ways a margin can be wrong:
    #   (a) the MODAL left edge of the page's ink lines - the margin itself. A mode cannot
    #       be moved by one stray span, a masthead or a stamp the way min() can, and it
    #       survives a re-wrap because it compares where lines START, not which words.
    #   (b) the distance from each source line's left edge to the nearest render line's left
    #       edge on the same page - the indent structure. A block indented 18 pt too far
    #       leaves the mode untouched and is caught here.
    # Both are distributions over lines, so the tolerance is stated on the distribution:
    # median <= 2 pt, p90 <= 6 pt. Vertical placement is NOT this check's job: 18/19/20
    # measure dy on every page and a deleted top margin moves them by the whole margin
    # (measured: a 56 pt lift takes 18_median_dy to -56 on 210 of 210 documents). It also
    # read page 1 only, which left a 30 pt shift confined to pages 2+ silent on 18 of 18
    # multi-page documents. This check owns x, on every page.
    # THREE FIXES TO THE FIRST VERSION OF THIS CHECK, each measured on the corpus.
    #
    # (a) THE ANCHOR WAS A TIE-BREAK. statistics.mode returns the FIRST value with the
    #     highest count, so on a page whose two commonest left edges hold the same number
    #     of lines the "margin" was whichever one the block order put first. 49 of the
    #     corpus's 545 pages are an exact tie and 22 more differ by one line (see the
    #     tie census in the patch notes). Constructed: on 02_stamp_rotated_15deg_upleft
    #     (left edges 56, 86, 332 each holding 11 lines) wrapping ONE line into two at
    #     x=86 - nothing moved - flipped the anchor to 86 and the check reported a 30 pt
    #     margin error. The anchor is now the LEFTMOST left edge that many lines share,
    #     which no single added or moved line can change.
    # (b) THE p90 LEFT THE TOP 10 % OF d UNCONSTRAINED. For a page with n lines the
    #     percentile index is round(0.9*(n-1)), so n-1-round(0.9*(n-1)) lines could be
    #     anywhere at all: 1607 of the corpus's 17214 body lines (9.3 %) and 134
    #     documents with >=4 such lines on some page. Constructed: 11 of 106 lines on
    #     product-catalogue-code-left-price-right moved +70 pt and the check still said
    #     (0.0, 0.0, ok). A COUNT BUDGET replaces it - at most max(2, 5 %) of the page's
    #     lines may be unregistered, and no single line may be further out than
    #     DX_WORST_TOL. Same shape as 18_displacement, which is the house standard.
    # (c) 3 pt ON THE ANCHOR IS KEPT. It is the one number here that is a real decision
    #     rather than a defect: a 2 pt whole-page shift still passes (measured), a 3 pt
    #     one fails on the registration rule. It is stated, not derived.
    LM_TOL = 3.0        # the body's left edge may differ by this much, per page
    DX_MED_TOL = 2.0    # a line is registered if a render line starts within this
    DX_TAIL_SHARE = 0.05  # at most this share of a page's lines may be unregistered
    DX_TAIL_MIN = 2       # ... but never fewer than this many
    DX_WORST_TOL = 24.0   # ... and no single line may be further out than this

    def anchor(xs):
        """The body's left margin: the leftmost left edge that many lines share.

        Not the mode. The mode is decided by a tie on 49 of 545 corpus pages, and one
        re-wrapped line is enough to move it (22 more pages differ from their runner-up
        by a single line). A margin is a place many lines start, and the leftmost such
        place is the one no single line can change.
        """
        if not xs:
            return None
        need = max(3, int(0.05 * len(xs)))
        cnt = collections.Counter(round(x) for x in xs)
        shared = [x for x, k in cnt.items() if k >= need]
        return min(shared) if shared else min(round(x) for x in xs)

    def line_lefts(doc):
        """[(page, body left edge, [(left edge, centre y), ...]), ...]

        The centre y is carried because the registration below is ROW-LOCAL. Matching
        each source line against every render line's left edge on the page made a
        displaced line invisible whenever it happened to land on another indent level:
        constructed, 11 of 106 lines on product-catalogue-code-left-price-right moved
        +70 pt straight onto the page's second column and d stayed 0.0 on every one of
        them. Restricting the match to render lines on the same row keeps the property
        the set-distance was there for - a re-wrapped line still starts at the column
        edge, so wrapping cannot move it - and removes the collision.
        """
        out = []
        for pi, p in enumerate(doc):
            xs = []
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    if not "".join(sp.get("text", "") for sp in ln.get("spans", [])).strip():
                        continue
                    b = ln["bbox"]
                    xs.append((round(b[0], 1), (b[1] + b[3]) / 2.0, b[3] - b[1]))
            out.append((pi, anchor([x[0] for x in xs]), xs))
        return out

    s_ll, g_ll = line_lefts(src), line_lefts(gd)
    margin_bad, indent_bad = [], []
    worst_med = worst_tail = worst_worst = 0.0
    for (pi, s_ml, s_xs), (_, g_ml, g_xs) in zip(s_ll, g_ll):
        if s_ml is not None and g_ml is not None and abs(s_ml - g_ml) > LM_TOL:
            margin_bad.append((pi + 1, s_ml, g_ml))
        if not s_xs or not g_xs:
            continue
        # set distance, not pairing: a render may split, merge or drop a line, and an index
        # pairing turns that into a false positional failure - the defect 59 had and 22 had.
        d = []
        for x, yc, h in s_xs:
            near = [y for y, gy, _ in g_xs if abs(gy - yc) <= max(2.0, 0.35 * h)]
            if not near:
                near = [y for y, _, _ in g_xs]     # the line moved vertically: 18/19's job
            d.append(min(abs(x - y) for y in near))
        tail = [v for v in d if v > DX_MED_TOL]
        budget = max(DX_TAIL_MIN, int(round(DX_TAIL_SHARE * len(d))))
        worst_med = max(worst_med, statistics.median(d))
        worst_tail = max(worst_tail, float(len(tail)))
        worst_worst = max(worst_worst, max(d))
        # A count budget, not a percentile. The percentile left the largest 10 % of d
        # unconstrained by construction; the budget leaves at most 5 %, and the worst-line
        # cap means even a line inside the budget cannot be arbitrarily far out.
        if len(tail) > budget or max(d) > DX_WORST_TOL:
            indent_bad.append((pi + 1, len(tail), round(max(d), 1)))

    # Reported as (worst page median, worst page unregistered-line count, ok), with the
    # worst single displacement in the failure record. The page numbers and the actual
    # margins are in margin_bad / indent_bad so a failure can be read without re-running:
    # "47_margins: pages 3,7 left edge 56->48" is what a fixer needs.
    del worst_worst
    c["47_margins"] = (round(worst_med, 1), int(worst_tail),
                       not margin_bad and not indent_bad)
    # A detail check would be counted as a check: all_check_ids() discovers ids by running
    # the verifier, so a second key here would add a free pass to every document's score.
    # The worst page's numbers are what the tuple already carries; the page numbers are in
    # margin_bad / indent_bad and are reproduced by any re-run with --json.
    del margin_bad, indent_bad

    # ---- 48 image area -----------------------------------------------------
    def img_area(doc):
        tot = 0
        for p in doc:
            for im in p.get_image_info():
                b = im["bbox"]
                tot += max(0, (b[2] - b[0])) * max(0, (b[3] - b[1]))
        return round(tot)

    # The floor was 50 %, so a document could lose 36 % of its picture area and pass -
    # measured on a synthetic pair: a 200x200 picture drawn at 160x160 reads src=40000
    # render=25600 ok=True. Every one of the 15 corpus documents that carries a picture
    # comes out of Google's export with MORE area than it went in with (5720 -> 104802,
    # 14184 -> 95939, 9692 -> 29111), so a 90 % floor moves no corpus number today and
    # closes the hole. Below half still fails, as it always did.
    s_ia, g_ia = img_area(src), img_area(gd)
    c["48_image_area"] = (s_ia, g_ia,
                          s_ia == 0 or g_ia >= s_ia * 0.9)

    return c


def compare(src_path, gd_path, docx_path=None):
    src = fitz.open(src_path)
    gd = fitz.open(gd_path)

    checks = {}

    # ---- gather -------------------------------------------------------------
    # Each run carries its page. The matcher below needs it: without a page, a source run on
    # page 1 can be paired with a render run on page 7 that holds the same word, and the
    # resulting dy is a page offset reported as a placement error.
    s_runs, g_runs = [], []
    for i, p in enumerate(src):
        s_runs += runs(p, i)
    for i, p in enumerate(gd):
        g_runs += runs(p, i)

    s_text = " ".join(r["text"] for r in s_runs)
    g_text = " ".join(r["text"] for r in g_runs)
    s_words = collections.Counter(norm_word(w) for w in s_text.split() if w.strip())
    g_words = collections.Counter(norm_word(w) for w in g_text.split() if w.strip())

    # 08 counts images the page DRAWS, not images its /Resources /XObject dictionary
    # DECLARES. get_images() is the dictionary: it includes an image nothing places and one
    # inherited from a shared Resources on the Pages node, and Google's export declares more
    # than the source draws (10_stamp_as_image reads 1 -> 7, 300_prescription_rx 1 -> 42),
    # which inflates the numerator until the predicate cannot fail. Proven both ways with a
    # synthetic pair: a render that declares two XObjects and draws none reads 08 src=1
    # render=2 ok=True - a total image loss passes - and a document that declares an XObject
    # it never draws reads src=2 render=1 and fails against a faithful render, with 39 and 48
    # (which already use get_image_info) reading 1 and passing. 57f521d described this fix in
    # its message and applied only the 47_margins half; the code kept get_images().
    s_imgs = sum(len(p.get_image_info()) for p in src)
    g_imgs = sum(len(p.get_image_info()) for p in gd)

    # ---- COMPLETENESS (1-16) ------------------------------------------------
    checks["01_page_count"] = (src.page_count, gd.page_count,
                               src.page_count == gd.page_count)
    # 02_text_run_count was DROPPED on 13 Nov. A "run" is not a document object: runs() splits
    # the text layer by (line, font, size, colour, flags), so a run boundary is a property of
    # the extractor's grouping, not of the page. Measured four ways:
    #   - under a one-sided rule 17 of 208 documents failed, and all 17 also failed 03/04;
    #   - 02 never disagreed with 03/04 in the loss direction: 77 documents where 03/04 fired
    #     and 02 was silent, 0 the other way;
    #   - dropping it changed NO document's overall verdict on 208 rows;
    #   - its one exclusive fire, constructed, is a document where every glyph, word, font,
    #     size and colour is identical and only the extractor's line gap moved across ~7 pt.
    # A check whose only unique signal is a false positive is a liability, and 03/04 are an
    # exact multiset comparison with zero tolerance - strictly stronger.

    missing = s_words - g_words
    extra = g_words - s_words

    # 03_word_count RETIRED 13 Nov: it was 04 with a second display, and a second vote.
    # The two carried the SAME predicate - `len(missing) == 0`, the identical expression,
    # not a similar one - so no document could ever fail one and pass the other. Measured
    # on the 211 rows of RATCHET-20261113-084751.json: 03 fails 95, 04 fails 95, and the
    # symmetric difference of the two failure sets is 0. On the 208 rows of RESULTS.jsonl
    # (engine 2a68de6) they agree on 208 of 208.
    #
    # What 03 displayed was the token totals, and those do not describe its own verdict.
    # On 5 rows the totals are EQUAL and it votes FAIL (311_fir_police_form 232 -> 232: a
    # word swapped for another); on 82 rows the totals differ and it votes PASS
    # (bank-statement-horizontal-rules-only 319 -> 459, boq-horizontal-rules-only
    # 364 -> 482). A number and a verdict that disagree on 87 of 208 rows teach a fixer
    # the wrong thing, and the vote was the second vote for the class classify.py already
    # records as "03_word_count (+1)" over {03, 04}: one fault, two of the universe.
    #
    # Retiring it moves no verdict. 0 of 211 rows fail only 03, and 0 fail only {03, 04}.
    # What must NOT go with it is the magnitude, which is the one thing its totals had
    # that 04's count of TYPES does not: a word type short by ten copies reads 1 here.
    # That is 04's own limit and it is kept below, because 04's verdict is the multiset
    # test and does not depend on the number. See 05 for the side where it does.
    # 04 was a zero-tolerance WORD-multiset test and a word is not a reproducible unit.
    # Measured over 211 documents: two extractors reading the SAME bytes disagree about the
    # word multiset on 49 % of the documents that fail this check, and a geometry tokeniser
    # that rebuilds words from glyph gaps changes the verdict on ZERO documents while moving
    # 156 of 60,387 tokens. Of 417 recorded deficits, 307 are a contiguous substring of the
    # render's own page text, 83 have every character present but split across a boundary,
    # and 8 are a character genuinely absent. A boundary is the extractor's, not the
    # document's - 45_char_accuracy already says so in its own comment. So the unit here is
    # the character: "not one thing may be missing" is a statement about characters.
    s_chars = collections.Counter(norm_text(s_text))
    g_chars = collections.Counter(norm_text(g_text))
    chars_missing = s_chars - g_chars
    checks["04_chars_missing"] = (0, sum(chars_missing.values()), not chars_missing)
    checks["05_words_extra"] = (0, len(extra), len(extra) <= max(1, sum(s_words.values()) // 100))

    # tables: count of distinct column x-positions that repeat down the page
    def table_signature(runs_list):
        xs = collections.Counter()
        for r in runs_list:
            xs[round(r["x"] / 6)] += 1
        return sum(1 for k, v in xs.items() if v >= 3)
    s_tbl, g_tbl = table_signature(s_runs), table_signature(g_runs)
    checks["06_table_columns"] = (s_tbl, g_tbl, abs(s_tbl - g_tbl) <= max(1, s_tbl // 10))
    # rows, not columns again - 06 already covers columns
    def table_rows(runs_list):
        ys = collections.Counter()
        for r in runs_list:
            ys[round(r["y"] / 6)] += 1
        return sum(1 for k, v in ys.items() if v >= 3)
    s_rows, g_rows = table_rows(s_runs), table_rows(g_runs)
    checks["07_table_rows"] = (s_rows, g_rows, abs(s_rows - g_rows) <= max(2, s_rows // 5))

    checks["08_image_count"] = (s_imgs, g_imgs, g_imgs >= s_imgs)

    s_fonts = collections.Counter(face_name(r["font"]) for r in s_runs)
    g_fonts = collections.Counter(face_name(r["font"]) for r in g_runs)
    # every source font family must appear in the render (a substitute is allowed
    # to have a different name, but a family that vanishes entirely is a loss)
    # Substitution renames a family (Arial -> Liberation Sans) so the names cannot be
    # compared, but a family that vanishes entirely is a loss. Require the render to carry
    # at least 80 % as many distinct faces as the source.
    # A source with no fonts has nothing to lose; failing it is a false positive.
    checks["09_font_names"] = (len(s_fonts), len(g_fonts),
                               len(s_fonts) == 0 or
                               len(g_fonts) >= max(1, int(len(s_fonts) * 0.8)))

    s_sizes = collections.Counter(r["size"] for r in s_runs)
    g_sizes = collections.Counter(r["size"] for r in g_runs)
    common = sum(1 for k in s_sizes if k in g_sizes)
    checks["10_font_sizes"] = (len(s_sizes), common,
                               len(s_sizes) == 0 or
                               common >= max(1, int(len(s_sizes) * 0.8)))

    def bold_count(rs):
        return sum(1 for r in rs if "bold" in norm_font(r["font"]))
    # Same rule as 02: a bold run split in two is still bold. 4 of the 6 rows where this fired
    # with render > source pass the per-span weight check 34c - the boldness is right and only
    # the segmentation moved.
    checks["11_bold_runs"] = (bold_count(s_runs), bold_count(g_runs),
                              bold_count(g_runs) >= bold_count(s_runs) - max(2, bold_count(s_runs) // 5))

    def italic_count(rs):
        return sum(1 for r in rs if "italic" in norm_font(r["font"]) or "oblique" in norm_font(r["font"]))
    checks["12_italic_runs"] = (italic_count(s_runs), italic_count(g_runs),
                                abs(italic_count(s_runs) - italic_count(g_runs)) <= max(2, italic_count(s_runs) // 5))

    s_cols = collections.Counter(r["colour"] for r in s_runs)
    g_cols = collections.Counter(r["colour"] for r in g_runs)
    checks["13_text_colours"] = (len(s_cols), len(g_cols),
                                 len(s_cols) == 0 or
                                 len(g_cols) >= max(1, int(len(s_cols) * 0.8)))

    s_fill = sum(1 for p in src for _ in fill_rects(p))
    g_fill = sum(1 for p in gd for _ in fill_rects(p))
    # Many documents legitimately contain no filled shapes. Requiring >= 1 when the
    # source has none failed every such document - a false positive, not a defect.
    checks["14_filled_shapes"] = (s_fill, g_fill,
                                  s_fill == 0 or g_fill >= max(1, int(s_fill * 0.8)))

    s_links = sum(len(p.get_links()) for p in src)
    g_links = sum(len(p.get_links()) for p in gd)
    checks["15_links"] = (s_links, g_links, s_links == 0 or g_links >= s_links)

    s_digits = sum(1 for r in s_runs if any(c.isdigit() for c in r["text"]))
    g_digits = sum(1 for r in g_runs if any(c.isdigit() for c in r["text"]))
    checks["16_numeric_runs"] = (s_digits, g_digits,
                                 abs(s_digits - g_digits) <= max(3, s_digits // 10))

    # ---- POSITION (17-24) ---------------------------------------------------
    # Match each source run to a render run on the SAME PAGE, consuming it once, and joining
    # adjacent runs when the render split a span.
    #
    # The old matcher bucketed by text across the whole document and took the nearest by
    # |dy|+|dx| with no page constraint and no consumption. Measured on 13 Nov, constructed:
    #   - a render that splits one span leaves no exact match, so the run was DROPPED from
    #     dys; with every span split the pair set is empty and 18/19/20/21 all passed;
    #   - one render run could satisfy several source runs, so a duplicate word reported a
    #     dy of 200 pt on a span that had not moved;
    #   - page 1's TOTAL could pair with page 7's TOTAL, reporting a page offset as placement.
    # On the 208-row record 56 documents had under 90 % of their source runs matched, 23 under
    # 70 %, and 4 of the 21 that PASSED this check passed on less than half their runs.
    by_page = collections.defaultdict(lambda: collections.defaultdict(list))
    for j, c in enumerate(g_runs):
        by_page[c["page"]][norm_word(c["text"])].append(j)

    dys, dxs, matched = [], [], 0
    pairs = []
    used = set()

    def _split_span(r):
        """Unused render runs on r's page and baseline that join to r's text."""
        want = norm_word(r["text"])
        near = [j for j, c in enumerate(g_runs)
                if j not in used and c["page"] == r["page"]
                and abs(c["y"] - r["y"]) <= 1.0 and c["x"] >= r["x"] - 1.0]
        near.sort(key=lambda j: g_runs[j]["x"])
        for k0 in range(min(3, len(near))):
            span = [near[k0]]
            joined = norm_word(g_runs[near[k0]]["text"])
            k = k0
            while joined != want and want.startswith(joined) and k + 1 < len(near):
                k += 1
                span.append(near[k])
                joined += norm_word(g_runs[near[k]]["text"])
            if joined == want:
                return span
        return []

    # ASSIGNMENT, not a per-source walk. Walking s_runs in document order and taking
    # each run's nearest unused candidate lets an EARLIER source run claim a render run
    # that belongs to a LATER one: the moment a source run's own counterpart is missing
    # (a merged span, a piece already consumed), it silently pairs with the next
    # occurrence of the same word on the page. Constructed 13 Nov: twelve rows reading
    # "0.00", the first row's label merged into its value so that one span no longer
    # matches - every one of the eleven pairs then reported dy = +30.0, the line pitch,
    # on a render whose every glyph was where the source put it, with 03, 04, 05 and 22
    # all clean. median dy 30.0 fails 18_median_dy outright.
    # Sorting all candidate pairs by distance and claiming in that order removes it: the
    # run whose counterpart did not move is always at distance 0 and is therefore
    # claimed before anything can steal it.
    cand = []
    for i, r in enumerate(s_runs):
        for j in by_page.get(r["page"], {}).get(norm_word(r["text"]), []):
            cand.append((abs(g_runs[j]["y"] - r["y"]) + abs(g_runs[j]["x"] - r["x"]), i, j))
    cand.sort()
    taken = {}
    for d, i, j in cand:
        if i in taken or j in used:
            continue
        taken[i] = j
        used.add(j)
    # Split spans are joined only for what the exact pass left over, so a piece of a
    # split span can no longer be eaten by an earlier source run before the join runs.
    for i, r in enumerate(s_runs):
        if i in taken:
            continue
        span = _split_span(r)
        if not span:
            continue
        for j in span:
            used.add(j)
        taken[i] = min(span, key=lambda j: abs(g_runs[j]["y"] - r["y"]) +
                                         abs(g_runs[j]["x"] - r["x"]))
    for i, r in enumerate(s_runs):
        if i not in taken:
            continue
        j = taken[i]
        dys.append(g_runs[j]["y"] - r["y"])
        dxs.append(g_runs[j]["x"] - r["x"])
        matched += 1
        pairs.append((r, g_runs[j]))

    def median(v):
        if not v:
            return 0.0
        v = sorted(v)
        n = len(v)
        return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2

    med_dy = round(median(dys), 1)
    worst_dy = round(max((abs(d) for d in dys), default=0), 1)
    med_dx = round(median(dxs), 1)

    # ceil, not int: int(2 * 0.9) is 1, so a two-run document passed on one match. The stated
    # rule is 90 % and a floor of the product is not 90 %.
    checks["17_matched_runs"] = (len(s_runs), matched,
                                 matched >= -(-len(s_runs) * 9 // 10))
    # ---- 18: the displacement standard --------------------------------------
    #
    # Three checks used to ask this question and gave three answers: 18 failed at 4 pt, 20
    # tolerated 10, 19 tolerated 15. This is one standard, and it is the only one of the three
    # calibrated against what a user SEES rather than against a round number. Measured on
    # rendered pages: 2 pt 3.4 % ink contact, 3 pt 5.3 % (the knee), 4 pt 15.8 %, 10 pt 59.7 %
    # (text printed on text), 15 pt 71.7 % with 46 % of lines inverting reading order.
    #
    # 18 as it stood was a POOLED MEDIAN against a fixed 3 pt, and a median is a majority rule:
    # 10 of 21 lines 20 pt out reads 0.0 and PASSED, and so did 9 of 10 pages 20 pt low. Judging
    # each page's median instead of the document's changes nothing on either case - the worst
    # page's median is that same 0.0 - so a per-page-then-median rewrite is not a fix, it is the
    # same majority rule wearing a page loop. Constructed and measured 13 Nov; it passes both.
    #
    # What is here instead:
    #     tolerance = clamp(0.35 * size, 1.5, 4.5) pt   -- 0.35 em, floored and capped, because
    #                                                   3 pt is 0.4 em at 7.4 pt type and 0.2 em
    #                                                   at 15 pt, so a fixed band means a
    #                                                   different thing at every size
    #     a page fails when n_out > max(2, ceil(0.05 * n)) on THAT PAGE, or when every run on
    #     the page is out (a page moved as a block, however few runs it carries)
    # Counting runs rather than averaging them is what makes it honest about a whole page
    # instead of a majority: ten lines out of twenty-one is 48 % and fails.
    #
    # The budget is per page, NOT per document. A document-wide 5 % budget is a ruler for
    # document length - it was measured here: one page of 20 runs moved 20 pt passes at 20 pages
    # (400 runs) and fails at 10 pages (200 runs), so the same fault is a defect in a short
    # document and not in a long one. That is the exact failure mode 20 was rewritten to remove
    # ("a share of a document is a ruler for its length"), and it is not reintroduced here.
    #
    # Rotated and curved text is excluded: on those runs dy is not a displacement, and
    # 05_round_company_seal_curved_text has 59 of 83 runs that way. That is 35_rotation's
    # question. An empty page stays a failure - the old rule passed a render with no text layer
    # at all (15_stamp_on_scanned_page) by scoring 0 of 0.
    #
        # IT ABSORBS 19_worst_dy. 19 was not a second question: it was max() of the same list this
    # check counts, taken over a WIDER population (every matched pair, including the rotated runs
    # excluded two paragraphs up), against a fixed 15 pt. Measured on 208 recorded documents
    # (RESULTS.jsonl, engine 2a68de6): 160 failed both and 13 failed 19 alone, and of those 13 a
    # lower bound on n_out already exceeds the per-page budget on 11 - so 19's own unique class
    # was at most 2 documents, both the one-catastrophic-run shape 361_product_catalogue_grid has.
    # Keeping it as a second check bought those two and charged every one of the 160 a second
    # point for one fault. Its clause is kept, inside this check, and its threshold is tied to
    # this check's own tolerance instead of to a number from a different standard.
    #
    # The pair also left a HOLE, which is the part that was never a question of taste. 18's count
    # budget absorbs one stray run and 19 did not look below 15 pt, so a single run 4.6 pt out and
    # a single run 14.9 pt out were caught by NEITHER (constructed, both, /scratch/work/matrix.py).
    # One standard cannot leave a band of the thing it measures unjudged: a run more than
    # TAIL_FACTOR of its own tolerance out is a displaced page whatever the budget says.
    #
    # 19's rounding went with it: it compared round(max|dy|, 1) against 15.0, so 14.96 pt failed
    # and 14.90 pt passed - a threshold at 14.95 that no comment in the file ever claimed.
    flat = set()
    for i, p in enumerate(src):
        for blk in p.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                if abs(ln.get("dir", (1, 0))[1]) > 0.02:
                    continue
                for sp in ln.get("spans", []):
                    if sp.get("text", "").strip():
                        flat.add((i, round(sp["bbox"][1], 2), sp["text"]))

    def _tol(size):
        return min(max(0.35 * size, 1.5), 4.5)

    # The tail clause. It replaces 19_worst_dy, which asked the same question of the same
    # list at a fixed 15 pt and so left the band between this check's cap (4.5 pt) and its
    # own threshold unjudged for every run the budget forgives.
    TAIL_FACTOR = 2.0
    bad_pages = []
    for pg in sorted(set(r["page"] for r in s_runs)):
        flat_src = [r for r in s_runs
                    if r["page"] == pg and (r["page"], r["y"], r["text"]) in flat]
        ds = [(g["y"] - r["y"], r["size"]) for r, g in pairs
              if r["page"] == pg and (r["page"], r["y"], r["text"]) in flat]
        # No upright run on the page is not the same as no text on the page. A page whose
        # every line is rotated or curved lands here with ds empty, and it used to be scored
        # as a displaced page: constructed, a fully rotated page against ITSELF failed this
        # check while 19 read 0.0. Those runs are 35_rotation's question.
        if not flat_src:
            continue
        # Upright text on the page and none of it matched: the render lost the page. That is
        # still a failure here - 15_stamp_on_scanned_page was passed by a render with no text
        # layer at all when this scored 0 of 0.
        if not ds:
            bad_pages.append(pg)
            continue
        n_out = sum(1 for d, sz in ds if abs(d) > _tol(sz))
        # The 2-run grace is for STRAY runs, so it may not swallow a page that has been moved
        # as a block: a two-run page shifted 12 pt is n_out == n == 2, and a bare
        # max(2, ...) passed it. Everything out is a displaced page whatever its run count.
        worst_here = max(abs(d) / _tol(sz) for d, sz in ds)
        if (n_out > max(2, -(-len(ds) * 5 // 100)) or n_out == len(ds)
                or worst_here > TAIL_FACTOR):
            bad_pages.append(pg)
    checks["18_displacement"] = (0, len(bad_pages), not bad_pages)
    checks["21_median_dx"] = (0, med_dx, abs(med_dx) < 3.0)

    # reading order: the sequence of normalised words
    s_seq = [norm_word(w) for w in s_text.split() if w.strip()]
    g_seq = [norm_word(w) for w in g_text.split() if w.strip()]
    order = order_score(s_seq, g_seq)
    checks["22_reading_order"] = (100, order, order > 95)

    # line spacing: median gap between consecutive baselines on page 1
    def pitch(doc):
        """Line pitch, measured page by page and then taken as a median.

        This pooled every run's y into ONE sorted set across all pages. Two pages each at a
        true 12 pt pitch, where page 2 simply starts 6 pt lower than page 1, then measured 6.0
        - the gap between page 1's last baseline and page 2's first was one of the gaps in the
        set. Measured on 13 Nov: pitch(page 1) = 12, pitch(page 2) = 12, pitch(all runs) = 6,
        so a document whose every page was correct FAILED whenever the two sides' pages started
        at different offsets - which is what 18_median_dy reports on this corpus.
        Per page, then the median across pages: a page break is not a line gap.
        """
        per_page = []
        for p in doc:
            ys = sorted(set(round(r["y"], 1) for r in runs(p)))
            gaps = [b - a for a, b in zip(ys, ys[1:]) if 1 < b - a < 200]
            if gaps:
                per_page.append(median(gaps))
        return round(median(per_page), 1) if per_page else 0
    s_p, g_p = pitch(src), pitch(gd)
    checks["23_line_pitch"] = (s_p, g_p, s_p == 0 or abs(g_p - s_p) <= 2.0)

    checks["24_page_breaks"] = (src.page_count, gd.page_count,
                                src.page_count == gd.page_count)

    # ---- VISUAL (25-31) -----------------------------------------------------
    s_invisible, s_off_page = _visual_counts(src)
    s_clipped = _clipped_count(src)
    invisible, off_page = _visual_counts(gd)

    on_text, clipped = 0, 0
    for p in gd:
        W, H = p.rect.width, p.rect.height
        rs = runs(p)
        for r in rs:
            # 26 text boxes overlapping other text
            for o in rs:
                if o is r:
                    continue
                if (r["x"] < o["x1"] - 1 and r["x1"] > o["x"] + 1 and
                        r["y"] < o["y1"] - 1 and r["y1"] > o["y"] + 1):
                    on_text += 1
                    break
            # 31 text clipped at the edge
            if r["x"] < 1 or r["x1"] > W - 1:
                clipped += 1

    # 25 and 27 compare the render against the source. Text that was already
    # invisible, or already off the page, is the document's own shape, and a
    # faithful conversion reproduces it.
    checks["25_invisible_text"] = (s_invisible, invisible, invisible <= s_invisible)
    # 26 compares the RENDER against the SOURCE, not against zero. A stamp printed
    # over a line of text is text-on-text in the original, and a perfect conversion
    # reproduces it - so counting absolute overlaps failed a document against
    # itself (57/58 on a self-comparison). Only overlaps the source did not have
    # are a defect.
    s_on_text = 0
    for p in src:
        rs = runs(p)
        for r in rs:
            for o in rs:
                if o is r:
                    continue
                if (r["x"] < o["x1"] - 1 and r["x1"] > o["x"] + 1 and
                        r["y"] < o["y1"] - 1 and r["y1"] > o["y"] + 1):
                    s_on_text += 1
                    break
    checks["26_text_overlap"] = (s_on_text, on_text,
                                 on_text <= max(s_on_text, 2, len(g_runs) // 50))
    checks["27_text_off_page"] = (s_off_page, off_page, off_page <= s_off_page)
    # The render may not clip MORE than the source already did. A document whose own text
    # sits at the page edge is not a defect; text that only the conversion pushed there is.
    # Same rule as 25 and 27.
    checks["28_clipped_at_edge"] = (s_clipped, clipped,
                                    clipped <= max(2, s_clipped + len(g_runs) // 50))

    # 29 blank where source has ink / 30 ink where source is blank
    # CORRECTION (13 Nov): bucket the RENDER in the SOURCE's frame. med_dx / med_dy are
    # the document-wide median offsets of the matched runs above - the amount the whole
    # document was translated. Subtracting them before bucketing means a uniform shift
    # lands in the cells the source itself used, so only cells whose occupancy really
    # changed are counted. Without it a 2.5 pt shift walks runs across the 24x24 lattice
    # boundaries and BOTH checks fire on a document whose text is intact: measured on
    # 12 real documents, a 2.5 pt horizontal shift failed 29 on 3 and 30 on 2, with
    # 18/19/20/21 all passing; at 5 pt it failed 29 and 30 on 7 of 12.
    # With no matched runs both medians are 0.0 and this is exactly the old behaviour.
    # Per PAGE, not per document. A whole-document median is right when the whole
    # document moved, but it cannot see a shift that only one page carries (the median
    # of a three-page document with page 2 displaced stays 0, so the correction does
    # nothing: measured, page 2 of table-across-page-break-repeated-header shifted 10 pt
    # still reported 29=52 30=49). On a single-page document this is the same number as
    # med_dx / med_dy, so it strictly dominates.
    pdx, pdy = {}, {}
    for _pg in sorted({r["page"] for r, _ in pairs}):
        _xs = [g["x"] - s["x"] for s, g in pairs if s["page"] == _pg]
        _ys = [g["y"] - s["y"] for s, g in pairs if s["page"] == _pg]
        if _xs:
            pdx[_pg] = round(median(_xs), 1)
            pdy[_pg] = round(median(_ys), 1)
    blank_loss, extra_ink, s_grid_total = 0, 0, 0
    for i in range(min(src.page_count, gd.page_count)):
        sp, gp = src[i], gd[i]
        W, H = sp.rect.width, sp.rect.height
        GRID = 24
        cw, ch = W / GRID, H / GRID
        s_cells = set()
        for r in runs(sp):
            s_cells.add((int(r["x"] / cw), int(r["y"] / ch)))
        g_cells = set()
        for r in runs(gp):
            g_cells.add((int((r["x"] - pdx.get(i, med_dx)) / cw),
                         int((r["y"] - pdy.get(i, med_dy)) / ch)))
        s_grid_total += len(s_cells)
        blank_loss += len(s_cells - g_cells)
        extra_ink += len(g_cells - s_cells)
    # tolerance is a fraction of the source's own occupied grid cells, not of its columns
    s_cells_total = max(1, s_grid_total)
    checks["29_blank_where_ink_was"] = (0, blank_loss, blank_loss <= max(4, int(s_cells_total * 0.10)))
    checks["30_ink_where_blank_was"] = (0, extra_ink, extra_ink <= max(4, int(s_cells_total * 0.10)))

    # 31 every page must carry some ink
    # A blank page in the source is legitimate; a blank page the source did not have is not.
    # The source column was the literal 0 on all 211 documents, so every report of this
    # check read "source=0" and DEFECT-CLASSES.md scored the class at 0 % pass for a check
    # that fires on one document. It now carries the number of source pages that have text -
    # the denominator the count is out of. The verdict is untouched: it still reads only
    # empty_pages, so no document moves.
    empty_pages = 0
    text_pages = 0
    for i in range(gd.page_count):
        g_has = bool(gd[i].get_text().strip())
        s_has = bool(src[i].get_text().strip()) if i < src.page_count else False
        if s_has:
            text_pages += 1
        if s_has and not g_has:
            empty_pages += 1
    checks["31_pages_lost_their_text"] = (text_pages, empty_pages, empty_pages == 0)

    checks.update(extra_checks(src, gd, s_runs, g_runs, pairs))
    checks.update(extra_checks2(src, gd, docx_path))

    src.close()
    gd.close()

    failed = [k for k, v in checks.items() if not v[2]]
    return {
        "source": src_path,
        "render": gd_path,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": sorted(failed),
        "ok": not failed,
        "checks": {k: {"source": v[0], "render": v[1], "ok": bool(v[2])}
                   for k, v in sorted(checks.items())},
    }


def all_check_ids():
    """Every check id this verifier knows, discovered by running it on two empty
    documents. Nothing is hard-coded, so adding a check updates the universe
    automatically and a stale list cannot silently hide a regression."""
    import tempfile
    d = tempfile.mkdtemp(prefix="ids-")
    a = os.path.join(d, "a.pdf")
    b = os.path.join(d, "b.pdf")
    for path in (a, b):
        doc = fitz.open()
        doc.new_page()
        doc.save(path)
        doc.close()
    return sorted(compare(a, b)["checks"])


def main(argv):
    if "--list-checks" in argv:
        for cid in all_check_ids():
            print(cid)
        return 0
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, gd = argv[1], argv[2]
    out = None
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
    # The .docx the engine wrote, when the caller has it. The pipeline keeps it beside the
    # source (out1/<name>.docx next to all/<name>.pdf), so it is looked for there too;
    # without it 54_image_dpi cannot be answered and says so rather than failing.
    docx_path = None
    if "--docx" in argv:
        docx_path = argv[argv.index("--docx") + 1]
    else:
        stem = os.path.splitext(os.path.basename(src))[0]
        for cand in (os.path.join(os.path.dirname(src), "..", "out1", stem + ".docx"),
                     os.path.join(os.path.dirname(src), stem + ".docx")):
            if os.path.exists(cand):
                docx_path = cand
                break
    try:
        res = compare(src, gd, docx_path)
    except Exception as e:
        print("could not run: %s" % e, file=sys.stderr)
        return 2

    print("%-38s %d/%d %s" % (
        src.split("/")[-1][:38], res["passed"], res["total"],
        "PASS" if res["ok"] else "FAIL"))
    if res["failed"]:
        for k in res["failed"]:
            c = res["checks"][k]
            print("    %-28s source=%-8s render=%-8s" % (k, c["source"], c["render"]))
    if out:
        # The run may be told to write into a directory it has not made yet - that is
        # exactly how the .txt half measured nothing for a whole day: restxt/ never existed,
        # so this line raised FileNotFoundError on every document and the half stayed empty.
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

        with open(out, "w") as f:
            res["document"] = os.path.splitext(os.path.basename(src))[0]
            res["source_file"] = src
            res["render_file"] = gd
            json.dump(res, f, indent=2)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
