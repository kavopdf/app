# 18_displacement: the guard IS what holds 68_journal - spending its gap moves the table 111 pt, and costs 7 shapes

**Measured 25 Nov 2026, fixer slot 09:02 IST. Two Google round-trips, one document, same engine, one
variable.** This corrects the prediction in
`18_displacement-SPACER-PATCH-ALREADY-LANDED-13-ARE-TWO-SHAPES-25NOV.md`, which named exactly this
experiment as the discriminator and expected a null result.

## What was run

The finding above says: *"The discriminator for the 7 is one Google round-trip:
`68_journal_wide_table_spanning` carries a single 144 pt un-split spacer, the largest in the corpus, so if
relaxing the guard for it does not move its dy, the guard is not what is holding that document up."*

That is the experiment. The guard at `DocxWriter.java:6122-6123` was made spendable unconditionally under an
environment variable (`P2W_SPACER_FORCE`, default **off** - with it unset every document is byte-identical
to the committed engine, verified by diffing `word/document.xml` of the two conversions: identical lengths,
identical bytes). The same source PDF was then converted twice on the same engine build, uploaded to Google
Docs, exported as PDF and scored with `verify_google.py`:

| | spacer paragraph | 18_displacement med_dy | worst_dy | checks |
|:--|:--|--:|--:|--:|
| CONTROL (guard as committed) | `w:line="2880"`, `w:before="0"` | **-114.3 pt** | 115.0 | 41/42, fails 18 only |
| FORCED (`P2W_SPACER_FORCE=1`) | gap split into `w:before`, hairline in `w:line` | **-3.1 pt** | 3.9 | 40/42, fails 18 and 59 |

`runs_matched` 74 on both sides, so the same text was matched both times; `med_dx` -0.4 on both.

## What this settles

1. **The guard is the blocker for 68_journal.** Spending the gap moves the table **111.2 pt down** - it goes
   from 114 pt too high to 3.1 pt too high. The old finding's expected null result is **falsified**: the
   spacer is not inert on this document, the `slackTw` arithmetic is what refuses it, and the fix belongs in
   the guard, not in a second construct.
2. **The residual after spending is ~3.1 pt, not zero.** 18_displacement still fails (3.9 pt worst on page
   0), so "spend the gap" alone does not make this document clean. Whatever the next attempt is, it must
   carry a ~3 pt floor term - the same magnitude the guard's `rowExcessTw` was guessing at with 15 twips
   (0.75 pt) per row.
3. **Spending has a measured cost on this document: 7 shapes disappear** (`59_shape_anchor`: source 49,
   render 42). The gap spent pushes content down far enough that shapes fall off the compared page. That is
   the same trade the 22 Nov measurement found on `mobile-bill` and `insurance-policy-schedule` (one page ->
   two pages, 46/47 -> 43/47), now reproduced on a third document. **A guard relaxed to fix 18 buys a 59 on
   the same document**, which is why the arithmetic must be right rather than removed.

## What to do next (for the next run, not this one)

- The prize is real and it is in `slackTw`: `budgetTw - pageInkBottomPt*TWIPS_PER_PT` refuses 144 pt of gap
  on a page that, once spent, only overshoots by 3.1 pt. A guard that credits the page's own bottom slack
  with the measured ~3 pt floor instead of `15 twips * pageRowCount` is the shape of the fix.
- Do **not** land the unconditional spend. It trades one check for another on the same document and the
  corpus gate would refuse it as a Google regression (68 goes from 1 failing check to 2).
- The env-gated probe was reverted at the end of this run; the engine on HEAD is unchanged. The lever is
  three lines and is reproduced in the "What was run" table above.

## The transferable rule

**A finding that names a discriminator is not a result.** The 25 Nov census priced this experiment
correctly and then the slot ended before it ran, so the next run read a prediction as if it were a
measurement. One Google round-trip per shape, taken *before* the class is scheduled, is cheaper than a
patch that has to be reverted.
