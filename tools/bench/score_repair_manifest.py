#!/usr/bin/env python3
"""
Score the repair batch against the manifest's own reference numbers.

The manifest carries what PyMuPDF recovered from each damaged file (ref_pages,
ref_text_chars) and what the healthy source held (original_pages, original_text_chars).
Those are the ceiling and the target:

    ceiling  = ref_*        what any tool could hope to get from the damaged file
    target   = original_*   what the file held before it was damaged

So each file is scored on two things:
    vs ceiling   - did we get everything that was still recoverable?
    vs original  - how much of the real document came back?

Both matter and they are not the same number. A file that only held 40 % of its text after
damage scores 100 % against the ceiling and 40 % against the original, and both statements
are true.

    python3 score_repair_manifest.py <inDir> <outDir> <report.jsonl> <manifest.csv>
"""
import os, sys, csv, json, warnings
warnings.filterwarnings("ignore")
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
pymupdf.TOOLS.mupdf_display_warnings(False)

IN = sys.argv[1]
OUT = sys.argv[2]
REPORT = sys.argv[3]
MANIFEST = sys.argv[4]

# ---------------------------------------------------------------- manifest
man = {}
with open(MANIFEST, encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        man[row["file"]] = row

# ---------------------------------------------------------------- engine report
rep = {}
with open(REPORT, encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            rep[r["file"]] = r
        except Exception:
            pass

def read(path):
    """Page count and text length, or None when the file will not open."""
    try:
        d = pymupdf.open(path)
    except Exception:
        return None
    if d.needs_pass:
        d.close()
        return None
    n = 0
    try:
        n = len(d)
    except Exception:
        n = 0
    chars = 0
    for i in range(n):
        try:
            chars += len(" ".join(d.load_page(i).get_text().split()))
        except Exception:
            pass
    d.close()
    return n, chars

rows = []
for name, m in sorted(man.items()):
    r = rep.get(name)
    if r is None:
        continue
    res = read(os.path.join(OUT, name))
    pages, chars = (res if res else (0, 0))
    opened = res is not None

    ref_pages = int(m.get("ref_pages") or 0)
    ref_chars = int(m.get("ref_text_chars") or 0)
    orig_pages = int(m.get("original_pages") or 0)
    orig_chars = int(m.get("original_text_chars") or 0)
    noref = (m.get("noref") or "").strip() == "1"

    rows.append({
        "file": name,
        "group": m.get("group", "?"),
        "group_name": m.get("group_name", ""),
        "faults": (m.get("faults") or "")[:80],
        "expected": m.get("expected_recovery", ""),
        "threw": bool(r.get("threw")),
        "verified": bool(r.get("verified")),
        "stage": r.get("stage", ""),
        "opened": opened,
        "pages": pages,
        "chars": chars,
        "ref_pages": ref_pages,
        "ref_chars": ref_chars,
        "orig_pages": orig_pages,
        "orig_chars": orig_chars,
        "noref": noref,
        "ms": r.get("ms", 0),
    })

# ---------------------------------------------------------------- aggregates
def pct(a, b):
    return round(a * 100.0 / b, 1) if b else None

tot = len(rows)
threw = sum(1 for x in rows if x["threw"])
opened = sum(1 for x in rows if x["opened"])
false_ok = sum(1 for x in rows if x["verified"] and not x["opened"])
honest = sum(1 for x in rows if not x["verified"] and not x["opened"])
slow = sum(1 for x in rows if x["ms"] > 8000)

# pages and text, only where a reference exists
with_ref = [x for x in rows if not x["noref"] and x["ref_pages"] > 0]
pg_vs_ref = sum(min(x["pages"], x["ref_pages"]) for x in with_ref)
pg_ref = sum(x["ref_pages"] for x in with_ref)
pg_vs_orig = sum(min(x["pages"], x["orig_pages"]) for x in with_ref)
pg_orig = sum(x["orig_pages"] for x in with_ref)

with_txt = [x for x in rows if not x["noref"] and x["ref_chars"] > 0]
tx_vs_ref = sum(min(x["chars"], x["ref_chars"]) for x in with_txt)
tx_ref = sum(x["ref_chars"] for x in with_txt)
tx_vs_orig = sum(min(x["chars"], x["orig_chars"]) for x in with_txt)
tx_orig = sum(x["orig_chars"] for x in with_txt)

M = []
def add(group, name, value, unit, verdict):
    M.append((group, name, value, unit, verdict))

add("Repair PDF", "files", tot, "files", "pass")
add("Repair PDF", "crashes", threw, "exceptions", "pass" if threw == 0 else "FAIL")
add("Repair PDF", "output opens", pct(opened, tot), "%",
    "pass" if opened == tot else "WARN")
add("Repair PDF", "false success (verified but will not open)", false_ok, "files",
    "pass" if false_ok == 0 else "FAIL")
add("Repair PDF", "honest refusals", honest, "files", "pass")
add("Repair PDF", "pages vs recoverable ceiling", pct(pg_vs_ref, pg_ref), "%",
    "pass" if (pct(pg_vs_ref, pg_ref) or 0) >= 99 else "WARN")
add("Repair PDF", "pages vs the original document", pct(pg_vs_orig, pg_orig), "%",
    "pass" if (pct(pg_vs_orig, pg_orig) or 0) >= 95 else "WARN")
add("Repair PDF", "text vs recoverable ceiling", pct(tx_vs_ref, tx_ref), "%",
    "pass" if (pct(tx_vs_ref, tx_ref) or 0) >= 99 else "WARN")
add("Repair PDF", "text vs the original document", pct(tx_vs_orig, tx_orig), "%",
    "pass" if (pct(tx_vs_orig, tx_orig) or 0) >= 95 else "WARN")
add("Repair PDF", "slow runs (>8 s)", slow, "files", "pass" if slow == 0 else "WARN")

print(f"{'BENCHMARK':<52} {'VALUE':>10}  {'UNIT':<22} VERDICT")
print("=" * 100)
for g, n, v, u, vd in M:
    vs = f"{v:.2f}" if isinstance(v, float) else f"{v}"
    print(f"{g + ' | ' + n:<52}"[:52] + f" {vs:>10}  {u:<22} {vd or ''}")
print("=" * 100)

# ---------------------------------------------------------------- per group
print()
print(f"{'GRP':<5} {'NAME':<34} {'N':>4} {'opens':>6} {'pg/ref':>7} {'pg/orig':>8} {'tx/ref':>7} {'tx/orig':>8} {'stage'}")
print("-" * 118)
by = {}
for x in rows:
    by.setdefault(x["group"], []).append(x)
for g in sorted(by):
    xs = by[g]
    n = len(xs)
    o = sum(1 for x in xs if x["opened"])
    wr = [x for x in xs if not x["noref"] and x["ref_pages"] > 0]
    pr = pct(sum(min(x["pages"], x["ref_pages"]) for x in wr), sum(x["ref_pages"] for x in wr))
    po = pct(sum(min(x["pages"], x["orig_pages"]) for x in wr), sum(x["orig_pages"] for x in wr))
    wt = [x for x in xs if not x["noref"] and x["ref_chars"] > 0]
    tr = pct(sum(min(x["chars"], x["ref_chars"]) for x in wt), sum(x["ref_chars"] for x in wt))
    to = pct(sum(min(x["chars"], x["orig_chars"]) for x in wt), sum(x["orig_chars"] for x in wt))
    st = {}
    for x in xs:
        st[x["stage"]] = st.get(x["stage"], 0) + 1
    sts = ",".join(f"{k}:{v}" for k, v in sorted(st.items(), key=lambda t: -t[1])[:3])
    print(f"{g:<5} {xs[0]['group_name'][:34]:<34} {n:>4} {o:>6} "
          f"{(f'{pr}%' if pr is not None else '-'):>7} {(f'{po}%' if po is not None else '-'):>8} "
          f"{(f'{tr}%' if tr is not None else '-'):>7} {(f'{to}%' if to is not None else '-'):>8} {sts}")

# ---------------------------------------------------------------- worst files
print()
print("=== files that did not open (and whether the tool was honest about it) ===")
for x in rows:
    if not x["opened"]:
        tag = "HONEST" if not x["verified"] else "FALSE SUCCESS"
        print(f"  [{tag}] {x['file'][:56]:<56} stage={x['stage']}")
        print(f"            {x['faults'][:78]}")

print()
print("=== biggest page losses against the ceiling ===")
losses = [x for x in with_ref if x["pages"] < x["ref_pages"]]
losses.sort(key=lambda x: x["ref_pages"] - x["pages"], reverse=True)
for x in losses[:12]:
    print(f"  {x['file'][:52]:<52} got {x['pages']:>3} of {x['ref_pages']:>3}  (orig {x['orig_pages']:>3})  {x['stage']}")
if not losses:
    print("  none - every file reached its ceiling")

json.dump({"metrics": {f"{g}|{n}": {"value": v, "unit": u, "verdict": vd}
                       for g, n, v, u, vd in M},
           "rows": rows}, open("/tmp/repair_scores.json", "w"), indent=1)
print()
print("detail written to /tmp/repair_scores.json")
