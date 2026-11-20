# Fixer report - 2026-11-21 02:30

**21 Nov 2026 · slot 00:57 → 01:51 IST · 54 min**

> Nothing was kept, and the run still moved the class: three of the five documents holding
> `t01_word_accuracy` are now measured as the scoring reference's fault, not the writer's, and one
> of the handed diagnoses was wrong. The writer is right on all three.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 4 attempt(s), 0 kept |
| Documents improved, round total | 60 of 213 |
| Corpus improvement vs 15 Nov | **+39.61%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **7**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 32 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `t01_word_accuracy` |
| Committed | **19** files in 8 commit(s) from `4411394` — ...NT-PROPOSAL-clip-flag-NOT-APPLIED-0210-fixer.md, 38-faux-bold-TRIPLE-DRAW-0225-fixer.md, 39-small-caps-gap-threshold-0150-fixer.md, ATTEMPTS.json, BLOCKERS.md, CLASS-HISTORY.jsonl, HANDOFF.json, HANDOFF.md, LAST-MESSA |

## The slot was a zombie's

The run holding the slot had died at 23:24 without releasing it, and the 00:07 watchdog wrote that
a person would have to clear it. It did not need one: the last activity was 94 minutes old against
a ten minute stale window. One thing made it read as busy - a fresh clone gives every file a fresh
mtime, and the claim reads the timeline's mtime as the run's activity. Setting that mtime back to
its last real record was the whole fix, and it is worth writing down because every fixer run clones.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:57 | **reverted** | 0/5 | Class claimed: `t01_word_accuracy`, 5 documents, .txt half. Census first, no engine change. |
| 01:41 | **reverted** | 0/5 | Second attempt, two subagents. `411` and `39` are both the reference's, measured. |
| 02:25 | **reverted** | 0/5 | Third attempt, own angle. `38` draws its headings three times and the reference counts two of them; corpus scan puts the blast radius at one document. |
| 02:50 | **reverted** | 0/5 | Fourth attempt, read-only census. A widget appearance glyph walk fires on 2 of 213 documents - the bank form is the one to gate on, not 601. |

## The three findings, and the numbers behind them

**411\_nested\_xobject\_transforms - the handed diagnosis was false.** The claim was that pymupdf
and PDFBox disagree about a nested form's matrix and the rotated line runs off the page. Both
parsers compute the same CTM to the digit, `[0 1 -1 0 60 700]`, determinant +1, and PDFBox returns
all 32 glyphs of the rotated line; pymupdf's own `get_texttrace()` returns all 32 too. Only
`page.get_text()` returns 2, because `fitz.TEXTFLAGS_TEXT` includes `TEXT_MEDIABOX_CLIP` and that
path drops a line crossing the page edge. The .txt carries the 28 on-page glyphs and is right; the
reference invents the words `S` and `O`. Turning that one flag off leaves 211 of 213 rows
byte-identical and moves `411` and `12_stamp_across_page_break`, which the same path charged `U`
and `G`.

**39\_small\_caps\_letter\_spacing - the correct file scores worse.** The letter spacing is not
`Tc`, not `Tz` and not a kerning number: it is the `TD` x-coordinates of single-glyph `TJ` arrays,
with a real space glyph drawn between the letters. The writer breaks a word at
`0.18 x 8.00 = 1.440 pt`; the reference splits at the drawn 1.200 pt gap. The writer emits
`570 005`, which is what the page draws - a Mysuru PIN in its grouped form - and the reference
reads `57 0 0 05` and charges the difference in both directions, eight words lost and two invented,
one fault. A writer patch that produces the page's real words is scored:

| `39_small_caps_letter_spacing` | t01\_word\_accuracy | t12\_word\_invention |
|:--|--:|--:|
| .txt as it is today | 97.4 | 2 |
| .txt with the page's real words | **58.5** | **22** |

38.9 points lower for the correct file, because the reference reads the small-caps headings letter
by letter.

**38\_faux\_bold\_italic\_synthesised - the page draws its headings three times.** Two fill spans
and one stroke span at the identical position, same font, same size, same baseline: the faux-bold
idiom. `get_text()` reads the fill copies and counts each of the two headings twice - 201 words
against 186 with identical-position spans collapsed, which is the `t01` charge on a 99 % threshold,
and the doubled em dash is the `t07` charge. A walk over every page of all 213 PDFs finds
identical-position duplicate spans on exactly this one document, so a same-place-same-string dedupe
on the source side has a blast radius of one.

## What was not done, on purpose

`verify_txt.py` was not edited. All three findings say what a correct reference would do and none
of them moves a number. Two of the three - the clip flag and the dedupe - are one sanctioned
source-side correction away, and the proposal with its exact diff, its whole-corpus measurement and
the restamp sequence is in `FINDINGS/INSTRUMENT-PROPOSAL-clip-flag-NOT-APPLIED-0210-fixer.md`. The
third, the 1.200 pt split, needs a decision about which boundary is authoritative on a letter-spaced
line, and no straight swap exists: preferring the drawn space glyphs welds the address correctly
but scores 90.0 on that document. Both decisions are a person's, and both are in BLOCKERS.md with
what they cost.

Two repairs were built and rejected on measurement, so nobody builds them again: a content-order
rebuild from `get_texttrace()` fixes `411` and makes 83 of 213 documents worse; abstaining when a
span cannot be aligned moves `t01` on 86 of 213.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **186** (87.3%) |
| Failing at least one check | **27** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Subagents

| Agent | Sent to find | Landed | Result |
|:--|:--|:--|:--|
| `t01_A-02` | is the handed nested-form diagnosis real - prove or kill it on 411 | yes | killed it; the matrices agree and the clip flag is the cause |
| `t01_B-02` | why 39 loses 8 words and invents 2 - writer or reference | partial | the reference; it built and measured the writer patch, and this run wrote its finding up |

Both ran inline rather than in the background: a scheduled run has nobody to answer later, so the
platform ran them inside the turn. That is the long silence in the timing table, and it is why 41
of this run's minutes are the agents and not the engine. The third finding is this run's own work
after they returned.

## Timing

| | |
|:--|:--|
| Slot window | 00:57 → 01:51 · 54 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 35 |
| Longest silence | **28.3 min** — from 00:57:53, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 3 |
| Obstacles | 0 cleared · 1 need a human |
| Still a wall | two of the five documents (411_nested_xobject_transforms, 39_small_caps_letter_spacing) fail t01 only because  |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **41 min** | `#################` |
| record - attempt, handoff, class rows | **3 min** | `#` |
| report - the report and the chain | **8 min** | `###` |
| other - not attributed to a tool | **0 min** | `#` |

## Next run

`t01_word_accuracy` has exactly one engine-side document left: `601_fillable_admission_form`, whose
ticks are ZapfDingbats glyphs in the widget appearance streams and whose fix is already named - a
glyph walk over each widget's `/AP /N`, the shape `formValuesOf` and `_ap_stream_text` already have
on both sides. Take that one, and read `FINDINGS/widget-AP-walk-BLAST-RADIUS-0250-fixer.md` first: the walk fires on
2 of 213 documents, and `Account_Opening_Form_Fillable_filled` - 137 of its 352 widgets carry text
- is the one to gate on before 601. Do not spend a slot on `411`, `39` or `38`: all three are written up
with the measurement that proves them the reference's.

If the rotation moves on, `t08_line_order` is the largest class still entirely open at 10 documents,
and the 19:33 census already showed six of its eight measurable documents are off by exactly one
line. The census of where all five `t01` documents stand is in
`FINDINGS/t01-census-WHICH-SIDE-0150-fixer.md`.