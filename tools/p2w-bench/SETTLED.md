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
