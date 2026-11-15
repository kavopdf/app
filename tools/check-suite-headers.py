#!/usr/bin/env python3
"""Every `echo "== ... =="` section header in a shell suite must have a body.

WHY THIS EXISTS
    tools/verify-engine.sh ended with three section headers and nothing under them:

        echo "== independent checks for the whole OCR path =="
        echo "== the layer must write the characters that were on the page, not substitutes =="
        echo "== what a reader copies out of an OCR layer =="

    A header with no body reads, in a log, exactly like a section that ran and passed.
    It is worse than a missing check, because it is a missing check that looks present.
    The same file also had "fonts really change the output" sitting above an unrelated
    section, with its real body a hundred lines further down.

    This reads the suite's own text and fails if any header is left dangling, so the
    fix cannot rot back out.

RULE
    A header group is one or more consecutive `echo "== ..."` lines (blank `echo`
    lines between them are allowed - they are spacing). After the group there must be
    at least one real command before the next header group or the end of the file.

    Two escapes, both explicit:
      * a group whose text says it was skipped/unchanged is its own body - there is
        nothing to run, and the message is the point.
      * comment lines and blank lines do not count as a body.

EXIT
    0  every header has a body
    1  at least one header is dangling (the offending lines are printed)
    3  nothing to check (file missing) - the caller's "could not run" convention
"""
import re
import sys

HEADER = re.compile(r'^\s*echo\s+"==')
ECHO = re.compile(r'^\s*echo\b')
COMMENT = re.compile(r'^\s*#')
SKIP_WORDS = ("skip", "unchanged", "not run", "could not run")


def check(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        print("SKIP-REASON: %s does not exist" % path)
        return 3

    bad = []
    i = 0
    n = len(lines)
    while i < n:
        if not HEADER.match(lines[i]):
            i += 1
            continue

        # collect the header group: consecutive header/blank-echo lines
        start = i
        text = []
        while i < n and (HEADER.match(lines[i]) or
                         (ECHO.match(lines[i]) and lines[i].strip() == "echo")):
            if HEADER.match(lines[i]):
                text.append(lines[i])
            i += 1

        group = " ".join(t.strip() for t in text).lower()
        if any(w in group for w in SKIP_WORDS):
            continue

        # look for a body before the next header group or EOF
        body = False
        j = i
        while j < n:
            line = lines[j]
            if HEADER.match(line):
                break
            stripped = line.strip()
            if stripped and not COMMENT.match(line) and not ECHO.match(line):
                body = True
                break
            j += 1
        if not body:
            bad.append((start + 1, lines[start].strip()))

    if not bad:
        print("every section header in %s has a body" % path)
        return 0

    print("dangling section header(s) in %s - a header with no body reads as a"
          " section that passed:" % path)
    for lineno, text in bad:
        print("  line %d: %s" % (lineno, text))
    return 1


def main(argv):
    targets = argv[1:] or ["tools/verify-engine.sh"]
    rc = 0
    for path in targets:
        r = check(path)
        if r == 3:
            return 3
        rc = rc or r
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
