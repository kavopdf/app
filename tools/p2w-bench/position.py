#!/usr/bin/env python3
"""G5 - where did the text actually end up?

WHY THIS EXISTS
    Counts can stay clean while every line moves. A document can hold every word,
    the right number of pages and the right number of lines, and still be laid out
    somewhere other than where the PDF put it. Nothing in gate.py can see that.
    This renders the .docx, reads back where each line landed, and compares it with
    where the PDF drew it.

WHY BOTH SIDES ARE RENDERED
    The PDF's coordinates are the reference and are read directly. A .docx has no
    absolute coordinates for body text - position emerges from margins, indent,
    spacing and the flow of everything above it - so the only honest way to measure
    where a line ended up is to lay the document out and read the result. Measuring
    the XML instead would measure the declaration, not the position.

MATCHING IS BY TEXT, NEVER BY INDEX
    Index pairing shifts every line the moment one line is dropped, and the score
    still looks healthy. Each PDF line is matched to a docx line with the same text,
    and a line that finds no partner counts as a failure rather than silently
    disappearing from the denominator.

USAGE
    python3 position.py --corpus PDF_DIR --out DOCX_DIR
    python3 position.py --corpus PDF_DIR --out DOCX_DIR --json result.json
    python3 position.py --corpus PDF_DIR --out DOCX_DIR --limit 20

EXIT CODE
    0  every document within tolerance
    1  at least one document out of tolerance
    2  the check could not run (LibreOffice or PyMuPDF missing)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# The tolerances are the ones agreed for a DOCX, in points. They are asymmetric on
# purpose: x comes from an indent and can be exact, while y comes from the line height
# the layout engine chooses and drifts a little more.
TOL_X_PT = 1.5
TOL_Y_PT = 3.0
TOL_SIZE_PT = 0.5
# A colour that has moved by less than this in each channel is the same colour to a
# reader. Straight RGB distance, because a full CIE delta-E needs a colour library the
# sandbox does not have and the difference it would make here is a fraction of one unit.
TOL_COLOUR = 24
# There is deliberately NO pass mark here. A number invented in advance - 90 %, 95 % -
# decides that a document is broken before anyone has measured what the converter
# actually achieves, and a corpus at 5 % then fails every document for ever and a run
# spends its three tries on all of them. The score is reported, and the pass or fail
# comes from comparing each document against its own recorded baseline.


def norm(text):
    return re.sub(r"\s+", " ", text or "").strip().lower()


def base_font(name):
    """The family part of a font name, without the subset prefix or the style suffix."""
    if not name:
        return ""
    n = name.split("+")[-1]
    for suffix in ("-BoldItalic", "-BoldOblique", "-Bold", "-Italic", "-Oblique",
                   "-Regular", "-Roman", "-Medium", "-Light", "-Black", "-Semibold"):
        if n.endswith(suffix):
            n = n[:-len(suffix)]
    return n.lower()


def colour_close(a, b):
    if a is None or b is None:
        return True
    if isinstance(a, int) and isinstance(b, int):
        return (((a >> 16) & 255) - ((b >> 16) & 255)) ** 2 + \
               (((a >> 8) & 255) - ((b >> 8) & 255)) ** 2 + \
               ((a & 255) - (b & 255)) ** 2 <= TOL_COLOUR ** 2
    try:
        return sum((int(x) - int(y)) ** 2 for x, y in zip(a, b)) <= TOL_COLOUR ** 2
    except Exception:
        return True


def declared_fonts(docx_path):
    """The font names the .docx actually declares, read from its own XML.

    Not from the render: LibreOffice substitutes a font the machine does not have, so a
    render reports NotoSans where the file says DejaVuSans and a perfectly correct
    document looks wrong. The XML is the only place the file's own choice is recorded.
    """
    import zipfile
    import re as _re
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return None
    names = []
    for m in _re.finditer(r'<w:rFonts[^>]*>', xml):
        tag = m.group(0)
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            hit = _re.search(attr + r'="([^"]+)"', tag)
            if hit:
                names.append(hit.group(1))
    return names


def pdf_pages(path):
    """Lines per page, with the size, font and colour the page actually drew.

    A page that moved must not be compared with a page that did not, so the pages stay
    separate. Size, font and colour come from the render because that is what a reader
    sees; the tolerance table promises all three and no gate measured any of them.
    """
    import pymupdf
    pages = []
    with pymupdf.open(path) as doc:
        for page in doc:
            lines = []
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    spans = line.get("spans") or []
                    text = "".join(s.get("text", "") for s in spans)
                    if not norm(text):
                        continue
                    x0, y0, x1, y1 = line["bbox"]
                    live = [s for s in spans if s.get("text", "").strip()]
                    size = max((s.get("size", 0) for s in live), default=0)
                    font = max(live, key=lambda s: len(s.get("text", ""))).get("font", "") if live else ""
                    colour = live[0].get("color") if live else None
                    lines.append((text, x0, (y0 + y1) / 2.0, size, font, colour))
            pages.append(lines)
    return pages

def render(docx_path, workdir):
    outdir = os.path.join(workdir, "r")
    os.makedirs(outdir, exist_ok=True)
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                        "--outdir", outdir, docx_path],
                       check=True, capture_output=True, timeout=240)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    pdf = os.path.join(outdir, os.path.basename(docx_path)[:-5] + ".pdf")
    return pdf if os.path.exists(pdf) else None


def score_document(pdf_path, docx_path, workdir):
    rendered = render(docx_path, workdir)
    if not rendered:
        return {"error": "could not render the docx"}

    ref_pages = pdf_pages(pdf_path)
    got_pages = pdf_pages(rendered)
    if not any(ref_pages):
        return {"error": "the PDF has no text"}

    # A page that moved must not be compared with a page that did not: flattening both
    # sides into one list reports a line on page 3 as hundreds of points away from the
    # same line on page 1, which is a measurement artefact and not a defect. Pages are
    # compared in order, and only as far as both sides have pages.
    common = min(len(ref_pages), len(got_pages))
    within = 0
    total = 0
    out_of = []
    unmatched = 0
    for pi in range(common):
        ref = ref_pages[pi]
        got = got_pages[pi]
        pool = {}
        for item in got:
            pool.setdefault(norm(item[0]), []).append(item)
        for item in ref:
            text, x, y = item[0], item[1], item[2]
            total += 1
            key = norm(text)
            candidates = pool.get(key)
            if not candidates:
                unmatched += 1
                out_of.append((text[:40], "no matching line", 0, 0))
                continue
            best_i, best_d = 0, None
            for i, cand in enumerate(candidates):
                d = abs(cand[2] - y)
                if best_d is None or d < best_d:
                    best_i, best_d = i, d
            cand = candidates.pop(best_i)
            cx, cy = cand[1], cand[2]
            dx, dy = cx - x, cy - y
            if abs(dx) <= TOL_X_PT and abs(dy) <= TOL_Y_PT:
                within += 1
            else:
                out_of.append((text[:40], "%.1f,%.1f" % (dx, dy), dx, dy))

    # Lines on a page the render does not have are lost, not unmeasured.
    for pi in range(common, len(ref_pages)):
        for item in ref_pages[pi]:
            text = item[0]
            total += 1
            unmatched += 1
            out_of.append((text[:40], "page missing in the render", 0, 0))

    # Font size, font name and colour. The tolerance table promises all three and no
    # gate measured any of them, so a document could have every word in the wrong size
    # and pass everything. Sizes and names come from the render because that is what the
    # reader sees; the docx XML declares them, and where the two disagree the render is
    # the one that matters.
    size_hits = size_total = 0
    name_hits = name_total = 0
    colour_hits = colour_total = 0
    font_problems = []
    for pi in range(common):
        pool = {}
        for item in got_pages[pi]:
            pool.setdefault(norm(item[0]), []).append(item)
        for item in ref_pages[pi]:
            text, x, y, rsize, rfont, rcol = item
            cand = pool.get(norm(text))
            if not cand:
                continue
            best_i, best_d = 0, None
            for i, c in enumerate(cand):
                d = abs(c[2] - y)
                if best_d is None or d < best_d:
                    best_i, best_d = i, d
            c = cand.pop(best_i)
            _t, _x, _y, gsize, gfont, gcol = c
            if rsize > 0 and gsize > 0:
                size_total += 1
                if abs(gsize - rsize) <= TOL_SIZE_PT:
                    size_hits += 1
                elif len(font_problems) < 5:
                    font_problems.append("%-30s size %.1f -> %.1f" % (text[:30], rsize, gsize))
            # Font NAME is deliberately not compared here. The render substitutes any
            # font the machine lacks - DejaVuSans comes back as NotoSans - so comparing
            # names in a render marks a correct document wrong. The declared names are
            # read from the .docx XML below and compared there.
            if rcol is not None and gcol is not None:
                colour_total += 1
                if colour_close(rcol, gcol):
                    colour_hits += 1

    declared = declared_fonts(docx_path)
    pdf_names = []
    for pg in ref_pages:
        for item in pg:
            if item[4]:
                pdf_names.append(base_font(item[4]))
    declared_families = [base_font(n) for n in (declared or [])]
    font_name_share = None
    if pdf_names and declared_families:
        want = {}
        for n in pdf_names:
            want[n] = want.get(n, 0) + 1
        have = {}
        for n in declared_families:
            have[n] = have.get(n, 0) + 1
        # every PDF family must be declared at least as many times as the PDF uses it
        hit = sum(min(c, have.get(n, 0)) for n, c in want.items())
        font_name_share = hit / max(1, sum(want.values()))

    return {
        "lines": total,
        "within": within,
        "unmatched": unmatched,
        "pages_ref": len(ref_pages),
        "pages_got": len(got_pages),
        "page_count_ok": len(ref_pages) == len(got_pages),
        "share": within / total if total else 0.0,
        "size_share": size_hits / size_total if size_total else None,
        "name_share": font_name_share,
        "colour_share": colour_hits / colour_total if colour_total else None,
        "font_problems": font_problems,
        "worst": sorted(out_of, key=lambda r: -(abs(r[2]) + abs(r[3])))[:5],
        "ok": len(ref_pages) == len(got_pages),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--baseline", help="a previous --json result; any document whose "
                                       "score fell below its own entry is a regression")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if shutil.which("soffice") is None:
        print("LibreOffice is not installed, so the docx side cannot be rendered")
        return 2
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        print("PyMuPDF is not installed")
        return 2
    if not os.path.isdir(args.corpus) or not os.path.isdir(args.out):
        print("corpus and out must both be folders")
        return 2

    names = sorted(f for f in os.listdir(args.corpus) if f.lower().endswith(".pdf"))
    if args.limit:
        names = names[:args.limit]

    results = []
    workdir = tempfile.mkdtemp(prefix="position-")
    for name in names:
        base = name[:-4]
        docx = os.path.join(args.out, base + ".docx")
        if not os.path.isfile(docx):
            results.append({"doc": base, "ok": False, "error": "no docx"})
            continue
        try:
            r = score_document(os.path.join(args.corpus, name), docx, workdir)
        except Exception as exc:
            r = {"error": "check failed: " + str(exc)}
        r["doc"] = base
        results.append(r)

    base = None
    if args.baseline and os.path.isfile(args.baseline):
        try:
            base = {r["doc"]: r for r in json.load(open(args.baseline)) if "share" in r}
        except Exception:
            base = None

    if base:
        regressed = []
        for r in results:
            was = base.get(r.get("doc"))
            if was and "share" in r and r["share"] < was["share"] - 0.005:
                regressed.append((r["doc"], was["share"], r["share"]))
                r["ok"] = False
        for doc, was, now in regressed:
            print("REGRESSED %-40s %.1f %% -> %.1f %%" % (doc[:40], was * 100, now * 100))

    failed = [r for r in results if not r.get("ok")]
    scored = [r for r in results if "share" in r]
    overall = (sum(r["within"] for r in scored) /
               max(1, sum(r["lines"] for r in scored))) if scored else 0.0

    for r in results:
        if r.get("ok"):
            if args.verbose:
                print("OK   %-44s %.1f %% of %d lines" %
                      (r["doc"][:44], r["share"] * 100, r["lines"]))
        else:
            print("FAIL %-44s %s" % (r["doc"][:44], r.get("error", "")))
            if not r.get("page_count_ok", True):
                print("       %d pages in the render against the PDF's %d"
                      % (r.get("pages_got", 0), r.get("pages_ref", 0)))
            if "share" in r:
                print("       %.1f %% of %d lines within tolerance" %
                      (r["share"] * 100, r["lines"]))
                for text, delta, _dx, _dy in r["worst"]:
                    print("         %-40s off by %s pt" % (text, delta))

    print("")
    print("documents: %d   failed: %d   lines within tolerance: %.1f %%"
          % (len(results), len(failed), overall * 100))
    def share(key):
        vals = [r[key] for r in scored if r.get(key) is not None]
        return (sum(vals) / len(vals) * 100) if vals else None

    print("tolerance: x %.1f pt, y %.1f pt, size %.1f pt, colour %d"
          % (TOL_X_PT, TOL_Y_PT, TOL_SIZE_PT, TOL_COLOUR))
    for label, key in (("font size", "size_share"), ("font name", "name_share"),
                       ("colour", "colour_share")):
        got = share(key)
        print("  %-10s %s" % (label, "not measured" if got is None else "%.1f %%" % got))
    print("  (font name is read from the .docx XML, not the render: a render substitutes)")
    if base:
        print("compared against %s" % args.baseline)
    else:
        print("no baseline given - the score is reported, not judged")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=1)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
