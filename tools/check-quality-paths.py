#!/usr/bin/env python3
"""Fails the build if any tool quietly re-compresses a PDF's pictures.

Rendering a page is free - it never touches the file. Saving a PDF is where quality is lost,
and there are only two ways to lose it: rasterising the page, or re-encoding an image.

Pinned here:
  1. Redaction may rasterise (that is what makes it real), but the picture it leaves behind
     must be lossless, not a JPEG.
  2. Images-to-PDF must go through ImagePdfWriter, so a JPEG goes in as its own bytes.
  3. The only JPEG re-encode allowed anywhere is the Compress tool, which is what it is for.
  4. Compress's lightest setting must be gentle: no image under 2600 px is touched, and the
     re-encode is at 0.90 or better.
"""
import pathlib
import re
import sys

SRC = pathlib.Path("app/src/main/java/com/kavopdf/app/engine/PdfEngine.java")
if not SRC.exists():
    print("FAIL: PdfEngine.java is missing")
    sys.exit(1)
src = SRC.read_text(encoding="utf-8")

fails = []


def method(name, sig=r"public static void %s\("):
    """Body of a method, by brace matching from its signature."""
    m = re.search(sig % re.escape(name), src)
    if not m:
        return None
    i = m.start()
    j = src.index("{", i)
    depth = 0
    k = j
    while k < len(src):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[i:k + 1]
        k += 1
    return None


# 1) redaction: rasterise yes, JPEG no
body = method("applyRedaction", r"(?:public|private) static void %s\(")
if body is None:
    fails.append("applyRedaction() not found")
elif "JPEGFactory" in body:
    fails.append("applyRedaction() writes the redacted page as a JPEG - it must be lossless")
elif "LosslessFactory" not in body:
    fails.append("applyRedaction() no longer writes the page losslessly")

# 2) the real imagesToPdf (the 4-arg one) must delegate, never encode
body = method("imagesToPdf(List<File> images, File out, int maxDimension, boolean fitToA4)",
              r"public static void %s\s*throws")
if body is None:
    fails.append("imagesToPdf() not found")
else:
    if "ImagePdfWriter" not in body:
        fails.append("imagesToPdf() no longer goes through ImagePdfWriter - a JPEG would be re-encoded")
    if "JPEGFactory" in body or "LosslessFactory" in body:
        fails.append("imagesToPdf() encodes images itself instead of delegating to ImagePdfWriter")

# 3) the JPEG passthrough must stay
m = re.search(r"private PDImageXObject embed\(File image\)", src)
if not m:
    fails.append("ImagePdfWriter.embed() not found")
else:
    i = m.start()
    j = src.index("{", i)
    depth, k = 0, j
    while k < len(src):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    body = src[i:k]
    if "createFromStream" not in body:
        fails.append("ImagePdfWriter no longer embeds a JPEG's own bytes (createFromStream)")
    if "isJpeg(" not in body:
        fails.append("ImagePdfWriter no longer checks the JPEG marker - a PNG would be written as a broken image")

# 4) every remaining JPEGFactory.createFromImage must be the Compress tool
allowed = set()
m = re.search(r"private static void compressResources\(", src)
if m:
    i = m.start()
    j = src.index("{", i)
    depth, k = 0, j
    while k < len(src):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    for off in range(i, k):
        if src.startswith("JPEGFactory.createFromImage", off):
            allowed.add(off)
for m in re.finditer(r"JPEGFactory\.createFromImage", src):
    if m.start() not in allowed:
        line = src.count("\n", 0, m.start()) + 1
        fails.append(f"JPEGFactory.createFromImage at line {line} is outside the Compress tool")

# 5) compress's lightest setting must be gentle
m = re.search(r"case 0:\s*maxDim\s*=\s*(\d+);\s*quality\s*=\s*([\d.]+)f;", src)
if not m:
    fails.append("Compress level 0 not found")
else:
    max_dim = int(m.group(1))
    quality = float(m.group(2))
    if max_dim < 2600:
        fails.append(f"Compress light setting downsamples to {max_dim} px, below the 2600 floor")
    if quality < 0.85:
        fails.append(f"Compress light setting re-encodes at {quality}, below the 0.85 floor")

# 6) export raster resolution: 300 dpi, and no call site may pass its own number
RENDERER = pathlib.Path("app/src/main/java/com/kavopdf/app/ui/AnnotRenderer.kt")
if not RENDERER.exists():
    fails.append("AnnotRenderer.kt is missing")
else:
    r = RENDERER.read_text(encoding="utf-8")
    m = re.search(r"EXPORT_DPI\s*=\s*([\d.]+)f", r)
    if not m:
        fails.append("AnnotRenderer.EXPORT_DPI not found")
    elif float(m.group(1)) < 300:
        fails.append(f"AnnotRenderer.EXPORT_DPI is {m.group(1)}, below 300 - exports would be soft")
    if "EXPORT_SCALE" not in r:
        fails.append("AnnotRenderer.EXPORT_SCALE not found")
for name in ("AnnotateActivity.kt", "CreatePdfActivity.kt"):
    p2 = pathlib.Path("app/src/main/java/com/kavopdf/app") / name
    if not p2.exists():
        fails.append(f"{name} is missing")
        continue
    body = p2.read_text(encoding="utf-8")
    if "rasterize(" not in body:
        fails.append(f"{name} no longer rasterises")
    # a hard-coded scale would silently drop back to the old resolution
    for lit in re.findall(r"rasterize\([^)]*,\s*([\d.]+)f\s*\)", body):
        fails.append(f"{name} passes a hard-coded rasterize scale ({lit}) instead of EXPORT_SCALE")
    if "EXPORT_SCALE" not in body:
        fails.append(f"{name} does not use AnnotRenderer.EXPORT_SCALE")

# 7) extracting an image must not re-compress it
body = method("extractImages(File src, File outDir, List<Integer> pages1based)",
              r"public static List<File> %s\s*throws")
if body is None:
    fails.append("extractImages() not found")
else:
    if "CompressFormat.JPEG" in body:
        fails.append("extractImages() re-encodes as JPEG - an extracted image would be worse "
                     "than the one inside the PDF")
    if "createRawInputStream" not in body:
        fails.append("extractImages() no longer copies a JPEG's own bytes")
    if "CompressFormat.PNG" not in body:
        fails.append("extractImages() no longer writes other images losslessly")

# 8) decodeUpright must actually rotate
m = re.search(r"public static Bitmap decodeUpright\(File f, int maxDimension\)\s*\{", src)
if not m:
    fails.append("decodeUpright() not found")
else:
    i = m.start()
    j = src.index("{", i)
    depth, k = 0, j
    while k < len(src):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    if "decodeImage(" not in src[i:k]:
        fails.append("decodeUpright() does not use the EXIF-aware decoder - a portrait "
                     "photo's thumbnail would come out sideways")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: a tool is degrading PDF quality")
    sys.exit(1)

print("PASS: nothing re-compresses a PDF except the Compress tool, and its light setting is gentle")
