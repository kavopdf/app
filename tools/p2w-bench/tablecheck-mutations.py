"""Mutation matrix for the table-geometry checks 61-65.

For each mutation: take a .docx whose grid the checks PASS, corrupt exactly one thing
in the OOXML table model, and ask which of 61-65 fire. A check that cannot be made to
fail is not a check; a check that fires on the untouched file is worse than useless.

The control row is the untouched file: it must pass all five, or every other row is
measuring the harness.
"""
import io
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tablechecks as TC

WORK = os.environ.get("P2W_MUT_DIR", "/tmp/p2w-mut")
DOCX = "word/document.xml"


def _read(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read(DOCX).decode("utf-8")
        names = z.namelist()
    return xml, names


def _write(src, dst, xml):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in zin.namelist():
            data = zin.read(n)
            if n == DOCX:
                data = xml.encode("utf-8")
            zout.writestr(n, data)


def _first_table(xml):
    i = xml.find("<w:tbl>")
    j = xml.find("</w:tbl>", i)
    return i, j + len("</w:tbl>")


def _rows(tbl):
    return [(m.start(), m.end()) for m in re.finditer(r"<w:tr>.*?</w:tr>", tbl, re.S)]


def _cells(tr):
    return [(m.start(), m.end()) for m in re.finditer(r"<w:tc>.*?</w:tc>", tr, re.S)]


# ---- the mutations -------------------------------------------------------

def m_span_shrink(xml):
    """A merged cell declares one column too few: gridSpan 3 -> 2."""
    i, j = _first_table(xml)
    t = xml[i:j]
    m = re.search(r'<w:gridSpan w:val="(\d+)"/>', t)
    if not m or int(m.group(1)) < 2:
        return None
    n = int(m.group(1))
    t2 = t[:m.start()] + '<w:gridSpan w:val="%d"/>' % (n - 1) + t[m.end():]
    return xml[:i] + t2 + xml[j:]


def m_span_weld(xml):
    """A cell that is one column claims two: gridSpan absent -> val=2."""
    i, j = _first_table(xml)
    t = xml[i:j]
    rows = _rows(t)
    if len(rows) < 2:
        return None
    a, b = rows[1]
    tr = t[a:b]
    cells = _cells(tr)
    if len(cells) < 3:
        return None
    ca, cb = cells[1]                    # a middle cell, not the last
    tc = tr[ca:cb]
    if "gridSpan" in tc:
        return None
    tc2 = tc.replace("<w:tcPr>", '<w:tcPr><w:gridSpan w:val="2"/>', 1)
    tr2 = tr[:ca] + tc2 + tr[cb:]
    t2 = t[:a] + tr2 + t[b:]
    return xml[:i] + t2 + xml[j:]


def m_col_drop(xml):
    """The grid loses a column: one w:gridCol deleted."""
    i, j = _first_table(xml)
    t = xml[i:j]
    m = re.search(r'<w:gridCol w:w="\d+"/>', t)
    if not m:
        return None
    t2 = t[:m.start()] + t[m.end():]
    return xml[:i] + t2 + xml[j:]


def m_col_add(xml):
    """The grid gains a column nothing occupies."""
    i, j = _first_table(xml)
    t = xml[i:j]
    m = re.search(r'<w:gridCol w:w="(\d+)"/>', t)
    if not m:
        return None
    t2 = t[:m.end()] + '<w:gridCol w:w="%s"/>' % m.group(1) + t[m.end():]
    return xml[:i] + t2 + xml[j:]


def m_row_drop(xml):
    """The table loses a row."""
    i, j = _first_table(xml)
    t = xml[i:j]
    rows = _rows(t)
    if len(rows) < 3:
        return None
    a, b = rows[1]
    t2 = t[:a] + t[b:]
    return xml[:i] + t2 + xml[j:]


def m_row_add(xml):
    """A row is duplicated."""
    i, j = _first_table(xml)
    t = xml[i:j]
    rows = _rows(t)
    if len(rows) < 2:
        return None
    a, b = rows[0]
    t2 = t[:b] + t[a:b] + t[b:]
    return xml[:i] + t2 + xml[j:]


def m_vmerge_false(xml):
    """Two stacked cells are declared one vertically merged cell the page never drew."""
    i, j = _first_table(xml)
    t = xml[i:j]
    rows = _rows(t)
    if len(rows) < 2:
        return None
    (a0, b0), (a1, b1) = rows[0], rows[1]
    out = t
    # second row first, so the first insertion does not shift the second's offsets
    for (a, b), tag in (((a1, b1), "<w:vMerge/>"),
                        ((a0, b0), '<w:vMerge w:val="restart"/>')):
        tr = out[a:b]
        cells = _cells(tr)
        if not cells:
            return None
        ca, cb = cells[0]
        tc = tr[ca:cb]
        tc2 = tc.replace("<w:tcPr>", "<w:tcPr>" + tag, 1)
        tr2 = tr[:ca] + tc2 + tr[cb:]
        out = out[:a] + tr2 + out[b:]
    return xml[:i] + out + xml[j:]


def m_width_shift(xml):
    """One column is 10 pt wider than the page's."""
    i, j = _first_table(xml)
    t = xml[i:j]
    m = re.search(r'<w:gridCol w:w="(\d+)"/>', t)
    if not m:
        return None
    w = int(m.group(1)) + 200           # 200 twips = 10 pt
    t2 = t[:m.start()] + '<w:gridCol w:w="%d"/>' % w + t[m.end():]
    return xml[:i] + t2 + xml[j:]


def m_span_weld_any(xml):
    """A one-column cell claims two: the FIRST PLAIN cell of row 1, whatever its index.

    `m_span_weld` above insists on the cell at index 1 and returns None when that cell
    already carries a gridSpan. On the fixed engine every row of
    `two-tables-stacked-with-no-gap` has a 3-column span in that position, so the weld
    case silently reported "not applicable" on the primary base and was only ever
    exercised on the second one. This row closes that hole: same defect, any position.
    """
    i, j = _first_table(xml)
    t = xml[i:j]
    rows = _rows(t)
    if len(rows) < 2:
        return None
    a, b = rows[1]
    tr = t[a:b]
    cells = _cells(tr)
    pick = None
    for ca, cb in cells:
        if "gridSpan" not in tr[ca:cb]:
            pick = (ca, cb)
            break
    if pick is None:
        return None
    ca, cb = pick
    tc2 = tr[ca:cb].replace("<w:tcPr>", '<w:tcPr><w:gridSpan w:val="2"/>', 1)
    tr2 = tr[:ca] + tc2 + tr[cb:]
    t2 = t[:a] + tr2 + t[b:]
    return xml[:i] + t2 + xml[j:]


MUTATIONS = [
    ("control (no change)", None),
    ("span_shrink  gridSpan 3->2", m_span_shrink),
    ("span_weld    absent->2", m_span_weld),
    ("col_drop     -1 gridCol", m_col_drop),
    ("col_add      +1 gridCol", m_col_add),
    ("row_drop     -1 w:tr", m_row_drop),
    ("row_add      +1 w:tr", m_row_add),
    ("vmerge_false restart/continue", m_vmerge_false),
    ("width_shift  +10 pt gridCol", m_width_shift),
    ("span_weld_any 1st plain cell", m_span_weld_any),
]


def run(stem, side="fix"):
    root = os.environ.get("P2W_RUN", "/scratch/work")
    src = os.path.join(root, "corpus", "flat", "%s.pdf" % stem)
    docx = os.path.join(root, "run", side, "out1", "%s.docx" % stem)
    os.makedirs(WORK, exist_ok=True)
    xml, _ = _read(docx)
    base = TC.checks_for(src, docx)
    print("\n### %s  (%s side)" % (stem, side))
    print("   base verdicts: %s" % {k: v[2] for k, v in sorted(base.items())})
    rows = []
    for name, fn in MUTATIONS:
        if fn is None:
            path = docx
            note = ""
        else:
            m = fn(xml)
            if m is None:
                print("   %-34s SKIPPED (mutation not applicable)" % name)
                continue
            path = os.path.join(WORK, "%s__%s.docx" % (stem, re.sub(r"\W+", "_", name)))
            _write(docx, path, m)
            note = ""
        got = TC.checks_for(src, path)
        fired = sorted(k for k in got if not got[k][2])
        # a check that ABSTAINS is not a pass and not a failure - report it
        absent = sorted(set(TC.CHECKS) - set(got))
        rows.append((name, fired, absent))
        print("   %-34s fires: %-58s abstains: %s"
              % (name, ", ".join(fired) if fired else "none", ",".join(absent) or "-"))
    return rows


if __name__ == "__main__":
    for stem in ("two-tables-stacked-with-no-gap", "very-long-single-column-table"):
        run(stem)
