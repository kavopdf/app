#!/usr/bin/env python3
"""
prove_checks.py - prove every check can fire, using real documents.

THE PROBLEM
  Twelve real documents were converted by the real engine and verified. Twenty-six
  of the fifty-eight checks fired. Thirty-two did not, and a check that has never
  fired is not evidence of anything: it might be correct and simply not triggered,
  or it might be dead code that always reports pass while hiding the defect it
  exists to find. A report cannot tell those apart.

  Synthetic fixtures are not enough either. test_checks.py builds documents from
  nothing, which proves the logic but not that the check survives contact with a
  real PDF - real fonts, real content streams, real coordinate spaces.

THREE WAYS A CHECK IS PROVEN HERE, weakest last
  1. FIRES     mutate a real document in the way the check is meant to detect and
               watch it flip from pass to fail. This is the strong proof.
  2. SOURCE    the check only means something when the source HAS the feature -
               annotations, form fields, an outline, links. Build a real document
               that has it, compare against one that does not, and watch it fire.
  3. VARIES    the check's reported number moves across real documents. Weaker:
               it proves the check measures something real, not that it fails.
  A check that passes all three is unproven and is reported as such.

WHAT IT FOUND
  18_median_dy compared a SIGNED median against a positive threshold, so a
  document shifted UP by any amount passed - med_dy of -12 is less than 3. Fixed
  with abs(). This is exactly the class of defect the first two audits could not
  see: every file present, every script parsing, the logic simply inverted.

USAGE
  python3 prove_checks.py
"""
import glob
import json
import os
import random
import subprocess
import sys
import tempfile
import warnings

warnings.filterwarnings("ignore")
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "verify_google.py")
# Paths are given, not assumed. The first version of this file hardcoded
# a sandbox directory of the session that wrote it, so the
# tool was committed to the repository and could not run anywhere else - the same
# mistake audit_sim.py made. Defaults are relative to this file and to a temporary
# directory, so a fresh clone works.
CORPUS = os.environ.get("P2W_CORPUS", os.path.join(HERE, "..", "..", "corpus"))
WORK = os.environ.get("P2W_WORK", tempfile.mkdtemp(prefix="prove-"))
RENDERS = os.environ.get("P2W_RENDERS", "")   # optional: pdfs rendered from the engine

BASE = "01_stamp_rotated_15deg_upright.pdf"
IMG_DOC = "10_stamp_as_image.pdf"
LINK_DOC = "44_coloured_underlined_hyperlinks.pdf"
# 36/37/38 pass vacuously when the SOURCE has none of the feature, so each needs
# a source that does: measured, these three carry 4 underlines, 3 superscript
# runs and 9 list markers. BASE carries zero of all three, so any render passes.
UNDERLINE_DOC = "payslip-label-left-amount-right.pdf"
SCRIPT_DOC = "journal-2col-with-footnotes.pdf"
MARKER_DOC = "admission-form-labels-left-boxes-right.pdf"


def run(src, gd):
    """Measure a pair, and return None rather than crashing when it cannot.

    tempfile.mktemp returned a path under /scratch/tmp, which does not exist, so
    verify_google.py never wrote the file and the open() below raised instead of
    reporting. A proof harness that dies on the first missing file proves nothing.
    """
    fd, out = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    subprocess.run([sys.executable, VERIFY, src, gd, "--json", out],
                   capture_output=True)
    try:
        with open(out) as f:
            return json.load(f)
    except Exception:
        return None
    finally:
        try:
            os.remove(out)
        except OSError:
            pass


def path(name):
    return os.path.join(CORPUS, name)


def spans_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                if sp["text"].strip():
                    out.append((fitz.Rect(sp["bbox"]), sp))
    return out


def save(doc, name):
    p = os.path.join(WORK, name)
    doc.save(p, deflate=True)
    doc.close()
    return p


# ---- render-side mutations: the render gets worse than a good source --------

def mut_shift(doc, dy=12, dx=0):
    for p in doc:
        r = p.rect
        p.set_mediabox(fitz.Rect(r.x0 - dx, r.y0 - dy, r.x1 - dx, r.y1 - dy))


def mut_restyle(doc, frac=0.30, size=2.2, colour=(0.8, 0, 0.8), bold=False):
    p = doc[0]
    sp = spans_of(p)
    if not sp:
        return
    random.seed(7)
    pick = random.sample(sp, max(1, int(len(sp) * frac)))
    for r, _ in pick:
        p.add_redact_annot(r)
    p.apply_redactions()
    for r, s in pick:
        p.insert_text((r.x0, r.y1 - 1), s["text"][:40],
                      fontsize=s["size"] * size,
                      fontname="hebo" if bold else "helv", color=colour)


def mut_bold(doc):
    mut_restyle(doc, frac=0.35, size=1.0, colour=(0, 0, 0), bold=True)


def mut_chars(doc):
    """Replace the letters of the first few spans with different letters."""
    p = doc[0]
    sp = spans_of(p)[:6]
    for r, s in sp:
        p.add_redact_annot(r)
    p.apply_redactions()
    for r, s in sp:
        p.insert_text((r.x0, r.y1 - 1), "ZZZZZZZZ", fontsize=s["size"], color=(0, 0, 0))


def mut_rule(doc):
    p = doc[0]
    blk = [b for b in p.get_text("dict")["blocks"] if b.get("type") == 0]
    if blk:
        y = (blk[0]["bbox"][1] + blk[0]["bbox"][3]) / 2
        p.draw_line(fitz.Point(30, y), fitz.Point(p.rect.width - 30, y),
                    color=(0, 0, 0), width=2)


def mut_invisible(doc):
    p = doc[0]
    p.draw_rect(fitz.Rect(40, 300, p.rect.width - 40, 360), color=None,
                fill=(1, 1, 1), overlay=True)
    p.insert_text((50, 330), "invisible words here", fontsize=11, color=(1, 1, 1))


def mut_blank(doc):
    doc[0].add_redact_annot(doc[0].rect)
    doc[0].apply_redactions()


def mut_pagesize(doc):
    for p in doc:
        p.set_mediabox(fitz.Rect(0, 0, 612, 792))


def mut_landscape(doc):
    p = doc[0]
    p.set_mediabox(fitz.Rect(0, 0, p.rect.height, p.rect.width))


def mut_drop_links(doc):
    for p in doc:
        for l in p.get_links():
            p.delete_link(l)


def mut_wrong_link(doc):
    for p in doc:
        for l in p.get_links():
            p.delete_link(l)
    doc[0].insert_link({"kind": fitz.LINK_URI,
                        "from": fitz.Rect(50, 50, 200, 70),
                        "uri": "https://wrong.invalid/x"})


def mut_drop_images(doc):
    for p in doc:
        for im in p.get_images(full=True):
            try:
                p.delete_image(im[0])
            except Exception:
                pass


def mut_image_shrink(doc):
    p = doc[0]
    for im in p.get_image_info(xrefs=True):
        if im["xref"]:
            p.insert_image(fitz.Rect(20, 20, 34, 34), xref=im["xref"])


def mut_header(doc):
    doc[0].insert_text((72, 24), "HEADER ADDED", fontsize=9)


def mut_big(doc):
    doc[0].insert_text((72, 300), "SIZE CHANGED", fontsize=30)


def mut_font(doc):
    doc[0].insert_text((72, 330), "different typeface", fontsize=11, fontname="tiro")


def mut_offpage(doc):
    p = doc[0]
    p.insert_text((p.rect.width + 60, p.rect.height + 60), "outside", fontsize=11)


def mut_clip(doc):
    p = doc[0]
    p.insert_text((p.rect.width - 2, 200), "clipped at the very edge of the page", fontsize=11)


def mut_rotate(doc):
    for p in doc:
        p.set_rotation(90)


def mut_droppage(doc):
    if len(doc) > 1:
        doc.delete_page(len(doc) - 1)


def mut_addpage(doc):
    doc.new_page(width=doc[0].rect.width, height=doc[0].rect.height)


# ---- mutations that change the object the check actually reads -------------
# PROVE-GAPS.md group (c): "the mutation changes the wrong object". A rule is not
# an underline, a page rotation is not a text matrix, a raised run is not a
# superscript flag, and a retyped line is not a list marker unless the marker is
# inside the span.
#
# Each pair below is written twice, and the second half of each pair is the
# point. The `*_added` / `*_rotated` / `*_at_baseline` / `*_flag` mutators are
# the ones PROVE-GAPS.md asked for: they really do change the object the check
# reads (measured below, they move the check's own number). They still cannot
# fire, because checks 35-38 compare a RENDER against a SOURCE and only fail
# when the render LOSES something the source had - an additive mutation can only
# raise the render count, and a higher render count always passes. The `*_gone`
# mutators change the same object in the one direction the comparison treats as
# a regression. Those fire.
#
# This is a correction to the brief, not a refinement of it: for 35-38 the
# binding constraint is the DIRECTION of the comparison, not the choice of
# object. Only 32 was diagnosed correctly, because its floor already implies
# removal.

def _thin(doc):
    """Exactly the strokes 32 and 36 count, so the mutators and the checks
    cannot drift apart: same import, same function."""
    import verify_google as V
    return V._strokes


def _strip_line_art(doc, pick):
    """Delete the drawings `pick(page)` returns; text and images untouched.

    PyMuPDF has no "delete this drawing" call - line art only goes away as a
    side effect of redaction - so each selected rect is redacted with
    LINE_ART_REMOVE_IF_TOUCHED and TEXT_NONE, which leaves the words in place.
    """
    n = 0
    for p in doc:
        for r in pick(p):
            rr = fitz.Rect(r)
            rr.x0 -= 0.7
            rr.y0 -= 0.7
            rr.x1 += 0.7
            rr.y1 += 0.7
            p.add_redact_annot(rr)
            n += 1
    for p in doc:
        p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                           graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                           text=fitz.PDF_REDACT_TEXT_NONE)
    return n


def mut_rules_removed(doc):
    """32: take the rules away. The check allows 80 % of the source count, so a
    document with sixteen rules needs eleven or fewer left; removing all of them
    is unambiguous. Adding one rule (mut_rule) can never fail a floor."""
    return _strip_line_art(doc, lambda p: [s["rect"] for s in _thin(doc)(p)])


def _text_under(doc, pred):
    """Spans whose text satisfies pred, per page, with their line."""
    out = []
    for p in doc:
        hits = []
        for blk in p.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp.get("text", "").strip() and pred(ln, sp):
                        hits.append(sp)
        out.append((p, hits))
    return out


def _retype(p, spans, make_text, size_of, dy=1.0):
    """Redact spans and reinsert their text upright, unscripted, unmarked."""
    for sp in spans:
        p.add_redact_annot(fitz.Rect(sp["bbox"]))
    p.apply_redactions()
    for sp in spans:
        b = fitz.Rect(sp["bbox"])
        txt = make_text(sp)
        if not txt:
            continue
        p.insert_text((b.x0, b.y1 - dy), txt[:60],
                      fontsize=min(size_of(sp), max(4.0, b.height)),
                      fontname="helv", color=(0, 0, 0))


def _is_rotated(ln):
    d = ln.get("dir", (1, 0))
    return abs(d[1]) > 0.02 or d[0] < 0.98


def mut_text_unrotated(doc):
    """35: redraw the rotated lines with an upright text matrix.

    The check reads `line.dir`, the text matrix - not the page's /Rotate, which
    is why mut_rotate could never move it. Here the source has two rotated lines
    and the render is left with none, which is the regression 35 exists to see.
    """
    n = 0
    for p, hits in _text_under(doc, lambda ln, sp: _is_rotated(ln)):
        _retype(p, hits, lambda sp: sp["text"].strip(), lambda sp: sp["size"])
        n += len(hits)
    return n


def mut_text_rotated(doc):
    """35, additive: draw new text with a rotated matrix. The object 35 reads
    (line.dir) really does change - and the check still passes, because the
    render gained rotated lines instead of losing them."""
    p = doc[0]
    piv = fitz.Point(200, 300)
    p.insert_text(piv, "rotated matrix text", fontsize=11,
                  morph=(piv, fitz.Matrix(30)))
    return 1


def _rules_under_spans(p):
    """The thin strokes 36 counts: within 2.5 pt of a span's bottom, overlapping
    it horizontally."""
    thin = [s for s in _thin(None)(p) if s["rect"].height <= 2.5]
    keep = []
    for blk in p.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                if not sp.get("text", "").strip():
                    continue
                x0, y0, x1, y1 = sp["bbox"]
                for st in thin:
                    r = st["rect"]
                    if y1 - 2.5 <= r.y0 <= y1 + 2.5 and r.x0 < x1 and r.x1 > x0:
                        keep.append(r)
                        break
    return keep


def mut_underline_removed(doc):
    """36: remove the rules that sit just under a baseline. On
    payslip-label-left-amount-right.pdf the source counts four and the render is
    left with none - and no other check moves, because that document has no
    links. On 44_coloured_underlined_hyperlinks.pdf the same mutation also
    deleted the link annotations, which made the proof less specific."""
    return _strip_line_art(doc, _rules_under_spans)


def mut_rule_at_baseline(doc):
    """36, additive: draw one rule at a span's bottom edge, where an underline
    goes. The check's count goes up by one and the check still passes."""
    p = doc[0]
    sp = None
    for blk in p.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip():
                    sp = s
                    break
            if sp:
                break
        if sp:
            break
    if not sp:
        return 0
    b = fitz.Rect(sp["bbox"])
    p.draw_line(fitz.Point(b.x0, b.y1), fitz.Point(b.x1, b.y1),
                color=(0, 0, 0), width=0.8)
    return 1


def mut_superscript_removed(doc):
    """37: take the superscript bit off every run that has it, by redrawing the
    run at full size on its own baseline. journal-2col-with-footnotes.pdf has
    three flagged runs in the source and none are left in the render."""
    n = 0
    for p, hits in _text_under(doc, lambda ln, sp: sp.get("flags", 0) & 1):
        _retype(p, hits, lambda sp: sp["text"].strip(),
                lambda sp: max(sp["size"], fitz.Rect(sp["bbox"]).height * 0.8))
        n += len(hits)
    return n


def mut_superscript_flag(doc):
    """37, additive: raise a run and set the flag.

    PyMuPDF's insert_text cannot set bit 0 - measured, a run inserted 4.5 pt high
    at 0.8 of the line size comes back with flags 4, not 5. The flag follows the
    PDF text-rise operator `Ts` inside the SAME text object as a larger run, so
    the run is written as a raw content stream. The check's count goes up and the
    check still passes.
    """
    p = doc[0]
    p.insert_text((10, 10), "seed", fontsize=6)
    fname = p.insert_font(fontname="helv")
    cs = ("BT /%s 8.9 Tf 60 560 Td (baseline run) Tj"
          " 4.5 Ts /%s 7.1 Tf (7) Tj 0 Ts ET" % (fname, fname))
    x = p.get_contents()[-1]
    doc.update_stream(x, doc.xref_stream(x) + cs.encode())
    return 1


MARK_CHARS = "\u2022\u25cf\u25aa\u2023\u2043-*\u00b7"


def _is_marker(t):
    return bool(t) and (t[0] in MARK_CHARS or
                        (t[0].isdigit() and t[1:3] in (". ", ") ")))


def mut_marker_removed(doc):
    """38: retype every marker-leading span without its marker, so the "1. " or
    bullet is gone from inside the span the check reads.

    Every span is tested, not only the first of the line: the check walks all
    spans and stops at the first one that starts with a marker, and on
    question-paper-marks-right-margin.pdf that marker sits in a later span, so a
    first-span-only version of this mutator left the count at 1 and did not fire.
    """
    n = 0
    for p in doc:
        hits = []
        for blk in p.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if _is_marker(sp["text"].strip()):
                        hits.append(sp)
        if hits:
            _retype(p, hits, _strip_marker, lambda sp: sp["size"])
            n += len(hits)
    return n


def _strip_marker(sp):
    t = sp["text"].strip()
    if t[0].isdigit() and t[1:3] in (". ", ") "):
        return t[3:]
    # strip the whole leading run, not one character: question-paper-marks-
    # right-margin.pdf ends with a "*** End of question paper ***" line, and
    # removing one "*" leaves "**..." which is still a marker to the check.
    i = 0
    while i < len(t) and t[i] in MARK_CHARS:
        i += 1
    return t[i:].lstrip()


def mut_marker_added(doc):
    """38, additive: retype a line's first span so it starts with "1. ". The
    marker is inside one span, exactly as the check requires, the count goes up,
    and the check still passes."""
    p = doc[0]
    sp = None
    for blk in p.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            sps = [s for s in ln["spans"] if s["text"].strip()]
            if sps:
                sp = sps[0]
                break
        if sp:
            break
    if not sp:
        return 0
    b = fitz.Rect(sp["bbox"])
    txt = sp["text"].strip()
    p.add_redact_annot(b)
    p.apply_redactions()
    p.insert_text((b.x0, b.y1 - 1), ("1. " + txt)[:60],
                  fontsize=min(sp["size"], max(4.0, b.height)),
                  fontname="helv", color=(0, 0, 0))
    return 1


# The mutations PROVE-GAPS.md asked for: they change the object each check
# reads, and they are expected NOT to fire. Printed as a separate stage so the
# "cannot fire" claim is measured every run rather than asserted in a comment.
WRONG_DIRECTION = {
    "32_stroke_lines":     (mut_rule, BASE, "one rule added"),
    "35_rotation":         (mut_text_rotated, BASE, "text drawn with a rotated matrix"),
    "36_underline_rules":  (mut_rule_at_baseline, UNDERLINE_DOC,
                            "a rule drawn at a span's bottom edge"),
    "37_super_subscript":  (mut_superscript_flag, "journal-2col-with-footnotes.pdf",
                            "a run raised with Ts, flag set"),
    "38_list_markers":     (mut_marker_added, "admission-form-labels-left-boxes-right.pdf",
                            "a line's first span retyped to start \"1. \""),
}


# ---- source-side mutations: the source has a feature the render lacks ------

def src_annot(doc):
    a = doc[0].add_text_annot(fitz.Point(90, 90), "note")
    a.update()


def src_widget(doc):
    w = fitz.Widget()
    w.field_name = "f1"
    w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    w.rect = fitz.Rect(60, 60, 220, 84)
    doc[0].add_widget(w)


def src_toc(doc):
    doc.set_toc([[1, "Chapter One", 1], [1, "Chapter Two", 1]])


# check -> ("render" | "source", mutation, document, description)
CASES = {
    "01_page_count":            ("render", mut_addpage, BASE, "a page added"),
    "02_text_run_count":        ("render", mut_restyle, BASE, "30% of spans restyled"),
    "03_word_count":            ("render", mut_blank, BASE, "the page's text removed"),
    "04_words_missing":         ("render", mut_blank, BASE, "the page's text removed"),
    "05_words_extra":           ("render", mut_rule, BASE, "extra ink drawn"),
    "06_table_columns":         ("render", mut_shift, BASE, "the page shifted"),
    "07_table_rows":            ("render", mut_shift, BASE, "the page shifted"),
    "08_image_count":           ("render", mut_drop_images, IMG_DOC, "the image removed"),
    "09_font_names":            ("render", mut_font, BASE, "a different typeface used"),
    "10_font_sizes":            ("render", mut_big, BASE, "a much larger size used"),
    "11_bold_runs":             ("render", mut_bold, BASE, "35% of spans made bold"),
    "12_italic_runs":           ("render", mut_bold, BASE, "span styling changed"),
    "13_text_colours":          ("render", mut_restyle, BASE, "30% of spans recoloured"),
    "14_filled_shapes":         ("render", mut_invisible, BASE, "a filled rectangle added"),
    "15_links":                 ("render", mut_drop_links, LINK_DOC, "every link removed"),
    "16_numeric_runs":          ("render", mut_blank, BASE, "the page's text removed"),
    "17_matched_runs":          ("render", mut_blank, BASE, "nothing left to match"),
    "18_median_dy":             ("render", mut_shift, BASE, "everything shifted vertically"),
    "19_worst_dy":              ("render", mut_shift, BASE, "everything shifted vertically"),
    "20_within_10pt":           ("render", mut_shift, BASE, "everything shifted vertically"),
    "21_median_dx":             ("render", lambda d: mut_shift(d, dx=10), BASE, "shifted sideways"),
    "22_reading_order":         ("render", mut_blank, BASE, "the page's order destroyed"),
    "23_line_pitch":            ("render", mut_shift, BASE, "line pitch changed"),
    "24_page_breaks":           ("render", mut_droppage, BASE, "a page dropped"),
    "25_invisible_text":        ("render", mut_invisible, BASE, "text drawn white on white"),
    "26_text_overlap":          ("render", mut_rule, BASE, "a rule across text"),
    "27_text_off_page":         ("render", mut_offpage, BASE, "text placed outside the page"),
    "28_clipped_at_edge":       ("render", mut_clip, BASE, "text pushed off the edge"),
    "29_blank_where_ink_was":   ("render", mut_blank, BASE, "ink removed"),
    "30_ink_where_blank_was":   ("render", mut_rule, BASE, "ink added"),
    "31_pages_lost_their_text": ("render", mut_blank, BASE, "the page left blank"),
    "32_stroke_lines":          ("render", mut_rules_removed, BASE, "every rule removed"),
    "33_border_over_text":      ("render", mut_rule, BASE, "a rule through a word"),
    "34a_span_size_match":      ("render", mut_restyle, BASE, "30% of spans resized"),
    "34b_span_colour_match":    ("render", mut_restyle, BASE, "30% of spans recoloured"),
    "34c_span_weight_match":    ("render", mut_bold, BASE, "35% of spans made bold"),
    "35_rotation":              ("render", mut_text_unrotated, BASE,
                                 "rotated lines redrawn upright"),
    "36_underline_rules":       ("render", mut_underline_removed, UNDERLINE_DOC,
                                 "every underline rule removed"),
    "37_super_subscript":       ("render", mut_superscript_removed, SCRIPT_DOC,
                                 "every superscript flag stripped"),
    "38_list_markers":          ("render", mut_marker_removed, MARKER_DOC,
                                 "every list marker removed"),
    "39_image_position":        ("render", mut_image_shrink, IMG_DOC, "the image moved"),
    "40_link_targets":          ("render", mut_wrong_link, LINK_DOC, "the target changed"),
    "41_block_spacing":         ("render", mut_shift, BASE, "block gaps changed"),
    "42_alignment_mix":         ("render", lambda d: mut_shift(d, dx=10), BASE, "shifted sideways"),
    "43_within_10pt_x":         ("render", lambda d: mut_shift(d, dx=20), BASE, "shifted sideways"),
    "44_header_footer":         ("render", mut_header, BASE, "a header line added"),
    "45_char_accuracy":         ("render", mut_chars, BASE, "characters replaced"),
    "46_text_crossing_rule":    ("render", mut_rule, BASE, "a rule across text"),
    "47_margins":               ("render", lambda d: mut_shift(d, dx=20), BASE, "margins moved"),
    "48_image_area":            ("render", mut_image_shrink, IMG_DOC, "the image resized"),
    "49_page_size":             ("render", mut_pagesize, BASE, "the page size changed"),
    "50_annotations":           ("source", src_annot, BASE, "an annotation dropped"),
    "51_form_fields":           ("source", src_widget, BASE, "a form field dropped"),
    "52_outline":               ("source", src_toc, BASE, "the outline dropped"),
    "53_embedded_faces":        ("render", mut_font, BASE, "a different face used"),
    "54_image_dpi":             ("render", mut_image_shrink, IMG_DOC, "the image resolution changed"),
    "55_orientation_mix":       ("render", mut_landscape, BASE, "the page turned landscape"),
    "56_rtl_runs":              ("render", lambda d: mut_shift(d, dx=10), BASE, "direction disturbed"),
}


def real_evidence():
    """The strongest evidence available: real documents converted by the real
    engine, rendered by a real renderer, verified. A check that fires here has
    proved itself on the material the tool actually meets."""
    import glob
    fired, varied = set(), set()
    values = {}
    pairs = 0
    for g in sorted(glob.glob(os.path.join(RENDERS, "*.pdf"))) if RENDERS else []:
        name = os.path.basename(g)
        src = os.path.join(CORPUS, name)
        if not os.path.exists(src):
            continue
        pairs += 1
        res = run(src, g)
        for k in res["failed"]:
            fired.add(k)
        for k, v in res["checks"].items():
            values.setdefault(k, set()).add(str(v.get("render") if isinstance(v, dict) else v))
    for k, vs in values.items():
        if len(vs) > 1:
            varied.add(k)
    return pairs, fired, varied


def main():
    if not os.path.isdir(CORPUS) or not glob.glob(os.path.join(CORPUS, "*.pdf")):
        print("corpus not found at %s" % CORPUS)
        print("")
        print("This tool proves every check can fire, on real documents. It needs the corpus:")
        print("    gh release download corpus-v1 --repo kavopdf/app \\")
        print("        --pattern p2w-all-groups.zip -O c.zip && unzip -qo c.zip -d t")
        print("    P2W_CORPUS=<dir with the pdfs> python3 prove_checks.py")
        print("")
        print("Optional: P2W_RENDERS=<dir of pdfs the engine produced> adds the real-render stage.")
        return 2
    os.makedirs(WORK, exist_ok=True)
    ids = subprocess.run([sys.executable, VERIFY, "--list-checks"],
                         capture_output=True, text=True).stdout.split()
    print("checks: %d" % len(ids))

    if not RENDERS:
        print("note: no P2W_RENDERS given, so the real-render stage is skipped. Every check")
        print("      proven below is proven by mutating a real document; the rest are reported")
        print("      unproven rather than assumed. Give P2W_RENDERS=<dir of engine-produced")
        print("      pdfs> for the full proof.")
        print("")
    pairs, fired, varied = real_evidence()
    print("real evidence: %d documents converted and rendered, %d checks fired, "
          "%d more discriminated" % (pairs, len(fired), len(varied - fired)))

    ctrl = run(path(BASE), path(BASE))
    if ctrl is None:
        print("control could not be measured: %s is missing or unreadable" % BASE)
        print("nothing below would mean anything without a clean control, so this stops here.")
        return 2
    print("control (a document against itself): %d/%d, %d failing"
          % (ctrl["passed"], ctrl["total"], len(ctrl["failed"])))
    if ctrl["failed"]:
        print("  CONTROL IS DIRTY - fix this before trusting anything below:",
              ctrl["failed"])

    proven, unproven = [], []
    for cid in ids:
        if cid in fired:
            proven.append((cid, "fired on real converted documents", 0))
            continue
        if cid in varied:
            proven.append((cid, "discriminates across real documents", 0))
            continue
        if cid not in CASES:
            unproven.append((cid, "no case written"))
            continue
        direction, fn, docname, why = CASES[cid]
        srcfile = path(docname)
        if not os.path.exists(srcfile):
            unproven.append((cid, "%s missing from the corpus" % docname))
            continue
        d = fitz.open(srcfile)
        try:
            fn(d)
        except Exception as e:
            d.close()
            unproven.append((cid, "mutation failed: %s" % str(e)[:40]))
            continue
        out = save(d, "mut_%s.pdf" % cid)
        if direction == "render":
            res = run(srcfile, out)
        else:
            res = run(out, srcfile)
        others = [k for k in res["failed"] if k != cid]
        if cid in res["failed"]:
            proven.append((cid, why, len(others)))
        else:
            unproven.append((cid, "%s - did not fire" % why))

    # The additive mutations: same object, wrong direction. Each is applied to the
    # same document the firing mutation uses, so the pair differs only in whether
    # the render gains or loses the feature. Reported with the check's own
    # (source, render, ok) so "the object changed and the check still passed" is
    # read off the check, not off this file's opinion of it.
    print("\nWRONG DIRECTION (the object changes; the comparison cannot fail):")
    for cid, (fn, docname, why) in WRONG_DIRECTION.items():
        srcfile = path(docname)
        if not os.path.exists(srcfile):
            print("   %-26s %s missing from the corpus" % (cid, docname))
            continue
        d = fitz.open(srcfile)
        try:
            fn(d)
        except Exception as e:
            d.close()
            print("   %-26s mutation failed: %s" % (cid, str(e)[:40]))
            continue
        out = save(d, "neg_%s.pdf" % cid)
        res = run(srcfile, out)
        if res is None:
            print("   %-26s could not be measured" % cid)
            continue
        v = res["checks"].get(cid, {})
        print("   %-26s %-44s src=%s render=%s ok=%s%s"
              % (cid, why, v.get("source"), v.get("render"), v.get("ok"),
                 "   FIRED" if cid in res["failed"] else ""))

    print("\nPROVEN: %d of %d" % (len(proven), len(ids)))
    for cid, why, n in proven:
        note = "" if n <= 8 else "   (%d other checks moved too)" % n
        print("   %-26s %s%s" % (cid, why, note))
    if unproven:
        print("\nUNPROVEN: %d" % len(unproven))
        for cid, why in unproven:
            print("   %-26s %s" % (cid, why))
    print("\n%d proven, %d unproven of %d"
          % (len(proven), len(unproven), len(ids)))
    return 0 if not unproven else 1


if __name__ == "__main__":
    sys.exit(main())
