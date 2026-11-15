#!/usr/bin/env python3
"""p2w -- validated, resumable displacement measurement + per-page diagnosis.

    p2w.py --validate          ground-truth gate only
    p2w.py --budget 250        do work for ~250 s (rebuild whatever is missing)
    p2w.py --status
    p2w.py --diagnose 20       per-page breakdown of the worst N documents
"""
import sys, os, json, subprocess, time, argparse, glob, csv, shutil
import numpy as np
try:
    import fitz
except ImportError:
    os.system("pip install -q pymupdf"); import fitz

ROOT="/scratch/work/p2w"; CORPUS=f"{ROOT}/corpus"; DOCX=f"{ROOT}/out"
DIST=f"{ROOT}/dist2"; CACHE="/scratch/output/_cache"; REPO=f"{ROOT}/repo"
IMG=f"{ROOT}/diag"; ZIPS=["p2w-all-groups","p2w-batch-1","pdf-to-word-test-corpus-v3","p2w-round2-additions"]
JH="/scratch/work/.p2w-jdk/jdk"; INK=68; MATCH=1

def sh(c,t=280):
    try: return subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t)
    except subprocess.TimeoutExpired: return None
def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}",flush=True)

# ---------- instrument ----------
def _dil(m,r):
    h,w=m.shape; t=m.copy()
    for dx in range(-r,r+1): t[:,max(0,-dx):w+min(0,-dx)]|=m[:,max(0,dx):w+min(0,dx)]
    o=t.copy()
    for dy in range(-r,r+1): o[max(0,-dy):h+min(0,-dy),:]|=t[max(0,dy):h+min(0,dy),:]
    return o
def edt(mask,shape,maxr=400):
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
def side(m,other,dpi):
    n=int(m.sum())
    if n==0: return None
    d,_=edt(other,m.shape); un=m&(d>MATCH); nu=int(un.sum()); pt=72.0/dpi
    if nu==0: return dict(share=0.0,max_pt=0.0,n=n,n_unmatched=0)
    return dict(share=round(nu/n,6),max_pt=round(float(d[un].max())*pt,3),n=n,n_unmatched=nu)
def page_side(src,our,dpi):
    H=max(src.shape[0],our.shape[0]); W=max(src.shape[1],our.shape[1])
    sm=pad(src,H,W)<INK; om=pad(our,H,W)<INK
    if sm.sum()==0 and om.sum()==0: return None
    if sm.sum()==0: return dict(loss=None,invent=dict(share=1.0,max_pt=0.0,n=0,n_unmatched=int(om.sum())))
    if om.sum()==0: return dict(loss=dict(share=1.0,max_pt=0.0,n=int(sm.sum()),n_unmatched=int(sm.sum())),invent=None)
    return dict(loss=side(sm,om,dpi),invent=side(om,sm,dpi))

def render(p,dpi=150):
    o=[]; d=fitz.open(p); m=fitz.Matrix(dpi/72.0,dpi/72.0)
    for pg in d:
        x=pg.get_pixmap(matrix=m,colorspace=fitz.csGRAY,alpha=False)
        o.append(np.frombuffer(x.samples,dtype=np.uint8).reshape(x.height,x.width).copy())
    d.close(); return o
def conv(dx,od):
    b=os.path.splitext(os.path.basename(dx))[0]; t=os.path.join(od,b+".pdf")
    subprocess.run(["soffice","--headless","--convert-to","pdf","--outdir",od,dx],check=False,
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
    return t if os.path.exists(t) else None

def measure_doc(pdf,dx,dpi=150):
    tmp=os.path.join(ROOT,"tmp"); os.makedirs(tmp,exist_ok=True)
    rp=conv(dx,tmp)
    if not rp: return dict(doc=os.path.basename(dx),error="no render")
    sp,op=render(pdf,dpi),render(rp,dpi); n=min(len(sp),len(op))
    pages=[]; ln=lu=inn=inu=0; lmax=imax=0.0
    for i in range(n):
        st=page_side(sp[i],op[i],dpi)
        if not st: pages.append(dict(page=i+1,worst=0.0)); continue
        pl=st["loss"]["max_pt"] if st["loss"] else 0.0
        pi=st["invent"]["max_pt"] if st["invent"] else 0.0
        pages.append(dict(page=i+1,worst=max(pl,pi),loss_pt=pl,invent_pt=pi,
                          loss_pct=round(st["loss"]["share"]*100,1) if st["loss"] else 0.0,
                          invent_pct=round(st["invent"]["share"]*100,1) if st["invent"] else 0.0))
        if st["loss"]: ln+=st["loss"]["n"]; lu+=st["loss"]["n_unmatched"]; lmax=max(lmax,pl)
        if st["invent"]: inn+=st["invent"]["n"]; inu+=st["invent"]["n_unmatched"]; imax=max(imax,pi)
    return dict(doc=os.path.basename(dx),pages_src=len(sp),pages_ours=len(op),
        loss_share=round(lu/ln,6) if ln else 0.0,loss_max_pt=round(lmax,3),
        invent_share=round(inu/inn,6) if inn else 0.0,invent_max_pt=round(imax,3),
        worst_pt=round(max(lmax,imax),3),
        worst_page=max(pages,key=lambda x:x["worst"])["page"] if pages else 1,pages=pages)

# ---------- ground truth gate ----------
def validate():
    DPI=150; PT=72.0/DPI
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

# ---------- build ----------
def corpus():
    n=len(glob.glob(f"{CORPUS}/*.pdf"))
    if n>=211: return n
    log(f"corpus {n}/211 -- rebuilding"); os.makedirs(CORPUS,exist_ok=True); os.makedirs(CACHE,exist_ok=True)
    for z in ZIPS:
        c=f"{CACHE}/{z}.zip"
        if not os.path.exists(c): sh(f"gh release download corpus-v1 --repo kavopdf/app -p '{z}.zip' -O '{c}' --clobber",130)
        if os.path.exists(c): sh(f"unzip -oq '{c}' -d {ROOT}/x",130)
    sh(f"find {ROOT}/x -name '*.pdf' -exec cp {{}} {CORPUS}/ \\;",130)
    return len(glob.glob(f"{CORPUS}/*.pdf"))
def engine():
    if os.path.exists(f"{REPO}/tools/engine-verify/out"): return True
    log("engine -- cloning/building"); os.makedirs(ROOT,exist_ok=True)
    if not os.path.exists(f"{REPO}/.git"): sh(f"git clone -q --depth 1 https://github.com/kavopdf/app.git {REPO}",200)
    sh(f"cd {REPO} && bash tools/p2w-bench/build-engine.sh",280)
    ok=os.path.exists(f"{REPO}/tools/engine-verify/out"); log(f"engine: {'ok' if ok else 'FAILED'}"); return ok
def docx(end):
    pdfs=sorted(glob.glob(f"{CORPUS}/*.pdf")); miss=[p for p in pdfs if not os.path.exists(f"{DOCX}/{os.path.basename(p)[:-4]}.docx")]
    if not miss: return len(pdfs)
    log(f"docx {len(pdfs)-len(miss)}/{len(pdfs)} -- converting {len(miss)}")
    os.makedirs(DOCX,exist_ok=True)
    E=REPO+"/tools/engine-verify"
    cp=":".join([E+"/out",E+"/libs/aar/classes.jar",E+"/libs/bcprov.jar",E+"/libs/bcpkix.jar",E+"/libs/bcutil.jar"])
    env=f'JAVA_HOME={JH} PATH={JH}/bin:$PATH JAVA_TOOL_OPTIONS="-XX:CompressedClassSpaceSize=64m -XX:MaxMetaspaceSize=200m"'
    sh(f'cd {E} && {env} java -Xmx700m -cp "{cp}" ConvertAll {CORPUS} {DOCX}',min(max(60,int(end-time.time())),280))
    return len(glob.glob(f"{DOCX}/*.docx"))
def run(end):
    os.makedirs(DIST,exist_ok=True)
    for p in sorted(glob.glob(f"{CORPUS}/*.pdf")):
        if time.time()>=end: break
        b=os.path.basename(p)[:-4]; jf=f"{DIST}/{b}.json"
        if os.path.exists(jf): continue
        d=f"{DOCX}/{b}.docx"
        if not os.path.exists(d): continue
        try: r=measure_doc(p,d)
        except Exception as e: r=dict(doc=os.path.basename(d),error=str(e)[:80])
        json.dump(r,open(jf,"w"))
def rank():
    seen={}
    for f in glob.glob(f"{DIST}/*.json"):
        try: d=json.load(open(f))
        except: continue
        if 'error' not in d: seen[d['doc']]=d
    r=sorted(seen.values(),key=lambda x:-x['worst_pt'])
    with open('/scratch/output/RANKING.csv','w',newline='') as fh:
        w=csv.writer(fh); w.writerow(['rank','document','worst_pt','loss_pct','loss_max_pt','invent_pct','invent_max_pt','pages','worst_page'])
        for i,x in enumerate(r,1):
            w.writerow([i,x['doc'][:-5],x['worst_pt'],round(x['loss_share']*100,1),x['loss_max_pt'],
                        round(x['invent_share']*100,1),x['invent_max_pt'],x.get('pages_src'),x.get('worst_page')])
    return r
def status():
    p=len(glob.glob(f"{CORPUS}/*.pdf")); d=len(glob.glob(f"{DOCX}/*.docx")); m=len(glob.glob(f"{DIST}/*.json"))
    log(f"corpus {p}/211  docx {d}/211  measured {m}/211  remaining {max(0,211-m)}")

# ---------- diagnosis ----------
def diagnose(n):
    os.makedirs(IMG,exist_ok=True)
    r=rank()
    out=[]
    for x in r[:n]:
        b=x['doc'][:-5]; w=x.get('worst_page',1)
        pdf=f"{CORPUS}/{b}.pdf"; dx=f"{DOCX}/{b}.docx"
        rec=dict(document=b,worst_pt=x['worst_pt'],worst_page=w,pages=x.get('pages'),
                 loss_pct=round(x['loss_share']*100,1),invent_pct=round(x['invent_share']*100,1),
                 per_page=x.get('pages',[]))
        if os.path.exists(pdf) and os.path.exists(dx):
            tmp=os.path.join(ROOT,"tmp"); os.makedirs(tmp,exist_ok=True)
            rp=conv(dx,tmp)
            if rp:
                for tag,src in (("src",pdf),("ours",rp)):
                    d=fitz.open(src)
                    if w-1 < d.page_count:
                        pg=d[w-1]; pix=pg.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False)
                        pix.save(f"{IMG}/{b}__p{w}__{tag}.png")
                    d.close()
        out.append(rec)
    json.dump(out,open(f"{IMG}/diagnosis.json","w"),indent=1)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--budget",type=int,default=250)
    ap.add_argument("--status",action="store_true"); ap.add_argument("--validate",action="store_true")
    ap.add_argument("--diagnose",type=int,default=0); a=ap.parse_args()
    if a.status: status(); return 0
    if a.validate: return 0 if validate() else 3
    if a.diagnose: 
        d=diagnose(a.diagnose)
        for x in d: print(f"  {x['worst_pt']:8.2f} p{x['worst_page']}  loss {x['loss_pct']:5.1f}% inv {x['invent_pct']:5.1f}%  {x['document'][:40]}")
        return 0
    end=time.time()+a.budget; os.makedirs(ROOT,exist_ok=True)
    if sh("python3 -c 'import scipy'",60) is None or sh("python3 -c 'import scipy'",60).returncode!=0:
        log("installing scipy"); sh("pip install -q scipy",220)
    if not validate(): log("ABORT: gate"); return 3
    if corpus()<100: log("ABORT: corpus"); return 2
    if not engine(): log("ABORT: engine"); return 2
    docx(end); run(end); r=rank(); status()
    if r:
        s=sorted(x['worst_pt'] for x in r); k=len(r)
        log(f"median {s[k//2]:.2f}pt  p90 {s[int(k*.9)]:.2f}  worst {s[-1]:.2f}")
    return 0
if __name__=="__main__": sys.exit(main())
