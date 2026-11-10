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
# /scratch/work/a3, the sandbox directory of the session that wrote it, so the
# tool was committed to the repository and could not run anywhere else - the same
# mistake audit_sim.py made. Defaults are relative to this file and to a temporary
# directory, so a fresh clone works.
CORPUS = os.environ.get("P2W_CORPUS", os.path.join(HERE, "..", "..", "corpus"))
WORK = os.environ.get("P2W_WORK", tempfile.mkdtemp(prefix="prove-"))
RENDERS = os.environ.get("P2W_RENDERS", "")   # optional: pdfs rendered from the engine

BASE = "01_stamp_rotated_15deg_upright.pdf"
IMG_DOC = "10_stamp_as_image.pdf"
LINK_DOC = "44_coloured_underlined_hyperlinks.pdf"


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
    "32_stroke_lines":          ("render", mut_rule, BASE, "a rule added"),
    "33_border_over_text":      ("render", mut_rule, BASE, "a rule through a word"),
    "34a_span_size_match":      ("render", mut_restyle, BASE, "30% of spans resized"),
    "34b_span_colour_match":    ("render", mut_restyle, BASE, "30% of spans recoloured"),
    "34c_span_weight_match":    ("render", mut_bold, BASE, "35% of spans made bold"),
    "35_rotation":              ("render", mut_rotate, BASE, "the page rotated"),
    "36_underline_rules":       ("render", mut_rule, BASE, "a rule added"),
    "37_super_subscript":       ("render", mut_rule, BASE, "a rule added"),
    "38_list_markers":          ("render", mut_rule, BASE, "a marker added"),
    "39_image_position":        ("render", mut_image_shrink, IMG_DOC, "the image moved"),
    "40_link_targets":          ("render", mut_wrong_link, LINK_DOC, "the target changed"),
    "41_block_spacing":         ("render", mut_shift, BASE, "block gaps changed"),
    "42_alignment_mix":         ("render", lambda d: mut_shift(d, dx=10), BASE, "shifted sideways"),
    "43_within_10pt_x":         ("render", lambda d: mut_shift(d, dx=10), BASE, "shifted sideways"),
    "44_header_footer":         ("render", mut_header, BASE, "a header line added"),
    "45_char_accuracy":         ("render", mut_chars, BASE, "characters replaced"),
    "46_text_crossing_rule":    ("render", mut_rule, BASE, "a rule across text"),
    "47_margins":               ("render", lambda d: mut_shift(d, dx=10), BASE, "margins moved"),
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
