#!/usr/bin/env python3
"""Guards the PDF to Word tool: engine stages present, wired into the app, tested."""
import pathlib, re, sys

fails = []
engine = pathlib.Path("app/src/main/java/com/kavopdf/app/engine/PdfToWord.java")
writer = pathlib.Path("app/src/main/java/com/kavopdf/app/engine/DocxWriter.java")
for f in (engine, writer):
    if not f.is_file():
        fails.append(f"{f} is missing")
        print("FAIL: " + "; ".join(fails)); sys.exit(1)

src = engine.read_text(encoding="utf-8")
docx = writer.read_text(encoding="utf-8")
tools = pathlib.Path("app/src/main/java/com/kavopdf/app/ToolsActivity.kt").read_text(encoding="utf-8")
enum = pathlib.Path("app/src/main/java/com/kavopdf/app/model/ToolItem.kt").read_text(encoding="utf-8")
home = pathlib.Path("app/src/main/java/com/kavopdf/app/MainActivity.kt").read_text(encoding="utf-8")
strings = pathlib.Path("app/src/main/res/values/strings.xml").read_text(encoding="utf-8")

# The pipeline stages each exist for a reason; losing one silently degrades every conversion.
for needle, why in [
    ("processTextPosition", "glyph extraction"),
    ("class RuleCollector extends PDFGraphicsStreamEngine", "drawn-rule table detection"),
    ("private static List<Line> toLines", "line clustering"),
    ("columnStarts(", "column detection"),
    ("classifyHeadings", "heading levels"),
    ("dedupe(", "duplicate text layer removal"),
    ("OcrHook", "scanned-page fallback"),
]:
    if needle not in src:
        fails.append(f"engine lost {why} ({needle})")

# A docx must be a real OOXML package, not text renamed.
for part in ("[Content_Types].xml", "word/document.xml", "word/styles.xml"):
    if part not in docx:
        fails.append(f"docx writer does not emit {part}")
if "w:tbl" not in docx:
    fails.append("docx writer cannot emit tables")
if "w:br w:type=\\\"page\\\"" not in docx and 'w:br w:type="page"' not in docx:
    fails.append("docx writer does not emit page breaks")

# Wired into the app: enum, home card, screen, strings, run branch.
if "PDF_TO_WORD" not in enum:
    fails.append("Action.PDF_TO_WORD missing")
if "Action.PDF_TO_WORD" not in home:
    fails.append("no home card for PDF to Word")
for needle in ("Action.PDF_TO_WORD", "PdfToWord.convert", "DocxWriter.write", "PdfToWord.writeTxt"):
    if needle not in tools:
        fails.append(f"ToolsActivity does not handle {needle}")
for s in ("tool_word", "tool_word_desc", "word_format_docx", "word_format_txt"):
    if f'name="{s}"' not in strings:
        fails.append(f"missing string {s}")
if "ic_word" not in pathlib.Path("app/src/main/res/drawable/ic_word.xml").read_text(encoding="utf-8") \
        if pathlib.Path("app/src/main/res/drawable/ic_word.xml").is_file() else True:
    if not pathlib.Path("app/src/main/res/drawable/ic_word.xml").is_file():
        fails.append("missing drawable ic_word.xml")

suite = pathlib.Path("tools/verify-engine.sh").read_text(encoding="utf-8")
if "TestPdfToWord" not in suite:
    fails.append("TestPdfToWord is not run by verify-engine.sh")

if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: PDF to Word keeps its extraction stages, writes a real OOXML package with "
      "tables and page breaks, is wired into the enum, home screen, screen, strings and icon, "
      "and its test runs in the suite")
