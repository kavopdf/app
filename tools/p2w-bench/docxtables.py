"""Read the TABLE MODEL out of a .docx - the thing the 43 checks never open.

What a Word table actually says about geometry:

  w:tblGrid/w:gridCol   the table's COLUMNS and each one's width (twips)
  w:tr                  a row
  w:tc                  a cell
  w:gridSpan w:val=N    this cell covers N grid columns  -> a horizontal merge
  w:vMerge              w:val="restart" opens a vertical merge, w:val="continue"
                        (or no val) is a cell the merge swallows
  w:tcW w:w=N           this cell's own width (twips)

A row's cells, once you expand gridSpan, must sum to the grid's column count. That is
the invariant a merged table has to satisfy, and it is exactly the invariant a table
built by welding a merged cell into one narrow slot violates.
"""
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TWIPS_PER_PT = 20.0


def _text(el):
    out = []
    for t in el.iter(W + "t"):
        if t.text:
            out.append(t.text)
    return "".join(out)


def _int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def read_tables(path):
    """Every table in the document body, in document order.

    Each: {
      'grid': [width_tw, ...],            # w:gridCol widths, in twips
      'ncol': len(grid),
      'rows': [ [cell, ...], ... ],       # cells AFTER gridSpan expansion is NOT done;
                                          # one entry per w:tc, in order
      'nrow': len(rows),
      'text': '...',                      # all cell text, for matching to the page
      'nested': bool,                     # this table sits inside a cell of another
    }
    cell: {'span': gridSpan (1 if absent), 'vm': None|'restart'|'continue',
           'tw': tcW in twips or None, 'text': str}
    """
    with zipfile.ZipFile(path) as z:
        try:
            xml = z.read("word/document.xml")
        except KeyError:
            return []
    root = ET.fromstring(xml)
    body = root.find(W + "body")
    if body is None:
        return []
    out = []

    def walk(el, nested):
        for child in el:
            tag = child.tag
            if tag == W + "tbl":
                out.append(_table(child, nested))
                walk(child, True)
            elif tag == W + "tr":
                walk(child, nested)
            elif tag == W + "tc":
                walk(child, nested)
            elif tag in (W + "sdt", W + "sdtContent"):
                walk(child, nested)

    walk(body, False)
    return out


def _table(tbl, nested):
    grid = []
    g = tbl.find(W + "tblGrid")
    if g is not None:
        for gc in g.findall(W + "gridCol"):
            grid.append(_int(gc.get(W + "w")))
    rows = []
    for tr in tbl.findall(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            pr = tc.find(W + "tcPr")
            span, vm, tw = 1, None, None
            if pr is not None:
                gs = pr.find(W + "gridSpan")
                if gs is not None:
                    span = max(1, _int(gs.get(W + "val"), 1))
                v = pr.find(W + "vMerge")
                if v is not None:
                    val = v.get(W + "val")
                    vm = "continue" if val in (None, "continue") else "restart"
                w = pr.find(W + "tcW")
                if w is not None:
                    tw = _int(w.get(W + "w"), 0)
            cells.append({"span": span, "vm": vm, "tw": tw, "text": _text(tc)})
        if cells:
            rows.append(cells)
    text = " ".join(c["text"] for r in rows for c in r)
    return {"grid": grid, "ncol": len(grid), "rows": rows, "nrow": len(rows),
            "text": text, "nested": nested}


def expand_rows(t):
    """The grid a reader SEES: one entry per grid column per row.

    Returns (occupancy, ncol_seen) where occupancy[r][c] is
    None for a slot covered by a merge, or the index of the cell that owns it.
    Also returns a list of problems - the invariants a real table must keep.
    """
    ncol = t["ncol"]
    occ = []
    problems = []
    open_v = {}          # column -> True while a vMerge restart is open above
    for r, row in enumerate(t["rows"]):
        line = [None] * max(ncol, 1)
        c = 0
        for ci, cell in enumerate(row):
            span = cell["span"]
            if cell["vm"] == "continue":
                # a continuation cell must sit where a restart is open
                if not open_v.get(c):
                    problems.append("row %d cell %d: vMerge continue with no restart above"
                                    % (r, ci))
                open_v[c] = True
            elif cell["vm"] == "restart":
                open_v[c] = True
            else:
                open_v[c] = False
            for k in range(span):
                if c + k < len(line):
                    line[c + k] = ci
            c += span
        if ncol and c != ncol:
            problems.append("row %d: cells span %d columns, grid has %d"
                            % (r, c, ncol))
        occ.append(line)
    return occ, ncol, problems
