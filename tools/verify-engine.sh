#!/usr/bin/env bash
# Independently verifies the PDF engine against the real Apache PDFBox Android
# library, on a plain JVM, using tiny stubs for the handful of android.* classes
# the engine touches. Runs the same 39 behavioural checks used during development.
set -euo pipefail

# A printed FAIL must fail the gate. Every assertion-bearing test below records its
# verdict here as well as in its own exit code, and the script exits on this at the end
# - so a test that prints FAIL can never leave the suite green.
SUITE_FAIL=0
assertion_test() { # assertion_test <header> <MainClass>
  echo "== $1 =="
  if ! java -cp "$CP" "$2"; then
    echo "  ^ $2 reported failures - see its FAIL lines above"
    SUITE_FAIL=1
  fi
}
cd "$(dirname "$0")/engine-verify"
mkdir -p libs

# A header with no body reads in a log exactly like a section that ran and passed.
# Three of them sat at the end of this script. Check the text before running anything.
if ! python3 ../check-suite-headers.py ../verify-engine.sh; then
  echo "a section header has no body - a header with no body reads as a passing section" >&2
  exit 2
fi

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

printf "%s" "$CP" > /tmp/engine-cp.txt

# ---------------------------------------------------------------------------
# Preflight: the Standard-14 AFM metrics must resolve on THIS classpath.
#
# TestPdfToWord died at Standard14Fonts.getAFM before reaching any engine code, and
# was never run at all, so the suite reported on an engine it had not exercised. The
# AFM files are present in the AAR (assets/com/tom_roush/pdfbox/resources/afm/, 14
# files) and absent from classes.jar by design; the only way they go missing is the
# classpath, and that is silent until a font is constructed. So test it here, by
# asking the JVM itself, and fail with the cause named instead of a stack trace
# fifteen minutes into the suite.
# ---------------------------------------------------------------------------
echo "== preflight: Standard-14 AFM metrics resolve on the classpath =="
AFM_DIR="libs/aar/assets/com/tom_roush/pdfbox/resources/afm"
AFM_MISSING=0
for f in Courier-Bold Courier-BoldOblique Courier-Oblique Courier Helvetica-Bold \
         Helvetica-BoldOblique Helvetica-Oblique Helvetica Symbol Times-Bold \
         Times-BoldItalic Times-Italic Times-Roman ZapfDingbats; do
  [ -f "$AFM_DIR/$f.afm" ] || { echo "  MISSING FILE $AFM_DIR/$f.afm"; AFM_MISSING=1; }
done
if [ "$AFM_MISSING" -ne 0 ]; then
  echo "  the AAR was not unpacked with its assets - re-run after deleting libs/aar" >&2
  exit 2
fi
AFM_PROBE=/tmp/afm-preflight
rm -rf "$AFM_PROBE" && mkdir -p "$AFM_PROBE"
cat > "$AFM_PROBE/AfmPreflight.java" <<'JAVA'
public class AfmPreflight {
    public static void main(String[] a) throws Exception {
        // The same lookup Standard14Fonts.loadMetrics() makes when PDFBoxResourceLoader
        // is not initialised - i.e. on this plain JVM.
        String[] names = {"Courier-Bold","Courier-BoldOblique","Courier-Oblique","Courier",
            "Helvetica-Bold","Helvetica-BoldOblique","Helvetica-Oblique","Helvetica","Symbol",
            "Times-Bold","Times-BoldItalic","Times-Italic","Times-Roman","ZapfDingbats"};
        int bad = 0;
        for (String n : names) {
            String r = "/com/tom_roush/pdfbox/resources/afm/" + n + ".afm";
            if (com.tom_roush.pdfbox.pdmodel.font.PDType1Font.class.getResourceAsStream(r) == null) {
                System.out.println("  UNREACHABLE " + r); bad++;
            }
        }
        if (bad > 0) {
            System.out.println("  " + bad + " AFM resource(s) are not on the classpath.");
            System.out.println("  libs/aar/assets is missing from CP - the Standard-14 fonts cannot load.");
            System.exit(1);
        }
        System.out.println("  all 14 AFM resources resolve on the classpath");
    }
}
JAVA
javac -nowarn -cp "$CP" -d "$AFM_PROBE" "$AFM_PROBE/AfmPreflight.java"
java -cp "$AFM_PROBE:$CP" AfmPreflight || {
  echo "AFM bootstrap is broken - TestPdfToWord cannot start. Fix the classpath, do not skip the test." >&2
  exit 2
}

echo "== compiling the real engine + tests =="
javac -cp "$CP" -d out $(find ../../app/src/main/java -name '*.java') TestEngine.java TestEncrypt.java TestBookmarks.java TestReport.java TestFonts.java TestNorms.java TestFallback.java TestOrder.java TestFlatten.java TestMeta.java TestImagePdf.java TestCachePolicy.java TestStalls.java

echo "== running engine verification =="
java -cp "$CP" TestEngine

echo "== rotation / overlay placement (rendered and pixel-checked) =="
javac -cp "$CP" -d out TestRotate.java TestCrop.java TestEnc.java TestHostile.java TestTextLayer.java TestSearch.java TestLinkIcon.java TestTextLink.java TestOpacity.java TestAllPages.java TestCopy.java TestRedact.java TestRepair.java TestRepairFixtures.java TestPdfToWord.java TestRealDocs.java
java -cp "$CP" TestRotate
java -cp "$CP" TestCrop
java -cp "$CP" TestEnc
java -cp "$CP" TestHostile

# TestPdfToWord was compiled on the line above and then never run - 29 assertions that
# counted for nothing while the suite reported 1,708 PASS lines. It is the only test of
# the PDF-to-Word path in this script, so it runs here and its verdict counts.
assertion_test "PDF to Word: text, headings, tables and a real .docx package" TestPdfToWord

echo "== OCR text layer (rendered and pixel-checked, all 4 rotations) =="
echo "== independent checks for the whole OCR path =="
echo "== the layer must write the characters that were on the page, not substitutes =="
echo "== what a reader copies out of an OCR layer =="
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

echo
echo "== real documents that once converted wrongly while the corpus said they passed =="
echo "   (a prescription that became one 30-column table, a question paper ordered by x,"
echo "    a police form whose label was welded into the text beside it)"
# TestRealDocs prints a TOTAL line and used to return from main() whatever it found,
# so a printed FAIL could not fail this script. Its exit status now carries the verdict.
if ! java -cp "$CP" TestRealDocs; then
  echo "  ^ TestRealDocs reported failures - see its FAIL lines above"
  SUITE_FAIL=1
fi

echo
echo "== fonts really change the output (watermark + custom link text) =="
java -cp "$CP" TestFonts
python3 verify-fonts.py

echo
if [ "$SUITE_FAIL" -ne 0 ]; then
  echo "SUITE FAILED - at least one assertion above printed FAIL."
  echo "  Every test above was still run, so the full picture is in this log."
  exit 1
fi
echo "SUITE PASSED - every assertion-bearing test exited 0."
