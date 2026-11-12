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

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "RESULTS.jsonl")

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
    with open(store, "w", encoding="utf-8") as f:
        for e in sorted(index.values(), key=lambda e: (e.get("round", 0),
                                                       e.get("doc", ""))):
            f.write(json.dumps(e, sort_keys=True) + "\n")
    return len(index)


def main(argv):
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
