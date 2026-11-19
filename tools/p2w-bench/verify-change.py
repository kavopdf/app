#!/usr/bin/env python3
"""verify-change.py - measure only the documents an engine change actually moved.

WHY THIS EXISTS. The gate is right and it was unaffordable. `regress.py` wants the whole corpus
measured with the engine as it stands, and a corpus pass is 213 documents at 22-24 per 4.5-minute
sandbox call - nine calls. A fixer slot is one run. So on 19 Nov a run built a real fix that moved
five documents with nothing worse, spent three calls getting to 46 of 213, ran out, reverted it, and
reported "0 documents improved". That is the gate working exactly as designed and the run being
unable to satisfy it, which is the same as no fixer at all.

The gate does not need 213 renders. It needs to know that no document got worse. A document whose
.docx is byte-identical to the one already in RANKING.csv cannot have moved - the writer produced
the same bytes, so the render is the same and the score is the same. On 19 Nov the justified-lines
change touched 25 of 213. Measuring 25 is three minutes; measuring 213 is forty-five.

So this tool:

    1. converts the corpus with the tree as it stands          -> /tmp/vc-after
    2. converts it again with the engine reverted to HEAD      -> /tmp/vc-before
    3. hashes every .docx by CONTENT (a zip carries timestamps, so raw bytes lie)
    4. measures ONLY the documents that differ, both ways
    5. prints better / worse / same, and exits 1 if anything got worse

Step 2 is the expensive half and it is the one that can be skipped: pass --before <dir> with a
.docx set you already have and it goes straight to the diff.

    python3 tools/p2w-bench/verify-change.py                 # full, builds both sides
    python3 tools/p2w-bench/verify-change.py --before /x     # reuse an existing "before" set
    python3 tools/p2w-bench/verify-change.py --list-only     # just say what changed, measure nothing

WHAT IT DOES NOT DO. It does not replace `regress.py`. When the change is done and the run is about
to commit, the full pass still runs - this is for the attempt loop, where a run needs to know in
three minutes whether its idea worked, not in forty-five.
"""
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CORPUS = "/scratch/work/p2w/corpus"
AFTER = "/tmp/vc-after"
BEFORE = "/tmp/vc-before"
RANK = os.path.join(ROOT, "benchmarks", "RANKING.csv")
EV = os.path.join(ROOT, "tools", "engine-verify")
CP = "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"


def sh(cmd, timeout=290, cwd=None):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          timeout=timeout, cwd=cwd or ROOT)


def docx_hash(path):
    """A .docx is a zip and a zip carries timestamps, so hash the CONTENT, not the file."""
    try:
        with zipfile.ZipFile(path) as z:
            h = hashlib.sha256()
            for name in sorted(z.namelist()):
                if name.endswith("/"):
                    continue
                h.update(name.encode())
                h.update(z.read(name))
            return h.hexdigest()
    except Exception:
        return None


def convert(out):
    os.makedirs(out, exist_ok=True)
    r = sh('java -cp "%s" ConvertAll %s %s' % (CP, CORPUS, out), cwd=EV)
    ok = [f for f in os.listdir(out) if f.endswith(".docx")]
    if not ok:
        print(r.stdout[-400:] or r.stderr[-400:])
    return len(ok)


def build(out):
    if not os.path.exists(os.path.join(EV, "out", "ConvertAll.class")):
        print("  building the engine")
        sh("bash tools/p2w-bench/build-engine.sh", timeout=280)
    n = convert(out)
    print("  converted %d documents into %s" % (n, out))
    return n


def changed_names(a, b):
    """Documents whose .docx content differs between two sets."""
    out = []
    for name in sorted(os.listdir(a)):
        if not name.endswith(".docx"):
            continue
        p2 = os.path.join(b, name)
        if not os.path.exists(p2) or docx_hash(os.path.join(a, name)) != docx_hash(p2):
            out.append(name[:-5])
    return out


_P2W = None


def p2w():
    """The instrument, loaded ONCE.

    Loading it per document re-imported the module, and the import re-read the render cache's stamp
    helper - so `conv()` missed the cache the pre-render had just filled and started a fresh
    soffice for every document. Measured 19 Nov: 236 s for ONE document, against 1-2 s when the
    cache hits. One instance, one cache.
    """
    global _P2W
    if _P2W is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("p2w",
                                                      os.path.join(ROOT, "benchmarks", "p2w.py"))
        _P2W = importlib.util.module_from_spec(spec)
        argv, sys.argv = sys.argv, ["p2w.py"]
        try:
            spec.loader.exec_module(_P2W)
        except SystemExit:
            pass
        finally:
            sys.argv = argv
    return _P2W


def measure(name, dx):
    """Score one document, using the same instrument the published table uses."""
    return p2w().measure_doc(os.path.join(CORPUS, name + ".pdf"), dx)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default="", help="an existing .docx set to compare against")
    ap.add_argument("--after", default=AFTER)
    ap.add_argument("--list-only", action="store_true")
    ap.add_argument("--google-candidates", action="store_true",
                    help="print the documents this change improved, one per line")
    ap.add_argument("--skip-convert", action="store_true",
                    help="reuse an existing --after set; a re-run does not re-convert 213")
    ap.add_argument("--budget", type=float, default=240.0, help="seconds for the measuring loop")
    a = ap.parse_args(argv)

    import time
    t0 = time.time()

    if a.google_candidates:
        # Recomputed from the two sets already on disk; no conversion, no measurement.
        pass

    if a.list_only:
        before = a.before or BEFORE
        if not os.path.isdir(before):
            print("no --before set and %s does not exist; run without --list-only once" % before)
            return 2
        names = changed_names(before, a.after)
        print("  %d of %d documents differ" % (len(names), len([f for f in os.listdir(before)
                                                               if f.endswith('.docx')])))
        for n in names[:40]:
            print("    " + n)
        return 0

    # THE AFTER SIDE IS THE TREE AS IT STANDS - that is the change under test.
    if a.skip_convert and os.path.isdir(a.after) and \
            len([f for f in os.listdir(a.after) if f.endswith(".docx")]) >= 200:
        print("  reusing %s (%d documents)" % (a.after,
              len([f for f in os.listdir(a.after) if f.endswith(".docx")])))
    else:
        build(a.after)

    before = a.before
    if not before:
        # THE BEFORE SIDE IS THE SAME TREE WITH THE ENGINE REVERTED. Stash only the engine so the
        # tooling and the corpus survive, build, convert, then put it back. If the stash is empty
        # there is no change to verify and saying so is more useful than a 40-minute pass.
        r = sh("git stash push -- app/src/main/java/com/kavopdf/app/engine/")
        stashed = "No local changes" not in (r.stdout + r.stderr)
        if not stashed:
            print("  the engine tree is clean - there is no change to verify")
            return 0
        try:
            sh("bash tools/p2w-bench/build-engine.sh", timeout=280)
            build(BEFORE)
        finally:
            sh("git stash pop")
            sh("bash tools/p2w-bench/build-engine.sh", timeout=280)
        before = BEFORE

    names = changed_names(before, a.after)
    total = len([f for f in os.listdir(before) if f.endswith(".docx")])
    print("  %d of %d documents changed - only those need measuring" % (len(names), total))
    if not names:
        print("  nothing moved. The change is inert; there is nothing to keep.")
        return 0

    pub = {}
    for row in csv.DictReader(open(RANK, encoding="utf-8")):
        try:
            pub[row["document"]] = float(row["share5"])
        except (KeyError, ValueError):
            pass

    # PRE-RENDER THE CHANGED SET IN ONE BATCH. A cold soffice start per document is 150-190 s;
    # twelve to a call is fifteen. Without this the tool took 190 s for ONE document and a run
    # would spend its whole slot measuring twenty-four. The renders are cached under
    # /scratch/work/p2w/pre keyed on the .docx stamp, so the measuring loop after this is seconds
    # each.
    _m = p2w()
    _m.DOCX = a.after
    _n = _m.prerender(names, time.time() + 150)
    print("  pre-rendered %d of %d changed documents" % (_n, len(names)))

    better, worse, same = [], [], []
    for name in names:
        if time.time() - t0 > a.budget:
            print("  budget reached after %d of %d - re-run with --before %s to carry on"
                  % (len(better) + len(worse) + len(same), len(names), before))
            break
        r = measure(name, os.path.join(a.after, name + ".docx"))
        now = r.get("share5")
        was = pub.get(name)
        if now is None or was is None:
            continue
        if now < was - 0.01:
            better.append((name, was, now))
        elif now > was + 0.01:
            worse.append((name, was, now))
        else:
            same.append((name, was, now))

    print()
    print("  better %d | worse %d | same %d   (%.0fs)" % (len(better), len(worse), len(same),
                                                         time.time() - t0))
    for name, was, now in sorted(better, key=lambda x: x[2])[:12]:
        print("    BETTER %-42s %5.2f -> %5.2f" % (name[:42], was, now))
    for name, was, now in worse:
        print("    WORSE  %-42s %5.2f -> %5.2f" % (name[:42], was, now))
    print()
    if worse:
        print("  VERDICT: REFUSED - %d document(s) got worse. The gate would not take this." % len(worse))
        return 1
    done = len(better) + len(worse) + len(same)
    if done < len(names):
        # A PARTIAL PASS IS NOT A VERDICT. Saying INERT here is how a run concludes its idea failed
        # when it only ran out of seconds - the 19 Nov run did exactly that, at 46 of 213.
        print("  VERDICT: INCOMPLETE - %d of %d measured. Re-run with --before %s; it carries on"
              % (done, len(names), before))
        return 2
    if better:
        print("  VERDICT: KEEP - %d improved, none worse. Now run the full pass to commit." % len(better))
        # LIBREOFFICE SAYS THESE IMPROVED. GOOGLE DECIDES WHETHER THE USER SEES IT.
        #
        # This tool measures with soffice, which honours nearly every construct this engine emits. A
        # change can improve every one of these documents in LibreOffice and improve none of them in
        # Google - measured 19 Nov: LibreOffice 65 open of 213 against Google 7 clean of 84, so the two
        # renderers disagree about 92 % of the corpus. A fix kept on the LibreOffice number alone is a
        # fix aimed at a renderer no user opens.
        #
        # So the improved set is printed, and the brief says to put exactly these through gverify.py
        # before the commit. It is a handful of documents, not the corpus.
        if better:
            print()
            print("  GOOGLE CANDIDATES - put these through gverify.py before you commit:")
            for name, was, now in better:
                print("    %s" % name)
        return 0
    print("  VERDICT: INERT - nothing improved and nothing broke. Not worth a commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
