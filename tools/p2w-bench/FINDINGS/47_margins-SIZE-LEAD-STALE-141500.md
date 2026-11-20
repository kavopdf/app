# The run-size lead in SETTLED.md does not reproduce on this engine - AND MY OWN FIRST READING OF IT WAS WRONG

Written 20 Nov 2026, 15:20 IST, by the fixer run that took `47_margins`.

`SETTLED.md` and `PATCH-AUDIT.md` both carry one open idea, and it is the only one either file calls
"the best single change available":

> `run-size-from-sizePt-not-Tf` takes `360_restaurant_menu` from **34.43 to 1.31** ... and in the same
> breath takes `392_statistical_console_output` from 1.61 to 13.94. The mechanism is real and it is
> aimed at the right thing; it is simply too broad. A version gated on the case it fixes ... is the
> best single change available.

**Measured today, against the engine in the tree, neither half of that is true.** The patch is one
line in `PdfToWord.processTextPosition`:

    g.size = tp.getFontSize() > 0 ? tp.getFontSize() : tp.getFontSizeInPt();

| document | RANKING.csv (this engine) | + the patch, ungated | |
|:--|--:|--:|:--|
| 360_restaurant_menu | 34.43 | **34.18** | 0.25 better, not 33 points |
| 392_statistical_console_output | 1.61 | **0.06** | 1.55 better, and it was said to be 12 points worse |

And the check, not just the score, on the same two renders:

    360  before: 47_margins median 0.1 pt, 9 unregistered, page-1 anchor source 52 / render 40  FAIL
         after : 47_margins median 0.1 pt, 9 unregistered, no anchor failure at all               FAIL
    392  before: fails 47_margins on the LibreOffice render of this engine too             FAIL
         after : 42 of 42 checks PASS, 47_margins median 0.1 pt, 0 unregistered                PASS

So the trade-off the whole lead is built on has gone. The patch does not lose 392; it **fixes** 392 -
every one of the 42 checks - and it repairs 360's body-column anchor without touching its remaining
nine unregistered runs. That is a better result than the one the lead promised, and it is the wrong
shape for the class: 2 of 26 documents, when the bar is 6.5.

## Why the gate failed

The obvious gate - apply the exact size on a proportional face, keep the rounded one on a monospaced
face, on the theory that a mono line's columns are already on the face's advance grid - was built and
measured first. It is aimed at nothing:

| document | face | Tf / rounded | gated result |
|:--|:--|:--|--:|
| 360_restaurant_menu | DejaVuSerif | 8.5 / 8.0 | 34.43 - unchanged |
| 392_statistical_console_output | DejaVuSansMono | 6.6 / 6.0 | 1.61 - unchanged |
| 365_recipe_card, 07_stamp_over_table, 21_form_labels | - | - | unchanged |

The 360 gain does not come from the serif's size at all: it appears only when the change is applied
ungated, which means it reaches 360 through some *other* glyph on the page - the Helvetica or the
DejaVuSans of the section headings - and not through the 8.5 pt body the gate was written for. A gate
is a claim about which glyphs matter, and this one is false. Diff: `47_margins-size-ungated-141500.diff`
(the gated variant is in that file's history; the ungated one is the last hunk).

## What the next run should do with it

The change is worth a screen, not a keep. It touches the size of every glyph in the corpus, and two
documents is not a blast radius:

    git apply tools/p2w-bench/FINDINGS/47_margins-size-ungated-141500.diff
    bash tools/p2w-bench/build-engine.sh
    pip install scipy                     # without it one page takes 150 s, not 2
    python3 tools/p2w-bench/screen.py --docs "360_restaurant_menu,392_statistical_console_output,<more>"

Judge it on `verify_google.py --detail`, not on share@5: 392 moves 1.55 on the score and 42-of-42 on
the checks, and it is the checks that say a document is fixed.

## The measurement that was missing, and now is not

`verify_google.py` computed the two lists behind 47's verdict and then `del`-ed them, so a FAIL printed
`source=0.1 render=9` and nothing about which page or how far out. `--detail` now prints both lists and
writes them into the `--json` output under a top-level `detail` key - never into the checks dict, which
`all_check_ids()` enumerates and would score as a free pass. It is what turned "360 fails 47_margins"
into "360's body column is 12 pt left, and nine runs are 11.9 pt out".


## CORRECTION, 15:25 - the numbers in the table above are HEAD's, not the patch's

The "ungated" build I measured turned out to be a **no-op**. The line I wrote

    g.size = (tp.getFontSize() > 0) ? tp.getFontSize() : tp.getFontSizeInPt();

is semantically identical to the line already in the tree - I had only added parentheses. So the
`/tmp/ung` .docx was HEAD's own output, and everything I attributed to "the patch ungated" is simply
what this engine already does:

| document | RANKING.csv says | a pristine HEAD build measures |
|:--|--:|--:|
| 392_statistical_console_output | 1.61, 47_margins FAIL | **0.06, 42 of 42 checks PASS** |
| 360_restaurant_menu | 34.43 | **34.18** |

I caught it by diffing the saved diff against HEAD after the fact - which is the check I should have
run before recording the attempt. The attempt record has been corrected in place.

**What survives, and it is bigger than the original claim:** `benchmarks/RANKING.csv` and both
`gverify` tables do not describe this engine for `392_statistical_console_output`. The class table
counts it as a 47_margins failure; a fresh LibreOffice render of the current tree passes all 42 checks
and scores 0.06 where the table says 1.61. Any attempt judged against those tables mis-reads its own
result - and this class's own size is therefore an upper bound, not a count.

**What does not survive:** there is no `run-size-from-sizePt-not-Tf` win to gate. The real patch (no
parentheses) changes 360 by 0.25 and 392 by nothing, because on this engine both documents already
read what the "fixed" number was supposed to be. Retire the lead.
