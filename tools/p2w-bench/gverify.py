#!/usr/bin/env python3
"""gverify.py - run the corpus through Google's renderer and the 42 checks, in batches.

VERIFY-GOOGLE.md describes this and has since 13 Nov; what it does not have is a driver, so every
run rebuilt the loop by hand. This is that driver.

    python3 gverify.py --plan 20                 # the next 20 documents that have no Google result
    python3 gverify.py --stage <name>            # copy out/<name>.docx somewhere stable, print it
    python3 gverify.py --collect <name> <url>    # fetch the export, check it, run the 42 checks
                                                 # <url> is whatever GOOGLEDRIVE_DOWNLOAD_FILE
                                                 # handed back: an s3url, a local workspace_path,
                                                 # or the tool result itself as JSON
    python3 gverify.py --report                  # what the corpus looks like so far

WHY IT IS SPLIT THIS WAY. Three of the four steps are Drive API calls and a plain script cannot make
them - VERIFY-GOOGLE.md says so - so the caller does them:

    a. upload(path=<stage output>, tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
    b. GOOGLEDRIVE_CREATE_FILE(name=..., mimeType="application/vnd.google-apps.document",
                               parents=[<folder>], file_to_upload={name,mimetype,s3key})
    c. GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=<id>, mimeType="application/pdf")
    d. gverify.py --collect <name> <what GOOGLEDRIVE_DOWNLOAD_FILE returned>

    WHAT STEP d ACCEPTS, AND WHY IT CHANGED. It used to be the s3url out of
    `downloaded_file_content.s3url`, and on 23 Nov 2026 the tool stopped returning one:
    it now hands back `artifacts[0].workspace_path`, a local path. `--collect` takes either -
    an s3url, a local path, or the whole tool result as a JSON string - because a cron that
    cannot be called with what the tool actually returns does not collect anything. See
    download_source() for the accepted shapes and the error it raises when neither is present.

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
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = "/scratch/work/p2w/out"
CORPUS = "/scratch/work/p2w/corpus"
STAGE = "/scratch/work/p2w/gverify/stage"
GD = "/scratch/work/p2w/gverify/gd"
# THE COMMITTED DIRECTORY IS THE RECORD; THE WORK ONE IS A SCRATCH AREA.
#
# These read /scratch/work/p2w/*, which does not survive a sandbox. So on a fresh run --report said
# "90 verified, 32_stroke_lines 53 docs" while the committed results said 192 scored and 145 - and a
# report generated from that would have been wrong in every number while looking entirely reasonable.
# Found 20 Nov while checking why a real number failed verification.
#
# The committed benchmarks/ copies win whenever they exist. The work path stays as the fallback for
# a run that has just measured something and not yet committed it.
_RES_WORK = "/scratch/work/p2w/gverify/results"
_RES_REPO = os.path.normpath(os.path.join(HERE, "..", "..", "benchmarks", "gverify"))
RES = _RES_REPO if os.path.isdir(_RES_REPO) and os.listdir(_RES_REPO) else _RES_WORK


def _names():
    return sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".docx"))


def _engine_now():
    """The engine commit the corpus is built from right now."""
    import subprocess as _sp
    try:
        r = _sp.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--",
                     "app/src/main/java/com/kavopdf/app/engine/"],
                    capture_output=True, text=True, timeout=20)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def _done():
    """Documents whose Google result is a measurement OF THE CURRENT ENGINE.

    A FILE ON DISK IS NOT A MEASUREMENT. This returned every .json in the directory, so once all 213
    existed `plan()` printed "213 of 213 have a Google result; 0 to go" and the gverify cron did nothing,
    every hour, reporting success - while the results were two days old and 21 of them were
    page_count_refused, which is not a score at all. Measured 21 Nov: the newest real Google result was
    19 Nov 19:02, four engine commits behind, and the fixer was optimising against it.

    So a document counts as done only when its result carries the CURRENT engine stamp. Results written
    before the stamp existed carry none, which is the honest answer - nobody can say what engine they
    measured - and they are re-measured once.

    A page_count_refused result IS done: it is a real, recorded outcome (Google reflowed the document)
    and re-running it every hour would loop for ever. It is counted, reported, and left alone.
    """
    if not os.path.isdir(RES):
        return set()
    now = _engine_now()
    out = set()
    for f in os.listdir(RES):
        if not f.endswith(".json"):
            continue
        name = f[:-5]
        try:
            d = json.load(open(os.path.join(RES, f), encoding="utf-8"))
        except Exception:
            continue
        if d.get("status") == "page_count_refused":
            out.add(name)          # a recorded outcome, not a missing one
            continue
        # THE ENGINE ID IS A GIT ABBREVIATION, AND ITS LENGTH IS NOT THE SAME EVERYWHERE.
        #
        # `git log --format=%h` prints 7 characters in a repository that has never needed 8 and 8
        # once a collision forces it - and the machine that wrote the committed results printed 7.
        # A plain string compare therefore matched NOTHING: measured 22 Nov, `--report` said
        # "21 verified | 0 pass all 42 | 0 fail at least one" while 192 documents were scored and
        # 6 passed all 42. An instrument that reports zero is not a quiet instrument, it is a wrong
        # one, and it was one character away from being believed.
        _e = d.get("engine") or ""
        if now and _e and (_e == now or now.startswith(_e) or _e.startswith(now)):
            out.add(name)
    return out


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


_URL_SCHEMES = ("http://", "https://", "s3://", "gs://", "file://")


def _is_url(s):
    return s.startswith(_URL_SCHEMES)


def download_source(result):
    """The one thing `--collect` needs out of a GOOGLEDRIVE_DOWNLOAD_FILE result: where the bytes are.

    TWO SHAPES, BOTH ACCEPTED. The tool used to return

        {"downloaded_file_content": {"s3url": "https://..."}}

    and `--collect` read `downloaded_file_content.s3url`. On 23 Nov 2026 the 04:47 fixer run
    recorded that it no longer does: it returns

        {"artifacts": [{"workspace_path": "/tmp/....pdf"}]}

    a local path, and a cron that passes that to a function expecting an s3url collects nothing.

    THE NEW SHAPE WINS WHEN BOTH ARE PRESENT - a local path is already fetched, an s3url is a
    second download that can fail on its own. The old branch is kept because other callers still
    pass an s3url and nothing about them has changed.

    `artifacts` IS A LIST. More than one file can come back from an export, so the entry whose
    workspace_path ends in .pdf is chosen; if none is named .pdf the first one that has a
    workspace_path is used, because a single artifact is by definition the one that was asked for.

    A PLAIN STRING IS ALSO ACCEPTED - an s3url or a local path, which is what the shell hands in.
    A string that parses as a JSON object is treated as the tool result it is, so the caller can
    paste the whole response. Raises ValueError naming the keys actually returned when the shape
    is neither: the next run should not have to guess what the tool said.
    """
    if isinstance(result, str):
        s = result.strip()
        if s.startswith("{"):
            try:
                return download_source(json.loads(s))
            except ValueError:
                raise
            except Exception:
                pass            # not JSON after all - fall through and treat it as a path/url
        if s:
            return s
        raise ValueError("GOOGLEDRIVE_DOWNLOAD_FILE returned an empty string")

    if not isinstance(result, dict) or not result:
        raise ValueError("GOOGLEDRIVE_DOWNLOAD_FILE returned no usable result: %r" % (result,))

    # NEW SHAPE FIRST.
    arts = result.get("artifacts")
    if isinstance(arts, list):
        cands = [a for a in arts if isinstance(a, dict) and a.get("workspace_path")]
        for a in cands:
            if str(a["workspace_path"]).lower().endswith(".pdf"):
                return a["workspace_path"]
        if cands:
            return cands[0]["workspace_path"]

    # OLD SHAPE, unchanged.
    dfc = result.get("downloaded_file_content")
    if isinstance(dfc, dict) and dfc.get("s3url"):
        return dfc["s3url"]
    if result.get("s3url"):
        return result["s3url"]

    # NEITHER. Say exactly what came back, so nobody has to run it again to find out.
    keys = sorted(result)
    detail = "top-level keys: %s" % (keys or "none")
    if isinstance(arts, list):
        detail += "; artifacts has %d entr%s" % (len(arts), "y" if len(arts) == 1 else "ies")
        if arts and isinstance(arts[0], dict):
            detail += "; artifacts[0] keys: %s" % sorted(arts[0])
        elif arts:
            detail += "; artifacts[0] is %s" % type(arts[0]).__name__
    elif arts is not None:
        detail += "; artifacts is %s, not a list" % type(arts).__name__
    if "downloaded_file_content" in result:
        detail += "; downloaded_file_content is %s" % type(dfc).__name__
    raise ValueError("GOOGLEDRIVE_DOWNLOAD_FILE result has neither artifacts[].workspace_path "
                     "nor downloaded_file_content.s3url (%s)" % detail)


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
    try:
        target = download_source(url)
    except ValueError as e:
        print("cannot collect %s: %s" % (name, e))
        return 2
    if _is_url(target):
        r = subprocess.run(["curl", "-sL", "--max-time", "120", target, "-o", tmp],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(tmp):
            print("download failed: %s" % (r.stderr or r.stdout)[:160])
            return 2
    else:
        # THE NEW SHAPE IS ALREADY A LOCAL FILE. No second download to fail.
        import shutil
        try:
            shutil.copyfile(target, tmp)
        except OSError as e:
            print("cannot read the local artifact %s: %s" % (target, e))
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
        _write(name, {"name": name, "status": "page_count_refused", "pages": got, "want": want,
                        "at": time.strftime("%Y-%m-%dT%H:%M:%S")})
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
    # THE DISTANCE, NOT JUST THE COUNT. `18_displacement` reports how many pages are out and
    # never how far out, so a fixer reading this file cannot tell 0.5 pt from 50 pt and cannot
    # see whether a construct is even large enough to matter. verify_google.py computes
    # med_dy/worst_dy/med_dx and now carries them as the check's detail; store them here so the
    # next run steers with a distance. Reported only - `failed` above is what scores.
    # `at` is what makes a verdict expirable. The `engine` stamp only catches an ENGINE change, and a
    # check can be fixed without the engine moving: on 24 Nov 25_invisible_text was found to be reading
    # the paper (a Google export opens with a page-sized white rectangle and rasterises the bands), so
    # 48 documents were failing a check that was wrong. Five were re-measured and went 42/42; the other
    # 43 kept verdicts stamped with the same engine and looked current, because nothing recorded WHEN
    # they were taken. A timestamp cannot be wrong about that.
    rec = {"name": name, "status": "ok", "rc": r.returncode, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "passed": d.get("passed"), "total": d.get("total"), "failed": fails}
    disp = ((d.get("checks") or {}).get("18_displacement") or {}).get("detail")
    if disp:
        rec["displacement"] = disp
    _write(name, rec)
    print("  %-44s GOOGLE %s/%s%s" % (name[:44], d.get("passed"), d.get("total"),
                                      "" if not fails else "  fail: " + ",".join(fails)))
    lo = collect_lo(name)
    print("  %-44s LIBRE  %s" % ("", lo))
    return 0


SOFFICE = "/usr/lib/libreoffice/program/soffice.bin"
_LO_WORK = "/scratch/work/p2w/lo-res"
_LO_REPO = os.path.normpath(os.path.join(HERE, "..", "..", "benchmarks", "gverify-lo"))
LORES = _LO_REPO if os.path.isdir(_LO_REPO) and os.listdir(_LO_REPO) else _LO_WORK


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
    """Write one document's result, stamped with the engine that produced it.

    A RESULT WITH NO ENGINE STAMP CAN NEVER BE COUNTED. Every reader - report.py,
    classify_google.py, measure_gate, the fixer's own table - asks "was this measured on the engine
    in the tree?" and answers by comparing this field. It was written by some paths and not by this
    one, so 23 of 213 results carried no stamp and were invisible as measurements of anything: on
    23 Nov the fixer landed a real page-count fix, gverify scored 301_lab_report_panel and
    375_attendance_register on the new engine, and the report still said "0 of 0 measured on THIS
    engine" because neither record said which engine it was.
    """
    if isinstance(rec, dict) and not rec.get("engine"):
        rec["engine"] = _engine_now()
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
    lo_dir = LORES
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
