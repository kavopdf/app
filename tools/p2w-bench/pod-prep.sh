#!/usr/bin/env bash
# pod-prep.sh - put EVERY prerequisite of the commit gate on the pod, in the one order that works.
#
# WHY THIS EXISTS
#   Three prerequisites are each documented in their own script, and nothing called them in order. On a
#   fresh pod the gate therefore failed four times in a row, each time with a different message, and each
#   time only after a person read the message and ran the next script by hand:
#
#     1. tools/install-gate.sh installs the hook, the hook refuses:
#          "corpus: could not be built (1) - no corpus PDFs found - run corpus-fetch.sh first"
#     2. after corpus-fetch.sh (213 PDFs, 0 missing):
#          "no java on PATH and no JAVA_HOME - run jdk-fetch.sh"
#     3. after jdk-fetch.sh:
#          "041122-Account_Opening_Form.pdf : Caused by: java.lang.ClassNotFoundException: ConvertAll"
#     4. only after libs + aar + stubs + engine compile by hand did out/ConvertAll.class exist.
#
#   A prerequisite that is not called by the thing that needs it is not a prerequisite, it is a
#   discovery. This script is the missing caller. It is idempotent at every step: on a warm pod each
#   step is a stat (or a one-file `find -newer`) and prints "skipped (warm)".
#
# WHAT IT DOES, IN THIS ORDER
#   1. corpus   bash tools/p2w-bench/corpus-fetch.sh        -> /scratch/work/p2w/corpus (213 PDFs)
#   2. jdk      bash tools/p2w-bench/jdk-fetch.sh           -> /scratch/work/.p2w-jdk/jdk
#   3. libs     curl the PDFBox-Android AAR + BouncyCastle 1.72 -> tools/engine-verify/libs/
#   4. aar      unzip the AAR                               -> libs/aar/{classes.jar,assets/}
#   5. stubs    javac stubs                                 -> tools/engine-verify/out/
#   6. engine   javac app/src/main/java + ConvertAll.java + ConvertOne.java -> out/
#
#   The URLs and the classpath are the ones verify-engine.sh and corpus-convert.py already use,
#   copied verbatim - this script must never be the second place a version is written down.
#
# NOTHING IS DELETED. tools/engine-verify/out-old/ (stale ConvertAll.class files, not on the
# classpath) is left exactly as it is, libs/aar is unpacked into rather than wiped, and the corpus
# directory is only ever added to. Only out/ is written, and only by javac and by two sentinels.
#
# USAGE
#   bash tools/p2w-bench/pod-prep.sh
#
# EXIT 0  every prerequisite is present and the engine classes are compiled
# EXIT 1  a named cause: corpus | jdk | libs | aar | stubs | engine
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
EV="$ROOT/tools/engine-verify"

# jdk-fetch.sh installs here, and corpus-convert.py:java_bin() looks here third - no JAVA_HOME, no
# PATH edit needed. This script sets both for its own javac calls anyway.
JDK="/scratch/work/.p2w-jdk/jdk"
CORPUS="/scratch/work/p2w/corpus"

# VERBATIM from verify-engine.sh:41 and corpus-convert.py:66 (DEFAULT_CP). Both resolve relative to
# tools/engine-verify, which is why every javac/java call below runs with that as the cwd.
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"

# VERBATIM from verify-engine.sh:29-32. PDFBox-Android 2.0.27.0 and BouncyCastle 1.72.
AAR_URL="https://repo1.maven.org/maven2/com/tom-roush/pdfbox-android/2.0.27.0/pdfbox-android-2.0.27.0.aar"
BCPROV_URL="https://repo1.maven.org/maven2/org/bouncycastle/bcprov-jdk15to18/1.72/bcprov-jdk15to18-1.72.jar"
BCPKIX_URL="https://repo1.maven.org/maven2/org/bouncycastle/bcpkix-jdk15to18/1.72/bcpkix-jdk15to18-1.72.jar"
BCUTIL_URL="https://repo1.maven.org/maven2/org/bouncycastle/bcutil-jdk15to18/1.72/bcutil-jdk15to18-1.72.jar"

AFM_DIR="libs/aar/assets/com/tom_roush/pdfbox/resources/afm"

STEP=0
TOTAL=6
say()  { STEP=$((STEP + 1)); printf 'pod-prep: [%d/%d] %-7s %s\n' "$STEP" "$TOTAL" "$1" "$2"; }
# A named cause, so the operator reads "jdk" and not a stack trace or a silent PASS.
die()  { echo "pod-prep: FAILED at step '$1' - $2" >&2; exit 1; }

[ -d "$EV" ] || die layout "no $EV - run this from a clone: tools/p2w-bench/pod-prep.sh"
[ -d "$ROOT/app/src/main/java" ] || die layout "no app/src/main/java under $ROOT"
cd "$EV" || die layout "cannot cd to $EV"

# ---------------------------------------------------------------------------
# 1. CORPUS. 208 of the 213 PDFs are release assets, not repository content, so a fresh pod has none
#    and the gate's first call answers "no corpus PDFs found". corpus-fetch.sh is cached and never
#    clears the directory, so it is safe to call; the guard below means a warm pod does not even do
#    that. RANKING.csv is the same source corpus-fetch.sh counts against.
# ---------------------------------------------------------------------------
RANK="$ROOT/benchmarks/RANKING.csv"
WANT=0
[ -f "$RANK" ] && WANT=$(( $(wc -l < "$RANK") - 1 ))
HAVE=$(ls -1 "$CORPUS"/*.pdf 2>/dev/null | wc -l)
if [ "$WANT" -gt 0 ] && [ "$HAVE" -ge "$WANT" ]; then
  say corpus "$HAVE PDFs in $CORPUS, $WANT scored - skipped (warm)"
else
  bash "$HERE/corpus-fetch.sh" || die corpus "corpus-fetch.sh exited $? - a partial corpus cannot be the full-corpus check the gate needs"
  HAVE=$(ls -1 "$CORPUS"/*.pdf 2>/dev/null | wc -l)
  [ "$HAVE" -gt 0 ] || die corpus "corpus-fetch.sh reported success but $CORPUS holds no PDFs"
  say corpus "$HAVE PDFs in $CORPUS (fetched)"
fi

# ---------------------------------------------------------------------------
# 2. JDK. jdk-fetch.sh already skips its download when $JDK/bin/java is executable, but it then runs
#    `java -version`; the guard here keeps a warm pod to one test -x per binary.
# ---------------------------------------------------------------------------
if [ -x "$JDK/bin/java" ] && [ -x "$JDK/bin/javac" ]; then
  say jdk "java + javac at $JDK/bin - skipped (warm)"
else
  bash "$HERE/jdk-fetch.sh" || die jdk "jdk-fetch.sh exited $? - is api.adoptium.net reachable?"
  [ -x "$JDK/bin/javac" ] || die jdk "jdk-fetch.sh exited 0 but $JDK/bin/javac is not executable"
  say jdk "installed $JDK ($("$JDK/bin/java" -version 2>&1 | head -1))"
fi
export JAVA_HOME="$JDK"
export PATH="$JDK/bin:$PATH"

# ---------------------------------------------------------------------------
# 3. LIBS. curl -sSL without -f writes an error page and exits 0, so every download is size-checked:
#    a 404 body saved as classes.jar is the failure mode that produces ClassNotFoundException later.
# ---------------------------------------------------------------------------
mkdir -p libs
need_libs=0
for f in pdfbox.aar bcprov.jar bcpkix.jar bcutil.jar; do
  [ -s "libs/$f" ] || need_libs=1
done
if [ "$need_libs" = "0" ]; then
  say libs "pdfbox.aar + bcprov/bcpkix/bcutil 1.72 present in libs - skipped (warm)"
else
  dl() { # dl <url> <dest>
    [ -s "$2" ] && return 0
    curl -sSL -o "$2" "$1" || return 1
    [ -s "$2" ] || return 1
    [ "$(wc -c < "$2")" -gt 10000 ] || { rm -f "$2"; return 1; }
  }
  dl "$AAR_URL"     libs/pdfbox.aar  || die libs "could not download pdfbox-android 2.0.27.0 .aar - is repo1.maven.org reachable?"
  dl "$BCPROV_URL"  libs/bcprov.jar  || die libs "could not download bcprov-jdk15to18 1.72"
  dl "$BCPKIX_URL"  libs/bcpkix.jar  || die libs "could not download bcpkix-jdk15to18 1.72"
  dl "$BCUTIL_URL"  libs/bcutil.jar  || die libs "could not download bcutil-jdk15to18 1.72"
  say libs "pdfbox-android 2.0.27.0 + bouncycastle 1.72 in libs (downloaded)"
fi

# ---------------------------------------------------------------------------
# 4. AAR. classes.jar alone is not enough: the Standard-14 AFM metrics live in the AAR's assets/,
#    and without libs/aar/assets on the classpath every font construction dies at getAFM. verify-engine
#    checks the same 14 files, so a half-unpacked AAR fails here rather than fifteen minutes into a
#    suite. Unpacked into, never wiped - this script deletes nothing.
# ---------------------------------------------------------------------------
afm_count() { ls -1 "$AFM_DIR"/*.afm 2>/dev/null | wc -l; }
if [ -s "libs/aar/classes.jar" ] && [ "$(afm_count)" -eq 14 ]; then
  say aar "libs/aar/classes.jar + 14 AFM assets - skipped (warm)"
else
  mkdir -p libs/aar
  ( cd libs/aar && unzip -oq ../pdfbox.aar ) || die aar "unzip of libs/pdfbox.aar failed"
  [ -s "libs/aar/classes.jar" ] || die aar "libs/pdfbox.aar holds no classes.jar"
  [ "$(afm_count)" -eq 14 ] || die aar "AAR unpacked without its 14 AFM assets ($(afm_count) found) - classes.jar alone cannot load a font"
  say aar "libs/aar/classes.jar + 14 AFM assets (unpacked)"
fi

# ---------------------------------------------------------------------------
# 5. STUBS. The engine touches a handful of android.* classes; the stubs in tools/engine-verify/stubs
#    stand in for them on a plain JVM. Compiled into out/ FIRST, because the engine compile puts out/
#    on its classpath and will not resolve android.* without it.
# ---------------------------------------------------------------------------
mkdir -p out
STUB_OK="out/.pod-prep-stubs.ok"
ENG_OK="out/.pod-prep-engine.ok"
if [ -f "$STUB_OK" ] && [ -z "$(find stubs -name '*.java' -newer "$STUB_OK" -print -quit)" ]; then
  say stubs "out/ up to date with stubs/ - skipped (warm)"
else
  javac -nowarn -d out $(find stubs -name '*.java') || die stubs "javac failed on tools/engine-verify/stubs"
  touch "$STUB_OK"
  say stubs "$(find stubs -name '*.java' | wc -l) stub sources compiled into out/"
fi

# ---------------------------------------------------------------------------
# 6. ENGINE + ConvertAll + ConvertOne. This is the step whose absence produced
#      "Caused by: java.lang.ClassNotFoundException: ConvertAll"
#    corpus-convert.py runs `java -cp out:... ConvertAll <shard> <out>` with cwd tools/engine-verify,
#    so out/ConvertAll.class is the only thing that makes the corpus buildable. out-old/ is NOT on
#    that classpath and is left untouched - a stale ConvertAll.class in it is not a fallback.
# ---------------------------------------------------------------------------
STALE=""
if [ -f "$ENG_OK" ]; then
  STALE="$(find ../../app/src/main/java -name '*.java' -newer "$ENG_OK" -print -quit)"
  [ -z "$STALE" ] && STALE="$(find ConvertAll.java ConvertOne.java -newer "$ENG_OK" -print -quit)"
  # out/ is on the engine's classpath, so a stub rebuilt after the engine makes the engine classes
  # stale in exactly the same way an engine edit does.
  [ -z "$STALE" ] && [ "$STUB_OK" -nt "$ENG_OK" ] && STALE="stubs"
fi
if [ -f "$ENG_OK" ] && [ -s out/ConvertAll.class ] && [ -s out/ConvertOne.class ] && [ -z "$STALE" ]; then
  say engine "out/ConvertAll.class + out/ConvertOne.class current - skipped (warm)"
else
  javac -nowarn -cp "$CP" -d out \
      $(find ../../app/src/main/java -name '*.java') ConvertAll.java ConvertOne.java \
    || die engine "javac failed on app/src/main/java + ConvertAll.java + ConvertOne.java (classpath: $CP)"
  [ -s out/ConvertAll.class ] || die engine "javac exited 0 but out/ConvertAll.class was not written"
  [ -s out/ConvertOne.class ] || die engine "javac exited 0 but out/ConvertOne.class was not written"
  touch "$ENG_OK"
  say engine "$(find ../../app/src/main/java -name '*.java' | wc -l) engine sources + ConvertAll + ConvertOne compiled into out/"
fi

echo "pod-prep: ready - corpus $HAVE PDFs, java $("$JDK/bin/java" -version 2>&1 | head -1 | awk '{print $3}' | tr -d '"'), classpath $CP"
exit 0
