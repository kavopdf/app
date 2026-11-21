**22 Nov 2026 · slot 23:57 → running IST · 14 min**

> `32_stroke_lines` is not a hard class, it is a wrong carrier. Across the 192 scored documents
> **not one document passes it on a rule carried as a floating `<w:drawing>`** — 76 of 76 fail.
> The only two documents that carry a source rule *and* pass carry it as a **table-cell border**.
> The class has been chasing a shape Google cannot see; `w:tcBorders` is the construct that
> survives, and last slot's carrier patch already proved it on two more documents.

## Progress

| | |
|:--|:--|
| Documents improved this run | **0** — 1 attempt(s), 0 kept |
| Documents improved, round total | 61 of 213 |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt, not measured | **0** — none |
| **Fixed - Google, all 42 checks** | **6**, out of the 192 documents both renderers measured |
| Fixed - LibreOffice proxy | 33 of 213 - a renderer the user does not open |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 6 clear — 6 class(es) still have an OPEN document |
| Working on | `32_stroke_lines` |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 00:20 | **lead** | 0/192 | THE DRAWING CARRIER HAS NEVER PASSED IN GOOGLE. All 213 converted, cross-tabulated against the 192 committed Google verdicts: 76 documents carry a rule as a floating `<w:drawing>` and no border — **all 76 fail**; the 2 documents with a source rule that pass (`373`, `64`) carry it as a `w:tcBorders` border; 0 documents pass with rules and no border; 0 fail with no source rules |

## The class I chose, and why

`classpick.py` suggested `t08_line_order` — a `.txt` check worth 10 documents in the renderer nobody
opens. I took `32_stroke_lines` instead, and the arithmetic is why. Sixteen documents fail **exactly
`{05_chars_extra, 32_stroke_lines}`** and nothing else: `17`, `18`, `19`, `24`, `26`, `32`, `34`,
`37`, `45`, `47`, `49`, `53`, `74`, `315`, `334`, `product-catalogue-code-left-price-right`. `05`
was cleared instrumentally last slot, so those sixteen are **one construct from clean**, and two
more (`394`, `407`) fail `32` alone. Eighteen documents hang on this one class, in Google. No `.txt`
class comes near it.

The class also carries the five-check family `classpick.py` names as one construct — `05`, `18`,
`32`, `59`, `25` — which the tool measures at **51 clean documents** if all five clear.

## Why this is a lead and not a fix

The measurement refutes the carrier the engine ships and confirms the one it does not. It does not
place the rules. The carrier patch (`patches/rule-carrier-per-rule-2008.patch`, rules as 1×1
floating tables with `tcBorders`) puts `394` at 42/42 and `45` at 42/42, and still loses **one of
two** carriers on the other sixteen, which read `{source: 2, render: 1}`.

A subagent read the XML of `17`, `45`, `53`, `74`, `394` and killed my first hypothesis. The carriers
are **byte-identical** between `45` (both placed) and `17` (one lost): same `tblpX/tblpY`, same
`trHeight 1 exact`, same `tcBorders`. Not the anchor context either — every carrier in all five
documents is body-level, none inside a `w:tbl` or `w:txbxContent`. The only property that separates
them is **position in the block sequence**: in `17`/`53`/`74` the two carriers are the **last two
blocks of `<w:body>`**, with nothing after them; every placed carrier in `394` and `45` has a
paragraph after it or between it and the next carrier.

That is a correlation on five documents, so it is stated as one and the falsification is written
down: append one empty `<w:p/>` after each carrier and re-read `17`/`53`/`74`. `{2, 2}` and sixteen
documents go clean; `{2, 1}` and the cause is elsewhere.

## Falsification

The claim was "a drawing-carried rule never passes". Three ways to break it, all run on the whole
corpus:

| test | expected if the claim is right | measured |
|:--|:--|:--|
| documents with a source rule, no border, passing `32` | 0 | **0** |
| documents with a source rule and a border, passing `32` | at least 1, else the border story is unsupported | **2** — `373`, `64` |
| documents with no source rule failing `32` | 0 | **0** |

The direction that could have refuted it — one document passing with a drawing-carried rule — has
**no instance in the corpus**. The 69 documents that fail *with* borders are not a counter-example:
their borders are a real table's grid at the table's own coordinates, not a carrier at the rule's
coordinates, and the check matches geometry.

The weaker half of the story — that Google *rasterises* the drawing so `_rule_segments()` cannot see
it — is **not proven here** and is not needed. Whether Google drops the shape or rasterises it, the
check reads zero either way and the fix is the same. One Google round trip on a document with a
known rule count would settle it; no export PDF exists in the repo and this slot did not spend one.

## The txt

| | |
|:--|:--|
| Scored | **213** of 213 |
| Clean - every applicable check passes | **197** (92.5%) |
| Failing at least one check | **16** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

One agent, `rule-carrier-probe`, deployed 23:58, returned in 9 minutes. It read `word/document.xml`
for `17`, `45`, `53`, `74` and `394` at both HEAD and the patched build, and reported every carrier
with byte offsets. It **refuted** the pipeline's own next probe ("the carrier Google drops is the one
anchored inside a `w:tbl`") with the fact that all 17 carriers are body-level, and it found the
byte-identical footer carrier in `17` and `45`. Its report is
`rule-carrier-anchor-context-report.md`; the numbers are folded into the finding above.

A second agent was not deployed. The first took nine of the slot's fourteen working minutes and
answered the question the second would have asked.

**Its own caveat, kept:** `_rules_lost` consumes each render segment once, so `{source: 2, render: 1}`
does **not** by itself prove a shape was dropped — it is equally what you see when two carriers land
at one y and the first render segment is consumed by the first source rule. Attaching the loss to a
named carrier needs a Google export, which no sandbox here can produce.

## Timing

| | |
|:--|:--|
| Slot window | 23:57 → running · 14 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 10 |
| Longest silence | **10.1 min** — from 23:57:48, after `handoff.py: reading or writing the handoff` |
| Silences over 2 min | 2 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |

### Where the time went

| Phase | Time | |
|:--|--:|:--|
| fix - diagnose and change the engine | **2 min** | `###` |
| measure or build - a conversion, screen or compile writes no beacon | **11 min** | `##################` |
| other - not attributed to a tool | **0 min** | `#` |

## Next run

Three things, in this order, and the first is the slot.

1. **The trailing-pair build.** Apply `patches/rule-carrier-per-rule-2008.patch`, then append one
   empty `<w:p/>` after each carrier. Convert and measure `17`, `53`, `74` through Google. Predicted
   before the run: `{source: 2, render: 2}` on all three, sixteen documents clean. If it reads
   `{2, 1}` the prediction is wrong and the paragraph-after theory dies with it — say so.
2. **Re-score `32` on the corpus.** 145 stored verdicts are stale against any carrier change, exactly
   as the 141 `05` verdicts are stale against last slot's `norm_text` fix. `benchmarks/gverify/`
   still carries pre-fix `05` on 141 documents, so every count in this pipeline understates the
   corpus.
3. **Do not retry the pBdr carrier or the bare floating drawing.** Both are refuted by measurement:
   pBdr in `HANDOFF.md`, the drawing here, 76 of 76 with no exception.
