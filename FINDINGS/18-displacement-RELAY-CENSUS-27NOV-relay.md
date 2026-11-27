> RELAYED BY A SUB-AGENT THIS RUN, NOT VERIFIED BY THE FIXER EXCEPT WHERE THE FINDING ABOVE CITES IT.
> 16 refuted hypotheses with their measurements, 7 standing ones ranked, and 16 ledger contradictions.

# `18_displacement` — the state of the construct, the one live hypothesis, and the one-document test

**27 Nov 2026 · code-and-ledger analysis only · repo `kavopdf/app` @ HEAD `a554f74` (shallow clone) ·
no PDFs, no Java build, no Drive. Every Google number below is quoted from the sources named beside it,
not re-measured by this run. What this run DID verify first-hand: every `file:line` in `DocxWriter.java`,
which patches apply to HEAD (`git apply --check`), and every count computable from the repo
(`benchmarks/gverify/*.json`, `benchmarks/DISP-TABLE.csv`, `ATTEMPTS.json`, `CLASS-HISTORY.jsonl`).**

Read: the nine `FINDINGS/18-*` files, `18DISPLACEMENT-COUNT-0125-27NOV.md`, `ATTEMPTS.json` (+`.bak`),
`CLASS-HISTORY.jsonl`, `HANDOFF.md`, `ROTATION.json`, `ROUND.json`, `patches/18-*`, `benchmarks/gverify/`,
`DISP-TABLE.csv`, the 27NOV triage, and `DocxWriter.java` `table()` / `spacing()` / `sectPrXml()`.

## 0. The premise needs one correction before anything else

**"52 of 213 documents fail it" is not a failure count.** 52.2 is what `classpick.py --leverage` printed on
27 Nov as **"worth, in CLEAN documents"** — the number of documents that would become fully clean if the
check were fixed, summed over a mixed-engine store. Run today it prints **53.2**. The actual failure counts
in the tree are:

| source | what it counts | 18_displacement |
|:--|:--|--:|
| `benchmarks/gverify/*.json` (213 rows, 205 scored) | every document whose verdict names 18 | **105** |
| same, `len(failed) == 1` | sole failure | **27** |
| `benchmarks/DISP-TABLE.csv` | `google_fail_18 == True` | **103** |
| triage 27NOV, current-engine rows only (`a4d8fca4`, 61 rows) | instances | **18** (and 5 sole) |
| `classpick.py --leverage` | documents it is worth | **53.2** |

And "largest open class" is only true on the leverage table: on the current-engine 61 rows,
`60_text_column_right_edge` fails 20 documents to `18`'s 18. Both are real; they are different statements.

## 1. REFUTED — with the measurement that refuted it. Do not run these again.

| # | hypothesis | the measurement that killed it | where |
|--:|:--|:--|:--|
| R1 | Snap the row's **border box** up to a whole 0.75 pt rung (`w:trHeight = snapped − rule`, ceiling only, `ROW_BOX_SNAP_TW=15`) | `320_balance_sheet_statutory` in Google: `med_dy` **+8.2 → +8.2**, `worst_dy` 19.4 → 18.7, no check changed state. *And the probe was void*: 292 tw = 14.60 pt rounds to the same rung as 280 (both lay 15.00), so "no change" was the only possible result | `18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`; correction in `ROW-HEIGHT-IS-CONTENT-DRIVEN` |
| R2 | `w:hRule="atLeast" → "exact"` on the content rows | Exported PDF **position-for-position identical** to base (73 lines, same y); and byte-patching every row moved `68_journal` **0.0 pt**, `mobile-bill` **0.0**, `bank5` **0.0**. Google does not read `hRule` | `ROW-HEIGHT-IS-CONTENT-DRIVEN` probe A; `GAP-CARRIER` item 4 |
| R3 | Shorten `w:trHeight` instead of subtracting from the cell's line | `electricity-bill` 18.0/19.0 → **17.5/18.5**; 18 gained fewer documents than it fixed | code comment `DocxWriter.java:6467-6474` |
| R4 | `w:before = rowLineTw − box` (make the cell's content equal the row's height) — form 1 | `18_median_dy` **64 → 100** | code comment `DocxWriter.java:6867` |
| R5 | Same construct, form 2: raise one-line cells' `w:before` to the row's `w:trHeight` | Corpus rebuild 204/212: **13 better, 91 worse**, mean `median_pt` 2.274 → **2.641**; worst `23_timetable_grid_txtpos` 0.96 → 12.48. (Its two Google passes — `362_price_list_dense`, `16_right_aligned_amounts_txtpos` 41/42 → 42/42 — are real but from a run whose probe files are gone) | `ROWH-CONTENT-EQUAL-TRHEIGHT-REFUTED-27NOV-relay.md` + `.patch` |
| R6 | Carry the page-top gap in a **1×1 table row** (`hRule="exact"`, zero borders) instead of `w:before` (`-Dp2w.gapcarrier=1/2`) | Google, 4 documents: **no document becomes clean**; `mobile-bill` `worst_dy` 10.0 → **33.8** (regression), `68_journal` loses check `59`. Residual left is an **over**-delivery of +7.2/+7.7/+9.1 pt | `GAP-CARRIER-25NOV-relay.md`, raw JSON in `FINDINGS/res-18-gapcarrier/` |
| R7 | Google charges a **constant 5–10 pt** for a refused exact-line spacer | `330_cad_drawing_sheet` asks 143.95 pt, loses **110.1**. The charge is **proportional**: `2.5873 × max(L/240, 0.06)` = 21.6 % of the ask (330 fits to 2.8 pt, `56_table_indented` to 0.5 pt) | `SINGLE-PAGE-SPACER-MEASURED-26NOV-explore.md` §4 |
| R8 | The page-scale half is one thing (the dropped page-top `w:before`) | 8 of the 17 are **single page**, no `w:br type="page"`, `pgMar top=0` — structurally unreachable; 3 of the 8 carry **no spacer at all** (`bank-statement-horizontal-rules-only`: 57 paragraphs, zero empty) | `PAGE-SCALE-IS-THE-DROPPED-PAGE-TOP-26NOV-explore.md` §1-2 |
| R9 | The check fails because Google adds / drops / splits a line | Run census, 14 documents: **0 source runs lost on 11 of 14**; the surplus is **U+200B** zero-width spaces (one per table cell); the 1-2 "losses" are a word split (`HANDLIN`+`G`) | `18DISPLACEMENT-COUNT-0125` §3 |
| R10 | `attribution = table-row` predicts the displacement | `med_dy` vs `docx_table_rows`: slope **−0.108, r²=0.00** over 207 committed rows. (`worst_dy` slope 2.188, r²=0.423 — the tail, not the median) | ledger 26 Nov 14:59, 15:46 |
| R11 | The multi-row family is the page-fit reserve | `p2w.fitreserve 96→300`: `word/document.xml` **byte-identical** on all 8 largest multi-row documents (70-657 pt out) — the reserve never fires | ledger 26 Nov 15:48 |
| R12 | `-Dp2w.lineRule=autoflow` (flow lines at `auto`) fixes the class | `electricity-bill` −7.2 → **+0.08** but `72_bank_statement` +1.1 → **+3.51**, worst 4.8 → 8.44, 52/80 runs out. Opposite signs, neither clean | ledger 26 Nov 11:49 (reverted) |
| R13 | The hairline deficit (`w:line` exact short by 0-1.8 pt) orders the solo documents | Measured 0-1.8 pt and **does not order them** | ledger 26 Nov 11:38 |
| R14 | `w:trHeight w:val` is only a floor the content absorbs (the conclusion R1 drew) | **Refuted by correction**: three values in one render, prediction stated first — 300 → **15.75**, 280 → **15.00**, 260 → **13.50**. Three for three. The value IS read | `ROW-HEIGHT-IS-CONTENT-DRIVEN` "CORRECTION, SAME RUN" |
| R15 | The 0.75 pt law is "+1 rung, ceiling, upward only" | `16_right_aligned_amounts_txtpos` declares 19.00 pt and Google lays **18.75** — a *negative* delta. Nearest rung, not ceiling | `18DISPLACEMENT-COUNT-0125` §5 consequence 1 |
| R16 | A floating table (`w:tblpPr`) or `w:framePr` as the page-top carrier | `framePr`: **0 in 213 emitted files**, Google ignores it; `tblpPr` wraps the page's text around the table (file 01's BILL TO shoved from x=64 to x=528) | `PAGE-SCALE` §2; `DocxWriter.java:6185-6205` |

## 2. Still standing, ranked by (documents it would clear) / (cost to test)

| rank | hypothesis | documents it would clear | cost to test | ratio |
|--:|:--|:--|:--|:--|
| **1** | **Declare the row's height on the 0.75 pt rung, net of the rule — and charge/place the flow after the table with the LAID number, not the declared pitch** (§3) | the table-row family: **75 of the 103** flagged documents are `attribution=table-row`; 10 of the 14 "within 7 pt" documents carry their movement in a table; 4 of the 5 sole-18 documents with a table | 1 engine build (~40 s) + **1** Google round trip + 1 free local LO render | **highest** |
| 2 | The page-top gap as `w:pgMar w:top` (patch exists, `git apply --check` **clean** on HEAD) | **1 clean** (`bank-statement-5-pages`, 46/47 and only 18 failing today) + `18` cleared on ~8 multipage page-scale documents | **already measured**: 3/3 PASS in Google, population 40 of 41, **0 worse, 1 better**. Cost is bookkeeping, not physics | land it, do not re-test it |
| 3 | The spacer-room guard measures room from the **source ink bottom**, which already contains the gap → `slackTw = ctx.budgetTw - ctx.flowTw` (`DocxWriter.java:6151-6157`) | 4 of the 8 page-scale single-page documents (`330_cad` −110.1 → +2.8, `341` −7.1 → +0.7, `56_table_indented` −14.0 → +0.5, `80_gstin` unquantified) | guard edit + up to 4 renders; LO control already 0.10 pt. Google after-side is **MODELLED**, never measured | high, but a model not a measurement |
| 4 | The cell's **type size** is the floor Google lays at (`1.25 × sz`); write the cell at the size the page draws so the floor lands on the source pitch | unknown; the only lever left where the rung cannot reach the pitch (12 pt text cannot be laid tighter than 15.00 pt) | 1 document, but it moves `w:sz` and must not touch `45_char_accuracy` | medium |
| 5 | The **flow-line term**: a one-signed +0.08-0.12 pt per line advance that accumulates (no table at all) | `31_times_body_arial_headings` (+1.3 pt over 13 lines), `70_magazine_drop_cap_photo_caption` | mechanism unnamed; no code site in any finding; needs a probe first | low |
| 6 | `-Dp2w.lineRule=autoflow -Dp2w.autoEm=1.2207` (flags only, no build) | **1 measured** (`72_bank_statement_no_rules_right_amounts` 41/42 → 42/42 PASS in Google, ledger 26 Nov 11:53, `moved: 1`) — never landed, never re-measured, in no FINDINGS file | 1 render, **zero** build | cheapest of all, smallest yield |
| 7 | Google's **minimum line box for a cell paragraph** is the +7-9 pt surplus the gap-carrier row over-delivers | 3 documents' residual (the `+7.2/+7.7/+9.1` band) | one row of known height, one render (its own stated falsifier) | low, and only after 1 |

**Rank 1 is the answer.** Rank 2 should be *landed* in the same slot: it is measured, applies clean,
regresses nothing on its population, and is orthogonal (it moves the page top, rank 1 moves the rows).

## 3. Rank 1: the exact site, the diff, the one document, the command

### 3.1 Why this one is live and the other six are not

The hypothesis has two halves, and **exactly one of them has ever been measured**:

* **Half A — the declaration.** `18-displacement-ROW-HEIGHT-IS-CONTENT-DRIVEN-26NOV-fixer.md`
  ("The engine build") wrote a cumulative-residue tracker into the row emitter and measured it in Google on
  `320_balance_sheet_statutory`: `med_dy` over the table rows **+10.30 → −0.70**, every row within ±0.95 pt,
  the ramp gone. Half A works.
* **Half B — the charge.** That same build **did not touch `writtenRowsTw`** — it kept charging the page's
  declared pitch (`pitchTwHere`) while Google laid the rung. Its only measured failure was the block after
  the table, at **−18.16 pt**: *"the paragraphs following a ruled table must be placed from the table's LAID
  bottom … rather than from the sum of the declared heights it wrote."* Half B was never measured.

`18DISPLACEMENT-COUNT-0125-27NOV.md` §6 states the same rule independently, and its second clause is that
same missing half: *"charge the page budget, and the `w:before` that places the paragraph after the table,
with that same laid number."* The 26 Nov build is therefore not evidence against the rule — it is the rule
with its second line missing, and it failed exactly where that line sits.

### 3.2 The code site

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, method **`table(StringBuilder sb, PdfToWord.Table t, Ctx ctx)`** at **`:6005`** (the content-table writer; note that `COUNT-0125` calls it `emitTable` — no such method exists, see §4).

| line | what it is |
|--:|:--|
| `:6299`, `:6344-6345` | `rowTw` — the page's own pitch, unrounded; `float[] rowEdge = t.rowEdge` — its row edges, in pt |
| `:6440` | `for (int r = 0; r < keepRows; r++) {` — the row loop |
| `:6446-6450` | `rowTwHere` overridden per row from `rowEdge` when `exactRows` |
| `:6462` | `ruleTwHere` — the rule the row pays |
| `:6475` | `int pitchTwHere = rowTwHere;` — the pitch the flow is charged |
| `:6541` | `int rowHeightTw = Math.max(rowTwHere, rowLineTw);` — **the value written to `w:trHeight`** |
| `:6550-6551` | `writtenRowsTw += Math.max(0, Math.max(pitchTwHere, …))` — **the flow charge after the table (half B)** |
| `:6631-6632` | `<w:trHeight w:val="rowHeightTw" w:hRule="atLeast"/>` — where the declaration reaches the file |

### 3.3 The change, as a unified diff

Against HEAD `a554f74`, produced by editing the file and taking `git diff -U4`; the working copy was then
restored, so it applies to the tree as it stands. **Not compiled — no `javac` on this pod**; what was checked
instead is that the edit is brace/paren balanced against the pristine file.

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
index 80c91ee..934c31f 100644
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -6436,8 +6436,17 @@ public final class DocxWriter {
         // The running top edge of a re-cut table's rows, in points from the page top: its rows
         // are stacked from the table's own top, so row 2 starts one WRITTEN row below row 1.
         float recutTopPt = Float.NaN;
         float rowTopPagePtHere = Float.NaN;
+        // THE ROW IS LAID ON A 0.75 pt GRID, SO DECLARE THE RUNG AND CHARGE THE RUNG.
+        // Measured on 12 documents (FINDINGS/18DISPLACEMENT-COUNT-0125-27NOV.md §5):
+        //     laid = 0.75 * round((w:trHeight + rule) / 0.75)     <- nearest rung, both signs
+        // so a declaration is laid as written only when (declared + rule) is on a rung. The
+        // residue need not accumulate: each row picks its own rung, so a run of rows averages
+        // the page's pitch exactly (two at 14.25 + one at 13.50 = 42.00 for three rows of 14.00).
+        // cumLaidPt is that accumulator, reset per table: a table restarts its own row flow.
+        float cumLaidPt = 0f;
+        final int RUNG_TW = Integer.getInteger("p2w.rungTw", 15);   // 0.75 pt; 0 = identity
         for (int r = 0; r < keepRows; r++) {
             List<String> row = t.rows.get(r);
             // This row's own pitch. A ruled table's rule lies inside the row's box, so it comes
             // off here exactly as it comes off the average above.
@@ -6542,14 +6551,31 @@ public final class DocxWriter {
             if (ctx.squeeze != 1f) {
                 rowHeightTw = Math.max(typeFloorTw, twScale(rowHeightTw, ctx.squeeze));
                 rowLineTw = Math.max(typeFloorTw, twScale(rowLineTw, ctx.squeeze));
             }
-            // The budget is charged what the renderer will LAY OUT, which is the content plus
-            // the rule - not the content alone. Charging the content alone under-measures every
-            // ruled table by one rule a row, and this is the number the flow after the table is
-            // placed from.
-            writtenRowsTw += Math.max(0, Math.max(pitchTwHere,
+            // WHAT THE RENDERER WILL ACTUALLY LAY, and the declaration that makes it that.
+            // wantTw is where this row's bottom edge must fall, from the page's own edges (rowEdge
+            // is absolute, so subtract the table's first edge) and net of what the rows above have
+            // laid. mustTw is the content floor: hRule="atLeast" means a row whose text needs more
+            // is laid at its content, and the tracker must not credit a height that did not happen.
+            // A row cut at the paper's bottom (rowCapTw) is a clip, not a pitch - it keeps its pair.
+            int laidTw = Math.max(0, Math.max(pitchTwHere,
                     Math.max(rowTwHere, rowLineTw) + ruleTwHere));
+            if (RUNG_TW > 0 && exactRows && rowCapTw <= 0 && rowTwHere > 0) {
+                float wantPt = Math.max(0.75f, (rowEdge[r + 1] - rowEdge[0]) - cumLaidPt);
+                int wantTw = Math.round(wantPt * TWIPS_PER_PT);
+                int mustTw = rowLineTw + ruleTwHere;
+                rowHeightTw = Math.max(typeFloorTw,
+                        RUNG_TW * Math.round(Math.max(wantTw, mustTw) / (float) RUNG_TW) - ruleTwHere);
+                // what Google lays for the declaration just chosen - the law, applied once more
+                laidTw = RUNG_TW * Math.round((rowHeightTw + ruleTwHere) / (float) RUNG_TW);
+                cumLaidPt += laidTw / (float) TWIPS_PER_PT;
+            }
+            // The budget is charged what the renderer will LAY OUT - content plus rule - and
+            // this is the number the flow after the table is placed from. THE RUNG, NOT THE
+            // PITCH: this is half B. The 26 Nov build changed the line above and left this one
+            // charging the declared pitch - table rows -0.70, the block under them -18.16.
+            writtenRowsTw += laidTw;
             // THE ROW'S OWN TOP EDGE IN THE PAGE'S COORDINATES, when the pass that built the
             // table measured the row edges. The cells below are placed from it.
             //
             // From the PAGE's edges, not from the flow's position. Placing them from the flow
```

Notes a reviewer will want:
* `-Dp2w.rungTw=0` restores today's behaviour exactly: the `if` is skipped, `laidTw` is the old
  expression, `cumLaidPt` stays 0. That is the repo's own idiom for making a change an identity, and it is
  what the "did the change fire?" check in step 3 below turns on.
* The `w:before` of the paragraph that follows the table is **not** in this diff: it is derived from
  `writtenRowsTw`. If the test below shows the block after the table still off by the residual, the next
  site is that consumer, not this one.

### 3.4 The one document that best tests it

**`303_discharge_summary`** — not `320_balance_sheet_statutory`.

`320` is the wrong test now: its `worst_dy 19.4` has **two** causes — the row ramp *and* a third line at
y 776.57 whose own `w:before` is 18 pt short (`ROW-HEIGHT…` §"The reading that matters most") — and the ramp
has been cancelling the second. Any result on `320` is a difference of two errors.

`303_discharge_summary` isolates the rule: **one page, one ruled 4-row table, sole-18 (46/47), and its
whole displacement is the table.** From `COUNT-0125` §4a, measured in Google:

    source pitch 15.00 pt  ->  Google pitch 15.75 pt     (4 rows: +3.00 pt)
    declared <w:trHeight w:val="300" w:hRule="atLeast"/>  = 15.00 pt = exactly the source pitch
    dy by line: -0.20 (header) -> +0.55 -> +1.30 -> +2.05 -> +2.80 (last row) -> +4.10 (footer)

The rule predicts, before the render:

| quantity | stored | predicted after the diff | why |
|:--|--:|--:|:--|
| `w:trHeight` in `word/document.xml` | 300 ×4 | **285 ×4** | 15.00 laid needs `(declared+0.75)` on a 0.75 rung → declared 14.25 pt = 285 tw |
| Google row pitch | 15.75 | **15.00** | the page's own pitch, reached, not approached |
| footer dy | +4.10 | **≈ +1.10** | 3.00 pt of accumulated row error removed |
| `med_dy` | −0.20 | ≈ −0.05 | |
| verdict | 46/47, fails `18` | **47/47 PASS** | +1.10 pt is inside the 1.5 pt tolerance |

That is the value of this document: **it is a prediction that can be wrong**, where the halves separate.

### 3.5 The exact command — one document, no corpus rebuild

```bash
cd /scratch/work/CS

# 0. pod prerequisites (a warm pod prints "skipped (warm)" at every step)
bash tools/p2w-bench/pod-prep.sh

# 1. apply the diff above (save it as /scratch/work/18-row-rung.patch) and build
git apply /scratch/work/18-row-rung.patch
bash tools/p2w-bench/build-engine.sh

# 2. convert ONLY 303_discharge_summary: one file in a one-file shard, exactly what
#    corpus-convert.py's convert_one() does; classpath is build-engine.sh:92 verbatim
mkdir -p /scratch/work/one
ln -sf /scratch/work/p2w/corpus/303_discharge_summary.pdf /scratch/work/one/
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertAll /scratch/work/one /scratch/work/p2w/out && cd /scratch/work/CS

# 3. read the declaration off the .docx BEFORE spending a render (no Drive call)
unzip -p /scratch/work/p2w/out/303_discharge_summary.docx word/document.xml \
  | grep -o 'w:trHeight w:val="[0-9]*"' | sort | uniq -c
#    EXPECT:  4 w:trHeight w:val="285"
#    If it is still 300, the change did not fire (exactRows false, or rowCapTw>0) - stop here.

# 4. stage, then the three Drive steps on that ONE file, then collect
python3 tools/p2w-bench/gverify.py --stage 303_discharge_summary
#    upload /scratch/work/p2w/gverify/stage/303_discharge_summary.docx -> copy as Google Doc
#    -> export application/pdf -> download
python3 tools/p2w-bench/gverify.py --collect 303_discharge_summary <path-or-url-of-the-exported-pdf>
python3 -c "import json;d=json.load(open('benchmarks/gverify/303_discharge_summary.json'));print(d['passed'],'/',d['total'],d['failed'],d['displacement'])"

# 5. the per-line readout that says WHICH half worked (table rows vs the block under them)
python3 tools/p2w-bench/dy.py /scratch/work/p2w/corpus/303_discharge_summary.pdf \
                              /scratch/work/p2w/gverify/gd/303_discharge_summary.pdf

# 6. the LO control. A plain --lo answers "already have it" for ever after an engine change
#    (gverify.py:583) - force it, or the LO half is not measured at all:
python3 -c "import sys;sys.path.insert(0,'tools/p2w-bench');import gverify;print(gverify.collect_lo('303_discharge_summary', force=True))"
```

**What would falsify the hypothesis, stated before running** (all four are readable from step 3-5 alone):

1. `w:trHeight` is 285 and Google still lays **15.75** → "net of the rule" is wrong for this table; re-read
   `ruleTwHere` from the emitted `w:tblBorders` and re-fit.
2. The pitch is 15.00 and the footer still reads **+4.10** → the row is not what the footer follows; half B
   is at the wrong site, and the next place to look is the `w:before` consumer of `writtenRowsTw`.
3. The footer goes to **−3.0** → right in sign, wrong in size: the charge is applied twice (once in
   `writtenRowsTw`, once in the following paragraph's own gap).
4. **LibreOffice regresses** (18 fails in LO where it passed) → refused by non-negotiable 3, not by the
   physics: LO honours `w:trHeight` as a floor and collapses every row whose content is below the rung. Same
   collision `ROWH…` hit, and the one outcome that ends this line of work rather than redirecting it.

**Cost:** one build (~40 s), three Drive calls, one local LO render. No corpus rebuild, no 213-document
pass, no attempt recorded on a dirty tree.

## 4. Where the ledger contradicts itself

| # | contradiction | evidence |
|--:|:--|:--|
| C1 | **Three attempt counts for one class.** `ATTEMPTS.json` says `attempts: 99` and retains **20** history rows; `CLASS-HISTORY.jsonl` holds **86** rows, attempts 6, 7, 37, 53, 60, 66, 68, 73, 75, 77, 78, 92, 96 absent | both files |
| C2 | **A merge conflict committed into the ledger.** `CLASS-HISTORY.jsonl:221-225` contains `<<<<<<< HEAD` / `=======` / `>>>>>>> origin/main`; the HEAD side drops attempt 86 (`18_displacement`, 13:11) and substitutes a `t12_word_invention` row | `sed -n '221,225p'` |
| C3 | **The class history does not record its own refutation.** Last `18_displacement` row in `CLASS-HISTORY.jsonl` is attempt 99 at 03:28, outcome `lead`. `ATTEMPTS.json`'s last row is 04:17, outcome **`reverted`** — the `ROWH` corpus-wide refutation | both files |
| C4 | **Out-of-order history.** `ATTEMPTS.json`'s `18_displacement` history runs 02:11 *before* 01:51 and 01:52 | history[14..16] |
| C5 | **The most informative failed measurement exists only in the backup.** `ATTEMPTS.json.bak[0]` (10:22) holds *"residue fix built and rendered: med_dy +10.30 → −0.70 on 320 but the block after the table broke to −18.16 … reverted"*. `ATTEMPTS.json` has dropped it and kept 04:17 instead. The `.bak` says `attempts: 98`, the live file 99 | `.bak` vs `.json` |
| C6 | **A measured clean document counted as nothing.** 26 Nov 11:53, `moved: 1`: *"autoflow + `-Dp2w.autoEm=1.2207`: `72_bank_statement_no_rules_right_amounts` 41/42 → 42/42 PASS in Google"*, recorded as outcome **`lead`**, never landed, never re-measured, and in **no** FINDINGS file. Both flags still exist (`DocxWriter.java:130-142`) | ledger + code |
| C7 | **A FINDINGS file still stands under a title its own later half reverses.** `18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md` concludes "the declaration is a floor the content absorbs"; the same day's `ROW-HEIGHT…` correction shows the probe was a no-op (292 tw lands on 280's rung) and `w:trHeight` **is** read (3/3). The refutation is of the probe, not of the declaration | both files |
| C8 | **`COUNT-0125` §5 consequence 2 is contradicted by the code's own measurement.** It says `320_balance_sheet_statutory`'s *"content exceeded the declaration — that document cannot see the declaration at all"*. `ROW-HEIGHT…`'s engine build changed **only** `w:trHeight` on 320 (280 → 270/255/240) and moved `med_dy` +10.30 → −0.70. 320 sees the declaration | both files |
| C9 | **`COUNT-0125` names a method that does not exist.** It says `emitTable` (the content-table writer); the method is `table(StringBuilder, PdfToWord.Table, Ctx)` at `:6005`, and `emitTable` occurs only in a comment at `:1394`. (Its line numbers — `:6299`, `:6444`, `:6462`, `:6475`, `:6541`, `:6550`, `:6631` — all check out) | verified in this run |
| C10 | **Three engine stamps in one tree.** `ROUND.json` `fixer_engine_at_claim: ee5a00d6`; `ATTEMPTS.json`'s last rows say *"gate: restore DocxWriter to 9f0a8207"*; every recent `gverify` row is stamped `a4d8fca469bba636`. The 27NOV triage's whole denominator rests on `a4d8fca4` | three files |
| C11 | **The triage's "worth zero clean documents" is wrong on the current store.** It says the section-top-margin patch is *"worth zero clean documents because all the sole-`18` documents are single-page"*. `benchmarks/gverify/bank-statement-5-pages.json` is **46/47, fails only `18`, 5 pages** — and `PAGE-SCALE` §3d measured that patch at **47/47 PASS** on it | triage vs store |
| C12 | **`PAGE-SCALE` contradicts itself.** §3d: the patched render of `bank-statement-5-pages` is *"47/47 PASS"*. §5: the same document *"still fails `59_shape_anchor` → not clean"*. The stored row (no `59`) sides with §3d | same file, §3d vs §5 |
| C13 | **Three dangling citations, one of them cited twice as if it existed.** `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md` (cited by `GAP-CARRIER`'s provenance and by `HANDOFF.md`), `FINDINGS/18-displacement-PAGE-BREAK-IS-UNEARNED-26NOV-relay.md` (`HANDOFF.md`), and `FINDINGS/18-displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md` (cited by `SINGLE-PAGE-SPACER` and `COUNT-0125` as the origin of the 0.75 pt law). `FINDINGS/` holds 19 entries; none of the three is among them. **The derivation of the law this whole class now rests on is not in the tree** | `ls FINDINGS/` |
| C14 | **`HANDOFF.md`'s instruction block is corrupted.** "What the next run should do first" is the same ~300-word paragraph repeated four times | `HANDOFF.md:15-20` |
| C15 | **An engine patch that rolls the ledger back.** `patches/18-row-pitch-net-of-rule-and-subpoint-grid.patch` bundles `HANDOFF.json`, `ROUND.json`, `RUN.json`, `ROTATION.json`, `TIMELINE.jsonl`, `TRACE.md`, `RUN-LOG.md` into the change. `git apply --check` fails on exactly those files (the `DocxWriter`/`PdfToWord` hunks still check clean). Its engine content is also dead: it declares `hRule="exact"` and `trHeight − 2×rule`, refuted by R2 and R3 | verified in this run |
| C16 | **The class is PARKED on an overturn condition that has since fired.** `ROTATION.json` parked it 25 Nov 21:07 with *"Overturned by: one measured attempt that moves a document under this class on the current engine."* `ROWH…` then measured two Google 41/42 → 42/42 — but on `362_price_list_dense` / `16_right_aligned_amounts_txtpos`, i.e. not "moves a document" under the charter's own definition, so the parking stands on a technicality while every later row is written `PARKED` | `ROTATION.json`, `CLASS-HISTORY.jsonl` |

## 5. What this run could not do

* **No Google measurement and no compile.** No PDFs, no Drive, no `javac`: every `med_dy` / `worst_dy` /
  pass count in §1-3 is quoted from a named source, and §3.3's diff is checked for balance, not compiled.
* **The triage's denominator was not recomputed** (205 scored rows of 213 files; the current-engine subset
  is 61, which `report.py:551-579` computes).

**Open questions** — things only the repo's owners can settle, not guessed here:

1. Which of the three engine stamps is the tree's (`ee5a00d6`, `9f0a8207`, `a4d8fca4`)? Every denominator in
   the 27NOV triage depends on the answer.
2. Was the 26 Nov 11:53 `autoflow + autoEm=1.2207` result (`72_bank_statement` 41/42 → 42/42 PASS in Google)
   ever re-measured? It is the only `moved: 1` in the class and it is in no FINDINGS file.
3. Where is the derivation of `laid = 0.75 × round((trHeight + rule) / 0.75)`? Two findings cite
   `FINDINGS/18-displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`; it is not in the repo.
4. Is the `pgMar w:top` patch (rank 2) still refused for any reason other than the table stamp? The ledger
   names none.
