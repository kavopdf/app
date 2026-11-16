#!/usr/bin/env python3
"""
round.py - the state machine that runs the whole thing three times.

THE SHAPE THE USER ASKED FOR
  Round 1: measure all 208, separate the defects, fix them all.
  When every document is done - however long that takes - start again:
  Round 2: a fresh baseline on the fixed engine, separate, fix.
  Round 3: the same once more. Then stop.

WHY A STATE FILE AND NOT THREE CRONS GUESSING
  Three crons on timers will not do this by themselves. The baseline fires every
  four hours whether or not the fixer has finished; the fixer fires whether or not
  anything has been measured; and nothing knows what a round is. Each one would
  keep doing its own job forever, which is exactly the behaviour that produced
  208 measurements and no progress in one direction.

  ROUND.json is the only thing that decides whose turn it is. Every cron reads its
  phase first and does nothing if the phase is not its own. One file, one writer
  per phase, no race.

THE PHASES
  measure    baseline runs, 20 documents a run, until all 208 have a score
  classify   classifier runs once and writes the ranked classes
  fix        fixer runs, one class a run, until no class is OPEN
  done       three rounds finished; every cron reports and stops

WHAT ENDS A PHASE
  measure -> classify   when every row in BASELINE.md has a score
  classify -> fix       when DEFECT-CLASSES.md is newer than BASELINE.md
  fix -> measure        when every class file reports no OPEN class (round.py --close-round)
  fix -> done           when that happens in round 3

USAGE
  python3 tools/p2w-bench/round.py                 # status
  python3 tools/p2w-bench/round.py --phase         # just the phase, for a cron to compare
  python3 tools/p2w-bench/round.py --advance       # move to the next phase
  python3 tools/p2w-bench/round.py --close-round   # archive, reset, next round
  python3 tools/p2w-bench/round.py --force-round N # set the round by hand
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "ROUND.json")
BASE = os.path.join(HERE, "BASELINE.md")
CLASSES = os.path.join(HERE, "DEFECT-CLASSES.md")
# The classifier now writes benchmarks/DEFECT-CLASSES.md, beside the measurement it
# describes. This file kept reading tools/p2w-bench/DEFECT-CLASSES.md, which nothing
# wrote any more, so open_classes() always said 0 and --close-round always said
# "nothing is OPEN" - a round could be closed with every class still unfixed.
CLASSES_B = os.path.normpath(os.path.join(os.path.dirname(HERE), "..",
                                          "benchmarks", "DEFECT-CLASSES.md"))


def class_files():
    """The class files this round is judged against. ONE authority, not two.

    benchmarks/DEFECT-CLASSES.md is what the classifier writes now. tools/p2w-bench/
    DEFECT-CLASSES.md is the old pipeline's list and describes defects in an engine that
    no longer exists.

    Reading BOTH is worse than reading either. The stale file still carries OPEN rows, so
    --close-round would refuse for ever on classes nobody can fix, while a fixer working
    from it would be fixing against a ghost. benchmarks/ wins outright when it is present;
    tools/ is read only when benchmarks/ is absent, which is the one case where it is
    still the best information available.
    """
    out = []
    if os.path.exists(CLASSES_B):
        out.append(CLASSES_B)
    elif os.path.exists(CLASSES):
        out.append(CLASSES)
    txt = os.path.join(HERE, "DEFECT-CLASSES-TXT.md")
    if os.path.exists(txt):
        out.append(txt)
    return out
ATTEMPTS = os.path.join(HERE, "ATTEMPTS.json")

ROUNDS_TOTAL = 3
PHASES = ["measure", "classify", "fix", "done"]

# A fixer attempt takes twelve to twenty-five minutes and the fixer is scheduled hourly,
# so two runs can land on top of each other - both editing the engine, both committing, one
# overwriting the other. This claim makes the second run step aside instead. It expires,
# because a run that dies must not block the next one for ever.
# Each cron claims its slot before working, so an overrun cannot put two runs of
# the same cron in the same phase at once. The stale window is per cron, sized to
# how long one run actually takes: a dead run must not block the next one forever,
# and a live run must never be mistaken for a dead one.
# FIXER_STALE_MIN was here, set to 100 and used by nothing. The real value is
# CLAIM_STALE_MIN["fixer"] = 45 below, and a constant that says 100 next to one that says 45 is
# worse than no constant: it is a reader - or a fixer reading its own pipeline - believing the
# slot lasts an hour and forty minutes when it lasts forty-five.
# The fixer's stale limit sits above its longest run and below its two-slot gap. A run that
# finishes releases the slot itself, so this governs only a run that died: 45 minutes means a
# crash costs one slot, and a live run of up to forty-five minutes is never doubled - two runs
# editing the engine at once would each revert the other's fix.
def _run_record(action, **kw):
    """RUN.json - one record per fixer run, written by the tools, never by hand.

    round.py stamps the start ONCE and the end once. It deliberately does not refresh the start
    on the heartbeat, which is what made the claim age useless for reporting: attempt.py resets
    that on every attempt, so "how long did this run take" was always about seven minutes.
    """
    import json as _j
    fp = os.path.join(HERE, "RUN.json")
    try:
        d = _j.load(open(fp, encoding="utf-8"))
    except Exception:
        d = {}
    if action == "start":
        d = {"started_ts": time.time(), "started": ist("%H:%M"), "ended_ts": None, "ended": None,
             "class": "", "attempts": 0, "kept": 0, "docs_improved": 0, "agents": [],
             "obstacles_cleared": 0, "needs_human": 0}
    elif action == "end":
        d["ended_ts"] = time.time()
        d["ended"] = ist("%H:%M")
    else:
        d.update(kw)
    try:
        _j.dump(d, open(fp, "w", encoding="utf-8"), indent=1)
    except Exception:
        pass


def _handoff(*args):
    """Best-effort: never let the handoff file break the round machine."""
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, "handoff.py")] + list(args),
                       capture_output=True, timeout=25)
    except Exception:
        pass


# The fixer window came down from 45 to 20 once round.py --heartbeat existed. Before that the
# only heartbeat was on an attempt, so a run doing a long ratchet was indistinguishable from a
# dead one, and the window had to cover the longest silent stretch - which also meant a dead run
# held the slot for 45 minutes. A run that is alive now says so; a run that is not costs 20.
CLAIM_STALE_MIN = {"fixer": 20, "baseline": 45, "classifier": 20}


def load():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"round": 1, "rounds_total": ROUNDS_TOTAL, "phase": "measure",
            "started": time.time(), "history": []}


def save(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), indent=2, sort_keys=True)


# THE INSTRUMENT CHANGED AND THIS FILE DID NOT.
#
# rows() used to read BASELINE.md, because BASELINE.md was what the old verifier wrote.
# The measurement layer is now benchmarks/p2w.py, and it writes benchmarks/RANKING.csv.
# Nothing wrote BASELINE.md any more, so rows() returned (0, 0): status() said "0 of 0
# documents scored" and every phase decision downstream was made against an empty table.
# A phase machine reading a file nobody writes is not a phase machine, it is a decoration.
#
# RANKING.csv is now the source of truth: one row per document, and a row counts as
# scored when share5 is a number. A MEASURE-ERROR row carries an empty share5 and is
# therefore unscored - which is right, because it was not measured.
RANKING = os.path.join(os.path.dirname(HERE), "..", "benchmarks", "RANKING.csv")


def rows():
    """(total, scored) from benchmarks/RANKING.csv."""
    total = scored = 0
    path = os.path.normpath(RANKING)
    if not os.path.exists(path):
        return 0, 0
    try:
        import csv as _csv
        with open(path, encoding="utf-8") as f:
            for r in _csv.DictReader(f):
                total += 1
                try:
                    float((r.get("share5") or "").strip())
                    scored += 1
                except (TypeError, ValueError):
                    pass
    except Exception:
        return 0, 0
    return total, scored


def open_classes():
    """Count classes still marked OPEN, across every class file that exists.

    "OPEN" is matched as a CELL, not as the last thing on the line. The old
    endswith("| OPEN |") test silently stopped working the moment a column was added to
    the right of it, which is a gate that turns itself off when the table is edited.
    """
    files = class_files()
    if not files:
        return None
    n = 0
    for fp in files:
        for line in open(fp, encoding="utf-8"):
            if not line.startswith("| ") or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and "OPEN" in cells:
                n += 1
    return n


def status(s=None):
    s = s or load()
    total, scored = rows()
    oc = open_classes()
    print("round %d of %d   phase: %s" % (s["round"], s["rounds_total"], s["phase"]))
    print("  documents scored : %d of %d" % (scored, total))
    print("  open classes     : %s" % ("-" if oc is None else oc))
    if s["phase"] == "measure":
        print("  next             : baseline runs until every row of RANKING.csv is scored")
    elif s["phase"] == "classify":
        print("  next             : classifier runs once")
    elif s["phase"] == "fix":
        print("  next             : fixer runs until no class is OPEN")
    else:
        shipped = s.get("apk_shipped") or ""
        print("  apk shipped      : %s" % (shipped or "not yet"))
        print("  next             : %s" % ("nothing - already shipped" if shipped
                                            else "the APK cron ships once, on its next run"))
    for h in s.get("history", [])[-4:]:
        print("  was: round %s %s -> %s" % (h.get("round"), h.get("phase"), h.get("at", "")))
    return s


try:
    from trace import note
except Exception:
    def note(*a, **k):
        pass

def ist(fmt="%d %b %H:%M"):
    """The wall clock this pipeline writes in. The sandbox is UTC; every row in every
    file here is IST, and a bare strftime writes a time five and a half hours behind the
    rows around it."""
    t = time.gmtime(time.time() + 5 * 3600 + 30 * 60)
    return time.strftime(fmt, t)


# How far into the future a claim may sit before it is treated as corrupt rather than
# live. Some jitter is real - two machines, NTP correcting, a run that writes a second
# early - so a small window is allowed. Beyond it, a future timestamp is a broken record,
# not a running job.
FUTURE_TOLERANCE_MIN = 5


def claim_age_min(started):
    """Minutes since a claim, or None when there is no claim.

    A NEGATIVE age is the dangerous case and this is why the helper exists. With
    `age = (now - started)/60` a timestamp written in the future - clock skew, a
    hand-edited ROUND.json, a timezone mistake - produces a negative age, and
    `age < limit` is then true for ever. The slot reads as busy for ever, the cron
    stands aside on every run, and the phase never moves. That is indistinguishable
    from the pipeline working until someone reads ROUND.json by hand.

    So a timestamp far in the future is treated as stale, which lets the next run take
    the slot. The cost of being wrong is one doubled run; the cost of the bug was a
    pipeline that never ran again.
    """
    if not started:
        return None
    age = (time.time() - started) / 60.0
    if age < -FUTURE_TOLERANCE_MIN:
        return 1e9
    return age


def claim(name):
    """Return 0 if this run may proceed, 1 if a previous one is still working.

    The fixer had this first because its runs are the longest, but a baseline run
    that overruns an hour would put two runs on the same ten empty rows: the same
    documents measured twice, and the later commit overwriting the earlier one.
    """
    s = load()
    key = "%s_started" % name
    limit = CLAIM_STALE_MIN.get(name, 60)
    age_min = claim_age_min(s.get(key))
    if age_min is None:
        age_min = 1e9
    if age_min < limit:
        print("%s busy - previous run started %d min ago (stale after %d min)"
              % (name, age_min, limit))
        return 1
    had_stale = bool(s.get(key))
    s[key] = time.time()
    save(s)
    print("%s claimed at %s" % (name, ist("%H:%M")))
    note("claim", "%s claimed the slot" % name)
    if name == "fixer":
        # A run that was killed never closed its record. Without this, _run_record("start")
        # overwrote it and the dead run's attempts, kept count and duration vanished - so the
        # report under-counted the day and chain.py judged the next run's productivity against a
        # record that had just been wiped. Archive it first.
        try:
            import json as _j
            _rp = os.path.join(HERE, "RUN.json")
            _prev = _j.load(open(_rp, encoding="utf-8"))
            if _prev.get("started") and _prev.get("ended") is None:
                _prev["ended_how"] = "killed - never released the slot"
                _prev["ended"] = _prev.get("ended") or "(never)"
                _hp = os.path.join(HERE, "RUN-HISTORY.json")
                try:
                    _hist = _j.load(open(_hp, encoding="utf-8"))
                except Exception:
                    _hist = []
                _hist.append(_prev)
                _j.dump(_hist[-60:], open(_hp, "w", encoding="utf-8"), indent=1)
        except Exception:
            pass
        _handoff("--run-start")
        _run_record("start")
    # A stale claim means the previous run ended WITHOUT releasing. That is a real failure -
    # on 16 Nov the fixer finished at 08:05 and left its slot held - and it used to be
    # silent: the next run simply took over and nobody could see a run had ended untidily.
    #
    # This note MUST come after the timestamp above. trace.who() attributes a line to the
    # cron whose slot is newest, and a stale slot is by definition the oldest - written
    # before the refresh, the note was credited to whichever OTHER cron had run most
    # recently. Tested: it said "classifier" for a fixer slot.
    if had_stale:
        note("stale-claim",
             "%s slot was stale (%.0f min) - the previous run ended without releasing it"
             % (name, age_min))

    # The claim leaves its own line in RUN-LOG.md, written by the tool rather than by the
    # run. "Commit ROUND.json immediately" is an instruction, and an instruction is a
    # promise: the fixer ran for seventeen minutes on 12 Nov and left no commit at all, so
    # from outside it was impossible to tell a working run from one that never started.
    # A tool that writes the evidence cannot forget to.
    try:
        log = os.path.join(HERE, "RUN-LOG.md")
        if os.path.exists(log):
            with open(log, "a", encoding="utf-8") as f:
                f.write("| %s | %s | slot claimed - %s running |\n"
                        % (ist("%d %b %H:%M"), name, name))
    except Exception:
        pass
    return 0


def _attempts_this_run():
    """How many attempt lines the trace holds since the last claim."""
    path = os.path.join(HERE, "TRACE.md")
    if not os.path.exists(path):
        return 0
    n, seen_claim = 0, False
    for line in open(path, encoding="utf-8"):
        if "| claim |" in line:
            n, seen_claim = 0, True
        elif seen_claim and "| attempt |" in line:
            n += 1
    return n


def release(name, force=False):
    """Release a slot, and for the fixer, refuse to waste it.

    WHY THIS IS A REFUSAL AND NOT A SENTENCE
      The brief has said since 13 Nov, twice, that an attempt recorded as 'error' is not a reason
      to stop - once as a restructured STEP 9 and once as an explicit paragraph. Sixteen runs
      later the average is 1.1 attempts against a target of 3, fourteen of them did exactly one,
      and the slot is used six minutes of forty-five. Instructions are promises; this is the check
      that makes it one.

      A fixer run that has been going less than 30 minutes and has recorded fewer than two
      attempts is not finished, whatever it thinks. It still holds the slot, the brief still tells
      it to go back to STEP 2, and releasing now hands 39 idle minutes to nobody.

      30 and not 25 (16 Nov): the ask was for one run to work continuously for as long as it can
      rather than have its time cut into small pieces. A cap is only worth having if the run can
      reach it - at 25 minutes a run that spent ten of them on a soffice timeout had barely begun
      its second attempt. 30 leaves room for two real attempts, and the heartbeat in attempt.py
      means a run that stops after this refusal frees the slot 45 minutes after its last attempt
      rather than 45 after its start.

      --force is the way out, and it exists for the honest cases: the build is broken, Drive is
      blocked, the class list is empty. It prints a line into RUN-LOG.md so a forced release is
      visible rather than silent.
    """
    s = load()
    started = s.get("%s_started" % name) or 0
    # A finished round is not a wasted slot. When no class is still OPEN the run's work is done
    # and it must be able to release and close - otherwise this check would block the only exit
    # from the fix phase, which is a worse bug than the one it fixes.
    any_open = False
    for fp in class_files():
        for line in open(fp, encoding="utf-8"):
            if not line.startswith("| ") or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and "OPEN" in cells:
                any_open = True
                break
        if any_open:
            break

    if name == "fixer" and started and not force and s.get("phase") == "fix" and any_open:
        age = claim_age_min(started) or 0.0
        done = _attempts_this_run()
        # NO CLOCK. ONE ATTEMPT, THEN THE WORK DECIDES.
        #
        # This has now been wrong twice: first `age < 30 and done < 2` - three attempts bought an
        # early exit at 22 minutes - then `age < 40`, which is a cap, and a cap is a number to
        # stop at. The instruction is that a run works continuously for as long as the system
        # allows, and the system's own limit is the only thing that should end it. So there is no
        # minute count here at all.
        #
        # The one floor left is that a run may not release having recorded nothing. That is not a
        # short run, it is a wasted slot. The round-finished bypass above still applies, and
        # --force remains for the honest cases - a broken build, a blocked Drive, an empty list.
        if done < 1:
            print("refused: this run has recorded no attempt at all.")
            print("An attempt is a patch, a measurement and a line in ATTEMPTS.json - or an honest")
            print("'error' because the root cause was not found. Any of those counts.")
            print("Nothing recorded means the slot produced nothing. Go back to STEP 2, take an")
            print("OPEN class and do one.")
            print("If you genuinely cannot - the build is broken, Drive is blocked, the class list")
            print("is empty - release with: round.py --release-fixer --force")
            return 1
        print("fixer: releasing after %d minute(s) with %d attempt(s)" % (age, done))
    s["%s_started" % name] = 0
    save(s)
    if name == "fixer":
        _handoff("--run-end", "forced" if force else "released")
        _run_record("end")
    if force:
        try:
            log = os.path.join(HERE, "RUN-LOG.md")
            with open(log, "a", encoding="utf-8") as f:
                f.write("| %s | %s | slot FORCED released - see INCIDENTS.md for why |\n"
                        % (ist("%d %b %H:%M"), name))
        except Exception:
            pass
        print("%s released (forced)" % name)
    else:
        print("%s released" % name)
    return 0


def main(argv):
    # Every cron calls this first. A hint here reaches all four on every run, which
    # is cheaper than hoping four prompts stay in step. stderr, because --phase must
    # print one bare word on stdout for $(...).
    sys.stderr.write("interface: tools/p2w-bench/TOOLBOX.md - read the sections for the tools you use\n")
    sys.stderr.write("brief:     tools/p2w-bench/{BASELINE,CLASSIFIER,FIXER}-BRIEF.md - yours is your instruction set\n")
    s = load()

    if "--apk-status" in argv:
        # "may ship" only when every round is finished and nothing was shipped yet.
        if s.get("phase") != "done":
            print("phase is %s - not done" % s.get("phase"))
            return 1
        done = s.get("apk_shipped") or ""
        if done:
            print("already shipped %s - nothing to do" % done)
            return 1
        print("may ship - all %s rounds done, nothing shipped yet" % s.get("rounds_total"))
        return 0

    if "--mark-apk-shipped" in argv:
        v = argv[argv.index("--mark-apk-shipped") + 1] if "--mark-apk-shipped" in argv else "yes"
        s["apk_shipped"] = v
        save(s)
        print("apk marked shipped: %s" % v)
        return 0

    if "--heartbeat" in argv:
        # A run that is alive must be able to say so between attempts.
        #
        # The only heartbeat was inside attempt.py, so a run doing a twenty-five minute corpus
        # ratchet looked exactly like a run that had died: the claim aged, and the stale check
        # could hand the slot to someone else while the first run was still working. That is why
        # the window had to stay at 45 minutes - long enough to cover the longest silent stretch,
        # which meant a genuinely dead run also blocked the slot for 45.
        #
        # With this, a live run can refresh between attempts, the window can come down, and a
        # dead run stops costing most of an hour.
        s2 = load()
        key = "fixer_started"
        if not s2.get(key):
            print("no fixer claim to refresh")
            return 1
        s2[key] = time.time()
        # WHAT IT IS DOING, NOT JUST THAT IT IS ALIVE.
        #
        # A heartbeat with no description answers "is the process up", which is not the question
        # anyone asks. The question is "is work happening". A run measuring 213 documents and a run
        # wedged in a loop look identical from a claim timestamp - both are silent, both refresh
        # if they refresh at all. So the beacon carries the activity and when it started.
        doing = ""
        if "--doing" in argv:
            doing = argv[argv.index("--doing") + 1]
        if doing:
            s2["fixer_doing"] = doing
            s2["fixer_doing_since"] = time.time()
        s2["fixer_last_beat"] = time.time()
        save(s2)
        if doing:
            print("fixer claim refreshed - doing: %s" % doing)
        else:
            print("fixer claim refreshed")
        return 0

    if "--claim-fixer" in argv:
        return claim("fixer")

    if "--release-fixer" in argv:
        return release("fixer", force="--force" in argv)

    # Written out rather than generated, so the flag is greppable in the source.
    # A tool that checks the interface reference against the code cannot see a
    # flag built from a format string, and a reference it cannot check is a
    # reference that drifts.
    if "--claim-baseline" in argv:
        return claim("baseline")

    if "--release-baseline" in argv:
        return release("baseline")

    if "--claim-classifier" in argv:
        return claim("classifier")

    if "--release-classifier" in argv:
        return release("classifier")

    if "--phase" in argv:
        print(s["phase"])
        return 0

    if "--force-round" in argv:
        n = int(argv[argv.index("--force-round") + 1])
        s["round"] = n
        s["phase"] = "measure"
        # Every claim is cleared. A slot left claimed by the round that just ended reads
        # as "a run is working" to the first run of the new round, which then sits out for
        # up to 45 minutes doing nothing - a phase that looks busy and is idle.
        for k in ("fixer_started", "baseline_started", "classifier_started"):
            s[k] = 0
        save(s)
        print("round forced to %d, phase measure, all slots released" % n)
        return 0

    if "--remeasure" in argv:
        """Put the round back into measure WITHOUT closing it.

        WHY THIS EXISTS. The only way out of phase 'fix' was --close-round, which archives the
        round and blanks every score. That is right when a round is finished and wrong when the
        engine itself changed underneath it: on 13 Nov three commits fixed ten defects - seven in
        the checker and three in DocxWriter.faceName - and the engine id changed with them, so
        every row in BASELINE.md and every class in DEFECT-CLASSES.md now describes an engine
        that no longer exists. Fixing against that list would be fixing against a ghost.

        Re-measuring is not a new round. The round number, the attempts ledger and the hypothesis
        ledger all stay; only the phase moves, so the baseline cron can re-measure the corpus on
        the engine that is actually in the tree. It is logged in RUN-LOG.md with the engine id,
        because "why did the phase go backwards" is a question someone will ask.
        """
        try:
            eng = subprocess.check_output(
                ["git", "log", "-1", "--format=%h", "--",
                 "app/src/main/java/com/kavopdf/app/engine/"],
                cwd=os.path.dirname(HERE), stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            eng = "unknown"
        s = load()
        was = s.get("phase")
        s["phase"] = "measure"
        # All three, not just the baseline. Re-measuring means the classify and fix work
        # built on the old numbers is void too, so their slots must not stay held: a
        # classifier claim left over would make the classifier skip the very run it is
        # needed for.
        for k in ("fixer_started", "baseline_started", "classifier_started"):
            s[k] = 0
        s.setdefault("history", []).append(
            {"at": ist("%d %b %H:%M"), "phase": "measure", "round": s.get("round"),
             "why": "engine changed - re-measure before fixing"})
        save(s)
        print("phase %s -> measure (round %s kept)" % (was, s.get("round")))
        print("engine at HEAD for app/src/.../engine/: %s" % eng)
        print("the baseline cron will now re-measure the corpus on this engine")
        return 0

    if "--advance" in argv:
        phase = s["phase"]

        # fix does not advance. The only way out of fix is --close-round, which archives the
        # round, blanks every score and starts the next one. --apk-status returns 0 the
        # moment the phase reads done, so a single wrong --advance from fix would let the APK
        # cron publish with rounds 2 and 3 never run and nothing archived. Refuse it here
        # rather than trust every reader of every brief to know which of the two to call.
        if phase == "fix":
            print("refused: fix does not advance. Use --close-round, which archives the round,")
            print("blanks the scores and starts the next one. Advancing from fix to done would")
            print("ship the app with rounds 2 and 3 never run.")
            return 1

        # measure and classify may only hand over when their work is actually finished. The
        # gates are tools, not sentences in a brief: every phase transition passes through
        # this branch, so nothing downstream can skip the check by misreading an instruction.
        gate = {"measure": "measure_gate.py", "classify": "classify_gate.py"}.get(phase)
        if gate:
            path = os.path.join(HERE, gate)
            if not os.path.exists(path):
                print("refused: %s is missing, so %s cannot be proved finished" % (gate, phase))
                return 1
            r = subprocess.run([sys.executable, path], capture_output=True, text=True)
            if r.returncode != 0:
                print("refused: %s is not finished - the phase stays at %s" % (phase, phase))
                for line in (r.stdout or r.stderr).strip().splitlines():
                    print("  " + line)
                return 1

        i = PHASES.index(phase)
        if i < len(PHASES) - 1:
            s.setdefault("history", []).append(
                {"round": s["round"], "phase": s["phase"], "at": ist("%Y-%m-%d %H:%M")})
            s["phase"] = PHASES[i + 1]
            save(s)
        print(s["phase"])
        return 0

    if "--close-round" in argv:
        # A round closes from fix, and only when no class is still OPEN.
        #
        # Without this, --close-round worked from any phase: three calls from measure reach
        # round 3, set the phase to done, and --apk-status then answers "may ship" - an app
        # published with no measurement finished and nothing fixed. Tested before this
        # guard existed: measure, close, close, close, ship.
        if s["phase"] != "fix":
            print("refused: a round closes from fix, and the phase is %s." % s["phase"])
            print("Closing from here would archive a round whose fix phase never ran and start")
            print("the next one with nothing fixed. Three such calls reach done, and done is what")
            print("lets the app ship.")
            return 1

        still_open = []
        for path in class_files():
            for line in open(path, encoding="utf-8"):
                if not line.startswith("| "):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                # "OPEN" is a cell, not necessarily the last one - a column added to the
                # class table must not turn this gate into one that never fires.
                if len(cells) >= 3 and "OPEN" in cells:
                    still_open.append(cells[1])
        if still_open:
            print("refused: %d class(es) are still OPEN - the round is not finished."
                  % len(still_open))
            for c in still_open[:5]:
                print("  %s" % c)
            print("Fix them, or let the fixer park them with a reason, then close the round.")
            return 1

        total, scored = rows()
        # Archive the finished round so its numbers are never lost.
        if os.path.exists(BASE):
            shutil.copy(BASE, os.path.join(HERE, "ROUND-%d.md" % s["round"]))
        # Always write the archive, even when nothing was attempted. A round that
        # closed with zero attempts is a fact worth keeping - it means the fixer
        # never ran, or every class was already parked - and silence would hide it.
        if os.path.exists(ATTEMPTS):
            shutil.copy(ATTEMPTS, os.path.join(HERE, "ATTEMPTS-round-%d.json" % s["round"]))
        else:
            json.dump({}, open(os.path.join(HERE, "ATTEMPTS-round-%d.json" % s["round"]),
                               "w", encoding="utf-8"), indent=2)

        s.setdefault("history", []).append(
            {"round": s["round"], "phase": "closed", "scored": scored,
             "at": ist("%Y-%m-%d %H:%M")})

        if s["round"] >= s["rounds_total"]:
            s["phase"] = "done"
            save(s)
            print("round %d closed - all %d rounds done" % (s["round"], s["rounds_total"]))
            return 0

        # Reset for the next round: every score empty, so the baseline has work
        # to do again and the ratchet is the only thing that remembers the past.
        out = []
        # A missing BASELINE.md must not crash a round close - the archive and
        # the phase move still have to happen, or the pipeline is stuck forever
        # in a round it cannot leave.
        base_lines = open(BASE, encoding="utf-8").readlines() if os.path.exists(BASE) else []
        for line in base_lines:
            if line.startswith("| ") and not line.startswith("|---"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if cells and cells[0] and cells[0].lower() != "document":
                    out.append("| %s |  |  |  |  |  |" % cells[0])
                    continue
            out.append(line.rstrip("\n"))
        open(BASE, "w", encoding="utf-8").write("\n".join(out) + "\n")

        # A new round means new defects to find, so the class files are BLANKED.
        #
        # They used to survive the boundary, and that made rounds 2 and 3 fake. The
        # fixer marks a class FIXED when its number improves; the next round then
        # inherits a file that already says everything is FIXED, --close-round finds no
        # OPEN row, and the round closes instantly having done nothing. Three such rounds
        # reach done and the app ships on one round of work dressed as three.
        #
        # Blanking forces the classifier to write a fresh classification from the new
        # measurement, and classify_gate refuses to advance until it has - so a round
        # cannot reach fix, let alone close, without a class list built for that round.
        # The file is emptied rather than deleted, so its absence is never mistaken for
        # "no defects found".
        for cf in (CLASSES_B, CLASSES):
            if os.path.exists(cf):
                open(cf, "w", encoding="utf-8").write(
                    "# Defect classes - this round has not been classified yet\n\n"
                    "The classifier writes this file. round.py blanks it when a round "
                    "closes, so a new round cannot inherit the previous round's verdicts.\n")

        if os.path.exists(ATTEMPTS):
            os.remove(ATTEMPTS)

        s["round"] += 1
        s["phase"] = "measure"
        s["started"] = time.time()
        s["fixer_started"] = 0
        s["baseline_started"] = 0
        s["classifier_started"] = 0
        s["apk_shipped"] = ""
        save(s)
        print("round %d closed, round %d begins in phase measure" % (s["round"] - 1, s["round"]))
        return 0

    status(s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
