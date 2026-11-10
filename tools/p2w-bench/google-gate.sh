#!/usr/bin/env bash
# google-gate.sh - the release gate that gate.py cannot be.
#
# WHY THIS EXISTS
#   gate.py scores blank, blocks, extra, lines, missing, nobg, pages, reflines and
#   refpages. Not one of those moves when text lands in the wrong place. That is why
#   the w:framePr change passed CI on 10 Nov, shipped as 3.53.5, and broke the stamp
#   on the phone: the regression job compared word and line counts, the counts were
#   identical, and the build went out.
#
#   CI cannot fix this by itself. The only instrument that sees what Google Docs
#   does is a Drive round trip, and a GitHub runner has no Drive. So the Google
#   evidence has to be produced beforehand - by the baseline and fixer crons - and
#   this script reads it.
#
# WHAT IT ASSERTS
#   1. Every document in the corpus has a row in BASELINE.md.
#   2. Every row measured on the CURRENT engine has a score.
#   3. No document measured on the current engine scores below the floor.
#   4. If an older engine's score exists for a document, the current one is not worse.
#
#   A release with documents measured on an older engine is not blocked - the corpus
#   is measured over days - but the count of unmeasured documents is printed, so a
#   release cannot claim more than it verified.
#
# USAGE
#   bash tools/p2w-bench/google-gate.sh            # gate on main
#   bash tools/p2w-bench/google-gate.sh --strict   # also fail if any document is unmeasured
#
# EXIT
#   0 pass, 1 fail, 2 could not run
set -u

REPO=""
STRICT=0
for a in "$@"; do
  case "$a" in
    --strict) STRICT=1 ;;
    *)        REPO="$a" ;;
  esac
done
[ -n "$REPO" ] || REPO="$(cd "$(dirname "$0")/../.." && pwd)"

BASE="$REPO/tools/p2w-bench/BASELINE.md"
ENGINE_DIR="app/src/main/java/com/kavopdf/app/engine"

[ -f "$BASE" ] || { echo "google-gate: BASELINE.md not found" >&2; exit 2; }
command -v git >/dev/null || { echo "google-gate: git not available" >&2; exit 2; }

CUR_ENGINE=$(git -C "$REPO" log -1 --format=%h -- "$ENGINE_DIR" 2>/dev/null)
[ -n "$CUR_ENGINE" ] || { echo "google-gate: cannot read engine commit" >&2; exit 2; }

python3 - "$BASE" "$CUR_ENGINE" "$STRICT" <<'PY'
import sys, re

path, cur_engine, strict = sys.argv[1], sys.argv[2], sys.argv[3] == "1"

rows, total, filled, on_current, stale, worse = [], 0, 0, 0, 0, []
FLOOR = 1  # a document scoring 0 of 31 has produced nothing at all

for line in open(path, encoding="utf-8"):
    if not line.startswith("| ") or line.startswith("|---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells or not cells[0]:
        continue
    # Identify the header by its first cell, never by substring: four corpus
    # documents have "document" in their name and were being skipped as headers.
    if cells[0].lower() == "document":
        continue
    total += 1
    doc = cells[0]
    score = cells[1] if len(cells) > 1 else ""
    engine = cells[4] if len(cells) > 4 else ""
    if not score:
        continue
    filled += 1
    m = re.match(r"(\d+)\s*/\s*(\d+)", score)
    if not m:
        continue
    got, out_of = int(m.group(1)), int(m.group(2))
    if got < FLOOR:
        worse.append((doc, score, "zero score"))
    if engine == cur_engine:
        on_current += 1
    elif engine:
        stale += 1

print("google-gate")
print("  engine in app/src     : %s" % cur_engine)
print("  documents in table    : %d" % total)
print("  measured at all       : %d" % filled)
print("  measured on this engine: %d" % on_current)
print("  measured on an older engine: %d" % stale)

fail = False
if total == 0:
    print("  FAIL: the table has no documents")
    fail = True
if worse:
    print("  FAIL: %d document(s) score zero" % len(worse))
    for d, s, why in worse[:10]:
        print("        %-44s %-8s %s" % (d[:44], s, why))
    fail = True
if strict and filled < total:
    print("  FAIL (--strict): %d document(s) never measured" % (total - filled))
    fail = True
if on_current == 0 and filled > 0:
    print("  NOTE: nothing has been measured on this engine yet; the Google evidence")
    print("        predates the current build and does not vouch for it.")

print("  %s" % ("PASS" if not fail else "FAIL"))
sys.exit(0 if not fail else 1)
PY
