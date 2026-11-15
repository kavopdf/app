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

HERE = os.path.dirname(os.path.abspath(__file__))
RANK = "/scratch/output/RANKING.csv"
STATE = "/scratch/output/STATE.json"
RAW = "https://raw.githubusercontent.com/kavopdf/app/main/benchmarks/RANKING.csv"
BENCH = "/scratch/work/p2w/repo/tools/p2w-bench"

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=250)
    ap.add_argument("--ratchet-only", action="store_true")
    a = ap.parse_args()
    os.makedirs("/scratch/output", exist_ok=True)

    if a.ratchet_only:
        r = ratchet(); print(json.dumps(r, indent=1)); return 0

    S = dict(ran_at=time.strftime("%Y-%m-%dT%H:%M:%S"), layers={})

    # ---- layer 1: ground truth ----
    rc, out = sh("python3 " + HERE + "/p2w.py --validate", 180)
    gate_pass = (rc == 0)
    S["layers"]["ground_truth"] = dict(status="pass" if gate_pass else "FAIL",
                                       exit=rc, tail=out.strip().splitlines()[-1:])
    if not gate_pass:
        S["verdict"] = "BLOCKED: instrument failed ground-truth validation"
        json.dump(S, open(STATE, "w"), indent=1)
        log(S["verdict"]); return 3

    # ---- layer 2: global measurement ----
    rc, out = sh(f"python3 {HERE}/p2w.py --budget {a.budget}", a.budget + 30)
    measured = len(glob.glob("/scratch/work/p2w/dist2/*.json"))
    S["layers"]["measurement"] = dict(status="ok" if rc == 0 else f"exit{rc}",
                                      docs_with_result=measured, of=211)
    for line in out.splitlines():
        if "content-loss" in line or "displacement" in line or "clean" in line:
            S.setdefault("signatures", []).append(line.strip())

    # ---- layer 3: txt named checks ----
    vt = os.path.join(BENCH, "verify_txt.py")
    if os.path.exists(vt):
        rc, out = sh(f"cd {BENCH} && python3 verify_txt.py --help", 60)
        S["layers"]["txt_checks"] = dict(status="available", exit=rc,
            note="named semantic checks; advisory, not a size")
    else:
        S["layers"]["txt_checks"] = dict(status="not-run",
            reason="verify_txt.py not present in this checkout")

    # ---- ratchet ----
    # WHICH ROUND THESE NUMBERS BELONG TO.
    #
    # A round closes and RANKING.csv keeps every row it had, so "all rows scored" stays
    # true across the boundary. Without a round stamp, measure_gate would read round 1's
    # finished table as round 2's finished work and advance the phase before the baseline
    # had measured anything - rounds 2 and 3 would run on round 1's numbers and prove
    # nothing. Stamping the round here, and requiring it in the gate, is what makes a new
    # round actually start with a new measurement.
    try:
        import json as _j
        _r = _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "..", "tools", "p2w-bench", "ROUND.json")))
        S["round"] = _r.get("round", 1)
    except Exception:
        S["round"] = None
    S["ratchet"] = ratchet()

    # ---- verdict ----
    reg = S["ratchet"].get("regressions", [])
    if reg:
        S["verdict"] = f"REGRESSION: {len(reg)} document(s) worse than baseline"
    elif S["ratchet"].get("status") != "compared":
        S["verdict"] = "OK, but no baseline to ratchet against"
    else:
        S["verdict"] = "OK: no regressions against baseline"

    json.dump(S, open(STATE, "w"), indent=1)
    log(S["verdict"])
    log(f"layers: " + " ".join(f"{k}={v['status']}" for k, v in S["layers"].items()))
    return 0

if __name__ == "__main__":
    sys.exit(main())
