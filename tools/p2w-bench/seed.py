#!/usr/bin/env python3
"""
seed.py - every document in the corpus gets a row in BASELINE.md, or nothing measures it.

WHY THIS EXISTS
    The baseline takes "the first 10 rows whose SCORE cell is empty" from BASELINE.md. That
    sentence is the whole of how work is chosen, and it has a hole: BASELINE.md is a
    hand-built table, so a document that exists in the corpus but has no row is never
    chosen, never measured, never classified and never fixed - and nothing anywhere says so.

    It was found by reading the round plan. Three documents were added to the corpus on
    12 Nov (600_reviewed_invoice_with_annotations, 601_fillable_admission_form,
    602_bookmarked_annual_report) specifically so that 50_annotations, 51_form_fields and
    52_outline would stop passing vacuously on a source count of zero. The plan said "round
    2 will measure 211, so the three documents enter the pipeline there". They would not
    have. Nothing adds a row.

    measure_gate would not have caught it either: it compares BASELINE.md against the
    store, and both would have said 208. The counts agree while three documents are absent.

WHAT IT DOES
    Reads the corpus directory, reads BASELINE.md, and appends a row with an empty score
    for every document that has no row. Idempotent - running it twice adds nothing the
    second time. It never removes or reorders a row, because a measured row carries a
    score and the archive of a closed round depends on those rows staying put.

USAGE
    python3 tools/p2w-bench/seed.py --corpus all
    python3 tools/p2w-bench/seed.py --corpus all --dry-run

    Exit 0  every corpus document has a row (added now, or already there)
    Exit 1  the corpus directory is missing or holds no PDFs
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "BASELINE.md")
HEADER = "| document | score | verdict | failed |"


def corpus_docs(directory):
    if not os.path.isdir(directory):
        return None
    names = []
    for f in sorted(os.listdir(directory)):
        if f.lower().endswith(".pdf"):
            names.append(f[:-4])
    return names


def base_docs(path):
    """The document names already in the table, header identified by its first cell."""
    names = []
    if not os.path.exists(path):
        return names
    for line in open(path, encoding="utf-8"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "document":
            continue
        names.append(cells[0])
    return names


def main(argv):
    directory = "all"
    if "--corpus" in argv:
        directory = argv[argv.index("--corpus") + 1]
    dry = "--dry-run" in argv

    docs = corpus_docs(directory)
    if docs is None:
        print("no corpus directory at %r - nothing to seed from" % directory)
        return 1
    if not docs:
        print("%r holds no PDFs - the corpus did not download, and seeding from an empty" % directory)
        print("directory would look like success while measuring nothing.")
        return 1

    known = base_docs(BASE)
    missing = [d for d in docs if d not in known]

    print("corpus    %d document(s) in %r" % (len(docs), directory))
    print("baseline  %d row(s) in BASELINE.md" % len(known))

    if not missing:
        print("nothing to add - every corpus document already has a row")
        return 0

    print("missing   %d document(s):" % len(missing))
    for d in missing[:20]:
        print("            %s" % d)
    if len(missing) > 20:
        print("            ... and %d more" % (len(missing) - 20))

    if dry:
        print("\ndry run - BASELINE.md unchanged")
        return 0

    lines = open(BASE, encoding="utf-8").read().splitlines() if os.path.exists(BASE) else []
    if not lines:
        lines = ["# Baseline", "", HEADER, "|---|---|---|---|"]
    # Insert after the last table row so the table stays contiguous; if there is no table
    # yet, append at the end.
    last_row = -1
    for i, line in enumerate(lines):
        if line.startswith("| ") and not line.startswith("|---"):
            last_row = i
    new_rows = ["| %s |  |  |  |" % d for d in missing]
    if last_row >= 0:
        lines[last_row + 1:last_row + 1] = new_rows
    else:
        lines.extend(new_rows)
    with open(BASE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\nadded %d row(s) - BASELINE.md now lists %d" % (len(missing), len(known) + len(missing)))
    print("The baseline will measure them like any other empty row.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
