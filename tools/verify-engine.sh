#!/usr/bin/env bash
# Independently verifies the PDF engine against the real Apache PDFBox Android
# library, on a plain JVM, using tiny stubs for the handful of android.* classes
# the engine touches. Runs the same 39 behavioural checks used during development.
set -euo pipefail
cd "$(dirname "$0")/engine-verify"
mkdir -p libs

echo "== downloading PDFBox-Android and its dependencies =="
curl -sSL -o libs/pdfbox.aar https://repo1.maven.org/maven2/com/tom-roush/pdfbox-android/2.0.27.0/pdfbox-android-2.0.27.0.aar
curl -sSL -o libs/bcprov.jar https://repo1.maven.org/maven2/org/bouncycastle/bcprov-jdk15to18/1.72/bcprov-jdk15to18-1.72.jar
curl -sSL -o libs/bcpkix.jar https://repo1.maven.org/maven2/org/bouncycastle/bcpkix-jdk15to18/1.72/bcpkix-jdk15to18-1.72.jar
curl -sSL -o libs/bcutil.jar https://repo1.maven.org/maven2/org/bouncycastle/bcutil-jdk15to18/1.72/bcutil-jdk15to18-1.72.jar

rm -rf libs/aar && mkdir -p libs/aar
( cd libs/aar && unzip -oq ../pdfbox.aar )

echo "== compiling Android stubs =="
rm -rf out && mkdir -p out
javac -d out $(find stubs -name '*.java')

CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"

echo "== compiling the real engine + tests =="
javac -cp "$CP" -d out $(find ../../app/src/main/java -name '*.java') TestEngine.java TestEncrypt.java TestBookmarks.java TestReport.java TestFonts.java TestNorms.java TestFallback.java TestOrder.java TestFlatten.java TestMeta.java TestImagePdf.java TestCachePolicy.java TestStalls.java

echo "== running engine verification =="
java -cp "$CP" TestEngine

echo "== rotation / overlay placement (rendered and pixel-checked) =="
javac -cp "$CP" -d out TestRotate.java TestCrop.java TestEnc.java TestHostile.java TestTextLayer.java TestSearch.java TestLinkIcon.java TestTextLink.java TestOpacity.java TestAllPages.java TestCopy.java TestRedact.java TestRepair.java TestRepairFixtures.java TestPdfToWord.java
java -cp "$CP" TestRotate
java -cp "$CP" TestCrop
java -cp "$CP" TestEnc
java -cp "$CP" TestHostile

echo "== OCR text layer (rendered and pixel-checked, all 4 rotations) =="
python3 -m pip install --quiet pymupdf >/dev/null 2>&1 || true
java -cp "$CP" TestTextLayer make
# the text layer must be correct whatever resolution the recogniser ran at
for dpi in 100 200; do
  echo "  -- raster at ${dpi} dpi --"
  TL_DPI=$dpi python3 verify-textlayer.py measure
  java -cp "$CP" TestTextLayer apply
  TL_DPI=$dpi python3 verify-textlayer.py check || exit 1
done

echo "== text search + hyperlinks (rendered and pixel-checked) =="
java -cp "$CP" TestSearch
python3 verify-search.py

echo "== visible link icon + search speed =="
java -cp "$CP" TestLinkIcon
python3 verify-linkicon.py

echo "== custom link text (rendered: visible, right colour, on the text) =="
java -cp "$CP" TestTextLink
python3 verify-textlink.py

echo "== link opacity (rendered: 40% must be lighter than 100%) =="
java -cp "$CP" TestOpacity
python3 verify-opacity.py

echo "== same link on every page =="
java -cp "$CP" TestAllPages
python3 verify-allpages.py

echo "== text lookup for tap-to-copy =="
java -cp "$CP" TestCopy
python3 verify-copy.py

echo "== redaction: is the content really gone? =="
python3 verify-redact-setup.py
java -cp "$CP" TestRedact
python3 verify-redact.py
python3 -m pip install --quiet pymupdf >/dev/null 2>&1 || true
python3 verify-render.py

echo
echo "== PDF protection: real AES-256, and it actually enforces =="
java -cp "$CP" TestEncrypt
python3 verify-encrypt.py

echo
echo "== bookmarks: a real PDF outline, read back independently =="
java -cp "$CP" TestBookmarks
python3 verify-bookmarks.py
echo
echo "== designed activity-log report (header, facts, table, colour) =="
java -cp "$CP" TestReport
python3 verify-report.py

echo
echo "== fonts really change the output (watermark + custom link text) =="
echo
echo "== filled values must be visible even when pdfbox cannot build the appearance =="
java -cp "$CP" TestFallback

echo
echo "== every field knows its page (from its widget, not from its name) =="
java -cp "$CP" TestOrder

echo
echo "== a filled value must be in the PAGE CONTENT, because Android's PdfRenderer =="
echo "== ignores annotations - that is why the app's own reader showed an empty form =="
java -cp "$CP" TestFlatten

echo
echo "== document properties must be read from XMP when the Info dictionary is empty, =="
echo "== and links must be found in .in / .co.in addresses, not split into words =="
java -cp "$CP" TestMeta
java -cp "$CP" TestImagePdf
java -cp "$CP" TestCachePolicy
java -cp "$CP" TestStalls

echo
echo "== repair: deliberately broken files must come back readable =="
echo "   (xref, startxref, trailer, header, junk prefix and suffix, truncation,"
echo "    a broken page tree, dangling and corrupt page content, encryption)"
java -cp "$CP" TestRepair

echo
# The 51-fixture sweep is the slowest thing in this script, and it only says anything about
# the repair engine. It runs when the engine, its tests or its fixtures change - and is
# skipped otherwise, so a change to any other tool does not pay for it.
REPAIR_STAMP="repair-suite.stamp"
REPAIR_HASH=$(
  {
    cat ../../app/src/main/java/com/kavopdf/app/engine/PdfRepair.java
    cat TestRepair.java TestRepairFixtures.java
    ls -l fixtures/repair fixtures/torture fixtures/gaps | awk '{print $5, $9}'
  } | sha256sum | cut -d' ' -f1
)
if [ "${REPAIR_FULL:-0}" != "1" ] && [ -f "$REPAIR_STAMP" ] \
   && [ "$(tr -d '\n' < "$REPAIR_STAMP")" = "$REPAIR_HASH" ]; then
  echo "== repair fixtures: unchanged since the last full run - skipped =="
  echo "   (REPAIR_FULL=1 bash tools/verify-engine.sh forces it)"
else
  echo "== repair against the 51 real damaged fixtures (the stress set) =="
  java -cp "$CP" TestRepairFixtures
  echo "$REPAIR_HASH" > "$REPAIR_STAMP"
fi

echo
echo "== the detector's own rules (no false positives, no missed regressions) =="
java -cp "$CP" TestNorms

java -cp "$CP" TestFonts
python3 verify-fonts.py

echo "== independent checks for the whole OCR path =="

echo
echo "== the layer must write the characters that were on the page, not substitutes =="

echo
echo "== what a reader copies out of an OCR layer =="
