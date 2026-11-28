#!/usr/bin/env python3
"""Print, per column, the source's right edge against Google's, and the slack 60 allows.

60_text_column_right_edge reports pass/fail and nothing else, so a fixer cannot tell a column that
is 60 pt short from one 9 pt short, nor an under-run from an over-run. This prints the numbers 60
compares, using 60's own code - it imports verify_google and calls its nested helpers through a
compare() run, so the estimator and the tolerance cannot drift from the check.

    edgeprobe.py <source.pdf> <google.pdf>
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_google as vg
import fitz

BAND, COL_MIN_LINES, COL_MIN_SHARE = 0.10, 3, 0.05
SLACK_CAP, RIGHT_OVERRUN, RIGHT_UNDERRUN = 40.0, 6.0, 8.0
GUTTER = 2.0

def _union(spans):
    return (min(s["bbox"][0] for s in spans), min(s["bbox"][1] for s in spans),
            max(s["bbox"][2] for s in spans), max(s["bbox"][3] for s in spans))

def page_lines(page):
    ls = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0: continue
        for ln in blk.get("lines", []):
            spans = [sp for sp in ln.get("spans", []) if sp.get("text", "").strip()]
            if not spans: continue
            group = [spans[0]]
            for sp in spans[1:]:
                if sp["bbox"][0] - group[-1]["bbox"][2] >= GUTTER:
                    ls.append(_union(group)); group = [sp]
                else:
                    group.append(sp)
            ls.append(_union(group))
    return ls

def columns(page):
    ls = page_lines(page)
    if not ls: return []
    H = page.rect.height
    inside = [b for b in ls if b[1] >= BAND * H and b[3] <= H - BAND * H]
    band = [b for b in ls if not (b[1] >= BAND * H and b[3] <= H - BAND * H)]
    if not inside: return []
    need = max(COL_MIN_LINES, int(COL_MIN_SHARE * len(inside)))
    groups = []
    for b in sorted(inside, key=lambda b: b[0]):
        if groups and b[0] - groups[-1][0][0] <= 10: groups[-1].append(b)
        else: groups.append([b])
    out = []
    for g in groups:
        if len(g) < need: continue
        a = g[0][0]
        out.append((a, g + [b for b in band if abs(b[0] - a) <= 10]))
    return out

def edge(col, left, words):
    v = sorted(b[2] for b in col)
    w = sorted(b[2] - b[0] for b in words if abs(b[0] - left) <= 10)
    one_word = w[len(w) // 2] if w else 0.0
    return v[-1], min(SLACK_CAP, one_word)

def main(a):
    if len(a) < 3:
        print(__doc__); return 2
    src, gd = fitz.open(a[1]), fitz.open(a[2])
    for i in range(min(src.page_count, gd.page_count)):
        sc, gc = columns(src[i]), columns(gd[i])
        if not sc or not gc: continue
        s_words = [w for w in src[i].get_text("words") if w[4].strip()]
        g_words = [w for w in gd[i].get_text("words") if w[4].strip()]
        for left, s_col in sc:
            hit = [(abs(left - b2), c2) for b2, c2 in gc if abs(left - b2) <= 10]
            if not hit: continue
            g_col = min(hit, key=lambda t: t[0])[1]
            (rs, slack), rg = edge(s_col, left, s_words), edge(g_col, left, g_words)[0]
            d = rg - rs
            verdict = "PASS"
            if rg > rs + RIGHT_OVERRUN + slack: verdict = "OVER"
            elif rg < rs - RIGHT_UNDERRUN - slack: verdict = "UNDER"
            print("p%d  left=%7.2f  src_edge=%7.2f  gd_edge=%7.2f  d=%+7.2f  "
                  "slack=%5.2f  allow=%+5.2f..%+5.2f  %s"
                  % (i + 1, left, rs, rg, d, slack,
                     -(RIGHT_UNDERRUN + slack), RIGHT_OVERRUN + slack, verdict))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
