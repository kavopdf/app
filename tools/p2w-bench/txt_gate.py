#!/usr/bin/env python3
"""txt_gate.py - the .txt half runs its own gate, and cannot move a .docx number.

WHY THE TXT IS SEPARATE. The two formats share one thing: the engine. DocxWriter writes the .docx and
the .txt from the same layout model, so a change made to improve the txt is a change to code the docx
also depends on. Everything else is kept apart so that neither side can damage the other by accident:

    tools/p2w-bench/txt/RANKING-TXT.csv   the txt scores. Nothing in the .docx path reads it.
    tools/p2w-bench/txt/STATE-TXT.json    the txt state. Not benchmarks/STATE.json.
    tools/p2w-bench/txt/HISTORY-TXT.jsonl one line per gate run.

AND THE ONE GUARANTEE THAT MATTERS: a txt run records the SHA-256 of benchmarks/RANKING.csv when it
starts. If that file is different when the gate finishes, a docx number moved during txt work - and
the gate says so, loudly, instead of letting the change through. The docx ratchet is still the only
thing that can authorise a docx change; this gate's job is to prove the txt work did not make one.

    python3 tools/p2w-bench/txt_gate.py --score 40     # score the next 40, then gate
    python3 tools/p2w-bench/txt_gate.py --gate         # gate only, no scoring
"""
import hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, "txt")
RANK_TXT = os.path.join(TXT, "RANKING-TXT.csv")
STATE_TXT = os.path.join(TXT, "STATE-TXT.json")
HIST = os.path.join(TXT, "HISTORY-TXT.jsonl")
DOCX_RANK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "benchmarks", "RANKING.csv")


def sha(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except Exception:
        return "missing"


def load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def main(argv):
    os.makedirs(TXT, exist_ok=True)
    docx_before = sha(DOCX_RANK)

    if "--score" in argv:
        n = int(argv[argv.index("--score") + 1])
        r = subprocess.run(["python3", os.path.join(HERE, "txt_rank.py"), "--limit", str(n)],
                           capture_output=True, text=True, timeout=280)
        tail = [l for l in r.stdout.strip().split("\n") if l.strip()][-3:]
        for l in tail:
            print("  " + l.strip())
        if r.returncode != 0:
            print("  the txt ratchet refused: a document got worse")

    # score the state from the csv, independently of how it was produced
    rows, clean, failing = 0, 0, 0
    try:
        import csv
        for r in csv.DictReader(open(RANK_TXT, encoding="utf-8")):
            try:
                app, bad = int(r.get("applicable") or 0), int(r.get("failed") or 0)
            except ValueError:
                continue
            if app <= 0 or bad < 0:
                continue
            rows += 1
            if bad == 0:
                clean += 1
            else:
                failing += 1
    except Exception:
        pass

    docx_after = sha(DOCX_RANK)
    moved = docx_before != docx_after and docx_before != "missing"

    st = load(STATE_TXT, {})
    st.update({
        "scored": rows,
        "clean": clean,
        "failing": failing,
        "pct": round(100.0 * clean / rows, 1) if rows else 0.0,
        "docx_rank_sha": docx_after,
        "at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 19800)),
        "docx_moved_during_txt": moved,
    })
    json.dump(st, open(STATE_TXT, "w", encoding="utf-8"), indent=1)
    with open(HIST, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": st["at"], "scored": rows, "clean": clean,
                             "failing": failing, "docx_moved": moved}) + "\n")

    print()
    print("  txt: %d scored | %d clean (%.1f%%) | %d failing" % (rows, clean, st["pct"], failing))
    if moved:
        print("  DOCX MOVED DURING TXT WORK: benchmarks/RANKING.csv changed from %s to %s."
              % (docx_before, docx_after))
        print("  That is not a txt result. The docx ratchet decides whether it may be kept; if this")
        print("  run was only meant to touch the txt, revert the engine change.")
        return 1
    print("  docx untouched: benchmarks/RANKING.csv is %s, unchanged by this gate" % docx_after)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
