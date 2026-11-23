# The refused spacer's `w:line` is not the same lever as `w:before` - measured in Google, and moving it REGRESSES

**23 Nov 2026 · relay fixer run, slot 14:16 IST · engine at HEAD 75ace97 · outcome: measured lead, reverted**

Two measurements, both Google Docs round trips (upload → convert to Google Doc → export PDF →
`verify_google.py`). LibreOffice was not used for either verdict.

## Measurement 1 - what Google does with each construct

A sub-agent built 13 single-page probe documents, each two identical anchor runs with one empty
spacer paragraph between them, and measured `ANCHORBOT` bottom minus `ANCHORTOP` bottom in Google's
own exported PDF. Slack was 1 twip, page 11906×16838 tw, margins 1134 tw.

`w:before` sweep (`w:line=1`, `lineRule=exact`):

| `w:before` twips | declared pt | delivered pt | % |
|---:|---:|---:|---:|
| 0 | 0.0 | 0.00 (baseline) | - |
| 288 | 14.4 | 14.40 | 100 |
| 576 | 28.8 | 28.80 | 100 |
| 1152 | 57.6 | 57.60 | 100 |
| 1440 | 72.0 | 72.00 | 100 |
| 2880 | 144.0 | 144.00 | 100 |
| 4320 | 216.0 | 216.00 | 100 |
| 6480 | 324.0 | 324.00 | 100 |
| 11520 | 576.0 | 576.00 | 100 |

Slope 1.000, intercept 12.19 pt, residual 0.00 pt at every point. **No threshold, no clamp.**

`w:line` sweep (`w:before=0`, `lineRule=exact`, `sz=2` mark):

| `w:line` twips | declared pt | delivered pt | % |
|---:|---:|---:|---:|
| 288 | 14.4 | 13.11 | 91.0 |
| 2880 | 144.0 | 137.30 | 95.3 |

The two levers are additive and independent (`before=2880, line=288` = 144.00 + 13.11 exactly).

**This refutes the premise the 13:20 run left open.** That run wrote: "`w:before` is NOT honoured at
its declared value on this spacer. 144 pt of `w:before` would have closed a 144 pt gap; it closed
none. Until someone explains what Google does with a `w:before` above some threshold..." There is no
threshold. `w:before` is exact; `w:line` exact is the lever that under-delivers.

## Measurement 2 - the change that follows from it, and why it is not kept

The engine has two spacer branches (`DocxWriter.java:6056-6070`):

- **spendable** - the gap is written as `w:before = spacerTw - 1`, `w:line = 1`.
- **refused** - the gap is written as `w:before = 0`, `w:line = spacerTw`.

So the *same gap* is delivered by two different constructs, and which one a document gets is decided
by how much room the page has - not by what the renderer does with it. Measurement 1 says the refused
branch is the losing one: it draws the spacer high by 4.7% of its own height at 144 pt.

`68_journal_wide_table_spanning` is the refused case: one spacer at `w:before="0" w:line="2880"`.
Its 18_displacement failure is exactly the 6.70 pt shortfall - the run tolerance is
`clamp(0.35*size, 1.5, 4.5)` pt.

Patch (`refused-spacer-before-lever-REGRESSES-GOOGLE-1458-relay.patch`): emit the refused spacer as
`w:before = spacerTw - 1`, `w:line = 1`, the same construct the spendable branch already uses.
`before + line` still equals the gap to the twip, so the engine's own accounting does not move.

| | before | after |
|:--|:--|:--|
| Construct written | `w:before="0" w:line="2880"` | `w:before="2879" w:line="1"` |
| Pages | 1 | 1 |
| Google score, 42 checks | **41/42** | **40/42** |
| Failing | `18_displacement` (source=0 render=1) | `18_displacement` (source=0 render=1), **`59_shape_anchor` (source=49 render=42)** |

Both scores are live Google round trips on this engine, same document, same source PDF.

**The change is refused.** It does not fix `18_displacement` at all, and it adds `59_shape_anchor`:
7 anchored runs that were inside their enclosing box are no longer. Pushing the flow down by 6.70 pt
moves the absolutely-anchored boxes relative to their containers. This is the same signature the 13:20
run measured for its partial spend (`68_journal` 41/42 → 40/42, `59_shape_anchor` added) - so the
regression is a property of moving this document's flow at all, not of how the gap is split.

## What this leaves

The 6.70 pt is real and it is the whole of `18_displacement` on this document, but it cannot be paid
for out of the spacer alone: every anchored box on the page is placed relative to the flow the spacer
sets, so the spacer and the anchors have to move together or neither moves. The next probe worth a
slot is whether `59_shape_anchor`'s box is measured against the paragraph the spacer precedes - if it
is, the anchors need their offsets re-based by the same 6.70 pt in the same change, and the two
constructs are one fix, not two.

Not measured: the corpus. `regress.py --check` was not run against this patch, because the patch was
refused on the one document it was aimed at.
