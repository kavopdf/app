#!/usr/bin/env python3
"""
hypothesis.py - carry what has already been tried from one attempt to the next.

WHY THIS EXISTS
  A hard defect class gets twelve attempts. Without a memory, those are twelve
  independent tries: attempt three rules out "the line box height comes from the
  font metric", reverts, and attempt four opens the same question because nobody
  wrote the answer down. Twelve attempts that each start from zero are worth one
  attempt, repeated.

  ATTEMPTS.json records the OUTCOME of an attempt - kept, improved, reverted,
  error. It does not record the reasoning, which is the part that costs the time
  and the only part worth keeping.

  So each class gets a ledger. Every attempt writes down what it believed and what
  the evidence showed, and every later attempt reads it first. The ledger is
  markdown on purpose: it is committed, it is readable in a diff, and a human can
  correct it.

WHAT A LINE LOOKS LIKE
  - RULED OUT - the line box height comes from the font metric, not from w:line
    evidence: calibrated 240/360/480 twips, pitch moved 11.3/17.1/22.8 pt
  - CONFIRMED - Google writes at 95% of the requested line height
    evidence: three variants, 240 twips gave 11.3 pt
  - UNTESTED - the paragraph mark's own font size may set the line box

USAGE
  hypothesis.py --show "19_worst_dy (+3)"
  hypothesis.py --next "19_worst_dy (+3)"
  hypothesis.py --add "19_worst_dy (+3)" "the line box comes from the font metric" \
                --result ruled-out --evidence "calibrated 240/360/480 twips"
  hypothesis.py --add "19_worst_dy (+3)" "the paragraph mark sets the line box" \
                --result untested
"""
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "HYPOTHESES.md")
RESULTS = {"ruled-out": "RULED OUT", "confirmed": "CONFIRMED", "untested": "UNTESTED"}
HEADER = (
    "# Hypotheses - what was tried, and what it proved\n\n"
    "One section per defect class. Written by `hypothesis.py`, read by every attempt\n"
    "before it forms its own theory. The point is that attempt twelve starts where\n"
    "attempt eleven finished instead of where attempt one started.\n\n"
    "RULED OUT entries are the expensive ones - they cost a calibration run each.\n"
    "Do not re-test one without new evidence, and if you do, say what changed.\n"
)


def load():
    if not os.path.exists(LEDGER):
        return {}
    sections, current = {}, None
    for line in open(LEDGER, encoding="utf-8"):
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            current = m.group(1)
            sections.setdefault(current, [])
            continue
        if current and line.strip().startswith("- "):
            sections[current].append(line.rstrip())
            continue
        if current and line.startswith("  ") and sections[current]:
            sections[current][-1] += "\n" + line.rstrip()
    return sections


def save(sections):
    out = [HEADER]
    for cls in sorted(sections):
        out.append("## %s\n" % cls)
        for entry in sections[cls]:
            out.append(entry + "\n")
        out.append("")
    open(LEDGER, "w", encoding="utf-8").write("\n".join(out))


def add(cls, text, result, evidence):
    sections = load()
    sections.setdefault(cls, [])
    label = RESULTS.get(result, result.upper())
    entry = "- %s - %s" % (label, text.strip())
    if evidence:
        entry += "\n  evidence: %s" % evidence.strip()
    entry += "\n  recorded: %s" % time.strftime("%Y-%m-%d %H:%M")
    # the same hypothesis twice is noise, not a record
    for existing in sections[cls]:
        if text.strip().lower() in existing.lower():
            print("already recorded for this class - not adding a duplicate")
            return 0
    sections[cls].append(entry)
    save(sections)
    print("%s: %s" % (label, text.strip()[:70]))
    return 0


def show(cls, only_next=False):
    sections = load()
    entries = sections.get(cls, [])
    if not entries:
        print("no hypotheses recorded for %r" % cls)
        print("nothing has been tried on this class yet - start with a calibration run")
        return 1
    if only_next:
        live = [e for e in entries if "UNTESTED" in e.split("\n")[0]]
        if live:
            print("still untested for %r:" % cls)
            for e in live:
                print(e)
            return 0
        ruled = sum(1 for e in entries if "RULED OUT" in e.split("\n")[0])
        conf = sum(1 for e in entries if "CONFIRMED" in e.split("\n")[0])
        print("%r: %d ruled out, %d confirmed, nothing left untested"
              % (cls, ruled, conf))
        print("Every theory has been tested. Form a new one from the evidence above,")
        print("or record the class as genuinely unfixable with those numbers.")
        return 0
    for e in entries:
        print(e)
    return 0


def main(argv):
    if "--add" in argv:
        i = argv.index("--add")
        cls = argv[i + 1]
        text = argv[i + 2]
        result = "untested"
        evidence = ""
        if "--result" in argv:
            result = argv[argv.index("--result") + 1]
        if "--evidence" in argv:
            evidence = argv[argv.index("--evidence") + 1]
        return add(cls, text, result, evidence)

    if "--show" in argv:
        return show(argv[argv.index("--show") + 1])

    if "--next" in argv:
        return show(argv[argv.index("--next") + 1], only_next=True)

    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
