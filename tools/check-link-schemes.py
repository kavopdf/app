#!/usr/bin/env python3
"""Fails the build if a link taken from a document or a QR code is launched unfiltered.

A PDF is untrusted input. Its /Link annotation can carry any URI - intent://, file://,
content://, javascript: - and if the app hands that straight to startActivity it lets a
document start something on the app's behalf, or hand a private file path to whatever
claims it. The QR scanner has always whitelisted http/https; the PDF link path did not.

This pins both down: the launching function must check the scheme against a small set
before it builds the Intent.
"""
import pathlib
import re
import sys

fails = []
SAFE = {"http", "https", "mailto", "tel"}

# 1) the reader's link launcher
p = pathlib.Path("app/src/main/java/com/kavopdf/app/ViewerActivity.kt")
if not p.exists():
    fails.append("ViewerActivity.kt is missing")
else:
    s = p.read_text(encoding="utf-8")
    m = re.search(r"private fun openUrl\([\s\S]{0,1800}?\n    \}", s)
    if not m:
        fails.append("ViewerActivity.openUrl is gone")
    else:
        body = m.group(0)
        if "LINK_SCHEMES" not in body:
            fails.append("openUrl no longer checks the scheme - a link inside a PDF could "
                         "launch intent://, file:// or content://")
        if not re.search(r"scheme\s*!in\s*LINK_SCHEMES", body):
            fails.append("openUrl does not reject unknown schemes")
    decl = re.search(r"LINK_SCHEMES\s*=\s*setOf\(([^)]*)\)", s)
    if not decl:
        fails.append("LINK_SCHEMES is gone")
    else:
        got = {x.strip().strip('"').lower() for x in decl.group(1).split(",") if x.strip()}
        if got != SAFE:
            fails.append(f"LINK_SCHEMES is {sorted(got)}, expected {sorted(SAFE)}")
    if s.count("companion object") > 1:
        fails.append("ViewerActivity has more than one companion object - Kotlin allows one")

# 2) the QR scanner
q = pathlib.Path("app/src/main/java/com/kavopdf/app/QrScanActivity.kt")
if not q.exists():
    fails.append("QrScanActivity.kt is missing")
else:
    t = q.read_text(encoding="utf-8")
    if not re.search(r'startsWith\("https?://"\)|startsWith\("http://"\)', t):
        fails.append("QrScanActivity no longer whitelists http/https before opening a link")

# 3) nothing else may launch an ACTION_VIEW from a string
for f in pathlib.Path("app/src/main/java").rglob("*.kt"):
    s = f.read_text(encoding="utf-8")
    for m in re.finditer(r"startActivity\([^)]*Intent\([^)]*ACTION_VIEW[^)]*Uri\.parse\(", s):
        if f.name not in ("ViewerActivity.kt", "QrScanActivity.kt"):
            fails.append(f"{f.name} launches an ACTION_VIEW from a parsed string without "
                         "the scheme check")

if fails:
    for x in fails:
        print("FAIL:", x)
    sys.exit(1)
print("PASS: links from a PDF or a QR code are limited to http/https/mailto/tel")
