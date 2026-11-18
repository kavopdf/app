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
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "LAST-MESSAGE.md")
MIN = 400


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
    open(OUT, "w", encoding="utf-8").write(text)
    print("wrote %s - %d characters" % (OUT, len(text.strip())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
