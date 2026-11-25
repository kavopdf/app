#!/usr/bin/env python3
"""minimal-repro.py - the smallest .docx that carries the ONE construct a check is known to fail on.

WHY THIS EXISTS. A full measurement cycle is ~54 minutes for 213 documents, so a fixer run affords
one to three patch attempts, and 218 attempts have produced zero kept changes. Most of that cost is
spent re-measuring 213 documents to learn one thing about one construct. If a single-page .docx
carrying only that construct reproduces the check's failure, a patch can be tested in seconds and
the corpus is spent only on the patch that survived.

WHAT IT IS NOT. A minimal repro is not evidence that the check fails. It is a HYPOTHESIS with the
smallest possible carrier. Nothing here has been through Google Docs - this tool cannot reach it -
so every repro it emits is unverified on the renderer of record, and the report says so per repro
rather than in a footnote. What IS verified is that the .docx opens, that the construct is in the
bytes, that google_safe.py's scan() counts it, and - with --render - that a renderer honours it.

    python3 tools/p2w-bench/minimal-repro.py --list
    python3 tools/p2w-bench/minimal-repro.py --check 18_displacement
    python3 tools/p2w-bench/minimal-repro.py --check 32_stroke_lines --variant cell-border-rule
    python3 tools/p2w-bench/minimal-repro.py --all --render --simulate --out /scratch/work/repro

Each run prints, for the repro it built: the exact OOXML it emitted, the construct count, what
google_safe.py scan() reads out of the file, and - when asked - what a renderer did with it.

THE SIMULATION IS LABELLED A SIMULATION. --simulate renders the same .docx twice with LibreOffice,
once as written and once with the construct neutralised the way Google is MEASURED to neutralise it
(w:before at a page top dropped to 0; a rule the renderer drops deleted). It then scores the pair
with verify_google.py. That proves the repro's failure is reachable by the measured mechanism and
that the instrument reads it as a failure. It is NOT a Google measurement and never becomes one.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
      'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"')

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

# Zero margins and a letter page, as the page-top probe used (FINDINGS/18_displacement-page-top-before-
# DROPPED-105000-f1x.md: "w:pgMar all zeros, page height 16838 twips"). A repro with a non-zero top
# margin cannot tell "Google dropped the gap" from "Google kept the margin".
SECT = ('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0" w:header="0" w:footer="0" w:gutter="0"/>'
        '</w:sectPr>')


def doc(body):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document %s mc:Ignorable="wps"><w:body>%s%s</w:body></w:document>' % (NS, body, SECT))


def write_docx(path, body):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        # Fixed timestamps: two runs of this tool must produce the same bytes, or a repro that is
        # diffed against yesterday's cannot be told apart from a changed construct.
        for name, data in (("[Content_Types].xml", CONTENT_TYPES),
                           ("_rels/.rels", ROOT_RELS),
                           ("word/_rels/document.xml.rels", DOC_RELS),
                           ("word/document.xml", body)):
            zi = zipfile.ZipInfo(name, date_time=(2026, 11, 24, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
    return path


def para(text, before=None, brk=False, sz=None):
    """One paragraph. before=<twips> is the ONLY construct 18_displacement is about."""
    ppr = ""
    if before is not None:
        ppr = '<w:pPr><w:spacing w:before="%d" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>' % before
    rpr = '<w:rPr><w:sz w:val="%d"/></w:rPr>' % sz if sz else ""
    br = '<w:br w:type="page"/>' if brk else ""
    return '<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t>%s</w:r></w:p>' % (ppr, rpr, text, br)


# ---- the constructs, one function each, so the emitted OOXML can be printed verbatim -----------

def drawing_rule(cy=25400, cx=3810000, y=1440000, name="Rule 1", ooxml_only=False):
    """A floating rule: a 300 x 2 pt filled rectangle inside wp:anchor.

    This is the construct the engine emits for a rule (a filled rect with a:ln noFill, per
    FINDINGS/32_stroke_lines-FLOATING-CARRIER-DRAWS-BUT-STACKS-2050-f1x.md: "on this corpus a rule
    is usually a FILL, not a stroke"). 25400 EMU = 2 pt, 3810000 EMU = 300 pt, 1440000 EMU = 113.4 pt
    from the page top - well inside the page, so "the rule is missing" cannot be confused with
    "the rule fell off the page".
    """
    return ('<w:drawing><wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" '
            'relativeHeight="1" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
            '<wp:simplePos x="0" y="0"/>'
            '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
            '<wp:positionV relativeFrom="page"><wp:posOffset>%d</wp:posOffset></wp:positionV>'
            '<wp:extent cx="%d" cy="%d"/>'
            '<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
            '<wp:docPr id="1" name="%s"/><wp:cNvGraphicFramePr/>'
            '<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
            '<wps:wsp><wps:cNvSpPr/><wps:spPr>'
            '<a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            '<a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:ln><a:noFill/></a:ln>'
            '</wps:spPr><wps:bodyPr/></wps:wsp>'
            '</a:graphicData></a:graphic></wp:anchor></w:drawing>'
            % (y, cx, cy, name, cx, cy))


def anchored_textbox(text, cx=2286000, cy=457200, y=1440000):
    """A text box: wp:anchor carrying a wps:txbx with a paragraph of its own text.

    ﻿One paragraph, inside an anchored box - the construct 04_chars_missing is measured to fail on
    (Google rasterises every anchored text box on import, so the characters are painted but are not
    characters, which is 166 failures across 04/45/13/44/17).
    """
    return ('<w:drawing><wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" '
            'relativeHeight="1" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
            '<wp:simplePos x="0" y="0"/>'
            '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
            '<wp:positionV relativeFrom="page"><wp:posOffset>%d</wp:posOffset></wp:positionV>'
            '<wp:extent cx="%d" cy="%d"/>'
            '<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
            '<wp:docPr id="2" name="TextBox 2"/><wp:cNvGraphicFramePr/>'
            '<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
            '<wps:wsp><wps:cNvSpPr txBox="1"/><wps:spPr>'
            '<a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>'
            '<a:ln><a:noFill/></a:ln></wps:spPr>'
            '<wps:txbx><w:txbxContent>'
            '<w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
            '</w:txbxContent></wps:txbx>'
            '<wps:bodyPr rot="0" wrap="none" lIns="0" tIns="0" rIns="0" bIns="0"/>'
            '</wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing>'
            % (y, cx, cy, cx, cy, text))


BORDER = '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'


def cell_border_table(text, border=True):
    """A rule as a table cell's TOP border, and nothing else.

    ONE side only. A full cell box (top+bottom+left+right) is not an isolated segment - each edge
    runs into the next at the corner - so verify_google._rules(isolated=True) does not count it and
    a repro built that way would carry a rule the check never asks about. The prompt names
    w:top|bottom|left|right; one side is the minimal faithful member of that family and it is the
    one that can be a lone rule. w:tblBorders all nil so no default grid is added.
    """
    nil = ''.join('<w:%s w:val="nil"/>' % s for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    return ('<w:tbl><w:tblPr><w:tblW w:w="6000" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            '<w:tblBorders>%s</w:tblBorders>'
            '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
            '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
            '</w:tblPr><w:tblGrid><w:gridCol w:w="6000"/></w:tblGrid>'
            '<w:tr><w:tc><w:tcPr><w:tcW w:w="6000" w:type="dxa"/>'
            '%s</w:tcPr>'
            '<w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
            '</w:tc></w:tr></w:tbl>' % (nil, ('<w:tcBorders>%s</w:tcBorders>' % BORDER) if border else '', text))


# ---- the repros --------------------------------------------------------------------------------

def body_18(neutralise=False):
    """18_displacement: w:before carrying a page's top gap, on the first paragraph after a hard break.

    Construct: exactly one w:before, on exactly one paragraph, and that paragraph is the first on
    page 2 after <w:br w:type="page"/>. Asked: 1103 twips = 55.15 pt, the value the corpus document
    bank-statement-5-pages emits and the value the probe measured.
    """
    before = 0 if neutralise else 1103
    return (para("P1MARK", brk=True)
            + para("P2MARK", before=before))


def body_32_drawing(neutralise=False):
    """32_stroke_lines, drawing variant: the rule is a floating wp:anchor drawing, and nothing else."""
    head = para("TOP")
    tail = para("BOTTOM")
    # THE ANCHOR PARAGRAPH STAYS WHEN THE SHAPE GOES. A renderer that drops the shape still lays
    # the paragraph the anchor lives in, and that paragraph's own line box is part of the flow -
    # measured here: deleting the whole paragraph instead moved BOTTOM up one line and fired
    # 18_displacement on a document that has no displacement in it. A neutralised variant that
    # changes the flow is not a control, it is a second defect.
    if neutralise:
        return head + '<w:p><w:r></w:r></w:p>' + tail
    return head + '<w:p><w:r>' + drawing_rule() + '</w:r></w:p>' + tail


def body_32_border(neutralise=False):
    """32_stroke_lines, border variant: the rule is a table cell's top border, and nothing else."""
    head = para("TOP")
    tail = para("BOTTOM")
    if neutralise:
        # Only the border goes. The table, its cell and its text stay, so the flow and the text
        # layer are byte-for-byte the same question - otherwise the pair measures the deletion of
        # a word, which is 04_chars_missing's question and not 32's.
        return head + cell_border_table("CELLMARK", border=False) + tail
    return head + cell_border_table("CELLMARK") + tail


def body_04(neutralise=False):
    """04_chars_missing: one paragraph of text inside an anchored text box, plus a body marker.

    BODYMARK is outside the box on purpose: with only the box's text in the document, "the characters
    are missing" and "the document is empty" are the same measurement, and a check that fails on an
    empty document tells you nothing about the box.
    """
    if neutralise:
        # Google rasterised the box: the glyphs are painted but they are not characters, so the
        # text layer has the body marker and nothing else.
        return para("BODYMARK")
    return para("BODYMARK") + '<w:p><w:r>' + anchored_textbox("TXBXMARK") + '</w:r></w:p>'


REPROS = [
    {
        "check": "18_displacement",
        "variant": "before-page-top",
        "body": body_18,
        "construct": "w:before on the first paragraph after a hard page break",
        "path": "w:document/w:body/w:p[2]/w:pPr/w:spacing/@w:before",
        "count_key": "w:before-page-top",
        "expect": "one w:before; the paragraph is the first on page 2",
        "law": ("Google drops w:before at the top of a page: 55.15 pt asked, 0.33 pt rendered. "
                "FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md, TOPA vs TOPD."),
        "caveat": ("the failure is a DISPLACEMENT between two renders, so it needs a reference. With "
                   "no source PDF, the reference has to be the .docx rendered by LibreOffice - which "
                   "is what the original probe compared. A document whose page 2 carries no other "
                   "content cannot show a displacement at all; this one carries one marker line."),
        "marker_page": 1, "marker": "P2MARK", "expect_y_pt": 55.15,
    },
    {
        "check": "32_stroke_lines",
        "variant": "drawing-rule",
        "body": body_32_drawing,
        "construct": "a rule as a floating w:drawing (wp:anchor, 300 x 2 pt filled rect)",
        "path": "w:document/w:body/w:p[2]/w:r/w:drawing/wp:anchor/a:graphic/.../wps:spPr",
        "count_key": "w:drawing",
        "expect": "one w:drawing, one wp:anchor, no table in the document",
        "law": ("A rule carried only as a floating <w:drawing> has never passed 32_stroke_lines "
                "(google_safe.py --predict docstring, measured 22 Nov over 192 scored documents); "
                "the two documents that pass carry the rule as a table-cell border. Measured "
                "directly on 73_marksheet: the floating anchor drew 0 of 2 rules in the Google "
                "export, FINDINGS/32_stroke_lines-FLOATING-CARRIER-DRAWS-BUT-STACKS-2050-f1x.md."),
        "caveat": ("THIS ONE IS CONTESTED IN THE REPO'S OWN DATA. verify_google.py:_rule_segments "
                   "reads pictures=True for check 32, because Google exports an anchored shape as a "
                   "raster image at the shape's own geometry - and on 22 Nov that reading took 16 "
                   "documents from FAIL to 42/42 (32_stroke_lines-CHECK-BLIND-TO-RASTERISED-RULES-"
                   "MEASURED-0610-f1x.md). So a floating drawing rule is found by the check whenever "
                   "Google rasterises it, and this repro then PASSES. It reproduces the failure only "
                   "if Google drops the shape rather than rasterising it, which is document- "
                   "dependent and which nothing in this sandbox can decide. Committed data: 182 of "
                   "191 scored documents pass 32, and 163 of those carry w:drawing - so 'carries a "
                   "drawing' is not sufficient for the failure at the document level."),
        "rules_expected": 1,
    },
    {
        "check": "32_stroke_lines",
        "variant": "cell-border-rule",
        "body": body_32_border,
        "construct": "a rule as a table cell's w:top border (w:val=\"single\"), one side only",
        "path": "w:document/w:body/w:tbl/w:tr/w:tc/w:tcPr/w:tcBorders/w:top",
        "count_key": None,
        "expect": "one table, one row, one cell, one border edge; no w:drawing anywhere",
        "law": ("The two documents that pass 32_stroke_lines carry the rule as a table-cell border "
                "(google_safe.py --predict); FINDINGS/32_stroke_lines-CELL-BORDER-HONOURED-1830-f1x.md "
                "measured Google honouring w:tcBorders."),
        "caveat": ("This is the CONTROL half of the pair, not a failure. It is the shape a patch is "
                   "supposed to move the drawing variant towards, and it should PASS. If it fails, "
                   "the construct is not honoured by whichever renderer dropped it, and the pair "
                   "proves nothing."),
        "rules_expected": 1,
    },
    {
        "check": "04_chars_missing",
        "variant": "anchored-textbox",
        "body": body_04,
        "construct": "one paragraph of text inside an anchored text box (wps:txbx)",
        "path": "w:document/w:body/w:p[2]/w:r/w:drawing/wp:anchor/a:graphic/.../wps:txbx/w:txbxContent/w:p",
        "count_key": "wp:anchor",
        "expect": "one wp:anchor, one w:drawing, exactly one paragraph inside the box",
        "law": ("Google rasterises every anchored text box on import; 194 of 213 documents carry "
                "them (13058 instances) and this is 166 failures across 04_chars_missing, "
                "45_char_accuracy, 13_text_colours, 44_header_footer, 17_matched_runs."),
        "caveat": ("04_chars_missing is a character multiset test with zero tolerance, so it fires on "
                   "ANY character the render lacks. That makes it easy to reproduce and easy to "
                   "reproduce BY ACCIDENT: any defect that loses one glyph anywhere also fires it, "
                   "and a patch 'fixed' against this repro would only be shown not to lose this one "
                   "glyph. The box's text also has to survive LibreOffice's own text layer for the "
                   "reference side to be right, and that is renderer-specific."),
        "marker": "TXBXMARK", "marker_page": 0,
    },
]


# ---- verification ------------------------------------------------------------------------------

def scan(path):
    """google_safe.py's own scan(), imported rather than re-implemented."""
    sys.path.insert(0, HERE)
    import google_safe
    return google_safe.scan(path)


def structural(path):
    """Everything that can be checked without a renderer: it opens, it parses, the construct counts."""
    out = {"opens": False, "xml_parses": False, "python_docx": None}
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            x = z.read("word/document.xml").decode("utf-8")
        out["opens"] = True
        out["parts"] = names
        import xml.dom.minidom
        xml.dom.minidom.parseString(x)
        out["xml_parses"] = True
        out["bytes"] = len(x)
        out["text_units"] = x.count("<w:t ")
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
    try:
        import docx
        d = docx.Document(path)
        out["python_docx"] = "%d paragraph(s), %d table(s)" % (len(d.paragraphs), len(d.tables))
    except Exception as e:
        out["python_docx"] = "FAILED %s: %s" % (type(e).__name__, e)
    return out


def construct_count(path, repro):
    """The single number a human checks for minimality: how many times the construct appears."""
    with zipfile.ZipFile(path) as z:
        x = z.read("word/document.xml").decode("utf-8")
    if repro["check"] == "18_displacement":
        return x.count('w:before="'), "w:before attributes"
    if repro["variant"] == "drawing-rule":
        return x.count("<w:drawing>"), "w:drawing elements"
    if repro["variant"] == "cell-border-rule":
        return x.count("<w:tcBorders>"), "w:tcBorders blocks (%d edge(s) inside)" % x.count('w:val="single"')
    if repro["variant"] == "anchored-textbox":
        return x.count("<w:txbxContent>"), "text-box bodies"
    return 0, "?"


def render(path, outdir):
    """soffice -> PDF. The only renderer in this sandbox; Google Docs is not reachable."""
    os.makedirs(outdir, exist_ok=True)
    r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, path],
                       capture_output=True, text=True, timeout=180)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + ".pdf")
    return pdf if os.path.exists(pdf) else None


def measure(repro, pdf):
    """What the reference renderer did with the construct. This is the half that CAN be measured."""
    import pymupdf
    doc = pymupdf.open(pdf)
    m = {"pages": doc.page_count}
    if repro["check"] == "18_displacement":
        page = doc[repro["marker_page"]]
        hits = page.search_for(repro["marker"])
        m["marker_y_pt"] = round(hits[0].y0, 2) if hits else None
        m["asked_pt"] = 55.15
    elif repro["check"] == "32_stroke_lines":
        sys.path.insert(0, HERE)
        import verify_google as vg
        pages = [doc[i] for i in range(doc.page_count)]
        rules = vg._doc_rules(pages, isolated=True)
        m["isolated_rules"] = len(rules)
        m["rule_geometry"] = [{"page": r["page"], "o": r["o"], "perp": round(r["perp"], 2),
                               "len": round(r["b"] - r["a"], 2), "t": round(r["t"], 2)} for r in rules]
    elif repro["check"] == "04_chars_missing":
        text = "".join(doc[i].get_text() for i in range(doc.page_count))
        m["marker_in_text_layer"] = repro["marker"] in text
        m["text_len"] = len(text)
    return m


def simulate(repro, real_pdf, neutral_pdf):
    """Score (real render, neutralised render) with verify_google.py. A SIMULATION, not a measurement.

    The neutralised render stands in for Google's export, and it stands in only for the ONE thing
    Google is measured to do to this construct. Every other check in the 42 is therefore reading a
    LibreOffice render and its verdict means nothing here; only the target check's verdict does.
    """
    sys.path.insert(0, HERE)
    import verify_google as vg
    res = {}
    for label, gd in (("control: real vs real", real_pdf), ("simulated: real vs neutralised", neutral_pdf)):
        try:
            r = vg.compare(real_pdf, gd)
            chk = r["checks"].get(repro["check"]) or {}
            res[label] = {"passed": r["passed"], "total": r["total"],
                          "target_failed": repro["check"] in (r.get("failed") or []),
                          "target": {"source": chk.get("source"), "render": chk.get("render"),
                                     "ok": chk.get("ok")},
                          "failed": r.get("failed")}
        except Exception as e:
            res[label] = {"error": "%s: %s" % (type(e).__name__, e)}
    return res


def emit(repro, outdir, do_render, do_simulate):
    stem = "%s--%s" % (repro["check"], repro["variant"])
    path = os.path.join(outdir, stem + ".docx")
    body = doc(repro["body"](False))
    write_docx(path, body)
    print("=" * 78)
    print("  %s  /  %s" % (repro["check"], repro["variant"]))
    print("=" * 78)
    print("  file        %s" % path)
    print("  construct   %s" % repro["construct"])
    print("  element     %s" % repro["path"])
    print("  law         %s" % repro["law"])
    print()
    print("  OOXML emitted, verbatim:")
    print()
    for line in body.replace("><", ">\n<").split("\n"):
        print("    " + line)
    print()

    n, unit = construct_count(path, repro)
    print("  CONSTRUCT COUNT  %d  (%s)" % (n, unit))
    print("  expected         %s" % repro["expect"])
    print()

    st = structural(path)
    print("  structural       opens=%s  xml_parses=%s  python-docx: %s  (%d bytes of document.xml)"
          % (st.get("opens"), st.get("xml_parses"), st.get("python_docx"), st.get("bytes", 0)))
    if st.get("error"):
        print("  STRUCTURAL FAILURE %s" % st["error"])
    sc = scan(path)
    print("  google_safe.scan()  %s" % (json.dumps(sc, sort_keys=True) if sc else "clean - no known-ignored construct"))
    if repro["count_key"]:
        got = sc.get(repro["count_key"])
        print("  scan counts %-18s %s" % (repro["count_key"], got))
    else:
        print("  scan counts w:drawing/wp:anchor   %s / %s  (must be absent: this is the control)"
              % (sc.get("w:drawing"), sc.get("wp:anchor")))
    print()

    out = {"path": path, "construct_count": n, "scan": sc, "structural": st}
    if do_render:
        pdf = render(path, os.path.join(outdir, "pdf"))
        if not pdf:
            print("  render           FAILED - soffice produced no PDF")
            out["render"] = None
        else:
            m = measure(repro, pdf)
            print("  LibreOffice      %s" % pdf)
            for k, v in m.items():
                print("    %-22s %s" % (k, v))
            out["render"] = m
            out["pdf"] = pdf
            if do_simulate:
                npath = os.path.join(outdir, stem + "--neutralised.docx")
                write_docx(npath, doc(repro["body"](True)))
                npdf = render(npath, os.path.join(outdir, "pdf"))
                if npdf:
                    s = simulate(repro, pdf, npdf)
                    print("  SIMULATION (not a Google measurement):")
                    for k, v in s.items():
                        print("    %-34s %s" % (k, json.dumps(v)))
                    out["simulation"] = s
                else:
                    print("  simulation       skipped - neutralised variant did not render")
    print()
    print("  NOT VERIFIED: whether Google Docs actually fails on this file. This tool has no Google")
    print("  access. Everything above is structural or LibreOffice.")
    print("  CAVEAT: %s" % repro["caveat"])
    print()
    return out


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check")
    ap.add_argument("--variant")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="/scratch/work/repro")
    ap.add_argument("--render", action="store_true", help="render with LibreOffice and measure")
    ap.add_argument("--simulate", action="store_true", help="score a simulated Google render (implies --render)")
    ap.add_argument("--json")
    a = ap.parse_args(argv)

    if a.list:
        print("  %-18s %-20s %s" % ("check", "variant", "construct"))
        for r in REPROS:
            print("  %-18s %-20s %s" % (r["check"], r["variant"], r["construct"]))
        return 0

    todo = REPROS
    if a.check:
        todo = [r for r in todo if r["check"] == a.check]
        if not todo:
            print("  no repro for %s - known: %s"
                  % (a.check, ", ".join(sorted(set(r["check"] for r in REPROS)))), file=sys.stderr)
            return 3
    if a.variant:
        todo = [r for r in todo if r["variant"] == a.variant]
        if not todo:
            print("  no variant %s" % a.variant, file=sys.stderr)
            return 3
    if not (a.check or a.all):
        print(__doc__.strip().split("\n\n")[0])
        print("  --list, --check <id>, --all.  Add --render and --simulate to measure.")
        return 2

    os.makedirs(a.out, exist_ok=True)
    results = [emit(r, a.out, a.render or a.simulate, a.simulate) for r in todo]
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        json.dump({"at": "minimal-repro", "repros": results}, open(a.json, "w"), indent=1)
        print("  written to %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
