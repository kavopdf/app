#!/usr/bin/env python3
"""
classify.py - turn a list of failing documents into a ranked list of defect classes.

WHY THIS EXISTS
  The fixer's first question every run is "what do I fix next", and it was
  answering that by counting how many documents failed each check. That is the
  right instinct and the wrong number. Twenty documents failing 32_stroke_lines
  and twenty failing 44_header_footer are not equally worth fixing: the first is
  one missing feature in the writer, the second may be twenty different causes.

  So this groups failures into named CLASSES, counts documents and occurrences
  separately, and ranks by how much of the corpus one fix would reach - then by
  how likely that fix is to be a single root cause.

  It also flags classes that look like symptoms of another class, because a fixer
  that repairs a symptom will keep finding the same defect under a new name.

WHAT IT READS
  tools/p2w-bench/BASELINE.md   scores and the failed-check list per document
  tools/p2w-bench/results/*.json   optional per-document detail from verify_google

WHAT IT WRITES
  tools/p2w-bench/DEFECT-CLASSES.md   ranked classes, one row each

USAGE
  python3 tools/p2w-bench/classify.py [--top N]
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

# check -> (class name, root-cause area, is this likely a symptom of another class)
CHECK_CLASS = {
    "01_page_count":            ("extra or missing pages",        "layout: content overflow", False),
    "24_page_breaks":           ("extra or missing pages",        "layout: content overflow", False),
    "31_pages_lost_their_text": ("blank page after conversion",   "layout: content overflow", False),
    "02_text_run_count":        ("text split or merged",          "text: run boundaries", False),
    "03_word_count":            ("text missing or duplicated",    "text: extraction", False),
    "04_words_missing":         ("text missing or duplicated",    "text: extraction", False),
    "05_words_extra":           ("text missing or duplicated",    "text: extraction", False),
    "16_numeric_runs":          ("numbers lost",                  "text: extraction", False),
    "45_char_accuracy":         ("characters wrong",              "text: encoding", False),
    "09_font_names":            ("font substitution",             "fonts: family mapping", False),
    "10_font_sizes":            ("font size drift",               "fonts: size mapping", False),
    "34a_span_size_match":      ("font size drift",               "fonts: size mapping", False),
    "34c_span_weight_match":    ("bold or italic lost",           "fonts: run properties", False),
    "11_bold_runs":             ("bold or italic lost",           "fonts: run properties", False),
    "12_italic_runs":           ("bold or italic lost",           "fonts: run properties", False),
    "13_text_colours":          ("text colour wrong",             "colours: run properties", False),
    "34b_span_colour_match":    ("text colour wrong",             "colours: run properties", False),
    "14_filled_shapes":         ("shading or fill lost",          "colours: shape fill", False),
    "25_invisible_text":        ("invisible text",                "colours: contrast", False),
    "32_stroke_lines":          ("borders and rules missing",     "drawing: strokes", False),
    "33_border_over_text":      ("borders drawn over text",       "drawing: z-order", False),
    "46_text_crossing_rule":    ("borders drawn over text",       "drawing: z-order", False),
    "36_underline_rules":       ("underline lost",                "drawing: text decoration", False),
    "06_table_columns":         ("table structure wrong",         "tables: grid", False),
    "07_table_rows":            ("table structure wrong",         "tables: grid", False),
    "08_image_count":           ("image missing",                 "images: extraction", False),
    "39_image_position":        ("image misplaced",               "images: placement", False),
    "48_image_area":            ("image resized",                 "images: placement", False),
    "15_links":                 ("hyperlink lost",                "links: extraction", False),
    "40_link_targets":          ("hyperlink target wrong",        "links: extraction", False),
    "17_matched_runs":          ("text not matchable at all",     "position: gross", True),
    "18_median_dy":             ("vertical drift",                "position: line height", False),
    "19_worst_dy":              ("vertical drift",                "position: line height", False),
    "20_within_10pt":           ("vertical drift",                "position: line height", False),
    "21_median_dx":             ("horizontal drift",              "position: indent", False),
    "43_within_10pt_x":         ("horizontal drift",              "position: indent", False),
    "22_reading_order":         ("reading order scrambled",       "position: block order", False),
    "23_line_pitch":            ("line spacing wrong",            "position: line height", False),
    "41_block_spacing":         ("paragraph spacing wrong",       "position: paragraph gap", False),
    "42_alignment_mix":         ("alignment wrong",               "position: alignment", False),
    "44_header_footer":         ("header or footer lost",         "layout: margins", False),
    "47_margins":               ("page margins wrong",            "layout: margins", False),
    "26_text_overlap":          ("text overlapping text",         "position: collision", False),
    "27_text_off_page":         ("text outside the page",         "position: bounds", False),
    "28_clipped_at_edge":       ("text clipped at the edge",      "position: bounds", False),
    "29_blank_where_ink_was":   ("content shifted out of place",  "position: gross", True),
    "30_ink_where_blank_was":   ("content shifted out of place",  "position: gross", True),
    "35_rotation":              ("rotation lost",                 "drawing: transform", False),
    "37_super_subscript":       ("superscript or subscript lost", "fonts: run properties", False),
    "38_list_markers":          ("bullets or numbering lost",     "text: list structure", False),
}


def read_baseline(path):
    """Rows of (document, score, verdict, failed list). Header found by first cell."""
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "document":
            continue
        rows.append({
            "doc": cells[0],
            "score": cells[1] if len(cells) > 1 else "",
            "verdict": cells[2] if len(cells) > 2 else "",
            "failed": cells[3] if len(cells) > 3 else "",
            "engine": cells[4] if len(cells) > 4 else "",
        })
    return rows


def main(argv):
    top = 20
    if "--top" in argv:
        top = int(argv[argv.index("--top") + 1])

    base = read_baseline(os.path.join(HERE, "BASELINE.md"))
    measured = [r for r in base if re.match(r"\d+\s*/\s*\d+", r["score"])]

    # Only tokens shaped like a check id are checks. The failed-checks cell
    # sometimes carries prose after the ids, and splitting on commas turned that
    # prose into invented check names - one row read "30_ink_where_blank_was -
    # Google Docs has no exact line spacing" and produced a class with that name.
    CHECK_RE = re.compile(r"^\d{2}[a-c]?_[a-z_]+$")

    per_check = Counter()
    docs_for = defaultdict(list)
    prose = Counter()
    for r in measured:
        for c in [x.strip() for x in r["failed"].split(",") if x.strip()]:
            if CHECK_RE.match(c):
                per_check[c] += 1
                docs_for[c].append(r["doc"])
            else:
                prose[c] += 1

    classes = defaultdict(lambda: {"docs": 0, "checks": [], "area": "", "symptom": False})
    for check, n in per_check.items():
        name, area, symptom = CHECK_CLASS.get(check, (check, "unmapped", False))
        cls = classes[name]
        cls["docs"] = max(cls["docs"], n)
        cls["checks"].append((check, n))
        cls["area"] = cls["area"] or area
        cls["symptom"] = cls["symptom"] or symptom

    total = max(1, len(measured))
    ranked = sorted(
        classes.items(),
        key=lambda kv: (kv[1]["symptom"], -kv[1]["docs"], -len(kv[1]["checks"])),
    )

    lines = []
    lines.append("# Defect classes\n")
    lines.append("Generated by `classify.py` from BASELINE.md. One row per class, ranked so the")
    lines.append("cheapest big win is first: classes that are likely symptoms of another class are")
    lines.append("pushed down, because fixing a symptom finds the same defect again under a new name.\n")
    lines.append("Documents measured: **%d of %d**\n" % (len(measured), len(base)))
    lines.append("| # | class | documents | share | root-cause area | checks | symptom |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, (name, c) in enumerate(ranked[:top], 1):
        checks = ", ".join("%s(%d)" % (k, v) for k, v in sorted(c["checks"], key=lambda x: -x[1]))
        lines.append("| %d | %s | %d | %d%% | %s | %s | %s |" % (
            i, name, c["docs"], round(100 * c["docs"] / total), c["area"],
            checks, "yes" if c["symptom"] else ""))
    lines.append("")
    lines.append("## Example documents per class\n")
    for name, c in ranked[:top]:
        first = []
        for check, _ in sorted(c["checks"], key=lambda x: -x[1]):
            first += docs_for[check][:2]
        seen, uniq = set(), []
        for d in first:
            if d not in seen:
                seen.add(d)
                uniq.append(d)
        lines.append("- **%s** — %s" % (name, ", ".join(uniq[:4]) or "none"))
    lines.append("")
    if prose:
        lines.append("## Non-check text found in the failed column\n")
        lines.append("Ignored, but it means the column is not clean:\n")
        for k, v in prose.most_common(5):
            lines.append("- %s (%d)" % (k[:90], v))
        lines.append("")

    unmapped = sorted(k for k in per_check if k not in CHECK_CLASS)
    if unmapped:
        lines.append("## Checks with no class mapping\n")
        lines.append("These fired but `classify.py` does not know what they mean. Map them.\n")
        for k in unmapped:
            lines.append("- %s (%d)" % (k, per_check[k]))
        lines.append("")

    out = os.path.join(HERE, "DEFECT-CLASSES.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))

    print("documents measured : %d" % len(measured))
    print("checks firing      : %d" % len(per_check))
    print("classes            : %d" % len(classes))
    print("written            : %s" % out)
    for name, c in ranked[:8]:
        print("  %-32s %3d docs  %s" % (name[:32], c["docs"], c["area"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
