#!/usr/bin/env python3
"""Documents the pipeline is allowed to stop trying.

STEP 6 refuses to advance while any row is unscored or any text row is missing. That is
the right rule and it has a trap in it: one document that genuinely cannot be converted -
a malformed PDF, a page whose text layer is empty - would hold the gate shut forever, and
every round after it would measure the other 207 and then fail to close. The pipeline
would look healthy and never finish.

So a run that has given up on a document records it here, with the reason, and the gate
stops counting it. The document is not hidden: it is named, with why, in a file that is
committed with everything else.

    exempt.py --add --half txt  --doc 12_broken --reason "writeTxt produces no file, 3 tries"
    exempt.py --add --half docx --doc 13_broken --reason "PDF has no text layer at all"
    exempt.py --count
    exempt.py --list --half txt
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "EXEMPT.json")


def load():
    if not os.path.exists(PATH):
        return {"docx": {}, "txt": {}}
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return {"docx": {}, "txt": {}}
    for half in ("docx", "txt"):
        if not isinstance(data.get(half), dict):
            data[half] = {}
    return data


def save(data):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def arg(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def main(argv):
    data = load()

    if "--add" in argv:
        half = arg(argv, "--half")
        doc = arg(argv, "--doc")
        reason = arg(argv, "--reason", "no reason recorded")
        if half not in ("docx", "txt") or not doc:
            print("need --half docx|txt and --doc <name>")
            return 2
        data[half][doc] = reason
        save(data)
        print("exempted %s for the %s half: %s" % (doc, half, reason))
        return 0

    if "--count" in argv:
        print("docx %d · txt %d" % (len(data["docx"]), len(data["txt"])))
        return 0

    if "--list" in argv:
        half = arg(argv, "--half", "txt")
        for doc in sorted(data.get(half, {})):
            print("%s\t%s" % (doc, data[half][doc]))
        return 0

    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
