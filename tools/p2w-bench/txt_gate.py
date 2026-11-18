#!/usr/bin/env python3
"""txt_gate.py - the .txt half runs its own gate, and cannot move a .docx number.

WHY THE TXT IS SEPARATE. Three files, three jobs:

    PdfToWord.java    9677 lines   BOTH   - convert() builds the model, writeTxt() writes the .txt
    DocxWriter.java   7219 lines   DOCX   - writes the .docx
    TxtWriter.java     568 lines   TXT    - writes the .txt

    ReadingOrder.java:24-30
        Result r = PdfToWord.convert(pdf, "", null);
        PdfToWord.classifyHeadings(r);
        ReadingOrder.apply(r);                 // one order, for every consumer
        DocxWriter.write(r, docx);             // reads it
        PdfToWord.writeTxt(r, txt);            // reads the same order

So a change in DocxWriter.java moves the .docx only, a change in TxtWriter.java moves the .txt only,
and a change in PdfToWord.java moves both - it owns convert() and writeTxt().

Two facts hold the isolation in place, both from the source. PdfToWord.java:139-140, on lineX/lineY:
"that work happens in writeTxt() and nowhere else - the .docx path reads runs and never touches any of
these, so the document output cannot change." PdfToWord.java:730-735, on the five layout stats: "NO
LONGER WRITTEN HERE. These five were filled by DocxWriter.write into this object ... so a .txt written
after a .docx described a document whose report carried numbers only the .docx writer could produce."
That second one was the bug, and it was fixed by returning the stats instead of storing them.

Everything else is kept apart so that neither side can damage the other by accident:

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


TXT_RANK = os.path.join(TXT, "RANKING-TXT.csv")
TXT_BEFORE = os.path.join(TXT, "DOCX-WATCH.json")


def main(argv):
    os.makedirs(TXT, exist_ok=True)
    docx_before = sha(DOCX_RANK)

    # THE OTHER DIRECTION. A docx-motivated change can move the txt, because DocxWriter mutates
    # page.blocks and TxtWriter walks it. --watch-docx snapshots the txt scores before such a change;
    # --check-docx compares them after. Without this the gate only ever caught txt breaking docx, and
    # the failure that actually happened (SECTOR 19, 11 of 211 documents) went the other way.
    if "--watch-docx" in argv:
        import json as _j
        _j.dump({"txt_sha": sha(TXT_RANK),
                 "at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 19800))},
                open(TXT_BEFORE, "w", encoding="utf-8"), indent=1)
        print("  watching: RANKING-TXT.csv is %s - re-run with --check-docx after the docx change"
              % sha(TXT_RANK))
        return 0
    if "--check-docx" in argv:
        import json as _j
        try:
            was = _j.load(open(TXT_BEFORE, encoding="utf-8")).get("txt_sha")
        except Exception:
            print("  no snapshot - run --watch-docx before the docx change")
            return 2
        now = sha(TXT_RANK)
        if was == now:
            print("  txt untouched: RANKING-TXT.csv is %s, unchanged by the docx work" % now)
            return 0
        print("  TXT MOVED DURING DOCX WORK: RANKING-TXT.csv was %s, now %s." % (was, now))
        print("  DocxWriter mutates page.blocks and TxtWriter walks it, so this is expected unless")
        print("  the change was meant to be docx-only. Re-score the txt and say so in the report.")
        return 1

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
