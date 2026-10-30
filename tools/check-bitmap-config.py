#!/usr/bin/env python3
"""Fails the build if a page bitmap is created in a format PdfRenderer cannot draw to.

android.graphics.pdf.PdfRenderer.Page.render() refuses anything but ARGB_8888:

    if (destination.getConfig() != Config.ARGB_8888) {
        throw new IllegalArgumentException("Unsupported pixel format");
    }

That exception is not an OutOfMemoryError, so a retry loop that only catches OOM lets it
through, every caller wraps render() in runCatching and gets null, and the page never
appears. In 3.30.3 a low-RAM device - and in 3.30.4 every device, because reduceBudget()
set it too - was switched to RGB_565 to save memory, and the whole app showed a black
screen with the PDF open.

Memory has to be saved by drawing fewer pixels, never by changing the format. This guard
keeps it that way.
"""
import pathlib
import re
import sys

KT = pathlib.Path("app/src/main/java")

# formats PdfRenderer will not accept, and a couple that are never worth using here
BAD = {
    "Bitmap.Config.RGB_565": "PdfRenderer rejects it (ARGB_8888 only)",
    "Bitmap.Config.ARGB_4444": "deprecated and rejected by PdfRenderer",
    "Bitmap.Config.ALPHA_8": "no colour, useless for a page",
}

offenders = []
for f in KT.rglob("*.kt"):
    text = f.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("//", "*", "/*")):
            continue
        for bad, why in BAD.items():
            if bad in line:
                offenders.append((str(f), line_no, bad, why))

print(f"scanned {len(list(KT.rglob('*.kt')))} Kotlin files")
if offenders:
    for path, line_no, bad, why in offenders:
        print(f"FAIL {path}:{line_no}  {bad} - {why}")
    print("FAIL: a page bitmap must be ARGB_8888")
    sys.exit(1)

# and the renderer itself must still be reachable, so this guard cannot pass on a
# codebase where the render call was quietly deleted
renderer = KT / "com/kavopdf/app/ui/PageRenderer.kt"
if not renderer.exists():
    print("FAIL: PageRenderer.kt is missing")
    sys.exit(1)
src = renderer.read_text(encoding="utf-8")
if "page.render(" not in src:
    print("FAIL: PageRenderer no longer calls page.render()")
    sys.exit(1)
if not re.search(r"createBitmap\([^)]*Bitmap\.Config\.ARGB_8888", src):
    print("FAIL: the page bitmap is not created as ARGB_8888")
    sys.exit(1)

print("PASS: every page bitmap is ARGB_8888, the only format PdfRenderer draws to")
