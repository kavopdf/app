#!/usr/bin/env python3
"""
code.py - the part of the engine you need, instead of the file you don't.

WHY THIS EXISTS
    FIXER-BRIEF's STEP 4 said "read the engine code that produces what fails - all of it,
    not just the function with the obvious name". Measured, that sentence costs 72,186
    tokens for DocxWriter.java (4,906 lines) and 86,557 for PdfToWord.java (6,893 lines).
    Together they are about 1.6 lakh tokens - most of a context window, spent before any
    work begins, on two files whose average fix touches one method.

    The first real attempt is the proof. It changed the page-body flow: `flowFromBox` and
    `flowRow`. Two methods. It did not need 4,906 lines to find them, and what it had left
    afterwards was two minutes of thinking out of eleven.

    Reading everything is not diligence, it is a way to run out of room. What a fix needs is
    the map, the method, and who calls it.

WHAT IT GIVES
    --outline [file]        every class and method with its line range. About 150 lines for
                            a 4,900-line file: enough to see the shape and pick a target.
    --method <name>         one method, whole, with line numbers. If several files define
                            it, all of them, each named.
    --find <text> [-c N]    matching lines with N lines of context, from every engine file.
    --callers <name>        every line that mentions the name - where it is used, which is
                            usually the half of the answer the method body does not give.
    --file <name> --lines A-B   an exact range, when the outline says where to look.

    Every command prints file and line numbers so the next call can be narrower.

WHY IT IS SAFE
    It reads the same source the compiler reads; it never edits anything. It exists to make
    a targeted read the easy path, not to hide code: --method prints the whole body, and
    --file --lines prints any range asked for.

USAGE
    python3 tools/p2w-bench/code.py --outline
    python3 tools/p2w-bench/code.py --outline DocxWriter
    python3 tools/p2w-bench/code.py --method emitParagraph
    python3 tools/p2w-bench/code.py --find flowFromBox -c 8
    python3 tools/p2w-bench/code.py --callers rowLineTw
    python3 tools/p2w-bench/code.py --file DocxWriter --lines 120-190
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "..", "app", "src", "main", "java",
                                      "com", "kavopdf", "app", "engine"))

# A Java method or constructor: something with a parameter list, ending in an open brace,
# that is not a control statement. Deliberately permissive - a missed method is a smaller
# problem than a false one, because --find still reaches it.
CONTROL = ("if", "for", "while", "switch", "catch", "synchronized", "try", "else", "do")
SIG = re.compile(r"^\s{0,8}(?:@\w+\s+)*"
                 r"(?:(?:public|private|protected|static|final|abstract|synchronized|native)\s+)*"
                 r"(?:[\w<>\[\],.?\s]+\s+)?"
                 r"(\w+)\s*\([^;{}]*\)\s*(?:throws\s+[\w,.\s]+)?\{?\s*$")


def engine_files():
    if not os.path.isdir(ENGINE):
        return []
    return sorted(f for f in os.listdir(ENGINE) if f.endswith(".java"))


def path_of(name):
    if name.endswith(".java"):
        return os.path.join(ENGINE, name)
    return os.path.join(ENGINE, name + ".java")


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.readlines()


def methods(lines):
    """(name, first_line, last_line) for each method, by brace matching from its signature."""
    out = []
    for i, line in enumerate(lines):
        m = SIG.match(line)
        if not m:
            continue
        name = m.group(1)
        if name in CONTROL:
            continue
        # find the opening brace, then match to its close
        j = i
        while j < len(lines) and "{" not in lines[j]:
            j += 1
        if j >= len(lines):
            continue
        depth = 0
        end = j
        for k in range(j, len(lines)):
            depth += lines[k].count("{") - lines[k].count("}")
            if depth <= 0:
                end = k
                break
        else:
            end = len(lines) - 1
        out.append((name, i + 1, end + 1))
    return out


def outline(argv):
    # argv[0] is this script's own path, so the file name is only ever the argument that
    # follows --outline. Taking "the first non-flag argument" found code.py.java.
    want = None
    if "--outline" in argv:
        i = argv.index("--outline")
        if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
            want = argv[i + 1]
    if not want:
        # No file named: a one-line-per-file summary, not every method of every file.
        # The full outline of all nine is 581 lines - better than 288 KB, but still 9,600
        # tokens before any work, and the fixer almost always knows which file it wants.
        print("\n%-18s %6s %8s" % ("file", "lines", "methods"))
        for f in engine_files():
            p = os.path.join(ENGINE, f)
            n = len(read(p))
            print("%-18s %6d %8d" % (f, n, len(methods(read(p)))))
        print("\nAsk for one: --outline DocxWriter")
        return 0
    files = [path_of(want)]
    for p in files:
        if not os.path.exists(p):
            print("no such engine file: %s" % os.path.basename(p))
            continue
        lines = read(p)
        ms = methods(lines)
        print("\n%s  (%d lines, %d methods)" % (os.path.basename(p), len(lines), len(ms)))
        for name, a, b in ms:
            print("  %5d-%-5d %-42s %4d lines" % (a, b, name, b - a + 1))
    print("\nRead one with --method <name>, or a range with --file <name> --lines A-B.")
    return 0


def show_method(name):
    hits = 0
    for f in engine_files():
        p = os.path.join(ENGINE, f)
        lines = read(p)
        for mname, a, b in methods(lines):
            if mname != name:
                continue
            hits += 1
            print("\n%s  %s  lines %d-%d  (%d lines)" % (f, mname, a, b, b - a + 1))
            for i in range(a - 1, b):
                print("%5d  %s" % (i + 1, lines[i].rstrip()))
    if not hits:
        print("no method named %r in the engine." % name)
        print("--outline lists every one, and --find reaches anything it misses.")
        return 1
    return 0


def find(text, ctx):
    hits = 0
    for f in engine_files():
        p = os.path.join(ENGINE, f)
        lines = read(p)
        for i, line in enumerate(lines):
            if text not in line:
                continue
            hits += 1
            lo, hi = max(0, i - ctx), min(len(lines), i + ctx + 1)
            print("\n%s  %d  (%d hits so far)" % (f, i + 1, hits))
            for k in range(lo, hi):
                mark = ">" if k == i else " "
                print("%s%5d  %s" % (mark, k + 1, lines[k].rstrip()))
            if hits >= 40:
                print("\n40 hits - narrow the search.")
                return 0
    if not hits:
        print("%r is not in the engine source." % text)
        return 1
    return 0


def callers(name):
    hits = 0
    for f in engine_files():
        p = os.path.join(ENGINE, f)
        for i, line in enumerate(read(p)):
            if name in line:
                hits += 1
                print("%-18s %5d  %s" % (f, i + 1, line.strip()[:150]))
    if not hits:
        print("%r is never mentioned in the engine source." % name)
        return 1
    print("\n%d mentions." % hits)
    return 0


def file_range(name, spec):
    p = path_of(name)
    if not os.path.exists(p):
        print("no such engine file: %s" % name)
        return 1
    lines = read(p)
    try:
        a, b = spec.split("-")
        a, b = int(a), int(b)
    except ValueError:
        print("--lines wants A-B, e.g. --lines 120-190")
        return 1
    a, b = max(1, a), min(len(lines), b)
    print("%s  lines %d-%d of %d" % (os.path.basename(p), a, b, len(lines)))
    for i in range(a - 1, b):
        print("%5d  %s" % (i + 1, lines[i].rstrip()))
    return 0


def main(argv):
    if "--outline" in argv:
        return outline(argv)
    if "--method" in argv:
        i = argv.index("--method")
        if i + 1 >= len(argv):
            print("--method wants a name")
            return 1
        return show_method(argv[i + 1])
    if "--find" in argv:
        i = argv.index("--find")
        if i + 1 >= len(argv):
            print("--find wants a string")
            return 1
        ctx = 4
        if "-c" in argv:
            try:
                ctx = int(argv[argv.index("-c") + 1])
            except (ValueError, IndexError):
                pass
        return find(argv[i + 1], ctx)
    if "--callers" in argv:
        i = argv.index("--callers")
        if i + 1 >= len(argv):
            print("--callers wants a name")
            return 1
        return callers(argv[i + 1])
    if "--file" in argv and "--lines" in argv:
        return file_range(argv[argv.index("--file") + 1], argv[argv.index("--lines") + 1])
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
