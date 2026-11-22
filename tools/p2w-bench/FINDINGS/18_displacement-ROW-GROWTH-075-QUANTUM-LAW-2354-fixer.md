# 18_displacement — what the row declaration must be so Google lays 18.40 pt: the laid height is a 0.75 pt ladder, and 18.40 is not on it

**23 Nov 2026 · measurement-only slot · engine `kavopdf/app` at HEAD, built in-sandbox with
`tools/p2w-bench/build-engine.sh` · both blockers converted with `tools/engine-verify/ConvertOne.java` ·
NO Google round trip this slot — every Google number below is quoted from a live measurement already in
`FINDINGS/` and is re-derived here from the `.docx` XML**

Documents: `mobile-bill` and `insurance-policy-schedule`, from the corpus release
(`gh release download corpus-v1 --repo kavopdf/app`, unpacked to `/scratch/work/p2w/corpus`), converted
with HEAD. Both are one page; `mobile-bill` 3 tables / 24 rows, `insurance-policy-schedule` 3 tables /
22 rows.

---

## 1. What the engine actually writes, from the XML

Every row of both documents, without exception, carries these declarations.

**Row (`<w:trPr>`)** — alternating, from `DocxWriter.java:6228` + `:6318`:

| emitted | pt | count, `mobile-bill` | count, `insurance-policy-schedule` |
|:--|--:|--:|--:|
| `<w:trHeight w:val="360" w:hRule="atLeast"/>` | 18.00 | 15 | 14 |
| `<w:trHeight w:val="380" w:hRule="atLeast"/>` | 19.00 | 9 | 8 |

Both documents also emit `<w:cantSplit/>` on every row.

**Cell paragraph (`<w:pPr>`)** — one paragraph per cell, no cell in either document wraps
(the engine writes the hairline `w:line` only when `rowParts == 1` — `DocxWriter.java:6507-6509`):

```
<w:pStyle w:val="TableText"/><w:snapToGrid w:val="0"/>
<w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
           w:before="186..210" w:after="0" w:line="10" w:lineRule="exact"/>
<w:ind w:left="…"/>
```

`w:before` takes one of seven values, `186 / 190 / 194 / 198 / 202 / 206 / 210` tw = **9.30 – 10.50 pt**.
`w:after` is 0. `w:line="10"` = 0.5 pt exact, which is `hairlinePt(7 pt) = 0.069 em` (`DocxWriter.java:3875`,
`:6509`) — the hairline box, not a line advance.

**Run (`<w:rPr>`)** — `rFonts Arial`, `w:sz w:val="14" w:szCs w:val="14"` → **7.00 pt**. (Four runs at
`sz=12` and four at `sz=13` appear in `mobile-bill`, two at 13 in `insurance-policy-schedule`, all
outside the ruled rows; the ruled cells are uniformly `sz=14`. The `sz=2` runs are the table spacers.)

**Table (`<w:tblPr>`)** — the cell margins are **already zero**:

```
<w:tblCellMar><w:top w:w="0"/><w:left w:w="0"/><w:bottom w:w="0"/><w:right w:w="0"/></w:tblCellMar>
<w:tblBorders> … <w:insideH w:val="single" w:sz="4"/> … </w:tblBorders>   (sz 4 = 0.5 pt)
<w:tblLayout w:type="fixed"/>
```

`w:tcBorders` appear on 13 cells of `mobile-bill` and 12 of `insurance-policy-schedule`, all
`w:bottom w:sz="7"` = 0.875 pt — the heavier header separators.

**The engine's own arithmetic** (`DocxWriter.java:6149`, `:6219`, `:6228`):

```
ruleTwHere   = round((szAbove + szBelow) * 20 / 16) = round((4+4)*20/16) = 10 tw = 0.50 pt
rowLineTw    ≥ round(sz * 1.25 * 20)                = round(7.00 * 1.25 * 20) = 175 tw = 8.75 pt
rowHeightTw  = max(rowTwHere, rowLineTw)            = max(360|380, 175)      = 360 | 380 tw
```

**The content the row has to hold, in Google's own terms** — the engine states Google's cell-box rule at
`DocxWriter.java:6450` (and `:79`): `Google charges max((w:line/240) * lineHeight(face, size), 0.069 * size)`.
For this XML:

```
box  = max((10/240) * 1.15 * 7.00, 0.069 * 7.00) = max(0.336, 0.483) = 0.483 pt
content = w:before + box + w:after = 9.30..10.50 + 0.483 + 0 = 9.78 .. 10.98 pt
```

So the tallest cell content in either document is **10.98 pt inside an 18.00 pt declaration**. The row is
7 pt of empty space holding a 10.2 pt paragraph; the baseline sits at `before + 0.8*box ≈ 10.09 pt` below
the row's top edge, i.e. 0.548 of the 18.40 pt pitch — which is where the page draws its cell text.

**Consequence, and it kills a standing explanation: the content never binds.** There is no "natural cell
height" of 19.10 pt. `max(declared, content) = declared` on every row of both documents, by a margin of
7 pt. Everything below follows from the declaration alone.

---

## 2. Google's laid-height law, and the evidence it rests on

Google does not lay the declaration; it snaps it to a **0.75 pt grid and adds one whole quantum**:

```
laid = 0.75 * ( round(declared_pt / 0.75) + 1 )            (pt, then expressed in twips)
```

Four independent measurements in this repo fit it exactly — re-checked here, not asserted:

| source | declared | laid (measured) | law |
|:--|--:|--:|--:|
| `ROW-GRID-AND-SPACER-1518-relay.md` §1 (9 identical rows/page, ±0.06 pt) | 17.00 | 18.00 | 18.00 ✓ |
| same | 17.40 | 18.00 | 18.00 ✓ |
| same | 17.80 | 18.75 | 18.75 ✓ |
| same | 18.20 | 18.75 | 18.75 ✓ |
| same | 18.60 | 19.50 | 19.50 ✓ |
| `ROW-PITCH-LAW-135800-relay.md` build 3 | 17.40 | 18.0 | 18.00 ✓ |
| same, build 2 (`exact`) | 18.40 | 19.5 | 19.50 ✓ |
| same, build 1 (360/380 mix) | 18.00 / 19.00 | 19.1 mean | 18.75/19.50 → **19.125** ✓ |
| `ROW-RULE-IS-OUTSIDE-TRHEIGHT-1220-f1x.md` on `mobile-bill` | 18.40 | Σ26 gaps = 513.0 | 24×19.50 + 45 = **513.00** ✓ |
| same | 17.90 | Σ = 495.0 | 24×18.75 + 45 = **495.00** ✓ |
| same | 17.40 | Σ = 477.0 | 24×18.00 + 45 = **477.00** ✓ |

Eleven points, three separate slots, three different instruments (baseline pitch, rule positions, whole-
table sums), and `hRule` never enters it (`atLeast` and `exact` laid the same pitch — which is why
build 2 above is 19.5, not 18.4). The `45` in the last three rows is the two non-row gaps between the
ruled blocks, which do not scale with the declaration.

**The reachable ladder is therefore 0.75 apart:**

```
… 17.25, 18.00, 18.75, 19.50, 20.25 …
```

**18.40 pt is not on it.** This is the answer to the question as posed: *no single declaration lays a row
at exactly 18.40 pt.* The nearest rungs are 18.00 (−0.40) and 18.75 (+0.35). Anything that claims to have
landed 18.40 per row has measured a mean, not a row.

---

## 3. What produces 19.10 — proven, and it is none of the four candidates

The declared heights are 360 and 380 tw. Under the law:

```
360 tw = 18.00 pt  →  round(18.00/0.75) = 24  →  0.75*(24+1) = 18.75 pt laid
380 tw = 19.00 pt  →  round(19.00/0.75) = 25  →  0.75*(25+1) = 19.50 pt laid
```

The document mixes the two. `mobile-bill` is 15×360 + 9×380:

```
(15 * 18.75 + 9 * 19.50) / 24 = (281.25 + 175.50) / 24 = 456.75 / 24 = 19.031 pt
```

`insurance-policy-schedule` is 14×360 + 8×380 → 19.023 pt. A 12/12 mix gives 19.125. **The reported
19.10 pt sits inside 19.02–19.13**: it is the *mean* of two whole-quantum values, and the residual 0.07 is
the ±0.5 pt resolution of a rule-position read.

So the mechanism is **a whole-quantum rounding of the declaration: Google snaps the declared height to the
nearest 0.75 pt and charges one further 0.75 pt on top.** Not a line box, not `w:before`, not cell
margins, not a whole-*point* rounding.

The other four explanations are refuted by this XML, arithmetically:

| proposed term | what the XML says | verdict |
|:--|:--|:--|
| **line box of the substituted face**, `1.15 × w:sz` (11:30 relay) | `sz = 7.00 pt` → 8.05 pt. To reach the claimed 18.35 it needs `sz = 15.96 pt`; the cells carry 7.00 | **refuted.** That finding inferred 16 pt text from the 19.10 it was trying to explain; the XML has the real size |
| **`w:before`** | 9.30–10.50 pt, seven different values across rows, yet every row lays the *same* height per declaration | **refuted.** A term that varies 1.2 pt cannot produce a pitch that varies by 0 |
| **cell top+bottom margin** | `w:tblCellMar` top = bottom = 0, no `w:tcMar` on any cell | **refuted — and this is why candidate (e) is a no-op** |
| **a whole-*point* rounding** (15:20 ladder) | the ladder is 0.75, and 18.20 declared lays 18.75, not 19 | **refuted**; the 0.75 grid explains its own 12-point sweep better than its stated law does |
| **content height** (10:05 finding, "natural height 19.10") | content = `w:before + 0.483` = 9.78–10.98 pt | **refuted.** The row is declaration-bound by 7 pt |

**Status: proven, to 0.07 pt.** The law reproduces eleven published points exactly, including three
whole-table sums on `mobile-bill` itself; 19.10 is its mean over the document's 360/380 mix.

---

## 4. The five candidates, computed

`content = 9.78–10.98 pt` (from §1). Clipping is only possible under `hRule="exact"`, and only if a row's
content exceeds its declaration — here it never does, and no cell wraps, so no candidate clips *this*
content. The clipping column says what happens in principle and on these documents.

| | declaration | laid (law) | mean over the table | excess vs 18.40 | clipping |
|:--|:--|--:|--:|--:|:--|
| **(a)** current | `trHeight` 18.0/19.0 `atLeast` (360/380) | 18.75 / 19.50 | **19.03** | **+0.63** mean, +15.2 pt at the foot of 24 rows | none — `atLeast` grows, content 10.98 ≪ 18.00 |
| **(b)** | `trHeight` 18.4 `exact` (368) | 19.50 | 19.50 | **+1.10** | none on this content, but `exact` will clip any cell that wraps to a second line (content 18.4+). Measured 19.5 in `ROW-PITCH-LAW` build 2 |
| **(c)** | `trHeight` 19.0 `exact` (380) | 19.50 | 19.50 | **+1.10** | same as (b), and 1.0 pt of dead space above the text |
| **(d)** | `atLeast`, `w:line` cut so natural = 18.4 | 18.75 / 19.50 | 19.03 | **+0.63** | none, and **no effect at all**: content is 10.98, so reducing `w:line` (already 0.5 pt) cannot move the row. Making content bind at 18.4 would need `w:before = 17.92 pt` (358 tw), and the row would *then* lay 19.50 anyway |
| **(e)** | `atLeast` 18.4 + cell margins zeroed | 19.50 | 19.50 | **+1.10** | **no-op half**: margins are already 0 in both documents; the declaration half is (b) |

**None of the five lands 18.40.** (a) is the least bad of the five and still fails by +15 pt at the foot of
the table. (b), (c) and (e) are worse than the status quo — each moves the declaration across a rung
boundary (18.375) and picks up the full quantum. (d) is inert because the content never binds.

---

## 5. Recommendation

Since 18.40 is unreachable *per row* and reachable *exactly* as a mean, the declaration has to dither on
the 0.75 grid — which is what the engine's 360/380 alternation was groping at, one rung too high.

**Land `laid = 18.00` on 7 of every 15 rows and `laid = 18.75` on the other 8:**

```
(8 * 18.75 + 7 * 18.00) / 15 = 276.00 / 15 = 18.400 pt exactly
```

**The exact Java edit** — `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:6228`, replacing

```java
int rowHeightTw = Math.max(rowTwHere, rowLineTw);
```

with

```java
// Google lays a row at 0.75 * (round(declared / 0.75) + 1): the declaration is snapped to a
// 0.75 pt grid and one whole quantum is added on top, so the laid ladder is 0.75 apart
// (18.00, 18.75, 19.50) and a page pitch of 18.40 is not on it. Declaring the pitch therefore
// lays a rung too tall. Declare one quantum NET of the rung the page's own cumulative height
// wants, and the table's laid height tracks the page instead of drifting a rung per row.
int targetTw = writtenRowsTw + Math.max(rowTwHere, 0);        // the page's height after this row
int rowHeightTw = Math.max(rowLineTw, 15 * Math.round(targetTw / 15f) - 15);   // 0.75 pt = 15 tw
```

and at `DocxWriter.java:6237-6238` the flow must be charged the height Google will *lay*, or the
diffusion has nothing to correct against:

```java
writtenRowsTw += Math.max(pitchTwHere, rowHeightTw + 15);
```

(15 tw is one quantum; `rowHeightTw + 15` is the laid height. `writtenRowsTw` is declared at
`:6116` and consumed at `:6781`, so it is the right accumulator — it is per table.)

**Predicted laid height.** Emitted declarations become **348 tw (17.40 pt)** on the lower rung and
**360 tw (18.00 pt)** on the upper:

```
348 tw → round(17.40/0.75) = 23 → 0.75*24 = 18.00 pt laid
360 tw → round(18.00/0.75) = 24 → 0.75*25 = 18.75 pt laid
```

Simulated over the two documents' real row lists:

| | rows | laid values | mean laid | worst row | foot of table vs 18.40/row |
|:--|--:|:--|--:|--:|--:|
| `mobile-bill` HEAD | 24 | 18.75 / 19.50 | 19.031 | +1.10 | **+15.15 pt** |
| `mobile-bill` this edit | 24 | 18.00 / 18.75 | 18.392 | **0.375** | **+0.15 pt** |
| `insurance-policy-schedule` HEAD | 22 | 18.75 / 19.50 | 19.023 | +1.10 | **+13.70 pt** |
| `insurance-policy-schedule` this edit | 22 | 18.00 / 18.75 | 18.373 | **0.375** | **+0.20 pt** |

So: **18.75 on 8 rows in 15, 18.00 on the rest, mean 18.400, never more than 0.375 pt from the source at
any row, and 0.15–0.20 pt at the foot of the table** against 13.7–15.2 pt today. On a 7 pt cell the check's
per-run tolerance is `clamp(0.35*7, 1.5, 4.5) = 2.45 pt`, and 0.375 is inside it by 6.5×.

**Predicted clipping: none.** `hRule` stays `atLeast`; Google's content is 9.78–10.98 pt against
declarations of 17.40–18.00; the row cannot grow to its content because the content is 6.4 pt shorter than
the *smallest* declaration, and it cannot be clipped because `atLeast` does not clip. This is the one
candidate where the "no clipping" requirement is structurally guaranteed rather than measured.

**Two caveats that are measurements, not opinions.**

1. `ROW-GRID-AND-SPACER-1518-relay.md` §3 built this diffusion alone
   (`patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`) and it made both probe documents
   **worse** (`mobile-bill` median dy −6.73 → −12.73) — because the +0.7 pt/row pitch error was cancelling
   a −10.18 pt table-spacer step. It must land **with** the spacer as `w:before` (the 10:05 construct),
   never alone. That is why the two blockers are blocked as a pair.
2. `rowLineTw` stays the floor in the expression above, so a row whose text genuinely needs more than its
   rung still grows. The type floor is 175 tw = 8.75 pt here and never binds, but keeping it is what stops
   this change from clipping a row on a document with larger type.

---

## 6. What would prove this wrong

- **One row measured at 18.40 pt.** The law says the laid ladder has no 18.40 rung. A single rule pair
  18.40 apart on a document declared off the grid kills the law outright, and the recommendation with it.
- **A declared 18.20 laying 19.00.** The law says 18.75; the whole-point ladder says 19.00. The 15:20 slot's
  own 12-point sweep already favours 0.75, but that sweep read rule positions, not baselines.
- **A document whose cell content exceeds its declaration.** Every prediction above assumes
  `max(declared, content) = declared`. A wrapped cell breaks that assumption and the law has never been
  measured in the content-bound regime.

## Cost

No Google round trip, no Drive call, no document touched. One engine build (36 s), two `ConvertOne`
conversions, XML reads. `DocxWriter.java` read only — not modified.
