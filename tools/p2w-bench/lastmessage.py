#!/usr/bin/env python3
"""lastmessage.py - store the exact text the run is about to send, so it can be read afterwards.

WHY THIS EXISTS. The cron delivers the fixer's final message to the user's chat and stores nothing.
`cron runs` returns output_summary: null for every run, so the one text the user actually reads exists
only in their chat window. Twice on 18 Nov the only way to see it was for the user to export the cron
page to a PDF and attach it - and the PDF carries the whole prompt too, seven pages of it.

report.py writes LAST-MESSAGE.md from what it printed, but the run then adds the three things only it
knows (the prose headline, the verdict per idea, why the silence happened) - so the file and the
message drift apart by exactly the parts that matter.

This closes that: the run writes its finished message here, commits it, then sends the same text.

    python3 tools/p2w-bench/lastmessage.py --file /tmp/report.md
    python3 tools/p2w-bench/lastmessage.py --check        # is the file there and non-trivial?
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "LAST-MESSAGE.md")
MIN = 400

# Rows of the Progress table that MUST equal report.py's own value. Everything else in the
# message is the run's to write: the headline, the per-idea verdicts, why the silence
# happened, the subagent durations. These are not.
BACKED_ROWS = (
    "documents improved this run",
    "documents improved, round total",
    "corpus improvement vs 15 nov",
    "regressions",
    "exempt, not measured",
    "fixed to 99%",
    "moved but still open",
    "classes solved",
    "committed",
)

_NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def _numbers(cell):
    """Every number in a table cell, in order, with commas and bold stripped."""
    # Cut at the first backtick: what follows is a file name or a document name, and a
    # commit sha or a document called `300_prescription_rx` is not a number this row is
    # making a claim about.
    c = cell.split("`")[0]
    c = c.replace("**", "").replace("\u2014", " ").replace("\u2192", " ")
    return [n.replace(",", "") for n in _NUM.findall(c)]


def progress_rows(text):
    """{lower-cased label: cell} for the Progress table of a report.

    The table is the one whose rows look like `| label | value |` and which sits under a
    `## Progress` heading. Reading only that table keeps a number in the prose from being
    compared against a number in a table, which would be a false alarm.
    """
    out = {}
    inside = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            inside = s.lower().startswith("## progress")
            continue
        if not inside or not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = cells[0].replace("**", "").replace("`", "").strip().lower()
        if not label or set(label) <= set(":- "):
            continue
        out[label] = cells[1]
    return out


def report_py_rows():
    """Run report.py and read its Progress table. None when it cannot be run."""
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "report.py")],
                           capture_output=True, text=True, timeout=280)
        if r.returncode != 0 or "## Progress" not in r.stdout:
            return None
        return progress_rows(r.stdout)
    except Exception:
        return None


def verify(text):
    """Compare the report's Progress rows against report.py. Returns (problems, checked)."""
    mine = progress_rows(text)
    theirs = report_py_rows()
    if theirs is None:
        return None, 0
    problems = []
    checked = 0
    for label in BACKED_ROWS:
        if label not in mine:
            continue
        if label not in theirs:
            problems.append("%-38s in the message but report.py has no such row" % label)
            continue
        a, b = _numbers(mine[label]), _numbers(theirs[label])
        checked += 1
        # The FIRST number is the claim. The rest are compared only when both sides carry
        # the same count, because a row may name a document in backticks on one side and in
        # plain text on the other - `1 - 416_many_tiny_pages` against `1 - 416` is the same
        # claim twice, and refusing it would teach a run to distrust a working check.
        same = (a[:1] == b[:1]) and (len(a) != len(b) or a == b)
        if not same:
            problems.append("%-38s message %s  !=  report.py %s" % (label, a, b))
    for label, cell in mine.items():
        if label in BACKED_ROWS:
            continue
        if label in theirs:
            continue
        # A row nobody backs. It is allowed only if it carries no number.
        if _numbers(cell):
            problems.append("%-38s carries %s and no tool produces this row"
                            % (label, _numbers(cell)))
    return problems, checked


def main(argv):
    if "--check" in argv:
        if not os.path.exists(OUT):
            print("MISSING - write the report to %s before you commit" % OUT)
            return 1
        n = len(open(OUT, encoding="utf-8").read().strip())
        if n < MIN:
            print("TOO SHORT - %d characters. That is not a report." % n)
            return 1
        print("ok - %d characters" % n)
        return 0
    if "--file" in argv:
        i = argv.index("--file") + 1
        if i >= len(argv):
            print("--file needs a path")
            return 2
        text = open(argv[i], encoding="utf-8").read()
    else:
        text = sys.stdin.read()
    if len(text.strip()) < MIN:
        print("refused: %d characters is not a report" % len(text.strip()))
        return 2
    problems, checked = verify(text)
    if problems is None:
        print("WARNING: report.py could not be run, so no number in this message was checked "
              "against it. Say so in the report.")
    elif problems:
        print("REFUSED - %d row(s) do not match report.py. Copy its numbers; do not retype them."
              % len(problems))
        for p in problems:
            print("  " + p)
        return 3
    else:
        print("numbers: %d Progress row(s) match report.py" % checked)
    open(OUT, "w", encoding="utf-8").write(text)
    print("wrote %s - %d characters" % (OUT, len(text.strip())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
