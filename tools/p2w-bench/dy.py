#!/usr/bin/env python3
"""dy.py - per-run vertical displacement in the REAL Google render, for one document pair.

This is the measurement `18_displacement` never prints. The check reports a count of bad
pages; the question "is this a constant offset, an accumulating drift, or a sawtooth" needs
the per-run dy. It reuses verify_google's own matcher by intercepting the call that receives
`pairs`, so it cannot disagree with the instrument it is explaining.

    python3 dy.py <source.pdf> <google-export.pdf> [--docx out.docx]
"""
import importlib.util, os, sys, math, collections, statistics

HERE = "/scratch/work/CS/tools/p2w-bench"
spec = importlib.util.spec_from_file_location("vg", os.path.join(HERE, "verify_google.py"))
vg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vg)

captured = {}
_orig = vg.extra_checks


def _spy(src, gd, s_runs, g_runs, pairs, docx_path=None):
    captured["s_runs"] = s_runs
    captured["g_runs"] = g_runs
    captured["pairs"] = list(pairs)
    return _orig(src, gd, s_runs, g_runs, pairs, docx_path)


vg.extra_checks = _spy


def main(argv):
    src_path, gd_path = argv[1], argv[2]
    docx = None
    if "--docx" in argv:
        docx = argv[argv.index("--docx") + 1]
    src = vg.fitz.open(src_path)
    gd = vg.fitz.open(gd_path)
    vg.compare(src_path, gd_path, docx)

    s_runs = captured["s_runs"]
    pairs = captured["pairs"]

    flat = {(r["page"], r["ry"], r["text"]) for r in s_runs
            if abs(math.sin(math.radians(r["angle"]))) <= 0.02}

    print(f"\n### {os.path.basename(src_path)}  pages src={src.page_count} "
          f"render={gd.page_count}")
    print(f"matched pairs: {len(pairs)}   upright source runs: {len(flat)}")

    rows = []
    for pg in sorted({r["page"] for r in s_runs}):
        ds = [(g["ry"] - r["ry"], r["size"], r["rx"], r["ry"], r["text"]) for r, g in pairs
              if r["page"] == pg and (r["page"], r["ry"], r["text"]) in flat]
        if not ds:
            print(f"  page {pg}: NO MATCHED UPRIGHT RUN (the `if not ds` branch)")
            continue
        v = sorted(d[0] for d in ds)
        n_out = sum(1 for d, sz, *_ in ds if abs(d) > min(max(0.35 * sz, 1.5), 4.5))
        print(f"  page {pg}: n={len(ds)} n_out={n_out} "
              f"min={v[0]:+.2f} p25={v[len(v)//4]:+.2f} med={statistics.median(v):+.2f} "
              f"p75={v[3*len(v)//4]:+.2f} max={v[-1]:+.2f}  "
              f"span={v[-1]-v[0]:.2f}")
        rows.extend((pg, d, sz, rx, ry, t) for d, sz, rx, ry, t in ds)

    # is the displacement a function of HEIGHT on the page (drift) or a constant?
    if rows:
        ys = [r[4] for r in rows]
        ds = [r[1] for r in rows]
        n = len(rows)
        my, md = sum(ys) / n, sum(ds) / n
        cov = sum((y - my) * (d - md) for y, d in zip(ys, ds))
        var = sum((y - my) ** 2 for y in ys)
        slope = cov / var if var else 0.0
        icpt = md - slope * my
        resid = [d - (icpt + slope * y) for y, d in zip(ys, ds)]
        rms = (sum(r * r for r in resid) / n) ** 0.5
        print(f"  FIT dy = {icpt:+.2f} {slope:+.5f}*y   rms_resid={rms:.2f} pt")
        print(f"  top-of-page dy {ds[0]:+.2f}  bottom-of-page dy {ds[-1]:+.2f}"
              f"   (first/last matched run in page order)")

    # the top 12 by |dy|, to name the runs that actually carry the failure
    rows.sort(key=lambda r: -abs(r[1]))
    print("  worst 12 runs:")
    for pg, d, sz, rx, ry, t in rows[:12]:
        tol = min(max(0.35 * sz, 1.5), 4.5)
        print(f"    p{pg} dy={d:+7.2f} tol={tol:.2f} y={ry:7.2f} sz={sz:5.2f} "
              f"{t[:44]!r}")


if __name__ == "__main__":
    main(sys.argv)
