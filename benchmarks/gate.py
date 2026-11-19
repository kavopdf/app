#!/usr/bin/env python3
"""gate.py -- the one command a cron runs. Produces STATE.json and a verdict.

THREE LAYERS, AND WHY EACH EXISTS
---------------------------------
1. p2w.py --validate       GROUND TRUTH. Sets displacement by construction on
                           synthetic pages and refuses to proceed if the
                           instrument cannot read it back. Nothing else may run
                           if this fails: a number from an unvalidated
                           instrument is not a measurement.

2. p2w.py --budget N       GLOBAL MEASUREMENT. Two axes per document --
                           where the ink sits (a tolerance sweep, whose shape
                           classifies the defect) and whether the characters
                           are the source's (multiset recall). Reproducible to
                           the digit across full environment wipes.

3. verify_txt.py           NAMED SEMANTIC CHECKS on the .txt. Carries what a
                           raster cannot: UTF-8 validity, page separators,
                           symbol counts, line order, page furniture.

LAYER POLICY, stated so no consumer has to guess
------------------------------------------------
* p2w is the authority for "how far off is this document". Its numbers are the
  ones to quote.
* verify_google.py (47 docx checks) and verify_txt.py (12 txt checks) are
  ADVISORY. They name a defect; they do not size it. A check that cannot fail
  is a bug in the check, not a pass -- the falsifiability gate already showed
  (The claim that 66 % of verify_google's passes were unfalsifiable has been
  WITHDRAWN - see benchmarks/LAYER-POLICY.md. It was measured on an earlier verifier,
  the harness had since broken, and when it was repaired all 47 checks proved able to
  fail. Falsifiable is the floor, not proof that a check is right.)
* No consumer may rank by a single number. Use signature + share@5px + max_pt.

THE RATCHET
-----------
gate.py compares the new RANKING.csv against the last committed one. A document
whose share@5px got worse is a REGRESSION, whatever else improved. Regressions
are reported, never silently accepted.

WHAT IT REFUSES TO DO
---------------------
* It will not measure with a failing gate.
* It will not drop a document it could not measure -- such a document becomes a
  MEASURE-ERROR row.
* It will not report a layer it did not run. A skipped layer is recorded as
  "not-run" with the reason, not as a pass.

    gate.py --budget 250          run everything, write STATE.json
    gate.py --ratchet-only        compare current RANKING.csv to the committed one
"""
import sys, os, json, csv, subprocess, time, argparse, glob, urllib.request
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
RANK = "/scratch/output/RANKING.csv"
STATE = "/scratch/output/STATE.json"
# THE RECORD THE REPOSITORY READS IS NOT THE FILE THIS SCRIPT WROTE.
#
# gate.py wrote /scratch/output/STATE.json, which is the delivered copy of a run and
# survives nothing; measure_gate.py, the ratchet reader and every brief read
# benchmarks/STATE.json in the repository. So the committed STATE.json could only ever
# be as new as the last time somebody copied it by hand - and on 18 Nov it was still
# carrying 17 Nov's ratchet ("improvements": []) while RANKING.csv beside it had a
# measured improvement in it. Two files in one commit disagreeing about the same run.
# Both are written now, from the same dict, in the same breath.
STATE_REPO = os.path.join(HERE, "STATE.json")
RAW = "https://raw.githubusercontent.com/kavopdf/app/main/benchmarks/RANKING.csv"
BENCH = "/scratch/work/p2w/repo/tools/p2w-bench"


def _write_state(S):
    """The delivered copy and the repository's copy, from one dict."""
    for p in (STATE, STATE_REPO):
        try:
            json.dump(S, open(p, "w"), indent=1)
        except Exception as e:
            log("STATE not written to " + p + ": " + str(e))

def sh(c, t=280):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def read_rank(path):
    out = {}
    if not os.path.exists(path): return out
    for r in csv.DictReader(open(path)):
        try: out[r["document"]] = float(r["share5"])
        except (ValueError, KeyError, TypeError): pass
    return out

def ratchet():
    """Compare current RANKING.csv against the committed baseline."""
    cur = read_rank(RANK)
    base = {}
    try:
        with urllib.request.urlopen(RAW, timeout=30) as f:
            tmp = "/scratch/work/_base.csv"
            open(tmp, "wb").write(f.read())
        base = read_rank(tmp)
    except Exception as e:
        return dict(status="no-baseline", reason=str(e)[:120],
                    regressions=[], improvements=[])
    reg, imp = [], []
    for d, v in cur.items():
        if d in base:
            delta = round(v - base[d], 2)
            if delta > 0.5:   reg.append(dict(document=d, was=base[d], now=v, delta=delta))
            elif delta < -0.5: imp.append(dict(document=d, was=base[d], now=v, delta=delta))
    return dict(status="compared", baseline_docs=len(base), current_docs=len(cur),
                regressions=sorted(reg, key=lambda x: -x["delta"]),
                improvements=sorted(imp, key=lambda x: x["delta"]),
                new_documents=sorted(set(cur) - set(base)),
                disappeared=sorted(set(base) - set(cur)))

def _find_round_json():
    """ROUND.json, wherever this copy of gate.py happens to be running from.

    The baseline cron copies gate.py into /scratch/work and runs it there, so
    dirname(__file__)/../tools/p2w-bench/ROUND.json resolves to /tools/p2w-bench/ROUND.json,
    which does not exist. S["round"] was then None on every real run, and measure_gate -
    which refuses a measurement whose round stamp does not match the machine's - would
    have refused for ever. The pipeline would have stopped at measure with the gate
    reporting success.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    # /scratch/work/base is where the BASELINE cron clones the repo, and it was missing
    # from this list. On 16 Nov the 00:46 baseline run measured all 213 documents and then
    # could not stamp the round, so measure_gate refused and the phase never advanced -
    # a complete measurement thrown away because a path was not searched.
    for c in (os.path.join(here, "..", "tools", "p2w-bench", "ROUND.json"),
              "/scratch/work/base/tools/p2w-bench/ROUND.json",
              "/scratch/work/p2w/repo/tools/p2w-bench/ROUND.json",
              "/scratch/work/cls/tools/p2w-bench/ROUND.json",
              "/scratch/work/fix/tools/p2w-bench/ROUND.json",
              os.path.join(here, "tools", "p2w-bench", "ROUND.json")):
        c = os.path.normpath(c)
        if os.path.exists(c):
            return c
    return None


def _expected_docs():
    """211 synthetic + the real documents, counted not assumed."""
    n = 211
    for d in ("/scratch/work/realworld",
              "/scratch/work/base/benchmarks/realworld",
              "/scratch/work/p2w/repo/benchmarks/realworld",
              "/scratch/work/cls/benchmarks/realworld",
              "/scratch/work/fix/benchmarks/realworld"):
        if os.path.isdir(d):
            real = len([f for f in os.listdir(d) if f.lower().endswith(".pdf")])
            if real:
                return n + real
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=250)
    ap.add_argument("--ratchet-only", action="store_true")
    a = ap.parse_args()
    os.makedirs("/scratch/output", exist_ok=True)

    if a.ratchet_only:
        r = ratchet(); print(json.dumps(r, indent=1)); return 0

    # WHICH ENGINE PRODUCED THESE NUMBERS. The file recorded everything about the run except the
    # one thing every later reader needs: what it measured. Without it, round.py's release guard
    # could only guess whether the tree it was about to ship had ever been ratcheted - it inferred
    # it from the attempt ledger's outcome list, which is a proxy, and on 18 Nov that proxy said
    # "reverted" about an engine that had been ratcheted cleanly. Record the identity, including
    # the uncommitted diff, and the guard can ask the exact question instead.
    def _engine_id():
        try:
            h = sh("git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/", 30)[1].strip()
            d = sh("{ git diff -- app/src/main/java/com/kavopdf/app/engine/; "
                   "git diff --cached -- app/src/main/java/com/kavopdf/app/engine/; } | sha1sum", 60)[1]
            d = (d.split() or [""])[0]
            if d and d != "da39a3ee5e6b4b0d3255bfef95601890afd80709":
                return "%s+%s" % (h, d[:10])
            return h or "unknown"
        except Exception:
            return "unknown"

    S = dict(ran_at=time.strftime("%Y-%m-%dT%H:%M:%S"), engine=_engine_id(), layers={})

    # ---- layer 1: ground truth ----
    # The instrument needs scipy, and on a fresh pod it is not installed yet: p2w.py
    # installs it itself, from inside the command this timeout covers. Measured: the pip
    # install alone took over 180 s on a cold pod, the validate call was killed at 180,
    # exit 124, and the gate reported "BLOCKED: instrument failed ground-truth validation"
    # - a verdict about the instrument for what was a slow package download. So the
    # dependency is satisfied here, with its own budget, before the timed validation.
    sh("python3 -c 'import scipy' || pip install -q scipy", 200)
    rc, out = sh("python3 " + HERE + "/p2w.py --validate", 240)
    gate_pass = (rc == 0)
    S["layers"]["ground_truth"] = dict(status="pass" if gate_pass else "FAIL",
                                       exit=rc, tail=out.strip().splitlines()[-1:])
    if not gate_pass:
        S["verdict"] = "BLOCKED: instrument failed ground-truth validation"
        _write_state(S)
        log(S["verdict"]); return 3

    # ---- layer 2: global measurement ----
    rc, out = sh(f"python3 {HERE}/p2w.py --budget {a.budget}", a.budget + 30)
    measured = len(glob.glob("/scratch/work/p2w/dist2/*.json"))
    expected = _expected_docs()
    # A run that stopped early is not a success. --budget is a time limit, so exit 0 can
    # mean "measured 13 of 213 and ran out of time", and calling that "ok" is how a
    # partial table got published with a clean verdict over it.
    complete = (measured >= expected)
    S["layers"]["measurement"] = dict(
        status="ok" if (rc == 0 and complete) else ("incomplete" if rc == 0 else f"exit{rc}"),
        docs_with_result=measured, of=expected, complete=complete)
    for line in out.splitlines():
        if "content-loss" in line or "displacement" in line or "clean" in line:
            S.setdefault("signatures", []).append(line.strip())

    # ---- layer 3: txt named checks ----
    vt = os.path.join(BENCH, "verify_txt.py")
    if os.path.exists(vt):
        # --list-checks is the supported way to prove the tool loads. --help exits 2, and
        # this used to record that as "available" anyway - a smoke test whose failure was
        # written down as a pass.
        rc, out = sh(f"cd {BENCH} && python3 verify_txt.py --list-checks", 60)
        S["layers"]["txt_checks"] = dict(
            status="available" if rc == 0 else "BROKEN",
            exit=rc,
            note="named semantic checks; advisory, not a size")
    else:
        S["layers"]["txt_checks"] = dict(status="not-run",
            reason="verify_txt.py not present in this checkout")

    # ---- census: what was lost, and where ----
    #
    # Runs here rather than as an instruction in a prompt because it needs the source PDFs
    # and the produced .docx files, and those only exist during this run - the sandbox is
    # wiped between runs, so the fixer cannot build this later. Its output is committed, so
    # the fixer reads CENSUS.csv from the repository in a run that has no corpus at all.
    #
    # Only on a complete measurement: a census of a half-measured corpus would name
    # mechanisms for documents whose numbers are not settled.
    if S["layers"]["measurement"].get("complete"):
        # Same trap as realworld/ and ROUND.json: the baseline cron copies only
        # p2w.py and gate.py into /scratch/work, so a plain HERE/census.py lookup
        # finds nothing and the census silently never runs. Search the places it
        # can actually be.
        cen = None
        for c in (os.path.join(HERE, "census.py"),
                  "/scratch/work/base/benchmarks/census.py",
                  "/scratch/work/p2w/repo/benchmarks/census.py",
                  "/scratch/work/cls/benchmarks/census.py",
                  "/scratch/work/fix/benchmarks/census.py"):
            if os.path.exists(c):
                cen = c
                break
        if cen:
            rc, out = sh("cd %s && python3 %s --corpus /scratch/work/p2w/corpus "
                         "--out /scratch/work/p2w/out --ranking /scratch/output/RANKING.csv"
                         % (os.path.dirname(HERE), cen), 240)
            tail = [l for l in out.strip().splitlines() if l.startswith("  ")]
            S["layers"]["census"] = dict(status="ok" if rc == 0 else f"exit{rc}",
                                         summary=tail[-8:])
            # THE CENSUS IS WRITTEN BESIDE THE RANKING, AND THE RANKING IS IN /scratch/output.
            #
            # census.py sets its output directory from --ranking ("the output belongs beside
            # the ranking it describes"), and gate.py passes /scratch/output/RANKING.csv, so
            # every census this pipeline ever ran wrote /scratch/output/CENSUS.csv and left
            # benchmarks/CENSUS.csv alone. It has been the header row and nothing else since
            # 18 Nov 17:19 - through four complete measurements that each logged "census: ok".
            # The fixer is told to read benchmarks/CENSUS.csv before forming a theory, and a
            # fresh pod has no corpus, so /scratch/output is gone by the time anyone reads it.
            # This is the RANKING.csv publish below, one file over: copy it into the repository
            # or the census exists only for the run that made it.
            for name in ("CENSUS.csv", "CENSUS.md"):
                src = os.path.join("/scratch/output", name)
                try:
                    if os.path.exists(src):
                        shutil.copyfile(src, os.path.join(HERE, name))
                        log("published %s into the repository" % name)
                except Exception as e:
                    log("could not publish %s: %s" % (name, str(e)[:120]))
        else:
            S["layers"]["census"] = dict(status="not-run", reason="census.py not present")

    # ---- ratchet ----
    # WHICH ROUND THESE NUMBERS BELONG TO.
    #
    # A round closes and RANKING.csv keeps every row it had, so "all rows scored" stays
    # true across the boundary. Without a round stamp, measure_gate would read round 1's
    # finished table as round 2's finished work and advance the phase before the baseline
    # had measured anything - rounds 2 and 3 would run on round 1's numbers and prove
    # nothing. Stamping the round here, and requiring it in the gate, is what makes a new
    # round actually start with a new measurement.
    rp = _find_round_json()
    try:
        S["round"] = json.load(open(rp)).get("round", 1) if rp else None
    except Exception:
        S["round"] = None
    S["ratchet"] = ratchet()

    # THE RANKING IS THE PIPELINE'S SOURCE OF TRUTH, AND IT WAS ONLY EVER WRITTEN TO /scratch/output.
    #
    # This is the same defect the 13:47 run fixed for STATE.json, one file over and far more
    # expensive: gate.py measured into /scratch/output/RANKING.csv, compared that against the
    # committed baseline, and never touched benchmarks/RANKING.csv. So the committed ranking could
    # only ever be as new as the last time somebody copied it by hand - and on 18 Nov the 15:30 run
    # measured itr-computation-with-slab-table from 68.82 to 50.80, recorded the attempt as kept,
    # released the slot, and left benchmarks/RANKING.csv reading 68.82. The ledger said the fix was
    # kept; the file every report reads said nothing had happened.
    #
    # Published only when the measurement is complete, for the same reason the verdict refuses to
    # speak on a partial one: a ranking half-written is worse than a ranking one run old.
    if S["layers"]["measurement"].get("complete"):
        try:
            if os.path.exists(RANK):
                dest = os.path.join(HERE, "RANKING.csv")
                shutil.copyfile(RANK, dest)
                # EXEMPT.json IS THE AUTHORITY, AND THE MEASUREMENT DOES NOT KNOW IT.
                #
                # p2w.py writes share5=0.0 and problem=none for a document it could not measure, so
                # 416_many_tiny_pages read as PERFECT in the table the whole pipeline is judged on -
                # a 300-page document that EXEMPT.json says was never measured at all. Copying that
                # file over the committed ranking put the lie back every time. Re-apply the exemption
                # after the copy: blank the scores, name the problem "exempt", and let the corpus mean
                # skip it instead of being dragged down by a zero that means "unknown".
                try:
                    ex_path = os.path.join(HERE, "..", "tools", "p2w-bench", "EXEMPT.json")
                    exempt = set()
                    if os.path.exists(ex_path):
                        exempt = set((json.load(open(ex_path, encoding="utf-8")).get("docx") or {}))
                    if exempt:
                        rows = list(csv.DictReader(open(dest, encoding="utf-8")))
                        if rows:
                            fields = list(rows[0].keys())
                            n = 0
                            for r in rows:
                                if r.get("document") in exempt:
                                    for k in ("share1", "share2", "share3", "share5", "share10",
                                              "median_pt", "p90_pt", "max_pt", "text_recall"):
                                        if k in r:
                                            r[k] = ""
                                    r["problem"] = "exempt"
                                    n += 1
                            import io as _io
                            buf = _io.StringIO()
                            w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
                            w.writeheader()
                            w.writerows(rows)
                            open(dest, "w", encoding="utf-8", newline="").write(buf.getvalue())
                            log("re-applied %d exemption(s) after the publish" % n)
                except Exception as e:
                    log("could not re-apply exemptions: %s" % e)
                log("published RANKING.csv into the repository")
        except Exception as e:
            log("could not publish RANKING.csv: %s" % str(e)[:120])

    # ---- verdict ----
    #
    # INCOMPLETE OUTRANKS EVERYTHING EXCEPT A FAILED GATE.
    #
    # A run that measured 13 of 213 documents has no regressions, because the 200 it
    # never looked at cannot regress. Read on its own, that is a clean bill of health for
    # a corpus that was barely touched - and this verdict is what measure_gate and the APK
    # cron both read. So an incomplete measurement is named as one, before any comparison
    # is allowed to speak.
    reg = S["ratchet"].get("regressions", [])
    meas = S["layers"]["measurement"]
    if not meas.get("complete"):
        S["verdict"] = ("INCOMPLETE: measured %d of %d documents - run again with more "
                        "budget before trusting any comparison"
                        % (meas["docs_with_result"], meas["of"]))
    elif reg:
        S["verdict"] = f"REGRESSION: {len(reg)} document(s) worse than baseline"
    elif S["ratchet"].get("status") != "compared":
        S["verdict"] = "OK, but no baseline to ratchet against"
    else:
        S["verdict"] = "OK: no regressions against baseline"

    _write_state(S)
    log(S["verdict"])
    log(f"layers: " + " ".join(f"{k}={v['status']}" for k, v in S["layers"].items()))
    return 0

if __name__ == "__main__":
    sys.exit(main())
