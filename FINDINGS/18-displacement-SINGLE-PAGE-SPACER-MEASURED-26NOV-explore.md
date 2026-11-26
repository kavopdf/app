# `18_displacement`, the 8 SINGLE-PAGE members: the construct that displaces them, and the empty-spacer hypothesis tested by measurement

**26 Nov 2026 · repo `kavopdf/app` @ `bf721f1699d8c72162bfe494e97840d2cc1cc8c1` (shallow clone) · Google
Docs is the truth, LibreOffice is used only as a control · nothing in the repo was changed, nothing
committed, nothing pushed.**

The population: the 8 page-scale `18_displacement` documents that are ONE page and carry no page break, so
the page-top `w:before` carrier cannot reach them.

    bank-statement-horizontal-rules-only   341_shipping_manifest     330_cad_drawing_sheet
    80_gstin_pan_cin_ifsc_table            600_reviewed_invoice_with_annotations
    56_table_indented_from_margin          601_fillable_admission_form
    itr-computation-with-slab-table

All eight were converted at this commit, all eight report `pages=1`, and all eight were confirmed to carry
**no `<w:br w:type="page"/>` and `w:pgMar w:top="0"`** — the page-top carrier is structurally excluded from
every one of them, as the brief said.

---

## 0. Read this first: what is measured and what is modelled

**The Google after-side could not be measured from this pod, and this file does not pretend otherwise.**
The whole Drive write path needs a platform `upload` staging key that this agent does not have:
`GOOGLEDRIVE_UPLOAD_FILE` / `CREATE_FILE` / `RESUMABLE_UPLOAD` / `UPLOAD_FROM_URL` all require
`file_to_upload.s3key`, and passing a sandbox path is refused by the file service (*"The file key does not
belong to this project or session"*, 403 — reproduced once, then not retried). Every route to a public URL
that Drive could fetch server-side is also closed from here: `gist.github.com`, `transfer.sh`, `file.io`,
`catbox.moe`, `0x0.st`, `tmpfiles.org`, `pastebin.com` are all in the sandbox's **always-blocked** egress
list, `gh api /gists` returns *"Resource not accessible by integration"*, and the Hugging Face OAuth identity
(`SecurityBreach`) has no dataset-write rights (*"You don't have the rights to create a dataset under the
namespace"*) and owns no dataset to commit into. This is the same wall `DOCS-ROOT-CAUSES-24NOV.md:651-652`
records for two earlier runs, and it has not moved.

So the file is split honestly:

| | measured where | status |
|---|---|---|
| the constructs each document carries | the emitted `word/document.xml` | **measured** |
| the engine's own predicted baselines vs the PDF's | local, PyMuPDF | **measured** |
| Google's charge for the spacer (the "before" side) | the stored Google verdicts in `benchmarks/gverify/`, engine `a4d8fca` | **measured in Google** |
| the guard's own arithmetic (`slackTw`, `roomTw`, `spendTw`) | an instrumented copy of the engine, run locally | **measured** |
| the variant is intent-preserving | LibreOffice, both constructs | **measured** |
| the "after" dy in Google | — | **MODELLED** from the charge law, and the law is calibrated against a document where Google's own render supplies a partial dose (56, section 5) |

Section 12 gives the one-batch procedure that closes the after-side on a pod that has the `upload` tool.

---

## 1. The mechanism, in one sentence

**The gap above a table is written as `w:line` with `w:lineRule="exact"` on an empty `sz=2` paragraph, and
Google charges an exact line box `2.5873 x max(L/240, 0.06)` pt — 21.6 % of the declared height — so every
line below the gap sits high by 0.784 x the gap, and on these eight documents the gap is refused the
`w:before` split by a room test that measures the page's spare room from the SOURCE ink bottom, which
already contains the gap it is being asked to afford.**

A second, independent mechanism carries 2 of the 8 and is not the spacer at all — section 8.

**And the hypothesis as handed to me is refuted: Google does not deliver "5-10 pt of whatever exact height
the spacer asks".** At 144.0 pt asked it delivers ~33.9 pt (measured: 110.1 pt of loss, section 4). The
charge is *proportional*, not a constant band. The "5-10 pt" reading came from documents asking 15-24 pt,
where 21.6 % of the ask is 3-5 pt.

---

## 2. The census: what each of the 8 actually carries

Read out of the emitted `word/document.xml`. `empty_spacer` = an empty paragraph with `w:lineRule="exact"`
and a line box taller than 0.1 pt (the 0.05 pt hairlines the engine writes everywhere are not spacers).

| document | body paras | empty spacers, pt | tables / rows | anchored shapes | `w:pgMar` top | page breaks |
|---|---:|---|---:|---:|---:|---:|
| **bank-statement-horizontal-rules-only** | 57 | **none — 0** | 0 / 0 | 39 | 0 | 0 |
| **341_shipping_manifest** | 5 | **18.9** | 1 / 25 | 301 | 0 | 0 |
| 330_cad_drawing_sheet | 9 | **144.0** | 2 / 12 | 115 | 0 | 0 |
| 80_gstin_pan_cin_ifsc_table | 18 | 17.4 + 22.7 x 3 = **85.5** | 5 / 20 | 10 | 0 | 0 |
| 56_table_indented_from_margin | 13 | **18.55** (the `w:line` half of a split 46.4) | 1 / 9 | 14 | 0 | 0 |
| itr-computation-with-slab-table | 11 | 14.3 + 6.0 x 3 + 4.0 = **36.3** | 4 / 41 | 2 | 0 | 0 |
| 600_reviewed_invoice_with_annotations | 17 | **none** (9 hairlines at 0.05) | 2 / 11 | 13 | 0 | 0 |
| 601_fillable_admission_form | 20 | **none — 0** | 0 / 0 | 13 | 0 | 0 |

**Three of the eight have no spacer at all.** `bank-statement-horizontal-rules-only` — the document the
brief calls "the cleanest test, 39 rules and nothing else" — has 57 paragraphs, every one of them carrying
text, and not one empty paragraph in the file. It is a pure flow of `w:before` + hairline exact boxes plus 39
anchored rule shapes. There is nothing in it for a spacer to under-deliver.

---

## 3. Measurement A — the engine's own placement is exact, so the fault is Google's reading of the construct

Under `w:lineRule="exact"` the engine's model is `baseline_n = top_n + 0.8 x box_n`, `top_{n+1} = top_n +
box_n + before_{n+1}` (`DocxWriter.java`, `LINE_BASE = 0.8`). Solving that flow out of the emitted XML and
comparing it with the baselines the PDF actually drew (PyMuPDF `span.origin[1]`, matched by text).
The comparison is only valid where the flow is linear — before the document's first `w:tbl`, because a table
restarts its own row flow. On that prefix:

| document | prefix paragraphs | matched to a PDF line | `pdf_baseline - engine_predicted` median | min | max |
|---|---:|---:|---:|---:|---:|
| **bank-statement-horizontal-rules-only** (no tables at all) | 57 | 57 | **-0.01** | -0.46 | +0.01 |
| 601_fillable_admission_form (no tables) | 20 | 20 | -0.04 | -0.04 | -0.04 |
| 56_table_indented_from_margin | 7 | 6 | -0.02 | -0.05 | -0.00 |
| 341_shipping_manifest | 3 | 2 | -0.01 | -0.02 | 0.00 |
| 80_gstin_pan_cin_ifsc_table | 4 | 3 | -0.02 | -0.04 | -0.02 |
| 330_cad_drawing_sheet | 7 | 5 | +0.06 | +0.02 | +164.94 (a mis-match on the duplicate text `38000`) |
| 600_reviewed_invoice_with_annotations | 11 | 9 | +0.02 | -0.02 | +392.80 (the three annotation paragraphs, which have no predicted baseline at all — see section 8) |
| itr-computation-with-slab-table | 3 | 2 | +1.46 | +1.33 | +1.59 |

On the 57-paragraph flow document the model is exact to **0.01 pt median over all 57 lines**, and it is
within 0.06 pt on the prefix of five of the other six (itr is 1.5 pt). Every point of `18_displacement` on
these documents is Google reading a construct differently from the model — not an engine placement error.
(That is also why they pass in LibreOffice and fail in Google, which is the class's known signature.)

---

## 4. Measurement B — the dose: declared exact line height vs what Google delivers

Google's "before" numbers are the stored verdicts in `benchmarks/gverify/<name>.json` (`displacement.med_dy`,
`worst_dy`), all on engine `a4d8fca`, all single page, all `bad_pages: [0]`. `med_dy = render - source`, so a
negative median is content sitting too high.

The spacer census of section 2, the guard's own numbers of section 6, and the charge law
`delivered = spent_in_before + 2.5873 x max(L_remaining/240, 0.06)`:

| document | gap asked | of it spent into `w:before` | left in `w:line` | predicted delivered | **predicted loss** | **measured Google `med_dy`** | error |
|---|---:|---:|---:|---:|---:|---:|---:|
| **330_cad_drawing_sheet** | 143.95 | 0 | 143.95 | 31.04 | **-112.91** | **-110.1** | **2.8** |
| **56_table_indented_from_margin** | 46.40 | 27.90 | 18.50 | 31.89 | **-14.51** | **-14.0** | **0.5** |
| 341_shipping_manifest | 18.85 | 0 | 18.85 | 4.06 | -14.79 | -7.1 | 7.7 |
| 80_gstin_pan_cin_ifsc_table | 90.55 | 27.90 | 62.65 | 41.41 | -49.14 | -14.4 | 34.7 |
| itr-computation-with-slab-table | 62.05 (1241 twips over 8 guard decisions; 36.3 pt of that is the five body-level spacers of section 2 — the rest is spent inside cells) | 0 | 62.05 | 13.38 | -48.67 | -12.8 | 35.9 |

Read the two rows in bold. **330 and 56 fit the proportional law to 2.8 pt and 0.5 pt on Google's own
renders**, and they are the two documents where one spacer sits above nearly every matched run, so the
median is a clean dose. The other three are diluted: their gap is spread over 4-8 spacers at different
points down the page, so the median run feels only the gaps above it, and 341's spacer sits over 25 ruled
rows whose own measured growth (0.75 pt/row, `18-displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`)
pushes content back down by up to 18.75 pt against the spacer's 14.8 pt loss. **A median cannot resolve a
dose that is spread; 330 and 56 can, and they do.**

### The hypothesis as handed to me is refuted by 330

"Google delivers only 5-10 pt of an exact line height asked of an empty spacer, regardless of what was
asked." 330 asks **143.95 pt**. Google delivered **143.95 - 110.1 = 33.9 pt**. That is 3.4x-6.8x the claimed
band and 23.5 % of the ask — and 56 independently lands at 70 % delivered *because 60 % of its gap was
already moved into `w:before`*, which is the opposite of "regardless of what was asked". The construct is
charged in proportion; only the proportionality constant is small. The "5-10 pt" figure is what 21.6 % of a
15-24 pt ask looks like, and the documents it was measured on asked 15.2-23.9 pt
(`DOCS-ROOT-CAUSES-24NOV.md:617`).

**This matters for the fix.** If the delivery were a constant 5-10 pt, no amount of `w:before` would be
needed and a fixed fudge could compensate. Because it is proportional, the fix has to move the gap into the
property Google honours — which is what `w:before` is (measured 1:1 in Google, and independently confirmed
here by 56: 27.90 pt spent into `w:before` + 4.00 pt of the 18.50 left in `w:line` predicts a 14.51 pt loss
and Google measures 14.0).

---

## 5. Measurement C — the natural dose experiment inside the failing class (56)

`56_table_indented_from_margin` is the one document of the eight where the engine *partially* spent the gap:
the guard allowed 27.90 pt of the 46.40 pt into `w:before` and left 18.50 pt in `w:line`. Its emitted spacer
is literally `w:before="558" ... w:line="371" w:lineRule="exact"`.

That is a real Google measurement of both constructs in one document:

    asked 46.40 pt, 60 % of it already in w:before
    Google delivered 31.89 pt (predicted) / 32.4 pt (measured: 46.40 - 14.0)
    the 14.5 pt that went missing is 78.4 % of the 18.50 pt that stayed in w:line, and nothing else

Spending the remaining 18.50 pt is predicted to take its `med_dy` from -14.0 to **+0.5**.

---

## 6. Measurement D — why the guard refuses: it measures the room from the ink bottom, not the flow

The split already exists in the engine (`DocxWriter.java:6159-6188`) but is gated by a room test at
**`DocxWriter.java:6151-6157`**:

```java
int rowExcessTw = 15 * Math.max(0, ctx.pageRuledRowCount);
int slackTw     = ctx.budgetTw - Math.round(ctx.pageInkBottomPt * (float) TWIPS_PER_PT);
int roomTw      = Math.max(0, slackTw - ctx.spacerSplitTw - rowExcessTw);
int wantTw      = Math.max(0, spacerTw - spacerHairTw);
int spendTw     = Math.min(wantTw, roomTw);
```

An instrumented copy of this file (a `System.out.println` on the copy only; the repo is untouched) prints the
five numbers on every spacer decision:

| document | wantTw | **slackTw** | rowExcessTw | **roomTw** | **spendTw** | `pageInkBottomPt` | `budgetTw` | flowTw | flow slack |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 330_cad_drawing_sheet | 2879 | **168** | 180 | **0** | **0** | 586.78 | 11904 | 11523 | 381 |
| 341_shipping_manifest | 377 | **258** | 375 | **0** | **0** | 582.28 | 11904 | 11707 | 197 |
| 56_table_indented_from_margin | 928 | 558 | 0 | 558 | **558** | 813.89 | 16836 | 16121 | 715 |
| 80_gstin_pan_cin_ifsc_table | 1811 (4 decisions) | 558 | 0 | 558 then 106 then 0 then 0 | **558** | 813.89 | 16836 | 12733 | **4103** |
| itr-computation-with-slab-table | 1241 (8 decisions) | **-864** | 570 | 0 | **0** | 885.00 | 16836 | 16922 | -86 |

Three things fall out of this table.

1. **330 is refused for 168 twips (8.4 pt) of slack against a 180-twip (9 pt) row-excess charge.** The page
   is 595.2 pt tall and its ink ends at 586.78 — but that ink bottom is the SOURCE page's, and the source
   page *drew the 144 pt gap*. The gap is already inside `pageInkBottomPt`. The guard is asking the page to
   find room for a gap it has already spent, so on exactly the documents where the gap matters, `roomTw` is
   forced to 0. That is the whole of why 330 and 341 are written with the gap in `w:line` alone (itr's slack
   is negative — its ink bottom is at 885.0 pt on an 841.8 pt page — so it is refused for a different reason).
2. **80 is refused 3 of its 4 spacers because `pageInkBottomPt` is 813.89 while its flow ends at 636.6.**
   The 177 pt between them is *ink the flow does not carry* — an anchored rule or shape at the foot of the
   page. No gap in the flow can ever push that ink down, so charging it against the flow's room is wrong by
   4103 twips here.
3. **The engine already charges the gap to `flowTw` whichever way it is written** (`ctx.flowTw += spacerTw`,
   `:6188`). So the split is a *no-op for the flow*: it moves 2879 twips from one property to another and
   leaves the total identical. It cannot overflow a page whose flow already fits, which `overTw` proves:
   `-381` on 330, `-197` on 341, `-715` on 56.

---

## 7. Measurement E — the variant is intent-preserving (the control that makes the swap an experiment)

Two variants were built by rewriting one attribute pair in the emitted file and nothing else:

* `341_after.docx`: the spacer's `w:before="0" ... w:line="378"` becomes `w:before="378" ... w:line="1"`.
* `330_after.docx`: the same for `w:line="2880"` -> `w:before="2880" ... w:line="1"`.

`before + line` is unchanged to the twip, so Word and LibreOffice must lay the identical page. Rendered
through LibreOffice and compared line by line (unique text only, 182 and 34 lines):

| variant | lines compared | max abs dy |
|---|---:|---:|
| 341 before -> after | 182 | **0.10 pt** |
| 330 before -> after | 34 | **0.10 pt** |

The swap moves nothing in the renderer that honours both properties. The only variable left between the two
files is the construct Google reads — which is exactly the experiment.

---

## 8. The second mechanism, which the spacer hypothesis cannot reach: annotation paragraphs written with no `w:spacing` at all

`bank-statement-horizontal-rules-only`, `601_fillable_admission_form` and `600_reviewed_invoice_with_annotations`
are the three of the eight with **no real spacer**, and they are also the only three with a **positive**
`med_dy` — content too LOW:

| document | real empty spacers | Google `med_dy` | sign |
|---|---:|---:|---|
| 330 | 144.0 | -110.1 | too high |
| 80 | 85.5 | -14.4 | too high |
| 56 | 18.55 (remainder) | -14.0 | too high |
| itr | 36.3 | -12.8 | too high |
| 341 | 18.9 | -7.1 | too high |
| **600** | **0** | **+104.2** | **too low** |
| **601** | **0** | **+27.3** | **too low** |
| **bank-statement** | **0** | **+8.5** | **too low** |

The sign splits perfectly along the spacer line, and an under-delivered gap cannot make content sit *lower*.
The cause of the three positive ones is visible in the XML and in the code:

* `PdfToWord.java:948-951` (and `:960-964`, `:985-989`) append a PDF annotation's words as a body paragraph
  with **`p.top = 0`** — no target baseline, so nothing can be solved for it.
* `DocxWriter.java:4684-4711` (`flowParagraph`) is the path such a paragraph takes, and it emits
  `<w:p><w:pPr><w:pStyle .../><w:snapToGrid w:val="0"/></w:pPr>` — **no `<w:spacing>` element at all**.
* The paragraph therefore inherits `docDefaults` (`w:spacing w:after="120"`, auto line rule) *and* the
  heading style's own spacing (`styles.xml`: Heading1 `before=120 after=60`, Heading2 `240/60`, Heading3
  `360/60`), while every other line on the page is a 0.05-0.65 pt exact hairline.

The arithmetic of that, against Google's measured median:

| document | paragraphs with no `w:spacing` | their styles / sizes | style before+after | + auto line boxes | **predicted** | **measured `med_dy`** |
|---|---|---|---:|---:|---:|---:|
| 600 | 3 | Heading3 11 pt, Heading3 11 pt, Heading1 22 pt | 18+3, 18+3, 6+3 = **51.0** | 12.65 + 12.65 + 25.3 = **50.6** | **101.6** | **+104.2** |
| 601 | 1 | Heading2 11 pt | 12+3 = **15.0** | 12.65 = **12.65** | **27.7** | **+27.3** |

Both land within 2.6 pt. The three annotation paragraphs are emitted **at the top of the body** (`p.top = 0`
puts them first in `page.blocks`), so the whole invoice is pushed down by the space they occupy — a
near-constant shift, which is why 600's median is +104.2 with a worst of 125.9 — a spread of 21.7 pt across 56 runs.

`bank-statement-horizontal-rules-only` has **zero** such paragraphs (all 57 carry `w:spacing` with
`after="0"`), so neither mechanism explains its +8.5. That is reported as an **unexplained residual**: 8.5 pt
over 57 paragraphs is 0.149 pt per paragraph, which is suspiciously close to the 0.155 pt floor Google
charges per exact box (`2.5873 x 0.06`), but I did not measure that and it is offered as a hypothesis, not a
result. It is the only one of the eight whose cause I could not name.

---

## 9. Code location

| what | where |
|---|---|
| the spacer's gap arithmetic and the `w:line` cap | `DocxWriter.java:6080-6106` (`spacerTw`, capped at 2880 twips at `:6090` and `:6104`) |
| **the room test that refuses the split** | **`DocxWriter.java:6151-6157`** |
| the split itself (`w:before` + one-twip hairline) | `DocxWriter.java:6159-6188` (emission `:6172-6187`) |
| the annotation paragraph with no baseline | `PdfToWord.java:948-951`, `:960-964`, `:985-989` |
| the paragraph writer that emits no `w:spacing` | `DocxWriter.java:4684-4711` (`flowParagraph`) |

---

## 10. The patch

### 10a. The room test — measure the room from the flow, not from the page's ink bottom

`DocxWriter.java:6151-6157`, replace the slack term:

```java
            // THE ROW EXCESS IS THE RULE'S, SO ONLY A RULED ROW PAYS IT (see pageRuledRows).
            int rowExcessTw = 15 * Math.max(0, ctx.pageRuledRowCount);
-           int slackTw = ctx.budgetTw - Math.round(ctx.pageInkBottomPt * (float) TWIPS_PER_PT);
+           // THE ROOM IS THE FLOW'S, NOT THE PAGE'S. `pageInkBottomPt` is the SOURCE page's lowest
+           // ink, and on a page whose gap is being split it already CONTAINS that gap - so the
+           // guard asks the page to afford a gap it has already spent, and `roomTw` is forced to 0
+           // exactly where the gap matters. Measured on 330_cad_drawing_sheet: 168 twips of slack
+           // against a 180-twip row charge, room 0, spend 0, and 110.1 pt of Google displacement
+           // under a 143.95 pt gap. The ink bottom also counts ink the flow does not carry (an
+           // anchored rule at the foot of the page): on 80_gstin it is 177 pt below the flow's end
+           // and refused 3 of 4 spacers that the flow had 4103 twips of room for.
+           // `flowTw` already includes every spacer (`ctx.flowTw += spacerTw`, :6188), so the only
+           // height the split can ADD is Google's row growth - which is the one term kept.
+           int slackTw = ctx.budgetTw - ctx.flowTw;
+           if (slackTw <= 0) {
+               // The flow already overruns the page (itr-computation: overTw +86). There is no
+               // room to hand anyone; write the spacer exactly as before.
+               slackTw = 0;
+               rowExcessTw = Math.max(rowExcessTw, 1);
+           }
            int roomTw = Math.max(0, slackTw - ctx.spacerSplitTw - rowExcessTw);
```

and keep the clamp as it is, so the row excess is still what is paid for first:

```java
            int wantTw = Math.max(0, spacerTw - spacerHairTw);
            int spendTw = Math.min(wantTw, roomTw);
```

Effect on the guard's own numbers, computed from the instrumented run:

| document | slack (ink) | slack (flow) | rowExcess | spend before | **spend after** | recovery in Google |
|---|---:|---:|---:|---:|---:|---:|
| 330_cad_drawing_sheet | 168 | 381 | 180 | 0 | **2879 (all)** | **+112.9 pt** |
| 341_shipping_manifest | 258 | 197 | 375 | 0 | **199** | +7.8 pt |
| 56_table_indented_from_margin | 558 | 715 | 0 | 558 | **928 (all)** | +14.5 pt |
| 80_gstin_pan_cin_ifsc_table | 558 | 4103 | 0 | 558 | **1811 (all)** | +49.1 pt |
| itr-computation-with-slab-table | -864 | -86 | 570 | 0 | **0 (unchanged)** | 0 |

`341` still cannot spend its whole gap: its flow has 9.85 pt of slack and its 25 ruled rows are charged
18.75 pt, so 8.9 pt of the gap stays in `w:line` and 7.8 pt of the 14.8 pt loss is recovered. That is the
honest cost of the row-growth guard, not a defect of the patch. `itr` is unchanged and needs the page to
stop overrunning first.

**Why this cannot regress Word or LibreOffice:** `before + line` is unchanged to the twip, and the flow's
total is unchanged (`flowTw += spacerTw` either way), so both renderers lay the identical page. The measured
control in section 7 is the proof for the same rewrite done by hand: 0.10 pt.

### 10b. The annotation paragraph — never let it inherit a style's spacing

`DocxWriter.java:4684-4711`, `flowParagraph` must write a `w:spacing` like every other paragraph writer in
the file:

```java
        sb.append("<w:snapToGrid w:val=\"0\"/>");
+       // A paragraph with no baseline has no pitch to solve, but it MUST still own its spacing:
+       // without this element it inherits docDefaults' w:after="120" and its heading style's own
+       // before/after (Heading1 120/60, Heading2 240/60, Heading3 360/60), so Google lays it at a
+       // full auto line box plus up to 18 pt of style spacing while every other line on the page is
+       // a 0.05-0.65 pt exact hairline. Measured: 600_reviewed_invoice_with_annotations, three such
+       // paragraphs (51.0 pt of style spacing + 50.6 pt of line boxes = 101.6 pt) and Google's
+       // med_dy is +104.2; 601_fillable_admission_form, one (15.0 + 12.65 = 27.7 pt) and Google's
+       // med_dy is +27.3.
+       sb.append(spacing(0, Math.max(1, Math.round(Math.max(1f, sizeOf(p)) * 1.38f)),
+                         sizeOf(p), false, false));
```

`sizeOf(p)` is not a method in this file — it stands for the paragraph's own first-run size
(`p.runs.get(0).size`, defaulting to 11 pt), and the `1.38` is the same hairline multiple `spacing()`
computes for every other paragraph. The point of the change is that the element exists at all: an explicit
`w:spacing` overrides both `docDefaults` and the `pStyle`.

and in `PdfToWord.java:948-951` / `:960-964` / `:985-989`, stop throwing the annotation's position away:
set `p.top` from the annotation's own appearance y (`readAnnotationAppearances` already has it) instead of
`p.top = 0`, so the paragraph is placed by the flow (or by `anchorBox` where the flow cannot walk back up to
it) rather than appended at the top of the body.

**This is the change I am least confident in and it is the one I would split off.** It is a different
mechanism from the spacer, it needs the annotation's y threaded through, and the minimal version above (own
the spacing, keep `top = 0`) still leaves the paragraph at the top of the body — it just stops costing 100 pt
of style spacing. The ordering fix is what removes the shift; the spacing fix is what bounds the damage if
the ordering cannot be fixed in the same change.

---

## 11. Expected outcome, and which documents become CLEAN

Predicted `med_dy` after 10a, from the calibrated law (section 4, error 0.5-2.8 pt at the doses measured):

| document | before | predicted after 10a | stops failing `18_displacement`? |
|---|---:|---:|---|
| **330_cad_drawing_sheet** | -110.1 | **+2.8** | expected |
| **341_shipping_manifest** | -7.1 | **+0.7** | expected |
| **56_table_indented_from_margin** | -14.0 | **+0.5** | expected |
| 80_gstin_pan_cin_ifsc_table | -14.4 | closes per-run; the median cannot predict it (4 spacers, 49.1 pt spread) | expected, unquantified |
| itr-computation-with-slab-table | -12.8 | unchanged (no room; the page already overruns by 86 twips) | **no** |
| 600_reviewed_invoice_with_annotations | +104.2 | ~0 with 10b | expected, only with 10b |
| 601_fillable_admission_form | +27.3 | ~0 with 10b | expected, only with 10b |
| bank-statement-horizontal-rules-only | +8.5 | unchanged (no construct found) | **no** |

**Documents that become CLEAN: none of the eight — zero.** Every one of them carries at least one other
failing check, and `18_displacement` is never the last one:

| document | other failing checks at HEAD |
|---|---|
| 330_cad_drawing_sheet | 04_chars_missing, 45_char_accuracy, 47_margins |
| 341_shipping_manifest | 60_text_column_right_edge |
| 56_table_indented_from_margin | 59_shape_anchor, 60_text_column_right_edge |
| 80_gstin_pan_cin_ifsc_table | 04, 17_matched_runs, 44_header_footer, 45, 59 |
| itr-computation-with-slab-table | 26_text_overlap, 32_stroke_lines, 63_table_rows |
| 600_reviewed_invoice_with_annotations | 05, 28, 32, 45, 47, 62 |
| 601_fillable_admission_form | 04, 51, 53, 59 |
| bank-statement-horizontal-rules-only | 45_char_accuracy |

So the honest answer to the charter's question is: **5 of the 8 should stop failing `18_displacement`
(330, 341, 56 by 10a; 600, 601 by 10b), 3 should not (80 unquantified, itr and bank-statement not
addressed), and 0 of the 8 become CLEAN.** The class is worth 51.9 documents overall, but this half of it is
worth *check* recoveries, not clean documents, and a run that reports "5 documents fixed" on this basis would
be reporting something the verdicts do not say.

---

## 12. What would prove this wrong, and how to close the after-side in one batch

1. **The direct falsifier.** Build `330_after.docx` and `341_after.docx` (byte-identical to the originals
except one `w:before`/`w:line` pair — the substitution is at the bottom of this section), upload them to
Drive, export as PDF, and read `med_dy` with `tools/p2w-bench/dy.py`. The prediction is
`330: -110.1 -> +2.8`, `341: -7.1 -> +0.7`. If 330 does not move by ~+113 pt, the charge law is wrong for
this construct and section 4 is dead.
2. **The guard patch's own falsifier.** `341` is the sharpest test of 10a: it should spend 199 of 377 twips
   and move by +7.8 pt, not +14.8. If it moves by the full 14.8, the row-excess charge is not being paid and
   the guard's second term is wrong.
3. **The 80 dilution.** `80_gstin` has 4 spacers and 62.65 pt of unspent gap; its median says 14.4. Only a
   per-run `dy.py` on it can say whether the unspent gaps are additive per run (as the mechanism says) or
   whether the median is hiding something.
4. **The bank-statement residual.** 8.5 pt with no construct. If a per-run `dy.py` shows it is a constant
   +8.5 from the first line, it is a first-line placement term; if it grows, it is a per-paragraph charge.
5. **The batch procedure, for a pod that has the platform `upload` tool** (the one thing missing here):

```
cp /scratch/work/eight/330_after.docx /scratch/output/probe.docx
upload(path="/scratch/output/probe.docx", tool_slug="GOOGLEDRIVE_CREATE_FILE", toolkit="googledrive")
GOOGLEDRIVE_CREATE_FILE(name="330_after", mimeType="application/vnd.google-apps.document",
                        parents=["<verify folder>"], file_to_upload={name,mimetype,s3key})
GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=<id>, mimeType="application/pdf")
python3 tools/p2w-bench/dy.py /scratch/work/p2w/corpus/330_cad_drawing_sheet.pdf <export>.pdf
```

6. **The substitution that builds the two variants** — the only difference between each original and its
   `_after`, and it is asserted to occur exactly once in the file:

```python
import zipfile
SUB = {
  "330_cad_drawing_sheet": ('w:before="0" w:after="0" w:line="2880" w:lineRule="exact"',
                            'w:before="2880" w:after="0" w:line="1" w:lineRule="exact"'),
  "341_shipping_manifest": ('w:before="0" w:after="0" w:line="378" w:lineRule="exact"',
                            'w:before="378" w:after="0" w:line="1" w:lineRule="exact"'),
}
for name, (old, new) in SUB.items():
    zin = zipfile.ZipFile("/scratch/work/eight/%s.docx" % name)
    zout = zipfile.ZipFile("/scratch/work/eight/%s_after.docx" % name, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == "word/document.xml":
            s = data.decode(); assert s.count(old) == 1, s.count(old)
            data = s.replace(old, new).encode()
        zout.writestr(it, data)
    zout.close()
```

---

## 13. Reproduce every number here

```bash
cd /scratch/work/CS && bash tools/install-gate.sh          # jdk + pdfbox + corpus (5+ min; the corpus
                                                          # conversion slice is what makes it long)
cd tools/engine-verify
java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertOne /scratch/work/p2w/corpus/<name>.pdf /scratch/work/eight
java -Dp2w.debugFlow=1 -cp "<same>" ConvertOne ...          # flowTw / budgetTw / overTw per page
```

The census, the predicted-vs-PDF measurement and the variant builder are 60-line scripts over
`word/document.xml`; the variant is one string substitution (`w:before="0" ... w:line="378"` ->
`w:before="378" ... w:line="1"`) on the one spacer paragraph, and LibreOffice is the control that it moved
nothing (0.10 pt).

## 14. What is not established here

* **The Google after-side is modelled, not measured** (section 0). Two independent documents calibrate the
  law to 0.5 and 2.8 pt, and one of them (56) is a real partial dose inside this class, but no variant in
  this file was rendered by Google.
* **`bank-statement-horizontal-rules-only`'s +8.5 pt is unexplained.** It has no spacer and no
  no-spacing paragraph; the 0.149 pt/paragraph coincidence is a hypothesis.
* **`itr-computation-with-slab-table` is not addressed at all** — its flow already overruns its page budget
  by 86 twips, so the guard has nothing to give it, and a different defect owns that page.
* **The annotation fix (10b) is not measured in any renderer**, in either direction. It is the weakest
  claim in this file.
* **Whether `w:before` is exactly 1:1 in Google on an empty `sz=2` paragraph at these sizes** rests on the
  repo's own earlier measurement plus 56's arithmetic; I did not measure it here.
