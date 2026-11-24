# The row-height law, and the one change that is LO-invariant

## 0. Answer in two sentences

**Law.** Google lays a table row at `0.75 pt × round( (max(w:trHeight, cell content) + the row's drawn
horizontal rule) / 0.75 )` — take the row's natural height, let the `atLeast` declaration floor it, add the
row's rule width, then snap the total to the *nearest* whole CSS pixel at 96 dpi (1 px = 0.75 pt = 15 tw).
The declaration is not laid; it is a floor that is quantised, and the rule is charged outside it.

**Change.** At `DocxWriter.java:6468`, declare the row one rule short —
`rowHeightTw = Math.max(rowLineTw, rowTwHere - ruleTwHere)` — instead of `Math.max(rowTwHere, rowLineTw)`.
LibreOffice lays `max(trHeight, content + rule)`, and HEAD already writes `content = rowTwHere - ruleTwHere`
(`:6403`), so the laid height is `max(P-r, P)` = `P` before and after: LibreOffice-identical by construction.
Google moves by exactly one pixel per row, which is the whole of the +0.75 pt/row ramp.

---

## 1. The four findings: what each refuted, and on what measurement

| finding | construct it refuted | the measurement that refuted it |
|:--|:--|:--|
| `…GOOGLE-LAYS-A-ROW-ON-WHOLE-PIXELS-0052-fixer.md` | (a) that `w:trHeight 168` lands at 8.40 pt; (b) that declaring every row a whole pixel (180 tw) is the fix; (c) its own fix as landable — the cumulative pixel snap passes Google and costs LibreOffice | (a) `362_price_list_dense`, 27 of 27 row gaps: source 8.40 pt, Google **8.25 pt**; (b) 180 tw (9.00 pt = 12 px) laid 9.00 exactly, i.e. +0.6 pt/row, still 41/42; (c) full corpus pass on the patched engine: **17 documents worse, 5 better**, `electricity-bill` 1.33→2.33 share@5, `330_cad_drawing_sheet` 4.91→5.22, `regress.py --check` and `gate.py` both refuse |
| `…GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` | (a) `hRule="exact"` making the floor bind; (b) `w:before` entering the row height; (c) `w:trHeight` being honoured as a height at all; and (d) the hairline cell box being honoured | (a) mobile-bill with `exact` where the floor binds: all 24 rows `exact`, rule gaps **identical, element for element** to `atLeast`; Google's own `.docx` read-back returns `w:hRule="atLeast"` for rows we wrote `exact` — Google normalises it away. (b) synthetic probe, floor 360, `w:before` 100→340 tw in 20-tw steps: **every row laid 19.0 pt**; and capping mobile-bill's `before` 190–210 → 163–188 tw moved **none of 26 gaps**. (c) read-back carries our `w:trHeight 360/380` and our `w:before`, yet the PDF lays 18.0/19.0/20.0 and lays a row written **380 at 18.0**. (d) `w:line="10" exact` came back as `w:line="14.399999999999999" lineRule="auto"` — the 0.5 pt box is replaced by a 14.4 pt auto line. Construct that *did* work: cell `before=0`, `w:line =` the row's height `exact` → 18.00, 18.00, 18.75 on floors 360/360/380 (mean 18.25 vs the page's 18.40) |
| `…FOUR-MECHANISMS-AND-THE-ROWPITCH-REFUTATION-1750-agent.md` | that `18_displacement` is **one** construct ("row pitch"), and that it is rule count, proportional to font size, scatter, or a LibreOffice fault | population recomputed from the JSONs: 101 fail in Google, 20 in LibreOffice, 18 in both; construct census over the 190 emitted `.docx` gives a spacer-in-`w:line` discriminator **53 failing / 0 clean**, page break 16/0, textbox 23/0, union 71/101 vs 0/30 → M1 53, M2 7, M3 11, M4 30, two arms with two different fixes. Rule count refuted by `16_right_aligned` (17 rules) and `balance-sheet` (5); font-size proportionality refuted by a flat −56 pt across 6.0 and 13.0 pt on one page (Pearson −0.68…+0.16); scatter refuted by `dy = a + b·y` with residual sd 0–5.5 pt on 28 pages; LibreOffice fault refuted by **12,308 matched LO pairs, 4.5 % out**, median 1.58 pt |
| `…STEP-IS-THE-UNSPENDABLE-SPACER-0323.md` | (a) the "first-row `w:before` carries the gap + `trHeight` reduced by the same amount" pair; (b) the step being a ramp rather than a discrete spacer loss | (a) source arithmetic, not a render: `content + rule == pitch` exactly and `trHeight = max(pitch, line) ≥ pitch`, so `atLeast` always binds at `trHeight`; lowering the declaration by 15 tw leaves the laid height at `max(declared, content+rule) = pitch` — **a no-op in every renderer**, and the code says so itself at 6342–6344. (b) four documents, four predictions, four measured steps: `72_bank` 14.35 predicted vs **−13.0** measured; mobile-bill 9.72/5.02/4.86 vs **−8.76/−4.19/−4.08**; `bus-timetable` 4.98 vs −3.0; `362` **0 unspendable spacers → no step**, med_dy −2.8 |

### Where the four contradict each other, and which side I take

1. **0052 vs the 0.75 pt ladder** (`ROW-GROWTH-075`, which FOUR-MECHANISMS quotes as the M4 law).
   0052 measured 168 tw (8.40 pt) laying **8.25** and 180 tw (9.00) laying **9.00**. The ladder law
   `0.75·(round(d/0.75)+1)` predicts 9.00 and 9.75 for those same two declarations. They cannot both hold.
   I take 0052: it is 27/27 gaps on one document, before-and-after, and the same document's own `med_dy`
   is **−2.8** — a +0.75 pt/row ramp would put the median at about +10. The ladder law's eleven points are
   all on **ruled** tables; 362's table draws no rules at all (`w:tblBorders` all `nil`). The missing term
   is the rule, and §4 shows that adding it fits all fifteen measured points on both sides.
2. **STEP's "29 × 0.75 = 21.75 pt of pure ramp"** on 362 is not supported by STEP's own quoted number for
   362 (`med_dy −2.8`, `worst_dy 5.4`). A 21.75 pt cumulative ramp cannot produce a −2.8 median. The
   sentence is an extrapolation of the ruled-table law onto an unruled table; the measured pitch of 8.25
   (0052) is the fact, and it is *negative* drift, not positive.
3. **`IGNORES` §3's mobile-bill read** (18.0/19.0/20.0, "a row written 380 at 18.0") disagrees with
   `ROW-RULE-IS-OUTSIDE-TRHEIGHT-1220`'s sums on the same document (26 gaps = 513.0 = 24×19.50 + 45 for
   declarations of 368 tw). Both are rule-position reads at ±0.5 pt resolution; the sums are the trustworthy
   form, and they are what §4 fits.
4. **0052's word "truncates"** is too strong for its own data: 8.40 → 11.2 px → 11 px and 9.00 → 12.0 px →
   12 px are the same answer under truncation and under rounding-to-nearest. The eleven ruled-table points
   distinguish them, and they say **nearest** (17.80 → 18.75 and 18.60 → 19.50 are roundings *up*).

---

## 2. Every place the engine writes `w:trHeight`

Only two writes exist in `app/src/main/java/com/kavopdf/app/engine/`. (`DocxWriter.java:448` defines the
string constant `TRHEIGHT` and `:2318`-ish read it, but `flowTwOf` only *parses* nested rows.)

| site | enclosing method | value written | `w:hRule` |
|:--|:--|:--|:--|
| `DocxWriter.java:2256-2258` | `columnPage(…)` (`:1763`) — the multi-column page layout table | `rowTw = max over cells of (flowTwOf(cellXml) + ctx.wrapDebtTotalTw)`, i.e. **exactly the cell content** (`:2241`, `:2243`) | **`exact`** |
| `DocxWriter.java:6557-6559` | `table(…)` (`:5948`) — the ordinary table, recursive for nested tables | `rowHeightTw` = `max(rowTwHere, rowLineTw)` (`:6468`), raised to `paraContentTw + ruleTwHere` on re-cut tables (`:6516`) and scaled by `ctx.squeeze` (`:6469-6473`); guarded `rowTwHere > 0` | **`atLeast`** (plus `<w:cantSplit/>`) |

`rowTwHere` is the page's pitch: `rowTw = round(extentPt / rowCount * 20)` (`:6226`), or the measured
`rowEdge[r+1]-rowEdge[r]` when `exactRows`, or the paper clip when the row straddles the sheet edge.

---

## 3. How the row's content height is computed, and whether `trHeight` can go below it

For a single-line cell the content the row must hold is `w:before + w:line` of its one paragraph
(`flowTwOf`, `:2306`), with `w:after = 0`, `w:tblCellMar` top/bottom hard-zeroed at the table (`:6202-6206`)
and `w:ind` carrying only the horizontal inset. The pieces:

* `ruleTwHere = round((szAbove + szBelow) * 20 / 16)` (`:6389`) — half of the rule above plus half of the
  rule below, 15 tw = 0.75 pt for a 0.5 pt `insideH`.
* `contentTwHere = max(1, rowTwHere - ruleTwHere)` (`:6403`), `cellLineHere = contentTwHere` (`:6407`).
* single line: `boxHere = hairlinePt(sz) = 0.069 em` (`:6747`, `:4056`) and
  `before = round(0.8·(rowLineTw − box))` (`:6803`) or, when the page's own baseline was measured,
  `before = want − 0.8·box` clamped to `capTw = min(rowHeightTw, contentTwHere) − box` (`:6786-6790`).
  So `content ≈ want + 0.2·box ≤ contentTwHere = pitch − rule`.
* several lines: `boxHere = rowLineTw` (`:6747`) and the type-size floor `rowLineTw ≥ 1.25·sz·20` (`:6444-6456`);
  `rowHeightTw = max(rowTwHere, rowLineTw)` then absorbs it.

**Does the engine ever write a `trHeight` smaller than the content it has emitted?**

* Ordinary table, single-line cells: **no, by construction.** `rowHeightTw ≥ rowLineTw` and the cell's
  content is capped at `min(rowHeightTw, contentTwHere)`; `ctx.squeeze` scales both by the same factor and
  holds both at `typeFloorTw`, and the paper-clip path caps both consistently. This is deliberate — it is
  why `hRule="atLeast"` never clips here.
* Ordinary table, **multi-paragraph cells on a table that is not `t.recut`**: **yes.** `cellParasTw`
  (the only place the stacked paragraph sum is compared with the row) is consulted *only* under `if (t.recut)`
  (`:6504-6516`). On a non-recut table with `cps.size() >= 2` the cell writes `before0 + Σ(before_q + box_q)`
  from the page's own baselines (`:6850`, `cellParaXml`), while `trHeight` stays at `max(rowTwHere, rowLineTw)`
  with `rowLineTw = min(contentTwHere, 200)` for `rowParts > 1`. The declaration is then smaller than the
  content, `atLeast` grows the row, and the row is laid at content+rule rather than at the page's pitch.
* Column layout table (`:2257`): `trHeight` **equals** the content exactly and `hRule="exact"`, so any
  renderer that measures the cell taller than the writer's sum clips rather than grows.

---

## 4. The law, its arithmetic, and what it predicts for 362

### The law

```
natural  = max(trHeight, content)          // atLeast floors the content, exact ignores it
row      = natural + r                     // r = the row's drawn horizontal rule, outside the box
laid     = 0.75 * round(row / 0.75)        // nearest whole CSS pixel at 96 dpi
```

Equivalently: the row is a whole number of pixels, the declaration is a floor that is quantised, and the
rule is charged outside the `w:trHeight` box (`ROW-RULE-IS-OUTSIDE-TRHEIGHT-1220` says the same thing
in prose: slope ~1.4 pt laid per 1 pt declared, i.e. the rule is on top).

Fitted to every Google number in the four findings and the two it quotes — 15 points, exact, no residual:

| source | declared | r | predicted | measured |
|:--|--:|--:|--:|--:|
| ROW-GRID-AND-SPACER-1518 | 17.00 | 0.75 | 18.00 | 18.00 |
| same | 17.40 | 0.75 | 18.00 | 18.00 |
| same | 17.80 | 0.75 | 18.75 | 18.75 |
| same | 18.20 | 0.75 | 18.75 | 18.75 |
| same | 18.60 | 0.75 | 19.50 | 19.50 |
| ROW-RULE-1220 (368 tw) | 18.40 | 0.75 | 19.50 | Σ513.0 = 24×19.50+45 |
| ROW-RULE-1220 (358 tw) | 17.90 | 0.75 | 18.75 | Σ495.0 = 24×18.75+45 |
| ROW-RULE-1220 (348 tw) | 17.40 | 0.75 | 18.00 | Σ477.0 = 24×18.00+45 |
| ROW-GROWTH (360/380) | 18.00 / 19.00 | 0.75 | 18.75 / 19.50 | 19.03 mean = 19.125 mix |
| IGNORES §4 probe (unruled) | 18.00 / 18.00 / 19.00 | 0 | 18.00 / 18.00 / 18.75 | 18.00 / 18.00 / 18.75 |
| 0052 (unruled) | 8.40 | 0 | 8.25 | 8.25, 27/27 |
| 0052 (unruled) | 9.00 | 0 | 9.00 | 9.00 |

The task's suggested form — *ceil* each row to a whole pixel, then add the rule — is **refuted by 0052's own
27/27 read**: ceil(11.2) = 12 px = 9.00 pt, and Google laid 8.25. The quantiser is nearest, not ceil, and
the eleven ruled-table points prove it (17.80 and 18.60 round *up*, 17.40 rounds *down*).

### The +0.75 pt/row arithmetic

A ruled row whose declaration is already on the pixel grid:

```
trHeight 360 tw = 18.00 pt = 24.00 px   (exact, no fraction)
rule     15 tw  =  0.75 pt =  1.00 px   (half the rule above + half below, 0.5 pt insideH)
row      = 18.75 pt = 25.00 px
laid     = 25 px = 18.75 pt
excess   = 18.75 - 18.00 = +0.75 pt = exactly one pixel per row
```

The excess is a whole pixel because the addition lands exactly on a boundary and the rounding cannot absorb
it. Row *n*'s top edge is `+0.75·(n−1)`; the foot of the table is `+0.75·N`. On 29 rows that is
**+21.75 pt**, which is the Half B ramp. The same arithmetic on the 380 tw rows gives 19.00 + 0.75 = 19.75 →
26 px = 19.50, i.e. +0.50 — which is why the ladder reads 0.75–1.5 pt per row rather than a constant.

### What it predicts for `362_price_list_dense`

362 is **unruled** (`w:tblBorders` all `nil`) and its rows are `w:trHeight 168` = 8.40 pt, one row of
240 tw (12.00 pt). With `r = 0`:

```
row 0     : 240 tw = 12.00 pt = 16.00 px -> 16 px = 12.00 pt   (excess 0)
rows 1-28 : 168 tw =  8.40 pt = 11.20 px -> 11 px =  8.25 pt   (excess -0.15)
laid total = 12.00 + 28 x 8.25 = 243.00 pt
declared   = 247.2 pt (0052 states the emitted sum as 4950 tw = 247.5)
foot of table: -4.2 to -4.5 pt ; row n's top edge: -0.15 (n-1)
```

**So the law predicts that 362 does not ramp +0.75 pt/row at all.** It predicts a *negative* drift of
0.15 pt/row, −4.35 pt over 29 rows, with the last row's top edge 4.2 pt high — and that is what was
measured (`med_dy −2.8`, `worst_dy 5.4`, one check, no step). The "29 × 0.75 = 21.75 pt of pure ramp" in
the brief is the ruled-table arithmetic applied to a table with no rules; the rule is the term that makes
it +0.75, and 362 does not have one. 362 is Half B only in the sense of "no unspendable spacer". Its
residual is pixel quantisation of an off-ladder pitch, and it is bounded at −4.35 pt, not cumulative at
+21.75.

Two consequences follow, and both are uncomfortable:

* An unruled table has one lever — `trHeight`, which equals its content — so **no LO-invariant change can
  move 362's rows.** LibreOffice lays `max(trHeight, content + r)`; Google lays a quantisation of the same
  two numbers. Any change that crosses a Google pixel boundary changes LibreOffice's laid height too. The
  reachable per-row ladder for 8.40 is 8.25 or 9.00 and nothing between; landing 8.40 requires mixing them
  22:6 (which is exactly what 0052 built: 165/180, sum preserved), and that is LO-visible — 17 documents
  worse, the gate refuses.
* A ruled table *does* have slack, because HEAD already writes `content = pitch − rule` (`:6403`). That is
  what makes §5's change possible.

---

## 5. The one change, and what would refute it

### The fix (the answer to the question as asked) — `DocxWriter.java:6468`

```java
// now
int rowHeightTw = Math.max(rowTwHere, rowLineTw);
// proposed
int rowHeightTw = Math.max(rowLineTw, rowTwHere - ruleTwHere);
```

* **LibreOffice: identical, by construction, not by measurement.** LO lays a row at
  `max(trHeight, content + rule)` (the engine's own 404_sudoku_grid measurement, `:6313`). HEAD: content =
  `P − r`, so LO lays `max(P, P) = P`. Proposed: `max(P − r, P − r + r) = max(P − r, P) = P`. Same number,
  same cell baselines (they are placed from `rowLineTw`, untouched), same `writtenRowsTw` charge (`:6477`
  is unchanged), same flow anchor after the table. One emitted integer changes and nothing else.
* **Google: one pixel per row.** `max(trHeight, content) + r` becomes `P` instead of `P + r`, so
  `round_px(P)` replaces `round_px(P + r)`: 18.00 instead of 18.75, 19.00 instead of 19.50. The +0.75/row
  ramp disappears at its source.
* It is a **no-op on 362** (`r = 0`), and a no-op on every unruled table. It cannot be tested on 362. It must
  be tested on a ruled Half B document — `mobile-bill` (insideH sz 4, rows 360/380, 24 rows) or
  `electricity-bill` (18.4 pt rows, 0.5 pt rules), the two documents `0052` and `ROW-RULE-1220` used.
* It supersedes `ROW-RULE-1220`'s patch only in the sense that it is the *same* idea (net the rule out of
  the declaration) applied against the current tree, where the cell's line has already been cut by the rule.
  That finding subtracted two rules because its tree still had the cell's line at the pitch; at HEAD one
  rule is the right subtraction and the change is LO-neutral, which that build was not.

### The one probe a single round trip on 362 can decide

Since 362 cannot test the fix, the change to run on it is the one that decides whether the *declaration*
or the *content* is what Google quantises — the question that decides whether the fix above is the whole
answer or a half of it.

```java
// DocxWriter.java:6403, on this table only (an env flag is enough for a probe)
int contentTwHere = rowTwHere > 0 && ruleTwHere > 0
        ? Math.max(1, rowTwHere - ruleTwHere - 15)     // -15 tw = -0.75 pt = -1 px
        : rowTwHere;                                    // 362 is unruled: force 168 - 15 = 153
```

`trHeight` stays at 168. The cell's `w:line` drops from 168 to 153 tw.

* **LibreOffice-invariant:** LO lays `max(168, 153) = 168` — the same row, to the twip. This can be checked
  with soffice before any Drive call, so the change cannot be refused by `regress.py` for being LO-visible.
* **Prediction (accept):** nothing moves. 362 stays 41/42 with `med_dy ≈ −2.8` and `worst_dy ≈ 5.4`; every
  row still 8.25 pt. That confirms the row is governed by the declaration and that the +0.75 ramp is the
  rule term — i.e. the §5 fix is the right one.
* **Refutation:** the rows shorten. If each row lays 7.50 pt (10 px), row *n*'s top edge is `−0.75·(n−1)`,
  the foot of the table is **−21.0 to −21.75 pt** high, `med_dy` goes to about −13 (0052's own run already
  has a −13.59 number for this document, from its spacer), `worst_dy` exceeds 20 and 362 loses checks. That
  result kills the declaration term: the row would be content-quantised, `w:trHeight` would be a pure
  no-op, and the fix would have to move *both* numbers — which brings back the LibreOffice cost of 0052 and
  puts the row half in the ledger with the spacer half.

One round trip, one integer, two outcomes, and the outcome decides which of the two laws the engine is
allowed to act on.
