# The row rung is a TRADE, not a fix: +1 document clean, -2 documents worse (Google, 27 Nov)

**Status: REFUTED AS A LANDABLE CHANGE. Kept as a lead, not committed.**

Class: `18_displacement`. Engine: HEAD `a4d8fca469bba636` (baseline) vs the patched tree
(`da134318812005fc`, then `859096ae1d66d351`, then `c469b55e6991918b` as the guard evolved).

## The hypothesis, as relayed to this run

The 26 Nov build declared a table row's height on the 0.75 pt rung and left `writtenRowsTw`
charging the *declared pitch*. The claim was that only one half of the rule was ever measured, and
that the rule is a **pair**:

```
laid   = 0.75 * round((declared + rule) / 0.75)      the law, measured on 12 documents
charge = laid                                        half B: writtenRowsTw += laidTw
```

so the patch is: declare the rung, and charge the rung. The relay's stated prediction for
`303_discharge_summary` was `w:trHeight` 300 → 285, pitch 15.75 → 15.00, footer +4.10 → ≈+1.10,
verdict 47/47.

## What was measured — every number below is Google, one Drive round trip each

| document | baseline (HEAD, a4d8fca) | patched (pair, da13431) | guarded (859096a / c469b55) |
|---|---|---|---|
| 303_discharge_summary | 46/47, worst_dy **4.1** | **47/47**, worst_dy **3.0** | **47/47**, worst_dy **3.0** |
| 320_balance_sheet_statutory | 46/47, worst_dy **19.4** | 46/47, worst_dy **7.4** | (not re-run) |
| mobile-bill | 46/47, worst_dy **9.2** | 46/47, worst_dy **66.7** | 46/47, worst_dy **65.9** |
| electricity-bill | 46/47, worst_dy **28.5** | 46/47, worst_dy **48.5** | 46/47, worst_dy **47.8** |

**One document goes clean and two go worse, by 56.7 pt and 19.3 pt.** The charter's third
non-negotiable — no document gets worse — refuses this, so it was reverted and is recorded here.

The prediction was right where it fired: the footer moved by exactly 1.10 pt on 303 (4.10 → 3.00),
and 303 is now 47/47. The rule is real. Its *generality* is not.

## The inert control — this is the part that makes the regression real

The patch carries `-Dp2w.rungTw=0` as an identity switch. Converting mobile-bill with the property
off, on the **same patched tree**, and measuring that file in Google gives:

```
mobile-bill  rungTw=0 (inert)  : 46/47, worst_dy 9.2   <- reproduces the committed baseline exactly
mobile-bill  rungTw=15 (pair)  : 46/47, worst_dy 65.9
```

So the 56.7 pt movement is the patch and not the conversion pipeline, not the probe path, not the
upload. Any future run that suspects its own harness should spend one round trip on this control
before believing a number in this table.

## What the regression is NOT

Two guards were built and both failed to remove it, which is the useful part:

1. **Content-driven guard.** `hRule="atLeast"` means a row whose content needs more than the
   declaration is laid at its content, and the rung law cannot predict it. The patch was changed to
   leave such rows untouched (`mustTw > rungTw` → no declaration change, original charge).
   mobile-bill 66.7 → 65.9, electricity-bill 48.5 → 47.8. **Barely moved. Not the cause.**
2. **Per-table kill switch.** Once a table has one content-driven row, the rung path stops for the
   rest of that table (`rungDead`). Same result — the numbers above are *with* this guard.

And the declarations themselves cannot explain 57 pt: on mobile-bill the patch changed exactly five
rows, 360 → 350 twips, i.e. 0.5 pt each, 2.5 pt in total, in the direction that moves content
**up**, not down. A 0.5 pt row change produced a 56.7 pt page movement, so the movement is not
coming from the row heights at all — it is coming from what the flow after the table is charged
(half B, `writtenRowsTw += laidTw`) or from `cumLaidPt` inside the table, not from the declaration.

**Next run: bisect the halves.** The property already isolates the whole block. Split it into two
properties — `p2w.rungDecl` (half A) and `p2w.rungCharge` (half B) — and measure mobile-bill and
electricity-bill with each alone (4 round trips). If half B alone reproduces +56.7 on mobile-bill
while leaving 303 clean, the rule is two rules with different scopes and only one of them is right.

## Why this is worth more than the document it fixed

`303_discharge_summary` is 1 of 26 documents whose only failure is `18_displacement`. The class is
worth 53.2 clean documents on `classpick.py --leverage`. A patch that clears one and damages two is
a net loss, and it would have been committed as a win if it had only been measured on the document
it was predicted on — which is exactly the failure mode the brief's "one document before the build"
rule is written against, and exactly why the corpus, not the target document, is the judge.
