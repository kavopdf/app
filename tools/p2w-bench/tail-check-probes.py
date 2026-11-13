#!/usr/bin/env python3
"""tail-check-probes.py - reproduce every constructed claim in the 13 Nov tail report.

No corpus, no network, no Drive: every document is built from nothing with PyMuPDF and
measured by verify_google.compare(). Run it from tools/p2w-bench, or with that directory on
PYTHONPATH:

    python3 tail-check-probes.py            # all probes, prints PASS/FAIL per claim
    python3 tail-check-probes.py --store    # also re-count the 211-row store claims

Each probe asserts the behaviour the report claims, so a line reading FAIL is a claim the
tree no longer supports. Exit status is the number of failed claims.
"""
import itertools, json, os, sys, tempfile, warnings
warnings.filterwarnings("ignore")
HERE = os.environ.get("P2W_BENCH", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import fitz
import verify_google as V

D = tempfile.mkdtemp(prefix="tail-probe-")
N = itertools.count()
BAD = []


def doc(fn, w=595, h=842):
    d = fitz.open()
    fn(d.new_page(width=w, height=h))
    p = os.path.join(D, "d%03d.pdf" % next(N))
    d.save(p)
    d.close()
    return p


def claim(name, cond, detail=""):
    print("%-4s %s%s" % ("ok" if cond else "FAIL", name, ("  [%s]" % detail) if detail else ""))
    if not cond:
        BAD.append(name)


def verdict(a, b, check):
    r = V.compare(a, b)
    c = r["checks"][check]
    return (check in r["failed"]), c


# ---------------------------------------------------------------- 42_alignment_mix
def lines(n):
    def f(p):
        for i in range(n):
            p.insert_text((72, 80 + i * 20), "body line %02d of the paragraph" % i, fontsize=10)
    return f


fired, c = verdict(doc(lines(24)), doc(lines(16)), "42_alignment_mix")
claim("42: 24 left lines vs 16 left lines, same alignment -> PASS", not fired, str(c))

def pricelist(right):
    def f(p):
        p.insert_text((72, 80), "Price list", fontsize=11)
        for i in range(12):
            p.insert_text((72, 110 + i * 20), "Item %02d description" % i, fontsize=10)
            p.insert_text((440 if right else 72, 110 + i * 20), "%d.00" % (i + 1), fontsize=10)
    return f


fired, c = verdict(doc(pricelist(True)), doc(pricelist(False)), "42_alignment_mix")
claim("42: right-aligned amounts -> flush left -> FAIL", fired, str(c))
fired, c = verdict(doc(pricelist(True)), doc(pricelist(True)), "42_alignment_mix")
claim("42: identical price list -> PASS", not fired, str(c))

# ---------------------------------------------------------------- 43_within_10pt_x
def body(dx=0.0):
    def f(p):
        for i, s in enumerate(["Invoice number 12345", "Total amount 4,500",
                               "Description of the goods"]):
            p.insert_text((72 + dx, 100 + i * 30), s, fontsize=11)
    return f


fired, c = verdict(doc(body()), doc(body(4.3)), "43_within_10pt_x")
claim("43: uniform +4.3 pt shift -> FAIL (21's case, folded in)", fired, str(c))
fired, c = verdict(doc(body()), doc(body(2.0)), "43_within_10pt_x")
claim("43: uniform +2.0 pt shift -> PASS", not fired, str(c))
fired, c = verdict(doc(body()), doc(body(30)), "43_within_10pt_x")
claim("43: uniform +30 pt shift -> FAIL", fired, str(c))
fired, c = verdict(doc(body()), doc(body()), "43_within_10pt_x")
claim("43: identical -> PASS", not fired, str(c))

# ---------------------------------------------------------------- 13_text_colours
def colours(last, extra=False):
    def f(p):
        cs = [(0.8, 0, 0), (0, 0.5, 0), (0, 0, 0.8)]
        for i in range(3):
            p.insert_text((72, 100 + i * 30), "line %d" % i, fontsize=11, color=cs[i])
        p.insert_text((72, 200), "tail", fontsize=11, color=last)
        if extra:
            p.insert_text((72, 230), "extra", fontsize=11, color=(0.1, 0.7, 0.1))
    return f


fired, c = verdict(doc(colours((0, 0, 0))), doc(colours((0.9, 0.9, 0))), "13_text_colours")
claim("13: one span recoloured to a NEW colour (count unchanged) -> FAIL", fired, str(c))
fired, c = verdict(doc(colours((0, 0, 0))), doc(colours((0, 0, 0))), "13_text_colours")
claim("13: identical -> PASS", not fired, str(c))
fired, c = verdict(doc(colours((0, 0, 0))), doc(colours((0, 0, 0), True)), "13_text_colours")
claim("13: render ADDS a colour -> PASS", not fired, str(c))
fired, c = verdict(doc(colours((0, 0, 0))), doc(colours((0.02, 0.02, 0.02))), "13_text_colours")
claim("13: near-identical colour (dE00 < 6) -> PASS", not fired, str(c))

# ---------------------------------------------------------------- 36_underline_rules
def underlined(p):
    p.insert_text((72, 100), "underlined words")
    p.draw_line((72, 103), (172, 103), color=(0, 0, 0), width=0.6)


def underlined_none(p):
    p.insert_text((72, 100), "underlined words")


def underlined_band(p):
    p.insert_text((72, 100), "underlined words")
    p.draw_rect(fitz.Rect(72, 102.5, 172, 103.4), color=None, fill=(0, 0, 0))


fired, c = verdict(doc(underlined), doc(underlined_none), "36_underline_rules")
claim("36: underline dropped -> FAIL", fired, str(c))
fired, c = verdict(doc(underlined), doc(underlined_band), "36_underline_rules")
claim("36: stroke -> filled 0.9 pt band, same rule -> PASS", not fired, str(c))

# ---------------------------------------------------------------- 27 / 28 edge
def edge(dx):
    def f(p):
        p.insert_text((72, 100), "body text here")
        p.insert_text((495 + dx, 200), "the trailing run")
    return f


fired20, _ = verdict(doc(edge(0)), doc(edge(20)), "27_text_off_page")
fired60, _ = verdict(doc(edge(0)), doc(edge(60)), "27_text_off_page")
claim("27: a 20 pt overhang is not counted, a 60 pt one is (the 1 pt tolerance is real)",
      (not fired20) and fired60, "20pt=%s 60pt=%s" % (fired20, fired60))

# ---------------------------------------------------------------- retired checks
ids = set(V.all_check_ids())
for gone in ("11_bold_runs", "16_numeric_runs", "21_median_dx"):
    claim("%s is out of the universe" % gone, gone not in ids)
for kept in ("01_page_count", "13_text_colours", "27_text_off_page", "28_clipped_at_edge",
             "34a_span_size_match", "34b_span_colour_match", "34c_span_weight_match",
             "36_underline_rules", "38_list_markers", "42_alignment_mix", "43_within_10pt_x"):
    claim("%s is still in the universe" % kept, kept in ids)

# 16's two blind spots, measured on the predicate it used (kept here so the retirement
# reason is checkable after the check is gone)
def digits(p, keep=True):
    def f(q):
        for i, s in enumerate(["Qty 12", "Rate 34", "Amount 56"]):
            q.insert_text((72, 100 + i * 30), s if keep else s.split()[0], fontsize=11)
    return f


def amt(p, val):
    p.insert_text((72, 100), "Total amount %s" % val, fontsize=11)


old16 = lambda s, g: abs(s - g) <= max(3, s // 10)
claim("16's predicate passes 3 numeric runs with every digit lost",
      old16(3, 0), "abs(3-0)=3 <= max(3,0)")
claim("16's predicate passes a changed digit (1 -> 1)", old16(1, 1))
fired, c = verdict(doc(lambda p: amt(p, "4500")), doc(lambda p: amt(p, "4508")), "04_chars_missing")
claim("04_chars_missing does fail a changed digit", fired, str(c))

# 11's slack, measured on the predicate it used
old11 = lambda s, g: g >= s - max(2, s // 5)
claim("11's predicate passes one bold run made regular (1 -> 0)", old11(1, 0))

if "--store" in sys.argv:
    path = os.path.join(HERE, "RESULTS.jsonl")
    rows = [json.loads(l) for l in open(path)]
    best = {}
    for r in rows:
        if r["engine"] in ("2a68de6", "eca9020"):
            best[r["doc"]] = r
    def val(d, c):
        return best[d]["values"].get(c) or {}
    def fails(c):
        return [d for d in best if c in best[d]["failed"]]
    f = fails("42_alignment_mix")
    claim("42: every store failure has render/source < 0.70",
          all(val(d, "42_alignment_mix")["render"] < 0.70 * val(d, "42_alignment_mix")["source"]
              for d in f), "%d documents" % len(f))
    f = fails("16_numeric_runs")
    claim("16: no document fails 16 and passes 04_words_missing",
          not [d for d in f if "04_words_missing" not in best[d]["failed"]], "%d documents" % len(f))
    f = fails("11_bold_runs")
    n = sum(1 for d in f if (val(d, "34c_span_weight_match").get("ok")
                             and val(d, "34c_span_weight_match").get("render", 0) >= 88))
    claim("11: 34c reads ok at >= 88 %% on 23 of the 26", n == 23, "%d" % n)
    f = fails("01_page_count")
    n = sum(1 for d in f if val(d, "01_page_count")["render"] - val(d, "01_page_count")["source"] == 1)
    claim("01: 55 of 57 failures are exactly one extra page", n == 55, "%d of %d" % (n, len(f)))
    f = fails("27_text_off_page")
    n = sum(1 for d in f if val(d, "27_text_off_page")["render"] == 1)
    claim("27: 28 of 31 read exactly one off-page run", n == 28, "%d of %d" % (n, len(f)))
    a, b = set(fails("13_text_colours")), set(fails("34b_span_colour_match"))
    claim("13 and 34b have disjoint failure sets", not (a & b), "%d / %d" % (len(a), len(b)))

print("\n%d claim(s) failed" % len(BAD))
sys.exit(len(BAD))
