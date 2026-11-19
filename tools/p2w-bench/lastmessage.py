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


def _report_json():
    """report.py's own numbers, as a dict. None when it cannot be read."""
    import json
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "report.py"), "--json"],
                           capture_output=True, text=True, timeout=120, cwd=os.path.dirname(HERE))
        if r.returncode != 0 or not r.stdout.strip():
            return None
        return json.loads(r.stdout)
    except Exception:
        return None


_HHMM = re.compile(r"(\d{1,2}):(\d{2})")


def verify_facts(text, data):
    """Compare the report's PROSE against report.py - the timing, the corpus size, the .txt, the agents.

    WHY THIS EXISTS. verify() above checks the Progress table and nothing else, and every wrong
    number the 19 Nov run printed lived outside that table:

      * the header said "slot 16:11 -> 17:18 IST - 1h 07m". RUN.json says the slot ended at 17:00
        and lasted 48 minutes. The run wrote the clock it was looking at, not the one it recorded,
        and over-reported its own runtime by nineteen minutes.
      * every sentence about the corpus said "of 212". The corpus is 213; 212 is the intersection of
        the baseline table and the current one, because 416_many_tiny_pages was exempt when the
        baseline was taken. Two different quantities, one word.
      * "29 files in 7 commit(s) from 0b8c821" - it was 25 files in 8 commits, and only three of them
        came after 0b8c821.
      * the .txt was not mentioned at all, and an agent's window was given as "16:22 -> 16:32" with
        nothing behind it.

    A number a run types is a number a run can get wrong. These are the ones it types most.
    """
    if not data:
        return ["report.py --json could not be read - nothing in this message is verified"]
    problems = []
    run = data.get("run") or {}
    co = data.get("corpus") or {}
    tx = data.get("txt") or {}

    # ---- 1. THE HEADER'S CLOCK ------------------------------------------------------------
    head = "\n".join(text.splitlines()[:12])
    m = re.search(r"slot\s+(\d{1,2}:\d{2})\s*(?:→|->|—)\s*(\d{1,2}:\d{2})\s*IST", head)
    if not m:
        problems.append("header: no 'slot HH:MM -> HH:MM IST' window, so the timing cannot be checked")
    elif run.get("present"):
        if m.group(1) != (run.get("started") or ""):
            problems.append("header: start %s, report.py says %s" % (m.group(1), run.get("started")))
        if m.group(2) != (run.get("ended") or ""):
            problems.append("header: end %s, report.py says %s" % (m.group(2), run.get("ended")))
    # the duration, wherever it appears in the first twelve lines
    mins = run.get("minutes")
    if isinstance(mins, int) and mins > 0:
        for hh, mm in _HHMM.findall(head):
            pass
        d = re.search(r"(\d+)\s*h\s*(\d+)\s*m|(\d+)\s*min", head)
        if d:
            claimed = (int(d.group(1)) * 60 + int(d.group(2))) if d.group(1) else int(d.group(3))
            if abs(claimed - mins) > 1:
                problems.append("header: duration %d min, report.py says %d min" % (claimed, mins))

    # ---- 2. THE CORPUS SIZE ---------------------------------------------------------------
    docs = co.get("docs")
    if isinstance(docs, int) and docs > 0:
        # ONLY A NUMBER NEAR THE CORPUS SIZE CAN BE A CLAIM ABOUT THE CORPUS. "5 of 10" is a
        # class's documents and "of 22" is a batch; flagging those teaches a run to ignore the
        # check, which is worse than not having it. A corpus claim is always in the hundreds.
        for n in re.findall(r"of\s+\*{0,2}(\d{2,4})\*{0,2}\b", text):
            v = int(n)
            if not (100 <= v <= 400):
                continue
            if v != docs and v != co.get("compared"):
                problems.append("corpus: 'of %s' appears, the corpus is %d (compared: %s)"
                                % (n, docs, co.get("compared")))
                break

    # ---- 3. THE .TXT ----------------------------------------------------------------------
    if tx.get("available"):
        scored, clean, failing = tx.get("scored"), tx.get("clean"), tx.get("failing")
        if not re.search(r"\.txt|\btxt\b", text, re.I):
            problems.append("txt: the .txt is not mentioned at all (%d scored, %d clean, %d failing)"
                            % (scored, clean, failing))
        else:
            tail = text[text.lower().find(".txt"):] if ".txt" in text.lower() else text
            for want, name in ((clean, "clean"), (failing, "failing")):
                if isinstance(want, int) and str(want) not in text:
                    problems.append("txt: %d %s in report.py, that number is not in the message"
                                    % (want, name))
                    break

    # ---- 4. THE AGENTS' TIMINGS -----------------------------------------------------------
    agents = data.get("subagents")
    rows = agents if isinstance(agents, list) else (agents or {}).get("agents") or []
    for a in rows:
        aid = (a.get("id") or "")[:12]
        if not aid:
            continue
        dep, land = a.get("deployed_at"), a.get("landed_at")
        if dep and dep not in text:
            problems.append("agent %s: deployed_at %s is not in the message" % (aid, dep))
        if land and land not in text:
            problems.append("agent %s: landed_at %s is not in the message" % (aid, land))
        mins = a.get("minutes")
        if isinstance(mins, int) and mins > 0 and str(mins) not in text:
            problems.append("agent %s: worked %d min, that number is not in the message" % (aid, mins))
    return problems


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
    # BOTH CHECKS RUN, AND EVERY PROBLEM IS PRINTED. The row check used to return before the fact
    # check ran, so a report with a wrong table row was rejected without ever telling the run that
    # its header clock was wrong too - and the run fixed the row and shipped the clock.
    problems, checked = verify(text)
    data = _report_json()
    facts = verify_facts(text, data)
    if problems is None:
        print("WARNING: report.py could not be run, so no number in this message was checked "
              "against it. Say so in the report.")
        problems = []
    bad = list(problems or []) + list(facts or [])
    if bad:
        print("REFUSED - %d number(s) in this message do not match report.py. "
              "Copy them from `report.py --json`; do not retype them." % len(bad))
        for p in bad:
            print("  " + p)
        return 3
    print("numbers: %d Progress row(s) match report.py" % checked)
    print("facts: header clock, corpus size, .txt and agent timings all match report.py")
    open(OUT, "w", encoding="utf-8").write(text)
    print("wrote %s - %d characters" % (OUT, len(text.strip())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
