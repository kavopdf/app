#!/usr/bin/env python3
"""
docnames.py - the exact documents this run measured, ready to paste into a commit message.

WHY THIS EXISTS
  The baseline cron writes its own commit message, and on 11 Nov it wrote:

      baseline: measure 5 more documents (375-382)

  Five documents were measured: 375_attendance_register, 37_font_not_embedded_substitution,
  380_runbook_terminal_output, 381_incident_report_timeline, 382_architecture_diagram.

  "(375-382)" reads as eight. It is wrong twice over: the corpus is not contiguous -
  37_font_not_embedded_substitution sits in the middle of that range - and 376 to 379
  are not in the corpus at all. A range is a guess dressed as a summary, and the commit
  log is the only record of what was actually measured.

  So the list is not written from memory. It is read from the file, by this script, and
  pasted.

USAGE
  python3 tools/p2w-bench/docnames.py            # comma-separated names, for the message
  python3 tools/p2w-bench/docnames.py --count    # just how many
  python3 tools/p2w-bench/docnames.py --long     # one per line, for reading
  python3 tools/p2w-bench/docnames.py --since <rev>   # compare against another commit

Exit 0 always - a commit message that cannot be generated is not a reason to stop a
measurement run. It prints "no document changed" when nothing did.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "BASELINE.md")
REL = "tools/p2w-bench/BASELINE.md"


def rows(text):
    """document -> score, from a BASELINE.md body. Empty scores count as absent."""
    out = {}
    for line in text.split("\n"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "document":
            continue
        out[cells[0]] = cells[1] if len(cells) > 1 else ""
    return out


def main(argv):
    rev = "HEAD"
    if "--since" in argv:
        rev = argv[argv.index("--since") + 1]

    if not os.path.exists(BASE):
        print("no BASELINE.md - nothing measured")
        return 0

    now = rows(open(BASE, encoding="utf-8").read())
    shown = subprocess.run(["git", "show", "%s:%s" % (rev, REL)],
                           cwd=HERE, capture_output=True, text=True)
    if shown.returncode != 0 or not shown.stdout.strip():
        # Cannot compare, so every row looks new. Say so rather than printing a list
        # that reads as "these all changed" when the truth is "the comparison failed".
        print("could not read %s at %s - listing every scored row" % (REL, rev),
              file=sys.stderr)
        before = {}
    else:
        before = rows(shown.stdout)

    changed = sorted(n for n, s in now.items() if before.get(n, "") != s)
    if not changed:
        print("no document changed")
        return 0

    if "--count" in argv:
        print(len(changed))
    elif "--long" in argv:
        for n in changed:
            print(n)
    else:
        print(", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
