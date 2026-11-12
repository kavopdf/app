#!/usr/bin/env bash
#
# commit-gate.sh - an engine change may not be committed without its evidence.
#
# WHY THIS EXISTS
#   The fixer prompt already said "you may not commit without running the ratchet"
#   and "precommit must exit 0". Both are instructions, and an instruction is a
#   promise. This is the check that makes it a fact.
#
#   The difference matters because of one specific sentence. "I ran the ratchet"
#   is a claim. "RATCHET.json changed in the same working tree as the engine" is
#   evidence, and evidence cannot be misremembered at 3am. So the gate demands
#   three things and refuses on any of them:
#
#     1. ratchet.py exits 0            - no document fell
#     2. precommit.sh --no-corpus exits 0 - it builds and the guards pass
#     3. the evidence files changed    - the numbers this fix produced are here
#
#   The third is the one that catches a fixer which reverted nothing, changed
#   nothing, and committed anyway.
#
#   THE .TXT HALF IS GATED TOO, once it has been measured at least once. One
#   conversion writes both outputs from the same model, so a change made for the
#   .docx can move the .txt, and only its own store can see that. Until
#   RESULTS-TXT.jsonl exists there is nothing to move and the gate says so rather
#   than demanding a file that does not exist yet.
#
# USAGE
#   bash tools/commit-gate.sh
#   exit 0 -> safe to commit, and .p2w-gate-ok records what was proven
#   exit 1 -> do not commit; the reason is printed
#
#   bash tools/commit-gate.sh --status   report without running anything

set -u

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO" || exit 1

ENGINE_DIR="app/src/main/java/com/kavopdf/app/engine"
BENCH="tools/p2w-bench"
EVIDENCE="BASELINE.md RESULTS.jsonl RATCHET.json"
EVIDENCE_TXT="RESULTS-TXT.jsonl RATCHET-TXT.json"
OK_FILE=".p2w-gate-ok"

say() { printf '%s\n' "$*"; }
bad() { printf '  FAIL  %s\n' "$*"; }

# The .txt half is gated only once it has been measured at least once. Before that
# there is no store to move, and demanding one would block every commit for a file
# that does not exist yet.
txt_live() { [ -f "$BENCH/RESULTS-TXT.jsonl" ]; }

engine_changed() {
  ! git diff --quiet HEAD -- "$ENGINE_DIR" 2>/dev/null && return 0
  ! git diff --cached --quiet -- "$ENGINE_DIR" 2>/dev/null && return 0
  return 1
}

file_changed() {
  ! git diff --quiet HEAD -- "$1" 2>/dev/null && return 0
  ! git diff --cached --quiet -- "$1" 2>/dev/null && return 0
  return 1
}

ENGINE=$(git log -1 --format=%h -- "$ENGINE_DIR" 2>/dev/null || echo unknown)

if [ "${1:-}" = "--status" ]; then
  say "commit-gate"
  say "  engine hash      : $ENGINE"
  if engine_changed; then say "  engine changed   : yes - this commit needs evidence"
  else say "  engine changed   : no - nothing to prove"; fi
  for f in $EVIDENCE; do
    if file_changed "$BENCH/$f"; then say "  $f : changed"
    else say "  $f : unchanged"; fi
  done
  if txt_live; then
    for f in $EVIDENCE_TXT; do
      if file_changed "$BENCH/$f"; then say "  $f : changed"
      else say "  $f : unchanged"; fi
    done
  else
    say "  .txt half        : not measured yet - not gated"
  fi
  [ -f "$OK_FILE" ] && say "  gate token       : present ($(cat "$OK_FILE"))" \
                    || say "  gate token       : none"
  exit 0
fi

say "commit-gate"
python3 -c "
import sys; sys.path.insert(0,'tools/p2w-bench')
try:
    from trace import note
    note('commit-gate', 'started')
except Exception:
    pass
" 2>/dev/null || true

if ! engine_changed; then
  say "  engine unchanged - nothing to prove"
  exit 0
fi

say "  engine changed ($ENGINE) - evidence required"
FAILED=0
LOG=$(mktemp)

# ---- 1. the ratchet -------------------------------------------------------
if python3 "$BENCH/ratchet.py" >"$LOG" 2>&1; then
  say "  ok    ratchet    - the bar held or rose"
else
  bad "ratchet - a document fell below its best"
  grep -E "REGRESSED|->|below" "$LOG" | head -6 | sed 's/^/        /'
  FAILED=1
fi

# ---- 1b. the .txt ratchet -------------------------------------------------
# Separate store, separate marks. One conversion writes both outputs from the same
# model, so a change made for the .docx can move the .txt, and only this half can see it.
if txt_live; then
  if python3 "$BENCH/ratchet.py" --txt >"$LOG" 2>&1; then
    say "  ok    ratchet --txt - the .txt bar held or rose"
  else
    bad "ratchet --txt - a .txt fell below its best"
    grep -E "REGRESSED|->|below" "$LOG" | head -6 | sed 's/^/        /'
    FAILED=1
  fi
fi

# ---- 2. it builds ---------------------------------------------------------
if bash tools/precommit.sh --no-corpus >"$LOG" 2>&1; then
  say "  ok    precommit  - builds, guards pass"
else
  bad "precommit - it does not build, or a guard tripped"
  grep -E "^ *FAIL|FAILED|error:" "$LOG" | head -6 | sed 's/^/        /'
  FAILED=1
fi

# ---- 3. the evidence is in this commit ------------------------------------
# The engine changed, so a measurement must have happened. A commit that carries
# a new engine and an old RATCHET.json is a fix nobody checked.
for f in $EVIDENCE; do
  if file_changed "$BENCH/$f"; then
    say "  ok    $f changed with it"
  else
    bad "$f is unchanged - the engine moved and the numbers did not"
    FAILED=1
  fi
done

if txt_live; then
  for f in $EVIDENCE_TXT; do
    if file_changed "$BENCH/$f"; then
      say "  ok    $f changed with it"
    else
      bad "$f is unchanged - the engine moved and the .txt numbers did not"
      FAILED=1
    fi
  done
fi

# ATTEMPTS.json appears on the first recorded attempt, so it may legitimately
# be absent on a first run; once it exists it must move with the engine.
if [ -f "$BENCH/ATTEMPTS.json" ]; then
  if file_changed "$BENCH/ATTEMPTS.json"; then
    say "  ok    ATTEMPTS.json changed with it"
  else
    bad "ATTEMPTS.json unchanged - no attempt was recorded for this engine change"
    FAILED=1
  fi
fi

rm -f "$LOG"

if [ "$FAILED" -ne 0 ]; then
  say ""
  say "  NO COMMIT. Fix what failed above, or revert the engine:"
  say "      git checkout -- $ENGINE_DIR"
  rm -f "$OK_FILE"
  exit 1
fi

printf 'engine=%s time=%s\n' "$ENGINE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OK_FILE"
say ""
say "  PASS - engine $ENGINE is proven and may be committed"
say "  token: $OK_FILE"
exit 0
