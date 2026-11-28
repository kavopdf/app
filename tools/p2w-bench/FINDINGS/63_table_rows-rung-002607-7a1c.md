# 63_table_rows — is `rowHeightTw -= ROW_RUNG_UNDER_TW` a bug or a compensation?

Measured 28 Nov 00:20–00:26 UTC on `main` (c8056b8d), engine built by `pod-prep.sh`, no engine
change committed. Variants were compiled in a scratch copy outside the repo
(`/scratch/work/var0`, `/scratch/work/var5`) and run through `ConvertOne`; the repository tree
was not modified.

## 1. The verdict, one sentence

**A deliberate compensation — for Google Docs' row-height rounding, not for the page — that is
exactly wrong in Word/LibreOffice: it shortens every roomy pitch-bound row by 0.50 pt, and the
shortfall accumulates as a straight ramp of 0.50 pt per row (12.50 pt at the bottom of a 26-row
table), so removing it puts the rows where the PDF puts them in a normal renderer and overshoots
only in Google.**

## 2. What the decrement actually touches (not "every table row")

`DocxWriter.java:6601` is gated three ways:

```java
boolean pitchBinds = rowLineTw <= rowTwHere;
...
if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW) rowHeightTw -= ROW_RUNG_UNDER_TW;
```

`footRoom` requires the row's lowest baseline to leave `FOOT_ROOM_MIN_TW = 100` tw (5 pt) under it.
Measured on five table documents, converting each three times (rung 10 = HEAD, 5, 0) and diffing
`w:trHeight` in `word/document.xml`:

| document | rows declared | rows the rung touched | Σ trHeight rung=10 | Σ rung=0 | Δ |
|---|---|---|---|---|---|
| table-with-no-header-row | 26 | **26** | 9300 tw | 9560 tw | **13.00 pt** |
| mobile-bill | 24 | **24** | 8580 tw | 8820 tw | **12.00 pt** |
| 42_table_coloured_header_alternating_rows | 8 | 0 | 3200 tw | 3200 tw | 0 |
| 56_table_indented_from_margin | 9 | 0 | 3240 tw | 3240 tw | 0 |
| price-list-2col-dense-right-aligned | 41 | 0 | 13360 tw | 13360 tw | 0 |

So the population is **pitch-bound rows with foot room**, not all rows: 50 rows in 2 of these 5
documents, 0 in the other 3. Per-row declarations on the affected pair are 350/370 tw
(17.50/18.50 pt) with the rung, 360/380 tw (18.00/19.00 pt) without — the 5-row pattern sums to
1790 tw = 89.5 pt with the rung and 1840 tw = **92.0 pt = 5 × 18.40 pt** without it. 18.40 pt is
the page's own pitch on these tables; the rung is the only reason the declaration is not it.

## 3. The measurement: PDF y vs rendered .docx y

Both `.docx` variants rendered with `soffice --headless --convert-to pdf`; y is the top of the
line's bbox from PyMuPDF, lines matched **by text**, not by index (215/215, 112/112, 51/51, 61/61
lines matched). `Δ = docx y − PDF y`; negative is high.

| document | row / line | PDF y | rung=10 y | Δ rung=10 | rung=0 y | Δ rung=0 |
|---|---|---|---|---|---|---|
| table-with-no-header-row (table starts y≈91, top of page) | line 3 (table row 1) | 91.38 | 92.00 | **+0.62** | 92.00 | **+0.62** |
| " | line 10 (table row 8) | 91.38 | 92.00 | +0.62 | 92.00 | +0.62 |
| " | line 53 (table row 51) | 201.78 | 199.40 | −2.38 | 202.40 | +0.62 |
| " | line 107 (table row 105) | 330.58 | 324.70 | **−5.88** | 331.20 | **+0.62** |
| " | line 161 (table row 159) | 440.98 | 432.10 | −8.88 | 441.60 | +0.62 |
| " | line 214 (below the table) | 811.41 | 799.60 | **−11.81** | 812.10 | **+0.69** |
| mobile-bill (table starts y≈80) | line 10 | 97.78 | 98.30 | +0.52 | 98.80 | +1.02 |
| " | line 56 | 285.33 | 281.80 | −3.53 | 286.30 | +0.97 |
| " | line 84 | 415.78 | 410.40 | −5.38 | 417.40 | +1.62 |
| " | line 111 (last line) | 811.41 | 802.60 | **−8.81** | 813.10 | **+1.69** |
| **56_table_indented_from_margin** — table starts **y≈210, well down the page** | line 25 | 282.48 | 286.70 | +4.22 | 286.70 | +4.22 |
| " | line 48 | 518.43 | 520.00 | +1.57 | 520.00 | +1.57 |
| **42_table_coloured_header_alternating_rows** — table starts y≈145 | line 30 | 225.28 | 230.00 | +4.72 | 230.00 | +4.72 |
| " | line 58 | 431.98 | 433.50 | +1.52 | 433.50 | +1.52 |

Read the two halves of that table against each other:

* **Where the rung is live** (first two documents): the first row is placed correctly (+0.62) and
  the error grows linearly with row index — +0.62 → −2.38 → −5.88 → −8.88 → −11.81 over 26 rows.
  That is a **per-row drift of 0.50 pt**, not an offset. At rung=0 the same rows read
  +0.62 … +0.62 … +0.69: a **constant offset**, no drift.
* **Where the rung is inert** (56_, 42_ — tables lower down the page, `pitchBinds` or `footRoom`
  false): the deltas are identical under both variants (+4.22/+1.57 and +4.72/+1.52) and do not
  ramp. Those are the engine's separate cell-top/`w:before` error, which the other finding owns;
  they are the control that proves the ramp above is the rung and nothing else.
* Constant offset vs drift is therefore cleanly separated by the rung itself: the offset survives
  rung=0, the ramp does not.

## 4. The git evidence — what the decrement was for

`git log -S ROW_RUNG_UNDER_TW` → introduced by **8fb4f503**, *"p2w fixer 27nov: table gap spent as
w:before (70%), pitch-bound rows declared 10 twips under, gated on 5 pt of room under the row's own
text"* (Fri 27 Nov 02:13:46 2026). It claims to fix, verbatim:

> mobile-bill 46/47 -> 47/47 and electricity-bill 46/47 -> 47/47 in Google.
> Measured: 4 declarations on mobile-bill (340/350/360/380 -> 18.15/18.40/19.15/19.90 pt against a
> page pitch of 18.40); ... 70% of the gap the point where both documents come out clean
> (60% -0.99 FAIL, 70% +0.49 PASS, 100% +4.70 FAIL).

The in-code comment at 6601 is explicit that the blanket form was tried and refused:

> The blanket form was measured and refused: -10 twips on every row of
> price-list-2col-dense-right-aligned took it 41/42 -> 40/42 by turning 46_text_crossing_rule
> 0 -> 2.

And the four declarations are the whole story: 340→18.15, 350→**18.40**, 360→19.15, 380→19.90.
The mapping from declaration to laid height in Google is not the identity — declaring 0.90 pt
*under* the pitch is what lands a row *at* the pitch. That is a compensation, with a measured
reason, for a renderer that lays an `atLeast` row taller than declared.

The reason it is still in the tree, after two attempts to revert it, is on the record:

* **8ce691d8** (27 Nov 18:25): "rung=0 restores 4 docs digit for digit" — table-with-no-header-row
  47.48 → 0.61, boq 0.62, electricity-bill 1.33, mobile-bill 1.55, all four reproducing
  `RANKING.csv`.
* **37be1707** (27 Nov 21:55): bisected the 84 LibreOffice regressions to this one constant,
  `-Dp2w.rung=0` → table-with-no-header-row 47.48→0.61, very-long-single-column-table
  41.14→2.38, boq 41.95→0.62, balance-sheet 36.69→0.21, electricity-bill 36.78→1.33,
  mobile-bill 30.09→1.55.
* **6865f403** (27 Nov 23:01): the Google cross-check, both directions — rung=0 rebuilt,
  uploaded, Drive-exported, scored: **46/47 on both mobile-bill and electricity-bill, failing
  18_displacement**. So rung=10 is clean in Google and 30.09/36.78 in the LibreOffice proxy, and
  rung=0 is 1.55/1.33 in the proxy and dirty in Google. Verdict recorded: "the revert must not be
  landed."

The recorded Google numbers at HEAD back this up: `benchmarks/gverify/mobile-bill.json` (engine
a05b20eb, 27 Nov 14:46) reads `47/47`, `med_dy 0.1`, `worst_dy 3.2`, 112 runs matched. In Google,
with the decrement, the rows are where the PDF puts them.

**So both halves of the question are true, in different renderers.** Removing the decrement makes
the rows land where the PDF puts them in Word/LibreOffice (§3) and makes them overshoot in Google
(6865f403). It is not a bug in the sense of "no reason behind it" — the reason is measured and
written down — but it is a single constant serving one renderer's quirk, and it costs 84 documents
on the live `p2w.py` gate, which renders through LibreOffice.

## 5. What would prove me wrong

1. **A Google export of table-with-no-header-row (or any rung-live table) with rung=0 showing the
   rows landing HIGH, not low** — i.e. the last row more than ~12 pt above the PDF's, matching the
   LibreOffice ramp in sign. That would make the decrement a fix rather than a Google-only
   compensation, and this finding wrong.
2. **A Google export at rung=10 of table-with-no-header-row** showing `med_dy` ≈ −12 pt or a
   `18_displacement` failure. The two documents that carry the compensation are mobile-bill and
   electricity-bill; neither is the 26-row table this finding measures, and that table's Google
   behaviour is **not stated anywhere in the repo**. If it drifts in Google too, the rung does not
   buy it anything and the 84 regressions are unopposed.
3. **`w:trHeight` being ignored by Google for rows whose cell paragraph is a degenerate exact line
   of 10 tw** (which is what the engine writes: `w:line="10" w:lineRule="exact"`,
   `w:before="194"`). If Google's laid height for such a row were exactly the declaration,
   `med_dy` on mobile-bill would be −0.9 and it is +0.1, so this is already contradicted by the
   record — but a second document would make it safe.
4. **A LibreOffice build that does NOT lay an `atLeast` row at its declaration.** My reading of the
   LibreOffice half depends on the rendered row height following `trHeight` here, because the
   content is 0.5 pt tall. It does: the rung=0 render's row pitch is 18.40 pt against the rung=10
   render's 17.90, and the whole bottom-of-table difference (12.50 pt) equals the declaration
   difference (13.00 pt less the one row whose own top does not move). A renderer that inflated the
   declaration would show no difference at all between the two `.docx` files, and it does.

## 6. If it is a bug: does removing it, or halving it, keep the total height right?

**Removing it: yes in LibreOffice, no in Google. Halving it: no in either — it keeps exactly half
the error in both directions.**

Arithmetic, table-with-no-header-row, 26 rows, pitch 18.40 pt:

```
declared total, rung=10 : 9300 tw / 20 = 465.00 pt
declared total, rung=0  : 9560 tw / 20 = 478.00 pt
page's own total        : 26 x 18.40  = 478.40 pt      (the 5-row pattern 360+360+380+360+380
                                                         = 1840 tw = 92.00 pt = 5 x 18.40)
difference              : 9560 - 9300 = 260 tw = 13.00 pt = 26 x 0.50
```

Measured at the bottom of the page, and this is the number that decides it:

```
rung=10 : 799.60 vs PDF 811.41  ->  -11.81 pt   (= 25 x 0.50; row 1's own top does not move,
                                                  only the 25 rows below it inherit its 0.50)
rung=0  : 812.10 vs PDF 811.41  ->   +0.69 pt   (constant offset, no ramp)
swing   : 812.10 - 799.60 = 12.50 pt = 25 x 0.50
```

So removing the decrement does **not** overshoot by 0.50 × N in a renderer that honours the
declaration — it lands the table, and the residual is the +0.69 pt constant that the three
rung-inert documents also show (§3). The "overshoot" reading is only true of Google, and only
because Google lays the row ~0.9 pt taller than it is declared (mobile-bill, 8fb4f503).

Halving (`ROW_RUNG_UNDER_TW = 5`) was built and measured, and it is the worst of the two:

```
row 107 : rung=10 -5.88, rung=5 -2.58, rung=0 +0.62   (midpoint of -5.88/+0.62 is -2.63)
row 214 : rung=10 -11.81, rung=5 -5.51, rung=0 +0.69  (6.25 pt short at the bottom)
row 161 : rung=10 -8.88,  rung=5 -4.08, rung=0 +0.62
```

Exactly half the ramp at every row, so it keeps half the 0.50 pt/row loss in LibreOffice and — if
the Google mechanism is a rung the declaration is snapped up to — would put the Google rows half a
rung the other way. A constant that has to be 10 for one renderer and 0 for the other cannot be
fixed by interpolating it; it needs to be conditional on the renderer, or dropped and the 2 Google
documents paid for.

## 7. For the fixer

* Do not change this line in isolation. `rung=0` is measured: it restores table-with-no-header-row,
  boq, balance-sheet, very-long-single-column-table, electricity-bill and mobile-bill in the
  LibreOffice gate, and it costs mobile-bill and electricity-bill their 47/47 in Google.
* The decrement is not "every table row half a point short" — it is 50 rows across 2 of 5 sampled
  table documents, and 0 rows wherever `pitchBinds`/`footRoom` are false. Any claim of a 0.50 × N
  shortfall must name a document where the rung is live.
* The +0.62/+0.69 constant that survives rung=0, and the +1.5…+4.7 offsets on the two rung-inert
  documents, are a different defect (cell top / `w:before`), and are not this one.

## 8. Reproduce

```bash
bash tools/p2w-bench/pod-prep.sh
# variants, outside the repo, so no engine line is changed here
cp -r app/src/main/java /scratch/work/var0/src
sed -i 's/ROW_RUNG_UNDER_TW = 10;/ROW_RUNG_UNDER_TW = 0;/' \
    /scratch/work/var0/src/com/kavopdf/app/engine/DocxWriter.java
cp -r tools/engine-verify/out /scratch/work/var0/out
cd tools/engine-verify && javac -nowarn \
  -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
  -d /scratch/work/var0/out $(find /scratch/work/var0/src -name '*.java') ConvertOne.java
# convert + render + match lines by text (see §3); rung=10 is the unmodified tools/engine-verify/out
soffice --headless --convert-to pdf --outdir pdf0 m/0/*.docx
```
