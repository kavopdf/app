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
import csv, json, os, re, sys

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")

# The documents EXEMPT.json excludes from measurement. They are in the corpus and in the
# ranking, and they have no score - so a count that says "213 of 213" is claiming a
# measurement that was never taken.
try:
    with open(os.path.join(HERE, "EXEMPT.json"), encoding="utf-8") as _f:
        EXEMPTED = set((json.load(_f).get("docx") or {}))
except Exception:
    EXEMPTED = set()
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
BASELINE = os.path.join(ROOT, "benchmarks", "RANKING-BASELINE.csv")

# A document below this share@5px is no longer the defect the class is named after. 5.0 is the
# same line the ranking already treats as "ink in the wrong place"; it is a flag so a run can
# justify a different number rather than silently inherit one.
# THE SAME LINE AS EVERYTHING ELSE: share5 <= 1.0, a 99% match.
#
# This was 5.0, so the class file marked a document FIXED at 5 per cent of its ink misplaced while
# the report and the classifier called it clean only below 1. Six documents - very-long-single-column-
# table at 2.38, admit-card 1.89, mobile-bill 1.55, landscape-page-inside-portrait-document 1.45,
# electricity-bill 1.33, salary-slip-corporate 1.28 - were FIXED in one file and below the bar in
# another. Two thresholds for one question is how a pipeline reports progress it does not have.
DEFAULT_FIXED_BELOW = 1.0


def load_rank(path=RANK):
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        d = r.get("document")
        if not d:
            continue
        try:
            out[d] = (float(r["share1"]), float(r["share5"]), (r.get("problem") or "").strip(),
                      float(r["max_pt"]))
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
    # TWO COLUMNS, BECAUSE ONE WAS ALWAYS AMBIGUOUS. The hand-maintained table counted OPEN
    # documents for defect classes and ALL rows for "none" - 29 beside 122, in the same column,
    # meaning two different things. A reader could not tell whether a class of 16 had 16 documents
    # or 16 left. open and fixed together say both, and cannot be misread.
    counts = {}
    for line in lines:
        st = line.strip()
        if not st.startswith("| ") or st.startswith("|---"):
            continue
        c = [x.strip() for x in st.strip("|").split("|")]
        if len(c) < 8 or not c[0].isdigit():
            continue
        rec = counts.setdefault(c[2], [0, 0])
        if "OPEN" in c[6].upper():
            rec[0] += 1
        else:
            rec[1] += 1
    head = "| signature | problem | open | fixed |"
    try:
        # MATCH BY PREFIX. The old header was "| signature | problem | documents |"; pinning the
        # exact string meant a file written by the previous version was never found, so the recount
        # silently did nothing - which is the same class of bug as the length-delta one.
        a = next(i for i, l in enumerate(lines) if l.strip().startswith("| signature |"))
        b = a
        while b + 1 < len(lines) and lines[b + 1].startswith("|"):
            b += 1
    except StopIteration:
        return lines, 0
    order = ["content-loss", "mixed", "displacement", "clean"]
    rows = sorted(counts.items(), key=lambda kv: (order.index(signature(kv[0]))
                                                  if signature(kv[0]) in order else 9,
                                                  -kv[1][0], -sum(kv[1])))
    new = [head, "|---|---|---|---|"]
    new += ["| %s | %s | %d | %d |" % (signature(k), k, v[0], v[1]) for k, v in rows]
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
    # THE BAR IS 99 % AND IT IS NOT NEGOTIABLE FROM THE COMMAND LINE.
    # --fixed-below could RAISE the threshold, and a run that did would mark documents FIXED at 2 %
    # or 5 % of ink displaced - the one number the whole pipeline is judged on, set by whoever ran
    # the tool. A lower threshold is now clamped back to 1.0 with a note; anything stricter is
    # allowed, because being stricter is never a false claim.
    thr = DEFAULT_FIXED_BELOW
    if "--fixed-below" in argv:
        want = float(argv[argv.index("--fixed-below") + 1])
        if want > DEFAULT_FIXED_BELOW:
            print("  --fixed-below %.2f is looser than the 99 %% bar; clamped to %.2f"
                  % (want, DEFAULT_FIXED_BELOW))
            want = DEFAULT_FIXED_BELOW
        thr = want
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
        s1, s5, prob, mpt = rank[doc]
        # The class this row was measured with, kept for the rows that are now clean: the file is a
        # record of what was wrong there as well as a work queue, and the paragraph under the summary
        # says so. Only the NUMBERS are repaired on those rows, never their history.
        measured_problem = c[2]
        # THE PROBLEM COMES FROM THE RANKING, NOT FROM THIS FILE. The column was written when the row
        # was first classified and nothing updated it, so four documents still carried
        # "content-missing-nothing-in-its-place" while RANKING said "none" with share5 of 0.66, 0.56,
        # 0.32 and 0.07. The none-branch below tested this stale column, never fired, and the summary
        # reported 70 open documents where 66 were real. A file that records a measurement must read
        # the measurement; anything else is a copy that can drift.
        if prob and prob != c[2]:
            c[2] = prob
        status = c[6].upper()
        note = c[7]
        if "no defect" in note.lower() or c[2].lower() == "none":
            # A CLEAN DOCUMENT CANNOT BE OPEN. This branch used to leave the whole row alone, which
            # was right about the numbers and wrong about the status: four documents sat in the class
            # file marked OPEN with problem "none" and share5 of 0.66, 0.56, 0.32 and 0.07 - passing
            # the 99% bar and counted as work to do. The summary then said 70 open when 66 were.
            if status == "OPEN":
                c[6] = "FIXED"
                c[7] = "no defect"
            # BOTH BRANCHES WRITE THE ROW. The else-branch used to `out.append(line)` - the row
            # exactly as it was found - which discarded the `c[2] = prob` correction three lines
            # above it and left every FIXED-and-clean row carrying whatever two numbers it was
            # born with. Measured 20 Nov: 152 of the 212 rows still showed share1 under the share5
            # heading and share5 under max_pt, because they are clean rows and only the OPEN ones
            # went through the branch below. The correction is applied here for all of them.
            out.append("| %s | `%s` | %s | %.2f | %.2f | %s | %s | %s |" % (
                c[0], doc, measured_problem, s5, mpt, c[5], c[6], c[7]))
            continue
        # FIXED means WE fixed it: it was above the line at baseline and is at or below it now.
        # Anything already below the line at baseline was never this defect, and claiming it
        # would inflate the one number the whole pipeline is judged on.
        was = base.get(doc, (None, None, None, None))[1]
        new_status = "FIXED" if (was is not None and was > thr >= s5) else "OPEN"
        new_note = ("share@5 %.2f" % s5) if new_status == "FIXED" else (note if note not in ("-", "") else "-")
        # THE COLUMNS ARE share5 AND max_pt, AND THIS WROTE share1 AND share5 INTO THEM.
        #
        # Measured 20 Nov: the header of the document table is
        #     | # | document | problem | share5 | max_pt | worst_page | status | note |
        # and this format string put `s1` in the share5 column and `s5` in the max_pt column, so
        # every row the tool has ever written carries two numbers under the wrong two names and
        # the real max_pt is nowhere. It read as impossible arithmetic to the first agent that
        # looked at it - mobile-bill "share@5 43.87, max_pt 1.55" is 44 % of ink beyond 5 px with
        # nothing more than 1.55 pt from its place, which cannot be true of one page. Both numbers
        # were right; only their labels were wrong: 43.87 is share@1px and 1.55 is share@5px.
        # Nothing computed a status from these two cells, so no FIXED/OPEN claim is affected -
        # new_status below is computed from `s5` in the dict, never from the row - and the repair
        # is to write the two columns the header names.
        newrow = "| %s | `%s` | %s | %.2f | %.2f | %s | %s | %s |" % (
            c[0], doc, c[2], s5, mpt, c[5], new_status, new_note)
        if newrow != line.strip():
            changed += 1
            if not write:
                print("  %-44s %8s -> %-5s  %s" % (doc[:44], c[6], new_status, new_note))
        out.append(newrow)

    out, sum_delta = recount(out)

    # THE HEADER COUNT WAS NEVER REWRITTEN, AND IT DISAGREED WITH EVERY OTHER TOOL.
    # Measured 19 Nov: this file said "Documents measured: **213 of 213**" while RANKING.csv
    # carried 212 scored rows (416_many_tiny_pages is exempt and has no score), the retired
    # tools/p2w-bench/DEFECT-CLASSES.md said "211 of 211", and report.py printed "36 of 212"
    # with "Exempt, not measured: 1". Four numbers for one corpus.
    #
    # The count is derived here, from the ranking, every time the file is written. A number
    # that can only be produced by reading the data cannot drift from the data.
    # load_rank() drops a row whose share5 is not a number, so `rank` holds the SCORED
    # documents only (measured 19 Nov: 212 of the table's 213 rows - 416_many_tiny_pages has an
    # empty share5 and is skipped). The total therefore has to add the exempt ones back.
    _scored = len(rank)
    _total = len(rank) + len(EXEMPTED)
    _head = ("Documents measured: **%d of %d**" % (_scored, _total))
    if EXEMPTED:
        _head += (" - %d exempt (%s), counted in the total and never scored"
                  % (len(EXEMPTED), ", ".join("`%s`" % e for e in sorted(EXEMPTED))))
    _head += "."
    _hit = False
    for i, ln in enumerate(out):
        if ln.startswith("Documents measured:"):
            # _hit IS SET EVEN WHEN THE LINE ALREADY MATCHES. It used to be set only when the
            # line was rewritten, so a run whose header was already correct fell through to the
            # `if not _hit` branch below and INSERTED A SECOND, IDENTICAL HEADER LINE. Measured
            # 19 Nov 22:5x: the file carried the same "Documents measured" line three times,
            # one per run that found nothing to change - and the line is what the brief tells a
            # reader to look for.
            if ln.strip() != _head:
                out[i] = _head
                changed += 1
            _hit = True
            break
    if not _hit:
        for i, ln in enumerate(out):
            if ln.startswith("# Defect classes"):
                out.insert(i + 1, _head)
                _hit = True
                break
    print("  %d row(s) %s" % (changed, "rewritten" if write else "would change"))
    if sum_delta:
        print("  class summary recounted (%d line(s) differ)" % abs(sum_delta))
    if write and (changed or sum_delta):
        open(CLASSES, "w", encoding="utf-8").write("\n".join(out))
        print("  wrote benchmarks/DEFECT-CLASSES.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
