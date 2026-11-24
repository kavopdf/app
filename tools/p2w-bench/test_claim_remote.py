#!/usr/bin/env python3
"""test_claim_remote.py - the claim must read the REMOTE, never its own working file.

THE BUG THIS PINS
  round.py --claim-fixer commits ROUND.json and pushes it. When the push is refused it used to
  `git pull -q --rebase` and then `load()` - its own working file. On a working run that file is
  DIRTY (every tool in the directory writes ROUND.json/RUN.json), so the pull fails, `load()`
  returns the file this very call just wrote, `other` is the claim from seconds ago, its age is 0,
  and the run stands down from a slot nobody holds.

  Measured 24 Nov 18:59 IST, in a real fixer run: --claim-fixer printed
      "fixer busy - another run claimed and pushed first (no detail). Standing down."
  while `git show origin/main:tools/p2w-bench/ROUND.json` said `"fixer_started": 0`. The slot was
  free. The run only continued because a human-shaped reader disbelieved the tool.

  A second, quieter half: the old code printed "claimed at HH:MM" after a REJECTED push, so a run
  believed it held a slot the other fixer could not see. Two runs then edit the engine at once.

WHAT IS ASSERTED
  1. a rival claim on origin, recent      -> stands down (return 1)
  2. NO claim on origin, our own local    -> claims (return 0), and the claim is re-pushed
     claim is fresh (the bug)
  3. a rival claim on origin that is stale -> claims (return 0)
  4. origin equals the claim we just wrote -> claims (return 0); it is ours, not a rival's
  5. the claim never reaches origin        -> stands down (return 1), never "claimed at"

Run: python3 tools/p2w-bench/test_claim_remote.py
"""
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("round", os.path.join(HERE, "round.py"))
round_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(round_mod)


class Fake:
    """Stands in for sh(), load() and save() so the claim can be driven without a repository."""

    def __init__(self, local, remote, push_ok=True):
        self.local = local
        self.remote = remote
        self.push_ok = push_ok
        self.calls = []

    def sh(self, cmd, timeout=290):
        self.calls.append(cmd)
        if cmd.startswith("git show origin/main"):
            return 0, json.dumps(self.remote)
        if cmd.startswith("git fetch"):
            return 0, ""
        if "git push" in cmd:
            return (0, "") if self.push_ok else (1, "! [rejected] main -> main (fetch first)")
        if "git pull" in cmd:
            return 0, ""
        return 0, ""

    def load(self):
        return dict(self.local)

    def save(self, s):
        self.local.update(s)


def run_case(name, local, remote, push_ok, want, note=""):
    f = Fake(local, remote, push_ok)
    orig = (round_mod.sh, round_mod.load, round_mod.save, round_mod.note,
            round_mod._timeline, round_mod._run_record, round_mod._handoff)
    round_mod.sh = f.sh
    round_mod.load = f.load
    round_mod.save = f.save
    round_mod.note = lambda *a, **k: None
    round_mod._timeline = lambda *a, **k: None
    round_mod._run_record = lambda *a, **k: None
    round_mod._handoff = lambda *a, **k: None
    try:
        got = round_mod.claim("fixer")
    finally:
        (round_mod.sh, round_mod.load, round_mod.save, round_mod.note,
         round_mod._timeline, round_mod._run_record, round_mod._handoff) = orig
    ok = got == want
    print("  %-4s %-52s got %d want %d %s" % ("PASS" if ok else "FAIL", name, got, want, note))
    return ok


def main():
    now = time.time()
    fresh = now - 120          # 2 minutes ago
    stale = now - 60 * 60 * 6  # 6 hours ago
    ok = True
    print("claim reads origin, not its own working file:")

    # 1. a real rival, recent. Our own file holds nothing - that is what a fresh clone looks like,
    # and a rival's timestamp is a DIFFERENT float from anything this run wrote.
    ok &= run_case("rival claim on origin, 2 min old",
                   {"fixer_started": 0}, {"fixer_started": fresh}, True, 1)

    # 2. THE BUG. No claim on origin at all; our own fresh claim is in the local file.
    ok &= run_case("no claim on origin, our own fresh claim locally",
                   {"fixer_started": fresh}, {"fixer_started": 0}, True, 0,
                   "(the 24 Nov stand-down)")

    # 3. a rival that has gone stale
    ok &= run_case("stale rival claim on origin, 6 h old",
                   {"fixer_started": 0}, {"fixer_started": stale}, True, 0)

    # 4. origin already holds exactly what we wrote - it is ours
    ok &= run_case("origin equals the claim we just wrote",
                   {"fixer_started": fresh}, {"fixer_started": fresh}, True, 0,
                   "(identical value = ours)")

    # 5. the claim never lands
    ok &= run_case("push refused and no rival - must not claim",
                   {"fixer_started": fresh}, {"fixer_started": 0}, False, 1,
                   "(a claim nobody can see is not a claim)")

    print("\n  %s" % ("all cases agree" if ok else "FAILURES ABOVE - the claim is not fixed"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
