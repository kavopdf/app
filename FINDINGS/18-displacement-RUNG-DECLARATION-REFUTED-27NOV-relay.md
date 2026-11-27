# `18_displacement`: declaring the row's laid height on the 0.75 pt rung — REFUTED as a clean-maker

**27 Nov 2026, 06:05 IST · fixer run (relay) · engine built `b727bedee872a7b8`, reverted to `a4d8fca469bba636`**

The candidate this run was the one `FINDINGS/18DISPLACEMENT-COUNT-0125-27NOV.md` §6 proposed and never built:
**declare the row height the renderer will actually lay, net of the row's rule, on the renderer's own
15-twip grid, and charge that same number to the page budget.** Its model said 10 documents become CLEAN.

It was built, and measured in Google on the two documents that finding used as its worked examples. **It
clears neither. The 0.75 pt law is confirmed; the fix built on it does not move the check.**

## What was built

`DocxWriter.java`, `emitTable`, after the squeeze block at `:6545` and before the write at `:6631`
(full diff: `FINDINGS/18-displacement-RUNG-DECLARATION-27NOV.patch`, 41 lines):

```java
final int RUNG_TW = 15;
int wantTw  = Math.max(rowTwHere, Math.max(rowHeightTw, rowLineTw) + ruleTwHere);
int laidTw  = RUNG_TW * Math.round(wantTw / (float) RUNG_TW);
rowHeightTw = Math.max(typeFloorTw, laidTw - ruleTwHere);
...
writtenRowsTw += Math.max(0, laidTw);          // was max(pitchTwHere, max(rowTwHere,rowLineTw)+ruleTwHere)
```

A first version also floored `laidTw` at `typeFloorTw + ruleTwHere`. That floor was removed before the
measurement below: the floor belongs on the height the renderer *lays*, not on the declaration, because
`max(w:trHeight, content + rule)` already protects the content.

## What changed in the file

Declared `w:trHeight`, HEAD vs patched, read out of `word/document.xml`:

| document | HEAD | patched | predicted by §6 |
|:--|:--|:--|:--|
| `303_discharge_summary` | 300 ×5 rows | **307 ×5** | 285 |
| `16_right_aligned_amounts_txtpos` | 380 ×12 | **375 / 380 alternating** | 375 |
| `report-2col-table-spanning-both-columns` | not cached | 365 / 380 | 340 |
| `362_price_list_dense` | not cached | 240 / 168 | — |

**`303` did not go to 285.** Its `typeFloorTw` — `rowLineTw` before the `rowCapTw` clamp, i.e. the type's
own line box at `sz × 1.25` — is **307 twips**. So on `303` the row is *content-bound in the engine's own
model*, not `trHeight`-bound, and `Math.max(typeFloorTw, …)` pins the declaration at 307. The §6 model
sampled the cell content as ≤ 15.0 pt and called the row `trHeight`-bound; the engine's own floor says
15.35 pt. **The 10-document model rests on that classification, and on its two worked examples the
classification is wrong.**

## The measurement — Google, before and after

Built from HEAD with the patch, converted with `ConvertOne`, imported through
`GOOGLEDRIVE_CREATE_FILE` (`mimeType=application/vnd.google-apps.document`), exported as PDF by Google,
scored by `gverify.py --collect`. The four probe documents were deleted from Drive after scoring.

| document | before (engine `a4d8fca469bba636`) | after (engine `b727bedee872a7b8`) | verdict |
|:--|:--|:--|:--|
| `303_discharge_summary` | 46/47, fail `18_displacement`, med_dy **-0.2**, worst_dy **4.1** | 46/47, fail `18_displacement`, med_dy **-0.2**, worst_dy **3.8** | no change to the verdict |
| `16_right_aligned_amounts_txtpos` | 41/42, fail `18_displacement`, med_dy **-1.6**, worst_dy **3.4** | 41/42, fail `18_displacement`, med_dy **-1.6**, worst_dy **3.4** | **identical to 0.1 pt** |

Neither document becomes clean. `303`'s worst_dy falls 0.3 pt and its median does not move; `16` is
unchanged in every field the store records.

## What this run did establish — the law, by a route the earlier fit did not use

`16_right_aligned` is the clean confirmation. HEAD declares **380** twips and the patched engine declares
**375**. `15 × round(380/15) = 15 × 25 = 375` and `15 × round(375/15) = 375`, so both declarations must lay
the same height — and the Google render is identical on every run, med_dy -1.6 and worst_dy 3.4 in both
arms. **A 5-twip change of declaration that crosses no rung produced no change in the render.** That is the
0.75 pt grid observed directly, on a document where the earlier fit inferred it from a ramp.

So the law in `18DISPLACEMENT-COUNT-0125` §5 stands. What is refuted is the step from the law to a clean
document: making the declaration land on a rung removes at most half a rung (0.375 pt) per row, and the
residual these documents fail on is not that.

## Why the fix cannot work on `303` — the arithmetic

`303`'s declared box is now 307, so the renderer takes `max(307, content + rule)`. For the declaration to
control the laid height, `content + rule` must be ≤ 307. It is not: the engine's own type floor is 307 and
the rule is 15, so `content + rule = 322`, and the renderer lays `15 × round(322/15) = 315` — the same 315
it laid from a 300 declaration. **The declaration was never the binding number on this document.** The
+0.75 pt per row the finding measured on `303` is the row's own line box exceeding its declared pitch, not
the declaration's rounding, and no choice of declaration removes it.

## What to try instead, in order

1. **`303`'s residual is `typeFloorTw > rowTwHere`** — the engine declares a row *shorter* than the line box
   it says the row needs (`rowHeightTw = max(rowTwHere, rowLineTw)` uses the **clamped** `rowLineTw`, not
   `typeFloorTw`). That is a defect in its own right and it is not the rung. Measure it before patching it.
2. **The flow-line hairline term** (`18DISPLACEMENT-COUNT-0125` §8, `hairlinePt()` `:4113` written by
   `spacing()` `:149-154`) is the untouched second-order term and the finding itself names it next.
3. Do **not** rebuild the rung rule as a clean-maker. It is measured and refused on its own worked examples.

## The patch, kept for the run that wants to measure the rest

`FINDINGS/18-displacement-RUNG-DECLARATION-27NOV.patch` is the exact 41-line diff that produced the numbers
above, applicable to `DocxWriter.java` at HEAD. It is not applied. Two of the ten documents it was meant to
clear are measured and do not clear; the other eight are unmeasured, and a change that clears nothing on its
two headline documents does not earn a 213-document rebuild.
