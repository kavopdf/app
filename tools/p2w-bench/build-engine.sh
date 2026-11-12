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
rm -rf out && mkdir -p out
javac -nowarn -d out $(find stubs -name '*.java')
CP="out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
javac -nowarn -cp "$CP" -d out $(find ../../app/src/main/java/com/kavopdf/app/engine -name '*.java')
javac -nowarn -cp "$CP" -d out ConvertAll.java

test -f out/ConvertAll.class || { echo "ConvertAll did not compile" >&2; exit 1; }
echo "engine built - ConvertAll ready" >&2
