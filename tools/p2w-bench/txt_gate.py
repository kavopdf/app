#!/usr/bin/env python3
"""txt_gate.py - the .txt half runs its own gate, and cannot move a .docx number.

WHY THE TXT IS SEPARATE. Three files, three jobs:

    PdfToWord.java    9677 lines   MODEL + TXT - convert() builds the model, writeTxt() writes the txt
    DocxWriter.java   7219 lines   DOCX        - write() writes the .docx
    TxtWriter.java     568 lines   TXT         - write() writes the .txt

  PdfToWord writes no .docx - no w:document, no word/document.xml, no ZipOutputStream, no ZipEntry.

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
BOTH_BEFORE = os.path.join(TXT, "BOTH-WATCH.json")


def main(argv):
    os.makedirs(TXT, exist_ok=True)
    docx_before = sha(DOCX_RANK)

    # THE OTHER DIRECTION. A docx-motivated change can move the txt, because DocxWriter.orderStamps()
    # mutates page.blocks (line 4757, blocks.removeAll) and TxtWriter walks it. Note it is that
    # method and not the file: DocxWriter.write() has zero mutation sites.
    # --watch-docx snapshots the txt scores before such a change;
    # --check-docx compares them after. Without this the gate only ever caught txt breaking docx, and
    # the failure that actually happened (SECTOR 19, 11 of 211 documents) went the other way.
    # THE ONE-DIRECTIONAL PAIR IS STILL HERE AND IS THE NARROWER OPTION. --watch-docx records only
    # the txt hash, so --check-docx can only answer "did the txt move during docx work" - it cannot
    # see a docx number moving, which is the other half. A run that used this pair and believed it
    # had checked both directions would be wrong, and that is a worse failure than not checking.
    # Kept working for anything already calling it, with the better command named on every use.
    if "--watch-docx" in argv:
        import json as _j
        _j.dump({"txt_sha": sha(TXT_RANK),
                 "at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 19800))},
                open(TXT_BEFORE, "w", encoding="utf-8"), indent=1)
        print("  watching: RANKING-TXT.csv is %s - re-run with --check-docx after the docx change"
              % sha(TXT_RANK))
        print("  NOTE: this watches one direction. --snapshot / --verify watches both and is what")
        print("        a run should use; this pair cannot see a docx number move.")
        return 0
    # ONE SNAPSHOT, BOTH DIRECTIONS. The two one-way commands above each guard half the problem,
    # and a run that remembers only one of them leaves the other open. These two take both hashes at
    # once and compare both at once, so there is no way to check the format you were working on and
    # forget the one you were not.
    if "--snapshot" in argv:
        import json as _j
        _j.dump({"docx_sha": sha(DOCX_RANK), "txt_sha": sha(TXT_RANK),
                 "at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 19800))},
                open(BOTH_BEFORE, "w", encoding="utf-8"), indent=1)
        print("  snapshot: docx %s | txt %s" % (sha(DOCX_RANK), sha(TXT_RANK)))
        print("  run --verify after the change; it compares both and names whichever moved")
        return 0

    if "--verify" in argv:
        import json as _j
        try:
            was = _j.load(open(BOTH_BEFORE, encoding="utf-8"))
        except Exception:
            print("  no snapshot - run --snapshot before the change")
            return 2
        dx_now, tx_now = sha(DOCX_RANK), sha(TXT_RANK)
        dx_moved = was.get("docx_sha") != dx_now
        tx_moved = was.get("txt_sha") != tx_now
        if not dx_moved and not tx_moved:
            print("  both untouched: docx %s | txt %s" % (dx_now, tx_now))
            return 0
        if dx_moved:
            print("  DOCX MOVED: RANKING.csv was %s, now %s" % (was.get("docx_sha"), dx_now))
        if tx_moved:
            print("  TXT MOVED:  RANKING-TXT.csv was %s, now %s" % (was.get("txt_sha"), tx_now))
        print("  An engine change must say which format it was for. If it was meant to move only one,")
        print("  the other moving is the defect - PdfToWord.convert() feeds both and")
        print("  DocxWriter.orderStamps() reorders page.blocks, which TxtWriter walks.")
        return 1

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
        print("  DocxWriter.orderStamps() mutates page.blocks and TxtWriter walks it, so this is")
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

    # AN EMPTY STORE IS NOT A CLEAN STORE. Without this the gate printed
    # "0 of 0 clean (0.0%)" and exited 0, which reads as a pass over a corpus nobody measured - the
    # same shape of mistake as a ratchet with nothing to compare. Say what is missing and refuse.
    if rows == 0:
        print()
        print("  UNMEASURED - %s holds no scoreable row." % os.path.basename(RANK_TXT))
        print("  Nothing was summarised, so nothing is proved. Score the corpus first:")
        print("      python3 tools/p2w-bench/txt_gate.py --score N")
        return 3
    marks_ok = os.path.exists(os.path.join(TXT, "RATCHET-TXT.json"))
    base_ok = os.path.exists(os.path.join(TXT, "RANKING-TXT-BASELINE.csv"))
    if not marks_ok or not base_ok:
        print()
        print("  INCOMPLETE - the .txt has scores but no %s."
              % ("marks" if not marks_ok else "baseline"))
        print("  marks    : %s" % ("present" if marks_ok else "MISSING - nothing to ratchet against"))
        print("  baseline : %s" % ("present" if base_ok else "MISSING - nothing to compare against"))
        print("  Fix with: python3 tools/p2w-bench/txt_rank.py --all   (writes the marks)")
        print("            python3 tools/p2w-bench/txt_rank.py --baseline")
        return 3

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
