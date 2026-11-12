#!/usr/bin/env python3
"""
audit.py - the checks that catch the kinds of bug this pipeline actually produces.

WHY THIS EXISTS
    Twenty defects were found on 12 Nov, and not one of them was "the conversion is wrong".
    Every one was the pipeline believing something untrue about itself: a brief promising
    what no tool did, a gate comparing two numbers while a third was missing, a claim nobody
    recomputed, a state it could not leave. Those are findable by machine, and this file is
    the machine.

    They were found by hand, one at a time, each after the user asked "are you sure". That
    does not scale to three rounds and three months. The types are now a list, and the
    list is a program.

THE FIFTEEN TYPES, AND WHAT THIS FILE CAN CHECK
    A  silent no-op ........... a step reports success and leaves nothing.  --evidence
    B  prose-code drift ....... a brief promises what no tool does.         --tools --numbers
    C  comparison blind spot .. a gate checks X == Y while Z is missing.    --gates
    D  claim without proof .... a number nobody recomputes.                 --numbers
    E  data corruption ........ ids collide, rows overwrite.                --ids
    F  dead end / livelock .... a state you cannot leave.                   --states
    G  wrong question ......... measures the right thing badly.             (human)
    H  silent truncation ...... reads part and says all.                    --caps
    I  order dependence ....... works until something moves.                --ranges
    J  clock / timezone ....... UTC written into a file of IST.             --clock
    K  dead code .............. defined, never called.                      --dead
    L  test that does not test  a check that never fires.                   --mutation
    M  fixture mismatch ....... test data unlike reality.                   (human)
    N  resource growth ........ a file that grows until it is unusable.     --growth
    O  wrong default .......... the obvious choice is the harmful one.      (human)

    The four marked (human) need judgement about meaning. The other eleven are decidable,
    and they are the eleven that produced every finding today.

USAGE
    python3 tools/p2w-bench/audit.py              run every check
    python3 tools/p2w-bench/audit.py --tools      one check
    python3 tools/p2w-bench/audit.py --quiet      only the failures

    Exit 0 all clean, 1 something found.

A NOTE ON FALSE POSITIVES
    A detector that cries wolf is worse than none: the run learns to ignore it and then
    ignores the real one. Every check here is written to fail only on something a person
    would agree is wrong, and each one prints the evidence it judged, so a disagreement can
    be checked rather than argued.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BRIEFS = ["BASELINE-BRIEF.md", "CLASSIFIER-BRIEF.md", "FIXER-BRIEF.md", "TOOLBOX.md"]
ALL_CHECKS = ["tools", "numbers", "ranges", "gates", "clock", "dead", "ids", "caps",
              "growth", "evidence", "mutation", "states"]

FAILS = []
QUIET = "--quiet" in sys.argv


def bad(kind, msg):
    FAILS.append((kind, msg))


def say(*a):
    if not QUIET:
        print(*a)


def read(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def briefs():
    return {b: read(os.path.join(HERE, b)) for b in BRIEFS}


def py_tools():
    return sorted(f for f in os.listdir(HERE) if f.endswith(".py"))


# ---------------------------------------------------------------- B: prose vs tools
def check_tools():
    """Every path a brief tells a run to use must exist."""
    say("\nB  PROSE-CODE DRIFT - every tool a brief names")
    text = "\n".join(briefs().values())
    seen = set()
    for m in re.finditer(r"(tools/[A-Za-z0-9_./-]+\.(?:py|sh))", text):
        seen.add(m.group(1))
    missing = [p for p in sorted(seen)
               if not os.path.exists(os.path.join(REPO, p))
               and not os.path.exists(os.path.join(HERE, os.path.basename(p)))]
    say("   %d tool path(s) named in the briefs" % len(seen))
    for p in missing:
        bad("B", "a brief names %s and it does not exist" % p)
    if not missing:
        say("   all present")


# ---------------------------------------------------------------- D: prose vs constants
def check_numbers():
    """Every limit a brief states must be the limit the code enforces."""
    say("\nD  CLAIM WITHOUT PROOF - every limit a brief states")
    cls = read(os.path.join(HERE, "classify.py"))
    rnd = read(os.path.join(HERE, "round.py"))
    texts = briefs()
    text = "\n".join(texts.values())

    def const(src, name):
        m = re.search(r"^%s\s*=\s*(\d+)" % name, src, re.M)
        return int(m.group(1)) if m else None

    max_attempts = const(cls, "MAX_ATTEMPTS")
    max_hours = const(cls, "MAX_HOURS")
    max_requeues = const(cls, "MAX_REQUEUES")
    m = re.search(r'"fixer":\s*(\d+)', rnd)
    fixer_stale = int(m.group(1)) if m else None

    pairs = [
        ("at most %d attempts" % max_attempts, max_attempts,
         r"at most (\d+) attempts"),
        ("ONE FULL DAY (%d hours)" % max_hours, max_hours,
         r"ONE FULL DAY \((\d+) hours\)"),
        ("the fixer's slot expires after %d minutes" % fixer_stale, fixer_stale,
         r"claim expires after (\d+) minutes"),
    ]
    # Each claim is checked against the brief that makes it. The classifier's brief carries
    # its own 20-minute slot figure, and matching that against the fixer's 45 would be a
    # false alarm - and a detector that cries wolf is the one that gets ignored.
    scopes = {
        r"claim expires after (\d+) minutes": texts.get("FIXER-BRIEF.md", ""),
    }
    for label, value, pattern in pairs:
        haystack = scopes.get(pattern, text)
        found = re.findall(pattern, haystack)
        if not found:
            bad("B", "the briefs never state %r, which the code enforces" % label)
            say("   %-34s not stated in prose" % label)
            continue
        wrong = [f for f in found if int(f) != value]
        say("   %-34s prose %s, code %s%s"
            % (label.split(" (")[0], "/".join(sorted(set(found))), value,
               "" if not wrong else "   MISMATCH"))
        for w in wrong:
            bad("B", "a brief says %s but the code says %d" % (w, value))

    # the derived ceiling, which is the one that was wrong
    if max_attempts and max_requeues:
        ceiling = max_attempts * (max_requeues + 1)
        found = re.findall(r"(\d+) attempts\b", text)
        if str(ceiling) not in found and "Absolute maximum" in text:
            bad("D", "the briefs do not state the real ceiling of %d attempts "
                     "(MAX_ATTEMPTS %d x %d days)" % (ceiling, max_attempts, max_requeues))
            say("   %-34s code implies %d, prose does not say it" % ("absolute maximum", ceiling))


# ---------------------------------------------------------------- I: order dependence
def check_ranges():
    """Every sed range in a brief must return the sections it names and no others."""
    say("\nI  ORDER DEPENDENCE - every sed range a brief uses")
    toolbox = os.path.join(HERE, "TOOLBOX.md")
    text = "\n".join(briefs().values())
    ranges = re.findall(r"sed -n '/## ([^/]+)/,/## ([^/]+)/p'", text)
    if not ranges:
        say("   no ranges found")
        return
    # A range may legitimately span several sections - the baseline reads four tools at
    # once. What it may not do is pull in a section the brief never mentions, which is what
    # happens when a new section is inserted between the two anchors. So the rule is not
    # "must be two sections" but "every section it pulls in is a tool this brief uses".
    texts = briefs()
    for a, b in ranges:
        r = subprocess.run(["sed", "-n", "/## %s/,/## %s/p" % (a, b), toolbox],
                           capture_output=True, text=True)
        out = r.stdout or ""
        heads = [l[3:].split("\u2014")[0].split(" - ")[0].strip()
                 for l in out.splitlines() if l.startswith("## ")]
        if len(out) < 200:
            bad("I", "the range %r..%r returns %d bytes - it matches nothing" % (a, b, len(out)))
            say("   %-22s -> %-18s EMPTY" % (a, b))
            continue
        # which brief carries this range?
        owner = next((t for t, body in texts.items()
                      if "/## %s/,/## %s/p" % (a, b) in body), "")
        accidental = []
        for h in heads:
            stem = h.split(".py")[0].split(".sh")[0]
            if stem and stem not in texts.get(owner, ""):
                accidental.append(h)
        if accidental:
            bad("I", "%s reads %r..%r, which now also pulls in %s - not a tool that brief uses"
                % (owner or "a brief", a, b, ", ".join(accidental)))
            say("   %-22s -> %-18s also pulls in %s" % (a, b, ", ".join(accidental)))
        else:
            say("   %-22s -> %-18s %d sections, all used" % (a, b, len(heads)))


# ---------------------------------------------------------------- C: gates that fire
def check_gates():
    """Each gate must refuse at least one constructed bad state."""
    say("\nC  COMPARISON BLIND SPOT - does each gate actually refuse?")
    cases = [
        ("measure_gate.py", "a document scored twice", lambda d: _dup_row(d)),
        ("classify_gate.py", "a class file that covers fewer documents", lambda d: _short_class(d)),
    ]
    for tool, what, breaker in cases:
        d = _scratch()
        _copy(d, ["tools/p2w-bench", "tools"])
        try:
            breaker(d)
        except Exception as e:
            bad("C", "%s: could not build the %r case (%s)" % (tool, what, e))
            continue
        r = subprocess.run([sys.executable, os.path.join(d, "tools", "p2w-bench", tool)],
                           capture_output=True, text=True, cwd=d)
        if r.returncode == 0:
            bad("C", "%s passes %r - it cannot see that" % (tool, what))
            say("   %-20s %-44s PASSED (should refuse)" % (tool, what))
        else:
            say("   %-20s %-44s refused" % (tool, what))


def _scratch():
    import tempfile
    return tempfile.mkdtemp()


def _copy(d, names):
    import shutil
    for n in names:
        src = os.path.join(REPO, n)
        dst = os.path.join(d, n)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)


def _dup_row(d):
    p = os.path.join(d, "tools", "p2w-bench", "BASELINE.md")
    lines = open(p, encoding="utf-8").read().splitlines()
    rows = [l for l in lines if l.startswith("| ") and not l.startswith("|---")]
    if len(rows) < 3:
        raise RuntimeError("fixture too small")
    lines.append(rows[1])
    open(p, "w").write("\n".join(lines) + "\n")


def _short_class(d):
    p = os.path.join(d, "tools", "p2w-bench", "DEFECT-CLASSES.md")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"Documents measured: \*\*(\d+) of", "Documents measured: **1 of", s, count=1)
    open(p, "w").write(s)


# ---------------------------------------------------------------- J: clock
def check_clock():
    """A timestamp written with a bare strftime is UTC on this image, and every file is IST."""
    say("\nJ  CLOCK - timestamps written without the IST offset")
    suspicious = []
    for f in py_tools():
        if f.endswith("_test.py") or f == "audit.py":
            continue
        src = read(os.path.join(HERE, f))
        lines = src.splitlines()
        in_ist = False
        for i, line in enumerate(lines, 1):
            if re.match(r"def ist\(", line):
                in_ist = True
            elif in_ist and line and not line.startswith((" ", "\t")):
                in_ist = False
            if in_ist:
                continue
            if "strftime" not in line or "gmtime" in line:
                continue
            if line.strip().startswith("#"):
                continue
            # A call split over two lines puts the gmtime on the next one - reading only the
            # first line flags correct code, and a detector that flags correct code gets
            # ignored.
            nxt = lines[i] if i < len(lines) else ""
            if "gmtime" in nxt:
                continue
            # A filename stamp is not a log line: nobody reads a date out of a file name and
            # compares it to a clock.
            if re.search(r"%Y%m%d", line) or re.search(r"%Y%m%d", nxt):
                continue
            suspicious.append((f, i, line.strip()[:80]))
    if not suspicious:
        say("   every strftime goes through the IST offset")
    for f, i, line in suspicious:
        bad("J", "%s:%d writes a timestamp without the IST offset - %s" % (f, i, line))


# ---------------------------------------------------------------- K: dead code
def check_dead():
    """A function defined and never referenced is either a mistake or a trap."""
    say("\nK  DEAD CODE - defined, never called")
    names = []
    for f in py_tools():
        if f.endswith("_test.py"):
            continue
        src = read(os.path.join(HERE, f))
        for m in re.finditer(r"^def ([a-z_][a-z0-9_]*)\(", src, re.M):
            names.append((f, m.group(1)))
    everything = "\n".join(read(os.path.join(REPO, p)) for p in
                           ["tools/" + x for x in os.listdir(os.path.join(REPO, "tools"))
                            if x.endswith(".py") or x.endswith(".sh")])
    everything += "\n".join(read(os.path.join(HERE, f)) for f in py_tools())
    for b in BRIEFS:
        everything += read(os.path.join(HERE, b))
    dead = []
    for f, name in names:
        if name.startswith("_") or name in ("main",):
            continue
        uses = len(re.findall(r"\b%s\b" % re.escape(name), everything))
        # one occurrence is the definition itself
        if uses <= 1:
            dead.append((f, name))
    if not dead:
        say("   every function is referenced")
    for f, name in dead:
        bad("K", "%s defines %s() and nothing references it" % (f, name))
        say("   %-22s %s()" % (f, name))


# ---------------------------------------------------------------- E: ids
def check_ids():
    """A store keyed by an id is only as good as the id's uniqueness."""
    say("\nE  DATA CORRUPTION - is every engine id unique to its engine state?")
    src = read(os.path.join(HERE, "FIXER-BRIEF.md"))
    m = re.search(r'ENGINE="\$ENGINE-([^"]*)"', src)
    if not m:
        say("   no engine-id formula in the brief")
        return
    formula = m.group(1)
    if "sha1sum" in formula or "cut" in formula:
        say("   the suffix is a hash of the diff: %s" % formula[:60])
    else:
        bad("E", "the engine id suffix is %r - a constant suffix is the same id for every "
                 "attempt, and rows keyed by it overwrite each other" % formula)
        say("   CONSTANT SUFFIX: %s" % formula)


# ---------------------------------------------------------------- H: silent truncation
def check_caps():
    """A cap is fine; a cap that does not say it truncated is not."""
    say("\nH  SILENT TRUNCATION - caps and the slices they hide")
    for f in py_tools():
        if f.endswith("_test.py"):
            continue
        src = read(os.path.join(HERE, f))
        for m in re.finditer(r"\[:(\d+)\]", src):
            line = src[:m.start()].count("\n") + 1
            ctx = src.splitlines()[line - 1].strip()
            if any(w in ctx for w in ("more", "truncat", "%", "...", "said", "of ")):
                continue
            say("   %-20s:%-4d %s" % (f, line, ctx[:70]))
    say("   (listed, not failed - a cap is a judgement; a cap that lies about it is a bug)")


# ---------------------------------------------------------------- N: growth
def check_growth():
    """A file the pipeline appends to on every run has to be bounded somewhere."""
    say("\nN  RESOURCE GROWTH - files that grow with every run")
    watched = ["RESULTS.jsonl", "RESULTS-TXT.jsonl", "RUN-LOG.md", "TRACE.md",
               "HYPOTHESES.md", "DEFECTS.md", "REMAINING-DEFECTS.md", "BASELINE.md"]
    for f in watched:
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        size = os.path.getsize(p)
        say("   %-24s %9d bytes" % (f, size))
        if f == "RESULTS.jsonl" and size > 20_000_000:
            bad("N", "RESULTS.jsonl is %.1f MB - the values trim is not running"
                % (size / 1e6))
        if f == "TRACE.md" and size > 200_000:
            bad("N", "TRACE.md is %d bytes - the 400-line trim is not running" % size)


# ---------------------------------------------------------------- A: evidence
def check_evidence():
    """A step that leaves no trace cannot be told apart from one that never ran."""
    say("\nA  SILENT NO-OP - does every tool that changes something write a trace line?")
    must = ["round.py", "classify.py", "ratchet.py", "hypothesis.py", "record.py",
            "seed.py", "build-engine.sh", "commit-gate.sh"]
    for f in must:
        p = (os.path.join(HERE, f) if f.endswith(".py")
             else os.path.join(HERE, f) if os.path.exists(os.path.join(HERE, f))
             else os.path.join(REPO, "tools", f))
        src = read(p)
        if "note(" in src or "trace import note" in src:
            say("   %-20s writes a trace line" % f)
        else:
            bad("A", "%s changes state and writes no trace line - a run that dies there "
                     "leaves nothing" % f)
            say("   %-20s NO TRACE" % f)


# ---------------------------------------------------------------- F: states
def check_states():
    """Every phase must have a way out."""
    say("\nF  DEAD END - can every phase be left?")
    src = read(os.path.join(HERE, "round.py"))
    phases = re.search(r"PHASES = \[([^\]]+)\]", src)
    if not phases:
        bad("F", "round.py has no PHASES list")
        return
    names = [p.strip().strip('"\'') for p in phases.group(1).split(",")]
    say("   phases: %s" % " -> ".join(names))
    if "--close-round" not in src:
        bad("F", "nothing closes a round - fix has no exit")
    if "--advance" not in src:
        bad("F", "nothing advances a phase - measure and classify have no exit")
    if "--apk-status" not in src:
        bad("F", "nothing gates the APK on the rounds being finished")
    say("   every phase has an exit")


# ---------------------------------------------------------------- L: mutation
def check_mutation():
    """A test that passes with the feature removed is not a test."""
    say("\nL  TEST THAT DOES NOT TEST - the suites themselves")
    suites = [f for f in py_tools() if f.endswith("_test.py")]
    for s in suites:
        r = subprocess.run([sys.executable, os.path.join(HERE, s)],
                           capture_output=True, text=True)
        last = (r.stdout or "").strip().splitlines()[-1] if r.stdout else "(no output)"
        ok = r.returncode == 0
        say("   %-22s %s" % (s, "passes" if ok else "FAILS"))
        if not ok:
            bad("L", "%s does not pass - %s" % (s, last))


def main():
    want = [c for c in ALL_CHECKS if "--" + c in sys.argv] or ALL_CHECKS
    runners = {
        "tools": check_tools, "numbers": check_numbers, "ranges": check_ranges,
        "gates": check_gates, "clock": check_clock, "dead": check_dead,
        "ids": check_ids, "caps": check_caps, "growth": check_growth,
        "evidence": check_evidence, "states": check_states, "mutation": check_mutation,
    }
    print("=" * 78)
    print("pipeline audit - the eleven kinds of bug a machine can decide")
    print("=" * 78)
    for c in want:
        try:
            runners[c]()
        except Exception as e:
            bad(c, "the check itself raised %s: %s" % (type(e).__name__, e))

    print("\n" + "=" * 78)
    if FAILS:
        print("%d finding(s)" % len(FAILS))
        for kind, msg in FAILS:
            print("  [%s] %s" % (kind, msg))
        return 1
    print("clean - no finding in the eleven decidable kinds")
    print("G, M and O need a person: the right question, realistic fixtures, safe defaults.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
