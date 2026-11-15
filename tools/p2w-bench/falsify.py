#!/usr/bin/env python3
"""
falsify.py - THE FALSIFIABILITY GATE. Can every check be made to fail?

WHY THIS EXISTS
  A check that passes is evidence of nothing until you know it could have failed.
  Measured three times by three agents on this instrument, 37.8 % of its passing
  cells - 3,376 of 8,923 - belonged to checks whose only firing case had been
  repaired, and 20 of 42 checks were dead at 0c2beaa. The share RISES as the engine
  improves, because every defect fixed turns a live check into a dead one. That is
  arithmetic, not a paradox, and it is why "the score went up" has meant nothing.

  The instrument has no defence against this on its own. A predicate whose guard is
  wrong, whose population is empty, or whose two operands are the same expression
  returns ok=True on every document in the corpus, and reads exactly like a check
  that is doing its job. test_checks.py is not that defence either: its fixtures are
  CONSTRUCTED, so it proves a check can fire on a document that was built to make it
  fire, which is the weakest form of the claim.

WHAT THIS DOES
  For every check id in the instrument it mutates ONE real corpus document - the
  source PDF, the engine's .docx, or the LibreOffice render of that .docx - in the
  one way the check claims to measure, and then runs the verifier on the mutated
  triple. The check MUST return ok=False. If no mutation fires it, the check is
  reported BROKEN. It is never reported as passing.

  Every mutation is run with a CONTROL: the same document, unmutated. A mutation
  only counts as evidence for a check if the control passed that check, because a
  check that was already failing cannot be said to have been made to fail. Where the
  corpus document itself already fails the check (601_fillable_admission_form fails
  51, 44_coloured_underlined_hyperlinks fails 40), the control is a stated
  modification of the same document - the note on the mutation says which.

  The mutation is applied to ONE side and the side is recorded:
    source  the corpus PDF      - "the page the document asked for"
    docx    the engine's .docx  - "what the engine wrote"
    render  the LibreOffice PDF - "what the reader gets"
  Mutating the source is the mirror image of mutating the render for a symmetric
  check, and it is used where a render-side mutation cannot be made reliably. Which
  side was mutated is in the table; nothing here claims the engine produces these
  defects.

  Knock-ons are expected and are not a defect: removing a line of text moves 04, 17,
  18, 31, 45 and 59 at once. Each check is credited with the mutation that fired it;
  the full matrix is written out so the overlap can be read rather than trusted.

USAGE
  python3 tools/p2w-bench/falsify.py --corpus DIR --render DIR --docx DIR \
          [--out falsify.json] [--md falsify.md] [-v]

EXIT
  0 = every check fired on at least one generated mutation
  1 = at least one check could not be made to fail  (the gate FAILS)
  2 = could not run
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import warnings
import zipfile

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import fitz
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)

import verify_google as V


# ---------------------------------------------------------------------------
# the triple a mutation is applied to
# ---------------------------------------------------------------------------
class Triple(object):
    def __init__(self, src, render, docx, tmp):
        self.src, self.render, self.docx, self.tmp = src, render, docx, tmp

    def copy(self, tag, side, ext):
        """A fresh path for the mutated file, in the mutation's own temp dir."""
        return os.path.join(self.tmp, "%s.%s" % (tag, ext))

    def with_side(self, tag, side, path):
        t = Triple(self.src, self.render, self.docx, self.tmp)
        if side == "source":
            t.src = path
        elif side == "render":
            t.render = path
        elif side == "docx":
            t.docx = path
        else:
            raise ValueError(side)
        return t


# ---------------------------------------------------------------------------
# PDF primitives. Every one of them produces a NEW file; nothing is edited in place.
# ---------------------------------------------------------------------------
def _lines(page):
    """Every text line on the page: (bbox, text, size)."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            t = " ".join("".join(sp.get("text", "") for sp in ln["spans"]).split())
            size = max((sp.get("size") or 0) for sp in ln["spans"]) if ln["spans"] else 0
            if t:
                out.append((fitz.Rect(ln["bbox"]), t, size))
    return out


def blank_rect(page, w=160.0, h=60.0, pad=2.0):
    """The first w x h rectangle on this page that the page draws nothing in.

    Needed because a mutation that ADDS ink has to add it where there is no ink, or
    it becomes a second mutation (an overlap, a crossing, a reflow) and the check
    under test is no longer the only thing that moved.
    """
    obst = [fitz.Rect(ln[0]) for ln in _lines(page)]
    for d in page.get_drawings():
        r = d.get("rect")
        if r is not None and not r.is_empty:
            obst.append(fitz.Rect(r))
    for im in page.get_image_info():
        obst.append(fitz.Rect(im["bbox"]))
    W, H = page.rect.width, page.rect.height
    y = H - h - 4
    while y > 4:
        x = 4
        while x + w < W - 4:
            cand = fitz.Rect(x, y, x + w, y + h)
            if not any(cand.intersects(o + (-pad, -pad, pad, pad)) for o in obst):
                return cand
            x += 12
        y -= 12
    return None


def shift_doc(src, dst, dx=0.0, dy=0.0):
    """Translate every page's content by (dx, dy). Text stays text."""
    doc = fitz.open(src)
    out = fitz.open()
    for p in doc:
        np_ = out.new_page(width=p.rect.width, height=p.rect.height)
        tgt = fitz.Rect(p.rect.x0 + dx, p.rect.y0 + dy,
                        p.rect.x1 + dx, p.rect.y1 + dy)
        np_.show_pdf_page(tgt, doc, p.number)
    out.save(dst, garbage=3, deflate=True)
    out.close()
    doc.close()


def vscale_doc(src, dst, s=0.85):
    """Compress the page's content vertically by s, anchored at the bottom.

    One call, and every line's baseline moves in proportion - which is what changes
    the LINE PITCH by (1-s) x pitch while leaving the text on the page.
    """
    doc = fitz.open(src)
    out = fitz.open()
    for p in doc:
        W, H = p.rect.width, p.rect.height
        np_ = out.new_page(width=W, height=H)
        np_.show_pdf_page(fitz.Rect(0, H * (1 - s), W, H), doc, p.number)
    out.save(dst, garbage=3, deflate=True)
    out.close()
    doc.close()


def dup_page(src, dst, pno=0):
    a = fitz.open(src)          # the page's source
    b = fitz.open(src)          # the document it is inserted into
    b.insert_pdf(a, from_page=pno, to_page=pno, start_at=pno)
    b.save(dst, garbage=3, deflate=True)
    b.close()
    a.close()


def redact(src, dst, boxes, images=None):
    """Remove the text (and optionally the images) under each box."""
    doc = fitz.open(src)
    for pno, box in boxes:
        doc[pno].add_redact_annot(fitz.Rect(box))
    for p in doc:
        kw = {}
        if images is not None:
            kw["images"] = images
        p.apply_redactions(**kw)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def drop_images(src, dst):
    doc = fitz.open(src)
    for p in doc:
        for im in p.get_image_info():
            p.add_redact_annot(fitz.Rect(im["bbox"]))
    for p in doc:
        p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def set_size(src, dst, w, h, pno=0):
    doc = fitz.open(src)
    doc[pno].set_mediabox(fitz.Rect(0, 0, w, h))
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def add_text(src, dst, items):
    """items: [(pno, x, y, text, size, colour, fontname, render_mode)]"""
    doc = fitz.open(src)
    for pno, x, y, t, size, col, font, mode in items:
        doc[pno].insert_text((x, y), t, fontsize=size, color=col,
                             fontname=font, render_mode=mode)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def add_fills(src, dst, items):
    """items: [(pno, rect, colour)] - a filled rectangle, no stroke."""
    doc = fitz.open(src)
    for pno, r, col in items:
        doc[pno].draw_rect(fitz.Rect(r), color=None, fill=col, width=0)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def add_rules(src, dst, items):
    """items: [(pno, p1, p2, width)] - a stroked rule."""
    doc = fitz.open(src)
    for pno, p1, p2, w in items:
        doc[pno].draw_line(p1, p2, color=(0, 0, 0), width=w)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def _grey(n, col):
    """An n x n solid grey pixmap. Pixmap.set_rect() wants an int, not a tuple."""
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, n, n), 0)
    pix.clear_with(int(round(255 * (sum(col) / 3.0))))
    return pix


def add_images(src, dst, items):
    """items: [(pno, rect, colour)] - a 40x40 raster picture placed in that rect."""
    doc = fitz.open(src)
    for pno, r, col in items:
        doc[pno].insert_image(fitz.Rect(r), pixmap=_grey(40, col))
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def add_links(src, dst, items):
    doc = fitz.open(src)
    for pno, r, uri in items:
        doc[pno].insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(r), "uri": uri})
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def add_toc(src, dst, entries):
    doc = fitz.open(src)
    doc.set_toc(entries)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def move_lines(src, dst, pno, moves):
    """Move whole lines, one at a time.

    moves: [(bbox, dx, dy)].

    THE ORIGINAL TEXT IS REDACTED OUT, NOT PAINTED OVER. A white rectangle hides a line
    from a reader and leaves it in the content stream, so the extractor reports BOTH
    copies and the line is no longer unique on the page - which made 42 skip every
    moved line (len(si) != 1 or len(gi) != 1) and read 0 contradictions on a page
    where eight lines had visibly moved. Found by this gate, on its own mutation.
    So: redact the line out of one copy of the page, draw that copy, then place each
    line back from the untouched original at its new place. Glyphs stay glyphs.
    """
    doc = fitz.open(src)
    page = doc[pno]
    hole = fitz.open(src)
    hp = hole[pno]
    for bbox, dx, dy in moves:
        hp.add_redact_annot(fitz.Rect(bbox))
    hp.apply_redactions()
    out = fitz.open()
    np_ = out.new_page(width=page.rect.width, height=page.rect.height)
    np_.show_pdf_page(np_.rect, hole, pno)
    for bbox, dx, dy in moves:
        r = fitz.Rect(bbox)
        tgt = fitz.Rect(r.x0 + dx, r.y0 + dy, r.x1 + dx, r.y1 + dy)
        np_.show_pdf_page(tgt, doc, pno, clip=r)
    out.save(dst, garbage=3, deflate=True)
    out.close()
    hole.close()
    doc.close()


def retext_span(src, dst, pno, bbox, text, size, colour, font):
    """Erase one span and draw the same text back in another face/colour/size.

    The text and the place are unchanged, so the run still PAIRS with its source
    counterpart and 34a/34b/34c have a pair to judge - which is the whole point: a
    mutation that broke the pairing would make those three checks abstain instead of
    fail, and an abstention is not evidence.
    """
    doc = fitz.open(src)
    page = doc[pno]
    r = fitz.Rect(bbox)
    page.add_redact_annot(r)
    page.apply_redactions()
    page.insert_text((r.x0, r.y1 - (r.height * 0.22)), text, fontsize=size,
                     color=colour, fontname=font)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


def clear_widgets(src, dst, value=None, which=None):
    """Set every form widget's value to `value` (default ''). `which` limits to one."""
    doc = fitz.open(src)
    n = 0
    for p in doc:
        for w in p.widgets() or []:
            if which is not None and n != which:
                n += 1
                continue
            try:
                w.field_value = "" if value is None else value
                w.update()
            except Exception:
                pass
            n += 1
    doc.save(dst, garbage=3, deflate=True)
    doc.close()


# ---------------------------------------------------------------------------
# docx primitives. A .docx is a zip; the mutation is a string edit of one part.
# ---------------------------------------------------------------------------
def docx_edit(src, dst, fn, part="word/document.xml"):
    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    data = zin.read(part).decode("utf-8")
    new = fn(data)
    if new is None:
        raise RuntimeError("docx mutation produced nothing")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            if n == part:
                z.writestr(n, new.encode("utf-8"))
            else:
                z.writestr(n, zin.read(n))
    zin.close()


def _drop_first(pattern, xml, count=1):
    for _ in range(count):
        m = re.search(pattern, xml, re.S)
        if not m:
            raise RuntimeError("nothing matched %r" % pattern)
        xml = xml[:m.start()] + xml[m.end():]
    return xml


# ---------------------------------------------------------------------------
# the mutations
# ---------------------------------------------------------------------------
# base: the corpus document the mutation is applied to. Chosen once, from the
# baseline run, as a document on which the target checks PASS and are applicable -
# a mutation on a document that already fails the check proves nothing.
BASES = {
    "A": "300_prescription_rx",                  # 47/47 pass, draws an image, 6 band lines
    "T": "two-tables-stacked-with-no-gap",       # 47/47 pass, carries two tables
    "L": "44_coloured_underlined_hyperlinks",    # links + 5 underlines (fails 40 as it stands)
    "N": "600_reviewed_invoice_with_annotations",  # 3 annotation strings (50 passes)
    "F": "601_fillable_admission_form",          # 11 form widgets (fails 51 as it stands)
    "R": "344_customs_declaration",              # 1 rotated run, 35 passes
    "J": "journal-2col-with-footnotes",          # 3 script runs (fails 37 as it stands)
}


class Mut(object):
    def __init__(self, mid, base, side, note, apply, targets, control=None):
        self.id, self.base, self.side = mid, base, side
        self.note, self.apply, self.targets = note, apply, targets
        self.control = control      # an override that produces the CONTROL triple


MUTATIONS = []


def mut(mid, base, side, targets, note, control=None):
    def deco(fn):
        MUTATIONS.append(Mut(mid, base, side, note, fn, targets, control))
        return fn
    return deco


# ---- source-side: the page the document asked for -------------------------
@mut("m_src_extra_sizes", "A", "source", ["10_font_sizes"],
     "five text sizes the page does not use are added to the source; the render "
     "cannot have kept them")
def _(t):
    doc = fitz.open(t.src)
    pg = doc[0]
    r = blank_rect(pg, 200, 90)
    doc.close()
    items = [(0, r.x0, r.y0 + 14 * (i + 1), "sized %d" % i, sz, (0, 0, 0), "helv", 0)
             for i, sz in enumerate((7.5, 9.5, 13.5, 17.5, 21.5))]
    p = t.copy("extra_sizes", "source", "pdf")
    add_text(t.src, p, items)
    return t.with_side("extra_sizes", "source", p)


@mut("m_src_extra_colour", "A", "source", ["13_text_colours"],
     "a run of text in a colour the document does not otherwise use is added to the "
     "source; a render that keeps every colour it was given still has not gained this one")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 200, 40)
    doc.close()
    p = t.copy("extra_colour", "source", "pdf")
    add_text(t.src, p, [(0, r.x0, r.y0 + 16, "coloured run", 11,
                         (0.05, 0.72, 0.31), "helv", 0)])
    return t.with_side("extra_colour", "source", p)


@mut("m_src_rule", "A", "source", ["32_stroke_lines"],
     "an isolated 0.8 pt rule is drawn in blank space in the source; the render cannot "
     "have carried a rule the page did not draw")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 220, 40)
    doc.close()
    p = t.copy("rule", "source", "pdf")
    add_rules(t.src, p, [(0, (r.x0, r.y0 + 20), (r.x0 + 200, r.y0 + 20), 0.8)])
    return t.with_side("rule", "source", p)


@mut("m_src_underline", "A", "source", ["36_underline_rules"],
     "four rules the exact width of four source lines are drawn under their baselines; "
     "the render carries 1 rule under text and the check needs 2 of 4")
def _(t):
    doc = fitz.open(t.src)
    lines = [l for l in _lines(doc[0]) if l[0].width > 60][:4]
    doc.close()
    p = t.copy("underline", "source", "pdf")
    add_rules(t.src, p, [(0, (b.x0, b.y1 - 0.5), (b.x1, b.y1 - 0.5), 0.7)
                         for b, _, _ in lines])
    return t.with_side("underline", "source", p)


@mut("m_src_markers", "A", "source", ["38_list_markers"],
     "four bulleted lines are added to the source; the render keeps the three markers "
     "it was given and cannot have kept the four it was not")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 200, 80)
    doc.close()
    p = t.copy("markers", "source", "pdf")
    add_text(t.src, p, [(0, r.x0, r.y0 + 16 * (i + 1), "\u2022 item %d" % i,
                         10, (0, 0, 0), "helv", 0) for i in range(4)])
    return t.with_side("markers", "source", p)


@mut("m_src_fill", "A", "source", ["14_filled_shapes"],
     "a 200 x 90 pt solid block is filled in blank space in the source; the render has "
     "no fill over its centre and the block is well over the check's 400 pt2 floor")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 200, 90)
    doc.close()
    p = t.copy("fill", "source", "pdf")
    add_fills(t.src, p, [(0, r, (0.10, 0.30, 0.60))])
    return t.with_side("fill", "source", p)


@mut("m_src_image", "A", "source", ["39_image_position", "08_image_count", "48_image_area"],
     "a 120 x 90 pt picture is placed in blank space in the source; the render draws the "
     "one picture it was given")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 120, 90)
    doc.close()
    p = t.copy("image", "source", "pdf")
    add_images(t.src, p, [(0, r, (0.2, 0.2, 0.2))])
    return t.with_side("image", "source", p)


def _script_repair(t):
    """journal-2col-with-footnotes draws 3 script runs and its .docx places none, so 37
    fails it as it stands. The control is that same .docx with three vertical placements
    written into it - the defect repaired - which 37 reads as a pass. The mutation then
    strips every placement back out."""
    def f(x):
        done = [0]

        def para(m):
            p = m.group(0)
            if done[0] >= 3:
                return p
            runs = list(re.finditer(r"<w:r>.*?</w:r>", p, re.S))
            if len(runs) < 2:
                return p
            out = p
            for r in reversed(runs):
                if done[0] >= 3:
                    break
                rr = r.group(0)
                if "<w:vertAlign" in rr or "<w:position " in rr:
                    continue
                i = rr.find("<w:rPr>")
                rr2 = (rr[:i + 7] + '<w:vertAlign w:val="superscript"/>' + rr[i + 7:]
                       if i >= 0 else rr)
                out = out[:r.start()] + rr2 + out[r.end():]
                done[0] += 1
            return out
        y = re.sub(r"<w:p[ >].*?</w:p>", para, x, flags=re.S)
        if not done[0]:
            raise RuntimeError("no multi-run paragraph to place a script mark in")
        return y
    q = os.path.join(t.tmp, "script_control.docx")
    docx_edit(t.docx, q, f)
    return t.with_side("script_control", "docx", q)


@mut("m_docx_script_strip", "J", "docx", ["37_super_subscript"],
     "every w:vertAlign / w:position is stripped out of the .docx: the page draws three "
     "script runs and the engine places none of them vertically", control=_script_repair)
def _(t):
    def f(x):
        y = re.sub(r"<w:vertAlign[^>]*/>", "", x)
        y = re.sub(r"<w:position [^>]*/>", "", y)
        if y == x:
            raise RuntimeError("no vertical placement to strip")
        return y
    q = os.path.join(t.tmp, "script_strip.docx")
    docx_edit(_script_repair(t).docx, q, f)
    return t.with_side("script_strip", "docx", q)


@mut("m_src_link", "A", "source", ["40_link_targets"],
     "a link target is added to the source; the render carries the none it was given, so "
     "the target is lost. (The corpus has one linked document and it already fails this "
     "check, so the control is an unlinked document and the mutation is the link.)")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 120, 20)
    doc.close()
    p = t.copy("link", "source", "pdf")
    add_links(t.src, p, [(0, r, "https://falsify.invalid/target")])
    return t.with_side("link", "source", p)


@mut("m_src_outline", "A", "source", ["52_outline"],
     "a one-entry /Outlines tree is added to the source; the render's own heading "
     "bookmarks are a different tree, so the structure differs")
def _(t):
    p = t.copy("outline", "source", "pdf")
    add_toc(t.src, p, [[1, "Falsify chapter", 1]])
    return t.with_side("outline", "source", p)


# ---- render-side: what the reader gets ------------------------------------
@mut("m_ren_page_dup", "A", "render",
     ["01_page_count", "55_orientation_mix"],
     "a page is duplicated in the render; the source has one page and the render now has two")
def _(t):
    p = t.copy("page_dup", "render", "pdf")
    dup_page(t.render, p, 0)
    return t.with_side("page_dup", "render", p)


@mut("m_ren_erase_all", "A", "render",
     ["31_pages_lost_their_text", "04_chars_missing", "17_matched_runs",
      "45_char_accuracy", "59_shape_anchor", "18_displacement"],
     "every glyph on the page is redacted out of the render: the page loses its text")
def _(t):
    doc = fitz.open(t.render)
    boxes = [(p.number, p.rect) for p in doc]
    doc.close()
    p = t.copy("erase_all", "render", "pdf")
    redact(t.render, p, boxes)
    return t.with_side("erase_all", "render", p)


@mut("m_ren_erase_lines", "A", "render", ["04_chars_missing", "45_char_accuracy"],
     "four lines are redacted out of the render; the source still has their characters")
def _(t):
    doc = fitz.open(t.render)
    lines = [l for l in _lines(doc[0]) if l[0].width > 40][:4]
    doc.close()
    p = t.copy("erase_lines", "render", "pdf")
    redact(t.render, p, [(0, b) for b, _, _ in lines])
    return t.with_side("erase_lines", "render", p)


@mut("m_ren_add_text", "A", "render", ["05_chars_extra"],
     "a word the source does not carry is drawn in blank space in the render")
def _(t):
    doc = fitz.open(t.render)
    r = blank_rect(doc[0], 160, 24)
    doc.close()
    p = t.copy("add_text", "render", "pdf")
    add_text(t.render, p, [(0, r.x0, r.y0 + 14, "ZZQXJ", 11, (0, 0, 0), "helv", 0)])
    return t.with_side("add_text", "render", p)


@mut("m_ren_drop_image", "A", "render",
     ["08_image_count", "48_image_area", "39_image_position"],
     "the picture is removed from the render; the source draws one")
def _(t):
    p = t.copy("drop_image", "render", "pdf")
    drop_images(t.render, p)
    return t.with_side("drop_image", "render", p)


@mut("m_ren_shrink_image", "A", "render", ["48_image_area"],
     "the picture is redrawn at half its width and height from the same top-left corner: "
     "the COUNT is unchanged (so 08 passes) and the corner has not moved (so 39 passes), "
     "and only the area is wrong. This is what separates 48 from 08 and 39")
def _(t):
    doc = fitz.open(t.render)
    boxes = [(p.number, fitz.Rect(im["bbox"])) for p in doc for im in p.get_image_info()]
    if not boxes:
        raise RuntimeError("no image in the render")
    pno, b = boxes[0]
    pg = doc[pno]
    pg.add_redact_annot(b)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
    pix = _grey(40, (30, 30, 30))
    pg.insert_image(fitz.Rect(b.x0, b.y0, b.x0 + b.width / 2.0, b.y0 + b.height / 2.0),
                    pixmap=pix)
    p = t.copy("shrink_image", "render", "pdf")
    doc.save(p, garbage=3, deflate=True)
    doc.close()
    return t.with_side("shrink_image", "render", p)


@mut("m_ren_page_size", "A", "render", ["49_page_size"],
     "the render's page box is made 50 pt wider and 50 pt taller than the source's")
def _(t):
    doc = fitz.open(t.render)
    w, h = doc[0].rect.width + 50, doc[0].rect.height + 50
    doc.close()
    p = t.copy("page_size", "render", "pdf")
    set_size(t.render, p, w, h, 0)
    return t.with_side("page_size", "render", p)


@mut("m_ren_landscape", "A", "render", ["55_orientation_mix"],
     "the render's only page is turned landscape; the source's is portrait")
def _(t):
    doc = fitz.open(t.render)
    w, h = doc[0].rect.width, doc[0].rect.height
    doc.close()
    p = t.copy("landscape", "render", "pdf")
    set_size(t.render, p, h, w, 0)
    return t.with_side("landscape", "render", p)


@mut("m_ren_shift_x8", "A", "render", ["47_margins"],
     "the whole page is translated 8 pt right: every run's left edge moves. 8 pt is inside "
     "43's per-span 10 pt window but NOT inside its 3 pt median clause, so 43 fires too - "
     "reported rather than tuned away, because a mutation that only moved the one check it "
     "was aimed at would be a mutation built to flatter the gate")
def _(t):
    p = t.copy("shift_x8", "render", "pdf")
    shift_doc(t.render, p, dx=8.0)
    return t.with_side("shift_x8", "render", p)


@mut("m_ren_shift_y12", "A", "render", ["18_displacement"],
     "the whole page is translated 12 pt down: every run is out of its own "
     "clamp(0.35 x size, 1.5, 4.5) pt budget, on a page where nothing else moved")
def _(t):
    p = t.copy("shift_y12", "render", "pdf")
    shift_doc(t.render, p, dy=12.0)
    return t.with_side("shift_y12", "render", p)


@mut("m_ren_shift_x40", "A", "render",
     ["43_within_10pt_x", "60_text_column_right_edge"],
     "the whole page is translated 40 pt right: no run is within 10 pt of where it was, "
     "and every line now runs past the source's widest")
def _(t):
    p = t.copy("shift_x40", "render", "pdf")
    shift_doc(t.render, p, dx=40.0)
    return t.with_side("shift_x40", "render", p)


@mut("m_ren_vscale", "A", "render", ["23_line_pitch", "34a_span_size_match"],
     "the page's content is compressed vertically to 85 %: the pitch between lines and "
     "the size of every span both fall by 15 %")
def _(t):
    p = t.copy("vscale", "render", "pdf")
    vscale_doc(t.render, p, 0.85)
    return t.with_side("vscale", "render", p)


@mut("m_ren_recolour", "A", "render", ["34b_span_colour_match", "13_text_colours"],
     "twelve lines are erased and drawn back at the same places in a colour the document "
     "does not use. Twelve and not one because 34b's verdict is a RATE with an 85 % floor: "
     "recolouring one span of fifty reads 98 % and PASSES, which is the check's own design "
     "and is reported here rather than worked around")
def _(t):
    doc = fitz.open(t.render)
    lines = [l for l in _lines(doc[0]) if l[0].width > 20][:12]
    pg = doc[0]
    for b, _, _ in lines:
        pg.add_redact_annot(b)
    pg.apply_redactions()
    for b, txt, size in lines:
        pg.insert_text((b.x0, b.y1 - b.height * 0.22), txt, fontsize=size,
                       color=(0.85, 0.10, 0.65), fontname="helv")
    p = t.copy("recolour", "render", "pdf")
    doc.save(p, garbage=3, deflate=True)
    doc.close()
    return t.with_side("recolour", "render", p)


@mut("m_ren_reweight", "A", "render", ["34c_span_weight_match"],
     "twelve lines are erased and drawn back in a bold face at the same place and size; "
     "same 85 % rate floor as 34b, so twelve and not one")
def _(t):
    doc = fitz.open(t.render)
    lines = [l for l in _lines(doc[0]) if l[0].width > 20][:12]
    pg = doc[0]
    for b, _, _ in lines:
        pg.add_redact_annot(b)
    pg.apply_redactions()
    for b, txt, size in lines:
        pg.insert_text((b.x0, b.y1 - b.height * 0.22), txt, fontsize=size,
                       color=(0, 0, 0), fontname="hebo")
    p = t.copy("reweight", "render", "pdf")
    doc.save(p, garbage=3, deflate=True)
    doc.close()
    return t.with_side("reweight", "render", p)


@mut("m_ren_invisible", "A", "render", ["25_invisible_text"],
     "a grey block is filled in blank space and a run of the SAME grey is written on it: "
     "text that matches its own background, which is what 25 counts")
def _(t):
    doc = fitz.open(t.render)
    r = blank_rect(doc[0], 200, 50)
    doc.close()
    p = t.copy("invisible", "render", "pdf")
    add_fills(t.render, p, [(0, r, (0.5, 0.5, 0.5))])
    doc = fitz.open(p)
    doc[0].insert_text((r.x0 + 4, r.y0 + 24), "invisible run", fontsize=11,
                       color=(0.5, 0.5, 0.5), fontname="helv")
    q = t.copy("invisible2", "render", "pdf")
    doc.save(q, garbage=3, deflate=True)
    doc.close()
    os.remove(p)
    return t.with_side("invisible", "render", q)


@mut("m_ren_overlap", "A", "render", ["26_text_overlap"],
     "six strings are written on top of six existing lines: text-on-text the source "
     "does not have (its budget is max(source, 2, runs//50) = 2)")
def _(t):
    doc = fitz.open(t.render)
    lines = [l for l in _lines(doc[0]) if l[0].width > 30][:6]
    doc.close()
    p = t.copy("overlap", "render", "pdf")
    add_text(t.render, p, [(0, b.x0 + 2, b.y1 - b.height * 0.22, "overlap", 10,
                            (0, 0, 0), "helv", 0) for b, _, _ in lines])
    return t.with_side("overlap", "render", p)


@mut("m_ren_offpage", "A", "render", ["27_text_off_page", "28_clipped_at_edge"],
     "six strings are written so that they run past the right edge of the page")
def _(t):
    doc = fitz.open(t.render)
    W = doc[0].rect.width
    r = blank_rect(doc[0], 200, 90)
    doc.close()
    p = t.copy("offpage", "render", "pdf")
    add_text(t.render, p, [(0, W - 40, r.y0 + 14 * (i + 1), "runs off the edge", 11,
                            (0, 0, 0), "helv", 0) for i in range(6)])
    return t.with_side("offpage", "render", p)


@mut("m_ren_blank_fill", "A", "render", ["61_blank_not_filled"],
     "a 200 x 90 pt block is filled in a place the SOURCE shows as blank: ink the render "
     "invented, which is the whole question of 61")
def _(t):
    doc = fitz.open(t.src)
    r = blank_rect(doc[0], 200, 90)
    doc.close()
    p = t.copy("blank_fill", "render", "pdf")
    add_fills(t.render, p, [(0, r, (0.10, 0.30, 0.60))])
    return t.with_side("blank_fill", "render", p)


@mut("m_ren_xrule", "A", "render", ["46_text_crossing_rule"],
     "a rule is drawn straight through the middle of an existing line of text")
def _(t):
    doc = fitz.open(t.render)
    b, _, _ = [l for l in _lines(doc[0]) if l[0].width > 60][0]
    doc.close()
    p = t.copy("xrule", "render", "pdf")
    add_rules(t.render, p, [(0, (b.x0, (b.y0 + b.y1) / 2), (b.x1, (b.y0 + b.y1) / 2), 0.8)])
    return t.with_side("xrule", "render", p)


@mut("m_ren_band_erase", "A", "render", ["44_header_footer"],
     "the topmost line of the page - a line in the top band - is redacted out of the "
     "render, so a band element the source has is dropped")
def _(t):
    doc = fitz.open(t.render)
    H = doc[0].rect.height
    band = [l for l in _lines(doc[0]) if l[0].y1 < H * 0.10]
    if not band:
        band = sorted(_lines(doc[0]), key=lambda l: l[0].y0)[:1]
    b = band[0][0]
    doc.close()
    p = t.copy("band_erase", "render", "pdf")
    redact(t.render, p, [(0, b)])
    return t.with_side("band_erase", "render", p)


@mut("m_ren_justify", "A", "render", ["42_justification_edges"],
     "every line the source render calls LEFT-aligned is moved right until its right edge "
     "is the page's widest, so the render calls it RIGHT-aligned: one contradiction per "
     "line, against the check's floor of three. Moving lines to an arbitrary x does not "
     "work - a line at neither edge is class '-' on both sides and is not compared")
def _(t):
    doc = fitz.open(t.render)
    lines = _lines(doc[0])
    doc.close()
    xmin = min(b.x0 for b, _, _ in lines)
    xmax = max(b.x1 for b, _, _ in lines)
    seen, moves = set(), []
    for b, txt, _ in lines:
        if txt in seen or b.x0 - xmin > 1.0:
            continue
        seen.add(txt)
        moves.append((b, xmax - b.x1, 0.0))
    p = t.copy("justify", "render", "pdf")
    move_lines(t.render, p, 0, moves)
    return t.with_side("justify", "render", p)


# ---- docx-side: what the engine wrote -------------------------------------
@mut("m_docx_table_col_drop", "T", "docx", ["62_table_columns"],
     "one <w:gridCol> is deleted: the .docx declares one column fewer than the page grid")
def _(t):
    p = t.copy("col_drop", "docx", "docx")
    docx_edit(t.docx, p, lambda x: _drop_first(r"<w:gridCol[^>]*/>", x))
    return t.with_side("col_drop", "docx", p)


@mut("m_docx_table_row_drop", "T", "docx", ["63_table_rows"],
     "one <w:tr> is deleted: the .docx declares one row fewer than the page grid")
def _(t):
    p = t.copy("row_drop", "docx", "docx")
    docx_edit(t.docx, p, lambda x: _drop_first(r"<w:tr>.*?</w:tr>", x))
    return t.with_side("row_drop", "docx", p)


@mut("m_docx_table_span_weld", "T", "docx", ["64_table_span_across"],
     "a gridSpan of 2 is written onto the first cell of the first row that does not "
     "already carry one: the .docx claims a merge the page grid does not draw")
def _(t):
    def f(x):
        m = re.search(r"<w:tr>.*?</w:tr>", x, re.S)
        if not m:
            raise RuntimeError("no row")
        row = m.group(0)
        for c in re.finditer(r"<w:tc>.*?</w:tc>", row, re.S):
            if "<w:gridSpan" in c.group(0):
                continue
            cell = c.group(0)
            i = cell.find("</w:tcPr>")
            if i < 0:
                continue
            cell2 = cell[:i] + '<w:gridSpan w:val="2"/>' + cell[i:]
            row2 = row[:c.start()] + cell2 + row[c.end():]
            return x[:m.start()] + row2 + x[m.end():]
        raise RuntimeError("every cell in row 1 already carries a gridSpan")
    p = t.copy("span_weld", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("span_weld", "docx", p)


@mut("m_docx_table_vmerge", "T", "docx", ["65_table_span_down"],
     "a false w:vMerge restart/continue pair is written into one column: the .docx "
     "claims a vertical merge the page grid does not draw")
def _(t):
    def f(x):
        rows = re.findall(r"<w:tr>.*?</w:tr>", x, re.S)
        if len(rows) < 2:
            raise RuntimeError("need two rows")
        out = x
        for n, tag in ((0, '<w:vMerge w:val="restart"/>'), (1, "<w:vMerge/>")):
            r = rows[n]
            m = re.search(r"<w:tc>(?!.*?<w:vMerge)", r, re.S)
            cell = r[m.start():]
            i = cell.find("</w:tcPr>")
            if i < 0:
                raise RuntimeError("no tcPr")
            r2 = r[:m.start()] + cell[:i] + tag + cell[i:]
            out = out.replace(r, r2, 1)
        return out
    p = t.copy("vmerge", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("vmerge", "docx", p)


@mut("m_docx_table_width", "T", "docx", ["66_table_cell_width"],
     "one <w:gridCol> is made 200 twips (10 pt) wider: the .docx's cell width no longer "
     "matches the page's column")
def _(t):
    def f(x):
        m = re.search(r'<w:gridCol w:w="(\d+)"/>', x)
        if not m:
            raise RuntimeError("no gridCol")
        w = int(m.group(1))
        return x[:m.start()] + '<w:gridCol w:w="%d"/>' % (w + 200) + x[m.end():]
    p = t.copy("width", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("width", "docx", p)


@mut("m_docx_face_rename", "A", "docx", ["53_embedded_faces"],
     "every w:rFonts face in the .docx is renamed to Georgia: the family the page draws "
     "with is carried by nothing")
def _(t):
    def f(x):
        return re.sub(r'(w:ascii|w:hAnsi|w:cs)="[^"]*"',
                      lambda m: '%s="Georgia"' % m.group(1), x)
    p = t.copy("face_rename", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("face_rename", "docx", p)


@mut("m_docx_image_shrink", "A", "docx", ["54_image_dpi"],
     "the picture's wp:extent is multiplied by 2.5: the same pixels are laid out over "
     "2.5x the width, so the engine's resolution decision is 2.5x worse")
def _(t):
    def f(x):
        n = [0]

        def one(m):
            n[0] += 1
            a = int(int(m.group(1)) * 2.5)
            b = int(int(m.group(2)) * 2.5)
            return '<wp:extent cx="%d" cy="%d"/>' % (a, b)
        y = re.sub(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', one, x)
        if not n[0]:
            raise RuntimeError("no wp:extent")
        return y
    p = t.copy("image_shrink", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("image_shrink", "docx", p)


@mut("m_docx_rot_strip", "R", "docx", ["35_rotation"],
     "the rot= on every <a:xfrm> in the .docx is removed: the page draws one rotated run "
     "and the .docx no longer places it at any angle")
def _(t):
    def f(x):
        y = re.sub(r'<a:xfrm rot="[^"]*"', "<a:xfrm", x)
        if y == x:
            raise RuntimeError("no a:xfrm rot= to strip")
        return y
    p = t.copy("rot_strip", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("rot_strip", "docx", p)


@mut("m_docx_ann_drop", "N", "docx", ["50_annotation_text"],
     "the annotation's own text is removed from the .docx: three strings the source "
     "carries reach the reader nowhere")
def _(t):
    def f(x):
        y = x
        for s in ("Rate for HSN 8536 confirmed with PO.",
                  "Checked against PO 4471.",
                  "Approved"):
            y = y.replace(s, "")
        if y == x:
            raise RuntimeError("none of the annotation strings were in the .docx")
        return y
    p = t.copy("ann_drop", "docx", "docx")
    docx_edit(t.docx, p, f)
    return t.with_side("ann_drop", "docx", p)


# ---- the one mutation whose control is itself a modification --------------
def _field_control(t):
    """601 carries 11 widgets, 3 of them answered, and the .docx carries none of the
    answers - so 51 fails it as it stands. Its answers cannot be emptied through the
    widget API (the ComboBox keeps a choice), so the control removes the widgets
    entirely: 51 reads that as `state=none`, which is a genuine pass, not a silence.
    The mutation then writes one answer back into a fresh box."""
    q = os.path.join(t.tmp, "field_control.pdf")
    d = fitz.open(t.src)
    for pg in d:
        for w in list(pg.widgets() or []):
            pg.delete_widget(w)
    d.save(q, garbage=3, deflate=True)
    d.close()
    return t.with_side("field_control", "source", q)


@mut("m_src_field_value", "F", "source", ["51_field_values"],
     "an answered form box is added to the source; the .docx carries no such answer, so "
     "the value is not inside its rectangle in the .docx", control=_field_control)
def _(t):
    q = os.path.join(t.tmp, "field_value.pdf")
    d = fitz.open(_field_control(t).src)
    w = fitz.Widget()
    w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    w.field_name = "falsify_box"
    w.rect = fitz.Rect(60, 600, 260, 620)
    w.field_value = "ANSWER-NOT-IN-THE-DOCX"
    w.text_fontsize = 10
    d[0].add_widget(w)
    d.save(q, garbage=3, deflate=True)
    d.close()
    return t.with_side("field_value", "source", q)


# ---------------------------------------------------------------------------
# the gate
# ---------------------------------------------------------------------------
def run_one(src, render, docx):
    V.all_check_ids()
    res = V.compare(src, render, docx)
    return {k: bool(v["ok"]) for k, v in res["checks"].items()}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--render", required=True)
    ap.add_argument("--docx", required=True)
    ap.add_argument("--out", default="falsify.json")
    ap.add_argument("--md", default=None)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    universe = V.all_check_ids()
    tmp = tempfile.mkdtemp(prefix="falsify-")
    rows = []
    controls = {}

    def triple_for(stem):
        s = os.path.join(a.corpus, stem + ".pdf")
        r = os.path.join(a.render, stem + ".pdf")
        d = os.path.join(a.docx, stem + ".docx")
        for p in (s, r, d):
            if not os.path.exists(p):
                raise SystemExit("missing %s" % p)
        return Triple(s, r, d, tmp)

    for m in MUTATIONS:
        stem = BASES[m.base]
        base = triple_for(stem)
        if stem not in controls:
            ctl = m.control(base) if m.control else base
            controls[stem] = (ctl, run_one(ctl.src, ctl.render, ctl.docx))
            if a.verbose:
                print("control %-34s %s" % (stem, "clean" if not controls[stem][1]
                                            or all(controls[stem][1].values()) else "has failures"))
        ctl_triple, ctl_verdicts = controls[stem]
        try:
            mt = m.apply(base)
            verd = run_one(mt.src, mt.render, mt.docx)
        except Exception as e:                                  # noqa: BLE001
            rows.append({"mutation": m.id, "base": stem, "side": m.side,
                         "note": m.note, "targets": m.targets,
                         "error": "%s: %s" % (type(e).__name__, e),
                         "fired": [], "control_clean": []})
            print("  %-26s ERROR %s" % (m.id, e), file=sys.stderr)
            continue
        fired = sorted(k for k, ok in verd.items() if not ok)
        control_clean = sorted(k for k, ok in ctl_verdicts.items() if ok)
        rows.append({"mutation": m.id, "base": stem, "side": m.side, "note": m.note,
                     "targets": m.targets, "fired": fired,
                     "control_clean": control_clean,
                     "targets_fired": sorted(set(fired) & set(m.targets)),
                     "targets_missed": sorted(set(m.targets) - set(fired))})
        print("%-26s %-10s fires %d: %s" % (m.id, m.side, len(fired),
                                            ", ".join(sorted(set(fired) & set(m.targets)))
                                            or "(none of its targets)"))
        if a.verbose and set(m.targets) - set(fired):
            print("     MISSED: %s" % ", ".join(sorted(set(m.targets) - set(fired))))

    # ---- the per-check verdict -------------------------------------------
    table = {}
    for cid in universe:
        hit = [r for r in rows
               if not r.get("error") and cid in r["fired"] and cid in r["control_clean"]]
        dirty = [r for r in rows
                 if not r.get("error") and cid in r["fired"] and cid not in r["control_clean"]]
        # THE INTENDED MUTATION IS THE EVIDENCE, NOT THE FIRST KNOCK-ON. Removing a line
        # of text fires 04, 17, 18, 31, 45 and 59 at once, and crediting 04 to whichever
        # mutation happens to be listed first would report a coincidence as a design.
        # A mutation that NAMES the check is preferred; a knock-on is the fallback.
        aimed = [r for r in hit if cid in r["targets"]]
        table[cid] = {
            "status": "fired" if hit else "could-not-fire",
            "fired_by": [r["mutation"] for r in (aimed or hit)],
            "fired_by_count": len(hit),
            "knock_on_only": not aimed,
            "fired_on_dirty_control": [r["mutation"] for r in dirty],
        }

    fired = sum(1 for v in table.values() if v["status"] == "fired")
    broken = sorted(c for c, v in table.items() if v["status"] != "fired")

    # ---- the per-document and per-check `applicable` census ----------------
    # The gate does not need the corpus for this; the scoreboard run does. What is
    # published here is the instrument's own statement about what it did not ask, on
    # the document the mutation was applied to, so the reader can see the difference
    # between "passed" and "was never asked" on a real row.
    census = {}
    for stem, (ctl_triple, _v) in controls.items():
        res = V.compare(ctl_triple.src, ctl_triple.render, ctl_triple.docx)
        census[stem] = {k: res.get(k) for k in
                        ("universe", "applicable", "passed", "passed_applicable",
                         "abstained", "abstain_reason")}
        census[stem]["vacuous"] = sorted(
            k for k, c in res["checks"].items() if c.get("vacuous") is True)
        census[stem]["not_auditable"] = sorted(
            k for k, c in res["checks"].items() if c.get("vacuous") is None)

    out = {
        "instrument": "verify_google.py",
        "universe_n": len(universe),
        "universe": universe,
        "mutations": rows,
        "checks": table,
        "controls": census,
        "fired": fired,
        "could_not_fire": broken,
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)

    # ---- report -----------------------------------------------------------
    lines = []
    lines.append("| check | status | fired by (the mutation aimed at it) | side | also fired by |")
    lines.append("|---|---|---|---|---|")
    side_of = {r["mutation"]: r["side"] for r in rows if not r.get("error")}
    for cid in universe:
        v = table[cid]
        if v["status"] == "fired":
            mid = v["fired_by"][0]
            also = [m for m in table[cid]["fired_by"][1:]]
            lines.append("| `%s` | **fired** | `%s` | %s | %d |"
                         % (cid, mid, side_of[mid], v["fired_by_count"] - 1))
        else:
            why = ("no generated mutation made it fail"
                   + (" (it does fire on %d mutation(s) whose control was already failing: %s)"
                      % (len(v["fired_on_dirty_control"]),
                         ", ".join("`%s`" % x for x in v["fired_on_dirty_control"]))
                      if v["fired_on_dirty_control"] else ""))
            lines.append("| `%s` | **COULD NOT FIRE** | %s | |" % (cid, why))
    text = "\n".join(lines)
    if a.md:
        with open(a.md, "w") as f:
            f.write("# Falsifiability gate\n\n" + text + "\n")

    print()
    print("%d of %d checks fired on a generated mutation of a real corpus document"
          % (fired, len(universe)))
    if broken:
        print("COULD NOT FIRE (%d): %s" % (len(broken), ", ".join(broken)))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
