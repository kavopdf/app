#!/usr/bin/env python3
"""Which class this run works on. Rotation, by how many documents each one costs.

    python3 tools/p2w-bench/classpick.py            # the class to take, and why
    python3 tools/p2w-bench/classpick.py --json     # the same, machine-readable
    python3 tools/p2w-bench/classpick.py --status   # where the rotation stands

THE RULE, in the user's words (20 Nov):

    "ek class me jab tak improvement ho raha hai tab tak kaam hota rahe agar kisi class me poore ek
     run me multiple attempt try karne ke baad bhi ek bhi documents improvement nhi ho raha hai toh
     next turn me dusre sabse jyada documents wale class par kaam ho aur yeh silsila rotation based
     chalna chahiye"

So: ranked by documents, biggest first. Stay on a class while it is producing movement. When a whole
run of attempts on it produced nothing, move to the next class in the ranking. When the ranking runs
out, wrap round and start again - a class that failed once is not a class that failed for ever, and the
engine will have changed by the time it comes round.

WHY NOT ALWAYS THE EASIEST. The handoff on 20 Nov said take 25_invisible_text because its LibreOffice
tail is one document and the gate therefore cannot refuse it. That is a good first pick and a bad
policy: if every run takes the easiest class, the hard ones are never touched and the corpus never
finishes. The rotation starts at the biggest and moves on when a class stalls, which reaches the easy
ones early anyway - 25_invisible_text is the seventh biggest - without ever abandoning the hard ones.

WHERE THE EVIDENCE COMES FROM. benchmarks/DEFECT-CLASSES-GOOGLE.md for the ranking (Google's counts,
because Google is the renderer the user opens), and ATTEMPTS.json for what has actually been tried -
`moved` is how many documents an attempt improved, and it is the only honest measure of progress.
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IST = timezone(timedelta(hours=5, minutes=30))

CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES-GOOGLE.md")
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")
ROTATION = os.path.join(HERE, "ROTATION.json")

MIN_ATTEMPTS_FOR_A_VERDICT = 2


def now_str():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M")


def load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def save(path, obj):
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, path)


def ranking():
    """[(class, google_docs)] biggest first, from the capability table."""
    out = []
    if not os.path.exists(CLASSES):
        return out
    for line in open(CLASSES, encoding="utf-8"):
        if not line.startswith("| `"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 6:
            continue
        name = c[0].strip("` ")
        try:
            out.append((name, int(c[5])))
        except ValueError:
            continue
    return sorted(out, key=lambda x: -x[1])


def attempts_for(cls, since=None):
    """The attempts recorded on a class, optionally only those at or after `since`."""
    d = load(ATTEMPTS, {})
    rec = d.get(cls) or {}
    h = rec.get("history") or []
    if since:
        h = [x for x in h if (x.get("at") or "") >= since]
    return h


def moved_of(history):
    return sum(int(x.get("moved") or 0) for x in history)


def exhausted():
    """Classes a run has already given up on, with the reason it wrote down.

    THE TWO LEDGERS DO NOT SHARE A NAMESPACE, and that cost the rotation its whole memory. ATTEMPTS.json
    is keyed by the classifier's class names - `content-present-partly-displaced` - while the capability
    table is keyed by the check names Google reports - `32_stroke_lines`. Eighteen attempts sit under the
    first and the rotation cannot see a single one under the second, so it would have started at
    `32_stroke_lines` and spent a nineteenth run on the same wall.

    So a run records the class it exhausted here, in the table's own namespace, with the reason. It is
    evidence, not a rule: nothing is hard-coded, and the entry is written by the run that proved it.
    A class listed here is skipped by the rotation and reached again only after a full cycle - the engine
    will have changed by then.
    """
    rot = load(ROTATION, {})
    return rot.get("exhausted") or {}


def decide():
    """Return (class, why, rotation_state). Pure function of the files on disk."""
    rank = ranking()
    if not rank:
        return None, "benchmarks/DEFECT-CLASSES-GOOGLE.md names no classes", {}
    names = [n for n, _ in rank]
    docs = dict(rank)
    rot = load(ROTATION, {})
    cur = rot.get("class")
    since = rot.get("since")

    dead = exhausted()

    if cur not in names:
        cur = next((n for n in names if n not in dead), names[0])
        since = now_str()
        return cur, ("starting the rotation at the biggest class: %s, %d documents"
                     % (cur, docs[cur])), {"class": cur, "since": since}

    h = attempts_for(cur, since)
    moved = moved_of(h)
    n = len(h)

    if n >= MIN_ATTEMPTS_FOR_A_VERDICT and moved == 0:
        i = names.index(cur)
        nxt = cur
        for step in range(1, len(names) + 1):
            cand = names[(i + step) % len(names)]
            if cand not in dead:
                nxt = cand
                break
        return nxt, ("%s had %d attempt(s) since %s and moved 0 documents - rotating to the next "
                     "biggest: %s, %d documents" % (cur, n, since, nxt, docs[nxt])), \
               {"class": nxt, "since": now_str()}

    if n == 0:
        return cur, ("staying on %s (%d documents): no attempt recorded on it since %s yet"
                     % (cur, docs[cur], since)), rot

    return cur, ("staying on %s (%d documents): %d attempt(s) since %s moved %d document(s) - "
                 "it is still producing, so it keeps the slot"
                 % (cur, docs[cur], n, since, moved)), rot


def main(argv):
    cls, why, state = decide()
    if "--exhaust" in argv:
        # the run records the class it gave up on, and why. Never silently.
        i = argv.index("--exhaust") + 1
        if i >= len(argv):
            print("--exhaust needs a class name", file=sys.stderr)
            return 2
        name = argv[i].strip()
        why = " ".join(argv[i + 1:]).strip() or "no reason recorded"
        rot = load(ROTATION, {})
        dead = rot.get("exhausted") or {}
        dead[name] = "%s - %s" % (now_str(), why)
        rot["exhausted"] = dead
        save(ROTATION, rot)
        print("recorded as exhausted: %s" % name)
        print("  reason: %s" % why)
        return 0
    if "--status" in argv:
        rot = load(ROTATION, {})
        rank = ranking()
        print("rotation")
        print("  current : %s" % (rot.get("class") or "-"))
        print("  since   : %s" % (rot.get("since") or "-"))
        print("  ranking :")
        dead = rot.get("exhausted") or {}
        if dead:
            print("  exhausted:")
            for k, v in dead.items():
                print("    %s  (%s)" % (k, v))
            print("  ranking :")
        for i, (n, c) in enumerate(rank[:12]):
            mark = "  <- now" if n == rot.get("class") else ("  [exhausted]" if n in dead else "")
            h = attempts_for(n)
            print("    %2d. %-30s %4d docs  %2d attempt(s), moved %d%s"
                  % (i + 1, n, c, len(h), moved_of(h), mark))
        return 0
    if "--json" in argv:
        print(json.dumps({"class": cls, "why": why, "state": state}, indent=1))
        return 0
    if cls is None:
        print("refused: %s" % why, file=sys.stderr)
        return 3
    # THE EXHAUSTED MAP MUST SURVIVE THE POINTER WRITE. This wrote `state` alone, so every call that
    # moved the rotation silently erased the record of which classes were exhausted - and the very next
    # call put the rotation straight back on 32_stroke_lines, the class 18 attempts had already failed on.
    # Found by watching it happen: after marking two classes dead it still picked the first.
    merged = dict(load(ROTATION, {}))
    merged.update(state)
    merged["exhausted"] = (load(ROTATION, {}).get("exhausted")
                           or state.get("exhausted") or {})
    save(ROTATION, merged)
    print("class   : %s" % cls)
    print("why     : %s" % why)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
