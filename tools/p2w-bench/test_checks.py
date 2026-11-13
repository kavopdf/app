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
import zipfile
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


def compare_files(a, b, docx=None):
    return V.compare(a, b, docx)


def docx_faces_doc(path, face):
    """A minimal .docx that declares one face on one run - all 53 reads.

    RESTORED 13 Nov. 0afff7a wrote this fixture and 64c2816, repairing that commit's
    regex accident by restoring test_checks.py from de2196e, did not carry it over -
    so the 53 case below went from asserting the check fires to asserting nothing, and
    53 has had no self-contained proof since. The fixture is verbatim from 0afff7a
    because it works: with it, a .docx naming "Liberation Serif" leaves 53 clean and
    one naming "DejaVu Sans" fails it, which is the whole of what 53 measures.
    """
    NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    z.writestr("word/document.xml",
               '<w:document xmlns:w="%s"><w:body><w:p><w:r><w:rPr>'
               '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/></w:rPr>'
               '<w:t>Invoice number 12345</w:t></w:r></w:p></w:body></w:document>'
               % (NS, face, face, face))
    z.writestr("word/styles.xml",
               '<w:styles xmlns:w="%s"><w:docDefaults><w:rPrDefault><w:rPr>'
               '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr></w:rPrDefault>'
               '</w:docDefaults></w:styles>' % NS)
    z.close()


def docx_image_doc(path, px=40, extent_pt=360):
    """A minimal .docx embedding one px-wide PNG drawn extent_pt wide.

    54_image_dpi reads exactly two things out of a .docx: the bytes in word/media, and the
    wp:extent beside the r:embed, so px / (extent_pt / 72) is the density the engine chose.
    Nothing else in the package is read, but the parts a reader would expect are written so
    the file is a real .docx and not a fixture that only this test can open.
    """
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, px, px), 0)
    pix.set_rect(pix.irect, (200, 30, 30))
    png = pix.tobytes("png")
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
    A = "http://schemas.openxmlformats.org/drawingml/2006/main"
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    cx = int(extent_pt * 12700)
    z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    z.writestr("[Content_Types].xml",
               '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/'
               'package/2006/content-types"><Default Extension="png" ContentType="image/png"/>'
               '<Default Extension="xml" ContentType="application/xml"/></Types>')
    z.writestr("_rels/.rels",
               '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/'
               'package/2006/relationships"><Relationship Id="rId0" Type="%s/officeDocument"'
               ' Target="word/document.xml"/></Relationships>' % R)
    z.writestr("word/document.xml",
               '<?xml version="1.0"?><w:document xmlns:w="%s" xmlns:wp="%s" xmlns:a="%s" '
               'xmlns:r="%s"><w:body><w:p><w:r><w:drawing><wp:inline><wp:extent cx="%d" '
               'cy="%d"/><a:graphic><a:graphicData><a:blip r:embed="rId1"/></a:graphicData>'
               '</a:graphic></wp:inline></w:drawing></w:r></w:p></w:body></w:document>'
               % (W, WP, A, R, cx, cx))
    z.writestr("word/_rels/document.xml.rels",
               '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/'
               'package/2006/relationships"><Relationship Id="rId1" Type="%s/image" '
               'Target="media/image1.png"/></Relationships>' % R)
    z.writestr("word/media/image1.png", png)
    # 53_embedded_faces reads the family the .docx declares and needs styles.xml to exist,
    # so the package carries one. It is not what 54 measures.
    z.writestr("word/styles.xml",
               '<w:styles xmlns:w="%s"><w:docDefaults><w:rPrDefault><w:rPr>'
               '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr></w:rPrDefault>'
               '</w:docDefaults></w:styles>' % W)
    z.close()


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
    out.append(("word missing", base, missing_word, ["04_chars_missing"], None))

    # ---- 18/19/20 vertical shift ------------------------------------------
    def shifted(p):
        text(p, 72, 112, "Invoice number 12345")
        text(p, 72, 142, "Total amount 4,500")
        table(p, 72, 212, 3, 3)
    # A uniform 12 pt shift is far outside clamp(0.35*size, 1.5, 4.5) at this document's
    # type size, so every run on the page is out and the page's budget of
    # max(2, ceil(0.05*n)) cannot absorb it. 18_displacement owns a uniform offset.
    out.append(("text shifted 12pt", base, shifted, ["18_displacement"], None))

    # ---- 18's tail clause: one run, however few ----------------------------
    # The count budget forgives a single stray run by construction, so a page whose only
    # fault is one run far out is the tail clause's case. It used to be 19_worst_dy's case
    # and 19 was max() of the same list, so nothing here distinguished them; 19 is gone and
    # this case now proves the clause that replaced it.
    def rows(p, wild=0):
        for i in range(24):
            dy = wild if i == 12 else 0
            text(p, 72, 100 + 24 * i + dy, "row %02d amount 4,500" % i)
    out.append(("one run of 24 out 20pt", lambda p: rows(p), lambda p: rows(p, 20),
                ["18_displacement"], None))

    # ---- 18 must not fail a page it cannot see -----------------------------
    # A page whose every line is rotated has no upright run, so it contributes nothing to
    # the population 18 measures. It used to be scored as a displaced page: constructed, a
    # fully rotated page against ITSELF failed 18 while 19 read 0.0. 35_rotation owns those
    # runs. This asserts the false positive stays gone.
    def all_rotated(p):
        for i in range(6):
            p.insert_text((72, 100 + 24 * i), "vertical marker %02d" % i, fontsize=11,
                          fontname="helv", rotate=90)
    out.append(("every line rotated, identical", all_rotated, all_rotated, [], "all"))

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

    # ---- 46 a rule drawn over text (33 retired - it was this check with a
    # 2 pt inset on each end, and the two agreed on all 208 corpus documents) ---
    def border_through(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.draw_line((60, 96), (400, 96), color=(0, 0, 0), width=1)
    out.append(("rule through text", base, border_through, ["46_text_crossing_rule"], None))

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
    out.append(("one digit changed", base, one_char, ["04_chars_missing"], None))

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

    # ---- 39 image position: the same picture, in the same size, moved 40 pt ----
    # The old proof in prove_checks.py was mut_image_shrink, which resizes: a resize leaves
    # the box origin where it was, so 39 could not fire on it. Nothing here resizes.
    def image_moved(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 40, 40), 0)
        pix.set_rect(pix.irect, (200, 30, 30))
        p.insert_image(fitz.Rect(112, 400, 212, 500), pixmap=pix)
    out.append(("image moved, not resized", with_image, image_moved,
                ["39_image_position"], None))

    # ---- 48 image area: shrunk to 9 % of its area ---------------------------
    # Below the 50 % floor the check already had, so this case passed before the floor was
    # tightened; it is here so the check has a self-contained proof at all, which it did not.
    def image_small(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 40, 40), 0)
        pix.set_rect(pix.irect, (200, 30, 30))
        p.insert_image(fitz.Rect(72, 400, 102, 430), pixmap=pix)
    out.append(("image shrunk to 9 % of its area", with_image, image_small,
                ["48_image_area"], None))

    # ---- 49 page size: A4 in, Letter out ------------------------------------
    # The failure this check exists for. Every one of the 211 corpus documents keeps its
    # size through the export, which is why it has never fired there - not because it cannot.
    def letter(p):
        text(p, 72, 100, "Invoice number 12345")
        text(p, 72, 130, "Total amount 4,500")
        table(p, 72, 200, 3, 3)
        p.set_mediabox(fitz.Rect(0, 0, 612, 792))
    out.append(("A4 exported as Letter", base, letter, ["49_page_size"], None))

    # ---- 09 font names: four faces in, one out ------------------------------
    def four_faces(p):
        for i, f in enumerate(("helv", "tiro", "cour", "symb")):
            p.insert_text((72, 100 + i * 20), "Invoice number 12345", fontsize=11, fontname=f)
    def one_face(p):
        p.insert_text((72, 100), "Invoice number 12345", fontsize=11, fontname="helv")
    out.append(("four faces, one face kept", four_faces, one_face, ["09_font_names"], None))

    # ---- 31 pages lost their text: a page that had text is empty ------------
    def empty_page(p):
        pass
    out.append(("a page that had text is blank", base, empty_page,
                ["31_pages_lost_their_text"], None))

    # ---- 54 image dpi: the engine places the picture at 40 dpi --------------
    # 54 reads the .docx, so the case has to carry one. A 40 px picture drawn 360 pt (5 in)
    # wide is 8 dpi against a source of 28.8 dpi, well under the 60 % floor.
    def low_dpi(path):
        docx_image_doc(path, px=40, extent_pt=360)
    out.append(("the engine places the picture at 8 dpi", with_image, with_image,
                ["54_image_dpi"], None, low_dpi))

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

    # ---- 53: a substituted face is not automatically a kept face -----------
    # Liberation Serif arriving as Times New Roman is the same metrics and must
    # pass; arriving as a sans is a different face and must still fail. Built from
    # real font files, because base-14 names cannot express this.
    SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
    SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    if os.path.exists(SERIF) and os.path.exists(SANS):
        def serif_only(p):
            p.insert_font(fontname="FS", fontfile=SERIF)
            p.insert_text((72, 100), "Invoice number 12345", fontsize=12, fontname="FS")

        def sans_only(p):
            p.insert_font(fontname="FN", fontfile=SANS)
            p.insert_text((72, 130), "Total amount 4,500", fontsize=12, fontname="FN")

        # 53 reads the .docx the engine wrote, not Google's export, so a PDF-only pair
        # cannot fire it - without --docx it cannot fail and says so on stderr. The sixth
        # element therefore carries the family the .docx declares, and the assertion below
        # is real again: 64c2816 had to weaken it to [] because it dropped 0afff7a's
        # fixture, which left 53 with no test that could fail it anywhere but on the corpus.
        out.append(("the same faces keep 53 clean", serif_only, serif_only, [], None,
                    "Liberation Serif"))
        out.append(("a different face still fails 53", serif_only, sans_only,
                    ["53_embedded_faces"], None, "DejaVu Sans"))

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
    for case in cases():
        name, src_b, gd_b, expect, allow = case[:5]
        docx_face = case[5] if len(case) > 5 else None
        a = os.path.join(tmp, "a.pdf")
        b = os.path.join(tmp, "b.pdf")
        simple(a, src_b)
        simple(b, gd_b)
        docx = None
        if docx_face:
            # A sixth element is what the engine's .docx has to say. 53 reads the family it
            # declares, so it passes a face name; 54 reads the density it places a picture
            # at, which a face name cannot express, so it passes a builder that writes the
            # package. Both need a .docx to fail at all.
            docx = os.path.join(tmp, "a.docx")
            if callable(docx_face):
                docx_face(docx)
            else:
                docx_faces_doc(docx, docx_face)
        try:
            res = compare_files(a, b, docx)
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
        elif allow:
            # The docstring above has always promised this: a check named in `allow` must NOT
            # be in `failed`. The code only ever implemented the "all" form, so every case
            # that passed a list was silently asserting nothing about it.
            for e in allow:
                if e in failed:
                    ok = False
                    why.append("%s should not fire but did" % e)
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
