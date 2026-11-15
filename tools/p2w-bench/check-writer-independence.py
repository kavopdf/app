#!/usr/bin/env python3
"""
check-writer-independence.py - the .txt must be a function of the PDF, not of the .docx write.

WHY THIS EXISTS
    SECTOR 19. DocxWriter.write moved a stamp's paragraphs inside page.blocks - the same list
    TxtWriter walks - so ConvertAll, which writes the .docx first, produced a .txt describing the
    .docx writer's relocations. With the .docx write omitted, 11 of the 211 corpus documents
    produced a DIFFERENT .txt: the same lines, in a different order.

    Nothing caught it, and nothing could have: all seven text checks pair by text, so a reordering
    scores exactly as well one way as the other. Measured: 191/211 all-pass on every one of the
    four .txt variants (docx-first, txt-only, reading order on, reading order off), while 11 files
    differed byte for byte. A check that reads only the text cannot see an order, so this check
    does not read the text - it compares two RUNS of the same PDF.

WHAT IT DOES
    Converts the same corpus twice, in one build:
        A: ConvertAll                      (model pass, .docx, .txt)
        B: ConvertAll -Dp2w.noDocx=true    (model pass, .txt only)
    and compares the .txt of every document byte for byte. Any difference is a document whose
    text output depends on the call order, and the run fails.

    A second pair of runs is not needed for the model pass itself: the .docx side is covered by
    tools/engine-verify/TestWriterIndependence.java, which fingerprints the whole Result before
    and after the write and fails if anything moved - including a field this script cannot see.

USAGE
    python3 tools/p2w-bench/check-writer-independence.py <pdfDir> [--work DIR] [--limit N]
                                                          [--java-cp CP] [--quiet]

    <pdfDir>     a folder of .pdf files (the corpus, unzipped flat)
    --work       where the two output trees go (default: a fresh temp dir, kept on failure)
    --limit N    the first N documents, for a fast loop while fixing
    --java-cp    classpath (default: out:libs/... relative to tools/engine-verify)
    --compare-only A B
                 skip both conversions and compare two output trees that already exist,
                 A written with the .docx and B without it. This is how the check itself is
                 validated: on the 211-document corpus as HEAD left it, A and B differ on 11
                 documents; after the fix they are identical on 211.

EXIT
    0  every document's .txt is identical with and without the .docx write
    1  at least one document's .txt changed
    2  could not run (no build, no corpus, a conversion failure)
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EVDIR = os.path.normpath(os.path.join(HERE, "..", "engine-verify"))
DEFAULT_CP = "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"


def java_bin():
    for c in (os.environ.get("JAVA_HOME", "") + "/bin/java", "/scratch/work/.p2w-jdk/jdk/bin/java"):
        if c and os.path.exists(c):
            return c
    return shutil.which("java")


def convert(src, out, cp, java, no_docx, quiet):
    os.makedirs(out, exist_ok=True)
    cmd = [java]
    if no_docx:
        cmd.append("-Dp2w.noDocx=true")
    cmd += ["-cp", cp, "ConvertAll", src, out]
    r = subprocess.run(cmd, cwd=EVDIR, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
        return None
    if not quiet:
        tail = [l for l in r.stdout.strip().split("\n") if l.startswith("done:")]
        print("   " + (tail[-1] if tail else "converted"))
    failed = [l for l in r.stdout.split("\n") if "\tFAILED" in l or l.startswith("EMPTY")]
    if failed:
        sys.stderr.write("conversion failures:\n  " + "\n  ".join(failed[:10]) + "\n")
        return None
    return r.stdout


def txts(d):
    return {f[:-4]: os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".txt")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="?", default=None)
    ap.add_argument("--work", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--java-cp", default=DEFAULT_CP)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--compare-only", nargs=2, metavar=("A", "B"), default=None,
                    help="skip the two conversions and compare two output folders that already "
                         "exist - A converted with the .docx write, B without it")
    a = ap.parse_args()

    if a.compare_only:
        return compare(a.compare_only[0], a.compare_only[1])
    if not a.pdfs:
        print("no corpus given (or use --compare-only A B)", file=sys.stderr)
        return 2

    java = java_bin()
    if not java:
        print("no java - set JAVA_HOME", file=sys.stderr)
        return 2
    src = os.path.abspath(a.pdfs)
    pdfs = sorted(f for f in os.listdir(src) if f.lower().endswith(".pdf"))
    if a.limit:
        pdfs = pdfs[:a.limit]
    if not pdfs:
        print("no pdfs in " + src, file=sys.stderr)
        return 2

    work = a.work or tempfile.mkdtemp(prefix="p2w-indep-")
    a_dir = os.path.join(work, "docx-first")
    b_dir = os.path.join(work, "txt-only")
    for d in (a_dir, b_dir):
        shutil.rmtree(d, ignore_errors=True)

    # A staged folder, so --limit converts exactly those documents.
    stage = os.path.join(work, "pdfs")
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    for n in pdfs:
        os.symlink(os.path.join(src, n), os.path.join(stage, n))

    print("A  .docx + .txt   (%d documents)" % len(pdfs))
    if convert(stage, a_dir, a.java_cp, java, False, a.quiet) is None:
        return 2
    print("B  .txt only")
    if convert(stage, b_dir, a.java_cp, java, True, a.quiet) is None:
        return 2

    return compare(a_dir, b_dir)


def compare(a_dir, b_dir):
    ta, tb = txts(a_dir), txts(b_dir)
    missing = sorted(set(ta) ^ set(tb))
    differ = []
    for k in sorted(set(ta) & set(tb)):
        da = open(ta[k], "rb").read()
        db = open(tb[k], "rb").read()
        if da != db:
            differ.append((k, len(da), len(db), hashlib.sha256(da).hexdigest()[:12],
                           hashlib.sha256(db).hexdigest()[:12]))

    print()
    print("documents compared : %d" % len(set(ta) & set(tb)))
    print("only in one run    : %d %s" % (len(missing), missing[:5] if missing else ""))
    print("txt differs        : %d" % len(differ))
    for k, na, nb, ha, hb in differ[:30]:
        print("   %-46s %6d -> %6d bytes  %s -> %s" % (k, na, nb, ha, hb))
    if differ:
        print()
        print("FAIL: the .txt depends on whether the .docx write ran. A writer is editing the")
        print("      model. Run TestWriterIndependence to see which field moved, and write it on")
        print("      the writer's own copy (PdfToWord.Page.copyForWrite).")
        return 1
    if missing:
        print("FAIL: a document produced a .txt in one run and not the other.")
        return 1
    print()
    print("PASS: every .txt is byte-identical with and without the .docx write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
