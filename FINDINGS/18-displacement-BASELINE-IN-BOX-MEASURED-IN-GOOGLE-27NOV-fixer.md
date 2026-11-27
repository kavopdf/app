# 18_displacement: the baseline inside the hairline box, measured in Google, and REFUTED as a general fix

**27 Nov 2026 · fixer run (10:05 slot) · engine `74a152e7d3fb3d26` / `d28ca7516c3f9165`**

Every number below came from a command run in this slot. Where the number is Google's it was taken
from a Google Doc export of the built `.docx`, matched line by line against the source PDF. Where it is
LibreOffice it is labelled proxy.

---

## 1. What was measured first: how far, and in which direction

`gverify.py --collect` on the built corpus document, exported from a real Google Doc:

| document | Google | fails |
|:--|:--|:--|
| `31_times_body_arial_headings` | **41/42** | `18_displacement` |

Then the export was matched against the source PDF (`PyMuPDF`, text of each line, first occurrence per
string, top of the line box):

```
src lines 29  google lines 25  matched 20
dy median +2.755   min +0.58   max +3.59        (positive = the built text sits LOWER than the page)
```

So the defect is a **downward displacement of about 2.75 pt**, and it is roughly a constant with a slow
growth of ~0.07 pt/line. LibreOffice scores the same document **42/42** — the proxy does not see it at
all, which is why 105 attempts on this class have been spent without a verdict.

## 2. The hypothesis, and why it looked right

`DocxWriter.LINE_BASE = 0.8` says the baseline sits `0.8 * box` below the box top. The corpus's flowing
line is not a normal box: it is the **hairline** `w:line = 13` twips `exact` (0.65 pt) — written that way
deliberately so Word and Google agree on the *advance* (the class comment at `DocxWriter.java:83-101`
derives `w:line = 1.38 * size` for exactly that). For a 10.5 pt line:

```
engine model : baseline = 0.8 * 0.65 pt  = 0.52 pt below the box top
renderer     : baseline = 0.312 * 10.5 pt = 3.28 pt below the box top      (measured, see below)
gap          = 2.76 pt                                                     -> the measured +2.755
```

The gap matches the measurement to 0.005 pt, which is why this looked like the answer.

## 3. Four arms, measured in Google, on `31_times_body_arial_headings`

Each arm was built, uploaded, converted to a Google Doc, exported as PDF, and matched against the
source PDF the same way. All four are 1 page.

| arm | construct | dy median | dy min | dy max | verdict |
|:--|:--|--:|--:|--:|:--|
| A | HEAD (`w:line=13 exact`, `LINE_BASE=0.8`) | **+2.75** | +0.58 | +3.59 | baseline |
| B | `-Dp2w.lineRule=auto` (`w:line=240 auto`) | **+4.57** | -1.20 | +7.58 | **REFUTED** — worse in the median *and* double the spread |
| C | `w:before` reduced by the gap, every paragraph | **-34.50** | -61.35 | -1.05 | **REFUTED** — `w:before` is a *gap*, so the correction accumulates: ~12.5 lines x 2.76 pt |
| D | the gap moved from `w:before` **into** `w:line` | **+1.71** | -0.50 | +2.55 | improves, does not zero |

Arm C is the trap worth recording. The displacement is ~constant down the page, which makes "subtract
2.76 pt from every `w:before`" look right; it is not, because `w:before + w:line` is the advance, so
subtracting from `before` shifts line *n* by *n* x 2.76 pt. **A constant offset in the render must be
corrected once per advance, not once per paragraph.**

Arm D was designed to avoid exactly that: moving `d` twips out of `w:before` and into `w:line` leaves
`w:before + w:line` — the advance — **unchanged**, and only lifts the box top. It is the only arm that
improved, and it left the page count at 1.

## 4. Arm D scored 42/42 — and then was refuted where it counts

Arm D on `31_times_body_arial_headings` scored **GOOGLE 42/42** (`failed: []`, `displacement.med_dy
1.7`, `worst_dy 2.5`, `runs_matched 29`). One document went from failing to CLEAN.

So the construct was written into the engine (`BASELINE_EM = 0.312`, the same swap, in `spacing()`'s
exact branch — patch kept at `FINDINGS/18-displacement-BASELINE-EM-SWAP-REFUTED-27NOV.patch`, engine
reverted after) and measured on **five more** documents that also fail only `18_displacement` on this
engine:

| document | before (stored, this engine) | after the change (Google, measured now) |
|:--|:--|:--|
| `31_times_body_arial_headings` | 41/42 | **42/42** |
| `10_stamp_as_image` | 41/42 | 41/42 — `18_displacement` |
| `22_invoice_four_columns_txtpos` | 41/42 | 41/42 — `18_displacement` |
| `320_balance_sheet_statutory` | 46/47 | 46/47 — `18_displacement` |
| `303_discharge_summary` | 46/47 | **45/47 — `18_displacement`, `59_shape_anchor`** |
| `33_sans_nondefault_body` | 41/42 | **40/42 — `18_displacement`, `59_shape_anchor`** |

**One document became clean; four did not move; two got worse and one of those gained a NEW failing
check.** By the charter's rule 3 that is a regression, and by rule 2 the construct is refused. The
engine is back at HEAD; the patch is kept for the next run to read, not to apply.

## 5. What this leaves true, and what it leaves open

True:

- The displacement on `31_times_body_arial_headings` is **+2.755 pt median, downward, Google-only**
  (LibreOffice 42/42 on the same file). It is now a measured number, not an inference.
- `-Dp2w.lineRule=auto` is **worse in Google** (+4.57 median, spread 8.8 pt) — it is not the escape
  hatch this class has been looking for.
- A per-paragraph subtraction from `w:before` **accumulates** and is unusable.
- The `before -> line` swap at `BASELINE_EM = 0.312` **clears this one document and regresses two
  others**, so the residual is not one constant and the swap alone is not the fix.

Open, and the first thing the next run should measure:

1. **The residual after arm D is +1.71 pt, not 0.** The swap moved the median by only 1.04 pt where the
   arithmetic predicted 2.76 pt. So Google does not place the baseline at a fixed fraction of the *box*
   either — the effect of a taller box is partial. Sweep `-Dp2w.baselineEm` (the property the patch
   adds) over, say, 0.20 / 0.312 / 0.45 / 0.60 on **two** documents, one of which is not
   `31_times_body_arial_headings`, and score each in Google. A construct that only clears the document
   it was derived on is the exact failure mode above.
2. **Why `59_shape_anchor` appears.** Both documents that gained it carry shapes near text. A change to
   where a text box's baseline sits moves every anchored shape's reference too. Any future baseline
   construct has to be scored against `59_shape_anchor` on the same batch, not only against
   `18_displacement`.
3. **`31_times` has ~0.59 pt of headroom** (its `worst_dy` after arm D is 2.5 pt and it passes, while
   HEAD's median is 2.75 pt and it fails). A one-document pass on this check is not evidence of a fix;
   the tolerance is tight enough that any arm must be scored on at least five.

## 6. Method, stated without naming a class

**When a render moves text, measure the absolute y of each line against the page, not the pitch between
lines.** A pitch measurement is blind to a constant offset — this is the same lesson the previous run
wrote down for rules, arriving from the text side.

**And when a constant offset is found, check whether the field you are correcting is a position or a
gap before you subtract from it.** `w:before` is a gap. Subtracting a constant from a gap multiplies the
correction by the line index, and the resulting build is worse than the one you started from by an order
of magnitude (-34.50 pt against +2.75 pt).

**A construct must be scored on documents it was not derived on.** The derivation document passed. Four
of five others did not, and two regressed.
