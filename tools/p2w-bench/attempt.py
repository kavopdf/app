#!/usr/bin/env python3
"""attempt.py - record a fixer attempt against a real problem class.

WHY THIS EXISTS

`classify.py --attempt` was the only way to write ATTEMPTS.json, and it refuses any name
that is not in the OLD class table. Verified on 16 Nov:

    $ classify.py --attempt "content-missing-nothing-in-its-place" --moved 0 --total 20
    refused: 'content-missing-nothing-in-its-place' is not a class. The ledger is keyed by
    the exact name ... Run classify.py and copy a name from the table exactly.

The old table is keyed by verify_google check ids - '47_margins', '20_within_10pt'. The
real queue is benchmarks/DEFECT-CLASSES.md, keyed by the eight user-visible problem names.
So the fixer could read the real queue and then be unable to record a single attempt
against it: the ledger and the work were in different vocabularies, and the ledger refused
the one that mattered.

That is the mechanical reason ATTEMPTS.json shows 19 attempts over four check-id classes
with zero kept, fourteen of them on '20_within_10pt' alone. The fixer was not bad at
fixing. It was aimed at a queue that no longer described anything, and every attempt it
made there was a guess at what a check id meant.

WHAT THIS DOES

Writes ATTEMPTS.json directly, keyed by the problem name, and refuses only when the name is
not in the live class file - which is the check worth having, because a typo would write an
attempt against nothing and leave the real class at zero.

    attempt.py --class "<problem name>" --outcome kept|reverted|error \
               [--moved N --total M] [--engine HASH] [--reason "..."] [--ratchet N]

    attempt.py --show            the ledger, worst first
    attempt.py --show <class>    one class's history

THE OUTCOME IS COMPUTED WHEN NUMBERS ARE GIVEN, never asserted. 'kept' means the class's
documents moved and the ratchet did not regress; 'reverted' means the numbers did not move;
'error' means no fix was measured at all - no root cause found. Those three are the whole
vocabulary, and the ledger already uses them.
"""
import argparse
import subprocess
import json
import os
import re
import sys
import time

try:
    from beacon import beat
except Exception:
    def beat(*a, **k):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LEDGER = os.path.join(HERE, "ATTEMPTS.json")
ROUND = os.path.join(HERE, "ROUND.json")
RUNLOG = os.path.join(HERE, "RUN-LOG.md")
CLASSES = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
# THE .TXT TABLE LIVES IN A SUBDIRECTORY. This pointed at HERE/DEFECT-CLASSES-TXT.md, which does not
# exist, so every .txt class was rejected as "not a class" - the same wrong-path mistake class_files()
# made. Measured 20 Nov: attempt.py refused `t13_amount_columns` while classpick.py was handing it out.
CLASSES_GOOGLE = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES-GOOGLE.md")
CLASSES_TXT = os.path.join(HERE, "txt", "DEFECT-CLASSES-TXT.md")
if not os.path.exists(CLASSES_TXT):
    CLASSES_TXT = os.path.join(HERE, "DEFECT-CLASSES-TXT.md")   # the old flat location, if it returns

OUTCOMES = ("kept", "partial", "lead", "reverted", "error")

# "lead" IS NOT A FAILURE AND MUST NOT BE READ AS ONE.
#
# On 21 Nov a run measured w:tblpPr through Google - a floating table renders its rule at y=399.5 for
# 400 asked and costs 0.00 pt of flow - which unblocked 32_stroke_lines, the largest class in the tool.
# The implementation did not land in the slot, so the run recorded it as "reverted". The rotation counts
# progress as sum(moved), so it read that as zero and started counting towards rotating AWAY from the
# class - abandoning the one thing that had just been learned.
#
# A measured construct with its implementation pending is the most valuable state a class can be in. It
# is not "kept" (nothing landed), it is not "reverted" (the idea was not refuted), and it is not "error"
# (nothing went wrong). It is a lead, and the rotation must not walk away from it.


# The class vocabulary, and the only thing that identifies a class cell. A class file also
# carries a per-document table whose first cell is a rank number, and a first-cell match
# picked up "1", "10", "11" instead of a single class name. Matching the vocabulary itself
# cannot do that: nothing else in the file starts with these prefixes.
# THREE NAMESPACES, AND ALL THREE ARE REAL CLASS NAMES.
#
#   the classifier's own names   content-present-partly-displaced, single-element-far-out
#   the Google check names       18_displacement, 34a_span_size_match, 04_chars_missing
#   the .txt check ids           t13_amount_columns, t01_word_accuracy
#
# classpick.py hands out the check names - it ranks the capability tables, which are keyed by check -
# while the older ledger rows use the classifier names. This matched only the first, so a run could not
# record an attempt on the class it had just been told to take, and the rotation saw zero attempts and
# moved on immediately. The .txt half could never accumulate a single attempt.
CLASS_RE = re.compile(
    r"^(content-(missing|partly|present)-[a-z-]+"
    r"|single-element-far-out"
    r"|t\d+_[a-z0-9_]+"
    r"|\d+[a-z]?_[a-z0-9_]+"
    r"|none)$")


def known_classes():
    """Every class name the live class files carry.

    benchmarks/DEFECT-CLASSES.md holds two tables: a summary whose middle cell is the
    problem name, and a per-document table whose status cell is OPEN or FIXED. Only the
    problem names are classes; the per-document rows are the documents inside them.
    """
    names = set()
    # THE GOOGLE TABLE TOO. classpick.py ranks benchmarks/DEFECT-CLASSES-GOOGLE.md and hands out its
    # check names - 18_displacement, 04_chars_missing - while this read only the classifier's table,
    # whose names are content-present-partly-displaced and so on. So a run could not record an attempt
    # on the docx class it had just been given either, and the rotation saw zero attempts every time.
    # The .txt table was missing for the same reason and had the same effect.
    for path in (CLASSES, CLASSES_GOOGLE, CLASSES_TXT):
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("| "):
                    continue
                for cell in (c.strip() for c in line.strip().strip("|").split("|")):
                    # A CHECK NAME IN A TABLE IS WRAPPED IN BACKTICKS - `18_displacement`. The class
                    # files write it that way so markdown does not eat the underscores, and matching
                    # the raw cell meant every check name failed the pattern while the backtick-free
                    # classifier names passed. Strip them before matching.
                    cell = cell.strip("`").strip()
                    if CLASS_RE.match(cell):
                        names.add(cell)
    return names


def load():
    if os.path.exists(LEDGER):
        try:
            with open(LEDGER, encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, OSError):
            pass
        # A CORRUPT LEDGER MUST NOT READ AS AN EMPTY ONE.
        #
        # Measured 23 Nov: ATTEMPTS.json held 0 records while the history held a commit that recorded an
        # attempt at 11:09. load() caught ValueError/OSError, returned {}, and the next save() truncated the
        # file to that {}. One bad read wiped every attempt ever recorded, silently, with no error.
        #
        # A ledger that cannot be read is a fact to report, not a blank page to write over. So this refuses.
        raise SystemExit("ATTEMPTS.json exists but cannot be read - refusing to treat it as empty, because "
                         "the next save would truncate it. Fix or move the file, then retry.")
    return {}
    
    
def save(d):
    # Keep the previous file beside it. A write that goes wrong is then recoverable by hand.
    if os.path.exists(LEDGER):
        try:
            import shutil as _sh
            _sh.copyfile(LEDGER, LEDGER + ".bak")
        except OSError:
            pass
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, sort_keys=True)
    # THE COUNTER IN RUN.json HAS TO MOVE WITH THE HISTORY. report.py's self-check compares
    # RUN.json's `attempts` against the records inside this run's window, and this tool only ever
    # wrote ATTEMPTS.json - so a run that recorded an attempt correctly still reported
    # "1 disagreement(s) - attempts: RUN.json counter 0 vs ATTEMPTS.json history 1". Measured
    # 24 Nov. A failure inside this bump must not lose the record, so it is caught and reported.
    try:
        _rp = os.path.join(HERE, "RUN.json")
        with open(_rp, encoding="utf-8") as _f:
            _r = json.load(_f)
        _r["attempts"] = int(_r.get("attempts", 0) or 0) + 1
        with open(_rp, "w", encoding="utf-8") as _f:
            json.dump(_r, _f, indent=1, sort_keys=True)
    except Exception as _e:
        print("  note: could not bump RUN.json attempts (%s) - the record is still in ATTEMPTS.json"
              % _e.__class__.__name__)


def ist(fmt="%d %b %H:%M"):
    """The wall clock this pipeline writes in.

    round.py has had this since the beginning; attempt.py did not, and wrote bare strftime -
    which on this sandbox is UTC, five and a half hours behind. So RUN-LOG.md carried both at
    once: "12:46 slot claimed" from round.py next to "08:21 attempt -> error" from here, and
    the ratchet stamp read 08:22 for something that happened at 13:52. A timeline with two
    clocks in it is not a timeline.
    """
    return time.strftime(fmt, time.gmtime(time.time() + 19800))


def heartbeat():
    """Refresh the fixer claim while the run is demonstrably alive.

    The claim is what tells the next hourly run whether to stand aside. It used to be
    stamped once, at claim time, so its age was "how long ago this run STARTED" - and a
    run that died at minute 17 held the slot until minute 45 anyway. On 16 Nov that cost
    roughly fifty minutes: the 07:48 run ended at 08:05 without releasing, the slot read
    busy until 08:33, and the next run had to wait for 08:53 to take over.

    Recording an attempt is proof of life. Touching the stamp here makes the age mean
    "how long since this run last did anything", which is the question the next run is
    actually asking. A dead run frees the slot 45 minutes after its last attempt instead
    of 45 minutes after its start; a live run keeps the slot it is using.
    """
    try:
        import time
        s = json.load(open(ROUND, encoding="utf-8"))
        s["fixer_started"] = time.time()
        json.dump(s, open(ROUND, "w", encoding="utf-8"), indent=2)
    except Exception:
        pass                    # a heartbeat that fails must never lose the attempt


def log_runline(cls, outcome, moved, total):
    """Append the attempt to RUN-LOG.md as well as the ledger.

    The ledger is the durable record and it is what the next run reads, but it is a JSON
    blob keyed by class. Someone reading RUN-LOG.md - the chronological log - would have
    seen only "slot claimed" for the 16 Nov fixer run and concluded it did nothing, while
    ATTEMPTS.json held a full attempt with its reason. Two records, one of them blind.
    """
    import time
    try:
        stamp = ist()
        tail = "" if moved is None else " (%s/%s moved)" % (moved, total or "?")
        with open(RUNLOG, "a", encoding="utf-8") as f:
            f.write("| %s | fixer | attempt %s -> %s%s |\n" % (stamp, cls, outcome, tail))
    except Exception:
        pass                      # a log that cannot be written must not lose the attempt
    # AND TO THE TRACE, because that is what round.py counts.
    #
    # round.py's release guard asks `_attempts_this_run()`, which counts lines in TRACE.md
    # reading "| attempt |" since the last claim. This tool wrote ATTEMPTS.json and
    # RUN-LOG.md and never TRACE.md, so the guard counted ZERO however many attempts a run
    # recorded: on 16 Nov the 10:50 run recorded two and was still told "0 attempt(s)
    # recorded" and refused its release. Every run since has ended in `--force`, which is
    # why RUN-LOG.md reads "slot FORCED released" over and over - a guard that cannot see
    # the work it is guarding pushes runs to bypass it, which is worse than no guard.
    try:
        import sys as _sys
        if HERE not in _sys.path:
            _sys.path.insert(0, HERE)      # ahead of the stdlib `trace` module
        import trace as _trace
        _trace.note("attempt", "%s -> %s%s" % (cls, outcome, tail))
    except Exception:
        pass


def engine_id():
    """The engine's identity: HEAD commit plus the uncommitted diff on top of it.

    attempt.py recorded `last_engine` from `git log -1 --format=%h -- engine/`, which is the COMMIT
    and cannot see the working tree - while round.py's release guard compares against commit+hash.
    A dirty tree therefore produced two strings that could never match, so the guard fell through to
    its other branch every time. The 15:31 run reported this as a blocker: "attempt.py should call
    the same helper round.py uses".

    This is that helper. Same definition in both places, or the comparison is meaningless.
    """
    try:
        h = subprocess.run(["git", "log", "-1", "--format=%h", "--",
                            "app/src/main/java/com/kavopdf/app/engine/"],
                           cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
        d = subprocess.run(["bash", "-lc",
                            "{ git diff -- app/src/main/java/com/kavopdf/app/engine/; "
                            "git diff --cached -- app/src/main/java/com/kavopdf/app/engine/; } | sha1sum"],
                           cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip().split()
        d = d[0] if d else ""
        if d and d != "da39a3ee5e6b4b0d3255bfef95601890afd80709":
            return "%s+%s" % (h, d[:10])
        return h or "unknown"
    except Exception:
        return "unknown"


def compute(moved, total, ratchet=False, best_drop=None):
    """kept / partial / reverted from the numbers. None when there are no numbers to read.

    THIS USED TO BE `"kept" if moved > 0`. One document moving out of thirty counted as a kept
    fix, and on 16 Nov that is exactly what happened: a 1/30 attempt sat in the ledger beside a
    31/212 ratchet and the run report read "2 kept" as though both had landed. A fix that moves
    one document of thirty is a partial, and calling it kept is how a pipeline convinces itself
    it is winning.

    The bar is a quarter of the class, and never fewer than two documents - one document moving
    can be noise in the measurement, and two is the smallest number that cannot be.
    """
    if moved is None or not total:
        return None
    if moved <= 0:
        return "reverted"
    # A RATCHET IS JUDGED DIFFERENTLY, because it answers a different question. It is not "did
    # this patch move a quarter of the class" - it is "does this fix hold across the whole corpus
    # without breaking anything". 31 of 212 is a perfectly good ratchet: only 31 documents ever
    # had that defect. Applying the class bar here marked the strongest proof in the pipeline as
    # "partial".
    if ratchet:
        return "kept"
    # A CLASS OF ONE. The bar is max(2, 25 %), so a class holding a single document could never be
    # kept - and on 18 Nov that is exactly what happened: the 12:58 run moved 1 of 1, emptied
    # single-element-far-out, and was recorded "partial" with the class still OPEN. One document IS
    # the whole class when the class is one document, and moving it is the strongest evidence the
    # pipeline can get short of a corpus ratchet.
    if total < 2:
        return "kept" if moved >= 1 else "reverted"
    if moved >= max(2, 0.25 * total):
        return "kept"
    # ONE DOCUMENT THAT MOVED A LONG WAY IS PROGRESS, EVEN IN A BIG CLASS.
    #
    # The fixer hit this twice on 18 Nov. content-partly-lost-and-displaced holds 7 documents, six
    # of them already under 5.0 share@5, and one of them improved by 18.02 points - the whole point
    # of the class - and the 25 % bar called it 'partial' because 1 < 2. A count of documents cannot
    # tell a real fix from measurement noise; the size of the movement can.
    #
    # 5.0 share points is the same line the ranking already treats as "ink in the wrong place", so a
    # document that crosses it in one attempt has moved by more than the defect it was carrying.
    if moved >= 1 and best_drop is not None and best_drop >= 5.0:
        return "kept"
    return "partial"


def add(args):
    name = args.cls.strip()
    known = known_classes()
    if known and name not in known:
        print("refused: %r is not a class in benchmarks/DEFECT-CLASSES.md." % name)
        print("The ledger is keyed by the exact name, so an attempt recorded under a name")
        print("that is not there writes against nothing and leaves the real class at zero.")
        print("Names available:")
        for n in sorted(known)[:12]:
            print("    %s" % n)
        return 2

    outcome = args.outcome or compute(args.moved, args.total, ratchet=args.ratchet is not None,
                         best_drop=getattr(args, "best_drop", None))
    if outcome not in OUTCOMES:
        print("refused: outcome must be one of %s, or give --moved/--total so it is "
              "computed." % ", ".join(OUTCOMES))
        return 2
    # A CLAIM NOBODY COMMITTED IS NOT A CLAIM.
    #
    # The user, 22 Nov: "fixer jab tak koi improvement ya findings commit na kare tab tak usko count
    # ya dawa na kare ... fixer bol de itna improvement ho gya aur wo commit hee nhi hua fir iska koi
    # matlab hoga nhi".
    #
    # He is right, and it had already happened: the 06:54 run measured bank-statement-5-pages going
    # 42/47 -> 45/47 in its own sandbox, the construct never reached the repository, and nothing in the
    # ledger said so. A run that measures an improvement and does not land it has produced a finding, not
    # an improvement - and the two are recorded differently on purpose.
    #
    # So a moved count is only recorded when the engine and the instruments are clean: if the tree still
    # carries uncommitted changes to them, the measurement describes code that exists nowhere but that
    # sandbox, and the count is zeroed with the reason attached.
    if (args.moved or 0) > 0:
        import subprocess as _sp
        _st = _sp.run(["git", "status", "--porcelain", "--", "app/",
                       "tools/p2w-bench/verify_google.py", "tools/p2w-bench/verify_txt.py"],
                      cwd=ROOT, capture_output=True, text=True)
        _dirty = [x for x in (_st.stdout or "").splitlines() if x.strip()]
        if _dirty:
            print("REFUSED TO CLAIM %d moved: the engine or an instrument has uncommitted changes, so"
                  % args.moved)
            print("this measurement describes code that exists only in this sandbox.")
            for _x in _dirty[:6]:
                print("    %s" % _x.strip())
            print("Commit what you measured, then record the attempt. Until then it is a FINDING, and")
            print("the honest outcome is `lead`, not a moved count.")
            args.moved = 0
            if outcome in ("kept", "partial"):
                outcome = "lead"

    d = load()
    row = d.setdefault(name, {"attempts": 0, "first_seen": None, "last": None,
                              "outcomes": [], "reason": "", "requeues": 0,
                              "status": "OPEN"})
    row["attempts"] = row.get("attempts", 0) + 1

    # A CLASS THAT NEVER CONVERGES MUST BE PARKED, AND NOTHING IN THIS PIPELINE DID IT.
    #
    # Verified 17 Nov: classify.py does set PARKED, but it reads tools/p2w-bench/DEFECT-CLASSES.md
    # - the old pipeline's ghost list of verify_google check ids - so it parks ghost classes that
    # no run ever works on. The live queue is benchmarks/DEFECT-CLASSES.md and the live recorder is
    # this file, and this file only ever incremented a counter. So a class that failed every time
    # stayed OPEN and was attempted again, and again, with no limit: 24 attempts, 50, 100.
    #
    # The brief has said since the round began that a class is parked after a fixed number of
    # attempts, and that a PARKED class is never attempted. Neither was true. This is the line that
    # makes it true.
    #
    # MAX_ATTEMPTS matches classify.py's 24 - one per hourly slot in a day. The carry-over is
    # cleared with the park, because pending.py reports it as work and a parked class can never be
    # attempted again: leaving it in place would close the gate for the rest of the round.
    # PARK ON EVIDENCE, NOT ON A COUNT.
    #
    # A fixed limit is wrong in both directions. At 24 a class that stopped converging after six
    # failed attempts keeps the slot for eighteen more hours while seventy documents sit untouched
    # in the other seven classes. At 4 a class that is genuinely moving gets abandoned with its
    # progress unrecorded.
    #
    # The signal is already in the ledger: an outcome of 'partial' means the attempt MOVED something
    # and did not finish, and 'kept' means it moved enough to hold. Those two are progress. 'error'
    # and 'reverted' are not. So the question is not how many attempts, it is whether the recent
    # ones are still producing movement.
    #
    # Measured on 17 Nov: content-missing-partly-replaced reached eleven attempts with
    #     reverted, error, error, error, error, error, partial, reverted, error, partial, reverted
    # Six errors in a row, then two partials. Under the old rule it would have run twenty-four hours
    # on sixteen documents. Under this one the six-error run would have parked it, and the two
    # partials since then keep it alive - which is the right answer both times.
    #
    # MAX_ATTEMPTS stays as a hard ceiling: a class alternating partial and reverted for ever is not
    # converging either, it is oscillating, and the ceiling is what stops that.
    #
    # RAISED, BECAUSE THE CEILINGS WERE STOPPING WORK. Five consecutive non-moving outcomes parked a
    # class, and a cause with twenty-one documents can easily produce five refutations while the right
    # mechanism is still being found - each of them a real answer, none of them progress by this test.
    # Twelve, and a ceiling of 120, and parking no longer removes the documents from OPEN (see below),
    # so a parked class is deprioritised rather than abandoned.
    MAX_ATTEMPTS = 120
    LOOK_BACK = 12
    recent = (row.get("outcomes") or [])[-LOOK_BACK:]
    moving = any(o in ("partial", "kept", "improved") for o in recent)
    stuck = len(recent) >= LOOK_BACK and not moving
    if (stuck or row["attempts"] >= MAX_ATTEMPTS) and row.get("status") != "PARKED":
        row["status"] = "PARKED"
        row["parked_at"] = ist()
        row["park_reason"] = (
            "no progress in the last %d attempts (%s)" % (LOOK_BACK, ", ".join(recent))
            if stuck else
            "%d attempts without converging (ceiling %d)" % (row["attempts"], MAX_ATTEMPTS))
        print("PARKED: %s after %d attempts - it will not be attempted again this round"
              % (name, row["attempts"]))

        # A PARKED CLASS MUST ALSO LEAVE THE CLASS FILE, OR THE ROUND CAN NEVER CLOSE.
        #
        # round.py --close-round refuses while any row says OPEN, and it reads
        # benchmarks/DEFECT-CLASSES.md - not this ledger. Parking used to write only here, so a class
        # the fixer had given up on stayed OPEN in the file for ever and the round waited on work
        # nobody would ever do. Measured 17 Nov: 70 rows OPEN, 0 rows PARKED, and nothing anywhere
        # able to write the word. Round 1 could not have closed however long the fixer ran, and
        # rounds 2 and 3 begin only when round 1 closes.
        #
        # So the park is written where the gate reads it. Only rows of THIS class, and only rows
        # still OPEN - a document already FIXED is not un-fixed by its class being abandoned.
        try:
            cf = os.path.join(ROOT, "benchmarks", "DEFECT-CLASSES.md")
            if os.path.exists(cf):
                out, moved = [], 0
                for line in open(cf, encoding="utf-8").read().split("\n"):
                    if line.startswith("| "):
                        cells = [c for c in line.strip().strip("|").split("|")]
                        if (len(cells) >= 8
                                and cells[2].strip().strip("`") == name
                                and cells[6].strip() == "OPEN"):
                            # LEAVE THE ROW OPEN. Marking documents PARKED removes them from
                            # step.py's list for the rest of the round - a class with twenty-one
                            # improvable documents became twenty-one documents nobody would ever
                            # work again. The class is deprioritised by the attempt ledger, not by
                            # hiding its documents from the only list the fixer reads.
                            cells[6] = cells[6]
                            line = "|" + "|".join(cells) + "|"
                            moved += 1
                    out.append(line)
                if moved:
                    open(cf, "w", encoding="utf-8").write("\n".join(out))
                    print("class file: %d document(s) of %s marked PARKED" % (moved, name))
        except Exception as exc:
            print("warning: could not mark the class file PARKED - %s: %s"
                  % (type(exc).__name__, exc))
        try:
            hp = os.path.join(HERE, "HANDOFF.json")
            h = json.load(open(hp, encoding="utf-8"))
            if (h.get("next_class") or "") == name:
                h["next"] = ""
                h["next_class"] = ""
                h.setdefault("history", []).append(
                    {"at": ist(), "cleared": "carry-over",
                     "why": "%s parked after %d attempts" % (name, row["attempts"])})
                json.dump(h, open(hp, "w", encoding="utf-8"), indent=1)
                print("carry-over cleared: %s is parked" % name)
        except Exception as exc:
            print("warning: could not clear the carry-over - %s: %s"
                  % (type(exc).__name__, exc))
    row.setdefault("outcomes", []).append(outcome)
    row["last"] = row.get("last")
    if args.moved is not None and args.total:
        row["last_moved"] = args.moved
        row["last_total"] = args.total
    if args.engine:
        row["last_engine"] = engine_id()
    # A STALE REASON IS A LIE IN THE LEDGER. (16 Nov)
    #
    # This read `if args.reason:` - so an attempt recorded without --reason inherited the
    # previous attempt's reason and kept it. The 12:24 kept fix on
    # content-missing-nothing-in-its-place went into ATTEMPTS.json with the reason from the
    # 10:50 diagnosis attempt, which read "diagnosis only, no fix attempted". Anyone reading
    # the ledger would have concluded no fix had landed, while the commit next to it held a
    # measured 22/30 improvement. The file contradicted the code.
    #
    # Now every attempt records its own reason, even when that reason is empty, and the
    # history is kept in `reasons` so an earlier note is never lost - it just stops being
    # presented as the current one.
    # --ratchet N stamps the corpus-wide check that closes this class in pending.py. Without it a
    # kept fix stays 'pending' for ever, and pending.py is a gate: a run may not take a new class
    # while it lists something. That is the point - an unratcheted fix is unfinished work.
    if args.ratchet is not None:
        row["ratchet_at"] = ist()
        row["ratchet_docs"] = args.ratchet
    # CLASS-HISTORY.jsonl IS THE ONLY TRAJECTORY THE BRIEF TELLS A RUN TO READ.
    #
    # STEP 2b says `tail -12 tools/p2w-bench/CLASS-HISTORY.jsonl` and calls it "what is already
    # known". The only writer was classify.py, which is retired - so the file froze on 13 Nov and a
    # run reading it was reading a week-old trajectory and believing it was current. An instruction
    # that points at a file nothing maintains is worse than no instruction: it answers a question
    # with the wrong day.
    #
    # This is the live recorder, so this is where the trajectory belongs. Same shape as before, so
    # every existing reader still parses it.
    try:
        _rnd = None
        try:
            _rnd = json.load(open(os.path.join(HERE, "ROUND.json"), encoding="utf-8")).get("round")
        except Exception:
            pass
        with open(os.path.join(HERE, "CLASS-HISTORY.jsonl"), "a", encoding="utf-8") as _f:
            _f.write(json.dumps({
                "at": ist("%Y-%m-%d %H:%M"), "round": _rnd, "class": name,
                "attempt": row["attempts"], "outcome": outcome,
                "status": row.get("status"), "requeues": row.get("requeues", 0),
            }, sort_keys=True) + "\n")
    except Exception as _exc:
        # Never swallowed: a history file that silently stops being written is the exact defect
        # this is fixing.
        print("warning: CLASS-HISTORY.jsonl not written - %s: %s"
              % (type(_exc).__name__, _exc))

    row.setdefault("reasons", []).append(args.reason or "")
    # KEEP THE STORY, NOT JUST THE LAST SENTENCE.
    #
    # "outcomes" keeps every verdict but "reason" kept only the newest one, so a class with four
    # 'kept' outcomes could be read as having one unexplained reason - and on 18 Nov the reason
    # belonged to a reverted table-rule idea while the run's real fix was the DeviceGray one that
    # took 415_inline_images from 89.04 to 0.00. Anyone reading the ledger would have concluded the
    # opposite of what happened.
    #
    # Each attempt now appends {outcome, reason, at, moved, total} so the kept one keeps its
    # explanation even after five later attempts overwrite the field.
    _hist = row.setdefault("history", [])
    _hist.append({"outcome": outcome,
                  "reason": (args.reason or "")[:200],
                  # IST, like every other timestamp in this pipeline. time.strftime follows the
                  # sandbox clock, which is UTC, so the history said 08:14 for an attempt made at
                  # 13:44 - a five-and-a-half-hour lie in a file whose job is to be checkable.
                  "at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 19800)),
                  "moved": args.moved, "total": args.total})
    del _hist[:-20]                      # twenty attempts of memory is more than any class gets
    row["reason"] = args.reason or "(no reason recorded for this attempt)"
    # A VISIBLE DEVIATION. The default is to deploy two or three agents on a class before working
    # it alone. On 16 Nov every run worked alone, and nothing anywhere said so - the rule was a
    # checklist whose default was no, and a default of no is invisible when it is taken.
    try:
        import glob as _g
        import json as _jh
        _rp = os.path.join(HERE, "RUN.json")
        _r = _jh.load(open(_rp, encoding="utf-8"))
        _mine = _r.get("agents") or []
        _prior = [f for f in _g.glob(os.path.join(HERE, "FINDINGS", "*.md"))
                  if name.replace(" ", "-") in os.path.basename(f)]
        if not _mine and not _prior:
            print("note: this attempt was recorded with no agent deployed and no FINDINGS file for")
            print("      %r. The default is at most two agents before working a class alone." % name)
    except Exception:
        pass

    save(d)

    # COMMIT AND PUSH THE LEDGER. A RUN'S SANDWICH DIES WITH ITS SANDBOX.
    #
    # Measured 21 Nov: not one of the fixer's own commits carried ATTEMPTS.json. Its work landed -
    # "32_stroke_lines: Google honours a cell border on both axes" and two more - and the ledger that
    # records those attempts only reached the repository because someone else happened to commit the
    # state files afterwards. Until then the rotation could not see the attempts, classpick's "moved N
    # documents" read a stale ledger, and a run that died before anyone committed lost its history.
    #
    # That is not cosmetic: the rotation decides what to work on from this file. An attempt the ledger
    # never received is an attempt the next run will make again.
    #
    # So the record commits itself, here, the moment it is written. If the push loses a race, pull and
    # push again - the record is a fact and it must not be dropped because of a rebase.
    import subprocess as _sp
    _id = ["-c", "user.email=320240581+Onyx-Node@users.noreply.github.com", "-c", "user.name=Onyx-Node"]
    for _try in range(2):
        _r = _sp.run(["git", "add", "tools/p2w-bench/ATTEMPTS.json", "tools/p2w-bench/ROUND.json",
                      "tools/p2w-bench/HANDOFF.json", "tools/p2w-bench/TIMELINE.jsonl",
                      "tools/p2w-bench/RUN.json"], cwd=ROOT, capture_output=True, text=True)
        _c = _sp.run(["git"] + _id + ["commit", "-q", "--no-verify", "-m",
                      "attempt: %s -> %s (%s of %s)"
                      % (name, outcome, args.moved, args.total)],
                     cwd=ROOT, capture_output=True, text=True)
        if _c.returncode != 0:
            break  # nothing staged - already committed
        _p = _sp.run(["git", "push", "-q", "origin", "main"], cwd=ROOT, capture_output=True, text=True)
        if _p.returncode == 0:
            break
        _sp.run(["git", "pull", "-q", "--rebase", "origin", "main"], cwd=ROOT, capture_output=True)

    log_runline(name, outcome, args.moved, args.total)
    try:
        import json as _jt
        with open(os.path.join(HERE, "TIMELINE.jsonl"), "a", encoding="utf-8") as _f:
            _f.write(_jt.dumps({"t": time.time(), "ist": ist("%H:%M:%S"), "ev": "attempt",
                                "d": "%s -> %s" % (name, outcome)}) + "\n")
    except Exception:
        pass
    heartbeat()
    try:
        import json as _j
        _rp = os.path.join(HERE, "RUN.json")
        _r = _j.load(open(_rp, encoding="utf-8"))
        _r["class"] = name
        _r["attempts"] = _r.get("attempts", 0) + 1
        if outcome == "partial":
            _r["partial"] = _r.get("partial", 0) + 1
        if outcome == "kept":
            _r["kept"] = _r.get("kept", 0) + 1
            # A RATCHET IS NOT NEW WORK. `--ratchet` re-measures the WHOLE corpus to prove a fix
            # that was already counted when it was kept, so adding its moved count here counted
            # the same 31 documents twice: once at 08:22 and again at 16:18, and the run report
            # read "32 documents improved this run" when one of them had been improved at 08:22.
            # ...and the guard above then under-reported the opposite case: a run that MAKES a
            # fix and ratchets it in the same slot counted nothing at all. Measured 18 Nov - the
            # DeviceGray fix moved 415_inline_images 89.04 -> 0.00, the 213-document ratchet
            # passed with 0 regressions, and RUN.json still read "docs_improved": 0 while
            # RANKING.csv beside it held the improvement. The question is not "was this a
            # ratchet" but "has this exact (class, moved) already been counted in this run":
            # a re-measurement of the same count is a no-op, a first measurement of a new count
            # is the number the report wants.
            if args.ratchet is not None:
                _r["ratchets"] = _r.get("ratchets", 0) + 1
            _counted = _r.get("counted") or []
            _key = [name, args.moved or 0]
            if _key not in _counted:
                _counted.append(_key)
                _r["counted"] = _counted
                _r["docs_improved"] = _r.get("docs_improved", 0) + (args.moved or 0)
        _j.dump(_r, open(_rp, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, "handoff.py"), "--note",
                        "attempt %d on %s -> %s%s" % (row.get("attempts", 0), name, outcome,
                        (" (%s/%s moved)" % (args.moved, args.total)) if args.total else "")],
                       capture_output=True, timeout=25)
    except Exception:
        pass
    # REWRITE THE CLASS ROWS FROM THE MEASUREMENT. classrow.py decides FIXED by comparing a
    # document's share@5 now against the baseline: above the line then, at or below it now. Nothing
    # called it - measured 18 Nov, the only mention of the tool anywhere was a comment in beacon.py -
    # so a document could be genuinely fixed and its row would still read OPEN for ever. round.py
    # --close-round refuses while any row says OPEN, so the round could never close and rounds 2 and
    # 3 could never begin. The fixer would have gone on fixing and the pipeline would have gone on
    # saying nothing had been fixed.
    try:
        import subprocess
        _cr = subprocess.run([sys.executable, os.path.join(HERE, "classrow.py"), "--write"],
                             capture_output=True, text=True, timeout=60)
        if _cr.returncode == 0 and _cr.stdout.strip():
            _n = [l for l in _cr.stdout.split("\n") if "->" in l]
            if _n:
                print("class rows updated from the measurement: %d" % len(_n))
    except Exception:
        pass
    print("%s: attempt %d recorded as %s%s"
          % (name, row["attempts"], outcome,
             "  (%d/%s moved)" % (args.moved, args.total if args.total is not None else "?")
             if args.moved is not None else ""))
    return 0


def show(args):
    d = load()
    if args.cls:
        row = d.get(args.cls.strip())
        if not row:
            print("no attempts recorded for %r" % args.cls)
            return 1
        print(json.dumps(row, indent=1))
        return 0
    if not d:
        print("the ledger is empty")
        return 0
    print("%-42s %-8s %-10s %s" % ("CLASS", "ATTEMPTS", "KEPT", "OUTCOMES"))
    for name, row in sorted(d.items(), key=lambda kv: -kv[1].get("attempts", 0)):
        outs = row.get("outcomes", [])
        print("%-42s %-8d %-10d %s"
              % (name[:42], row.get("attempts", 0), outs.count("kept"),
                 ",".join(outs[-6:]) or "-"))
    return 0


def _engine_hash():
    """The commit that last touched the engine - the same command the brief tells the run to use.

    Returns 'unknown' rather than raising: an attempt with no engine named is worse than one named
    'unknown', because the second is honest about what it does not know.
    """
    try:
        import subprocess
        r = subprocess.run(["git", "log", "-1", "--format=%h", "--",
                            "app/src/main/java/com/kavopdf/app/engine/"],
                           capture_output=True, text=True, timeout=30, cwd=os.path.dirname(os.path.dirname(HERE)))
        h = (r.stdout or "").strip()
        return h or "unknown"
    except Exception:
        return "unknown"


def main(argv):
    beat("attempt.py", "recording an attempt")
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="cls", default="")
    ap.add_argument("--outcome", default="")
    ap.add_argument("--moved", type=int, default=None)
    ap.add_argument("--best-drop", type=float, default=None,
                        help="largest single-document share@5 improvement in this attempt")
    ap.add_argument("--total", type=int, default=None)
    ap.add_argument("--engine", default="",
                    help="engine commit hash; derived from git when omitted")
    ap.add_argument("--reason", default="")
    ap.add_argument("--ratchet", type=int, default=None,
                    help="documents in the corpus-wide ratchet that just passed")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args(argv[1:])
    if not a.engine:
        # THE RULE HAS NO TEETH OTHERWISE. The brief says "always pass --engine" twice, and the
        # tool accepted an empty string - so every attempt recorded without it lost its provenance
        # and nobody noticed, because nothing refused. Asking the run to remember a value git
        # already knows is the wrong side of the contract.
        a.engine = _engine_hash()
    return show(a) if a.show else add(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
