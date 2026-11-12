#!/usr/bin/env python3
"""
code_test.py - does code.py actually save what it claims?

The claim is narrow and checkable: the outline of a file is a small fraction of the file,
and every command returns something real from the real source. A navigation tool that
silently returns nothing is worse than no tool, because the run concludes the code does
not contain what it was looking for.

    python3 tools/p2w-bench/code_test.py
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(HERE, "code.py")
ENGINE = os.path.abspath(os.path.join(HERE, "..", "..", "app", "src", "main", "java",
                                      "com", "kavopdf", "app", "engine"))

FAILS = []


def check(name, got, want):
    ok = got == want
    print("  %s  %-58s %s" % ("PASS" if ok else "FAIL", name, got))
    if not ok:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def run(*args):
    r = subprocess.run([sys.executable, CODE] + list(args),
                       capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    print("=" * 78)
    print("code.py - the part of the engine, not the file")
    print("=" * 78)

    if not os.path.isdir(ENGINE):
        print("  engine source not found at %s - nothing to test" % ENGINE)
        return 1

    docx = os.path.join(ENGINE, "DocxWriter.java")
    whole = os.path.getsize(docx)

    print("\n1. THE OUTLINE IS A MAP, NOT THE FILE")
    rc, out = run("--outline", "DocxWriter")
    check("outline exits 0", rc, 0)
    check("outline names the file", "DocxWriter.java" in out, True)
    check("outline is under a tenth of the file", len(out) * 10 < whole, True)
    print("      file %d bytes, outline %d bytes (%.1f%%)"
          % (whole, len(out), 100.0 * len(out) / whole))
    methods_listed = sum(1 for l in out.splitlines() if l.strip()[:1].isdigit()
                         or l.strip().startswith("-"))
    check("outline lists many methods", methods_listed > 50, True)

    print("\n2. NO FILE NAMED MEANS A SUMMARY, NOT NINE OUTLINES")
    rc, out = run("--outline")
    check("summary exits 0", rc, 0)
    check("summary is short", len(out) < 2000, True)
    check("summary names the files", "DocxWriter.java" in out, True)

    print("\n3. --method RETURNS A WHOLE BODY")
    rc, out = run("--method", "spacingTw")
    check("method exits 0", rc, 0)
    check("it says which file and range", "DocxWriter.java" in out and "lines" in out, True)
    check("it has the signature", "spacingTw(" in out, True)
    check("it has a closing brace", "}" in out, True)
    check("a method is far smaller than the file", len(out) * 20 < whole, True)

    print("\n4. --method REFUSES A NAME IT DOES NOT HAVE, AND SAYS WHERE TO LOOK")
    rc, out = run("--method", "noSuchMethodAnywhere")
    check("an unknown method exits 1", rc, 1)
    check("and it points at --outline", "--outline" in out, True)

    print("\n5. --find FINDS THE DEFINITION AND THE CALL SITE")
    rc, out = run("--find", "flowFromBox", "-c", "2")
    check("find exits 0", rc, 0)
    check("it prints line numbers", "2165" in out or ">" in out, True)
    check("it names the file", "DocxWriter.java" in out, True)

    print("\n6. --find REFUSES A STRING THAT IS NOT THERE")
    rc, out = run("--find", "zzzNotInTheEngineZzz")
    check("an absent string exits 1", rc, 1)

    print("\n7. --callers LISTS EVERY MENTION")
    rc, out = run("--callers", "rowLineTw")
    check("callers exits 0", rc, 0)
    check("it found several", out.count("DocxWriter.java") >= 3, True)

    print("\n8. --file --lines PRINTS AN EXACT RANGE")
    rc, out = run("--file", "DocxWriter", "--lines", "233-240")
    check("range exits 0", rc, 0)
    check("it says the range", "233-240" in out, True)
    check("it has eight numbered lines", sum(1 for l in out.splitlines()
                                             if l.strip()[:1].isdigit()) >= 8, True)

    print("\n9. NOTHING IT PRINTS IS A LIE ABOUT THE SOURCE")
    rc, out = run("--file", "DocxWriter", "--lines", "233-233")
    real = open(docx, encoding="utf-8").readlines()[232].rstrip()
    check("line 233 is the line it says it is", real in out, True)

    print()
    print("=" * 78)
    if FAILS:
        print("%d failed" % len(FAILS))
        for f in FAILS:
            print("   " + f)
        return 1
    print("all cases behave as claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
