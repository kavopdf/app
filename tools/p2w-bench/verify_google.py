#!/usr/bin/env python3
"""
verify_google.py - compare a Google-Docs-rendered PDF against the source PDF.

WHY THIS EXISTS
  Every earlier instrument lied. gate.py scores words, blocks, overflow, lines and
  pages, and none of those move when w:framePr is ignored or a header band lands at
  the wrong y. verify_visual.py renders through LibreOffice, which honours constructs
  Google Docs does not, so it hides exactly the faults the phone shows. NOTE (13 Nov): the
  pipeline in PIPELINE.md step 6 renders with `soffice --headless`, so EVERY number this file
  produces today is LibreOffice's, not Google's. The two are NOT comparable - a 211-document
  round measured engine +230, instrument -1833 and renderer +1634 of the same total. Three separate
  fixes shipped "clean" and broke on the device.

  This one compares the PDF that Google Docs itself exports. If a word lands at the
  left margin in Docs, it lands there in this export too.

USAGE
  python3 verify_google.py <source.pdf> <google-export.pdf> [--docx <engine.docx>] [--json out.json]

  --docx is REQUIRED for a document whose source draws a raster picture. 54_image_dpi reads
  the engine's resolution decision out of the .docx, and there is no other place it is
  observable. Without a readable .docx it FAILS rather than passes: a check that returns
  ok=True having measured nothing is a vote that can never be cast, and it used to hide a
  real resolution loss on every document in the corpus. When the source draws no picture
  there is nothing to measure, and that pass is genuine.

  53_embedded_faces has the same defect and still passes unmeasured. It is not fixed here
  because two cases in test_checks.py rely on that pass; the one-line change is recorded in
  the round's patch notes.

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
import os, sys, json, re, bisect, collections, statistics, difflib, math, zipfile, unicodedata
import xml.etree.ElementTree as ET

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
_CTRL = set(chr(_i) for _i in range(0, 32))


def ink_box(sp, ln):
    """(x0, x1) of the glyphs in this span that put ink on the page.

    A span's bbox starts at its first glyph's ORIGIN - the pen - and a space advances the
    pen without drawing anything. A source that writes "    (a) Salary" reports a left
    edge 8 pt left of the first thing a reader can see, and a renderer that drops the
    leading spaces (all of them do) is charged for the difference. The reader sees ink,
    so the measurement is taken at the ink: min/max over the glyph boxes that are not
    whitespace and not the C0 controls producers use as padding. min/max, not
    first/last, because on a 180-degree run the character order runs right to left.

    Falls back to the span's own box when the producer recorded no glyph boxes.
    """
    chars = sp.get("chars")
    if chars is None:
        chars = [c for s in ln.get("spans", []) for c in s.get("chars", [])]
    ink = [c for c in chars
           if c.get("c", "") not in _CTRL and not c.get("c", "").isspace()
           and c["bbox"][2] - c["bbox"][0] > 0.01]
    if not ink:
        return sp["bbox"][0], sp["bbox"][2]
    return min(c["bbox"][0] for c in ink), max(c["bbox"][2] for c in ink)


def reading_frame(angle_deg, w, h, mirrored=False):
    """The basis of a run's READING frame, for a page w x h and a baseline angle.

    WHY THIS EXISTS. Every geometric check in this file compared a source run's device
    bbox against a render run's device bbox. That is only meaningful when both pages are
    drawn the same way up. They are not: the engine writes an UPRIGHT .docx from a page
    whose text layer is rotated, so the render of `one-page-rotated-180-degrees` page 2
    comes back with dir=(1,0) while the source page 2 has dir=(-1,0) on every one of its
    61 lines. The comparison then subtracts two coordinate systems that differ by a 180
    degree rotation about the page centre, and the residue is a full page height: worst
    |dy| 791 pt on that page, 0 of 61 runs within 10 pt in x, on a page the engine
    reproduced faithfully. 18_displacement and 43_within_10pt_x both charged it.

    The fix is to compare in READING space, derived from each LINE's own dir - the space
    in which a reader sees the text, whatever way up the producer drew it. The frame is
    the baseline direction d=(cos a, sin a) and its perpendicular p=(-dy, dx), taken about
    the page centre so that a rotation about the centre is undone rather than translated:

        rx = (x-cx)*dx + (y-cy)*dy        along the baseline, increasing rightwards
        ry = (x-cx)*px + (y-cy)*py        across it, increasing downwards

    For an upright line (a=0) this is rx=x-cx, ry=y-cy: a constant shift that cancels in
    every difference, so NOTHING changes for an upright document. For a 180-degree line
    (a=180) it is rx=cx-x, ry=cy-y: the rotation undone. The perpendicular points "down" in
    reading terms, so ry grows the way a reader's eye travels down the page, and dy is a
    displacement rather than a page height.

    ONLY A HORIZONTAL BASELINE IS PROJECTED. A reading frame is the space in which a reader
    reads a LINE, and that is only well defined when the line is level: upright or upside
    down (|sin a| <= 0.02). A curved seal - 05_round_company_seal_curved_text, and the
    ~24 rotated glyphs on each of 312/318/352/371/305/60 - draws every glyph at its own
    angle, so there is no single frame its x is comparable in; runs() already says as much
    about 47. Projecting those made 43 charge the curvature as horizontal displacement
    (05 read 99 -> 76, 352 read 100 -> 46) and collapsed their pairing (05 matched 79 -> 37).
    A slanted line therefore keeps its DEVICE frame (the identity), which is exactly what
    every check read before this change - so those documents do not move at all.

    A 90/270 degree line is deliberately NOT projected either: undoing it needs the page's
    width and height swapped, and no corpus page in this run turns a whole page by a
    quarter turn. That residual is recorded in the round's write-up, not papered over.
    """
    # A MIRRORED LINE IS NOT A ROTATED ONE. dir=(-1,0) is what a reflection and a 180-degree
    # rotation BOTH report, and a rotation cannot undo a reflection - undoing it needs a
    # flip, which is not an angle. 417_rotate180_and_mirrored page 2 is drawn under
    # "-1 0 0 1 595 0 cm" (det = -1); projecting it as a rotation took its 43 from 100 to 50.
    # page_mirrors_text() reads the page's CTM and says which it is, so a mirrored page keeps
    # the zero-rotation frame and reads exactly as it did before this change.
    a = math.radians(angle_deg)
    if mirrored or abs(math.sin(a)) > 0.02:
        # Slanted: zero ROTATION, but still about the page centre - NOT a bare identity.
        # The origin must be the same one every other line on the page uses, or a document
        # that mixes a curved seal with upright body text compares a device x against a
        # centred x and reads the page centre (297 pt) as a displacement. Zero rotation about
        # the centre is rx=x-cx, ry=y-cy, which cancels in every difference exactly as the
        # old device comparison did.
        return (w / 2.0, h / 2.0, 1.0, 0.0, 0.0, 1.0)
    # SNAP a level line to an exact 0 or exact 180. A line the extractor reports at 0.05
    # degrees would otherwise get a frame tilted by that much, and because the tilt term is
    # (y-cy)*sin, two lines at different heights shift by different sub-pt amounts - enough
    # to walk a line across 42_justification_edges' 1 pt bucket (newsletter-3col-header-footer
    # read 0 -> 6 contradicted pairs on that alone). A level baseline is level; the snap is
    # what the old device comparison did implicitly.
    sgn = -1.0 if math.cos(a) < 0 else 1.0
    return (w / 2.0, h / 2.0, sgn, 0.0, 0.0, sgn)


def rproj(x, y, fr):
    """(rx, ry) of a device point in the reading frame `fr` from reading_frame()."""
    cx, cy, dx, dy, px, py = fr
    vx, vy = x - cx, y - cy
    return (vx * dx + vy * dy, vx * px + vy * py)


def page_reading_frame(page):
    """The baseline orientation a reader reads this PAGE in: 0.0 or 180.0 degrees.

    A page is read in ONE orientation, and that is the frame every line on it belongs to.
    Projecting each LINE by its own dir is right when the page is uniformly rotated - the
    case that matters - because then every line agrees and the page frame IS each line's
    own dir. On a page that is upright except for a rotated stamp or a rotated contact
    block, per-line projection compares that block against a render that CANNOT DRAW
    ROTATION AT ALL: `soffice --headless` emits zero non-level lines on all 211 documents
    (measured; see the 35_rotation note above), so the render always puts a rotated block
    upright at its DEVICE position. Charging it in reading space therefore measures
    LibreOffice, not the engine. Measured on the corpus, strict per-line projection flipped
    04_stamp_180deg_upside_down (18 - and 35_rotation already fails that document on the
    same lost stamp, so it was a DOUBLE charge) and 401_trifold_brochure (18 and 43 - where
    35_rotation PASSES, because the .docx does carry the rotation and only the renderer
    drops it).

    So the frame is the page's DOMINANT level orientation. A page whose text is mostly
    slanted - a curved seal - gets 0, the device frame, for the same reason runs() already
    refuses to project slanted lines.
    """
    c0 = c180 = cs = 0
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            if not ln.get("spans"):
                continue
            dx, dy = ln.get("dir", (1, 0))[:2]
            if abs(dy) > 0.02:
                cs += 1
            elif dx < 0:
                c180 += 1
            else:
                c0 += 1
    if cs >= max(c0, c180):
        return 0.0
    return 180.0 if c180 > c0 else 0.0


def runs(page, page_no=0, mirrored=False, page_angle=None):
    """Every text span on a page, with the attributes we compare."""
    out = []
    pw, ph = page.rect.width, page.rect.height
    for blk in page.get_text("rawdict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                t = (sp.get("text", "")
                     or "".join(c.get("c", "") for c in sp.get("chars", [])))
                if not t.strip():
                    continue
                ix0, ix1 = ink_box(sp, ln)
                ang = round(math.degrees(math.atan2(ln.get("dir", (1, 0))[1],
                                                    ln.get("dir", (1, 0))[0])), 1)
                fr = reading_frame(page_angle if page_angle is not None else ang,
                                   pw, ph, mirrored)
                b = sp["bbox"]
                # THE BASELINE ORIGIN, not the bbox, is the point that transforms exactly.
                # PyMuPDF's span bbox anchors the font's ascent/descent in the UNROTATED
                # frame, so on a 180-degree line the box it reports is not the geometric
                # image of the upright box: measured on a page against its own exact 180
                # (content wrapped in `-1 0 0 -1 W H cm`), the bbox came back 6.07 pt off
                # while the origin came back to 0.001 pt. A displacement is a property of
                # the baseline, so the baseline is what is projected: ry is where the line
                # sits across the reading direction, and the ink extents give its span
                # along it (device x is exact under any multiple of 90 degrees).
                #
                # The reading-space TOP is the origin projected, minus the ascent, where the
                # ascent is measured in device space as (origin - bbox_top) - a quantity
                # PyMuPDF reports the same way for a level line whichever way up it is
                # drawn (measured: 8.535 pt upright, 8.534 pt on the exact 180). That makes
                # ry EXACT for a 180-degree line and IDENTICAL to the old bbox top for an
                # upright one (ry = y - cy), so upright documents do not move.
                ox, oy = sp.get("origin", (b[0], b[3]))
                ascent = oy - b[1]
                ryb = rproj(ox, oy, fr)[1] - ascent
                xa = rproj(b[0], oy, fr)[0]
                xb = rproj(b[2], oy, fr)[0]
                rxbox, rx1box = min(xa, xb), max(xa, xb)
                i0 = rproj(ix0, oy, fr)[0]
                i1 = rproj(ix1, oy, fr)[0]
                rxink, rx1ink = min(i0, i1), max(i0, i1)
                out.append({
                    "page": page_no,
                    "text": t,
                    "x": round(sp["bbox"][0], 2),
                    "xink": round(ix0, 2),
                    "x1ink": round(ix1, 2),
                    "y": round(sp["bbox"][1], 2),
                    "x1": round(sp["bbox"][2], 2),
                    "y1": round(sp["bbox"][3], 2),
                    # READING SPACE. The same box and ink box projected through this line's
                    # own dir (reading_frame above). The position family - the pair matcher,
                    # 18, 34, 43 and 42 - reads THESE, so a rotated page compares against an
                    # upright render the way a reader reads it. The device fields above are
                    # kept for the checks that are genuinely about the sheet of paper (44
                    # bands, 46 strokes, 59 anchors, 60 column edge, 47 margins), which
                    # exclude rotated runs rather than project them.
                    "rx": round(rxbox, 2),
                    "rx1": round(rx1box, 2),
                    "ry": round(ryb, 2),
                    "ry1": round(ryb + (b[3] - b[1]), 2),
                    "rxink": round(rxink, 2),
                    "rx1ink": round(rx1ink, 2),
                    "ox": ox,
                    "oy": oy,
                    "fr": fr,
                    # THE BASELINE'S OWN DIRECTION. 47 is a left-edge statistic, and a
                    # left edge is only an edge on a baseline that runs left to right:
                    # on a curved seal every glyph has its own angle and its own origin,
                    # so its x is not comparable with another run's. 18_displacement has
                    # always restricted itself to UPRIGHT runs for exactly this reason;
                    # 47 never recorded the angle and could not. Recorded here, once.
                    "angle": ang,
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


# face_name() stood here and was the whole of 09_font_names' normaliser: it stripped the
# style word, the MT/PSMT/PS suffix and the comma form off a face name so that five style
# variants of one family read as one family. It had exactly one caller, and that caller is
# gone. Its history is kept where the check used to be (see "09_font_names RETIRED"), and
# 53 does the same reduction inside family(), which is also the only place that needs it.


def _torn_lines(s_text, g_text):
    """Lines whose second half reappears elsewhere in the render.

    A line is torn when its first words and its last words both occur in the render but no
    single render line contains them together. That is what a reader sees as broken order;
    everything else the LCS rule counted was two extractors disagreeing about a table's
    cell order, which is a property of the producer's drawing sequence, not of the document.
    """
    s_lines = [ln for ln in s_text.split("\n") if ln.strip()]
    g_lines = [ln.strip() for ln in g_text.split("\n") if ln.strip()]
    if not s_lines or not g_lines:
        return []
    g_joined = "\n".join(g_lines)
    torn = []
    for ln in s_lines:
        words = [norm_word(w) for w in ln.split() if w.strip()]
        if len(words) < 4:
            continue
        head, tail = " ".join(words[:2]), " ".join(words[-2:])
        if head not in g_joined or tail not in g_joined:
            continue
        if any(head in g_ln and tail in g_ln for g_ln in g_lines):
            continue
        torn.append(ln.strip())
    return torn



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


def is_blackish(v):
    """Is this int a BLACK, in the sense the black-point rule above uses?

    Neutral (chroma <= 12) and dark (L* <= 13). Used by 13's GAIN clause only: an
    Automatic run resolves to whatever black the reader paints, and that black need not be
    the source's black int. D-23 keeps `w:color` off the run and leaves it on Automatic for
    exactly that reason, so a render carrying #000000 where the source drew #1C1C1C is the
    same text colour written down twice, not an invented colour.
    """
    L, a, b = _lab(_rgb01(v))
    return L <= BLACK_L and math.hypot(a, b) <= BLACK_C


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
# URL identity - the normalised form a link target must be compared in
# ----------------------------------------------------------------------------
# 40_link_targets compared two sets of URI STRINGS with `==`. A URI is not a byte
# string: it reaches this comparison through a docx relationship and a LibreOffice
# PDF export, so one target can arrive spelled differently. Constructed 13 Nov,
# 44_coloured_underlined_hyperlinks as the source, ONE link changed and four
# untouched - before this helper, four of the seven rows below were failures:
#
#   render's change to link 1                40 before   40 after
#   (none)                                   pass        pass
#   trailing "/" added to the path           FAIL        pass
#   percent-encoded "-" in the path          FAIL        pass
#   fragment "#section2" added               FAIL        pass
#   host lowercased to mixed case            FAIL        pass
#   default port :443 added                  FAIL        pass
#   scheme rewritten https -> http           FAIL        FAIL   (deliberate)
#   target changed to wrong.invalid          FAIL        FAIL
#
# This is the same defect shape as 13_text_colours' exact int equality, which
# colour_same() replaced, and 36_underline_rules' too-wide rule match: a
# comparison that is too literal.
#
# WHAT IS FOLDED is what RFC 3986 6.2.2-6.2.3 calls an equivalent REPRESENTATION
# of one URI: case of scheme and host, a default port, the percent-encoding of an
# UNRESERVED character, and an empty path against "/". Two further folds are
# DELIBERATE EXCEPTIONS, named because they are what a docx round trip produces:
# one trailing "/", and the fragment. RFC 3986 does not declare /a and /a/
# equivalent, so that fold is a product decision, not a reading of the spec - it
# is a constant here so it can be turned off.
#
# WHAT IS NOT FOLDED: the scheme. http://x and https://x can serve different
# resources, and a converter that rewrites a scheme has changed the link - that is
# a real defect and 40 must keep catching it. One constant, if that is ever wrong.
from urllib.parse import urlsplit, urlunsplit

URL_FOLD_TRAILING_SLASH = True
URL_FOLD_FRAGMENT = True
URL_FOLD_SCHEME = False           # True would merge http:// and https://

_UNRESERVED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_DEFAULT_PORTS = {"http": "80", "https": "443", "ftp": "21"}


def _pct_decode_unreserved(s):
    """Decode %XX only where the octet is an UNRESERVED character (RFC 3986 6.2.2.2).
    %2F is left alone: decoding it would turn one path segment into two."""
    out = []
    i = 0
    while i < len(s):
        if (s[i] == "%" and i + 2 < len(s)
                and all(c in "0123456789abcdefABCDEF" for c in s[i + 1:i + 3])):
            ch = chr(int(s[i + 1:i + 3], 16))
            out.append(ch if ch in _UNRESERVED else s[i:i + 3].upper())
            i += 3
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def url_key(u):
    """The normalised identity of a link target. Not a resolver, and not a fetcher:
    it never touches the network and never claims a URL is reachable."""
    if u is None:
        return None
    s = u.strip()
    if not s:
        return None
    try:
        parts = urlsplit(s)
        scheme = parts.scheme.lower()
        if URL_FOLD_SCHEME and scheme in ("http", "https"):
            scheme = "https"
        host = parts.hostname or ""
        port = parts.port
        if port is not None and _DEFAULT_PORTS.get(scheme) == str(port):
            port = None
        netloc = host + (":%d" % port if port is not None else "")
        if parts.username:
            cred = parts.username
            if parts.password:
                cred += ":" + parts.password
            netloc = cred + "@" + netloc
        path = _pct_decode_unreserved(parts.path)
        if not path:
            path = "/"
        elif URL_FOLD_TRAILING_SLASH and len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/") or "/"
        query = _pct_decode_unreserved(parts.query)
        frag = "" if URL_FOLD_FRAGMENT else _pct_decode_unreserved(parts.fragment)
        return urlunsplit((scheme, netloc, path, query, frag))
    except Exception:
        # An unparseable URI is compared as written. Better a literal comparison on
        # one odd target than a crash that reports nothing for the whole document.
        return s



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
    # THE FACE IS THE NEXT RULE THAT ACTUALLY CLOSES A BOX, not the next rule in y.
    # `zip(hs, hs[1:])` tested only y-ADJACENT pairs, so ONE extra hairline landing
    # between a band's two rules destroyed the face those two rules still draw: the
    # pair (a, b) was never tested, and (a, extra) / (extra, b) have no vertical rule
    # standing at their ends. Measured on 330_cad_drawing_sheet: the engine gained the
    # page's own 380x0.4 pt rule at y 430.05 (a rule the source draws and the old
    # shape pass dropped), it fell between the revision table's band edges at 417.6
    # and 430.6, and the face (21.0, 417.6, 255.4, 430.6) - the box four runs were
    # anchored to - was no longer assembled. Their enclosing box became the sheet
    # border, dx/dy jumped to 11.1/407.7, and 5 of 40 judged runs on that page were
    # scored `moved` against a budget of 2. Nothing on the page moved: the text is
    # unmoved (18_displacement passes), and both band rules are in the render at the
    # same coordinates. That is the tool talking, and the fix is to test the pair
    # that closes rather than the pair that is adjacent.
    for i, a in enumerate(hs):
        for b in hs[i + 1:]:
            if b.y0 - a.y0 < 8:
                continue
            if b.y0 - a.y0 > FACE_MAX_H:
                break
            x0, x1 = min(a.x0, b.x0), max(a.x1, b.x1)
            if x1 - x0 < 8:
                continue
            if (any(abs(v.x0 - x0) <= 2 and v.y0 <= a.y0 + 2 and v.y1 >= b.y0 - 2 for v in vs)
                    and any(abs(v.x1 - x1) <= 2 and v.y0 <= a.y0 + 2 and v.y1 >= b.y0 - 2 for v in vs)):
                out.append(fitz.Rect(x0, a.y0, x1, b.y0))
                break
    try:
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                if r.width >= 8 and r.height >= 8:
                    out.append(r)
    except Exception:
        pass
    return out


def _size_buckets(shapes):
    """The size classes a page can express, bucketed at half the identity tolerance.

    Answering "does the other document have a box this size" for every shape on this
    one is the pairing test in _anchors, and a scan of the whole shape list per shape
    is quadratic on a page with 300 of them. Bucketing at ANCHOR_RECT_TOL / 2 makes it
    a nine-bucket lookup: two sizes within 2.0 pt cannot land more than one bucket
    apart, so the 3x3 neighbourhood around a shape's bucket holds every candidate.
    """
    b = collections.defaultdict(list)
    for sh in shapes:
        b[(int(round(sh.width / 2.0)), int(round(sh.height / 2.0)))].append(sh)
    return b


def _has_size(sh, buckets, tol=2.0):
    """Is there a shape in `buckets` of sh's size, within `tol` on both sides?"""
    w0, h0 = int(round(sh.width / 2.0)), int(round(sh.height / 2.0))
    for dw in (-1, 0, 1):
        for dh in (-1, 0, 1):
            for o in buckets.get((w0 + dw, h0 + dh), ()):
                if abs(o.width - sh.width) <= tol and abs(o.height - sh.height) <= tol:
                    return True
    return False


def _smallest_holding(shapes, cx, cy):
    """The smallest shape in `shapes` containing (cx, cy), ties broken by geometry.

    fitz.Rect is x0/y0/x1/y1, not x/y - the run dicts use x/y, which is what made
    this crash on its first run. A tie on AREA is broken by geometry, not by draw
    order: min() with a strict < kept whichever shape get_drawings() happened to
    yield first, and two producers need not agree on that order - the same defect
    47_margins had when statistics.mode returned the first of a tie. Constructed
    (break59.py M3b): two boxes of equal area both holding the text centre, drawn in
    the opposite order on the render side. Nothing moved and 59 failed the page.
    """
    best, best_key = None, None
    for sh in shapes:
        if sh.x0 <= cx <= sh.x1 and sh.y0 <= cy <= sh.y1:
            key = (sh.width * sh.height, sh.width, sh.height, sh.y0, sh.x0)
            if best_key is None or key < best_key:
                best, best_key = sh, key
    return best, best_key


def _anchors(page, rs, other_shapes=None):
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

    AND "SMALLEST" IS NOT THE SAME ANSWER FROM TWO PRODUCERS, which comparing the rect
    afterwards only half repairs. Which boxes a page has at all is the producer's
    choice, so the smallest box round a run can be a cell on one side and the row band
    or the table's whole frame on the other; 59 then measures dx from a different
    origin on each side and reads movement where none happened. When the other
    document's shapes are known, the pool is therefore restricted to boxes THAT
    DOCUMENT CAN ALSO EXPRESS - a box with no counterpart is not an object the two can
    be compared on. The restriction is a preference, not a filter: where no paired box
    holds the run, the unrestricted smallest is used and the run is judged exactly as
    before.

    This is a change of OBJECT, not of tolerance, and it is what makes dx mean what the
    check says it means. dx = (gx - gb.x0) - (sx - sb.x0) is the text's displacement
    only when gb and sb are the same box; on different boxes it is the displacement
    plus the distance between the two origins, which is the defect this check was
    written to report. Measured on the 56 documents that fail 59 at 23ffa25: of 1165
    judged runs, 249 were enclosed by a box the other side does not have (46 unjudged,
    203 scored `moved` only because a box of that size happened to exist elsewhere on
    the page). Pairing moves 127 of those 249 to `anchored`, moves 55 more to `moved`
    where they can now be judged in points, and leaves all 530 genuine `moved` runs
    `moved`.
    """
    shapes = _shapes(page)
    pool = shapes
    if other_shapes is not None:
        buckets = _size_buckets(other_shapes)
        paired = [sh for sh in shapes if _has_size(sh, buckets)]
        if paired:
            pool = paired
    out = []
    for r in rs:
        cx, cy = (r["x"] + r["x1"]) / 2.0, (r["y"] + r["y1"]) / 2.0
        best, best_key = _smallest_holding(pool, cx, cy)
        if best is None and pool is not shapes:
            best, best_key = _smallest_holding(shapes, cx, cy)
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
# A RULE IS A SEGMENT, NOT A DRAWING OBJECT (32_stroke_lines)
#
# The old 32 counted drawing objects: s_n on the source, g_n on the render, pass when
# g_n >= 0.8 * s_n. Measured on the 211-document corpus, that number is not a count of
# rules - it is 7,979 objects of which 1,653 are 2-D outlines (a 300x400 pt table
# outline is ONE "stroke line") and 1,948 are exactly 13.00 pt table-cell segments. On
# a table-heavy document s_n is a cell count. It is also blind to position, length,
# thickness and colour, so a rule lost on page 3 is paid for by a rule gained on
# page 1, and 20 % of a document's rules can vanish inside the floor for free.
#
# A rule here is one straight axis-aligned SEGMENT of ink:
#   thin      perpendicular extent <= 4.0 pt (stroke width, or filled-band thickness)
#   long      along-axis extent   >= 10.0 pt
#   isolated  neither end runs into another segment (3 pt past each end is empty)
#   painted   it has ink that is not the page colour
# So a 300x400 pt outline is four rules, and it cannot be traded against a rule
# elsewhere. `thin` and `long` are the calibrated detector's values; `isolated` is what
# separates a rule from a table grid, because a cell edge ends at a T-junction.
#
# PRESERVED means: every isolated rule the source draws is still drawn on the SAME page
# of the render, same orientation, within TOL pt across the rule, covering at least
# OVERLAP of its own length. Per rule, per page - so a gain can never pay for a loss.
#
# Isolation is asked of the SOURCE only. The grid's geometry is re-derived by the
# renderer from the table model; on the render side we only ask "is there ink of this
# shape here", because a rule that came back as a closed box or a table border is still
# painted. Requiring isolation on the render side is a false positive factory: on
# 64_newspaper_uneven_columns_ad_boxes all four rules are on the render within 0.8 pt and
# all four read "lost".
#
# NOT 06/07's QUESTION - and since 13 Nov neither check exists. 06_table_columns counted
# distinct round(x / 6) values with at least three runs down the page and 07_table_rows
# counted the same in y: both were histograms of TEXT coordinates and neither read a drawn
# line, which is exactly why they were retired (see "06_table_columns and 07_table_rows
# RETIRED" in compare()). Nothing in the 43 counts a grid side. The measurement lives in
# tools/p2w-bench/grid_sides.py, which is a tool and not a check.
#
# WHAT THE EXCLUSION COSTS, MEASURED (13 Nov, engine 3d715dd, tools/p2w-bench/grid_sides.py
# over the 211-document corpus). The filter removes 9,694 of the 10,841 thin-long segments,
# and 9,694 of the 9,695 non-isolated segments are grid sides - a segment that T-junctions
# into a perpendicular at one of its ends. Exactly ONE is a rule drawn in pieces that meets
# only collinearly. So the filter is a grid filter and nothing else, which is what makes
# "how much does it hide" a question with an answer.
#
# Counted per side instead of dropped: 238 table lattices on 127 documents carry 9,189 of
# those sides. At a 4 pt tolerance, after each lattice is given its own best rigid
# translation, 230 are not covered by the render (2.5 %) - 225 of them relocated (the row
# or column was re-laid-out, which is displacement's question) and 5 vanished (0.05 %). All
# five are accounted for and not one is a lost border: three are on
# itr-computation-with-slab-table, whose table the render pushed onto a second page
# (01_page_count 1 -> 2), and two are the off-page ends of a rule starting at y -16.4 on
# 12_stamp_across_page_break (27_text_off_page already fails it). At this check's own 24 pt
# the count is 28 sides on 8 documents. On the loss axis the exclusion is right for the
# reason it was introduced: of the 22 documents that lose a grid side at all, 21 already
# fail 18_displacement, and the widened population reproduces it - 52 documents fail with
# every thin-long segment as the source, 48 of them already failing 18_displacement.
#
# The direction the exclusion cannot see even in principle is the other one, and it is
# real ink: 791 render grid sides (8.6 %) are rules the page did not draw, on 55
# documents. That is the .docx's six-sides-per-table model (DocxWriter.TABLE_SIDES,
# DocxWriter.java:4351) doing what it must. 80_gstin_pan_cin_ifsc_table draws five framed
# cards; the writer emits five tables with all four sides "single" AND five frame shapes
# (9 wps:wsp in the .docx), so the render draws each card twice - 20 source sides all
# present, 20 invented, the "Status: VERIFIED" line left outside the inner box. 32 reads
# source=2 lost=0 PASS on that document, and on 353_admit_card (62 invented, 0 lost) only
# 14_filled_shapes fires. A per-side check would fail 55 documents to say so, 45 of which
# already fail 18_displacement and 30 of which fail 14_filled_shapes or 59_shape_anchor:
# the same 92 % redundancy that justifies the exclusion, arriving from the other side. It
# is recorded here, not added as a check.
#
# TOL is 24 pt, and it is chosen from measurement, not taste. Across 1,042 matched pairs
# the perpendicular residual is p50 0.02 / p99 8.57 pt; the engine places a standalone
# rule absolutely and the renderer honours it. The residual is not a continuum, it is
# two populations: rules that did not move at all (max 1.74 pt) and table borders that
# moved with the table they cap (6-22 pt). 24 pt is the smallest tolerance at which the
# verdict stops changing - fails by tolerance: 2 pt 28, 4 pt 28, 6 pt 28, 8 pt 24,
# 12 pt 17, 16 pt 15, 20 pt 15, 24 pt 14, 30 pt 14, 45 pt 14 - and at 2 pt, 24 of the 28
# failures are documents 18_displacement already fails, i.e. a tight tolerance turns 32
# into a second vote for displacement. Matching is 1:1, so no tolerance can hide a lost
# rule behind its neighbour.
#
# RE-MEASURED 13 Nov on engine 3d715dd against a LibreOffice export of the same .docx, 211
# documents: 2 pt 27, 4 pt 27, 6 pt 26, 8 pt 22, 12 pt 16, 16 pt 14, 20 pt 13, 24 pt 13,
# 30 pt 13, 45 pt 13. The same curve one document lower at every step, and the plateau
# starts at 20 rather than 24 - so 24 is inside the flat region rather than at its edge,
# and the smallest value at which the verdict stops changing is 20 pt. The two populations
# are unchanged on 1,048 matched pairs: 1,018 at or below 1.74 pt (p50 0.02, p95 0.03),
# 30 between 6 and 23.8 pt, and 4 in the 1.74-6 pt gap between them. p99 8.73 pt.
#
# PAINTED is not decoration: a pale rule written as a shape with neither fill nor line
# painted nothing in any renderer (972 of 7,380 anchors), and it took this check from 26
# failures to 6. Without the ink test the engine can satisfy 32 by emitting geometry that
# draws nothing - and the old count literally preferred it: deleting a rule reads g_n=25,
# drawing it white reads g_n=26.
# ----------------------------------------------------------------------------
RULE_THIN = 4.0
# How much wider than RULE_THIN the RENDER's copy of a rule may be and still be that rule.
#
# RULE_THIN is a width, and a width is the one thing a renderer does not reproduce
# exactly. 49_coloured_background_block_paragraph draws a 4.00 pt filled strip (the
# accent bar down the side of a shaded block) - exactly RULE_THIN - and the .docx
# carries it at 4.00 pt with the page's own colour (29529E) and the page's own
# position (wp:positionV 146 pt, which is the source's top-down 146.00 pt to the
# hundredth). LibreOffice exports that path 0.05 pt wider on each side, so the render's
# copy is 4.10 pt and `t > RULE_THIN` threw it away: the source's rule then had no
# candidate on its own page and was counted LOST, on a document whose ink is right.
# The allowance is on the render side only - the source's own rules are read from the
# PDF the check is the reference for, and widening that set can only invent losses.
RULE_THIN_REN = 4.25
# RULE_BAND is the same width question one step earlier - "is this filled rect a band
# rather than a box" - and it is what actually rejected the render's 4.10 pt copy
# (4.10 > RULE_BAND, so the rect was classified as neither a band nor a rule and never
# reached the RULE_THIN test at all). Both widths move together on the render side.
RULE_BAND_REN = 4.25
# A face taller than this is not a band between two rules; it is the page frame or a
# panel, and testing every pair of rules across it is quadratic for no answer.
FACE_MAX_H = 900.0
RULE_LONG = 10.0
RULE_GAP = 3.0
RULE_BAND = 4.0
RULE_TOL = 24.0
RULE_OVERLAP = 0.80
PAGE_WHITE = 0.94


def _rgb3(c):
    if c is None:
        return None
    if len(c) == 1:
        return (c[0],) * 3
    if len(c) == 3:
        return tuple(c)
    return None


def _paints(col, alpha):
    """Does this paint anything on a white page?"""
    if col is None:
        return False
    if alpha is not None and alpha <= 0.02:
        return False
    lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
    if alpha is not None and alpha < 0.999:
        lum = lum * alpha + (1 - alpha)
    return lum < PAGE_WHITE


def _rule_segments(page, band=None):
    """Every straight axis-aligned segment the page draws.

    perp is the coordinate across the segment (y for horizontal, x for vertical);
    a..b is its extent along it. A filled band counts whether it is a `re` or a closed
    `l`/`qu` path with a fill - the latter is how LibreOffice draws every cell border,
    and missing it reads a correct render as 1,009 rules against 11,983 segments.
    """
    band = RULE_BAND if band is None else band
    out = []
    for d in page.get_drawings():
        w = d.get("width")
        col = _rgb3(d.get("color"))
        s_alpha = d.get("stroke_opacity")
        fill = _rgb3(d.get("fill"))
        f_alpha = d.get("fill_opacity")
        r = d["rect"]
        stroked = col is not None and w is not None and _paints(col, s_alpha)
        filled = fill is not None and _paints(fill, f_alpha)
        t_s = max(0.05, float(w)) if w is not None else 0.05
        if filled and not stroked:
            h, wd = r.height, r.width
            if h <= band and wd > h:
                out.append({"o": "h", "perp": (r.y0 + r.y1) / 2.0, "a": r.x0, "b": r.x1,
                            "t": max(0.05, h), "col": fill})
            elif wd <= band and h > wd:
                out.append({"o": "v", "perp": (r.x0 + r.x1) / 2.0, "a": r.y0, "b": r.y1,
                            "t": max(0.05, wd), "col": fill})
            continue
        for item in d.get("items", []):
            kind = item[0]
            if kind == "l":
                p1, p2 = item[1], item[2]
                dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                if dy <= 0.8 and dx >= 1 and stroked:
                    out.append({"o": "h", "perp": (p1.y + p2.y) / 2.0,
                                "a": min(p1.x, p2.x), "b": max(p1.x, p2.x),
                                "t": t_s, "col": col})
                elif dx <= 0.8 and dy >= 1 and stroked:
                    out.append({"o": "v", "perp": (p1.x + p2.x) / 2.0,
                                "a": min(p1.y, p2.y), "b": max(p1.y, p2.y),
                                "t": t_s, "col": col})
            elif kind in ("re", "qu"):
                rr = item[1] if kind == "re" else item[1].rect
                if stroked:
                    for perp, a, b, o in ((rr.y0, rr.x0, rr.x1, "h"),
                                          (rr.y1, rr.x0, rr.x1, "h"),
                                          (rr.x0, rr.y0, rr.y1, "v"),
                                          (rr.x1, rr.y0, rr.y1, "v")):
                        out.append({"o": o, "perp": perp, "a": a, "b": b,
                                    "t": t_s, "col": col})
    return out


def _rule_touches(seg, others, gap):
    """True when another segment crosses, meets or abuts either end of seg."""
    lo, hi = seg["a"] - gap, seg["b"] + gap
    for o in others:
        if o is seg:
            continue
        if not (lo <= o["perp"] <= hi):
            continue
        if o["o"] != seg["o"]:
            if not (o["a"] - gap <= seg["perp"] <= o["b"] + gap):
                continue
            if abs(o["perp"] - seg["a"]) <= gap or abs(o["perp"] - seg["b"]) <= gap:
                return True
        elif abs(o["perp"] - seg["perp"]) <= gap and (
                abs(o["b"] - seg["a"]) <= gap or abs(o["a"] - seg["b"]) <= gap):
            return True
    return False


def _rules(page, isolated=True, thin=None, band=None):
    segs = _rule_segments(page, band)
    thin = RULE_THIN if thin is None else thin
    out = []
    for s in segs:
        if s["t"] > thin or (s["b"] - s["a"]) < RULE_LONG:
            continue
        if isolated and _rule_touches(s, segs, RULE_GAP):
            continue
        out.append(s)
    return out


def _doc_rules(doc, isolated=True, thin=None, band=None):
    out = []
    for i, p in enumerate(doc):
        for s in _rules(p, isolated, thin, band):
            s = dict(s)
            s["page"] = i
            out.append(s)
    return out


def _rules_lost(src_rules, ren_segs, tol=RULE_TOL, overlap=RULE_OVERLAP):
    """Every source rule that no render segment on its own page covers. 1:1."""
    by_page = {}
    for s in ren_segs:
        by_page.setdefault((s["page"], s["o"]), []).append(s)
    lost, matched = [], 0
    for s in src_rules:
        cands = by_page.get((s["page"], s["o"]), [])
        L = s["b"] - s["a"]
        best, best_key = None, None
        for o in cands:
            ov = min(s["b"], o["b"]) - max(s["a"], o["a"])
            if ov <= 0 or ov < overlap * L or abs(o["perp"] - s["perp"]) > tol:
                continue
            key = (abs(o["perp"] - s["perp"]), -ov)
            if best_key is None or key < best_key:
                best, best_key = o, key
        if best is None:
            lost.append(s)
        else:
            cands.remove(best)
            matched += 1
    return matched, lost


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


# ---------------------------------------------------------------------------
# The .docx side of rotation: every angle the ENGINE wrote.
#
# WHY THIS EXISTS AT ALL. 35_rotation compared the source's rotated runs against the
# RENDER's, and the render cannot draw them: measured 14 Nov on 211 documents, `soffice
# --headless` emits ZERO lines with a non-level `dir` - not one, in any of the 211 - while
# the source corpus carries 372 rotated lines across 30 documents. The check therefore read
# kept=0 on all 30 and failed all 30, at every tolerance from 0.0 to 360.0 degrees, because
# the render side of the pairing was empty rather than wrong. That is a measurement of
# LibreOffice, not of the engine.
#
# WHAT THE ENGINE ACTUALLY WRITES. OOXML turns a text box with `<a:xfrm rot="N">` in
# 60000ths of a degree, clockwise, and the engine emits it from DocxWriter.anchorShape.
# A rotated line that the page draws inside its own stroked rectangle (a stamp) is bound to
# that rectangle and goes out with the angle; a rotated line with no rectangle round it (the
# per-glyph text of a round seal, a rotated label on a drawing, a rotated table header) is
# placed on its own origin with rotDeg 0f at DocxWriter.java:2508 - the angle is DROPPED, not
# invented. So the .docx is a faithful record of a decision the engine makes, which is
# exactly what a check should read.
#
# SIGN CONVENTION. `line.dir` is the baseline's unit vector in a frame whose y counts down
# the page, so atan2(dy, dx) is already clockwise-positive - the same sense as a:xfrm rot.
# Measured on the 12 anchors the corpus carries, the agreement is exact to 0.0 degrees:
# -15 -> 345, -90 -> 270, -8 -> 352, -14 -> 346, -12 -> 348, -11 -> 349, 15 -> 15, 180 -> 180,
# 9 -> 9, 11 -> 11, 13 -> 13. No conversion is applied, because none is needed; applying
# 360-angle would turn 11 correct anchors into 11 wrong ones.
# ---------------------------------------------------------------------------

def docx_rot_anchors(path):
    """[(rot_deg, norm_text, raw_text)] for every anchored text box the engine rotated.

    Returns None when no .docx can be read, so a caller can tell "the engine wrote no
    rotation" (an empty list) from "this check measured nothing" (None). Those two must
    never collapse: 54_image_dpi passed twelve documents by treating them as one.
    """
    if not path:
        return None
    try:
        import zipfile
        from xml.etree import ElementTree as ET
        A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
        W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        WPS = "{http://schemas.microsoft.com/office/word/2010/wordprocessingShape}"
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        out = []
        for sp in root.iter(WPS + "wsp"):
            xfrm = sp.find(".//" + A + "xfrm")
            rot = xfrm.get("rot") if xfrm is not None else None
            # A QUARTER TURN IS NOT WRITTEN AS <a:xfrm rot>, AND THE FILE SAYS SO PLAINLY.
            #
            # The engine emits a 90-degree line as a text frame turned inside an upright box:
            # <wps:bodyPr vert="vert270"> with the box's extent swapped (DocxWriter.java:2789-
            # 2811). That is deliberate and it is the only construct a quarter turn survives
            # in: <a:xfrm rot> is IGNORED by LibreOffice and by the Docs export (D-13/D-16), so
            # a box that carries its angle only in a:xfrm renders level. Measured on
            # table-with-rotated-header at HEAD: its 11 header cells render at -90.00 deg
            # through vert270, and the same file's <a:xfrm> elements carry no rot at all.
            #
            # This function used to read <a:xfrm rot> alone, so a quarter turn written the one
            # way the target renderer honours it read as "no rotation" - and a run the engine
            # had rotated correctly was charged as lost. Measured on 411_nested_xobject_
            # transforms: its 90-degree title is in the file as vert270 and the check reported
            # both of the page's rotated runs lost.
            #
            # vert="vert" is 90 degrees clockwise (text reads down), vert="vert270" is 270
            # (text reads up), which is the sense the engine uses: it writes vert270 exactly
            # when the line's angle is 270 (readsUp, DocxWriter.java:2401).
            vert = None
            if not rot:
                bodyPr = sp.find(".//" + WPS + "bodyPr")
                v = bodyPr.get("vert") if bodyPr is not None else None
                if v == "vert270":
                    rot = "16200000"       # 270 * 60000
                elif v == "vert":
                    rot = "5400000"        # 90 * 60000
                vert = v
            if not rot:
                continue
            txt = "".join(t.text or "" for t in sp.iter(W + "t"))
            out.append((int(rot) / 60000.0, norm_text(txt), txt))
        return out
    except Exception:
        return None


def page_mirrors_text(doc, page):
    """True when this page shows text under a negative-determinant CTM - a MIRROR.

    A mirrored line is not a rotated line, and the difference is not academic: the source's
    text layer reports a mirrored run exactly as it reports a 180-degree one, dir=(-1,0), so
    35_rotation asked the .docx for a 180-degree anchor for text the page never rotated.
    Measured on 417_rotate180_and_mirrored page 2, drawn under "-1 0 0 1 595 0 cm": 4 runs at
    -180.0 degrees, and no anchor in any .docx can satisfy them - a rotation would turn the
    words upside down, and a mirror is not expressible as an angle at all.

    The determinant is the test because it is the one thing the two do not share: a rotation
    by 180 degrees is [-1 0 0 -1], det = +1; a reflection is [-1 0 0 1], det = -1. PyMuPDF's
    span record does not carry the matrix (no "matrix" key in get_texttrace on this build), so
    the page's own content stream is walked instead - q/Q for the CTM stack, cm for the
    change. Text inside a nested form that is itself mirrored is not seen by this walk; no
    document in the corpus does that, and the cost of missing it is that the run is charged
    as it is today.
    """
    try:
        data = b"".join(doc.xref_stream(x) for x in page.get_contents())
    except Exception:
        return False
    stack = [1.0]
    nums = []
    for m in re.finditer(rb"[-+]?\d*\.?\d+|[A-Za-z'\"*]+", data):
        tok = m.group(0)
        c = tok[:1]
        if c.isdigit() or c in (b"-", b"+", b"."):
            try:
                nums.append(float(tok))
            except ValueError:
                pass
            if len(nums) > 6:
                nums.pop(0)
            continue
        if tok == b"q":
            stack.append(stack[-1])
        elif tok == b"Q":
            if len(stack) > 1:
                stack.pop()
        elif tok == b"cm" and len(nums) >= 6:
            a, b, cc, d = nums[-6], nums[-5], nums[-4], nums[-3]
            stack[-1] = stack[-1] * (a * d - b * cc)
        elif tok == b"BT" and stack[-1] < 0:
            return True
        nums = []
    return False


def page_is_turned_round(page):
    """True when EVERY line on this page is drawn 180 degrees round and nothing is upright.

    This is the engine's own test (PdfToWord.uprightIfPageIsUpsideDown), asked here so the
    check can judge the same page the same way. A sheet printed the wrong way up is not a
    page of stamps: a reader turns the paper, and the baseline is horizontal either way. The
    engine therefore offers that page's text UPRIGHT, and the .docx is right to hold it so.

    35_rotation used to charge every one of those runs as a lost rotation - 61 of them on
    one-page-rotated-180-degrees, which is the largest single charge in the corpus for a page
    that is not wrong. Asking the file for 61 anchors at 180 degrees would ask for 61 floating
    text boxes: buildTables drops every rotated line ("a stamp is not a table row"), so the
    checklist's five columns would stop being a table, and the target renderers ignore
    <a:xfrm rot> anyway, so the boxes would show upright text in the wrong place.

    The page's text is not unchecked by this: 04_chars_missing, 17_matched_runs and
    45_char_accuracy still read it, on the render, where the text really is.
    """
    turned = 0
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            t = "".join(s.get("text", "") for s in ln.get("spans", []))
            if not t.strip():
                continue
            dx, dy = (ln.get("dir") or (1.0, 0.0))[:2]
            if abs(dy) > 0.25:
                return False            # the baseline is not horizontal
            if dx > -0.5:
                return False            # an upright line: an ordinary page
            turned += 1
    return turned > 0


def _ang_diff(a, b):
    """Shortest angular distance in degrees, on the circle."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


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

    # ---- 50_annotations RETIRED 13 Nov -------------------------------------
    # It asked the RENDER for PDF annotation OBJECTS. A .docx has none: its only
    # annotation is a w:comment, which lives in word/comments.xml and is exported to PDF
    # only when the exporter is told to, and then only as one /Text per comment. Three of
    # the six kinds on the one document that failed it (600_reviewed_invoice_with_
    # annotations) have no DOCX counterpart at all - a Highlight, an Underline and a
    # StrikeOut are character FORMATTING in Word, never objects. So the ceiling was
    # arithmetic, not engineering, and it is measured below.
    #
    # WHAT IT MEASURED. verify_google.py:835-844 counted every annotation whose type is
    # not Link and not Widget, in the source and in the render, and demanded
    # g_a >= max(1, int(s_a * 0.9)). On this document s_a = 6, g_a = 0, floor 5: FAIL by
    # five, and no reachable number of annotations in a .docx gets within four of it.
    #
    # THE SIX, from the source (PyMuPDF, page 1):
    #   Highlight  (294.7,221.1,461.3,236.9)  no /Contents
    #   Underline  ( 47.3, 70.3,198.7, 82.7)  no /Contents
    #   StrikeOut  (347.2,123.2,547.8,136.8)  no /Contents
    #   Text       (523.0,132.0,539.0,148.0)  "Rate for HSN 8536 confirmed with PO."
    #   FreeText   ( 48.0,384.0,378.0,414.0)  "Checked against PO 4471. Quantity on line 3
    #                                          raised from 20 to 25."
    #   Stamp      (377.0,383.6,517.0,420.4)  "Approved"
    #
    # THE ENGINE'S PATH, and it is the same for all six. PdfToWord.java:1565-1577
    # (annotationContentsOf) returns ann.getContents() for every non-Widget annotation and
    # nothing else; PdfToWord.java:518 appends those strings to the page's blocks as plain
    # paragraphs at top=0. It never imports PDAnnotationMarkup and never reads
    # getQuadPoints (grep over app/src/main/java/com/kavopdf/app/engine: no match), so the
    # three markup annotations' geometry is not seen at all, and DocxWriter writes no
    # w:highlight, no w:u and no w:strike (grep -c: 0), so it could not write their look
    # either. DocxWriter.java:537-546 writes nine parts - [Content_Types].xml, _rels/.rels,
    # word/document.xml, styles.xml, theme/theme1.xml, settings.xml, _rels/document.xml.rels,
    # docProps/core.xml, docProps/app.xml - and word/comments.xml is not one of them.
    #
    # WHAT THAT COSTS, measured on the pair (ConvertAll, then soffice --headless
    # --convert-to pdf, then this verifier):
    #   * the three /Contents strings survive as TEXT, at x = 0.1 pt, y = 15.0 / 42.0 /
    #     69.0 - the left margin of the first line - where the source had them at x >= 48
    #     and y 132-420. Carried, and hoisted. 05_chars_extra reads 30 on this document
    #     for exactly this reason: the words are in the render and not in the source's
    #     text layer, because an annotation is not a text layer.
    #   * the three markup annotations' INK is gone. The yellow is in the source only as
    #     the Highlight's appearance stream (xref 79: "1 1 0 rg"), not in the page content
    #     (the content stream contains no "1 1 0 rg"), so no text extractor can carry it;
    #     the render's only fill colour is black. That is a real loss and it is NOT what
    #     this check was counting.
    #
    # CAN THE TARGET FORMAT CARRY IT? Constructed and measured, so this is not an opinion.
    # A .docx holding a real w:comment (word/comments.xml + commentRangeStart/End +
    # commentReference) over a highlighted run, an underlined run and a struck-out run was
    # rendered twice by the same soffice:
    #   soffice --convert-to pdf                     -> 0 annotation objects
    #   soffice --convert-to pdf, ExportNotes=true   -> 1 annotation object, /Text, carrying
    #                                                   the comment's text
    # The highlight, the underline and the strike came through both times as INK (the
    # render's fills include (1,1,0) yellow) and never as objects. So the maximum a
    # perfectly annotation-aware engine could score here is 1 of 6, against a floor of 5.
    # And on the renderer this verifier is named for, the ceiling is 0: Google Docs' PDF
    # download drops comments entirely (there is no include-comments option on Download or
    # Print; the workaround everyone uses is to download .docx and print from Word with
    # Print Markup). A check whose answer is set by the exporter's flags cannot be moved by
    # a fix to the engine, which is the same argument that retired 53's render-side form and
    # 54's.
    #
    # NO UNIQUE CLASS, by construction rather than by corpus count. No engine output can
    # reach the floor, so removing the check cannot hide an engine regression - it can only
    # stop reporting the renderer's export policy as an engine defect. What the class really
    # is - markup ink lost, note text hoisted - is asked of the things themselves below and
    # in 05_chars_extra, 14_filled_shapes and 13_text_colours.
    #
    # WHAT REPLACES IT, keeping the count at 47 and asking the .docx, which is the file the
    # engine actually decides. Every annotation /Contents the source carries must appear as
    # text in the engine's .docx. That is answerable, it is passable, and it is the only part
    # of an annotation the target format can carry as text at all.
    #
    # NOT COVERED HERE, and deliberately not smuggled in: the markup ink. Grading it needs a
    # rect-scoped ink test - is there fill or a rule inside this annotation's /Rect - and a
    # new id, not this one. Written as an occupancy lattice it would be retired 29 and 30
    # again, and the corpus has no document whose only defect is of that class.
    def annot_texts(doc):
        out = []
        for p in doc:
            for a in p.annots():
                if a.type[1] in ("Link", "Widget"):
                    continue
                s = (a.info.get("content") or "").strip()
                if s:
                    out.append(s)
        return out

    def docx_flat(path):
        try:
            z = zipfile.ZipFile(path)
            x = z.read("word/document.xml").decode("utf-8", "replace")
        except Exception:
            return None
        x = re.sub(r"<w:tab[^>]*/>", " ", x)
        x = re.sub(r"</w:p>", "\n", x)
        x = re.sub(r"<[^>]+>", "", x)
        return re.sub(r"\s+", " ", x).strip()

    s_at = annot_texts(src)
    d_at = docx_flat(docx_path) if docx_path else None
    if d_at is None:
        # Same rule as 53 and 54: a run that forgot --docx measured nothing here, and must
        # be visible as such rather than passing silently.
        print("50_annotation_text: no .docx given, annotation text unmeasured", file=sys.stderr)
        c["50_annotation_text"] = (len(s_at), 0, True)
    else:
        want = [re.sub(r"\s+", " ", s) for s in s_at]
        carried = sum(1 for w in want if w in d_at)
        if carried < len(want):
            print("50_annotation_text: %d of %d annotation strings are not in the .docx: %s"
                  % (len(want) - carried, len(want),
                     "; ".join(repr(w[:40]) for w in want if w not in d_at)), file=sys.stderr)
        c["50_annotation_text"] = (len(want), carried, carried == len(want))

    # ---- 51 form field values ---------------------------------------------
    # UNTIL 14 Nov this counted page.widgets() in the RENDER and asked the render for 90 %
    # of the source's count. A .docx cannot carry one, and the check's answer was therefore
    # the exporter's, not the engine's - which is the defect 50_annotations was retired for
    # in 65fd7a6 ("the check's answer was set by the exporter's flags, not the engine's
    # decision"), one document over. Measured on 601 with three minimal probe .docx files
    # and LibreOffice 7.4.7.2, ExportFormFields defaulting to true
    # (/usr/lib/libreoffice/share/registry/main.xcd:2281):
    #   w:fldChar/w:ffData  -> imported as a fieldmark          -> 0 widgets in the render
    #   w:sdt + w:sdtPr     -> imported as loext:content-control -> 0 widgets in the render
    #   w:object/w:control  -> imported as a real control        -> 1 widget per field, and
    #                          the only encoding that passes the old check. Built for 601 it
    #                          read 11/11 and PASSED while every answer still sat in three
    #                          paragraphs at the top of page 1.
    #
    # What IS the engine's decision is where each answer goes. A filled form keeps its
    # answers in each widget's /V and a reader draws them inside the widget's own rectangle,
    # so that is what is asked, per source widget:
    #   ink  - if the source draws inside the rect (2 pt in from its edge, so the box's own
    #          border is not content), the render must draw inside it too. A tick is a mark,
    #          not a string: the source's tick extracts as the glyph '3' out of ZapfDingbats,
    #          and asking for that character would be asking the render to reproduce one
    #          font's encoding.
    #   text - if the source's words inside the rect contain a letter, the render's words
    #          inside the same rect must contain them. This is the typed answer.
    # A rect that shows nothing asks nothing: an empty box has no answer to lose. Measured on
    # 601: the source reads 3/3, the engine's own .docx reads 0/3, the ActiveX build 2/3, and
    # the same engine with its three answers moved onto their rects reads 3/3 (601 33/43 ->
    # 37/43, 18/28/45/47 flipping to pass because the page is no longer pushed down).
    FIELD_INK_FLOOR = 0.02
    FIELD_INSET = 2.0

    def field_ink(page, r):
        rr = fitz.Rect(r.x0 + FIELD_INSET, r.y0 + FIELD_INSET,
                       r.x1 - FIELD_INSET, r.y1 - FIELD_INSET)
        if rr.width <= 0 or rr.height <= 0:
            return 0.0
        s = page.get_pixmap(clip=rr, colorspace=fitz.csGRAY, dpi=72).samples
        return (sum(1 for b in s if b < 200) / len(s)) if s else 0.0

    def field_words(page, r):
        out = []
        for wd in page.get_text("words"):
            if fitz.Rect(wd[:4]).intersects(r):
                t = " ".join(unicodedata.normalize("NFC", wd[4] or "").split())
                if t:
                    out.append(t)
        return out

    f_asked = f_ok = 0
    f_bad = []
    for sp in src:
        ws = list(sp.widgets())
        if not ws:
            continue
        rp = gd[sp.number] if sp.number < len(gd) else None
        for w in ws:
            r = fitz.Rect(w.rect)
            s_ink, s_words = field_ink(sp, r), field_words(sp, r)
            if s_ink < FIELD_INK_FLOOR and not s_words:
                continue                      # an empty box asks nothing
            f_asked += 1
            if rp is None:
                f_bad.append("%s: page %d is not in the render" % (w.field_name, sp.number + 1))
                continue
            ink_ok = s_ink < FIELD_INK_FLOOR or field_ink(rp, r) >= FIELD_INK_FLOOR
            r_words = field_words(rp, r)
            text_ok = all(any(t in rw for rw in r_words)
                          for t in s_words if any(c.isalpha() for c in t))
            if ink_ok and text_ok:
                f_ok += 1
            else:
                f_bad.append("%s (ink=%s text=%s)" % (w.field_name, ink_ok, text_ok))
    if f_bad:
        print("51_field_values: %d of %d answers are not inside their field's rectangle: %s"
              % (len(f_bad), f_asked, "; ".join(f_bad[:8])), file=sys.stderr)
    c["51_field_values"] = (f_asked, f_ok, f_ok == f_asked)

    # ---- 52 outline / bookmarks -------------------------------------------
    # A bookmark tree is a STRUCTURE, and until 13 Nov this check counted ENTRIES.
    # `len(doc.get_toc())` is one integer and the tree it came from is thrown away -
    # levels, titles and page targets never reach the comparison. That is 32_stroke_lines
    # again: counting objects where the object is the structure.
    #
    # MEASURED 13 Nov on the only corpus document that carries a tree,
    # 602_bookmarked_annual_report (3 roots + 3 children, 6 entries, 3 pages), by
    # building constructed renders and running them through this verifier: a renamed
    # title, one entry promoted from level 2 to level 1, the whole tree flattened to six
    # level-1 entries, all six titles replaced with different ones, and all six
    # retargeted to page 1 each kept six entries and each PASSED. The only thing that
    # could fire was a count below the 90 % floor, so on a six-entry tree exactly one
    # lost entry is invisible (max(1, int(6 * 0.9)) = 5).
    #
    # What replaces it: the tree is read as an ordered sequence of (level, title) and
    # compared to the source's entry for entry. Three states, not one -
    #   no /Outlines             -> "none": the pair is not asked about a tree it never had
    #   /Outlines it cannot walk -> "unreadable", and that FAILS. Measured: a First/Next
    #                               cycle makes get_toc() return 0 entries with no
    #                               exception, so "corrupt" and "absent" were the same
    #                               value, and a corrupt source read as "nothing to lose"
    #                               and short-circuited the whole check to pass.
    #                               "asked and could not answer" is a FAIL, not a PASS -
    #                               the rule 54_image_dpi was retired for.
    # Page targets are reported in `detail` and NOT scored: a reflow that pushes a
    # heading onto the next page moves its bookmark legitimately, and 01_page_count and
    # 24_page_breaks already own pagination. Additions are not scored when the source had
    # no tree, because Google's export builds heading bookmarks the source never carried
    # (DEFECTS.md:375) and that is the exporter's decision, not a conversion loss.
    def _t52(s):
        return " ".join(unicodedata.normalize("NFC", s or "").split())

    def _outline52(doc):
        """(state, [(level, title, page)]) with state in {"tree", "none", "unreadable"}."""
        try:
            cat = doc.pdf_catalog()
            has_outlines = "/Outlines" in doc.xref_object(cat, compressed=False)
        except Exception:
            has_outlines = False
        try:
            raw = doc.get_toc(simple=False)
        except Exception:
            return "unreadable", []
        if not raw:
            if not has_outlines:
                return "none", []
            # /Outlines is in the catalog and get_toc() still returned nothing: either a
            # legal empty /Outlines dict (no /First) or a tree it refuses to walk.
            try:
                ref = doc.xref_get_key(cat, "Outlines")[1]
                first = doc.xref_get_key(int(ref.split()[0]), "First")[1]
            except Exception:
                first = "null"
            return ("unreadable", []) if first not in ("null", "") else ("none", [])
        out = []
        for e in raw:
            try:
                out.append((int(e[0]), _t52(e[1]), int(e[2])))
            except Exception:
                return "unreadable", []
        return "tree", out

    s_state, s_tree = _outline52(src)
    g_state, g_tree = _outline52(gd)
    s_shape = [(l, t) for l, t, _ in s_tree]
    g_shape = [(l, t) for l, t, _ in g_tree]
    if "unreadable" in (s_state, g_state):
        ok52 = False
        which = "source" if s_state == "unreadable" else "render"
        d52 = "%s /Outlines is present and could not be walked - 0 entries is not the same as no outline" % which
    elif s_state == "none":
        # Nothing to preserve. Reported, never failed: see the note above.
        ok52 = True
        d52 = ("source has no outline; render adds %d entries (not scored)" % len(g_tree)
               if g_tree else "neither side carries an outline")
    elif s_shape == g_shape:
        ok52 = True
        moved = [(t, sp, gp) for (_, t, sp), (_, _, gp) in zip(s_tree, g_tree) if sp != gp]
        d52 = ("tree preserved: %d entries, depth %d" % (len(g_tree), max(l for l, _ in g_shape)))
        if moved:
            d52 += "; %d bookmark(s) on a different page: %s" % (len(moved), moved[:4])
    else:
        ok52 = False
        missing = [x for x in s_shape if x not in g_shape]
        added = [x for x in g_shape if x not in s_shape]
        flat = (len(s_shape) == len(g_shape) and len({l for l, _ in s_shape}) > 1
                and len({l for l, _ in g_shape}) == 1)
        d52 = "structure differs: %d -> %d entries" % (len(s_shape), len(g_shape))
        if missing:
            d52 += "; missing %s" % (missing[:4],)
        if added:
            d52 += "; added %s" % (added[:4],)
        if flat:
            d52 += "; whole tree flattened to one level"
        elif not missing and not added:
            d52 += "; same titles and count but the levels or the order changed"
    c["52_outline"] = (len(s_tree), len(g_tree), ok52, d52)

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
              % (len({face_bucket(f) for f in s_fa}
                     & {face_bucket(f) for f in faces(gd)}), len(s_fa)), file=sys.stderr)
        c["53_embedded_faces"] = (len(s_fa), 0, True)
    else:
        s_tot = sum(s_fa.values()) or 1
        d_tot = sum(d_fa.values()) or 1

        # ONE BUCKET PER READER-FAMILY, AND A BUCKET CAN HOLD TWO SOURCE FAMILIES.
        # The source side is grouped by the family a READER will have (face_bucket), not by
        # the name the PDF spelled: that is the whole of what SAME_FACE means. The .docx
        # side is NOT grouped - a name is taken for what it says.
        #
        # Grouping is not free. A document that draws Liberation Sans AND Arial puts both
        # into `arial`, and the .docx carries one bucket of characters with no way to say
        # which source family each run came from. Two things follow, and both are done
        # here rather than left to chance:
        #   - the characters of BOTH spellings are credited to the bucket, so a .docx that
        #     kept "Liberation Sans" because the engine did not rename it is not read as a
        #     loss;
        #   - the bucket is judged against the SUM of the group's shares, not against one
        #     member's, and the merge is printed. Per-family ratios inside a merged bucket
        #     would be a number the .docx cannot support: crediting the whole bucket to
        #     each member would pass anything, and crediting it to neither would fail a
        #     document that lost nothing.
        groups = collections.defaultdict(list)
        for fam in s_fa:
            groups[face_bucket(fam)].append(fam)
        merged = {b: fs for b, fs in groups.items() if len(fs) > 1}
        lost = []
        for bucket, members in groups.items():
            # Characters the .docx carries under the reader-family, counting the spellings
            # the engine may have left alone.
            got_chars = d_fa.get(bucket, 0) + sum(d_fa.get(m, 0) for m in members if m != bucket)
            want_chars = sum(s_fa[m] for m in members)
            want = want_chars / s_tot
            got = got_chars / d_tot
            # A family the source only DECLARES (weight 0) has no share to lose; it only has
            # to be present - and `faces` keeps such a family only when the page drew nothing
            # at all, where the dictionary is the only evidence there is.
            ratio = (got / want) if want else (1.0 if got else 0.0)
            if ratio < SHARE_FLOOR:
                for m in members:
                    lost.append((m, round(ratio, 3), s_fa[m]))
        kept = len(s_fa) - len(lost)
        if merged:
            print("53_embedded_faces: %s - the .docx has one face for these, so the split "
                  "between them is unmeasured and only the group's share was judged"
                  % ", ".join("+".join(sorted(fs)) for fs in merged.values()),
                  file=sys.stderr)
        if lost:
            print("53_embedded_faces: %s" % ", ".join(
                "%s kept %.0f%% of %d chars" % (f, r * 100, ch) for f, r, ch in lost),
                file=sys.stderr)
        c["53_embedded_faces"] = (len(s_fa), kept, len(s_fa) == 0 or not lost)

        # 09_font_names' surviving fact, demoted from a vote to a note. 09 counted the
        # families in Google's export against the source and failed when the count fell by
        # more than 20 %; that fired on Google's substitution, which no .docx change can
        # move, so it is not a check. It is still worth saying out loud when it happens,
        # because a reader opening the converted file will see it - and because the day the
        # engine starts writing a family the exporter cannot carry, this line is the evidence.
        # Only when the .docx is CLEAN. If the engine dropped the family, 53 has already
        # said so above and the exporter is not the story - reporting it twice would blame
        # Google for the engine's loss, which is the mistake that retired 09.
        g_fams = faces(gd)
        if not lost and len(g_fams) < max(1, int(len(s_fa) * 0.8)):
            print("53_embedded_faces: the .docx carries %d of %d source families, but Google's "
                  "export shows %d - the exporter collapsed them, not the engine "
                  "(retired 09's signal, reported, not scored)"
                  % (len(s_fa) - len(lost), len(s_fa), len(g_fams)), file=sys.stderr)

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
    if s_d == 0:
        # The source draws no raster picture, so there is no engine resolution decision
        # this check could be wrong about. Nothing to measure and nothing to lose - a real
        # pass, and the only pass this check may take without a .docx.
        c["54_image_dpi"] = (s_d, d_d if d_d is not None else 0, True)
    elif d_d is None:
        # UNMEASURED IS NOT A PASS. Google's number answers a different question - it is
        # the exporter's tier, not the engine's decision - so when no .docx can be read
        # this check has measured NOTHING and has no verdict to cast. It used to return
        # ok=True with a line on stderr, and that made it a vote that can never be cast:
        # every run that did not pass --docx scored this check as a PASS on all 211
        # documents, including documents whose .docx had genuinely lost resolution.
        #
        # Measured, 13 Nov, on 10_stamp_as_image: with a .docx whose picture had been
        # shrunk 8x, `--docx` gives (source=344, render=43, ok=False) - a real fail. The
        # same document with the same degraded .docx out of reach gives
        # (source=344, render=0, ok=True). Same defect, opposite verdict, and the only
        # difference is whether the verifier could see the file it was asked about.
        #
        # So it now fails, loudly: the score says it, not just a stderr line. render=-1
        # marks "not measured" and is not a density - nothing downstream does arithmetic
        # on it - so an unmeasured row can never be mistaken for a measured zero.
        print("54_image_dpi: FAIL - cannot measure. No readable .docx, so the engine's image "
              "resolution is unknown (the render reads %s dpi, which is Google's export tier, "
              "not the engine's decision). Pass --docx <engine.docx>, or put it beside the "
              "source (out1/<name>.docx next to all/<name>.pdf)." % g_d, file=sys.stderr)
        c["54_image_dpi"] = (s_d, -1, False)
    else:
        c["54_image_dpi"] = (s_d, d_d, d_d >= s_d * 0.6)

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
    ANCHOR_WIDTH_TOL = 1.5     # pt; the render reproduced the run's own ink width
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


    # ---- 59: what OBJECT a box is, decided from the file, not from a tolerance
    def _face(rect, page):
        """The primitive the file actually drew there: a filled face or an outline.

        A filled band and a stroked frame of the same rectangle are different objects -
        a background panel versus an outline drawn round something. The corpus draws one
        table face four ways (one rect, four line paths, four filled hairlines, and
        _shapes' assembled rule pair) and all four are ONE object: an outline. So the
        answer is two-valued and it is read off the drawings rather than guessed.
        """
        for d in page.get_drawings():
            r = d["rect"]
            if (abs(r.x0 - rect.x0) < 0.6 and abs(r.y0 - rect.y0) < 0.6
                    and abs(r.x1 - rect.x1) < 0.6 and abs(r.y1 - rect.y1) < 0.6):
                return "filled" if d.get("fill") is not None else "outline"
        return "outline"        # an assembled rule pair, or a placed image

    def _held(rect, rs):
        """The set of texts this box encloses - the box's identity, as a set.

        A stamp's outline holds the stamp's text. A table row band holds the row. A page
        frame holds the page. Two rectangles holding different texts are different
        objects even when their corners agree to the point, and the text's offset inside
        them is then measured between two unrelated origins.
        """
        out = set()
        for r in rs:
            cx, cy = (r["x"] + r["x1"]) / 2.0, (r["y"] + r["y1"]) / 2.0
            if rect.x0 <= cx <= rect.x1 and rect.y0 <= cy <= rect.y1:
                out.add(norm_word(r["text"]))
        return frozenset(out)

    def _same_object(sb, gb, sp, gp, srs, grs):
        """Are these two coincident rectangles the same object?

        Two questions, neither of them a tolerance on the answer:
          1. the same primitive        - filled face vs outline, from the drawings
          2. the same text population  - the set of texts each box encloses must be equal
        (2) is what catches "same size, different object": a cell rect and the band that
        replaced it agree to the point but do not hold the same text. Measured on the
        corpus this decides 406_passport_mrz_page (its page frame holds 32 texts on one
        side and 31 on the other) and, with clause A, brochure-3col-with-sidebar-box
        (its sidebar holds 22 against 21) - and it fires on 1 document of 211 on its own.
        """
        if _face(sb, sp) != _face(gb, gp):
            return False
        return _held(sb, srs) == _held(gb, grs)

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
        gshapes = _shapes(gp)
        sshapes = _shapes(sp)                   # for the size-class population test
        gtext = norm_word(gp.get_text())
        # Each side's anchors are chosen against the OTHER side's shapes: a box the
        # other document cannot express is not an object the two can be compared on.
        sa = _anchors(sp, sruns, gshapes)
        ga = _anchors(gp, gruns, sshapes)
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
                # ITS TEXT IS NOT IN THE RENDER AT ALL - unless the matcher simply did
                # not pair it. _match pairs on the exact word and, failing that, on a
                # join of runs on one baseline; a page that draws one glyph per span on
                # a curve defeats both. The page itself can answer the question the
                # matcher could not: if the word is in the page's text, the text was not
                # lost and this instrument has no verdict to cast.
                if norm_word(sruns[i]["text"]) in gtext:
                    unjudged += 1
                    continue
                lost += 1         # its text is not in the render at all
                n_judged += 1
                n_out += 1
                continue
            used.update(js)
            bs = [ga[j] for j in js if ga[j] is not None]
            # THE UNION'S CENTRE, not the mean of the pieces' centres. _match may pair one
            # source run with SEVERAL render runs (a split), and the mean of their centres
            # is not the centre of the text they make: a run split into a narrow piece and
            # a wide one reads as a point weighted towards the narrow one. Measured on
            # 320_balance_sheet_statutory, whose source run is one span and whose render
            # splits it in two: dx read +3.50 with the ink's left edge 0.01 pt from where
            # it started, i.e. a 3.5 pt "drift" produced entirely by the averaging.
            gx = (min(gruns[j]["x"] for j in js) + max(gruns[j]["x1"] for j in js)) / 2.0
            gy = (min(gruns[j]["y"] for j in js) + max(gruns[j]["y1"] for j in js)) / 2.0
            if not bs:
                if _box_moved(sb, gshapes, sshapes):
                    moved += 1    # the outline is on the page, somewhere else
                    n_judged += 1
                    n_out += 1
                    hard_out += 1
                else:
                    unjudged += 1
                continue
            gb = bs[0][2]
            # DX IS TAKEN AT THE INK, which is what every other position check in this
            # file does and this one did not. A span's bbox starts at the PEN, and a run
            # that begins with spaces advances the pen without drawing anything: the
            # source's '   Cost of materials consumed' has bbox x0 31.00 and its first
            # glyph at 38.16, and the render drops the three spaces. Comparing bbox to
            # bbox charges that 7.16 pt to the run's place - measured on
            # 320_balance_sheet_statutory, dx read +3.50 on five rows whose ink had moved
            # 0.01 pt. dy stays on the bbox, as 18_displacement takes it, so the ascent
            # sensitivity is the house standard's and not this check's own.
            gxl = min(gruns[j]["xink"] for j in js)
            dx = (gxl - gb.x0) - (sruns[i]["xink"] - sb.x0)
            dy = (gy - gb.y0) - (sy - sb.y0)
            # AGREEMENT IS NEVER A DEFECT, whatever box it was measured against. Two
            # rectangles that differ still put the text in the same place inside
            # themselves, and a number that reads 0 is not evidence of drift. So the
            # acquittal needs no identity test and keeps it - it is the CONVICTION that
            # does, and that is the whole of what changed here.
            if abs(dx) <= ANCHOR_TOL_PT and abs(dy) <= ANCHOR_TOL_PT:
                anchored += 1
                n_judged += 1
                continue
            # A DISAGREEMENT IS A CONVICTION ONLY WHERE BOTH SIDES ARE THE SAME OBJECT.
            #
            # The box: on two different rectangles dx is the text's movement PLUS the
            # distance between two unrelated origins, and the two cannot be separated
            # from the number alone. 119 of the 826 runs this check fails on the corpus
            # are exactly that (57 with a box of the same size elsewhere on the page, 62
            # with none), and every one of them has moved 110-450 pt on the page - the
            # page reflowed, which is 18_displacement's and 24_page_breaks' question, not
            # a question about a relation to an outline. The check has no verdict here.
            #
            # The run: dx is taken at the run's CENTRE, and a centre is a function of the
            # run's WIDTH as well as its place. A run whose ink is 6.7 pt wider - the
            # 90th percentile of this corpus's same-box runs - has its centre 3.35 pt
            # further right with its left edge exactly where it was: over the tolerance,
            # with nothing moved. Measured on the 418 same-box runs the shipped check
            # fails: 113 are within 3 pt once the offset is taken at the ink's LEFT edge
            # instead of the centre. So a run whose width the render did not reproduce is
            # not comparable either.
            if not _same_box(sb, gb):
                # ...UNLESS THE OUTLINE IS THE THING THAT MOVED. "The outline slid and
                # the text stayed" is this check's own defect and it needs no offset
                # comparison at all: the text's place on the page and the box's place on
                # the page are each measurable on their own, and the defect is the one
                # combination - text where it was, box somewhere else - that a
                # displacement check cannot see, because nothing the reader reads moved.
                # Decidable only when the source's rectangle still exists on the page at
                # its own size, which is what _box_moved asks.
                dtx, dty = gx - sx, gy - sy
                if (abs(dtx) <= ANCHOR_TOL_PT and abs(dty) <= ANCHOR_TOL_PT
                        and _box_moved(sb, gshapes, sshapes)):
                    moved += 1
                    n_judged += 1
                    n_out += 1
                    hard_out += 1
                    continue
                unjudged += 1
                continue
            s_w = sruns[i]["x1ink"] - sruns[i]["xink"]
            g_w = sum(gruns[j]["x1ink"] - gruns[j]["xink"] for j in js)
            if abs(s_w - g_w) > ANCHOR_WIDTH_TOL:
                unjudged += 1
                continue
            moved += 1
            n_judged += 1
            n_out += 1
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
    #     substituted face, fired over=1. The answer taken here was the 90th percentile.
    #     THAT ANSWER WAS WRONG TOO, and it was wrong because the noise it was defending
    #     against was never bounded - see edge() for the measurement: the percentile's own
    #     slack reached 65.5 pt at p90 and the short-column fallback reached 416.7 pt, so
    #     the check was defending a one-line move with a tolerance five times the figure it
    #     states, and still firing on 25 documents whose columns had not moved at all. The
    #     widest line plus ONE MEASURED WORD of slack absorbs the same one-line move, at a
    #     bound that is a property of the type, and it is the widest line that sees a
    #     single line running into the margin - which is the defect, not the noise.
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
    SLACK_CAP = 40.0        # one word wider than this is a token, not a word - see edge()

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

    def edge(col, left, words):
        """(the column's right edge, how precisely the page can state it).

        THE EDGE IS THE COLUMN'S WIDEST LINE. It was the 90th percentile of the right
        edges, and the percentile was wrong for two measured reasons.

        1. IT MEASURED RAGGEDNESS, NOT WIDTH. A percentile sits below the text area's
           right edge by however ragged the column is, and the source and the render are
           ragged for different reasons: a justified source block ends every full line at
           exactly one x (370_offer_letter: four lines at 538.6) while a renderer that has
           lost the justification ends them anywhere (same page: 497.9, 506.2, 510.5,
           523.9). p90 against p90 read that as a column 32 pt narrower and fired on 25
           documents. Over the 1421 judged columns of the 211-document corpus the p90
           difference has |d| p99 = 67.3 pt; the widest-line difference has 47.2.
        2. ITS SLACK COULD NOT BE BOUNDED. See below - the whole-range fallback.

        The widest line is the right estimator for a BOUNDARY, and this is one: no line
        may cross the text area's right edge, and on a column with any full line at all
        the widest line IS that edge. Its noise under a legitimate re-break is one word -
        the last word of the widest line moving to the next line - which is a measured
        quantity, not an order-statistic gap.

        THE SECOND NUMBER IS ONE WORD OF THIS COLUMN. A line's right edge can only move
        when its last word moves, and then by that word's width, so the width of a word in
        the column's own font is exactly the largest movement that is not evidence of a
        defect. It is measured from the column's words (the median, so one long token
        cannot set the tolerance for the whole column): over 1421 columns p50 = 24.0 pt,
        p75 = 28.3, p90 = 34.0. This replaces the order-statistic gap, which reached
        p90 = 65.5 pt uncapped and was capped at 24 - a cap 42.9 % of all columns rode.

        AND IT REPLACES THE SHORT-COLUMN FALLBACK. The old branch returned the whole
        column range as the slack whenever the column held under five lines. The p90 of
        five lines is already the widest line, so the branch never changed the edge; it
        only replaced the slack with the column's entire spread - measured at up to 416.7
        pt, and ridden by 72.3 % of the 502 short columns. Nothing needs a fallback now:
        one word is defined for a column of one line and for a column of two hundred.

        SLACK_CAP now bounds a token, not a page. p99 of the median word width is 45.4 pt
        and the largest is 146.0, so a cap of 40 caps 3.0 % of columns - against 42.9 %
        at 24 - and the class size does not move between a cap of 30 and no cap at all.
        """
        v = sorted(b[2] for b in col)
        w = sorted(b[2] - b[0] for b in words if abs(b[0] - left) <= 10)
        one_word = w[len(w) // 2] if w else 0.0
        return v[-1], min(SLACK_CAP, one_word)

    over = under = 0
    for i in range(min(src.page_count, gd.page_count)):
        sc, gc = columns(src[i]), columns(gd[i])
        if not sc or not gc:
            continue
        # The words are what a re-break moves, so they are read once per page rather
        # than per column.
        s_words = [w for w in src[i].get_text("words") if w[4].strip()]
        g_words = [w for w in gd[i].get_text("words") if w[4].strip()]
        for a, s_col in sc:
            hit = [(abs(a - b2), c2) for b2, c2 in gc if abs(a - b2) <= 10]
            if not hit:
                continue                      # the column is gone: 04/05 own that
            g_col = min(hit, key=lambda t: t[0])[1]
            (rs, slack), rg = (edge(s_col, a, s_words),
                               edge(g_col, a, g_words)[0])
            # The single-line defence is now the slack, not the estimator: one word of
            # the column's own text is exactly as far as the widest line can move when a
            # line breaks differently, so a re-break cannot decide the verdict while a
            # line that runs a word past the column still can.
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

    # ---- 61 blank_not_filled ------------------------------------------------
    #
    # A region the SOURCE SHOWS AS BLANK must not be filled in the RENDER.
    #
    # THIS IS NOT 14's QUESTION, and that is why 14 passes 414_transparency_softmask.
    # 14 compares INK AREA - the render may not hold less than 80 % of the source's - and
    # places the source's own fills. Both halves walk the SOURCE and ask what became of it.
    # Ink the render INVENTED is invisible to both: 40,000 pt2 of solid #1A4D99 added to a
    # page that shows white RAISES the render's area and leaves every source fill where it
    # was, so 14 reads 1.0 and PASSES. It is the same shape 13_text_colours had before its
    # GAIN clause: a check that walks one set cannot see the other.
    #
    # MEASURED ON 414. The page is (255,255,255) at five points across the bar and at every
    # pixel of its 400 x 100 pt; the .docx painted a solid 400 x 100 pt block of #1A4D99 and
    # the render read (26,77,153) at the same five points. The bar is a fill under a
    # luminosity /SMask whose group paints at the page origin, so it covers none of the bar
    # and the page paints nothing there. Every check in this file passed that document.
    #
    # WHY THE SOURCE SIDE IS A RASTER AND NOT A LIST OF DRAWINGS. pymupdf's get_drawings()
    # cannot answer this question. It reports the masked bar with fill_opacity 1.0 - the
    # mask's effect is not in any drawing attribute - and it walks INTO the mask's form
    # XObject and reports the mask's own two rectangles as page ink. A check built on that
    # list either sees the bar as ink (and never fires) or has to re-implement the mask. So
    # the question is asked of the pixels, which is how the evidence for this class was
    # gathered in the first place: what does the page show.
    #
    # WHY THE RENDER SIDE IS STILL A DRAWING LIST. The render's fills are what the .docx
    # asked for, and their rects are exact. A raster on both sides would blur the rect of
    # the fill it is charging.
    #
    # WHAT COUNTS AS BLANK. The page's own PAPER colour - the most common pixel - sampled on
    # a 5 x 5 grid inset 1 pt inside the render fill, each point a 3 x 3 median so an
    # antialiased edge cannot decide it. Paper, not white: a document with a tinted page
    # background is judged against its own background.
    #
    # WHY A FILL THE COLOUR OF THE PAPER IS NOT CHARGED. LibreOffice writes a white fill
    # under a table cell and under a text frame. A fill the colour of the paper shows
    # nothing, and the question here is what a READER sees - the same reason 25_invisible_text
    # exists. The tolerance is the same 8/255 the blank test uses, so a fill that is paper to
    # the eye is paper to both halves.
    #
    # WHY 400 pt2. It is 14's own placement floor, kept rather than re-derived: below it a
    # fill is a rule or a speck, and whether a mark that size moved is 32_stroke_lines' and
    # 59_shape_anchor's question. A 20 x 20 pt block is 400 pt2; the 414 bar is 40,000.
    #
    # NO SAME-COLOUR EXCUSE, and that is deliberate. The obvious tolerance - "a source fill
    # of this colour overlaps the box, so this is that cell moved" - would EXCUSE 414, whose
    # invented block is the same #1A4D99 as the source's own masked bar. A renderer's
    # slightly oversized cell still puts most of the grid over the source's ink, so the 95 %
    # bar is what carries the shifted-cell case, not a colour match.
    BLANK_FILL_PT2 = 400.0
    BLANK_CLEAR = 0.95
    BLANK_GRID = 5
    BLANK_INSET = 1.0
    BLANK_DPI = 100
    BLANK_TOL = 8

    def _rgb_of(col):
        if col is None:
            return None
        try:
            return tuple(int(round(c * 255)) for c in col[:3])
        except Exception:
            return None

    def _near(a, b):
        return a is not None and b is not None and \
            max(abs(x - y) for x, y in zip(a[:3], b[:3])) <= BLANK_TOL

    def _median3(pix, x, y):
        """The colour at a point, as the median of its 3 x 3 neighbourhood."""
        vals = [[], [], []]
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                px = min(max(x + dx, 0), pix.width - 1)
                py = min(max(y + dy, 0), pix.height - 1)
                c = pix.pixel(px, py)
                for k in range(3):
                    vals[k].append(c[k])
        return tuple(sorted(v)[len(v) // 2] for v in vals)

    def _paper(pix):
        """The page's own background: the most common colour of a coarse sample."""
        counts = {}
        for y in range(0, pix.height, 7):
            for x in range(0, pix.width, 7):
                c = pix.pixel(x, y)
                counts[c] = counts.get(c, 0) + 1
        if not counts:
            return (255, 255, 255)
        return max(counts.items(), key=lambda kv: kv[1])[0]

    invented = 0
    invented_where = []
    page_pix = {}
    for i in range(min(src.page_count, gd.page_count)):
        try:
            g_drawings = gd[i].get_drawings()
        except Exception:
            continue
        candidates = []
        for d in g_drawings:
            r = d.get("rect")
            if r is None or r.is_empty:
                continue
            if d.get("fill") is None or (d.get("fill_alpha") or 1.0) <= 0.02:
                continue
            box = fitz.Rect(r)
            if box.width * box.height < BLANK_FILL_PT2:
                continue
            candidates.append((box, _rgb_of(d.get("fill"))))
        if not candidates:
            continue
        if i not in page_pix:
            page_pix[i] = src[i].get_pixmap(dpi=BLANK_DPI)
        pix = page_pix[i]
        paper = _paper(pix)
        scale = BLANK_DPI / 72.0
        for box, rgb in candidates:
            if _near(rgb, paper):
                continue                      # a fill the colour of the paper shows nothing
            inner = fitz.Rect(box.x0 + BLANK_INSET, box.y0 + BLANK_INSET,
                              box.x1 - BLANK_INSET, box.y1 - BLANK_INSET)
            if inner.is_empty:
                inner = box
            blank = total = 0
            for gx in range(BLANK_GRID):
                for gy in range(BLANK_GRID):
                    px = int((inner.x0 + inner.width * (gx + 0.5) / BLANK_GRID) * scale)
                    py = int((inner.y0 + inner.height * (gy + 0.5) / BLANK_GRID) * scale)
                    total += 1
                    if _near(_median3(pix, px, py), paper):
                        blank += 1
            if total == 0 or blank / float(total) < BLANK_CLEAR:
                continue
            invented += 1
            if len(invented_where) < 3:
                invented_where.append("%.0fx%.0f pt at %.0f,%.0f" % (
                    box.width, box.height, box.x0, box.y0))
        if invented and len(invented_where) >= 3:
            break
    if invented:
        print("61_blank_not_filled: %d fill(s) over paper the page leaves blank: %s"
              % (invented, "; ".join(invented_where)))
    # source is 0 by construction: this check exists for the places the page shows nothing,
    # and the page shows nothing in exactly the places it shows nothing.
    c["61_blank_not_filled"] = (0, invented, invented == 0)

    return c


def extra_checks(src, gd, s_runs, g_runs, pairs, docx_path=None):
    """Return checks 32-48. pairs is [(source_run, render_run), ...] already matched."""
    c = {}

    # ---- 32 stroke lines ---------------------------------------------------
    # A rule is a segment, not a drawing object; preserved means the same rule is on
    # the same page of the render. See _rules() for the definition, the calibration and
    # why isolation is asked of the source only. The verdict is a count of LOST RULES,
    # not a ratio of counts: a document with no isolated rule passes and says so with a
    # source of 0, rather than inventing a denominator out of table grid it does not own.
    s_rules = _doc_rules(src, isolated=True)
    g_segs = _doc_rules(gd, isolated=False, thin=RULE_THIN_REN, band=RULE_BAND_REN)
    _, s_lost = _rules_lost(s_rules, g_segs)
    c["32_stroke_lines"] = (len(s_rules), len(s_lost), not s_lost)

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
    # NO PAIRS IS SAID OUT LOUD, NOT SHOWN AS ZERO. With nothing paired all three reported
    # render=0 with ok=True, which on the page reads as a total style loss that passed.
    # 15_stamp_on_scanned_page is exactly that row (34b render 0, ok True, because the render
    # has no text at all - 31_pages_lost_their_text and 04 own that loss). The verdict is
    # right and stays: a document with no pairs has no style question left to ask.
    #
    # A MINIMUM SAMPLE WAS CONSIDERED AND REJECTED. 414_transparency_softmask fails 34b on 2
    # pairs and 411_nested_xobject_transforms fails 34a on 2, and a gate of n >= 10 was tried
    # on 13 Nov. It removed the check's only self-contained proof - test_checks' "one span
    # resized" and "one span recoloured" are 3-span fixtures and both stopped firing - and
    # nothing in the record shows either of those two verdicts is WRONG. A small denominator
    # is not evidence of a bad verdict, and 2 of 2 spans being recoloured is a true answer.
    tot = max(1, len(pairs))
    none = not pairs
    if none and s_runs:
        # `and s_runs` is load-bearing: all_check_ids() discovers the universe by comparing two
        # EMPTY documents, so an unconditional print here would land in --list-checks output
        # and be read as a check id.
        print("34a/34b/34c: no span paired, so size, colour and weight are unmeasured "
              "rather than zero")
    c["34a_span_size_match"] = (100, 0 if none else round(100 * ok_size / tot),
                                none or ok_size >= tot * 0.85)
    c["34b_span_colour_match"] = (100, 0 if none else round(100 * ok_col / tot),
                                  none or ok_col >= tot * 0.85)
    c["34c_span_weight_match"] = (100, 0 if none else round(100 * ok_weight / tot),
                                  none or ok_weight >= tot * 0.85)

    # ---- 35 rotation -------------------------------------------------------
    # 35_rotation: the rotated RUN, not a count of rotated lines.
    #
    # WHAT A COUNT MISSED. Counting rotated lines answers "how many", so six runs turned to
    # the wrong angle reads 6 -> 6 and passes, and six runs each rotated 90 degrees off reads
    # the same as six correct ones. Constructed 13 Nov: a 15-degree run redrawn at 90 degrees
    # passed the count. The defect is an ANGLE AND A PLACE, so the check has to name both.
    #
    # WHAT IT MEASURED UNTIL 14 NOV, AND WHY THAT WAS THE WRONG HOP. Each source run whose
    # baseline is not level had to find a RENDER run on the same page with the same normalised
    # text, within ROT_ANGLE_TOL and within 18's displacement clamp. The render cannot answer
    # that question. Measured 14 Nov on the 211-document corpus: `soffice --headless` writes
    # 0 lines with a non-level `dir` in ALL 211 renders, against 372 rotated lines in 30 source
    # documents, so the pairing set on the render side was empty and the check read kept=0 on
    # all 30 and failed all 30. The sweep proves it is a constant, not a threshold: at
    # ROT_ANGLE_TOL 0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 15.0, 45.0, 180.0 and 360.0 degrees the class
    # reads 30 every time. A check whose verdict does not move over the whole circle is
    # measuring the renderer's absence of a feature, not the engine's angle. This is the same
    # defect 53_embedded_faces and 54_image_dpi had, and the same fix: read the .docx.
    #
    # WHAT IT MEASURES NOW. Every source run whose baseline is not level must have an ANCHOR in
    # the engine's .docx, carrying that run's text, whose <a:xfrm rot> is within ROT_ANGLE_TOL
    # of the page's angle; and NO anchor in the .docx may carry an angle the page does not
    # draw (ROT_INVENTED_MAX = 0). Both clauses read the engine's own decision, which is the
    # only place the angle is observable.
    #
    # WHAT IT NO LONGER MEASURES, AND SAYS SO. The displacement clause is gone, not because it
    # was wrong but because the .docx cannot express it at this grain: one anchor holds a whole
    # stamp's several lines, so there is no per-run origin in the file to compare against the
    # page's. Position for rotated runs is 18's and 20_line_placement's question on the render;
    # this check now answers only the angle, which is what its name says. Dropping a clause it
    # cannot measure is honest; keeping one that reads 0.0 on every document is not.
    #
    # THE ANGLE TOLERANCE IS 2.0 DEGREES. The rotations this corpus actually carries are 7, 8,
    # 9, 11, 12, 13, 14, 15, 90, 110 and 180 degrees, plus curved seal text down to 1.4. Two
    # degrees is under a third of the smallest stamp rotation, so a run drawn at the wrong
    # angle cannot pass it, while a producer that quantises the angle slightly still does.
    # ONE THING TWO DEGREES CANNOT DO. The curved seal text (05, 305, 312, 318, 352, 371, 60)
    # is one run per glyph along an arc, and those runs carry angles down to 1.4 degrees. For
    # those, a 2-degree tolerance is "was it rotated at all", not "was it rotated correctly".
    # They are not silently forgiven: the 0.8 keep floor still has to be met over the whole
    # document, and measured at 2.0 every one of those documents fails. A tolerance tight
    # enough to judge them (under 1.4 degrees) would fail a producer that rounds the angle,
    # which is a different defect from losing the rotation.
    # MEASURED 14 Nov on 211 .docx: the corpus itself does not exercise the tolerance either
    # - the engine's anchors agree with the page's angle to 0.0 degrees exactly (12 anchors:
    # -15->345, -90->270, -8->352, -14->346, -12->348, -11->349, 15->15, 180->180, 9->9,
    # 11->11, 13->13), so the class reads 20 at every tolerance from 0.5 to 360.0 and 28 only
    # at 0.0, where float noise in atan2 (-14.999990224 against 345.0) fails two correct
    # anchors. That is the argument for a NON-ZERO tolerance, measured rather than assumed.
    # The tolerance earns its keep on the mutation matrix instead: an anchor shifted 10 degrees
    # is caught up to ROT_ANGLE_TOL 8.0 and escapes at 15.0, and one shifted 1 degree passes at
    # 2.0 by design. It is a floor on producer rounding, not a licence to be wrong.
    ROT_ANGLE_TOL = 2.0
    # The keep floor is a SHARE, not "all": a render may split one rotated run into two, and
    # 13's rule for a set (equality) is not available for a population that can be regrouped.
    # 0.8 of 6 is 4.8, so 3 of 6 kept FAILS - which is the constructed case this floor exists
    # to fail. It survives the move to the .docx unchanged: the engine writes ONE anchor per
    # stamp holding several lines, so a document with 2 rotated runs and 1 anchor is 2 of 2
    # kept, and a document that loses one run of four (08) is 3 of 4 against a floor of 4.
    ROT_KEEP_FLOOR = 0.8
    # A ROTATION THE PAGE DOES NOT DRAW IS A FAIL AT ZERO, not a tolerance. The user's rule is
    # "kisi bhi PDF ke stamps ko jabardasti rotate nhi karna": inventing an angle is the same
    # fault as dropping one, and it is the fault the render cannot see at all - LibreOffice
    # ignores <a:xfrm rot> on a text box (see D-13/D-16), so a fabricated 15 degrees renders
    # exactly like no rotation. Measured 14 Nov: adding rot="900000" to an unrotated anchor in
    # 34_monospace_document leaves the render with 0 rotated lines and the OLD check passes it;
    # the clause below fails it. On the corpus as built, this clause finds 0.
    ROT_INVENTED_MAX = 0

    def rot_runs(doc):
        out = []
        for i, p in enumerate(doc):
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    t = "".join(s["text"] for s in ln.get("spans", []))
                    if not t.strip():
                        continue
                    dx, dy = (ln.get("dir") or (1.0, 0.0))[:2]
                    if not (abs(dy) > 0.02 or dx < 0.98):
                        continue
                    sp0 = (ln.get("spans") or [{}])[0]
                    # THE ANCHOR IS THE BASELINE ORIGIN, not the box centre. A rotated
                    # line's bbox is axis-aligned, so its centre MOVES when the angle
                    # changes: constructed, the same run at 15 and 13 degrees has an
                    # identical origin and a bbox centre 1.6 pt apart, at 5 degrees off
                    # 4.0 pt apart. Measuring the box centre would leak the angle into
                    # the position clause and fail a run twice for one fault. 18 measures
                    # a run's baseline, and so does this.
                    org = sp0.get("origin")
                    if org is None:
                        org = ((ln["bbox"][0] + ln["bbox"][2]) / 2.0,
                               (ln["bbox"][1] + ln["bbox"][3]) / 2.0)
                    out.append({"page": i, "text": t, "nt": norm_text(t),
                                "angle": math.degrees(math.atan2(dy, dx)),
                                "org": (org[0], org[1]),
                                "bbox": ln["bbox"],
                                "size": (sp0.get("size") or 10.0)})
        return out

    s_rot = rot_runs(src)
    # A MIRRORED RUN IS NOT A ROTATED RUN. 417_rotate180_and_mirrored's page 2 is drawn under
    # "-1 0 0 1 595 0 cm", and the text layer reports its four runs at -180.0 degrees - the
    # same reading a 180-degree rotation gives - so this check demanded four 180-degree
    # anchors for text the page never turned. There is no anchor that could satisfy it: the
    # angle would have to turn the words upside down, which is a worse document than the one
    # the page draws, and the engine's own reading of the page (the characters in reading
    # order, upright, where the page puts them) is what a reader gets from a mirror anyway.
    # The page's CTM says which of the two it is; see page_mirrors_text.
    if s_rot:
        mirrored_pages = [i for i, p in enumerate(src) if page_mirrors_text(src, p)]
        if mirrored_pages:
            s_rot = [r for r in s_rot if r["page"] not in mirrored_pages]
    # A PAGE THE ENGINE RIGHTS ON PURPOSE IS NOT A PAGE OF LOST ANGLES - see
    # page_is_turned_round. The test is the engine's own, so the check and the converter agree
    # about which pages are sheets printed the wrong way up.
    if s_rot:
        turned_pages = [i for i, p in enumerate(src) if page_is_turned_round(p)]
        if turned_pages:
            s_rot = [r for r in s_rot if r["page"] not in turned_pages]
    d_rot = docx_rot_anchors(docx_path)
    if d_rot is None and s_rot:
        # UNMEASURED IS NOT A PASS - 54_image_dpi's rule, applied to the same kind of hop.
        # The render cannot answer this question (0 rotated lines in 211 of 211 renders), so
        # without a .docx there is nothing here that has a verdict to cast. It used to be
        # cast anyway: the render side read 0 kept and the check failed every document with
        # rotated text, which looked like a strict check and was in fact a blind one.
        print("35_rotation: FAIL - cannot measure. The source draws %d rotated run(s) and the "
              "render carries none, so the angle is only observable in the engine's .docx. "
              "Pass --docx <engine.docx>." % len(s_rot), file=sys.stderr)
        c["35_rotation"] = (len(s_rot), -1, False)
    elif d_rot is not None:
        kept = 0
        lost = []
        for r in s_rot:
            ang = r["angle"] % 360.0
            # THE TEXT IS THE PAIRING KEY AND THE ANGLE IS THE QUESTION. An engine anchor may
            # hold several of the page's lines (one stamp box = one anchor), so the test is
            # containment, not equality: a 2-line stamp whose anchor reads
            # "AUTHORISED SIGNATORYSUNRISE FASTENERS" carries both of its runs. What that
            # anchor may NOT do is carry a different angle - which is what the tolerance is
            # for, and what the mutation matrix in patches/35-rotation-docx.md measures.
            if any(_ang_diff(q[0], ang) <= ROT_ANGLE_TOL and r["nt"] and r["nt"] in q[1]
                   for q in d_rot):
                kept += 1
            else:
                lost.append(r)
        need = max(1, math.ceil(ROT_KEEP_FLOOR * len(s_rot)))
        src_ang = [r["angle"] % 360.0 for r in s_rot]
        invented = [q for q in d_rot
                    if not any(_ang_diff(q[0], a) <= ROT_ANGLE_TOL for a in src_ang)]
        if s_rot and kept < need:
            print("35_rotation: %d of %d rotated run(s) kept their angle in the .docx "
                  "(need %d, |d angle| <= %.1f deg). Lost: %s"
                  % (kept, len(s_rot), need, ROT_ANGLE_TOL,
                     "; ".join("%.1f deg %r" % (r["angle"], r["text"][:24])
                               for r in lost[:6])), file=sys.stderr)
        if len(invented) > ROT_INVENTED_MAX:
            print("35_rotation: %d rotation(s) in the .docx that the page does not draw "
                  "(allowed %d): %s"
                  % (len(invented), ROT_INVENTED_MAX,
                     "; ".join("%.1f deg %r" % (q[0], q[2][:24]) for q in invented[:6])),
                  file=sys.stderr)
        c["35_rotation"] = (len(s_rot), kept,
                            (not s_rot or kept >= need)
                            and len(invented) <= ROT_INVENTED_MAX)
    else:
        c["35_rotation"] = (0, 0, True)

    # ---- 36 underline / strike --------------------------------------------
    # No underline flag in the text model, so count thin strokes sitting just
    # under a baseline - an approximation, and named as one.
    # A RULE UNDER A BASELINE IS NOT AN UNDERLINE UNLESS IT IS THE TEXT'S OWN LENGTH.
    #
    # The old predicate asked only "is there a thin rule within 2.5 pt below this span and
    # does it overlap it horizontally". Measured on 211 documents on 22728b1: of the 21
    # documents that read a source count, NINETEEN carry no underline at all - the rule is a
    # table row separator, a masthead rule, a certificate's decorative rule, three music
    # staff lines, or the bottom edge of a P&ID tag box, 1.3 to 37 times the width of the
    # span that happens to sit above it. Only 44_coloured_underlined_hyperlinks (5 of 5
    # hits text-width) and 600_reviewed_invoice_with_annotations (1 of 4) carry one, and
    # both PASS. So the class read "cannot pass a document with underlines" on a population
    # that was 90 % documents without underlines.
    #
    # The test added below is the one 32_stroke_lines and 46_text_crossing_rule already
    # carry in another form: a rule that belongs to a span is about as long as the span and
    # starts where the span starts. 1.5x + 4 pt is loose on purpose - a hyperlink underline
    # can overhang its text - and it is measured, not chosen: on 44's five real underlines
    # the rule is 1.00x the span width and starts exactly at its left edge, and no document
    # in the corpus has a genuine underline that this rejects.
    def rules_under_text(doc, own_length=True):
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
                        span_w = x1 - x0
                        for st in lines:
                            r = st["rect"]
                            if not (y1 - 2.5 <= r.y0 <= y1 + 2.5 and r.x0 < x1 and r.x1 > x0):
                                continue
                            # ITS OWN LENGTH, ASKED OF THE SOURCE ONLY - the same rule
                            # 32_stroke_lines applies to isolation. The source decides what
                            # is an underline; the render only has to carry a rule under the
                            # same span, because the renderer re-derives the geometry and a
                            # rule it draws 1.6x wide is still that underline.
                            if own_length:
                                if r.x1 - r.x0 > span_w * 1.5 + 4:
                                    continue
                                if not (x0 - 4 <= r.x0 <= x0 + 4):
                                    continue
                            n += 1
                            break
        return n

    s_u = rules_under_text(src, own_length=True)
    g_u = rules_under_text(gd, own_length=False)
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

    # WHERE THE ATTRIBUTE LIVES, AND WHY THIS CHECK NO LONGER LOOKS AT THE RENDER.
    # A PDF has no superscript attribute. It has a font size and a baseline, and
    # `scripts()` above reads exactly those two numbers. Measured 13 Nov on a probe
    # document (probe.pdf, one page, seven rows): a run raised with the text-rise
    # operator `Ts` and a run at the SAME 7.10 pt size and the SAME 4.50 pt rise placed
    # by `Td` in its own text object are counted identically by `scripts()` - both read
    # r = -0.506 em and both are scored as one superscript. PyMuPDF's own superscript
    # flag agrees with neither distinction: it is set on both (flags & 1), and it is
    # also set on a FULL-SIZE span 0.30 em above its line
    # (academic-paper-ieee-2col-abstract) and on a full-size one 0.73 em above
    # (400_comic_page_speech_bubbles). The flag is a geometric heuristic, not an
    # attribute, so nothing on the source side can tell a script run from a merely
    # raised one.
    #
    # The only two places the attribute can exist are w:vertAlign and w:position in the
    # engine's .docx, and the engine writes neither (grep vertAlign over
    # app/src/main/java/com/kavopdf/app/engine: 0 hits). So the render-side count this
    # check used to make was asking the renderer a question the .docx never answered:
    # on journal-2col-with-footnotes the engine turns each of the 3 markers into its OWN
    # paragraph, positioned by w:spacing w:before, and the raise survives as paragraph
    # position to within 0.04 pt (source y 180.14 -> render 180.10) while no line in the
    # render holds two baselines at all (0 of 75). The old clause read that as 3 -> 0 and
    # failed a conversion whose vertical placement is right.
    #
    # So 37 reads the .docx. What it asks: for a source that drew script runs, does the
    # engine's file carry a vertical placement for them, and is that placement still
    # inside the run's own paragraph? A run with neither element is a small run on the
    # paragraph baseline - which is what a "superscript" that lost its attribute is.
    def docx_script_marks(path):
        """(runs carrying w:vertAlign or w:position, how many of those are alone)."""
        try:
            xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
        except Exception:
            return None
        flagged = alone = 0
        for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
            runs = re.findall(r"<w:r[ >].*?</w:r>", p, re.S)
            marks = [r for r in runs if "w:vertAlign" in r or "<w:position " in r]
            if not marks:
                continue
            flagged += len(marks)
            if len(runs) < 2:
                alone += len(marks)
        return flagged, alone

    s_sc = scripts(src)
    s_script = s_sc[0] + s_sc[1]
    marks = docx_script_marks(docx_path) if docx_path else None
    if s_script == 0:
        # Nothing to preserve. This pass is genuine and is the same one 53 and 54 take.
        c["37_super_subscript"] = (s_sc, 0, True)
    elif marks is None:
        print("37_super_subscript: FAIL - cannot measure. The source draws %d script run(s) "
              "and the .docx was not given, so whether the engine carried their vertical "
              "placement is unknown. The render cannot answer it: the engine expresses the "
              "raise as paragraph position, not as a run attribute. Pass --docx <engine.docx>."
              % s_script, file=sys.stderr)
        c["37_super_subscript"] = (s_sc, 0, False)
    else:
        d_flag, d_alone = marks
        ok = d_flag >= max(1, int(s_script * 0.9)) and d_alone == 0
        if not ok:
            print("37_super_subscript: %d script run(s) in the source, %d vertical placement(s) "
                  "in the .docx, %d of those alone in their paragraph"
                  % (s_script, d_flag, d_alone), file=sys.stderr)
        c["37_super_subscript"] = (s_sc, d_flag, ok)

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

    # Compared in the NORMALISED form (url_key), not as strings - see the URL
    # identity block above colour_same() for the seven constructed cases.
    # The strictness is unchanged: the source set and the render set must still be
    # the same set, so an invented target is still a failure. Only the SPELLING is
    # normalised.
    s_l, g_l = link_targets(src), link_targets(gd)
    s_k = {url_key(u) for u in s_l}
    g_k = {url_key(u) for u in g_l}
    kept = len(s_k & g_k)
    lost = sorted(s_k - g_k)
    extra = sorted(g_k - s_k)
    if lost:
        print("40_link_targets: %d target(s) lost, e.g. %s" % (len(lost), lost[0]))
    if extra:
        print("40_link_targets: %d target(s) the source does not carry, e.g. %s"
              % (len(extra), extra[0]))
    c["40_link_targets"] = (len(s_l), kept, not s_k or (not lost and not extra))

    # 41_block_spacing RETIRED 13 Nov - it measured the extractor's block segmentation,
    # not the page. Kept here as the record of what it was and why it is gone.
    #
    # What it read: the median gap between distinct text-BLOCK tops, page 1 only, against a
    # fixed 3.0 pt. Both halves of that are wrong.
    #
    # 1. A BLOCK IS NOT A PROPERTY OF THE PAGE. It is how the producer happened to group its
    #    text objects, and the source PDF and the LibreOffice render group them differently on
    #    97 of the 211 documents in corpus-v1 (measured on 22728b1). On 60 of those 97 the
    #    median landed within 3 pt anyway, so the check was blind to its own instability; on
    #    the rest it called the regrouping a defect. Both of its sole failures are exactly
    #    that:
    #      63_three_column_brochure  29 -> 27 blocks, 45 lines either side, body gaps equal to
    #                                0.1 pt; dropping one element moved the median's RANK
    #                                from 16.1 (6th of 11) to 25.2 (6th of 10)
    #      20_numbered_list_separate_column_txtpos  15 -> 23 blocks, 33 lines either side; the
    #                                render split each row into a 1.1 pt sliver plus its gap,
    #                                so the median fell 52.0 -> 24.7
    #    Neither document moved a line. 18_displacement, the displacement standard, passes both.
    #
    # 2. A MEDIAN IS A MAJORITY RULE, AND IT IS THE WRONG ONE HERE. One 10 pt gap defect,
    #    constructed and measured through this file: it fails a page of 2 blocks and a page of
    #    3, and PASSES at 4, 5, 6, 9, 12 and 20 blocks - because one bad gap out of n stops
    #    being the middle value as soon as n >= 4. That is the same ruler-for-document-length
    #    defect 18 was rewritten to remove (see its budget note above), and 23 was rewritten to
    #    remove. Reading page 1 only (doc[:1]) made it blind on top of that: the same 10 pt
    #    defect on page 2 of a two-page document reads 0.0 and passes.
    #
    # 3. IT DECIDED NO DOCUMENT'S VERDICT. Over 211 documents it failed 39; 37 of those were
    #    already failed by another check, and the 2 it failed alone are the segmentation
    #    artefacts above. Same test that retired 21_median_dx (see above): a check that decides
    #    nothing on its own is a second vote on someone else's question.
    #
    # It is not redefined, because it cannot be: "block" is not identifiable across two
    # producers, so no pairing rule can make a block-gap statistic mean the same thing on both
    # sides. Vertical rhythm is asked where it IS identifiable - 23_line_pitch pairs LINES by
    # text on the baseline within one column, and 18_displacement owns every per-line dy,
    # including the tails a median is blind to.

    # ---- 42 justification edges -------------------------------------------
    # 42_alignment_mix IS RETIRED. It could not answer its own question, and the
    # measurement is in /scratch/output/42-reference-report.md. The short form:
    #
    #   The check classified every qualifying line as left, right or centred
    #   against a reference derived PER PAGE AND PER SIDE from the mode of the
    #   page's BLOCK bboxes (`statistics.mode([round(b["bbox"][0]) ...])`). A
    #   block bbox is a segmentation artefact: PdfToWord and the renderer group
    #   the same glyphs into different blocks, so the reference is not a property
    #   of the page and not even the same quantity on the two sides.
    #
    #   Measured on all 211 documents with six defensible references - mode of
    #   block bbox (shipped), union bbox of the blocks, mode of line bbox, mode of
    #   span bbox, union bbox of the lines, and the page rect - the failure sets
    #   are 24, 29, 34, 34, 29, 0 and they are NOT NESTED. Their intersection is
    #   EMPTY: no document in corpus-v1 fails this check under all six, so there
    #   is no document the check convicts whatever reference you pick. Their union
    #   is 56 of 211. A check whose answer depends on which of six defensible
    #   references you pick is measuring the reference, not the document.
    #
    #   There is no reference that is a property of the PAGE. A PDF records no
    #   text frame; the only page-intrinsic horizontal landmarks are x0, x1 and
    #   the centre of the MediaBox. Using them (`page_rect`) buckets 789 of the
    #   corpus's 15,261 qualifying source lines - 5 % - and fails 0 of 211, i.e.
    #   it returns the same answer for every document and measures nothing. The
    #   text margin is a layout decision recorded nowhere in the file. For
    #   comparison the retired reference buckets 7,087 of the same 15,261, 46 %,
    #   so 53.6 % of the corpus's lines were in no bucket at all.
    #
    #   On the shipped reference 21 of the 24 failures have ZERO paired lines
    #   whose justification changed, and 9 of the 24 have a reference narrower
    #   than half the page's own text width (17 reads 18 pt against a 490 pt text
    #   extent; 31 reads 8 pt; 65 reads 11 pt). Two documents - 31 and
    #   20_numbered_list_separate_column_txtpos - have a render reference under
    #   10 pt, so the page is skipped, the render mix is empty, and
    #   `g_share = [0.0, 0.0, 0.0]` judges the document at "0 % left" against a
    #   source that is 86 % left. That is not a misalignment; it is a division by
    #   a reference that does not exist.
    #
    # WHAT REPLACES IT. Not a better column. The question "which of three buckets
    # is this line in, relative to a column I inferred from this document" has no
    # invariant answer, so it is not asked. The question the two PDFs CAN settle
    # between them is asked instead: a line that is flush left in the source must
    # still be flush left in the render, and likewise right and centred.
    #
    #   - lines are PAIRED BY THEIR OWN TEXT (unique on both sides, within a
    #     page), so a line is compared with itself and not with a page-level share;
    #   - "flush" is read off each page's own line set as an EXTREME - minimum x0,
    #     maximum x1 - at 1 pt, plus two centred tests (the page's modal line
    #     centre, and symmetry within the page's own extent). Extremes are
    #     attained by construction and are identical under five of the six
    #     references; a MODE of a block grouping is not;
    #   - a line that neither side can classify ("-") makes no claim, so a
    #     document is never failed for a line the instrument cannot read.
    #
    # The report's number is the count of CONTRADICTED pairs; the document fails
    # when that reaches max(3, 2 % of the pairs). The floor stops a two-line
    # document being judged on one line; the rate stops a 900-line document being
    # judged on three.
    #
    # Measured on the same 211 documents: 2 failures, against 24 - and it fires on
    # a single block realigned by hand (34_monospace_document, one block flushed
    # right: drift 0.000, PASS under the retired check; 4 contradictions, FAIL
    # here) which the retired check cannot see at all, because a line that leaves
    # all three buckets simply stops being counted and the SHARE does not move.
    JE_TOL = 1.0
    JE_FLOOR = 3
    JE_RATE = 0.02

    def _je_lines(pg):
        # LEFT and RIGHT are reading-space edges, not device edges. On a 180-degree page the
        # device left edge is the reading RIGHT edge, so a mirrored page read as a pure L-to-R
        # flip of every line and 42 charged the rotation as a justification change.
        out = []
        pw, ph = pg.rect.width, pg.rect.height
        for b in pg.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            for ln in b.get("lines", []):
                _a = math.degrees(math.atan2(ln.get("dir", (1, 0))[1],
                                             ln.get("dir", (1, 0))[0]))
                _fr = reading_frame(_a, pw, ph)
                # + cx puts the level case back on the device axis (rx + cx = x) and turns
                # the 180 case into the mirror W - x. The centre must NOT stay subtracted:
                # this check buckets a line by round(midpoint) and takes the MODE, and a
                # constant shift moves every midpoint across a rounding boundary, so the
                # mode - and therefore the bucket of 7 lines - changed on a document that had
                # not moved (newsletter-3col-header-footer read 0 -> 6 contradicted pairs).
                _cx = _fr[0]
                _p0 = rproj(ln["bbox"][0], ln["bbox"][1], _fr)
                _p1 = rproj(ln["bbox"][2], ln["bbox"][3], _fr)
                lx0 = min(_p0[0], _p1[0]) + _cx
                lx1 = max(_p0[0], _p1[0]) + _cx
                if lx1 - lx0 < 10:
                    continue
                t = " ".join(" ".join(sp["text"] for sp in ln["spans"]).split())
                if t:
                    out.append((t, lx0, lx1))
        return out

    def _je_class(lines):
        if not lines:
            return []
        xmin = min(l[1] for l in lines)
        xmax = max(l[2] for l in lines)
        cmode = statistics.mode([round((l[1] + l[2]) / 2.0) for l in lines])
        out = []
        for _t, lx0, lx1 in lines:
            if lx0 - xmin <= JE_TOL:
                out.append("L")
            elif xmax - lx1 <= JE_TOL:
                out.append("R")
            elif (abs((lx0 + lx1) / 2.0 - cmode) <= JE_TOL
                  or abs((lx0 - xmin) - (xmax - lx1)) <= JE_TOL):
                out.append("C")
            else:
                out.append("-")
        return out

    je_pairs = je_con = 0
    for pi in range(min(len(src), len(gd))):
        s_l = _je_lines(src[pi])
        g_l = _je_lines(gd[pi])
        s_c = _je_class(s_l)
        g_c = _je_class(g_l)
        s_ix, g_ix = {}, {}
        for i, t in enumerate(x[0] for x in s_l):
            s_ix.setdefault(t, []).append(i)
        for i, t in enumerate(x[0] for x in g_l):
            g_ix.setdefault(t, []).append(i)
        for t, si in s_ix.items():
            gi = g_ix.get(t)
            if len(si) != 1 or not gi or len(gi) != 1:
                continue
            je_pairs += 1
            a, b = s_c[si[0]], g_c[gi[0]]
            if a != "-" and b != "-" and a != b:
                je_con += 1
    je_need = max(JE_FLOOR, int(JE_RATE * je_pairs + 0.999))
    # reported: contradicted pairs, the count it had to reach, and the verdict
    c["42_justification_edges"] = (je_con, je_need, je_con < je_need)

    # ---- 43 horizontal placement ------------------------------------------
    # The old 21_median_dx only looked at the median, which hides a whole column
    # shifted. This asks how many spans are horizontally close, span by span.
    #
    # 21_median_dx IS FOLDED IN HERE, not merely dropped. A uniform shift of the whole
    # document moves every span by the same amount, so a 4.3 pt shift leaves every span
    # inside the 10 pt window and this check read 91 % and PASSED (constructed 13 Nov;
    # 375_attendance_register is the same shape at 4.3 pt). The median is the document-level
    # clause a per-span window structurally cannot see, and it is the one thing 21 answered
    # that 43 did not - so 43 carries it now and 21 has no question of its own left.
    near_x = sum(1 for s_sp, g_sp in pairs
                 if abs(g_sp.get("rxink", g_sp["rx"]) - s_sp.get("rxink", s_sp["rx"])) <= 10)
    tot_p = max(1, len(pairs))
    ddx = [g_sp["rx"] - s_sp["rx"] for s_sp, g_sp in pairs]
    med_dx_p = round(statistics.median(ddx), 1) if ddx else 0.0
    c["43_within_10pt_x"] = (100, round(100 * near_x / tot_p),
                             ((not pairs) or near_x >= tot_p * 0.9)
                             and abs(med_dx_p) < 3.0)

    # ---- 44 header / footer ------------------------------------------------
    #
    # THE OLD PREDICATE, STATED EXACTLY (it is replaced below, not tuned):
    #   population  every block of get_text("dict")["blocks"] with type 0 whose bbox TOP y
    #               satisfies  y < H*0.10  or  y > H*0.90  (H = that page's rect height),
    #               on every page, with the block's spans concatenated and whitespace
    #               collapsed; no page index is carried.
    #   predicate   every such source string must equal some render band string, or be a
    #               substring of one, or reach difflib ratio >= 0.9 against one - where the
    #               render pool is again the band blocks of the whole document.
    #   verdict     c["44"] = (len(source band strings), matched, not missing).
    #
    # TWO THINGS ARE WRONG WITH IT, AND BOTH ARE MEASURED ON THE 211.
    #
    # 1. A BLOCK IS NOT A DOCUMENT OBJECT. It is the extractor's grouping, and the source and
    #    the render group differently. On the 50 documents this check failed, the 272 source
    #    band blocks are: 151 present as one render block, and 121 not - of which 68 have
    #    every character present at the SAME y inside a differently-cut block and 53 have
    #    them elsewhere on the page (window +-6 pt; measured, scripts in the patch notes).
    #    Not one of the 272 has a character missing from its page. The check was reading the
    #    segmentation, not the conversion.
    #
    # 2. IT CANNOT SEE THE THING IT IS NAMED AFTER. A header is a header because it REPEATS,
    #    and this predicate has no page index, so repetition is not in it at all. 192 of the
    #    211 documents have a single page, where repetition is structurally impossible - and
    #    44 of the 50 failures are on exactly those documents. Meanwhile it PASSES
    #    mutual-fund-statement, which loses its footer on page 2 (811.4 pt -> 123.2 pt), and
    #    FAILS gst-invoice-multipage-item-table, whose headers and footers are all carried at
    #    the source y on all four pages. Its verdict disagrees with the truth in both
    #    directions, which is what a check looks like when it is asking the wrong question.
    #
    # SO: THE POPULATION IS NOW THE ONE THE NAME PROMISES. Band LINES that repeat on two or
    # more pages of the source, digit-normalised so that a page number is the same element on
    # every page. The band constants are unchanged (0.10 / 0.90, and still on the line's bbox
    # top, which is what keeps 416_many_tiny_pages - header top 0.30 pt inside the cut - from
    # moving: a centre-of-block rule was measured at 50 -> 51 and all-pass 29 -> 28, because
    # it puts that header outside). Measured: 16 documents, 79 repeating lines, 615
    # element-pages. The other 195 documents have no repeating element and this check has
    # nothing to say about them - 44 of its 50 old failures live there.
    #
    # AND THE PREDICATE IS THE ONE A FLOW CONVERTER CAN ANSWER. It cannot promise a w:hdr
    # part: it writes none (0 header/footer parts across all 211 docx) and in this design it
    # cannot, because sectPrXml (DocxWriter.java:1790) emits pgMar top/right/bottom/left = 0
    # so the text area IS the page and a part is subtracted from the body. Measured by
    # injecting a real header part into bank-statement-5-pages: every body line moves
    # +10.9 pt, and paying for it with real section margins moves the body by the whole top
    # margin instead (+92.5 pt, and 354 of 525 body lines can no longer be found at all).
    # What it CAN promise is what the flow actually delivers: the text is still on that page,
    # and it is still in the margin band - or, if it drifted just past the band edge, that it
    # barely moved. Both clauses are needed and neither is a tolerance invented here: the
    # band is this check's own 0.10/0.90, and the 2x displacement budget is 18_displacement's
    # TAIL_FACTOR (see _tol() below) so a header that 18 already forgives is not failed here.
    def text_lines(doc):
        out = []
        for pi, p in enumerate(doc):
            H = p.rect.height
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    t = " ".join("".join(sp["text"] for sp in ln["spans"]).split())
                    if not t:
                        continue
                    y = ln["bbox"][1]
                    out.append({"page": pi, "y": y, "frac": y / H, "text": t,
                                "size": max((sp["size"] for sp in ln["spans"]), default=0.0)})
        return out

    def _band(l):
        return l["frac"] < 0.10 or l["frac"] > 0.90

    def _same(a, b):
        # Unchanged from the old _present: a line either is the string, contains it, or is
        # within 0.9 of it. Kept because a re-wrapped header is the same header.
        return (a == b or a in b or b in a
                or difflib.SequenceMatcher(None, a, b).ratio() >= 0.9)

    def _44tol(size):
        # 18_displacement's own per-run budget, times its TAIL_FACTOR.
        return 2.0 * min(max(0.35 * size, 1.5), 4.5)

    s_ln, g_ln = text_lines(src), text_lines(gd)
    s_band = [l for l in s_ln if _band(l)]
    g_by = {}
    for l in g_ln:
        g_by.setdefault(l["page"], []).append(l)

    def _find(l, placed):
        for c in g_by.get(l["page"], []):
            if not _same(l["text"], c["text"]):
                continue
            if not placed:
                return c
            if _band(c) or abs(c["y"] - l["y"]) <= _44tol(l["size"]):
                return c
        return None

    grp = {}
    for l in s_band:
        grp.setdefault(("top" if l["frac"] < 0.10 else "bot",
                        re.sub(r"\d+", "#", l["text"])), []).append(l)
    rep = [l for v in grp.values() if len({x["page"] for x in v}) >= 2 for l in v]
    lost = [l for l in rep if _find(l, True) is None]
    # The completeness clause. Without it the check would be silent on 195 documents, and a
    # band line dropped from the page entirely is a real loss whether or not it repeats:
    # 350_question_paper loses 9 (an exam paper whose footer column never reached the render)
    # and itr-computation-with-slab-table loses 2 to a 1 -> 2 page overflow. Text that moved
    # but is still on its page is 18_displacement's question, not this one's.
    dropped = [l for l in s_band if _find(l, False) is None]
    # The reported pair is "N band elements made a claim, M were honoured". A document with a
    # repeating element is judged on the repeating lines (the header question); one without
    # is judged on its band lines (the completeness question). A single pair that always
    # means the same thing, rather than 0/0 on a document that failed.
    claim, unmet = (rep, lost) if rep else (s_band, dropped)
    c["44_header_footer"] = (len(claim), len(claim) - len(unmet), not lost and not dropped)

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
        # C0 CONTROLS ARE NOT CHARACTERS A RENDER CAN CARRY. norm_word() strips them with
        # its own comment - six documents in corpus-v1 hold U+0000 in their text layer - and
        # this line did not, so 406_passport_mrz_page was charged for 8 NULs that no
        # renderer can draw: 431 of 448 reads 96, 431 of 440 reads 98. Invisible control
        # characters are not "character accuracy", they are the extractor's opinion of the
        # file, and counting them here measures the source, not the conversion.
        return re.sub(r"[\s\u00a0\x00-\x1f\x7f]+", "", "".join(r["text"] for r in rs))

    # AND IT WAS STILL MEASURING ORDER, WHICH IS NOT ITS QUESTION. Measured 13 Nov on a probe
    # carrying one ligature, one combining mark, one Arabic word with a fathatan, one
    # Devanagari cluster, a bullet, a checkbox and five maths signs: all 360 glyphs are in the
    # render, each exactly once (multiset difference empty in both directions), and the
    # sequence ratio reads 95.83 - a FAIL. Two causes, both in the extractor, neither in the
    # document:
    #
    #   run splitting   a glyph the named face does not carry is drawn from a fallback face,
    #                   so the renderer emits it as its own run. It lands at the right x on the
    #                   right baseline, but the extractor returns it AFTER the rest of the
    #                   line. Measured: the 10 fallback glyphs alone take the pair from 95.83
    #                   to 98.29.
    #   bidi            a source PDF's text layer holds Arabic in VISUAL order, a render holds
    #                   it in LOGICAL order: the same 10 characters, reversed. Measured: the
    #                   10 Arabic characters alone take the pair from 95.83 to 97.43.
    # Remove both and the same pair reads 100.00. Neither is a lost character, and neither is
    # this check's question - 22_reading_order owns order and read PASS on the same pair.
    #
    # So the verdict is the multiset, which is what "character accuracy" says it is, and the
    # sequence ratio is kept as a number that can be printed but never decides. NFKC first,
    # because a producer's ligature U+FB01 and an extractor's expansion "fi" are one glyph to
    # a reader and two characters to a Counter; the same fold turns Arabic presentation forms
    # back into the letters they stand for.
    def _canon(s):
        return unicodedata.normalize("NFKC", s)

    s_cs, g_cs = _canon(_glyphs(s_runs)), _canon(_glyphs(g_runs))
    common = sum((collections.Counter(s_cs) & collections.Counter(g_cs)).values())
    ratio = round(100 * common / max(1, max(len(s_cs), len(g_cs))))
    if os.environ.get("P2W_45_SEQUENCE"):
        print("45_char_accuracy: multiset %d %%, sequence %d %%"
              % (ratio, round(100 * difflib.SequenceMatcher(None, s_cs, g_cs,
                                                            autojunk=False).ratio())),
              file=sys.stderr)
    c["45_char_accuracy"] = (100, ratio, ratio >= 97)

    # ---- 46 text crossing a rule (per span) --------------------------------
    # WHAT THIS USED TO ASK. "Does the render count more rules inside text boxes than the
    # source?" with a 20 % allowance: `g_c <= s_c + s_c // 5`. Two COUNTS, so it cannot say
    # which of the two moved, and on the 211 it never says the thing it exists to say.
    # Measured (engine 23ffa25, LibreOffice's render of the engine's own .docx): it fails 7
    # documents, and 0 of the 7 is a rule drawn through text that should not have one.
    #   34 of the 42 render crossings are a rule the source drew at the SAME y (0.2-0.6 pt)
    #     with the TEXT moved onto it by 6.2-10.0 pt - 18_displacement's question.
    #     payslip-label-left-amount-right: 12 crossings, rule unmoved to 0.3 pt, text down
    #     6.2-10.0 pt. bank-statement-horizontal-rules-only: 13 crossings, same shape.
    #   4 are on a render page the source does not have - itr-computation-with-slab-table,
    #     whose table the render pushed onto a second page (01_page_count 1 -> 2).
    #   3 are the same ink re-segmented: 60_page_border counts ONE 48 pt tall span in the
    #     source and TWO spans in the render, so one rule reads as two crossings.
    #   1 is a 2.1 pt text shift: 311_fir_police_form.
    # Constructed (mutation matrix, /scratch/work/mutation.py, one change per document):
    # a rule moved 10 pt into text and a rule drawn through the middle of a word both read
    # fail, which is the question; TEXT moved 12 pt onto a rule the source already drew
    # reads fail too, which is not the question and is the same confusion the corpus shows.
    #
    # WHAT IT ASKS NOW. Rule by rule: is any rule inside a text box that had none? A render
    # crossing is NEW only when the text did not move AND the rule crossing it is not a
    # source rule that already crossed text. So:
    #   a rule moved into text          NEW  - no source rule at that y          -> fails
    #   a rule drawn through a word     NEW  - no source rule at all             -> fails
    #   text moved onto a source rule   not  - the text is not registered        -> 18 owns it
    #   a source crossing preserved     not  - the source counted this rule     -> passes
    #   a rule deleted                  not  - nothing crosses                  -> 32 owns it
    # On the 211 this reads 0 documents failing, and it still fails both constructed
    # crossings above. XTEXT_DY is 18_displacement's own FLOOR, so the line between "the
    # text moved" and "the rule moved" is the house standard's, not a new number. XRULE_DY
    # is 4.0 pt and not 32_stroke_lines' 24 pt on purpose: 24 is right for "did this rule
    # survive", and wrong here - a rule that moved 10 pt has survived and is now through a
    # line of text.
    XRULE_DY = 4.0     # a render rule is the source's own rule within this of its own y
    XTEXT_DY = 1.5     # ... and the text is registered within this of where it was set
    XRULE_OV = 0.80    # ... covering this share of the shorter of the two rules

    def x_spans(doc):
        out = {}
        for i, p in enumerate(doc):
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        t = sp.get("text", "").strip()
                        if t:
                            out.setdefault(i, []).append((sp["bbox"], t))
        return out

    def x_rules(doc):
        return {i: [s for s in _strokes(p) if s["rect"].height <= 2.5]
                for i, p in enumerate(doc)}

    def x_crossings(doc):
        """One hit per span, `break`, height <= 2.5, 1.5 pt inset - the old predicate."""
        out = []
        for i, p in enumerate(doc):
            lines = [s for s in _strokes(p) if s["rect"].height <= 2.5]
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        t = sp.get("text", "").strip()
                        if not t:
                            continue
                        x0, y0, x1, y1 = sp["bbox"]
                        for st in lines:
                            r = st["rect"]
                            if r.y0 > y0 + 1.5 and r.y0 < y1 - 1.5 and r.x0 < x1 and r.x1 > x0:
                                out.append((i, (x0, y0, x1, y1), t, r))
                                break
        return out

    def x_text_at(spans, page, text, bbox):
        """The source span carrying this text nearest this place, or None."""
        best, bd = None, None
        for bb, t in spans.get(page, ()):
            if t != text:
                continue
            d = abs(bb[1] - bbox[1]) + 0.25 * abs(bb[0] - bbox[0])
            if bd is None or d < bd:
                best, bd = bb, d
        return best

    def x_rule_here(r, cands):
        """The source rule this render rule is, or None."""
        L = r.x1 - r.x0
        for s in cands:
            sr = s["rect"]
            ov = min(sr.x1, r.x1) - max(sr.x0, r.x0)
            if ov <= 0 or ov < XRULE_OV * max(1e-6, min(L, sr.x1 - sr.x0)):
                continue
            if abs(sr.y0 - r.y0) <= XRULE_DY:
                return s
        return None

    s_sp, s_rl = x_spans(src), x_rules(src)
    s_x, g_x = x_crossings(src), x_crossings(gd)
    had = set((i, round(r.x0, 1), round(r.y0, 1), round(r.x1, 1)) for i, _, _, r in s_x)
    g_new = 0
    for i, bb, text, r in g_x:
        sb = x_text_at(s_sp, i, text, bb)
        if sb is None or abs(sb[1] - bb[1]) > XTEXT_DY:
            continue                      # the text moved: 18_displacement's question
        m = x_rule_here(r, s_rl.get(i, ()))
        if m is None:
            g_new += 1                    # a rule the source does not draw there
            continue
        if (i, round(m["rect"].x0, 1), round(m["rect"].y0, 1),
                round(m["rect"].x1, 1)) not in had:
            g_new += 1                    # the source's own rule, but it crossed no text
    s_c, g_c = len(s_x), g_new
    c["46_text_crossing_rule"] = (s_c, g_c, g_c == 0)

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
    #
    # (d) THE LEFT EDGE WAS THE PEN, NOT THE INK. Every x in this file came from a span's
    #     bbox, and a span's bbox starts at its first glyph's ORIGIN. A space advances the
    #     pen and draws nothing, so a source that writes "    (a) Salary" reports its left
    #     edge 8.6 pt left of the first letter - and the engine, which reads a cell's text
    #     at its first VISIBLE glyph (PdfToWord.glyphFirstX, and visibleX for a line),
    #     writes w:ind for the whitespace and emits the text without it. The render
    #     therefore draws the ink exactly where the page drew it, and this check charged it
    #     8.6 pt for the spaces. Measured on 211: 49 documents failed, 8 of them for this
    #     and nothing else (form16-part-b and itr-computation-with-slab-table are the two
    #     the brief named as a cell-inset defect - they are 4 spaces of 2.002 pt each, and
    #     the residual is 0.6 pt). The measurement is now ink to ink on both sides.
    #     Constructed (case-build2.py, shipped with this patch): a source with "    (a) ..." against the same page
    #     with the spaces dropped reads 6 unregistered runs here and none after the change,
    #     and against the same page with the indent genuinely moved 9 pt it still reads 6.
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

    def page_lefts(doc):
        """[(page index, the body's left edge, how many lines the page has), ...]

        Only the anchor is taken from the page now. The per-line registration below is
        measured on the caller's matched runs, not on this page's raw left edges.

        The edge is the line's INK, for the reason 47(d) states: a line that begins with
        an indent written as spaces has a pen left of anything it draws, and the anchor
        would then be a place no reader sees.
        """
        out = []
        for pi, p in enumerate(doc):
            xs = []
            for blk in p.get_text("rawdict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    if not "".join(c.get("c", "") for sp in ln.get("spans", [])
                                   for c in sp.get("chars", [])).strip():
                        continue
                    # A turned line is not part of the body's left edge. On
                    # 15_stamp_on_scanned_page the page's ONLY text is a 9-degree stamp,
                    # and the anchor became that stamp's x (337 against the render's 138);
                    # on one-page-rotated-180-degrees page 2 every line is turned 180 and
                    # the "margin" was the mirrored column of a rotated sheet. A page with
                    # no upright line has no body margin, and the clause says nothing
                    # about it rather than comparing two stamps.
                    _dx, _dy = ln.get("dir", (1, 0))
                    if abs(math.degrees(math.atan2(_dy, _dx))) > 1.0:
                        continue
                    xs.append(min(ink_box(sp, ln)[0] for sp in ln.get("spans", [])))
            out.append((pi, anchor(xs), len(xs)))
        return out

    margin_bad, indent_bad = [], []
    worst_med = worst_tail = 0.0

    # ---- (a) the margin itself: the page's anchor left edge ------------------
    for (pi, s_ml, _sn), (_, g_ml, _gn) in zip(page_lefts(src), page_lefts(gd)):
        if s_ml is not None and g_ml is not None and abs(s_ml - g_ml) > LM_TOL:
            margin_bad.append((pi + 1, s_ml, g_ml))

    # ---- (b) the indent structure: every matched run's left edge -------------
    # MEASURED ON THE MATCHED RUNS, NOT ON A ROW-LOCAL SET DISTANCE.
    #
    # The set distance was a VERTICAL check wearing a horizontal ruler. It paired each
    # source line with the render line whose left edge was nearest ON THE SAME ROW, where
    # "same row" was +-max(2, 0.35 * h) pt of that line's centre y; when no render line was
    # on the row it fell back to EVERY render line on the page. A vertical displacement of
    # a few points therefore became a horizontal distance to an unrelated line. Measured on
    # the 211 (the corpus, the engine at 22728b1, LibreOffice's render):
    #
    #   purchase-order   the footer "Page 1 of 1" is at x=520.0 in the source and x=520.1
    #                    in the render - 0.1 pt out horizontally - but 2.5 pt low. The row
    #                    window on that line is max(2, 0.35 * 6.4) = 2.24 pt, so it missed,
    #                    the fallback returned the nearest left edge on the page (42.6),
    #                    and the check reported a 477.4 pt margin error. All 106 of that
    #                    document's matched runs are within 0.67 pt horizontally.
    #   the same footer  electricity-bill, eway-bill, salary-slip-factory-wages,
    #                    property-tax-receipt and purchase-order all report exactly 477.4:
    #                    five documents, one shape. Across the 82 failures, 201 of the 202
    #                    unregistered lines that the render holds AT THE SAME x are beyond
    #                    the row window vertically, and 43 of the 82 are decided by such a
    #                    line.
    #   dropping the fallback does not fix it. When the footer's own counterpart is 2.5 pt
    #                    low, a BODY line standing on the footer's row is in the row set and
    #                    sits at x=42.6. Constructed (construct2.py): one body line on the
    #                    footer's row, the footer 3.9 pt low, nothing moved horizontally at
    #                    all - and the check reports (0.0, 1) and FAILS.
    #
    # The pairing is the caller's `pairs`: one-to-one, page-constrained, text-matched and
    # claimed nearest-first (see the assignment in compare()). It is the same evidence 43
    # and 18 are built on, so this clause now asks its question of the same material they
    # do instead of inventing a second, weaker pairing of its own.
    #
    # The worst-run cap needs CORROBORATION. One run out is a pairing artefact - a
    # duplicated word can still claim a distant occurrence - so a single outlier is not a
    # displacement; two are. Measured: with the cap unconditional, 370_offer_letter fails
    # on 1 of its 37 runs at 43.0 pt and 69_two_col_legal_numbered_clauses on 1 of 51 at
    # 239.2 pt; both are clean at every other run.
    DX_MIN_PAIRS = 5        # below this many matched runs a page is not judged on a count
    # INK TO INK. xink is the first glyph that puts ink on the page (see ink_box()), so
    # the leading whitespace a source draws and a renderer drops is no longer a
    # displacement. It is the same edge the engine places text by, so the two sides of
    # this subtraction now mean the same thing. Falls back to x for any run whose producer
    # recorded no glyph boxes.
    # WHICH PAIRS THIS CLAUSE MAY JUDGE. Two filters, each for a measured reason.
    #
    # (i) UPRIGHT ON BOTH SIDES. A curved seal draws 59 glyphs at 59 angles; the render
    #     flattens the arc into one horizontal run. Subtracting the two x values is
    #     subtracting a point on a curve from a point on a straight line - it is not a
    #     displacement and no engine change can make it zero. Measured on the 31 failures
    #     of corpus-v1: dropping the turned pairs closes 8 of them (03_stamp_vertical_90deg,
    #     05_round_company_seal, 305, 312, 318, 352, 371, 401_trifold) and moves no
    #     document the other way. This is the same test 18_displacement already applies -
    #     "no single UPRIGHT run may be more than twice its own tolerance out".
    #
    # (ii) NOTHING ELSE. A merged-run pair - the render writing as one span what the source
    #     drew as several, so g_sp is a PIECE with its x taken from the render's own glyph
    #     boxes (see _inside) - IS JUDGED, because that x is exact: it is where the render
    #     really drew the characters, so the difference is a real horizontal displacement
    #     and not an estimate. Excluding those pairs was tried and rejected on 14 Nov: it
    #     takes 21_form_labels, 40_devanagari, 64_newspaper, 76_devanagari_table and
    #     magazine-2col to a pass, and 43_within_10pt_x - the only other check that reads
    #     the same pairs - already fails 2 of those 5 and passes the other 3. So the
    #     exclusion would blind the instrument on three documents to save five.
    by_page = collections.defaultdict(list)
    for s_sp, g_sp in pairs:
        if abs(s_sp.get("angle", 0.0)) > 1.0 or abs(g_sp.get("angle", 0.0)) > 1.0:
            continue
        by_page[s_sp["page"]].append(g_sp.get("xink", g_sp["x"]) -
                                     s_sp.get("xink", s_sp["x"]))
    for pg, dd in sorted(by_page.items()):
        if len(dd) < DX_MIN_PAIRS:
            continue
        out = [v for v in dd if abs(v) > DX_MED_TOL]
        budget = max(DX_TAIL_MIN, int(round(DX_TAIL_SHARE * len(dd))))
        worst_med = max(worst_med, statistics.median([abs(v) for v in dd]))
        worst_tail = max(worst_tail, float(len(out)))
        if len(out) > budget or (len(out) >= 2 and max(abs(v) for v in dd) > DX_WORST_TOL):
            indent_bad.append((pg + 1, len(out), round(max(abs(v) for v in dd), 1)))

    # Reported as (worst page median, worst page unregistered-run count, ok). The page
    # numbers and the actual edges are in margin_bad / indent_bad so a failure can be read
    # without re-running: "47_margins: pages 3,7 left edge 56->48" is what a fixer needs.
    c["47_margins"] = (round(worst_med, 1), int(worst_tail),
                       not margin_bad and not indent_bad)
    # A detail check would be counted as a check: all_check_ids() discovers ids by running
    # the verifier, so a second key here would add a free pass to every document's score.
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


# ---- 53's face vocabulary ---------------------------------------------------
# Hoisted out of compare() on 13 Nov so the table and the two counters can be
# imported and tested: a forgiveness table is the one thing in this file that can
# hide a defect, and a table that can only be read by running the whole comparison
# is a table nobody checks. Bodies unchanged.
SAME_FACE = {
    # A FORGIVENESS, AND THE TWO RULES THAT LIMIT IT.
    #
    # The table says: text this PDF drew in family K may be carried in the .docx under
    # family V, and that counts as the face surviving. Every entry is a rename the ENGINE
    # performs - DocxWriter.BASE14 (DocxWriter.java:4798-4816) - and every entry joins two
    # faces that are the same face at the same width. That is the whole rule:
    #
    #   1. IT MUST BE A RENAME THE ENGINE PERFORMS. A name the engine never writes is a
    #      name this table could only be forgiving in the abstract, and an abstract
    #      forgiveness can only hide. `dejavuserif -> timesnewroman` was exactly that: the
    #      engine never wrote DejaVu Serif for anything, so the entry existed only to
    #      excuse a substitution somebody else made, and it read a .docx that names DejaVu
    #      Serif where the source drew Times New Roman as 2 of 2 kept when 1 of 2 was true
    #      (350_question_paper, 13 Nov). prove_checks.py now asserts this rule against
    #      DocxWriter.java itself, so the next entry of that kind cannot be added quietly.
    #
    #   2. THE TWO FACES MUST BE METRIC-IDENTICAL, not merely "a reasonable substitute".
    #      A forgiveness that spans two widths turns the check blind by construction: the
    #      text reflows, the look changes, and the name on the run still matches. Measured
    #      on this box (fontTools, advance widths over printable ASCII at 1 em): DejaVu
    #      Serif is 21.4 % wider than Liberation Serif and DejaVu Sans 13.3 % wider than
    #      Liberation Sans - which is why those two entries hid a reflow, and why the
    #      engine's own build of them moved 77 lines in 8 documents with a worst |dx| of
    #      432.50 pt. Liberation against the three faces below measures 0: it was drawn as
    #      their metric drop-in, and the engine's rename of it is a verified no-op on a
    #      reader that has Liberation - 17,817 line boxes, 0 moved, max|dx| 0.00 pt.
    #
    # Both halves matter here because a document may draw BOTH sides of an entry: 3 of
    # the 211 documents draw Liberation Sans and Arial, or Liberation Serif and Times New
    # Roman (09_stamp_font_not_embedded, 14_stamp_chars_positioned_td,
    # 38_faux_bold_italic_synthesised). The .docx then has ONE bucket for two source
    # families and cannot say which text went where. That is not a blind spot for the
    # LOOK - the two are the same face at the same width, so text in either renders
    # identically - but it does mean the split is unverified, so the comparison judges
    # the bucket against the group's combined share and says so on stderr rather than
    # reporting a per-family pass it did not measure.
    #
    # What is NOT forgiven, and must not be: one face arriving as a face of a different
    # width. A serif as a sans, a sans as a serif, anything as DejaVu. Those stay losses,
    # and the granularity of this table is what keeps them losses - `liberationserif`
    # reaches `timesnewroman` and nothing else, so a Liberation Serif document whose text
    # arrives in Arial has still lost its face and still fails.
    # FIVE DEAD KEYS REMOVED 13 Nov: helveticaps, arialps, timesnewromanps, courierps,
    # couriernewps. They could never fire. family() strips the PS/MT suffix BEFORE this
    # table is consulted, so "ArialPS" has already become "arial" by the time the lookup
    # runs and "arialps" is a key nothing can spell. Checked directly - family(k) == k
    # holds for every key that can fire and fails for all five of these - and removing
    # them changes no document's verdict (measured: 211 documents, 6 and 5 either way on
    # the two engine states). A forgiveness entry that cannot fire is not a hidden loss,
    # but it is a line in the table that reads as a claim, and this table is only worth
    # something if every line in it is one.
    "helvetica": "arial",
    "times": "timesnewroman", "timesroman": "timesnewroman",
    "timesnew": "timesnewroman",
    "courier": "couriernew",
    # ADDED 13 Nov, when the engine began renaming Liberation (5a09931,
    # DocxWriter.java:4810-4815). Without these three the check reads every Liberation
    # document as a total face loss: 6 documents failed before that commit and 129 after
    # it, all 123 new ones on "liberationsans kept 0 %" or "liberationserif kept 0 %".
    # The engine is right and the check was measuring a name. On this box fontconfig
    # resolves "Arial" to LiberationSans-Regular.ttf and "Times New Roman" to
    # LiberationSerif-Regular.ttf, so the rename is the identity on a reader without the
    # Microsoft faces and a metric-identical swap on one with them: it cannot lose a face,
    # and the check must not call it one.
    "liberationsans": "arial", "liberationserif": "timesnewroman",
    "liberationmono": "couriernew",
}


def face_bucket(fam):
    """The family a reader will actually have, for a family this PDF drew with.

    The table is applied here and ONLY here - to the source side. The .docx side is
    never folded: what the engine wrote is the evidence, and folding it as well would
    make the two sides agree by construction.
    """
    return SAME_FACE.get(fam, fam)

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
    # NOTHING IS FORGIVEN HERE. This returns the family the name spells, and only that;
    # SAME_FACE is applied by face_bucket() on the source side alone. Until 13 Nov this
    # line was `return SAME_FACE.get(n, n)`, so the table folded BOTH sides and the two
    # sides of the check could not disagree about a name the table covered - which is how
    # a document that drew both Liberation Sans and Arial became one bucket with no way
    # left to tell which text went where.
    return n

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



def compare(src_path, gd_path, docx_path=None):
    src = fitz.open(src_path)
    gd = fitz.open(gd_path)

    checks = {}

    # ---- gather -------------------------------------------------------------
    # Each run carries its page. The matcher below needs it: without a page, a source run on
    # page 1 can be paired with a render run on page 7 that holds the same word, and the
    # resulting dy is a page offset reported as a placement error.
    # A page that shows its text under a negative-determinant CTM is a MIRROR, and a mirror
    # is not undone by a rotation (reading_frame). Told to runs() per page, once, so every
    # run on that page keeps the zero-rotation frame and reads exactly as it did before.
    s_mir = {i for i, p in enumerate(src) if page_mirrors_text(src, p)}
    g_mir = {i for i, p in enumerate(gd) if page_mirrors_text(gd, p)}
    s_runs, g_runs = [], []
    for i, p in enumerate(src):
        s_runs += runs(p, i, mirrored=(i in s_mir), page_angle=page_reading_frame(p))
    for i, p in enumerate(gd):
        g_runs += runs(p, i, mirrored=(i in g_mir), page_angle=page_reading_frame(p))

    # Per-character boxes for the render, so a run that sits inside a longer one can be
    # placed by its own glyphs instead of by a linear guess. Keyed the way runs() rounds
    # a span's bbox, so a render run and its characters meet on the same key.
    g_chars = {}
    for i, p in enumerate(gd):
        for blk in p.get_text("rawdict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                for sp in ln.get("spans", []):
                    if not sp.get("text", "").strip():
                        continue
                    g_chars[(i, round(sp["bbox"][0], 2), round(sp["bbox"][1], 2))] = \
                        sp.get("chars", [])

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
    g_char_count = collections.Counter(norm_text(g_text))
    chars_missing = s_chars - g_char_count
    checks["04_chars_missing"] = (0, sum(chars_missing.values()), not chars_missing)
    # 05 was `len(extra) <= max(1, sum(s_words.values()) // 100)` - a count of TYPES on the
    # left against a budget derived from TOKENS on the right. The two sides were not the
    # same quantity, so the predicate could not be read as a tolerance at all.
    #
    # THE UNITS, proved by construction on a controlled pair (1,353-token source, one line
    # drawn 200 more times): extra TYPES 1, extra TOKENS 66-300 depending on the line, budget
    # 13 - and `len(extra)` is 1, so the check PASSES a render that added 300 words. The
    # understatement is the ratio of the two counts, which is unbounded: one repeated type
    # hides any number of copies. In the store (RESULTS.jsonl, engine 2a68de6) 114 of 208
    # documents read exactly 1 extra type and pass, which is the same fault at rest.
    #
    # THE UNIT is the character, for the reason 04 moved - a word boundary is the
    # extractor's, not the document's - and the measurement is harsher here than it was for
    # 04. Of the 23 documents the old predicate failed on a 211-document LibreOffice render
    # of this corpus, 257 of 257 extra word types were a contiguous substring of the
    # render's own text, i.e. every one was a fragment rather than a new word, and 14 of the
    # 23 had gained NOT ONE CHARACTER - a document cannot be failed for adding text when its
    # character multiset is unchanged.
    #
    # ZERO TOLERANCE, not a percentage. 04 states "not one thing may be missing"; the same
    # sentence in the other direction is "not one thing may be added", and a budget is what
    # lets the fault this check exists for walk through it: drawing one line of a document a
    # second time - the "one duplicated line" verify_txt.py:137 names - reads 1-4 extra types
    # and 8-26 extra characters against budgets of 13-25, so a 1 % budget passed it on 3 of
    # the 4 documents it was tried on. Zero tolerance caught all 4. Measured over 211: zero
    # tolerance fires on 9, a 1 % character budget on 8 - one document apart, and the budget
    # is the side that misses.
    chars_extra = g_char_count - s_chars
    checks["05_chars_extra"] = (0, sum(chars_extra.values()), not chars_extra)

    # ---- 06_table_columns and 07_table_rows RETIRED 13 Nov -----------------
    # They were the universe's only two "table" checks and neither of them could see a
    # table. Both were HISTOGRAMS OF TEXT COORDINATES, read off the extractor's runs:
    #
    #   06  how many distinct round(x / 6) values carry >= 3 runs, down the page
    #   07  the same in y
    #
    # Neither reads a drawn line. A page that keeps every border and loses the text between
    # them can pass both; a page that draws no table at all can fail both. What they count
    # is how the extractor happened to cut glyphs into runs, once per axis.
    #
    # THIS IS 02_text_run_count's RETIRED DEFECT, MEASURED A SECOND TIME (see its note under
    # 01_page_count): a run boundary is a property of the extractor's grouping, not of the
    # page. Constructed on
    # the corpus's own pages - the same bytes, re-read at one run per GLYPH instead of one
    # run per span, nothing moved, nothing added, nothing removed - 06 moves on 210 of 211
    # documents (mean 6.24 -> 70.65) and 07 on 208 of 211 (mean 8.71 -> 25.53), and each
    # check's OWN verdict flips on 210 and 195 of them. A number that answers to the
    # grouping cannot be a fact about the document.
    #
    # THE VALUE IS THE RENDER'S SPAN COUNT. On the 211 (engine d8fb69e, LibreOffice
    # 7.4.7.2), 07's GAP tracks how far the render inflated its own span count at r = 0.850
    # (Pearson, n = 211; the same correlation for 06 is 0.523). 350_question_paper is the
    # whole argument in one row: 07 reads 16 -> 48 while the render emitted 454 spans
    # against the source's 104 - 4.37x - so the "rows gained" are spans gained. 22 of 211
    # documents emit more spans than their source; the ratio runs to 4.37, mean 1.00.
    #
    # WHAT THE SOURCE'S NUMBER IS. On 05_round_company_seal_curved_text 06 reads 15
    # "columns". Twelve of the fifteen are the GLYPHS OF A CURVED SEAL: the ring reads "SRI
    # VINAYAKA INSTITUTE OF TECHNOLOGY" / "KENGERI CAMPUS 560060", every glyph is its own
    # rotated span at its own x (dir runs 0.6,-0.8 -> 1.0,0.1 -> 0.6,0.8 across the arc), so
    # each x-bucket collects three or more "runs" and becomes a column. The other three are
    # real edges - the body margin at x 54, the department line at 198, the signature block
    # at 354. A curved stamp is not a table, and 06 could not tell.
    #
    # ZERO EXCLUSIVE FIRES ON 211. 06 fails 14 and 07 fails 14; they share 4, Jaccard
    # 0.167. Not one document fails 06 alone, not one fails 07 alone, not one fails only the
    # pair - so retiring both flips 0 of 211 verdicts. The lightest of the 28 fires carries
    # 2 other failing checks, and 47_margins is among them on 11 of the 14 in each column.
    # These were second votes, which is what retired 03_word_count.
    #
    # THE FIRES RAN THE WRONG WAY, which is the fact that settles it. On the 50 documents
    # that DRAW a table lattice (>= 2 horizontal and >= 2 vertical thin-long segments
    # meeting - the segment rule 32 calibrates) 07 fired on 1 = 2.0 %; on the 161 that draw
    # none it fired on 13 = 8.1 %, 4.04x harder where there is no table to lose. That
    # population is stable at 50/161 across thin <= 4 or 6 pt and 2x2 or 3x3, and a second,
    # independent population says the same from the .docx side: 145 documents carry a w:tbl
    # and 66 do not, and 07 fired on 3.4 % against 13.6 % (3.95x). 06 did not run that way -
    # 8.0 % against 6.2 % - so the two were not even the same fault in this respect. Both
    # carried a weak table signal in their VALUES (mean source 06 10.32 with a lattice
    # against 4.98 without; 07 14.38 against 6.94). It was their FIRES that ignored it.
    #
    # NOT ONE CHECK WRITTEN TWICE, and the case does not rest on their agreement. 14 each
    # and only 4 shared is a Jaccard of 0.17: on this evidence they separate. "The same
    # function on two axes" is true of the CODE - the two helpers below were one body with
    # x swapped for y - and false of the EVIDENCE, so what retires them is the unit and the
    # direction of the fires, not redundancy between them.
    #
    # THE SLACK WAS PROPORTIONAL TO ITS OWN NUMBER. 06 allowed abs(d) <= max(1, s // 10)
    # and 07 abs(d) <= max(2, s // 5), so the tolerance grew with the very quantity being
    # questioned: 144 of 211 documents have a source 07 of 10 or less, i.e. 68 % of the
    # corpus could lose two whole "rows" for free, and 178 of 211 have a source 06 of 10 or
    # less and could lose one.
    #
    # WHAT CARRIES THE TABLE QUESTION NOW. 32_stroke_lines measures rules per side, per
    # page, and excludes grid sides on purpose (see its block); the grid's own measurement
    # lives in tools/p2w-bench/grid_sides.py, which is a tool and not a check. Nothing in
    # the universe counted a grid side before today either, so this retirement removes two
    # votes and no measurement - and every document that failed 06 or 07 already fails at
    # least two other checks, so nothing goes unwatched.
    #
    # table_signature() and table_rows() stood here and were the whole of these checks: one
    # body counting x-buckets and the same body counting y-buckets. They are kept as text
    # above rather than as code, because the formulas are the evidence and a helper with no
    # caller is a check waiting to be re-adopted.

    checks["08_image_count"] = (s_imgs, g_imgs, g_imgs >= s_imgs)

    # ---- 09_font_names RETIRED 13 Nov --------------------------------------
    # It asked "did every family the source drew survive?" on the WRONG SIDE OF THE
    # PIPELINE, and it asked it with a metric that could not see a loss.
    #
    # THE SIDE. This verifier compares a source PDF against the PDF Google Docs exports
    # (line 12). 53 asks the same question against the .docx the engine writes. Google's
    # export is Google's fontconfig, not the engine's decision - the same correction 53
    # and 54 were both redefined for, and the one 53's own comment states in as many
    # words: "Everything else - Google's substitution, LibreOffice's fontconfig, whether
    # the machine has Liberation installed - is somebody else's decision".
    # MEASURED 13 Nov, case (a) of the discrimination matrix: source draws four families,
    # the engine's .docx names all four correctly, Google's export shows one. 09 fired and
    # 53 did not, so the fire was Google's substitution and no engine change could clear
    # it. That is the defect the test file's own docstring names - "a check that always
    # fails ... condemns every document and hides the real defect behind its noise".
    #
    # THE METRIC. It compared distinct family COUNTS at an 80 % floor, so it could not fail
    # on a loss it was built to catch: at a source of two families the floor is 1, and a
    # render carrying one family passes. Measured on the matrix, case (c): source draws
    # Times and Arial, the .docx keeps only Arial - one of two families gone entirely -
    # and 09 read 2 vs 1 and passed. 53 reads the family at ratio 0.000 and fails.
    # The floor's blind spot, computed: s=2..5 may each drop one family silently, s=6..8 two.
    #
    # NOT AN EXACT DUPLICATE, which is why it is retired as SUPERSEDED and not as a repeat.
    # The matrix discriminates in both directions: case (a) fails 09 only, case (b) - a
    # .docx that renames one family, the 350_question_paper shape - fails 53 only. Two
    # checks that separate are not one check written twice; what makes 09 redundant is that
    # its exclusive fire is never the engine's to fix.
    #
    # Its one uncovered fact - Google's export carrying fewer families than the source drew -
    # is still reported, as information, from 53's block in extra_checks2(). A fact worth
    # knowing is not the same as a vote, and this one is not the engine's to win.

    # ---- what a "size set" is, and in whose units, after 13 Nov -----------
    # THE TWO SIDES WERE NOT IN THE SAME UNITS, and a set of sizes is a set of numbers.
    # The source side carries what PyMuPDF reads out of the page, which is continuous: the
    # corpus draws 64 distinct sizes and 31 of them are off the half-point grid (6.2, 6.4,
    # 6.8, 7.2, 7.4, 7.8, 8.6, 8.9, 9.3, 11.7 ...). The render side cannot carry any of
    # those, because the number travelled through w:sz and w:sz is an ST_HpsMeasure - an
    # INTEGER count of half-points. DocxWriter.java:3461 writes it from halfPointsDown()
    # (DocxWriter.java:5051), which floors; the same rule is at :2888 and :4942. Measured
    # on the 211-document store, 0 of 211 renders carry a size that is not an exact
    # multiple of 0.5. So an off-grid source size was a GUARANTEED miss, not a loss.
    #
    # WHAT THAT COST. Across the 52 documents that failed 10, 253 of their 254 missing
    # sizes were off the grid. Of those 253, 248 had every glyph of that size present in
    # the render at exactly floor(2*size)/2 with the span COUNT preserved - on
    # 304_package_insert_small_print the page draws 6.2 pt in 25 spans, the .docx says
    # w:sz 12 and the render says 6.0 pt in 25 spans - and quantising the source set
    # through the writer's own rule cleared 52 of 52. table-inside-two-column-page read
    # "source=7 render=3" for this reason and no other: its 6.4, 6.8, 7.2 and 8.9 pt floor
    # onto 6.0, 6.5, 7.0 and 8.5, and 7.0 was already in the set, so the render gained
    # three sizes and lost four.
    #
    # SO THE SOURCE SIDE IS NOW MEASURED IN THE UNITS THE .DOCX CAN EXPRESS. This is not a
    # loosened tolerance - the comparison is still exact, at 0.0 pt, on 0.1-pt values - it
    # is the same question asked of two quantities that are commensurable. A size the
    # engine DROPS still fails: its bucket is absent from the render and nothing fills it.
    # Proof, not assertion. table-inside-two-column-page rewritten so that its w:sz 12, 17
    # and 30 become 13, 18 and 28 - three sizes removed and no other change - then
    # re-rendered, reads source 6, render 3, ok=False. 34a on the same pair reads 100 -> 98
    # and PASSES, because its 0.6 pt per-span tolerance swallows a half-point shift; so
    # this check is not the redundant half of that pair.
    def expressible(pt):
        """The size a page can be written at: DocxWriter.halfPointsDown, line 5051."""
        return max(2, min(3276, int(math.floor(pt * 2)))) / 2.0

    s_sizes = collections.Counter(expressible(r["size"]) for r in s_runs)
    g_sizes = collections.Counter(r["size"] for r in g_runs)
    common = sum(1 for k in s_sizes if k in g_sizes)
    checks["10_font_sizes"] = (len(s_sizes), common,
                               len(s_sizes) == 0 or
                               common >= max(1, int(len(s_sizes) * 0.8)))

    # 11_bold_runs RETIRED 13 Nov. It asked "how many bold runs", which is two questions it
    # cannot answer and one that is already answered:
    #
    #   - IT READS THE FACE NAME, 34c READS THE FLAG. bold_count() tests `"bold" in
    #     norm_font(font)`; 34c tests `flags & 16`. Where they disagree the flag is right and
    #     the name is wrong, because a renderer may embolden without renaming the face.
    #     Measured on the 211-document store: of the 26 documents 11 failed, 23 have 34c at
    #     88-100 % with ok=True - 05_round_company_seal_curved_text reads 66 bold runs -> 3
    #     while 34c reads 100 %, 371_experience_certificate 30 -> 2 at 100 %, 60_page_border
    #     52 -> 5 at 94 %. Only 3 of the 26 fail 34c. That is the 10_font_sizes/34a signature
    #     exactly: a count contradicted by the per-span matcher at ~100 %.
    #   - ITS SLACK IS BLIND ON SMALL DOCUMENTS. The tolerance is `s - max(2, s // 5)`, so
    #     with one or two bold runs a document may lose ALL of them and pass. Constructed:
    #     one bold run made regular reads source=1 render=0 and PASSES, while 34c fails it.
    #   - THE LOSS IT WOULD CATCH IS 17's. If the render loses bold spans outright, the pairs
    #     shrink and 34c (a share of pairs) cannot see it - but 17_matched_runs can, and does:
    #     05 pairs 20 of 83 runs and fails 17. Run LOSS is 17's question, run SEGMENTATION is
    #     what 02_text_run_count was retired for, and per-span weight is 34c's.

    # 12_italic_runs RETIRED 13 Nov. It is the other half of 11_bold_runs' defect, and it has
    # that defect three times over plus one of its own:
    #
    #   - IT READS THE FACE NAME, 34c READS THE FLAG. italic_count() tested
    #     `"italic" in norm_font(font)`; 34c compares `weight`, which runs() builds from
    #     `flags & 16` and `flags & 2` (lines 75-76), so the ITALIC BIT was already matched
    #     span for span by 34c. Two votes on one question is what retired 11 the same day.
    #   - THE NAME READ IS LOSSY IN A WAY THE FLAG IS NOT. PyMuPDF cuts the face name in
    #     get_text("dict") at 24 characters, so "LiberationSerif-BoldItalic" arrives as
    #     "LiberationSerif-BoldItal" and contains neither "italic" nor "oblique". Measured on
    #     62_two_col_newsletter_pull_quote: the render carries FIVE italic spans by flag and
    #     the name test sees TWO - which is exactly the source=5 render=2 this check recorded
    #     for that document. The three it could not see are the three bold-italic ones.
    #     Nothing was lost; the face name was cut.
    #   - IT IS A COUNT ON THE WRONG SIDE. It compared the source against the PDF Google Docs
    #     exports, not against the .docx the engine writes - 09's and 53's correction. Measured
    #     on the four documents that read render=0 (bank-statement-5-pages 5->0,
    #     gst-invoice-multipage-item-table 3->0, mutual-fund-statement 3->0,
    #     very-long-single-column-table 3->0): the engine's .docx carries <w:i/> on exactly the
    #     source's italic runs (DocxWriter:3452), and rendering that .docx with a renderer that
    #     honours w:i gives back 5, 3, 3 and 3 - the source counts, unchanged. The zero is
    #     Google's naming of a substituted face, and no engine change could clear it.
    #   - ITS SLACK IS BLIND AND IT FIRES ON A GAIN. The tolerance was `max(2, s // 5)`, so at
    #     two italic runs a document could lose BOTH and pass. Constructed: two italic spans
    #     against a render with none reads source=2 render=0 and PASSES, where three reads
    #     3->0 and fails. And the two sides were global counts, not pairs, so a render that
    #     keeps all three and adds three elsewhere reads 3->6 and FAILS with nothing lost.
    #
    # ITS PROOF WAS NEVER ITS OWN. prove_checks.py gave it 34c's mutation - mut_bold, 35 % of
    # spans made bold - and mut_restyle inserts with fontname "hebo"/"helv", neither italic.
    # Measured: on BASE that mutation reads 12 as source=1 render=0 ok=True, so the case could
    # not fire it, while 34c read 72 % and fired. The harness never said so because 12 fired on
    # real converted documents and real_evidence() counts that as proof - the only proof 12
    # ever had was the false alarm.
    #
    # RETIRING IT MOVES NO VERDICT. 0 of the 211 rows of RATCHET.json fail 12 alone, and each
    # of the six it failed carries 12 to 19 other failures.
    #
    # THE ONE THING IT WOULD HAVE CAUGHT AND DID NOT. A per-span italic loss small enough to
    # stay inside 34c's 85 % floor - five italic spans out of 585 is 0.85 % - is caught by
    # neither check. That is 34c's floor, not a second check's job: it is recorded here as
    # 34c's known looseness, the way 46 records its 1 pt inset. Tightening it is a one-line
    # change to 34c's predicate and belongs in a round that measures it, not in a retirement.

    # A SET, NOT A COUNT. This compared the NUMBER of distinct colours, so it could not see
    # a colour CHANGE: a span recoloured to a colour the document already uses leaves both
    # counts where they were. Constructed 13 Nov: four colours, one span recoloured - 13
    # read 4 -> 4 and passed, 34b read 75 % and failed. That is the same mistake
    # 39_image_position made ("a set numerator against a list denominator") and the same
    # shape 10_font_sizes made against 34a.
    # Compared with colour_same(), not with ==, so CMYK black and RGB black are one colour -
    # exact int equality here is what REMAINING-DEFECTS.md:205 still records as 34b's defect
    # and it was the same defect in this line.
    # 13 is NOT a duplicate of 34b, and the store says so: 13 fails 4 documents, 34b fails 2,
    # and the two sets are disjoint. 34b judges only the spans that PAIRED, so a colour that
    # vanished with its span is invisible to it (402_calendar_month_grid: 4 colours -> 2, 04
    # passes, 17_matched 45 of 46, 34b reads 91 %). This keeps that signal.
    # THE FLOOR IS EQUALITY, because a set is not a sample: this file already holds that
    # rule twice - 15_links (`s_links == 0 or g_links >= s_links`) and 40_link_targets
    # (`s_l == g_l or not s_l`). A colour that is GONE is gone; 80 % of four colours rounds
    # down to three, so the percentage floor let one colour of four disappear silently.
    # A render carrying MORE colours used to pass. It does not any more: see the GAIN clause
    # below, which is the second half of this check.
    #
    # THE GAIN CLAUSE, added 14 Nov. `kept_cols` walks the SOURCE set and never the render
    # set, so a colour the render INVENTED was invisible to this check: it asked whether every
    # source colour survived and never whether the render added one. Measured on 414_
    # transparency_softmask - the page draws its two text lines in black and the engine wrote
    # #1A4D99 on both, which is the blue of the bar above them - the render's only colour had
    # no source counterpart. 13 did fail that document, but for the LOSS (black gone), not for
    # the gain: had the render kept black anywhere else on the page it would have read 1 of 1
    # kept and PASSED with #1A4D99 invented. Both directions are one clause each; a check that
    # reads one of them is half a check.
    #
    # TOLERANCE, and only one: #000000 in the render is not a gain when the source drew a
    # black in another encoding. That is D-23's Automatic case - the engine deliberately
    # leaves `w:color` off a run and the reader resolves it to its own black - plus the CMYK
    # black already handled by colour_same(). It is keyed on the EXACT int 0, so a render that
    # paints #000000 where the source painted a COLOUR still fires, which is the case the
    # tolerance must not buy.
    s_col_set = {r["colour"] for r in s_runs}
    g_col_set = {r["colour"] for r in g_runs}
    kept_cols = sum(1 for a in s_col_set if any(colour_same(a, b) for b in g_col_set))
    gained_cols = sorted(
        b for b in g_col_set
        if not any(colour_same(a, b) for a in s_col_set)
        and not (b == 0x000000 and any(is_blackish(a) for a in s_col_set)))
    if gained_cols:
        print("13_text_colours: the render carries %d colour(s) the source does not: %s"
              % (len(gained_cols), ", ".join("#%06X" % c for c in gained_cols)))
    checks["13_text_colours"] = (len(s_col_set), kept_cols,
                                 (len(s_col_set) == 0 or kept_cols == len(s_col_set))
                                 and not gained_cols)

    # 14_filled_shapes: INK AREA and PLACEMENT, not a count.
    #
    # WHAT A COUNT MISSED. The old line compared the NUMBER of filled rects, so it could not
    # tell a moved fill from a lost one, or a lost fill from an invented one: constructed 13 Nov,
    # eight cells lost AND eight invented elsewhere reads 40 -> 40 and passed while the shading
    # had moved off the rows it belonged to. It was also blind to size: one page-sized fill
    # traded for twenty thin bands (3 x 500 pt, 1500 pt2 each) read 1 -> 20 and PASSED, while
    # the area fell to 9.3 % of the source's. Constructed 13 Nov, /scratch/work/cases/14D_*.
    #
    # WHAT IT MEASURES NOW, per page:
    #   AREA      the page's filled area may not fall below FILL_AREA_FLOOR of the source's.
    #             A ratio, not a count, so trading one big fill for several small ones is not
    #             a loss - and a page that lost a fifth of its ink is, however it was drawn.
    #   PLACEMENT every source fill of FILL_PLACE_PT2 or more must have a RENDER fill whose
    #             rect contains its CENTRE. Containment, not overlap and not a coordinate
    #             match, because the render legitimately redraws one cell as one cell of a
    #             different rect: what must not happen is the ink being somewhere else.
    #
    # THE FLOOR IS THE ONE THIS CHECK ALREADY CARRIED (0.8). It is kept rather than re-derived
    # because it was never the count's problem - the count was.
    #
    # THE 400 pt2 PLACEMENT FLOOR IS BAND ARITHMETIC, and it keeps thin bands with 32/46.
    # A 20 x 20 pt patch is 400 pt2; a 0.8 pt band across a 450 pt column is 360 pt2. Below
    # the floor a fill is a rule, and whether a rule survived is 32_stroke_lines' and
    # 46's question, not this one's.
    #
    # MEASURED ON 211 RENDERS, 13 Nov, and the measurement does NOT confirm the floor - it
    # only fails to contradict it. The largest thin fill any source page in corpus-v1 draws is
    # 80 pt2 (a 0.4 pt x 200 pt band); no thin fill in the corpus reaches 100 pt2. So no floor
    # from 100 upward can be exercised by a band here, and the class size is the same 85
    # documents at 10, 25, 50, 100, 200, 400, 800, 1600 and 3200 pt2. What the sweep does show
    # is that at 400 every orphan is block-shaped - 354 of 354, min side > 2 pt - so the floor
    # is not throwing away a real loss, and the corpus never puts a band above it. 400 stays
    # because the arithmetic says a band cannot reach it; the corpus cannot say more than that.
    FILL_AREA_FLOOR = 0.80
    FILL_PLACE_PT2 = 400.0

    def softmask_ink(page):
        """The fills a page's /SMask group draws, which the page never paints.

        pymupdf's get_drawings() walks INTO a luminosity soft mask's form XObject and reports
        the mask's own rectangles as page ink. Measured on 414_transparency_softmask: the page
        draws one `re f` (1A4D99) under /GS1, and get_drawings() returns three fills - the blue
        bar plus 262626 and FFFFFF, which are the two `re f` of xref 7, the /SMask /G of
        /ExtGState 6. The mask defines the bar's alpha; nothing of it reaches the page, so the
        engine is right to write neither and 14 charged it for two lost fills plus 80,000 pt2 of
        ink area that was never on the page.

        A drawing is mask ink when its colour and its size both match a fill the mask stream
        draws. Only pages that carry an /SMask ExtGState are scanned - one document of 211.
        """
        masks = []
        doc = page.parent
        try:
            # One cheap lookup first: a page with no ExtGState resource cannot carry a mask.
            if doc.xref_get_key(page.xref, "Resources/ExtGState")[0] == "null":
                return []
            for x in range(1, doc.xref_length()):
                try:
                    o = doc.xref_object(x, compressed=True)
                except Exception:
                    continue
                if "/SMask" not in o or "/ExtGState" not in o:
                    continue
                m = re.search(r"/SMask\s*<<[^>]*?/G\s+(\d+)\s+0\s+R", o)
                if not m:
                    continue
                form = int(m.group(1))
                try:
                    stream = doc.xref_stream(form).decode("latin-1", "replace")
                except Exception:
                    continue
                colours, sizes = set(), set()
                for cm in re.finditer(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg", stream):
                    colours.add(tuple(round(float(cm.group(i)) * 255) for i in (1, 2, 3)))
                for rm in re.finditer(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+re", stream):
                    sizes.add((round(float(rm.group(3)), 1), round(float(rm.group(4)), 1)))
                masks.append((colours, sizes))
        except Exception:
            return []
        if not masks:
            return []
        out = []
        for d in page.get_drawings():
            f = d.get("fill")
            if f is None:
                continue
            rgb = tuple(round(c * 255) for c in f[:3])
            r = d["rect"]
            size = (round(r.width, 1), round(r.height, 1))
            hit = False
            for colset, szset in masks:
                if size not in szset:
                    continue
                if any(all(abs(a - b) <= 2 for a, b in zip(rgb, col)) for col in colset):
                    hit = True
                    break
            if hit:
                out.append(r)
        return out

    def _overlap(a, b):
        w = min(a.x1, b.x1) - max(a.x0, b.x0)
        h = min(a.y1, b.y1) - max(a.y0, b.y0)
        return w * h if w > 0 and h > 0 else 0.0

    def _replay(stream, height):
        """A soft mask's own paints, as (rect, luminance) in pymupdf's top-down page space.

        The stream is replayed as far as coverage needs it: the CTM, `re` and the fill
        colours. Anything else - a curve, a shading, a form - is left out, which can only
        make a rect smaller than it is, and a rect that is too small hides too little.
        """
        out = []
        ctm = (1, 0, 0, 1, 0, 0)
        stack = []
        value = 1.0
        path = None
        toks = re.findall(r"\((?:[^()\\]|\\.)*\)|\[|<|>\]|[^\s\[\]<>()]+", stream)
        nums = []
        for t in toks:
            try:
                nums.append(float(t))
                continue
            except ValueError:
                pass
            a, nums = nums, []
            if t == "q":
                stack.append((ctm, value))
            elif t == "Q" and stack:
                ctm, value = stack.pop()
            elif t == "cm" and len(a) >= 6:
                m = (a[0], a[1], a[2], a[3], a[4], a[5])
                ctm = (ctm[0] * m[0] + ctm[2] * m[1],
                       ctm[1] * m[0] + ctm[3] * m[1],
                       ctm[0] * m[2] + ctm[2] * m[3],
                       ctm[1] * m[2] + ctm[3] * m[3],
                       ctm[0] * m[4] + ctm[2] * m[5] + ctm[4],
                       ctm[1] * m[4] + ctm[3] * m[5] + ctm[5])
            elif t == "re" and len(a) >= 4:
                r = (a[0], a[1], a[0] + a[2], a[1] + a[3])
                if path is None:
                    path = r
                else:
                    path = (min(path[0], r[0]), min(path[1], r[1]),
                            max(path[2], r[2]), max(path[3], r[3]))
            elif t == "rg" and len(a) >= 3:
                value = max(0.0, min(1.0, 0.3 * a[0] + 0.59 * a[1] + 0.11 * a[2]))
            elif t == "g" and len(a) >= 1:
                value = max(0.0, min(1.0, a[0]))
            elif t in ("f", "F", "f*", "b", "b*", "B", "B*"):
                if path is None:
                    continue
                xs = [path[0], path[2], path[0], path[2]]
                ys = [path[1], path[1], path[3], path[3]]
                px = [ctm[0] * x + ctm[2] * y + ctm[4] for x, y in zip(xs, ys)]
                py = [ctm[1] * x + ctm[3] * y + ctm[5] for x, y in zip(xs, ys)]
                # PDF y counts up from the bottom; pymupdf's rects count down from the top.
                out.append((fitz.Rect(min(px), height - max(py), max(px), height - min(py)),
                            value))
                path = None
            elif t in ("n", "S", "s", "W", "W*"):
                path = None
        return out

    def mask_paints(page):
        """The paints of every /SMask group a page's ExtGStates name, or None if it has none.

        A fill under a soft mask is only ink where the mask lets something through. pymupdf
        cannot say so: it reports 414's masked bar with fill_opacity 1.0, and it reports the
        mask's own rectangles as page ink. So the mask is read here, the same way the engine
        reads it, and 14 judges the fills the page actually PAINTS.
        """
        doc = page.parent
        try:
            if doc.xref_get_key(page.xref, "Resources/ExtGState")[0] == "null":
                return None
        except Exception:
            return None
        found = None
        for x in range(1, doc.xref_length()):
            try:
                o = doc.xref_object(x, compressed=True)
            except Exception:
                continue
            if "/SMask" not in o or "/ExtGState" not in o:
                continue
            m = re.search(r"/SMask\s*<<[^>]*?/G\s+(\d+)\s+0\s+R", o)
            if not m:
                continue
            try:
                stream = doc.xref_stream(int(m.group(1))).decode("latin-1", "replace")
            except Exception:
                continue
            if found is None:
                found = []
            found.extend(_replay(stream, page.rect.height))
        return found

    def fill_boxes(page):
        """Every drawing that PAINTS a fill, with its rect. Any size - the floor does the
        cutting, and it does it in the placement clause only.

        A fill a soft mask lets nothing through is not ink the page shows, so it is not
        counted on the source side either. Measured on 414_transparency_softmask: without
        this, 14 read the masked bar as 40,000 pt2 of source ink and FAILED the corrected
        engine for not drawing a block the page never showed.
        """
        out = []
        skip = softmask_ink(page)
        paints = mask_paints(page)
        for d in page.get_drawings():
            if d.get("fill") is None:
                continue
            if (d.get("fill_alpha") or 1.0) == 0.0:
                continue
            r = d["rect"]
            if r.width <= 0 or r.height <= 0:
                continue
            if any(r == q for q in skip):
                continue
            if paints is not None and not any(
                    v > 0.02 and _overlap(r, mr) > 0 for mr, v in paints):
                continue
            out.append(r)
        return out

    s_area = g_area = 0.0
    thin_pages = []
    orphans = 0
    for i in range(max(src.page_count, gd.page_count)):
        sb = fill_boxes(src[i]) if i < src.page_count else []
        gb = fill_boxes(gd[i]) if i < gd.page_count else []
        sa = sum(r.width * r.height for r in sb)
        ga = sum(r.width * r.height for r in gb)
        s_area += sa
        g_area += ga
        if sa > 0 and ga < FILL_AREA_FLOOR * sa:
            thin_pages.append(i + 1)
        for r in sb:
            if r.width * r.height < FILL_PLACE_PT2:
                continue
            cx, cy = (r.x0 + r.x1) / 2.0, (r.y0 + r.y1) / 2.0
            if not any(q.x0 <= cx <= q.x1 and q.y0 <= cy <= q.y1 for q in gb):
                orphans += 1
    if thin_pages:
        print("14_filled_shapes: ink area under %.0f %% of the source on page(s) %s"
              % (100 * FILL_AREA_FLOOR, ",".join(str(p) for p in thin_pages[:6])))
    if orphans:
        print("14_filled_shapes: %d source fill(s) of %.0f pt2 or more have no render fill "
              "over their centre" % (orphans, FILL_PLACE_PT2))
    # Source has no filled ink: there is no area to fall below, and the placement clause has
    # no candidates. A render that GAINS fills is not a loss and still passes.
    checks["14_filled_shapes"] = (int(round(s_area)), int(round(g_area)),
                                  not thin_pages and orphans == 0)

    # 15_links RETIRED 13 Nov. It counted LINK ANNOTATIONS, and the object is a SET
    # OF TARGETS. Three separate measurements say so.
    #
    # 1. IT IS A DUPLICATE OF 40_link_targets, by this file's own test. 13_text_colours
    #    records that criterion: "13 is NOT a duplicate of 34b... 13 fails 4 documents,
    #    34b fails 2, and the two sets are disjoint." Measured over all 211 documents
    #    of corpus-v1, 15 and 40 fail the SAME ONE document, 44_coloured_underlined_
    #    hyperlinks, and pass the other 210. Not disjoint - identical.
    #    And 40 pass implies 15 pass: corpus-v1 carries exactly 5 links in total, all
    #    on that one page, all LINK_URI, all distinct (measured, pymupdf get_links over
    #    211 files). With no duplicate URIs, 40's set equality forces g_links >= s_links.
    #    There is no document on which 15 fires and 40 does not.
    #
    # 2. IT IS BLIND where 40 is not. Constructed 13 Nov: a render carrying the source's
    #    five link rectangles with all five targets rewritten to https://wrong.invalid/N
    #    reads 5 -> 5 and PASSES 15, while 40 reads 5 -> 0 and fails. A count cannot see
    #    a retarget, which is the defect 40 exists to catch.
    #
    # 3. IT IS WRONG where 40 is right - it can FALSE-FAIL. Constructed 13 Nov: a source
    #    with five annotations but only FOUR distinct targets (two links over the same
    #    rect, the duplicate a Word-produced PDF commonly carries) against a faithful
    #    render emitting one hyperlink per target reads 5 -> 4 and FAILS 15, while 40
    #    reads 4 -> 4 and passes. The render lost nothing; the count lost an annotation.
    #
    # WHY NOT REDEFINE IT AS A SPAN CHECK INSTEAD. The gap both checks leave is that
    # neither reads the link's RECTANGLE: a render with the right targets on the wrong
    # spans passes both (constructed, 13 Nov). Measuring spans was considered and
    # rejected for the reason 41_block_spacing and 47_margins were retired: a link
    # rectangle is where the PRODUCER put the text, and a render that legitimately
    # reflows moves it. That is the same mistake, one rectangle further on. If internal
    # (GoTo) link fidelity is wanted, it is a different question and should be named as
    # one - 15_links was never that question.
    #
    # The universe goes 47 -> 46 live checks and 44's defect class stops counting one
    # real defect twice. Two follow-ups this patch does NOT make, because they are
    # outside verify_google.py: prove_checks.py:1193's "15_links" case can now never
    # fire (the same dead-entry state 02_text_run_count was left in), and
    # test_checks.py:319 still expects ["15_links"] from the "link dropped" case.

    # 16_numeric_runs RETIRED 13 Nov. It counted RUNS CONTAINING A DIGIT, which is neither
    # the number of numbers nor their content:
    #
    #   - IT CANNOT SEE A CHANGED DIGIT, which is the numeric defect that matters. Constructed:
    #     "Total amount 4500" against "Total amount 4508" reads 1 -> 1 and passes; 04_chars_missing
    #     (character-level since fbef7ac) fails it.
    #   - ITS FLOOR IS ABSOLUTE. The tolerance is `max(3, s // 10)`, so a document with three
    #     numeric runs may lose every digit and pass: constructed, "Qty 12 / Rate 34 / Amount 56"
    #     against "Qty / Rate / Amount" reads 3 -> 0 and PASSES.
    #   - IT IS STRICTLY WEAKER THAN 04 ON THE CORPUS. On the 211-document store all 28
    #     documents it fails also fail 04_words_missing (now 04_chars_missing) - 0 of 28 are
    #     exclusive - and 21 of the 28 fail in the GAIN direction (350_question_paper 76 -> 115,
    #     price-list-2col-dense-right-aligned 198 -> 237), i.e. the render split one numeric run
    #     into several. That is a property of the extractor's grouping, which is the ground
    #     02_text_run_count was retired on.

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
                and abs(c["ry"] - r["ry"]) <= 1.0 and c["rx"] >= r["rx"] - 1.0]
        near.sort(key=lambda j: g_runs[j]["rx"])
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
            cand.append((abs(g_runs[j]["ry"] - r["ry"]) + abs(g_runs[j]["rx"] - r["rx"]), i, j))
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

    # ---- A SOURCE RUN THAT SITS INSIDE ONE LONGER RENDER RUN ----------------
    #
    # The two passes above can join render runs into a source run. Neither can do the
    # reverse, so when the render draws as ONE span what the source drew as several, every
    # source run in it is unpaired and 17 charges the document for a run that is on the
    # page, at the right place, in the right order.
    #
    # MEASURED 13 Nov on 211 documents (source vs the engine's .docx rendered by
    # LibreOffice): of 582 source runs left unpaired in the 22 documents 17 fails, 352 -
    # 60.5 % - are inside a longer render run that covers their box, and 247 of those 352
    # are SINGLE CHARACTERS. The shape is text the source positions glyph by glyph -
    # 05_round_company_seal_curved_text draws 'R','I','V',... as 59 spans and the render
    # writes "SRI VINAYAKA INSTITUTE OF TECHNOLOGY" as one; 21_form_labels_x60_values_x300
    # draws "Member Name" and ":" and the render writes "Member Name :". Closing this one
    # case takes 15 of the 22 to a pass with no other change (cases C2, C10 in
    # /scratch/work/cases; matrix and attribution in /scratch/work/matrix.py, corpus.py).
    #
    # A render run is not consumed here, because it legitimately answers for several source
    # runs at once - that is what being merged means. What IS enforced is that no two source
    # runs claim the same characters of it, so a source run still cannot be paired with text
    # that another source run already accounts for.
    piece_of = {}
    claimed = collections.defaultdict(list)

    def _inside(r):
        """(render index, character range) of r's text inside one longer render run."""
        want = norm_word(r["text"])
        if not want:
            return None
        for j, c in enumerate(g_runs):
            if c["page"] != r["page"]:
                continue
            ct = norm_word(c["text"])
            if len(ct) <= len(want) or want not in ct:
                continue
            # the glyphs have to be where the source put them: the run must COVER r's box,
            # and it must be on the SAME LINE. Without the baseline test this pass pairs a
            # footnote marker "1" at the foot of the page with the "1" inside a header 620 pt
            # above it - measured on journal-2col-with-footnotes, three such pairs, and
            # 18_displacement read a 619.5 pt displacement on a page where nothing moved.
            # Same test _split_span() already uses for the same reason.
            if c["rx"] > r["rx"] + 1.0 or c["rx1"] < r["rx1"] - 1.0:
                continue
            # SAME LINE, by box overlap in READING space. ry/ry1 are the reading-space top
            # and bottom, so for an upright pair this is the same test as before (it was
            # device y/y1) and for a 180-degree pair it is the box the reader sees. Keeping
            # the overlap form matters: a baseline-proximity test broke the curved seals,
            # whose glyphs sit at their own angles.
            if min(c["ry1"], r["ry1"]) - max(c["ry"], r["ry"]) < 0.5:
                continue
            span = c["rx1"] - c["rx"]
            if span <= 0:
                continue
            # where the source run starts, as a character offset in the render run
            guess = int(round((r["rx"] - c["rx"]) / span * len(ct)))
            guess = max(0, min(guess, len(ct) - len(want)))
            off = ct.find(want, guess)
            if off < 0:
                off = ct.find(want)
            if off < 0:
                continue
            lo, hi = off, off + len(want)
            if any(not (hi <= a or lo >= b) for a, b in claimed[j]):
                continue          # those characters are already spoken for
            # THE PIECE'S OWN BOX, from the render's characters. A linear map of the run's
            # width is off by up to one character and made 43_within_10pt_x report
            # displacements that were the estimate's, not the document's - measured on
            # 60_page_border, where a curved caption is rendered straight and six glyphs
            # read 12-17 pt out under the linear map. The characters are exact.
            raw = g_chars.get((c["page"], c["x"], c["y"]))
            px = px1 = None
            if raw:
                idx = []
                acc = ""
                for k, ch in enumerate(raw):
                    piece = re.sub(r"[\s\u00a0\x00-\x1f]+", "", ch.get("c", "")).lower()
                    for _ in piece:
                        idx.append(k)
                        acc += piece
                if acc == ct and hi <= len(idx):
                    px = raw[idx[lo]]["bbox"][0]
                    px1 = raw[idx[hi - 1]]["bbox"][2]
            # px/px1 are DEVICE x - that is the frame g_chars is keyed in and the one the
            # paper checks read. The piece is also given its READING-space x, projected
            # through the render run's own dir, because 43 and 18 judge it there.
            if px is None:
                rpx = c["rx"] + span * lo / len(ct)
                rpx1 = c["rx"] + span * hi / len(ct)
                px, px1 = rpx + c["fr"][0], rpx1 + c["fr"][0]
            else:
                pa = rproj(px, c["oy"], c["fr"])[0]
                pb = rproj(px1, c["oy"], c["fr"])[0]
                rpx, rpx1 = min(pa, pb), max(pa, pb)
            return j, lo, hi, px, px1, rpx, rpx1
        return None

    for i, r in enumerate(s_runs):
        if i in taken:
            continue
        hit = _inside(r)
        if hit is None:
            continue
        j, lo, hi, px, px1, rpx, rpx1 = hit
        claimed[j].append((lo, hi))
        taken[i] = j
        # the pair is the PIECE, not the whole run: 21_median_dx reads x, and the run's own
        # x is the start of somebody else's text.
        piece = dict(g_runs[j])
        piece["x"] = round(px, 2)
        piece["x1"] = round(px1, 2)
        piece["xink"] = round(px, 2)
        piece["x1ink"] = round(px1, 2)
        piece["rx"] = round(rpx, 2)
        piece["rx1"] = round(rpx1, 2)
        piece["rxink"] = round(rpx, 2)
        piece["rx1ink"] = round(rpx1, 2)
        piece_of[i] = piece

    for i, r in enumerate(s_runs):
        if i not in taken:
            continue
        j = taken[i]
        g = piece_of.get(i, g_runs[j])
        dys.append(g["ry"] - r["ry"])
        dxs.append(g["rx"] - r["rx"])
        matched += 1
        pairs.append((r, g))

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
    # The population is the UPRIGHT source runs, keyed in READING space. A 180-degree line
    # has a horizontal baseline (dir_y == 0) and belongs here - it is text a reader reads
    # left to right once the page is turned, and its dy is a displacement, not a page
    # height, once it is projected (reading_frame). Only SLANTED text (|dir_y| > 0.02) is
    # excluded, which is what this test always meant: on slanted and curved runs dy is not
    # a displacement. Built from s_runs so the key is the same ry the ds lookup uses.
    flat = {(r["page"], r["ry"], r["text"]) for r in s_runs
            if abs(math.sin(math.radians(r["angle"]))) <= 0.02}

    def _tol(size):
        return min(max(0.35 * size, 1.5), 4.5)

    # The tail clause. It replaces 19_worst_dy, which asked the same question of the same
    # list at a fixed 15 pt and so left the band between this check's cap (4.5 pt) and its
    # own threshold unjudged for every run the budget forgives.
    TAIL_FACTOR = 2.0
    bad_pages = []
    for pg in sorted(set(r["page"] for r in s_runs)):
        flat_src = [r for r in s_runs
                    if r["page"] == pg and (r["page"], r["ry"], r["text"]) in flat]
        ds = [(g["ry"] - r["ry"], r["size"]) for r, g in pairs
              if r["page"] == pg and (r["page"], r["ry"], r["text"]) in flat]
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
    # 21_median_dx RETIRED 13 Nov - folded into 43_within_10pt_x, which now carries its
    # median clause. It was the median-only half of one question, and both of the documents
    # it fired on were already failed by other checks in the same store:
    #   375_attendance_register  med_dx 4.3   also fails 19_worst_dy, 20_within_10pt, 47_margins
    #   401_trifold_brochure     med_dx 300.9 also fails 18/19/20, 43_within_10pt_x, 47_margins
    # so it decided no document's verdict on its own. Its unique signal - a uniform sideways
    # shift, which a per-span 10 pt window cannot see - is kept, in 43. med_dx itself is still
    # computed here because 29/30 bucket the render in the source's frame with it.
    # (This is the same fold as 19_worst_dy into 18_displacement, and for the same reason: two
    # summaries of one population, one vote each.)

    # Reading order: a TORN LINE, not an LCS over two extractors' sequences.
    #
    # The old rule scored an LCS between the source PDF's get_text() order and the render's.
    # get_text() returns the order the PRODUCER DREW THE GLYPHS, not a reading order - so the
    # check was measuring agreement between two extractors, and a table's cells are row-major
    # by definition (w:tbl -> w:tr -> w:tc) while the producer may have drawn down a column.
    # Measured on 76 failures under a fresh build: 72 have ZERO torn lines, 44 render visually
    # intact with no weld and no torn line (32 tables, 20 text boxes), and only 4 have a
    # genuinely torn line. Re-reading the same .docx with cells enumerated down columns
    # recovers only 4 of the 76, which proves the deficit is not recoverable from a correct
    # document - the reference itself is the problem.
    #
    # A reader notices ONE thing here: a line of text broken in the middle and its second half
    # reappearing somewhere else. That is what this now asks, and it fails 4 documents where
    # the old rule failed 88. The 10 visually destroyed pages are overflow, and they belong to
    # 26_text_overlap, which already fails them. (41_block_spacing was named here too and is
    # now retired - see its note above 42.)
    torn = _torn_lines(s_text, g_text)
    checks["22_reading_order"] = (0, len(torn), not torn)

    # ---- 23 line pitch: PAIRED, PER COLUMN, ON THE BASELINE -----------------
    # What this used to be: per page, the sorted set of distinct SPAN TOPS, the median of
    # the gaps between neighbours, then the median across pages, compared to within 2 pt.
    # On a single-column page of one type size that number is the line pitch. On anything
    # else it is not:
    #   - a table or a grid: the gaps are ROW pitches (23_timetable_grid_txtpos read 39.2 pt,
    #     402_calendar_month_grid 30.0, 411_nested_xobject_transforms 36.6);
    #   - two columns starting at different offsets: the gaps alternate between the column
    #     offset and the pitch (27_two_column_left_short_txtpos 11.0/13.5, and its lines are
    #     11.0 apart on both sides);
    #   - curved or rotated text: spans on one visual line sit at different tops, so the set
    #     fills with sub-line gaps (05_round_company_seal_curved_text read 3.2 pt against a
    #     true 15.7 pt pitch that the render reproduces to 0.0).
    # And the docstring above said "baselines" while the code read sp["bbox"][1], which is the
    # TOP of the span: on 7 of the 18 documents that failed it, reading the baseline it claims
    # to read flips the verdict.
    # Measured on 13 Nov over 211 documents on the current engine: it failed 18, and on every
    # one of them the render's own pitch, paired line for line, was correct to within 0.6 pt.
    # 14 of the 18 also fail 18_displacement, which measures per-line dy directly.
    # So: measure the pitch where pitch is defined - two consecutive lines of the SAME column,
    # on the BASELINE, present on both sides - and ask only that the median paired difference
    # be small. A single line out of place inside a table row is 18_displacement's question
    # and must not fail this one, which is why the statistic is a median and not a tail.
    def _pitch_lines(page):
        """(text, baseline_y, x0) for upright text lines. Slanted text is 35_rotation's."""
        out = []
        for blk in page.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                t = " ".join(s["text"] for s in ln.get("spans", [])).strip()
                if not t:
                    continue
                if abs(ln.get("dir", (1, 0))[0] - 1) > 0.01:
                    continue
                base = max(s["origin"][1] for s in ln["spans"] if s["text"].strip())
                out.append((t, round(base, 2), round(ln["bbox"][0], 1)))
        return out

    def _columns(lines, tol=2.0):
        cols = {}
        for t, y, x in lines:
            cols.setdefault(round(x / tol) * tol, []).append((y, t))
        for k in cols:
            cols[k].sort()
        return cols

    def pitch_pairs(a, b):
        """Consecutive baseline gaps down one column of `a`, paired by text to `b`."""
        pairs = []
        for i in range(min(a.page_count, b.page_count)):
            bl = _pitch_lines(b[i])
            bcols, bidx = _columns(bl), {}
            for t, y, x in bl:
                bidx.setdefault(t, []).append(y)
            for col in _columns(_pitch_lines(a[i])).values():
                texts = {t for _, t in col}
                best, bestn = None, 0
                for c in bcols.values():
                    n = len(texts & {t for _, t in c})
                    if n > bestn:
                        best, bestn = c, n
                if best is None or bestn < 2:
                    continue
                for (ya, ta), (yb, tb) in zip(col, col[1:]):
                    if ta not in bidx or tb not in bidx:
                        continue
                    ra = min(bidx[ta], key=lambda v: abs(v - ya))
                    rb = min(bidx[tb], key=lambda v: abs(v - yb))
                    if 1 < yb - ya < 200:
                        pairs.append((yb - ya, rb - ra))
        return pairs

    _pp = pitch_pairs(src, gd)
    if len(_pp) < 5:
        # Fewer than five lines can be paired: the render lost the lines, reflowed them, or
        # drew them as pictures. That is 04/31's, 22's and 35's question. This check reports
        # it measured nothing rather than inventing a pitch from a pooled y-set.
        s_p, g_p = 0, 0
        _p23_ok = True
        _p23_note = "unmeasured: %d paired line(s)" % len(_pp)
    else:
        _d = [r - a for a, r in _pp]
        s_p = round(median([a for a, r in _pp]), 1)
        g_p = round(median([r for a, r in _pp]), 1)
        _p23_ok = abs(median(_d)) <= 1.0
        _p23_note = ("%d paired gaps, median difference %+.2f pt"
                     % (len(_pp), median(_d)))
    checks["23_line_pitch"] = (s_p, g_p, _p23_ok)

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
    # THE CLASS IS TWO POPULATIONS AND THE COUNT CANNOT TELL THEM APART.
    #
    # Measured on 22728b1 over the 211-document corpus: 26_text_overlap fails 15 documents
    # with 588 counted overlaps between them, and those 588 are not one defect. Asking the
    # .docx which paragraph each overlapping run belongs to splits them cleanly:
    #
    #   539  both runs are in the SAME w:p - a line the paragraph wrapped onto a second
    #        line, whose advance collapsed. A paragraph is written with a line box of
    #        1.38 * size twips, lineRule="exact" (DocxWriter.java:110) - 0.069 em, 0.6 pt
    #        at 8.5 pt - while w:before is charged once per PARAGRAPH. So line 2 of a
    #        wrapped paragraph sits 0.6 pt under line 1 and every line after it adds
    #        another 0.6. On 360_restaurant_menu the cell is 1437 twips = 71.85 pt and the
    #        page drew "Chicken Malai Kebab" 92.12 pt wide in it, so "Kebab" lands 0.60 pt
    #        under "Chicken Malai"; on 350_question_paper a 43.4 pt cell holds a 15-line
    #        question and the cascade reaches 4.8 pt - 373 of the 588 on its own.
    #
    #   47   the two runs are in DIFFERENT paragraphs - no wrap and no collapsed advance.
    #        One line was placed on top of another: the flow after a table resuming from a
    #        table bottom the renderer did not draw (17_three_column_widths_txtpos 7,
    #        itr-computation-with-slab-table 5), two columns written into one flow
    #        (policy-2col-spanning-section-heading 4, 69_two_col_legal_numbered_clauses 2),
    #        a rotated stamp box off its y (02_stamp_rotated_15deg_upleft 5), a line pushed
    #        past the right margin (marksheet-subject-left-marks-right 5,
    #        table-of-contents-dot-leaders 5).
    #
    #   2    neither run is in the flow at all - it is inside an anchored text box, i.e. a
    #        stamp drawn over the page. 59_shape_anchor's question.
    #
    # Reported, not scored: the pass/fail rule is unchanged, the universe stays at 49, and
    # the split is attached only to a document that already fails - so every passing
    # document's JSON is byte-identical to what it was. Without it the two halves keep
    # being read as one number, which is how a fix for one is read as a regression of the
    # other.
    _p26 = None
    if on_text > max(s_on_text, 2, len(g_runs) // 50):
        _p26 = {"wrap": 0, "line_on_line": 0, "anchored": 0}
        _paras = []
        if docx_path and os.path.exists(docx_path):
            try:
                _xml = zipfile.ZipFile(docx_path).read("word/document.xml")
                _paras = [re.sub(r"\s+", "",
                                 "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", _s, re.S)))
                          for _s in _xml.decode("utf-8", "replace").split("</w:p>")]
                _paras = [q for q in _paras if q]
            except Exception:
                _paras = []
        for p in gd:
            rs = runs(p)
            for r in rs:
                for o in rs:
                    if o is r:
                        continue
                    if (r["x"] < o["x1"] - 1 and r["x1"] > o["x"] + 1 and
                            r["y"] < o["y1"] - 1 and r["y1"] > o["y"] + 1):
                        a = re.sub(r"\s+", "", r["text"])
                        b = re.sub(r"\s+", "", o["text"])
                        if any(a in q and b in q for q in _paras):
                            _p26["wrap"] += 1
                        elif any(a in q for q in _paras) and any(b in q for q in _paras):
                            _p26["line_on_line"] += 1
                        else:
                            _p26["anchored"] += 1
                        break
    checks["26_text_overlap"] = (s_on_text, on_text,
                                 on_text <= max(s_on_text, 2, len(g_runs) // 50),
                                 _p26)
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
    blank_loss, s_grid_total = 0, 0
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
    # tolerance is a fraction of the source's own occupied grid cells, not of its columns
    s_cells_total = max(1, s_grid_total)
    # The measurement is kept; the verdict is not. P2W_29_LATTICE prints the number this
    # lattice produced, so every figure in the retirement block below can be re-taken
    # without re-inventing the check. It never votes.
    if os.environ.get("P2W_29_LATTICE"):
        print("29 lattice: blank_loss %d, source cells %d, floor %d"
              % (blank_loss, s_cells_total, max(4, int(s_cells_total * 0.10))),
              file=sys.stderr)

    # ---- 29_blank_where_ink_was RETIRED 13 Nov -----------------------------
    # 30's twin, one line apart, on the same ruler. It was retired second only because 30
    # was the noisier of the two: the same residual flips 29 on 16 documents and 30 on 33
    # at 3.0 pt over half the runs. Same defect, same verdict, so the same retirement.
    #
    # WHAT IT MEASURED. One anchor point per SPAN - not ink area. Each run's TOP-LEFT is
    # bucketed into a 24x24 lattice (24.80 x 35.08 pt on A4), the render is bucketed in the
    # source's frame using the per-page median offset, and the score is the number of cells
    # the source occupied and the render did not, against max(4, 10 % of the source's own
    # occupied cells).
    #
    # THE RULER IS THE DEFECT, AND IT STILL IS. Re-measured at 22728b1 on three constructed
    # A4 pages, 30 runs one per lattice cell, ten of them moved 0.6 pt - a shift
    # 18_displacement cannot see, its tolerance being clamp(0.35*size, 1.5, 4.5) = 3.5 pt
    # at 10 pt:
    #   A  the ten sit 0.3 pt under a row edge and the move crosses it
    #      -> 29 = 6, FAIL, and 29 is the ONLY failing check of the 49
    #   B  the same ten, the same 0.6 pt, sitting 0.9 pt under the edge so nothing crosses
    #      -> 29 = 0, PASS, 49/49
    #   17_matched_runs, 18_displacement, 22_reading_order and 43_within_10pt_x are
    #   identical on A and B: 30/30, 0, 0, 100 %. A document's verdict turned on 0.6 pt.
    # The count is not even the number of runs that moved: ten moved and 29 read 6, because
    # four of them entered cells a neighbour already held. That is 30's anchor-not-ink
    # defect, in the direction that fails.
    #
    # AND THE 0.6 pt CASE NOW NEEDS A MINORITY. A fourth page moved ALL 30 runs the same
    # 0.6 pt and read 29 = 0: 6565508's per-page median subtracts a uniform shift before
    # bucketing, so the exact constructed case the condemnation was written from no longer
    # reproduces when every run moves. That does not rescue the check - it narrows which
    # documents it can fire on, and the ruler decides the rest.
    #
    # NO UNIQUE DOCUMENT, RE-CONFIRMED ON 211. Re-run at 22728b1 over the full corpus
    # (build-engine.sh, all 211 converted, LibreOffice renders, verify_google.py on each
    # pair): 34 documents fail 29, and ZERO of them fails 29 alone - removing the check
    # changes no document's verdict. 21 of the 34 sit at the constant floor of 4 cells, and
    # 4 are one cell over it (5 against 4). The direction is covered by checks that ask it
    # of the thing itself: 04_chars_missing and 17_matched_runs (constructed: ten runs
    # deleted reads 29 = 10, 04 = 30, 17 = 20 - 29 never fires alone), 47_margins (26 of
    # the 34), 18_displacement (27), 59_shape_anchor (22), 10_font_sizes (13).
    #
    # CORRECTION TO THE BRIEF THAT CONDEMNED IT, which claimed "of the 134 that failed it
    # in the 208-doc record, ZERO passed 17, 18 and 22". On RATCHET-20261112-095452.json
    # 134 fail 29 and TWELVE of them pass 17_matched_runs, 18_displacement and
    # 22_reading_order (306_clinical_protocol_synopsis, 32_serif_nondefault_body,
    # 333_datasheet_spec_tables, 341_shipping_manifest, 344_customs_declaration,
    # 375_attendance_register, 393_spectrum_peak_table, 404_sudoku_grid,
    # 410_form_xobject_reused, 416_many_tiny_pages, marksheet-university-consolidated,
    # table-of-contents-dot-leaders). Every one of the twelve fails 18_median_dy and
    # 19_worst_dy and 47_margins as well - the criterion named the wrong three checks, not
    # the wrong conclusion. On the live 211, 2 of the 34 pass 17/18/22 -
    # boq-horizontal-rules-only (29 = 11) and product-catalogue-code-left-price-right
    # (29 = 8) - and both fail 10_font_sizes and 47_margins.
    #
    # The class "ink in a region the source left blank" is an INK-AREA question and needs a
    # rasterised coverage test with a % -of-page tolerance; the spec is recorded in the 30
    # block below and is not shipped, for the reason given there. A check that asks it with
    # an occupancy lattice would be this check again under a new name.

    # ---- 30_ink_where_blank_was RETIRED 13 Nov -----------------------------
    # It was 29's expression with the difference taken the other way round, on the same
    # 24x24 lattice, the same per-page medians and the SAME denominator (the source's
    # occupied cells) and the SAME floor (max(4, 10 % of them)). The ruler was the
    # question, and the direction was not.
    #
    # WHAT IT MEASURED. One anchor point per SPAN - not ink area. A line of text 511 pt
    # wide is one cell if the extractor returns it as one span; eight short words are
    # eight cells (constructed: 16 added words at a 32 pt pitch came back as ONE span and
    # scored 30 = 1, while 8 added words at a 65 pt pitch scored 30 = 8). Cells occupied
    # by the render and not by the source, against max(4, int(0.10 * source cells)).
    #
    # THE RULER IS THE DEFECT, and it is measurable in both directions.
    #   * A residual of 0.3 pt - a fifth of 18_displacement's 1.5 pt floor, 1/83 of a
    #     cell - flips the verdict. Constructed, same 30-run page twice: five runs sitting
    #     0.15 pt before a column edge, nudged 0.3 pt, read 30 = 5 and FAIL; the same five
    #     runs sitting 0.15 pt past the edge, the same 0.3 pt nudge, read 30 = 0 and PASS,
    #     and on both pairs every other live check passes.
    #   * A displacement carried by the MAJORITY of runs is subtracted away by the median:
    #     a 25 pt shift of 25 of 30 runs reads 30 = 5, because the median dx is 25 and the
    #     correction undoes the shift it is supposed to expose. 43_within_10pt_x and
    #     21_median_dx catch that document; 30 does not.
    #   * The floor is not a fraction in practice: 153 of the 211 corpus documents hold
    #     <= 45 occupied cells, so the floor is the constant 4 on 73 % of the corpus and
    #     never exceeds 60. "10 % of cells" reads as "more than four cells" almost always.
    #
    # NO UNIQUE CLASS. Measured on the two recorded snapshots (RATCHET.json, 211 rows;
    # RATCHET-20261112-095452.json, 208 rows), with the retired ids mapped to their live
    # successors and the absorbed ones dropped: 30 fails 145 and 143 documents, and 0 of
    # them is failed by nothing else. 27 documents fail 30 without failing 29, and all 27
    # fail another live check. On the 208-row values, 13 of the 143 failures sit at
    # exactly 5 cells against a floor of 4 - one cell over, the same 13 knife-edge
    # documents 29 has.
    #
    # AND THE DIRECTION IS ALREADY COVERED, by checks that ask it of the thing itself:
    # text added -> 05_words_extra and 45_char_accuracy (constructed: a word added in a
    # blank row fails 45 and 30 reads 1 cell and passes; a band of eight added words fails
    # 45 and 30); a run moved into
    # blank space -> 43_within_10pt_x, 21_median_dx, 18_displacement, 47_margins,
    # 60_text_column_right_edge; a rule or shape drawn where the source had none ->
    # 32_stroke_lines, 14_filled_shapes, 59_shape_anchor; ink over ink -> 26_text_overlap;
    # an image where there was none -> 08_image_count, 39_image_position, 48_image_area.
    # 30's own proof mutation was mut_rule, which PROVE-GAPS.md already records as unable
    # to fire this check ("one rule rarely occupies a cell").
    #
    # If the class "ink in a region the source left blank" is ever wanted as its own
    # question, it is an INK-AREA question and needs a rasterised coverage test with a
    # % -of-page tolerance, not an occupancy lattice: the lattice's answer is decided by
    # where the anchor happened to fall, and the corpus contains no document whose only
    # defect is of that class.
    # 29_blank_where_ink_was, its twin, was on the same ruler and is retired in the block
    # above - same defect, same evidence, one day later.

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

    checks.update(extra_checks(src, gd, s_runs, g_runs, pairs, docx_path))
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
        # A check may carry a fourth element: what its count is MADE OF. Reported only,
        # never scored - a document that passes writes no detail and its JSON is
        # unchanged. 26_text_overlap is the one that needs it (see the split there).
        "checks": {k: dict({"source": v[0], "render": v[1], "ok": bool(v[2])},
                           **({"detail": v[3]} if len(v) > 3 and v[3] is not None else {}))
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
    # without it 54_image_dpi cannot be answered, and it now FAILS rather than passing
    # silently. The fallback is a convenience, not the contract: it only finds the .docx in
    # the two layouts the briefs use, so a run that reorganises its working directory loses
    # the measurement without losing the argument - pass --docx explicitly.
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
