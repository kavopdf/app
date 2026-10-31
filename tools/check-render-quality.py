#!/usr/bin/env python3
"""Fails the build if page rendering quality is quietly reduced for some devices.

Memory safety for page bitmaps has to come from two places only:
  - render() retrying a single page smaller when the allocator actually refuses a
    size, without writing that smaller size back into the shared budget, and
  - the page cache budget.

It must never come from lowering the page budget up front, because that is exactly how
the app went blurry: 3.30.3 gave low-RAM devices a smaller page, and 3.30.4 halved the
budget on every onTrimMemory callback and never restored it, so after a few trips to the
background a page was drawn at 530 px wide and scaled up.

This guard pins the four things that keep that from happening again.
"""
import pathlib
import re
import sys

SRC = pathlib.Path("app/src/main/java/com/kavopdf/app/ui/PageRenderer.kt")
FULL_PIXELS = "16_000_000L"
MIN_FLOOR = 900_000

if not SRC.exists():
    print("FAIL: PageRenderer.kt is missing")
    sys.exit(1)
src = SRC.read_text(encoding="utf-8")

fails = []

# 1) the page budget must start at the full-quality ceiling
m = re.search(r"private var maxPixels: Long = ([\d_]+L)", src)
if not m:
    fails.append("maxPixels initialiser not found")
elif m.group(1) != FULL_PIXELS:
    fails.append(f"maxPixels starts at {m.group(1)}, expected {FULL_PIXELS} (full quality)")

# 2) reduceBudget must not touch the page budget - only the cache
m = re.search(r"fun reduceBudget\(\)\s*\{(.*?)\n        \}", src, re.S)
if not m:
    fails.append("reduceBudget() not found")
elif re.search(r"\bmaxPixels\s*=", m.group(1)):
    fails.append("reduceBudget() still lowers maxPixels - that is the blurry-page bug")

# 3) no device-dependent shrink of the page budget at configure time
m = re.search(r"fun configure\(context: Context\)\s*\{(.*?)\n        \}", src, re.S)
if not m:
    fails.append("configure() not found")
else:
    body = m.group(1)
    if re.search(r"maxPixels\s*=\s*\(?", body) and "16_000_000L" not in body:
        fails.append("configure() computes maxPixels from the device instead of using the ceiling")
    if "isLowRamDevice" in body and "maxPixels" in body:
        fails.append("configure() still shrinks the page budget on low-RAM devices")

# 4) the last-resort floor must stay legible
m = re.search(r"FLOOR_PIXELS\s*=\s*([\d_]+)L", src)
if not m:
    fails.append("FLOOR_PIXELS not found")
else:
    value = int(m.group(1).replace("_", ""))
    if value < MIN_FLOOR:
        fails.append(f"FLOOR_PIXELS is {value}, below the {MIN_FLOOR} legibility floor")

# 5) the reader must still ask for at least twice the screen width
viewer = pathlib.Path("app/src/main/java/com/kavopdf/app/ViewerActivity.kt")
if viewer.exists():
    v = viewer.read_text(encoding="utf-8")
    f = re.search(r"BASE_FACTOR\s*=\s*([\d.]+)f", v)
    if not f or float(f.group(1)) < 2.0:
        fails.append("ViewerActivity BASE_FACTOR dropped below 2.0 - pages would render at screen size")
    w = re.search(r"MAX_WIDTH\s*=\s*(\d+)", v)
    if not w or int(w.group(1)) < 2800:
        fails.append("ViewerActivity MAX_WIDTH dropped below 2800")

# 6) render() must never write a smaller size back into the page budget
m = re.search(r"fun render\(index: Int[^\n]*\{(.*?)\n    \}", src, re.S)
if not m:
    fails.append("render() not found")
elif re.search(r"\bmaxPixels\s*=", m.group(1)):
    fails.append("render() writes a smaller size back into maxPixels - one hard page then "
                 "shrinks every page after it, so a long document fades towards the end "
                 "while page one stays sharp")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: page quality must not be traded for memory")
    sys.exit(1)

print("PASS: page quality is fixed at full resolution on every device")
