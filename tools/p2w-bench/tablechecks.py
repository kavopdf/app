"""The table-geometry checks the 43 never had.

IDS. These are the five the design note calls 61-65. On main the number 61 is already
taken by `61_blank_not_filled` (added in bf2355c), so they land as 62-66. The questions
are unchanged; only the number moved.

MAPPING (design note -> here)
  61_table_columns     -> 62_table_columns
  62_table_rows        -> 63_table_rows
  63_table_span_across -> 64_table_span_across
  64_table_span_down   -> 65_table_span_down
  65_table_cell_width  -> 66_table_cell_width

WHAT WAS MISSING. `grep -c gridSpan verify_google.py` -> 0. Not one check in the suite
read `w:gridSpan`, `w:vMerge`, `w:tcW`, `w:tblGrid`, the column count or the row count.
The suite measured whether a RULE survived (32_stroke_lines), whether ink landed where
the source had blank paper (14/59), whether a line crossed a rule (46) - and none of
those is a question about the GRID. A table can have every rule in place, every word in
place and the wrong geometry, and score 43/43.

FIVE QUESTIONS, EACH A SEPARATE CHECK:

  62_table_columns      the w:tblGrid count == the columns the page's rules enclose
  63_table_rows         the w:tr count     == the rows the page's rules enclose
  64_table_span_across  each cell's w:gridSpan == the columns its page rectangle encloses
  65_table_span_down    each cell's w:vMerge coverage == the rows its page rectangle encloses
  66_table_cell_width   each cell's width == its page rectangle's width

ABSTENTION IS THE WHOLE DESIGN. The engine writes 234 tables into 142 documents; the
page draws a ruled grid under only 136 of them. A whitespace table - a column layout
cut into a w:tbl with no rules anywhere - has NO page grid to be measured against. It
is not a pass and it is not a failure: it is not a question this check can ask. Such a
table abstains, and a document in which every table abstains omits the check entirely
rather than scoring it. That is why the denominator moves.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")

try:
    import tablegrid as TG
    import docxtables as D
except ImportError:                     # running from tools/p2w-bench
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import tablegrid as TG
    import docxtables as D

import re

TW = 20.0
MATCH_THRESH = 0.60     # share of the smaller table's words found in the larger
WIDTH_TOL_PT = 2.0      # a cell's width may differ by this much, in points


def _words(s):
    return [w for w in re.split(r"\s+", s or "") if w.strip()]


def _contain(a, b):
    A, B = set(_words(a)), set(_words(b))
    if not A or not B:
        return 0.0
    return len(A & B) / float(min(len(A), len(B)))


def _page_rects(t):
    return [{"r0": c["r0"], "c0": c["c0"], "r1": c["r1"], "c1": c["c1"],
             "spanC": c["c1"] - c["c0"] + 1, "spanR": c["r1"] - c["r0"] + 1,
             "wPt": t["xs"][c["c1"] + 1] - t["xs"][c["c0"]]}
            for c in t["cells"]]


def _docx_rects(t):
    """The docx table as cell rectangles, w:vMerge applied."""
    ncol = t["ncol"]
    parent = {}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    owner = []
    info = {}
    for r, row in enumerate(t["rows"]):
        c = 0
        line = {}
        for cell in row:
            key = (r, c)
            parent.setdefault(key, key)
            info[key] = cell
            for k in range(cell["span"]):
                if c + k < ncol:
                    line[c + k] = key
            if cell["vm"] == "continue" and r > 0:
                above = owner[r - 1].get(c)
                if above is not None:
                    union(above, key)
            c += cell["span"]
        for k in range(ncol):
            line.setdefault(k, None)
        owner.append(line)

    boxes = {}
    for r in range(len(owner)):
        for c in range(ncol):
            key = owner[r].get(c)
            if key is None:
                continue
            root = find(key)
            b = boxes.get(root)
            if b is None:
                boxes[root] = [r, c, r, c]
            else:
                b[0] = min(b[0], r); b[1] = min(b[1], c)
                b[2] = max(b[2], r); b[3] = max(b[3], c)
    grid = t["grid"]
    out = []
    for b in boxes.values():
        c0, c1 = b[1], b[3]
        w = sum(grid[c0:c1 + 1]) if grid and c1 < len(grid) else None
        out.append({"r0": b[0], "c0": c0, "r1": b[2], "c1": c1,
                    "spanC": c1 - c0 + 1, "spanR": b[2] - b[0] + 1, "wTw": w})
    out.sort(key=lambda x: (x["r0"], x["c0"]))
    return out


def _row_cols(rects, nrow):
    """Per row, the sorted (c0, c1) intervals of the cells covering it.

    Horizontal merges are compared this way and not as a set of rectangles, because a
    cell that spans several ROWS appears once in the rectangle set but in every row it
    covers - and asking the horizontal question through the rectangle set would charge
    a vertical merge to the horizontal check.
    """
    return [sorted((c["c0"], c["c1"]) for c in rects if c["r0"] <= r <= c["r1"])
            for r in range(nrow)]


def _col_rows(rects, ncol):
    """Per column, the sorted (r0, r1) intervals - the vertical-merge question."""
    return [sorted((r["r0"], r["r1"]) for r in rects if r["c0"] <= col <= r["c1"])
            for col in range(ncol)]


def measure(src_path, docx_path):
    """Per-table measurements. Returns (tables, n_docx_tables).

    Each table: the counts on both sides and which of the five questions hold.
    """
    import pymupdf as fitz
    doc = fitz.open(src_path)
    try:
        ptabs = TG.doc_tables(doc)
    finally:
        doc.close()
    dtabs = D.read_tables(docx_path)

    used_p = set()
    out = []
    for di, dt in enumerate(dtabs):
        best, bd = None, MATCH_THRESH
        for pi, (pg, pt) in enumerate(ptabs):
            if pi in used_p:
                continue
            sc = _contain(pt["text"], dt["text"])
            if sc >= bd:
                best, bd = pi, sc
        if best is None:
            continue
        used_p.add(best)
        pg, pt = ptabs[best]
        pr, dr = _page_rects(pt), _docx_rects(dt)
        rec = {"p_cols": pt["ncol"], "d_cols": dt["ncol"],
               "p_rows": pt["nrow"], "d_rows": dt["nrow"],
               "p_rects": pr, "d_rects": dr, "match": bd}
        rec["ok_cols"] = (rec["p_cols"] == rec["d_cols"])
        rec["ok_rows"] = (rec["p_rows"] == rec["d_rows"])
        if rec["ok_cols"] and rec["ok_rows"]:
            rec["ok_across"] = (_row_cols(pr, rec["p_rows"])
                                == _row_cols(dr, rec["d_rows"]))
            rec["ok_down"] = (_col_rows(pr, rec["p_cols"])
                              == _col_rows(dr, rec["d_cols"]))
            worst = 0.0
            for c in pr:
                d = next((d for d in dr if (d["r0"], d["c0"]) == (c["r0"], c["c0"])),
                         None)
                if d is None or d["wTw"] is None:
                    worst = max(worst, 999.0)
                    continue
                worst = max(worst, abs(d["wTw"] / TW - c["wPt"]))
            rec["width_worst"] = worst
            rec["ok_width"] = (worst <= WIDTH_TOL_PT)
        else:
            rec["ok_across"] = rec["ok_down"] = rec["ok_width"] = None
            rec["width_worst"] = None
        out.append(rec)
    return out, len(dtabs)


CHECKS = ("62_table_columns", "63_table_rows", "64_table_span_across",
          "65_table_span_down", "66_table_cell_width")


def checks_for(src_path, docx_path):
    """The five checks' verdicts, or {} entries for those that ABSTAIN.

    Returns {check_id: (source, render, ok)} containing ONLY the checks that had
    something to judge. A check missing from the dict abstains for this document.
    """
    if not docx_path:
        return {}
    try:
        tables, n_docx = measure(src_path, docx_path)
    except Exception:
        return {}
    if not tables:
        return {}          # no page grid under any table: nothing to ask

    res = {}
    for cid, key, unit in (
            ("62_table_columns", "ok_cols", "tables"),
            ("63_table_rows", "ok_rows", "tables"),
            ("64_table_span_across", "ok_across", "tables"),
            ("65_table_span_down", "ok_down", "tables"),
            ("66_table_cell_width", "ok_width", "tables")):
        asked = [t for t in tables if t.get(key) is not None]
        if not asked:
            continue        # every table abstained on this question
        bad = sum(1 for t in asked if not t[key])
        res[cid] = (len(asked), bad, bad == 0)
    return res
