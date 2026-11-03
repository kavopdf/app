# ID integrity: do the identifiers a business document depends on survive exactly?
# A wrong GSTIN, CIN, invoice number or account number makes the whole document useless,
# and char volume / word recall cannot see it because they measure totals, not strings.
import os, sys, re, json, warnings
warnings.filterwarnings("ignore")
import pymupdf
CMP="/scratch/work/base53/in"; OUT=sys.argv[1]

PATS = [
 ("gstin",   r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b"),
 ("pan",     r"\b[A-Z]{5}\d{4}[A-Z]\b"),
 ("cin",     r"\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b"),
 ("ifsc",    r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
 ("acct",    r"\b\d{11,18}\b"),
 ("invoice", r"\b[A-Z]{2,5}/\d{2}-\d{2}/\d{2,6}\b"),
 ("eway",    r"\b\d{12}\b"),
 ("uin",     r"\b\d{12,14}\b"),
]
def find(text):
    out=set()
    for name,p in PATS:
        for m in re.finditer(p, text):
            out.add((name, m.group(0)))
    return out

tot=0; kept=0; lost=[]; per=[]
for f in sorted(os.listdir(CMP)):
    if not f.lower().endswith(".pdf"): continue
    b=f[:-4]; tp=os.path.join(OUT,b+".txt")
    if not os.path.isfile(tp): continue
    d=pymupdf.open(os.path.join(CMP,f)); ref="".join(p.get_text() for p in d); d.close()
    ours=open(tp,encoding="utf-8",errors="replace").read()
    rid=find(ref)
    if not rid: continue
    def exact(v):
        # The ID must appear as a whole token. "CIN U28129HR2004PTC" followed by "0412" is a
        # different CIN, and a substring test calls that a pass.
        for m in re.finditer(re.escape(v), ours):
            a = ours[m.start()-1] if m.start() > 0 else " "
            b = ours[m.end()] if m.end() < len(ours) else " "
            if not (a.isalnum()) and not (b.isalnum()):
                return True
        return False
    oid={i for i in rid if exact(i[1])}
    tot+=len(rid); kept+=len(oid)
    miss=[i for i in rid if i not in oid]
    per.append((len(oid)*100/len(rid), b, miss))
    if miss: lost.append((b, miss))
print(f"documents with identifiers: {len(per)}")
print(f"ID INTEGRITY: {kept}/{tot} = {kept*100/max(tot,1):.2f}%")
print(f"documents with a lost or corrupted ID: {len(lost)}/{len(per)}")
for b,miss in lost[:12]:
    print(f"  {b[:40]:40} lost={len(miss)}")
    for name,val in miss[:3]: print(f"      {name}: {val}")
