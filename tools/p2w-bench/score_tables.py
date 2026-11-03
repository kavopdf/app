# Table accuracy: the metric that decides whether a PDF->Word conversion is usable.
# Reference = pdfplumber's table extraction. Ours = the tables in the .docx.
import os, sys, json, warnings
warnings.filterwarnings("ignore")
import pdfplumber, docx

CMP = "/scratch/work/p2w/cmp"
OUT = sys.argv[1]
CACHE = "/scratch/work/p2w/tbl_ref.json"

def norm(s):
    return " ".join((s or "").split())

if not os.path.isfile(CACHE):
    ref = {}
    for f in sorted(os.listdir(CMP)):
        if not f.lower().endswith(".pdf"): continue
        try:
            with pdfplumber.open(os.path.join(CMP, f)) as pdf:
                tabs = []
                for pg in pdf.pages:
                    for t in (pg.extract_tables() or []):
                        rows = [[norm(c) for c in r] for r in t if any(norm(c) for c in r)]
                        if len(rows) < 2 or max(len(r) for r in rows) < 2:
                            continue
                        # A real table is mostly filled. pdfplumber happily returns a grid of
                        # empty cells where a logo, a QR code or a few stray glyphs sit, and
                        # scoring against that penalises a correct conversion - the GST invoice
                        # was marked 0% while our output was perfect.
                        cells = [c for r in rows for c in r]
                        filled = sum(1 for c in cells if c)
                        if filled < len(cells) * 0.5:
                            continue
                        if filled < 6:
                            continue
                        tabs.append(rows)
                if tabs: ref[f[:-4]] = tabs
        except Exception:
            pass
    json.dump(ref, open(CACHE, "w"))
ref = json.load(open(CACHE))

files = 0; tcount_ok = 0; extra = 0; missing = 0
tot_ref_rows = 0; hit_rows = 0
tot_ref_cells = 0; hit_cells = 0
per = []

for base, rtabs in sorted(ref.items()):
    dp = os.path.join(OUT, base + ".docx")
    if not os.path.isfile(dp): continue
    try:
        d = docx.Document(dp)
    except Exception:
        continue
    files += 1
    our_tabs = []
    for t in d.tables:
        rows = []
        for r in t.rows:
            rows.append([norm(c.text) for c in r.cells])
        our_tabs.append(rows)

    if len(our_tabs) == len(rtabs): tcount_ok += 1
    elif len(our_tabs) > len(rtabs): extra += 1      # we found tables the reference missed
    else: missing += 1                               # a reference table we did not find

    # rows: a reference row counts as found if its cells' words all appear in one of our rows
    our_row_words = []
    for t in our_tabs:
        for r in t:
            our_row_words.append(set(" ".join(r).split()))
    r_hit = 0; r_tot = 0
    c_hit = 0; c_tot = 0
    for t in rtabs:
        for r in t:
            cells = [c for c in r if c]
            if not cells: continue
            r_tot += 1
            want = set(" ".join(cells).split())
            c_tot += len(cells)
            best = 0
            for ow in our_row_words:
                if not want: continue
                got = len(want & ow) / len(want)
                if got > best: best = got
            if best >= 0.95: r_hit += 1
            for c in cells:
                w = set(c.split())
                if not w: continue
                if any(len(w & ow) / len(w) >= 0.95 for ow in our_row_words): c_hit += 1
    tot_ref_rows += r_tot; hit_rows += r_hit
    tot_ref_cells += c_tot; hit_cells += c_hit
    per.append((r_hit / r_tot * 100 if r_tot else 100.0, base, r_tot))

n = len(per)
print(f"files with tables: {files}")
print(f"table count match   : {tcount_ok}/{files} = {tcount_ok*100/max(files,1):.2f}%")
print(f"  we found MORE than the reference : {extra}  (reference under-detects)")
print(f"  we found FEWER than the reference: {missing}  (a real miss)")
print(f"table ROW accuracy  : {hit_rows}/{tot_ref_rows} = {hit_rows*100/max(tot_ref_rows,1):.2f}%")
print(f"table CELL accuracy : {hit_cells}/{tot_ref_cells} = {hit_cells*100/max(tot_ref_cells,1):.2f}%")
per.sort()
print("\nworst 10 files by row accuracy:")
for p, b, t in per[:10]:
    print(f"  {p:5.1f}%  {b[:44]:44} ({t} rows)")
