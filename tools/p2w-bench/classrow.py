#!/usr/bin/env python3
"""classrow.py - refresh the class file from the measurement, instead of by hand.

STEP 8 used to say "update the class file's own row for this class - FIXED if the number
improved". There was no tool for it, so it was a hand-edit of a 212-row markdown table, and on
16 Nov it simply did not happen: mobile-bill had gone 18.48 -> 1.55 and its row still read 18.48
OPEN. Every report built on that file then under-counted the work by everything that had actually
been fixed.

This tool reads benchmarks/RANKING.csv and rewrites each document row's numbers and status from
it. It cannot forget, and it cannot disagree with the measurement.

    python3 tools/p2w-bench/classrow.py            # dry run, prints what would change
    python3 tools/p2w-bench/classrow.py --write    # rewrite benchmarks/DEFECT-CLASSES.md
    python3 tools/p2w-bench/classrow.py --write --fixed-below 5.0
"""
import csv, os, re, sys

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
BASELINE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")

# A document below this share@5px is no longer the defect the class is named after. 5.0 is the
# same line the ranking already treats as "ink in the wrong place"; it is a flag so a run can
# justify a different number rather than silently inherit one.
DEFAULT_FIXED_BELOW = 5.0


def load_rank(path=RANK):
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        d = r.get("document")
        if not d:
            continue
        try:
            out[d] = (float(r["share1"]), float(r["share5"]))
        except (KeyError, ValueError, TypeError):
            pass
    return out


SIG = (("content-missing", "content-loss"),
       ("content-partly", "mixed"),
       ("content-present", "displacement"))


def signature(problem):
    for pre, sig in SIG:
        if problem.startswith(pre):
            return sig
    return "clean"


def recount(lines):
    """Rewrite the class summary from the document rows, so it cannot drift.

    The summary at the top of the file is a table of classes and their document counts, and it was
    maintained by hand - on 18 Nov a run had to recount it from RANKING.csv and write a paragraph
    explaining that `single-element-far-out` was closed. A table that has to be recounted by hand
    after every class closes is a table that will be wrong most of the time, and this one is the
    first thing any reader sees.
    """
    counts = {}
    for line in lines:
        st = line.strip()
        if not st.startswith("| ") or st.startswith("|---"):
            continue
        c = [x.strip() for x in st.strip("|").split("|")]
        if len(c) < 8 or not c[0].isdigit():
            continue
        counts[c[2]] = counts.get(c[2], 0) + 1
    head = "| signature | problem | documents |"
    try:
        a = next(i for i, l in enumerate(lines) if l.strip() == head)
        b = a
        while b + 1 < len(lines) and lines[b + 1].startswith("|"):
            b += 1
    except StopIteration:
        return lines, 0
    order = ["content-loss", "mixed", "displacement", "clean"]
    rows = sorted(counts.items(), key=lambda kv: (order.index(signature(kv[0]))
                                                  if signature(kv[0]) in order else 9, -kv[1]))
    new = [head, "|---|---|---|"]
    new += ["| %s | %s | %d |" % (signature(k), k, v) for k, v in rows]
    # COUNT CHANGED ROWS, NOT A LENGTH DELTA. The first version returned len(new) - len(old), which
    # is zero whenever a recount changes a number without changing the row count - so the summary
    # printed "0 differ" while its counts were wrong, and --write skipped the save.
    old_rows = lines[a:b + 1]
    changed = sum(1 for x, y in zip(old_rows, new) if x != y) + abs(len(old_rows) - len(new))
    if not changed:
        return lines, 0
    return lines[:a] + new + lines[b + 1:], changed


def main(argv):
    beat("classrow.py", "refreshing the class file")
    write = "--write" in argv
    thr = DEFAULT_FIXED_BELOW
    if "--fixed-below" in argv:
        thr = float(argv[argv.index("--fixed-below") + 1])
    rank = load_rank()
    # The baseline is what stops this tool from claiming credit it did not earn. The first
    # version marked a row FIXED whenever its share@5 was below the threshold - which marked 57
    # documents fixed while the ratchet had proved 31 improvements, because 26 of them were
    # already below the threshold at baseline and had never been fixed by anyone.
    base = load_rank(BASELINE) if os.path.exists(BASELINE) else {}
    if not rank:
        print("no RANKING.csv rows - nothing to do")
        return 1

    lines = open(CLASSES, encoding="utf-8").read().split("\n")
    changed = 0
    out = []
    for line in lines:
        s = line.strip()
        if not s.startswith("| "):
            out.append(line)
            continue
        c = [x.strip() for x in s.strip("|").split("|")]
        if len(c) < 8 or not c[0].isdigit():
            out.append(line)
            continue
        doc = c[1].strip("`")
        if doc not in rank:
            out.append(line)
            continue
        s1, s5 = rank[doc]
        status = c[6].upper()
        note = c[7]
        if "no defect" in note.lower() or c[2].lower() == "none":
            out.append(line)          # never broken - leave it alone
            continue
        # FIXED means WE fixed it: it was above the line at baseline and is at or below it now.
        # Anything already below the line at baseline was never this defect, and claiming it
        # would inflate the one number the whole pipeline is judged on.
        was = base.get(doc, (None, None))[1]
        new_status = "FIXED" if (was is not None and was > thr >= s5) else "OPEN"
        new_note = ("share@5 %.2f" % s5) if new_status == "FIXED" else (note if note not in ("-", "") else "-")
        newrow = "| %s | `%s` | %s | %.2f | %.2f | %s | %s | %s |" % (
            c[0], doc, c[2], s1, s5, c[5], new_status, new_note)
        if newrow != line.strip():
            changed += 1
            if not write:
                print("  %-44s %8s -> %-5s  %s" % (doc[:44], c[6], new_status, new_note))
        out.append(newrow)

    out, sum_delta = recount(out)
    print("  %d row(s) %s" % (changed, "rewritten" if write else "would change"))
    if sum_delta:
        print("  class summary recounted (%d line(s) differ)" % abs(sum_delta))
    if write and (changed or sum_delta):
        open(CLASSES, "w", encoding="utf-8").write("\n".join(out))
        print("  wrote benchmarks/DEFECT-CLASSES.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
