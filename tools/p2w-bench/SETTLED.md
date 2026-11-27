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

**THE ONE IDEA WORTH CARRYING FORWARD - RE-MEASURED 20 Nov, AND IT IS NOT THE TRADE IT SAYS.**
`run-size-from-sizePt-not-Tf` was recorded as taking `360_restaurant_menu` 34.43 -> 1.31 while taking
`392_statistical_console_output` 1.61 -> 13.94. On the engine in the tree it does neither:

    360_restaurant_menu          34.43 -> 34.18   (0.25 better, not 33 points)
    392_statistical_console_output 1.61 -> 0.06   (1.55 BETTER, not 12 points worse)
    and 392 goes from failing 47_margins to 42 of 42 checks PASS

Worse than stale: **there is no win there at all.** The gate the lead asks for - exact size on a
proportional face, rounded on a monospaced one - was built and measured and moves neither document. The
real one-liner changes 360 by 0.25 and 392 by nothing. Retire the lead; it was measured against an
engine two days old.

**AND THE TABLES THEMSELVES ARE STALE FOR AT LEAST ONE DOCUMENT.** A pristine build of the current
tree scores `392_statistical_console_output` at 0.06 with **42 of 42 checks PASS**, where
`benchmarks/RANKING.csv` carries 1.61 and both `gverify` tables carry a `47_margins` FAIL. 360 reads
34.18 against 34.43. Judge an attempt against a fresh render of the document, not against the table,
until a corpus pass rewrites it. Numbers: `FINDINGS/47_margins-STALE-TABLES-152500.md`.

**AND DO NOT SPEND A RUN ON THE LEADING-SPACE INDENT FOR `47_margins`.** It reaches 3 of that class's
26 documents and can reach no more - the trace in `FINDINGS/47_margins-REACH-140500.md` counts every
writer on all 26. The 25 % bar is 7.

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

## The table-top spacer is NOT what fails the 16 solo `18_displacement` documents

Built, measured through Google on 22 Nov, reverted. The gap above a table was written as
`w:line="spacerTw" w:lineRule="exact"` on a `w:sz=2` mark, and Google reads `w:line` as a MULTIPLE
of the face's line height, so 2880 twips came back 13.74 pt instead of 144. That is a real defect
and the fix for it is real — `w:before` is honoured exactly, and the engine's own `ctx.flowTw` and
`cenSetY` already charged the full spacer. Writing it as `w:before` with the box cut to a hairline
moved **1 of 16**, `68_journal_wide_table_spanning` 12.09 -> 11.24, and nothing else. Reverted;
the bar is 4.

**Do not rebuild it, and do not believe the −114.8 pt figure.** It came from a FINDINGS measurement
at HEAD; `benchmarks/RANKING.csv` gives the same document `max_pt` **8.64**. Two records of one
document, a factor of thirteen apart, and the table is the one the gate and the ratchet read. A
130 pt spacer loss cannot produce a render whose largest error is 8.64 pt, and the after-render's
median/p90/max are identical to the before row to the hundredth — the table never moved.

**What the sixteen actually look like — and do NOT read `median_pt` 0.96 as an offset.**
`benchmarks/p2w.py` computes it as `p50(dv) * 0.48` where `dv = d[sm & (d > 1)]` and `d` is an
INTEGER distance transform. Every pixel at distance 0 or 1 is excluded, so the smallest value the
statistic can hold is 2 px = **0.96 pt: that is the floor of the instrument, not a measurement.**
Fourteen of the sixteen sitting on 0.96 means "at or below two pixels", nothing more. It is also
self-contradicting as a cause: `18_displacement`'s tolerance is `clamp(0.35 * size, 1.5, 4.5)` pt, so
a real 0.96 pt offset would PASS. This was written up as a lead and retracted inside the same run.

**What is left is a tail, not a shift** — `p90_pt` 1.44 to 6.24, `max_pt` 1.44 to 17.76, three to
thirty-seven pixels on a minority of the ink.

**AND SIX OF THE SIXTEEN ARE UNDER THE CHECK'S OWN FLOOR.** `22_invoice_four_columns_txtpos`,
`41_coloured_headings_white_bg`, `73_marksheet_subject_marks_grade`, `16_right_aligned_amounts_txtpos`,
`29_dot_leaders_txtpos` and `72_bank_statement_no_rules_right_amounts` all have `max_pt` 1.44 to 2.40,
under the 1.5 pt floor for every face size, and `18_displacement` fails them anyway. **The check's dy
and the ranking's dy are therefore not the same quantity.** Settle which one the class is defined by
before building anything for these six; part of the class's 18.6-clean-document leverage may be an
artefact of the check rather than of the engine. `71_invoice_space_aligned_no_rules` is the opposite
and a separate question: share@5 26.88, `median_pt` 3.84, no table spacer at all.

**AND `18_displacement` IS NOT A DISPLACEMENT THRESHOLD.** Its tolerance `clamp(0.35 * size, 1.5, 4.5)`
is never below 1.5 pt, so a page with nothing more than 1.5 pt out can only fail it through the
`if not ds: bad_pages.append(pg)` branch — upright text on the page and none of it matched. Six of the
sixteen have `max_pt` 1.44–2.40 and `share5` 0.00, i.e. under the tolerance, and fail anyway. Test
which clause fired (`verify_google.py --json` on one of them, no build needed) before believing the
class is about vertical position; if it is `not ds`, the fault is run matching or reading order and no
vertical constant will fix it.

Full numbers: `FINDINGS/18_displacement-SPACER-REFUTED-0900-f1x.md`.

## `screen.py` measured NOTHING on a fresh pod, and said the idea had failed

`screen.py` set `p2w.REPO` after importing `benchmarks/p2w.py`, but `p2w.py` computes
`ENGINE_SRC = os.environ.get("P2W_ENGINE_SRC") or REPO` at MODULE level from `ROOT + "/repo"`.
On a pod that has never run, that directory does not exist: every `ConvertOne` died on
`ClassNotFoundException` in under a second, nothing reached `dist/`, and the tool printed
`PARTIAL - 0 of N measured. Call again` for ever. A run following the brief would revert a good
change on that verdict.

**Settled:** `screen.py` sets `p2w.ENGINE_SRC = REPO` beside `p2w.REPO`. Verified 22 Nov: 0 of 2
measured before, 2 of 2 after, with no environment variable set. If a screen ever reports
"0 of N measured" again, check that `p2w.ENGINE_SRC` resolves to the tree before believing it.

## Stamps: separate by object identity, not by colour. Five colour masks are dead.

Full detail: `FINDINGS/STAMP-GENERAL-METHOD-OBJECT-IDENTITY-NOT-COLOUR-27NOV-agent.md`.

A stamp sits **on top of** body text, so both paint the same pixels, and the result is a blend that records
nothing about how much of each contributed. **No colour test can undo that** - not distance, not saturation,
not a residual, not an ordering test. Five were built and measured and every one failed differently:

1. colour distance plus a saturation floor - discarded pale lettering entirely
2. coverage only - **the whole black body text came through at full alpha**
3. residual to the paper-to-ink line - left a pale ghost
4. plus a small absolute saturation floor - cleaned two documents, not the third
5. plus rejecting anything darker than the pure ink - **punched holes in the stamp's own letters**

**Settled:** render the stamp from its **own objects** onto a blank page. The body text is not on that page,
so nothing can blend, and the stamp comes out complete and alone **by construction** rather than by
threshold. It is colour-blind, so it holds for black stamps, multi-colour, semi-transparent, any shape, and
stamps that are already raster or are glyphs with no border.

**Do not build a sixth colour mask.** Measured, dead, recorded so no run spends itself rediscovering it.

## Stamps: the rect is the ink box, not the stroke's centre path

`get_drawings()` returns `rect` as the bounding box of the stroke's **centre path**. The ink extends half the
stroke width beyond it on every side. Measured:

    06  stamp rect 147.62x114.13   rendered ink 152.64x119.16   error +5.02   stroke 4.89
    07  stamp rect 159.71x82.89    rendered ink 161.28x84.48    error +1.57   stroke 1.44

**The error equals the stroke width, exactly.** Every size deficit measured on these documents was this:
-4.6 and -5.0 on 06 against a stroke of 4.89, -3.4 on 02 against 1.67, -2.2 on 07 against 1.44.

**Settled:** `SR = SR expanded by (max_stroke_width / 2)` on every side, then place the image at that rect
with that rect's size. After the fix the render matches the rect within **0.09, 0.12, 0.02 and 0.15 pt** on
01, 02, 06 and 07. Self-correcting crop-and-stretch was tried first and **made 06 worse** - do not use it.

## Stamps: colour cannot locate one. Three discriminators measured, three dead.

- **Rarity** - stamp colour counts run 2 to 5, body colour counts run 4 to 32. **Ranges overlap completely.**
  On `15_stamp_on_scanned_page` and `43_red_stamp_over_black_text` the stamp's colour **is** the most common
  colour on the page.
- **Saturation** - 312's body text is `(0.25,0.25,0.55)` at 0.30 against a stamp at `(0.48,0.12,0.12)` at
  0.36. Six hundredths apart.
- **Overlap** - 7 of 15 stamps overlap any body text against 5 of 16 non-stamps; **eight of fifteen stamps
  overlap nothing.**

**Settled:** the locator must be **geometric**. Rotated text spans find the stamp on **14 of 16**; the page
carrying an image finds `10_stamp_as_image`; a closed tall path finds `12_stamp_across_page_break`. **16 of
16 located, 15 renderable** (12 is one stamp drawn across a page boundary, at y -16.4 on page 1).

**But the locator has false positives and the count is NOT 52.** Across 213 documents it returns 31 + 12 + 9
= 52 candidates, and the lists include `table-with-rotated-header`, `60_page_border`,
`one-page-rotated-180-degrees`, prescription photographs and coloured callout boxes. **The corpus has 16
documents with a stamp.** Reporting 52 would be reporting rotated content, not stamps.

## Stamps: opacity is measured inside the glyphs, not inside the span box

`get_texttrace()` returns `alpha=None` for every span, so the PDF's text alpha is not available from the API.
It has to be measured from the render as coverage along the paper-to-ink line.

**Measured inside the span's bounding box it is wrong**, because the box is mostly background: 07 came out
0.88 when its text is fully opaque. **Measured inside the glyphs** - the median of covered pixels, clamped to
1.0 above 0.85 - the answer is right.

**Settled:** 06's `PAID` is genuinely **0.55** (a semi-transparent stamp), and every other stamp text is
**1.0**. Peak coverage p90 and max are 1.00 on all four test documents.

## Stamps: position and size are inside 1 pt on four documents, through a real Google export

    01  +0.0, +0.0   size -0.2, +0.0      exact
    02  +0.2, +0.2   size -0.7, -0.2
    06  +0.5, +0.2   size -1.0, -0.5      PAID at its true 0.55, ink -5%
    07  +0.2, +0.2   size -0.2, -0.5

**And the measurement that produced "+4.6" and "+3.8" earlier was wrong, not the placement.** The .docx
anchor is the ink box to the hundredth of a point on all three. The error was a colour tolerance of 120
catching neighbouring ink and growing the bounding box - at tolerance 60 both documents read +0.2, +0.2.

**Settled:** measure the stamp with a **tight** colour tolerance, or the window grows and the number lies.
Every geometry "failure" in this work was the stamp measured with a window that included what was not the
stamp.

## Stamps: the engine should copy the operators, not reconstruct

Reconstruction from `get_drawings()` and `get_text()` has now lost three things the API does not hand over:
**the text's alpha**, **the exact stroke cap and join**, and **the font metrics**. Each cost a run to
discover. Copying the stamp's operators into a fresh page loses nothing - that is the engine's job and it is
not to be done by rebuilding the stamp from the XML.

## Every document's text is clipped at the bottom, and it is `w:lineRule="exact"`

**213 of 213 docx use `w:lineRule="exact"`. None use `atLeast`, none use `auto`, none omit it.**

The paragraph that clips reads:

    <w:spacing w:before="262" w:after="0" w:line="12" w:lineRule="exact"/>
    <w:sz w:val="17"/>            <- 8.5 pt of text

`w:line="12"` with `lineRule="exact"` is **0.6 pt of line box** around **8.5 pt of text**. The part of the glyph
outside the box is cut, and that is the descender - `p`, `y`, `g` lose their tails.

**Settled by measurement, not assumption:**

    exact,   line 0.6   body text  -> line contributes 0.6 pt
    exact,   line 0.6   table cell -> line contributes 6.3 pt   (a floor, still short of the 11.07 pt glyph)
    atLeast, line 0.6   either     -> 9.8 pt, the natural height for 8.5 pt Times

**`exact` clips. `atLeast` does not, and gives the same natural height in body text and in a cell.** The cost
is about 3.5 pt of extra advance per line, so `before` must come down by the same amount.

**Do not simply switch `exact` to `atLeast` and stop** - tried, and the document grew from one page to two.

## Text overlapping itself: the tab stop sits at the cell edge

**FIXED AND MEASURED.** A label and its value are one paragraph already; the tab between them was wrong:

    <w:tabs><w:tab w:val="left" w:pos="2747"/></w:tabs>
    <w:tcW w:w="2747"/>          <- the cell is the same width

The tab sat exactly at the cell's right edge, so the value had no room, **wrapped to the next line**, and with
a 0.6 pt line box printed almost on top of the label. Four tabs in that row, all wrong: 2747 equal to the cell
width, 2889 twice which is outside the cell, 2562 which is inside but still leaves no room. **The cell itself
was too narrow** - the source PDF needs 183 pt of content in a 137 pt cell.

**The fix, measured through Google: cell 2747 -> 3660 twips and all four tabs -> right at 3660. Overlaps go
from 4 to 0, page count unchanged.**

**Rule:** a tab stop must leave room for what follows it. A label/value pair needs a **right** tab inside the
cell at least the value's width from the label's end - never a left tab at the cell edge - and the cell must be
wide enough for both.

**And measure x as well as y.** An earlier reading of this defect compared y only and reported two overlaps
between two different table columns that never touch.

## What is and is not wrong in the exported PDF - a correction

An earlier version of this section claimed the engine drops table rules and shading and rasterises content.
**Two of those three claims were wrong and are withdrawn.** They came from counting drawings in the *exported
PDF* and treating those counts as if they described the `.docx`.

Measured on the `.docx` itself and confirmed by eye in Google Docs with print layout on:

    w:lineRule="exact"      79 of 79 paragraphs
    w:before (absolute Y)   79 of 79 paragraphs
    wp:anchor               17, all relativeFrom="page", zero inline
    w:br (breaks)            0        <- Adobe's output has section and column breaks; ours has none
    sectPr                   1
    w:tcBorders              6        <- table borders ARE present, and visible in the render
    w:shd                    0        <- but the Grand Total row IS shaded, so shading comes from elsewhere
    images in package        1        <- only the stamp. The 17 images in the export are Google's doing.

**So: table borders are present and render correctly. The Grand Total row's shading is present and renders
correctly.** Both claims in the earlier version were wrong.

**What IS wrong, confirmed by eye in print layout on:**

- **The totals block prints on top of itself** - `Total job work charges` over `2,81,120.00`, `CGST @ 6%` over
  `16,867.20`, `SGST @ 6%` over `16,867.20`, `Grand Total` over `3,14,854.40`. **This is the tab-stop defect
  described above, and it is visible in the default view, not only in pageless mode.**
- **The header banner's text does not render** - `TAX INVOICE — JOB WORK` is in the document and text
  extraction finds it, but the dark red bar renders empty.

**And the 17 images are not ours.** The package contains one image, the stamp. Whatever rasterisation appears in
the export is done by Google on the way out, not written by the engine. **That distinction matters: it means
there is nothing to fix in the `.docx` for it.**

## Pageless mode is not a defect to chase

With print layout **off**, Google Docs reflows the document and our output looks worse than Adobe's or
iLovePDF's. **Adobe and iLovePDF show the same class of breakage there** - section and column break markers
become visible and content shifts - so this is a property of the viewer, not of any one converter.

**Do not change the output to suit pageless mode.** It is not the default view, the default view is what is
measured, and changing constructs for it risks the paginated render that is the official one.

**One difference is worth knowing, though it is not a task:** Adobe's output carries **section and column
breaks**; ours carries **none** (`w:br` = 0, `sectPr` = 1). Breaks give a reflowing viewer something to hold
on to. That is an observation, not a recommendation.

## `SETTLED.md` is far longer than the brief says, and that matters

The brief tells a run that this file is 87 lines and takes two minutes. **It has not been true for a long time.**
A run that budgets two minutes for it will skim exactly the sections that cost the most to learn - the stamp
method, the `lineRule` clipping, the tab-stop overlap, and the pageless decision.

**The brief now carries the real number, and it says to read the newest sections first.** Everything added on
27 November sits at the bottom of the file, after 400 lines of older material, so a run that reads top-down and
stops early misses all of it.

**Read the last six sections before anything else in this file.** They are the ones a run will otherwise
rediscover the hard way.
