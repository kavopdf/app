# TOOLBOX — how to use every tool in this pipeline

One section per tool: the exact command, what it prints, what it returns, what it
writes, and what it must not be used for. Read only the sections your cron needs.

Every flag here is checked against the code by `toolbox_check.py`. If this file and
the code ever disagree, the check fails — a stale interface reference is worse than
none, because it teaches a cron to call something that no longer exists.

Common to every tool below: run from the repository root, and `git push` does not
work in this environment. Commit with `GITHUB_COMMIT_MULTIPLE_FILES`.

---

## verify_google.py — the measurement

**Used by:** baseline. **Not used by:** classifier, fixer (it reads recorded
numbers instead), APK.

```
python3 tools/p2w-bench/verify_google.py <source.pdf> <google-export.pdf> [--json out.json]
python3 tools/p2w-bench/verify_google.py --list-checks
```

Prints one line per document, then one line per failing check:

```
300_prescription_rx.pdf                40/58 FAIL
    01_page_count                source=1        render=2
    20_within_10pt               source=100      render=20
```

`--json out.json` adds every check with its source and render value, plus
`document`, `source_file`, `render_file`, `passed`, `total`, `ok`, `failed`.

`--list-checks` prints every check id, one per line. The count has grown 31, 50, 58, 59 - Use this when you need the
denominator — never write a total from memory.

Exit codes: **0** every check passed, **1** at least one failed, **2** could not run
(a missing or unreadable PDF).

The denominator is whatever `total` the script reports. Never hardcode it.

Deterministic: the same pair twice gives byte-identical output, so a changed result
means the document changed, not the measurement.

---

## record.py — keep the numbers so nobody measures twice

**Used by:** baseline (writes), fixer (reads). **Not used by:** classifier, APK.

```
python3 tools/p2w-bench/record.py res/*.json --round <n> --engine <hash>
python3 tools/p2w-bench/record.py --show <document>
python3 tools/p2w-bench/record.py --show <document> --check <id>
```

Writes `RESULTS.jsonl`, one line per document per round per engine. Re-running the
same document for the same round and engine replaces its line instead of adding a
second one.

`--show` prints what the baseline already measured:

```
round 1  engine 2a68de6  31/58  18 failing
    20_within_10pt             source=100        render=62         FAIL
```

This is how the fixer sees how far off and in which direction, without pushing the
document through Drive again. Exit **0** found, **1** no record.

---


**`--txt`** writes to `RESULTS-TXT.jsonl` instead of `RESULTS.jsonl`, and `--show --txt`
reads that store. The .txt half keeps its own record because a .txt regression and a
.docx regression are fixed by different code in different classes; one file covering both
would make them indistinguishable.

    python3 tools/p2w-bench/record.py --baseline --round <n>
      Rewrite the BASELINE.md row for every document the store has a measurement for this round.
      Every other line is written back exactly as it was - this is a row replacement, not a
      rebuild. A -d engine id is refused: a reverted attempt's scores must never reach the table
      the gate and the ratchet treat as the truth.
      exit 0 with "N row(s) rewritten", or 0 with "every row already matches" (you measured
      nothing new, and the gate will refuse the commit for that reason), or 1 with "the store has
      no row for this round/engine".
      Why it exists: commit-gate.sh demands that BASELINE.md changed when the engine changed, and
      nothing wrote it. The brief used to tell the fixer to hand-edit twenty rows of six columns.

## ratchet.py — the regression rule

**Used by:** all four. Baseline runs it after measuring, classifier runs `--check`,
fixer runs it before committing, APK runs `--check` before publishing.

```
python3 tools/p2w-bench/ratchet.py            # update marks, fail on regression
python3 tools/p2w-bench/ratchet.py --check    # same, but never raise a mark
```

Prints a four-line summary and any regressed documents:

```
ratchet
  documents scored this run : 20 of 208 rows
  high-water marks held     : 20
  new documents, first mark : 0
  REGRESSED: 1 document(s) below their best ever score
      04_stamp_180deg_upside_down        44/58 was 46/58  (-2)
  FAIL - the bar fell
```

Exit **0** the bar held or rose, **1** something fell. It has no third code: with no
BASELINE.md to read there is nothing to compare and it exits 0, which is why a cron must
never treat 0 as proof that measurement happened - check the row count for that.

It holds, per document, the best score ever reached AND the set of failing checks at
that point. Two things count as a regression: the score falling, and a check that
used to pass now failing — even when the score is unchanged. It compares only
checks that existed at both marks, and a mark taken by a smaller verifier does not
bind a larger one. Do not try to out-think it and do not edit `RATCHET.json` by hand.

---


**`--txt`** uses `RATCHET-TXT.json` and takes its scores from `RESULTS-TXT.jsonl` and its
check universe from `verify_txt.py --list-checks`. There is no BASELINE-TXT.md: the .docx
path keeps a table a human also reads, and the .txt path has no reader but this one, so
the store is the truth. Both ratchets must be run - one conversion writes both outputs,
and each can only see its own half.

    python3 tools/p2w-bench/round.py --release-fixer [--force]
      Release the fixer slot. Exit 1 with a refusal when the run is under 25 minutes old and has
      recorded fewer than two attempts - the slot is good for 45 minutes and one attempt takes
      ten, so releasing there hands the rest of the hour to nobody. `--force` releases anyway and
      writes a FORCED line into RUN-LOG.md; use it for a broken build, a blocked Drive or an empty
      class list, and say why in INCIDENTS.md.
      It does not refuse when no class is still OPEN: a finished round must be able to release and
      close, or this check would block the only exit from the fix phase.

## round.py — whose turn it is

**Used by:** all four.

```
python3 tools/p2w-bench/round.py                 # status
python3 tools/p2w-bench/round.py --phase         # prints exactly: measure | classify | fix | done
python3 tools/p2w-bench/round.py --advance       # measure -> classify -> fix
python3 tools/p2w-bench/round.py --close-round   # archive, empty scores, next round or done
python3 tools/p2w-bench/round.py --claim-fixer   # 0 = go, 1 = another run is working
python3 tools/p2w-bench/round.py --release-fixer
python3 tools/p2w-bench/round.py --claim-baseline    / --release-baseline
python3 tools/p2w-bench/round.py --claim-classifier  / --release-classifier
python3 tools/p2w-bench/round.py --apk-status    # 0 = may ship, 1 = no (prints why)
python3 tools/p2w-bench/round.py --mark-apk-shipped <version>
python3 tools/p2w-bench/round.py --force-round <n>   # set the round by hand; recovery only
```

`--phase` prints one bare word. Compare it, do not parse the status output.

Status prints:

```
round 1 of 3   phase: measure
  documents scored : 20 of 208
  open classes     : 0
  next             : baseline runs until 208 of 208 are scored
```

`--close-round` archives `BASELINE.md` as `ROUND-<n>.md`, `ATTEMPTS.json` as
`ATTEMPTS-round-<n>.json`, empties every score, clears the fixer claim and the
shipped mark, and moves the phase. It survives a missing BASELINE.md.

Every cron claims its own slot before working, so an overrun cannot put two runs
of the same cron in the same phase at once - the same ten empty rows measured
twice, and the later commit overwriting the earlier one. The stale window is per
cron, sized to one run: fixer 45 minutes, baseline 45, classifier 20. A run that
dies cannot block the next one, and a live run is never mistaken for a dead one.
Always release the claim when you finish, even on failure.

---

## classify.py — separate and rank the defects

**Used by:** classifier (writes), fixer (reads and records attempts).

```
python3 tools/p2w-bench/classify.py
python3 tools/p2w-bench/classify.py --subclusters "<exact class name>"
python3 tools/p2w-bench/classify.py --attempt "<exact class name>" --moved <n> --total <n>
python3 tools/p2w-bench/classify.py --attempt "<exact class name>" --outcome error
python3 tools/p2w-bench/classify.py --top <n>        # how many classes the table lists
```

Writes `DEFECT-CLASSES.md` on every run. `ATTEMPTS.json` appears only when the first
attempt is recorded with `--attempt` - a plain run does not create it. Prints:

```
documents measured : 20
checks firing      : 35
classes (data-driven): 28
  47_margins                          20 docs  OPEN
  53_embedded_faces                   20 docs  OPEN
```

Classes are named after the check that touches the most documents. There are no
hand-written names, and adding one is a mistake: a friendly label written before
the data was seen sends the fixer after the wrong cause.

A check that fails on almost every document is its own class, because it cannot
discriminate between causes. A class bigger than six checks is re-split at a
stricter threshold until the parts can name one cause each.

`--subclusters` splits one class by the checks its documents also fail:

```
class '47_margins' - 20 documents, 32 outside checks

   16 docs  with 19_worst_dy
    3 docs  with 09_font_names
```

Copy the class name exactly as printed, including the `(+N)` suffix. If it says no
class matches, run `classify.py` first and copy from the output.

The outcome is COMPUTED from `--moved` and `--total`, not chosen:

```
moved 12 of 20 (60%) -> kept        the target now passes on at least half
moved  8 of 20 (40%) -> improved    moved on at least a third; day restarts, up to 3 times
moved  3 of 20 (15%) -> reverted    real progress was not made
```

`--outcome kept` or `--outcome improved` without numbers is refused, and a claim
that disagrees with the numbers is refused and NOT recorded. `--outcome error` is
accepted without numbers, because an attempt that found no root cause has nothing
to count. Limits: one day per class, 24 attempts, 3 requeues.

---


**`--txt`** reads `RESULTS-TXT.jsonl` instead of `BASELINE.md`, so the classes it reports
are the .txt checks `t01` to `t05` rather than the .docx checks `01` to `59`. Run both and
take the largest OPEN class from either; which half you are in decides whether the rest of
the run uses `verify_google.py` with `ratchet.py` or `verify_txt.py` with `ratchet.py --txt`.

## seed.py - every corpus document gets a row, or nothing measures it

    python3 tools/p2w-bench/seed.py --corpus all
    python3 tools/p2w-bench/seed.py --corpus all --dry-run

  BASELINE.md is a hand-built table, and the baseline takes "the first 10 rows whose score
  is empty". A document in the corpus with no row is therefore never chosen, never measured,
  never classified and never fixed - and no gate notices, because measure_gate compares the
  table against the store and both would agree while a document is absent.

  seed.py appends an empty row for every corpus PDF that has none. Idempotent, never touches
  a measured row, never reorders. Exit 1 when the corpus directory is missing or empty: an
  empty directory means the download failed, and seeding from it would look like success.

## patches/ - a fix that was proved but never measured

    tools/p2w-bench/patches/<name>.patch     git apply <file>
    tools/p2w-bench/patches/<name>.md        the reasoning, the numbers, why it was not shipped

  A run that confirms a fix on one document and then cannot run the twenty-document measurement
  saves it here instead of losing it. That is not a failure - the theory is proved, the class
  outcome is not, and the difference is one measurement.

  A CONFIRMED entry in HYPOTHESES.md that names a patch here is the highest-value work available
  to the next run: apply it, measure twenty documents, decide kept/improved/reverted. Do not form
  a rival theory while a proved patch is sitting unmeasured.

## code.py — the part of the engine you need, not the file

    python3 tools/p2w-bench/code.py --outline                 one line per file
    python3 tools/p2w-bench/code.py --outline DocxWriter      every method, with its range
    python3 tools/p2w-bench/code.py --method spacingTw        one method, whole
    python3 tools/p2w-bench/code.py --find flowFromBox -c 8   definition, call site, comments
    python3 tools/p2w-bench/code.py --callers rowLineTw       every line that touches it
    python3 tools/p2w-bench/code.py --file DocxWriter --lines 233-268

  DocxWriter.java is 288,746 bytes and PdfToWord.java is 346,229 - about 1.6 lakh tokens
  between them. Reading either whole ends a run before it starts. The outline of one file
  is 1,644 tokens; one method is 483; a --find is 2 KB and carries the call site and any
  "tried and reverted" comment with it.

  It reads the same source the compiler reads and edits nothing.

## trace.py

    python3 tools/p2w-bench/trace.py --show 40    # the last 40 lines
    python3 tools/p2w-bench/trace.py --clear

  TRACE.md, written by the tools themselves - claim, classify, attempt, ratchet, build,
  commit-gate. It is the only record of what a run actually did: a cron reports succeeded
  or failed and its output is not retrievable, so a run that dies between two steps leaves
  its path here and nowhere else.

  Commit it with the claim and after each step. It is not code, it touches nothing, and it
  cannot break a build - so it is safe to commit at any moment, unlike the engine.

## CLASS-HISTORY.jsonl - a class's own trajectory

    tail -12 tools/p2w-bench/CLASS-HISTORY.jsonl
    grep '"class": "20_within_10pt' tools/p2w-bench/CLASS-HISTORY.jsonl | tail -20

  One line per attempt, appended by classify.py --attempt:

      {"at": "2026-11-13 09:24", "attempt": 15, "class": "20_within_10pt (+4)",
       "outcome": "error", "requeues": 0, "round": 1, "status": "OPEN"}

  DEFECT-CLASSES.md is rewritten every run, so it cannot answer "what was this class six hours
  ago" or "has it been getting better". This can. Twelve lines tell you whether a class is
  converging or stuck, which is the difference between working it and burning it.

## hypothesis.py — what earlier attempts already ruled out

**Used by:** fixer only.

```
python3 tools/p2w-bench/hypothesis.py --show "<exact class name>"
python3 tools/p2w-bench/hypothesis.py --next "<exact class name>"
python3 tools/p2w-bench/hypothesis.py --add "<exact class name>" "<theory>" \
        --result ruled-out|confirmed|untested --evidence "<the numbers>"
```

Writes `HYPOTHESES.md`, one section per class. `--next` prints only the untested
theories; when nothing is left it says so and tells you to form a new one.

Recording the same theory again with a different result updates it in place, so a theory
first written as UNTESTED can later become RULED OUT without leaving a stale line that
`--next` keeps offering. Recording the same result twice changes nothing.

RULED OUT entries each cost a calibration run — do not re-test one without new evidence, and if you do, say
what changed.

---

## calibrate.py — is this a renderer limit or an engine bug?

**Used by:** fixer only.

Builds the smallest docx that isolates one variable in three variants, sends each
through Drive, and measures what comes back. This is how you tell "Google will not
do this" from "our engine writes the wrong thing". It is not optional before an
`unfixable` verdict — 89 rows were once closed on an untested assumption and all
had to be reopened.

---

## google-gate.sh — how much was measured on this engine

**Used by:** APK.

```
bash tools/p2w-bench/google-gate.sh
```

Prints the engine hash, how many documents are in the table, how many were measured
at all, and how many on the current engine. Exit **0** pass, **1** fail.

If it reports nothing measured on the current engine, say so plainly: the APK is
then unverified by Google. Do not quietly publish.

---

## retry.sh — run a command, and decide whether retrying can help

**Used by:** all four crons, for any command that talks to the network.

```
bash tools/retry.sh -- <command...>
bash tools/retry.sh --tries 4 -- <command...>
bash tools/retry.sh --classify "<the error text>"
bash tools/retry.sh --quiet -- <command...>
```

Classifies the failure before retrying anything:

```
transient    rate limit, 429, 502/503/504, connection reset, timeout
             wait 5s, 15s, 45s. Three tries.
permanent    bad credentials, 401, 404, "Resource not accessible", no space
             stop at once. Retrying a missing permission just costs two minutes.
already-done "destination path already exists" - the state you wanted is the state
             you have. Exit 0 and continue.
unknown      neither pattern matched. One retry, then stop.
```

`--classify` prints the class for a piece of error text and exits 0, so a cron can
ask which of the four it is instead of guessing.

Exit 0 means the command succeeded or was already done. Any other code is the
command's own, after the last attempt.

The backoff is capped at 65 seconds in total because bash stops at 300 seconds in
this environment. Anything longer is the next scheduled run's job.

**Never wrap a write in this without a way to check whether the first attempt
landed.** A release or an upload that failed to answer may have succeeded, and the
retry then does the work twice. See RETRY.md.

## docnames.py — the exact documents a run measured, for the commit message

**Used by:** baseline, before every commit.

```
python3 tools/p2w-bench/docnames.py             # comma-separated, ready to paste
python3 tools/p2w-bench/docnames.py --count     # just how many
python3 tools/p2w-bench/docnames.py --long      # one per line, for reading
python3 tools/p2w-bench/docnames.py --since <rev>   # compare against another commit
```

Reads BASELINE.md, compares it with the same file at HEAD, and prints every document
whose row changed. Always exits 0 - a commit message that cannot be generated is not a
reason to stop a measurement run. Prints "no document changed" when nothing did.

It exists because a range is a guess dressed as a summary. On 11 Nov the baseline wrote
"(375-382)" for a batch of five: 375_attendance_register, 37_font_not_embedded_substitution,
380_runbook_terminal_output, 381_incident_report_timeline, 382_architecture_diagram. The
corpus is not contiguous - 37_font_... sits inside that range, and 376 to 379 are not in
the corpus at all. The commit log is the only record of what was measured, so the list is
read from the file rather than remembered.

## txt_gap.py — documents that have a .docx score but no .txt score

**Used by:** baseline, before STEP 3b and before it advances the phase.

```
python3 tools/p2w-bench/txt_gap.py --count        # how many are missing
python3 tools/p2w-bench/txt_gap.py --list 10      # the first ten, one per line
python3 tools/p2w-bench/txt_gap.py --list 10 --all   # every one, ignoring the limit
```

Reads RESULTS.jsonl and RESULTS-TXT.jsonl, and prints the documents in the first store
and not the second. A store that does not exist is treated as an empty one, so on a
fresh corpus this prints 130 rather than failing. Always exits 0 - an empty gap is a
result, not a failure.

It exists because the .txt half wrote its verdict into a directory that did not exist,
so the 130 documents measured before that was fixed have a .docx row and no .txt row.
The baseline takes the first rows whose SCORE cell is empty and never revisits a filled
one, so without something that points at the hole those documents would never get a .txt
at all - and round 2's .txt ratchet would have nothing to compare them against.

## verify_txt.py — does the .txt describe the same document as the source PDF?

**Used by:** the fixer, on the .txt half of the tool. Separate from verify_google.py,
which measures the .docx half; neither can hide a regression in the other.

```
python3 tools/p2w-bench/verify_txt.py <source.pdf> <output.txt>
python3 tools/p2w-bench/verify_txt.py <source.pdf> <output.txt> --json out.json
python3 tools/p2w-bench/verify_txt.py --list-checks
```

Exit 0 every check passed, 1 at least one failed, 2 could not run.

Five checks, covering the four things a .txt can actually carry:

| check | what it asks |
|---|---|
| t01_word_accuracy | the source's words are all there (>= 98%) |
| t02_position | a line's x survives as its leading spaces (>= 90% within 2 chars) |
| t03_symbols | every non-ASCII character in the source is in the .txt |
| t04_structure | the page drew N rows, the .txt has about N lines (<= 1.5x) |
| t05_completeness | a PDF with text produces a .txt with text |

It does not measure fonts or colours. A .txt has neither, and a number for them would
mean nothing.

Sample real output:

```
372_timesheet_grid.txt                   4/5 FAIL
    t04_structure              source=12         txt=68
```

That is the whole point of the check: the page drew twelve rows, the .txt has sixty-eight
lines, because every table cell went on a line of its own. A 17-row attendance register
becomes 459 lines. Half the corpus is over 1.8x.

## test_txt_checks.py — does each txt check fire, and stay quiet?

**Used by:** anyone changing verify_txt.py.

```
python3 tools/p2w-bench/test_txt_checks.py        summary
python3 tools/p2w-bench/test_txt_checks.py -v     every case
```

Seven cases, each changing exactly one thing, so a check that fires can only be the one
that was meant to. A check that never fires is decoration; a check that always fires
condemns every document and hides the real defect behind its noise.

## commit-gate.sh — an engine change may not be committed without its evidence

**Used by:** fixer, before every commit.

```
bash tools/commit-gate.sh            # 0 = commit, 1 = do not
bash tools/commit-gate.sh --status   # report only, changes nothing
```

Exits 0 immediately when the engine did not change - there is nothing to prove.
When it did, three things are required and the gate refuses on any of them:

```
ratchet.py exits 0                     no document fell
precommit.sh --no-corpus exits 0       it builds, the guards pass
BASELINE.md, RESULTS.jsonl, RATCHET.json changed in the same working tree
```

The third is the one that matters. "I ran the ratchet" is a claim;
"RATCHET.json changed with the engine" is evidence, and evidence cannot be
misremembered. On pass it writes `.p2w-gate-ok` with the engine hash and the time.

A CI job re-checks the same thing on every push: an engine change whose commit
does not also touch those files turns the build red, so it can never ship.

**The .txt half is gated too**, once `RESULTS-TXT.jsonl` exists: the .txt ratchet (see the
ratchet.py section for how to ask for that store) must exit 0, and `RESULTS-TXT.jsonl` and
`RATCHET-TXT.json` must both have moved with the engine. Before the first .txt measurement
there is no store to move, so the gate reports "not measured yet - not gated" and demands
nothing. `--status` shows which half is live.

## precommit.sh — build and sanity before any commit

**Used by:** fixer, APK.

```
bash tools/precommit.sh --no-corpus     # fast; what the crons use
bash tools/precommit.sh                 # also runs the corpus
bash tools/precommit.sh --all           # every tier, including the corpus
```

Exit **0** pass, non-zero fail. Must exit 0 before a commit is allowed.

---

## reset_round.py — back to round 1 with nothing measured

**Used by:** a human, or the agent on request. Never by a cron.

```
python3 tools/p2w-bench/reset_round.py          # dry run, changes nothing
python3 tools/p2w-bench/reset_round.py --yes    # do it
```

Archives everything under `archive/reset-<timestamp>/` first, then clears
`BASELINE.md` scores, `RATCHET.json`, `ATTEMPTS.json`, `RESULTS.jsonl`, regenerates
`DEFECT-CLASSES.md` and sets `ROUND.json` to round 1, phase measure. Then it re-counts
and exits **1** if anything survived. A reset is a new attempt, not a deletion.

---

## The files these tools share

| File | Written by | Read by | Meaning |
|---|---|---|---|
| `BASELINE.md` | baseline, fixer | all | one row per document: score, verdict, failing checks, engine, date |
| `RATCHET.json` | ratchet.py | ratchet.py | best ever score + the failing set at that point |
| `RESULTS.jsonl` | record.py | record.py | per-check source vs render, per round, per engine |
| `ROUND.json` | round.py | all | round, phase, fixer claim, shipped mark |
| `DEFECT-CLASSES.md` | classify.py | fixer | ranked classes with status |
| `ATTEMPTS.json` | classify.py | fixer | attempts, requeues, outcomes per class |
| `HYPOTHESES.md` | hypothesis.py | fixer | what was ruled out, per class |
| `REMAINING-DEFECTS.md` | fixer | human | what is genuinely unfixable, with numbers |
| `ROUND-<n>.md` | round.py | human | the archived scores of a finished round |

`BASELINE.md` rows are exactly six columns. Never rebuild the file from a fetched
string — that deleted 119 rows on 10 Nov. Edit it in the local clone.
