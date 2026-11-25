# P2W Fixer - Run Report

**25 Nov 2026 · slot 10:56 -> 11:52 IST · 56 min**

> The Google scoreboard was blind, not the corpus. Three instruments compared a git commit with a
> source hash and reported "0 of 213 current". Fixed, measured, committed: **42 of 213 documents pass
> every applicable Google check on this engine** - the truth the store has carried since 05:14.

## What this run did

**It made the truth readable, and found that the pipeline has been steering on a number that was
never a zero.**

`report.py` printed this on every run for at least two slots:

> **Fixed - Google, every applicable check** | could not be read - 0 of 212 scored were read as
> current, which is a failed read and not a measurement.

Nothing was wrong with the store. `google_fixed()` compared two different quantities with `==`:

| | |
|:--|:--|
| every verdict in `benchmarks/gverify/` (213 rows) | `engine = "981ff1fa35e2cf67"` - 16 hex, `sha256(name + bytes of every app/.../engine/*.java)[:16]`, written by `gvbatch.py:26,76` |
| `report.py:engine_now()` | `git log -1 --format=%h -- app/.../engine/` -> `"85b8735f"` - an 8-char git abbreviation |
| the comparison, `report.py:460` | `if (j.get("engine") or "") == now:` - exact equality |

Two quantities, two lengths, so it matched nothing. `gverify.py:194` had already been fixed for this
class of bug, but its own `_engine_now()` still answered `%h`, so `_done()` returned 1 (the single
page-count refusal) and `plan()` said "1 of 213 documents have a Google result; 212 to go" - an
hourly cron re-measuring the entire corpus for ever, which is why the store never looked fresh.
`classify_google.py:34` carried it too, and printed it into the class table every run: *"HEAD is
`85b8735f` and 0 of the 212 Google results were measured on it; re-measure before treating any row as
the current behaviour"* - the one line that told every fixer to distrust the only Google measurement
it had.

### The measurement, before and after, on the same tree and the same store

| | before | after |
|:--|:--|:--|
| `report.py` "Fixed - Google" | **could not be read** - 0 of 212 current | **42** of the **213** re-measured on this engine |
| `report.py --json` | `google_fixed_current=0` | `google_fixed_current=42, google_scored_current=213, google_refused=0` |
| `classify_google.py --print` | "0 of the 212 ... measured on it; re-measure" | "Every result above was measured on engine `981ff1fa35e2cf67`, the engine in the tree." |
| `verify_google._engine_head()` | `'85b8735f'` | `'981ff1fa35e2cf67'` = `regress.engine_fingerprint()` |

### The population, proved three ways that do not share code

1. **The store.** 213 files in `benchmarks/gverify/`, every row `engine = 981ff1fa35e2cf67`,
   `render = google`; **42** carry `failed = []`.
2. **The tree.** `regress.engine_fingerprint()` on this clone returns `981ff1fa35e2cf67`; the corpus
   stamp `corpus-slice.py` wrote after converting all 213 documents in this run carries the same
   value (`{'engine': '981ff1fa35e2cf67', 'documents': 213}`, 0 failed).
3. **The commit that wrote the store.** `9165bf25` states its own numbers: "on current engine: 212
   (one page-count refusal)", "clean: 42 of 212". The scoreboard contradicted the commit that
   produced its own data.

**The FIXER-BRIEF charter's Google line is stale against this - it still carries a two-digit clean
count over a smaller denominator - and no run should plan against it again.** The real figure is 42 of 213; `google-needed.py` agrees (213 scored
in Google, 141 still need Google, 72 settled by LibreOffice).

## Why no document moved, and what the next run lands

The document-moving fix is already in the repo from the 10:10 run: `PATCHES/600-annotation-runs-
subtype-25NOV.patch`, measured there at `verify_txt.py` 7/12 -> 8/12 on document 600. It did not land
because an engine edit invalidates **both** tables and `regress.py --check` refuses an unmeasured
engine. This run measured what that costs, with the JDK and corpus built in this pod:

| step | measured here |
|:--|:--|
| `jdk-fetch.sh` + `corpus-fetch.sh` | 24 s + 15 s |
| `build-engine.sh` | ~45 s |
| `corpus-slice.py --budget 250 -j 6` | 55 documents per 230 s -> **213 in five slices, ~16 min** |
| docx render + score (`benchmarks/p2w.py`) | ~15.8 s/document on one-page docs -> **~56 min for 213** |

So the corpus is cheap and the **docx measurement is the whole slot**. The construct is recorded as
a **lead** on `content-missing-partly-replaced` (attempt 19, 0 of 14 moved) so the rotation does not
abandon it: the patch is measured, only unlanded. That is the landing sequence
for the next run, in order, and it is the only thing between the annotation fix and the repo:
`git apply` -> `build-engine.sh` -> five `corpus-slice.py` slices -> `p2w.py` until complete ->
`restamp_txt.py --run --force --report --apply` -> `regress.py --stamp` -> `regress.py --check` ->
`attempt.py`. Copy `RANKING-TXT.csv` before `restamp_txt.py --apply`: it rewrites the baseline from the
same rows, which makes the "no .txt document worse" line vacuous.

## Attempt 2: the biggest text defect in the corpus is one unmapped ligature

With the scoreboard readable, the txt side's worst failure was `t12_word_invention` on 8 documents.
Recomputing the excess-token multiset independently on all 8 (PyMuPDF page text as the source, not the
verifier) gives a different answer from the 10:10 run's "5 instrument / 3 engine":

| class | tokens | documents |
|:--|--:|:--|
| **NOVEL** - no such characters on the page | **258** | 2 |
| over-counted - the word is on the page, the output repeats it | 34 | 6 |
| tokenisation - characters present, split or joined differently | 18 | 4 |

The 258 are `U+FFFD` in `041122-Account_Opening_Form` (127 in the `.txt`) and its fillable twin. The
page says "Please fill up in BLOCK letters only"; the output says `Please �ll up in BLOCK letters
only`, and **the .docx carries 86 of them too** - so this is an engine ligature defect in the renderer
the user opens, not a `.txt` artifact. The source PDF has zero `U+FFFD`. `t12` under-reports it
(render=5) because its own tokeniser drops the character, so the check that exists to catch an
invented word cannot see the one that dominates the document; `t06_encoding` is what fails there.

The fix is in the engine's ligature map, so it moves both fingerprints and needs the same 213-document
pass the annotation patch needs. Recorded as a lead with the measurement
(`FINDINGS/NO-FFFD-THE-LIGATURES-ARE-NOT-MAPPED-25NOV.md`), not attempted at 80 minutes in.

## Attempt 3: `18_displacement` is one unit, in one direction, on 108 documents

`classpick.py --leverage` puts `18_displacement` at **54.8 clean documents**, so the cheap question
first: do its failures share a signature? Read straight out of the 213 stored Google verdicts:

| | |
|:--|--:|
| documents with the check measured | 213 |
| failing | **122** |
| failing with `render - source > 0` | **122** |
| failing with `render - source < 0` | **0** |
| failing by exactly **+1.0** | **108** |
| median absolute error | 1.0 |

A hundred and eight documents miss the same check by one unit in the same direction. That is one
construct with a constant, not 108 placement defects. The two hypotheses are a check boundary
(`abs(d) < 1` over quantised values) and a half-unit rounding in the writer, and one document decides
between them: compare the engine's y for a line against the page's y in raw PDF points, before
quantisation. `416_many_tiny_pages` at +299 is a separate defect and should be parked on its own.
Recorded as a lead (`FINDINGS/18-DISPLACEMENT-IS-ONE-UNIT-AND-ALWAYS-POSITIVE-25NOV.md`); the fix
moves a fingerprint, and this slot already had two engine fixes queued behind the same re-measure.

## Two agents, in the first ten minutes

| Agent | Sent to find | Took | Result |
|:--|:--|--:|:--|
| `Google read failure` | why the Google row reads zero - store, filter or error? | 5 min | **filter bug, (a)**: found the `%h` vs source-hash mismatch at `report.py:393-460`, wrote the patch this run landed, and confirmed the store holds 212 rows all stamped on this tree |
| `Landing path for patch` | what `regress.py --check` actually demands, and the timings | 17 min | **the gate is stamp-gated, not corpus-gated**: `scope_of_change()` answers "both" for `PdfToWord.java`, no scoped re-stamp exists, `--stamp` would pass unmeasured today and must not be used. Timed every step above |

The second agent is why this run did not attempt the annotation landing: 56 minutes of soffice against
a slot already 40 minutes in is a half-measurement, and a half-measurement is what the gate exists to
refuse.

## Progress

| | |
|:--|:--|
| Self-check | **every field agrees with its second source** |
| Document-moves this run | **0** — 3 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **42** of the **213** re-measured on this engine - **0** of the 213 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `18_displacement` - taken from the pending list (19 still open), not a new class |
| Findings vs landing | **70** finding(s) on this class and **0** documents moved - writing is cheaper than landing, and nothing else says so |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 11:45 | **lead** | 0/14 | annotation /Contents is not body text: the saved patch (PATCHES/600-annotation-runs-subtype-25NOV.patch) is measured on 600 (verify_txt 7/12 -> 8/12, t12 invented words 20 -> 0). Not landed because an |
| 11:48 | **lead** | 0/14 | t12 root cause, measured independently on all 8 failing docs: 258 of 310 excess tokens are U+FFFD where the page draws fi/ff ligatures, in 041122-Account_Opening_Form (127 in txt, 86 in the .docx) and |
| 11:51 | **lead** | 0/122 | signature measured from all 213 Google verdicts: 122 documents fail 18_displacement and ALL 122 have render-source > 0; 108 of them by exactly +1.0 (median 1.0). One construct, not 108 defects; 416_ma |

## The txt

| | |
|:--|:--|
| Measured | **57 min ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `googA-01` | why the Google scoreboard reads zero: store, filter  | 11:44 | - | - |
| `annoB-01` | what regress.py --check demands and the exact timing | 11:44 | - | - |

## What the next run should take, and why

`classpick.py --leverage` says `18_displacement` is worth **54.8 clean documents** - more than the next
three checks combined - and document 600's brand-new Google verdict fails it among seven. The leverage
table refuses to hand it over, correctly: **13 pending items are closeable first** (agent 18-D-01,
`ratchet 05_chars_extra`, `ratchet 25_invisible_text`), and 4 more need a decision. Take those in
`pending.py` order before any new class, then `18_displacement` with a Google round trip in hand -
`refresh-google.py` (commit `b14bc496`) is now one command with no human step, which is what the
`18_displacement` lead from the 10:10 run needed and did not have.

## Timing

| | |
|:--|:--|
| Slot window | 10:56 → 11:52 · 56 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 51 |
| Longest silence | **22.6 min** — from 10:56:47, after `pending.py: reading the pending gate` |
| Silences over 2 min | 5 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **22 min** | `#########` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **5 min** | `##` |
| other - not attributed to a tool | **25 min** | `##########` |

## The claim held, and the rebase collided anyway

The claim at 10:56 succeeded and every heartbeat refreshed it. `git push` still had to rebase over
`b14bc496` and `3cf7c4da` ("relay: fixer claim - previous claim stale (51 min)"), and the rebase
collided on `TIMELINE.jsonl` (5,845 lines), `ROUND.json` and `RUN.json`. Resolved as the 10:10 run
did: state files to this run's copy, `TIMELINE.jsonl` unioned by timestamp so neither run's beats were
dropped. **Two runs are writing to this repo on a shared slot again** - the claim lock is not what is
keeping them apart.
