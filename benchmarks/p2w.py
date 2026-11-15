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
DIST=ROOT+"/dist2"; CACHE="/scratch/output/_cache"; REPO=ROOT+"/repo"
IMG=ROOT+"/diag"; ZIPS=["p2w-all-groups","p2w-batch-1","pdf-to-word-test-corpus-v3","p2w-round2-additions"]
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
    """Exact distance to the nearest True. scipy's published EDT; ladder fallback."""
    try:
        from scipy.ndimage import distance_transform_edt
        return distance_transform_edt(~mask).astype(np.int32),"scipy"
    except ImportError: pass
    d=np.full(shape,maxr,np.int32); done=np.zeros(shape,bool)
    for r in range(maxr+1):
        cur=mask if r==0 else _dil(mask,r); hit=cur&~done
        if hit.any(): d[hit]=r; done|=hit
        if done.all(): break
    return d,"ladder"
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
def conv(dx,od):
    b=os.path.splitext(os.path.basename(dx))[0]; t=os.path.join(od,b+".pdf")
    subprocess.run(["soffice","--headless","--convert-to","pdf","--outdir",od,dx],check=False,
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=300)
    return t if os.path.exists(t) else None

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
def corpus():
    n=len(glob.glob(CORPUS+"/*.pdf"))
    if n>=211: return n
    log(f"corpus {n}/211 -- rebuilding"); os.makedirs(CORPUS,exist_ok=True); os.makedirs(CACHE,exist_ok=True)
    for z in ZIPS:
        c=f"{CACHE}/{z}.zip"
        if not os.path.exists(c): sh(f"gh release download corpus-v1 --repo kavopdf/app -p '{z}.zip' -O '{c}' --clobber",130)
        if os.path.exists(c): sh(f"unzip -oq '{c}' -d {ROOT}/x",130)
    sh("find "+ROOT+"/x -name '*.pdf' -exec cp {} "+CORPUS+"/ \\;",130)
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
def run(end):
    os.makedirs(DIST,exist_ok=True)
    for p in sorted(glob.glob(CORPUS+"/*.pdf")):
        if time.time()>=end: break
        b=os.path.basename(p)[:-4]; jf=f"{DIST}/{b}.json"
        if os.path.exists(jf): continue
        d=f"{DOCX}/{b}.docx"
        if not os.path.exists(d): continue
        try: r=measure_doc(p,d)
        except Exception as e: r=dict(doc=os.path.basename(d),error=str(e)[:100])
        json.dump(r,open(jf,"w"))
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
    with open('/scratch/output/RANKING.csv','w',newline='') as fh:
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
    log(f"corpus {p}/211  docx {d}/211  measured {m}/211  remaining {max(0,211-m)}")

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

def main():
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
    if sh("python3 -c 'import scipy'",60) is None or sh("python3 -c 'import scipy'",60).returncode!=0:
        log("installing scipy"); sh("pip install -q scipy",220)
    if not validate(): log("ABORT: gate"); return 3
    if corpus()<100: log("ABORT: corpus"); return 2
    if not engine(): log("ABORT: engine"); return 2
    docx(end); run(end); r=rank(); status()
    if r:
        for sig in ("content-loss","displacement","mixed","clean"):
            k=[x for x in r if x['signature']==sig]
            if k: log(f"  {sig:14} {len(k):3} docs  median share@1px {sorted(x['share1'] for x in k)[len(k)//2]:5.1f}%")
    return 0
if __name__=="__main__": sys.exit(main())
