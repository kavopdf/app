#!/usr/bin/env python3
"""
record.py - keep the numbers the verifier already computed, so nobody measures twice.

THE WASTE THIS FIXES
  verify_google.py --json returns, for every check, the source value and the render
  value: 20_within_10pt source=100 render=62, 41_block_spacing source=6.1
  render=9.4. That is the material a fix is built from - it says by how much and in
  which direction the conversion is wrong.

  Nothing kept it. The baseline cron wrote a pass/fail into BASELINE.md and threw
  the numbers away, so the fixer had to push ten documents through Drive again
  every single run just to see values that had already been measured. Ten
  documents is three Drive calls each, and the fixer does it once per class, every
  four hours, across three rounds. Most of that work is a repeat.

  RESULTS.jsonl keeps one line per document per round per engine:
      {"round": 1, "engine": "2a68de6", "doc": "01_stamp...", "score": 31,
       "total": 58, "failed": [...], "values": {"20_within_10pt": [100, 62], ...}}

  The fixer reads the line instead of re-measuring. Re-measuring is still correct
  when a fix has just been made - the record is only used to understand the
  starting state.

USAGE
  python3 tools/p2w-bench/record.py res/*.json --round 1 --engine 2a68de6
  python3 tools/p2w-bench/record.py --show 01_stamp_rotated_15deg_upright
  python3 tools/p2w-bench/record.py --show 01_stamp_rotated_15deg_upright --check 20_within_10pt
"""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "RESULTS.jsonl")

# The human-readable table the gate checks. record.py used to only read this file; the
# fixer was told to hand-edit it, which is twenty rows of six columns per attempt.
BASE = os.path.join(HERE, "BASELINE.md")

# The .txt half of the tool keeps its own store. One file would make a .txt regression
# and a .docx regression indistinguishable in the record, and the two are fixed by
# different code in different classes.
STORE_TXT = os.path.join(HERE, "RESULTS-TXT.jsonl")


def load(store=None):
    store = store or STORE
    if not os.path.exists(store):
        return []
    out = []
    for line in open(store, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


KEEP_VALUES_FOR = 2     # engines whose raw values are still worth keeping


def _trim_values(index):
    """Drop the raw values from all but the last few engines.

    A row carries `values` - every one of the 59 checks with its source and rendered
    number - and that is about 4 KB. The fixer measures twenty documents under a new
    engine id on every attempt, so twenty-four attempts a day added roughly 2 MB a day:
    a week would have made this file 14 MB and a single `cat` would have been fatal.

    Nothing reads `values` except a person looking at one document. The classifier groups
    on `failed`, the ratchet compares `failed` and the score, the gates count documents.
    So the last two engines keep theirs - enough for a before/after - and every older row
    keeps its score and its failed list, which is everything the pipeline uses.
    """
    engines = []
    for e in index.values():
        eng = e.get("engine")
        if eng not in engines:
            engines.append(eng)
    keep = set(engines[-KEEP_VALUES_FOR:]) if len(engines) > KEEP_VALUES_FOR else set(engines)
    # A committed engine is a reference, and a reference does not expire. The baseline row
    # carries source=N render=N for every check - the numbers that say how far off the
    # conversion was and in which direction - and the fixer reads them with
    # `record.py --show <doc>` before forming any theory. Trimming those away to save space
    # would leave it knowing only that a check failed, never by how much.
    #
    # Only dirty engines are history: each attempt writes twenty rows under its own id and
    # none of them is a reference to anything. Keeping the last two of those bounds the file
    # without touching the row the whole comparison is built on.
    keep |= {e for e in engines if "-d" not in e}
    for e in index.values():
        if e.get("engine") not in keep:
            e.pop("values", None)
    return index


def append(entries, store=None):
    """Append, replacing any earlier line for the same (round, engine, doc)."""
    store = store or STORE
    existing = load(store)
    key = lambda e: (e.get("round"), e.get("engine"), e.get("doc"))
    index = {key(e): e for e in existing}
    for e in entries:
        index[key(e)] = e
    _trim_values(index)
    try:
        note("record", "%d row(s) written, store now holds %d" % (len(entries), len(index)))
    except NameError:
        pass
    with open(store, "w", encoding="utf-8") as f:
        for e in sorted(index.values(), key=lambda e: (e.get("round", 0),
                                                       e.get("doc", ""))):
            f.write(json.dumps(e, sort_keys=True) + "\n")
    return len(index)


def update_baseline(round_no=0, engine=""):
    """Rewrite the BASELINE.md row for every document the store has for this round.

    WHY THIS EXISTS
      commit-gate.sh demands that BASELINE.md changed whenever the engine changed, and until
      now nothing in the pipeline wrote it. The brief said "Edit BASELINE.md IN THE LOCAL
      CLONE ... rows are exactly six columns" and left the fixer to hand-edit twenty rows of
      six columns each - copying the failed-check list out of verify_google.py's JSON by eye.
      That is twenty chances to mistype a check name, and the gate refuses a commit whose
      evidence does not line up. It had never been exercised either: no fix has ever been
      kept, so the first run that keeps one would have been the first to try it.

    WHAT IT DOES NOT DO
      It does not rebuild the file. The 10 Nov disaster was a rebuild from a fetched string,
      which deleted 119 rows. This reads BASELINE.md, replaces the row for a document it has
      a measurement for, and writes every other line back exactly as it was. A document with
      no new measurement keeps its old row untouched.

    Returns the number of rows replaced.
    """
    if not os.path.exists(BASE):
        return 0

    # Only a COMMITTED engine may write into BASELINE.md.
    #
    # An engine id is <hash>, or <hash>-d<sha1 of the diff> for a build that was measured and
    # then reverted. Writing a -d engine's numbers here would put a reverted attempt's scores
    # into the table the gate and the ratchet treat as the truth - 362_price_list_dense reads
    # 51/59 on the committed engine and 53/59 on a reverted one, and the second number is a
    # measurement of code that no longer exists.
    if not engine:
        committed = []
        for e in load():
            eng = e.get("engine") or ""
            if "-d" in eng:
                continue
            if round_no and e.get("round") != round_no:
                continue
            if eng and eng not in committed:
                committed.append(eng)
        if not committed:
            return 0
        engine = committed[-1]

    latest = {}
    for e in load():
        if round_no and e.get("round") != round_no:
            continue
        if e.get("engine") != engine:
            continue
        doc = e.get("doc")
        if not doc:
            continue
        # Later entries win: the store is written in measurement order and append() replaces
        # a row for the same (round, engine, doc), so the last one seen is the current one.
        latest[doc] = e
    if not latest:
        return -1

    lines = open(BASE, encoding="utf-8").read().split("\n")
    out, replaced = [], 0
    today = time.strftime("%d %b")
    for line in lines:
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 6 and cells[0] in latest:
                e = latest[cells[0]]
                failed = ", ".join(e.get("failed", []))
                score = "%s/%s" % (e.get("score"), e.get("total"))
                verdict = "PASS" if not e.get("failed") else "FAIL"
                eng = e.get("engine", "")
                # Only write a row that actually changed. The gate reads "BASELINE.md changed"
                # as evidence that a measurement happened, so a rewrite that only refreshes
                # the date on all 208 rows would satisfy the gate while proving nothing.
                if (cells[1], cells[2], cells[3], cells[4]) == (score, verdict, failed, eng):
                    out.append(line)
                    continue
                out.append("| %s | %s | %s | %s | %s | %s |"
                           % (cells[0], score, verdict, failed, eng, today))
                replaced += 1
                continue
        out.append(line)
    if replaced:
        with open(BASE, "w", encoding="utf-8") as f:
            f.write("\n".join(out))
    return replaced


def main(argv):
    if "--baseline" in argv:
        rnd = int(argv[argv.index("--round") + 1]) if "--round" in argv else 0
        eng = argv[argv.index("--engine") + 1] if "--engine" in argv else ""
        n = update_baseline(rnd, eng)
        if n < 0:
            print("baseline: the store has no row for this round/engine - nothing written")
            return 1
        if n == 0:
            print("baseline: every row already matches the store - nothing written")
            return 0
        print("baseline: %d row(s) rewritten from the store" % n)
        try:
            note("record", "BASELINE.md: %d row(s) rewritten" % n)
        except Exception:
            pass
        return 0

    if "--show" in argv:
        doc = argv[argv.index("--show") + 1]
        only = argv[argv.index("--check") + 1] if "--check" in argv else None
        rows = [e for e in load() if e.get("doc") == doc]
        if not rows:
            print("no record for %s - it has not been measured yet" % doc)
            return 1
        rows.sort(key=lambda e: (e.get("round", 0), e.get("engine", "")))
        for e in rows[-3:]:
            print("round %s  engine %s  %s/%s  %d failing"
                  % (e.get("round"), e.get("engine"), e.get("score"),
                     e.get("total"), len(e.get("failed", []))))
            vals = e.get("values", {})
            keys = [only] if only else sorted(vals)
            for k in keys:
                if k in vals:
                    v = vals[k]
                    if isinstance(v, dict):
                        src, ren = v.get("source", "?"), v.get("render", "?")
                    elif isinstance(v, (list, tuple)) and len(v) >= 2:
                        src, ren = v[0], v[1]
                    else:
                        src, ren = v, "?"
                    print("    %-26s source=%-10s render=%-10s %s"
                          % (k, src, ren, "FAIL" if k in e.get("failed", []) else "pass"))
        return 0

    store = STORE_TXT if "--txt" in argv else STORE
    rnd = int(argv[argv.index("--round") + 1]) if "--round" in argv else 0
    engine = argv[argv.index("--engine") + 1] if "--engine" in argv else ""
    files = [a for a in argv[1:] if a.endswith(".json")]
    if not files:
        files = sorted(glob.glob(os.path.join(HERE, "res", "*.json")))
    if not files:
        print("record: nothing to record - no --json output given or found in res/")
        return 0

    entries = []
    for path in files:
        try:
            j = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        doc = j.get("document") or os.path.splitext(os.path.basename(path))[0]
        entries.append({
            "round": rnd,
            "engine": engine,
            "doc": doc,
            "score": j.get("passed"),
            "total": j.get("total"),
            "failed": j.get("failed", []),
            "values": j.get("checks", {}),
        })

    total = append(entries, store)
    print("record: %d documents recorded from %d files, %d in the store"
          % (len(entries), len(files), total))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
