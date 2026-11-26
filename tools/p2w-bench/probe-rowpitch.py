#!/usr/bin/env python3
"""probe-rowpitch.py - ask Google and LibreOffice the same question about one construct.

WHY THIS EXISTS. Every earlier attempt at 18_displacement was steered by a number the checker
reported and a renderer it could not see. Google's side is 4 MCP calls away and LibreOffice is
one `soffice` away, so a construct can be measured on BOTH in about two minutes. This builds a
single .docx holding one table per variant, so ONE upload answers every variant at once.

    python3 tools/p2w-bench/probe-rowpitch.py --build          # writes /scratch/output/probe-rowpitch.docx
    #   upload it, CREATE_FILE as a Google Doc, EXPORT to pdf, then:
    python3 tools/p2w-bench/probe-rowpitch.py --measure <google.pdf> [<lo.pdf>]

--measure prints, per variant, the row pitch in each renderer. `--build` also renders the
LibreOffice side locally so the LO column is free.

WHAT IT FOUND (27 Nov 2026): a ruled row is `trHeight + 0.75 pt` in Google and `trHeight` in
LibreOffice. `hRule` makes no difference, and moving the rule from insideH to the cells' bottom
border makes no difference. See FINDINGS/18-displacement-RULED-ROW-PITCH-IS-GOOGLE-ONLY-27NOV-fixer.md.

The variants are deliberately redundant: V1/V5/V6 separate hRule from the rule, V2/V4 separate
"no borders" from "outer box only", V8/V9 separate WHERE the rule is written from WHETHER it is
written. If you add a variant, add one that could prove the current law wrong.
"""
import argparse, os, subprocess, sys

OUT = "/scratch/output/probe-rowpitch.docx"
WORK = "/scratch/work/probe-rowpitch"
HEAD = 11.0   # cell paragraph line, pt - matches 303_discharge_summary's before=209 line=11

ALL6 = ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']
OUTER = ['top', 'left', 'bottom', 'right']
INNER = ['left', 'right', 'insideH', 'insideV']


def build():
    from docx import Document
    from docx.shared import Pt
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    def set_borders(parent, edges, sz=3, tag='w:tblBorders'):
        for old in parent.findall(qn(tag)):
            parent.remove(old)
        b = OxmlElement(tag)
        for edge in edges:
            e = OxmlElement('w:' + edge)
            e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz))
            e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000')
            b.append(e)
        parent.append(b)

    def variant(doc, title, edges, tw, rule, cell_edges=None):
        doc.add_paragraph(title)
        t = doc.add_table(rows=5, cols=2)
        t.autofit = False
        tblPr = t._tbl.tblPr
        set_borders(tblPr, edges)
        m = OxmlElement('w:tblCellMar')
        for edge in ['top', 'left', 'bottom', 'right']:
            e = OxmlElement('w:' + edge); e.set(qn('w:w'), '0'); e.set(qn('w:type'), 'dxa'); m.append(e)
        tblPr.append(m)
        for r in range(5):
            trPr = t.rows[r]._tr.get_or_add_trPr()
            h = OxmlElement('w:trHeight'); h.set(qn('w:val'), str(tw)); h.set(qn('w:hRule'), rule)
            trPr.append(h)
            for c in range(2):
                cell = t.rows[r].cells[c]
                if cell_edges is not None:
                    set_borders(cell._tc.get_or_add_tcPr(), cell_edges(r), tag='w:tcBorders')
                par = cell.paragraphs[0]
                par.paragraph_format.space_before = Pt(0)
                par.paragraph_format.space_after = Pt(0)
                par.paragraph_format.line_spacing = Pt(HEAD)
                run = par.add_run("R%dC%d" % (r, c)); run.font.size = Pt(8)

    doc = Document()
    variant(doc, "V1 all6 atLeast300", ALL6, 300, 'atLeast')
    variant(doc, "V2 noborder atLeast300", [], 300, 'atLeast')
    variant(doc, "V3 all6 atLeast285", ALL6, 285, 'atLeast')
    variant(doc, "V4 outerbox atLeast300", OUTER, 300, 'atLeast')
    variant(doc, "V5 all6 exact300", ALL6, 300, 'exact')
    variant(doc, "V6 all6 exact315", ALL6, 315, 'exact')
    variant(doc, "V8 inner atLeast300", INNER, 300, 'atLeast')
    variant(doc, "V9 cellrules atLeast300", ['left', 'right'], 300, 'atLeast',
            cell_edges=lambda r: (['top'] if r == 0 else []) + ['bottom'])
    os.makedirs("/scratch/output", exist_ok=True)
    doc.save(OUT)
    print("wrote", OUT)
    print("now: upload -> CREATE_FILE (google-apps.document) -> EXPORT pdf -> --measure <that.pdf>")

    os.makedirs(WORK, exist_ok=True)
    subprocess.run(["cp", OUT, WORK + "/probe.docx"], check=False)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "probe.docx"],
                   cwd=WORK, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lo = WORK + "/probe.pdf"
    if os.path.exists(lo):
        print("\nLibreOffice side (free, local):")
        measure(lo)


def measure(path):
    import pymupdf
    d = pymupdf.open(path)
    p = d[0]
    # R1C0 is NOT a row pitch: it is the distance from the variant's title paragraph to the
    # table's first row, which moves with the border above it. The row pitch is R2C0..R4C0.
    prev = None
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            y = l["spans"][0]["origin"][1]
            if t.startswith("V") and t[1:2].isdigit():
                prev = None
                print("  " + t)
            elif t.startswith("R") and t.endswith("C0"):
                if prev is not None and not t.startswith("R1"):
                    print("     %s pitch=%6.2f" % (t, y - prev))
                prev = y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--measure", nargs="*", default=None)
    a = ap.parse_args()
    if a.build:
        build()
    if a.measure:
        for f in a.measure:
            print("==", f)
            measure(f)
    if not a.build and not a.measure:
        ap.print_help()


if __name__ == "__main__":
    main()
