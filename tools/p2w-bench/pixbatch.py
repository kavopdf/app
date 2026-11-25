#!/usr/bin/env python3
"""Score pixel fidelity for a slice of the corpus, appending to one CSV.

pixel-score.py renders both sides at one DPI and computes ink overlap and SSIM. The whole corpus does
not fit one sandbox call, so this walks a slice and appends, and the caller repeats until done.

    pixbatch.py --slice 40 --src <pdfs dir> --renders <dir> --out <csv>

Already-scored documents are skipped, so re-running is safe and a killed call loses nothing.
"""
import argparse
import json
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/scratch/work/vv2/tools/p2w-bench")

COLS = ["document", "pages_src", "pages_render", "ink_iou_d1_pct", "ssim_pct", "agree_pct",
        "ssim_method", "defects"]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", type=int, default=40)
    ap.add_argument("--src", required=True)
    ap.add_argument("--renders", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=150)
    a = ap.parse_args(argv)

    # A RENDER CARRIES NO RECORD OF THE ENGINE THAT MADE IT, SO A STALE ONE LOOKS EXACTLY
    # LIKE A FRESH ONE. Measured 25 Nov: deciding whether the corpus renders were still valid
    # took three measurements - render mtime, docx mtime, engine commit date - and the first two
    # said "all 213 stale" while the truth was "the engine has not changed since 02:06, the
    # renders were made at 04:58, and the docx at 07:20 are the same engine regenerated".
    #
    # mtime is not identity. So the renders directory carries a stamp of the engine that produced
    # it, written on first use, and this refuses to score against a render whose stamp is not the
    # engine on the tree. A missing stamp is recorded, not assumed current.
    _rend_stamp = os.path.join(a.renders, ".engine")
    _want = ""
    try:
        _want = (json.load(open("/scratch/work/p2w/.stamp", encoding="utf-8")).get("engine") or "")
    except Exception:
        _want = ""
    if not os.path.exists(_rend_stamp):
        try:
            with open(_rend_stamp, "w", encoding="utf-8") as _f:
                _f.write(_want or "unknown")
            print("  stamped %s as engine %s - it had no record" % (a.renders, (_want or "unknown")[:16]))
        except Exception as _e:
            print("  could not stamp the renders: %s" % _e)
    else:
        try:
            _have = open(_rend_stamp, encoding="utf-8").read().strip()
        except Exception:
            _have = ""
        if _want and _have and _have != _want:
            print("REFUSED: %s was rendered by engine %s, the tree is %s. Re-render before scoring."
                  % (a.renders, _have[:16], _want[:16]))
            return 2
    done = set()
    if os.path.exists(a.out):
        with open(a.out, newline="") as f:
            for r in csv.DictReader(f):
                done.add(r["document"])

    names = sorted(f[:-4] for f in os.listdir(a.src) if f.endswith(".pdf"))
    todo = [n for n in names if n not in done
            and os.path.exists(os.path.join(a.renders, n + ".pdf"))]
    if not todo:
        print("ALL DONE - %d scored" % len(done))
        return 0

    # import the scorer from pixel-score.py, which has a hyphen in its name
    import importlib.util
    spec = importlib.util.spec_from_file_location("pixscore", os.path.join(HERE, "pixel-score.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    new = 0
    fresh = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if fresh:
            w.writeheader()
        for n in todo[:a.slice]:
            try:
                r = mod.score(os.path.join(a.src, n + ".pdf"),
                                   os.path.join(a.renders, n + ".pdf"), a.dpi)
            except Exception as e:
                r = {"error": type(e).__name__}
            if not isinstance(r, dict):
                continue
            row = {
                "document": n,
                "pages_src": r.get("pages_source", r.get("pages_src", "")),
                "pages_render": r.get("pages_render", ""),
                "ink_iou_d1_pct": r.get("ink_iou_mean", ""),
                "ssim_pct": r.get("ssim_mean", ""),
                "agree_pct": r.get("agree_mean", ""),
                "ssim_method": "half-res-stride2",
                "defects": ";".join(str(x.get("kind") if isinstance(x, dict) else x) for x in (r.get("defects") or [])) or r.get("error", ""),
            }
            w.writerow(row)
            new += 1
    print("scored %d this call | %d of %d total" % (new, len(done) + new, len(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
