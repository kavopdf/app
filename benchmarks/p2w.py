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
import sys, os, json, subprocess, time, argparse, glob, csv, re
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
IMG=ROOT+"/diag"; PRE=ROOT+"/pre"; CHUNK=12; ZIPS=["p2w-all-groups","p2w-batch-1","pdf-to-word-test-corpus-v3","p2w-round2-additions"]
JH="/scratch/work/.p2w-jdk/jdk"; INK=68; DPI=150; PT=72.0/DPI
SWEEP=[1,2,3,5,10]

def sh(c,t=280):
    try: return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t)
    except subprocess.TimeoutExpired: return None
def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}",flush=True)

# ---------------- geometry helpers ----------------
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
# SOFFICE FINISHES THE CONVERSION AND THEN NEVER EXITS - SO WE WAIT FOR THE FILE, NOT THE PID.
#
# Measured 16 Nov on 041122-Account_Opening_Form.docx (9 pages, 4.5 MB document.xml): the PDF
# is complete on disk 97 s after launch, and the process is still alive 240 s later. Both
# `soffice` (the oosplash wrapper) and `/usr/lib/libreoffice/program/soffice.bin` called
# directly do this; after the kill, soffice.bin sits in state Z and oosplash keeps the pipe
# open, so anything that waits for the process - subprocess.run with a timeout included -
# blocks until the caller's own ceiling, with the finished PDF already written.
#
# That is what "the two nine-page bank forms cannot be converted inside the 290 s call limit"
# actually was: not a slow render and not a hard PDF. A pass that converts 12 documents per
# launch (see prerender) lost the whole batch to a process that had already finished its work,
# which is why the class measurement stalled and the ratchet never ran.
#
# So: launch in its own session, poll for the output files to appear and stop growing, then
# kill the session. The PDF is the deliverable; the exit code never was.
SOFFICE_BIN = "/usr/lib/libreoffice/program/soffice.bin"

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
    cmd = [_soffice_exe(), "--headless", "--norestore"] + list(extra or []) + \
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
    if not got:
        got = [w for w in want if os.path.exists(w) and os.path.getsize(w) > 0]
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
def prerender(names,end):
    os.makedirs(PRE,exist_ok=True); n=0
    for i in range(0,len(names),CHUNK):
        if time.time()>=end: break
        grp=[b for b in names[i:i+CHUNK]
             if not _cached_render(DOCX+"/"+b+".docx")]
        fs=[DOCX+"/"+b+".docx" for b in grp if os.path.exists(DOCX+"/"+b+".docx")]
        if not fs: continue
        soffice_pdf(fs, PRE, deadline=min(end, time.time()+280))
        for f in fs:
            p = PRE + "/" + os.path.splitext(os.path.basename(f))[0] + ".pdf"
            if os.path.exists(p): _stamp_render(f, p)
        n+=len(fs)
    return n

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

def problem_name(sig, share5, invent5, max_pt):
    """The NAME of the defect, derived from the numbers alone.

    Measurement, not opinion: every branch is a statement about the two axes,
    nothing is a guess about the engine's internals. It answers 'what kind of
    problem is this document' without anyone opening a rendered image."""
    if share5 < 1.0:           return "none"
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

def measure_doc(pdf,dx):
    tmp=ROOT+"/tmp"; os.makedirs(tmp,exist_ok=True)
    rp=conv(dx,tmp)
    if not rp: return dict(doc=os.path.basename(dx),error="no render")
    sp,op=render(pdf),render(rp)
    st,ot=text_of(pdf),text_of(rp)
    n=min(len(sp),len(op))
    pages=[]
    for i in range(n):
        p=position(sp[i],op[i])
        c=content([st[i]] if i<len(st) else [""],[ot[i]] if i<len(ot) else [""])
        inv=invention(sp[i],op[i])
        p["page"]=i+1; p["signature"]=signature(p); p["text_recall"]=c["recall"]
        p["invent5"]=inv["shares"][5]; p["invent_max_pt"]=inv["max_pt"]
        pages.append(p)
    worst=max(pages,key=lambda x:x["shares"][5]) if pages else None
    ct=content(st,ot)
    return dict(doc=os.path.basename(dx),
        pages_src=len(sp),pages_ours=len(op),pages_compared=n,
        extra_pages=max(0,len(op)-len(sp)),missing_pages=max(0,len(sp)-len(op)),
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
        signature=worst["signature"] if worst else "clean",
        invent5=worst.get("invent5",0.0) if worst else 0.0,
        invent_max_pt=worst.get("invent_max_pt",0.0) if worst else 0.0,
        problem=problem_name(worst["signature"],worst["shares"][5],
                             worst.get("invent5",0.0),worst["max_pt"]) if worst else "none",
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
    # The real-world documents travel with the repository, not the release, so a cron that
    # clones the repo gets them without any extra download. real_dir is wherever they were
    # actually found - see _realworld_dirs() for why it is not simply HERE/realworld.
    if real_dir:
        sh(f"cp {real_dir}/*.pdf {CORPUS}/",60)
    return len(glob.glob(CORPUS+"/*.pdf"))
def engine():
    if os.path.exists(REPO+"/tools/engine-verify/out"): return True
    log("engine -- cloning/building"); os.makedirs(ROOT,exist_ok=True)
    if not os.path.exists(REPO+"/.git"): sh("git clone -q --depth 1 https://github.com/kavopdf/app.git "+REPO,200)
    sh("cd "+REPO+" && bash tools/p2w-bench/build-engine.sh",280)
    ok=os.path.exists(REPO+"/tools/engine-verify/out"); log(f"engine: {'ok' if ok else 'FAILED'}"); return ok
def docx(end):
    pdfs=sorted(glob.glob(CORPUS+"/*.pdf"))
    miss=[p for p in pdfs if not os.path.exists(DOCX+"/"+os.path.basename(p)[:-4]+".docx")]
    if not miss: return len(pdfs)
    log(f"docx {len(pdfs)-len(miss)}/{len(pdfs)} -- converting {len(miss)}")
    os.makedirs(DOCX,exist_ok=True)
    E=REPO+"/tools/engine-verify"
    cp=":".join([E+"/out",E+"/libs/aar/classes.jar",E+"/libs/bcprov.jar",E+"/libs/bcpkix.jar",E+"/libs/bcutil.jar"])
    env='JAVA_HOME='+JH+' PATH='+JH+'/bin:$PATH JAVA_TOOL_OPTIONS="-XX:CompressedClassSpaceSize=64m -XX:MaxMetaspaceSize=200m"'
    sh('cd '+E+' && '+env+' java -Xmx700m -cp "'+cp+'" ConvertAll '+CORPUS+' '+DOCX,min(max(60,int(end-time.time())),280))
    return len(glob.glob(DOCX+"/*.docx"))
def _engine_stamp():
    """The engine commit this measurement belongs to, or 'unknown'."""
    try:
        return subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h", "--",
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
    if was and was != now:
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
    todo=[os.path.basename(p)[:-4] for p in sorted(glob.glob(CORPUS+"/*.pdf"))
          if not os.path.exists(DIST+"/"+os.path.basename(p)[:-4]+".json")]
    if not todo:
        return
    for i in range(0,len(todo),CHUNK):
        if time.time()>=end: break
        grp=todo[i:i+CHUNK]
        got=prerender(grp,end)
        if got: log(f"prerender {got} docx in soffice batches of {CHUNK}")
        for b in grp:
            if time.time()>=end: break
            jf=f"{DIST}/{b}.json"
            if os.path.exists(jf): continue
            p=f"{CORPUS}/{b}.pdf"; d=f"{DOCX}/{b}.docx"
            if not (os.path.exists(p) and os.path.exists(d)): continue
            try: r=measure_doc(p,d)
            except Exception as e: r=dict(doc=os.path.basename(d),error=str(e)[:100])
            json.dump(r,open(jf,"w"))
        done=len(glob.glob(DIST+"/*.json"))
        log(f"chunk {i//CHUNK+1}: measured {done} of {len(todo)+done}")
def rank():
    seen={}; errs={}
    for f in glob.glob(DIST+"/*.json"):
        try: d=json.load(open(f))
        except: continue
        if 'error' in d: errs[d['doc']]=d
        else: seen[d['doc']]=d
    # rank by share@5px: share@1px is inflated by text antialiasing (glyph edges
    # never align to the pixel grid), so it cannot order documents fairly.
    r=sorted(seen.values(),key=lambda x:(-x['share5'],-x['max_pt']))
    cols=['rank','document','signature','problem','share1','share2','share3','share5','share10',
          'median_pt','p90_pt','max_pt','text_recall','chars_missing','worst_page','pages']
    # A PARTIAL RUN MUST NOT DESTROY THE PUBLISHED TABLE.
    #
    # --budget is a time limit, so a run can stop after 13 documents of 213. This used to
    # write whatever it had to RANKING.csv, replacing the committed table with 13 rows -
    # and gate.py then reported "OK: no regressions" because the 200 missing documents
    # were not regressions, they were absent. One timed-out run silently deleted the
    # baseline. A partial measurement now goes to RANKING.partial.csv and the published
    # table is left alone.
    want = len(glob.glob(CORPUS + "/*.pdf"))
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
                        x['text_recall'],x['chars_missing'],x['worst_page'],x['pages_src']])
        # a document that failed to measure is an UNMEASURED row, never a silent gap
        for j,d in enumerate(errs.values(), len(r)+1):
            w.writerow([j,d['doc'][:-5],'MEASURE-ERROR','unmeasured','','','','','','','','','','','',''])
    if errs: log(f"  {len(errs)} MEASURE-ERROR rows written (never dropped)")
    return r
def status():
    p=len(glob.glob(CORPUS+"/*.pdf")); d=len(glob.glob(DOCX+"/*.docx")); m=len(glob.glob(DIST+"/*.json"))
    # The corpus is 211 synthetic + the real documents, so the denominator is counted,
    # never assumed. A hard-coded 211 made a 213-document corpus look permanently short.
    want = p or (CORPUS_SYNTHETIC + _realworld_count()[0])
    log(f"corpus {p}/{want}  docx {d}/{want}  measured {m}/{want}  remaining {max(0,want-m)}")

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


def main():
    global INSTRUMENT_MODE
    ap=argparse.ArgumentParser(); ap.add_argument("--budget",type=int,default=250)
    ap.add_argument("--status",action="store_true"); ap.add_argument("--validate",action="store_true")
    ap.add_argument("--diagnose",type=int,default=0); a=ap.parse_args()
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
    docx(end); run(end); r=rank(); status()
    if r:
        for sig in ("content-loss","displacement","mixed","clean"):
            k=[x for x in r if x['signature']==sig]
            if k: log(f"  {sig:14} {len(k):3} docs  median share@1px {sorted(x['share1'] for x in k)[len(k)//2]:5.1f}%")
    return 0
if __name__=="__main__": sys.exit(main())
