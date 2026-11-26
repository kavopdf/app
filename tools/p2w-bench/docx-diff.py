#!/usr/bin/env python3
"""docx-diff.py - compare two directories of .docx by CONTENT, not by bytes.

    python3 tools/p2w-bench/docx-diff.py /tmp/scopeA /tmp/scopeB

Prints one line per document that differs in content, and a summary. Exit 0 when every
document is identical in content, 1 when any differs, 2 on a usage error.

WHY THIS EXISTS. A .docx is a zip, and the writer stamps every entry with the time it was
written. Two conversions of one unchanged document therefore produce different bytes and
identical content. Measured 26 Nov on 600_reviewed_invoice_with_annotations at engine
a4d8fca469bba636:

    run 1  sha256 2b1fd92ff99dc79f7797a734...  6983 bytes  entry date_time 2026-11-26 8,52,28
    run 2  sha256 b8e7860dd45e9f4ab1d56f19...  6983 bytes  entry date_time 2026-11-26 8,52,32

Every inner file was byte-identical. So `diff -rq` - which is what scope.py --prove used to
print - reports every document as changed and proves nothing. This compares the parts.
"""
import hashlib
import os
import sys
import zipfile


def content_hash(path):
    """A hash of (entry name, entry bytes) for every entry, sorted. Zip metadata is ignored."""
    h = hashlib.sha256()
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            h.update(name.encode("utf-8"))
            h.update(b"\0")
            h.update(hashlib.sha256(z.read(name)).digest())
    return h.hexdigest()


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2])
        return 2
    a, b = argv[1], argv[2]
    for d in (a, b):
        if not os.path.isdir(d):
            print("  not a directory: %s" % d)
            return 2

    names = sorted(n for n in os.listdir(a) if n.lower().endswith(".docx"))
    if not names:
        print("  no .docx in %s" % a)
        return 2

    same = 0
    differ = []
    missing = []
    for n in names:
        pa, pb = os.path.join(a, n), os.path.join(b, n)
        if not os.path.exists(pb):
            missing.append(n)
            continue
        try:
            ha, hb = content_hash(pa), content_hash(pb)
        except Exception as e:
            differ.append((n, "unreadable: %s" % type(e).__name__))
            continue
        if ha == hb:
            same += 1
        else:
            differ.append((n, ha[:12] + " vs " + hb[:12]))

    print("  compared by content (zip metadata ignored): %d documents" % len(names))
    print("  identical in content: %d" % same)
    if missing:
        print("  missing on the right: %d" % len(missing))
        for n in missing[:5]:
            print("    %s" % n)
    if differ:
        print("  DIFFERENT in content: %d" % len(differ))
        for n, why in differ[:10]:
            print("    %-44s %s" % (n[:44], why))
    ok = not differ and not missing
    print()
    print("  %s" % ("PROVEN - the untouched format did not move" if ok
                    else "NOT PROVEN - content differs, see the rows above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
