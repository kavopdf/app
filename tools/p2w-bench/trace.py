#!/usr/bin/env python3
"""
trace.py - what the run actually did, written by the tools it called.

WHY THIS EXISTS
    A cron run is a black box from outside. The run reports succeeded or failed, its own
    output is not retrievable, and the only durable evidence is a commit. On 12 Nov the
    fixer worked for seventeen minutes, reported success, and left no commit at all - and
    there was no way to tell whether it had failed at the clone, the build, the class pick,
    the calibration or the measurement. Every tool it would have called works when called
    by hand, so the failure was somewhere between them, and nothing recorded the path.

    An instruction to log is a promise. A tool that logs is a fact. So the tools write it.

WHAT IT WRITES
    TRACE.md, one line per call, appended, never rewritten:

        | 12 Nov 17:41 | fixer | build-engine | started |
        | 12 Nov 17:46 | fixer | build-engine | engine built - ConvertAll ready |
        | 12 Nov 17:47 | fixer | classify     | 43 classes from 208 documents |

    The run name is guessed from ROUND.json's slot fields, so a line knows whether it came
    from the baseline, the classifier or the fixer without being told.

HOW IT MUST BEHAVE
    It must never break the tool that calls it. Every entry point is wrapped: a trace that
    raises would turn a working run into a failed one, which is worse than no trace.

    It must never grow without limit. TRACE.md is trimmed to the last 400 lines on write.

USAGE
    from trace import note
    note("build-engine", "started")
    note("build-engine", "engine built - ConvertAll ready")

    python3 trace.py --show          # last 40 lines
    python3 trace.py --show 200      # last 200
    python3 trace.py --clear
"""

import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TRACE = os.path.join(HERE, "TRACE.md")
ROUND = os.path.join(HERE, "ROUND.json")
MAX_LINES = 400

HEADER = (
    "# Trace - what the tools were actually asked to do\n\n"
    "Written by the tools themselves, not by the run. A run that dies mid-way leaves its\n"
    "path here, which is the one thing the run's own report cannot do. Commit it with the\n"
    "claim and after each step; it is not code and cannot break anything.\n\n"
    "| time | run | tool | what happened |\n"
    "|---|---|---|---|\n"
)


def ist(fmt="%d %b %H:%M"):
    """The wall clock every file in this directory is written in. The sandbox is UTC."""
    return time.strftime(fmt, time.gmtime(time.time() + 5 * 3600 + 30 * 60))


def who():
    """Which cron is calling, from the slots ROUND.json already keeps."""
    try:
        s = json.load(open(ROUND, encoding="utf-8"))
    except Exception:
        return "?"
    now = time.time()
    best, best_age = "?", 1e9
    for name in ("fixer", "classifier", "baseline"):
        t = s.get("%s_started" % name) or 0
        if t:
            age = now - t
            if age < best_age:
                best, best_age = name, age
    return best


def trim(path, keep, header_lines=0):
    """Keep the last `keep` lines of a growing log, with its header intact.

    RUN-LOG.md and INCIDENTS.md had no cap. One day of runs left RUN-LOG at 117 lines; three
    months at 24 runs a day is about ten thousand. A log nobody can read whole is not a record,
    it is a liability - and the fixer is told not to read the big files, so a log that grows
    forever is a log that stops being read at all.

    Nothing is lost: the lines that fall off are in git. This keeps the live file at a size a run
    can actually open.
    """
    try:
        if not os.path.exists(path):
            return 0
        lines = open(path, encoding="utf-8").readlines()
        if len(lines) <= keep:
            return 0
        head = lines[:header_lines]
        tail = lines[-(keep - header_lines):]
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(head)
            f.writelines(tail)
        return len(lines) - keep
    except Exception:
        return 0


def trim_all():
    """Every log this directory grows, capped in one place."""
    here = os.path.dirname(os.path.abspath(__file__))
    trim(os.path.join(here, "RUN-LOG.md"), 200)
    trim(os.path.join(here, "INCIDENTS.md"), 120)


def note(tool, what):
    """Append one line. Never raises - a trace that breaks a run is worse than no trace."""
    try:
        line = "| %s | %s | %s | %s |\n" % (
            ist(), who(), tool, str(what).replace("|", "/").replace("\n", " ")[:200])
        if not os.path.exists(TRACE):
            with open(TRACE, "w", encoding="utf-8") as f:
                f.write(HEADER)
        with open(TRACE, "a", encoding="utf-8") as f:
            f.write(line)
        trim_all()
        # Trim: keep the header and the last MAX_LINES of entries.
        with open(TRACE, encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > MAX_LINES + 8:
            keep = lines[:8] + lines[-(MAX_LINES):]
            with open(TRACE, "w", encoding="utf-8") as f:
                f.writelines(keep)
    except Exception:
        pass


def main(argv):
    if "--clear" in argv:
        try:
            os.remove(TRACE)
            print("trace cleared")
        except FileNotFoundError:
            print("no trace to clear")
        return 0
    n = 40
    if "--show" in argv:
        i = argv.index("--show")
        if i + 1 < len(argv):
            try:
                n = int(argv[i + 1])
            except ValueError:
                pass
    if not os.path.exists(TRACE):
        print("no trace yet - nothing has been run")
        return 0
    lines = open(TRACE, encoding="utf-8").read().splitlines()
    body = [l for l in lines if l.startswith("| ")]
    for l in body[-n:]:
        print(l)
    print("\n%d entries" % len(body))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
