#!/usr/bin/env python3
"""Fails the build if the OCR path drifts back to the shapes that caused real bugs.

Three of the fixes in 3.32.0 cannot be exercised on a build machine - EXIF orientation
needs a device camera, the small-print retry needs ML Kit, and the confidence filter needs
real recognition output. What CAN be checked is that the code still has the shape those
fixes depend on. Each rule below names the bug it prevents.
"""
import pathlib
import sys

KT = pathlib.Path("app/src/main/java/com/kavopdf/app")
ENGINE = KT / "engine/PdfEngine.java"
IMAGE_OCR = KT / "ImageOcrActivity.kt"
OCR = KT / "OcrActivity.kt"
APP = KT / "KavoPdfApp.kt"
FONT = pathlib.Path("app/src/main/assets/fonts/NotoSans-Regular.ttf")

fails = []


def read(p):
    if not p.exists():
        fails.append(f"{p} is missing")
        return ""
    return p.read_text(encoding="utf-8")


engine = read(ENGINE)
image_ocr = read(IMAGE_OCR)
ocr = read(OCR)
app = read(APP)

# --- EXIF: there must be exactly ONE image decoder, and it must apply the orientation ---
if "private fun decodeBounded(" in image_ocr or "fun decodeBounded(" in image_ocr:
    fails.append("ImageOcrActivity has its own decoder again - it ignores EXIF and puts "
                 "the text layer 90 degrees off the page")
if "PdfEngine.decodeImage(" not in image_ocr:
    fails.append("ImageOcrActivity does not decode through PdfEngine.decodeImage")
if "public static Bitmap decodeImage(" not in engine:
    fails.append("PdfEngine.decodeImage is gone")
if "applyExifRotation" not in engine:
    fails.append("PdfEngine no longer applies EXIF rotation - the shared decoder is the "
                 "whole point")
if image_ocr.count("copyToCache") < 1:
    fails.append("ImageOcrActivity no longer caches the image before decoding")

# --- the small-print retry must still be there, and must ask for a BIGGER page ---
if "words.size < 6" not in ocr:
    fails.append("the small-print retry is gone from OcrActivity")
if "OCR_WIDTH * 1.6" not in ocr:
    fails.append("the small-print retry no longer asks for a larger render")
if ocr.count("recognise(") < 3:
    fails.append("the retry no longer re-recognises the page")

# --- both screens must apply the same, deliberately narrow junk rule ---
RULE = "t.trim().length <= 1 && conf != null && conf < 0.3f"
for name, src in (("OcrActivity", ocr), ("ImageOcrActivity", image_ocr)):
    if RULE not in src:
        fails.append(f"{name} lost the narrow junk rule ({RULE}) - either nothing is "
                     f"filtered, or real short words are dropped")
if "conf < 0.5f" in ocr or "conf < 0.5f" in image_ocr:
    fails.append("a wider junk threshold came back - it can drop real one- and "
                 "two-character words")

# --- no stacked layers, and the check must cover every content stream ---
if "hasInvisibleLayer(page)" not in engine:
    fails.append("addTextLayer no longer skips a page that already has a layer")
if "getContentStreams()" not in engine:
    fails.append("the layer check only reads one content stream - a page with several "
                 "would get a second layer")
if "alreadySearchable" in engine:
    fails.append("the old visible-text skip is back - it refused to OCR a scanned page "
                 "that had a typed header")

# --- the font: cache must be dropped when the font changes, and the asset must exist ---
if "GLYPH_CACHE.clear()" not in engine:
    fails.append("the glyph cache is not cleared when the font changes - it would answer "
                 "for the previous font")
if "PDType0Font.load" not in engine:
    fails.append("the OCR layer no longer embeds a Unicode font")
if "setOcrFont" not in app:
    fails.append("KavoPdfApp no longer hands the font to the engine")
if not FONT.exists():
    fails.append("assets/fonts/NotoSans-Regular.ttf is missing")
else:
    head = FONT.read_bytes()[:4]
    if head != b"\x00\x01\x00\x00":
        fails.append("the font asset is not a TrueType file")
    if FONT.stat().st_size < 100_000:
        fails.append("the font asset looks truncated")

if fails:
    for f in fails:
        print("FAIL:", f)
    print("FAIL: the OCR path has drifted")
    sys.exit(1)

print("PASS: the OCR path keeps its shape - one EXIF-aware decoder, the small-print "
      "retry, the narrow junk rule, one layer per page, and a subset Unicode font")
