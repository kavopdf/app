#!/usr/bin/env python3
"""Defect detector for the PDF -> Word converter.

Answers one question per document: *would a human opening this .docx find something
missing, clipped, glued or wrapped?* It does that by comparing the .docx against the
PDF it was made from, and it prints one line per defect.

Nine classes. The first six are read out of the .docx's XML; the last three are not
visible there at all, because they are about what a READER gets: the pictures the page
drew, and the text a word processor actually renders.

  MISSING TEXT   a word on the PDF page that appears nowhere in the .docx
  MISSING ROWS   a PDF line whose text is absent from that page of the .docx, grouped
                 by page so a whole clipped table row shows up as one block
  GLUED WORDS    a .docx leaf paragraph that is the concatenation of 2+ consecutive
                 PDF lines ("SUNRISEFASTENERS" out of "SUNRISE" + "FASTENERS")
  WRAPPED        a .docx leaf paragraph of 1-3 characters where the PDF has a longer
                 word at that position (IFSC rendered as I / F / S / C)
  DUPLICATED     a leaf paragraph appearing more times than the PDF has that line
  EMPTY PAGE     a page of the .docx with no leaf paragraphs on it
  IMAGE LOST     a PDF page that draws a picture while the .docx carries no word/media/
                 part at all - the pixels were counted and thrown away
  CLIPPED        a leaf paragraph whose text in the RENDER is a strict prefix of what
                 the XML holds: the tail is not wrapped, it is gone
  RENDER MISSING text the XML holds that appears nowhere in the render

Why the last three needed adding: every defect that mattered in the 3.49.6 batch was
image-level or render-level. RuleCollector.drawImage counted images and threw the pixels
away, so a scanned page came out blank and three stamps vanished; and text boxes were
sized to the exact PDF advance, so Word cut "31-03-2026" to "31-". None of the six text
metrics moved when those were fixed, and this file reported the same 57 lines before and
after. A detector that reads only word/document.xml cannot see a picture, and cannot see
a box clipping its own text.

CLIPPED is not "the render has less text". A leaf that WRAPS is not clipped - every
character is still there, on two lines - so the test is made with the spaces removed:
only a leaf whose characters are genuinely absent counts.

Why "leaf paragraphs": the converter puts each PDF line in a text box. A text box is
`<w:p><w:r><w:drawing>...<w:txbxContent><w:p>text</w:p></w:txbxContent>`, so the outer
`w:p` is a *wrapper* around a real paragraph. Counting every `w:p` counts the wrapper
too - it holds the same text as its child on some writers - and every "duplicated" and
"missing" number is then wrong. A leaf paragraph is one that contains no nested `w:p`.

python-docx cannot see text-box content at all, so the XML is read with lxml.

Usage
  detect.py --pdf-dir PDFS --docx-dir DOCX [--json OUT] [--quiet] [--only NAME]
  detect.py --pdf-dir PDFS --docx-dir DOCX --summary
  detect.py --pdf-dir PDFS --docx-dir DOCX --render-dir RENDERED
  detect.py --pdf-dir PDFS --docx-dir DOCX --render

--render-dir points at .docx files that were already converted to PDF (the name must
match, .pdf instead of .docx). --render does the conversion here, with LibreOffice:
`soffice --headless --convert-to pdf`. Without one of the two, CLIPPED and
RENDER MISSING cannot be judged and are reported as not run, never as zero.

Exit code is 0 always: this is a report, not a gate. A caller that wants a gate reads
the --json output and looks at `totals`.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

try:
    import pymupdf as fitz
except ImportError:  # older installs
    import fitz

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "wp": WP, "a": A}

EMU_PER_PT = 12700.0

CLASSES = ("MISSING_TEXT", "MISSING_ROWS", "GLUED_WORDS",
           "WRAPPED", "DUPLICATED", "EMPTY_PAGE",
           "IMAGE_LOST", "CLIPPED", "RENDER_MISSING")

# The three that need something other than word/document.xml: a look at the package's
# media parts, and a render.
RENDER_CLASSES = ("CLIPPED", "RENDER_MISSING")


# ---------------------------------------------------------------- normalisation

_WS = re.compile(r"\s+")
# Characters that are not text: soft hyphens, zero-width marks, the BOM, and U+0000.
# U+0000 is in the list for a measured reason - file 79 draws the rupee sign from a mono
# face with no Unicode map, so PyMuPDF reports it as \u0000. The PDF itself does not say
# which character that is, so "the .docx lost it" cannot be claimed from the text layer.
_INVISIBLE = dict.fromkeys(map(ord, "\u0000\u00ad\u200b\u200c\u200d\ufeff\u2060"), None)


def norm(s):
    """Text as a reader sees it: no invisible marks, one space per run of space."""
    return _WS.sub(" ", s.translate(_INVISIBLE)).strip()


def squash(s):
    """The same text with every space removed.

    Used for containment tests. A PDF line the converter split across two paragraphs
    is not missing, and a line it welded to the next one is not missing either - both
    are found by the classes that own them. Comparing with the spaces gone keeps
    MISSING ROWS about absence and nothing else.
    """
    return norm(s).replace(" ", "")


def words(s):
    return [w for w in norm(s).split(" ") if w]


# ---------------------------------------------------------------- PDF side

class PdfDoc:
    def __init__(self, path):
        self.path = path
        self.pages = []          # list of list of PdfLine
        self.image_pages = {}    # page number -> how many pictures that page draws
        doc = fitz.open(path)
        try:
            for pno in range(doc.page_count):
                page = doc[pno]
                # A picture is either an image XObject or an inline image block. Both are
                # what a reader sees and what a .docx has to carry in word/media/.
                n_img = len(page.get_images(full=True))
                for block in page.get_text("dict")["blocks"]:
                    if block.get("type") == 1:
                        n_img += 1
                if n_img:
                    self.image_pages[pno] = n_img
                lines = []
                for block in page.get_text("dict")["blocks"]:
                    if block.get("type") != 0:
                        continue
                    for ln in block["lines"]:
                        text = "".join(sp["text"] for sp in ln["spans"])
                        if not norm(text):
                            continue
                        lines.append(PdfLine(text, pno, ln["bbox"]))
                self.pages.append(lines)
        finally:
            doc.close()

    @property
    def page_count(self):
        return len(self.pages)


class PdfLine:
    __slots__ = ("text", "n", "page", "bbox", "squashed")

    def __init__(self, text, page, bbox):
        self.text = norm(text)
        self.n = self.text
        self.page = page
        self.bbox = bbox              # x0, y0, x1, y1 in points, y from the top
        self.squashed = self.text.replace(" ", "")

    def __repr__(self):
        return "<line p%d %r>" % (self.page + 1, self.text[:40])


# ---------------------------------------------------------------- DOCX side

class Leaf:
    """One leaf paragraph: a w:p that contains no other w:p."""
    __slots__ = ("text", "n", "squashed", "page", "box", "kind", "el")

    def __init__(self, text, page, box, kind, el):
        self.text = text
        self.n = norm(text)
        self.squashed = self.n.replace(" ", "")
        self.page = page
        self.box = box                # (x, y, w, h) in points, or None
        self.kind = kind              # "textbox" | "flow" | "table"
        self.el = el

    def __repr__(self):
        return "<leaf p%d %r>" % (self.page + 1, self.n[:40])


def _has_nested_p(el):
    """True when this w:p wraps another w:p - i.e. it is a text box's container.

    `el.iter(tag)` yields `el` itself as its first item, so the element has to be
    skipped or every paragraph looks nested and the document comes back empty.
    """
    for sub in el.iter("{%s}p" % W):
        if sub is not el:
            return True
    return False


def _text_of(el):
    return "".join(t.text or "" for t in el.iter("{%s}t" % W))


def _anchor_box(anchor):
    """(x, y, w, h) of an anchored drawing, in points from the page's top-left."""
    x = y = None
    for tag, axis in (("positionH", "x"), ("positionV", "y")):
        node = anchor.find("{%s}%s" % (WP, tag))
        if node is None:
            continue
        off = node.find("{%s}posOffset" % WP)
        val = 0.0
        if off is not None and off.text:
            val = float(off.text) / EMU_PER_PT
        if axis == "x":
            x = val
        else:
            y = val
    ext = anchor.find("{%s}extent" % WP)
    w = h = 0.0
    if ext is not None:
        w = float(ext.get("cx", "0")) / EMU_PER_PT
        h = float(ext.get("cy", "0")) / EMU_PER_PT
    return (x or 0.0, y or 0.0, w, h)


class DocxDoc:
    def __init__(self, path):
        self.path = path
        self.leaves = []
        self.page_count = 0
        self.media = []
        with zipfile.ZipFile(path) as z:
            self.media = [n for n in z.namelist() if n.startswith("word/media/")]
            xml = z.read("word/document.xml")
        root = etree.fromstring(xml)
        body = root.find("{%s}body" % W)
        if body is None:
            return

        page = 0
        page_break_seen = 0
        for child in body:
            tag = etree.QName(child).localname
            if tag == "sectPr":
                continue
            for leaf in self._leaves_in(child, page):
                self.leaves.append(leaf)
            # A page break or a next-page section ends the page after this child.
            if child.find(".//{%s}br[@{%s}type='page']" % (W, W)) is not None:
                page += 1
                page_break_seen += 1
            else:
                sp = child.find(".//{%s}sectPr" % W)
                if sp is not None:
                    ty = sp.find("{%s}type" % W)
                    if ty is None or ty.get("{%s}val" % W) in (None, "nextPage"):
                        page += 1
                        page_break_seen += 1
        self.page_count = page_break_seen + 1
        # Anything anchored at a y beyond the page it was counted on still belongs to
        # the page the break counter put it on; the counter is the authority because
        # the converter writes one break per PDF page.

    def _leaves_in(self, node, page):
        """Yield the leaf paragraphs under one body child, in document order."""
        out = []
        for el in node.iter("{%s}p" % W):
            if _has_nested_p(el):
                continue
            # kind + position: walk up to a text box's anchor if there is one.
            box = None
            kind = "flow"
            anc = el.getparent()
            while anc is not None:
                if etree.QName(anc).localname == "txbxContent":
                    kind = "textbox"
                    break
                anc = anc.getparent()
            if kind == "textbox":
                anc = el.getparent()
                anchor = None
                while anc is not None:
                    if etree.QName(anc).localname == "anchor":
                        anchor = anc
                        break
                    anc = anc.getparent()
                if anchor is not None:
                    box = _anchor_box(anchor)
            else:
                tc = el.getparent()
                while tc is not None and etree.QName(tc).localname != "tc":
                    tc = tc.getparent()
                if tc is not None:
                    kind = "table"
            out.append(Leaf(_text_of(el), page, box, kind, el))
        return out

    def leaves_on(self, page):
        return [l for l in self.leaves if l.page == page]

    def text_on(self, page):
        return " ".join(l.n for l in self.leaves_on(page) if l.n)


# ---------------------------------------------------------------- defects

def _line_at(pdf_page, box, tol=4.0):
    """The PDF line that occupies a .docx anchor's box, or None.

    A wrapped fragment ("I") sits on the same baseline as the whole word it was cut
    from, so the line is found by vertical overlap with the anchor's own box, widened
    a little: a 1-character paragraph is only a few points tall and rounding moves it.
    """
    if not box:
        return None
    x, y, w, h = box
    y0, y1 = y - tol, y + h + tol
    best, best_dy = None, 1e9
    for ln in pdf_page:
        lx0, ly0, lx1, ly1 = ln.bbox
        if ly1 < y0 or ly0 > y1:
            continue
        # prefer the line whose left edge is nearest the paragraph's left edge
        dx = abs(lx0 - x)
        if dx < best_dy:
            best, best_dy = ln, dx
    return best


class Render:
    """The .docx turned back into a PDF, so its text can be read as a reader sees it.

    Not a formality: this is the only way to see a text box that is narrower than the line
    it holds. `bodyPr wrap="none"` means the box does not wrap - it CLIPS - and the clipped
    characters are still sitting in word/document.xml, so nothing that reads the XML can
    tell that they are gone.
    """

    def __init__(self, path):
        self.path = path
        self.pages = []
        doc = fitz.open(path)
        try:
            for page in doc:
                self.pages.append(norm(page.get_text()))
        finally:
            doc.close()
        self.all = " ".join(self.pages)
        self.squashed = self.all.replace(" ", "")

    def count(self, text):
        """Non-overlapping occurrences of `text`, spaces ignored on both sides."""
        return self.squashed.count(text.replace(" ", ""))


def _prefix_seen(text, render):
    """Longest prefix of `text` that the render holds and then STOPS at.

    Returned as a length, 0 when the render holds no prefix of it.

    Two conditions, and both are needed. The prefix has to end where a clipping box can
    actually stop - the end of a word, or a hyphenated fragment - so a prefix that merely
    matches inside a longer word is not read as a clipped one. And the render must not carry
    the next character after it: if the render has "31-0" anywhere then "31-" is not a
    clipping, it is a coincidence.

    The second condition is what makes a SHORT clip detectable. "31-03-2026" comes back as
    "31-" - three characters - and the old rule demanded four plus half the string, so the
    clearest clipping in the batch was reported as RENDER_MISSING, i.e. as "the box lost
    everything" when it had lost only the tail. Measured on the 3.49.5 engine, file 03's
    stamp date was the one of the three known clips the detector did not name.
    """
    hay = render.all
    best = 0
    for k in range(1, len(text)):
        if text[k] == " " or not text[k].isalnum():
            pass                      # a box can stop here
        elif text[k - 1] in "-.,;:/":
            pass                      # ... or just after a hyphen, comma, point
        else:
            continue
        if len(text[:k].strip()) < 3:
            continue
        if text[:k] not in hay:
            continue
        # The render has to stop exactly here: the next non-space character must be absent.
        j = k
        while j < len(text) and text[j] == " ":
            j += 1
        if j < len(text) and text[:j + 1] in hay:
            continue
        best = k
    return best


def find_render_defects(name, docx, render):
    """CLIPPED and RENDER MISSING: what the XML holds that the render does not show."""
    out = []

    def add(cls, page, detail, **extra):
        d = {"class": cls, "doc": name, "page": page + 1, "detail": detail}
        d.update(extra)
        out.append(d)

    # Grouped by text, because the same line can legitimately appear on several pages: what
    # matters is how many copies the render holds against how many the XML holds.
    want = {}
    for lf in docx.leaves:
        if len(lf.n) < 4:
            # Four characters is below the shortest line the batch contains that a box can
            # cut in two, and short strings are substrings of longer ones far too easily.
            continue
        want.setdefault(lf.n, []).append(lf)

    for text, leaves in want.items():
        have = render.count(text)
        short = len(leaves) - have
        if short <= 0:
            continue
        # A leaf that merely WRAPPED is not lost: every character is still on the page, on
        # two lines. Comparing with the spaces gone separates the two cases exactly.
        if render.count(text) >= len(leaves):
            continue
        k = _prefix_seen(text, render)
        for lf in leaves[have:have + short]:
            if k >= 3 and k < len(text):
                add("CLIPPED", lf.page, text, kept=text[:k].strip(),
                    lost=text[k:].strip(), kept_chars=k, of_chars=len(text),
                    box=[round(v, 1) for v in lf.box] if lf.box else None)
            else:
                add("RENDER_MISSING", lf.page, text,
                    box=[round(v, 1) for v in lf.box] if lf.box else None)
    return out


def find_defects(name, pdf, docx, render=None):
    """Every defect in one document, as dicts."""
    out = []

    def add(cls, page, detail, **extra):
        d = {"class": cls, "doc": name, "page": page + 1, "detail": detail}
        d.update(extra)
        out.append(d)

    # ---- a. MISSING TEXT -------------------------------------------------
    pdf_words = {}
    for lines in pdf.pages:
        for ln in lines:
            for w in words(ln.text):
                pdf_words[w] = pdf_words.get(w, 0) + 1
    docx_words = {}
    for lf in docx.leaves:
        for w in words(lf.n):
            docx_words[w] = docx_words.get(w, 0) + 1
    for w, cnt in sorted(pdf_words.items()):
        if not any(c.isalnum() for c in w):
            # A lone comma or full stop is not text a reader misses; the line that held
            # it is already reported by MISSING_ROWS if the whole line went.
            continue
        if w not in docx_words:
            add("MISSING_TEXT", -1, w, pdf_count=cnt)
    out.sort(key=lambda d: (d["class"] != "MISSING_TEXT", d["page"]))

    # ---- b. MISSING ROWS -------------------------------------------------
    # Grouped by page: every PDF line on a page whose text is not in that page's
    # .docx text. One clipped table row = one run of consecutive lines, so they are
    # reported in page order and the caller sees the run.
    for pno, lines in enumerate(pdf.pages):
        page_squash = squash(docx.text_on(pno)) if pno < docx.page_count else ""
        for ln in lines:
            if ln.squashed and ln.squashed in page_squash:
                continue
            add("MISSING_ROWS", pno, ln.text, line_bbox=[round(v, 1) for v in ln.bbox])

    # ---- c. GLUED WORDS --------------------------------------------------
    # A leaf whose squashed text is the squashed concatenation of 2..5 consecutive PDF
    # lines, and which is not itself one PDF line. Spaces removed on both sides because
    # a weld that kept the space ("SUNRISE FASTENERS" out of two lines) is the same
    # defect as one that did not.
    for lf in docx.leaves:
        s = lf.squashed
        if len(s) < 4:
            continue
        lines = pdf.pages[lf.page] if lf.page < pdf.page_count else []
        hit = None
        for i in range(len(lines)):
            acc = ""
            for k in range(5):
                if i + k >= len(lines):
                    break
                acc += lines[i + k].squashed
                if len(acc) > len(s):
                    break
                if k >= 1 and acc == s:
                    hit = lines[i:i + k + 1]
                    break
            if hit:
                break
        if hit:
            add("GLUED_WORDS", lf.page,
                " | ".join(h.text for h in hit),
                paragraph=lf.n, parts=len(hit))

    # ---- d. WRAPPED ------------------------------------------------------
    # The symptom is I / F / S / C stacked one above the other: a word that did not fit
    # its column, cut into single characters and each character given its own line. So
    # the test is not "a short paragraph exists" - that matches a drop cap, a serial
    # number, a list marker - it is "short paragraphs stacked at one x, which together
    # spell a word the PDF drew as one word".
    stacks = {}
    for lf in docx.leaves:
        if lf.box is None or not lf.n:
            continue
        stacks.setdefault((lf.page, round(lf.box[0] / 3.0)), []).append(lf)
    for key in sorted(stacks):
        col = sorted(stacks[key], key=lambda l: l.box[1])
        page_lines = pdf.pages[col[0].page] if col[0].page < pdf.page_count else []
        for i, lf in enumerate(col):
            s = lf.n
            if not s or len(s) > 3 or " " in s:
                continue
            ln = _line_at(page_lines, lf.box)
            if ln is None:
                continue
            pool = set(words(ln.text))
            acc = lf.squashed
            for k in range(i + 1, len(col)):
                acc += col[k].squashed
                if len(acc) > 24:
                    break
                if acc in pool and len(acc) > len(s):
                    add("WRAPPED", lf.page, "%r stacked as %r"
                        % (acc, [c.n for c in col[i:k + 1]]),
                        paragraph=s, word=acc, pieces=k - i + 1,
                        box=[round(v, 1) for v in lf.box])
                    break

    # ---- e. DUPLICATED ---------------------------------------------------
    pdf_count = {}
    for pno, lines in enumerate(pdf.pages):
        for ln in lines:
            if len(ln.squashed) < 3:
                continue
            pdf_count[(pno, ln.squashed)] = pdf_count.get((pno, ln.squashed), 0) + 1
    seen = {}
    for lf in docx.leaves:
        s = lf.squashed
        if len(s) < 3:
            continue
        key = (lf.page, s)
        seen[key] = seen.get(key, 0) + 1
        have = pdf_count.get(key, 0)
        if have >= 1 and seen[key] > have and seen[key] == have + 1:
            add("DUPLICATED", lf.page, lf.n,
                docx_copies=None, pdf_copies=have)

    # ---- f. EMPTY PAGE ---------------------------------------------------
    for pno in range(pdf.page_count):
        if pno >= docx.page_count:
            add("EMPTY_PAGE", pno, "page absent from the .docx entirely")
            continue
        if not any(lf.n for lf in docx.leaves_on(pno)):
            add("EMPTY_PAGE", pno,
                "no leaf paragraph on this page (PDF has %d lines)"
                % len(pdf.pages[pno]))

    # ---- g. IMAGE LOST ---------------------------------------------------
    # A page that draws a picture has to reach the .docx as a picture. Every PDF page that
    # draws one, in a .docx that carries no word/media/ part at all, lost all of them.
    if pdf.image_pages and not docx.media:
        for pno in sorted(pdf.image_pages):
            add("IMAGE_LOST", pno,
                "%d picture(s) drawn on the page, .docx has no word/media/ part"
                % pdf.image_pages[pno], images=pdf.image_pages[pno])

    # ---- h/i. CLIPPED, RENDER MISSING ------------------------------------
    if render is not None:
        out.extend(find_render_defects(name, docx, render))

    # duplicate counts need the final total per key
    dup_total = {}
    for lf in docx.leaves:
        if len(lf.squashed) >= 3:
            k = (lf.page, lf.squashed)
            dup_total[k] = dup_total.get(k, 0) + 1
    for d in out:
        if d["class"] == "DUPLICATED":
            d["docx_copies"] = dup_total[(d["page"] - 1, norm(d["detail"]).replace(" ", ""))]

    return out


# ---------------------------------------------------------------- render

def render_one_dir(docx_dir, out_dir):
    """Convert every .docx in a directory to .pdf with LibreOffice, once, in one call.

    `soffice --headless --convert-to pdf` takes a list, so one process does the whole
    directory. A profile directory of its own is passed because two conversions sharing
    one profile is how LibreOffice silently returns a stale file.
    """
    docx = sorted(f for f in os.listdir(docx_dir) if f.lower().endswith(".docx"))
    if not docx:
        return out_dir
    profile = os.path.join(out_dir, ".lo-profile")
    cmd = ["soffice", "--headless",
           "-env:UserInstallation=file://" + profile,
           "--convert-to", "pdf", "--outdir", out_dir]
    cmd += [os.path.join(docx_dir, f) for f in docx]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.stderr.write("detect: LibreOffice render failed: %s\n" % exc)
    shutil.rmtree(profile, ignore_errors=True)
    return out_dir


# ---------------------------------------------------------------- driver

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--docx-dir", required=True)
    ap.add_argument("--json", help="write the full report here")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    ap.add_argument("--only", help="substring of a document name")
    ap.add_argument("--summary", action="store_true", help="per-document totals table")
    ap.add_argument("--render-dir",
                    help=".pdf renders of the .docx, named like them; enables CLIPPED "
                         "and RENDER_MISSING")
    ap.add_argument("--render", action="store_true",
                    help="convert the .docx with LibreOffice here and judge the render")
    args = ap.parse_args(argv)

    render_dir = args.render_dir
    tmpdir = None
    if args.render and not render_dir:
        tmpdir = tempfile.mkdtemp(prefix="p2w-render-")
        render_dir = render_one_dir(args.docx_dir, tmpdir)
    if render_dir and not os.path.isdir(render_dir):
        ap.error("--render-dir %s is not a directory" % render_dir)

    pdfs = sorted(f for f in os.listdir(args.pdf_dir) if f.lower().endswith(".pdf"))
    all_defects = []
    per_doc = {}
    missing_docx = []
    no_render = []

    for f in pdfs:
        name = f[:-4]
        if args.only and args.only not in name:
            continue
        dpath = os.path.join(args.docx_dir, name + ".docx")
        if not os.path.exists(dpath):
            missing_docx.append(name)
            continue
        pdf = PdfDoc(os.path.join(args.pdf_dir, f))
        docx = DocxDoc(dpath)
        render = None
        if render_dir:
            rpath = os.path.join(render_dir, name + ".pdf")
            if os.path.exists(rpath):
                render = Render(rpath)
            else:
                no_render.append(name)
        defects = find_defects(name, pdf, docx, render)
        all_defects.extend(defects)
        counts = {c: 0 for c in CLASSES}
        for d in defects:
            counts[d["class"]] += 1
        per_doc[name] = {"counts": counts, "total": len(defects),
                         "pdf_pages": pdf.page_count, "docx_pages": docx.page_count,
                         "leaves": len([l for l in docx.leaves if l.n]),
                         "media": len(docx.media),
                         "image_pages": sorted(pdf.image_pages),
                         "rendered": render is not None}
        if not args.quiet:
            for d in defects:
                page = "all" if d["page"] == 0 else "p%d" % d["page"]
                print("%-13s %-52s %-5s %s" % (d["class"], name, page, d["detail"]))

    totals = {c: 0 for c in CLASSES}
    for v in per_doc.values():
        for c in CLASSES:
            totals[c] += v["counts"][c]

    print()
    print("=" * 96)
    print("TOTALS over %d documents (%d defect lines)"
          % (len(per_doc), len(all_defects)))
    for c in CLASSES:
        docs = sum(1 for v in per_doc.values() if v["counts"][c])
        print("  %-13s %6d  in %2d documents" % (c, totals[c], docs))
    if missing_docx:
        print("  no .docx produced for %d documents: %s"
              % (len(missing_docx), ", ".join(missing_docx[:5])))
    if not render_dir:
        print("  CLIPPED and RENDER_MISSING were NOT RUN (pass --render or "
              "--render-dir): a .docx has to be rendered before a clipped box can be seen")
    elif no_render:
        print("  no render for %d documents, so their CLIPPED/RENDER_MISSING are unknown: %s"
              % (len(no_render), ", ".join(no_render[:5])))

    ranked = sorted(per_doc.items(), key=lambda kv: -kv[1]["total"])
    print()
    print("WORST DOCUMENTS")
    for name, v in ranked[:10]:
        if v["total"] == 0:
            break
        parts = ", ".join("%s=%d" % (c, n) for c, n in v["counts"].items() if n)
        print("  %-52s %4d  %s" % (name, v["total"], parts))

    if args.summary:
        print()
        print("PER DOCUMENT")
        print("  %-52s %5s %5s %5s %5s %5s %5s %5s %5s %5s %6s"
              % ("document", "MISS", "ROWS", "GLUE", "WRAP", "DUP", "EMPTY",
                 "IMG", "CLIP", "RMISS", "total"))
        for name in sorted(per_doc):
            v = per_doc[name]
            c = v["counts"]
            print("  %-52s %5d %5d %5d %5d %5d %5d %5d %5d %5d %6d"
                  % (name, c["MISSING_TEXT"], c["MISSING_ROWS"], c["GLUED_WORDS"],
                     c["WRAPPED"], c["DUPLICATED"], c["EMPTY_PAGE"],
                     c["IMAGE_LOST"], c["CLIPPED"], c["RENDER_MISSING"], v["total"]))

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"totals": totals, "documents": per_doc,
                       "defects": all_defects,
                       "no_docx": missing_docx,
                       "rendered": bool(render_dir),
                       "no_render": no_render}, fh, indent=1)
        print("\njson -> %s" % args.json)

    if tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
