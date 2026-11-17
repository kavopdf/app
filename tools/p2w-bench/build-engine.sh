#!/usr/bin/env bash
# Build the PDF engine for a measurement run - and nothing else.
#
# Two things were wrong with how a run built this.
#
# 1. It called tools/verify-engine.sh, which downloads the libraries and then runs the
#    whole 39-check behavioural suite. That suite measures the engine; a measurement run
#    measures the corpus. It is minutes of the run's budget spent on a question that is
#    not being asked.
#
# 2. verify-engine.sh puts the libraries in tools/engine-verify/libs/, but the brief then
#    pointed javac at /scratch/work/libs/ - an absolute path outside the clone that only
#    exists if someone built them by hand in that sandbox. /scratch/work does not survive
#    a sandbox being recycled, so on a fresh pod the compile failed, there was nothing to
#    convert, and the run ended without committing anything.
#
# Everything here is inside the clone, so a fresh clone is a working build. javac is
# fetched from Adoptium if the image does not have one - the same download the JDK came
# from when this was worked out by hand.
set -euo pipefail
HERE_SELF="$(cd "$(dirname "$0")" && pwd)"
tr() { python3 "$HERE_SELF/trace.py" >/dev/null 2>&1; python3 -c "
import sys; sys.path.insert(0,'$HERE_SELF')
try:
    from trace import note
    note('build-engine', '''$1''')
except Exception:
    pass
" 2>/dev/null || true; }
tr "started"
cd "$(dirname "$0")/../engine-verify"

# /tmp on this image is 64 MB and already full - a JDK is 180 MB, so it goes on /scratch.
JDK_DIR=/scratch/work/.p2w-jdk
if ! command -v javac >/dev/null 2>&1; then
  echo "== no javac on this image, fetching a JDK ==" >&2
  mkdir -p "$JDK_DIR"
  if [ ! -x "$JDK_DIR/jdk/bin/javac" ]; then
    curl -sSL --max-time 240 -o "$JDK_DIR/jdk.tar.gz" \
      "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"
    tar xzf "$JDK_DIR/jdk.tar.gz" -C "$JDK_DIR"
    rm -f "$JDK_DIR/jdk.tar.gz"
    rm -rf "$JDK_DIR/jdk"
    mv "$JDK_DIR"/jdk-* "$JDK_DIR/jdk"
  fi
  export JAVA_HOME="$JDK_DIR/jdk"
  export PATH="$JAVA_HOME/bin:$PATH"
fi
command -v javac >/dev/null 2>&1 || { echo "still no javac - cannot build" >&2; exit 1; }

if [ ! -f libs/aar/classes.jar ]; then
  echo "== fetching PDFBox-Android and its dependencies ==" >&2
  mkdir -p libs
  curl -sSL -o libs/pdfbox.aar https://repo1.maven.org/maven2/com/tom-roush/pdfbox-android/2.0.27.0/pdfbox-android-2.0.27.0.aar
  curl -sSL -o libs/bcprov.jar https://repo1.maven.org/maven2/org/bouncycastle/bcprov-jdk15to18/1.72/bcprov-jdk15to18-1.72.jar
  curl -sSL -o libs/bcpkix.jar https://repo1.maven.org/maven2/org/bouncycastle/bcpkix-jdk15to18/1.72/bcpkix-jdk15to18-1.72.jar
  curl -sSL -o libs/bcutil.jar https://repo1.maven.org/maven2/org/bouncycastle/bcutil-jdk15to18/1.72/bcutil-jdk15to18-1.72.jar
  rm -rf libs/aar && mkdir -p libs/aar
  ( cd libs/aar && unzip -oq ../pdfbox.aar )
fi

echo "== compiling stubs, engine and ConvertAll ==" >&2
mkdir -p out
# MEASURED, 16 Nov: a full compile of this engine is 42-46 s. It is NOT the reason an
# attempt costs seventeen minutes - the 09:12 fixer report put that on the scipy ladder
# (soffice on a 4088-run form exceeded the 290 s call limit twice) and that is fixed in
# p2w.py. javac recompiles every file it is handed regardless of -d, so removing the
# `rm -rf out` below bought nothing measurable; what it does buy is not deleting a
# directory we are about to rewrite. Keep the wipe out, but do not pretend it is the win.
#
# The real saving available here is skipping the compile when no source is newer than the
# newest class file - a run that rebuilds to prove the tree is unchanged should not spend
# 45 s doing it.
# `find -newer` on a file that does not exist exits 1, and under `set -e` that killed the
# whole build on a fresh clone - the 16 Nov 11:53 run lost five minutes to "compiling stubs"
# printing nothing and exiting 1. The guard must answer "nothing is newer", not "cannot tell".
_newest_src=$(find stubs ../../app/src/main/java/com/kavopdf/app/engine ConvertAll.java ConvertOne.java -name '*.java' -newer out/ConvertAll.class 2>/dev/null | head -1) || true
if [ -f out/ConvertAll.class ] && [ -z "$_newest_src" ]; then
  echo "engine unchanged - skipping compile" >&2
  tr "engine unchanged, compile skipped"
  exit 0
fi
_t0=$(date +%s)
javac -nowarn -d out $(find stubs -name '*.java')
# libs/aar/assets is NOT optional. pdfbox-android ships the 14 Standard-14 AFM metric
# files in the AAR's assets/ directory, not in classes.jar (classes.jar contains zero
# .afm entries - they are Android assets by design). Standard14Fonts.loadMetrics()
# falls back to PDType1Font.class.getResourceAsStream("/com/tom_roush/pdfbox/resources/
# afm/<name>.afm") on a plain JVM, so with assets off the classpath every PDType1Font
# dies with "resource 'com/tom_roush/pdfbox/resources/afm/Times-Roman.afm' not found".
# That is what made TestPdfToWord unrunnable: an asset-bootstrap bug, not engine code.
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
javac -nowarn -cp "$CP" -d out $(find ../../app/src/main/java/com/kavopdf/app/engine -name '*.java')
javac -nowarn -cp "$CP" -d out ConvertAll.java ConvertOne.java

test -f out/ConvertAll.class || { echo "ConvertAll did not compile" >&2; exit 1; }
test -f out/ConvertOne.class || { echo "ConvertOne did not compile" >&2; exit 1; }
echo "engine built - ConvertAll ready ($(( $(date +%s) - _t0 ))s)" >&2
tr "engine built in $(( $(date +%s) - _t0 ))s"
