#!/usr/bin/env python3
"""
unmeasured.py - may a commit pass through a gap in the ratchet, and on what terms.

WHY THIS FILE EXISTS
  On 13 Nov the p2w instrument retired five checks and added two. 59 became 56, and
  every one of the 211 high-water marks had been taken by the instrument that no
  longer exists. Nothing had been re-measured under the new one.

  ratchet.py is right to refuse to call that a pass. But commit-gate.sh asked it one
  question - "did it exit 0" - and the answer was no, forever, for every commit. A
  guard that is always red is not a guard; it is a thing people learn to step over.
  The two ways out of that are both wrong: delete the guard, or teach the gate to
  ignore it. This file is the third way.

WHAT IT DECIDES
  ratchet.py says UNMEASURED (exit 3) and writes down exactly what it could not
  compare and why. This file reads that record and answers a narrower question:

      is this particular gap one that may be committed through, today?

  It may, only when ALL of these hold. Each one closes a different way of using a
  waiver as a way of never measuring:

  1. THERE IS A WAIVER FOR THIS INSTRUMENT.
     WAIVER.json exists, was written by --allow-stale, and names the check universe
     in force right now. A waiver signed under the 57-check instrument does not
     authorise a commit under the 56-check one: that is the drift it was about.

  2. THE WAIVER HAS A REASON.
     Non-empty. A waiver nobody can read is an anonymous green light, which is what
     --allow-stale used to produce when it discarded --reason.

  3. NOTHING BECAME UNMEASURED SINCE THE WAIVER.
     The current gap must be a subset of the gap that was signed for. Otherwise the
     stores moved after the decision and the decision is about a different tree.

  4. SOMETHING WAS ACTUALLY COMPARED.
     At least one document was compared against its mark under the live instrument.
     A waiver over a corpus where nothing at all was asked is not a gap in a
     ratchet, it is the absence of one, and this is the rule that stops "I ran the
     ratchet" from meaning "I ran the ratchet over nothing".

  5. THE EVIDENCE THAT CHANGED IS EVIDENCE FROM THIS INSTRUMENT.
     Every document whose row in RESULTS.jsonl differs from HEAD must be stamped
     with the live universe sha. This is the rule the old gate was missing: it asked
     only that the evidence files had CHANGED, so a fixer could restamp a row, or
     append a measurement made by a retired verifier, and satisfy it. A number
     produced by an instrument that no longer exists is not evidence about this
     engine.

  6. THE GAP IS NOT GROWING.
     No document that was compared at the last waiver may have become uncompared
     since. A gap that grows while being waived is not being paid down, it is being
     normalised.

  7. THE GAP HAS NOT BEEN CARRIED FOR MORE THAN THREE WAIVERS.
     After that, a measurement round is required before another engine commit. Three
     because commit-gate.sh already says a run does up to three attempts and commits
     between them, so three waivers is exactly one run's worth of commits; the next
     run has to have measured something. This is the deadline that stops the gap
     from being immortal, and it is derived from the pipeline's own shape rather
     than picked.

  Every rule is checked and every failure is printed with the documents that caused
  it. There is no --force. A waiver that cannot pass these seven is not a waiver,
  and the fix is to measure, which is what the gate was for in the first place.

USAGE
  python3 tools/p2w-bench/unmeasured.py           # the .docx half
  python3 tools/p2w-bench/unmeasured.py --txt     # the .txt half
  python3 tools/p2w-bench/unmeasured.py --max-carry 3

exits   0 the gap is recorded, bounded and paid for - a commit may proceed
        1 refuse; the reason and the documents are printed
        2 could not decide (no git, no ledger, no instrument) - refuse as well
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from instrument import live_universe  # noqa: E402

RESULTS = "RESULTS.jsonl"
RESULTS_TXT = "RESULTS-TXT.jsonl"


def ledger_paths(txt):
    suffix = "-TXT" if txt else ""
    return (os.path.join(HERE, "UNMEASURED%s.json" % suffix),
            os.path.join(HERE, "WAIVER%s.json" % suffix),
            os.path.join(HERE, "UNMEASURED-HISTORY%s.jsonl" % suffix))


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def history(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def latest_rows(text):
    """{doc: row} - the current row per document: the last one written.

    Last-seen, not the largest (round, engine) key, because that is the store's own
    contract: record.py documents that the file is written in measurement order and
    "the last one seen is the current one". Comparing keys would let the alphabet
    decide which of two measurements of one document is current, and on a store that
    mixes an engine id with a hash that decision is arbitrary.
    """
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        doc = e.get("doc")
        if doc:
            out[doc] = e
    return out


def signature(row):
    """What makes two measurements of one document the same measurement."""
    return (row.get("score"), row.get("total"),
            row.get("universe_sha") or "", row.get("universe_n"))


def head_rows(relpath):
    """The store as committed, or (None, why) when git cannot say."""
    try:
        out = subprocess.check_output(
            ["git", "-C", ROOT, "show", "HEAD:%s" % relpath],
            stderr=subprocess.DEVNULL, timeout=60, text=True)
    except subprocess.CalledProcessError as e:
        # 128 with nothing on stdout is "not in HEAD yet" - a store that has never
        # been committed. That is not an error: every row in it is new, and rule 5
        # then asks that every row be live, which is the right demand for a store
        # that has no history to be measured against.
        if "does not exist" in (e.stderr or "") or "exists on disk" in (e.stderr or ""):
            return {}, ""
        return None, "git show HEAD:%s failed" % relpath
    except Exception as e:
        return None, "git show HEAD:%s failed: %s" % (relpath, e)
    return latest_rows(out), ""


def main(argv):
    txt = "--txt" in argv
    max_carry = 3
    if "--max-carry" in argv:
        i = argv.index("--max-carry")
        if i + 1 < len(argv):
            try:
                max_carry = int(argv[i + 1])
            except ValueError:
                pass

    label = ".txt" if txt else ".docx"
    led_p, wvr_p, hist_p = ledger_paths(txt)
    relstore = "tools/p2w-bench/" + (RESULTS_TXT if txt else RESULTS)

    print("unmeasured %s" % label)

    ids, live_sha, err = live_universe(txt)
    if not ids:
        print("  REFUSED - %s" % err)
        print("  Without an instrument there is no universe to be unmeasured against.")
        return 2
    N = len(ids)

    led = load_json(led_p)
    wvr = load_json(wvr_p)
    hist = history(hist_p)
    problems = []

    # ---- 1. a waiver, for this instrument ----------------------------------
    if not led:
        print("  REFUSED - no %s" % os.path.basename(led_p))
        print("  Nothing has recorded what this run could not compare. Run ratchet.py.")
        return 2
    if not wvr or not wvr.get("waived"):
        problems.append(
            "no waiver - run: python3 tools/p2w-bench/ratchet.py%s --allow-stale "
            "--reason \"<what you are accepting>\""
            % (" --txt" if txt else ""))
    else:
        wsha = (wvr.get("instrument") or {}).get("sha")
        wN = (wvr.get("instrument") or {}).get("checks")
        if wsha != live_sha:
            problems.append(
                "the waiver was signed under a different instrument (sha %s, %s checks); "
                "this run's is sha %s, %d checks"
                % (wsha or "(none)", wN, live_sha, N))

    # ---- 2. the waiver has a reason ---------------------------------------
    if wvr and wvr.get("waived") and not (wvr.get("reason") or "").strip():
        problems.append("the waiver has no reason - an unreadable waiver is a shrug")

    # ---- 3. nothing became unmeasured since the waiver ---------------------
    cur_gap = set((led.get("not_compared") or {}).keys())
    if wvr and wvr.get("waived"):
        signed = set((wvr.get("not_compared") or {}).keys())
        appeared = sorted(cur_gap - signed)
        if appeared:
            problems.append(
                "%d document(s) became unmeasurable after the waiver was signed: %s"
                % (len(appeared), ", ".join(appeared[:6])
                   + (" ..." if len(appeared) > 6 else "")))

    # ---- 4. something was compared ----------------------------------------
    counts = led.get("counts") or {}
    compared = counts.get("compared") or 0
    if compared < 1:
        problems.append(
            "no document was compared under the live instrument - %d scored, %d "
            "compared. A waiver over a corpus where nothing was asked proves nothing "
            "about any document; measure at least one."
            % (counts.get("scored") or 0, compared))

    # ---- 5. the changed evidence came from this instrument -----------------
    live_docs = set()
    try:
        with open(os.path.join(ROOT, relstore), encoding="utf-8") as f:
            work = latest_rows(f.read())
    except Exception as e:
        problems.append("cannot read %s: %s" % (relstore, e))
        work = {}
    head, why = head_rows(relstore)
    if head is None:
        problems.append("cannot tell which rows are new (%s)" % why)
    elif work:
        changed = sorted(d for d, row in work.items()
                         if d not in head or signature(row) != signature(head[d]))
        stale_rows = sorted(d for d in changed
                            if (work[d].get("universe_sha") or "") != live_sha)
        live_docs = set(changed) - set(stale_rows)
        if not changed:
            problems.append(
                "no row in %s differs from HEAD - the engine moved and no measurement "
                "did" % relstore)
        elif stale_rows:
            problems.append(
                "%d row(s) changed since HEAD without being measured by the live "
                "instrument (sha %s): %s"
                % (len(stale_rows), live_sha,
                   ", ".join("%s (%s/%s, sha %s)"
                             % (d, work[d].get("score"), work[d].get("total"),
                                work[d].get("universe_sha") or "(none)")
                             for d in stale_rows[:5])
                   + (" ..." if len(stale_rows) > 5 else "")))

    # ---- 6. the gap is not growing ----------------------------------------
    same = [h for h in hist if h.get("instrument") == live_sha]
    if len(same) >= 2:
        prev = set(same[-2].get("not_compared_docs") or [])
        grew = sorted(cur_gap - prev)
        if grew:
            problems.append(
                "%d document(s) were compared at the last waiver and are not now: %s"
                % (len(grew), ", ".join(grew[:6])
                   + (" ..." if len(grew) > 6 else "")))

    # ---- 7. the gap has not been carried too long -------------------------
    carried = len(same)
    if carried > max_carry:
        problems.append(
            "the gap has been carried for %d waivers under this instrument (limit %d). "
            "A measurement round is required before another engine commit: the same "
            "documents cannot be waived indefinitely."
            % (carried, max_carry))

    # ---- the answer --------------------------------------------------------
    total_scored = counts.get("scored") or 0
    print("  instrument            : %d checks (sha %s)" % (N, live_sha))
    print("  gap recorded          : %d of %d document(s) not compared"
          % (len(cur_gap), total_scored))
    print("  compared              : %d" % compared)
    print("  measured in this tree : %d document(s) stamped live" % len(live_docs))
    print("  waivers carried       : %d of %d" % (carried, max_carry))
    if wvr and wvr.get("reason"):
        print("  reason given          : \"%s\"" % wvr["reason"])

    if problems:
        print("")
        print("  REFUSED - the gap may not be committed through:")
        for p in problems:
            print("      %s" % p)
        print("")
        print("  NO COMMIT. Either measure what is named above under the live")
        print("  instrument, or revert the engine. The ratchet is not being ignored")
        print("  here; it has said it was not asked, and this says so was the waiver.")
        return 1

    print("")
    print("  WAIVED - %d of %d document(s) were not compared and this run says so."
          % (len(cur_gap), total_scored))
    print("  %d were compared under the live instrument, and %d of the rows that moved"
          % (compared, len(live_docs)))
    print("  in this tree were measured by it. The gap is recorded, not closed; the")
    print("  next engine commit must not enlarge it, and after %d waivers it must be"
          % max_carry)
    print("  measured before another engine commit is allowed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
