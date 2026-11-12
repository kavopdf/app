#!/usr/bin/env python3
"""Is the classify phase finished? One question, one answer.

The fixer must not start on a partial class list. If classify ran when 160 documents
were scored and 48 more arrived afterwards, the classes describe the corpus as it was,
not as it is - and the fixer would spend its day on a ranking that is already out of
date, then hand a round to a baseline that measures something different.

That is the same shape as the measure gate: a phase that advances on a partial result
looks like progress and produces work that has to be thrown away.

    python3 tools/p2w-bench/classify_gate.py            # human answer, exit 0 or 1
    python3 tools/p2w-bench/classify_gate.py --quiet    # exit code only

Exit 0 means both class files exist and each one's own document count matches the store
it was built from. Exit 1 means not yet, and the lines above say which half is short.

Why the document count and not the file's timestamp: a fresh clone gives every file the
same mtime, so a timestamp comparison proves nothing there. The count is content, and it
survives being copied, committed and checked out again.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX_CLASSES = os.path.join(HERE, "DEFECT-CLASSES.md")
TXT_CLASSES = os.path.join(HERE, "DEFECT-CLASSES-TXT.md")
DOCX_STORE = os.path.join(HERE, "RESULTS.jsonl")
TXT_STORE = os.path.join(HERE, "RESULTS-TXT.jsonl")

MEASURED = re.compile(r"Documents measured:\s*\*\*(\d+)\s*of\s*(\d+)\*\*")


def store_docs(path):
    """Distinct documents in a results store."""
    docs = set()
    if not os.path.exists(path):
        return docs
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
                docs.add(row["doc"])
    return docs


def header_count(path):
    """(measured, total) from a class file's header, or None if it cannot be read."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = MEASURED.search(line)
            if m:
                return int(m.group(1)), int(m.group(2))
    return None


def main(argv):
    docx_docs = store_docs(DOCX_STORE)
    txt_docs = store_docs(TXT_STORE)

    docx_head = header_count(DOCX_CLASSES)
    txt_head = header_count(TXT_CLASSES)

    problems = []

    if docx_head is None:
        problems.append("DEFECT-CLASSES.md is missing or has no 'Documents measured' line")
    else:
        measured, _total = docx_head
        if measured != len(docx_docs):
            problems.append(
                "DEFECT-CLASSES.md covers %d documents, the .docx store holds %d - "
                "classify again" % (measured, len(docx_docs)))

    if txt_head is None:
        problems.append("DEFECT-CLASSES-TXT.md is missing or has no 'Documents measured' line")
    else:
        measured, _total = txt_head
        if measured != len(txt_docs):
            problems.append(
                "DEFECT-CLASSES-TXT.md covers %d documents, the .txt store holds %d - "
                "run classify.py --txt again" % (measured, len(txt_docs)))

    if not docx_docs:
        problems.append("the .docx store is empty - there is nothing to classify")

    ok = not problems

    if "--quiet" not in argv:
        print("docx   %d in store, class file covers %s"
              % (len(docx_docs), "%d" % docx_head[0] if docx_head else "nothing"))
        print("txt    %d in store, class file covers %s"
              % (len(txt_docs), "%d" % txt_head[0] if txt_head else "nothing"))
        for p in problems:
            print("  - %s" % p)
        print("READY - both class files match their stores" if ok
              else "NOT READY")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
