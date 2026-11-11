#!/usr/bin/env python3
"""Documents that have a .docx score but no .txt score.

The .txt half wrote its verdict into a directory that did not exist, so every document
measured before that was fixed has a row in RESULTS.jsonl and none in RESULTS-TXT.jsonl.
The baseline takes the first rows whose SCORE cell is empty, so it never revisits a
document that already has one - which means those documents would never get a .txt at
all, and round 2's .txt ratchet would have nothing to compare them against.

    txt_gap.py --count        how many documents are missing a .txt verdict
    txt_gap.py --list 10      the first ten of them, one per line
    txt_gap.py --list 10 --all  every one, ignoring the limit

Exit 0 always: an empty gap is a result, not a failure.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "RESULTS.jsonl")
TXT = os.path.join(HERE, "RESULTS-TXT.jsonl")


def documents(path):
    """The set of document names in a store. A missing store is an empty one."""
    names = set()
    if not os.path.exists(path):
        return names
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("doc"):
                names.add(row["doc"])
    return names


def main(argv):
    limit = 10
    if "--list" in argv:
        i = argv.index("--list")
        if i + 1 < len(argv):
            try:
                limit = int(argv[i + 1])
            except ValueError:
                pass
    missing = sorted(documents(DOCX) - documents(TXT))
    if "--count" in argv:
        print(len(missing))
        return 0
    if "--all" in argv:
        limit = len(missing)
    for name in missing[:limit]:
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
