#!/usr/bin/env python3
"""Verifies the written outline is a real PDF outline - read back by an
independent library, with the right titles and the right target pages."""
import os, sys
import pymupdf

W = "/tmp/kavopdf-engine-test"
want = [("Introduction", 1), ("Methods", 3), ("Results", 4), ("Appendix", 5)]

d = pymupdf.open(os.path.join(W, "bm_out.pdf"))
toc = d.get_toc()
got = [(t[1], t[2]) for t in toc]

ok = True
print(f"  outline entries           : {len(got)}")
for lvl, title, page in toc:
    print(f"    L{lvl}  p{page}  {title}")
if got != want:
    print(f"    expected {want}")
    ok = False

print(f"  pages still present       : {d.page_count}")
if d.page_count != 5:
    ok = False
print(f"  page text untouched       : {d[2].get_text().strip()!r}")
if "Chapter 3" not in d[2].get_text():
    ok = False

# the exported log report
r = pymupdf.open(os.path.join(W, "log_report.pdf"))
txt = "".join(r[i].get_text() for i in range(r.page_count))
has_title = "KavoPDF activity log" in txt
has_first = "report-1.pdf" in txt
has_last = "report-120.pdf" in txt
print(f"  log report                : {r.page_count} pages, title={has_title}, first={has_first}, last={has_last}")
if not (has_title and has_first and has_last):
    ok = False

print()
print("BOOKMARKS + REPORT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
