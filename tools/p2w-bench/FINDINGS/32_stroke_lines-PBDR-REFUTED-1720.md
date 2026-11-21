# Does a `w:pBdr` paragraph border fix `32_stroke_lines` in Google — or only move the LibreOffice number?

**Class:** `32_stroke_lines` (145 documents open, 144 of them LibreOffice-correct)
**Tree:** `kavopdf/app` @ `462353f` (21 Nov 2026), `versionCode 316`, `versionName "3.53.26"`
**Built and measured:** 21 Nov 2026, this run. Nothing was committed; nothing was pushed. The patch was
applied to a *copy* of the clone (`/scratch/work/CS-patched`); `/scratch/work/CS` is left byte-identical
to `HEAD` (the one file `build-engine.sh` touches, `tools/p2w-bench/TRACE.md`, was reverted).

---

## Verdict

**No. The `w:pBdr` replacement does not fix the class in Google, and it does not merely "change the
LibreOffice score" — it makes the LibreOffice score worse on 8 of the 12 documents measured, and
catastrophically worse on the rule-dense ones.**

Measured on 12 documents of the class (172 source rules): the patch converts **68 of 172** rules from
`<w:drawing>` to `<w:pBdr>`; of those 68, **20 land within the instrument's own 24 pt tolerance and 48
do not**. `32_stroke_lines` goes from **0 lost rules in LibreOffice (12/12 pass)** to **52 lost rules in
LibreOffice (8 of 12 fail)**, and body text moves by a median of up to **−375 pt**, with
`bank-statement-horizontal-rules-only` writing its first line at **y = −9.1 pt, off the top of the page**.

The construct is *honoured* by Google — that part of the finding is right and is confirmed by the
project's own earlier Google measurement — but a paragraph border is placed **by flow**, and this engine
writes every shape **after** the page's paragraphs, so the border's `w:before` is measured from wherever
the flow had already ended, not from the text above the rule. Adding `ctx.flowY = s.topPt` (the line the
finding calls essential) does not repair that; it is in the patch I built, and the borders still land
wrong.

Second, independent reason the class cannot close this way: **only 40 % of the class's rules are
shape-carried hairlines at all.** 102 of the 172 source rules in the sample are *vertical* strokes — MICR
bands on `323_credit_card_statement` (31), `340_bill_of_lading` (29), `353_admit_card` (36), column rules
on `64_newspaper_uneven_columns_ad_boxes` and `315_gazette_notification`. `ruleAsBorder()` refuses
vertical rules by design (`|hPt| > |wPt| → return false`), so the patch is a **no-op on 2 of the 12
documents** (`323_credit_card_statement`, `64_newspaper_uneven_columns_ad_boxes`), converts exactly one
rule on two more (`340_bill_of_lading`, `353_admit_card`), and **cannot reach 104 of the 172 rules at
all**.

**Limit stated plainly: I cannot run Google Docs.** Everything below about Google is reasoning from
`tools/p2w-bench/google_safe.py`'s measured list plus the XML, plus one prior Google measurement already
recorded in the repo. The LibreOffice numbers are measured here, from my own renders.

---

## 1. Does the patch apply cleanly to current `HEAD`?

Almost. The insertion point is intact and every symbol the finding uses exists — but the snippet does not
compile as written.

**What the current code looks like at that point** (`DocxWriter.java:2772`, unchanged from what the
finding quotes):

```java
    private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
        int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
        long cx = Math.max(1, Math.round(s.wPt * EMU_PER_PT));
        long cy = Math.max(1, Math.round(s.hPt * EMU_PER_PT));
        long offX = Math.round(s.xPt * EMU_PER_PT);
        long offY = Math.round(s.topPt * EMU_PER_PT);
        int relHeight = 100000000 + (id & 0xFFFF);
        sb.append("<w:p><w:pPr><w:snapToGrid w:val=\"0\"/>")
          .append("<w:spacing w:beforeAutospacing=\"0\" w:afterAutospacing=\"0\" w:before=\"0\" w:after=\"0\" w:line=\"1\" w:lineRule=\"exact\"/>")
          ...
          .append("<w:r><w:drawing>")
          .append("<wp:anchor distT=\"0\" ... behindDoc=\"1\" ...>")
```

* `Ctx` still carries `flowY` (:787), `flowBoxPt` (:793), `newPage` (:795); `pageWidthPt` (:913),
  `isHairline` (:2845), `hex` (:2690), `LINE_BASE = 0.8f` (:214), `TWIPS_PER_PT = 20.0` (:52, a
  **double**) all exist.
* `grep -rn "pBdr" app/src/main/java` returns **nothing** — the engine has no paragraph-border path at
  all today. The only borders are table-side (`DocxWriter.java:6420`, `<w:tcBorders><w:bottom`,
  fed from `t.rowStroke`, not from a `Shape`).
* **Three `(int)` casts are required** and are not in the snippet: `TWIPS_PER_PT` is a `double` and
  `Math.max(0L, …)` returns `long`, so `int leftTw = Math.max(0L, …)`, `int rightTw = …` and
  `int szEighth = Math.max(2L, …)` are all compile errors. With those three casts the tree builds
  (`build-engine.sh`: 42 s, `engine built - ConvertAll ready`).

So: the change is mechanically appliable, and it builds — it is not a code problem. It is a
**measurement** problem, and the measurement says no.

### The exact change I built

```diff
     private static void shape(StringBuilder sb, Shape s, Ctx ctx) {
+        if (ruleAsBorder(sb, s, ctx)) return;
         int id = SHAPE_ID_BASE + (ctx.shapeSeq++);
```

plus the method itself, verbatim from `FINDINGS/RULES-PBDR-IMPLEMENTATION.md` (hairline test → reject
vertical → colour → `beforeTw` from `s.topPt − ctx.flowY − flowBoxPt·(1−LINE_BASE)` → `w:pBdr><w:bottom
w:val="single" w:sz w:space="0" w:color` + `w:ind` + `w:spacing w:before` + `w:line="1" exact` + a single
space run → `ctx.flowY = s.topPt; ctx.flowBoxPt = 0f; ctx.newPage = false;`), with the three `(int)`
casts added. Nothing else in the engine was touched (`git diff --stat`: +40 lines, one file).

---

## 2. Per-document measurement

Sample: 12 documents, all drawn from the class's own document list (the 145 names come from
`benchmarks/gverify/*.json`; the class table in `benchmarks/DEFECT-CLASSES-GOOGLE.md` carries counts
only), and including every document the finding names as a probe or a risk case
(`18_centred_heading_left_body_txtpos`, plus `bank-statement`, `gst-invoice`, `mobile-bill`,
`315_gazette_notification`, `62_two_col`, `64_newspaper`). Source rules are counted with the check's own
detector (`verify_google._doc_rules(isolated=True)`); "lost" is the check's own verdict
(`_rules_lost`, 1:1, 24 pt, 80 % overlap) against **my** LibreOffice render of the .docx.

| document | src rules (h/v) | → `w:pBdr` | of those, land ≤24 pt | 32 lost: base → patch | text lines moved >2 pt (median dy) | `<w:drawing>` base → patch |
|:--|:--|--:|--:|:--|:--|:--|
| `18_centred_heading_left_body_txtpos` *(probe)* | 2 (2/0) | 2 | 0 | **0 → 2** | 18 of 23 (−176.7 pt) | 2 → 0 |
| `23_timetable_grid_txtpos` | 2 (2/0) | 2 | 0 | **0 → 2** | 66 of 66 (−7.9 pt) | 11 → 9 |
| `315_gazette_notification` | 5 (2/3) | 2 | 0 | **0 → 2** | 0 | 5 → 3 |
| `323_credit_card_statement` | 31 (0/31) | 0 | – | 0 → 0 | 0 | 111 → 111 |
| `340_bill_of_lading` | 29 (0/29) | 1 | 0 | 0 → 0 | 0 | 56 → 55 |
| `353_admit_card` | 37 (1/36) | 1 | 0 | 0 → 1 | 0 | 70 → 69 |
| `394_map_with_legend` | 3 (3/0) | 2 | 2 (dy 0.0) | 0 → 1 | 14 of 15 (−113.0 pt) | 25 → 23 |
| `62_two_col_newsletter_pull_quote` | 2 (1/1) | 1 | 1 (dy 0.3) | 0 → 0 | 0 | 8 → 7 |
| `64_newspaper_uneven_columns_ad_boxes` | 4 (2/2) | 0 | – | 0 → 0 | 0 | 3 → 3 |
| `bank-statement-horizontal-rules-only` | 39 (39/0) | 39 | 9 | **0 → 32** | 196 of 196 (−375.0 pt) | 39 → 0 |
| `gst-invoice-horizontal-rules-only` | 16 (16/0) | 16 | 7 | **0 → 11** | 79 of 84 (−197.2 pt) | 21 → 5 |
| `mobile-bill` | 2 (2/0) | 2 | 1 (dy 3.5) | **0 → 1** | 112 of 112 (−11.0 pt) | 15 → 13 |
| **total** | **172 (70/102)** | **68** | **20** | **0 → 52** | 485 lines moved | 353 → 298 |

### Which construct carries each rule

* **Converted, and it lands (20 rules).** `394_map_with_legend` 2 of 3 at dy 0.0;
  `62_two_col_newsletter_pull_quote` 1 of 1 at dy 0.3; `bank-statement` 9 of 39 at dy −15.9…+21.1;
  `gst-invoice` 7 of 16; `mobile-bill` 1 of 2. These are the rules nearest the *end* of the flow, where
  the engine's `w:before` happens to be measured from a flow position that is already close to the rule.
* **Converted, and it does not land (48 rules).** Same construct, wrong y — see §3.
* **Never converted, still a floating drawing.** Almost none: thin anchored rules (`cy ≤ 4.5 pt`,
  `cx ≥ 10 pt`) go 2→0 on `18_centred`, 39→0 on `bank-statement`, 16→0 on `gst-invoice`, 2→0 on
  `mobile-bill`, 2→0 on `23_timetable`, 2→0 on `315_gazette`. The one exception is
  `394_map_with_legend`, which keeps 2 of its 4 thin anchors (one of them matches no isolated source
  rule, so it is a rule drawn in pieces or a band edge). On every document measured the swap of the
  class's rules is complete: **what fails is the placement, not the conversion.**
* **Not shape-carried at all (104 rules).** `323_credit_card_statement` 31 vertical MICR strokes,
  `340_bill_of_lading` 29, `353_admit_card` 36, `64_newspaper` 2 column rules, `315_gazette` 3 — plus
  `323`'s 111 anchors, none of which is thinner than 7 pt (its rules are vertical; the anchors are
  14 pt and 22 pt shaded bands). `ruleAsBorder` refuses these by design, and `32` fails on them for a
  different carrier's reason.

---

## 3. Why the borders land wrong even with `ctx.flowY = s.topPt`

The finding's diagnosis (a border is placed by flow, so the gap must be measured from `flowY`) is right
about the mechanism but wrong about the fix's reach, and one of its load-bearing claims is **false on
this tree**:

* It says the gap "is never computed" because a rule is appended after the page's paragraphs
  (`PdfToWord.java:7122`, `page.blocks.add(s)`) so `s.topPt > ctx.flowY` is always false.
  **Measured, that is not so:** the emitted `w:before` is **non-zero for 36 of 39** pBdr paragraphs on
  `bank-statement` (0…88 pt), **15 of 16** on `gst-invoice` (0…257.7 pt), 1 of 2 on the one- and
  two-rule documents. The gap *is* computed whenever a rule sits below the point the flow has already
  reached — which, because the shapes are written last, is only the lower part of the page.
* What the guard then does is the damage. For a rule *above* the flow's end (`s.topPt < flowY`) the gap
  is 0, and `w:before="0"` means "draw the border immediately after the previous paragraph" — i.e. at
  the bottom of the page. Measured on the probe `18_centred_heading_left_body_txtpos`, whose two rules
  are at **y 110.0 and 793.9**:

  | source rule | pBdr `w:before` | ink in the LO export | error |
  |:--|--:|--:|--:|
  | y 110.0 (page head) | 0 | y 167.8 (drawn twice, coincident) | **+57.8 pt** |
  | y 793.9 (footer) | 669.4 pt | y 837.4 (drawn twice, coincident) | **+43.5 pt** |

  The 669.4 pt is not the gap to the rule; it is the gap from the *first border's wrong position* to the
  second rule, so the error at the head is carried down. On `bank-statement` (39 rules, 72.4→~750) only
  6 distinct y values survive in the export — 72.1, 638.7, 657.5, 712.9, 750.1, 838.4, each drawn twice —
  because 30 rules above the flow's end all got `w:before="0"` and piled up.
* `ctx.flowY = s.topPt` cannot help: it makes the engine *believe* the reader is at the rule's y, but the
  reader is at the rule's y **plus the border the reader has just added**, and for the rules that get
  `w:before="0"` the belief was already wrong before the first border. The patch is not inert; it is
  self-consistently wrong.

This reproduces, in LibreOffice, exactly the failure the finding reports from Google on 19 Nov (both
rules at y 807/808 instead of 793/110).

---

## 4. What Google will and will not do with this — and what I can and cannot claim

Reasoning from `google_safe.py` and the XML, plus one prior measurement in the repo:

1. **`w:pBdr` is not on Google's measured ignore list.** `IGNORED` in `tools/p2w-bench/google_safe.py`
   names seven constructs — `w:framePr`, `w:drawing`, `wp:anchor`, `w:w`, letter `w:spacing`,
   `w:position`, `w:before`-at-page-top — and paragraph borders are not among them. The two constructs
   that carry the class today (`w:drawing`, `wp:anchor`) are.
2. **The construct itself is honoured by Google, measured before this run.**
   `FINDINGS/RULES-PBDR-FIX-MEASURED.md` records a minimal .docx with one bottom border rendering in both
   LibreOffice and Google, and — on the same probe document — **rules drawn 0 → 2 through Google** after
   the swap, with **1 of 2 still lost** because both borders landed at y 807/808 instead of 793/110. So
   Google *draws* a `w:pBdr` bottom border. That is the one Google fact available, and it is not mine; it
   is the project's own 19 Nov measurement.
3. **Therefore the expected Google outcome is "construct right, position wrong"** — the same failure I
   measured in LibreOffice. `32_stroke_lines` asks for the rule on the same page, same orientation,
   within 24 pt; a border at +57.8 pt fails it exactly as a missing drawing does. On the probe, the prior
   Google run reported 1 of 2 lost *with* the borders drawn; my LibreOffice measurement of the same patch
   shows 2 of 2 outside 24 pt.
4. **What I cannot claim:** I have not seen Google render these 12 documents, so I cannot say how many of
   the 68 converted rules Google would place correctly. On the evidence available, the *construct* is no
   longer the class's cause and the *placement* is — which is the opposite of "the fix works", and is
   also not the same as "only the LO score changes": LO gets worse, measurably, which is what a Google
   run would then have to be compared against.

---

## 5. Blast radius

**In the emitted .docx (12 documents, measured):**

| | base | patched |
|:--|--:|--:|
| `<w:drawing>` instances / documents carrying one | 353 / 12 | 298 / 10 |
| `wp:anchor` instances | 353 | 298 |
| `<w:pBdr>` paragraphs | 0 | 68 |
| `<w:p>` paragraphs | unchanged (e.g. 24→24, 96→96) | unchanged |
| `w:before`-bearing spacing (google_safe `w:before-page-top`) | 968 | **968** |

* The pBdr paragraph **replaces** the drawing paragraph one-for-one — `shape()` already emitted a
  `<w:p>` to hold the anchor — so paragraph counts do not move and `w:before-page-top` counts do not
  rise. That is good news for the gate and bad news for correctness: **the carrier is the same
  paragraph, and its `w:before` is what carries the error.**
* **The gate cannot see this construct.** `google_safe.py --check` would find `w:drawing`/`wp:anchor`
  carriers falling (12 → 10 documents) and nothing raised, so it would **pass a commit that loses 52
  rules in LibreOffice**. `w:pBdr` has no entry in `IGNORED`; adding one would be recording a construct
  Google *does* honour, which is not the same thing. The gate's blind spot is real and is worth a line in
  `BLOCKERS.md` regardless of what happens to this patch.
* **Reach:** 68 of 172 rules (40 %). Even with perfect placement, 102 rules in this sample are vertical
  strokes or non-shape carriers the patch never touches — so `32_stroke_lines` cannot close on this
  construct alone.

**In the render (LibreOffice, my own exports, base vs patched):**

| check | base | patched |
|:--|:--|:--|
| `32_stroke_lines` | 0 lost on 12/12 | **52 lost, 8 of 12 fail** |
| `18_displacement` (text lines moved >2 pt) | — | **485 lines**, median dy up to **−375 pt**; `bank-statement` first line at **y −9.1 pt** (off-page) |
| `00_page_count` | 1 page each | 1 page each (no change in this sample) |

`bank-statement-horizontal-rules-only` in the patched build is a blank page with a band of overlapping
text at the top and a handful of rules near the foot — the visual confirms the numbers, not the other way
round.

---

## 6. What this means for the class, and the single next action

The pBdr paragraph is the right *model* (COORDINATION.md's "rules as paragraph borders") and the wrong
*construct as implemented here*, for a reason no value of `w:before` can fix: the border's y is derived
from the flow, and this engine writes shapes after the flow has ended. The finding's own escape hatch is
the one to take — a construct that draws the rule **without adding a paragraph to the flow**:

**Next action:** stop re-deriving this. Record the pBdr-carrier construct as measured-and-closed (this
file, plus the four findings already in `FINDINGS/`), and spend the next `32_stroke_lines` slot on the
**table-row border**: `DocxWriter.java:6420` already writes `<w:tcBorders><w:bottom>` from `t.rowStroke`
and Google honours it, it adds no paragraph, and 102 of the 172 rules measured here are the vertical /
grid kind that a cell border can carry and a paragraph bottom border cannot. Measure that on
`bank-statement-horizontal-rules-only` + `18_centred_heading_left_body_txtpos` first.

---

## Method / provenance

* Clone `git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS` @ `462353f`; a second copy
  `/scratch/work/CS-patched` holds the only modified file (`DocxWriter.java`, +40 lines).
* Corpus: release `corpus-v1` of `kavopdf/app`, the four assets `benchmarks/p2w.py` names
  (`p2w-all-groups`, `p2w-batch-1`, `pdf-to-word-test-corpus-v3`, `p2w-round2-additions`) — 211 PDFs.
  All 145 documents in the class's list are present in it.
* Engines built with `bash tools/p2w-bench/build-engine.sh` (42 s and 44 s); one document per JVM via
  `ConvertOne` from `tools/engine-verify`, JDK at `/scratch/work/.p2w-jdk/jdk`.
* Source rules: `verify_google._doc_rules(isolated=True)` on the source PDF. Rendered rules: the same
  detector with the render-side widths (`RULE_THIN_REN`, `RULE_BAND_REN`, `isolated=False`). Verdict:
  `verify_google._rules_lost` — the check's own 1:1, 24 pt, 80 %-overlap matcher — against a LibreOffice
  export of each .docx (`soffice --headless --convert-to pdf`).
* `google_safe.scan()` run on every .docx for the gate counts. **Google Docs itself was not run.**
* Numbers that differ from the finding's, and why: the finding quotes "84 documents with both renders,
  LO 0, Google 53" while `benchmarks/DEFECT-CLASSES-GOOGLE.md` (regenerated 21 Nov 14:25 IST) says
  **192 with both renders, LO 1, Google 145**. The table is the newer instrument and is the one used
  here. The finding also counts a rule as a *hairline drawing object* (looser: `min(w,h) ≤ 1.5`), which
  reads `mobile-bill` as 32 rules where check 32's isolated-segment detector reads 2; both counts are
  given where they differ, and the check's own detector is used for the verdict.
