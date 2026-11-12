#!/usr/bin/env python3
"""Is the measure phase finished? One question, one answer, three numbers.

The baseline advances to classify only when both halves are complete. That used to be
three separate checks a run had to remember to make, in the right order, and getting it
wrong has two failure modes that both look like success:

  too eager   - advance on the word half alone, and the text store is left short forever
                because nothing downstream ever comes back for it
  too strict  - refuse while one document that genuinely cannot be converted holds the
                gate shut, and every round measures 207 documents and never closes

So the rule lives here, in code, where it can be tested, instead of in a paragraph a run
may or may not follow.

    python3 tools/p2w-bench/measure_gate.py            # human answer, exit 0 or 1
    python3 tools/p2w-bench/measure_gate.py --quiet    # exit code only

Exit 0 means every row is scored (or exempted) and both text gaps are zero.
Exit 1 means not yet, and the lines above say which half is short.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "BASELINE.md")
EXEMPT = os.path.join(HERE, "EXEMPT.json")
ROUND = os.path.join(HERE, "ROUND.json")


def exempt():
    data = {"docx": {}, "txt": {}}
    if os.path.exists(EXEMPT):
        try:
            with open(EXEMPT, encoding="utf-8") as f:
                raw = json.load(f)
            for half in ("docx", "txt"):
                if isinstance(raw.get(half), dict):
                    data[half] = raw[half]
        except (ValueError, OSError):
            pass
    return data


def rows():
    """(document, scored) for every row of BASELINE.md."""
    out = []
    if not os.path.exists(BASE):
        return out
    with open(BASE, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("| ") or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or not cells[0] or cells[0].lower() == "document":
                continue
            score = cells[1] if len(cells) > 1 else ""
            out.append((cells[0], bool(re.match(r"\d+\s*/\s*\d+", score))))
    return out


def state():
    ex = exempt()
    all_rows = rows()
    scored = [d for d, ok in all_rows if ok]
    unscored = [d for d, ok in all_rows if not ok]
    # A document exempted for the word half is allowed to stay unscored.
    blocked_docx = [d for d in unscored if d not in ex["docx"]]
    return {
        "total": len(all_rows),
        "scored": len(scored),
        "exempt_docx": len(ex["docx"]),
        "exempt_txt": len(ex["txt"]),
        "blocked_docx": blocked_docx,
    }


def gap(args):
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "txt_gap.py"), "--count"] + args,
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except ValueError:
        return -1


def round_of():
    try:
        with open(ROUND, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return {}


def engine_hash():
    """The engine this run is measuring.

    git first, because that is the definition. If git is unavailable - a bare checkout, a
    sandbox without the repo - fall back to the engine on the newest row in the store,
    which is what the last measurement actually used. Returning nothing here would make
    the round gap -1 and the gate would say NOT READY forever for a reason that has
    nothing to do with the corpus.
    """
    out = os.popen("git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/ 2>/dev/null").read().strip()
    if out:
        return out
    store = os.path.join(HERE, "RESULTS.jsonl")
    last = ""
    if os.path.exists(store):
        with open(store, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    last = json.loads(line).get("engine") or last
                except ValueError:
                    continue
    return last


def main(argv):
    s = state()
    rnd = round_of().get("round", 1)
    engine = engine_hash()

    backfill = gap([])
    this_round = gap(["--round", str(rnd), "--engine", engine]) if engine else -1

    ok = (not s["blocked_docx"]) and backfill == 0 and this_round == 0

    if "--quiet" not in argv:
        print("docx   %d/%d scored, %d exempt, %d still blocking"
              % (s["scored"], s["total"], s["exempt_docx"], len(s["blocked_docx"])))
        if s["blocked_docx"][:5]:
            print("       blocking: %s" % ", ".join(s["blocked_docx"][:5]))
        print("txt    backfill gap %d, %d exempt" % (backfill, s["exempt_txt"]))
        print("round  %d missing for round %s on engine %s"
              % (this_round, rnd, engine or "?"))
        print("READY - both halves complete" if ok else "NOT READY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
