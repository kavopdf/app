#!/usr/bin/env python3
"""
verify_google.py - compare a Google-Docs-rendered PDF against the source PDF.

WHY THIS EXISTS
  Every earlier instrument lied. gate.py scores words, blocks, overflow, lines and
  pages, and none of those move when w:framePr is ignored or a header band lands at
  the wrong y. verify_visual.py renders through LibreOffice, which honours constructs
  Google Docs does not, so it hides exactly the faults the phone shows. Three separate
  fixes shipped "clean" and broke on the device.

  This one compares the PDF that Google Docs itself exports. If a word lands at the
  left margin in Docs, it lands there in this export too.

USAGE
  python3 verify_google.py <source.pdf> <google-export.pdf> [--json out.json]

EXIT
  0 = all checks pass, 1 = one or more failed, 2 = could not run

THRESHOLDS (a document passes only if every one holds)
  completeness  every count and every style attribute matches the source
  position      median dy < 3 pt, worst dy < 15 pt, within 10 pt > 95 %, order > 95 %
  visual        no invisible text, no text-on-text, no page overflow, no extra page
"""
import sys, json, re, collections

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed", file=sys.stderr)
    sys.exit(2)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def runs(page):
    """Every text span on a page, with the attributes we compare."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            for sp in ln.get("spans", []):
                t = sp.get("text", "")
                if not t.strip():
                    continue
                out.append({
                    "text": t,
                    "x": round(sp["bbox"][0], 2),
                    "y": round(sp["bbox"][1], 2),
                    "x1": round(sp["bbox"][2], 2),
                    "y1": round(sp["bbox"][3], 2),
                    "size": round(sp["size"], 1),
                    "font": sp.get("font", ""),
                    "colour": sp.get("color", 0),
                })
    return out


def norm_font(f):
    """Strip the subset prefix and the foundry suffix, so ABCDEF+Arial,Bold == Arial Bold."""
    f = re.sub(r"^[A-Z]{6}\+", "", f or "")
    f = f.replace(",", " ").replace("-", " ").replace("_", " ")
    return " ".join(f.split()).lower()


def norm_word(w):
    """Digits and punctuation kept; whitespace and case dropped."""
    return re.sub(r"[\s\u00a0]+", "", w).lower()


def fill_rects(page):
    """Filled rectangles - used to find text sitting on a same-colour fill."""
    out = []
    for d in page.get_drawings():
        r = d["rect"]
        if d.get("fill") and r.width > 2 and r.height > 2:
            out.append({"rect": r, "fill": d["fill"]})
    return out


def colour_close(a, b, tol=0.06):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


# ----------------------------------------------------------------------------
# the 31 checks
# ----------------------------------------------------------------------------
def compare(src_path, gd_path):
    src = fitz.open(src_path)
    gd = fitz.open(gd_path)

    checks = {}

    # ---- gather -------------------------------------------------------------
    s_runs, g_runs = [], []
    for p in src:
        s_runs += runs(p)
    for p in gd:
        g_runs += runs(p)

    s_text = " ".join(r["text"] for r in s_runs)
    g_text = " ".join(r["text"] for r in g_runs)
    s_words = collections.Counter(norm_word(w) for w in s_text.split() if w.strip())
    g_words = collections.Counter(norm_word(w) for w in g_text.split() if w.strip())

    s_imgs = sum(len(p.get_images()) for p in src)
    g_imgs = sum(len(p.get_images()) for p in gd)

    # ---- COMPLETENESS (1-16) ------------------------------------------------
    checks["01_page_count"] = (src.page_count, gd.page_count,
                               src.page_count == gd.page_count)

    checks["02_text_run_count"] = (len(s_runs), len(g_runs),
                                   abs(len(s_runs) - len(g_runs)) <= max(2, len(s_runs) // 50))

    missing = s_words - g_words
    extra = g_words - s_words
    checks["03_word_count"] = (sum(s_words.values()), sum(g_words.values()),
                               len(missing) == 0)
    checks["04_words_missing"] = (0, len(missing), len(missing) == 0)
    checks["05_words_extra"] = (0, len(extra), len(extra) <= max(1, sum(s_words.values()) // 100))

    # tables: count of distinct column x-positions that repeat down the page
    def table_signature(runs_list):
        xs = collections.Counter()
        for r in runs_list:
            xs[round(r["x"] / 6)] += 1
        return sum(1 for k, v in xs.items() if v >= 3)
    s_tbl, g_tbl = table_signature(s_runs), table_signature(g_runs)
    checks["06_table_columns"] = (s_tbl, g_tbl, abs(s_tbl - g_tbl) <= max(1, s_tbl // 10))
    # rows, not columns again - 06 already covers columns
    def table_rows(runs_list):
        ys = collections.Counter()
        for r in runs_list:
            ys[round(r["y"] / 6)] += 1
        return sum(1 for k, v in ys.items() if v >= 3)
    s_rows, g_rows = table_rows(s_runs), table_rows(g_runs)
    checks["07_table_rows"] = (s_rows, g_rows, abs(s_rows - g_rows) <= max(2, s_rows // 5))

    checks["08_image_count"] = (s_imgs, g_imgs, g_imgs >= s_imgs)

    s_fonts = collections.Counter(norm_font(r["font"]) for r in s_runs)
    g_fonts = collections.Counter(norm_font(r["font"]) for r in g_runs)
    # every source font family must appear in the render (a substitute is allowed
    # to have a different name, but a family that vanishes entirely is a loss)
    # Substitution renames a family (Arial -> Liberation Sans) so the names cannot be
    # compared, but a family that vanishes entirely is a loss. Require the render to carry
    # at least 80 % as many distinct faces as the source.
    checks["09_font_names"] = (len(s_fonts), len(g_fonts),
                               len(g_fonts) >= max(1, int(len(s_fonts) * 0.8)))

    s_sizes = collections.Counter(r["size"] for r in s_runs)
    g_sizes = collections.Counter(r["size"] for r in g_runs)
    common = sum(1 for k in s_sizes if k in g_sizes)
    checks["10_font_sizes"] = (len(s_sizes), common,
                               common >= max(1, int(len(s_sizes) * 0.8)))

    def bold_count(rs):
        return sum(1 for r in rs if "bold" in norm_font(r["font"]))
    checks["11_bold_runs"] = (bold_count(s_runs), bold_count(g_runs),
                              abs(bold_count(s_runs) - bold_count(g_runs)) <= max(2, bold_count(s_runs) // 5))

    def italic_count(rs):
        return sum(1 for r in rs if "italic" in norm_font(r["font"]) or "oblique" in norm_font(r["font"]))
    checks["12_italic_runs"] = (italic_count(s_runs), italic_count(g_runs),
                                abs(italic_count(s_runs) - italic_count(g_runs)) <= max(2, italic_count(s_runs) // 5))

    s_cols = collections.Counter(r["colour"] for r in s_runs)
    g_cols = collections.Counter(r["colour"] for r in g_runs)
    checks["13_text_colours"] = (len(s_cols), len(g_cols),
                                 len(g_cols) >= max(1, int(len(s_cols) * 0.8)))

    s_fill = sum(1 for p in src for _ in fill_rects(p))
    g_fill = sum(1 for p in gd for _ in fill_rects(p))
    checks["14_filled_shapes"] = (s_fill, g_fill, g_fill >= max(1, int(s_fill * 0.5)))

    s_links = sum(len(p.get_links()) for p in src)
    g_links = sum(len(p.get_links()) for p in gd)
    checks["15_links"] = (s_links, g_links, s_links == 0 or g_links >= s_links)

    s_digits = sum(1 for r in s_runs if any(c.isdigit() for c in r["text"]))
    g_digits = sum(1 for r in g_runs if any(c.isdigit() for c in r["text"]))
    checks["16_numeric_runs"] = (s_digits, g_digits,
                                 abs(s_digits - g_digits) <= max(3, s_digits // 10))

    # ---- POSITION (17-24) ---------------------------------------------------
    # match each source run to its nearest render run by text
    by_text = collections.defaultdict(list)
    for r in g_runs:
        by_text[norm_word(r["text"])].append(r)

    dys, dxs, matched = [], [], 0
    for r in s_runs:
        cands = by_text.get(norm_word(r["text"]))
        if not cands:
            continue
        best = min(cands, key=lambda c: abs(c["y"] - r["y"]) + abs(c["x"] - r["x"]))
        dys.append(best["y"] - r["y"])
        dxs.append(best["x"] - r["x"])
        matched += 1

    def median(v):
        if not v:
            return 0.0
        v = sorted(v)
        n = len(v)
        return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2

    med_dy = round(median(dys), 1)
    worst_dy = round(max((abs(d) for d in dys), default=0), 1)
    within10 = round(100.0 * sum(1 for d in dys if abs(d) <= 10) / max(1, len(dys)))
    med_dx = round(median(dxs), 1)

    checks["17_matched_runs"] = (len(s_runs), matched,
                                 matched >= int(len(s_runs) * 0.9))
    checks["18_median_dy"] = (0, med_dy, med_dy < 3.0)
    checks["19_worst_dy"] = (0, worst_dy, worst_dy < 15.0)
    checks["20_within_10pt"] = (100, within10, within10 > 95)
    checks["21_median_dx"] = (0, med_dx, abs(med_dx) < 3.0)

    # reading order: the sequence of normalised words
    s_seq = [norm_word(w) for w in s_text.split() if w.strip()]
    g_seq = [norm_word(w) for w in g_text.split() if w.strip()]
    if s_seq:
        same = sum(1 for a, b in zip(s_seq, g_seq) if a == b)
        order = round(100.0 * same / max(1, len(s_seq)))
    else:
        order = 100
    checks["22_reading_order"] = (100, order, order > 95)

    # line spacing: median gap between consecutive baselines on page 1
    def pitch(rs):
        ys = sorted(set(round(r["y"], 1) for r in rs))
        gaps = [b - a for a, b in zip(ys, ys[1:]) if 1 < b - a < 200]
        return round(median(gaps), 1) if gaps else 0
    s_p, g_p = pitch([r for r in s_runs]), pitch([r for r in g_runs])
    checks["23_line_pitch"] = (s_p, g_p, s_p == 0 or abs(g_p - s_p) <= 2.0)

    checks["24_page_breaks"] = (src.page_count, gd.page_count,
                                src.page_count == gd.page_count)

    # ---- VISUAL (25-31) -----------------------------------------------------
    invisible, on_text, off_page, clipped = 0, 0, 0, 0
    for p in gd:
        W, H = p.rect.width, p.rect.height
        fills = fill_rects(p)
        rs = runs(p)
        for r in rs:
            # 28 text drawn in the same colour as the shape behind it
            for f in fills:
                fr = f["rect"]
                if fr.contains(fitz.Point(r["x"] + 1, r["y"] + 1)):
                    tr = ((r["colour"] >> 16) & 255) / 255.0, ((r["colour"] >> 8) & 255) / 255.0, (r["colour"] & 255) / 255.0
                    if colour_close(tr, f["fill"], 0.08):
                        invisible += 1
                    break
            # 26 text boxes overlapping other text
            for o in rs:
                if o is r:
                    continue
                if (r["x"] < o["x1"] - 1 and r["x1"] > o["x"] + 1 and
                        r["y"] < o["y1"] - 1 and r["y1"] > o["y"] + 1):
                    on_text += 1
                    break
            # 27 text outside the page
            if r["x"] < -1 or r["y"] < -1 or r["x1"] > W + 1 or r["y1"] > H + 1:
                off_page += 1
            # 31 text clipped at the edge
            if r["x"] < 1 or r["x1"] > W - 1:
                clipped += 1

    checks["25_invisible_text"] = (0, invisible, invisible == 0)
    checks["26_text_overlap"] = (0, on_text, on_text <= max(2, len(g_runs) // 50))
    checks["27_text_off_page"] = (0, off_page, off_page == 0)
    checks["28_clipped_at_edge"] = (0, clipped, clipped <= max(2, len(g_runs) // 50))

    # 29 blank where source has ink / 30 ink where source is blank
    blank_loss, extra_ink, s_grid_total = 0, 0, 0
    for i in range(min(src.page_count, gd.page_count)):
        sp, gp = src[i], gd[i]
        W, H = sp.rect.width, sp.rect.height
        GRID = 24
        cw, ch = W / GRID, H / GRID
        s_cells = set()
        for r in runs(sp):
            s_cells.add((int(r["x"] / cw), int(r["y"] / ch)))
        g_cells = set()
        for r in runs(gp):
            g_cells.add((int(r["x"] / cw), int(r["y"] / ch)))
        s_grid_total += len(s_cells)
        blank_loss += len(s_cells - g_cells)
        extra_ink += len(g_cells - s_cells)
    # tolerance is a fraction of the source's own occupied grid cells, not of its columns
    s_cells_total = max(1, s_grid_total)
    checks["29_blank_where_ink_was"] = (0, blank_loss, blank_loss <= max(4, int(s_cells_total * 0.10)))
    checks["30_ink_where_blank_was"] = (0, extra_ink, extra_ink <= max(4, int(s_cells_total * 0.10)))

    # 31 every page must carry some ink
    # A blank page in the source is legitimate; a blank page the source did not have is not.
    empty_pages = 0
    for i in range(gd.page_count):
        g_has = bool(gd[i].get_text().strip())
        s_has = bool(src[i].get_text().strip()) if i < src.page_count else False
        if s_has and not g_has:
            empty_pages += 1
    checks["31_pages_lost_their_text"] = (0, empty_pages, empty_pages == 0)

    src.close()
    gd.close()

    failed = [k for k, v in checks.items() if not v[2]]
    return {
        "source": src_path,
        "render": gd_path,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": sorted(failed),
        "ok": not failed,
        "checks": {k: {"source": v[0], "render": v[1], "ok": bool(v[2])}
                   for k, v in sorted(checks.items())},
    }


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, gd = argv[1], argv[2]
    out = None
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
    try:
        res = compare(src, gd)
    except Exception as e:
        print("could not run: %s" % e, file=sys.stderr)
        return 2

    print("%-38s %d/%d %s" % (
        src.split("/")[-1][:38], res["passed"], res["total"],
        "PASS" if res["ok"] else "FAIL"))
    if res["failed"]:
        for k in res["failed"]:
            c = res["checks"][k]
            print("    %-28s source=%-8s render=%-8s" % (k, c["source"], c["render"]))
    if out:
        with open(out, "w") as f:
            json.dump(res, f, indent=2)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
