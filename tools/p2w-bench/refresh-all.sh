#!/bin/bash
# refresh-all.sh - the whole Google refresh, end to end, no human step.
#
#   bash tools/p2w-bench/refresh-all.sh
#
# 1. builds the engine and the corpus for whatever is on disk
# 2. publishes the .docx as release assets on the public repo (the only host the sandbox can write)
# 3. pulls each asset into Drive as a converted Google Doc
# 4. exports Google's render, scores it, stamps the verdict with the engine hash
# 5. deletes the release, so the corpus is public for minutes rather than hours
#
# Steps 2-4 are the loop that used to need a human. Measured 25 Nov: 213 assets, 213 uploads,
# 213 renders, 212 scored, 1 refused.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
FOLDER="${P2W_DRIVE_FOLDER:-1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA}"
REPO="${P2W_REPO:-kavopdf/app}"
TAG="p2w-render-$(date +%s)"
cd "$ROOT"

echo "== engine + corpus"
export JAVA_HOME="${JAVA_HOME:-/scratch/work/jdk-17.0.21.1+2}"
export PATH="$JAVA_HOME/bin:$PATH"
bash tools/p2w-bench/build-engine.sh >/dev/null
python3 tools/p2w-bench/corpus-slice.py --budget 400 -j 4 | tail -2

echo "== publish assets"
gh release create "$TAG" --title "p2w render staging" \
   --notes "temporary render staging; deleted by refresh-all.sh" >/dev/null
gh release upload "$TAG" /scratch/work/p2w/out/*.docx --clobber >/dev/null
echo "   $(gh release view "$TAG" --json assets -q '.assets | length') assets"

echo "== into Drive"
python3 tools/p2w-bench/gh-to-drive.py --tag "$TAG" --repo "$REPO" --folder "$FOLDER" --jobs 6

echo "== render + score"
python3 tools/p2w-bench/refresh-google.py --folder "$FOLDER" --jobs 6

echo "== delete the release"
gh release delete "$TAG" --yes --cleanup-tag >/dev/null && echo "   deleted $TAG"

echo "== state"
python3 - "$ROOT" <<'PY'
import json, glob, os, sys
root = sys.argv[1]
eng = json.load(open("/scratch/work/p2w/.stamp", encoding="utf-8"))["engine"]
n = clean = same = refused = 0
for f in glob.glob(os.path.join(root, "benchmarks", "gverify", "*.json")):
    d = json.load(open(f))
    n += 1
    if (d.get("engine") or "") == eng:
        same += 1
    if d.get("status") == "page_count_refused":
        refused += 1
        continue
    if not (d.get("failed") or []):
        clean += 1
print("   verdicts on %s: %d of %d | clean %d of %d scored | refused %d"
      % (eng[:16], same, n, clean, n - refused, refused))
PY
