#!/usr/bin/env python3
"""
classify.py - group failures into classes FROM THE DATA, and keep a ledger of attempts.

WHY THIS EXISTS
  The fixer's first question every run is "what do I fix next". It used to answer
  by counting documents per check, which is the right instinct and the wrong
  number: twenty documents failing one check may be one missing feature, twenty
  failing another may be twenty separate causes.

WHY THE CLASSES ARE NOT HAND-WRITTEN
  The first version of this file grouped checks with a hard-coded map - borders
  together, fonts together, and so on. That is a guess about the data written
  before looking at it, and it fails in the way that matters: a genuinely
  different defect that happens to live in the same area gets merged into a class
  it does not belong to, and the fixer then hunts one cause for two unrelated
  faults and fails at both.

  So classes are derived from what actually co-occurs. For every pair of checks,
  compare the SET of documents that fail each. If two checks almost always fail
  on the same documents they are almost certainly one cause; if they fail on
  disjoint sets they are certainly not. Checks are merged by connected components
  at a Jaccard threshold, so a check that fails on its own stays on its own.

  Nothing here is hand-written any more, not even the names. A class is called
  after the check that touches the most documents - "19_worst_dy (+3)" - and
  nothing else. Every human label is an interpretation written before the data was
  seen, and a wrong one sends the fixer after the wrong cause: an earlier version
  labelled a cluster "vertical drift" and a fixer told to fix vertical drift would
  have chased four different faults at once. The fixer reads the check ids and
  works out the cause itself, which is the only place that judgement belongs.

WHY THERE IS A LEDGER
  A fixer without a clock loops. It picks the top class, fails, picks the top
  class, fails, and a week later the same class is still on top and nothing else
  has been touched. Every attempt is recorded here with a first-seen time and a
  count. A class gets ONE FULL DAY - MAX_HOURS - and at most MAX_ATTEMPTS tries
  inside it; when either limit is reached it is PARKED, skipped by the fixer, and
  kept in the file with its reason so the record survives and the work moves on.

USAGE
  python3 tools/p2w-bench/classify.py [--top N]
  python3 tools/p2w-bench/classify.py --attempt <class> --outcome kept|reverted|error
"""
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "ATTEMPTS.json")

MAX_HOURS = 24        # one full day per class - the hard limit
MAX_ATTEMPTS = 24     # 24 tries inside that day - one per hourly slot. A run takes twelve
                      # to twenty-five minutes and releases its slot, so the gaps between them
                      # were idle: twelve tries in twenty-four hours left the machine working
                      # about a fifth of the day. The day is the limit; the number of tries
                      # inside it follows the schedule. The platform will not fire a cron more
                      # often than hourly, so 24 is the most a day can hold.
MAX_REQUEUES = 3      # a class that keeps improving gets three fresh days, then stops
JACCARD = 0.55        # how alike two checks must be to count as one cause
UNIVERSAL = 0.90      # a check failing on this share of documents cannot discriminate
MAX_CLASS_CHECKS = 6  # a class bigger than this names no single cause

# The suffix carries digits: 20_within_10pt and 43_within_10pt_x are real checks, and
# [a-z_]+ dropped both on the floor. 20_within_10pt fails on 91% of the corpus - the
# second largest defect there is - and the classifier never saw it, so it never became
# a class and the fixer was never pointed at it.
CHECK_RE = re.compile(r"^(?:\d{2}[a-c]?|t\d{2})_[a-z0-9_]+$")


RESULTS_TXT = os.path.join(HERE, "RESULTS-TXT.jsonl")


def read_txt_results():
    """The .txt rows, in the same shape read_baseline returns, latest row per document.

    The .docx path reads a table a human also reads; the .txt path has no such table and
    does not need one, so the store is read directly rather than kept in step by hand.
    """
    rows = []
    if not os.path.exists(RESULTS_TXT):
        return rows
    latest = {}
    for line in open(RESULTS_TXT, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        doc = e.get("doc")
        if not doc:
            continue
        key = (e.get("round", 0), e.get("engine", ""))
        if doc not in latest or key >= latest[doc][0]:
            latest[doc] = (key, e)
    for doc, (_k, e) in sorted(latest.items()):
        rows.append({
            "doc": doc,
            "score": "%s/%s" % (e.get("score") or 0, e.get("total") or 0),
            "failed": ", ".join(e.get("failed") or []),
        })
    return rows


def _rows_for_mode():
    """The rows classify works on. The .txt half has no hand-written table to read, so
    under --txt the store is the truth; otherwise it is BASELINE.md as before."""
    if "--txt" in sys.argv:
        return read_txt_results()
    return read_baseline(os.path.join(HERE, "BASELINE.md"))


def read_baseline(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "document":
            continue
        rows.append({
            "doc": cells[0],
            "score": cells[1] if len(cells) > 1 else "",
            "failed": cells[3] if len(cells) > 3 else "",
        })
    return rows


def load_ledger():
    if os.path.exists(LEDGER):
        try:
            return json.load(open(LEDGER, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_ledger(led):
    json.dump(led, open(LEDGER, "w", encoding="utf-8"), indent=2, sort_keys=True)


def split_oversized(groups, doc_sets, unsplittable=None):
    """A class of seventeen checks names no single cause.

    When most documents fail most checks, everything co-occurs and the threshold
    merges the corpus into one unactionable blob. So any group too large to name
    a cause is re-clustered on its own at a stricter threshold, repeatedly, until
    the parts are small enough to be worth attacking one at a time.

    A threshold cannot separate checks that fail on exactly the same documents, and
    that case used to leave an oversized class in place without a word - the invariant
    this function exists to keep, quietly broken. It is not a bad split when it
    happens: identical document sets mean one cause with several symptoms, which is
    one engine change, not several. So the class stays whole and the caller is told,
    because a class of eight that could not be split for a reason is a different
    thing from a class of eight nobody looked at.
    """
    out = []
    for g in groups:
        if len(g) <= MAX_CLASS_CHECKS:
            out.append(g)
            continue
        threshold = JACCARD
        parts = [g]
        while threshold < 0.95:
            threshold = min(0.95, threshold + 0.10)
            parts = cluster({c: doc_sets[c] for c in g}, threshold)
            if max(len(p) for p in parts) <= MAX_CLASS_CHECKS:
                break
        if unsplittable is not None and max(len(p) for p in parts) > MAX_CLASS_CHECKS:
            unsplittable.append(len(g))
        out.extend(parts)
    return out


def build_groups(doc_sets, measured_count, unsplittable=None):
    """The one grouping both classify and subclusters use."""
    total = measured_count or 1
    universal = {c for c, ds in doc_sets.items()
                 if len(ds) >= max(10, UNIVERSAL * total)}
    groups = []
    rest = {c: ds for c, ds in doc_sets.items() if c not in universal}
    if rest:
        groups.extend(split_oversized(cluster(rest), doc_sets, unsplittable))
    groups.extend([[c] for c in sorted(universal)])
    return groups


def cluster(doc_sets, threshold=None):
    """Union checks that fail on largely the same documents. Data decides."""
    names = list(doc_sets)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    t = JACCARD if threshold is None else threshold
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, sb = doc_sets[a], doc_sets[b]
            if not sa or not sb:
                continue
            j = len(sa & sb) / len(sa | sb)
            if j >= t:
                union(a, b)

    groups = defaultdict(list)
    for n in names:
        groups[find(n)].append(n)
    return list(groups.values())


def subclusters(cls_name, top=8):
    """Split one class into the sub-causes hiding inside it.

    A class of 126 documents is rarely one cause. If forty of them also fail
    22_reading_order and fifty also fail 32_stroke_lines, the class is two or
    three defects wearing one name, and a fixer that treats it as one will fix
    the largest group and then report the rest as hard.

    Documents are grouped by the check they fail most often across the class,
    excluding the class's own checks. The biggest group is the one worth
    attacking first.
    """
    rows = [r for r in _rows_for_mode()
            if re.match(r"\d+\s*/\s*\d+", r["score"])]
    docs = {}
    for r in rows:
        failed = {c.strip() for c in r["failed"].split(",") if CHECK_RE.match(c.strip())}
        if failed:
            docs[r["doc"]] = failed

    doc_sets = {c: {d for d, f in docs.items() if c in f}
                for c in {x for f in docs.values() for x in f}}
    classes = build_groups(doc_sets, len(docs))
    target = None
    for group in classes:
        group = sorted(group, key=lambda c: -sum(1 for f in docs.values() if c in f))
        name = group[0] if len(group) == 1 else "%s (+%d)" % (group[0], len(group) - 1)
        if name == cls_name or group[0] == cls_name or cls_name in name:
            target = group
            break
    if target is None:
        print("no class matching %r - run classify.py first, then copy the exact name"
              % cls_name)
        return 1

    own = set(target)
    members = [d for d, f in docs.items() if f & own]
    if not members:
        print("class %r has no documents" % cls_name)
        return 1

    # A universal check co-fails with everything, so grouping on it would put the
    # whole class in one bucket and say nothing. It is excluded from the grouping
    # signal for the same reason it is excluded from the merge graph.
    total = len(docs) or 1
    universal = {c for c, ds in
                 {x: {d for d, f in docs.items() if x in f}
                  for x in {y for f in docs.values() for y in f}}.items()
                 if len(ds) >= max(10, UNIVERSAL * total)}

    # how often each outside check appears among this class's documents
    freq = Counter()
    for d in members:
        for c in (docs[d] - own) - universal:
            freq[c] += 1
    if not freq:
        print("class %r: %d documents, no discriminating outside check" % (cls_name, len(members)))
        print("every document fails the same set, so the class is one cause and the")
        print("whole class moves together - or nothing in the data separates them yet.")
        return 0

    groups = defaultdict(list)
    for d in members:
        extras = (docs[d] - own) - universal
        best = max(extras, key=lambda c: (freq[c], c)) if extras else None
        groups[best or "(only the class checks)"].append(d)

    print("class %r - %d documents, %d outside checks" % (cls_name, len(members), len(freq)))
    print("")
    for label, ds in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:top]:
        print("  %3d docs  with %s" % (len(ds), label))
        print("            e.g. %s" % ", ".join(sorted(ds)[:3]))
    if len(groups) > top:
        print("  ... and %d smaller groups" % (len(groups) - top))
    print("")
    print("Start with the largest group. Fixing it moves that many documents;")
    print("the rest are a different cause and need their own calibration.")
    return 0


try:
    from trace import note
except Exception:
    def note(*a, **k):
        pass

def current_class_names():
    """The class names exactly as main() writes them - the only valid ledger keys."""
    base = _rows_for_mode()
    docs = {}
    for r in base:
        failed = {c.strip() for c in (r.get("failed") or "").split(",")
                  if CHECK_RE.match(c.strip())}
        if failed:
            docs[r["doc"]] = failed
    if not docs:
        return []
    doc_sets = {c: {d for d, f in docs.items() if c in f}
                for c in {x for f in docs.values() for x in f}}
    names = []
    for g in build_groups(doc_sets, len(docs)):
        g = sorted(g, key=lambda c: -len(doc_sets[c]))
        names.append(g[0] if len(g) == 1 else "%s (+%d)" % (g[0], len(g) - 1))
    return names


def compute_moved(cls_name, new_engine=None):
    """How many documents the class actually moved, read from the store.

    Returns (moved, failing_before, verified). verified is False when the store holds
    only one engine, which means nothing was measured against a changed engine and no
    document can have moved.

    "Moved" is the brief's definition: at least one of the class's checks was failing
    on this document before, and none of them fails now. A document that was already
    passing every one of them is not counted either way - it proves nothing about this
    fix.
    """
    # BASELINE.md carries no engine column - read_baseline returns doc, score and the
    # failed set only - so the before/after comparison has to come from the store.
    store = os.path.join(HERE, "RESULTS-TXT.jsonl" if "--txt" in sys.argv else "RESULTS.jsonl")
    if not os.path.exists(store):
        return 0, 0, False
    # doc -> {engine: failed set}, in the order the file lists the engines
    per_doc = {}
    engines = []
    for line in open(store, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        eng = r.get("engine")
        if eng is None:
            continue
        if eng not in engines:
            engines.append(eng)
        raw = r.get("failed") or []
        if isinstance(raw, str):
            raw = raw.split(",")
        failed = {c.strip() for c in raw if CHECK_RE.match(str(c).strip())}
        per_doc.setdefault(r.get("doc"), {})[eng] = failed

    if len(engines) < 2:
        return 0, 0, False

    # "Before" is the last COMMITTED engine, not the one before this attempt.
    #
    # Two attempts are independent experiments: each one starts from the committed engine,
    # tries a change, and is reverted if it does not work. So the question is never "did
    # this beat the previous attempt" - it is "did this beat what ships". Comparing the last
    # two engines instead was wrong twice over: it compared an attempt against another
    # attempt, and when two attempts shared an engine id (which the bare "-dirty" suffix
    # made possible) it compared the baseline against a mixture of both.
    #
    # A dirty id is "<hash>-d<six hex of the diff>"; a committed one is the bare hash. So
    # the last id without a "-d" suffix is the baseline, and the last id overall is this
    # attempt.
    # WHICH ENGINE IS "THIS ATTEMPT"?
    #
    # Not engines[-1]. record.py writes the store sorted by (round, doc), so the engine on the
    # last line is whatever engine that document was last measured under - not the most recent
    # attempt. On 13 Nov the store's tail read
    #     ['2a68de6-dirty', '2a68de6-d80a524', '2a68de6-d5215cb', '2a68de6-df33807']
    # so engines[-1] was df33807 from the 07:00 run while the 08:40 run had measured under
    # d5215cb. The tool compared the baseline against the wrong attempt and answered "0 of 5"
    # for a round that had really moved 3 of 10 - and refused the run's honest numbers.
    if new_engine:
        if new_engine not in engines:
            return 0, 0, False
        new_eng = new_engine
    else:
        new_eng = engines[-1]
    clean = [e for e in engines if e != new_eng and "-d" not in e]
    old_eng = clean[-1] if clean else engines[-2]

    # THE CLASS IS RESOLVED FROM THE "BEFORE" ENGINE, NOT FROM BASELINE.md.
    #
    # This used to call _rows_for_mode(), which reads BASELINE.md - the state AFTER the
    # attempt's own rows are in it. A document that moved now passes the class's checks, so
    # it is no longer in the class, so the group rebuilt from the post-attempt state is a
    # different group with a different check set. The comparison then asked "did the
    # documents that are STILL failing move", which is a different question from "did the
    # documents that were failing move", and the answer it gives is always too small.
    #
    # On 13 Nov that cost a real number: a run measured 3 of 10 documents moved onto a pass
    # of 20_within_10pt (304 12->100, 34_monospace 14->100, 334_patent 16->100). The tool
    # answered 0 of 5 and refused the claim. The run recorded the tool's numbers because the
    # ratchet's FAIL decided the outcome anyway - so the store now says "0 of 5" where the
    # truth is "3 of 10", and INCIDENTS.md carries the correction instead of the data.
    docs = {}
    for doc, by_eng in per_doc.items():
        failed = by_eng.get(old_eng)
        if failed:
            docs[doc] = failed
    if not docs:
        return 0, 0, False
    doc_sets = {c: {d for d, f in docs.items() if c in f}
                for c in {x for f in docs.values() for x in f}}
    target = None
    for g in build_groups(doc_sets, len(docs)):
        g = sorted(g, key=lambda c: -len(doc_sets[c]))
        name = g[0] if len(g) == 1 else "%s (+%d)" % (g[0], len(g) - 1)
        if name == cls_name:
            target = set(g)
            break
    if target is None:
        return 0, 0, False

    moved = failing = 0
    for doc, by_eng in per_doc.items():
        if old_eng not in by_eng or new_eng not in by_eng:
            continue
        before = by_eng[old_eng] & target
        after = by_eng[new_eng] & target
        if not before:
            continue
        failing += 1
        if not after:
            moved += 1
    return moved, failing, True


def main(argv):
    if "--subclusters" in argv:
        return subclusters(argv[argv.index("--subclusters") + 1])

    # ---- attempt recording mode -------------------------------------------
    if "--attempt" in argv:
        cls = argv[argv.index("--attempt") + 1]
        claimed = argv[argv.index("--outcome") + 1] if "--outcome" in argv else None

        # The class name is the ledger KEY. An unvalidated one creates an entry for a
        # class that does not exist: the attempt is recorded against nothing, the real
        # class never sees it and keeps its own attempt count at zero until it is
        # parked for not converging, and the ledger fills with names nobody can match.
        # Tested before this guard: --attempt "koi bhi bakwas naam" was accepted and
        # marked FIXED.
        known = current_class_names()
        if cls not in known:
            print("refused: %r is not a class. The ledger is keyed by the exact name," % cls)
            print("so recording under a name that is not in DEFECT-CLASSES.md writes the")
            print("attempt against nothing and leaves the real class at zero attempts.")
            near = [k for k in known if cls.split(" (")[0] in k or k.split(" (")[0] in cls]
            if near:
                print("Did you mean:")
                for k in near[:5]:
                    print("    %s" % k)
            else:
                print("Run classify.py and copy a name from the table exactly.")
            return 1

        # The outcome is computed from the numbers, not chosen by the run.
        # "kept" and "improved" were two words a fixer could pick between, and the
        # difference between them is the difference between an honest report and a
        # flattering one. Numbers cannot be talked into a better answer.
        def num(flag):
            if flag not in argv:
                return None
            try:
                return int(argv[argv.index(flag) + 1].split("/")[0])
            except (ValueError, IndexError):
                return None

        moved = num("--moved")
        total = num("--total")

        # A number bigger than its own denominator is not a strong claim, it is a typo
        # or a lie, and either way it used to be accepted: --moved 999 --total 20
        # printed "moved 999 of 20 (4995%) -> kept" and marked the class FIXED, which
        # removes it from the pipeline permanently. Nothing is easier to check than this.
        if moved is not None and total is not None:
            if moved < 0:
                print("refused: --moved %d is negative - a count of documents cannot be" % moved)
                return 1
            if total > 0 and moved > total:
                print("refused: --moved %d of --total %d. More documents moved than were" % (moved, total))
                print("measured. That is a typo or an invented number, and either one marks the")
                print("class FIXED on evidence that does not exist.")
                return 1

        if moved is None or total is None or total <= 0:
            if claimed in ("kept", "improved"):
                print("refused: '%s' needs numbers. Pass --moved <n> --total <n> so the" % claimed)
                print("outcome is computed rather than asserted. A run that cannot say how")
                print("many documents moved has not measured anything.")
                return 1
            outcome = claimed or "error"
        else:
            # The claim is checked against the store, not taken on trust. The comment
            # above says numbers cannot be talked into a better answer - that is only
            # true if the numbers are not supplied by the run that wants them. Tested
            # before this: --moved 10 --total 20 marked a class FIXED without a single
            # document having moved, and FIXED is permanent.
            eng = argv[argv.index("--engine") + 1] if "--engine" in argv else None
            actual, failing, verified = compute_moved(cls, eng)
            if not verified:
                print("refused: the store holds only one engine, so nothing was measured")
                print("against a changed engine and no document can have moved. Check that")
                print("ENGINE carries the -dirty suffix when the engine folder is modified.")
                return 1
            if actual != moved:
                print("refused: you said %d of %d moved; the store says %d of %d."
                      % (moved, total, actual, failing))
                print("The store compares the last two engines row by row. Record what")
                print("happened: --moved %d --total %d" % (actual, failing))
                return 1
            ratio = float(moved) / float(total)
            if ratio >= 0.5:
                outcome = "kept"
            elif ratio >= 1.0 / 3.0:
                outcome = "improved"
            else:
                outcome = "reverted"
            if claimed and claimed != outcome:
                print("refused: you said '%s' but %d of %d documents moved, which is '%s'."
                      % (claimed, moved, total, outcome))
                print("Record what happened, not what you hoped. Re-run without --outcome")
                print("to record the computed result.")
                return 1
            print("moved %d of %d (%.0f%%) -> %s" % (moved, total, ratio * 100, outcome))

        led = load_ledger()
        e = led.setdefault(cls, {"first_seen": time.time(), "attempts": 0,
                                 "last": 0, "outcomes": [], "requeues": 0})
        e.setdefault("requeues", 0)
        e["attempts"] += 1
        e["last"] = time.time()
        e["outcomes"].append(outcome)

        if outcome == "kept":
            e["status"] = "FIXED"
            e["reason"] = "fix kept and proven"

        elif outcome == "improved":
            # The class moved but did not pass. It is not stuck, it is working, so
            # it gets a fresh day rather than being parked on the clock. Bounded by
            # MAX_REQUEUES: a class that improves a little every day forever is not
            # converging, and pretending otherwise is how a fixer loops slowly
            # instead of quickly.
            e["requeues"] += 1
            if e["requeues"] > MAX_REQUEUES:
                e["status"] = "PARKED"
                e["reason"] = ("improved on %d separate days without converging (limit %d)"
                               % (e["requeues"], MAX_REQUEUES))
            else:
                e["first_seen"] = time.time()   # the day restarts
                e["attempts"] = 0
                e["status"] = "OPEN"
                e["reason"] = "improved - day restarted (requeue %d of %d)" % (
                    e["requeues"], MAX_REQUEUES)

        else:  # reverted or error - real progress was not made
            if e["attempts"] >= MAX_ATTEMPTS:
                e["status"] = "PARKED"
                e["reason"] = "%d attempts without progress (limit %d)" % (
                    e["attempts"], MAX_ATTEMPTS)
            else:
                e["status"] = "OPEN"
                e["reason"] = ""

        save_ledger(led)
        # The trajectory, one line per attempt.
        #
        # DEFECT-CLASSES.md is rewritten every run, so it cannot answer "what was this class six
        # hours ago" or "has it been getting better". That history is the most useful thing the
        # next run could have and the one thing nothing kept. Seven fields, one line, appended -
        # small enough that nobody has to be told not to read it whole.
        try:
            import time as _t
            stamp = _t.strftime("%Y-%m-%d %H:%M", _t.gmtime(_t.time() + 5 * 3600 + 30 * 60))
            rnd = None
            try:
                rnd = json.load(open(os.path.join(HERE, "ROUND.json"),
                                     encoding="utf-8")).get("round")
            except Exception:
                pass
            with open(os.path.join(HERE, "CLASS-HISTORY.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "at": stamp, "round": rnd, "class": cls,
                    "attempt": e["attempts"], "outcome": outcome,
                    "status": e.get("status"), "requeues": e.get("requeues", 0),
                }, sort_keys=True) + "\n")
        except Exception as exc:
            # Not swallowed. A history file that silently stops being written is the exact
            # defect this whole session is about - the first version of this block called
            # load(), which does not exist here, and except-pass hid it so well that the file
            # was created empty and nothing said why.
            print("warning: CLASS-HISTORY.jsonl not written - %s: %s"
                  % (type(exc).__name__, exc))
        note("attempt", "%s -> %s (%s)" % (cls, outcome, e.get("status")))
        print("%s: attempts=%d requeues=%d status=%s  %s" % (
            cls, e["attempts"], e["requeues"], e.get("status"), e.get("reason", "")))
        return 0

    top = 20
    if "--top" in argv:
        top = int(argv[argv.index("--top") + 1])

    base = _rows_for_mode()
    measured = [r for r in base if re.match(r"\d+\s*/\s*\d+", r["score"])]

    doc_sets = defaultdict(set)
    prose = Counter()
    for r in measured:
        for c in [x.strip() for x in r["failed"].split(",") if x.strip()]:
            if CHECK_RE.match(c):
                doc_sets[c].add(r["doc"])
            else:
                prose[c] += 1

    # A check that fails on almost every document carries no information about
    # WHICH sub-cause a document has - it is a systematic defect. Its Jaccard
    # against every other universal check is near 1.0, so merging on it produced
    # a class of 21 checks covering all 20 documents, which no fixer can act on.
    # Universal checks become their own classes; the rest cluster among themselves.
    unsplittable = []
    groups = build_groups(doc_sets, len(measured), unsplittable) if doc_sets else []
    led = load_ledger()
    now = time.time()

    classes = []
    for g in groups:
        g = sorted(g, key=lambda c: -len(doc_sets[c]))
        docs = set()
        for c in g:
            docs |= doc_sets[c]
        # The class is named after the check that touches the most documents,
        # and nothing else. Any human label would be an interpretation written
        # before the data was seen, and a wrong label sends the fixer after the
        # wrong cause - which is exactly what a hard-coded map did. The fixer
        # reads the check ids and works out the cause itself.
        name = g[0] if len(g) == 1 else "%s (+%d)" % (g[0], len(g) - 1)
        entry = led.get(name, {})
        attempts = entry.get("attempts", 0)
        requeues = entry.get("requeues", 0)
        status = entry.get("status", "OPEN")
        hours_open = round((now - entry["first_seen"]) / 3600, 1) if entry else 0
        reason = entry.get("reason", "")
        if entry and status == "OPEN":
            if hours_open >= MAX_HOURS:
                status = "PARKED"
                reason = "%s hours open without a kept fix (limit %s)" % (hours_open, MAX_HOURS)
            elif attempts >= MAX_ATTEMPTS:
                status = "PARKED"
                reason = "%s attempts without a kept fix (limit %s)" % (attempts, MAX_ATTEMPTS)
        classes.append({
            "name": name, "checks": g, "docs": docs,
            "attempts": attempts, "requeues": requeues, "status": status,
            "hours": hours_open, "reason": reason,
        })

    # Two unrelated clusters can land on the same label. Disambiguate rather than
    # let the ledger record two different defects under one name.
    seen = Counter()
    for c in classes:
        seen[c["name"]] += 1
    dupes = {k for k, v in seen.items() if v > 1}
    for c in classes:
        if c["name"] in dupes:
            c["name"] = "%s [%s]" % (c["name"], c["checks"][0])

    classes.sort(key=lambda c: (c["status"] == "PARKED", -len(c["docs"])))

    total = max(1, len(measured))
    out = ["# Defect classes\n",
           "Generated by `classify.py` from BASELINE.md.\n",
           "Classes are derived from the data, not from a hand-written map: two checks are put in",
           "the same class only when they fail on largely the same documents (Jaccard >= %.2f)." % JACCARD,
           "A check that fails on its own stays on its own, so a genuinely different defect cannot",
           "be swallowed by a class it does not belong to.\n",
           "Documents measured: **%d of %d**\n" % (len(measured), len(base)),
           "Limits: one full day (%d hours) per class, %d attempts inside it, and a class that"
           % (MAX_HOURS, MAX_ATTEMPTS),
           "improves but does not pass gets its day restarted - up to %d times, after which it is"
           % MAX_REQUEUES,
           "parked as not converging. A parked class is skipped by the fixer and kept here with its reason.\n",
           "| # | class | documents | share | checks in class | attempts | requeues | status |",
           "|---|---|---|---|---|---|---|---|"]
    # EVERY class goes in the file, not the first twenty. The classifier computes 43 on
    # this corpus and the file listed 20, so once the top twenty were FIXED or PARKED the
    # fixer would find no class to pick while twenty-three were still OPEN - and a fixer
    # with nothing to pick closes the round. --top still limits the console summary, which
    # is what it was for.
    for i, c in enumerate(classes, 1):
        out.append("| %d | %s | %d | %d%% | %s | %d | %d | %s |" % (
            i, c["name"], len(c["docs"]), round(100 * len(c["docs"]) / total),
            ", ".join(c["checks"]), c["attempts"], c.get("requeues", 0), c["status"]))

    out.append("\n## Documents per class\n")
    for c in classes:
        # The count is printed, and the list is marked as truncated when it is: the
        # table above says 203 documents and this line used to show four of them with
        # no hint that more existed, so the two halves of the same file disagreed.
        docs = sorted(c["docs"])
        more = "" if len(docs) <= 4 else " (+%d more)" % (len(docs) - 4)
        out.append("- **%s** — %d docs: %s%s" % (
            c["name"], len(docs), ", ".join(docs[:4]) or "none", more))

    parked = [c for c in classes if c["status"] == "PARKED"]
    if parked:
        out.append("\n## Parked\n")
        for c in parked:
            out.append("- **%s** — %s" % (c["name"], c.get("reason") or "limit reached"))

    if prose:
        out.append("\n## Non-check text in the failed column\n")
        out.append("Ignored. It means the column is not clean:\n")
        for k, v in prose.most_common(5):
            out.append("- %s (%d)" % (k[:90], v))


    # The two halves get their own file. Writing both into DEFECT-CLASSES.md meant a
    # classify --txt run replaced the .docx class list with the .txt one, and the fixer
    # reads that file to decide what to attack next.
    name = "DEFECT-CLASSES-TXT.md" if "--txt" in sys.argv else "DEFECT-CLASSES.md"
    open(os.path.join(HERE, name), "w", encoding="utf-8").write("\n".join(out) + "\n")

    note("classify%s" % (" --txt" if "--txt" in argv else ""),
         "%d classes from %d documents" % (len(classes), len(measured)))
    print("documents measured : %d" % len(measured))
    print("checks firing      : %d" % len(doc_sets))
    print("classes (data-driven): %d" % len(classes))
    for _n in unsplittable:
        print("note: a class of %d checks could not be split below %d - its checks fail"
              % (_n, MAX_CLASS_CHECKS))
        print("      on exactly the same documents, so there is nothing to split on.")
        print("      Treat it as one cause with %d symptoms, not %d causes." % (_n, _n))
    for c in classes[:10]:
        print("  %-34s %3d docs  %s" % (c["name"][:34], len(c["docs"]), c["status"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
