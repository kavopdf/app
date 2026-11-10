#!/usr/bin/env python3
"""
classify.py - group failures into classes FROM THE DATA, and keep a ledger of attempts.

WHY THIS EXISTS
  The fixer's first question every run is "what do I fix next". It used to answer
  by counting documents per check, which is the right instinct and the wrong
  number: twenty documents failing one check may be one missing feature, twenty
  failing another may be twenty separate causes.

WHY THE CLASSES ARE NOT HAND-WRITTEN
  The first version of this file grouped checks with a hard-coded map - borders
  together, fonts together, and so on. That is a guess about the data written
  before looking at it, and it fails in the way that matters: a genuinely
  different defect that happens to live in the same area gets merged into a class
  it does not belong to, and the fixer then hunts one cause for two unrelated
  faults and fails at both.

  So classes are derived from what actually co-occurs. For every pair of checks,
  compare the SET of documents that fail each. If two checks almost always fail
  on the same documents they are almost certainly one cause; if they fail on
  disjoint sets they are certainly not. Checks are merged by connected components
  at a Jaccard threshold, so a check that fails on its own stays on its own.

  The hand-written table survives only as a HINT - a human label and a root-cause
  area shown next to the cluster. It never decides the grouping.

WHY THERE IS A LEDGER
  A fixer without a clock loops. It picks the top class, fails, picks the top
  class, fails, and a week later the same class is still on top and nothing else
  has been touched. Every attempt is recorded here with a first-seen time and a
  count, and a class that has had MAX_ATTEMPTS tries or has been open longer than
  MAX_HOURS without its score moving is PARKED: skipped, with the reason kept, so
  the fixer moves on and the record survives.

USAGE
  python3 tools/p2w-bench/classify.py [--top N]
  python3 tools/p2w-bench/classify.py --attempt <class> --outcome kept|reverted|error
"""
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "ATTEMPTS.json")

MAX_ATTEMPTS = 3      # tries per class before it is parked
MAX_HOURS = 24        # wall-clock hours a class may stay open
JACCARD = 0.55        # how alike two checks must be to count as one cause

# Human labels only. These never group anything - they are shown beside a
# cluster so a reader recognises it, and the area hints at where to look.
CHECK_HINT = {
    "01_page_count": ("extra pages", "layout: overflow"),
    "24_page_breaks": ("extra pages", "layout: overflow"),
    "31_pages_lost_their_text": ("blank page", "layout: overflow"),
    "02_text_run_count": ("text split or merged", "text: run boundaries"),
    "03_word_count": ("text lost or duplicated", "text: extraction"),
    "04_words_missing": ("text lost or duplicated", "text: extraction"),
    "05_words_extra": ("text lost or duplicated", "text: extraction"),
    "16_numeric_runs": ("numbers lost", "text: extraction"),
    "45_char_accuracy": ("characters wrong", "text: encoding"),
    "09_font_names": ("font substitution", "fonts: family"),
    "10_font_sizes": ("font size drift", "fonts: size"),
    "34a_span_size_match": ("font size drift", "fonts: size"),
    "34c_span_weight_match": ("bold or italic lost", "fonts: run properties"),
    "11_bold_runs": ("bold or italic lost", "fonts: run properties"),
    "12_italic_runs": ("bold or italic lost", "fonts: run properties"),
    "13_text_colours": ("text colour wrong", "colours: run"),
    "34b_span_colour_match": ("text colour wrong", "colours: run"),
    "14_filled_shapes": ("shading lost", "colours: fill"),
    "25_invisible_text": ("invisible text", "colours: contrast"),
    "32_stroke_lines": ("borders missing", "drawing: strokes"),
    "33_border_over_text": ("borders over text", "drawing: z-order"),
    "46_text_crossing_rule": ("borders over text", "drawing: z-order"),
    "36_underline_rules": ("underline lost", "drawing: decoration"),
    "06_table_columns": ("table structure", "tables: grid"),
    "07_table_rows": ("table structure", "tables: grid"),
    "08_image_count": ("image missing", "images: extraction"),
    "39_image_position": ("image misplaced", "images: placement"),
    "48_image_area": ("image resized", "images: placement"),
    "15_links": ("hyperlink lost", "links: extraction"),
    "40_link_targets": ("hyperlink target", "links: extraction"),
    "17_matched_runs": ("text unmatchable", "position: gross"),
    "18_median_dy": ("vertical drift", "position: line height"),
    "19_worst_dy": ("vertical drift", "position: line height"),
    "20_within_10pt": ("vertical drift", "position: line height"),
    "21_median_dx": ("horizontal drift", "position: indent"),
    "43_within_10pt_x": ("horizontal drift", "position: indent"),
    "22_reading_order": ("reading order", "position: block order"),
    "23_line_pitch": ("line spacing", "position: line height"),
    "41_block_spacing": ("paragraph spacing", "position: paragraph gap"),
    "42_alignment_mix": ("alignment", "position: alignment"),
    "44_header_footer": ("header or footer", "layout: margins"),
    "47_margins": ("page margins", "layout: margins"),
    "26_text_overlap": ("text overlap", "position: collision"),
    "27_text_off_page": ("text off page", "position: bounds"),
    "28_clipped_at_edge": ("text clipped", "position: bounds"),
    "29_blank_where_ink_was": ("content shifted", "position: gross"),
    "30_ink_where_blank_was": ("content shifted", "position: gross"),
    "35_rotation": ("rotation lost", "drawing: transform"),
    "37_super_subscript": ("super/subscript lost", "fonts: run properties"),
    "38_list_markers": ("bullets lost", "text: list structure"),
}

CHECK_RE = re.compile(r"^\d{2}[a-c]?_[a-z_]+$")


def read_baseline(path):
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
            "failed": cells[3] if len(cells) > 3 else "",
        })
    return rows


def load_ledger():
    if os.path.exists(LEDGER):
        try:
            return json.load(open(LEDGER, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_ledger(led):
    json.dump(led, open(LEDGER, "w", encoding="utf-8"), indent=2, sort_keys=True)


def cluster(doc_sets):
    """Union checks that fail on largely the same documents. Data decides."""
    names = list(doc_sets)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, sb = doc_sets[a], doc_sets[b]
            if not sa or not sb:
                continue
            j = len(sa & sb) / len(sa | sb)
            if j >= JACCARD:
                union(a, b)

    groups = defaultdict(list)
    for n in names:
        groups[find(n)].append(n)
    return list(groups.values())


def main(argv):
    # ---- attempt recording mode -------------------------------------------
    if "--attempt" in argv:
        cls = argv[argv.index("--attempt") + 1]
        outcome = "kept"
        if "--outcome" in argv:
            outcome = argv[argv.index("--outcome") + 1]
        led = load_ledger()
        e = led.setdefault(cls, {"first_seen": time.time(), "attempts": 0,
                                 "last": 0, "outcomes": []})
        e["attempts"] += 1
        e["last"] = time.time()
        e["outcomes"].append(outcome)
        if e["attempts"] >= MAX_ATTEMPTS and outcome != "kept":
            e["status"] = "PARKED"
            e["reason"] = "%d attempts without a kept fix" % e["attempts"]
        elif outcome == "kept":
            e["status"] = "FIXED"
            e["reason"] = "fix kept and proven"
        else:
            e["status"] = "OPEN"
        save_ledger(led)
        print("%s: attempts=%d status=%s" % (cls, e["attempts"], e.get("status")))
        return 0

    top = 20
    if "--top" in argv:
        top = int(argv[argv.index("--top") + 1])

    base = read_baseline(os.path.join(HERE, "BASELINE.md"))
    measured = [r for r in base if re.match(r"\d+\s*/\s*\d+", r["score"])]

    doc_sets = defaultdict(set)
    prose = Counter()
    for r in measured:
        for c in [x.strip() for x in r["failed"].split(",") if x.strip()]:
            if CHECK_RE.match(c):
                doc_sets[c].add(r["doc"])
            else:
                prose[c] += 1

    groups = cluster(doc_sets) if doc_sets else []
    led = load_ledger()
    now = time.time()

    classes = []
    for g in groups:
        g = sorted(g, key=lambda c: -len(doc_sets[c]))
        docs = set()
        for c in g:
            docs |= doc_sets[c]
        hint_name, area = CHECK_HINT.get(g[0], (g[0], "unmapped"))
        # A cluster whose checks carry different hints is a group the data found,
        # not one a human named. Say so instead of pretending it has a single
        # identity, and name it after the check that touches the most documents.
        distinct = {CHECK_HINT.get(c, (c, ""))[0] for c in g}
        if len(distinct) == 1:
            name = hint_name
        else:
            name = "%s +%d" % (hint_name, len(distinct) - 1)
        entry = led.get(name, {})
        attempts = entry.get("attempts", 0)
        status = entry.get("status", "OPEN")
        hours_open = round((now - entry["first_seen"]) / 3600, 1) if entry else 0
        if entry and status == "OPEN":
            if attempts >= MAX_ATTEMPTS:
                status = "PARKED"
            elif hours_open >= MAX_HOURS:
                status = "PARKED"
        classes.append({
            "name": name, "checks": g, "docs": docs,
            "area": area, "attempts": attempts, "status": status,
            "hours": hours_open,
        })

    # Two unrelated clusters can land on the same label. Disambiguate rather than
    # let the ledger record two different defects under one name.
    seen = Counter()
    for c in classes:
        seen[c["name"]] += 1
    dupes = {k for k, v in seen.items() if v > 1}
    for c in classes:
        if c["name"] in dupes:
            c["name"] = "%s [%s]" % (c["name"], c["checks"][0])

    classes.sort(key=lambda c: (c["status"] == "PARKED", -len(c["docs"])))

    total = max(1, len(measured))
    out = ["# Defect classes\n",
           "Generated by `classify.py` from BASELINE.md.\n",
           "Classes are derived from the data, not from a hand-written map: two checks are put in",
           "the same class only when they fail on largely the same documents (Jaccard >= %.2f)." % JACCARD,
           "A check that fails on its own stays on its own, so a genuinely different defect cannot",
           "be swallowed by a class it does not belong to.\n",
           "Documents measured: **%d of %d**\n" % (len(measured), len(base)),
           "Limits: a class is PARKED after %d attempts without a kept fix, or %d hours open."
           % (MAX_ATTEMPTS, MAX_HOURS),
           "A parked class is skipped by the fixer and kept here with its reason.\n",
           "| # | class | documents | share | area | checks | attempts | status |",
           "|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(classes[:top], 1):
        out.append("| %d | %s | %d | %d%% | %s | %s | %d | %s |" % (
            i, c["name"], len(c["docs"]), round(100 * len(c["docs"]) / total), c["area"],
            ", ".join(c["checks"]), c["attempts"], c["status"]))

    out.append("\n## Documents per class\n")
    for c in classes[:top]:
        out.append("- **%s** — %s" % (c["name"], ", ".join(sorted(c["docs"])[:4]) or "none"))

    parked = [c for c in classes if c["status"] == "PARKED"]
    if parked:
        out.append("\n## Parked\n")
        for c in parked:
            out.append("- **%s** — %s" % (c["name"], led.get(c["name"], {}).get("reason", "limit reached")))

    if prose:
        out.append("\n## Non-check text in the failed column\n")
        out.append("Ignored. It means the column is not clean:\n")
        for k, v in prose.most_common(5):
            out.append("- %s (%d)" % (k[:90], v))

    unmapped = sorted(c for c in doc_sets if c not in CHECK_HINT)
    if unmapped:
        out.append("\n## Checks with no hint\n")
        for k in unmapped:
            out.append("- %s (%d)" % (k, len(doc_sets[k])))

    open(os.path.join(HERE, "DEFECT-CLASSES.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")

    print("documents measured : %d" % len(measured))
    print("checks firing      : %d" % len(doc_sets))
    print("classes (data-driven): %d" % len(classes))
    for c in classes[:10]:
        print("  %-30s %3d docs  %-26s %s" % (c["name"][:30], len(c["docs"]), c["area"], c["status"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
