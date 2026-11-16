#!/usr/bin/env python3
"""report.py - the eight numbers, computed from committed data only.

THE RULE THIS TOOL EXISTS TO ENFORCE: a number appears here only if something on disk proves it.
If a run claims thirty-one documents improved and never committed the measurement that shows it,
this tool reports zero - not because the work did not happen, but because nobody can check it.

That is not pedantry. On 16 Nov the fixer recorded "212 documents compared, 0 regressions, 31
improvements" in ATTEMPTS.json, and benchmarks/RANKING.csv was byte-identical to the round-one
baseline. The claim was in a sentence and the evidence was nowhere, so the claim could not be
told apart from a hope.

    python3 tools/p2w-bench/report.py            # the report
    python3 tools/p2w-bench/report.py --json     # same, machine-readable
"""
import csv, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLASSES  = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
RANK     = os.path.join(ROOT, "benchmarks", "RANKING.csv")
BASELINE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")
RUN      = os.path.join(HERE, "RUN.json")
HANDOFF  = os.path.join(HERE, "HANDOFF.json")


def _json(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def classes():
    """Count CLASSES, not document rows.

    The file is one row per document - 212 of them - grouped by problem name. The first version
    of this function counted rows and called them classes, so the report said "212 classes total"
    when there are eight. A number that is wrong by a factor of twenty-six is worse than a number
    that is missing.

    A class is solved when no document under it is still OPEN.
    """
    per_class = {}          # problem -> [open_count, fixed_count, never_broken]
    docs = 0
    try:
        for line in open(CLASSES, encoding="utf-8"):
            s = line.strip()
            if not s.startswith("| ") or s.startswith("|---"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 8 or cells[0] in ("rank", "") or not cells[0].isdigit():
                continue
            docs += 1
            problem, status, note = cells[2], cells[6].upper(), cells[7].lower()
            rec = per_class.setdefault(problem, [0, 0, 0])
            if "OPEN" in status:
                rec[0] += 1
            elif "no defect" in note or problem.lower() == "none":
                rec[2] += 1
            else:
                rec[1] += 1
    except Exception:
        pass
    total = len(per_class)
    solved = sum(1 for v in per_class.values() if v[0] == 0 and v[1] > 0)
    openc = sum(1 for v in per_class.values() if v[0] > 0)
    return total, solved, openc, docs, per_class


def _share5(path):
    d = {}
    try:
        for r in csv.DictReader(open(path, encoding="utf-8")):
            doc, v = r.get("document"), r.get("share5")
            if doc and v:
                try:
                    d[doc] = float(v)
                except ValueError:
                    pass
    except Exception:
        pass
    return d


def corpus():
    """Improvement measured against the round-one baseline, from committed files only."""
    b, c = _share5(BASELINE), _share5(RANK)
    if not b or not c:
        return {"available": False,
                "why": "RANKING-BASELINE.csv or RANKING.csv missing"}
    common = sorted(set(b) & set(c))
    if not common:
        return {"available": False, "why": "no documents in common"}
    bm = sum(b[k] for k in common) / len(common)
    cm = sum(c[k] for k in common) / len(common)
    improved = [k for k in common if c[k] < b[k] - 0.05]
    regressed = [k for k in common if c[k] > b[k] + 0.05]
    unchanged = len(common) - len(improved) - len(regressed)
    identical = all(abs(b[k] - c[k]) < 1e-9 for k in common)
    # share@5px is the fraction of ink that landed more than 5px from where it belongs, so a
    # FALL is an improvement. The first version printed (current - baseline), which reported
    # 6.15 -> 5.01 as "-18.55%" - arithmetically right, and read by every human as a regression.
    return {"available": True, "docs": len(common),
            "baseline_mean": round(bm, 2), "current_mean": round(cm, 2),
            "pct": round((bm - cm) / bm * 100, 2) if bm else 0.0,
            "improved": len(improved), "regressed": len(regressed), "unchanged": unchanged,
            "measurement_committed": not identical,
            "best": [{"doc": k, "before": round(b[k], 2), "after": round(c[k], 2)}
                     for k in sorted(improved, key=lambda k: c[k] - b[k])[:5]]}


def this_run():
    r = _json(RUN, {})
    if not r.get("started"):
        return {"present": False}
    end = r.get("ended_ts") or time.time()
    mins = int((end - (r.get("started_ts") or end)) / 60)
    return {"present": True, "started": r.get("started"), "ended": r.get("ended"),
            "minutes": mins, "class": r.get("class") or "-",
            "attempts": r.get("attempts", 0), "kept": r.get("kept", 0),
            "docs_improved": r.get("docs_improved", 0),
            "agents": r.get("agents") or [], "obstacles_cleared": r.get("obstacles_cleared", 0),
            "needs_human": r.get("needs_human", 0)}


def main(argv):
    total, solved, openc, docs, per_class = classes()
    co = corpus()
    tr = this_run()
    h = _json(HANDOFF, {})
    working = tr.get("class") if tr.get("present") else "-"

    if "--json" in argv:
        print(json.dumps({"classes": {"total": total, "clear": solved, "open": openc,
                                      "documents": docs},
                          "corpus": co, "run": tr, "working_class": working,
                          "needs_human": len(h.get("needs_human") or [])}, indent=1))
        return 0

    L = []
    L.append("=== FIXER REPORT - every number computed from committed files ===")
    L.append("")
    L.append("1. classes total            : %d  (%d documents across them)" % (total, docs))
    L.append("2. classes solved           : %d clear, %d still have an OPEN document"
             % (solved, openc))
    if tr.get("present"):
        L.append("3. docs improved THIS run   : %d  (%d attempts, %d kept)"
                 % (tr["docs_improved"], tr["attempts"], tr["kept"]))
        L.append("4. this run total time      : %d min  (%s -> %s)"
                 % (tr["minutes"], tr["started"], tr["ended"] or "running"))
        L.append("5. subagents this run       : %d%s"
                 % (len(tr["agents"]), (" - " + ", ".join(tr["agents"])) if tr["agents"] else ""))
    else:
        L.append("3. docs improved THIS run   : no run record (RUN.json missing)")
        L.append("4. this run total time      : unknown")
        L.append("5. subagents this run       : unknown")
    L.append("6. working on class         : %s" % working)
    if co.get("available"):
        L.append("7. corpus improvement       : %+.2f%%  (mean share5 %.2f -> %.2f over %d docs)"
                 % (co["pct"], co["baseline_mean"], co["current_mean"], co["docs"]))
        L.append("8. docs improved total      : %d of %d  (%d regressed, %d unchanged)"
                 % (co["improved"], co["docs"], co["regressed"], co["unchanged"]))
        if not co["measurement_committed"]:
            L.append("")
            L.append("   NOTE: RANKING.csv is identical to the baseline, so no improvement has")
            L.append("   been COMMITTED since round one. If a run reported improvements, its")
            L.append("   measurement was never committed and cannot be checked. Re-measure and")
            L.append("   commit benchmarks/RANKING.csv with the attempt.")
        if co.get("best"):
            L.append("")
            L.append("   best so far:")
            for x in co["best"]:
                L.append("     %-42s %6.2f -> %5.2f" % (x["doc"][:42], x["before"], x["after"]))
    else:
        L.append("7. corpus improvement       : not measurable - %s" % co.get("why"))
        L.append("8. docs improved total      : not measurable")
    nh = len(h.get("needs_human") or [])
    if nh:
        L.append("")
        L.append("   %d item(s) NEED A HUMAN - see the top of HANDOFF.md" % nh)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
