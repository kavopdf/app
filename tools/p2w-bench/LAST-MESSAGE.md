# P2W Fixer - Run Report

**21 Nov 2026 · slot 18:17 → 19:10 IST · 53 min**

> No change was kept this run. But the single biggest blocker in the pipeline was measured closed, and
> that is worth more than the four attempts it cost.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 4 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## The result worth having: the rule carrier is complete

`32_stroke_lines` is priced at **36.3 clean documents** — the largest single prize in the pipeline — and it
has been blocked for weeks on one question: the engine emits every rule as a floating `<w:drawing>`, Google
**drops** it, and no run could measure what Google *does* honour, because staging a local `.docx` into
Drive needs a platform `upload` tool a sub-agent does not have. The relay has that tool. Everything below
was measured through Google Docs itself, not through LibreOffice.

| construct | asked for | Google rendered | verdict |
|:--|:--|:--|:--|
| `w:tab w:pos="4320"` in a flow paragraph | 216.0 pt | **216.00 pt** | honoured, exactly |
| the same, 72 pt left margin | 72 + 216 | **288.00** | honoured, **from the margin** |
| `w:tcBorders/w:bottom` | a rule | 1 segment, **468.00 pt** | honoured |
| `w:tcBorders/w:left`, 1440-twip row | 72.0 pt | **72.00** | honoured, exactly |
| anchored `<w:drawing>` rule | a rule | **no segment, no image** | **dropped** |
| `w:tblInd` 1000 twips | 50.0 pt | **50.00** | placed exactly |
| `tblLayout=fixed` + `tblGrid` 2000 twips | 100.0 pt | **100.00** | placed exactly |
| **`w:tblpPr` floating, `tblpY` 8000 twips** | **400.0 pt** | **399.5, and 0.00 pt of flow** | **honoured, flow-free** |

The last row is the one that unblocks the work. A three-page probe, one export:

| page | carrier | `BELOW` y | displacement | rule drawn |
|:--|:--|--:|--:|:--|
| 1 | none (control) | **11.92** | — | none |
| 2 | inline, `trHeight val="1" exact` | **12.83** | +0.91 pt | x 122→222, y 11.5 |
| 3 | **floating `w:tblpPr`** | **11.92** | **0.00 pt** | x 122→222, **y 399.5** |

A floating table is honoured, renders its rule at the requested y to within 0.5 pt, and costs the flow
**nothing at all** — `BELOW` sits at the control's exact value. The construct, the traps
(`vertAnchor="page"` is silently dropped, an all-zero `tblpPr` is discarded, `tblPr` child order is fatal)
and the four things still unmeasured are written up in
`FINDINGS/32_stroke_lines-TBLPPR-ZERO-FLOW-1905-f1x.md`.

## What was tried, and why none of it landed

| Attempt | Outcome | What it measured |
|:--|:--|:--|
| Tab stop for `47_margins` | **reverted** | Google honours it: 216.00 pt rendered against 216.0 pt asked. The engine patch could not be built: the agent returned a **sketch with `…` placeholders**, not a diff. Worth ~1 clean document, under the bar. |
| Cell-border carrier for `32_stroke_lines` | **reverted** | Honoured both axes, placeable to 0.00 pt in x and length. Blocked on flow — the row displaced text by 38 pt. |
| `t08_line_order` falsification | **reverted** | The handoff's one instruction, run. Both sides were wrong; see below. |
| Floating carrier `w:tblpPr` | **reverted** | The flow blocker **closed**, 0.00 pt. No engine patch: no time left to convert and score a real document. |

### The t08 falsification

Four synthetic documents, draw order controlled, `.txt` order written by hand:

| case | current tree | handoff's global sort | per-page sort |
|:--|:--|:--|:--|
| control, drawn top-down | PASS | PASS | PASS |
| drawn **bottom-up**, `.txt` correct | **FAIL** `5/2` | PASS | PASS |
| `.txt` order deliberately wrong | FAIL `5/3` | **FAIL `5/3`** | **FAIL `5/3`** |
| two pages, correct `.txt` | t08 PASS | **FAIL `5/4`** | t08 PASS |

The check is wrong — a page drawn bottom-up gets a correct `.txt` and the check calls it a defect. The
handoff's fear that a sort would "compare sorted-vs-sorted" is **refuted**: the falsifier still fails with
the identical score. And its *implementation* is wrong anyway — a global sort puts page 2's `y=100` above
page 1's `y=200` and **fails a correct two-page document**. Per-page sorting is the correct four lines.

It was applied and reverted. `regress.py --check` **passed** on the patched tree and that is not evidence:
it compares the *engine* to the stamped table, and a verifier change moves no engine byte, so it never
re-runs the verifier. Landing on that PASS would have been the fifth unmeasured change behind a green gate.

## What the next run should do

1. **Convert `394_map_with_legend` with three floating carriers.** It has 3 rules, fails `32_stroke_lines`
   alone, and sits at 41/42. If it reaches 42/42, the construct is proven on a real document and the other
   145 are repetition. Everything needed is in the finding.
2. **Then the multi-rule question.** Nothing measured says what 46 floating tables do to each other or to
   the page count. `407_id_card_front_back` (46 rules) is the stress case.
3. **Do not chase `t08_line_order` as a fix.** The ten documents are not broken; the instrument is. The
   patch is written out and needs one restamp pass, not a fixer slot.

## Obstacles, and two that are still walls

* **The gate cannot see a verifier change.** `regress.py --check` answers PASS on a patched
  `verify_txt.py` without re-running it. A verifier edit is the one change that moves every number and the
  gate is blind to it. Worth fixing as a tool.
* **The build is the slot.** Three of four attempts died on "the patch is ready and there is no time to
  build and measure it". A slot that starts with a warm engine and a converted corpus would land several
  times what this one did.
* **The last run's reported wall did not reproduce.** It said `regress.py --check` refuses *every* commit
  because the docx stamp no longer matched the tree. On this run it passed cleanly on six commits. A gate
  that refuses everything and a gate that refuses nothing are both failures, and it is worth knowing which
  this was.
* **This run's own timeline is incomplete.** The beacons from the first half were lost in three
  `git stash`/`rebase` cycles against a moving remote, so the "longest silence" above (5.4 min) understates
  the real gap — the first sub-agent ran **22 minutes inside the turn** rather than in the background.

## Subagents

| Agent | Sent to find | Result |
|:--|:--|:--|
| `47_margins` docx half | the construct, the code site, one falsifiable patch | 26 documents counted; `DocxWriter.flowFromBox` and `runXml` located; a tab-stop proposal measured on 12 documents. Its diff was a **sketch with placeholders** and could not be applied. **Took 22 min inside the turn** — the run's clearest failure, since it left no room for a second agent. |
| zero-flow carrier | what OOXML construct makes a bordered box occupy no flow space | **Found `w:tblpPr`**, quoted the ECMA-376 definition, ruled out the nested-table and paragraph-container routes, and built the 3-page probe this run then measured through Google. **Took 6 min.** |

The difference between 22 minutes and 6 is the whole story of why the first agent was the failure and the
second was the run's best asset: one was asked for a patch, the other for an answer.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **190** (89.2%) |
| Failing at least one check | **23** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t08_line_order` - 10 documents |

## Timing

| | |
|:--|:--|
| Slot window | 18:17 → 19:10 · 53 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 23 |
| Longest silence | **5.4 min** — from 19:04:35, after `classrow.py: refreshing the class file` |
| Silences over 2 min | 5 |
| Obstacles | 4 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| setup - claim, housekeeping, reading the gate | **1 min** | `##` |
| fix - diagnose and change the engine | **7 min** | `#######` |
| record - attempt, handoff, class rows | **1 min** | `#` |
| report - the report and the chain | **12 min** | `############` |

---
*Every number in this report was read from a tool's output or measured in this run. The five Drive probe
documents created this run were all deleted.*
