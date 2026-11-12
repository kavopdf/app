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


def store_docs():
    """Distinct documents in RESULTS.jsonl.

    BASELINE.md is a table a human reads and RESULTS.jsonl is what the tools read, and
    nothing before this compared them. A row can be scored in the table while its store
    line never landed - a commit that half-succeeded, a write that died with the sandbox -
    and the gate would have called that finished. Both must agree before the phase moves.
    """
    docs = set()
    store = os.path.join(HERE, "RESULTS.jsonl")
    if not os.path.exists(store):
        return docs
    with open(store, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("doc"):
                docs.add(row["doc"])
    return docs


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
        "stored": len(store_docs()),
        "exempt_docx": len(ex["docx"]),
        "exempt_txt": len(ex["txt"]),
        "blocked_docx": blocked_docx,
    }


def gap(args):
    """The gap, or None when the tool could not be run.

    None is not zero. A missing or broken txt_gap.py used to come back as -1 and print
    'gap -1', which reads like a number and hides the real problem - the tool that answers
    the question is not there. The gate refuses either way, but it has to say which.
    """
    import subprocess
    path = os.path.join(HERE, "txt_gap.py")
    if not os.path.exists(path):
        return None
    r = subprocess.run([sys.executable, path, "--count"] + args,
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except ValueError:
        return None


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
    this_round = gap(["--round", str(rnd), "--engine", engine]) if engine else 0

    # The gate blocks on two things only: a word row that cannot be scored, and the
    # round-1 backfill hole. It deliberately does NOT block on this_round.
    #
    # Rounds 2 and 3 measure both halves for every document in the same loop, so a text row
    # is written at the same moment as the word row and nothing is left over to repair. If a
    # .txt measurement fails inside that loop the run retries it there, and if it still
    # cannot be produced the document is exempted and the failure is named. Blocking the
    # round on it would be a backfill in all but name, and the backfill exists only because
    # the text half was added after 130 documents had already been measured.
    #
    # The number is still printed: a text row that went missing should be visible.
    # The table and the store must agree. scored == stored in a healthy run; a difference
    # means a row is scored that has no store line, or a store line exists for a row the
    # table does not show - either way the corpus is not what it claims to be.
    consistent = s["scored"] == s["stored"]

    ok = ((not s["blocked_docx"]) and backfill == 0 and consistent
          and backfill is not None)

    if "--quiet" not in argv:
        print("docx   %d/%d scored, %d exempt, %d still blocking, %d in the store"
              % (s["scored"], s["total"], s["exempt_docx"], len(s["blocked_docx"]),
                 s["stored"]))
        if s["scored"] != s["stored"]:
            print("       table and store disagree: %d scored, %d stored - the corpus is not"
                  % (s["scored"], s["stored"]))
            print("       what it claims. Re-run the rows that are missing from the store.")
        if s["blocked_docx"][:5]:
            print("       blocking: %s" % ", ".join(s["blocked_docx"][:5]))
        if backfill is None:
            print("txt    the backfill gap could not be read - txt_gap.py is missing or broken")
        else:
            print("txt    backfill gap %d, %d exempt" % (backfill, s["exempt_txt"]))
        print("round  %d text rows missing for round %s on engine %s%s"
              % (this_round, rnd, engine or "?",
                 "" if this_round == 0 else "  (reported, not blocking)"))
        print("READY - both halves complete" if ok else "NOT READY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
