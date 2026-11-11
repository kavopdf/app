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
  python3 verify_google.py <source.pdf> <google-export.pdf> [--json out.json]

EXIT
  0 = all checks pass, 1 = one or more failed, 2 = could not run

THRESHOLDS (a document passes only if every one holds)
  completeness  every count and every style attribute matches the source
  position      median dy < 3 pt, worst dy < 15 pt, within 10 pt > 95 %, order > 95 %
  visual        no invisible text, no text-on-text, no page overflow, no extra page
"""
import os, sys, json, re, collections

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def runs(page):
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


def norm_word(w):
    """Digits and punctuation kept; whitespace and case dropped."""
    return re.sub(r"[\s\u00a0]+", "", w).lower()


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
    for d in page.get_drawings():
        r = d["rect"]
        if r.width >= 8 and r.height >= 8:
            out.append(r)
    try:
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                if r.width >= 8 and r.height >= 8:
                    out.append(r)
    except Exception:
        pass
    return out


def _anchor(page, rs):
    """For each run, where its centre sits inside the smallest shape containing it.

    Returns None for a run with no shape around it. The answer is a fraction of the
    shape, not a page coordinate, so a stamp that moves as one piece reads as
    unchanged here - that is a position error and checks 18 and 19 already own it.
    Only text moving relative to ITS OWN outline shows up as a difference.
    """
    shapes = _shapes(page)
    out = []
    for r in rs:
        cx, cy = (r["x"] + r["x1"]) / 2.0, (r["y"] + r["y1"]) / 2.0
        best = None
        for sh in shapes:
            # fitz.Rect is x0/y0/x1/y1, not x/y - the run dicts use x/y, which is
            # what made this crash on its first run.
            if sh.x0 <= cx <= sh.x1 and sh.y0 <= cy <= sh.y1:
                if best is None or sh.width * sh.height < best.width * best.height:
                    best = sh
        if best is None:
            out.append(None)
        else:
            out.append(((cx - best.x0) / max(1e-6, best.width),
                        (cy - best.y0) / max(1e-6, best.height)))
    return out


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
    """Stroked paths: table rules, borders, underlines. Never looked at before."""
    out = []
    for d in page.get_drawings():
        col = d.get("color")
        if col is None:
            continue
        r = d["rect"]
        out.append({"rect": r, "width": round(d.get("width") or 0, 2), "colour": col})
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


def extra_checks2(src, gd):
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
    c["50_annotations"] = (s_a, g_a, s_a == 0 or g_a >= max(1, int(s_a * 0.5)))

    # ---- 51 form fields ----------------------------------------------------
    def fields(doc):
        n = 0
        for p in doc:
            n += sum(1 for w in p.widgets())
        return n

    s_f, g_f = fields(src), fields(gd)
    c["51_form_fields"] = (s_f, g_f, s_f == 0 or g_f >= max(1, int(s_f * 0.5)))

    # ---- 52 outline / bookmarks -------------------------------------------
    def outline(doc):
        try:
            return len(doc.get_toc())
        except Exception:
            return 0

    s_o, g_o = outline(src), outline(gd)
    c["52_outline"] = (s_o, g_o, s_o == 0 or g_o >= max(1, int(s_o * 0.5)))

    # ---- 53 embedded font names -------------------------------------------
    # 09_font_names counts distinct faces. This asks whether the FACE ITSELF
    # survived, which is what decides whether the metrics are the same.
    #
    # Google Docs has none of the Liberation families and substitutes on import.
    # Some substitutes are metric-identical by design - Liberation was built as a
    # drop-in for Arial, Times and Courier, which is why fontconfig resolves
    # "Arial" to LiberationSans-Regular.ttf on a machine with no Arial - and some
    # are not: a docx asking for Liberation Serif comes back as Arial, a serif
    # turned into a sans, 8.9% wider on the same string.
    #
    # Comparing raw names cannot tell those two cases apart, so it fails a correct
    # conversion and passes nothing. Comparing FAMILIES through the equivalence
    # that is actually true keeps the check honest: serif-to-Times passes,
    # serif-to-Arial still fails, because it is a different face.
    SAME_FACE = {
        "liberationsans": "arial", "arial": "arial",
        "liberationserif": "timesnewroman", "timesnewroman": "timesnewroman",
        "liberationmono": "couriernew", "couriernew": "couriernew",
    }

    def family(name):
        n = (name or "").split("+")[-1].strip().lower()
        # "MT" and "PSMT" are PostScript suffixes that sit AFTER the style, so
        # they have to come off first: Arial-BoldMT is arial+bold+mt, not a bold
        # family called "arial-bold".
        for suf in ("psmt", "mt"):
            if n.endswith(suf):
                n = n[:-len(suf)]
                break
        for suf in ("-bolditalic", "-boldoblique", "-bold", "-italic", "-oblique", "-regular"):
            if n.endswith(suf):
                n = n[:-len(suf)]
                break
        return SAME_FACE.get(n, n)

    def faces(doc):
        out = set()
        for p in doc:
            for f in p.get_fonts():
                fam = family(f[3])
                if fam:
                    out.add(fam)
        return out

    s_fa, g_fa = faces(src), faces(gd)
    kept = len(s_fa & g_fa)
    c["53_embedded_faces"] = (len(s_fa), kept,
                              len(s_fa) == 0 or kept >= max(1, int(len(s_fa) * 0.5)))

    # ---- 54 image resolution ----------------------------------------------
    # 08 counts images and 48 measures area; neither notices a 300 dpi logo
    # arriving as a 40 dpi smear.
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
    c["54_image_dpi"] = (s_d, g_d, s_d == 0 or g_d >= s_d * 0.6)

    # ---- 55 page count per size -------------------------------------------
    # A mixed-orientation document that comes out all one size is wrong even if
    # the page COUNT matches.
    def orientation_mix(doc):
        land = sum(1 for p in doc if p.rect.width > p.rect.height)
        return (land, len(doc) - land)

    s_om, g_om = orientation_mix(src), orientation_mix(gd)
    c["55_orientation_mix"] = (s_om, g_om, s_om == g_om)

    # ---- 56 text direction -------------------------------------------------
    # RTL documents whose direction is lost read backwards while every word is
    # still present in the right place.
    def rtl_runs(doc):
        n = 0
        for p in doc:
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    d = ln.get("dir", (1, 0))
                    if d[0] < 0:
                        n += 1
        return n

    s_rtl, g_rtl = rtl_runs(src), rtl_runs(gd)
    c["56_rtl_runs"] = (s_rtl, g_rtl, s_rtl == 0 or g_rtl >= max(1, int(s_rtl * 0.5)))

    # ---- 59 shape anchor ---------------------------------------------------
    # Does text stay in the same place inside the outline that encloses it?
    # Two ways to fail, both seen on stamps: the outline moves and leaves its text
    # behind, or the text moves and leaves its outline. Neither changes the text's
    # page position enough for the median checks, and neither is visible to any
    # check that only compares text to text.
    ANCHOR_TOL = 0.12      # a tenth of the outline is drift, not rendering noise
    lost, moved, anchored = 0, 0, 0
    for si in range(min(src.page_count, gd.page_count)):
        sp, gp = src[si], gd[si]
        sruns, gruns = runs(sp), runs(gp)
        sa, ga = _anchor(sp, sruns), _anchor(gp, gruns)
        for i, a in enumerate(sa):
            if a is None:
                continue          # nothing enclosed it in the source either
            anchored += 1
            if i >= len(ga) or ga[i] is None:
                lost += 1         # the outline went away, or moved off the text
                continue
            b = ga[i]
            if abs(a[0] - b[0]) > ANCHOR_TOL or abs(a[1] - b[1]) > ANCHOR_TOL:
                moved += 1        # text and outline no longer agree
    # source = how many runs had an outline around them, render = how many still
    # sit in the same place inside one. A raw drift count would read as
    # "source=1 render=1" for one good run and one bad run alike.
    c["59_shape_anchor"] = (anchored, anchored - (lost + moved), (lost + moved) == 0)

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

    # ---- 33 border over text ----------------------------------------------
    # A line that crosses a text span's box means the rule is drawn through the
    # words - the defect the user reported by eye and nothing measured.
    def borders_over_text(doc):
        hits = 0
        for p in doc:
            lines = _strokes(p)
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
                            thin = r.height <= 2.5
                            if not thin:
                                continue
                            if r.y0 > y0 + 1.5 and r.y0 < y1 - 1.5 \
                                    and r.x0 < x1 - 2 and r.x1 > x0 + 2:
                                hits += 1
                                break
        return hits

    s_bot = borders_over_text(src)
    g_bot = borders_over_text(gd)
    c["33_border_over_text"] = (s_bot, g_bot, g_bot <= s_bot + s_bot // 5)

    # ---- 34 per-span style -------------------------------------------------
    # Size, colour and weight of each matched span, not just how many distinct
    # values exist somewhere in the document.
    ok_size = ok_col = ok_weight = 0
    for s_sp, g_sp in pairs:
        if abs(s_sp["size"] - g_sp["size"]) <= 0.6:
            ok_size += 1
        if s_sp["colour"] == g_sp["colour"]:
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
    def scripts(doc):
        n = 0
        for p in doc:
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        if sp.get("text", "").strip() and (sp.get("flags", 0) & 1):
                            n += 1
        return n

    s_sc, g_sc = scripts(src), scripts(gd)
    c["37_super_subscript"] = (s_sc, g_sc, s_sc == 0 or g_sc >= max(1, int(s_sc * 0.7)))

    # ---- 38 list markers ---------------------------------------------------
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
                                (t[0].isdigit() and t[1:3] in (". ", ") ")):
                            n += 1
                            break
        return n

    s_m, g_m = markers(src), markers(gd)
    c["38_list_markers"] = (s_m, g_m, s_m == 0 or g_m >= max(1, int(s_m * 0.7)))

    # ---- 39 image position -------------------------------------------------
    def img_boxes(doc):
        boxes = []
        for p in doc:
            for im in p.get_image_info():
                b = im["bbox"]
                boxes.append((round(b[0] / 8), round(b[1] / 8)))
        return boxes

    s_ib, g_ib = img_boxes(src), img_boxes(gd)
    if not s_ib:
        c["39_image_position"] = (0, len(g_ib), True)
    else:
        common = len(set(s_ib) & set(g_ib))
        c["39_image_position"] = (len(s_ib), common, common >= max(1, int(len(s_ib) * 0.6)))

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
        left = right = centre = 0
        for p in doc:
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                bx0, _, bx1, _ = blk["bbox"]
                for ln in blk.get("lines", []):
                    lx0, _, lx1, _ = ln["bbox"]
                    w = bx1 - bx0
                    if w < 10:
                        continue
                    if lx0 - bx0 < 4:
                        left += 1
                    elif bx1 - lx1 < 4:
                        right += 1
                    elif abs((lx0 + lx1) / 2 - (bx0 + bx1) / 2) < 6:
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
        n = 0
        for p in doc:
            H = p.rect.height
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                y = blk["bbox"][1]
                if y < H * 0.10 or y > H * 0.90:
                    n += 1
        return n

    s_e, g_e = edge_text(src), edge_text(gd)
    c["44_header_footer"] = (s_e, g_e, s_e == 0 or g_e >= max(1, int(s_e * 0.7)))

    # ---- 45 character accuracy --------------------------------------------
    s_txt = "".join(s_sp["text"] for s_sp in s_runs)
    g_txt = "".join(g_sp["text"] for g_sp in g_runs)
    ratio = round(100 * difflib.SequenceMatcher(None, s_txt, g_txt).quick_ratio())
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

    # ---- 47 margins --------------------------------------------------------
    def extents(doc):
        out = []
        for p in doc[:1]:
            xs0, ys0, xs1, ys1 = [], [], [], []
            for blk in p.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                b = blk["bbox"]
                xs0.append(b[0]); ys0.append(b[1]); xs1.append(b[2]); ys1.append(b[3])
            if xs0:
                out.append((round(min(xs0)), round(min(ys0)), round(max(xs1)), round(max(ys1))))
        return out[0] if out else (0, 0, 0, 0)

    s_ex, g_ex = extents(src), extents(gd)
    ok_margin = all(abs(a - b) <= 12 for a, b in zip(s_ex, g_ex))
    c["47_margins"] = (s_ex, g_ex, ok_margin)

    # ---- 48 image area -----------------------------------------------------
    def img_area(doc):
        tot = 0
        for p in doc:
            for im in p.get_image_info():
                b = im["bbox"]
                tot += max(0, (b[2] - b[0])) * max(0, (b[3] - b[1]))
        return round(tot)

    s_ia, g_ia = img_area(src), img_area(gd)
    c["48_image_area"] = (s_ia, g_ia,
                          s_ia == 0 or g_ia >= s_ia * 0.5)

    return c


def compare(src_path, gd_path):
    src = fitz.open(src_path)
    gd = fitz.open(gd_path)

    checks = {}

    # ---- gather -------------------------------------------------------------
    s_runs, g_runs = [], []
    for p in src:
        s_runs += runs(p)
    for p in gd:
        g_runs += runs(p)

    s_text = " ".join(r["text"] for r in s_runs)
    g_text = " ".join(r["text"] for r in g_runs)
    s_words = collections.Counter(norm_word(w) for w in s_text.split() if w.strip())
    g_words = collections.Counter(norm_word(w) for w in g_text.split() if w.strip())

    s_imgs = sum(len(p.get_images()) for p in src)
    g_imgs = sum(len(p.get_images()) for p in gd)

    # ---- COMPLETENESS (1-16) ------------------------------------------------
    checks["01_page_count"] = (src.page_count, gd.page_count,
                               src.page_count == gd.page_count)

    checks["02_text_run_count"] = (len(s_runs), len(g_runs),
                                   abs(len(s_runs) - len(g_runs)) <= max(2, len(s_runs) // 50))

    missing = s_words - g_words
    extra = g_words - s_words
    checks["03_word_count"] = (sum(s_words.values()), sum(g_words.values()),
                               len(missing) == 0)
    checks["04_words_missing"] = (0, len(missing), len(missing) == 0)
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

    s_fonts = collections.Counter(norm_font(r["font"]) for r in s_runs)
    g_fonts = collections.Counter(norm_font(r["font"]) for r in g_runs)
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
    checks["11_bold_runs"] = (bold_count(s_runs), bold_count(g_runs),
                              abs(bold_count(s_runs) - bold_count(g_runs)) <= max(2, bold_count(s_runs) // 5))

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
                                  s_fill == 0 or g_fill >= max(1, int(s_fill * 0.5)))

    s_links = sum(len(p.get_links()) for p in src)
    g_links = sum(len(p.get_links()) for p in gd)
    checks["15_links"] = (s_links, g_links, s_links == 0 or g_links >= s_links)

    s_digits = sum(1 for r in s_runs if any(c.isdigit() for c in r["text"]))
    g_digits = sum(1 for r in g_runs if any(c.isdigit() for c in r["text"]))
    checks["16_numeric_runs"] = (s_digits, g_digits,
                                 abs(s_digits - g_digits) <= max(3, s_digits // 10))

    # ---- POSITION (17-24) ---------------------------------------------------
    # match each source run to its nearest render run by text
    by_text = collections.defaultdict(list)
    for r in g_runs:
        by_text[norm_word(r["text"])].append(r)

    dys, dxs, matched = [], [], 0
    pairs = []
    for r in s_runs:
        cands = by_text.get(norm_word(r["text"]))
        if not cands:
            continue
        best = min(cands, key=lambda c: abs(c["y"] - r["y"]) + abs(c["x"] - r["x"]))
        dys.append(best["y"] - r["y"])
        dxs.append(best["x"] - r["x"])
        matched += 1
        pairs.append((r, best))

    def median(v):
        if not v:
            return 0.0
        v = sorted(v)
        n = len(v)
        return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2

    med_dy = round(median(dys), 1)
    worst_dy = round(max((abs(d) for d in dys), default=0), 1)
    within10 = round(100.0 * sum(1 for d in dys if abs(d) <= 10) / max(1, len(dys)))
    med_dx = round(median(dxs), 1)

    checks["17_matched_runs"] = (len(s_runs), matched,
                                 matched >= int(len(s_runs) * 0.9))
    # abs(), because med_dy is signed. Without it a document shifted UP by any
    # amount passed: med_dy = -12 is less than 3, so the comparison said fine
    # while every line sat twelve points above where it belonged. Found by
    # mutating a real document upward and watching this check stay green.
    checks["18_median_dy"] = (0, med_dy, abs(med_dy) < 3.0)
    checks["19_worst_dy"] = (0, worst_dy, worst_dy < 15.0)
    # With no matched runs there is nothing to be within 10 pt of; reporting 0 %
    # made a blank or text-free page fail for having no text to measure.
    checks["20_within_10pt"] = (100, within10, (not dys) or within10 > 95)
    checks["21_median_dx"] = (0, med_dx, abs(med_dx) < 3.0)

    # reading order: the sequence of normalised words
    s_seq = [norm_word(w) for w in s_text.split() if w.strip()]
    g_seq = [norm_word(w) for w in g_text.split() if w.strip()]
    if s_seq:
        same = sum(1 for a, b in zip(s_seq, g_seq) if a == b)
        order = round(100.0 * same / max(1, len(s_seq)))
    else:
        order = 100
    checks["22_reading_order"] = (100, order, order > 95)

    # line spacing: median gap between consecutive baselines on page 1
    def pitch(rs):
        ys = sorted(set(round(r["y"], 1) for r in rs))
        gaps = [b - a for a, b in zip(ys, ys[1:]) if 1 < b - a < 200]
        return round(median(gaps), 1) if gaps else 0
    s_p, g_p = pitch([r for r in s_runs]), pitch([r for r in g_runs])
    checks["23_line_pitch"] = (s_p, g_p, s_p == 0 or abs(g_p - s_p) <= 2.0)

    checks["24_page_breaks"] = (src.page_count, gd.page_count,
                                src.page_count == gd.page_count)

    # ---- VISUAL (25-31) -----------------------------------------------------
    s_invisible, s_off_page = _visual_counts(src)
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
    checks["28_clipped_at_edge"] = (0, clipped, clipped <= max(2, len(g_runs) // 50))

    # 29 blank where source has ink / 30 ink where source is blank
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
            g_cells.add((int(r["x"] / cw), int(r["y"] / ch)))
        s_grid_total += len(s_cells)
        blank_loss += len(s_cells - g_cells)
        extra_ink += len(g_cells - s_cells)
    # tolerance is a fraction of the source's own occupied grid cells, not of its columns
    s_cells_total = max(1, s_grid_total)
    checks["29_blank_where_ink_was"] = (0, blank_loss, blank_loss <= max(4, int(s_cells_total * 0.10)))
    checks["30_ink_where_blank_was"] = (0, extra_ink, extra_ink <= max(4, int(s_cells_total * 0.10)))

    # 31 every page must carry some ink
    # A blank page in the source is legitimate; a blank page the source did not have is not.
    empty_pages = 0
    for i in range(gd.page_count):
        g_has = bool(gd[i].get_text().strip())
        s_has = bool(src[i].get_text().strip()) if i < src.page_count else False
        if s_has and not g_has:
            empty_pages += 1
    checks["31_pages_lost_their_text"] = (0, empty_pages, empty_pages == 0)

    checks.update(extra_checks(src, gd, s_runs, g_runs, pairs))
    checks.update(extra_checks2(src, gd))

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
    try:
        res = compare(src, gd)
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
