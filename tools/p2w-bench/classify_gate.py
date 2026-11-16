#!/usr/bin/env python3
"""Is the classify phase finished? One question, one answer.

WHY THIS FILE WAS REWRITTEN

It used to read DEFECT-CLASSES.md and RESULTS.jsonl from tools/p2w-bench/, and it required
a header line "Documents measured: **N of M**". Three things were wrong with that once the
measurement layer changed:

  1. The classifier now writes benchmarks/DEFECT-CLASSES.md. This file read the old path,
     which still held the previous pipeline's list, so the count it compared was the count
     of a different corpus.
  2. RESULTS.jsonl is not written by benchmarks/p2w.py at all. store_docs() therefore
     returned an empty set, and "the .docx store is empty - there is nothing to classify"
     fired on every single run.
  3. Because of (2) the gate could never return 0.

A classify gate that can never return 0 means the phase never advances from classify to
fix, which means the fixer never runs, which means no round ever closes - and rounds 2 and
3 never happen at all. That is the whole pipeline stopping at step two while every cron
reports success.

WHAT IT READS NOW

  benchmarks/RANKING.csv          the document set that was measured
  benchmarks/DEFECT-CLASSES.md    the classifier's output, beside the measurement

The contract with the classifier is unchanged and is still worth keeping: the class file
must state how many documents it covers, in the header line

    Documents measured: **N of M**

and N must equal the number of documents RANKING.csv scored. That comparison is content,
not a timestamp - a fresh clone gives every file the same mtime, so a timestamp comparison
proves nothing there, while a count survives being copied, committed and checked out.

    python3 tools/p2w-bench/classify_gate.py            # human answer, exit 0 or 1
    python3 tools/p2w-bench/classify_gate.py --quiet    # exit code only
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RANKING = os.path.join(ROOT, "benchmarks", "RANKING.csv")
DOCX_CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")

MEASURED = re.compile(r"Documents measured:\s*\*\*(\d+)\s*of\s*(\d+)\*\*")


def scored_docs():
    """(scored, total) - distinct documents with a real score, and every row.

    They are NOT the same number and the gate used to assume they were. A document that
    cannot be measured is exempted, so the class file's header reads "212 of 213": 212
    scored, 213 in the corpus. Comparing the header's M against the SCORED count made
    every corpus with one exemption fail for ever - the gate would refuse, the phase would
    never advance, and the reason it printed ("classify again") would be wrong, because
    classifying again cannot change how many documents were measured.
    """
    docs = set()
    total = 0
    if not os.path.exists(RANKING):
        return docs, 0
    with open(RANKING, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            doc = (r.get("document") or "").strip()
            if not doc:
                continue
            total += 1
            try:
                float((r.get("share5") or "").strip())
            except (TypeError, ValueError):
                continue
            docs.add(doc)
    return docs, total


def header_count(path):
    """(measured, total) from the class file's header, or None if it cannot be read."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = MEASURED.search(line)
            if m:
                return int(m.group(1)), int(m.group(2))
    return None


def document_rows(md):
    """Every per-document row in the class file: (doc, pipe_count, status_cells).

    The class file is supposed to be ONE table of documents. The 16 Nov run produced
    THREE shapes - 92 rows with 11 pipes, 122 with 9, one with 7 - and listed the two
    bank forms twice, once in each layout. round.py counts every row that says OPEN, so
    it reported 94 classes when there were 92 defective documents: the round-close gate
    was counting two phantoms, and a fixer reading the file would see the same document
    in two tables with different column meanings.
    """
    import re as _re
    out = []
    for line in md.splitlines():
        if not _re.match(r"^\|\s*\d+\s*\|\s*`", line):
            continue
        m = _re.search(r"`([^`]+)`", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        status = [c for c in cells if c in ("OPEN", "FIXED", "PARKED")]
        out.append((m.group(1), line.count("|"), status))
    return out


def main(argv):
    docs, total_rows = scored_docs()
    head = header_count(DOCX_CLASSES)
    problems = []

    if not docs:
        problems.append("RANKING.csv scored no documents - there is nothing to classify")

    if head is None:
        problems.append("benchmarks/DEFECT-CLASSES.md is missing or has no "
                        "'Documents measured: **N of M**' line - the classifier must write "
                        "that header, it is how coverage is proved")
    else:
        measured, total = head
        if measured != len(docs):
            problems.append(
                "DEFECT-CLASSES.md covers %d documents, RANKING.csv scored %d - "
                "classify again" % (measured, len(docs)))
        # M is the corpus size, not the scored count - see scored_docs().
        if total != total_rows:
            problems.append(
                "DEFECT-CLASSES.md says the corpus is %d documents, RANKING.csv holds %d "
                "rows - classify again" % (total, total_rows))

    # ---- the file must be ONE table, one row per document ----
    rows = document_rows(open(DOCX_CLASSES, encoding="utf-8").read()) if os.path.exists(DOCX_CLASSES) else []
    if rows:
        from collections import Counter
        dup = {d: n for d, n in Counter(r[0] for r in rows).items() if n > 1}
        if dup:
            problems.append("%d document(s) appear more than once in the class file: %s - "
                            "round.py counts every OPEN row, so a duplicate is a phantom "
                            "class and the round can never close cleanly"
                            % (len(dup), ", ".join(sorted(dup)[:5])))
        shapes = Counter(r[1] for r in rows)
        if len(shapes) > 1:
            problems.append("the class file has %d different table shapes (%s pipes) - it "
                            "must be one table with one set of columns, or a reader has to "
                            "guess what each column means in each block"
                            % (len(shapes), ", ".join(str(k) for k in sorted(shapes))))
        listed = {r[0] for r in rows}
        missing = sorted(docs - listed)
        if missing:
            problems.append("%d scored document(s) are not in the class file: %s"
                            % (len(missing), ", ".join(missing[:5])))
        extra = sorted(listed - docs)
        if extra:
            problems.append("%d document(s) are in the class file but were not scored: %s "
                            "- an unmeasured document must be PARKED with a reason, not "
                            "OPEN, or the round waits for a measurement that does not exist"
                            % (len(extra), ", ".join(extra[:5])))

    ok = not problems

    if "--quiet" not in argv:
        print("docx   %d scored of %d rows, class file covers %s"
              % (len(docs), total_rows, "%d of %d" % head if head else "nothing"))
        for p in problems:
            print("  - %s" % p)
        print("READY - the class file covers the whole measurement" if ok
              else "NOT READY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
