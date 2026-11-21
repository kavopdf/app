#!/usr/bin/env bash
# corpus-fetch.sh - put the 213-document corpus on a fresh pod, and prove it is the whole one.
#
# WHY THIS EXISTS
#   Two fixer runs measured a construct through Google and could not land it, for one mechanical
#   reason: an engine change may not be committed until the whole corpus has been measured
#   (regress.py --check, the pre-commit hook), and the corpus is not in the repository. 208 of the
#   213 PDFs are four release assets; the other five travel in the repo. Nobody had written the six
#   minutes down, so every run started from nothing and ended with an unlandable patch.
#
# WHAT IT DOES
#   1. downloads the four corpus-v1 release zips (cached, so a re-run costs nothing)
#   2. unpacks them flat into /scratch/work/p2w/corpus
#   3. adds benchmarks/corpus-extra/*.pdf and benchmarks/realworld/*.pdf from the clone
#   4. counts against benchmarks/RANKING.csv and refuses if any document is missing
#
# USAGE
#   bash tools/p2w-bench/corpus-fetch.sh
#   bash tools/p2w-bench/corpus-fetch.sh --dir /scratch/work/p2w/corpus
#
# EXIT 0  the corpus holds every document the published ranking scores
# EXIT 1  a document is missing, or the count disagrees - do not measure
#
# NOTHING IS DELETED. An existing corpus directory is added to, never cleared: a run that already
# measured something keeps its files.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
CORPUS="/scratch/work/p2w/corpus"
CACHE="/scratch/work/cache"
X="/scratch/work/p2w/x"
while [ $# -gt 0 ]; do
  case "$1" in
    --dir) CORPUS="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done
mkdir -p "$CORPUS" "$CACHE" "$X"

ZIPS="p2w-all-groups p2w-batch-1 pdf-to-word-test-corpus-v3 p2w-round2-additions"
for z in $ZIPS; do
  if [ ! -s "$CACHE/$z.zip" ]; then
    echo "== $z"
    gh release download corpus-v1 --repo kavopdf/app -p "$z.zip" -O "$CACHE/$z.zip" --clobber || true
  fi
  if [ -s "$CACHE/$z.zip" ]; then
    unzip -oq "$CACHE/$z.zip" -d "$X"
  else
    echo "!! could not fetch $z.zip - the corpus will be short" >&2
  fi
done

find "$X" -name '*.pdf' -exec cp -n {} "$CORPUS"/ \;
cp -n "$ROOT"/benchmarks/corpus-extra/*.pdf "$CORPUS"/ 2>/dev/null || true
cp -n "$ROOT"/benchmarks/realworld/*.pdf   "$CORPUS"/ 2>/dev/null || true

python3 - "$CORPUS" "$ROOT" <<'EOF'
import csv, glob, os, sys
corpus, root = sys.argv[1], sys.argv[2]
have = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(corpus, "*.pdf"))}
rank = os.path.join(root, "benchmarks", "RANKING.csv")
if not os.path.exists(rank):
    print("corpus: %d PDFs (no RANKING.csv to check against)" % len(have)); sys.exit(0)
names = [r["document"] for r in csv.DictReader(open(rank, encoding="utf-8"))]
missing = [n for n in names if n not in have]
print("corpus: %d PDFs, %d scored in RANKING.csv, %d missing" % (len(have), len(names), len(missing)))
if missing:
    print("  " + ", ".join(missing[:10]))
    print("  DO NOT MEASURE - a partial corpus cannot be the full-corpus check the gate needs.")
    sys.exit(1)
EOF
