#!/usr/bin/env python3
"""Snapshot and compare what is INSIDE a folder of .docx files.

WHY
    A change made for the .txt must not alter the .docx. Comparing the file bytes
    does not work: a .docx is a zip and its timestamps differ on every write, so two
    identical documents never match byte for byte. This compares the SHA-256 of every
    entry inside the archive instead, which is the only comparison that means anything.

USAGE
    python3 txt-guard.py snapshot --dir OUT --save before.json
    ... apply the txt change, reconvert the same documents ...
    python3 txt-guard.py compare  --dir OUT --against before.json

EXIT CODE
    0  every document identical
    1  something changed, or a document disappeared
"""

import argparse
import hashlib
import json
import os
import sys
import zipfile


def digest(path):
    """SHA-256 of every entry in the archive, keyed by entry name."""
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            try:
                out[name] = hashlib.sha256(z.read(name)).hexdigest()
            except Exception as exc:  # a damaged entry must not abort the scan
                out[name] = "unreadable: " + str(exc)
    return out


def scan(folder):
    found = {}
    if not os.path.isdir(folder):
        return found
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith(".docx"):
            continue
        try:
            found[name] = digest(os.path.join(folder, name))
        except Exception as exc:
            found[name] = {"__error__": str(exc)}
    return found


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    snap = sub.add_parser("snapshot")
    snap.add_argument("--dir", required=True)
    snap.add_argument("--save", required=True)

    comp = sub.add_parser("compare")
    comp.add_argument("--dir", required=True)
    comp.add_argument("--against", required=True)

    args = ap.parse_args()

    if args.cmd == "snapshot":
        found = scan(args.dir)
        with open(args.save, "w") as fh:
            json.dump(found, fh, indent=1, sort_keys=True)
        print("snapshot: %d documents -> %s" % (len(found), args.save))
        return 0

    with open(args.against) as fh:
        before = json.load(fh)
    now = scan(args.dir)

    same = 0
    changed = []
    for name in sorted(before):
        if name not in now:
            changed.append((name, ["MISSING FROM THIS FOLDER"]))
            continue
        if before[name] == now[name]:
            same += 1
            continue
        entries = [k for k in now[name] if before[name].get(k) != now[name][k]]
        entries += [k for k in before[name] if k not in now[name]]
        changed.append((name, entries))

    new = [n for n in now if n not in before]

    for name, entries in changed:
        print("DIFFERENT: " + name)
        for entry in entries[:10]:
            print("    " + entry)
    for name in new:
        print("NEW: " + name)

    print("identical: %d, different: %d, new: %d" % (same, len(changed), len(new)))
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
