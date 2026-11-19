#!/usr/bin/env python3
"""classify_txt.py - the .txt's own class table, census and cause record.

The .docx has four records that turn a score table into something a fixer can act on:

    benchmarks/DEFECT-CLASSES.md   which classes exist, and how many documents each holds
    benchmarks/CENSUS.csv          one row per document, every signal the instrument reported
    tools/p2w-bench/CAUSES.json    what actually causes each document's damage
    tools/p2w-bench/UNMEASURED.json what was not compared, and why

The .txt had only the score table, so a reader could see documents failing and not which
check was doing the damage or which documents shared a cause. This builds the same four
records for the .txt, from RANKING-TXT.csv and nothing else.

Everything it writes lands in tools/p2w-bench/txt/. Nothing here reads or writes any file
on the .docx side.

    python3 tools/p2w-bench/classify_txt.py            # write all four
    python3 tools/p2w-bench/classify_txt.py --print    # write nothing, show the classes
"""
import csv, json, os, subprocess, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, "txt")
RANK = os.path.join(TXT, "RANKING-TXT.csv")
MARKS = os.path.join(TXT, "RATCHET-TXT.json")
BASELINE = os.path.join(TXT, "RANKING-TXT-BASELINE.csv")

CLASSES = os.path.join(TXT, "DEFECT-CLASSES-TXT.md")
CENSUS = os.path.join(TXT, "CENSUS-TXT.csv")
CAUSES = os.path.join(TXT, "CAUSES-TXT.json")
UNMEASURED = os.path.join(TXT, "UNMEASURED-TXT.json")

def meaning_map():
    """{check id: what the check says it does}, read from the verifier itself.

    The .docx side does the same thing: the instrument is the authority on what it measures, so
    `verify_txt.py --list-checks` prints the id and its own sentence and this parses them. A table
    written here would be a second copy of the truth, and a second copy goes stale the first time
    someone rewords a check.
    """
    out = {}
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "verify_txt.py"), "--list-checks"],
                           capture_output=True, text=True, timeout=120)
        for line in r.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].startswith("t") and "_" in parts[0]:
                out[parts[0]] = parts[1].strip()
    except Exception:
        pass
    return out


MEANING = {}


def check_ids(cell):
    """The failing check ids in a RANKING-TXT.csv cell.

    A clean row writes "-" rather than nothing, so splitting the cell alone would make "-" a
    check that most of the corpus fails. Only ids shaped like t01_xxx count.
    """
    return [c for c in (cell or "").split() if c.startswith("t") and "_" in c]


def cause_of(ids):
    """A name for why a document fails, derived from the failing set and nothing else.

    THERE IS NO HAND-WRITTEN GROUPING HERE, AND THERE USED TO BE. The first version asserted that
    position and line order were one defect and that word accuracy and word invention were another.
    The corpus says otherwise: t02 fails alone on 67% of its documents and t08 on 50%, and the two
    occur together on four. They are two defects, and naming them one would have hidden the second
    from whoever went to fix the first. A grouping written into the code is an opinion; this file
    is supposed to be a measurement.

    So the cause is the set: one check names itself, two are named for both, and a document failing
    many is named for the count. The full list is always in `failed_ids`.
    """
    if not ids:
        return "clean"
    if len(ids) == 1:
        return ids[0]
    if len(ids) == 2:
        return " + ".join(sorted(ids))
    return "%d checks" % len(ids)


def rows():
    if not os.path.exists(RANK):
        return []
    out = []
    for r in csv.DictReader(open(RANK, encoding="utf-8")):
        try:
            app, bad = int(r.get("applicable") or 0), int(r.get("failed") or 0)
        except ValueError:
            continue
        if app <= 0 or bad < 0:
            continue                       # nothing to judge: not applicable, or an error row
        out.append({"document": r["document"], "applicable": app,
                    "passed": int(r.get("passed") or 0), "failed": bad,
                    "abstained": int(r.get("abstained") or 0),
                    "failed_ids": check_ids(r.get("failed_ids"))})
    return sorted(out, key=lambda x: x["document"])


def baseline_failed():
    if not os.path.exists(BASELINE):
        return {}
    out = {}
    for r in csv.DictReader(open(BASELINE, encoding="utf-8")):
        try:
            out[r["document"]] = int(r.get("failed") or 0)
        except ValueError:
            pass
    return out


def build():
    global MEANING
    MEANING = meaning_map()
    rs = rows()
    by_check = Counter()
    docs_by_check = defaultdict(list)
    causes = {}
    base = baseline_failed()
    for r in rs:
        for cid in r["failed_ids"]:
            by_check[cid] += 1
            docs_by_check[cid].append(r["document"])
        causes[r["document"]] = {
            "cause": cause_of(r["failed_ids"]),
            "failed": r["failed"],
            "applicable": r["applicable"],
            "failed_ids": r["failed_ids"],
            "baseline_failed": base.get(r["document"]),
        }
    return rs, by_check, docs_by_check, causes, base


def write_classes(rs, by_check, base):
    clean = [r for r in rs if r["failed"] == 0]
    failing = [r for r in rs if r["failed"] > 0]
    L = ["# .txt defect classes", "",
         "Documents measured: **%d of %d** - %d clean, %d failing at least one check."
         % (len(rs), len(rs), len(clean), len(failing)), "",
         "Grouped from `tools/p2w-bench/txt/RANKING-TXT.csv` only. A document's class is the check",
         "that fails it; a document failing several is counted under each and its own row names all",
         "of them. Ranked by how many documents each check holds, because one fix that clears a check",
         "serves every document under it.", "",
         "## Classes", "",
         "| check | what it means | documents | share |",
         "|---|---|---:|---:|"]
    for cid, n in sorted(by_check.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append("| `%s` | %s | %d | %.0f%% |"
                 % (cid, MEANING.get(cid, ""), n, 100.0 * n / max(1, len(rs))))
    if not by_check:
        L.append("| - | no failing document | 0 | 0% |")
    if not base:
        # A missing baseline is not the same as a corpus nobody had measured before. Without this
        # line every row below reads "not in baseline", which says "these documents are new" when
        # what it means is "there is no reference to compare against".
        L += ["", "> **NO BASELINE.** `RANKING-TXT-BASELINE.csv` is missing, so the last column below",
              "> says `not in baseline` for every row - that is the absence of a reference, not a",
              "> corpus of new documents. Restore it with `txt_rank.py --baseline` before reading",
              "> any comparison from this table.", ""]
    L += ["", "## Documents", "",
          "| document | class | failed | failing checks | vs baseline |", "|---|---|---:|---|---|"]
    for r in rs:
        if r["failed"] == 0:
            continue
        b = base.get(r["document"])
        note = "not in baseline" if b is None else ("**was clean**" if b == 0 else "was %d" % b)
        L.append("| `%s` | `%s` | %d/%d | %s | %s |"
                 % (r["document"], cause_of(r["failed_ids"]), r["failed"], r["applicable"],
                    ", ".join("`%s`" % c for c in r["failed_ids"]) or "-", note))
    open(CLASSES, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return len(by_check), len(failing)


def write_census(rs, causes):
    fields = ["document", "applicable", "passed", "failed", "abstained",
              "failed_ids", "cause", "baseline_failed"]
    with open(CENSUS, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rs:
            c = causes[r["document"]]
            w.writerow({"document": r["document"], "applicable": r["applicable"],
                        "passed": r["passed"], "failed": r["failed"],
                        "abstained": r["abstained"],
                        "failed_ids": " ".join(r["failed_ids"]),
                        "cause": c["cause"],
                        "baseline_failed": "" if c["baseline_failed"] is None else c["baseline_failed"]})
    return len(rs)


def write_causes(causes):
    json.dump(causes, open(CAUSES, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return len(causes)


def write_unmeasured(rs, base):
    scored = {r["document"] for r in rs}
    marks = {}
    universe = {}
    if os.path.exists(MARKS):
        try:
            d = json.load(open(MARKS, encoding="utf-8"))
            marks = d.get("marks") or {}
            universe = d.get("instrument") or {}
        except (ValueError, OSError):
            pass
    counts = {
        "scored": len(rs),
        "clean": len([r for r in rs if r["failed"] == 0]),
        "failing": len([r for r in rs if r["failed"] > 0]),
        "in_baseline": len(base),
        "in_marks": len(marks),
        "scored_not_in_baseline": sorted(scored - set(base)),
        "baseline_not_scored": sorted(set(base) - scored),
        "scored_not_in_marks": sorted(scored - set(marks)),
    }
    json.dump({"counts": counts, "instrument": universe},
              open(UNMEASURED, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return counts


def main(argv):
    if not os.path.exists(RANK):
        print("no %s - score the corpus first" % os.path.basename(RANK))
        return 2
    rs, by_check, docs_by_check, causes, base = build()
    if "--print" in argv:
        print("  %d documents scored, %d failing" % (len(rs), len([r for r in rs if r["failed"]])))
        for cid, n in sorted(by_check.items(), key=lambda kv: (-kv[1], kv[0])):
            print("  %-24s %3d  %s" % (cid, n, MEANING.get(cid, "")[:52]))
        print()
        print("  causes:")
        for k, n in Counter(c["cause"] for c in causes.values()).most_common():
            print("    %-30s %d" % (k, n))
        return 0
    ncls, nfail = write_classes(rs, by_check, base)
    ncen = write_census(rs, causes)
    ncau = write_causes(causes)
    counts = write_unmeasured(rs, base)
    print("  classes : %d, holding %d failing documents -> %s"
          % (ncls, nfail, os.path.basename(CLASSES)))
    print("  census  : %d rows -> %s" % (ncen, os.path.basename(CENSUS)))
    print("  causes  : %d documents -> %s" % (ncau, os.path.basename(CAUSES)))
    if not base:
        print("  WARNING: %s is missing - the class table's baseline column is meaningless."
              % os.path.basename(BASELINE))
        print("           restore it with: python3 tools/p2w-bench/txt_rank.py --baseline")
    print("  unmeasured: %d scored, %d in baseline, %d in marks -> %s"
          % (counts["scored"], counts["in_baseline"], counts["in_marks"], os.path.basename(UNMEASURED)))
    if counts["scored_not_in_baseline"]:
        print("  NOT IN BASELINE (%d): %s" % (len(counts["scored_not_in_baseline"]),
                                              ", ".join(counts["scored_not_in_baseline"][:5])))
    if counts["scored_not_in_marks"]:
        print("  NOT IN MARKS (%d): %s" % (len(counts["scored_not_in_marks"]),
                                           ", ".join(counts["scored_not_in_marks"][:5])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
