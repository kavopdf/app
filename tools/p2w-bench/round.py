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
# THE LIVE MEASUREMENT. BASE is the retired markdown table; nothing writes it any more, so archiving
# and blanking it archived and blanked nothing. The round's numbers live here now.
RANK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "benchmarks", "RANKING.csv")
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
    # THE .txt CLASSES LIVE IN A SUBDIRECTORY, and this looked in the wrong one for as long as the
    # file has existed - so --close-round has never seen a single .txt class. Found in the final audit
    # by printing what class_files() actually returns instead of assuming it was right.
    txt = os.path.join(HERE, "txt", "DEFECT-CLASSES-TXT.md")
    if not os.path.exists(txt):
        txt = os.path.join(HERE, "DEFECT-CLASSES-TXT.md")   # the old flat location, if it ever returns
    if os.path.exists(txt):
        out.append(txt)
    # THE GOOGLE TABLE TOO, AND THIS IS THE ONE THAT MATTERS MOST.
    #
    # Without it, --close-round judged a round finished on the .docx and .txt classes alone - both of
    # which come from a soffice render - while 53 documents still failed `32_stroke_lines` in Google.
    # The round would close, the pipeline would move on, and the largest block in the corpus would
    # never be fixed. Found in the final audit, not by a run failing.
    google = os.path.join(os.path.dirname(HERE), "..", "benchmarks",
                          "DEFECT-CLASSES-GOOGLE.md")
    google = os.path.normpath(google)
    if os.path.exists(google):
        out.append(google)
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
def _timeline(ev, detail=""):
    """Append one line to TIMELINE.jsonl - the record gaps.py reads.

    Every event carries an epoch float, because the whole point is to measure the distance
    between two of them. A run that stopped for five minutes in the middle and a run that
    stopped for five at the end look the same in a claim timestamp; they do not look the same
    here, because there is a line either side of the gap.
    """
    import json as _j
    try:
        rec = {"t": time.time(), "ist": ist("%H:%M:%S"), "ev": ev, "d": detail}
        with open(os.path.join(HERE, "TIMELINE.jsonl"), "a", encoding="utf-8") as f:
            f.write(_j.dumps(rec) + "\n")
    except Exception:
        pass


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
# FIXER 20 -> 10. The window must exceed the longest silent stretch a live run can produce, or a
# working run loses its claim mid-render. The longest single tool call is 290 s (4.8 min) and the
# model may think for a few minutes before the next one, so 10 covers a 290 s call plus five minutes
# of thought. Twenty was chosen when the age meant "time since start", where a dead run blocked the
# slot for twenty minutes; now that the age means "time since last activity", the window is purely a
# safety margin and can be as small as that margin allows.
CLAIM_STALE_MIN = {"fixer": 10, "baseline": 45, "classifier": 20}


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


def _pending_count():
    """How many items pending.py lists, or 0 when the gate is clear.

    Run as a subprocess rather than imported: pending.py is the single authority on what is
    outstanding and duplicating its logic here is how two answers to one question start.
    """
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "pending.py")],
                           capture_output=True, text=True, timeout=60)
        for line in (r.stdout or "").split("\n"):
            m = re.match(r"PENDING \((\d+)\)", line.strip())
            if m:
                return int(m.group(1))
        return 0
    except Exception:
        # A gate that cannot be read must not become a lock that never opens.
        return 0


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


def sh(cmd, timeout=290):
    """Run a shell command from the repo root. Returns (returncode, stdout+stderr).

    THIS FUNCTION DID NOT EXIST AND THE GUARD THAT CALLED IT SILENTLY DID NOTHING.
    The auto-revert below calls `sh("git checkout <claim> -- .../engine/")` so that an engine
    change with no kept attempt goes back to the state the slot was claimed in. There was no
    `sh` in this file - it is defined in step.py, repro.py and gate.py, and this module imported
    only shutil and subprocess - so the call raised NameError, the bare `except Exception` around
    it printed a one-line warning, and the release carried on. Measured 19 Nov in the 00:58 run's
    own report: "round.py --release-fixer printed could not check the engine against the attempt
    ledger - NameError: name 'sh' is not defined. The auto-revert guard therefore did not run."

    A guard that has never once run is worse than no guard, because the run reads its silence as
    a pass. Found by the fixer, not by me, and fixed here.
    """
    try:
        # The repo root, from this file's own location - round.py already derives RANK the
        # same way two levels up, and it has no ROOT constant to borrow.
        root = os.path.dirname(os.path.dirname(HERE))
        r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 1, str(e)


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

    # THE AGE THAT MATTERS IS TIME SINCE THE RUN LAST DID ANYTHING, NOT TIME SINCE IT STARTED.
    #
    # This read <slot>_started, which is stamped once at claim and never refreshed. So a run that
    # had been working productively for twenty minutes read as STALE to the next slot, which took
    # the claim and started editing the same files. That is not a theory: on 17 Nov a slot read
    # DocxWriter at 9f7a094, another slot committed a 218-line engine fix at cf2f9c6, and the first
    # slot's whole-file commit silently reverted it. Two runs on one tree, and nothing reported an
    # error.
    #
    # attempt.py's heartbeat already wrote <slot>_last_beat for exactly this reason, and its own
    # docstring says the stamp makes the age mean "how long since this run last did anything" - but
    # nothing ever read it. The fix was written and the reader was not updated.
    #
    # The timeline file is the third and cheapest witness: EVERY run-facing tool appends a line to
    # it on entry, so its mtime is the last moment the run touched anything at all. No extra write,
    # no lock, no cost. Taking the newest of the three is the honest answer to "is anyone home".
    if not s.get(key):
        # NO CLAIM AT ALL. Activity must not be consulted here: the timeline is written by every
        # tool, so after a release its mtime is always recent, and taking it as the claim's age made
        # a free slot read as busy for ever - the slot could be released and never claimed again.
        # Caught by test D: release, then claim, then "busy - last activity 0 min ago".
        age_min = 1e9
    else:
        newest = s.get(key) or 0
        for other in ("%s_last_beat" % name, "%s_doing_since" % name):
            newest = max(newest, s.get(other) or 0)
        try:
            # READ THE LAST LINE'S STAMP, NOT THE FILE'S MTIME.
            # The fixer's prompt makes every run execute `git checkout -- tools/p2w-bench/` before it
            # does anything, and that checkout rewrites every tracked file in the directory - so
            # TIMELINE.jsonl's mtime becomes "now" even for a run that then died without doing a thing.
            # Found by the 04:36 run in its own words: "round.py --claim-fixer read 'last activity 0
            # min ago' because the mandatory git checkout rewrites TIMELINE.jsonl and refreshes the very
            # mtime the staleness check reads. The true last event in that file is 03:36:40."
            #
            # Both directions are wrong with an mtime: a dead run looks alive for ever, so its slot is
            # never reclaimed and the pipeline stalls. The content carries the real time. The key is
            # "t" - a float epoch, written by beacon.py as {"t": ..., "ist": ..., "ev": ...}.
            # THE TIMELINE CANNOT TELL WHO IS ALIVE, SO IT IS NOT READ HERE.
            #
            # Every tool writes a beat to it - attempt.py, report.py, classpick.py, and every tool a person or
            # another cron runs outside this slot. Its last stamp therefore says "something ran recently", not
            # "the fixer is working", and reading it made the slot unclaimable whenever any other tool had
            # touched the repository.
            #
            # Found by the final audit: status.py said "LIKELY DEAD - the claim is 126 minutes old" while
            # --claim-fixer said "fixer busy - last activity 4 min ago", because four minutes earlier a
            # verification run had written a beat. Two tools, one state, opposite answers - and the one that
            # gates the work was the wrong one.
            #
            # The explicit fields ARE per-run: attempt.py's heartbeat writes <name>_last_beat and
            # <name>_doing_since for the run holding the slot, and those are read above. That is the evidence.
            _tl = None
        except Exception:
            pass
        age_min = claim_age_min(newest)
        if age_min is None:
            age_min = 1e9
    if age_min < limit:
        print("%s busy - last activity %d min ago (stale after %d min)"
              % (name, age_min, limit))
        return 1
    had_stale = bool(s.get(key))
    s[key] = time.time()
    save(s)
    print("%s claimed at %s" % (name, ist("%H:%M")))
    note("claim", "%s claimed the slot" % name)
    _timeline("claim", "%s claimed the slot" % name)
    if name == "fixer":
        # THE ENGINE THE SLOT WAS CLAIMED ON, RECORDED LIVE.
        #
        # The release guard READ `fixer_engine_at_claim` and NOTHING EVER WROTE IT, so the field
        # held a fossil. On 19 Nov it still said 2945cb0 - a commit older than the previous run's
        # kept fix - and the guard's `git checkout 2945cb0 -- engine/` stripped that fix out of the
        # tree on every release. It printed a cheerful "reverted: the engine changed this run" and
        # the run's own work was gone. Recording it here is the other half of that guard.
        try:
            _eng = sh("git log -1 --format=%h -- "
                      "app/src/main/java/com/kavopdf/app/engine/", timeout=60)[1].strip()
            if _eng:
                s["fixer_engine_at_claim"] = _eng
                save(s)
        except Exception:
            pass
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

    THE COMMIT GATE COMES FIRST, AND IT IS NOT BYPASSED BY --force. No commit may land, for the
    .docx or the .txt, unless the whole corpus has been measured with the engine as it stands and
    no document got worse. A run that is trying to release while regress.py refuses is a run about
    to hand back an engine change nobody measured - and --force exists for a broken build, not for
    an unmeasured one. Verified 19 Nov: the git pre-commit hook aborts the commit itself, so this
    is the second of three locks rather than the only one.

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

    if name == "fixer" and started and s.get("phase") == "fix" and any_open:
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
        # TWO AGENTS, OR THE SLOT IS NOT SPENT. The brief says deploy two every run; a rule that
        # only lives in a brief is a rule a tired run skips. On 19 Nov the fixer deployed one agent,
        # made one attempt, got to 46 of 213 and reported zero documents improved - and one of those
        # three would have saved the run. The agents are the part that still produces something when
        # the run's own idea fails.
        try:
            _rr = json.load(open(os.path.join(HERE, "RUN.json"), encoding="utf-8"))
        except Exception:
            _rr = {}
        _agents = len((s.get("fixer") or {}).get("agents") or []) or \
                  len((_rr.get("agents") or []))
        # A FORCE RELEASE WITH NO AGENTS NEEDS A BLOCKER FROM TODAY, UNRESOLVED.
        if _agents < 2 and force:
            _blk = os.path.join(HERE, "BLOCKERS.md")
            _txt = ""
            try:
                for _line in open(_blk, encoding="utf-8"):
                    _l = _line.strip()
                    if not _l.startswith("| ") or _l.startswith("|---"):
                        continue
                    if "what I was doing" in _l or "the obstacle" in _l:
                        continue
                    if "resolved" in _l.lower():
                        continue
                    if time.strftime("%Y-%m-%d") not in _l:
                        continue
                    _txt += _l.lower() + "\n"
            except Exception:
                pass
            _why = ("broken build", "build broken", "drive blocked", "blocked drive",
                    "no findings", "empty list", "cannot reach drive")
            if not any(w in _txt for w in _why):
                print("refused: %d agent(s) with --force, and no unresolved blocker from today." % _agents)
                print("'Budget gone' is not a blocker - it is what happens when the two agents the")
                print("brief asks for in the first ten minutes are deployed last, or not at all.")
                print("Deploy them, or write a real blocker into BLOCKERS.md.")
                return 1
        if _agents < 2 and not force:
            print("refused: this run deployed %d agent(s). The brief requires TWO every run." % _agents)
            print("Two angles working for the whole slot is two more than a run that works alone, and")
            print("their findings land even when this run's own idea does not. Deploy them, then work")
            print("your own third angle - and do not wait for them.")
            print("If a genuine blocker stopped both (no findings to answer, budget gone), say so in the")
            print("report and release with --force.")
            return 1
        # --force MUST WORK HERE, because the message below tells the run to use it.
        # It did not: this branch had no `and not force`, so a run that claimed the slot and then
        # did nothing could never release it - it had to wait out the stale window, and the
        # next run lost its first ten minutes to a slot nobody was using. Found by the final
        # audit, which ran the command the error message recommends and watched it fail.
        if done < 1 and not force:
            print("refused: this run has recorded no attempt at all.")
            print("An attempt is a patch, a measurement and a line in ATTEMPTS.json - or an honest")
            print("'error' because the root cause was not found. Any of those counts.")
            print("Nothing recorded means the slot produced nothing. Go back to STEP 2, take an")
            print("OPEN class and do one.")
            print("If you genuinely cannot - the build is broken, Drive is blocked, the class list")
            print("is empty - release with: round.py --release-fixer --force")
            return 1

        # WORK LEFT IS NOT A REASON TO STOP.
        #
        # A run that released after one attempt handed back a slot the scheduler would not fill for
        # up to an hour, and the next run spent its first thirteen minutes reading and building
        # before it touched the work. Measured on 17 Nov: six runs, gaps of 8, 8, 51, 56 and 23
        # minutes, roughly half of every day idle, and the same setup paid twenty-four times.
        #
        # pending.py is the gate and it already knows whether anything is outstanding. If it is, the
        # run is not finished, whatever it thinks - and the platform's own limit is what ends it, not
        # the run's guess about how long it has worked. A killed run frees the slot ten minutes after
        # its last activity, so this cannot wedge: the slot always comes back.
        #
        # --force still bypasses everything, and the round-finished bypass above still applies.
        # AN ENGINE CHANGE OUTSIDE A KEPT ATTEMPT IS NEVER MEASURED, SO IT MUST NOT SHIP.
        #
        # The ratchet measures what an attempt says it kept. A run that edits the engine, records
        # 'reverted' and commits anyway puts the change into the tree with nothing comparing it to
        # the corpus. Measured 17 Nov: a run recorded '1 attempt, 0 kept' and committed a folio rule
        # that regressed seventy documents - 392_statistical_console_output went 1.61 -> 28.39 - and
        # nothing in the pipeline said a word. The corpus number moved, the baseline did not, and
        # the next run inherited an engine nobody had measured.
        #
        # step.py records the engine hash when the slot is claimed. If the engine differs now and
        # the attempts this run recorded no 'kept', the run is holding an unmeasured change: revert
        # it or prove it. --force still bypasses.
        try:
            import json as _j
            import subprocess as _sp
            _start = (load().get("fixer_engine_at_claim") or "").strip()
            _root = os.path.normpath(os.path.join(HERE, "..", ".."))
            # THE ENGINE'S IDENTITY INCLUDES THE WORKING TREE. `git log -1 --format=%h` is the HEAD
            # commit, so an UNCOMMITTED engine edit left _now unchanged and this guard could not see
            # it at all - which is precisely the change it exists to catch. The same defect was
            # found in screen.py's cache stamp on 18 Nov and fixed there; this is the other half.
            _now = _sp.run(["git", "log", "-1", "--format=%h", "--",
                            "app/src/main/java/com/kavopdf/app/engine/"],
                           cwd=_root, capture_output=True, text=True).stdout.strip()
            _dirty = _sp.run(["bash", "-lc",
                              "{ git diff -- app/src/main/java/com/kavopdf/app/engine/; "
                              "git diff --cached -- app/src/main/java/com/kavopdf/app/engine/; } | sha1sum"],
                             cwd=_root, capture_output=True, text=True).stdout.strip().split()
            _dirty = _dirty[0] if _dirty else ""
            if _dirty and _dirty != "da39a3ee5e6b4b0d3255bfef95601890afd80709":
                _now = "%s+%s" % (_now, _dirty[:10])
            _kept = False
            # ASK THE STATE RECORD FIRST. benchmarks/STATE.json now carries the engine its numbers
            # were produced by, so "has this tree been measured" is a fact rather than an inference.
            # The ledger is the fallback for a state file written before that field existed.
            _have_state = False
            try:
                _st = _j.load(open(os.path.join(_root, "benchmarks", "STATE.json"), encoding="utf-8"))
                if (_st.get("engine") or "").strip():
                    _have_state = True
                    _kept = (_st.get("engine") or "").strip() == _now
            except Exception:
                pass
            # THE .TXT HALF HAS ITS OWN STATE RECORD, AND IT IS THE ONLY ONE THAT CAN PROVE A .TXT
            # CHANGE WAS MEASURED. benchmarks/STATE.json carries the engine the .docx table was
            # measured on; a run that changed TxtWriter leaves that field alone - correctly - so
            # `_have_state` was true and the ledger fallback below was never reached, and _kept
            # could never be true. Measured 20 Nov: the release refused a run that had kept two
            # measured attempts, and would have reverted both. STATE-TXT.json is written by the
            # .txt measurement and now records the engine it scored.
            if not _kept:
                try:
                    _stt = _j.load(open(os.path.join(HERE, "txt", "STATE-TXT.json"),
                                        encoding="utf-8"))
                    if (_stt.get("engine") or "").strip():
                        _have_state = True
                        _kept = (_stt.get("engine") or "").strip() == _now
                except Exception:
                    pass
            # WHEN THE STATE RECORD KNOWS THE ENGINE, IT IS THE ONLY AUTHORITY. The ledger is a
            # claim; STATE.json is the measurement. On 18 Nov the 15:30 run recorded its attempt as
            # kept and released, while benchmarks/RANKING.csv still read 68.82 - the measurement had
            # gone to /scratch/output and never reached the repository. A ledger override here let
            # exactly that ship. It no longer can: if the state file names an engine and the tree is
            # a different one, the tree has not been measured, whatever the ledger says.
            if not _have_state:
                try:
                    _att = _j.load(open(ATTEMPTS, encoding="utf-8"))
                    for _row in _att.values():
                        if (_row.get("last_engine") or "").strip() != _now:
                            continue
                        # THE LAST OUTCOME, NOT ANY OUTCOME. "kept" in outcomes was true for ever once
                        # a class had ever been kept, so a run that kept something last week and
                        # reverted this week passed the guard holding an unmeasured change. What
                        # matters is what the last attempt against THIS engine decided.
                        _outs = _row.get("outcomes") or []
                        if _outs and _outs[-1] == "kept":
                            _kept = True
                            break
                except Exception:
                    pass
            if _start and _now and _start != _now and not _kept:
                # REVERT IT, DO NOT REFUSE IT.
                #
                # Refusing kept the quality guarantee and cost the throughput: a refused release leaves
                # the slot held, the chain never fires, and the scheduler does not fill it for up to an
                # hour - so one unmeasured change ended a run and the next one paid its setup again
                # before touching any work. The change still must not ship unmeasured; that is the rule
                # the 17 Nov regression bought. So the engine goes back to the state it had when the
                # slot was claimed, the release proceeds, and the run carries on with its remaining
                # time instead of dying on a bookkeeping failure.
                _claim = (_start or "").split("+")[0].strip()
                _reverted = False
                # NOTHING TO REVERT WHEN THE TREE IS CLEAN. `_dirty` is the uncommitted engine
                # diff; when it is empty every engine change this run made is already committed
                # or already gone, and checking out an old commit then only DAMAGES what is
                # there. That is not hypothetical: on 19 Nov this branch checked out 2945cb0 and
                # removed the previous run's kept per-row separator stroke - 22 documents - from a
                # tree that held no unmeasured change at all.
                _clean_tree = (not _dirty) or _dirty == "da39a3ee5e6b4b0d3255bfef95601890afd80709"
                if _claim and len(_claim) >= 7 and not _clean_tree:
                    rc, out = sh("git checkout %s -- app/src/main/java/com/kavopdf/app/engine/ 2>&1"
                                 % _claim, timeout=60)
                    if rc == 0:
                        _reverted = True
                        print("reverted: the engine changed this run (%s -> %s) with no kept attempt."
                              % (_start, _now))
                        print("The engine is back at %s, the state it had when the slot was claimed."
                              % _claim)
                        print("COMMIT THAT REVERT before you release, or the release will not see a")
                        print("clean tree. Then carry on - you have the rest of the run.")
                if not _reverted:
                    print("refused: the engine changed this run (%s -> %s) and no attempt was kept." % (_start, _now))
                    print("The ratchet only measures what an attempt says it kept, so this change has never")
                    print("been compared against the corpus - and on 17 Nov exactly this shipped a rule that")
                    print("regressed seventy documents. Either revert the engine, or record the attempt that")
                    print("measured it. If you genuinely must ship it unmeasured: --force.")
                    return 1
                return 1
        except Exception as exc:
            print("warning: could not check the engine against the attempt ledger - %s: %s"
                  % (type(exc).__name__, exc))

        # --force IS THE WAY OUT OF THIS GATE, AND IT SAID SO WITHOUT HONOURING ITSELF.
        #
        # The refusal below printed "release with: round.py --release-fixer --force" and then
        # returned 1 whatever was passed, because force was only consulted after it. A run whose
        # pending rows are blockers it cannot fix - the watchdog writes them with "can I fix it:
        # no", and the cron half needs a person - was therefore wedged: it could not release, and
        # the slot only came back when its beacon went stale. Measured 20 Nov: two such rows, one
        # attempt, and a finished run that could not hand the slot on.
        left = _pending_count()
        if left > 0 and not force:
            print("refused: %d item(s) still pending. The slot is not spent while work is left." % left)
            print("A run that stops here hands back a slot the scheduler will not fill for up to an")
            print("hour, and the next run pays its setup again before touching the work. Keep going:")
            print("pending.py lists what is outstanding, in the order it should be taken.")
            print("If you genuinely cannot continue - the build is broken, the drive is blocked, the")
            print("class list is empty - release with: round.py --release-fixer --force")
            return 1
        if left > 0:
            print("fixer: releasing after %d minute(s) with %d attempt(s), FORCED past %d pending item(s)"
                  % (age, done, left))
        else:
            print("fixer: releasing after %d minute(s) with %d attempt(s), nothing pending" % (age, done))
    s["%s_started" % name] = 0
    # CLEAR THE BEACON WITH THE CLAIM, or the next reader is told a lie.
    #
    # --heartbeat stores what the run said it was doing in fixer_doing / fixer_doing_since, and
    # status.py reads those two fields to answer "what is happening". Release cleared the claim and
    # left the beacon, so after a release status.py printed:
    #
    #     verdict : IDLE        (correct - the slot is free)
    #     doing   : "claimed, gathering work" for 124 min
    #
    # Both lines were read off the same screen and they contradicted each other. That stale line is
    # what made the pipeline look busy while it was idle, and it is why a run was repeatedly judged
    # working when the slot was free and nothing was happening. A released slot has no activity to
    # describe, so it says nothing.
    s.pop("%s_doing" % name, None)
    s.pop("%s_doing_since" % name, None)
    save(s)
    _timeline("release", "%s released%s" % (name, " (forced)" if force else ""))
    if name == "fixer":
        _handoff("--run-end", "forced" if force else "released")
        # A FORCED RELEASE OF A DEAD CLAIM IS AN AUTOPSY, NOT A NORMAL END.
        #
        # The run that held this slot is not the one releasing it - a stale claim means the run
        # died and something else is clearing up. Its record has to be archived with that fact
        # attached, or the next run's _run_record("start") overwrites it and the dead run's
        # attempts vanish. Closing it with a normal "ended" would say it finished, which is the
        # one thing it did not do.
        if force:
            try:
                import json as _j
                _rp = os.path.join(HERE, "RUN.json")
                _prev = _j.load(open(_rp, encoding="utf-8"))
                if _prev.get("started"):
                    _prev["ended_how"] = "killed - slot cleared by a force release"
                    _prev["ended"] = _prev.get("ended") or "(never)"
                    _hp = os.path.join(HERE, "RUN-HISTORY.json")
                    try:
                        _hist = _j.load(open(_hp, encoding="utf-8"))
                    except Exception:
                        _hist = []
                    _hist.append(_prev)
                    _j.dump(_hist[-60:], open(_hp, "w", encoding="utf-8"), indent=1)
                    _timeline("killed", "dead claim cleared by force release")
            except Exception:
                pass
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
            # A RUN THAT HAS NOT CLAIMED YET IS STILL A RUN, AND IT IS THE ONE MOST LIKELY TO HANG.
            #
            # This returned 1 with nothing written, so the heartbeat the prompt puts immediately after the
            # clone was a no-op: the claim comes later, at STEP 0. A run that hung anywhere between starting
            # and claiming therefore left no beacon, no claim and no commit - which is exactly what the 07:57
            # run did on 21 Nov, and it swallowed the 09:50 fire while every status line said healthy.
            #
            # So: always write the beacon. Without a claim it cannot refresh the slot, but the timeline entry
            # is the only evidence that this run existed at all, and it is what gaps.py reads.
            _timeline("beat", "heartbeat before any claim: "
                      + (argv[argv.index("--doing") + 1] if "--doing" in argv else "started"))
            print("no fixer claim to refresh - beacon written anyway")
            return 0
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
        _timeline("beat", doing or "(no activity given)")
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
        # THE ROUND'S ACTUAL NUMBERS. Without this the archive held a file that had not been written
        # since the pipeline moved to RANKING.csv, and the real scores were never kept at all.
        if os.path.exists(RANK):
            shutil.copy(RANK, os.path.join(HERE, "ROUND-%d.csv" % s["round"]))
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

        # BLANK THE LIVE SCORES, OR THE NEXT ROUND MEASURES NOTHING.
        #
        # measure_gate counts a row as scored when share5 is a number, and the baseline cron only
        # measures rows that have no score. Leaving RANKING.csv full meant round 2 opened with every
        # document already "measured" against round 1's engine: the gate passed instantly, the
        # baseline cron found nothing to do, and rounds 2 and 3 were the first round wearing two
        # more hats. Measured 18 Nov: close-round touched BASELINE.md, which does not exist.
        #
        # share1..max_pt are blanked, not deleted, so the row keeps its identity and the next
        # measurement fills it. text_recall and chars_missing are left alone - they are content
        # facts about the document, not scores, and p2w.py rewrites them anyway.
        if os.path.exists(RANK):
            try:
                rl = open(RANK, encoding="utf-8").read().split("\n")
                keep = [rl[0]]
                for line in rl[1:]:
                    if not line.strip():
                        continue
                    c = line.split(",")
                    for i in range(4, min(12, len(c))):
                        c[i] = ""
                    keep.append(",".join(c))
                open(RANK, "w", encoding="utf-8").write("\n".join(keep) + "\n")
            except Exception as _e:
                print("warning: could not blank RANKING.csv (%s)" % type(_e).__name__)

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

    if "--reopen" in argv:
        # DONE IS NOT THE END. `rounds_total` rounds finish and the phase becomes `done`; from then on
        # every claim refuses and the pipeline stops for good. If the corpus is not actually perfect at
        # that point that is a silent stop - the app ships, the documents still fail, nothing says so.
        #
        # This reopens a round and refuses unless something is still failing. A reopen with nothing
        # failing would loop forever; a reopen with failures is the pipeline admitting it is not done.
        if s["phase"] != "done":
            print("refused: the phase is %s, not done - there is nothing to reopen." % s["phase"])
            return 1
        failing = 0
        try:
            import csv as _csv
            with open(RANK, encoding="utf-8") as f:
                for r in _csv.DictReader(f):
                    try:
                        if float(r.get("share5") or 0) > 1.0:
                            failing += 1
                    except ValueError:
                        pass
        except Exception:
            print("refused: %s cannot be read, so there is no evidence either way." % RANK)
            return 1
        txt_failing = 0
        try:
            import csv as _csv
            with open(os.path.join(HERE, "txt", "RANKING-TXT.csv"), encoding="utf-8") as f:
                for r in _csv.DictReader(f):
                    try:
                        if int(r.get("failed") or 0) > 0:
                            txt_failing += 1
                    except ValueError:
                        pass
        except Exception:
            pass
        if failing == 0 and txt_failing == 0:
            print("refused: nothing fails in either format - the pipeline is finished.")
            return 1
        s.setdefault("history", []).append(
            {"round": s["round"], "phase": "reopened", "docx_failing": failing,
             "txt_failing": txt_failing, "at": ist("%Y-%m-%d %H:%M")})
        s["round"] += 1
        s["rounds_total"] = max(s["rounds_total"], s["round"])
        s["phase"] = "measure"
        s["started"] = time.time()
        s["fixer_started"] = 0
        s["baseline_started"] = 0
        s["classifier_started"] = 0
        s["apk_shipped"] = ""
        save(s)
        print("reopened as round %d - %d .docx and %d .txt still fail"
              % (s["round"], failing, txt_failing))
        return 0

    status(s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
