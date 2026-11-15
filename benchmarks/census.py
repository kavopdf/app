#!/usr/bin/env python3
"""census.py - what was lost, and where. Evidence, not a score.

WHY THIS EXISTS

The fixer was given a number and a name: `415_inline_images, 89.04 %@5, content-loss,
max 153 pt, 1 page`. From that it had to guess the MECHANISM, then write a patch, then
measure. ATTEMPTS.json records the result: 19 attempts over four classes, zero kept,
fourteen of them on one class. It was not failing at patching - it was guessing at what
to patch.

A pixel score cannot tell you that four images are missing. A structural diff can.

WHAT IT MEASURES

For every document the ranking calls defective, count what the SOURCE holds and what the
OUTPUT holds, element type by element type:

    images       raster images in the source pages   vs   inline pictures in the docx
    rules        drawn lines/rects in the source     vs   table cells in the docx
    text         characters in the source            vs   characters in the docx
    annotations  annotation objects in the source    vs   (reported, not compared)

and which page carries the worst displacement, so a reader can open that page and look.

THE SIGNAL IS A HYPOTHESIS, NOT A PROOF

The counts are facts. The `signal` column is a candidate mechanism derived from them, and
it is deliberately conservative: it fires only when the evidence is unambiguous (source
has images, output has none). Everything else says `none-identified` rather than inventing
a cause. A wrong mechanism is worse than no mechanism, because it sends the fixer after a
patch that cannot work.

    python3 benchmarks/census.py --corpus /scratch/work/p2w/corpus \
                                 --out /scratch/work/p2w/out \
                                 --ranking benchmarks/RANKING.csv

Writes benchmarks/CENSUS.csv (one row per defective document) and benchmarks/CENSUS.md
(the same grouped by signal, which is the part that tells you which mechanism to fix first).
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict


def src_facts(pdf_path):
    """Per-page element counts from the source PDF."""
    import pymupdf
    out = {"pages": 0, "chars": 0, "images": 0, "drawings": 0, "annots": 0,
           "page_chars": {}, "page_images": {}, "page_drawings": {}}
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        out["error"] = str(e)[:120]
        return out
    out["pages"] = len(doc)
    for i, page in enumerate(doc):
        try:
            text = page.get_text("text") or ""
            n_img = len(page.get_images(full=True))
            n_draw = len(page.get_drawings())
            n_ann = 0
            try:
                n_ann = len(list(page.annots() or []))
            except Exception:
                pass
            out["chars"] += len(text)
            out["images"] += n_img
            out["drawings"] += n_draw
            out["annots"] += n_ann
            out["page_chars"][i + 1] = len(text)
            out["page_images"][i + 1] = n_img
            out["page_drawings"][i + 1] = n_draw
        except Exception:
            continue
    try:
        doc.close()
    except Exception:
        pass
    return out


def docx_facts(docx_path):
    """Element counts from the produced .docx."""
    out = {"chars": 0, "images": 0, "tables": 0, "cells": 0, "paragraphs": 0}
    try:
        import docx
        d = docx.Document(docx_path)
    except Exception as e:
        out["error"] = str(e)[:120]
        return out
    try:
        for p in d.paragraphs:
            out["paragraphs"] += 1
            out["chars"] += len(p.text or "")
        for t in d.tables:
            out["tables"] += 1
            for row in t.rows:
                out["cells"] += len(row.cells)
                for c in row.cells:
                    out["chars"] += len(c.text or "")
        # inline pictures live in the document part's relationships
        try:
            from docx.oxml.ns import qn
            out["images"] = len(d.element.body.findall(".//" + qn("pic:pic")))
        except Exception:
            out["images"] = -1
    except Exception as e:
        out["error"] = str(e)[:120]
    return out


def signal_for(s, d):
    """The candidate mechanism. Conservative on purpose - see the module docstring."""
    if s.get("error") or d.get("error"):
        return "unreadable"
    si, di = s["images"], d["images"]
    if si > 0 and di == 0:
        return "images-none-extracted"
    if si >= 2 and 0 < di < si * 0.5:
        return "images-mostly-missing"
    if s["chars"] > 200 and d["chars"] < s["chars"] * 0.85:
        return "text-missing"
    if s["drawings"] >= 20 and d["cells"] == 0:
        return "rules-not-tables"
    if s["annots"] > 0 and s["chars"] > 0:
        return "annotations-present"
    return "none-identified"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="/scratch/work/p2w/corpus")
    ap.add_argument("--out", default="/scratch/work/p2w/out")
    ap.add_argument("--ranking", default="benchmarks/RANKING.csv")
    ap.add_argument("--limit", type=int, default=0, help="only the N worst documents")
    ap.add_argument("--csv", default="benchmarks/CENSUS.csv")
    ap.add_argument("--md", default="benchmarks/CENSUS.md")
    a = ap.parse_args(argv[1:])

    rows = []
    with open(a.ranking, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            p = (r.get("problem") or "").strip()
            if p in ("", "none", "unmeasured"):
                continue
            try:
                r["_s5"] = float(r.get("share5") or "")
            except ValueError:
                continue
            rows.append(r)
    rows.sort(key=lambda r: -r["_s5"])
    if a.limit:
        rows = rows[:a.limit]

    cols = ["document", "problem", "share5", "max_pt", "worst_page", "pages",
            "src_chars", "docx_chars", "src_images", "docx_images",
            "src_drawings", "docx_tables", "docx_cells", "src_annots", "signal"]
    out_rows = []
    for r in rows:
        doc = r["document"]
        sp = os.path.join(a.corpus, doc + ".pdf")
        dp = os.path.join(a.out, doc + ".docx")
        if not os.path.exists(sp) or not os.path.exists(dp):
            continue
        s, d = src_facts(sp), docx_facts(dp)
        out_rows.append({
            "document": doc, "problem": r.get("problem", ""), "share5": r.get("share5", ""),
            "max_pt": r.get("max_pt", ""), "worst_page": r.get("worst_page", ""),
            "pages": s.get("pages", ""),
            "src_chars": s.get("chars", ""), "docx_chars": d.get("chars", ""),
            "src_images": s.get("images", ""), "docx_images": d.get("images", ""),
            "src_drawings": s.get("drawings", ""), "docx_tables": d.get("tables", ""),
            "docx_cells": d.get("cells", ""), "src_annots": s.get("annots", ""),
            "signal": signal_for(s, d),
        })

    os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
    with open(a.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    by = defaultdict(list)
    for r in out_rows:
        by[r["signal"]].append(r)
    order = ["images-none-extracted", "images-mostly-missing", "rules-not-tables",
             "text-missing", "annotations-present", "none-identified", "unreadable"]

    md = ["# Census - what was lost, and where", "",
          "Every document the ranking calls defective, with what the SOURCE holds beside",
          "what the OUTPUT holds. The counts are facts. The `signal` is a candidate",
          "mechanism and it is deliberately conservative: it fires only when the evidence",
          "is unambiguous. `none-identified` means the counts do not point at one cause,",
          "and that is a real answer - a wrong mechanism sends the fixer after a patch",
          "that cannot work.", "",
          "**%d defective documents censused.**" % len(out_rows), "",
          "| signal | documents | total share@5 | worst document |",
          "|---|---|---|---|"]
    for sig in order:
        g = by.get(sig)
        if not g:
            continue
        worst = max(g, key=lambda r: float(r["share5"]))
        md.append("| %s | %d | %.1f%% | %s %.1f%%@5 p%s |"
                  % (sig, len(g), sum(float(r["share5"]) for r in g),
                     worst["document"][:34], float(worst["share5"]), worst["worst_page"]))
    md.append("")
    for sig in order:
        g = by.get(sig)
        if not g:
            continue
        md += ["## %s (%d documents)" % (sig, len(g)), "",
               "| document | share@5 | worst page | src img | docx img | src chars | docx chars | src draws | docx cells |",
               "|---|---|---|---|---|---|---|---|---|"]
        for r in g[:25]:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                      % (r["document"][:34], r["share5"], r["worst_page"],
                         r["src_images"], r["docx_images"], r["src_chars"],
                         r["docx_chars"], r["src_drawings"], r["docx_cells"]))
        if len(g) > 25:
            md.append("| ... %d more | | | | | | | | |" % (len(g) - 25))
        md.append("")
    with open(a.md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("censused %d defective documents" % len(out_rows))
    for sig in order:
        if by.get(sig):
            print("  %-24s %d" % (sig, len(by[sig])))
    print("wrote %s and %s" % (a.csv, a.md))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
