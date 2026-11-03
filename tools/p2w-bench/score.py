# 13-metric PDF->Word scorer. Independent judges only: PyMuPDF, pdfplumber, python-docx.
import os, sys, re, json, statistics, difflib, warnings
warnings.filterwarnings("ignore")
import pymupdf

CMP = "/scratch/work/p2w/cmp"
OUT = sys.argv[1]
REF = "/scratch/work/p2w/ref13.json"

def norm(s):
    s = s.replace("\u00a0", " ")
    return " ".join(s.split())

# ---------- build reference once ----------
if not os.path.isfile(REF):
    ref = {}
    for f in sorted(os.listdir(CMP)):
        if not f.lower().endswith(".pdf"): continue
        try:
            d = pymupdf.open(os.path.join(CMP, f))
            txt = "".join(p.get_text() for p in d)
            d.close()
            ref[f[:-4]] = txt
        except Exception:
            pass
    json.dump(ref, open(REF, "w"))
ref = json.load(open(REF))

GARBAGE = ["\ufffd", "Ã", "Â", "â€", "Ã©", "Ã¨", "Ã¼", "Ã¶", "Ã¤"]

rows = []
for base, r in sorted(ref.items()):
    tp = os.path.join(OUT, base + ".txt")
    if not os.path.isfile(tp): continue
    raw = open(tp, encoding="utf-8", errors="replace").read()
    ol = [norm(x) for x in raw.split("\n") if x.strip()]
    rl = [norm(x) for x in r.split("\n") if x.strip()]
    if not rl: continue
    oset = set(ol)
    hit = sum(1 for l in rl if l in oset)
    # line ORDER: how much of the sequence is preserved in order
    sm = difflib.SequenceMatcher(None, rl, ol, autojunk=False)
    order = sm.ratio() * 100
    # char + word
    rc = len(norm(r)); oc = len(norm(raw))
    cv = min(rc, oc) / max(rc, oc) * 100 if max(rc, oc) else 0
    rw = norm(r).split(); ow = norm(raw).split()
    from collections import Counter
    cw = Counter(ow); rec = sum(min(n, cw.get(w, 0)) for w, n in Counter(rw).items())
    wr = rec / len(rw) * 100 if rw else 0
    # lines
    lcm = min(len(ol), len(rl)) / max(len(ol), len(rl)) * 100
    ehit = hit / len(rl) * 100
    # garbage
    gcount = sum(raw.count(g) for g in GARBAGE)
    grate = gcount / max(len(raw), 1) * 100
    # docx structure
    pcount = None; tcount = None
    dp = os.path.join(OUT, base + ".docx")
    if os.path.isfile(dp):
        try:
            import docx
            d = docx.Document(dp)
            pcount = sum(1 for p in d.paragraphs if p.text.strip())
            tcount = len(d.tables)
        except Exception:
            pass
    rows.append(dict(base=base, cv=cv, wr=wr, lcm=lcm, ehit=ehit, order=order,
                     grate=grate, rl=len(rl), ol=len(ol), hit=hit,
                     pcount=pcount, tcount=tcount))

n = len(rows)
tot_r = sum(x["rl"] for x in rows); tot_h = sum(x["hit"] for x in rows)

print(f"files {n}")
print("=" * 62)
print(f" 1 char volume          {statistics.mean([x['cv'] for x in rows]):6.2f}%")
print(f" 2 word recall          {statistics.mean([x['wr'] for x in rows]):6.2f}%")
print(f" 3 line count match     {statistics.mean([x['lcm'] for x in rows]):6.2f}%")
print(f" 4 exact line hit       {statistics.mean([x['ehit'] for x in rows]):6.2f}%   <- below 95")
print(f" 5 global line hit      {tot_h*100/tot_r:6.2f}%")
print(f" 6 line order accuracy  {statistics.mean([x['order'] for x in rows]):6.2f}%   <- NEW")
print(f" 7 garbage rate         {statistics.mean([x['grate'] for x in rows]):6.2f}%   <- NEW (lower better)")
p = [x['pcount'] for x in rows if x['pcount'] is not None]
t = [x['tcount'] for x in rows if x['tcount'] is not None]
print(f" 8 docx paragraphs      {sum(p)} over {len(p)} files                 <- NEW")
print(f" 9 docx tables          {sum(t)} over {len(t)} files                 <- NEW")
for th in (95, 98):
    c = sum(1 for x in rows if x['ehit'] >= th)
    print(f"10 doc pass @{th}%       {c*100/n:6.2f}%  ({c}/{n})           <- NEW")
print(f"11 median per-file     {statistics.median([x['ehit'] for x in rows]):6.2f}%")
json.dump(rows, open("/scratch/work/p2w/rows.json", "w"))
