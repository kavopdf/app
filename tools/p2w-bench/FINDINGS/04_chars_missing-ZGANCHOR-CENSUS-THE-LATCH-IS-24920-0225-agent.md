# ZERO_GAP_ANCHOR: why 20,024 characters become anchored text boxes, and whether they can flow

**Repo** `github.com/kavopdf/app` @ `--depth 1`, engine `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (7,671 lines)
**Corpus** all 213 documents (`tools/p2w-bench/pod-prep.sh`, 213 PDFs, 0 missing)
**Measured** 2026-11-25. Nothing committed, nothing pushed, no Google pass run.

---

## Verdict (one line)

**Not flowable by a tolerance** — the misses are 13.6–113.5 pt (per-document medians 14.5–113.5 pt), and
99.4 % of the anchored characters miss by more than 12 pt, so a raised `ZERO_GAP_FLOOR_PT` buys
26–84 characters corpus-wide; the same characters *are* flowable (20,267 of 25,278, 80 %) but only by
resyncing the positioner once per miss, which is a different change from the one the brief proposed.

**No patch written** — the deciding histogram (below) is the "mostly large" case, and the brief's own
rule for that case is to say so plainly and not write the tolerance patch.

---

## 0. The headline correction to the prior investigation

The prior note said the 20,024 characters "come from the ZERO_GAP_ANCHOR cascade". That is right about
the **attribution** and wrong about the **mechanism**, and the difference decides whether a tolerance
can help. Measured on 213 documents with a per-line probe (all mechanisms, all 61 boxed documents):

| mechanism | lines | characters | what it is |
|---|---|---|---|
| `pos` — `para()` anchored because `ctx.positioned` is true | 655 | **24,920** | the **latch**: every line after the first anchored line on a page |
| `rule` — the zero-gap guard itself (`flowFromBox`) | 11 | **354** | a line whose `err >= 6.0` |
| `rowrule` — the same guard in `flowRow` | 1 | 4 | ditto, a row of fields |
| `noroom` — `zeroGapNoRoom` | 0 | 0 | wanted to anchor, no room above |
| `cap` + `rowcap` — the 120 pt `GAP_CAP_TW` rule | 38 | 1,469 | the gap-cap rule, a different latch |
| `pin` — `pinnedBoxes` | 14 | 488 | short line inside a table band |
| `rot` + `rotline` — rotated baselines | 331 | 1,192 | stamps, watermarks, vertical labels |
| **total anchored** | 1,050 | **28,427** | (28,553 chars sit inside `w:txbxContent` in the .docx) |

So the zero-gap **rule** fires on **11 lines / 354 characters** in the whole corpus. The other
**24,920 characters are not misses at all** — they are ordinary flow lines that inherit a page-level
latch set by one earlier miss. That is the cascade, and it is why the census counters in the brief look
so small: `zeroGapAnchored` is **2** on the worst document, because the counter sees the rule and not
the latch (`cenAnchorPos` is the counter that sees the latch).

---

## 1. The two guard blocks, in terms of the variables (Q1)

### 1.1 `flowFromBox`, the general form (DocxWriter.java:4564–4599)

```java
if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {          // 4564
    float topNow  = flowTopPt(ctx) + beforeTw / (float) TWIPS_PER_PT;
    float landY   = topNow + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
    float err     = landY - b.y;                                  // 4567  <- the miss
    float prevBoxTop  = flowTopPt(ctx) - ctx.flowBoxPt;
    float thisBoxBottom = b.y + (1f - LINE_BASE) * linePt;
    if (err >= ZERO_GAP_FLOOR_PT && thisBoxBottom <= prevBoxTop) { // 4579
        ctx.zeroGapAnchored++; ctx.cenAnchorRule++;
        anchorBox(sb, p, b, ctx);
        if (PAGE_POSITION_ON_ANCHOR) ctx.positioned = true;        // 4587  <- the latch
        ...
        return;
    }
    if (err >= ZERO_GAP_FLOOR_PT) ctx.zeroGapNoRoom++;             // 4597
}
```

* **`err` (the miss)** is *where the line would land, minus where the page drew it*, in points.
  `topNow` is the top of the paragraph as the flow is about to place it (`flowTopPt(ctx)` plus the
  `w:before` it just decided to write); `landY` is the baseline that placement produces
  (`+ LINE_BASE * lineTw`); `b.y` is the source baseline. **`err > 0` means the flowed line would land
  `err` points BELOW its source y.** It is checked *after* `fitPage()` (line 4562), so it also carries
  the fit clamp: when the page budget is exhausted `fitPage` returns `beforeTw = 0` and `err` jumps by
  exactly the gap that was refused.
* **`ZERO_GAP_FLOOR_PT`** (`6.0`, `-Dp2w.zgfloor`) is the smallest miss worth a text box. The
  javadoc's calibration: an anchored line lands ~1.0–1.3 pt from where the flow would have put it, and
  at a 1.0 pt floor five lines of `78_mixed_english_devanagari_line` (worst miss 3.6 pt) became boxes
  and four landed on the line above — a *new* `26_text_overlap` bought for 3 pt of position. 6 pt is
  about half a line box at 10–12 pt type.
* **`!ctx.inColumn`** — inside a layout-table cell the cell's height is measured from exactly what it
  writes, so a wide or negative gap there is *space the cell can hold*; a page-anchored box written
  from inside a cell lands outside it. (`brochure-3col-with-sidebar-box`: anchoring cell lines turned
  24 lines into boxes.)
* **`!ctx.newPage`** — the first line of a page has no predecessor to be "below", and `place()`
  already gives it its own y from the paper's top edge (`ctx.newPage` branch, 4479–4492). `flowY < 0` on a
  fresh page, so `err` would be meaningless.
* **`thisBoxBottom <= prevBoxTop`** — the "room" test. `prevBoxTop` is the top edge of the line above
  (the flow's box minus `ctx.flowBoxPt`), `thisBoxBottom` is the bottom of this line's own box. If the
  box would be placed on top of the line above, the anchor is refused and the line stays in the flow.
* **`zeroGapNoRoom`** — a line that *should* have been anchored (`err >= floor`) but had no room, so
  it stayed in the flow and lands `err` pt low. It is the honest count of "the page is in the way".
  **Measured: 0 in the shipped build, 15 lines / 1,187 chars once each line is judged on its own.**
* **`ctx.positioned = true` (the latch).** `PAGE_POSITION_ON_ANCHOR` (`-Dp2w.pagepos`, on by default).
  The javadoc's reason: leaving the flow live after an anchored line puts two positioners on one page
  (`policy-2col-spanning-section-heading`: 51 flowed + 27 anchored on one page, 21 overlaps, median
  |dy| 105.7 pt). `para()` (3101) then reads `ctx.positioned` in three places (3116, 3126, 3144) and
  sends **every remaining line of the page** to `anchorBox()` — this is the 24,920 characters.

### 1.2 `flowRow` (3645–3681, clean file) — the same rule, one row of fields at a time

Identical arithmetic with `first.y` in place of `b.y` and `landY` built from the row's own
`beforeTw`/`lineTw`; on success it anchors *each field* at its own x (`for (Box ab : cols)
anchorBox(...)`) and sets `ctx.positioned` at 3663. `ctx.cenAnchorRule += cols.size()`. It also
records `miss` into `zeroGap`/`zeroGapWorstPt` at 3648–3657 (the pre-clamp negative gap), which is why
the `zeroGap` counter and the anchor rule disagree: `zeroGap` counts *negative gaps*, the rule fires
on `err` *after* the fit clamp.

### 1.3 What `zeroGap` actually counts (and why it is not the miss)

```java
if (beforeTw == 0 && ctx.flowY >= 0f && !ctx.newPage && ctx.afterTablePt < 0f && absTop < ctx.flowY) {
    ctx.zeroGap++;                       // a NEGATIVE gap: the page put the line above the flow
    float miss = ctx.flowY - absTop;     // 4516
    ...
}
```
`zeroGap` is a *pre-clamp* count of lines the flow would have had to walk backwards to. In the shipped
build it is 30 on `041122-Account_Opening_Form` and 2 on `69_two_col_legal_numbered_clauses`, while
189 and 36 lines respectively become boxes. **`zeroGap`, `zeroGapAnchored` and `zeroGapNoRoom` do not
measure the cascade**; `cenAnchorPos` and the `pos` probe do.

---

## 2. Build and measurement method (Q2)

Nothing invented: `tools/install-gate.sh` delegates to `tools/p2w-bench/pod-prep.sh`, which is the
current recipe (TOOLBOX.md is stale by its own header — `record.py`/`classify.py` are retired and
`INSTRUMENT.md` wins; `pod-prep.sh` is what `install-gate.sh` actually calls).

```
bash tools/p2w-bench/pod-prep.sh                 # corpus 213 PDFs, JDK 17, PDFBox-Android 2.0.27.0,
                                                 # AAR assets, android stubs, engine + ConvertAll
cd tools/engine-verify
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -cp "$CP" ConvertAll /scratch/work/p2w/corpus <outdir>     # 213 docs, 68 s, 0 failed
```

`ConvertAll` prints the engine's own `Stats` per document — that is the census in the brief
(`DocxWriter.Stats`, lines 694–700, filled at 706–713):

```
<doc>  pages=N  paragraphs=N  zeroGap=N  zeroGapWorst=N  zeroGapInCol=N  zeroGapAnchored=N  zeroGapNoRoom=N
```

The diagnostic **property names** (found in the code, not guessed):

| property | what it writes |
|---|---|
| `-Dp2w.census=<file>` | one `CENSUS` line per page: `flow/row/col/tbl/anchor/stamp/anchorRule/anchorPos/flowYset/absYset/rewind/rewindWorst` (4264–4311) |
| `-Dp2w.traceLines=<file>` | one `LINE` line per flowed line: writer, source y, `before`, `line`, flowY before/after, text (4245–4262) |
| `-Dp2w.zganchor=false` | kills the zero-gap rule and its latch |
| `-Dp2w.pagepos=0` | `PAGE_POSITION_ON_ANCHOR=false` — no latch, flow stays live after an anchor |
| `-Dp2w.anchorkeep=0` | `ANCHOR_KEEPS_FLOW=false` — after an anchor the flow is set to the **source** `b.y` (line 68, 4188–4199) |
| `-Dp2w.zgfloor=<pt>` | `ZERO_GAP_FLOOR_PT`, default 6.0 (334–335) |

To get the miss *per line* — which no counter in the engine reports — I added a temporary probe
(`-Dp2w.zgprobe=<file>`) inside the clone. It writes nothing to the document and does not change any
branch; it prints, for every line that reaches either guard,
`ZG <doc> p=<n> <who> y=<b.y> err=<miss> miss=<flowY-absTop> rawBefore=<pre-fit w:before> before=<written> chars=<n>`
with `who ∈ {rule, rowrule, noroom, rownoroom, flow, pos, cap, rowcap, pin, rot, rotline, shape}`.
The probe is **not** part of any deliverable; it was removed from the tree after measuring.

---

## 3. Per-document census, the ten documents that carry the most boxed characters (Q2)

`zeroGap`/`zeroGapAnchored`/`zeroGapNoRoom`/`zeroGapWorstPt` are the engine's own `Stats` on the
shipped build; `boxes`/`boxed chars` are counted from `word/document.xml` (`<w:txbxContent>` and its
`<w:t>` text). The last three columns are the same document under three configurations.

| document | pages | zeroGap | zeroGapAnchored | zeroGapNoRoom | zeroGapWorstPt | boxes | boxed chars | of which zganchor (rule+pos) | same under `pagepos=0 anchorkeep=0` | total boxed chars under `pagepos=0 anchorkeep=0` |
|---|---|---|---|---|---|---|---|---|---|---|
| 041122-Account_Opening_Form | 9 | 30 | 2 | 0 | 34.3 | 189 | 6840 | 6574 | 77 | 322 |
| Account_Opening_Form_Fillable_filled | 9 | 30 | 2 | 0 | 34.3 | 189 | 6840 | 6574 | 77 | 322 |
| policy-2col-spanning-section-heading | 1 | 1 | 1 | 0 | 13.4 | 62 | 3046 | 3041 | 251 | 300 |
| academic-paper-ieee-2col-abstract | 2 | 7 | 1 | 0 | 34.5 | 51 | 2942 | 2942 | 181 | 181 |
| magazine-2col-pullquote-spanning | 1 | 1 | 0 | 0 | 0.4 | 37 | 2182 | 2035 | 2035 | 2182 |
| 69_two_col_legal_numbered_clauses | 1 | 2 | 1 | 0 | 15.4 | 36 | 1358 | 1358 | 283 | 367 |
| 65_two_col_full_width_figure_caption | 1 | 5 | 0 | 0 | 0.5 | 25 | 627 | 624 | 624 | 627 |
| 66_two_col_footnotes_bottom | 1 | 7 | 0 | 0 | 0.5 | 8 | 448 | 358 | 358 | 448 |
| 322_mutual_fund_factsheet | 1 | 1 | 1 | 0 | 34.3 | 8 | 362 | 345 | 122 | 292 |
| 400_comic_page_speech_bubbles | 1 | 0 | 0 | 0 | 0.0 | 25 | 275 | 249 | 249 | 275 |

Corpus totals (213 documents, 61 with boxes on the shipped build):

| configuration | boxed characters | documents with boxes |
|---|---|---|
| shipped build | **28,553** | 61 |
| `-Dp2w.pagepos=0` | 23,791 (−4,762) | 61 |
| `-Dp2w.zganchor=false` | 7,726 (−20,827) | 58 |
| `-Dp2w.pagepos=0 -Dp2w.anchorkeep=0` | **8,586 (−19,967)** | 61 |
| zganchor-attributable characters only (rule+rowrule+pos+noroom) | **25,278 → 5,011 (−20,267, −80.2 %)** | |

Read the table with §0: `magazine-2col-pullquote-spanning`, `65_two_col_full_width_figure_caption`,
`66_two_col_footnotes_bottom`, `400_comic_page_speech_bubbles` and most of `322_mutual_fund_factsheet`
are **not** zganchor at all — they are the `GAP_CAP_TW` rule's own latch (the cap rule sets
`ctx.positioned` at 4453/4487/3571/3594 too), and no zero-gap switch touches them. That is why
`zganchor=false` does not reach zero.

`Account_Opening_Form_Fillable_filled` is the same PDF as `041122-Account_Opening_Form` with fields
filled; it carries identical numbers and is counted twice in the corpus.

---

## 4. What the miss actually is (Q3)

### 4.1 The histogram, in the requested bins

Four populations. **`err` is the miss in points** (`landY - b.y`, the quantity the floor is compared
against); characters are the `<w:t>` length of the line that would be anchored.

**A — the shipped build, the lines the zero-gap rule itself anchors (12 lines):**

| bin | lines | chars | % of chars |
|---|---|---|---|
| < 1 pt | 0 | 0 | 0.0 % |
| 1–3 pt | 0 | 0 | 0.0 % |
| 3–6 pt | 0 | 0 | 0.0 % |
| 6–12 pt | 0 | 0 | 0.0 % |
| **> 12 pt** | **12** | **358** | **100.0 %** |

Every one of those 12 lines has `rawBefore = 0`, i.e. it is a genuine backwards jump of the flow, not
a clamped gap. Individual values: 13.55, 14.50, 15.52, 20.24, 20.24, 20.51, 24.40, 34.25, 34.25,
34.32, 34.63, 72.55 pt.

**B — `-Dp2w.pagepos=0`, so each line is judged on its own (the honest counterfactual for the 20,024):**

| bin | lines | chars | % of chars |
|---|---|---|---|
| < 1 pt | 0 | 0 | 0.0 % |
| 1–3 pt | 0 | 0 | 0.0 % |
| 3–6 pt | 0 | 0 | 0.0 % |
| 6–12 pt | 6 | 84 | 0.6 % |
| **> 12 pt** | **263** | **13,636** | **99.4 %** |

Of these 269 lines, **238 (12,632 chars) had `rawBefore > 0`** — the anchor fired because `fitPage()`
zeroed a real gap (the page's budget was spent), not because the flow had to walk backwards; the other
31 (1,088 chars) are true rewinds.

**C — `-Dp2w.pagepos=0 -Dp2w.anchorkeep=0` (24 lines left):** 4 lines / 56 chars at 6–12 pt,
20 lines / 739 chars > 12 pt. The class has collapsed; see §5.

**D — reference: the lines that already flow on the shipped build (3,478 lines / 217,982 chars):**

| bin | lines | chars | % of chars |
|---|---|---|---|
| < 1 pt | 3,310 | 208,642 | 95.7 % |
| 1–3 pt | 25 | 276 | 0.1 % |
| 3–6 pt | 143 | 9,064 | 4.2 % |
| 6–12 pt | 0 | 0 | 0.0 % |
| > 12 pt | 0 | 0 | 0.0 % |

The engine's flow is already accurate to under 1 pt on 95.7 % of characters and never worse than 6 pt
on any flowed line. **The hypothesis in the brief — "most misses are small, a few points from the
model's own line-height error" — is false.** There is no population of 1–3 pt misses to forgive; the
6 pt floor is not rejecting small errors, it is rejecting 13–113 pt jumps.

### 4.2 The threshold sweep: what a tolerance would buy

Anchoring only when `err > T`, on population B (13,720 anchored chars):

| T (pt) | still anchored: lines / chars | becomes flow: lines / chars | share of the class recovered |
|---|---|---|---|
| 6 (today) | 269 / 13,720 | 0 / 0 | 0.0 % |
| 8 | 265 / 13,694 | 4 / 26 | 0.2 % |
| 12 | 263 / 13,636 | 6 / 84 | 0.6 % |
| 15 | 258 / 13,357 | 11 / 363 | 2.6 % |
| 20 | 244 / 12,841 | 25 / 879 | 6.4 % |
| 24 | 239 / 12,771 | 30 / 949 | 6.9 % |
| 36 | 80 / 4,472 | 189 / 9,248 | 67.4 % |

### 4.3 What the checks tolerate, which caps T

`18_displacement` (`verify_google.py` ~5,760–5,785) is the position standard:
`tol = clamp(0.35 * size, 1.5, 4.5) pt`, a per-page budget of `n_out > max(2, ceil(0.05 n))`, **and a
tail clause `worst_here > 2.0 * tol` that fails the page on a single run**. So the largest per-run
error that can never fail is `2 * 4.5 = 9.0 pt`, and for 10–12 pt type it is 7.0–8.4 pt. Every bin
that matters here (13.6–113.5 pt) is 1.5× to 13× the tail bound: a line flowed at its measured miss
does not "land within tolerance", it fails `18_displacement` on its own. **T can be at most ~9 pt and
that recovers 26 characters.**

The 4.2 % of characters already flowing at 3–6 pt are inside the tail bound, which is why they pass
today — that is the real envelope, and it is already used.

---

## 5. Anatomy: two worked examples (what the miss *is*)

**5.1 `041122-Account_Opening_Form`, page 3** (`-Dp2w.traceLines` + probe, shipped build):

```
flowFromBox y=34.36  before=686 line=1  flowBefore=-1.00  flowAfter=34.34   ACCOUNT OPENING FORM ...
flowFromBox y=57.16  before=215 line=1  flowAfter=57.14
table       top=66.0                    flowAfter=57.14   (a table: the flow does not advance)
flowRow     y=74.27  before=0   line=1  flowBefore=79.00  flowAfter=79.04   (For office use only)
flowFromBox y=87.09  before=255         flowAfter=91.84   err=4.75  <- flow is already 4.75 pt low
flowFromBox y=100.80 before=273         flowAfter=105.54  err=4.74
flowFromBox y=118.13 before=345         flowAfter=122.84  err=4.71
flowFromBox y=131.72 before=270         flowAfter=136.39  err=4.67
anchorBox   y=102.19                                     <- miss 34.26: a REAL backward jump
anchorBox   y=109.39  (miss 27.11)  ... 186 more boxes
```

Two different things are happening and only one of them is a miss:

1. The table + `flowRow` leave the flow **4.7 pt low**, and every following line inherits it
   (`err` 4.75 → 4.67). That is a small, tolerated error — under 6, so those lines flow.
2. The form then draws "Bank / Branch to affix rubber stamp of" at **y = 102.19**, i.e. *above* the
   line the flow has just written at 131.72. Reading order is not monotone in y on a form. `miss =
   136.39 − 102.19 = 34.26 pt`. **This line genuinely cannot be flowed** — flowing it lands it 34 pt
   low, 3.8× `18_displacement`'s tail bound.
3. Then the latch fires: the 186 lines *after* it, which the flow could walk to perfectly well
   (their own `err` is 4.7 pt), all become text boxes. **That is the 20,024 characters.**

**5.2 `academic-paper-ieee-2col-abstract`, page 1** — the same shape at a column boundary:

```
flow  y=279.25 err=0.63 / 1.23 / 1.83 / 2.43 / 3.03 / 3.63   <- 6 lines on ONE baseline, 0.6 pt
                                                                accumulated line-height error each
rule  y=248.85 err=34.63 miss=34.52 rawBefore=0   <- column 2 starts 34.6 pt ABOVE the flow
rule  y=260.45 err=34.63 miss=23.52 rawBefore=220 <- and then err is CONSTANT 34.63 for 46 lines
rule  y=295.25 err=54.03 miss=53.92 rawBefore=0   <- second backward jump
```

`err` is a **constant 34.63 pt on 46 consecutive lines** with `rawBefore` alternating between 0 and a
real gap. That constant is the signature of a *displaced positioner*: once the flow is 34.6 pt below
the page, every subsequent line needs the same −34.6 pt correction, and a `w:before` cannot be
negative, so each one is anchored. **Anchoring each of the 46 is one box too many — the displacement
should be corrected once.** This is the sub-population a tolerance can never reach and a resync fixes
in one step.

---

## 6. Verdict and the patch decision (Q4)

### 6.1 Verdict

**Not flowable by a tolerance.** The requested histogram, in the configuration where the rule judges
each line on its own (population B): **0 characters below 6 pt, 84 characters in 6–12 pt, 13,636
characters above 12 pt (99.4 %)**. The misses are 13.6–113.5 pt because they are not line-height
error — they are (a) genuine backward jumps in reading order (forms, column boundaries, footers) and
(b) the *accumulated* displacement since the last correction point. `ZERO_GAP_FLOOR_PT = 6.0` is not
rejecting small errors; the flow model is already accurate to < 1 pt on 95.7 % of flowed characters.

The threshold sweep caps out far below usefulness: **T = 12 pt recovers 84 characters; T = 24 pt
recovers 949; and `18_displacement`'s tail clause (2 × 4.5 pt) forbids anything above ~9 pt anyway,
which is 26 characters.**

### 6.2 Therefore: no patch written

Per the brief's own rule, a mostly-large histogram means no tolerance patch, and I have not written
one. There is no `zganchor-patch.diff` in the output for that reason. A patch that raised the floor to
12 pt would move 0.6 % of the class and put those lines outside the position standard; one that raised
it to 36 pt would move 67 % of the class and put lines up to 36 pt low on the page.

### 6.3 What *is* flowable, measured — and why it is not a patch

The class is 80 % recoverable, but by the **other** half of the pair the rule writes: the positioner
correction, not the threshold.

| configuration (both switches already exist in the code) | zganchor-attributable chars | all boxed chars | flowed lines with `err` > 6 pt | docs with a changed page count | overrunning pages |
|---|---|---|---|---|---|
| shipped | 25,278 | 28,553 | 0 | — | 149 |
| `-Dp2w.pagepos=0` | 15,010 | 23,791 | 21 lines / 1,290 chars (the `noroom` set) | 0 / 213 | 151 |
| `-Dp2w.pagepos=0 -Dp2w.anchorkeep=0` | **5,011 (−80.2 %)** | **8,586** | **0** | **0 / 213** | 153 |

With `ANCHOR_KEEPS_FLOW=false` the flow is set to the **source** `b.y` after an anchored line
(4590–4592) instead of to the flow's own landing point (4188–4199). Every line after the correction
then flows with `err < 6` again: the 3,748 flowed lines of that run land within 6 pt of their source
baseline, 2,147 of them within 1 pt. The boxes that survive are the ones that must: 24 rule-anchored
lines (795 chars), the gap-cap latch (4,216 chars), pinned/rotated (1,680 chars).

I have **not** turned that into a patch, for one reason I cannot discharge here: `ANCHOR_KEEPS_FLOW`'s
own javadoc (60–78) records that the resync-to-source behaviour is what produced the 18 pt miss on
`69_two_col_legal_numbered_clauses` and the 101.24 pt rewind on
`policy-2col-spanning-section-heading` — i.e. the switch exists because this behaviour was already
tried and rejected once, presumably measured with the latch still on (`pagepos` default). My run pairs
it with `pagepos=0`, which is a configuration nobody has measured over the corpus before. The
structural proxies are clean — page count identical on all 213 documents, 4 more overrunning pages out
of 213, no line flowed more than 6 pt from its source — but `26_text_overlap`, `18_displacement` and
`04_chars_missing` are Google-side checks and the brief forbids running that pass. **Proposing this as
a landed change on engine-side proxies alone would repeat the mistake the repo's own gate exists to
prevent.**

The measured next step, in one line, for whoever can run the Google pass:

```
-Dp2w.pagepos=0 -Dp2w.anchorkeep=0     # 28,553 -> 8,586 boxed chars, 0 page-count changes,
                                       # 0 flowed lines > 6 pt out; needs 26/18/04 over the corpus
```

---

## 7. Where this disagrees with the prior note (verify, do not trust — applied to it)

| prior note | measured here |
|---|---|
| "the 120 pt cap accounts for 3,770 of 23,794 boxed chars (15.9 %)" | cap + rowcap = **1,469** chars of 28,553 (5.1 %); pinned + rotated = 1,680 (5.9 %) |
| "the remaining 20,024 come from the ZERO_GAP_ANCHOR cascade" | **confirmed in magnitude** (25,278 → 5,011, −20,267) but the cascade is **the latch**, not the rule: rule 354 chars, latch 24,920 |
| "`zeroGap`, `zeroGapAnchored`, `zeroGapNoRoom` are the census" | they count the rule only; on the worst document `zeroGapAnchored = 2` while 189 lines are boxes. `cenAnchorPos` / the `pos` probe is the counter that sees the cascade |
| "`-Dp2w.pagepos=0` was worth 4,037 characters but ZERO documents" | 4,762 characters here, 0 documents — **confirmed**, and the reason is now known: without the latch each line is still judged alone and 99.4 % of them miss by > 12 pt |
| "`-Dp2w.zganchor=false` has never been measured" | measured: 28,553 → 7,726 boxed chars (−20,827), 58 of 61 documents still boxed. It is the *largest* single reduction and it is also the worst placement (lines land at their full miss, up to 113 pt) |

---

## 8. Reproduction

```
bash tools/p2w-bench/pod-prep.sh
cd tools/engine-verify
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"

java -cp "$CP" ConvertAll /scratch/work/p2w/corpus out/base        # census counters (stdout)
java -Dp2w.pagepos=0                -cp "$CP" ConvertAll ... out/pp0
java -Dp2w.zganchor=false           -cp "$CP" ConvertAll ... out/zgoff
java -Dp2w.pagepos=0 -Dp2w.anchorkeep=0 -cp "$CP" ConvertAll ... out/pp0ak0

# boxed characters per document: sum of <w:t> inside <w:txbxContent> in word/document.xml
# page-fit proxy: split document.xml on <w:br w:type="page"/>, sum w:before+w:line per segment,
#                 compare with w:pgSz/@w:h (the section has zero margins)
```

Timings on this pod: `pod-prep.sh` 96 s cold; one 213-document conversion 68 s; the four
configurations 5 min total. No document failed to convert in any configuration (`0 failed`, 213/213).

---

## 9. Caveats

* The `pos` "err" printed by the probe in **latched** mode is not a counterfactual: `anchorBox()` in
  `para()` does not move `flowY`, so `flowY` freezes and the number grows to −537 pt on
  `69_two_col_legal_numbered_clauses`. That is why population B (the `pagepos=0` run, where every line
  really is judged by `flowFromBox`) is the population used for the histogram, and the latched
  numbers are used only for the character attribution.
* `err` is the engine's own placement model. It is not a rendering measurement; the render-side
  question (`18_displacement`, `26_text_overlap`) is the Google pass I was told not to run.
* Table-cell lines (`columnPage`) and first-line-on-page placements never reach either guard and are
  outside every number here.
* `Account_Opening_Form_Fillable_filled` is a duplicate of `041122-Account_Opening_Form` in the
  corpus; both are counted, and both appear in the table.

## Open questions

* Whether `pagepos=0 + anchorkeep=0` passes `26_text_overlap`, `18_displacement` and `04_chars_missing`
  over the corpus — the only thing that decides whether the 20,267 characters can actually leave the
  boxes. It needs the Google/Drive pass, which this task forbade.
* Which of the 24 remaining rule-anchored lines in that configuration are unavoidable (the genuine
  backward jumps) versus another displaced-positioner symptom; that needs the same render.
* Whether the cap rule's latch (4,216 chars, e.g. `magazine-2col-pullquote-spanning` unchanged under
  every zero-gap switch) should be attacked next — it is now the largest single block of boxed body
  text that the zero-gap work cannot reach.
