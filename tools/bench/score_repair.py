#!/usr/bin/env python3
"""
Score PdfRepair's output against what the engine claimed.

The engine writes a report for every file. This opens the output with PyMuPDF - a library
that knows nothing about our code - and checks the claims:

    did it really open?
    are the pages there that the report says are there?
    is the text still readable?
    is the report honest about what it lost?

A repair tool that says "fixed" on a file that does not open is worse than one that says
"could not fix this", because the user walks away believing their data was saved.

    python3 score_repair.py <inDir> <outDir> <report.jsonl> [--json out.json]
"""
import os, sys, json, warnings
warnings.filterwarnings("ignore")
import pymupdf

IN = sys.argv[1]
OUT = sys.argv[2]
REPORT = sys.argv[3]
JSON_OUT = None
if "--json" in sys.argv:
    JSON_OUT = sys.argv[sys.argv.index("--json") + 1]

rows = []
with open(REPORT, encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass

def norm(s):
    return " ".join((s or "").split())

def text_of(path):
    """Page texts, or None when the file cannot be opened at all.

    A damaged file can open and still throw on an individual page ("cannot find page 2 in
    page tree"). That is a page-level failure, not a file-level one, so each page is read
    inside its own try - otherwise one bad page would abort the whole measurement.
    """
    try:
        d = pymupdf.open(path)
    except Exception:
        return None
    if d.needs_pass:
        d.close()
        return None
    t = []
    try:
        n = len(d)
    except Exception:
        n = 0
    for i in range(n):
        try:
            t.append(norm(d.load_page(i).get_text()))
        except Exception:
            t.append("")
    d.close()
    return t, n

M = []   # (metric, value, unit, verdict)
def add(*a):
    M.append(a)

stats = {
    "files": 0,
    "threw": 0,
    "opened": 0,
    "report_claims_readable": 0,
    "report_claims_verified": 0,
    "claimed_but_broken": 0,
    "broken_but_honest": 0,
    "pages_claimed": 0,
    "pages_real": 0,
    "text_recovered": 0,
    "text_reference": 0,
    "blank_outputs": 0,
    "slow": 0,
}

SLOW_MS = 8000

for r in rows:
    stats["files"] += 1
    rel = r.get("file", "")
    if r.get("threw"):
        stats["threw"] += 1
        continue

    out_path = os.path.join(OUT, rel)
    res = text_of(out_path)
    opened = res is not None
    if opened:
        pages, npages = res
        stats["opened"] += 1
    else:
        pages, npages = [], 0

    # `readable` only means the INPUT could be parsed. `verified` is the engine's claim that
    # the OUTPUT is good. The honesty check is on `verified`, not on `readable` - checking
    # the wrong one reported three false successes that were in fact correct refusals.
    claims_readable = bool(r.get("readable"))
    claims_verified = bool(r.get("verified"))
    if claims_readable:
        stats["report_claims_readable"] += 1
    if claims_verified:
        stats["report_claims_verified"] += 1
    # a claim of success on a file that does not open is the worst failure this tool has
    if claims_verified and not opened:
        stats["claimed_but_broken"] += 1
    if not claims_verified and not opened:
        stats["broken_but_honest"] += 1

    # pages
    claimed = int(r.get("pagesAfter") or 0)
    stats["pages_claimed"] += claimed
    stats["pages_real"] += npages
    if npages == 0 and claimed > 0:
        stats["blank_outputs"] += 1

    # text recovery, only where the original could be read at all
    src_res = text_of(os.path.join(IN, rel))
    if src_res is not None:
        src_pages, _ = src_res
        ref = "".join(src_pages)
        if ref:
            got = "".join(pages)
            stats["text_reference"] += len(ref)
            stats["text_recovered"] += min(len(got), len(ref))
            # "blank" only counts when the original had text to lose. A scanned PDF has no
            # text layer at all, and calling that a blank output is a false alarm.
            if not got.strip() and claims_verified:
                stats["blank_outputs"] += 1

    if int(r.get("ms") or 0) > SLOW_MS:
        stats["slow"] += 1

n = max(1, stats["files"])

add("Repair PDF", "files processed", stats["files"], "files", "pass")
add("Repair PDF", "crashes", stats["threw"], "exceptions",
    "pass" if stats["threw"] == 0 else "FAIL")
add("Repair PDF", "output opens", round(stats["opened"] * 100 / n, 1), "%",
    "pass" if stats["opened"] == stats["files"] else "WARN")

honest = stats["files"] - stats["threw"]
add("Repair PDF", "report honest (no false success)", stats["claimed_but_broken"],
    "files it verified that do not open",
    "pass" if stats["claimed_but_broken"] == 0 else "FAIL")

add("Repair PDF", "honest refusals", stats["broken_but_honest"], "files it admitted it could not fix",
    "pass")

if stats["pages_claimed"]:
    ratio = stats["pages_real"] * 100 / stats["pages_claimed"]
    add("Repair PDF", "pages the report claims are really there", round(min(ratio, 100), 1), "%",
        "pass" if ratio >= 99 else "FAIL")

if stats["text_reference"]:
    tr = stats["text_recovered"] * 100 / stats["text_reference"]
    add("Repair PDF", "text recovered vs readable original", round(tr, 1), "%",
        "pass" if tr >= 95 else "WARN")

add("Repair PDF", "blank output where the original had text", stats["blank_outputs"], "files",
    "pass" if stats["blank_outputs"] == 0 else "FAIL")
add("Repair PDF", "slow runs (>8 s)", stats["slow"], "files",
    "pass" if stats["slow"] == 0 else "WARN")

print(f"{'ASPECT':<48} {'VALUE':>12}  {'UNIT':<44} VERDICT")
print("=" * 124)
for tool, name, v, unit, verdict in M:
    vs = f"{v:.2f}" if isinstance(v, float) else f"{v}"
    print(f"{tool + ' | ' + name:<48}"[:48] + f" {vs:>12}  {unit:<44} {verdict or ''}")
print("=" * 124)
np_ = sum(1 for t in M if t[4] == "pass")
nf = sum(1 for t in M if t[4] == "FAIL")
nw = sum(1 for t in M if t[4] == "WARN")
print(f"metrics {len(M)}   pass {np_}   warn {nw}   FAIL {nf}")
print()
print("counts:", json.dumps(stats, indent=1))

if JSON_OUT:
    json.dump({f"{tool}|{name}": {"value": v, "unit": unit, "verdict": verdict}
               for tool, name, v, unit, verdict in M},
              open(JSON_OUT, "w"), indent=1)
    print("wrote", JSON_OUT)
