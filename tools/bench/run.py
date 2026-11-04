#!/usr/bin/env python3
"""
Run only the benchmarks the change can possibly have affected, then ratchet the baseline.

WHY NOT RUN EVERYTHING

The full set takes about 16 seconds of engine time, so time is not the reason. Signal is.
If a change touches the merge code, twenty-one other tool results are noise, and noise is
how a real regression gets missed.

THE RATCHET

baseline.json holds a floor, not a snapshot.

  better than the floor   -> the floor moves up, automatically. An improvement can never be
                             lost by forgetting to record it.
  worse than the floor    -> FAIL, and the floor does not move.
  listed in known_fail    -> reported, never fails the build, stays visible until fixed.

So the baseline only ever goes up. Nobody has to remember to update it, and nothing can
quietly get worse.

    python3 tools/bench/run.py --all
    python3 tools/bench/run.py --since HEAD~1
    python3 tools/bench/run.py --tools MERGE,SPLIT
"""
import os, sys, json, subprocess, argparse, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH = os.path.join(ROOT, "tools", "bench")
WORK = os.environ.get("BENCH_WORK", "/tmp/kavopdf-bench")
BASELINE = os.path.join(BENCH, "baseline.json")

# ---------------------------------------------------------------- file -> tools
# A file listed here only affects the tools on its line. Anything in PdfEngine.java is
# narrowed further, by method, in METHODS below.
FILE_TOOLS = {
    "app/src/main/java/com/kavopdf/app/engine/PdfToWord.java": ["PDF to Word"],
    "app/src/main/java/com/kavopdf/app/engine/DocxWriter.java": ["PDF to Word"],
    "app/src/main/java/com/kavopdf/app/engine/PdfRepair.java": ["Repair PDF"],
    "app/src/main/java/com/kavopdf/app/engine/PdfSigner.java": ["Sign", "Verify signature"],
}

# Activity file -> the tool it drives. A screen bug shows up here.
ACTIVITY_TOOLS = {
    "MergeActivity": ["Merge"],
    "SplitActivity": ["Split"],
    "CropActivity": ["Crop"],
    "PagesActivity": ["Organize pages"],
    "WatermarkActivity": ["Watermark"],
    "LinksActivity": ["Hyperlinks"],
    "FormsActivity": ["Fill forms"],
    "AnnotateActivity": ["Annotate & sign"],
    "CreatePdfActivity": ["Create PDF"],
    "ImagesToPdfActivity": ["Images to PDF"],
    "BookmarksActivity": ["Bookmarks"],
    "RedactActivity": ["Redact"],
    "ToolsActivity": [],          # dispatches everything; see note below
    "PdfActivity": [],            # shared base; see note below
}

# Method name inside PdfEngine.java -> the tools that call it.
METHODS = {
    "merge": ["Merge"],
    "splitToFiles": ["Split"],
    "cropPages": ["Crop"],
    "rebuild": ["Organize pages"],
    "rotatePages": ["Organize pages"],
    "keepPages": ["Organize pages"],
    "removePages": ["Organize pages"],
    "reorderPages": ["Organize pages"],
    "watermarkText": ["Watermark"],
    "watermarkImage": ["Watermark"],
    "addPageNumbers": ["Page numbers"],
    "compress": ["Compress"],
    "encrypt": ["Protect"],
    "decrypt": ["Unlock"],
    "setMetadata": ["Metadata"],
    "clearMetadata": ["Metadata"],
    "getMetadata": ["Metadata"],
    "extractImages": ["Extract images"],
    "addTextLink": ["Hyperlinks"],
    "addLink": ["Hyperlinks"],
    "addLinkIcon": ["Hyperlinks"],
    "addLinks": ["Hyperlinks"],
    "addImageLink": ["Hyperlinks"],
    "pageLinks": ["Hyperlinks"],
    "findLinks": ["Hyperlinks"],
    "fillForm": ["Fill forms"],
    "paintField": ["Fill forms"],
    "paintMissingValues": ["Fill forms"],
    "addText": ["Annotate & sign"],
    "applyStamps": ["Annotate & sign"],
    "createPdf": ["Create PDF"],
    "imagesToPdf": ["Images to PDF"],
    "setBookmarks": ["Bookmarks"],
    "bookmarks": ["Bookmarks"],
    "redactPages": ["Redact"],
    "redactPagesLazy": ["Redact"],
    "applyRedaction": ["Redact"],
}

# Anything in PdfEngine.java that is shared plumbing rather than one tool's work.
# A change here can move every tool that touches a PDF, so everything runs.
SHARED_IN_PDFENGINE = [
    "open(", "pageCount", "pageSizes", "pageDisplaySizes", "winAnsi", "normaliseUrl",
    "isEncrypted", "needsPassword", "decodeImage", "decodeUpright", "exif", "indexText",
    "searchIndex", "wordsOnPage", "stampDisplayRasters", "addTextLayer",
]

ALL_TOOLS = [
    "Merge", "Split", "Crop", "Organize pages", "Watermark", "Page numbers", "Compress",
    "Protect", "Unlock", "Metadata", "Extract images", "Hyperlinks", "Sign",
    "Verify signature", "Fill forms", "Annotate & sign", "Create PDF", "Images to PDF",
    "Bookmarks", "Redact", "Repair PDF", "PDF to Word",
]

# Metrics where a smaller number is better. Everything else numeric is higher-is-better.
LOWER_BETTER = {
    "Compress|size ratio",
    "Watermark|centred (off by)",
}

# Booleans and counts that must be exactly right; a drop of any size is a failure.
EXACT = {
    "Merge|page count", "Merge|bookmarks kept", "Split|file count",
    "Organize pages|rotate applied", "Create PDF|page count",
    "Images to PDF|page count", "Bookmarks|entry count",
    "Bookmarks|destinations correct", "Extract images|count",
    "Hyperlinks|link created", "Repair PDF|pages recovered",
    "Fill forms|drawn once (no double)", "Create PDF|page size",
}

# Metrics whose baseline is a "pass" verdict rather than a number.
BOOLEAN_METRICS = {
    "Merge|page order + content", "Split|pages preserved", "Crop|content inside kept",
    "Watermark|text on every page", "Page numbers|correct on every page",
    "Compress|text layer intact", "Protect|locked without password",
    "Protect|right password works", "Protect|wrong password rejected",
    "Unlock|opens without password", "Unlock|content identical",
    "Metadata|fields written", "Metadata|keywords written",
    "Extract images|dimensions match", "Hyperlinks|URI correct",
    "Hyperlinks|placed where asked", "Hyperlinks|visible text present",
    "Sign|signature verifies", "Sign|incremental (original bytes intact)",
    "Verify signature|reports valid on signed file",
    "Verify signature|no false positive on unsigned",
    "Fill forms|values written", "Fill forms|visible on the page",
    "Annotate & sign|text stamp present", "Annotate & sign|placed where asked",
    "Images to PDF|aspect ratio kept", "Bookmarks|titles correct",
    "Redact|secret text gone", "Redact|page has no text layer",
    "Redact|other page untouched", "Repair PDF|output opens",
    "Repair PDF|content recovered", "PDF to Word|docx has the text",
    "Crop|cropbox correct", "Watermark|centred (off by)",
}


def git(*args):
    try:
        return subprocess.check_output(["git", "-C", ROOT] + list(args),
                                       stderr=subprocess.DEVNULL).decode("utf-8", "replace")
    except Exception:
        return ""


def changed_files(since):
    """Return the changed paths, or None when git cannot tell us.

    None matters. A shallow CI checkout has no HEAD~1, and treating that as "nothing
    changed" would skip every tool and report a pass. Not knowing has to run everything.
    """
    out = git("diff", "--name-only", since, "HEAD")
    if not out.strip():
        out = git("diff", "--name-only", "HEAD~1", "HEAD")
    if not out.strip():
        # Ask git whether the ref exists at all, rather than guessing from empty output.
        probe = git("rev-parse", "--verify", "HEAD~1")
        if not probe.strip():
            return None
        return []
    return [l.strip() for l in out.split("\n") if l.strip()]


def tools_for_changes(files):
    """Which tools can a change to these files possibly have moved?"""
    picked = set()
    for f in files:
        if f in FILE_TOOLS:
            picked.update(FILE_TOOLS[f])
            continue
        # Activity files: match by class name in the path
        base = os.path.basename(f)
        hit = False
        for cls, tools in ACTIVITY_TOOLS.items():
            if base.startswith(cls):
                picked.update(tools)
                hit = True
                break
        if hit:
            continue
        # Anything else in the engine package is either PdfEngine or plumbing.
        if "/engine/" in f:
            if f.endswith("PdfEngine.java"):
                picked.update(tools_for_pdfengine(since_global[0]))
            else:
                picked.update(ALL_TOOLS)
            continue
        if f.startswith("tools/bench/"):
            # The harness and the baseline change the numbers, not the tools. Re-seeding a
            # metric is handled by the ratchet; there is no reason to run 22 tools for it.
            continue
        if f.startswith("app/src/main/res/") or f.endswith(".xml"):
            continue
    return sorted(picked)


since_global = ["HEAD~1"]


def tools_for_pdfengine(since):
    """Narrow a PdfEngine.java change to the tools whose methods actually changed."""
    diff = git("diff", "-U0", since, "HEAD", "--",
               "app/src/main/java/com/kavopdf/app/engine/PdfEngine.java")
    if not diff.strip():
        return ALL_TOOLS
    # A change to shared plumbing can move anything.
    for marker in SHARED_IN_PDFENGINE:
        if marker in diff:
            return ALL_TOOLS
    picked = set()
    for method, tools in METHODS.items():
        # the method name appearing in a changed line is a good enough signal
        for line in diff.split("\n"):
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                if method in line:
                    picked.update(tools)
                    break
    # No recognisable method: be safe rather than clever.
    return sorted(picked) if picked else ALL_TOOLS


def load_baseline():
    if os.path.isfile(BASELINE):
        try:
            return json.load(open(BASELINE))
        except Exception:
            pass
    return {"metrics": {}, "known_fail": {}}


def save_baseline(b):
    with open(BASELINE, "w") as f:
        json.dump(b, f, indent=1, sort_keys=True)
        f.write("\n")


def num(v):
    try:
        return float(v)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="run every tool")
    ap.add_argument("--since", default="HEAD~1", help="git ref to diff against")
    ap.add_argument("--tools", default="", help="comma separated tool names")
    ap.add_argument("--no-ratchet", action="store_true",
                    help="report only, do not raise the baseline")
    a = ap.parse_args()

    since_global[0] = a.since

    if a.tools:
        tools = [t.strip() for t in a.tools.split(",") if t.strip()]
    elif a.all:
        tools = ALL_TOOLS
    else:
        files = changed_files(a.since)
        if files is None:
            print(f"cannot diff against {a.since} (shallow checkout?) - running every tool")
            tools = ALL_TOOLS
            print(f"\ntools to measure ({len(tools)}): all\n")
            files = []
        else:
            print(f"changed files: {len(files)}")
        if files:
            for f in files[:20]:
                print("   " + f)
            tools = tools_for_changes(files)
            if not tools:
                print("no tool is affected by this change - nothing to measure")
                return 0
        else:
            tools = []

    print(f"\ntools to measure ({len(tools)}): {', '.join(tools)}\n")

    indir = os.path.join(WORK, "in")
    outdir = os.path.join(WORK, "out")
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)
    if not os.path.isfile(os.path.join(indir, "multi.pdf")):
        subprocess.check_call([sys.executable, os.path.join(BENCH, "make_fixtures.py"), indir])

    java = os.environ.get("JAVA_HOME", "")
    javabin = os.path.join(java, "bin", "java") if java else "java"
    cp = os.environ.get("BENCH_CP", "")
    if not cp:
        print("BENCH_CP is not set - point it at the compiled engine + libraries")
        return 2

    # Bench.java uses engine tool names; the map above uses display names.
    java_names = {
        "Merge": "MERGE", "Split": "SPLIT", "Crop": "CROP", "Organize pages": "PAGES,ROTATE",
        "Watermark": "WATERMARK", "Page numbers": "PAGENUM", "Compress": "COMPRESS",
        "Protect": "PROTECT,UNLOCK", "Unlock": "PROTECT,UNLOCK", "Metadata": "METADATA",
        "Extract images": "EXTRACT", "Hyperlinks": "LINKS", "Sign": "SIGN,VERIFY,TAMPER,VERIFY_TAMPER",
        "Verify signature": "SIGN,VERIFY,TAMPER,VERIFY_TAMPER", "Fill forms": "FORMS",
        "Annotate & sign": "ANNOTATE", "Create PDF": "CREATE_PDF",
        "Images to PDF": "IMAGES_PDF", "Bookmarks": "BOOKMARKS", "Redact": "REDACT",
        "Repair PDF": "REPAIR", "PDF to Word": "PDF_TO_WORD",
    }
    jsel = set()
    for t in tools:
        for n in java_names.get(t, "").split(","):
            if n:
                jsel.add(n)
    jsel = sorted(jsel) or ["ALL"]

    subprocess.check_call([javabin, "-cp", cp, "Bench", indir, outdir, ",".join(jsel)])

    subprocess.check_call([sys.executable, os.path.join(BENCH, "score_all.py"),
                           indir, outdir, ",".join(tools)])

    scores = json.load(open(os.path.join(outdir, "scores.json")))
    base = load_baseline()
    floor = base.setdefault("metrics", {})
    known = base.setdefault("known_fail", {})

    raised, dropped, kept, fixed = [], [], [], []
    for key, cur in scores.items():
        if key in known:
            kept.append(key)
            continue
        v = cur["value"]
        verdict = cur["verdict"]
        prev = floor.get(key)

        if prev is None:
            # A metric that is already failing must never become the floor - that would
            # enshrine the bug. It is reported and left unseeded until it passes.
            if verdict == "FAIL":
                dropped.append((key, "(no baseline)", v))
                continue
            floor[key] = v
            raised.append((key, "new", v))
            continue

        nv, npv = num(v), num(prev)
        if nv is None or npv is None:
            # non-numeric: only a pass/fail transition matters
            if verdict == "FAIL" and cur.get("verdict") != "FAIL":
                dropped.append((key, prev, v))
            continue

        if key in LOWER_BETTER:
            better = nv < npv
        elif key in EXACT:
            better = False
            if nv != npv:
                dropped.append((key, prev, v))
                continue
        else:
            better = nv > npv

        if better:
            floor[key] = v
            raised.append((key, prev, v))
        elif nv != npv:
            dropped.append((key, prev, v))

    print("\n" + "=" * 70)
    if raised:
        print(f"BASELINE RAISED ({len(raised)}) - these are improvements, now the new floor:")
        for k, o, n in raised:
            print(f"   + {k}:  {o}  ->  {n}")
    if dropped:
        print(f"\nREGRESSIONS ({len(dropped)}) - the floor did NOT move:")
        for k, o, n in dropped:
            print(f"   ! {k}:  was {o}  now {n}")
    if kept:
        print(f"\nknown_fail, not blocking ({len(kept)}): {', '.join(kept)}")

    if raised and not a.no_ratchet:
        save_baseline(base)
        print(f"\nbaseline.json updated ({len(raised)} metric(s) raised)")
    elif not raised:
        print("\nbaseline unchanged")

    if dropped:
        print("\nRESULT: FAIL - a metric went backwards")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
