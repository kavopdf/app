#!/usr/bin/env bash
# jdk-fetch.sh - put a JDK on a fresh pod, at the path the tools already look for.
#
# WHY THIS EXISTS. A fresh pod has no `java` and no `javac`. Every measurement in this project needs
# one: the engine is Java, corpus-convert.py compiles and runs ConvertAll, regress.py --check cannot
# build the corpus the gate reads, and google_safe.py then has nothing to inspect. The failure is
# silent in the worst way - the gate prints "no java on PATH and no JAVA_HOME - the engine cannot be
# run" and then "PASS", so a run reads a green gate it never actually exercised.
#
# Measured 24 Nov, 15:03 slot: a fresh pod, `java` absent, `verify_requirements(binary:java)` false.
# The whole corpus was converted 6 minutes after this download. Nobody had written the download down.
#
# THE PATH MATTERS. corpus-convert.py:java_bin() looks for, in order:
#     $JAVA_HOME/bin/java
#     /scratch/work/jdk-17.0.21.1+2/bin/java
#     /scratch/work/.p2w-jdk/jdk/bin/java
# so this installs to the third, which needs no JAVA_HOME and no PATH edit. api.adoptium.net is on the
# pod's egress allowlist; nothing here needs a token.
#
# USAGE
#   bash tools/p2w-bench/jdk-fetch.sh          # install if absent, then print the version
#   eval "$(bash tools/p2w-bench/jdk-fetch.sh --path)"   # also put it on PATH for this shell
#
# EXIT 0 a JDK is present and runs. 1 it could not be fetched.
set -uo pipefail

DEST="/scratch/work/.p2w-jdk/jdk"
URL="https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse"
WANT_PATH=0
[ "${1:-}" = "--path" ] && WANT_PATH=1

if [ ! -x "$DEST/bin/java" ]; then
  echo "fetching a JDK 17 from adoptium" >&2
  mkdir -p /scratch/work/.p2w-jdk
  TMP=/scratch/work/.p2w-jdk/jdk.tar.gz
  if ! curl -sSL -o "$TMP" "$URL"; then
    echo "download failed - is api.adoptium.net reachable?" >&2
    exit 1
  fi
  rm -rf /scratch/work/.p2w-jdk/unpacked
  mkdir -p /scratch/work/.p2w-jdk/unpacked
  if ! tar xzf "$TMP" -C /scratch/work/.p2w-jdk/unpacked; then
    echo "unpack failed" >&2
    exit 1
  fi
  # The tarball's top directory carries the build number, so it is found rather than assumed.
  SRC="$(find /scratch/work/.p2w-jdk/unpacked -maxdepth 1 -mindepth 1 -type d | head -1)"
  [ -n "$SRC" ] || { echo "no top-level directory in the tarball" >&2; exit 1; }
  rm -rf "$DEST"
  mv "$SRC" "$DEST" || exit 1
  rm -f "$TMP"
fi

if ! "$DEST/bin/java" -version >/dev/null 2>&1; then
  echo "a JDK is at $DEST but does not run" >&2
  exit 1
fi

if [ "$WANT_PATH" = "1" ]; then
  echo "export JAVA_HOME=$DEST; export PATH=$DEST/bin:\$PATH"
else
  "$DEST/bin/java" -version 2>&1 | head -1
  echo "java at $DEST/bin/java"
fi
exit 0
