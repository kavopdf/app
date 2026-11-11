#!/usr/bin/env python3
"""
toolbox_check.py - make sure TOOLBOX.md still describes the tools that exist.

A stale interface reference is worse than no reference: it teaches a cron to call a
flag that was renamed, or to expect output that changed shape, and the failure
surfaces two hours later inside a run nobody is watching.

So every `--flag` written in TOOLBOX.md is checked against the source it names. A
flag that is documented but absent, or absent but documented, fails this check.

Getting this right took three attempts, and the mistakes are worth keeping:

  1. A plain text search counted `git log --format` - git's flag, not ours - and
     counted flags named in comments. It reported six mismatches, three of them
     imaginary, which is the quickest way to get a check ignored.

  2. A strict search for `"--flag" in argv` fixed that and broke the other
     direction: a flag passed to a helper, `num("--moved")`, was invisible, so
     four working flags were reported as undocumented.

  3. This version strips comments and docstrings first, then takes string
     literals. A flag named in prose is not a flag the code accepts; a flag in a
     string literal is, however it is later used.
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
    "docnames.py": "docnames.py",
    "verify_txt.py": "verify_txt.py",
    "test_txt_checks.py": "test_txt_checks.py",
    "calibrate.py": "calibrate.py",
}
SHELL = {
    "google-gate.sh": os.path.join(HERE, "google-gate.sh"),
    "precommit.sh": os.path.join(HERE, "..", "precommit.sh"),
    "commit-gate.sh": os.path.join(HERE, "..", "commit-gate.sh"),
    "retry.sh": os.path.join(HERE, "..", "retry.sh"),
}

# flags a shell script passes through to another program rather than handling
PASS_THROUGH = {"--no-corpus"}   # named in prose, handled by precommit
INTERNAL = {"--list-checks"}     # ratchet calls verify_google with it


def strip_noise(src):
    """Remove comments and docstrings before looking for flags."""
    src = re.sub(r'"""(?:.|\n)*?"""', "", src)
    src = re.sub(r"'''(?:.|\n)*?'''", "", src)
    src = re.sub(r"#[^\n]*", "", src)
    return src


def flags_in(text):
    """Every flag mentioned, anywhere - used for the document side."""
    return set(re.findall(r"--[a-z][a-z-]+", text))


def parsed_flags(src, shell=False):
    """Every flag the code itself handles, with the prose removed first.

    A shell script also carries flags that belong to the programs it calls -
    `git log --format`, `git diff --cached`. Those are not its interface, so for a
    shell script a flag counts only when the script dispatches on it: a `--flag)`
    case arm, or a `" --flag"` string it compares against. Python has no such
    ambiguity, so any string literal counts - which covers `"--flag" in argv`,
    `argv.index("--flag")` and a helper call like `num("--moved")` alike.
    """
    src = strip_noise(src)
    if shell:
        found = set(re.findall(r"^\s*(--[a-z][a-z-]+)\)", src, flags=re.M))
        found |= set(re.findall(r'"(--[a-z][a-z-]+)"', src))
        return found
    return set(re.findall(r'"(--[a-z][a-z-]+)"', src))


def main():
    if not os.path.exists(DOC):
        print("TOOLBOX.md missing")
        return 1
    doc = open(DOC, encoding="utf-8").read()

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
        # Resolve against this file, not the caller's working directory. The python
        # entries are bare file names while the shell ones are built from HERE, so
        # running this from the repo root - which is where the gates and the briefs
        # invoke every other tool - found none of the eleven and reported all eleven
        # as missing sources.
        if not os.path.isabs(path):
            path = os.path.join(HERE, path)
        if not os.path.exists(path):
            problems.append("%s: source file not found at %s" % (tool, path))
            continue
        src = open(path, encoding="utf-8", errors="ignore").read()
        src_flags = parsed_flags(src, shell=(tool in SHELL))
        doc_flags = flags_in(sec)

        missing = sorted(f for f in doc_flags
                         if f not in src_flags and f not in PASS_THROUGH)
        if missing:
            problems.append("%s: documented but not in the code: %s"
                            % (tool, ", ".join(missing)))

        undocumented = sorted(f for f in src_flags
                              if f not in doc_flags
                              and f not in ("--help", "--version", "--quiet", "--strict")
                              and f not in INTERNAL)
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
