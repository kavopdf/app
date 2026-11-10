#!/usr/bin/env python3
"""
toolbox_check.py - make sure TOOLBOX.md still describes the tools that exist.

A stale interface reference is worse than no reference: it teaches a cron to call a
flag that was renamed, or to expect output that changed shape, and the failure
surfaces two hours later inside a run nobody is watching.

So every `--flag` written in TOOLBOX.md is checked against the source it names. A
flag that is documented but absent, or absent but documented, fails this check.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "TOOLBOX.md")

# the file each tool's flags must appear in
SOURCES = {
    "verify_google.py": "verify_google.py",
    "record.py": "record.py",
    "ratchet.py": "ratchet.py",
    "round.py": "round.py",
    "classify.py": "classify.py",
    "hypothesis.py": "hypothesis.py",
    "reset_round.py": "reset_round.py",
    "calibrate.py": "calibrate.py",
}
SHELL = {
    "google-gate.sh": os.path.join(HERE, "google-gate.sh"),
    "precommit.sh": os.path.join(HERE, "..", "precommit.sh"),
}


def flags_in(text):
    """Every flag mentioned, anywhere - used for the document side."""
    return set(re.findall(r"--[a-z][a-z-]+", text))


def parsed_flags(src, shell=False):
    """Only flags the code actually reads.

    A plain text search counts `git log --format`, a flag that belongs to git and
    not to us, and counts a flag named in a comment. Both made the check report
    mismatches that were not real, which is the quickest way to get a check
    ignored. So a flag counts only if the code parses it: `"--flag" in argv` or
    `argv.index("--flag")` in Python, `--flag)` in a shell case block.
    """
    found = set()
    if shell:
        found |= set(re.findall(r"^\s*(--[a-z][a-z-]+)\)", src, flags=re.M))
        found |= set(re.findall(r'^\s*(--[a-z][a-z-]+)\)', src, flags=re.M))
    else:
        found |= set(re.findall(r'"(?:--[a-z][a-z-]+)"\s+in\s+argv', src) and [])
        for m in re.finditer(r'\[?\s*"(--[a-z][a-z-]+)"\s+in\s+argv', src):
            found.add(m.group(1))
        for m in re.finditer(r'argv\.index\("(--[a-z][a-z-]+)"\)', src):
            found.add(m.group(1))
        for m in re.finditer(r'"(--[a-z][a-z-]+)"\s+in\s+argv', src):
            found.add(m.group(1))
    return found


def main():
    if not os.path.exists(DOC):
        print("TOOLBOX.md missing")
        return 1
    doc = open(DOC, encoding="utf-8").read()

    # split the document into tool sections by "## <tool>"
    sections = re.split(r"^## ", doc, flags=re.M)
    problems = []
    checked = 0

    for sec in sections:
        head = sec.split("\n", 1)[0].strip()
        tool = None
        for name in list(SOURCES) + list(SHELL):
            if head.startswith(name):
                tool = name
                break
        if not tool:
            continue

        path = SOURCES.get(tool) or SHELL[tool]
        if not os.path.exists(path):
            problems.append("%s: source file not found at %s" % (tool, path))
            continue
        src = open(path, encoding="utf-8", errors="ignore").read()
        src_flags = parsed_flags(src, shell=(tool in SHELL))
        doc_flags = flags_in(sec)

        # flags the document promises but the code does not implement
        missing = sorted(f for f in doc_flags if f not in src_flags)
        if missing:
            problems.append("%s: documented but not in the code: %s"
                            % (tool, ", ".join(missing)))

        # flags the code implements but the document never mentions
        undocumented = sorted(f for f in src_flags
                              if f not in doc_flags
                              and f not in ("--help", "--version", "--quiet", "--strict"))
        if undocumented:
            problems.append("%s: in the code but undocumented: %s"
                            % (tool, ", ".join(undocumented)))
        checked += 1

    print("toolbox")
    print("  tool sections checked : %d" % checked)
    if problems:
        print("  MISMATCH: %d" % len(problems))
        for p in problems:
            print("      %s" % p)
        print("  FAIL - the reference and the code disagree")
        return 1
    print("  PASS - every documented flag exists, every flag is documented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
