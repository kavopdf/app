# SETTLED — decided, measured, and not to be re-opened

Every line here cost a run. Read this before you form a theory, so you do not pay for it twice.
Nothing in this file needs re-testing; if you think one is wrong, measure it and say so, but say what
changed.

## The baseline is `ead0d0e` plus the DeviceGray fix. Compare against THAT.

`benchmarks/RANKING.csv` is no longer `ead0d0e`'s output. It carries the fix from 11:56 that made
`415_inline_images` go 89.04 -> 0.00, and the corpus ratchet that proved it across 212 documents.

**So do not judge a candidate commit or patch against the current `RANKING.csv`.** A commit made
before that fix produces 89.04 for 415 and will look like a regression when it is only older. Judge
against `ead0d0e`'s own output. This cost a wrong verdict on 18 Nov before it was caught.

## Install scipy before you measure anything

Without scipy, `edt()` takes the 40-mask fallback and one page costs 150 seconds instead of 2. A
one-page document measured in 156 s; seven documents measured in 12 s with scipy present. Every
verification attempt that "timed out" on 18 Nov was a missing package, not a broken tool.

    pip install scipy

## The 29 patches are decided. Do not retry any of them.

    23  cannot be applied - written against an engine state that no longer exists, and their class
        labels are check ids the live classification has none of. `git apply` refuses them, which is
        the correct outcome.
     1  table-spacer-before-not-line       neutral - 0 better, 0 worse on 6 table documents
     4  REJECTED - each breaks a document that works today:
            run-size-from-sizePt-not-Tf       392_statistical_console_output  1.61 -> 13.94
            ruled-band-by-overlap-not-centre  392_statistical_console_output  1.61 -> 13.94
            wrap-charge-gated-1.04            76_devanagari_table             7.91 -> 54.99
            wrap-charge-face-aware            76_devanagari_table             7.91 -> 54.99

`PATCH-AUDIT.md` has the measurement for every one. The files stay in `patches/` because the mechanism
each tried is written in its diff - read it, do not apply it.

**ONE IDEA WORTH CARRYING FORWARD.** `run-size-from-sizePt-not-Tf` takes `360_restaurant_menu` from
**34.43 to 1.31** - a 96 % improvement, the largest single-document gain measured on this corpus - and
in the same breath takes `392_statistical_console_output` from 1.61 to 13.94. The mechanism is real
and aimed at the right thing; it is too broad. A version gated on the case it fixes, rather than
applied to every run, is the best single change available. That is new work, not a patch to apply.

## The four commits after the baseline are decided. Do not re-verify.

    232f622  15 documents: 0 better, 0 worse. The .docx bytes differ; the scores do not.
    5e0af50  claim "041122 10 pages -> 9, p7 73.99 -> 0.00" does NOT reproduce: ead0d0e already
             gives 9 pages and already scores 98.65.
    3232601  claim "411_nested_xobject 48.64 -> 0.00" does NOT reproduce: ead0d0e scores it 31.05.
    0554e8c  8 documents: 0 better, 0 worse.

Their claims were measured against an engine carrying other changes. Against the baseline the pipeline
accepts, none of them adds anything.

## Three files describe a pipeline that no longer runs. Do not read them.

`tools/p2w-bench/BASELINE.md`, `tools/p2w-bench/DEFECT-CLASSES.md` and `tools/p2w-bench/INSTRUMENT.md`
are the retired check-id pipeline. They carry plausible-looking tables of documents and scores that are
a year of history, not current state. `round.py` reads `benchmarks/DEFECT-CLASSES.md` and nothing else.
`RETIRED.md` says what replaced each.

## Two tools now do work you might otherwise do by hand

`attempt.py` runs `classrow.py --write` after every attempt, so a document whose share@5 falls below
5.0 flips to FIXED without anyone remembering to do it. Before 18 Nov nothing called classrow, and a
fixed document stayed OPEN for ever - which means the round could never close.

`screen.py --class "<name>"` measures only that class's documents, minutes instead of the forty a
corpus pass costs. SCREEN FAIL means revert and move on. SCREEN PASS means the corpus pass is now
worth spending. It is not a substitute for the ratchet; it only decides whether to spend it.

## One rule for "kept", in one place - and three ways to satisfy it

`attempt.py compute()` is the only authority. An attempt is kept when ANY of these holds:

    1. moved >= max(2, 25 % of the class)        the original bar
    2. total < 2 and moved >= 1                  a class of one: one document IS the class
    3. moved >= 1 and --best-drop >= 5.0         one document that moved a long way

**PASS `--best-drop`.** It is the largest single-document share@5 improvement in the attempt, and
without it rule 3 cannot fire:

    attempt.py --class "<cls>" --moved 1 --total 7 --best-drop 18.02 --reason "..."

Rule 3 exists because of `content-partly-lost-and-displaced`: 7 documents, six already under 5.0, one
improved by 18.02 points - the whole point of the class - and the 25 % bar called it 'partial' because
1 < 2. A count of documents cannot tell a real fix from measurement noise; the size of the movement
can, and 5.0 is the same line the ranking already treats as ink in the wrong place.

## One rule for "kept", in one place

`attempt.py compute()` is the only authority: kept when `moved >= max(2, 25% of the class)`. `classify.py`
imports it rather than restating it. They used to disagree - 25 % against 50 % - so the same numbers
recorded through the two tools produced different verdicts.

## The report says two things it never used to

`report.py` prints **"looked dead, was not"** - the longest stretch with no tool call, when it started,
and what the run had just called. A forty-minute ratchet and a hung run look identical from outside;
this row is the difference. It also prints **"obstacles this run"**, counted from `BLOCKERS.md`.

So when something goes wrong, write the row in `BLOCKERS.md` and let the report carry it. Being stuck
is not a failure to report - it is the most useful thing you can report, because the next run reads the
file and starts where you stopped instead of walking into the same wall.

## A document that was never measured is not a clean document

`416_many_tiny_pages` sat in `RANKING.csv` with `share5=0.0` and `problem=none` - reading as PERFECT
in the one table the pipeline is judged on - while `EXEMPT.json` said it had never been measured at
all. Two lies in one row: `none` told the class file it was clean, and `0.0` dragged the corpus mean
down so every other number looked better than it was.

**Settled:** an exempt document carries a BLANK score and `problem=exempt`. Blank means unknown; zero
means perfect. The corpus mean covers 212 documents, and the report prints the exempt one on its own
line. `gate.py` re-applies the exemption after every publish, because `p2w.py` writes `0.0`/`none`
for anything it cannot measure and would put the lie back.

## Two clocks, and the report prints both

`RUN.json` records when the slot was CLAIMED. Nothing writes a beat before `step.py` runs, so the time
a pod spends cloning and retrying before it claims is invisible to every file - on 18 Nov a run began
at 13:50, claimed at 14:50, and the report said "38 min" about a session that lasted 1h 47m.

**Settled:** the prompt's first command writes the epoch to `/tmp/session_start`; `step.py` copies it
into `ROUND.json`; `report.py` prints Session, Slot window and Before the claim as three separate rows.
Never type a time - `blockers.py` stamps blocker rows from the clock, because three rows once went in
stamped 16:35/16:38/16:44 inside a commit dated 16:24:27.

## The report is a file, and it is the message

The cron delivers the fixer's last text to the chat and stores nothing - `cron runs` returns
`output_summary: null`. Twice the only way anyone could read what the user was told was for the user to
export the cron page to a PDF, seven pages of prompt included.

**Settled:** write the finished message to `/tmp/report.md`, run `lastmessage.py --file`, commit
`LAST-MESSAGE.md`, then send that exact text. The file and the message must be identical.

## Sign every commit "p2w fixer <HH:MM>: <subject>"

`report.py` finds the run's commits by that prefix and unions their files for the Committed line.
Without it the line counts somebody else's work: on 18 Nov it reported nineteen files across ten
commits for a run that made three.

## Do not commit while a fixer run is in flight

A run clones once. Commits that land after its clone leave it reading stale ledgers - on 18 Nov it read
a blocker row that had been fixed a minute before it started, and a 60-minute re-clone cost the run
half its session. If origin has moved, `git fetch` and `git reset --hard origin/main` inside the clone
you already have, and keep your `TIMELINE.jsonl`.

## What the agent already did, so you do not do it twice

The agent worked 19 Nov with no `java` and no write path. It could read the engine, the corpus and
the 213 `.txt` files, and it could run `verify_txt.py`. Everything below is **already done** — do not
redo it, and do not re-derive it.

### Two bugs were found in `verify_txt.py` and are fixed

**`t13` matched an amount by TOKEN and always took its first occurrence.** On an invoice the CGST
and SGST columns routinely hold the same figures, so one token ended in two columns and both source
columns read the same first position. The SGST column was judged against the CGST position and
passed for the wrong reason — and the reverse, which is what the corpus shows: the check was
*failing* documents that were genuinely aligned. Measured on `390_wide_data_appendix`, 4 of 19
columns preserved before, 19 of 19 after.

The fix matches the **k-th source occurrence of a token to the k-th `.txt` occurrence**, walking the
source in the order the page draws its lines.

**`t12` counted a punctuation-only token as an invented word.** `_strip_punct` strips
`.,;:!?()[]{}"'…-` from both ends, so a lone em dash becomes `""` — and `""` was counted. Both
`balance-sheet-and-profit-loss` and `balance-sheet-two-columns-of-figures` were failing t12 on
nothing but empty strings.

### The `.txt` baseline has been re-stamped for both

    OLD  149 clean of 213 (70.0%)   64 failing
    NEW  159 clean of 213 (74.6%)   54 failing

13 documents improved, **0 worsened**. `tools/p2w-bench/txt/RESTAMP-TXT.jsonl` holds all 213
per-document records that produced it. `restamp_txt.py --report` re-prints the comparison;
`--apply` rewrites both CSVs atomically.

**Do not run `txt_rank.py` bare.** It scores 20 documents and overwrites the published table. Use
`restamp_txt.py --run` (resumable, writes to JSONL) then `--report` then `--apply`.

### Two tooling bugs are fixed

* **`round.py` called `sh()` and had no `sh`.** The auto-revert guard — the thing that puts an
  unmeasured engine change back — raised `NameError` and was swallowed by a bare `except`, so it
  **never once ran**. Found by the 00:58 run and fixed.
* **`lastmessage.py` now refuses a report whose numbers do not equal `report.py`'s.** Exit 3 means a
  number was not copied from the tool. The 13:50 run published "17 files" where `report.py` said 6.

* **AND IT CHECKS THE PROSE, NOT ONLY THE TABLE - because that is where every later error lived.**
  Four reports in a row were wrong outside the Progress rows, and each cost a manual audit:

      header     "slot 16:11 -> 17:18 IST - 1h 07m"   RUN.json: 16:11 -> 17:00, 48 min
      corpus     "of 212" in every sentence            the corpus is 213; 212 is the baseline
                                                       intersection, since 416 was exempt then
      .txt       not mentioned at all                  166 clean, 47 failing
      agents     "16:22 -> 16:32"                      nothing behind it
      committed  "29 files in 7 commits from 0b8c821"   25 files in 8 commits

  `report.py --json` now carries `corpus.docs` (213) AND `corpus.compared` (212) as separate fields,
  plus `txt` and `subagents`, which were computed for the document and absent from the JSON so
  nothing could check a .txt sentence against them. `verify_facts()` compares the header's clock and
  duration, any number in the corpus range, the .txt's clean and failing counts, and each agent's
  deployed_at / landed_at / minutes. It refuses; it does not warn. Both checks run before deciding -
  the row check used to return early, so a report with a bad row was rejected without being told its
  clock was wrong too.

  **The rule this encodes: never type a number that a tool can print.** Run
  `report.py --json` and copy. If `lastmessage.py` refuses, the number is wrong - it is not being
  pedantic.

### Three root causes are diagnosed, in `FINDINGS/t02-t12-t08-root-causes.md`

* **`t02`** — the check fits ONE global character width. In every failing document the failing lines
  sit further right than the passing ones (`58_header_rule_footer_rule`: passing at x=56, failing at
  x=423 and 503, off by 3 columns). **A proportional font has no single character width.** This is a
  check redesign, not a writer bug, and `310_court_judgment` fails at 89 against a 90 bar.
* **`t12`** — five separate causes: curved-text segmentation, source-side misses on stamps,
  Devanagari clusters split mid-word (`केवल` → `क` + `ेवल`), two table cells joined with no space
  (`60067mobile`), and line-wrap word splitting. **Four writer faults, one name.**
* **`t08`** — zero tolerance, and six of ten documents fail by **exactly one line out of 16 to 88**.

### Three specifications are written, in `PATCHES-READY.md`

`PATCH-411-ctm-size.patch`, `PATCH-t13-table-row-per-line.patch`, and `SPEC-justified-lines.md`
(the `855f443` rebuild). **All three are unbuilt and unmeasured** — the agent had no `java`. Build
each, screen it, ratchet it. The specs say what to expect and what to prove; they are not proof.

### What is still yours

The engine work. 72 `.docx` open, 54 `.txt` failing, `416_many_tiny_pages` never measured, the
census at 6 of 72, and every one of the three patches above to build and measure.

## THE COMMIT GATE — universal, no override, no exceptions

**No commit may land, for the .docx or the .txt, unless the whole corpus has been measured with the
engine as it stands and no document got worse.** Not one document. Not by one point. A fix that
improves 20 documents and damages 1 is not a fix, it is a trade, and nobody authorised the trade.

This is not advice. It is enforced in three places:

    tools/p2w-bench/regress.py --check     the check itself; exit 1 refuses
    .git/hooks/pre-commit                  installed by tools/install-gate.sh; a real commit is
                                           aborted, verified 19 Nov - HEAD stayed at 8e8fdd2
    tools/p2w-bench/step.py                a fixer slot is not released while it fails

### What "worse" means

    .docx   share@5px went UP. It is compared against TWO floors: the 15 Nov baseline AND the
            last committed value. The baseline alone is a ratchet with a slack rope - a document
            that improved 10.78 -> 0.50 could drift back to 5.00 and still beat its baseline.

    .txt    any document fails a check it did not fail in the baseline. Checks are pass/fail, so a
            new member of the failing set is a regression however small the check looks.

### An unmeasured change is not a pass

If the engine has changed since the corpus was last measured, the tables describe an engine that no
longer exists. `regress.py` compares the current engine fingerprint against `txt/ENGINE-STAMP.json`
and refuses when they differ. After re-measuring, run `regress.py --stamp`.

**This is why the 411 fix is committable and the t13 patch is not.** 411 was measured across all 213
documents and proved to move exactly one: 212 `.docx` byte-identical, 213 `.txt` byte-identical,
and the one that moved went 31.05 -> 0.00. t13 was measured and moved 101 documents the wrong way,
with 0 better. One has a proof, the other has a story.

### The order to work in

    1. change the engine
    2. measure the whole corpus in BOTH formats
    3. regress.py --check        must PASS
    4. regress.py --stamp        record which engine the tables describe
    5. commit

Skipping 2 and 3 is the one thing that cannot be recovered from, because a regression that lands is
a regression every later measurement inherits.

### Scoped or both: the scope is DERIVED and then PROVED

Running the `.docx` pass for a `.txt`-only change costs hours and proves nothing; running only the
`.txt` pass for a model change lets a `.docx` regression land. So the scope is not claimed by the
author, it is worked out from the code:

    tools/p2w-bench/scope.py

It reads `git diff` and finds which **methods** changed, not which files — because `PdfToWord.java`
holds `convert()` (BOTH formats) and `writeTxt()` (txt only), so a file-level rule is either too
coarse or unsafe. The table:

    TxtWriter.write            -> txt
    PdfToWord.writeTxt         -> txt
    DocxWriter.write           -> docx
    DocxWriter.orderStamps     -> both   (reorders page.blocks, which TxtWriter walks)
    PdfToWord.convert          -> both   (builds the model both writers read)
    ReadingOrder.apply         -> both

**A change it cannot name a method for is BOTH.** A change inside a model class (`Box`, `Para`,
`Table`, `CellPara`, `Line`, `Result`, `Page`, `Glyph`) is BOTH even when it sits in a writer file,
because the other writer reads the same field. Verified 19 Nov: the 411 change lands in
`processTextPosition` and scopes to BOTH, which is correct — it changes `g.size`, and `TxtWriter`
reads that.

### And then it is PROVED, not trusted

The scope is only worth having if it is true, and the way to know is byte-identity:

    build the tree, convert the whole corpus to the format you say cannot move
    build HEAD,  convert the whole corpus the same way
    diff the two directories

Zero differences is proof that no score in that format can differ — the writers produced the same
bytes for all 213 documents. That is what was done for 411: **212 `.docx` byte-identical, 213 `.txt`
byte-identical**, and the one `.docx` that moved went 31.05 -> 0.00.

**If the byte check shows movement, the scope was wrong.** Run both.

### Stamps are per format

`txt/ENGINE-STAMP.json` holds a fingerprint for `docx` and one for `txt`. A txt-only change re-stamps
`txt` and leaves `docx` alone, so the .docx table is not invalidated by work that could not touch it.
`regress.py --check` compares only the fingerprints for the formats in scope.

    regress.py --check              scope from scope.py
    regress.py --check --only txt   force it (for when scope.py cannot see your change)
    regress.py --stamp              stamp the formats in scope
