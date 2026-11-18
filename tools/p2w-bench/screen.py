#!/usr/bin/env python3
"""Measure one class's own documents, resuming across calls, and say if a corpus pass is worth it.

WHY THIS EXISTS. Every attempt cost a full corpus pass - convert 213 documents one JVM at a time and
measure them. Forty minutes to learn that an idea did nothing, five such attempts to park one class,
and 92 OPEN classes: 307 hours of measuring before a single document is fixed.

A change aimed at content-present-partly-displaced can only help or hurt that class's documents. The
full corpus pass exists to catch the ones it might hurt by accident, so it belongs AFTER the cheap
question, not before it.

    python3 tools/p2w-bench/screen.py --class "content-present-partly-displaced"
    python3 tools/p2w-bench/screen.py --docs "360_restaurant_menu,76_devanagari_table"

Run it as many times as it takes. Each call converts and measures what it can inside the sandbox's
280-second command limit and keeps its cache, so the next call continues instead of starting again.
It prints a verdict only when every document in the class has been measured.

    SCREEN PASS   something improved and nothing got worse - run the full ratchet
    SCREEN FAIL   nothing improved, or something got worse - do not spend a corpus pass on it
    PARTIAL       n of m measured - call it again

A SCREEN PASS is not a kept fix. It says the idea survived the documents it was aimed at. The ratchet
still has to prove it across all 213, and only that can keep it.

THE ENGINE IS PART OF THE CACHE KEY. The docx and the measurements in screen-out are stamped with the
engine commit; a screen run after an engine change throws them away. Without that, a screen would
report the previous engine's numbers and pass an idea that had already failed.
"""
import csv, json, os, shutil, subprocess, sys, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = "/scratch/work/p2w"
CORPUS = ROOT + "/corpus"
REPO = ROOT + "/repo"
SUB = ROOT + "/screen-corpus"
OUT = ROOT + "/screen-out"
BASELINE = os.path.join(REPO_ROOT, "benchmarks", "RANKING.csv")
CLASSES = os.path.join(REPO_ROOT, "benchmarks", "DEFECT-CLASSES.md")


def run(cmd, timeout=280):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def engine_stamp():
    return run("cd %s && git log -1 --format=%%h -- app/src/main/java/com/kavopdf/app/engine/" % REPO,
               30).stdout.strip() or "unknown"


def docs_for(name):
    """The OPEN documents the classifier put in this class."""
    out = []
    for line in open(CLASSES, encoding="utf-8"):
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        doc, problem, status = cells[1].strip("`"), cells[2], cells[6]
        if status == "OPEN" and name in (problem, doc):
            out.append(doc)
    return out


def main(argv):
    name = ""
    for i, a in enumerate(argv):
        if a in ("--class", "--docs") and i + 1 < len(argv):
            name = argv[i + 1]
    if not name:
        print("usage: screen.py --class <problem> | --docs <d1,d2,...>")
        return 2

    docs = name.split(",") if "," in name else docs_for(name)
    if not docs:
        print("no OPEN documents for %r" % name)
        return 2

    base = {r["document"]: float(r["share5"])
            for r in csv.DictReader(open(BASELINE)) if r.get("share5")}
    docs = [d for d in docs if d in base and os.path.exists("%s/%s.pdf" % (CORPUS, d))]
    if not docs:
        print("none of the class's documents are in the corpus")
        return 2

    # The engine stamp decides whether the cache is still evidence about this engine.
    stamp_path = OUT + "/ENGINE"
    now = engine_stamp()
    was = ""
    try:
        was = open(stamp_path, encoding="utf-8").read().strip()
    except Exception:
        pass
    if was and was != now:
        print("engine changed %s -> %s - discarding the screen cache" % (was, now))
        shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    open(stamp_path, "w", encoding="utf-8").write(now)

    shutil.rmtree(SUB, ignore_errors=True)
    os.makedirs(SUB, exist_ok=True)
    for d in docs:
        try:
            os.link("%s/%s.pdf" % (CORPUS, d), "%s/%s.pdf" % (SUB, d))
        except Exception:
            shutil.copy("%s/%s.pdf" % (CORPUS, d), SUB)

    spec = importlib.util.spec_from_file_location("p2w", os.path.join(REPO_ROOT, "benchmarks", "p2w.py"))
    p2w = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(p2w)
    except SystemExit:
        pass
    # point the proven machinery at the class's documents and this run's engine
    p2w.CORPUS = SUB
    p2w.DOCX = OUT
    p2w.DIST = OUT + "/dist"
    p2w.PRE = OUT + "/pre"
    p2w.REPO = REPO
    os.makedirs(p2w.DIST, exist_ok=True)

    print("screening %d document(s) for %r  (engine %s)" % (len(docs), name[:44], now))
    t0 = time.time()
    p2w.docx(t0 + 170)
    p2w.run(t0 + 268)

    rows = []
    for d in docs:
        jf = "%s/dist/%s.json" % (OUT, d)
        if not os.path.exists(jf):
            continue
        try:
            m = json.load(open(jf)).get("share5")
        except Exception:
            m = None
        if m is not None:
            rows.append((d, base[d], m))

    if len(rows) < len(docs):
        print("   PARTIAL - %d of %d measured. Call again; the cache carries over." % (len(rows), len(docs)))
        return 3

    worse = [(d, b, m) for d, b, m in rows if m - b > 0.5]
    better = [(d, b, m) for d, b, m in rows if m - b < -0.5]
    same = len(rows) - len(worse) - len(better)
    for d, b, m in sorted(better, key=lambda r: r[2] - r[1])[:8]:
        print("   better  %-42s %7.2f -> %7.2f  %+6.2f" % (d[:42], b, m, m - b))
    for d, b, m in sorted(worse, key=lambda r: -(r[2] - r[1]))[:8]:
        print("   WORSE   %-42s %7.2f -> %7.2f  %+6.2f" % (d[:42], b, m, m - b))
    print("   %d measured, %d same, %d better, %d worse" % (len(rows), same, len(better), len(worse)))

    if worse:
        print("   SCREEN FAIL - %d got worse; a corpus pass would only confirm it" % len(worse))
        return 1
    if not better:
        print("   SCREEN FAIL - nothing improved; do not spend a corpus pass on this idea")
        return 1
    print("   SCREEN PASS - %d improved, none worse. Run the full ratchet before keeping it." % len(better))
    return 0


sys.exit(main(sys.argv))
