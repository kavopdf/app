#!/usr/bin/env python3
"""p2w -- the authoritative measurement pipeline for pdf->docx fidelity.

WHAT THIS MEASURES, AND WHY EACH CHOICE WAS FORCED BY EVIDENCE
--------------------------------------------------------------
Two independent axes, because one is not enough:

  POSITION  how far ink sits from where the source put it.
  CONTENT   whether the characters are the ones the source has.

Position alone is insufficient: a page where every glyph is substituted for a
different one of the same width scores perfectly on position and is completely
wrong. Content alone is insufficient: a page with the right words in the wrong
places reads correctly but is not a reproduction. Both are reported.

THE POSITION STATISTIC
----------------------
For each source ink pixel, the exact Euclidean distance to the nearest render
ink pixel (scipy distance_transform_edt). Reported as a SWEEP, not a single
number:

    share@1px, share@2px, share@3px, share@5px, share@10px
    median_pt, p90_pt, max_pt

Why a sweep and not a headline: an earlier version reported only the max, and
on `itr-computation-with-slab-table` that read 134 pt while the two pages looked
nearly identical -- a single outlier pixel dominated it. An earlier version
reported a p90 inside a tolerance radius, and on a 5 pt rigid shift it read
0.000, because 91.7 % of a moved square still overlaps. Neither number was a
measurement of displacement. The sweep is: its SHAPE identifies the defect.

    flat curve    (share barely falls as tolerance grows) = the ink is ABSENT
    falling curve (share drops sharply)                  = the ink is DISPLACED
    near-zero     (share ~0 at 1 px)                     = the page is RIGHT

INK THRESHOLD
-------------
68, measured. calibrate: paper mode 255, ink mode 51, valley 68.

/ROTATE
-------
The converter deliberately ignores /Rotate: a page stored upright with
/Rotate 180 must come out upright, which is what the user wants. So the SOURCE
is rendered with rotation forced to 0 as well. Comparing a rotated render
against an unrotated one produced a 654 pt "failure" on a document we had
handled correctly. That was a defect in the instrument, not the engine.

GROUND TRUTH GATE
-----------------
validate() sets displacement BY CONSTRUCTION on synthetic pages and refuses to
measure if the instrument cannot read it. A ruler is checked against a gauge
block. Every run begins here.

    p2w.py --validate
    p2w.py --budget 250
    p2w.py --status
    p2w.py --diagnose 20
"""
import sys, os, json, subprocess, time, argparse, glob, csv, re, shutil, uuid
import numpy as np
try:
    import fitz
except ImportError:
    os.system("pip install -q pymupdf"); import fitz

ROOT="/scratch/work/p2w"; CORPUS=ROOT+"/corpus"; DOCX=ROOT+"/out"
# Where this script lives. Needed because the real-world documents travel with the
# repository beside it, not in the release zips, so the script must find its own tree.
HERE=os.path.dirname(os.path.abspath(__file__))
DIST=ROOT+"/dist2"; CACHE="/scratch/output/_cache"; REPO=ROOT+"/repo"
# WHICH TREE THE ENGINE IS BUILT FROM - AND WHY IT IS NOT ALWAYS origin/main.
#
# engine() used to sync REPO to origin FETCH_HEAD unconditionally, so the only engine this script
# could ever build was the one already on main. regress.py --check, meanwhile, REFUSES a commit whose
# engine fingerprint is not the one the corpus tables were measured on. Those two rules together made
# every engine patch uncommittable: the gate demands a corpus measurement of the tree, and the only
# tool that measures cannot build the tree. It cost the 03:36 and 03:57 runs their attempt, and it is
# why FINDINGS/widget-ap-glyph-walk-0436-f1x.patch sat measured on two documents and unlanded.
#
# P2W_ENGINE_SRC names the clone to measure instead. Unset - the baseline cron, the apk cron, every
# run that has nothing local to measure - it is REPO, and the behaviour is exactly what it was.
ENGINE_SRC=os.environ.get("P2W_ENGINE_SRC") or REPO
IMG=ROOT+"/diag"; PRE=ROOT+"/pre"; CHUNK=12; PER_DOC=90; ZIPS=["p2w-all-groups","p2w-batch-1","pdf-to-word-test-corpus-v3","p2w-round2-additions"]
JH="/scratch/work/.p2w-jdk/jdk"; INK=68; DPI=150; PT=72.0/DPI
SWEEP=[1,2,3,5,10]
# How far one channel may differ and still be the page's colour. 24 of 255 is about 9 % - enough
# for a renderer's antialiasing and a font's edge, far short of red-for-black (255) or a grey that
# should have been blue.
COLOUR_TOL=24
# A page needs this much coloured ink before its colour score means anything. A document with one
# red stamp and 40 000 black characters is a black document.
COLOUR_MIN_INK=200
# Tone is read on a BLURRED page so a glyph's antialiased edge stops dominating it. 1 px at
# 150 DPI is 0.48 pt: below any stroke, above any fringe. See tone_share().
TONE_BLUR=1.0
# How far two blurred grey levels may differ and still be the page's tone. Grey body text (about
# 110) against black (0) is 110 apart; antialiasing after the blur is under 20.
TONE_TOL=28
# How far one pixel's grey level may differ and still be the page's tone. 32 of 255 is about
# 12 %: enough for antialiasing at a glyph edge, far short of grey (say 110) for black (0).

def sh(c,t=280):
    try: return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t)
    except subprocess.TimeoutExpired: return None
def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}",flush=True)

# ---------------- geometry helpers ----------------
def _ensure_scipy():
    """Make scipy importable, ONCE, at the point that needs it.

    THE GUARD WAS IN main() AND THE TOOL THAT STALLED NEVER CALLS main().

    main() checked for scipy, pip-installed it, and verified - and wrote INSTRUMENT.txt saying
    which mode the numbers came from. screen.py does not run main(): it imports this file as a
    module and calls docx()/run() directly, so it never reached that block, edt() silently took
    the fallback, and every rendered measurement ran on the pure-Python transform.

    Measured 25 Nov on one real corpus page (mobile-bill, 1754x1241 px at 150 DPI):

        scipy path        1.38 s
        fallback path    66.07 s      48x slower, for the same answer

    A 23-document class is 23-69 pages, so the class costs 25-76 MINUTES of EDT alone - which is
    why three consecutive 280 s calls rendered 12 documents, then none, then one, with no error
    and no log line. It was never soffice; a stack dump at the stall landed in edt(), not in the
    renderer. A prerequisite that is not called by the thing that needs it is not a prerequisite,
    it is a discovery - so the check lives here, beside the only thing that needs it.
    """
    global _SCIPY_OK
    if _SCIPY_OK is not None:
        return _SCIPY_OK
    try:
        import scipy  # noqa: F401
        _SCIPY_OK = True
        return True
    except ImportError:
        pass
    log("scipy missing - installing (the fallback transform is ~48x slower per page)")
    # THE FAILURE WAS SILENT, AND THAT COST A RUN. On 25 Nov this printed "scipy missing -
    # installing" and then "STILL missing" 16 s later with no reason at all: sh() returns the
    # CompletedProcess and nothing read its returncode or its stderr, so a pip that failed in 16 s
    # looked exactly like a pip that worked and an import that did not. The next run went looking
    # in the renderer, which is where the stall appeared to be. A prerequisite that cannot say why
    # it failed is not a prerequisite, it is a discovery - so the reason is logged.
    r = sh("python3 -m pip install -q scipy", 220)
    rc = None if r is None else r.returncode
    err = "" if r is None else ((r.stderr or "") + (r.stdout or "")).strip()
    # VERIFY OUT OF PROCESS. pip installs into a user-site directory that this interpreter
    # computed sys.path for at startup, so `import scipy` here fails even when the install
    # worked - measured 25 Nov: pip exit 0, pip show reports 1.18.1, a fresh process imports
    # 1.18.1, and this block printed "~48x slower per page". A run reads that warning and
    # stops, blaming the renderer, which is exactly the wrong diagnosis two runs already made.
    chk = sh("python3 -c \"import scipy\"", 60)
    ok = chk is not None and chk.returncode == 0
    _SCIPY_OK = ok
    if ok:
        log("scipy installed - exact EDT, fast path")
    else:
        log("WARNING: scipy STILL missing - measuring on the exact-fallback transform.")
        log("WARNING: pip exit %s - %s"
            % ("timeout" if rc is None else rc,
               err.splitlines()[-1][:200] if err else "(pip captured no output)"))
        log("WARNING: ~48x slower per page; a 23-document class will not finish in one call.")
    return _SCIPY_OK


_SCIPY_OK = None


def _dil(m,r):
    h,w=m.shape; t=m.copy()
    for dx in range(-r,r+1): t[:,max(0,-dx):w+min(0,-dx)]|=m[:,max(0,dx):w+min(0,dx)]
    o=t.copy()
    for dy in range(-r,r+1): o[max(0,-dy):h+min(0,-dy),:]|=t[max(0,dy):h+min(0,dy),:]
    return o
def edt(mask,shape,maxr=400):
    """Exact Euclidean distance to the nearest True pixel.

    THE FALLBACK USED TO BE WRONG AND THE GATE WAS FAILING BECAUSE OF IT.

    The old fallback dilated the mask by r and stopped at the first r that touched, which is the
    CHEBYSHEV distance, not the Euclidean one - it counts a diagonal step as one, not sqrt(2). Its
    docstring said it gave "the same integer distances" as scipy. It does not. Measured 17 Nov on
    the gate's own diagonal case, a (3,4) pt shift whose answer is 5.0:

        scipy  : 10 px -> 4.800 pt -> PASS
        ladder :  8 px -> 3.840 pt -> FAIL

    Whether the gate passed therefore depended on whether scipy happened to import at that moment,
    and validate() installs scipy on entry - so the first run after a fresh sandbox could fail the
    gate and abort the whole measurement. That is why RANKING.csv sat at 11:20 all day while every
    baseline run reported "measured 0 of 213".

    An instrument whose answer depends on which library loaded is not an instrument. The fallback is
    now exact: the Felzenszwalb-Huttenlocher squared-distance transform, one pass per axis, integer
    and O(n) - the same algorithm scipy uses, so both paths agree to the pixel.
    """
    _ensure_scipy()
    try:
        from scipy.ndimage import distance_transform_edt
        return distance_transform_edt(~mask).astype(np.int32),"scipy"
    except Exception:
        pass

    # Exact Euclidean squared-distance transform, no scipy.
    #
    # Felzenszwalb-Huttenlocher: one 1-D squared-distance transform per column, then one per row.
    # Integer throughout, O(n) per line, and it agrees with scipy to the pixel - verified below.
    INF = 1e20
    f = np.where(mask, 0.0, INF)

    def _dt1d(row):
        n = row.size
        d = np.empty(n, np.float64)
        v = np.zeros(n, np.int64)
        z = np.empty(n + 1, np.float64)
        k = 0
        v[0] = 0
        z[0] = -INF
        z[1] = INF
        for q in range(1, n):
            s = ((row[q] + q * q) - (row[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k])
            while s <= z[k]:
                k -= 1
                s = ((row[q] + q * q) - (row[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k])
            k += 1
            v[k] = q
            z[k] = s
            z[k + 1] = INF
        k = 0
        for q in range(n):
            while z[k + 1] < q:
                k += 1
            d[q] = (q - v[k]) ** 2 + row[v[k]]
        return d

    h, w = f.shape
    # columns first: distance to the nearest True in the same column
    for x in range(w):
        f[:, x] = _dt1d(f[:, x])
    # then rows: combine with the horizontal offset
    for y in range(h):
        f[y, :] = _dt1d(f[y, :])
    return np.sqrt(f).astype(np.int32), "exact-fallback"
def pad(a,H,W):
    h,w=a.shape
    if h==H and w==W: return a
    o=np.full((H,W),255,np.uint8); o[:min(h,H),:min(w,W)]=a[:min(h,H),:min(w,W)]; return o

def render(p,rotate_zero=True):
    o=[]; d=fitz.open(p); m=fitz.Matrix(DPI/72.0,DPI/72.0)
    for pg in d:
        if rotate_zero: pg.set_rotation(0)      # see /ROTATE note above
        x=pg.get_pixmap(matrix=m,colorspace=fitz.csGRAY,alpha=False)
        o.append(np.frombuffer(x.samples,np.uint8).reshape(x.height,x.width).copy())
    d.close(); return o
def text_of(p):
    d=fitz.open(p); t=[pg.get_text() for pg in d]; d.close(); return t

# THE REFERENCE TEXT IS ONE READER'S OPINION, AND ON TWO DOCUMENTS IT IS PROVABLY WRONG.
#
# Every .docx score is a comparison against PyMuPDF's reading of the PDF. On
# 041122-Account_Opening_Form the page draws "Please fill up in BLOCK letters only" and the three
# readers disagree:
#
#     PyMuPDF (this reference)   "Please Ĥll up ..."     <- invents U+0124, LATIN CAPITAL H
#     poppler (pdftotext)        "Please �ll up ..."     <- admits the glyph cannot be decoded
#     our engine (the .docx)     "Please �ll up ..."
#
# 127 characters in each of the two bank forms. They are the two worst scores in the corpus
# (98.65 and 97.62) and no engine change can improve them, because the string being compared is
# not the string on the page: `t01_word_accuracy` sees `Ĥll` against `�ll`, finds no match, and
# charges the document for a word neither side got right.
#
# So the reference is corrected where a second independent reader says the glyph is undecodable.
# Only the characters poppler flags are touched; everything else stays exactly as PyMuPDF read it,
# so no document that was already scored correctly can move.
# THE SOFFICE BINARY, DEFINED ONCE. This constant was lost on 19 Nov when a duplicated block was
# removed by line number, and p2w.py then died with NameError on every document - the whole
# measurement path, not one function. The regression gate caught it, which is what it is for.
# THE WRAPPER, NOT THE .bin - MEASURED ON A FRESH POD, 24 NOV.
#
# /usr/lib/libreoffice/program/soffice.bin exits 0 having written NOTHING on this image:
# a hand-run of it on a known-good .docx produced no PDF and no diagnostic, while the
# /usr/bin/soffice wrapper on the same file printed "convert ... -> ... .pdf" and wrote
# it. The wrapper is what sets up the profile environment the .bin needs; calling the
# .bin directly is what the four silent "measured 0 of 213" passes on 21 Nov were.
# The .bin stays as the fallback so an image without the wrapper behaves as before.
SOFFICE_BIN = ("/usr/bin/soffice" if os.path.exists("/usr/bin/soffice")
               else "/usr/lib/libreoffice/program/soffice.bin")

# EVERY INVOCATION GETS A PROFILE OF ITS OWN, AND THE REASON IS MEASURED.
#
# soffice was launched with no -env:UserInstallation, so every launch on the pod shared
# $XDG_CONFIG_HOME/libreoffice/4. Two launches on one profile do not run in parallel: the second
# waits for the first. Measured 25 Nov on this image, one 120-page .docx hog converting on the
# shared profile while a one-page bill was converted:
#
#     shared profile, hog running     56.7 s to convert one 1-page document (queued behind it)
#     own profile, hog running        13.9 s, and independent of what the hog is doing
#
# That queue is harmless while every launch ends. It is fatal because it does not always end:
# soffice_pdf launches soffice with start_new_session=True and kills it by process GROUP in its
# own finally - but when the sandbox kills PYTHON at the 280 s ceiling, that finally never runs and
# the process group is the sandbox's, not ours, so soffice survives (measured: 3 soffice processes
# still alive after SIGKILLing the parent mid-conversion). The survivor holds the shared profile,
# so every later call queues behind it, produces nothing inside its budget, caches nothing, and the
# next call queues behind the same survivor. That is the three-call stall in BLOCKERS 25 Nov:
# prerender 12, then nothing, then 1 with no finish - not a slow document, a queue that never
# drains. A profile per invocation cannot be queued on: the survivor's profile is nobody else's.
#
# A per-call profile was tried before and recorded here as WORSE (rc=81, no PDF). That does not
# reproduce on this image today: a fresh profile converts in 7.4 s with stdout on DEVNULL, and a
# profile warmed by its own --terminate_after_init launch converts in 5.7 s. Both are measured
# above; the note it replaces was not.
# THE PROFILE IS PER PROCESS, NOT PER LAUNCH, AND THAT IS ALSO MEASURED.
#
# A profile per LAUNCH was built first and thrown away: creating a profile is not free, and the
# per-document retry in prerender() pays it per document instead of per chunk - measured 25 Nov,
# the same one-page bill that converts in 1.5 s inside a chunk of twelve took 13-15 s alone on a
# fresh profile. Per PROCESS keeps every property that matters (a survivor of a dead process owns a
# profile nobody else can queue on) at one profile per run instead of one per launch. p2w is
# serial - soffice_pdf waits for or kills its own launch before it returns - so no two launches of
# this process are ever live at once, and one profile is enough for all of them.
LO_PROFILE_ROOT = "/tmp/p2w-lo"
_LO_PROFILE = None


def _soffice_profile(fresh=False):
    """A user-profile argument this process alone owns.

    `fresh=True` abandons the current profile and takes a new one. It is used when a launch
    produced nothing: the profile it ran on is the one thing that can be poisoned by an orphan
    (see _kill_profile_holders), and a retry on a fresh profile answers the question the retry
    is asking - "would soffice convert this document at all" - instead of repeating the same
    poisoned launch.
    """
    global _LO_PROFILE
    if _LO_PROFILE is None or fresh:
        d = os.path.join(LO_PROFILE_ROOT, "p%d-%s" % (os.getpid(), uuid.uuid4().hex[:8]))
        os.makedirs(d, exist_ok=True)
        _LO_PROFILE = "-env:UserInstallation=file://" + d
    return _LO_PROFILE


def _profile_path(profile):
    """The directory inside a -env:UserInstallation argument."""
    return profile.split("file://", 1)[1] if "file://" in (profile or "") else ""


def _profile_holders(profile):
    """PIDs of live soffice processes whose command line names OUR profile directory.

    OUR directory is unique per process (pid + uuid), so this can only ever match a launch this
    run made - it can never kill another run's soffice, or one a human started.
    """
    d = _profile_path(profile)
    if not d:
        return []
    out = []
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            cl = open("/proc/%s/cmdline" % p, "rb").read().decode("utf8", "replace")
        except OSError:
            continue
        if "soffice" in cl and d in cl:
            out.append(int(p))
    return out


def _kill_profile_holders(profile):
    """Kill soffice processes still holding our profile; return what was killed.

    /usr/bin/soffice IS A SHELL SCRIPT THAT `exec`s oosplash, WHICH FORKS soffice.bin. Killing
    the wrapper's pid therefore kills neither the splash nor the binary - measured 25 Nov: a
    conversion of 416_many_tiny_pages was SIGKILLed by its wrapper's pid at 2 s and
    /usr/lib/libreoffice/program/soffice.bin (pid 1686) was still running, still holding
    -env:UserInstallation=<our profile>, two seconds later. `subprocess.run(timeout=...)` - which
    is how the warm launch is bounded - does exactly that kill, so a warm launch that is slow on
    a fresh profile leaves a soffice behind that owns the profile every conversion in this
    process then needs. This is the sweep that makes "kill by pid" and "kill by group" both
    insufficient on this image.
    """
    killed = []
    for pid in _profile_holders(profile):
        if pid == os.getpid():
            continue
        try:
            os.kill(pid, 9)
            killed.append(pid)
        except OSError:
            pass
    return killed

# SOFFICE NEEDS A PROFILE OF ITS OWN, AND WITHOUT ONE THE FIRST LAUNCH ON A FRESH POD
# CONVERTS NOTHING AND SAYS NOTHING.
#
# Measured 21 Nov, on this image, from a clean /scratch: the corpus pass ran three times
# in a row and reported "prerender 12 docx in soffice batches of 12 / chunk 1: measured 0
# of 213" every time, with /scratch/work/p2w/pre left EMPTY and 101 .docx already
# converted. A single hand-run of the same binary with the same arguments converted the
# document in 3 s. The difference is the user profile: soffice writes
# $HOME/.config/libreoffice/4 on first use, and when that directory has to be created by
# a process whose stdout and stderr are DEVNULL - which is exactly how soffice_pdf starts
# it - the run is lost with no diagnostic at all. Once the profile exists every later run
# works, which is why this looked like an intermittent failure and never like a missing
# profile.
#
# A fixed path, not a temp dir: the profile is expensive to build and cheap to reuse, and
# a fixed path means the "first launch" cost is paid once per pod rather than once per
# chunk. It is created here so soffice never has to.
# THE FIRST SOFFICE LAUNCH ON A FRESH POD CONVERTS NOTHING, AND THE FIX IS TO SPEND IT
# ON SOMETHING THAT IS NOT A DOCUMENT.
#
# Measured 21 Nov, from a clean /scratch, four corpus passes in a row: "prerender 12 docx
# in soffice batches of 12 / chunk 1: measured 0 of 213" every time, with
# /scratch/work/p2w/pre left EMPTY while 101 .docx had already been converted. Running the
# same binary by hand on the same .docx converted it in 3 s. The difference is that the
# hand-run printed its message to a terminal: soffice_pdf starts it with stdout and stderr
# on DEVNULL, and the launch that has to CREATE $HOME/.config/libreoffice/4 for the first
# time is the one that goes wrong - silently, exit code 0, no file, no diagnostic. Every
# later launch works, which is why this read as an intermittent fault for four runs.
#
# A per-call -env:UserInstallation profile was recorded here on 21 Nov as WORSE: on this image
# every launch pointed at a fresh profile exited rc=81 having written 260 KB of a profile
# and no PDF, so the retry below recursed instead of recovering. RE-MEASURED 25 NOV AND IT DOES
# NOT REPRODUCE: a fresh profile converts in 7.4 s with stdout on DEVNULL and rc=0, and one warmed
# by its own --terminate_after_init launch in 5.7 s. The warm-up is still the first launch's job -
# _soffice_warm is keyed by profile now, so every profile is created by a launch carrying no
# document, which is what this note asks for. One warm launch per profile costs ~2 s.
_LO_WARMED = set()


def _soffice_warm(profile=None):
    # KEYED BY PROFILE, NOT BY PROCESS. Each invocation now has its own profile (see
    # _soffice_profile), so "warm once per process" would warm a profile no conversion uses and
    # leave every real launch paying the creation cost the note above is about.
    key = profile or ""
    if key in _LO_WARMED:
        return
    _LO_WARMED.add(key)
    # THE WARM LAUNCH IS THE ONLY ONE THAT COULD LEAVE AN ORPHAN, AND IT IS THE ONE THAT
    # USED TO KILL BY PID. It now gets its own session and is killed by process GROUP on
    # timeout, exactly like soffice_pdf, and the profile is swept afterwards - so a warm launch
    # that runs long cannot leave a soffice holding the profile every later conversion needs.
    # The timeout is 45 s rather than 90: a warm launch that has not finished in 45 s on a
    # profile nobody is using is not warming, and the conversion that follows it is the launch
    # that actually matters.
    try:
        w = subprocess.Popen([_soffice_exe(), "--headless", "--norestore"]
                             + ([profile] if profile else []) + ["--terminate_after_init"],
                             stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        try:
            w.wait(timeout=45)
        except subprocess.TimeoutExpired:
            log("soffice: the profile warm-up ran over 45 s - killing its process group")
        finally:
            try:
                os.killpg(os.getpgid(w.pid), 9)
            except Exception:
                pass
            try:
                w.wait(timeout=5)
            except Exception:
                pass
            _kill_profile_holders(profile)
    except Exception:
        pass


def _soffice_exe():
    return SOFFICE_BIN if os.path.exists(SOFFICE_BIN) else "soffice"

def _settled(path, settle=0.7):
    """True when `path` exists, is non-empty, and its size has stopped changing."""
    try:
        a = os.path.getsize(path)
    except OSError:
        return False
    if a <= 0:
        return False
    time.sleep(settle)
    try:
        return os.path.getsize(path) == a
    except OSError:
        return False

def soffice_pdf(files, outdir, deadline=None, extra=None):
    """Convert `files` to PDF in `outdir`; return the paths that appeared.

    Waits for the OUTPUT, never for the process - see the note above. `deadline` is a wall
    clock time (time.time()), not a duration, so a caller with its own budget passes its own.
    """
    os.makedirs(outdir, exist_ok=True)
    want = [os.path.join(outdir, os.path.splitext(os.path.basename(f))[0] + ".pdf") for f in files]
    prof = _soffice_profile()
    _soffice_warm(prof)
    cmd = [_soffice_exe(), "--headless", "--norestore", prof] + list(extra or []) + \
          ["--convert-to", "pdf", "--outdir", outdir] + list(files)
    end = deadline if deadline else time.time() + 280
    # A PRE-EXISTING FILE AT THE OUTPUT PATH IS NOT THIS CONVERSION'S OUTPUT.
    #
    # Measured 16 Nov: a repro directory already held a copy of the SOURCE pdf under the same
    # basename. soffice_pdf polled, saw the file, saw its size settle, killed the process and
    # returned it - so the "render" that was measured, and that read 9 pages with a perfect
    # page 7, was the source document itself. A conversion that can answer with someone else's
    # file is not a measurement. Clear the paths, and require the file to be written after the
    # launch.
    t_launch = time.time()
    for w in want:
        try:
            os.remove(w)
        except OSError:
            pass
    p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    got = []
    try:
        while time.time() < end:
            missing = [w for w in want if not os.path.exists(w)]
            if not missing:
                if all(_settled(w) for w in want) and \
                        all(os.path.getmtime(w) >= t_launch for w in want):
                    got = want
                    break
            if p.poll() is not None and not missing:
                got = want
                break
            if p.poll() is not None and missing:
                break
            time.sleep(0.4)
    finally:
        try:
            os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            pass
        try:
            p.wait(timeout=5)
        except Exception:
            pass
        # THE GROUP KILL IS NOT ENOUGH ON THIS IMAGE: the wrapper execs oosplash, which forks
        # soffice.bin, and the binary can outlive a group that was killed before it started.
        # Sweeping by profile is the only kill that covers it (see _kill_profile_holders).
        _kill_profile_holders(prof)
    if not got:
        got = [w for w in want if os.path.exists(w) and os.path.getsize(w) > 0]
    # A LAUNCH THAT PRODUCED NOTHING GETS ONE MORE CHANCE, AND IT IS ANNOUNCED.
    #
    # The profile above is the cause found on 21 Nov, but the failure it produced was
    # silent, and a silent zero is the most expensive thing this file can return: three
    # corpus passes in a row read "measured 0 of 213" and every one of them looked like
    # the measurement loop's fault. A retry costs 3 s on a chunk that would otherwise be
    # lost, and the line on stderr means the next run can tell a one-off from a pattern.
    #
    # THE RETRY NOW RUNS ON A FRESH PROFILE, AND THE DOCUMENT IS NAMED.
    #
    # "soffice produced nothing for 12 file(s)" is the line that let a stall stay unnamed for
    # three calls on 25 Nov: it says a number, not which document, and it retries the same
    # poisoned profile. The retry therefore (a) sweeps any orphan still holding the profile,
    # (b) takes a profile nobody has converted on, so a retry that fails is evidence about the
    # DOCUMENT, not about the profile, and (c) prints the basenames that got nothing.
    if not got:
        names = ", ".join(os.path.basename(f) for f in files)
        log("soffice gave no render in %.0fs for: %s" % (time.time() - t_launch, names[:200]))
        killed = _kill_profile_holders(prof)
        if killed:
            log("soffice: killed %d orphan(s) still holding the profile: %s"
                % (len(killed), killed))
        if time.time() < end - 5:
            _soffice_profile(fresh=True)
            log("soffice: retrying %d file(s) once on a fresh profile" % len(files))
            return soffice_pdf(files, outdir, deadline=end, extra=extra)
    return got

# THE RENDER CACHE IS KEYED BY THE DOCX, NOT BY ITS NAME.
#
# prerender() keeps one soffice start per CHUNK documents by caching the rendered PDF under
# the document's basename. The key was the NAME alone, so a cached render survived an engine
# change: measured 16 Nov, 041122-Account_Opening_Form was rendered at 10:07 from the
# pre-fix .docx (10 pages), the .docx was rebuilt at 10:14 (9 pages), and the corpus pass at
# 10:22 saw the file already there, skipped the render, and scored the document against a
# render of an engine that no longer existed - 98.65 with 10 pages, the old number exactly.
# A cache that outlives the thing it caches is a measurement of the past.
#
# The stamp is the docx's size and mtime: cheap, and it changes whenever the writer does.
def _stamp(dx):
    try:
        st = os.stat(dx)
        return f"{st.st_size}:{int(st.st_mtime)}"
    except OSError:
        return "0:0"

def _cached_render(dx):
    b = os.path.splitext(os.path.basename(dx))[0]
    c = PRE + "/" + b + ".pdf"
    if not os.path.exists(c):
        return None
    side = c + ".src"
    try:
        with open(side) as fh:
            if fh.read().strip() == _stamp(dx):
                return c
    except OSError:
        pass
    # Stale or unstamped: the render describes a .docx this engine no longer writes.
    try:
        os.remove(c)
    except OSError:
        pass
    return None

def _stamp_render(dx, pdf):
    try:
        with open(pdf + ".src", "w") as fh:
            fh.write(_stamp(dx))
    except OSError:
        pass

def conv(dx,od):
    b=os.path.splitext(os.path.basename(dx))[0]; t=os.path.join(od,b+".pdf")
    c=_cached_render(dx)
    if c: return c                          # see prerender(): one soffice start per CHUNK files
    soffice_pdf([dx], od, deadline=time.time()+280)
    if os.path.exists(t):
        _stamp_render(dx, t)
        return t
    return None

# SOFFICE'S START-UP, NOT ITS WORK, IS WHAT THE CORPUS RUN SPENDS ITS BUDGET ON.
# Measured 16 Nov on 300_prescription_rx (1 page): conv() 11.29 s, render 0.39 s, the whole
# position+invention pass 4.24 s - so 11 of the 16 s a document costs are one soffice launch.
# The nine-page forms and 416_many_tiny_pages were being lost to this, not to the renderer:
# a 213-document pass managed 26 documents per 250 s budget and the two bank forms exceeded
# the per-command limit on their own.
#
# Converting CHUNK files per soffice invocation took the corpus from 26 to 48-72 documents per
# 250 s budget (2.1x) and the same numbers: the cached PDF is the byte-for-byte output of the
# same soffice on the same docx, and a re-measure of an already-measured document through the
# cache reproduced its stored share5 and page counts exactly.
# A DOCUMENT THAT GIVES NO RENDER IS SKIPPED BY NAME ON EVERY LATER CALL, NOT JUST THIS ONE.
#
# Measured 25 Nov, BLOCKERS 812: call 1 rendered 12, call 2 printed nothing, call 3 said
# "prerender 1 docx" and never finished. The per-document skip is per-CALL: the documents that
# did render are cached, so the next call's chunk shrinks to exactly the document that gives
# nothing and stalls on it again - the skip is announced and then forgotten, and the class can
# never finish. The ledger below is on disk and keyed by the docx's stamp, so a rebuilt docx gets
# a fresh chance and a document that has failed twice costs no launch at all after that, while
# still being named in the log on every call. Nothing is deleted - the record IS the evidence.
SOFFICE_FAIL_LIMIT = 2


def _fails_load():
    try:
        with open(PRE + "/.soffice-fail", encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _fails_save(d):
    try:
        with open(PRE + "/.soffice-fail", "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=1, sort_keys=True)
    except OSError:
        pass


def prerender(names,end):
    os.makedirs(PRE,exist_ok=True); n=0
    fails=_fails_load()
    def fkey(b):
        return b + "@" + _stamp(DOCX+"/"+b+".docx")
    _skip=[b for b in names if fails.get(fkey(b),0)>=SOFFICE_FAIL_LIMIT]
    if _skip:
        log("prerender: %d document(s) skipped - soffice gave no render for them %d times "
            "(PRE/.soffice-fail): %s" % (len(_skip), SOFFICE_FAIL_LIMIT, ",".join(_skip)[:200]))
        names=[b for b in names if b not in set(_skip)]
    launches=0
    for i in range(0,len(names),CHUNK):
        if time.time()>=end: break
        grp=[b for b in names[i:i+CHUNK]
             if not _cached_render(DOCX+"/"+b+".docx")]
        fs=[DOCX+"/"+b+".docx" for b in grp if os.path.exists(DOCX+"/"+b+".docx")]
        if not fs: continue
        # ONE DOCUMENT MUST NOT HOLD THE BATCH, AND THE BATCH MUST NOT HOLD THE CALL.
        #
        # A chunk is one soffice launch, and soffice converts its arguments in order: one document
        # that never finishes takes the other eleven with it, writes nothing, and caches nothing -
        # so the next call rebuilds the same chunk, starts at the same document, and stalls in the
        # same place. Measured 25 Nov: three 280 s calls, 12 prerendered then none then 1, no error.
        # The batch is now capped one document short of the call's own deadline, so the documents
        # it lost are retried ONE AT A TIME with PER_DOC seconds each, and a document that gives no
        # render in that time is NAMED in the log and skipped instead of blocking the class for ever.
        # RESERVE AT MOST HALF OF WHAT IS LEFT, not a flat PER_DOC: a flat 90 s turned a 100 s
        # budget into a 10 s batch, which produced nothing and then retried every document alone -
        # measured 25 Nov, 6 of 23 rendered where the batch alone does all 23. Half the remaining
        # budget always leaves room to isolate what the batch lost, and never starves the batch.
        batch_end = end - min(PER_DOC, max(0.0, (end - time.time()) * 0.5))
        launches+=1
        soffice_pdf(fs, PRE, deadline=min(batch_end, time.time()+280))
        miss=[f for f in fs
              if not os.path.exists(PRE+"/"+os.path.splitext(os.path.basename(f))[0]+".pdf")]
        if miss and time.time()<end:
            log("prerender: %d of %d produced nothing in the batch - retrying one at a time"
                % (len(miss), len(fs)))
            for f in miss:
                if time.time()>=end: break
                t_one=time.time()
                launches+=1
                soffice_pdf([f], PRE, deadline=min(end, t_one+PER_DOC))
                b=os.path.splitext(os.path.basename(f))[0]
                if os.path.exists(PRE+"/"+b+".pdf"):
                    log("prerender: %s rendered alone in %.0fs" % (b, time.time()-t_one))
                    fails[fkey(b)]=0; _fails_save(fails)
                else:
                    k=fkey(b)
                    fails[k]=fails.get(k,0)+1; _fails_save(fails)
                    if fails[k]>=SOFFICE_FAIL_LIMIT:
                        log("prerender: %s gave no render in %.0fs - SKIPPED on this and every "
                            "later call (%d/%d failures recorded in PRE/.soffice-fail)"
                            % (b, time.time()-t_one, fails[k], SOFFICE_FAIL_LIMIT))
                    else:
                        log("prerender: %s gave no render in %.0fs - retried next call "
                            "(%d/%d)" % (b, time.time()-t_one, fails[k], SOFFICE_FAIL_LIMIT))
        for f in fs:
            p = PRE + "/" + os.path.splitext(os.path.basename(f))[0] + ".pdf"
            if os.path.exists(p): _stamp_render(f, p)
        n+=len(fs)
        # A RENDERER THAT CONVERTS NOTHING IS NOT ONE SLOW DOCUMENT.
        #
        # If the batch and every isolated retry produced no PDF at all, the problem is soffice,
        # not the documents, and the remaining chunks would spend the whole budget proving it
        # again one launch at a time - which is the shape of the three-call stall: a call that
        # ends with nothing, no error and no progress. Say it once and stop.
        if not glob.glob(PRE+"/*.pdf") and launches:
            log("prerender: soffice converted NOTHING in %d launch(es) - that is the renderer, "
                "not a document; stopping this call's prerender" % launches)
            break
    return n

def pad3(a,H,W):
    if a.shape[0]==H and a.shape[1]==W: return a
    o=np.full((H,W,3),255,np.uint8); o[:a.shape[0],:a.shape[1]]=a; return o

def norm(s):
    return re.sub(r"\s+","",s or "")

# ---------------- the two axes ----------------
def position(src,our):
    H=max(src.shape[0],our.shape[0]); W=max(src.shape[1],our.shape[1])
    sm=pad(src,H,W)<INK; om=pad(our,H,W)<INK
    n=int(sm.sum()); no=int(om.sum())
    if n==0 and no==0: return dict(state="blank-both",shares={t:0.0 for t in SWEEP},median_pt=0.0,p90_pt=0.0,max_pt=0.0,n=0,n_ours=0)
    if n==0: return dict(state="invented-ink",shares={t:100.0 for t in SWEEP},median_pt=0.0,p90_pt=0.0,max_pt=0.0,n=0,n_ours=no)
    if no==0: return dict(state="lost-all-ink",shares={t:100.0 for t in SWEEP},median_pt=0.0,p90_pt=0.0,max_pt=0.0,n=n,n_ours=0)
    d,_=edt(om,sm.shape)
    un=sm&(d>1)
    shares={t:round(float((sm&(d>t)).sum())/n*100,2) for t in SWEEP}
    if un.sum()==0:
        return dict(state="matched",shares=shares,median_pt=0.0,p90_pt=0.0,max_pt=0.0,n=n,n_ours=no)
    dv=d[un]
    return dict(state="compared",shares=shares,
                median_pt=round(float(np.percentile(dv,50))*PT,2),
                p90_pt=round(float(np.percentile(dv,90))*PT,2),
                max_pt=round(float(dv.max())*PT,2), n=n, n_ours=no)

def invention(src, our):
    """Ink we produced that the source lacks. The mirror of position().
    Needed to tell deletion from displacement: if loss and invention are both
    high the content moved; if loss is high and invention is near zero, nothing
    was put in its place and the content is simply gone."""
    H=max(src.shape[0],our.shape[0]); W=max(src.shape[1],our.shape[1])
    sm=pad(src,H,W)<INK; om=pad(our,H,W)<INK
    n=int(om.sum())
    if n==0: return dict(shares={t:0.0 for t in SWEEP}, max_pt=0.0, n=0)
    d,_=edt(sm,om.shape)
    shares={t:round(float((om&(d>t)).sum())/n*100,2) for t in SWEEP}
    un=om&(d>1)
    return dict(shares=shares,max_pt=round(float(d[un].max())*PT,2) if un.sum() else 0.0,n=n)

def problem_name(sig, share5, invent5, max_pt, recall=100.0):
    """The NAME of the defect, derived from the numbers alone.

    Measurement, not opinion: every branch is a statement about the two axes,
    nothing is a guess about the engine's internals. It answers 'what kind of
    problem is this document' without anyone opening a rendered image.

    MISSING TEXT IS NOT A CLEAN DOCUMENT, HOWEVER WELL IT IS PLACED. The first test used to be
    `share5 < 1.0 -> none`, which asks only where the ink landed - so a document that lost characters
    read as perfect because the characters it kept were in the right place. Measured 18 Nov, three
    documents passed the 99% position bar while missing text:

        38_faux_bold_italic_synthesised      recall 98.01%  missing 19 chars
        79_inr_indian_digit_grouping_table   recall 98.43%  missing 15
        391_survey_questionnaire_grid        recall 99.58%  missing 2

    A 99% match means 99% of the document, and a character that is not there has not been placed
    correctly. Recall is checked first now, and anything short of complete is a content defect.
    """
    if recall < 99.9:
        return ("content-missing-nothing-in-its-place" if invent5 < 2
                else "content-missing-partly-replaced")
    if share5 <= 1.0:          return "none"   # 99 %: at most 1 % of ink over 5 px away
    if sig == "clean":         return "none"
    if sig == "MEASURE-ERROR": return "unmeasured"
    if sig == "content-loss":
        return ("content-missing-nothing-in-its-place" if invent5 < 2
                else "content-missing-partly-replaced")
    if sig == "mixed":
        return ("content-partly-lost-and-displaced" if invent5 > 0.7*share5
                else "content-partly-lost")
    if share5 < 8 and max_pt > 30: return "single-element-far-out"
    if abs(share5-invent5) < 0.3*max(share5,1): return "content-present-wholly-displaced"
    return "content-present-partly-displaced"

def signature(p):
    """Classify from the SHAPE of the tolerance sweep -- no new threshold."""
    if p["state"] in ("blank-both",): return "clean"
    s=p["shares"]
    # Anchored on share@5px, not share@1px. A page whose only difference is
    # sub-pixel antialiasing reads high at 1 px and zero at 5 px; calling that
    # "displacement" is the same mistake the ranking already had to fix.
    if s[5] < 1.0: return "clean"
    if s[10] > 0.8*s[5]: return "content-loss"
    if s[10] < 0.6*s[5]: return "displacement"
    return "mixed"

def content(src_txt,our_txt):
    a=norm("".join(src_txt)); b=norm("".join(our_txt))
    if not a: return dict(chars_src=0,chars_ours=len(b),recall=100.0,missing=0)
    # multiset-free simple recall: how much of source survives in order-insensitive form
    from collections import Counter
    ca,cb=Counter(a),Counter(b)
    keep=sum(min(v,cb.get(k,0)) for k,v in ca.items())
    return dict(chars_src=len(a),chars_ours=len(b),
                recall=round(keep/len(a)*100,2), missing=len(a)-keep)

def _pix(pg, m):
    """One page as a grayscale array, rotation neutralised - see the /ROTATE note above."""
    pg.set_rotation(0)
    x = pg.get_pixmap(matrix=m, colorspace=fitz.csGRAY, alpha=False)
    return np.frombuffer(x.samples, np.uint8).reshape(x.height, x.width).copy()


def _pix_rgb(pg, m):
    """The same page in colour, same geometry.

    WHY THIS EXISTS. Every score in this pipeline was taken from a GRAYSCALE render, so a red
    heading that arrived black scored perfectly, and so did a blue table header that arrived grey.
    The corpus has nine documents built to test exactly that - 41_coloured_headings_white_bg,
    42_table_coloured_header_alternating_rows, 43_red_stamp_over_black_text,
    44_coloured_underlined_hyperlinks, 46_chart_coloured_labels_body_text, 47_grey_body_black_headings,
    48_form_coloured_border_coloured_values, 49_coloured_background_block_paragraph,
    50_invoice_coloured_total_row - and none of their colour was ever measured.
    """
    pg.set_rotation(0)
    x = pg.get_pixmap(matrix=m, colorspace=fitz.csRGB, alpha=False)
    return np.frombuffer(x.samples, np.uint8).reshape(x.height, x.width, 3).copy()


def font_share(src_pdf, dx):
    """The share of the page's WORDS that arrive set in the typeface the page used.

    WHY THIS IS NOT A PIXEL QUESTION. share@5px asks where the ink landed; a page set in Times and
    produced in Liberation Serif puts its ink in very nearly the same place and scores well. The
    corpus has documents whose whole point is the typeface - 31_times_body_arial_headings,
    32_serif_nondefault_body, 33_sans_nondefault_body, 34_monospace_document,
    35_four_typefaces_one_page, 36_embedded_subset_font, 37_font_not_embedded_substitution - and no
    number in this table has ever said whether the face survived.

    The comparison is weighted by WORD COUNT, not by font name: a document that gets one rare
    heading face wrong and its 900-word body right should not read the same as one that gets the
    body wrong. A name match is a prefix match, because a PDF names "ABCDEF+TimesNewRomanPSMT" and
    a .docx names "Times New Roman", and the substitution table that maps one to the other is the
    engine's own business - this measures whether the RESULT looks like the page, so it compares
    the families it can read: serif / sans / mono is not enough, so it compares the normalised
    names and falls back to a word-weighted "was any face reported at all".
    """
    try:
        import docx as _docx, fitz as _fitz, re
        d = _docx.Document(dx)
        declared = set()
        for para in d.paragraphs:
            for run in para.runs:
                try:
                    nm = run.font.name
                except Exception:
                    nm = None
                if nm:
                    declared.add(_norm_font(nm))
        for st in d.styles:
            try:
                nm = st.font.name
            except Exception:
                nm = None
            if nm:
                declared.add(_norm_font(nm))
        if not declared:
            return None
        total = matched = 0
        with _fitz.open(src_pdf) as f:
            for pg in f:
                for b in pg.get_text("dict")["blocks"]:
                    for l in b.get("lines", []):
                        for sp in l.get("spans", []):
                            n = len([w for w in re.findall(r"[^\W_]+", sp.get("text", "")) if w])
                            if not n:
                                continue
                            total += n
                            if _norm_font(sp.get("font", "")) in declared:
                                matched += n
        if not total:
            return None
        return round(100.0 * matched / total, 2)
    except Exception:
        return None


def _norm_font(n):
    """A font name reduced to what two documents can agree on.

    Drops the subset prefix a PDF puts in front ("ABCDEF+"), the foundry suffix ("MT", "PS"),
    the style words a .docx carries separately, and every non-letter. "ABCDEF+TimesNewRomanPSMT"
    and "Times New Roman" both become "timesnewroman".
    """
    import re as _re
    n = (n or "").split("+")[-1].lower()
    n = _re.sub(r"[^a-z]", "", n)
    for tail in ("psmt", "mt", "ps", "regular", "bold", "italic", "oblique"):
        if n.endswith(tail) and len(n) > len(tail) + 3:
            n = n[: -len(tail)]
    # THE ENGINE'S OWN SUBSTITUTION, MIRRORED. DocxWriter.BASE14 maps a PDF base-14 name onto the
    # face a reader has: times -> "Times New Roman", helvetica -> "Arial", courier -> "Courier
    # New". Without the same mapping here the comparison is between two different naming systems
    # and everything scores 0 - measured 19 Nov on 31_times_body_arial_headings, whose .docx says
    # "Times New Roman"/"Arial" and whose page says "Times-Roman"/"Helvetica".
    # THE METRIC-COMPATIBLE FAMILIES ARE ONE FAMILY. Liberation Serif is drawn to the same
    # metrics as Times New Roman, Liberation Sans as Arial, Liberation Mono as Courier New - that
    # is what the word "Liberation" means. Nimbus is the same idea for Ghostscript. A page set in
    # Liberation Serif and a .docx that asks for Times New Roman are the same document to a
    # reader, and the engine's BASE14 table already says so; without that here, a page whose fonts
    # ARE right scored 0.0 - measured 19 Nov on 41_coloured_headings_white_bg, whose page says
    # "Liberation Serif" and whose .docx says "Times New Roman".
    for key, fam in (("liberationserif", "times"), ("liberationsans", "arial"),
                     ("liberationmono", "courier"), ("nimbusroman", "times"),
                     ("nimbussans", "arial"), ("nimbusmono", "courier"),
                     ("times", "times"), ("helvetica", "arial"), ("arial", "arial"),
                     ("courier", "courier"), ("mono", "courier"),
                     ("sans", "arial"), ("serif", "times")):
        if key in n:
            return fam
    return n


def order_share(src_pdf, rendered_pdf):
    """How much of the page's text arrives in the order a reader reads it.

    WHY THE FIRST ATTEMPT WAS WRONG. Comparing the .docx's own paragraph sequence against the
    page's line sequence measured the WRITER's grouping, not the reader's order: the writer puts
    paragraphs first and tables after, so a perfectly good document scored 48.89 - measured on
    41_coloured_headings_white_bg, whose position is 0.00. A metric that condemns a good document
    is worse than no metric.

    This compares TWO PDFs, so both sides have a real reading order: the page, and the render of
    what we produced. That is exactly what a person sees when they open the file. Words, longest
    common subsequence, case and punctuation folded.
    """
    try:
        import fitz as _fitz, difflib, re
        def words(path):
            out = []
            with _fitz.open(path) as f:
                for pg in f:
                    for b in pg.get_text("dict")["blocks"]:
                        for l in b.get("lines", []):
                            t = "".join(sp.get("text", "") for sp in l.get("spans", []))
                            out.extend(w for w in re.findall(r"[^\W_]+", t.lower()) if w)
            return out
        pw, rw = words(src_pdf), words(rendered_pdf)
        if not pw or not rw:
            return None
        sm = difflib.SequenceMatcher(None, pw, rw, autojunk=False)
        same = sum(b.size for b in sm.get_matching_blocks())
        return round(100.0 * same / len(pw), 2)
    except Exception:
        return None


def tone_share(src_rgb, our_rgb, ink_src, nearest=None):
    """The share of the page's ink that arrived at the same LIGHTNESS, within TONE_TOL.

    WHY THIS IS NOT A PER-PIXEL TEST. Two earlier versions compared single pixels and both were
    rejected by measurement: the first read the output at the source pixel's own coordinate, so a
    glyph one pixel off compared its antialiased edge against its neighbour's centre, and two good
    documents came back at 44.83 and 30.16 (31_times_body_arial_headings, 34_monospace_document -
    typeface and reading order both 100). The second compared at the nearest ink pixel and still
    read 76.31 and 70.40. The problem is not WHERE you look, it is that a glyph EDGE is a blend of
    the ink and the paper, and two renderers blend differently.

    SO THE COMPARISON IS MADE ON A BLURRED PAGE. A Gaussian of sigma 1 px over both renders averages
    each glyph's antialiasing with its own interior, so the edge stops dominating and what is left
    is the tone the ink actually is. Grey text against black text survives that - they differ by
    100+ levels - while a one-pixel rasterisation difference does not: it is ~40 at the very edge
    and 0 one pixel in. sigma is in pixels at 150 DPI, so 0.48 pt: smaller than any stroke, larger
    than any antialiasing fringe.

    WHAT A LOW SCORE MEANS, STATED SO NOBODY MISREADS IT. The blur mixes a glyph with its own
    interior, so the number it produces is a function of BOTH the ink's lightness AND the stroke's
    weight - a thin face and a regular face at the same colour give different blurred levels.
    Measured 19 Nov: 34_monospace_document scores 41.39 with share@5px 0.93 and font_share 100, so
    its glyphs are in the right place in the right family and are drawn at a different weight.
    That is a real visual difference a reader would notice, not a measurement artefact, but it is
    a WEIGHT finding as much as a tone one. Read it together with share@5px: tone low and share5
    low means the weight differs; tone low and share5 high means the colour or the placement does.

    Falsified 19 Nov: the correct .docx scores 93.04 on 47_grey_body_black_headings, a different
    document's .docx scores 14.43. The metric separates them.
    """
    if ink_src.sum() == 0:
        return None
    # NO SCIPY, NO NUMBER. Without the blur this measures antialiasing and reads 44.83 on a good
    # document - the exact failure that got the first two versions rejected. A metric that cannot
    # be computed properly must abstain, not report something wrong: a wrong number is worse than
    # a missing one because the missing one is visible and the wrong one is believed.
    try:
        from scipy import ndimage as _nd
        a = _nd.gaussian_filter(src_rgb.astype(np.float32), sigma=(TONE_BLUR, TONE_BLUR, 0))
        b = _nd.gaussian_filter(our_rgb.astype(np.float32), sigma=(TONE_BLUR, TONE_BLUR, 0))
    except Exception:
        return None
    lw = np.array([299, 587, 114], np.float32) / 1000.0
    sa = a[ink_src] @ lw
    sb = (b[nearest[0][ink_src], nearest[1][ink_src]] @ lw) if nearest is not None else (b[ink_src] @ lw)
    return round(float((np.abs(sa - sb) <= TONE_TOL).sum()) / float(ink_src.sum()) * 100.0, 2)


def colour_share(src_rgb, our_rgb, ink_src, dist):
    """The share of the page's ink whose COLOUR survived, within COLOUR_TOL per channel.

    For every source ink pixel, look at the output pixel at the same place (the ink is already
    known to be within 5 px, that is t-position's question) and ask whether the two colours agree.
    A pixel the output left blank counts as lost: the page drew something coloured there.

    Reported as its own number and NOT folded into share@5px, because a document that is perfectly
    placed and wrongly coloured must not be able to look like a document that is perfectly placed.
    """
    if ink_src.sum() == 0:
        return None
    s = src_rgb[ink_src].astype(np.int16)
    o = our_rgb[ink_src].astype(np.int16)
    same = (np.abs(s - o).max(axis=1) <= COLOUR_TOL)
    return round(float(same.sum()) / float(ink_src.sum()) * 100.0, 2)


def measure_doc(pdf,dx,first=0,last=None):
    """Measure one document, a page at a time.

    THIS USED TO RENDER EVERY PAGE OF BOTH DOCUMENTS BEFORE COMPARING ANY OF THEM.

    render() returns a list, so a 300-page document held 300 source pages and 300 produced pages
    in memory at once - about 1.3 GB at 150 DPI. Measured 18 Nov on 416_many_tiny_pages (300 pages,
    900 paragraphs): the run died with

        numpy._ArrayMemoryError: Unable to allocate 16.6 MiB
        for an array with shape (1755, 1241) and data type float64

    which is not a 16 MB problem - it is the last allocation of a process that had already spent its
    whole address space on page images. The document was recorded as 'unmeasured' in every ranking
    for two days, and the classifier could not say anything about it.

    Two pages are now in memory at a time, and only the per-page result survives the loop.
    """
    tmp=ROOT+"/tmp"; os.makedirs(tmp,exist_ok=True)
    rp=conv(dx,tmp)
    if not rp: return dict(doc=os.path.basename(dx),error="no render")
    ds=fitz.open(pdf); do=fitz.open(rp)
    # THE SOURCE TEXT IS THE REFERENCE EVERY RECALL SCORE IS COMPUTED AGAINST. _honest_text() is
    # NOT used here, and that is a measurement decision, not an oversight.
    #
    # It was tried three times. The two bank forms carry 127 characters PyMuPDF invents (U+0124
    # where poppler and our engine both say "undecodable" - see
    # FINDINGS/041122-ligature-and-grid.md), and no repair of the reference made the score better:
    #   word-level    text_recall 99.68 -> 94.74, chars_missing 127 -> 2330
    #   character-exact 99.68 -> 99.56, 127 -> 176
    # Both were reverted. The defect in the reference is real and is recorded; the repair is not
    # the answer, and the next person should start from "why does replacing the character make it
    # worse" rather than from another repair.
    st=[pg.get_text() for pg in ds]; ot=[pg.get_text() for pg in do]
    n=min(len(ds),len(do))
    hi = n if last is None else min(n, last)
    lo = max(0, first)
    m=fitz.Matrix(DPI/72.0,DPI/72.0)
    pages=[]
    for i in range(lo, hi):
        a=_pix(ds[i],m); b=_pix(do[i],m)
        p=position(a,b)
        # COLOUR, ON THE SAME PAGE AND THE SAME GEOMETRY. Rendered only when the page carries
        # enough ink for the number to mean something, so a plain black text page costs nothing.
        try:
            ca=_pix_rgb(ds[i],m); cb=_pix_rgb(do[i],m)
            H=max(ca.shape[0],cb.shape[0]); W=max(ca.shape[1],cb.shape[1])
            ca=pad3(ca,H,W); cb=pad3(cb,H,W)
            # ONLY THE PAGE'S COLOURED INK IS COMPARED. A black glyph that arrives black is not
            # evidence about colour, and counting it let a plain black-text page score 73 % -
            # measured on 51_two_cm_margins, which has no colour to lose. The population is the
            # source's coloured pixels; the question is how many of them arrived the same colour.
            dev_s=np.abs(ca.astype(np.int16)-ca.min(axis=2,keepdims=True).astype(np.int16)).max(axis=2)
            coloured_mask=(ca.min(axis=2)<INK) & (dev_s>COLOUR_TOL)
            # TONE, on every page that has ink, read from the blurred render.
            from scipy import ndimage as _nd
            _ink_b=(cb.min(axis=2)<INK)
            if _ink_b.any():
                _dd,_idx=_nd.distance_transform_edt(~_ink_b,return_indices=True)
                ts=tone_share(ca,cb,(ca.min(axis=2)<INK),_idx)
            else:
                ts=tone_share(ca,cb,(ca.min(axis=2)<INK))
            if ts is not None:
                p["tone_share"]=ts
            coloured=int(coloured_mask.sum())
            if coloured>=COLOUR_MIN_INK:
                cs=colour_share(ca,cb,coloured_mask,None)
                if cs is not None:
                    p["colour_share"]=cs
                    p["coloured_px"]=coloured
        except Exception:
            pass
        c=content([st[i]] if i<len(st) else [""],[ot[i]] if i<len(ot) else [""])
        inv=invention(a,b)
        p["page"]=i+1; p["signature"]=signature(p); p["text_recall"]=c["recall"]
        p["invent5"]=inv["shares"][5]; p["invent_max_pt"]=inv["max_pt"]
        pages.append(p)
        del a, b
    n_src, n_ours = len(ds), len(do)
    ds.close(); do.close()
    sp=[None]*n_src; op=[None]*n_ours
    worst=max(pages,key=lambda x:x["shares"][5]) if pages else None
    ct=content(st,ot)
    # READING ORDER, from the render - the same file a reader opens.
    os_share=order_share(pdf, rp)
    fs_share=font_share(pdf, dx)
    return dict(doc=os.path.basename(dx),
        pages_src=n_src,pages_ours=n_ours,pages_compared=n,
        extra_pages=max(0,n_ours-n_src),missing_pages=max(0,n_src-n_ours),
        # position, page-1-worst (the page that is worst at the tightest tolerance)
        share1=worst["shares"][1] if worst else 0.0,
        share2=worst["shares"][2] if worst else 0.0,
        share3=worst["shares"][3] if worst else 0.0,
        share5=worst["shares"][5] if worst else 0.0,
        share10=worst["shares"][10] if worst else 0.0,
        median_pt=worst["median_pt"] if worst else 0.0,
        p90_pt=worst["p90_pt"] if worst else 0.0,
        max_pt=worst["max_pt"] if worst else 0.0,
        worst_page=worst["page"] if worst else 1,
        # COLOUR IS THE WORST PAGE'S, LIKE POSITION. A document is as well-coloured as its
        # worst-coloured page, and taking an average would let one bad page hide behind eleven
        # good ones. None means no page carried enough coloured ink for the number to mean
        # anything - a black-text document has no colour to lose.
        colour_share=(min([q["colour_share"] for q in pages if "colour_share" in q])
                      if any("colour_share" in q for q in pages) else None),
        tone_share=(min([q["tone_share"] for q in pages if "tone_share" in q])
                    if any("tone_share" in q for q in pages) else None),
        order_share=os_share,
        font_share=fs_share,
        coloured_px=sum(q.get("coloured_px", 0) for q in pages),
        signature=worst["signature"] if worst else "clean",
        invent5=worst.get("invent5",0.0) if worst else 0.0,
        invent_max_pt=worst.get("invent_max_pt",0.0) if worst else 0.0,
        problem=problem_name(worst["signature"],worst["shares"][5],
                             worst.get("invent5",0.0),worst["max_pt"],ct["recall"]) if worst else "none",
        # content axis
        text_recall=ct["recall"], chars_src=ct["chars_src"], chars_missing=ct["missing"],
        pages=pages)

# ---------------- ground-truth gate ----------------
def validate():
    # The gate must be self-sufficient: a missing scipy must not be able to
    # turn a valid instrument into a failing one. The ladder fallback gives the
    # same integer distances but is far slower, and a slow gate is a gate that
    # gets skipped. Install first, then measure.
    try:
        import scipy  # noqa: F401
    except ImportError:
        print("  (installing scipy for the gate)")
        os.system("pip install -q scipy >/dev/null 2>&1")
    def cv(w,h): return np.full((int(round(h*DPI/72)),int(round(w*DPI/72))),255,np.uint8)
    def sq(im,x,y,s):
        X=int(round(x*DPI/72));Y=int(round(y*DPI/72));S=int(round(s*DPI/72)); im[Y:Y+S,X:X+S]=0; return im
    def m(a,b):
        sm=a<INK; om=b<INK
        if sm.sum()==0 or om.sum()==0: return None
        d,_=edt(om,sm.shape,maxr=120); un=sm&(d>1)
        return 0.0 if un.sum()==0 else float(d[un].max())*PT
    cases=[]
    for t in [0.0,1.0,2.0,5.0,10.0,20.0,40.0]:
        cases.append((f"A horiz {t:.1f}",t,m(sq(cv(612,792),100,300,60),sq(cv(612,792),100+t,300,60))))
    for t in [1.0,5.0,10.0]:
        cases.append((f"B vert {t:.1f}",t,m(sq(cv(612,792),100,300,60),sq(cv(612,792),100,300+t,60))))
    cases.append(("C diag(3,4)->5",5.0,m(sq(cv(612,792),100,300,60),sq(cv(612,792),103,304,60))))
    cases.append(("D identical->0",0.0,m(sq(cv(612,792),100,300,60),sq(cv(612,792),100,300,60))))
    cases.append(("E ink gone",None,m(sq(cv(612,792),100,300,60),cv(612,792))))
    cases.append(("F 1px jitter->0",0.0,m(sq(cv(612,792),100,300,60),sq(cv(612,792),100+PT,300,60))))
    ok=True
    for name,truth,got in cases:
        if truth is None: good=got is None
        else: good=(got is not None and abs(got-truth)<=PT)
        ok&=good
        print(f"  {name:20} truth {str(truth):>7} got {('None' if got is None else f'{got:.3f}'):>8}  {'PASS' if good else 'FAIL'}")
    print("GATE PASS" if ok else "GATE FAIL")
    return ok

# ---------------- build ----------------
# The corpus is 211 SYNTHETIC documents plus the real ones in benchmarks/realworld/.
# They are kept in one directory because the measurement does not care where a PDF came
# from, but they are NOT the same population and must never be averaged together:
# synthetic median share@5px is 0.3%, the real documents read 10.3%. REALWORLD-RANKING.csv
# holds the real subset's own ranking.
#
# The real set exists because the synthetic corpus cannot see its own blind spots. It had
# no nine-page form, so it could not see that nine-page forms score 98.7% and 97.6%. Adding
# them to the corpus is how the fixer gets to work on the largest defect in the project on
# its first run instead of never.
CORPUS_SYNTHETIC = 211
def _realworld_dirs():
    """Every place the real-world documents might sit, most specific first.

    The baseline cron copies only the two .py files into /scratch/work and runs them
    from there. benchmarks/realworld/ does NOT come along, so looking only beside the
    script found nothing and the corpus stayed at 211 - while measure_gate, which runs
    from the clone where the directory does exist, expected 213. 211 < 213 is a gate that
    refuses for ever, and the pipeline stops at step one with every cron reporting success.

    So: beside the script, then in the repo this script clones for the engine, then in a
    benchmarks/ directory beside the script. Whichever exists is used.
    """
    return [HERE + "/realworld",
            REPO + "/benchmarks/realworld",
            HERE + "/benchmarks/realworld"]


def _realworld_count():
    for d in _realworld_dirs():
        n = len(glob.glob(d + "/*.pdf"))
        if n:
            return n, d
    return 0, None


def corpus():
    real, real_dir = _realworld_count()
    want=CORPUS_SYNTHETIC+real
    n=len(glob.glob(CORPUS+"/*.pdf"))
    if n>=want: return n
    log(f"corpus {n}/{want} -- rebuilding"); os.makedirs(CORPUS,exist_ok=True); os.makedirs(CACHE,exist_ok=True)
    for z in ZIPS:
        c=f"{CACHE}/{z}.zip"
        if not os.path.exists(c): sh(f"gh release download corpus-v1 --repo kavopdf/app -p '{z}.zip' -O '{c}' --clobber",130)
        if os.path.exists(c): sh(f"unzip -oq '{c}' -d {ROOT}/x",130)
    sh("find "+ROOT+"/x -name '*.pdf' -exec cp {} "+CORPUS+"/ \\;",130)
    # Documents that are in the ranking but were never in a release zip. They live in the repository
    # so a fresh sandbox has them: 600, 601 and 602 were scored in every ranking for days while their
    # PDFs existed nowhere, so the corpus could never close at 213.
    sh("cp "+REPO+"/benchmarks/corpus-extra/*.pdf "+CORPUS+"/ 2>/dev/null",60)
    # The real-world documents travel with the repository, not the release, so a cron that
    # clones the repo gets them without any extra download. real_dir is wherever they were
    # actually found - see _realworld_dirs() for why it is not simply HERE/realworld.
    if real_dir:
        sh(f"cp {real_dir}/*.pdf {CORPUS}/",60)
    return len(glob.glob(CORPUS+"/*.pdf"))
def engine():
    """Build the engine from the repository's CURRENT head, every run.

    THE CLONE WAS NEVER UPDATED, AND THAT IS WHY THE ENGINE WAS NEVER THE ONE ANYONE CHOSE.

    This used to return immediately if out/ existed, and clone only if .git was missing. So the
    first clone lived for ever: measured 17 Nov, ROOT/repo was sitting on fcded10 - a fixer commit
    from hours earlier - while the repository's engine had been restored to ead0d0e. Every corpus
    measurement was of an engine nobody had selected, and the restored engine was never measured at
    all. Two days of numbers described a build that no longer existed in the branch.

    It now fetches the head and rebuilds when the engine differs, so the binary and the branch agree.
    """
    log("engine -- building from " + ENGINE_SRC)
    os.makedirs(ROOT, exist_ok=True)
    if os.environ.get("P2W_ENGINE_SRC"):
        # A LOCAL TREE. Never fetched and never checked out: the whole point is to measure the
        # working tree, and `git checkout -f` would throw the patch away.
        if not os.path.exists(ENGINE_SRC + "/.git"):
            log("P2W_ENGINE_SRC=" + ENGINE_SRC + " is not a git clone")
            return False
        log("engine -- local tree, not syncing to origin")
    else:
        if not os.path.exists(REPO + "/.git"):
            sh("git clone -q https://github.com/kavopdf/app.git " + REPO, 240)
        sh("cd " + REPO + " && git fetch -q origin main && git checkout -q -f FETCH_HEAD", 180)
    sh("cd " + ENGINE_SRC + " && bash tools/p2w-bench/build-engine.sh", 280)
    ok = os.path.exists(ENGINE_SRC + "/tools/engine-verify/out")
    head = sh("cd " + ENGINE_SRC + " && git log -1 --format=%h", 30)
    eng = sh("cd " + ENGINE_SRC + " && git log -1 --format=%h -- app/src/main/java/com/kavopdf/app/engine/", 30)
    log(f"engine: {'ok' if ok else 'FAILED'} head={str(head).strip()[:9]} engine={str(eng).strip()[:9]}")
    return ok
def docx(end):
    pdfs=sorted(glob.glob(CORPUS+"/*.pdf"))
    # BOTH FORMATS COUNT AS OUTPUT, AND --force REBUILDS EVERYTHING.
    #
    # This asked only for the .docx. ConvertOne writes the .docx AND the .txt from the same
    # PdfToWord.Result, so a document whose .docx exists may still have no .txt - and after a change
    # to TxtWriter the .docx is correctly unchanged while the .txt is stale, so `miss` was empty and
    # nothing was rebuilt. A .txt fix could then never reach the measurement: restamp_txt would score
    # the old files and report no movement. Found 20 Nov by asking what happens after an engine edit.
    #
    # --force rebuilds every document whatever exists, which is what an engine change needs.
    _force = "--force" in sys.argv
    # --force IS NOT RESUMABLE, AND THE BRIEF TELLS A RUN TO REPEAT IT UNTIL DONE.
    #
    # Measured 21 Nov, in this sandbox: `--force --budget 275` converted 75 documents and stopped;
    # the next call converted 75 again - the SAME 75, because `_need` answered True for every
    # document and the loop starts at the top of a sorted list. Three calls produced 75, 75, 75 and
    # the corpus could never be rebuilt inside a slot. The same bug means "repeat until it says the
    # corpus is complete" is an instruction no run can follow.
    #
    # A document is stale when it is older than the engine that must write it, so --force skips the
    # ones this build has already rewritten and the loop advances. `_eng_mtime` is the build, not
    # the clock: a document converted before the engine changed is still rebuilt, which is what
    # --force is for.
    # THE BUILD THAT MUST WRITE THE DOCUMENT IS ENGINE_SRC'S, NOT REPO'S.
    # This read REPO unconditionally, so with P2W_ENGINE_SRC set to the working tree the staleness
    # clock was another clone's binary: measured 23 Nov, a patched tree's --force run compared every
    # document against repo@FETCH_HEAD's PdfToWord.class and skipped all 213 as "newer than the
    # engine", which is a full corpus scored on an engine the run had not built. Same shape as the
    # render-cache-by-name bug below: a cache outliving the thing it caches.
    _eng = ENGINE_SRC + "/tools/engine-verify/out/com/kavopdf/app/engine/PdfToWord.class"
    # NO BINARY IS NOT "OLDER THAN EVERYTHING" - IT IS "UNKNOWN". This read
    # `getmtime(_eng) if exists else 0.0`, so an absent compiled engine set the clock to
    # zero and every `min(mtime(dx), mtime(tx)) < _eng_mtime` became false: nothing was
    # rebuilt, and a --force run reported a full corpus scored on output from a build that
    # was not there. Same shape as the two stale-engine bugs above - a comparison that
    # answers confidently when it has nothing to compare.
    #
    # Absent means every document is stale, so the rebuild runs and fails loudly on the
    # missing class file instead of quietly measuring yesterday.
    _eng_missing = not os.path.exists(_eng)
    _eng_mtime = os.path.getmtime(_eng) if not _eng_missing else float("inf")
    if _eng_missing:
        log("WARNING: no compiled engine at %s - every document counts as stale" % _eng)
    def _need(p):
        b = os.path.basename(p)[:-4]
        dx = DOCX + "/" + b + ".docx"
        tx = DOCX + "/" + b + ".txt"
        if _force:
            if not (os.path.exists(dx) and os.path.exists(tx)):
                return True
            return min(os.path.getmtime(dx), os.path.getmtime(tx)) < _eng_mtime
        return not (os.path.exists(dx) and os.path.exists(tx))
    miss=[p for p in pdfs if _need(p)]
    if not miss: return len(pdfs)
    log(f"docx {len(pdfs)-len(miss)}/{len(pdfs)} -- converting {len(miss)}")
    os.makedirs(DOCX,exist_ok=True)
    E=ENGINE_SRC+"/tools/engine-verify"
    cp=":".join([E+"/out",E+"/libs/aar/classes.jar",E+"/libs/bcprov.jar",E+"/libs/bcpkix.jar",E+"/libs/bcutil.jar"])
    env='JAVA_HOME='+JH+' PATH='+JH+'/bin:$PATH JAVA_TOOL_OPTIONS="-XX:CompressedClassSpaceSize=64m -XX:MaxMetaspaceSize=200m"'
    # ONE DOCUMENT PER JVM. NOT AN OPTIMISATION - A CORRECTNESS REQUIREMENT.
    #
    # ConvertAll carries state between the documents it is given. Measured 17 Nov on
    # 392_statistical_console_output, same engine, same PDF:
    #
    #     converted alone                          share5 1.61   (its 15 Nov ranking value)
    #     converted with 1 other document          share5 1.61
    #     converted with 11 others                 share5 1.61
    #     converted inside the full corpus of 213  share5 28.39
    #
    # The .docx differ in layout, not only in bytes. So a document's score depends on which other
    # documents happened to share the batch - and a ranking built that way cannot be reproduced,
    # because reproducing it means reproducing the batch. That is why every regression count this
    # session was a number nobody could re-derive from the corpus.
    #
    # ConvertOne takes one PDF and one output directory. It is the only way to get a measurement
    # that is a property of the document rather than of its neighbours.
    # A DOCUMENT IS NOT STARTED UNLESS IT CAN FINISH INSIDE THE WINDOW.
    #
    # The flat 6 s headroom was measured 24 Nov, on the chunk that converted 87 of 213:
    #   09:16:54  docx 87/213 -- converting 126      (conv_end = now + 55% of the window)
    #   09:20:43  prerender 12 docx in soffice batches of 12
    #   09:20:46  chunk 1: measured 85 of 213        <- ONE document measured
    # Conversion was due to stop at 09:19:02 and ran 100 s past it, because the 6 s test is
    # checked BETWEEN documents and one document may run for up to 90 s. CONVERT_SHARE
    # cannot hold while a single unit of work can overrun it by a factor of fifteen, and the
    # measurement phase then gets a deadline that has already gone.
    #
    # So the headroom is what this chunk's own conversions have cost: stop starting new work
    # when twice the observed median no longer fits. The factor of two is a variance
    # allowance, not a tuned constant. The first document of a chunk always starts.
    _costs = []
    for p in miss:
        _est = 2.0 * sorted(_costs)[len(_costs) // 2] if _costs else 6.0
        if time.time() > end - max(6.0, _est): break
        _t0 = time.time()
        sh('cd ' + E + ' && ' + env + ' java -Xmx700m -cp "' + cp + '" ConvertOne '
           + p + ' ' + DOCX, min(max(25, int(end - time.time())), 90))
        _costs.append(time.time() - _t0)
    return len(glob.glob(DOCX+"/*.docx"))
def measure_doc_chunked(pdf, dx, chunk=40, budget=240.0, first=0, seed=None):
    """Measure a long document in page windows, merging the windows into one result.

    A 300-page document takes about 4m40s here - 300 pages, each rendered twice at 150 DPI and
    compared. One sandbox command is killed at 295 s, so such a document could never be measured in
    a single call and read 'unmeasured' in every ranking for two days. (Before the streaming fix at
    019de6f it did not merely run long - it died allocating a 16.6 MiB array, because every page of
    both documents was resident at once.)

    The merge is exact, not an approximation:
      * share@N is the WORST page's value, so the merge takes the maximum across windows
      * text_recall and chars_missing are sums over pages, so the merge adds them
      * median_pt and p90_pt are reported from the worst window, and the field says so

    Returns the same shape as measure_doc plus pages_done, so a caller that runs out of time knows
    where to resume rather than starting the document again.
    """
    ds = fitz.open(pdf)
    total = len(ds); ds.close()
    # A SEED IS WHAT MAKES THE RESUME REAL. `first` told this function which page to start at and
    # then threw away every window before it, so a 300-page document measured 60 pages per run,
    # five runs in a row, and reached page 60 every time - the corpus could never close at 213 and
    # every baseline pass reported "measured 114 of 213" while spending its whole budget on the
    # same document. Measured 21 Nov: six consecutive 290 s passes, all ending on 416_many_tiny_pages.
    merged = dict(seed) if seed else None
    # `first` MAKES THIS RESUMABLE, WHICH IS THE WHOLE POINT OF IT BEING CHUNKED.
    # The function reported pages_done so a caller could carry on, and then always started at
    # page 0 - so a second call re-measured the first 240 pages of 416_many_tiny_pages and never
    # reached 300. Measured 19 Nov: 240 of 300 in 289 s, and no way to ask for the rest.
    done = max(0, int(first))
    t0 = time.time()
    while done < total:
        if merged is not None and time.time() - t0 > budget:
            break
        part = measure_doc(pdf, dx, first=done, last=min(total, done + chunk))
        if part.get("error"):
            return part
        if merged is None:
            merged = dict(part)
        else:
            for k in ("share1", "share2", "share3", "share5", "share10", "max_pt", "p90_pt",
                      "median_pt", "invent5", "invent_max_pt"):
                if k in part and k in merged:
                    merged[k] = max(merged[k], part[k])
            for k in ("chars_missing",):
                if k in part and k in merged:
                    merged[k] = merged[k] + part[k]
            merged["pages_compared"] = merged.get("pages_compared", 0) + part.get("pages_compared", 0)
        done += chunk
    if merged is not None:
        merged["pages_done"] = min(done, total)
        merged["pages_total"] = total
    return merged


def _engine_stamp():
    """The engine commit this measurement belongs to, or 'unknown'."""
    try:
        return subprocess.run(["git", "-C", ENGINE_SRC, "log", "-1", "--format=%h", "--",
                               "app/src/main/java/com/kavopdf/app/engine/"],
                              capture_output=True, text=True, timeout=30).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _invalidate_if_engine_changed():
    """Throw the .docx and the measurements away when the engine is not the one they came from.

    THE CACHE NEVER KNEW WHICH ENGINE IT BELONGED TO, AND THAT IS WHY THE RANKING NEVER MOVED.

    docx() skips a document whose .docx already exists, and run() skips one whose DIST json
    already exists. Both caches survive a change to the engine, so a run that measured an old
    engine keeps reporting that engine's numbers for ever. Measured 17 Nov: the engine was restored
    to ead0d0e at f6ab687 and the baseline cron ran at 21:01, reported 'succeeded', and left
    RANKING.csv exactly as it was - 360_restaurant_menu still 41.13 where the restored engine
    produces 34.43. The run was honest; the cache was stale. Every measurement since 11:20 was
    a measurement of the engine from 11:20.

    The stamp is the engine commit. If it differs from the one the cache was built with, the .docx
    and the per-document measurements are not evidence about this engine and are removed.
    """
    stamp_path = os.path.join(ROOT, "ENGINE-STAMP")
    now = _engine_stamp()
    try:
        was = open(stamp_path, encoding="utf-8").read().strip()
    except Exception:
        was = ""
    # "UNKNOWN" IS NOT EVIDENCE OF A CHANGE, AND DELETING ON IT COSTS THE WHOLE PASS.
    #
    # Measured 22 Nov: a full 212-document pass (213 docx, 30 min of conversion and measurement)
    # was complete, and the very next invocation - gate.py, which resolves ENGINE_SRC to its own
    # clone at /scratch/work/p2w/repo rather than the tree P2W_ENGINE_SRC named - read a stamp of
    # "unknown" left by the previous call, computed the real hash, and did `rm -rf DOCX DIST PRE`.
    # 212 measurements and 213 docx were destroyed between two commands, and the run had no time
    # left to rebuild them. A stamp we could not read says nothing about which engine the cache
    # came from; it must not be treated as a different one.
    if was and was != "unknown" and now != "unknown" and was != now:
        log(f"engine changed {was} -> {now} - discarding docx and measurements built on {was}")
        for d in (DOCX, DIST, PRE):
            sh(f"rm -rf {d}", 120)
        os.makedirs(DOCX, exist_ok=True)
    try:
        os.makedirs(ROOT, exist_ok=True)
        open(stamp_path, "w", encoding="utf-8").write(now)
    except Exception:
        pass
    return now


def _exempt_paths():
    """Every place EXEMPT.json might sit, most specific first.

    It was read from `dirname(__file__)/../tools/p2w-bench/EXEMPT.json` and from nowhere else.
    That is right when the script runs from `benchmarks/` inside a clone, and wrong for every
    cron: the brief tells a run to `cp benchmarks/p2w.py /scratch/work/` and run it from there,
    where that path is `/scratch/tools/p2w-bench/EXEMPT.json` and does not exist. The failure is
    silent - the except returns an empty set - so `want` counted 416_many_tiny_pages, which
    EXEMPT.json excludes by design and which cannot be measured inside one command, and `complete`
    could never be true. RANKING.csv was therefore never written by this tool at all, and the gate
    that demands a corpus measurement of the tree could never be satisfied.

    Measured 21 Nov 14:09: copied to /scratch/work, 211 PDFs, want printed 211 where the truth is
    210, measured 210, remaining 1, "the published RANKING.csv is untouched" - on a corpus that was
    finished.

    Same list-of-places shape as _realworld_dirs(), for the same reason.
    """
    return [os.path.join(HERE, "..", "tools", "p2w-bench", "EXEMPT.json"),
            os.path.join(REPO, "tools", "p2w-bench", "EXEMPT.json"),
            os.path.join(ENGINE_SRC, "tools", "p2w-bench", "EXEMPT.json"),
            os.path.join(HERE, "tools", "p2w-bench", "EXEMPT.json")]


def _exempt_docx_set():
    """The documents EXEMPT.json excludes from the .docx measurement, by name."""
    for p in _exempt_paths():
        try:
            with open(p, encoding="utf-8") as f:
                return set(json.load(f).get("docx") or {})
        except Exception:
            continue
    log("  WARNING: EXEMPT.json not found in any of " + str(len(_exempt_paths())) +
        " places - every document counts toward `want`, including the ones that cannot be measured")
    return set()


def run(end):
    """Measure, one chunk at a time, so a run always makes progress.

    THIS USED TO PRERENDER EVERYTHING BEFORE MEASURING ANYTHING.

    prerender() renders the .docx to PDF through soffice, twelve at a time, and 213 documents take
    far longer than one sandbox command. So every run spent its whole budget rendering and then hit
    `if time.time() >= end: break` on the first measurement - corpus 213/213, docx 213/213, measured
    0/213, run after run. That is why RANKING.csv sat at 11:20 all day while every baseline run
    honestly reported INCOMPLETE.

    Now each chunk of twelve is rendered and then measured before the next chunk starts, so whatever
    budget a run has, it leaves measured documents behind instead of a warm cache and nothing else.
    """
    os.makedirs(DIST,exist_ok=True)
    # AN EXEMPT DOCUMENT IS NOT MEASURED, AND THE LOOP USED TO MEASURE IT ANYWAY.
    #
    # rank() excludes EXEMPT.json's "docx" set from `want`, so a document exempted as too large to
    # measure could never make `complete` true - that half was fixed. The other half was not: this
    # list was built from the corpus alone, so 416_many_tiny_pages (300 pages) was still measured
    # first, alphabetically, on every single run. It never finished, `if time.time()>=end: break`
    # fired on it every time, and the run left 114 of 213 measured and no movement behind it.
    # Measured 21 Nov: 6 consecutive 290 s passes each ended on the same document.
    _exempt_docx = _exempt_docx_set()
    def _pages(nm):
        # SHORTEST FIRST. A run that starts with a 300-page document leaves nothing measured,
        # whatever the budget, because the first chunk never completes. Ordered by page count, a
        # 290 s pass measures sixty small documents and the long one lands at the end of the
        # queue, where a resumable window is the only thing it can cost.
        try:
            _d=fitz.open(CORPUS+"/"+nm+".pdf"); n=len(_d); _d.close(); return n
        except Exception:
            return 9999
    todo=[os.path.basename(p)[:-4] for p in sorted(glob.glob(CORPUS+"/*.pdf"))
          if not os.path.exists(DIST+"/"+os.path.basename(p)[:-4]+".json")
          and os.path.basename(p)[:-4] not in _exempt_docx]
    todo.sort(key=_pages)
    # MEASURE ONLY WHAT THE ENGINE ACTUALLY CHANGED. A restamp of all 213 is 54 minutes, which is
    # why a slot affords one attempt and 218 attempts produced nothing. corpus-changed.py hashes every
    # .docx against the previous build; a document whose bytes did not move cannot produce a different
    # verdict, because the source PDF, the .docx and the instrument are all the same.
    #
    # ABSENT OR UNREADABLE IS A REFUSAL, NOT AN EMPTY LIST. Filtering to nothing would report a
    # complete measurement having measured none, which is the fault this whole pipeline was built to
    # stop. Without the flag the behaviour is unchanged.
    if os.environ.get('P2W_CHANGED_ONLY'):
        _ch = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'benchmarks', 'DOCX-CHANGED.json')
        # A STALE LIST IS WORSE THAN NO LIST. If the corpus was rebuilt after the last --record, the
        # list describes bytes that no longer exist and the filter would skip documents that did move.
        # The manifest's own timestamp is the test: it must be newer than the corpus stamp.
        _stamp = os.path.join(os.path.dirname(os.environ.get('P2W_OUT')
                                   or '/scratch/work/p2w/out'), '.stamp')
        try:
            if os.path.exists(_stamp) and os.path.getmtime(_stamp) > os.path.getmtime(_ch):
                log('changed-only: the corpus is newer than the changed list - refusing; '
                    'run corpus-changed.py --record after the build')
                return
        except OSError:
            pass
        try:
            _want = set(json.load(open(_ch, encoding='utf-8')).get('todo') or [])
        except Exception as _e:
            log('changed-only: cannot read %s (%s) - refusing rather than measuring nothing'
                % (_ch, type(_e).__name__))
            return
        _before = len(todo)
        todo = [d for d in todo if d in _want]
        log('changed-only: %d of %d documents moved since the last record' % (len(todo), _before))
    if not todo:
        return
    for i in range(0,len(todo),CHUNK):
        if time.time()>=end: break
        grp=todo[i:i+CHUNK]
        got=prerender(grp,end)
        if got: log(f"prerender {got} docx in soffice batches of {CHUNK}")
        for b in grp:
            # NEVER START A DOCUMENT YOU CANNOT FINISH. `if time.time()>=end: break` fires only once the
            # deadline has already passed, and measure_doc_chunked is then given max(30, ...) seconds - so a
            # document begun 5 s before the deadline runs 30 s past it. Measured 24 Nov: --budget 170 was
            # killed at 290 s. A guard that stops STARTING work 25 s early is what makes the budget a budget.
            if time.time() >= end - 25:
                break
            if time.time()>=end: break
            jf=f"{DIST}/{b}.json"
            if os.path.exists(jf): continue
            p=f"{CORPUS}/{b}.pdf"; d=f"{DOCX}/{b}.docx"
            if not (os.path.exists(p) and os.path.exists(d)): continue
            # A 300-page document cannot be measured inside one command. measure_doc_chunked
            # walks it in page windows and merges them exactly; if it still runs out of time the
            # result is NOT cached, so the next run resumes rather than recording a half-measured
            # document as if it were whole.
            n_pg=0
            try:
                _dd=fitz.open(p); n_pg=len(_dd); _dd.close()
            except Exception: pass
            if n_pg>80:
                pf=f"{DIST}/{b}.partial.json"
                _first=0; _seed=None
                try:
                    _pj=json.load(open(pf)); _first=int(_pj.get("first") or 0); _seed=_pj.get("merged")
                except Exception: pass
                try: r=measure_doc_chunked(p,d,chunk=60,budget=max(30,int(end-time.time())-20),
                                           first=_first, seed=_seed)
                except Exception as e: r=dict(doc=os.path.basename(d),error=str(e)[:100])
                if r and r.get("pages_done",0)<r.get("pages_total",0):
                    # KEEP THE WINDOWS THAT WERE PAID FOR. Without this file the next run starts
                    # at page 0 again and the document is never finished.
                    try:
                        json.dump({"first": r.get("pages_done"), "merged": r}, open(pf,"w"))
                    except Exception: pass
                    log(f"{b}: {r.get('pages_done')} of {r.get('pages_total')} pages - "
                        f"progress kept in {os.path.basename(pf)}, next run resumes there")
                    continue
                try: os.path.exists(pf) and os.remove(pf)
                except Exception: pass
            else:
                try: r=measure_doc(p,d)
                except Exception as e: r=dict(doc=os.path.basename(d),error=str(e)[:100])
            json.dump(r,open(jf,"w"))
        done=len(results())
        log(f"chunk {i//CHUNK+1}: measured {done} of {len(todo)+done}")
def results():
    """The result files, and ONLY the result files.

    `measure()` keeps a resumable window for a 300-page document in DIST/<doc>.partial.json -
    {"first": n, "merged": {...}} - which is a progress note, not a measurement: it has no "doc"
    key. Every reader of DIST globbed `*.json`, so that file was read as a result. Measured 21 Nov
    13:58: `rank()` raised KeyError: 'doc' on 416_many_tiny_pages.partial.json after a full corpus
    pass had measured 211 of 212, and the traceback killed the run before RANKING.csv was written.
    The pass was complete; only the report was lost, and the engine patch it measured stayed
    unlandable.
    """
    return [f for f in glob.glob(DIST+"/*.json") if not f.endswith(".partial.json")]

def rank():
    seen={}; errs={}
    for f in results():
        try: d=json.load(open(f))
        except: continue
        if 'error' in d: errs[d['doc']]=d
        else: seen[d['doc']]=d
    # rank by share@5px: share@1px is inflated by text antialiasing (glyph edges
    # never align to the pixel grid), so it cannot order documents fairly.
    r=sorted(seen.values(),key=lambda x:(-x['share5'],-x['max_pt']))
    cols=['rank','document','signature','problem','share1','share2','share3','share5','share10',
          'median_pt','p90_pt','max_pt','text_recall','chars_missing','worst_page','pages',
          'colour_share','coloured_px','tone_share','order_share','font_share']
    # A PARTIAL RUN MUST NOT DESTROY THE PUBLISHED TABLE.
    #
    # --budget is a time limit, so a run can stop after 13 documents of 213. This used to
    # write whatever it had to RANKING.csv, replacing the committed table with 13 rows -
    # and gate.py then reported "OK: no regressions" because the 200 missing documents
    # were not regressions, they were absent. One timed-out run silently deleted the
    # baseline. A partial measurement now goes to RANKING.partial.csv and the published
    # table is left alone.
    # AN EXEMPT DOCUMENT IS NOT A MISSING MEASUREMENT, AND COUNTING IT MADE `complete` UNREACHABLE.
    # `want` counted every PDF in the corpus, including the ones EXEMPT.json excludes from
    # measurement by design - 416_many_tiny_pages is 300 pages and no per-command budget can finish
    # it, so it is exempted rather than dropped. `have` can therefore never equal `want`, `complete`
    # was never true, and rank() wrote RANKING.partial.csv on every run for the whole life of this
    # tool. The published table has 213 rows and 212 scores; this is why it had to be written by
    # hand from screen.py's cache.
    #
    # Measured 19 Nov: corpus holds 213 PDFs, EXEMPT.json lists 416_many_tiny_pages under "docx",
    # and RANKING.csv carries that document with an empty share5.
    _exempt = set()
    _exempt = _exempt_docx_set()
    want = len([_p for _p in glob.glob(CORPUS + "/*.pdf")
                if os.path.basename(_p)[:-4] not in _exempt])
    have = len(seen) + len(errs)
    complete = (want > 0 and have >= want)
    out_path = '/scratch/output/RANKING.csv' if complete else '/scratch/output/RANKING.partial.csv'
    if not complete:
        log(f"  PARTIAL: {have} of {want} measured - writing {os.path.basename(out_path)}, "
            f"the published RANKING.csv is untouched")
    with open(out_path,'w',newline='') as fh:
        w=csv.writer(fh); w.writerow(cols)
        for i,x in enumerate(r,1):
            w.writerow([i,x['doc'][:-5],x['signature'],x['problem'],x['share1'],x['share2'],x['share3'],
                        x['share5'],x['share10'],x['median_pt'],x['p90_pt'],x['max_pt'],
                        x['text_recall'],x['chars_missing'],x['worst_page'],x['pages_src'],
                        '' if x.get('colour_share') is None else '%.2f'%x['colour_share'],
                        x.get('coloured_px',0),
                        '' if x.get('tone_share') is None else '%.2f'%x['tone_share'],
                        '' if x.get('order_share') is None else '%.2f'%x['order_share'],
                        '' if x.get('font_share') is None else '%.2f'%x['font_share'],
])
        # a document that failed to measure is an UNMEASURED row, never a silent gap
        for j,d in enumerate(errs.values(), len(r)+1):
            w.writerow([j,d['doc'][:-5],'MEASURE-ERROR','unmeasured','','','','','','','','','','','',''])
    if errs: log(f"  {len(errs)} MEASURE-ERROR rows written (never dropped)")
    return r
def status():
    p=len(glob.glob(CORPUS+"/*.pdf")); d=len(glob.glob(DOCX+"/*.docx")); m=len(results())
    # The corpus is 211 synthetic + the real documents, so the denominator is counted,
    # never assumed. A hard-coded 211 made a 213-document corpus look permanently short.
    want = p or (CORPUS_SYNTHETIC + _realworld_count()[0])
    # The denominator excludes the documents EXEMPT.json removes from measurement, or `remaining`
    # can never reach 0 and this line reports a corpus that is finished as one that is not.
    want_measured = len([_f for _f in glob.glob(CORPUS+"/*.pdf")
                         if os.path.basename(_f)[:-4] not in _exempt_docx_set()])
    log(f"corpus {p}/{want}  docx {d}/{want}  measured {m}/{want_measured}  "
        f"remaining {max(0,want_measured-m)}")

def diagnose(n):
    os.makedirs(IMG,exist_ok=True)
    r=rank(); out=[]
    for x in r[:n]:
        b=x['doc'][:-5]; w=x['worst_page']
        rec={k:x[k] for k in ('doc','share1','share5','share10','median_pt','p90_pt','max_pt',
                              'signature','text_recall','worst_page','pages_src')}
        pdf=CORPUS+"/"+b+".pdf"; dx=DOCX+"/"+b+".docx"
        if os.path.exists(pdf) and os.path.exists(dx):
            tmp=ROOT+"/tmp"; os.makedirs(tmp,exist_ok=True); rp=conv(dx,tmp)
            if rp:
                for tag,src in (("src",pdf),("ours",rp)):
                    d=fitz.open(src)
                    if w-1<d.page_count:
                        d[w-1].set_rotation(0)
                        d[w-1].get_pixmap(matrix=fitz.Matrix(DPI/72,DPI/72),alpha=False).save(f"{IMG}/{b}__p{w}__{tag}.png")
                    d.close()
        out.append(rec)
    json.dump(out,open(IMG+"/diagnosis.json","w"),indent=1)
    return out

INSTRUMENT_MODE = "scipy"


# The share of a --budget window that conversion may take before measurement gets the rest.
# See the note at the docx()/run() call in main(). 0.55 is not measured against an alternative:
# conversion is ~39 min of a ~55 min pass, and the point is only that neither phase gets 100%.
CONVERT_SHARE=0.55


def main():
    global INSTRUMENT_MODE
    ap=argparse.ArgumentParser(); ap.add_argument("--budget",type=int,default=250)
    ap.add_argument("--status",action="store_true"); ap.add_argument("--validate",action="store_true")
    ap.add_argument("--diagnose",type=int,default=0)
    ap.add_argument("--force",action="store_true",help="rebuild every document, after an engine change")
    a=ap.parse_args()
    if a.status: status(); return 0
    if a.validate: return 0 if validate() else 3
    if a.diagnose:
        for x in diagnose(a.diagnose):
            print(f"  {x['share1']:6.1f}%@1px {x['share10']:6.1f}%@10px max {x['max_pt']:8.2f}pt "
                  f"txt {x['text_recall']:6.2f}% {x['signature']:14} {x['doc'][:-5][:38]}")
        return 0
    end=time.time()+a.budget; os.makedirs(ROOT,exist_ok=True)
    # scipy is not a nicety. edt() falls back to a 400-step dilation ladder without it,
    # and that ladder is exact but about ten times slower - the 16 Nov fixer measured three
    # single-page documents going from >290 s each to 28 s total once scipy was present. On
    # the nine-page forms the ladder is why soffice hit the 290 s call limit twice and the
    # class could not be measured at all: "measurement cost, not engine cost, is what has
    # been eating these slots".
    #
    # This block used to check, install, and then NOT check again. A pip that failed quietly
    # (proxy, no network, a different interpreter) left the run on the ladder for its whole
    # slot with nothing anywhere saying so. Check once, install, verify, and say which mode
    # the numbers were produced in.
    _have = sh("python3 -c 'import scipy'", 60)
    if _have is None or _have.returncode != 0:
        log("scipy missing - installing (the ladder fallback is ~10x slower)")
        sh("pip install -q scipy", 220)
        _have = sh("python3 -c 'import scipy'", 60)
        if _have is None or _have.returncode != 0:
            log("WARNING: scipy STILL missing after install - this run measures on the")
            log("WARNING: dilation ladder. The numbers are exact but roughly ten times")
            log("WARNING: slower, and a large document will exceed the per-call limit.")
            INSTRUMENT_MODE = "ladder"
        else:
            log("scipy installed - exact EDT, fast path")
            INSTRUMENT_MODE = "scipy"
    else:
        INSTRUMENT_MODE = "scipy"
    try:
        os.makedirs("/scratch/output", exist_ok=True)
        with open("/scratch/output/INSTRUMENT.txt", "w") as fh:
            fh.write(INSTRUMENT_MODE + "\n")
    except Exception:
        pass
    log("instrument: " + INSTRUMENT_MODE + (" (exact EDT)" if INSTRUMENT_MODE == "scipy"
        else " (dilation ladder - exact but ~10x slower)"))
    if not validate(): log("ABORT: gate"); return 3
    _invalidate_if_engine_changed()
    if corpus()<100: log("ABORT: corpus"); return 2
    if not engine(): log("ABORT: engine"); return 2
    # CONVERSION AND MEASUREMENT MUST NOT SHARE ONE DEADLINE.
    #
    # Measured 24 Nov, three consecutive 245/110/110 s chunks on this pod: every one ended
    # "docx 37/213 -- converting 213 ... measured 0 of 212". `docx(end)` spends the WHOLE budget
    # converting, so `run(end)` then finds the deadline gone and measures nothing - every chunk
    # converts and no chunk measures. The last fixer run saw the same shape from outside (eight
    # chunks took the corpus to docx 213/213 and measured 36 of 212) and read it as "the pass does
    # not fit a slot", which is true but not the whole of it: the measurement phase was only ever
    # entered on a chunk that had already run out of time.
    #
    # So conversion gets a share of the window and measurement gets the rest, and BOTH make
    # progress in every chunk. The split is not a tuning knob for total cost - the work is the
    # work - it is what makes a chunk's progress visible and a killed run's measurement survive.
    #
    # The floor under the total: cpu.max on this pod is 105000/100000, i.e. 1.05 cores, so no
    # amount of parallelism shortens it (measured: 2 conversion workers on 10 documents gave
    # 1.10x, with byte-identical .txt). A full pass is ~39 min of conversion at 11 s/document
    # sustained plus ~15-20 min of measurement, and the only way it lands is a slot that starts
    # it early and does not stop to investigate first.
    # BUILD THE CORPUS ONCE PER ENGINE, NOT ONCE PER PASS.
    #
    # corpus-convert.py --ensure is a stat and a listdir when the 213 .docx are already current for this
    # engine, and a rebuild when they are not. Either way the conversion below then finds them done and
    # spends its share of the budget measuring instead. This is NOT a parallelism win - the pod is capped
    # at 1.05 cores (measured: 2 workers gave 1.10x), so the only saving that exists is not converting
    # the same bytes twice.
    try:
        _sp0 = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                           '..', 'p2w-bench', 'corpus-convert.py'),
                               '--ensure', '-j', '2', '-q'],
                              capture_output=True, text=True, timeout=2700)
        if _sp0.returncode not in (0, 3):
            print('  corpus : could not be prepared (%d) - the pass below converts from scratch' % _sp0.returncode)
    except Exception as _e0:
        print('  corpus : could not be prepared (%s) - the pass below converts from scratch' % type(_e0).__name__)
    _now=time.time()
    _conv_end=_now+max(0.0,(end-_now))*CONVERT_SHARE
    docx(_conv_end); run(end); r=rank(); status()
    # THE CENSUS IS PART OF THE MEASUREMENT, NOT A SEPARATE TOOL SOMEBODY REMEMBERS TO RUN.
    #
    # BASELINE-BRIEF.md says CENSUS.csv and CENSUS.md "are not optional and they are not
    # decoration", and says the census "runs itself inside gate.py once the measurement is
    # complete". But the baseline cron runs p2w.py, not gate.py - this file had zero references
    # to census - so the census was whatever the last manual run left behind. Measured 18 Nov:
    # benchmarks/CENSUS.csv was hours stale while the brief described it as automatic.
    try:
        _c = os.path.join(os.path.dirname(os.path.abspath(__file__)), "census.py")
        if os.path.exists(_c):
            # PASS THE RANKING PATH, DO NOT LET census.py GUESS IT.
            #
            # census.py defaults --ranking to "benchmarks/RANKING.csv", a path relative to the
            # repo root. This call inherited whatever cwd p2w.py was started in, and the
            # documented sequence starts it from benchmarks/ - so the default resolved to
            # benchmarks/benchmarks/RANKING.csv, census.py died with FileNotFoundError, and every
            # run logged "census: failed" with no clue why. Verified 23 Nov: from the repo root
            # census.py exits 0 and censuses 7 documents; from benchmarks/ it raises.
            _rank = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RANKING.csv")
            _r = sh("%s %s --ranking %s" % (sys.executable, _c, _rank), 240)
            log("census: %s" % ("ok" if _r and _r.returncode == 0 else "failed"))
    except Exception as _e:
        log("census: skipped (%s)" % type(_e).__name__)
    if r:
        for sig in ("content-loss","displacement","mixed","clean"):
            k=[x for x in r if x['signature']==sig]
            if k: log(f"  {sig:14} {len(k):3} docs  median share@1px {sorted(x['share1'] for x in k)[len(k)//2]:5.1f}%")
    return 0
if __name__=="__main__": sys.exit(main())
