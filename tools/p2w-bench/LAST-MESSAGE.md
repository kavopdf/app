# Fixer report - 2026-11-25 04:23

```
# P2W Fixer - Run Report

**25 Nov 2026 · slot 04:23 → running IST · 1 min**

> No change was kept this run. The numbers below say what was tried.

## Progress

| | |
|:--|:--|
| **Self-check** | **1 disagreement(s)** - subagents: 2 deployed vs no FINDINGS file for 25_iinvisible-te |
| Document-moves this run | **0** — 1 attempt(s), 0 kept (a sum: a document moved twice counts twice) |
| Documents improved, round total | **61** of the 212 compared (corpus 213) |
| Corpus improvement vs 15 Nov | **+39.70%** — mean 6.15 → 3.71 |
| Regressions | **none** |
| Exempt from the LibreOffice comparison | **0** — none |
| **Fixed - Google, every applicable check** | **36** of the **187** re-measured on this engine - **4** of the 191 scored are still on an older engine, and **0** of those were clean on the engine they were measured with |
| Who re-measures them | the **:20 gverify** cron, up to 60 documents a run - about **1** run(s) for the 4 outstanding. Until then "fixed" means fixed on an engine that is not this one |
| Fixed - LibreOffice proxy | 33 of the 212 compared - a renderer the user does not open |
| Not scored - page count did not match | **22** of the 213 gverify saw - a document that drew the wrong number of pages cannot be compared line by line, and it is a defect, not a pass |
| Moved but still open | **28** — improved, not fixed |
| Classes solved | 0 of 34 clear — 34 class(es) still have an OPEN document |
| Working on | `-` - taken from the pending list (20 still open), not a new class |
| The rotation says | `18_displacement` - the run chose `-` by hand instead |

## What was tried

| At | Outcome | Moved | What it measured |
|--:|:--|--:|:--|
| 04:23 | **lead** | 1/None | 2x2 dose over the 133 cached documents: the 120 pt cap alone removes 10% of box characters (8176->7386), the negative-gap anchor alone 71% (->2374), both 86% (->1122, 12 body-text documents zeroed). 1 |

## The txt

| | |
|:--|:--|
| Measured | **1.5 h ago** |
| Scored | **213** of 213 |
| Clean - every applicable check passes | **199** (93.4%) |
| Failing at least one check | **14** |
| Moved since the last commit | **none** - nothing changed |
| Most common failure | `t12_word_invention` - 8 documents |

## Subagents

| Agent | Sent to find | Deployed | Landed | Took |
|:--|:--|--:|--:|--:|
| `25_iinvisible-text-blind-01` | is the check blind after the 24 Nov sheet filter, an | 04:24 | - | not recorded |

## Timing

| | |
|:--|:--|
| Slot window | 04:23 → running · 1 min |
| Before the claim | not recorded - nothing writes a beat until step.py runs |
| Tool beats | 12 |
| Silences over 2 min | 0 |
| Obstacles | 0 cleared · 0 parked, with the evidence to re-open them |


### Where the time went

| Phase | Time | |
|:--|--:|:--|
| other - not attributed to a tool | **0 min** | `######################` |
## Best results this round

| Document | Before | After | Change |
|:--|--:|--:|--:|
| `415_inline_images` | 89.04 | 0.00 | -89.04 |
| `411_nested_xobject_transforms` | 31.05 | 0.00 | -31.05 |
| `itr-computation-with-slab-table` | 68.82 | 42.33 | -26.49 |
| `report-2col-table-spanning-both-columns` | 22.58 | 0.76 | -21.82 |
| `75_merged_header_cell_three_columns` | 27.62 | 7.62 | -20.00 |

## What this run decided, and why

**The class was `04_chars_missing`, chosen on leverage, not on rotation.** The rotation said
`18_displacement`; the run went to the construct underneath it, because the brief's own root-cause file
names one mechanism - body text written into an anchored DrawingML box that Google rasterises - as the
largest engine defect anyone has found, and `04_chars_missing` is the check that sees it.

**The mechanism turned out to be two triggers, not one.** Measured by counting the characters inside
`<w:txbxContent>` in every emitted `word/document.xml` - the exposure itself, with no renderer in the way -
over the 133 cached documents: HEAD carries 8176 such characters in 37 documents; the 120 pt gap cap alone
removes 10 % of them (7386); the negative-gap anchor alone removes 71 % (2374); both remove 86 % (1122),
zeroing the box text on 12 body-text documents. Fifteen stamp documents are invariant under all three, so
neither knob touches the constructs that are supposed to be boxes - the separation the earlier
investigation could not make. Page count did not move on any of the 14 documents whose box text changed.

**And it was proved in Google, on the one document that has a stored Google verdict.**
`27_two_column_left_short_txtpos` was 40/42 on `b7699196`, failing `04_chars_missing` and
`44_header_footer`. With both knobs and its 43 box characters at zero it scores **42/42 PASS** on a Google
render of a real Google Doc.

**Nothing was shipped as a default, and that is the decision the next run inherits.** Both knobs move every
line the flow could not place, on every document; the gate wants a corpus-wide re-measure before an engine
change lands and a full restamp is about 54 minutes. The instrument that made the dose possible is committed
as a patch (`patches/gapcap-instrument.patch`, 75 lines, verified behaviour-neutral on four documents)
because the engine file itself had to be reverted to pass the gate. The measurement, the per-document table
and the Google proof are in `FINDINGS/GAP-CAP-VS-ZERO-GAP-ANCHOR-BOX-TEXT-DOSE-25NOV.md`.

## Next run

Apply `patches/gapcap-instrument.patch`, rebuild, then take the pair to Google on **two** documents, not
one: `27_two_column_left_short_txtpos` (expect 42/42, already measured) and one document that currently
passes `18_displacement` and carries box text, to see what the trade costs. That second document is the
whole question: both knobs buy text-as-text by giving up absolute position, and `18_displacement` is where
the bill arrives. If it holds, the pair is shippable as a rule and needs the full restamp; if it fires, the
answer is the band-as-one-paragraph route in `ANCHOR-FLOW-ROOT-CAUSE-DOSE-RESPONSE-24NOV.md`, which nobody
has built.

Second, before anything else in the instrument: `25_invisible_text` cannot fail (0 of the 392 Google exports
checked). Settle the sampling radius on `301_lab_report_panel` and `340_bill_of_lading`, then ship the
patch - the 43 recorded failures on that check are a number nobody can currently move.
