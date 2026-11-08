#!/usr/bin/env python3
"""Verify a finding against the PDF before anyone fixes anything.

WHY THIS EXISTS
    On 7 Nov the pipeline reported nine problems across five documents. Two of them were
    false alarms: a "lost table" and a "lost chart" on a page that had neither. Both were
    fixed at the source, but the lesson is the one that matters here - a finding is a
    claim, and a claim is worth nothing until it has been checked against the page.

    So no finding is fixed until it has been verified. One verification per finding, not
    one per pass: a finding verified three times is the same answer three times.

TWO KINDS OF FINDING, TWO WAYS TO CHECK
    measure   a number the tools produced - reading order 88.5 %, page count 2 vs 1,
              position off by 197 pt. Verified by re-deriving it from the PDF with code
              that does not share the tool's path.
    visual    something the eye saw on the side-by-side image - "this line wraps", "this
              label sits lower", "this text is missing". Verified by going to the PDF and
              measuring the specific claim.

    The eye records a STRUCTURED claim, not a sentence, because a sentence cannot be
    checked by a program and an unchecked finding is what this file exists to prevent:

        wraps:<text>     the PDF has <text> on one line and the render puts it on more
        breaks:<text>    the same number of lines, broken at a different word
        count:<text>     how many times the PDF holds <text>, against the render
        moved:<text>     the render puts <text> more than the x or y tolerance from the PDF
        missing:<text>   the PDF has <text> and the render does not
        extra:<text>     the render has <text> the PDF does not
        order            the rows are out of sequence
        pagecount        the render has more or fewer pages than the PDF
        overlap          the render overlaps lines the PDF keeps apart
        shapes           the render has fewer shapes than the PDF

THE FINDINGS FILE (tab separated, one line per finding)
    id  document  page  kind  claim
    F1  303_discharge_summary  1  measure  order
    F2  303_discharge_summary  1  visual   wraps:WARNING SIGNS
    F3  350_question_paper     1  visual   moved:[08]
    F4  350_question_paper     1  measure  pagecount

USAGE
    python3 verify.py --findings F.tsv --corpus DIR --out DIR --rendered DIR

EXIT
    0  every finding was verified
    1  at least one finding was REFUTED - it is not a defect, do not fix it
    2  a finding could not be checked, or the input is wrong
"""

import argparse
import difflib
import os
import sys


def rows(lines):
    """Lines grouped into the visual rows a reader traverses, band by band."""
    out = []
    for l in sorted(lines, key=lambda l: (l.get("base", l["bbox"][3]), l["bbox"][0])):
        y = l.get("base", l["bbox"][3])
        tol = max(1.5, 0.3 * (l.get("size") or 10))
        if out and abs(out[-1][0] - y) <= tol:
            out[-1][1].append(l)
        else:
            out.append([y, [l]])
    res = []
    for _y, ls in out:
        ls.sort(key=lambda l: l["bbox"][0])
        t = " ".join(" ".join(l["text"].split()) for l in ls).strip()
        if t:
            res.append(t)
    return res


def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            if t:
                out.append({"text": t, "bbox": l["bbox"],
                            "base": l["bbox"][3], "size": l["spans"][0]["size"]})
    return out


def check_measure(claim, ref, got, ref_lines, got_lines, ref_doc, got_doc):
    """Re-derive a number the tools produced, without using the tool."""
    c = claim.split(":", 1)[0].strip()
    if c == "order":
        a, b = rows(ref_lines), rows(got_lines)
        import difflib
        share = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
        return ("REFUTED" if share >= 1.0 else "VERIFIED",
                "%d rows in the PDF, %d in the render, %.1f %% in sequence"
                % (len(a), len(b), share * 100))
    if c == "pagecount":
        if ref_doc.page_count != got_doc.page_count:
            return "VERIFIED", "%d pages in the PDF, %d in the render" % (
                ref_doc.page_count, got_doc.page_count)
        return "REFUTED", "both have %d pages" % ref_doc.page_count
    if c == "shapes":
        # A count alone is blind to the two things that actually go wrong with a drawing.
        # On 352_certificate_ornate_border the page draws two page-sized border rectangles and
        # the render draws twelve corner curls instead: 12 against 12, so a count called it
        # refuted while the border was gone. On 371 the seal's two rings come out as 16 x 9 pt
        # blobs: 2 against 2, refuted again, with the ring missing.
        #
        # So a shape is also classified by SIZE. BIG_FRAC is a CLASSIFICATION bound, not a
        # positional tolerance, in the same sense as RULE_MAX_PT below: a frame or a seal ring
        # covers a real fraction of the paper, a curl or a glyph does not, and nothing here is
        # compared against the other side's coordinate. A tenth of a per cent of an A4 page is
        # 50 pt2 - 7 x 7 pt - which no corner ornament reaches and every border, seal and panel
        # outline exceeds.
        BIG_FRAC = 0.001

        def shapes(pg):
            n = big = 0
            area = max(1.0, pg.rect.width * pg.rect.height)
            for d in pg.get_drawings():
                r = d["rect"]
                if r.width >= 1.5 and r.height >= 1.5:
                    n += 1
                    if (r.width * r.height) >= BIG_FRAC * area:
                        big += 1
            return n, big
        a, b = shapes(ref), shapes(got)
        if a[0] != b[0] or a[1] != b[1]:
            return ("VERIFIED",
                    "%d shapes in the PDF (%d large), %d in the render (%d large)"
                    % (a[0], a[1], b[0], b[1]))
        return ("REFUTED",
                "%d shapes in the PDF, %d in the render, %d large on both sides"
                % (a[0], b[0], a[1]))
    return "UNVERIFIABLE", "no measure check for '%s'" % c


def check_visual(claim, ref_lines, got_lines, ref, got):
    """Go to the PDF and measure the specific thing the eye said it saw."""
    if claim.startswith("wraps:"):
        # A wrapped line's first fragment starts the same way as the whole line, so
        # matching the start proves nothing. Containment proves nothing either: a render
        # line that holds the PDF's line AND the line after it contains the first one
        # completely, and the old check called that "on one line too".
        #
        # What the reader experiences is the line COUNT for that block of text. So the
        # PDF's line and the one below it are taken together, and the render is asked how
        # many lines it spends on the same words:
        #
        #   the render uses the same number      -> nothing wrong
        #   fewer lines than the PDF             -> the render MERGED two lines into one
        #   more lines than the PDF              -> the render WRAPPED one line into two
        needle = claim.split(":", 1)[1].strip()
        rl = [l for l in ref_lines if l["text"].strip().startswith(needle)]
        if not rl:
            rl = [l for l in ref_lines if needle in l["text"]]
        if not rl:
            near = difflib.get_close_matches(needle, [l["text"] for l in ref_lines], n=1, cutoff=0.4)
            hint = (" - did you mean %r?" % near[0][:60]) if near else ""
            return "UNVERIFIABLE", "the PDF has no line starting %r%s" % (needle[:40], hint)

        first = min(rl, key=lambda l: l["base"])
        block = [first]
        below = [l for l in ref_lines if l["base"] > first["base"] + 0.5]
        if below:
            block.append(min(below, key=lambda l: l["base"]))
        words = " ".join(" ".join(l["text"].split()) for l in block).split()

        # how many render lines the block's words are spent on
        spans = 0
        i = 0
        for l in got_lines:
            if i >= len(words):
                break
            t = " ".join(l["text"].split())
            hit = False
            while i < len(words) and words[i] in t:
                i += 1
                hit = True
            if hit:
                spans += 1
        if i < len(words):
            return "UNVERIFIABLE", "could not follow %d of %d words through the render" % (
                len(words) - i, len(words))

        if spans == len(block):
            return "REFUTED", "%d line(s) on both sides" % len(block)
        if spans < len(block):
            return "VERIFIED", "the PDF has %d line(s); the render MERGES them into %d" % (
                len(block), spans)
        return "VERIFIED", "the PDF has %d line(s); the render WRAPS them into %d" % (
            len(block), spans)

    if claim.startswith("breaks:"):
        # The same number of lines, broken at a different word. Neither a wrap (more
        # lines) nor a merge (fewer) - the reader gets the same shape with the wrong
        # break in it, which is what 303_discharge_summary does to its WARNING SIGNS line.
        needle = claim.split(":", 1)[1].strip()
        rl = [l for l in ref_lines if l["text"].strip().startswith(needle)]
        if not rl:
            rl = [l for l in ref_lines if needle in l["text"]]
        if not rl:
            return "UNVERIFIABLE", "the PDF has no line starting %r" % needle[:40]
        first = min(rl, key=lambda l: l["base"])
        words = " ".join(first["text"].split()).split()
        if not words:
            return "UNVERIFIABLE", "the PDF's line is empty"
        # the last word of the PDF's line must end a render line, and the next word of
        # the PDF must start the following one - otherwise the break moved
        last = words[-1]
        rl_hit = [i for i, l in enumerate(got_lines) if " ".join(l["text"].split()).endswith(last)]
        if not rl_hit:
            return "VERIFIED", "the PDF's line ends at %r and no render line does" % last
        i = rl_hit[0]
        if i + 1 < len(got_lines):
            nxt = " ".join(got_lines[i + 1]["text"].split())
            pdf_next = [l for l in ref_lines if l["base"] > first["base"] + 0.5]
            if pdf_next:
                pn = " ".join(min(pdf_next, key=lambda l: l["base"])["text"].split())
                if pn and not nxt.startswith(pn.split()[0]):
                    return "VERIFIED", "the PDF breaks after %r; the render continues %r" % (
                        last, nxt[:40])
        return "REFUTED", "the line breaks in the same place"

    if claim == "rules":
        # A rule is a thin filled rectangle: a table border, a box, a row divider. Every
        # other claim here is about TEXT, so a page whose text is perfect and whose rules
        # are wrong had no way to say so - 351_omr_answer_sheet draws its bubble grid as
        # bare circles and the render put a ruled table round it, and "extra:1" could only
        # count lines containing the character 1. The eye saw it and the vocabulary could
        # not, which is the third of the three causes PIPELINE.md names.
        # A stroke of width w reaches the page as a filled band about w tall: the PDF here
        # draws 58's rules as zero-height stroked lines and the renderer exports each as a
        # filled rect 0.4 to 1.2 pt high. The old cut-off was exactly 1.2, and the render
        # reports 1.2000000476837158 for a 1.2 pt border, so the widest rule on the page
        # was excluded from the render's count and the page was charged with a missing
        # rule it did not miss. RULE_MAX_PT is a CLASSIFICATION bound for "this rectangle
        # is a line, not a box", not a positional tolerance: nothing here is compared
        # against the other side's coordinate. A box is many points thick, so a bound half
        # a point above the widest hairline the writer emits separates the two cleanly.
        RULE_MAX_PT = 1.5

        def rules(pg):
            n = 0
            for d in pg.get_drawings():
                r = d["rect"]
                horizontal = r.height <= RULE_MAX_PT and r.width >= 4.0
                vertical = r.width <= RULE_MAX_PT and r.height >= 4.0
                if horizontal or vertical:
                    n += 1
            return n
        a, b = rules(ref), rules(got)
        # The claim is "the rules on this page do not match the page's", not "there are
        # too many of them". It was written one-way (b > a) when 351 was the case that
        # needed it - a ruled grid drawn round a bubble sheet that the page leaves
        # unruled. A check that can only see one direction of a difference turns every
        # MISSING rule into a false pass, which is the failure PIPELINE.md names as "the
        # verifier's check is wrong". Both directions now count.
        if a == b:
            return "REFUTED", "%d rules on both sides" % a
        return ("VERIFIED",
                "%d rules in the PDF, %d in the render" % (a, b))

    if claim.startswith("moved:"):
        # The WORST offset, not the first. "[08]" appears 25 times on 350_question_paper;
        # comparing the first of each side gave 4.3 pt and called it verified, while the
        # real damage is that six are gone and the rest are spread 36 pt apart where the
        # PDF puts them 26 pt apart. The first occurrence is the least useful one to see.
        needle = claim.split(":", 1)[1].strip()
        rl = [l for l in ref_lines if l["text"].strip().startswith(needle)]
        gl = [l for l in got_lines if l["text"].strip().startswith(needle)]
        if not rl or not gl:
            return "UNVERIFIABLE", "%r is not on both sides" % needle[:40]
        if len(rl) == 1 and len(gl) == 1:
            # Both axes, not just y. A line can sit on the page's own baseline and still be
            # in the wrong place: 303's WARNING SIGNS line is 2.8 pt low - inside the 3.0 pt
            # y tolerance - and 11.4 pt to the LEFT, because a right-aligned paragraph with
            # no right indent is flushed to the paper's edge instead of the page's own
            # x=28.0. Checking y alone called that REFUTED and the eye looked wrong when it
            # was right. The tolerances are the ones every gate uses: x 1.5, y 3.0.
            d = gl[0]["base"] - rl[0]["base"]
            dx = gl[0]["bbox"][0] - rl[0]["bbox"][0]
            if abs(d) > 3.0 or abs(dx) > 1.5:
                return ("VERIFIED",
                        "%r at x=%.1f y=%.1f in the PDF, x=%.1f y=%.1f in the render - "
                        "%.1f pt down, %.1f pt across"
                        % (needle[:30], rl[0]["bbox"][0], rl[0]["base"],
                           gl[0]["bbox"][0], gl[0]["base"], d, dx))
            return ("REFUTED",
                    "%r at x=%.1f y=%.1f in the PDF, x=%.1f y=%.1f in the render - within "
                    "tolerance on both axes"
                    % (needle[:30], rl[0]["bbox"][0], rl[0]["base"],
                       gl[0]["bbox"][0], gl[0]["base"]))
        ry = [l["base"] for l in sorted(rl, key=lambda l: l["base"])]
        gy = [l["base"] for l in sorted(gl, key=lambda l: l["base"])]
        n = min(len(ry), len(gy))
        worst = 0.0
        for i in range(n):
            worst = max(worst, abs(gy[i] - ry[i]))
        if len(ry) != len(gy):
            return "VERIFIED", "%d in the PDF, %d in the render, worst offset %.1f pt" % (
                len(ry), len(gy), worst)
        return ("VERIFIED" if worst > 3.0 else "REFUTED",
                "%d on both sides, worst offset %.1f pt" % (len(ry), worst))

    if claim.startswith("missing:"):
        needle = claim.split(":", 1)[1].strip()
        rl = [l for l in ref_lines if needle in l["text"]]
        gl = [l for l in got_lines if needle in l["text"]]
        if not rl:
            near = difflib.get_close_matches(needle, [l["text"] for l in ref_lines],
                                             n=1, cutoff=0.4)
            hint = (" - the closest line in the PDF is %r" % near[0][:60]) if near else ""
            return "UNVERIFIABLE", "the PDF has no %r either%s" % (needle[:40], hint)
        return ("REFUTED" if gl else "VERIFIED",
                "%d line(s) in the PDF, %d in the render" % (len(rl), len(gl)))

    if claim.startswith("extra:"):
        needle = claim.split(":", 1)[1].strip()
        rl = [l for l in ref_lines if needle in l["text"]]
        gl = [l for l in got_lines if needle in l["text"]]
        return ("REFUTED" if rl or not gl else "VERIFIED",
                "%d line(s) in the PDF, %d in the render" % (len(rl), len(gl)))

    if claim.startswith("count:"):
        # How many times the PDF holds this text against how many times the render does.
        # On 350_question_paper the PDF has 25 marks and the render 19, and no claim could
        # say so - moved: compared the first of each and reported 4.3 pt.
        needle = claim.split(":", 1)[1].strip()
        rn = sum(1 for l in ref_lines if l["text"].strip().startswith(needle))
        gn = sum(1 for l in got_lines if l["text"].strip().startswith(needle))
        if rn == 0:
            return "UNVERIFIABLE", "the PDF has no %r either" % needle[:40]
        if gn == rn:
            return "REFUTED", "%d of %r on both sides" % (rn, needle[:24])
        return "VERIFIED", "%d of %r in the PDF, %d in the render" % (rn, needle[:24], gn)

    if claim.startswith("overlap"):
        def pairs(ls):
            n = 0
            for i in range(len(ls)):
                x0, y0, x1, y1 = ls[i]["bbox"]
                for j in range(i + 1, len(ls)):
                    a0, b0, a1, b1 = ls[j]["bbox"]
                    if x0 < a1 and a0 < x1 and y0 < b1 and b0 < y1:
                        if min(x1, a1) - max(x0, a0) > 1.0 and min(y1, b1) - max(y0, b0) > 1.0:
                            n += 1
            return n
        a, b = pairs(ref_lines), pairs(got_lines)
        return ("REFUTED" if b <= a else "VERIFIED",
                "%d overlapping pairs in the PDF, %d in the render" % (a, b))

    if claim.split(":")[0].strip() == "pagecount":
        return "UNVERIFIABLE", "pagecount is a measure finding, not a visual one"
    return "UNVERIFIABLE", "no visual check for '%s'" % claim[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rendered", required=True)
    ap.add_argument("--json", default="",
                    help="write the per-finding verdicts here, so the decision"
                         " can be made on verified data and not on raw tool output")
    a = ap.parse_args()

    try:
        import pymupdf
    except ImportError:
        print("verify: needs PyMuPDF")
        return 2

    if not os.path.isfile(a.findings):
        print("verify: no findings file at %s" % a.findings)
        return 2

    findings = []
    seen = set()
    for line in open(a.findings, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 5:
            continue
        # One verification per finding. The same problem listed twice is one finding.
        key = (f[1], f[2], f[3], f[4])
        if key in seen:
            print("skip  %-4s (already verified - same problem)" % f[0])
            continue
        seen.add(key)
        findings.append(f[:5])

    if not findings:
        print("verify: no findings to check")
        return 2

    verified = refuted = unverifiable = 0
    decided = []
    for fid, doc, page, kind, claim in findings:
        pdf = os.path.join(a.corpus, doc + ".pdf")
        rend = os.path.join(a.rendered, doc + ".pdf")
        if not os.path.isfile(pdf) or not os.path.isfile(rend):
            decided.append({"id": fid, "document": doc, "page": int(page), "kind": kind,
                            "claim": claim, "verdict": "UNVERIFIABLE",
                            "why": "a file is missing"})
            print("UNVERIFIABLE  %-4s %s p%s  %s (a file is missing)"
                  % (fid, doc[:34], page, claim[:44]))
            unverifiable += 1
            continue
        try:
            with pymupdf.open(pdf) as r, pymupdf.open(rend) as g:
                pi = max(0, int(page) - 1)
                # A pagecount claim is about the document, not about a page. The eye sees
                # the extra sheet and records it against that page, which is the right
                # place to record it - but that page does not exist in the PDF, so the
                # guard below rejected the one claim the eye was most sure about.
                whole_doc = claim.split(":")[0].strip() == "pagecount"
                if not whole_doc and (pi >= r.page_count or pi >= g.page_count):
                    decided.append({"id": fid, "document": doc, "page": int(page),
                                    "kind": kind, "claim": claim,
                                    "verdict": "UNVERIFIABLE",
                                    "why": "page not on both sides"})
                    print("UNVERIFIABLE  %-4s %s p%s  %s (page not on both sides)"
                          % (fid, doc[:34], page, claim[:44]))
                    unverifiable += 1
                    continue
                rp = r[min(pi, r.page_count - 1)]
                gp = g[min(pi, g.page_count - 1)]
                rlines, glines = lines_of(rp), lines_of(gp)
                if kind == "measure":
                    verdict, why = check_measure(claim, rp, gp, rlines, glines, r, g)
                else:
                    verdict, why = check_visual(claim, rlines, glines, rp, gp)
        except Exception as exc:
            decided.append({"id": fid, "document": doc, "page": int(page), "kind": kind,
                            "claim": claim, "verdict": "UNVERIFIABLE",
                            "why": type(exc).__name__})
            print("UNVERIFIABLE  %-4s %s p%s  %s (%s)"
                  % (fid, doc[:34], page, claim[:44], type(exc).__name__))
            unverifiable += 1
            continue

        decided.append({"id": fid, "document": doc, "page": int(page), "kind": kind,
                        "claim": claim, "verdict": verdict, "why": why})
        mark = {"VERIFIED": "VERIFIED", "REFUTED": "REFUTED",
                "UNVERIFIABLE": "UNVERIFIABLE"}[verdict]
        print("%-12s  %-4s %-34s p%-2s %-6s %-28s %s"
              % (mark, fid, doc[:34], page, kind, claim[:28], why[:70]))
        if verdict == "VERIFIED":
            verified += 1
        elif verdict == "REFUTED":
            refuted += 1
        else:
            unverifiable += 1

    if a.json:
        import json as _json
        _json.dump(decided, open(a.json, "w"), indent=1)

    print("")
    print("%d findings: %d verified, %d refuted, %d unverifiable"
          % (len(findings), verified, refuted, unverifiable))
    if refuted:
        print("A refuted finding is not a defect. Do not fix it.")
        return 1
    if unverifiable:
        print("An unverifiable finding needs a structured claim before it can be acted on.")
        return 2
    print("every finding was checked against the PDF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
