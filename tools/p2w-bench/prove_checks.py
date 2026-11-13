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
# The relative mutations below need a page whose median is not pinned by a
# cluster of identical values. The invoice (BASE) has five gaps of exactly
# 17.0 pt around its median block gap and nine baseline gaps between 9.0 and
# 12.5 pt around its median pitch, so moving one block or respacing one block
# leaves both medians where they were - measured, not assumed. This document has
# 41 left-aligned lines, 35 of them inside multi-line blocks, and no cluster of
# equal gaps around either median, so one moved block moves them.
MONO_DOC = "34_monospace_document.pdf"


def run(src, gd, docx=None):
    """Measure a pair, and return None rather than crashing when it cannot.

    tempfile.mktemp returned a path under /scratch/tmp, which does not exist, so
    verify_google.py never wrote the file and the open() below raised instead of
    reporting. A proof harness that dies on the first missing file proves nothing.
    """
    fd, out = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    cmd = [sys.executable, VERIFY, src, gd, "--json", out]
    if docx:
        cmd += ["--docx", docx]
    subprocess.run(cmd, capture_output=True)
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


def find_docx(srcfile):
    """The engine's .docx for this source, where the pipeline keeps it."""
    stem = os.path.splitext(os.path.basename(srcfile))[0]
    for cand in (os.path.join(os.path.dirname(srcfile), "..", "out1", stem + ".docx"),
                 os.path.join(os.path.dirname(srcfile), stem + ".docx"),
                 os.path.join(WORK, stem + ".docx")):
        if os.path.exists(cand):
            return cand
    return None


def render_for(srcfile):
    """The engine-produced render for this source, when P2W_RENDERS was given."""
    if not RENDERS:
        return None
    cand = os.path.join(RENDERS, os.path.basename(srcfile))
    return cand if os.path.exists(cand) else None


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


def mut_column_narrow(doc, page=0, sx=0.72):
    """Shrink the body column's right edge on one page, leaving every left edge alone.

    60_text_column_right_edge had NO case in this table at all - it was reported
    UNPROVEN, "no case written", so the 210-mutant run this check was signed off on never
    touched it. This is the defect it exists for: the render's column is narrower than the
    source's, which is the mirror of w:pgMar right="0" running the other way. The left
    edges are kept, so 47 stays silent and only 60 can see it.
    """
    p = doc[page]
    moves = []
    for b in _blocks(p):
        for ln in b.get("lines", []):
            sp = [s for s in ln["spans"] if s["text"].strip()]
            if not sp:
                continue
            moves.append((fitz.Rect(ln["bbox"]),
                          "".join(s["text"] for s in sp),
                          max(s["size"] for s in sp)))
    if not moves:
        return
    for r, t, sz in moves:
        p.add_redact_annot(r)
    p.apply_redactions()
    kw = {"fontname": _FACE, "fontfile": UNI_FONT} if _HAVE_UNI else {"fontname": "helv"}
    for r, t, sz in moves:
        p.insert_text((r.x0, r.y1 - 1), t, fontsize=sz, color=(0, 0, 0),
                      morph=(fitz.Point(r.x0, r.y1 - 1),
                             fitz.Matrix(sx, 0, 0, 1, 0, 0)), **kw)


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


def _face_class(name):
    """serif / sans / mono, read off a PostScript face name.

    Only used to choose a mutator's target, never to score anything: 53's own
    SAME_FACE table is the authority on which names are the same family, and it
    is not consulted here. Anything unrecognised is sans, which is what the
    corpus is overwhelmingly made of.
    """
    n = (name or "").lower()
    if any(k in n for k in ("courier", "mono")):
        return "mono"
    if any(k in n for k in ("times", "serif", "roman", "georgia", "garamond",
                            "book", "century", "palatino", "cambria")):
        return "serif"
    return "sans"


def mut_font_drop(doc):
    """Re-draw every span in a face from a DIFFERENT style class.

    NO LONGER 53's CASE - kept because it proves 09_font_names, which still reads the
    render. 53 now reads the .docx (13 Nov), so a mutation of the RENDER cannot move it;
    its case is `mut_docx_face` below.

    History: 53_embedded_faces counted the families the SOURCE draws with that the render
    no longer draws with, so it could only fail when the render LOST a family.
    `mut_font` above ADDS one - "tiro" is Times-Roman, a serif - to a document
    that already draws its own face. The intersection can only grow, so 53 could
    not fail and had never been proved (PROVE-GAPS.md). This mutator goes the
    one direction the comparison treats as a regression.

    Each span is redacted and re-drawn at its exact baseline origin, at its own
    size. Words, coordinates, sizes and page count are unchanged; only the drawn
    family differs, and images and line art are explicitly kept so the fire is
    attributable to the face rather than to something the redaction ate.

    The target class is chosen from what the page actually draws. Drawing a sans
    face over a sans document leaves SAME_FACE with the same family on both
    sides - a correct conversion would then read as kept, and the mutation would
    prove nothing. So a serif document is re-drawn sans, and a sans or mono
    document is re-drawn serif; both land in a different bucket.

    A document that draws no text at all cannot fire, by construction: `faces()`
    returns an empty set, the check passes vacuously on `len(s_fa) == 0`, and no
    mutation can change that. That is a property of the check, not of the
    mutation, and is recorded in PROVE-GAPS.md.
    """
    target = {"serif": "helv", "sans": "tiro", "mono": "tiro"}
    for p in doc:
        sp = spans_of(p)
        if not sp:
            continue
        seen = {}
        for _, s in sp:
            k = _face_class(s.get("font"))
            seen[k] = seen.get(k, 0) + 1
        want = target[max(seen, key=seen.get)]
        for r, _ in sp:
            p.add_redact_annot(r)
        p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                           graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                           text=fitz.PDF_REDACT_TEXT_REMOVE)
        for r, s in sp:
            p.insert_text(s["origin"], s["text"], fontsize=s["size"],
                          fontname=want, color=(0, 0, 0))


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


# ---- relative mutations: change a RELATIVE quantity, not the page ----------
# mut_shift translates the whole page, and every check that measures a RELATION
# between two things is invariant under that translation: the gap between two
# blocks, the count of left/right/centre lines, the direction of a line, the
# pitch between two baselines. Four checks were mutated with mut_shift and could
# therefore never fire, whatever the document. Each mutator below changes the
# measured relation itself and leaves the page where it is.
#
# All four redraw spans through _reflow, which is the redaction plus reinsertion
# mut_restyle already does, but per SPAN and at the span's own x unless it is
# deliberately moved. Two things were measured and are why it is per span:
# reinserting a whole line as one string loses the gaps between spans (the
# invoice's "1 Hex" came back as "1Hex"), and a base-14 font drops the glyphs it
# has no character for (the em dash and the bullet vanished from the invoice).
# DejaVu has them; helv is the fallback when the font file is not there.
UNI_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_HAVE_UNI = os.path.exists(UNI_FONT)
_FACE = "uni" if _HAVE_UNI else "helv"
_FONT = fitz.Font(fontfile=UNI_FONT) if _HAVE_UNI else fitz.Font("helv")


def _reflow(page, moves):
    """Redraw exactly the spans in moves: (rect, text, size, x, dy)."""
    if not moves:
        return
    for r, t, sz, x, dy in moves:
        page.add_redact_annot(r)
    page.apply_redactions()
    kw = {"fontname": _FACE, "fontfile": UNI_FONT} if _HAVE_UNI else {"fontname": "helv"}
    for r, t, sz, x, dy in moves:
        page.insert_text((x, r.y1 - 1 + dy), t, fontsize=sz, color=(0, 0, 0), **kw)


def _blocks(page):
    return [b for b in page.get_text("dict")["blocks"] if b.get("type") == 0]


def _span_moves(block, dy=0.0, dx=0.0):
    out = []
    for ln in block.get("lines", []):
        for sp in ln["spans"]:
            if sp["text"].strip():
                out.append((fitz.Rect(sp["bbox"]), sp["text"], sp["size"],
                            sp["bbox"][0] + dx, dy))
    return out


def _tops(page):
    return sorted({round(b["bbox"][1], 1) for b in _blocks(page)})


def _median_gap(tops):
    g = sorted([round(b - a, 1) for a, b in zip(tops, tops[1:]) if 1 < b - a < 300])
    return g[len(g) // 2] if g else 0


def mut_block_gap(doc, steps=(-60, -40, -30, 30, 40, 60)):
    """Move ONE block, leaving every other block where it is.

    41_block_spacing reads the median gap between block tops on page 1. mut_shift
    moved the whole page, so every gap was unchanged and the check could not fire.
    Moving one block changes the gap above it and the gap below it.

    The block and the distance are searched for, not assumed, because a single
    moved block does NOT always move a median: the invoice (BASE) has five gaps of
    exactly 17.0 pt around its median, and measured here all 168 candidates (its
    28 block tops x the 6 distances) leave the median at 17.0 - the search would
    find nothing. On MONO_DOC one moved block takes the median from 24.4 to 86.1.
    """
    p = doc[0]
    tops = _tops(p)
    base = _median_gap(tops)
    best = (0.0, None, None)
    for i in range(len(tops)):
        for dy in steps:
            m = _median_gap(sorted(tops[:i] + [round(tops[i] + dy, 1)] + tops[i + 1:]))
            if abs(m - base) > best[0]:
                best = (abs(m - base), i, dy)
    if best[1] is None:
        return
    top, dy = tops[best[1]], best[2]
    moves = []
    for b in _blocks(p):
        if abs(round(b["bbox"][1], 1) - top) < 0.05:
            moves += _span_moves(b, dy=dy)
    _reflow(p, moves)


def mut_alignment(doc):
    """Centre the lines of every block that has more than one line.

    42_alignment_mix compares the counts of left, right and centred lines. A
    uniform shift leaves all three counts identical, so mut_shift(dx=10) could
    not prove it. Here each block is re-laid with its lines centred on that
    block's own width, which turns its left lines into centre lines.

    Centring ONE line is not enough and that is measured, not assumed: the check
    passes while 70 % of the source's classified lines still match, so on a
    document with 42 classified lines thirteen must move, and one centred line
    leaves 41 of 42 matching. Centring every multi-line block on MONO_DOC takes
    the counts from (41 left, 1 right, 0 centre) to (6, 0, 36) and fires.
    """
    for p in doc:
        moves = []
        for b in _blocks(p):
            lines = [ln for ln in b.get("lines", []) if ln["spans"]]
            if len(lines) < 2:
                continue
            geom, bw = [], 0.0
            for ln in lines:
                spans, w, prev = [], 0.0, None
                for sp in ln["spans"]:
                    if not sp["text"]:
                        continue
                    if prev is not None:
                        w += max(0.0, sp["bbox"][0] - prev)   # keep the gap between spans
                    spans.append((fitz.Rect(sp["bbox"]), sp["text"], sp["size"], w))
                    w += _FONT.text_length(sp["text"], fontsize=sp["size"])
                    prev = sp["bbox"][2]
                geom.append((spans, w))
                bw = max(bw, w)
            bx0 = b["bbox"][0]
            for spans, w in geom:
                dx = (bw - w) / 2.0
                for r, t, sz, off in spans:
                    moves.append((r, t, sz, bx0 + dx + off, 0))
        _reflow(p, moves)


def mut_rtl(doc):
    """Draw a run with a negative-direction text matrix.

    56_rtl_runs counts lines whose dir[0] < 0 and PASSES when the source has
    none, because of `s_rtl == 0 or ...`. No render-side mutation can fail it on a
    document with no reversed run - mut_shift least of all - so the run is added
    to the SOURCE side of the pair, the same shape as src_annot: the source then
    has one reversed line and the render has none.

    Note what this check actually counts: dir[0] < 0 is any line whose x axis
    points left, which includes text rotated 180 degrees. Ten corpus documents
    have such lines and none of them is right-to-left script.
    """
    p = doc[0]
    p.insert_text((300, 620), "reversed run", fontsize=11, color=(0, 0, 0),
                  morph=(fitz.Point(300, 620), fitz.Matrix(-1, 1)))


def _run_ys(page):
    return sorted({round(sp["bbox"][1], 1) for b in _blocks(page)
                   for ln in b.get("lines", []) for sp in ln["spans"]
                   if sp["text"].strip()})


def _pitch_of(ys):
    g = sorted([round(b - a, 1) for a, b in zip(ys, ys[1:]) if 1 < b - a < 200])
    return g[len(g) // 2] if g else 0


def mut_line_pitch(doc, factors=(2.0, 1.6, 0.6)):
    """Change one block's baseline pitch, keeping its first baseline in place.

    23_line_pitch reads the median gap between consecutive baselines. mut_shift
    moved every baseline by the same amount, so every gap stayed 11.0 pt and the
    check could not fire. Here one block's lines are respaced about that block's
    own first baseline: the block's pitch changes, the page does not move.

    The block and the factor are searched for, because the median is taken over
    the whole page and one block among many need not move it. On MONO_DOC the
    search doubles one block's pitch and takes the median from 12.4 to 24.8 pt.
    """
    pages = list(doc)
    best = (0.0, None, None)
    for pi, p in enumerate(pages):
        ys = _run_ys(p)
        base = _pitch_of(ys)
        for bi, b in enumerate([x for x in _blocks(p) if len(x.get("lines", [])) >= 2]):
            ly = [round(ln["bbox"][1], 1) for ln in b["lines"]]
            for fac in factors:
                y0 = ly[0]
                new = set(ys) - set(ly)
                new |= {round(y0 + (y - y0) * fac, 1) for y in ly}
                m = _pitch_of(sorted(new))
                if abs(m - base) > best[0]:
                    best = (abs(m - base), pi, (bi, fac))
    if best[1] is None:
        return
    p = pages[best[1]]
    bi, fac = best[2]
    b = [x for x in _blocks(p) if len(x.get("lines", [])) >= 2][bi]
    y0 = b["lines"][0]["bbox"][1]
    moves = []
    for ln in b["lines"]:
        for sp in ln["spans"]:
            if sp["text"].strip():
                yb = sp["bbox"][3] - 1
                moves.append((fitz.Rect(sp["bbox"]), sp["text"], sp["size"],
                              sp["bbox"][0], (y0 + (yb - y0) * fac) - yb))
    _reflow(p, moves)


def mut_docx_face(path):
    """Rewrite the engine's .docx so a family the source DREW WITH is no longer named.

    This is the mutation 53 needs and the one it never had. 53 fails on LOSS, and a face
    can only be lost where the engine writes it: w:rFonts in word/document.xml. The
    render-side mutations cannot prove it any more, because 53 no longer reads the render
    at all - mut_font_drop redraws the RENDER, and a check that measures the .docx cannot
    see it. The least-used declared face is renamed to a name no SAME_FACE entry maps, so
    exactly one family disappears and every other family keeps its share. Returns the path
    of the mutated copy.
    """
    import zipfile, re as _re, collections as _c
    zin = zipfile.ZipFile(path)
    xml = zin.read("word/document.xml").decode("utf-8")
    faces = _c.Counter(_re.findall(r'w:ascii="([^"]*)"', xml))
    if not faces:
        raise RuntimeError("no w:rFonts in the .docx")
    victim = min(faces, key=lambda k: (faces[k], k))
    dst = os.path.join(WORK, "mut_53_%s.docx"
                       % os.path.splitext(os.path.basename(path))[0])
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            data = xml.replace('w:ascii="%s"' % victim,
                               'w:ascii="NoSuchFace"').encode("utf-8")
        zout.writestr(item, data)
    zout.close()
    return dst


# check -> ("render" | "source" | "docx", mutation, document, description)
CASES = {
    "01_page_count":            ("render", mut_addpage, BASE, "a page added"),
    "02_text_run_count":        ("render", mut_restyle, BASE, "30% of spans restyled"),
    "04_chars_missing":         ("render", mut_blank, BASE, "the page's text removed"),
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
    "18_displacement":          ("render", mut_shift, BASE, "everything shifted vertically"),
    "19_worst_dy":              ("render", mut_shift, BASE, "everything shifted vertically"),
    "21_median_dx":             ("render", lambda d: mut_shift(d, dx=10), BASE, "shifted sideways"),
    "22_reading_order":         ("render", mut_blank, BASE, "the page's order destroyed"),
    "23_line_pitch":            ("render", mut_line_pitch, MONO_DOC, "one block's pitch doubled"),
    "24_page_breaks":           ("render", mut_droppage, BASE, "a page dropped"),
    "25_invisible_text":        ("render", mut_invisible, BASE, "text drawn white on white"),
    "26_text_overlap":          ("render", mut_rule, BASE, "a rule across text"),
    "27_text_off_page":         ("render", mut_offpage, BASE, "text placed outside the page"),
    "28_clipped_at_edge":       ("render", mut_clip, BASE, "text pushed off the edge"),
    "29_blank_where_ink_was":   ("render", mut_blank, BASE, "ink removed"),
    "30_ink_where_blank_was":   ("render", mut_rule, BASE, "ink added"),
    "31_pages_lost_their_text": ("render", mut_blank, BASE, "the page left blank"),
    "32_stroke_lines":          ("render", mut_rules_removed, BASE, "every rule removed"),
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
    "41_block_spacing":         ("render", mut_block_gap, MONO_DOC, "one block moved, the rest left alone"),
    "42_alignment_mix":         ("render", mut_alignment, MONO_DOC, "every multi-line block centred"),
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
    # 53 reads the .docx, so its mutation has to be a .docx. "docx" hands the mutation the
    # engine's own file and measures the same pair with the mutated copy.
    "53_embedded_faces":        ("docx", mut_docx_face, BASE, "a drawn family dropped from the .docx"),
    "54_image_dpi":             ("render", mut_image_shrink, IMG_DOC, "the image resolution changed"),
    "55_orientation_mix":       ("render", mut_landscape, BASE, "the page turned landscape"),
    "56_rtl_runs":              ("source", mut_rtl, BASE, "a reversed run the render does not have"),
    "60_text_column_right_edge": ("render", mut_column_narrow, MONO_DOC,
                                 "the body column 28 % narrower, every left edge kept"),
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
        if direction == "docx":
            # A .docx mutation: the same source and the same render, with the engine's file
            # swapped for the mutated one. The render is held fixed on purpose - a re-render
            # would move the position checks and the "how many others moved" number would
            # describe the renderer, not this check. The control is the same pair with the
            # unmutated .docx, and it must pass or the fire proves nothing.
            docx = find_docx(srcfile)
            if not docx:
                unproven.append((cid, "no .docx beside %s" % docname))
                continue
            gd = render_for(srcfile) or srcfile
            ctrl = run(srcfile, gd, docx=docx)
            if ctrl is None or cid in ctrl["failed"]:
                unproven.append((cid, "the control already fails - nothing to prove"))
                continue
            try:
                mut = fn(docx)
            except Exception as e:
                unproven.append((cid, "mutation failed: %s" % str(e)[:40]))
                continue
            res = run(srcfile, gd, docx=mut)
        else:
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
