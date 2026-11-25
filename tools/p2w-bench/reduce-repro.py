#!/usr/bin/env python3
"""reduce-repro.py - shrink a REAL corpus .docx that fails exactly one check, keeping its construct.

    python3 tools/p2w-bench/reduce-repro.py --candidates          # the documents this can be run on
    python3 tools/p2w-bench/reduce-repro.py <name>                # carrier guard (default)
    python3 tools/p2w-bench/reduce-repro.py <name> --strict       # scan-count guard
    python3 tools/p2w-bench/reduce-repro.py <name> --rows --lo    # also drop table rows, verify via LibreOffice

WHY REDUCTION AND NOT SYNTHESIS.

A minimal .docx written from scratch encodes what its author THOUGHT the failure depends on. If the
real failure depends on something nobody thought of - a substituted face, a row height, the number of
paragraphs above - the synthetic file is faithful to the theory and not to the defect. A reduced real
document keeps every ingredient nobody named, because it is the same document with parts removed.

WHAT THIS TOOL DOES. It takes a corpus .docx whose Google verdict (benchmarks/gverify/<name>.json)
lists exactly ONE failed check, and deletes body elements from word/document.xml - whole pages, whole
tables, table rows, whole paragraphs - accepting a deletion only when the guard says the construct that
carries the failure is still there. It stops when no single deletion survives the guard.

WHAT IT CANNOT DO, AND SAYS SO. There is no Google Docs in this sandbox, so nothing here observes a
Google render. The reduced file is NOT shown to fail in Google. What is verified is: the .docx is a
valid zip, word/document.xml parses, the file opens in python-docx, google_safe.py:scan() reports the
same counts for the constructs that carry the failure, the reduction changed nothing except the deleted
spans, and (with --lo) the file still converts in LibreOffice and the 42 checks still score the same.
A reduction can therefore have dropped the REAL cause without any of these checks noticing. That is
stated in the output of every run, not only here.

THE TWO GUARDS.

    --strict   the scan() count of every construct that carries the failing check is IDENTICAL to the
               original's, at every step. This is the literal reading of "the construct count is
               unchanged", and it is the stronger claim. On the 18_displacement documents it is nearly
               unusable: w:before-page-top is counted by scan() on every paragraph that asks for space
               before it (214 instances in one 6-paragraph document), while the measured defect is only
               about w:before AT A PAGE TOP (google_safe.py's own note: 55.15 pt asked, 0.33 rendered).
               Preserving the over-inclusive count preserves almost the whole document.

    carrier    (default) at least ONE child that carries the construct survives BYTE-IDENTICAL, and
               that child is never touched. Other carriers may go: the point of a minimal repro is one
               instance of the construct, not every instance. scan() counts are reported at every step
               so the loss of the other instances is visible rather than hidden.

Both are run for every document in the summary, because the difference between them is itself a
measurement about how coarse scan() is.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import google_safe  # noqa: E402  - the same scanner the commit gate uses
from diagnose import CAUSE  # noqa: E402  - the measured construct -> check mapping

CORPUS = "/scratch/work/p2w/corpus"
OUT = "/scratch/work/p2w/out"
GV = os.path.join(ROOT, "benchmarks", "gverify")
SOFFICE = "/usr/lib/libreoffice/program/soffice.bin"

# check -> the constructs that are MEASURED to carry it (diagnose.CAUSE, inverted).
CHECK_CONSTRUCT = {}
for _c, _checks in CAUSE.items():
    for _k in _checks:
        CHECK_CONSTRUCT.setdefault(_k, []).append(_c)

# Checks with NO measured construct carrier. For these the carrier is located in the SOURCE PDF's
# geometry instead, and the tool says so rather than inventing a mapping.
#   60_text_column_right_edge  the failing line is the one whose right edge is furthest right
#   47_margins                 the failing paragraph is the one whose left edge is furthest left
GEOM = {"60_text_column_right_edge": "rightmost", "47_margins": "leftmost"}

# Two checks whose carrier IS measured but is not in diagnose.CAUSE. Both quotes are from
# google_safe.py's own IGNORED table, i.e. the gate's recorded measurement, not an inference:
#   32_stroke_lines   "a rule carried only as a floating <w:drawing> has NEVER passed 32_stroke_lines
#                      in 192 scored documents; the two that pass carry it as a table-cell border"
#   59_shape_anchor   "<w:drawing> / wp:anchor: Google does not lay out floating drawings from an
#                      imported .docx. It drops the shape and leaves the anchor."
EXTRA_CAUSE = {"32_stroke_lines": ["w:drawing", "wp:anchor"],
               "59_shape_anchor": ["wp:anchor", "w:drawing"]}
for _k, _v in EXTRA_CAUSE.items():
    CHECK_CONSTRUCT.setdefault(_k, []).extend(_v)


# ---------------------------------------------------------------------------------------------
# raw XML surgery
#
# The reduced file must differ from the original ONLY by the deleted spans, so nothing is ever
# re-serialised: the original bytes are kept and a byte range is cut out of them. ElementTree/lxml
# round-trips rename prefixes and rewrite attribute order, which would make "the construct survived"
# a claim about a different file.
# ---------------------------------------------------------------------------------------------

def _tag_end(s, i):
    """Offset just past the '>' that closes the tag starting at s[i]=='<', quotes respected."""
    q = None
    j = i + 1
    while j < len(s):
        ch = s[j]
        if q:
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
        elif ch == ">":
            return j + 1
        j += 1
    raise ValueError("unterminated tag at %d" % i)


def body_spans(xml):
    """[(start, end, kind)] for every direct child of <w:body>, in document order.

    kind is the local tag name: p, tbl, sectPr, bookmarkEnd, ...
    """
    m = re.search(r"<w:body\b[^>]*>", xml)
    if not m:
        raise ValueError("no <w:body> - not a wordprocessingml document")
    i = m.end()
    depth = 1
    out = []
    n = len(xml)
    while i < n and depth > 0:
        j = xml.find("<", i)
        if j < 0:
            break
        if xml.startswith("<!--", j):
            i = xml.index("-->", j) + 3
            continue
        if xml.startswith("<![CDATA[", j):
            i = xml.index("]]>", j) + 3
            continue
        if xml.startswith("<?", j):
            i = xml.index("?>", j) + 2
            continue
        end = _tag_end(xml, j)
        tok = xml[j:end]
        if tok.startswith("</"):
            depth -= 1
            if depth == 0:
                break
            i = end
            continue
        selfclose = tok.endswith("/>")
        name = re.match(r"</?([\w:.-]+)", tok)
        local = name.group(1).split(":")[-1] if name else "?"
        if depth == 1:
            if selfclose:
                out.append((j, end, local))
                i = end
                continue
            # find the matching close tag by re-walking from here
            k = end
            d = 1
            while d > 0 and k < n:
                p = xml.find("<", k)
                if p < 0:
                    break
                if xml.startswith("<!--", p):
                    k = xml.index("-->", p) + 3
                    continue
                if xml.startswith("<![CDATA[", p):
                    k = xml.index("]]>", p) + 3
                    continue
                e2 = _tag_end(xml, p)
                t2 = xml[p:e2]
                if t2.startswith("</"):
                    d -= 1
                elif not t2.endswith("/>"):
                    d += 1
                k = e2
            out.append((j, k, local))
            i = k
            continue
        if not selfclose:
            depth += 1
        i = end
    return out


def child_spans(span, xml, tag):
    """Spans of direct <w:tag> children inside xml[span[0]:span[1]] (used for w:tr inside w:tbl)."""
    sub = xml[span[0]:span[1]]
    res = []
    # walk the subtree at depth 1 relative to the container
    i = sub.find("<", sub.find(">") + 1)  # skip the container's own start tag
    depth = 1
    while i >= 0 and i < len(sub):
        if sub.startswith("<!--", i):
            i = sub.index("-->", i) + 3
            continue
        e = _tag_end(sub, i)
        tok = sub[i:e]
        if tok.startswith("</"):
            depth -= 1
            i = e
            if depth == 0:
                break
            continue
        selfclose = tok.endswith("/>")
        name = re.match(r"</?([\w:.-]+)", tok)
        local = name.group(1).split(":")[-1] if name else "?"
        if depth == 1 and local == tag:
            if selfclose:
                res.append((span[0] + i, span[0] + e))
                i = e
                continue
            k = e
            d = 1
            while d > 0 and k < len(sub):
                p = sub.find("<", k)
                if p < 0:
                    break
                e2 = _tag_end(sub, p)
                t2 = sub[p:e2]
                if t2.startswith("</"):
                    d -= 1
                elif not t2.endswith("/>"):
                    d += 1
                k = e2
            res.append((span[0] + i, span[0] + k))
            i = k
            continue
        if not selfclose and depth == 1:
            # descend
            depth += 1
            i = e
            continue
        i = e
    return res


def element_span_at(xml, pos):
    """(start, end) of the whole element that contains offset pos."""
    start = xml.rfind("<", 0, pos + 1)
    while start > 0 and xml[start + 1:start + 2] in ("/", "!", "?"):
        start = xml.rfind("<", 0, start)
    end = _tag_end(xml, start)
    if xml[start:end].endswith("/>"):
        return start, end
    depth, k = 1, end
    while depth > 0 and k < len(xml):
        p2 = xml.find("<", k)
        if p2 < 0:
            break
        if xml.startswith("<!--", p2):
            k = xml.index("-->", p2) + 3
            continue
        e2 = _tag_end(xml, p2)
        t2 = xml[p2:e2]
        if t2.startswith("</"):
            depth -= 1
        elif not t2.endswith("/>"):
            depth += 1
        k = e2
    return start, k


def cut(xml, spans):
    """Delete byte ranges, right to left, so earlier offsets stay valid."""
    for s, e in sorted(spans, reverse=True):
        xml = xml[:s] + xml[e:]
    return xml


def text_of(fragment):
    return re.sub(r"\s+", " ", "".join(re.findall(r"<w:t\b[^>]*>([^<]*)</w:t>", fragment))).strip()


# ---------------------------------------------------------------------------------------------
# structure + census
# ---------------------------------------------------------------------------------------------

def load(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        xml = z.read("word/document.xml").decode("utf-8")
    return names, xml


def rebuild(src, dest, xml):
    """Write dest = src with word/document.xml replaced. Every other part is copied byte for byte."""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = xml.encode("utf-8") if item.filename == "word/document.xml" \
                else zin.read(item.filename)
            zi = zipfile.ZipInfo(item.filename, date_time=item.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = item.external_attr
            zout.writestr(zi, data)


def census(xml):
    spans = body_spans(xml)
    kinds = [k for _s, _e, k in spans]
    breaks = len(re.findall(r'<w:br w:type="page"', xml))
    return {
        "body_children": len(spans),
        "paragraphs": kinds.count("p"),
        "tables": kinds.count("tbl"),
        "table_rows": len(re.findall(r"<w:tr\b", xml)),
        "explicit_page_breaks": breaks,
        "sections": len(re.findall(r"<w:sectPr", xml)),
        "bytes_document_xml": len(xml.encode("utf-8")),
    }


def pages(xml):
    """Body children grouped into pages: a page ends at a child carrying an explicit page break.

    Only meaningful when the document has explicit breaks. A flow document that merely spills onto a
    second page has no page units - the page boundary is a rendering decision, not a byte in the file -
    and this tool says "no page units" rather than pretending.
    """
    spans = body_spans(xml)
    if not re.search(r'<w:br w:type="page"', xml):
        return []
    groups, cur = [], []
    for sp in spans:
        cur.append(sp)
        if re.search(r'<w:br w:type="page"', xml[sp[0]:sp[1]]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups if len(groups) > 1 else []


# ---------------------------------------------------------------------------------------------
# carriers: which child carries the failing check
# ---------------------------------------------------------------------------------------------

def _line_boxes(pdf):
    import fitz
    out = []
    with fitz.open(pdf) as d:
        for pno, page in enumerate(d):
            for b in page.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    t = "".join(sp["text"] for sp in ln["spans"]).strip()
                    if t:
                        out.append((pno, ln["bbox"], re.sub(r"\s+", " ", t)))
    return out


def geometry_carrier(name, which):
    """The body child whose text matches the source PDF's most extreme line.

    Used only for checks with no measured construct mapping. The failure is a geometry mismatch
    between the source line and the rendered line, so the paragraph carrying that line is the one
    that must survive; everything else is free to go.
    """
    src = os.path.join(CORPUS, name + ".pdf")
    if not os.path.exists(src):
        return None, "no source PDF to locate the failing line in"
    lines = _line_boxes(src)
    if not lines:
        return None, "source PDF has no text lines"
    key = (lambda r: r[1][2]) if which == "rightmost" else (lambda r: r[1][0])
    lines.sort(key=key, reverse=(which == "rightmost"))
    pno, bbox, text = lines[0]
    return {"line": text, "bbox": list(bbox), "page": pno}, None


def find_child(xml, text):
    """Index of the body child whose text best matches `text`."""
    if not text:
        return None
    spans = body_spans(xml)
    want = re.sub(r"\s+", " ", text).strip()
    best, best_score = None, 0.0
    for i, (s, e, _k) in enumerate(spans):
        have = text_of(xml[s:e])
        if not have:
            continue
        if have == want:
            return i
        # longest common prefix, as a fraction of the shorter string
        n = 0
        for a, b in zip(have, want):
            if a != b:
                break
            n += 1
        score = n / max(1, min(len(have), len(want)))
        if score > best_score:
            best, best_score = i, score
    return best if best_score >= 0.5 else None


# ---------------------------------------------------------------------------------------------
# the reduction itself
# ---------------------------------------------------------------------------------------------

class Guard(object):
    def __init__(self, mode, xml0, scan0, targets, carrier_sig):
        self.mode = mode
        self.scan0 = scan0
        self.targets = targets
        self.carrier_raw = carrier_sig
        self.orig_bytes = len(xml0.encode("utf-8"))
        # A document reduced to no text at all is not a smaller repro of a text-layout failure, it is
        # a different document: 18_displacement, 60_text_column_right_edge, 47_margins and
        # 17_matched_runs all measure where text sits. Only a check carried by a drawing may end up
        # with no text, because a rule exists whether or not there is a word near it.
        self.want_text = bool(text_of(xml0)) and not (set(targets) & {"w:drawing", "wp:anchor"})

    def __call__(self, cand, path_tmp):
        try:
            import lxml.etree as LE
            LE.fromstring(cand.encode("utf-8"))
        except ImportError:
            import xml.etree.ElementTree as ET
            ET.fromstring(cand.encode("utf-8"))
        except Exception as e:
            return False, "does not parse: %s" % e
        if "<w:body" not in cand or "<w:sectPr" not in cand:
            return False, "would remove the body or the section properties"
        if not body_spans(cand):
            return False, "would leave an empty body"
        if self.carrier_raw is not None and self.carrier_raw not in cand:
            return False, "would remove the carrier of the construct"
        if self.want_text and not text_of(cand):
            return False, "would leave no text at all - nothing for the check to measure"
        if self.mode == "strict":
            now = _scan_xml(None, cand)
            for k in self.targets:
                if now.get(k, 0) != self.scan0.get(k, 0):
                    return False, "construct %s would go %d -> %d" % (
                        k, self.scan0.get(k, 0), now.get(k, 0))
        return True, ""


def _scan_xml(tmp_path, xml):
    """google_safe.scan() on a candidate body, without writing a .docx per attempt."""
    out = {}
    for label, _short, pat, _why in google_safe.IGNORED:
        n = len(pat.findall(xml))
        if n:
            out[label] = n
    return out


def reduce_doc(name, strict=False, rows=False, runs=False, allow_multi=False, verbose=True,
               check=None):
    docx = os.path.join(OUT, name + ".docx")
    if not os.path.exists(docx):
        raise SystemExit("no .docx for %s in %s - run corpus-convert.py first" % (name, OUT))
    g = json.load(open(os.path.join(GV, name + ".json"), encoding="utf-8"))
    failed = list(g.get("failed") or [])
    if g.get("status") != "ok":
        raise SystemExit("%s was refused on page count - it has no single failing check" % name)
    if len(failed) != 1 and not allow_multi:
        raise SystemExit("%s fails %d checks (%s) - a reduction needs exactly one, so the failure it "
                         "preserves is unambiguous" % (name, len(failed), ", ".join(failed)))
    check = check or (failed[0] if failed else None)
    if check not in failed:
        raise SystemExit("%s does not fail %s (it fails: %s)" % (
            name, check, ", ".join(failed) or "nothing"))

    names, xml0 = load(docx)
    scan0 = google_safe.scan(docx)
    cen0 = census(xml0)

    # ---- what carries the failure
    targets = CHECK_CONSTRUCT.get(check, [])
    carrier_raw, carrier_note, carrier_idx = None, "", None
    spans = body_spans(xml0)
    if targets:
        if "w:before-page-top" in targets:
            # the defect is w:before AT A PAGE TOP (google_safe.py: 55.15 pt asked, 0.33 rendered),
            # not every w:before in the file, so the carrier is the first child that asks for space
            # before it and starts a page.
            pat = re.compile(r'<w:spacing\b[^>]*w:before="')
            for i, (s, e, _k) in enumerate(spans):
                at_top = (i == 0) or re.search(r'<w:br w:type="page"', xml0[spans[i - 1][0]:spans[i - 1][1]])
                if at_top and pat.search(xml0[s:e]):
                    carrier_idx = i
                    break
            carrier_note = ("w:before-page-top at a page top (google_safe.py: Google renders 0.33 of "
                            "the 55.15 pt asked)")
        if carrier_idx is None:
            pats = [p for lab, _s, p, _w in google_safe.IGNORED if lab in targets]
            for i, (s, e, _k) in enumerate(spans):
                if any(p.search(xml0[s:e]) for p in pats):
                    carrier_idx = i
                    break
            if carrier_note == "":
                carrier_note = "%s (diagnose.CAUSE: measured to break %s)" % (
                    ", ".join(targets), check)
    elif check in GEOM:
        info, err = geometry_carrier(name, GEOM[check])
        if info:
            idx = find_child(xml0, info["line"])
            if idx is not None:
                carrier_idx = idx
                carrier_note = ("no measured construct maps to %s; carrier located by geometry: the "
                                "source line %s at %s" % (check, GEOM[check], info["bbox"]))
    if carrier_idx is None:
        # REDUCING WITHOUT A CARRIER IS NOT A REDUCTION. The first version of this tool had no such
        # refusal, and on 407_id_card_front_back (32_stroke_lines, no mapping in diagnose.CAUSE at the
        # time) it deleted all 16 paragraphs, all 41 drawings and the construct itself, then reported
        # "18.9% smaller" - a smaller document that carries nothing. A run that cannot name what it is
        # preserving must stop, not shrink.
        raise SystemExit(
            "refused: %s fails %s and this tool cannot name the construct that carries it "
            "(no measured mapping in diagnose.CAUSE, and no geometry selector for this check).\n"
            "  Reducing anyway would delete the construct and call the result a repro."
            % (name, check))
    carrier_raw = xml0[spans[carrier_idx][0]:spans[carrier_idx][1]]
    # WHAT "THE CARRIER SURVIVES" MEANS. Protecting the whole body child is too strong once the
    # construct lives in one run of a paragraph that also holds 39 other drawings (407_id_card: one
    # paragraph, 41 anchored shapes). So the protected object is the ELEMENT the construct is written
    # in - the <w:spacing> that asks for space before, or the <w:drawing> itself - and it must survive
    # byte-identical. For a geometry carrier the whole paragraph is protected, because the check is
    # about that line's text and position, not about one element inside it.
    #
    # w:before-page-top IS THE EXCEPTION, AND IT MATTERS. 18_displacement measures how far RUNS sit
    # from their source baselines; a page with a dropped 55 pt gap and no text on it has nothing to
    # displace, so a repro reduced to "one empty paragraph asking for space" would carry the construct
    # and be vacuous. The whole carrier paragraph is therefore protected, text included.
    if targets and "w:before-page-top" not in targets:
        pats = [pp for lab, _s, pp, _w in google_safe.IGNORED if lab in targets]
        sig = None
        for pp in pats:
            m = pp.search(carrier_raw)
            if m:
                a, b = element_span_at(carrier_raw, m.start())
                sig = carrier_raw[a:b]
                break
        carrier_sig = sig if sig else carrier_raw
    else:
        carrier_sig = carrier_raw

    guard = Guard("strict" if strict else "carrier", xml0, scan0, targets, carrier_sig)

    steps = []
    cur = xml0
    tmp = "/scratch/work/.reduce-cand.xml"
    kind_order = {"sectPr": 99}

    def units_of(x):
        """Removable units for this round: pages, tables, paragraphs, and rows inside free tables."""
        u = []
        pg = pages(x)
        for grp in pg:
            u.append(("page", (grp[0][0], grp[-1][1]),
                      "%d children" % len(grp)))
        for s, e, k in body_spans(x):
            if k == "sectPr":
                continue
            u.append((k, (s, e), text_of(x[s:e])[:60] or "(no text)"))
            if rows and k == "tbl":
                for rs, re_ in child_spans((s, e), x, "tr"):
                    u.append(("row", (rs, re_), text_of(x[rs:re_])[:60] or "(empty row)"))
            if runs and k == "p":
                for rs, re_ in child_spans((s, e), x, "r"):
                    u.append(("run", (rs, re_), text_of(x[rs:re_])[:60] or "(no text)"))
        # biggest first: a byte-span sort removes the most per accepted step
        u.sort(key=lambda t: -(t[1][1] - t[1][0]))
        return u

    npass = 0
    while True:
        npass += 1
        changed = False
        for kind, span, label in units_of(cur):
            cand = cut(cur, [span])
            ok, why = guard(cand, tmp)
            if not ok:
                if verbose and kind in ("page", "tbl") and npass == 1:
                    print("    refused %s (%s): %s" % (kind, label[:40], why))
                continue
            steps.append({
                "step": len(steps) + 1,
                "removed": kind,
                "label": label,
                "bytes_document_xml": len(cand.encode("utf-8")),
                "scan": _scan_xml(tmp, cand),
                "census": census(cand),
            })
            cur = cand
            changed = True
            break
        if not changed:
            break
        if len(steps) > 500:
            break

    # ---- write the result
    resdir = os.path.join("/scratch/work/reduced", "strict" if strict else "carrier")
    os.makedirs(resdir, exist_ok=True)
    outpath = os.path.join(resdir, name + ".docx")
    rebuild(docx, outpath, cur)

    # ---- verify what can be verified
    v = verify(docx, outpath, xml0, cur, scan0, targets, carrier_sig)
    return {
        "name": name,
        "check": check,
        "guard": ("strict" if (strict and targets) else "carrier"),
        "guard_requested": "strict" if strict else "carrier",
        "guard_note": ("" if targets else
                       "this check has no scan()-countable construct, so --strict had nothing to "
                       "enforce and the run is a carrier run"),
        "targets": targets,
        "carrier": carrier_note,
        "carrier_index": carrier_idx,
        "carrier_text": text_of(carrier_raw) if carrier_raw else "",
        "carrier_element": (carrier_sig[:200] if carrier_sig else ""),
        "carrier_space_before_twips": (re.findall(r'w:before="(\d+)"', carrier_sig)[0]
                                       if carrier_sig and "w:before" in (carrier_sig or "") else None),
        "census_before": cen0,
        "census_after": census(cur),
        "scan_before": scan0,
        "scan_after": google_safe.scan(outpath),
        "bytes_before": os.path.getsize(docx),
        "bytes_other_parts": _other_parts_bytes(docx),
        "bytes_after": os.path.getsize(outpath),
        "steps": steps,
        "verified": v,
        "reduced_path": outpath,
    }


def _other_parts_bytes(path):
    """Bytes that are NOT word/document.xml: the floor a reduction cannot go below.

    The reduced 72_bank_statement is 4 052 bytes while its document.xml is 1 202, because styles,
    numbering, theme, settings and the section's fonts are separate parts that the removal never
    touches. Reporting only the total would make a 97.4% cut of the document body look like a 38% cut
    of the file.
    """
    with zipfile.ZipFile(path) as z:
        return sum(i.file_size for i in z.infolist() if i.filename != "word/document.xml")


def verify(orig, red, xml0, xml1, scan0, targets, carrier_sig=None):
    """Everything that CAN be checked without Google. Nothing here observes a Google render."""
    v = {}
    try:
        with zipfile.ZipFile(red) as z:
            bad = z.testzip()
            v["zip_valid"] = bad is None
            v["document_xml_present"] = "word/document.xml" in z.namelist()
            same = True
            with zipfile.ZipFile(orig) as zo:
                for n in zo.namelist():
                    if n == "word/document.xml":
                        continue
                    if n not in z.namelist() or z.read(n) != zo.read(n):
                        same = False
                        break
                v["other_parts_byte_identical"] = same and set(z.namelist()) == set(zo.namelist())
    except Exception as e:
        v["zip_valid"] = False
        v["zip_error"] = str(e)
    try:
        import lxml.etree as LE
        LE.fromstring(xml1.encode("utf-8"))
        v["document_xml_parses"] = "lxml"
    except ImportError:
        import xml.etree.ElementTree as ET
        ET.fromstring(xml1.encode("utf-8"))
        v["document_xml_parses"] = "ElementTree"
    except Exception as e:
        v["document_xml_parses"] = False
        v["parse_error"] = str(e)
    try:
        import docx as _d
        d = _d.Document(red)
        v["python_docx_opens"] = True
        v["python_docx_paragraphs"] = len(d.paragraphs)
        v["python_docx_tables"] = len(d.tables)
    except Exception as e:
        v["python_docx_opens"] = False
        v["python_docx_error"] = "%s: %s" % (type(e).__name__, e)
    # the only claim about the construct this tool makes
    now = _scan_xml(red, xml1)
    v["construct_counts_before"] = scan0
    v["construct_counts_after"] = now
    v["target_constructs"] = targets
    v["target_constructs_identical"] = all(now.get(k, 0) == scan0.get(k, 0) for k in targets) \
        if targets else None
    # The construct element itself, byte for byte, is still in the file that was written to disk.
    # Checked against the WRITTEN bytes, not against the string the reducer held in memory.
    if carrier_sig:
        v["carrier_element_present_in_written_file"] = carrier_sig in xml1
        v["carrier_element_bytes"] = len(carrier_sig.encode("utf-8"))
    # The reduction is a set of deletions from the original byte string, so every byte that survived
    # is in the same relative order: b must be a SUBSEQUENCE of a, and the deleted text must be
    # recoverable as the complement. A re-serialisation (prefix renaming, attribute reordering) would
    # break this, which is why it is checked rather than assumed.
    v["surviving_text_is_a_subsequence_of_the_original"] = _is_subsequence(xml1, xml0)
    return v


def _is_subsequence(small, big):
    """True if `small` can be obtained from `big` by deletions only."""
    i = 0
    for ch in big:
        if i < len(small) and small[i] == ch:
            i += 1
            if i == len(small):
                return True
    return i == len(small)


def lo_render(docx, tag):
    """Render one .docx through LibreOffice. Returns (pdf_path or None, pages, reason).

    A private user profile per call: two soffice processes sharing one profile is the classic way this
    silently produces no file, and it did - the first of two renders in a run returned nothing while
    the second worked. The profile is per call, not per run, so the two never meet.
    """
    exe = SOFFICE if os.path.exists(SOFFICE) else "soffice"
    outdir = "/tmp/lo-reduce-%s" % tag
    prof = "file:///tmp/lo-profile-%s" % tag
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(docx))[0]
    for attempt in (1, 2):
        try:
            subprocess.run([exe, "-env:UserInstallation=" + prof, "--headless", "--norestore",
                            "--convert-to", "pdf", "--outdir", outdir, docx],
                           capture_output=True, text=True, timeout=240)
        except Exception as e:
            return None, None, "soffice failed: %s" % e
        pdf = os.path.join(outdir, base + ".pdf")
        if os.path.exists(pdf) and os.path.getsize(pdf) > 512:
            try:
                import fitz
                with fitz.open(pdf) as d:
                    return pdf, d.page_count, ""
            except Exception as e:
                return None, None, "render is not a readable PDF: %s" % e
    return None, None, "LibreOffice produced no PDF (the .docx did not convert)"


def _text_pos(pdf, text, limit=60):
    """(page, x0, y0) of the first line in `pdf` whose text contains `text`."""
    import fitz
    want = re.sub(r"\s+", " ", text).strip()[:limit]
    if not want:
        return None
    # A paragraph's text can span several rendered lines, and a renderer may hyphenate or re-space it,
    # so the prefix is tried at decreasing lengths instead of demanding the whole paragraph on one line.
    probes = [want[:n] for n in (60, 40, 30, 22, 16, 12) if n <= len(want)]
    with fitz.open(pdf) as d:
        lines = []
        for pno, page in enumerate(d):
            for b in page.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    t = re.sub(r"\s+", " ", "".join(sp["text"] for sp in ln["spans"])).strip()
                    if t:
                        lines.append((pno, ln["bbox"], t))
    for probe in probes:
        for pno, bbox, t in lines:
            if probe in t:
                return pno, round(bbox[0], 1), round(bbox[1], 1)
    return None


def lo_compare(name, orig_docx, red_docx, carrier_text):
    """What LibreOffice can and cannot say about a reduced document.

    IT CANNOT SCORE IT. verify_google.py compares a render against the SOURCE PDF, and the source PDF
    is the whole original document - a reduced .docx has had most of that content deleted on purpose,
    so it fails 04_chars_missing, 17_matched_runs, 45_char_accuracy and friends by construction. That
    score measures the reduction, not the defect. Running it and reporting "9 checks now fail" would be
    a true number used as a false claim, so it is not reported.

    IT CAN SAY: the file still converts; the page count the local renderer produces; and where the
    carrier text lands, against where it landed before. That is a real measurement of "the reduction
    did not disturb the thing that carries the failure", within the one renderer available locally.
    """
    o_pdf, o_pages, o_why = lo_render(orig_docx, "orig")
    r_pdf, r_pages, r_why = lo_render(red_docx, "red")
    out = {
        "original_converts": o_pdf is not None, "original_pages": o_pages,
        "reduced_converts": r_pdf is not None, "reduced_pages": r_pages,
        "why": "; ".join(x for x in (o_why, r_why) if x),
        "note": ("LibreOffice honours the constructs Google drops, so a clean local render is not "
                 "evidence about Google; it only shows the reduced file is still a renderable document."),
    }
    if o_pdf and r_pdf and carrier_text:
        po = _text_pos(o_pdf, carrier_text)
        pr = _text_pos(r_pdf, carrier_text)
        out["carrier_text"] = carrier_text[:60]
        out["carrier_pos_original"] = po
        out["carrier_pos_reduced"] = pr
        if po and pr:
            out["carrier_drift_pt"] = [round(pr[1] - po[1], 1), round(pr[2] - po[2], 1)]
    return out


# ---------------------------------------------------------------------------------------------

def candidates():
    rows = []
    for f in sorted(os.listdir(GV)):
        if not f.endswith(".json"):
            continue
        try:
            g = json.load(open(os.path.join(GV, f), encoding="utf-8"))
        except Exception:
            continue
        if g.get("status") != "ok" or len(g.get("failed") or []) != 1:
            continue
        name = f[:-5]
        docx = os.path.join(OUT, name + ".docx")
        pdf = os.path.join(CORPUS, name + ".pdf")
        pages_n = None
        if os.path.exists(pdf):
            try:
                import fitz
                with fitz.open(pdf) as d:
                    pages_n = d.page_count
            except Exception:
                pass
        rows.append((name, g["failed"][0], pages_n,
                     os.path.getsize(docx) if os.path.exists(docx) else None))
    print("  %-44s %-28s %5s %8s" % ("document", "single failing check", "pages", "docx"))
    print("  " + "-" * 90)
    for n, c, p, b in rows:
        print("  %-44s %-28s %5s %8s" % (n, c, p if p is not None else "?", b or "-"))
    print("\n  %d documents fail exactly one check" % len(rows))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("name", nargs="?")
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--strict", action="store_true", help="require identical scan() counts")
    ap.add_argument("--rows", action="store_true", help="also drop table rows")
    ap.add_argument("--runs", action="store_true",
                    help="also drop individual runs inside a paragraph (keeps the construct element)")
    ap.add_argument("--lo", action="store_true", help="render both files in LibreOffice and re-score")
    ap.add_argument("--allow-multi", action="store_true",
                    help="allow a document that fails more than one check (machinery demos only)")
    ap.add_argument("--check", help="which failing check to preserve (needs --allow-multi if >1)")
    ap.add_argument("--json", help="write the run record here")
    a = ap.parse_args(argv)
    if a.candidates:
        return candidates()
    if not a.name:
        print(__doc__.strip().split("\n\n")[0])
        return 2
    rec = reduce_doc(a.name, strict=a.strict, rows=a.rows, runs=a.runs,
                     allow_multi=a.allow_multi, check=a.check)
    if a.lo:
        rec["libreoffice"] = lo_compare(a.name, os.path.join(OUT, a.name + ".docx"),
                                        rec["reduced_path"], rec.get("carrier_text") or "")
    cb, ca = rec["census_before"], rec["census_after"]
    print("  %s  (%s, guard=%s%s)" % (rec["name"], rec["check"], rec["guard"],
                                      "" if not rec.get("guard_note") else " - " + rec["guard_note"]))
    print("    carrier : %s" % (rec["carrier"] or "NONE IDENTIFIED"))
    print("    bytes   : %d -> %d  (%.1f%% smaller)" % (
        rec["bytes_before"], rec["bytes_after"],
        100.0 * (1 - rec["bytes_after"] / float(rec["bytes_before"]))))
    print("    document.xml bytes: %d -> %d" % (cb["bytes_document_xml"], ca["bytes_document_xml"]))
    print("    paragraphs: %d -> %d   tables: %d -> %d   rows: %d -> %d   pages: %d -> %d" % (
        cb["paragraphs"], ca["paragraphs"], cb["tables"], ca["tables"],
        cb["table_rows"], ca["table_rows"],
        1 + cb["explicit_page_breaks"], 1 + ca["explicit_page_breaks"]))
    print("    scan before: %s" % json.dumps(rec["scan_before"], sort_keys=True))
    print("    scan after : %s" % json.dumps(rec["scan_after"], sort_keys=True))
    for s in rec["steps"]:
        print("      %2d. drop %-4s %-40s scan=%s" % (
            s["step"], s["removed"], s["label"][:40], json.dumps(s["scan"], sort_keys=True)))
    for k in ("zip_valid", "document_xml_parses", "python_docx_opens",
              "other_parts_byte_identical", "target_constructs_identical"):
        if k in rec["verified"]:
            print("    %-30s %s" % (k, rec["verified"][k]))
    if "libreoffice" in rec:
        r = rec["libreoffice"]
        print("    %-30s %s" % ("libreoffice converts", "original=%s reduced=%s  pages %s/%s" % (
            r["original_converts"], r["reduced_converts"], r["original_pages"], r["reduced_pages"])))
        if r.get("carrier_pos_original") and r.get("carrier_pos_reduced"):
            print("    %-30s %s -> %s  drift=%s pt" % (
                "carrier text position", r["carrier_pos_original"], r["carrier_pos_reduced"],
                r.get("carrier_drift_pt")))
        elif r.get("carrier_text"):
            print("    %-30s original=%s reduced=%s" % (
                "carrier text found", r.get("carrier_pos_original"), r.get("carrier_pos_reduced")))
        if r.get("why"):
            print("    %-30s %s" % ("libreoffice note", r["why"]))
    print("    NOT VERIFIED: whether this file still fails %s in Google Docs." % rec["check"])
    if a.json:
        json.dump(rec, open(a.json, "w", encoding="utf-8"), indent=1, sort_keys=True)
        print("    record: %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
