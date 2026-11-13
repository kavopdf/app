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
  # The gap is part of the status, not something you find out by running the gate.
  # A reader asking "where does this tree stand" must see that the ratchet has not
  # been asked about some documents, and on whose authority that was accepted.
  if [ -f "$BENCH/UNMEASURED.json" ]; then
    python3 - "$BENCH" <<'PYGAP' || true
import json, os, sys
b = sys.argv[1]
try:
    d = json.load(open(os.path.join(b, "UNMEASURED.json")))
except Exception:
    raise SystemExit(0)
c = d.get("counts") or {}
i = d.get("instrument") or {}
print("  ratchet gap      : %s of %s document(s) not compared (instrument %s checks, sha %s)"
      % (c.get("not_compared"), c.get("scored"), i.get("checks"), i.get("sha")))
w = os.path.join(b, "WAIVER.json")
if os.path.exists(w):
    try:
        wd = json.load(open(w))
        print("  waiver           : \"%s\"" % wd.get("reason"))
    except Exception:
        pass
else:
    print("  waiver           : none - a gap like this cannot be committed through")
PYGAP
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

# NO SLOT CHECK HERE, and this is deliberate.
#
# It was added on 12 Nov because the 20:43 run committed its outcome and left the slot claimed.
# But a run now does up to three attempts and commits between them - holding the slot the whole
# time, as it should - so this check refused the between-attempt commits. The agent worked around
# it exactly as you would expect: release, commit, re-claim, three times a run. Two claims ten
# minutes apart on the morning of 13 Nov were that workaround.
#
# The check was also not needed. A leaked slot blocks the next run for 45 minutes, and the next
# run is 60 minutes later, so a leak always clears itself before it costs anything. What the
# claim exists for - stopping two runs editing the engine at once - it still does, and the
# release is STEP 9's job, with the stale timer as the backstop.

if ! engine_changed; then
  # A reverted attempt is still an attempt.
  #
  # This used to exit here, before any check. On 12 Nov a run changed the engine, measured
  # ten documents, reverted the change and committed - so the engine was unchanged, the gate
  # said "nothing to prove", and ATTEMPTS.json was never touched. The class stayed at
  # attempts=0 and was picked again on the next run, and the one after that: a loop with no
  # end, no error, and a hypothesis ledger quietly filling with ruled-out theories for a
  # class the pipeline believed had never been tried.
  #
  # Recording a theory without recording the attempt is the exact shape of that bug, so the
  # gate now refuses it whether or not the engine survived.
  if [ -f "$BENCH/HYPOTHESES.md" ] && file_changed "$BENCH/HYPOTHESES.md"; then
    if [ ! -f "$BENCH/ATTEMPTS.json" ] || ! file_changed "$BENCH/ATTEMPTS.json"; then
      bad "HYPOTHESES.md records a theory but ATTEMPTS.json records no attempt"
      bad "A reverted attempt still counts - run classify.py --attempt <class> --moved N --total M"
      exit 1
    fi
    say "  engine unchanged, but an attempt was recorded - that is allowed"
  fi
  say "  engine unchanged - nothing else to prove"
  exit 0
fi

say "  engine changed ($ENGINE) - evidence required"
FAILED=0
LOG=$(mktemp)

# ---- 1. the ratchet -------------------------------------------------------
# One question used to be asked here: "did ratchet.py exit 0". On 13 Nov the answer
# became no, permanently, for every commit - the instrument retired five checks and
# added two, all 211 marks were taken by the instrument that no longer exists, and
# nothing had been re-measured. A guard that is always red is not a guard. The two
# ways out are to delete it or to ignore it, and both were wrong, so the ratchet
# now has three answers and this gate has three actions:
#
#   exit 0  PASS        the bar held or rose
#   exit 1  FAIL        a document fell. No waiver exists for this and none will be
#                       added: a number that moved under the same instrument is not
#                       a gap, it is a regression.
#   exit 2  REFUSED     no instrument, or a waiver with no reason
#   exit 3  UNMEASURED  nothing fell, but some marks could not be compared. Not a
#                       pass. Whether it may be committed through is decided by
#                       unmeasured.py against WAIVER.json, never by this script.
RATCHET_GAP=""
WAIVED=""
DOCX_WAIVED=0
TXT_WAIVED=0

ratchet_half() {
  local mode="$1" label="$2" log rc
  log=$(mktemp)
  # shellcheck disable=SC2086
  python3 "$BENCH/ratchet.py" $mode >"$log" 2>&1
  rc=$?
  case "$rc" in
    0) say "  ok    ratchet$label - the bar held or rose" ;;
    1) bad "ratchet$label - a document fell below its best"
       grep -E "REGRESSED|was +[0-9]+/" "$log" | head -6 | sed 's/^/        /'
       FAILED=1 ;;
    2) bad "ratchet$label - refused to gate"
       grep -E "refused|CANNOT GATE|No check list" "$log" | head -4 | sed 's/^/        /'
       FAILED=1 ;;
    3) # NOT a failure and NOT a pass. Named, and sent to the policy below.
       say "  gap   ratchet$label - UNMEASURED: nothing fell, something was not asked"
       grep -E "^  (UNMEASURED|STALE|compared|NOT COMPARED)" "$log" | head -3 \
         | sed 's/^/        /'
       # "docx" rather than "" - a bare empty word disappears in $RATCHET_GAP and
       # the gap on the .docx half would then be silently skipped by the policy
       # below, which is the same class of bug as the one this gate is about.
       if [ "$mode" = "--txt" ]; then RATCHET_GAP="$RATCHET_GAP txt"
       else RATCHET_GAP="$RATCHET_GAP docx"; fi ;;
    *) bad "ratchet$label - unexpected exit $rc"
       tail -3 "$log" | sed 's/^/        /'
       FAILED=1 ;;
  esac
  rm -f "$log"
}

ratchet_half "" ""
if txt_live; then ratchet_half "--txt" " --txt"; fi

# ---- 1a. the gap: a waiver is a written decision, not a flag --------------
# The gate never passes --allow-stale itself. If it did, every commit would waive
# its own gap and the flag would become the silent pass it used to be. The waiver
# has to have been written by whoever is asking to commit, with a reason, and
# unmeasured.py decides whether it is good enough - it checks the instrument the
# waiver names, that something was actually compared, that the rows which moved
# were measured by the live instrument, that the gap is not growing, and that it
# has not been carried for more than three commits.
if [ -n "$RATCHET_GAP" ]; then
  for half in $RATCHET_GAP; do
    if [ "$half" = "txt" ]; then mode="--txt"; label=" --txt"; else mode=""; label=""; fi
    LOG2=$(mktemp)
    # shellcheck disable=SC2086
    if python3 "$BENCH/unmeasured.py" $mode >"$LOG2" 2>&1; then
      say "  ok    unmeasured$label - the gap is recorded, bounded and paid for"
      sed -n 's/^  \(gap recorded\|compared \|waivers carried\|reason given\)/        \1/p' "$LOG2"
      WAIVED="$WAIVED $half"
      if [ "$half" = "txt" ]; then TXT_WAIVED=1; else DOCX_WAIVED=1; fi
    else
      bad "unmeasured$label - the gap may not be committed through"
      sed -n '/REFUSED/,$p' "$LOG2" | head -10 | sed 's/^/        /'
      FAILED=1
    fi
    rm -f "$LOG2"
  done
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
#
# Under a waiver RATCHET.json is allowed to stand still, and only under a waiver.
# While any row is counted out of a universe the instrument does not have, ratchet.py
# refuses to write the store at all ("NOTHING WRITTEN") - raising a mark from a
# comparison it could not make is the substitution this whole file was repaired for.
# So demanding a new RATCHET.json on a waived commit would demand the one thing the
# ratchet is right to refuse, and the gate would be red for a reason that is not a
# defect. The evidence that matters in that case is RESULTS.jsonl, and unmeasured.py
# has already proved every row that moved in it was measured by the live instrument.
if [ "$DOCX_WAIVED" -eq 1 ]; then
  EVIDENCE_HERE="BASELINE.md RESULTS.jsonl"
else
  EVIDENCE_HERE="$EVIDENCE"
fi
for f in $EVIDENCE_HERE; do
  if file_changed "$BENCH/$f"; then
    say "  ok    $f changed with it"
  else
    bad "$f is unchanged - the engine moved and the numbers did not"
    FAILED=1
  fi
done

if txt_live; then
  # Same exemption, same reason, on the .txt half.
  if [ "$TXT_WAIVED" -eq 1 ]; then EVIDENCE_TXT_HERE="RESULTS-TXT.jsonl"
  else EVIDENCE_TXT_HERE="$EVIDENCE_TXT"; fi
  for f in $EVIDENCE_TXT_HERE; do
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

if [ -n "$WAIVED" ]; then
  printf 'engine=%s time=%s ratchet=unmeasured-waived waived="%s"\n' \
    "$ENGINE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(echo $WAIVED)" > "$OK_FILE"
else
  printf 'engine=%s time=%s ratchet=pass\n' \
    "$ENGINE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OK_FILE"
fi
say ""
if [ -n "$WAIVED" ]; then
  say "  PASS WITH A RECORDED GAP - engine $ENGINE may be committed"
  say "  The ratchet was NOT asked about some documents; WAIVER.json names which,"
  say "  why, and how many commits the gap has been carried for. It is not closed."
else
  say "  PASS - engine $ENGINE is proven and may be committed"
fi
say "  token: $OK_FILE"
exit 0
