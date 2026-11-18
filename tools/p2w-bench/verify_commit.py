#!/usr/bin/env python3
"""Measure a sample of the corpus at one engine commit, using p2w.py's own conversion and scoring.

WHY THIS SHAPE. p2w.py already knows how to convert one document per JVM (ConvertOne), how to score
it, and how to cache the result against the engine commit. Re-implementing that in a second script
produced a loop that hung on the first document for reasons that had nothing to do with the engine.
So this points p2w.py at a sample directory and lets it do the work.

    python3 verify_commit.py <commit> [<commit> ...]        build, then measure
    python3 verify_commit.py <commit> --measure-only       measure the engine already built

The sample is every document named in the twelve commit messages plus a guard band across the score
range, so a commit that helps its own document but breaks a bystander is caught.
"""
import csv, json, os, shutil, subprocess, sys, time, importlib.util

ROOT = "/scratch/work/p2w"
FULL = "/scratch/work/FULL"
CORPUS = ROOT + "/corpus"
BASE = "/scratch/work/N15.csv"
SAMPLE_DIR = "/scratch/work/vc-sample"
OUT_DIR = "/scratch/work/vc-out"
STABLE = "/scratch/work/W2/benchmarks/p2w.py"

NAMED = [
    "041122-Account_Opening_Form", "Account_Opening_Form_Fillable_filled",
    "411_nested_xobject_transforms", "392_statistical_console_output",
    "76_devanagari_table", "78_mixed_english_devanagari_line", "360_restaurant_menu",
    "310_court_judgment", "321_auditors_report", "317_rti_response",
    "313_power_of_attorney", "304_package_insert_small_print",
    "316_contract_with_schedules", "371_experience_certificate",
    "312_affidavit_stamp_paper", "302_radiology_report",
]
GUARD = [
    "01_stamp_rotated_15deg_upright", "03_stamp_vertical_90deg", "07_stamp_over_table",
    "gst-invoice-3line-items", "salary-slip-corporate", "admit-card",
    "delivery-challan", "property-tax-receipt", "415_inline_images",
    "20_numbered_list_separate_column_txtpos", "80_gstin_pan_cin_ifsc_table",
    "62_two_col_newsletter_pull_quote", "63_three_column_brochure",
    "352_certificate_ornate_border", "375_attendance_register",
]
SAMPLE = NAMED + GUARD


def run(cmd, timeout=280):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def build(commit):
    run("cd %s && git checkout -q -f %s" % (FULL, commit), 120)
    # the engine is what is being verified; the build tooling stays at head so ConvertOne compiles
    run("cd %s && git checkout -q origin/main -- tools/p2w-bench/build-engine.sh "
        "tools/engine-verify/ConvertOne.java" % FULL, 120)
    run("rm -f %s/tools/engine-verify/out/ConvertAll.class" % FULL, 60)
    run("cd %s && bash tools/p2w-bench/build-engine.sh" % FULL, 280)
    head = run("cd %s && git log -1 --format=%%h" % FULL, 30).stdout.strip()
    eng = run("cd %s && git log -1 --format=%%h -- app/src/main/java/com/kavopdf/app/engine/" % FULL, 30).stdout.strip()
    ok = os.path.exists(FULL + "/tools/engine-verify/out/ConvertOne.class")
    print("  built head=%s engine=%s ConvertOne=%s" % (head, eng, ok), flush=True)
    return ok


def sample_corpus():
    """A corpus of just the sampled documents, so a pass takes a minute instead of forty."""
    shutil.rmtree(SAMPLE_DIR, ignore_errors=True)
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    n = 0
    for d in SAMPLE:
        src = "%s/%s.pdf" % (CORPUS, d)
        if os.path.exists(src):
            shutil.copy(src, SAMPLE_DIR)
            n += 1
    return n


def measure(commit, keep=False):
    if not keep:
        shutil.rmtree(OUT_DIR, ignore_errors=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    spec = importlib.util.spec_from_file_location("p2w", STABLE)
    p2w = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(p2w)
    except SystemExit:
        pass
    # point the proven machinery at the sample and the freshly built engine
    p2w.CORPUS = SAMPLE_DIR
    p2w.DOCX = OUT_DIR
    p2w.DIST = OUT_DIR + "/dist"
    p2w.PRE = OUT_DIR + "/pre"
    p2w.REPO = FULL
    os.makedirs(p2w.DIST, exist_ok=True)

    t0 = time.time()
    p2w.docx(t0 + 200)
    p2w.run(t0 + 260)

    base = {r["document"]: float(r["share5"]) for r in csv.DictReader(open(BASE)) if r.get("share5")}
    rows = []
    for f in sorted(os.listdir(p2w.DIST)):
        if not f.endswith(".json"):
            continue
        d = f[:-5]
        try:
            m = json.load(open(p2w.DIST + "/" + f)).get("share5")
        except Exception:
            m = None
        if d in base and m is not None:
            rows.append((d, base[d], m))
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    measure_only = "--measure-only" in sys.argv
    n = sample_corpus()
    print("  sample: %d documents" % n, flush=True)
    for c in args:
        print("\n=== %s ===" % c, flush=True)
        t0 = time.time()
        if not measure_only:
            build(c)
        rows = measure(c, keep=measure_only)
        worse = [(d, b, m, m - b) for d, b, m in rows if m - b > 0.5]
        better = [(d, b, m, m - b) for d, b, m in rows if m - b < -0.5]
        same = len(rows) - len(worse) - len(better)
        print("  measured %d  same %d  better %d  worse %d" % (len(rows), same, len(better), len(worse)), flush=True)
        if worse:
            worse.sort(key=lambda r: -r[3])
            for d, b, m, dl in worse[:8]:
                print("   WORSE  %-40s %7.2f -> %7.2f  %+6.2f" % (d[:40], b, m, dl), flush=True)
        if better:
            better.sort(key=lambda r: r[3])
            for d, b, m, dl in better[:5]:
                print("   better %-40s %7.2f -> %7.2f  %+6.2f" % (d[:40], b, m, dl), flush=True)
        print("  VERDICT: %s   (%.0fs)" % ("REJECT - %d worse" % len(worse) if worse else "KEEP - nothing worse",
                                           time.time() - t0), flush=True)
        json.dump({"commit": c, "worse": worse, "better": better},
                  open("/scratch/work/vc-%s.json" % c, "w"))


main()
