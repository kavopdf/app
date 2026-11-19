#!/usr/bin/env python3
"""restamp_txt.py - re-score every .txt with the current verifier and record what moved.

WHY. Two bugs were fixed in verify_txt.py on 19 Nov: t13 matched an amount by TOKEN and always
took its first occurrence, so two columns holding the same figures were judged against one of
them; and t12 counted a punctuation-only token, which strips to "", as a word the writer had
invented. Both fixes change what the verifier says, so every number in RANKING-TXT.csv was taken
with an instrument that no longer exists. A score you cannot reproduce is not a score.

The tool is resumable. Each document's result is appended to a JSONL as it is scored, so a call
that runs out of time loses nothing and the next call starts where this one stopped.

    python3 tools/p2w-bench/restamp_txt.py --run [--budget 260]
    python3 tools/p2w-bench/restamp_txt.py --report
    python3 tools/p2w-bench/restamp_txt.py --apply          # only after --report looks right

--apply is deliberately a separate step. It writes RANKING-TXT.csv and RANKING-TXT-BASELINE.csv
from the new results, and it refuses while any document is unscored.
"""
import argparse, csv, importlib.util, io, contextlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CORPUS = "/scratch/work/p2w/corpus"
OUT = "/scratch/work/p2w/out"
RANK = os.path.join(HERE, "txt", "RANKING-TXT.csv")
NEW = os.path.join(HERE, "txt", "RESTAMP-TXT.jsonl")
BASELINE = os.path.join(HERE, "txt", "RANKING-TXT-BASELINE.csv")


def verifier():
    spec = importlib.util.spec_from_file_location("v", os.path.join(HERE, "verify_txt.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def done():
    """{document: row} for everything already scored by this run."""
    out = {}
    if not os.path.exists(NEW):
        return out
    for line in open(NEW, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        out[r["document"]] = r
    return out


def universe(v):
    """The hash the marks are stamped with - the live check list, as the ratchet computes it."""
    import hashlib
    ids = sorted(v.CHECKS) if hasattr(v, "CHECKS") else []
    return hashlib.sha256(("|".join(ids)).encode()).hexdigest()[:12], len(ids)


def run(budget):
    v = verifier()
    seen = done()
    rows = list(csv.DictReader(open(RANK, encoding="utf-8")))
    todo = [r for r in rows if r["document"] not in seen]
    print("  already scored: %d | to do: %d" % (len(seen), len(todo)))
    t0 = time.time()
    f = open(NEW, "a", encoding="utf-8")
    n = 0
    for r in todo:
        if time.time() - t0 > budget:
            print("  budget reached after %d this call" % n)
            break
        d = r["document"]
        pdf = os.path.join(CORPUS, d + ".pdf")
        txt = os.path.join(OUT, d + ".txt")
        if not (os.path.exists(pdf) and os.path.exists(txt)):
            rec = {"document": d, "error": "missing pdf or txt"}
            f.write(json.dumps(rec) + "\n"); f.flush(); n += 1
            continue
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                c = v.compare(pdf, txt)
            failed = sorted(k for k, (s, g, ok, a) in c.items() if a and not ok)
            rec = {"document": d,
                   "applicable": sum(1 for k, (s, g, ok, a) in c.items() if a),
                   "passed": sum(1 for k, (s, g, ok, a) in c.items() if a and ok),
                   "failed": len(failed),
                   "failed_ids": " ".join(failed)}
        except Exception as e:
            rec = {"document": d, "error": "%s: %s" % (type(e).__name__, e)}
        f.write(json.dumps(rec) + "\n"); f.flush(); n += 1
    f.close()
    print("  scored %d this call in %.0fs" % (n, time.time() - t0))
    return 0


def _ids(cell):
    """The check ids in a failed_ids cell.

    The published table writes a lone "-" for a document that fails nothing, and splitting that
    gives the set {"-"} - which is not a check id and which made the first version of this report
    announce 162 documents "newly clean" when every one of them had been clean all along. A
    placeholder is not a finding.
    """
    return {x for x in (cell or "").split() if x and x != "-"}


def report():
    seen = done()
    old = {r["document"]: r for r in csv.DictReader(open(RANK, encoding="utf-8"))}
    if len(seen) < len(old):
        print("  INCOMPLETE: %d of %d scored. Run --run again." % (len(seen), len(old)))
    better = worse = same = 0
    gained = []
    lost = []
    for d, r in seen.items():
        if "error" in r or d not in old:
            continue
        was = _ids(old[d]["failed_ids"])
        now = _ids(r["failed_ids"])
        if now < was:
            better += 1; gained.append((d, sorted(was - now)))
        elif now > was:
            worse += 1; lost.append((d, sorted(now - was)))
        else:
            same += 1
    print("  %d scored | %d documents newly clean, %d newly failing, %d unchanged"
          % (len(seen), better, worse, same))
    if gained:
        print("\n  NEWLY CLEAN (the old check was wrong about these):")
        for d, k in gained[:15]:
            print("    %-44s no longer fails %s" % (d[:44], ", ".join(k)))
    if lost:
        print("\n  NEWLY FAILING (the old check was too lenient):")
        for d, k in lost[:15]:
            print("    %-44s now fails %s" % (d[:44], ", ".join(k)))
    return 0


def apply():
    seen = done()
    old = {r["document"]: r for r in csv.DictReader(open(RANK, encoding="utf-8"))}
    missing = [d for d in old if d not in seen]
    if missing:
        print("  REFUSED: %d document(s) unscored, e.g. %s" % (len(missing), missing[:3]))
        print("  A partial pass must not become the baseline.")
        return 3
    fields = ["document", "applicable", "passed", "failed", "abstained", "failed_ids"]
    rows = []
    for d in old:                      # keep the published order
        r = seen[d]
        if "error" in r:
            print("  REFUSED: %s errored (%s)" % (d, r["error"]))
            return 3
        rows.append({"document": d, "applicable": r["applicable"], "passed": r["passed"],
                     "failed": r["failed"], "abstained": r["applicable"] - r["passed"],
                     "failed_ids": r["failed_ids"]})
    for path, tag in ((RANK, "RANKING-TXT.csv"), (BASELINE, "RANKING-TXT-BASELINE.csv")):
        # Write to a temp beside the target and replace, so a crash mid-write cannot leave an
        # EMPTY table where the baseline used to be. That is not hypothetical: a NameError in
        # this function truncated both CSVs to zero bytes on 19 Nov, and the next --apply then
        # read an empty baseline and divided by zero.
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            # csv's default lineterminator is \r\n and THE PUBLISHED FILE IS ALREADY CRLF - so
            # the default is what keeps the diff to the rows that moved. Forcing "\n" here
            # rewrote all 213 lines and hid the thirteen real changes inside a whole-file diff.
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
        print("  wrote %s (%d rows)" % (tag, len(rows)))
    clean = sum(1 for r in rows if r["failed"] == 0)
    print("  %d of %d clean (%.1f%%)" % (clean, len(rows), 100.0 * clean / len(rows)))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--budget", type=int, default=260)
    a = ap.parse_args(argv)
    if a.run:    return run(a.budget)
    if a.report: return report()
    if a.apply:  return apply()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
