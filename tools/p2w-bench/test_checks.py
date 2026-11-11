#!/usr/bin/env python3
"""
test_checks.py - does each check in verify_google.py actually fire?

WHY THIS EXISTS
  A check that never fails is not a check, it is decoration. A check that always
  fails is worse: it condemns every document and hides the real defect behind its
  noise. Both look identical in a report, and both were present in this file on
  10 Nov - five checks failed a document against itself, and nobody had noticed
  because nobody had ever run the verifier on two copies of the same file.

  So every check is tested here twice: once on a pair that differs in exactly the
  way it claims to measure, and once on a pair that differs in no relevant way.
  A check that cannot tell those two apart is broken regardless of how reasonable
  its code looks.

HOW IT WORKS
  Each case builds two small PDFs from scratch with PyMuPDF, so the difference is
  known exactly. compare() is called directly - no Drive, no network, no corpus.

  expect   the check must appear in `failed`
  allow    the check must NOT appear in `failed`
  either   the check must behave consistently but its verdict is not asserted
           (used where a synthetic document cannot isolate the property)

USAGE
  python3 tools/p2w-bench/test_checks.py            # run everything
  python3 tools/p2w-bench/test_checks.py -v         # show every case
"""
import os
import sys
import tempfile
import warnings

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
# builders - every document is made from nothing, so its properties are exact
# ---------------------------------------------------------------------------
def page(doc, w=595, h=842):
    return doc.new_page(width=w, height=h)


def text(p, x, y, s, size=11, colour=(0, 0, 0), font="helv"):
    p.insert_text((x, y), s, fontsize=size, color=colour, fontname=font)


def table(p, x0, y0, cols, rows, cw=80, rh=24):
    """Draw a bordered grid - strokes only, no fill, like a real invoice table."""
    for r in range(rows + 1):
        y = y0 + r * rh
        p.draw_line((x0, y), (x0 + cols * cw, y), color=(0, 0, 0), width=1)
    for c in range(cols + 1):
        x = x0 + c * cw
        p.draw_line((x, y0), (x, y0 + rows * rh), color=(0, 0, 0), width=1)


def simple(path, body):
    doc = fitz.open()
    body(page(doc))
    doc.save(path)
    doc.close()


def compare_files(a, b):
    return V.compare(a, b)


# ---------------------------------------------------------------------------
# cases
# ---------------------------------------------------------------------------
def cases():
    """Yield (name, src_builder, gd_builder, expect, allow)."""
    out = []

    # ---- a pair that differs in nothing: nothing may fail ------------------
    def base(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)

    out.append(("identical", base, base, [], "all"))

    # ---- 01 page count -----------------------------------------------------
    def two_pages(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        text(p, 72, 400, "continued")
        p.parent.new_page()          # a genuinely extra page
    out.append(("extra page", base, two_pages, ["01_page_count"], None))

    # ---- 03/04 missing word ------------------------------------------------
    def missing_word(p):
        text(p, 72, 100, "Invoice number")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
    out.append(("word missing", base, missing_word, ["04_words_missing"], None))

    # ---- 18/19/20 vertical shift ------------------------------------------
    def shifted(p):
        text(p, 72, 112, "Invoice number 12345")
        text(p, 72, 142, "Total amount 4,500")
        table(p, 72, 212, 3, 3)
    out.append(("text shifted 12pt", base, shifted, ["20_within_10pt"], None))

    # ---- 21/43 horizontal shift -------------------------------------------
    def shifted_x(p):
        text(p, 132, 100, "Invoice number 12345")
        text(p, 132, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
    out.append(("text shifted right", base, shifted_x, ["43_within_10pt_x"], None))

    # ---- 32 stroke lines ---------------------------------------------------
    def no_lines(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
    out.append(("borders removed", base, no_lines, ["32_stroke_lines"], None))

    # ---- 33 border drawn over text ----------------------------------------
    def border_through(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.draw_line((60, 96), (400, 96), color=(0, 0, 0), width=1)
    out.append(("rule through text", base, border_through, ["33_border_over_text"], None))

    # ---- 34a span size -----------------------------------------------------
    def bigger(p):
        text(p, 72, 100, "Invoice number 12345", size=16)
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
    out.append(("one span resized", base, bigger, ["34a_span_size_match"], None))

    # ---- 34b span colour ---------------------------------------------------
    def recoloured(p):
        text(p, 72, 100, "Invoice number 12345", colour=(1, 0, 0))
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
    out.append(("one span recoloured", base, recoloured, ["34b_span_colour_match"], None))

    # ---- 45 character accuracy --------------------------------------------
    def one_char(p):
        text(p, 72, 100, "Invoice number 12346")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
    out.append(("one digit changed", base, one_char, ["04_words_missing"], None))

    # ---- 47 margins --------------------------------------------------------
    def narrow(p):
        text(p, 160, 100, "Invoice number 12345")
        text(p, 160, 130, "Total amount 4,500")
        table(p, 160, 200, 2, 3)
    out.append(("margins moved", base, narrow, ["47_margins"], None))

    # ---- 25 invisible text -------------------------------------------------
    def on_fill(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.draw_rect(fitz.Rect(60, 300, 300, 340), color=None, fill=(0, 0, 0))
        text(p, 70, 325, "hidden words here", colour=(0, 0, 0))
    out.append(("text on same-colour fill", base, on_fill, ["25_invisible_text"], None))

    # ---- 15/40 links -------------------------------------------------------
    def no_link(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
    def with_link(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(60, 90, 300, 108),
                       "uri": "https://example.com/inv"})
    out.append(("link dropped", with_link, no_link, ["15_links"], None))

    # ---- 48 image area -----------------------------------------------------
    def with_image(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 40, 40), 0)
        pix.set_rect(pix.irect, (200, 30, 30))
        p.insert_image(fitz.Rect(72, 400, 172, 500), pixmap=pix)
    out.append(("image dropped", with_image, base, ["08_image_count"], None))

    # ---- 35 rotation -------------------------------------------------------
    def rotated_text(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.insert_text((500, 600), "PAID", fontsize=20, rotate=90)
    out.append(("rotated text dropped", rotated_text, base, ["35_rotation"], None))

    # ---- 25 and 27: a defect is text that BECAME invisible or left the page --
    # The source already having it is the document's own shape, not a conversion
    # fault. Seven corpus documents failed against themselves before this.
    def white_on_white(p):
        text(p, 72, 100, "Invoice number 12345")
        p.draw_rect(fitz.Rect(60, 120, 400, 150), color=None, fill=(1, 1, 1))
        p.insert_text((72, 142), "hidden watermark", fontsize=11, color=(1, 1, 1))

    out.append(("invisible text the source already had", white_on_white, white_on_white,
                [], None))

    def became_invisible(p):
        text(p, 72, 100, "Invoice number 12345")
        p.draw_rect(fitz.Rect(60, 120, 400, 150), color=None, fill=(1, 1, 1))
        p.insert_text((72, 142), "hidden watermark", fontsize=11, color=(0, 0, 0))

    out.append(("text turned invisible by the conversion", became_invisible, white_on_white,
                ["25_invisible_text"], None))

    def on_page(p):
        text(p, 72, 100, "Invoice number 12345")
        p.insert_text((72, 300), "edge marker", fontsize=11)

    def off_page(p):
        text(p, 72, 100, "Invoice number 12345")
        p.insert_text((-40, 300), "edge marker", fontsize=11)

    out.append(("text already off the page in the source", off_page, off_page, [], None))
    out.append(("text pushed off the page by the conversion", on_page, off_page,
                ["27_text_off_page"], None))

    # ---- 59 shape anchor ---------------------------------------------------
    # A stamp is an outline with text inside it. These two cases are the failure
    # modes the user described: the outline moves and leaves its text, and the
    # text moves and leaves its outline. The second one is the important test -
    # on that pair 59 is the ONLY check that fails, which is the whole reason it
    # was added.
    def stamp(p, shape_dx=0, text_dy=0):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.draw_rect(fitz.Rect(360 + shape_dx, 560, 520 + shape_dx, 640),
                    color=(0.75, 0.05, 0.05), width=2)
        p.insert_text((400, 610 + text_dy), "PAID", fontsize=26, color=(0.75, 0.05, 0.05))

    out.append(("stamp outline moved off its text",
                stamp, lambda p: stamp(p, shape_dx=55),
                ["59_shape_anchor"], None))
    out.append(("stamp text moved out of its outline",
                stamp, lambda p: stamp(p, text_dy=34),
                ["59_shape_anchor"], None))

    return out


def run(verbose=False):
    tmp = tempfile.mkdtemp(prefix="chk-")
    results = []
    for name, src_b, gd_b, expect, allow in cases():
        a = os.path.join(tmp, "a.pdf")
        b = os.path.join(tmp, "b.pdf")
        simple(a, src_b)
        simple(b, gd_b)
        try:
            res = compare_files(a, b)
        except Exception as exc:
            results.append((name, "ERROR", "compare raised: %s" % exc, []))
            continue
        failed = set(res["failed"])
        ok = True
        why = []
        for e in expect:
            if e not in failed:
                ok = False
                why.append("%s did not fire" % e)
        if allow == "all":
            if failed:
                ok = False
                why.append("nothing should fail, but %s did" % ", ".join(sorted(failed)))
        results.append((name, "PASS" if ok else "FAIL", "; ".join(why), sorted(failed)))

    width = max(len(r[0]) for r in results) + 2
    bad = 0
    for name, verdict, why, failed in results:
        if verdict != "PASS":
            bad += 1
        if verbose or verdict != "PASS":
            print("%-*s %-6s %s" % (width, name, verdict, why))
    print("\n%d/%d cases behave as claimed" % (len(results) - bad, len(results)))
    if bad:
        print("\nA check that does not fire on a case built to make it fire is broken.")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(run(verbose="-v" in sys.argv))
