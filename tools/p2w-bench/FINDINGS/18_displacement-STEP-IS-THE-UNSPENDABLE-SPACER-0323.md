# `18_displacement`: the block-top step IS the unspendable spacer, and the last slot's pair cannot work

Slot 02:19 → 24 Nov 2026. Two measurements: one from the document's own XML (this run), one from
the engine source (this run, agent B). Both are independent of the four live Google numbers the
previous slot recorded, and both are checked against them below.

## 1. The step is exactly the unspendable spacers — nothing else

The engine writes a table's block-top gap as an empty paragraph in one of two forms
(`DocxWriter.java` 6101–6113): **spendable** = `w:before = gap - 1` + a 1-twip `w:line` hairline;
**unspendable** = `w:before="0"` with the whole gap in `w:line`. Google draws `w:before` 1:1 and
`w:line` at ≈0.2156 (the 22 Nov sweep: 2880 twips → 30.2 pt), so an unspendable spacer delivers
**0.784 of its declared gap as lost height**.

Converted the four documents the previous slot measured live, on this tree, and counted the
unspendable spacers in `word/document.xml`:

| document | unspendable spacers (twips in `w:line`) | gap lost if 0.784× | step the previous slot measured in Google |
|:--|:--|--:|:--|
| `72_bank_statement_no_rules_right_amounts` | 1 × 366 (18.3 pt) | **14.35 pt** | `med_dy` **−13.0**, `worst_dy` 28.2 |
| `mobile-bill` | 3 × 248, 128, 124 (12.4, 6.4, 6.2 pt) | **9.72, 5.02, 4.86 pt** | steps **−8.76, −4.19, −4.08 pt** |
| `bus-timetable-station-left-times-right` | 1 × 127 (6.35 pt) | **4.98 pt** | `med_dy` −3.0, `worst_dy` 4.9 |
| `362_price_list_dense` | **0** | **0** | **no step**, `med_dy` −2.8, `worst_dy` 5.4 |

Three documents with unspendable spacers, three measured steps, and the three predicted magnitudes
land in the same order and within 1–2.6 pt of the measured ones (the shortfall is the +0.75 pt/row
ramp partly cancelling). The document with **zero** unspendable spacers is the one the previous
slot recorded as having **no step**. That is four for four, and it is the first time the step has
been tied to named elements instead of inferred from a run profile.

**So the class is two disjoint sub-defects, not one:**

* **A — the spacer half.** Documents carrying at least one unspendable spacer. Their error is a
  discrete step at each table top, magnitude `0.784 × declared`.
* **B — the row half.** Documents with no unspendable spacer at all. `362_price_list_dense` is one:
  29 rows × 0.75 pt = 21.75 pt of pure ramp, no step.

A change aimed at A moves nothing on B, and `362_price_list_dense` is not a falsifier of the pair —
it is a document of the other half.

## 2. Why the previous slot's pair cannot work (source, refuted)

The handoff asked for "the first-row cell `w:before` carries the table gap + `w:trHeight` declared
less by the same per-row amount, so the table's total height is unchanged". Read the emitter:

* `rowTw = round((t.bottom - t.top)/rowCount * 20)` (6226); `ruleTwHere = round((szAbove+szBelow)*20/16)`
  = **15 twips** (6389); `content = max(1, pitch - rule)` (6403); `line = max(1.25 × fontSize, content)`
  (6459); `trHeight = max(pitch, line)` (6468); written `hRule="atLeast"` (6558).
* Because `content + rule == pitch` **exactly**, and `trHeight == max(pitch, line) >= pitch`,
  `atLeast` always binds at `trHeight` — so **lowering `w:trHeight` by 15 twips lowers the declared
  minimum to `pitch - 15`, and the row is still laid at `max(declared, content + rule) = pitch`.
  The declaration change is a no-op in every renderer.** The code says so itself at 6342–6344.
* The cell's `w:before` is clamped to `min(rowHeight, content) - box` (6786–6790), roughly one row's
  content height, so a gap larger than a row is truncated rather than carried.
* Worse for the guard: `spacingTw` skips cell-level `before`/`line` (469–474), `fitPage` does not
  charge a cell (582–596) and `shaveToFit` only rewrites `depth == 0` `w:before` (515–536) — a gap
  moved into a cell becomes **invisible to every page-height guard**, so the one thing the guard
  exists to prevent (content pushed off the page) would become unobservable.

## 3. Why the spacer half is where it is, and what it would cost to move it

The unspendable form exists because spending needs page room:
`spendable = slackTw > 0 && spacerSplitTw + (spacerTw - 20) + 15×pageRowCount <= slackTw`
(6093–6100). The row excess is charged **in full** to every spacer decision, so on a page whose ink
reaches the bottom no spacer is ever spent, and the guard's own record says spending it unguarded
took `mobile-bill` and `insurance-policy-schedule` from 46/47 on one page to 43/47 on two.

There is no free parameter here. For an unspendable spacer the engine writes `before = X`,
`line = spacerTw - X`. LibreOffice draws the sum, so **any** X is LO-identical; Google draws
`X + 0.2156 × (spacerTw - X)`, which reaches the full gap only at `X = spacerTw - 1` — the spendable
form. So the choice is binary and the only currency is page room, which the row excess has already
taken.

And the row excess cannot be repaid without moving LibreOffice: the only declaration that makes
Google land at `pitch` is `trHeight = pitch - 15`, and LibreOffice then lays `max(pitch - 15, line)`
= `pitch - 15` on every pitch-bound row, i.e. up to 18 pt of shrink on a 24-row page. `regress.py`
compares LibreOffice, so it refuses that.

**Conclusion.** On this class the LibreOffice comparison and the Google goal are in direct conflict:
every candidate fix for either half is LO-visible, and the one LO-invisible move (spending the
spacer) is blocked by a page-room budget the other half has spent. This is a decision for the
ledger, not a patch — recorded in `BLOCKERS.md`.

## 4. What the next run should measure first

One Google round trip on `362_price_list_dense` with `trHeight = max(content, line - 15)` declared
**only on rows where `line > content`** (tight rows). There LibreOffice lays `max(trHeight, line) =
line` whatever the declaration, so the change is LO-invariant *by construction* — the only candidate
this run found that is — and it discriminates the two possible laws for Google's +0.75 pt/row:
if Google lays `trHeight + rule`, the ramp disappears and the document passes; if Google lays
`max(trHeight, content + rule)`, nothing moves and the law is `max`, which sends the row half to
the ledger with the spacer half.
