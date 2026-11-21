**22 Nov 2026 · relay slot 00:15 → running IST · 38 min**

> The class is not "a construct Google drops". It is **one block after the carrier**.
> `17` and `53` go 40/42 → **42/42 PASS** in Google Docs with one empty paragraph added after each
> rule carrier and nothing else changed. The change is written as a patch and **not landed**: the
> re-measurement needs about 25 minutes of corpus rendering and this slot ran out before it finished.

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:40 | **refuted** | 0 | The trailing-block theory, corpus-wide. all 145 failures carry it **and** every one of the 146 documents with a floating carrier does too - 100% prevalence, no discriminating power on the HEAD build. `373` passes with the property present. The cross-tab was measuring the writer's block ordering, not the cause. |
| 00:47 | **refuted** | 0 | "A drawing-carried rule never passes" (last slot's `76 of 76`). `373` passes `32_stroke_lines` on a floating `<w:drawing>` with **zero** `w:tcBorders` and **zero** floating tables - a real table's top border sits at y=108.00, the source rule at 87.70, inside the check's own 24 pt tolerance. |
| 00:56 | **lead** | 0 | A six-rung `tblpY` ladder (80, 700, 750, 775, 785, 793.89 pt), all six carriers trailing, one Google export: the 80 pt carrier rendered at 80.5, **the other five at 81.5-84.5, every one ignoring its own `tblpY`**. Google lays a trailing carrier out in flow under the one before it. |
| 01:02 | **fix, measured** | 2 | One empty `<w:p/>` after each carrier: `17` 40/42 → **42/42**, `53` 40/42 → **42/42**. The 793.89 pt rule renders at 794.5 pt, `_rules_lost` reads 0 on both. |

## The class I chose, and why

`classpick.py` suggested `32_stroke_lines` and the arithmetic agreed, so I took it - but not for the
reason the tool gave. Sixteen documents fail **exactly `{05_chars_extra, 32_stroke_lines}`** and
nothing else, and `05` was cleared instrumentally two slots ago, so those sixteen are **one construct
from clean in Google**. Two more (`394`, `407`) fail `32` alone. Eighteen documents, all of them
`.docx`, in the renderer the user opens. No `.txt` class is near it.

The class was worked to a measured fix, not to another lead. What stopped it landing is not the
construct and not the evidence - it is that a 146-document construct change needs the full corpus
re-measured before it may be stamped, and that is a 25-minute job this slot did not have left.

## Why it is a lead and not landed

`regress.py --check` passes - **no document worse than baseline, docx or txt**, and
`google-safe` reports no ignored construct has spread. It refuses on the fingerprint alone:
"ENGINE CHANGED (docx): table measured on `6c6cf642e13b7ed2`, the tree is `88ddb2bfdfe91962`."

`benchmarks/gate.py` is the re-measurement and it caches per document in `/scratch/work/p2w/dist2/`,
so repeated `--budget 280` calls make progress. This slot got **39 of 213 docx rendered, 0 of 212
measured** before it had to stop. Stamping on that would be the exact "unmeasured change" the gate
exists to refuse, so the engine is reverted to HEAD and the change ships as
`patches/rule-carrier-followed-by-block-2008.patch`.

## Falsification

The prediction was written to `/scratch/work/PREDICTION.txt` **before** the test ran: *"32_stroke_lines
reads {source:2, lost:0} on both; the 793.89 rule appears within 24 pt of 793.89; page count stays 1.
If it reads {2,1} the following-block theory is dead in Google too."*

| test | expected | measured |
|:--|:--|:--|
| `17` carrier alone, Google export | lost 1 | **lost 1** (rule at 793.89 absent) |
| `17` + one empty block, Google export | lost 0 | **lost 0**, rule at 794.5 |
| `53` + one empty block, Google export | lost 0 | **lost 0**, rule at 794.5 |
| page count, both | stays 1 | **stays 1** |
| six-rung ladder, all trailing | every rung at its own `tblpY` | **five of six stacked at 81.5-84.5** |

The direction that could have refuted the mechanism - a trailing carrier landing at its own `tblpY`
without a following block - has **no instance** in the ladder. The reading was taken with the check's
own functions at the check's own constants, not with the tool I had just edited.

## Subagents

Two, both deployed inside the first ten minutes.

**`carrier-geometry`** read the check's implementation and the XML of the passing and failing
documents. It established that the check never reads XML - it is `page.get_drawings()` on both sides -
and it refuted last slot's `w:tcBorders` claim: `373` and `64` carry **zero** `w:tcBorders`; `64` uses
`w:tblBorders` on a real flow table, `373` passes on tolerance. Its own probes found the trailing-block
effect in LibreOffice, which is what sent me to Google to test it properly.

**`carrier-position`** built all 213 `.docx` and cross-tabulated carrier position against the
committed Google verdicts: all 145 failures carry the property, **and so does every one of the 146 documents with a floating
carrier**. That refuted the theory as a corpus claim - correctly, for the HEAD build -
and it is why I did not spend the slot on a corpus-wide correlation and went to a single Google export
instead.

## Next run

1. `python3 benchmarks/gate.py --budget 280` in a loop until `p2w.py` reports 213 of 213. It caches;
   repeated calls make progress. Do not stamp before it completes.
2. Apply `patches/rule-carrier-per-rule-2008.patch` then
   `patches/rule-carrier-followed-by-block-2008.patch`, rebuild, convert, `regress.py --check`,
   `regress.py --stamp`, commit.
3. Re-measure the sixteen `{05, 32}` documents through Google. Predicted **42/42 on all sixteen**;
   `394` and `407` should follow to 42/42. That is eighteen documents, and it takes the Google total
   from 6 to 24.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 0 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `-` |

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Timing

| | |
|:--|:--|
| Slot window | 00:15 → running · 38 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 7 |
| Longest silence | **18.0 min** — from 00:15:30, after `gaps.py: reading the timeline` |
| Silences over 2 min | 5 |
| Obstacles | 2 cleared · 2 parked, with the evidence to re-open them |
| Still a wall | **this watchdog has no `cron` tool, so a paused or zombie cron cannot be moved by automation.** STEP 3 and STE |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| measure or build - a conversion, screen or compile writes no beacon | **25 min** | `###############` |
| report - the report and the chain | **6 min** | `####` |
| other - not attributed to a tool | **6 min** | `####` |
