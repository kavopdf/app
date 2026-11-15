"""Reconstruct a page's TABLE GRID from the rules it draws.

The question this answers is the one the 43 checks never ask: what grid did the PAGE
draw? Not "is there ink", not "do the rules survive" - the geometry: how many columns,
how many rows, where each boundary is, and which cells are MERGED (one cell covering
several slots) because the page drew no interior rule there.

Method:

  1. Collect the page's thin straight segments (horizontal and vertical).
  2. Group segments into TABLES by CONNECTIVITY: two segments are in the same table
     when they touch or cross. A ruled table's borders all meet each other; two
     tables that do not touch are two tables. (This is the same grouping the engine's
     own cellsToTables does with shared corners, and it is why clustering all the
     page's lines into one global X/Y lattice is wrong: on a page with a header rule
     and a footer rule that lattice chains two tables into one.)
  3. For a table, the distinct vertical rules give the COLUMN BOUNDARIES X, the
     distinct horizontal rules the ROW BOUNDARIES Y.
  4. Slot (i,j) is bounded by Y[i],Y[i+1],X[j],X[j+1]. A boundary between two adjacent
     slots EXISTS only where the page drew a rule covering that slot's span. Slots with
     no rule between them are ONE CELL.
  5. A cell's spanC/spanR are the number of slots it covers.

Step 4 is the whole point. A merged cell is a cell the page did not divide, and the
only evidence of the division is the rule. Reading it off the rules is reading the
page; reading it off the text extent (which is what the engine does today) is a guess.
"""

TOL = 1.6          # two rules within this are the same boundary line
MIN_LEN = 6.0      # a segment shorter than this is a tick, not a boundary
MAX_THICK = 2.5    # a boundary is a thin rule; a filled band is not a cell edge
TOUCH = 2.5        # two segments this close abut / meet
MIN_COL = 6.0      # a slot narrower than this is not a column - the engine's
                   # own floor in tableFromCells (nextX - C.get(c) < 6f)
MIN_ROW = 2.0      # ... nor this a row


def _paints(col, alpha):
    if col is None:
        return False
    try:
        if alpha is not None and alpha < 0.10:
            return False
    except TypeError:
        pass
    if isinstance(col, (int, float)):
        return True
    try:
        if len(col) == 4:                      # CMYK: all-zero is white paper
            return not all(abs(v) < 0.02 for v in col)
        return len(col) in (1, 3)
    except TypeError:
        return True


def _segments(page):
    """Thin straight axis-aligned segments: {'o','perp','a','b'}."""
    out = []
    for d in page.get_drawings():
        w = d.get("width")
        col = d.get("color")
        fill = d.get("fill")
        s_op = d.get("stroke_opacity")
        f_op = d.get("fill_opacity")
        stroked = col is not None and w is not None and _paints(col, s_op)
        filled = fill is not None and _paints(fill, f_op)
        t_s = max(0.05, float(w)) if w is not None else 0.05
        if filled and not stroked:
            r = d["rect"]
            h, wd = r.height, r.width
            if h <= MAX_THICK and wd > h and wd >= MIN_LEN:
                out.append({"o": "h", "perp": (r.y0 + r.y1) / 2.0, "a": r.x0, "b": r.x1})
            elif wd <= MAX_THICK and h > wd and h >= MIN_LEN:
                out.append({"o": "v", "perp": (r.x0 + r.x1) / 2.0, "a": r.y0, "b": r.y1})
            continue
        if t_s > MAX_THICK:
            continue
        for item in d.get("items", []):
            kind = item[0]
            if kind == "l":
                if not stroked:
                    continue
                p1, p2 = item[1], item[2]
                dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
                if dy <= 0.8 and dx >= MIN_LEN:
                    out.append({"o": "h", "perp": (p1.y + p2.y) / 2.0,
                                "a": min(p1.x, p2.x), "b": max(p1.x, p2.x)})
                elif dx <= 0.8 and dy >= MIN_LEN:
                    out.append({"o": "v", "perp": (p1.x + p2.x) / 2.0,
                                "a": min(p1.y, p2.y), "b": max(p1.y, p2.y)})
            elif kind in ("re", "qu"):
                if not stroked:
                    continue
                rr = item[1] if kind == "re" else item[1].rect
                for perp, a, b, o in ((rr.y0, rr.x0, rr.x1, "h"),
                                      (rr.y1, rr.x0, rr.x1, "h"),
                                      (rr.x0, rr.y0, rr.y1, "v"),
                                      (rr.x1, rr.y0, rr.y1, "v")):
                    if b - a >= MIN_LEN:
                        out.append({"o": o, "perp": perp, "a": a, "b": b})
    return out


def _adjacent(s, t):
    """Do two segments touch or cross?"""
    if s["o"] == t["o"]:
        if abs(s["perp"] - t["perp"]) > TOUCH:
            return False
        return not (s["b"] < t["a"] - TOUCH or t["b"] < s["a"] - TOUCH)
    h, v = (s, t) if s["o"] == "h" else (t, s)
    return (h["a"] - TOUCH <= v["perp"] <= h["b"] + TOUCH
            and v["a"] - TOUCH <= h["perp"] <= v["b"] + TOUCH)


def _components(segs):
    n = len(segs)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[a] = b

    hs = [i for i in range(n) if segs[i]["o"] == "h"]
    vs = [i for i in range(n) if segs[i]["o"] == "v"]
    for i in hs:
        for j in hs:
            if i < j and _adjacent(segs[i], segs[j]):
                union(i, j)
    for i in vs:
        for j in vs:
            if i < j and _adjacent(segs[i], segs[j]):
                union(i, j)
    for i in hs:
        for j in vs:
            if _adjacent(segs[i], segs[j]):
                union(i, j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [groups[k] for k in groups]


def _cluster_axis(vals, tol=TOL):
    """Sorted cluster centres of a list of coordinates."""
    if not vals:
        return []
    vals = sorted(vals)
    out = [[vals[0]]]
    for v in vals[1:]:
        if abs(v - out[-1][-1]) <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(g) / len(g) for g in out]


def _covers(spans, lo, hi, need=0.7):
    for a, b in spans:
        ov = min(b, hi) - max(a, lo)
        if ov > 0 and ov >= need * max(1e-6, hi - lo):
            return True
    return False


def _table_from(segs, idxs):
    """One connected component -> a grid, or None."""
    sub = [segs[i] for i in idxs]
    vlines = _cluster_axis([s["perp"] for s in sub if s["o"] == "v"])
    hlines = _cluster_axis([s["perp"] for s in sub if s["o"] == "h"])
    if len(vlines) < 2 or len(hlines) < 2:
        return None
    # Drop columns / rows too narrow to be real.
    def thin(xs):
        keep = [xs[0]]
        for x in xs[1:]:
            if x - keep[-1] >= MIN_COL:
                keep.append(x)
        return keep
    vlines = thin(vlines)
    hlines = thin(hlines)
    if len(vlines) < 2 or len(hlines) < 2:
        return None

    def spans_at(orient, coord):
        out = []
        for s in sub:
            if s["o"] == orient and abs(s["perp"] - coord) <= TOL:
                out.append((s["a"], s["b"]))
        return out

    nr, nc = len(hlines) - 1, len(vlines) - 1
    # The engine's own definition of a table: tableFromCells rejects ncol < 2 and
    # nrow < 1. A single-column framed box is a box, not a grid - reading it as a
    # table is how a rotated stamp's own frame got paired with an invoice.
    if nc < 2 or nr < 1:
        return None
    # vwall[r][j]: is there a rule at x=vlines[j] across row r?
    vwall = [[_covers(spans_at("v", vlines[j]), hlines[r], hlines[r + 1])
              for j in range(nc + 1)] for r in range(nr)]
    hwall = [[_covers(spans_at("h", hlines[i]), vlines[c], vlines[c + 1])
              for c in range(nc)] for i in range(nr + 1)]

    parent = list(range(nr * nc))

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for r in range(nr):
        for c in range(nc):
            k = r * nc + c
            if c + 1 < nc and not vwall[r][c + 1]:
                union(k, k + 1)
            if r + 1 < nr and not hwall[r + 1][c]:
                union(k, k + nc)

    boxes = {}
    for r in range(nr):
        for c in range(nc):
            root = find(r * nc + c)
            b = boxes.get(root)
            if b is None:
                boxes[root] = [r, c, r, c]
            else:
                b[0] = min(b[0], r); b[1] = min(b[1], c)
                b[2] = max(b[2], r); b[3] = max(b[3], c)
    cells = [{"r0": b[0], "c0": b[1], "r1": b[2], "c1": b[3]}
             for b in boxes.values()]
    cells.sort(key=lambda x: (x["r0"], x["c0"]))
    # IS THIS A TABLE, OR A DRAWING? A ruled table's interior boundaries run the
    # table's own height (a column separator) and width (a row separator). An org
    # chart, a CAD sheet or a BOM drawing is a pile of boxes whose edges sit at many
    # x and stop where the box stops - no interior line spans the figure. Measured:
    # without this gate the org chart reads as a 17-column table and the CAD sheet as
    # a 4-column one, and a check that fails an org chart for having the wrong column
    # count is measuring the instrument, not the engine.
    H = hlines[-1] - hlines[0]
    W = vlines[-1] - vlines[0]
    vcov, hcov = [], []
    for j in range(1, nc):
        sp = spans_at("v", vlines[j])
        cov = sum(max(0.0, min(b, hlines[-1]) - max(a, hlines[0])) for a, b in sp)
        vcov.append(min(1.0, cov / H) if H > 0 else 0.0)
    for i in range(1, nr):
        sp = spans_at("h", hlines[i])
        cov = sum(max(0.0, min(b, vlines[-1]) - max(a, vlines[0])) for a, b in sp)
        hcov.append(min(1.0, cov / W) if W > 0 else 0.0)
    vcov.sort(); hcov.sort()
    vmed = vcov[len(vcov) // 2] if vcov else 1.0
    hmed = hcov[len(hcov) // 2] if hcov else 1.0
    if vmed < 0.50 or hmed < 0.50:
        return None
    return {
        "xs": vlines, "ys": hlines, "ncol": nc, "nrow": nr, "cells": cells,
        "colw": [vlines[i + 1] - vlines[i] for i in range(nc)],
        "rowh": [hlines[i + 1] - hlines[i] for i in range(nr)],
        "rect": (vlines[0], hlines[0], vlines[-1], hlines[-1]),
        "text": "",
    }


def page_tables(page):
    """Every table the page draws, with its grid and its cells."""
    segs = _segments(page)
    out = []
    for idxs in _components(segs):
        t = _table_from(segs, idxs)
        if t is None:
            continue
        if len(t["cells"]) < 2:          # one slot is a box, not a table
            continue
        out.append(t)
    out.sort(key=lambda t: (round(t["rect"][1], 1), round(t["rect"][0], 1)))
    return out


def page_spans(page):
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                t = sp.get("text", "").strip()
                if t:
                    out.append((sp["bbox"], t))
    return out


def fill_text(tbl, spans):
    """Put the page's words into the table's cells, in reading order per cell."""
    xs, ys = tbl["xs"], tbl["ys"]
    buckets = {}
    for bb, t in spans:
        cx, cy = (bb[0] + bb[2]) / 2.0, (bb[1] + bb[3]) / 2.0
        if not (xs[0] - 1 <= cx <= xs[-1] + 1 and ys[0] - 1 <= cy <= ys[-1] + 1):
            continue
        for ci, cell in enumerate(tbl["cells"]):
            x0, x1 = xs[cell["c0"]], xs[cell["c1"] + 1]
            y0, y1 = ys[cell["r0"]], ys[cell["r1"] + 1]
            if x0 - 1 <= cx <= x1 + 1 and y0 - 1 <= cy <= y1 + 1:
                buckets.setdefault(ci, []).append((bb[1], bb[0], t))
                break
    parts = []
    for ci, cell in enumerate(tbl["cells"]):
        ws = [w for _, _, w in sorted(buckets.get(ci, []))]
        cell["text"] = " ".join(ws)
        parts.append(cell["text"])
    tbl["text"] = " ".join(p for p in parts if p)
    return tbl


def doc_tables(doc):
    """Every table in a PDF, page-tagged: [(page_no, table), ...]"""
    out = []
    for i, p in enumerate(doc):
        sp = page_spans(p)
        for t in page_tables(p):
            fill_text(t, sp)
            out.append((i, t))
    return out
