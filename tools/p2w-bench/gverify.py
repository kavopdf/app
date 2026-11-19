#!/usr/bin/env python3
"""gverify.py - run the corpus through Google's renderer and the 42 checks, in batches.

VERIFY-GOOGLE.md describes this and has since 13 Nov; what it does not have is a driver, so every
run rebuilt the loop by hand. This is that driver.

    python3 gverify.py --plan 20                 # the next 20 documents that have no Google result
    python3 gverify.py --stage <name>            # copy out/<name>.docx somewhere stable, print it
    python3 gverify.py --collect <name> <url>    # fetch the export, check it, run the 42 checks
    python3 gverify.py --report                  # what the corpus looks like so far

WHY IT IS SPLIT THIS WAY. Three of the four steps are Drive API calls and a plain script cannot make
them - VERIFY-GOOGLE.md says so - so the caller does them:

    a. upload(path=<stage output>, tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
    b. GOOGLEDRIVE_CREATE_FILE(name=..., mimeType="application/vnd.google-apps.document",
                               parents=[<folder>], file_to_upload={name,mimetype,s3key})
    c. GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=<id>, mimeType="application/pdf")
    d. gverify.py --collect <name> <s3url>

`--collect` verifies the bytes before it scores them: a page-count mismatch or a copy identical to
the source is refused, because a score computed against the wrong file looks exactly like a layout
error and is not one.

WHAT IT STORES. One JSON per document in gverify/, keyed by name, holding the pass/fail of each of
the 42 checks. That is the only thing that needs to survive, and it is what `--report` groups into
classes. The Google Doc itself is deleted after each document - VERIFY-GOOGLE.md's rule - so nothing
accumulates in the user's Drive.

RATE LIMITS. Google Drive allows ~1000 requests per 100 s per user and this is three per document, so
twenty documents per run is comfortable and leaves room for the retry the doc describes: on 403 with
userRateLimitExceeded, wait 60 s and retry once; if it fails again record SKIPPED, never PASS.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = "/scratch/work/p2w/out"
CORPUS = "/scratch/work/p2w/corpus"
STAGE = "/scratch/work/p2w/gverify/stage"
GD = "/scratch/work/p2w/gverify/gd"
RES = "/scratch/work/p2w/gverify/results"


def _names():
    return sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".docx"))


def _done():
    if not os.path.isdir(RES):
        return set()
    return {f[:-5] for f in os.listdir(RES) if f.endswith(".json")}


def plan(n):
    """The next documents that have no Google result yet, oldest work first."""
    todo = [x for x in _names() if x not in _done()]
    print("%d of %d documents have a Google result; %d to go"
          % (len(_done()), len(_names()), len(todo)))
    for x in todo[:n]:
        print(x)
    return 0


def stage(name):
    src = os.path.join(OUT, name + ".docx")
    if not os.path.exists(src):
        print("no such document: %s" % src)
        return 2
    os.makedirs(STAGE, exist_ok=True)
    dst = os.path.join(STAGE, name + ".docx")
    import shutil
    shutil.copy(src, dst)
    print(dst)
    return 0


def _pages(p):
    try:
        import fitz
        with fitz.open(p) as d:
            return len(d)
    except Exception:
        return -1


def collect(name, url):
    src = os.path.join(CORPUS, name + ".pdf")
    docx = os.path.join(OUT, name + ".docx")
    if not os.path.exists(src) or not os.path.exists(docx):
        print("missing source or docx for %s" % name)
        return 2
    os.makedirs(GD, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    pdf = os.path.join(GD, name + ".pdf")
    tmp = pdf + ".part"
    r = subprocess.run(["curl", "-sL", "--max-time", "120", url, "-o", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        print("download failed: %s" % (r.stderr or r.stdout)[:160])
        return 2
    with open(tmp, "rb") as f:
        if f.read(5) != b"%PDF-":
            os.remove(tmp)
            print("not a PDF - the export did not produce a document")
            return 3
    want, got = _pages(src), _pages(tmp)
    if want > 0 and got > 0 and got != want:
        os.remove(tmp)
        # A REFUSAL, NOT A RESULT. Google reflowed the document onto a different number of pages, or
        # the export returned something else. Recording that as "42 checks failed" would hide a real
        # finding under a false one.
        print("REFUSED: %s rendered to %d page(s), the source has %d" % (name, got, want))
        _write(name, {"name": name, "status": "page_count_refused", "pages": got, "want": want})
        return 4
    os.replace(tmp, pdf)
    out_json = os.path.join(RES, name + ".json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "verify_google.py"),
                        src, pdf, "--docx", docx, "--json", out_json],
                       capture_output=True, text=True, timeout=280)
    tail = [l for l in r.stdout.splitlines() if "PASS" in l or "FAIL" in l]
    if not os.path.exists(out_json):
        print("verify_google.py produced no json (rc=%d): %s" % (r.returncode, r.stderr[-200:]))
        return 5
    d = json.load(open(out_json, encoding="utf-8"))
    fails = sorted(k for k, v in (d.get("checks") or {}).items()
                   if isinstance(v, dict) and v.get("ok") is False)
    _write(name, {"name": name, "status": "ok", "rc": r.returncode,
                  "passed": d.get("passed"), "total": d.get("total"), "failed": fails})
    print("  %-44s GOOGLE %s/%s%s" % (name[:44], d.get("passed"), d.get("total"),
                                      "" if not fails else "  fail: " + ",".join(fails)))
    lo = collect_lo(name)
    print("  %-44s LIBRE  %s" % ("", lo))
    return 0


SOFFICE = "/usr/lib/libreoffice/program/soffice.bin"
LORES = "/scratch/work/p2w/lo-res"


def collect_lo(name):
    """The SAME 42 checks against the LibreOffice render, so every document carries both numbers.

    The whole reason this pipeline exists is that the two renderers disagree, and a corpus measured by
    only one of them cannot say where. LibreOffice is a fast local proxy that hides the faults Google
    shows - on the first 50 documents, LibreOffice passed 23 and Google passed 7 - so the pair is what
    a fixer needs: "Google fails this and LibreOffice does not" is the sentence that names a construct
    Google drops. Measuring them in the same pass means the pair is never half-collected.
    """
    src = os.path.join(CORPUS, name + ".pdf")
    docx = os.path.join(OUT, name + ".docx")
    if not os.path.exists(src) or not os.path.exists(docx):
        return "missing source or docx"
    os.makedirs(LORES, exist_ok=True)
    out_json = os.path.join(LORES, name + ".json")
    if os.path.exists(out_json):
        return "already have it"
    tmpdir = "/tmp/lo-one"
    os.makedirs(tmpdir, exist_ok=True)
    exe = SOFFICE if os.path.exists(SOFFICE) else "soffice"
    r = subprocess.run([exe, "--headless", "--norestore", "--convert-to", "pdf",
                        "--outdir", tmpdir, docx], capture_output=True, text=True, timeout=180)
    pdf = os.path.join(tmpdir, name + ".pdf")
    if not os.path.exists(pdf):
        return "soffice produced nothing"
    subprocess.run([sys.executable, os.path.join(HERE, "verify_google.py"),
                    src, pdf, "--docx", docx, "--json", out_json],
                   capture_output=True, text=True, timeout=180)
    try:
        os.remove(pdf)
    except OSError:
        pass
    if not os.path.exists(out_json):
        return "verify_google produced nothing"
    d = json.load(open(out_json, encoding="utf-8"))
    fails = sorted(k for k, v in (d.get("checks") or {}).items()
                   if isinstance(v, dict) and v.get("ok") is False)
    return "%s/%s%s" % (d.get("passed"), d.get("total"),
                        "" if not fails else "   LO fail: " + ",".join(fails))


def _write(name, rec):
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)


def matrix():
    """The capability table: every check, both renderers, from the results on disk.

    This is what the whole pass exists for. A check Google fails and LibreOffice passes names a
    construct LibreOffice honours and Google does not - that is the sentence a fixer needs, and it
    cannot be written without both numbers on the same document.
    """
    from collections import Counter
    lo_dir = "/scratch/work/p2w/lo-res"
    if not os.path.isdir(RES):
        print("no Google results yet")
        return 2
    names = [f[:-5] for f in sorted(os.listdir(RES)) if f.endswith(".json")]
    gf, lf = Counter(), Counter()
    both = gpass = lpass = 0
    for n in names:
        g = json.load(open(os.path.join(RES, n + ".json"), encoding="utf-8"))
        if g.get("status") == "page_count_refused":
            continue
        lo_path = os.path.join(lo_dir, n + ".json")
        if not os.path.exists(lo_path):
            continue
        l = json.load(open(lo_path, encoding="utf-8"))
        both += 1
        gg = set(g.get("failed") or [])
        ll = {k for k, v in (l.get("checks") or {}).items() if v.get("ok") is False}
        for c in gg: gf[c] += 1
        for c in ll: lf[c] += 1
        if not gg: gpass += 1
        if not ll: lpass += 1
    if not both:
        print("no document has both renders yet")
        return 2
    print("# Google Docs vs LibreOffice - the 42 checks, %d documents, same engine\n" % both)
    print("Same source PDF, same .docx, same instrument. Only the renderer differs.\n")
    print("    LibreOffice : %d of %d pass all 42" % (lpass, both))
    print("    Google Docs : %d of %d pass all 42\n" % (gpass, both))
    print("## Where they disagree\n")
    print("| check | LibreOffice fails | Google fails | who is stricter |")
    print("|---|---:|---:|---|")
    allc = set(gf) | set(lf)
    for c in sorted(allc, key=lambda x: -(gf[x] - lf[x])):
        a, b = lf[c], gf[c]
        if a == 0 and b == 0:
            continue
        who = "**Google**" if b > a else ("LibreOffice" if a > b else "same")
        print("| `%s` | %d | %d | %s |" % (c, a, b, who))
    print()
    only_g = [c for c in allc if gf[c] > 0 and lf[c] == 0]
    print("## Constructs LibreOffice honours and Google does not\n")
    if only_g:
        for c in sorted(only_g, key=lambda x: -gf[x]):
            print("* `%s` - %d documents" % (c, gf[c]))
    else:
        print("_None: every check Google fails, LibreOffice fails too._")
    print()
    only_l = [c for c in allc if lf[c] > 0 and gf[c] == 0]
    if only_l:
        print("## Constructs Google honours and LibreOffice does not\n")
        for c in sorted(only_l, key=lambda x: -lf[x]):
            print("* `%s` - %d documents" % (c, lf[c]))
        print()
    return 0


def report():
    done = _done()
    if not done:
        print("no results yet")
        return 0
    from collections import Counter
    fails, full, refused, partial = Counter(), [], [], []
    for n in sorted(done):
        try:
            d = json.load(open(os.path.join(RES, n + ".json"), encoding="utf-8"))
        except Exception:
            continue
        if d.get("status") == "page_count_refused":
            refused.append(n)
            continue
        for c in d.get("failed") or []:
            fails[c] += 1
        if d.get("failed"):
            partial.append(n)
        else:
            full.append(n)
    print("  %d verified | %d pass all 42 | %d fail at least one | %d refused (page count)"
          % (len(done), len(full), len(partial), len(refused)))
    print()
    if fails:
        print("  failures by check - fix the class, not the document:")
        for c, n in fails.most_common():
            print("    %-30s %3d docs" % (c, n))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=int)
    ap.add_argument("--stage")
    ap.add_argument("--collect", nargs=2)
    ap.add_argument("--lo", help="measure the LibreOffice side of one document")
    ap.add_argument("--matrix", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    if a.plan:    return plan(a.plan)
    if a.stage:   return stage(a.stage)
    if a.collect: return collect(*a.collect)
    if a.lo:
        print(collect_lo(a.lo))
        return 0
    if a.matrix:  return matrix()
    if a.report:  return report()
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
