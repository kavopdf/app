#!/usr/bin/env bash
# txt-only-commit-gate.sh - the minimal ordered procedure that makes a TxtWriter-only
# engine change committable through tools/p2w-bench/regress.py --check (the pre-commit hook).
#
# Every step below is a command that exists in the repo, with the flags the code requires.
# Nothing here re-measures the .docx (benchmarks/RANKING.csv) - the code proves that is not
# needed for a TxtWriter change (regress.py:70 DOCX_EXCLUDES, corpus-convert.py:134).
#
# USAGE:  bash txt-only-commit-gate.sh            # run from the repo root, in order, top to bottom
# Each block prints what it should print. Stop at the first non-zero exit.
#
# Time on a 2-core pod, from the code's own numbers:
#   pod-prep (corpus fetch + jdk + libs + engine javac)   ~6 min cold, seconds warm
#   corpus-slice, 213 documents, 4.5 s/doc at 4 workers   ~16 min = 4 slices of 240 s
#   restamp_txt --run --force over 213-214 documents      47 s (BLOCKERS.md:281)
#   regress.py --check, warm corpus                       ~12 s
# TOTAL, cold pod, txt-only change                      ~25 min
# The .docx half (gate.py / p2w.py measure pass) is NOT run: ~54 min saved.

set -uo pipefail
cd "$(dirname "$0")" 2>/dev/null || true
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

say() { printf '\n=== %s\n' "$*"; }

# ---------------------------------------------------------------- 0. scope, before anything
# Proves the change is txt-only BY METHOD (scope.py:37-71). If this prints "BOTH formats",
# stop: the change is not txt-scoped and the .docx half really is required.
say "0. scope"
python3 tools/p2w-bench/scope.py
# EXPECT:
#   scope: txt
#     TxtWriter.write -> txt
#   regress.py must therefore check: txt
# If it prints "TxtWriter.java: change in an unrecognised method -> both (cannot scope)":
# your edit landed in a method scope.py's METHOD_FORMAT table does not know (pageOrder,
# rtrim, cellLeft, column, ...). Either move the change into write()/appendTable()/appendPara(),
# or add the method to the table - otherwise the gate demands the 54-minute .docx pass.

# ---------------------------------------------------------------- 1. prerequisites
# corpus (213 PDFs) -> jdk -> libs -> aar -> stubs -> engine. Idempotent; each step prints
# "skipped (warm)" when already done.
say "1. pod-prep (corpus, jdk, libs, aar, stubs, engine)"
bash tools/p2w-bench/pod-prep.sh
# EXPECT: "pod-prep: [6/6] engine  <N> engine sources + ConvertAll + ConvertOne compiled into out/"

# ---------------------------------------------------------------- 2. what is left to convert
say "2. corpus status"
python3 tools/p2w-bench/corpus-slice.py --status
# EXPECT (cold):  corpus PDFs : 213 / converted : 0 / to go : 213 / stamp : none
# EXPECT (warm):  converted : 213 / to go : 0 / stamp : {'engine': '<docx fp>', 'documents': 213, ...}

# ---------------------------------------------------------------- 3. build the corpus cache
# This writes BOTH formats into /scratch/work/p2w/out via ConvertAll on a one-file shard
# (corpus-slice.py:197-199 -> corpus-convert.py:196-230), and writes a per-document key naming
# the docx engine fingerprint + the PDF's content hash (corpus-convert.py:276-287).
# It converts ONLY documents whose .docx is not fresh for THIS docx fingerprint
# (corpus-slice.py:117 -> corpus-convert.py:289-318) - and TxtWriter.java is excluded from that
# fingerprint, so a warm pod converts NOTHING here and its .txt files stay stale. That is why
# step 3 is mandatory after a TxtWriter change on a warm pod only if the .txt is missing; the
# .txt rebuild is step 3b.
say "3. corpus-slice (repeat until DONE)"
for i in 1 2 3 4 5; do
  python3 tools/p2w-bench/corpus-slice.py --budget 240 -j 4
  rc=$?
  [ $rc -ne 0 ] && { echo "corpus-slice failed ($rc) - a document did not convert"; exit $rc; }
  out=$(python3 tools/p2w-bench/corpus-slice.py --status | sed -n 's/.*to go *: *//p')
  [ "${out:-1}" = "0" ] && break
done
# EXPECT per slice: "  <N> to go, converting 53 this slice (4 workers, 240 s budget)"
#                   "  53 converted, 0 failed in <240> s"
#                   "  <N-53> to go - run this again"
# EXPECT final:     "  DONE - 213 documents converted, stamp written for engine <docx fp>"
#                   (write_stamp -> /scratch/work/p2w/.stamp, corpus-slice.py:231)

# ---------------------------------------------------------------- 3b. rebuild the .txt ONLY if
# corpus-slice converted nothing (warm pod, .txt already stale from the TxtWriter edit).
# ConvertOne is the per-document, measurement-grade harness; it always writes the .docx too
# (ConvertOne.java:38-40), there is no per-document txt-only switch - only ConvertAll has
# -Dp2w.noDocx=true (ConvertAll.java:72-76), and ConvertAll batches, which is what
# p2w.py:1400-1410 measured as unreproducible. Cost is dominated by PdfToWord.convert(), so the
# .docx write you cannot skip is a small fraction of it.
say "3b. txt-only rebuild (only when step 3 printed DONE with nothing converted)"
# cp benchmarks/p2w.py /scratch/work/
# P2W_ENGINE_SRC="$ROOT" python3 /scratch/work/p2w.py --force --budget 250
#   EXPECT: "engine -- building from $ROOT" / "engine -- local tree, not syncing to origin"
#           "docx <n>/213 -- converting <m>"   (repeat the same command until it converts 0)
#   WARNING: p2w.py writes into the same /scratch/work/p2w/out and writes NO .keys, so the next
#   corpus-slice call re-converts all 213 (16 min) and rewrites the .txt you are about to score.
#   Prefer step 3 alone. Do NOT run p2w.py after the engine change is committed:
#   _invalidate_if_engine_changed() does `rm -rf DOCX` when the commit hash moves (p2w.py:1505-1516).

# ---------------------------------------------------------------- 4. score the .txt
# --force re-scores every document; without it restamp re-scores only .txt whose size/mtime
# changed since its row was written (restamp_txt.py:150-172). 213 scored in 47 s.
say "4a. restamp --run --force"
python3 tools/p2w-bench/restamp_txt.py --run --force --budget 260
# EXPECT: "  already scored: <n> | to do: <m>"  then  "  scored <m> this call in <47>s"
# If it prints "refused: 0 pdf in /scratch/work/p2w/corpus, 0 .txt in /scratch/work/p2w/out"
# then step 1/3 did not run (ensure_inputs, restamp_txt.py:114-136).

say "4b. restamp --report   (read this before publishing)"
python3 tools/p2w-bench/restamp_txt.py --report
# EXPECT: "  <n> scored | <a> documents newly clean, <b> newly failing, <c> unchanged"
# b > 0 means the change regressed documents: the gate will refuse at step 6. Revert.

say "4c. restamp --apply   (writes the table the gate reads)"
python3 tools/p2w-bench/restamp_txt.py --apply
# EXPECT: "  wrote RANKING-TXT.csv (<n> rows)"
#         "  wrote RANKING-TXT-BASELINE.csv (<n> rows)"
#         "  wrote STATE-TXT.json (engine <full fp>)"
#         "  <clean> of <n> clean (<pct>%)"
# NOTE: --apply overwrites the BASELINE with the same rows (restamp_txt.py:277), so after this
# the txt ratchet can only refuse a DELETED row, never a worsened one. That is the tool's
# behaviour, not a mistake in this script - keep the pre-apply copy if you want the floor:
#   git diff --stat tools/p2w-bench/txt/RANKING-TXT-BASELINE.csv
# The gate reads tools/p2w-bench/txt/RANKING-TXT.csv (regress.py:44). The top-level
# tools/p2w-bench/RANKING-TXT.csv is stale and read by nothing except report.py's fallback
# (report.py:1156) - do not "regenerate" it.

# ---------------------------------------------------------------- 5. stamp the txt fingerprint
say "5. regress.py --stamp"
python3 tools/p2w-bench/regress.py --stamp
# EXPECT: "  stamped txt to engine <new full fp>"
# and tools/p2w-bench/txt/ENGINE-STAMP.json now holds {"txt": "<new fp>", "docx": "<unchanged>"}.
# IT CAN REFUSE (regress.py:426-465):
#   "REFUSED to stamp: a stamp says a table was measured on this engine, and it was not."
#   "  txt: tools/p2w-bench/txt/RANKING-TXT.csv is older than the last engine change"
# That happens when the last COMMIT touching RANKING-TXT.csv is older than the last commit
# touching app/src/.../engine/ (_newer_than_engine, regress.py:373-383). The only other evidence
# the code accepts is benchmarks/STATE.json with layers.measurement.complete and
# engine == "<head>+<sha1 of the engine diff>[:10]" (_measured_on_this_tree, regress.py:386-423),
# which only benchmarks/gate.py writes (gate.py:219-231) - and gate.py is the 54-minute .docx
# measurement. That is the ONE genuinely unavoidable fork in this procedure; see the report.

# ---------------------------------------------------------------- 6. the gate the hook runs
say "6. regress.py --check"
python3 tools/p2w-bench/regress.py --check
# EXPECT (pass):
#   engine fingerprint : <new full fp>
#   scope of the change: txt   (scope.py: txt)
#   docx: out of scope - scope.py proved this change cannot move it
#   docx: not re-measured - the tree is the engine the table was measured on (<docx fp>)
#   txt : no document worse than baseline
#   corpus : ... / google-safe : no construct Google ignores has spread
#   PASS - nothing got worse in the .txt only, and the table matches this engine.
# The corpus-slice call inside the gate (regress.py:654-656) must print "DONE ... stamp written"
# with nothing converted, or this PASS describes a corpus it rebuilt while checking.

# ---------------------------------------------------------------- 7. optional, not prerequisites
say "7. advisory gates (not called by the hook)"
python3 tools/p2w-bench/txt_gate.py --gate        # refuses if benchmarks/RANKING.csv moved
python3 tools/p2w-bench/measure_gate.py           # docx measure-phase report; READY at HEAD
# EXPECT txt_gate:   "  txt: <n> scored | <c> clean (<pct>%) | <f> failing" / "docx untouched: ..."
# EXPECT measure_gate: "docx   213/213 scored, 1 exempt, 0 blocking, 212 expected"
#                      "engine docx <fp>, tree <fp>" / "READY - every document measured"

# ---------------------------------------------------------------- 8. commit
say "8. commit (hook re-runs step 6)"
git add app/src/main/java/com/kavopdf/app/engine/TxtWriter.java \
        tools/p2w-bench/txt/RANKING-TXT.csv \
        tools/p2w-bench/txt/RANKING-TXT-BASELINE.csv \
        tools/p2w-bench/txt/STATE-TXT.json \
        tools/p2w-bench/txt/ENGINE-STAMP.json
git commit -m "TxtWriter: <what changed>; txt restamped on <fp>, docx out of scope"
