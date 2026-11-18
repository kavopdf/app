#!/usr/bin/env python3
"""cause.py - why is this document wrong, not just how wrong.

THE CLASSES WE WORKED IN WERE SYMPTOMS. `content-missing-nothing-in-its-place` says where the ink is
not; it says nothing about why the engine put it there. Twenty-nine documents share that name and
they are not one bug: measured 18 Nov, their median displacement ranges 1.44 to 6.24 pt and their p90
from 8.16 to 28.8 - a landscape page inside a portrait document, a pair of tables with no gap, and a
right-aligned amount column, all filed together. One fix cannot serve all twenty-nine, which is why
four attempts on a seven-document class improved one document.

CAUSE IS WHAT ONE FIX CAN SERVE. Every open document gets its lines matched against the PDF's own
lines - position.py already does that, line by line, and returns each displacement as (dx, dy). The
SHAPE of those displacements names the mechanism:

  lost-text          a line in the PDF has no counterpart in ours
  page-shift         every line off by the same (dx, dy) - margin or page setup
  vertical-drift     dy grows down the page - line height, spacing, paragraph pitch
  horizontal-scale   dx grows with x - font size, character spacing, column width
  column-width       dx large and dy small, confined to one x band - a table column
  element-block      a run of adjacent lines far off, the rest clean - one table or image
  scattered          none of the above - needs a human to look

    python3 tools/p2w-bench/cause.py --docs a,b,c        # classify these
    python3 tools/p2w-bench/cause.py --open --limit 20   # the worst N open documents
    python3 tools/p2w-bench/cause.py --report            # CAUSES.md from what is recorded
"""
import json, os, subprocess, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "CAUSES.json")
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")


def open_docs():
    """Open documents worst first, with the score that decides the order."""
    import csv
    rows = []
    try:
        for r in csv.DictReader(open(RANK, encoding="utf-8")):
            v = r.get("share5") or ""
            if not v:
                continue
            try:
                f = float(v)
            except ValueError:
                continue
            if f > 5.0:
                rows.append((r["document"], f))
    except Exception:
        pass
    return sorted(rows, key=lambda t: -t[1])


def classify(lines):
    """Name the mechanism from the shape of the displacements.

    `lines` is position.score_document's out_of list: (text, label, dx, dy), where a line the render
    does not have arrives as label "no matching line" with dx=dy=0.
    """
    if not lines:
        return "clean", 0.0
    lost = [l for l in lines if l[1] == "no matching line"]
    moved = [l for l in lines if l[1] != "no matching line"]
    n = len(lines)
    # A QUARTER OF THE LINES MISSING IS A CONTENT LOSS, NOT A SHIFT. At half, the first version
    # asked for > 0.5 and a document with exactly half its lines lost fell through to the shift test
    # on the half that survived - ten lines all off by (1,1) read as "page-shift", which would have
    # sent a fixer after margins on a document that had lost its content.
    if n and len(lost) / float(n) >= 0.25:
        return "lost-text", round(len(lost) / float(n), 2)
    if not moved:
        return "lost-text", 1.0

    dxs = [l[2] for l in moved]
    dys = [l[3] for l in moved]
    amx = sum(abs(v) for v in dxs) / len(dxs)
    amy = sum(abs(v) for v in dys) / len(dys)
    spread_x = max(dxs) - min(dxs)
    spread_y = max(dys) - min(dys)

    # every line off by the same amount, and it is not zero
    if amy > 0.5 and spread_y <= 2.0 and spread_x <= 2.0:
        return "page-shift", amy
    # dy grows with position down the page - a pitch problem, not an offset
    if amy > 0.5 and spread_y > 2.0 and amx < 1.0:
        return "vertical-drift", amy
    # dx moves but dy does not - a width or font-size problem
    if amx > 0.5 and amy < 1.0 and spread_x > 2.0:
        return "horizontal-scale", amx
    # both move, and the movement is not uniform
    if amx > 0.5 and amy > 0.5:
        # ONE ELEMENT, NOT A SCATTER. The test used to ask whether the number of MOVED lines was
        # small, which is never true when everything moved a little and three lines moved a lot -
        # exactly the shape of one table or one image in an otherwise clean page. Count the lines
        # that are FAR off instead: if they are a fifth or less, it is one element.
        far = [l for l in moved if abs(l[2]) > 5.0 or abs(l[3]) > 5.0]
        if far and len(far) <= max(3, n // 5):
            return "element-block", round(max(abs(l[2]) for l in far) if far else 0, 2)
        return "scattered", max(amx, amy)
    return "scattered", max(amx, amy)


def run_docs(docs):
    """Classify each document by rendering it and matching its lines against the PDF."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "p2w-bench"))
    import position
    work = "/scratch/work/cause"
    os.makedirs(work, exist_ok=True)
    corpus = "/scratch/work/p2w/corpus"
    # the built docx live wherever the last conversion put them; out/ is the corpus run's
    docx = "/scratch/work/p2w/docx"
    if not os.path.isdir(docx) or not os.listdir(docx):
        for cand in ("/scratch/work/p2w/out", "/scratch/work/p2w/fixout"):
            if os.path.isdir(cand):
                docx = cand
                break
    out = {}
    for d in docs:
        pdf = os.path.join(corpus, d + ".pdf")
        dx = os.path.join(docx, d + ".docx")
        if not (os.path.exists(pdf) and os.path.exists(dx)):
            out[d] = {"cause": "not-built", "size": 0.0}
            continue
        try:
            r = position.score_document(pdf, dx, work)
        except Exception as e:
            out[d] = {"cause": "error", "size": 0.0, "why": str(e)[:80]}
            continue
        if r.get("error"):
            out[d] = {"cause": "error", "size": 0.0, "why": r["error"][:80]}
            continue
        lines = r.get("out_of") or []
        cause, size = classify(lines)
        out[d] = {"cause": cause, "size": round(size, 2), "lines_out": len(lines),
                  "total": r.get("lines"), "within": r.get("within"),
                  "unmatched": r.get("unmatched")}
        print("  %-40s %-18s %5.2f  (%d of %s lines out)" % (d[:40], cause, size,
              len(lines), r.get("lines")))
    return out


def merge(new):
    d = {}
    if os.path.exists(OUT):
        try:
            d = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            d = {}
    d.update(new)
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return d


def report():
    d = {}
    if os.path.exists(OUT):
        d = json.load(open(OUT, encoding="utf-8"))
    if not d:
        print("nothing classified yet - run with --docs or --open")
        return 1
    by = collections.defaultdict(list)
    for doc, rec in d.items():
        by[rec.get("cause", "?")].append(doc)
    path = os.path.join(HERE, "CAUSES.md")
    # A CENSUS MUST SAY HOW MUCH OF THE CORPUS IT SAW. Six documents classified out of ninety-four
    # open is not a census, and a reader who takes it for one will size the work from a sample. The
    # coverage line is the first thing under the heading for that reason.
    try:
        import csv as _c
        _rank = {r["document"]: r for r in _c.DictReader(
            open(os.path.join(ROOT, "benchmarks", "RANKING.csv"), encoding="utf-8"))}
        _open = [d for d, r in _rank.items()
                 if r.get("share5") and float(r["share5"]) > 1.0]
    except Exception:
        _open = []
    _covered = len([d for d in d if d in set(_open)])
    L = ["# Causes, not symptoms", "",
         "**Coverage: %d of %d open documents classified.** The rest are unclassified, and a cause"
         % (_covered, len(_open)),
         "table built from a sample is not a census - re-run `cause.py --open --limit N` against docx",
         "built by the CURRENT engine before sizing any work from this file.", "",
         "Grouped from `CAUSES.json`, which `cause.py` writes by matching every line of our render",
         "against the line the PDF drew and classifying the SHAPE of the displacement.", "",
         "| cause | documents | what one fix would serve |", "|---|---:|---|"]
    hint = {"lost-text": "text extraction, encoding or a dropped block",
            "page-shift": "margins, page size or an offset applied to the whole sheet",
            "vertical-drift": "line height, paragraph pitch or table row height",
            "horizontal-scale": "font size, character spacing or column width",
            "column-width": "table column widths",
            "element-block": "one table or image and the flow around it",
            "scattered": "needs a human to look at one",
            "not-built": "the docx was never built",
            "error": "the render failed"}
    for cause, docs in sorted(by.items(), key=lambda t: -len(t[1])):
        L.append("| `%s` | **%d** | %s |" % (cause, len(docs), hint.get(cause, "")))
    L.append("")
    L.append("## Documents")
    L.append("")
    for cause, docs in sorted(by.items(), key=lambda t: -len(t[1])):
        L.append("### `%s` — %d" % (cause, len(docs)))
        L.append("")
        for doc in sorted(docs):
            rec = d[doc]
            L.append("- `%s` — %s pt" % (doc, rec.get("size")))
        L.append("")
    open(path, "w", encoding="utf-8").write("\n".join(L))
    print("wrote %s" % path)
    for cause, docs in sorted(by.items(), key=lambda t: -len(t[1])):
        print("  %-18s %d" % (cause, len(docs)))
    return 0


def main(argv):
    if "--report" in argv:
        return report()
    docs = []
    if "--docs" in argv:
        i = argv.index("--docs") + 1
        docs = [x.strip() for x in argv[i].split(",") if x.strip()]
    elif "--open" in argv:
        docs = [d for d, _ in open_docs()]
        if "--limit" in argv:
            docs = docs[:int(argv[argv.index("--limit") + 1])]
    if not docs:
        print("usage: cause.py --docs a,b,c | --open [--limit N] | --report")
        return 2
    merge(run_docs(docs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
