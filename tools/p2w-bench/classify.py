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

  Nothing here is hand-written any more, not even the names. A class is called
  after the check that touches the most documents - "19_worst_dy (+3)" - and
  nothing else. Every human label is an interpretation written before the data was
  seen, and a wrong one sends the fixer after the wrong cause: an earlier version
  labelled a cluster "vertical drift" and a fixer told to fix vertical drift would
  have chased four different faults at once. The fixer reads the check ids and
  works out the cause itself, which is the only place that judgement belongs.

WHY THERE IS A LEDGER
  A fixer without a clock loops. It picks the top class, fails, picks the top
  class, fails, and a week later the same class is still on top and nothing else
  has been touched. Every attempt is recorded here with a first-seen time and a
  count. A class gets ONE FULL DAY - MAX_HOURS - and at most MAX_ATTEMPTS tries
  inside it; when either limit is reached it is PARKED, skipped by the fixer, and
  kept in the file with its reason so the record survives and the work moves on.

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

MAX_HOURS = 24        # one full day per class - the hard limit
MAX_ATTEMPTS = 6      # six tries inside that day, about 12 hours of real work
MAX_REQUEUES = 12     # a class that keeps improving gets twelve fresh days, then stops
JACCARD = 0.55        # how alike two checks must be to count as one cause

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
                                 "last": 0, "outcomes": [], "requeues": 0})
        e.setdefault("requeues", 0)
        e["attempts"] += 1
        e["last"] = time.time()
        e["outcomes"].append(outcome)

        if outcome == "kept":
            e["status"] = "FIXED"
            e["reason"] = "fix kept and proven"

        elif outcome == "improved":
            # The class moved but did not pass. It is not stuck, it is working, so
            # it gets a fresh day rather than being parked on the clock. Bounded by
            # MAX_REQUEUES: a class that improves a little every day forever is not
            # converging, and pretending otherwise is how a fixer loops slowly
            # instead of quickly.
            e["requeues"] += 1
            if e["requeues"] > MAX_REQUEUES:
                e["status"] = "PARKED"
                e["reason"] = ("improved on %d separate days without converging (limit %d)"
                               % (e["requeues"], MAX_REQUEUES))
            else:
                e["first_seen"] = time.time()   # the day restarts
                e["attempts"] = 0
                e["status"] = "OPEN"
                e["reason"] = "improved - day restarted (requeue %d of %d)" % (
                    e["requeues"], MAX_REQUEUES)

        else:  # reverted or error - real progress was not made
            if e["attempts"] >= MAX_ATTEMPTS:
                e["status"] = "PARKED"
                e["reason"] = "%d attempts without progress (limit %d)" % (
                    e["attempts"], MAX_ATTEMPTS)
            else:
                e["status"] = "OPEN"
                e["reason"] = ""

        save_ledger(led)
        print("%s: attempts=%d requeues=%d status=%s  %s" % (
            cls, e["attempts"], e["requeues"], e.get("status"), e.get("reason", "")))
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
        # The class is named after the check that touches the most documents,
        # and nothing else. Any human label would be an interpretation written
        # before the data was seen, and a wrong label sends the fixer after the
        # wrong cause - which is exactly what a hard-coded map did. The fixer
        # reads the check ids and works out the cause itself.
        name = g[0] if len(g) == 1 else "%s (+%d)" % (g[0], len(g) - 1)
        entry = led.get(name, {})
        attempts = entry.get("attempts", 0)
        requeues = entry.get("requeues", 0)
        status = entry.get("status", "OPEN")
        hours_open = round((now - entry["first_seen"]) / 3600, 1) if entry else 0
        reason = entry.get("reason", "")
        if entry and status == "OPEN":
            if hours_open >= MAX_HOURS:
                status = "PARKED"
                reason = "%s hours open without a kept fix (limit %s)" % (hours_open, MAX_HOURS)
            elif attempts >= MAX_ATTEMPTS:
                status = "PARKED"
                reason = "%s attempts without a kept fix (limit %s)" % (attempts, MAX_ATTEMPTS)
        classes.append({
            "name": name, "checks": g, "docs": docs,
            "attempts": attempts, "requeues": requeues, "status": status,
            "hours": hours_open, "reason": reason,
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
           "Limits: one full day (%d hours) per class, %d attempts inside it, and a class that"
           % (MAX_HOURS, MAX_ATTEMPTS),
           "improves but does not pass gets its day restarted - up to %d times, after which it is"
           % MAX_REQUEUES,
           "parked as not converging. A parked class is skipped by the fixer and kept with its reason.",
           "A parked class is skipped by the fixer and kept here with its reason.\n",
           "| # | class | documents | share | checks in class | attempts | requeues | status |",
           "|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(classes[:top], 1):
        out.append("| %d | %s | %d | %d%% | %s | %d | %d | %s |" % (
            i, c["name"], len(c["docs"]), round(100 * len(c["docs"]) / total),
            ", ".join(c["checks"]), c["attempts"], c.get("requeues", 0), c["status"]))

    out.append("\n## Documents per class\n")
    for c in classes[:top]:
        out.append("- **%s** — %s" % (c["name"], ", ".join(sorted(c["docs"])[:4]) or "none"))

    parked = [c for c in classes if c["status"] == "PARKED"]
    if parked:
        out.append("\n## Parked\n")
        for c in parked:
            out.append("- **%s** — %s" % (c["name"], c.get("reason") or "limit reached"))

    if prose:
        out.append("\n## Non-check text in the failed column\n")
        out.append("Ignored. It means the column is not clean:\n")
        for k, v in prose.most_common(5):
            out.append("- %s (%d)" % (k[:90], v))


    open(os.path.join(HERE, "DEFECT-CLASSES.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")

    print("documents measured : %d" % len(measured))
    print("checks firing      : %d" % len(doc_sets))
    print("classes (data-driven): %d" % len(classes))
    for c in classes[:10]:
        print("  %-34s %3d docs  %s" % (c["name"][:34], len(c["docs"]), c["status"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
