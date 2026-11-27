# The gate was never refusing a change. It was refusing a pod.

**27 Nov 2026, fixer slot 07:22 IST. Measured on a fresh clone of `kavopdf/app` @ `c11b57a8`, engine
`a4d8fca469bba636`.**

## The claim this file corrects

Runs have recorded, for weeks, that an engine change is measured, then reverted, because
`regress.py --check` charges a full corpus re-score that a slot cannot pay for. `pending.py` item 26/33/43
says it in as many words: *"Not implemented here - regress.py and the verifiers are on the do-not-touch list"*.

**That is not what the gate was doing.** On an unmodified HEAD tree the gate refuses with three different
messages, one after another, and not one of them is about the change:

```
1. corpus : could not be built (1)   ->  no corpus PDFs found - run corpus-fetch.sh first
2. (after corpus-fetch.sh, 213 PDFs, 0 missing)
   no java on PATH and no JAVA_HOME  ->  run jdk-fetch.sh
3. (after jdk-fetch.sh)
   041122-Account_Opening_Form.pdf : Caused by: java.lang.ClassNotFoundException: ConvertAll
4. (after libs + aar + stubs + engine compile)
   PASS
```

Every one of those is a missing prerequisite of the pod, not a measurement of the tree. `pod-prep.sh` exists
precisely to install them in that order, and its own header documents the same four failures.

## What was measured this run

```
bash tools/install-gate.sh                 -> timed out at 300 s (it runs pod-prep.sh first)
bash tools/p2w-bench/corpus-fetch.sh       -> 213 PDFs, 212 scored, 0 missing           (~5 s, warm cache)
bash tools/p2w-bench/pod-prep.sh           -> [1..6/6] warm; then converted 53, 79 to go
python3 tools/p2w-bench/corpus-slice.py    -> 53 converted in 242 s, 26 to go
python3 tools/p2w-bench/corpus-slice.py    -> 26 converted in 130 s, DONE, stamp a4d8fca469bba636
python3 tools/p2w-bench/regress.py --check -> PASS, exit 0
```

`regress.py --check` on the finished corpus:

```
  engine fingerprint : a4d8fca469bba636
  scope of the change: docx   (scope.py: scope: docx)
  txt: out of scope - scope.py proved this change cannot move it
  docx: no document worse than baseline
  txt : not re-measured - the tree is the engine the table was measured on (a4d8fca469bba636)
  google-safe : no construct Google ignores has spread
  PASS - nothing got worse in the .docx only, and the table matches this engine.
```

**The whole gate costs 3 tool calls and about 10 minutes of wall clock from cold, and about 13 seconds
once the corpus is warm.** It is not the reason a slot lands nothing. A slot that starts with
`install-gate.sh` and does not allow it 300 s never gets past step 1, and then reports the gate as the
blocker.

## The method this leaves behind

`install-gate.sh` is the first thing a run calls and it cannot finish in one call: it runs `pod-prep.sh`,
which fetches the corpus, the JDK, the PDFBox AAR and compiles the engine, and then converts a corpus
slice. **A run must give it three calls, in this order, and each one under 290 s:**

```
bash tools/p2w-bench/corpus-fetch.sh
bash tools/p2w-bench/pod-prep.sh          # skips what is warm, converts one slice
python3 tools/p2w-bench/corpus-slice.py   # repeat until it prints DONE (53 docs per ~240 s)
```

Only then is `install-gate.sh` (the hook) cheap, because pod-prep is warm. A run that skips this and then
concludes "the gate refuses me" has measured the pod, not the code.

## Two instrument defects found on the way, NOT fixed, with their evidence

Both are recorded as proposals because neither could be A/B measured inside this slot, and a change that
cannot be measured is a guess (charter, non-negotiable 2).

**1. `regress.py:636` mislabels every non-zero-3 return of `google_safe.py` as "no .docx output directory".**
`google_safe.py` returns 3 from two unrelated places: `corpus_dir()` is None (`:207`) *and* the corpus size
does not match the mark (`:299`, "cannot compare: the mark was recorded over N documents"). On a partial
corpus the gate therefore prints a false statement about what happened. The message should carry
`google_safe.py`'s own last stderr line.

**2. A .docx-scoped commit can land with `google_safe.py` not having run.** `regress.py:636-638` treats
rc 3 as a disclosure (`_skipped`) and still exits 0, so the pre-commit hook accepts it. That leaves
non-negotiable 4 — "no construct Google ignores; the gate refuses a commit that spreads one" — unenforced
exactly on the pods where the corpus is incomplete, which is where a construct can spread unseen. It is
disclosed ("CHECKS THAT DID NOT RUN: google-safe"), not enforced. Proposed: fail the gate when
`need_docx` and google-safe returned 3. **Not applied**, because the "before" state (rc 3) could not be
reproduced on this pod without moving the 213-document output directory, and moving corpus output is
against non-negotiable 5's spirit even when it is a move and not a delete.

**What would settle it:** a second fixer run on a cold pod, capturing `regress.py --check` at the moment
`corpus-slice.py` reports "N to go" — that run has the rc-3 state for free.

## Fixed: the corpus cache was keyed on the .txt engine

`corpus-convert.engine_sources()` hashed **every** `.java` in the engine, and the only thing that cache
holds is 213 `.docx`. A one-line edit to `TxtWriter.java` therefore made every `.docx` stale and the next
gate call paid a two-slice, ~10 minute rebuild for a change that cannot reach a `.docx` byte.

**This is the identical defect `regress.py` fixed for the RANKING table on 20 Nov** and wrote down at
`regress.py:60-68` (`DOCX_EXCLUDES = ("TxtWriter.java",)`): the docx path never calls `TxtWriter`;
`DocxWriter.write()` reads the `Result` that `PdfToWord.convert()` built and `TxtWriter.write()` is its only
caller. The table was fixed; the corpus cache was left with it, one layer out.

**Measured, before and after, on this pod** (`app/src/main/java/.../TxtWriter.java` given a one-line comment
and then restored):

| | key after touching `TxtWriter.java` | what happens to the 213 `.docx` |
|:--|:--|:--|
| before | `44e9113125a109fa` | all stale - rebuild, 2 slices, ~10 min |
| after | `d28ca7516c3f9165` | unchanged - cache stays warm |

**Independent cross-check, not the tool I edited:** `regress.engine_fingerprint("docx")` computes
`d28ca7516c3f9165` on the same tree, and `corpus-convert.engine_now()` now returns exactly that. Two tools,
one number. `DocxWriter.java` stays in the key, because `DocxWriter.orderStamps()` reorders `page.blocks`
and `TxtWriter` walks them - the one place a docx-side method can move the `.txt`.

The stamp on disk was **not** rewritten. The 213 `.docx` in the cache were built from the previous engine
(`a4d8fca469bba636`); they are genuinely stale and the next run should rebuild them rather than inherit a
certificate they did not earn.

### Correction to §"What was measured this run", and it matters

While this run was working, the **:10 fixer landed a kept engine change** (`8fb4f503`, `18_displacement`,
"table gap spent as `w:before`"). So the engine moved under the measurement above: the all-`.java`
fingerprint is now `74a152e7d3fb3d26`, not `a4d8fca469bba636`. **The gate PASS at `a4d8fca469bba636` was true
when it was taken and is not the current engine's verdict.** Anyone reading it should re-run
`regress.py --check`; it will need the 213-document rebuild first, which is now three `corpus-slice.py`
calls and about ten minutes.
