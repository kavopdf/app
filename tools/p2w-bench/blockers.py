#!/usr/bin/env python3
"""blockers.py - append a BLOCKERS row with the time taken from the clock, not from memory.

WHY THIS EXISTS. On 18 Nov the 15:58 run wrote three rows stamped 16:35, 16:38 and 16:44 into a
commit made at 16:24:27 - between ten and twenty minutes in the future. Nothing caught it: the file
is markdown, the columns are free text, and the only person who would notice is a reader comparing
the row against `git log`, which is exactly what nobody does.

A timestamp typed by hand is a timestamp that can be wrong. This takes it from the system, in IST
like every other time in the pipeline, and refuses a row that does not have all six cells.

    python3 tools/p2w-bench/blockers.py \
        --doing "measuring itr-computation-with-slab-table" \
        --obstacle "the footer is a ROW of table 3, not a flow line after it" \
        --tried "implemented the anchor rule, built it, screened it - it never fires" \
        --can "yes - done, and it was the wrong thing to do" \
        --need "test the handoff's diagnosis before building on it"
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKERS = os.path.join(HERE, "BLOCKERS.md")
HEADER = "| time | what I was doing | the obstacle | what I tried | can I fix it | what is needed |"


def arg(argv, name):
    if name not in argv:
        return ""
    i = argv.index(name) + 1
    return argv[i].replace("|", "/").strip() if i < len(argv) else ""


def main(argv):
    doing = arg(argv, "--doing")
    obstacle = arg(argv, "--obstacle")
    tried = arg(argv, "--tried")
    can = arg(argv, "--can")
    need = arg(argv, "--need")
    missing = [n for n, v in (("--doing", doing), ("--obstacle", obstacle),
                              ("--can", can), ("--need", need)) if not v]
    if missing:
        print("missing: %s" % ", ".join(missing))
        print("a row with an empty cell is a row nobody can act on.")
        return 2
    stamp = time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 19800))
    row = "| %s | %s | %s | %s | %s | %s |" % (stamp, doing, obstacle, tried or "-", can, need)

    lines = open(BLOCKERS, encoding="utf-8").read().split("\n")
    try:
        head = next(i for i, l in enumerate(lines) if l.strip() == HEADER)
    except StopIteration:
        print("could not find the row header in BLOCKERS.md")
        return 1
    k = head + 2                                   # past the header and the separator
    while k < len(lines) and lines[k].startswith("| "):
        k += 1
    lines.insert(k, row)
    open(BLOCKERS, "w", encoding="utf-8").write("\n".join(lines))
    print(row)
    print("appended under '## Rows' at %s IST - taken from the clock, not typed" % stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
