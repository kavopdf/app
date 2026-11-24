# The 120 pt gap cap and anchored body text — analysis and patch

**Target:** `kavopdf/app` @ HEAD `4bf70e5` ("claim: baseline takes the slot"), shallow clone,
`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (7,671 lines at HEAD).
**Deliverables:** `gapcap-patch.diff` (unified diff, applies with `git apply` / `patch -p1`),
this file. Nothing was committed, pushed, or measured on a corpus.

All line numbers below are **HEAD line numbers, before the patch**. The patched file shifts the
`para()` / `flowRow()` / `flowFromBox()` region down by ~104 lines.

---

## 1. What the code actually says

### 1.1 The mechanism — confirmed, with three corrections

| brief's claim | what the code does | verdict |
|---|---|---|
| `DocxWriter.para()` ~3101 routes every line into `anchorBox()` once `ctx.positioned` | `para()` is at **3101**; its positioned branch is **3126–3133**: `if (ctx.positioned && !anyRotated) { for (Box b : p.boxes) { cenAnchorPos++; anchorBox(...); } return; }`. A second site at **3144** (`if (ctx.positioned \|\| containerOf(...) != null)`) catches the same mode for the non-row, non-rotated path. | **confirmed** |
| `anchorBox()` ~5580, `txbxContent` ~5664 | `anchorBox()` is at **2793**. **5580** is `anchorShape(...)` (the rotated-shape writer, second overload); `<wps:txbx><w:txbxContent>` is emitted at **5664** inside it. Both write DrawingML; `anchorBox` is the one body text takes. | **line number corrected** (2793, not 5580) |
| `ctx.positioned` is set by gap guards in `flowFromBox()` (~4381, 4453, 4487, 4587) and `flowRow()` (~3571, 3594, 3663) | Six assignment sites, not seven. `flowFromBox()` starts at **4381** — that is the method signature, not a guard. Assignments: `flowFromBox` **4453** (`afterTablePt` branch), **4487** (`pitch` branch), **4587** (the `ZERO_GAP_ANCHOR`/`PAGE_POSITION_ON_ANCHOR` cascade); `flowRow` **3571** (`afterTablePt`), **3594** (`pitch`), **3663** (zero-gap cascade). | **confirmed**, 4381 is the signature |
| the guards fire when a gap exceeds `gapCapTw()` = 2400 tw (120 pt) unless `ctx.spendGaps` | `GAP_CAP_TW = 2400` at **261**; `gapCapTw(ctx)` at **399–401** returns `ctx.spendGaps ? GAP_CAP_SPEND_TW : GAP_CAP_TW` with `GAP_CAP_SPEND_TW = 20000` (**283**, i.e. 1000 pt); `ctx.spendGaps = pageFits(page, ph)` is set once per page at **1144**. | **confirmed** |

Two facts that matter for the fix and are not in the brief:

* **`ctx.positioned` is read in exactly three places, all inside `para()` (3116, 3126, 3144).**
  Nothing else in the writer consults it. So the blast radius of the latch is exactly "every
  paragraph written after the guard fires, on that page" — `pinnedBoxes()` is skipped (3116),
  and both remaining branches call `anchorBox()` per box. There is no partial mode.
* **`positioned` is reset per page (1130) and per writing pass (1246, 2211, 2288).** The latch is
  page-local, so the damage is bounded by one page — but on that page it is total, from the gap
  onwards.

### 1.2 What the 120 pt cap protects against

The comment at **236–261** states it and gives the failed experiment:

* a gap is a **measurement** (a diagram's boxes stand 90 pt apart; clamping to 72 pt walks every
  label up — measured 141.6 pt and 227.1 pt on `393_spectrum_peak_table` / `394_map_with_legend`);
* the cap is **not a layout rule**: it exists because (a) a malformed PDF can report `y = 100000 pt`,
  and (b) **a gap wider than the flow can afford pushes everything below it down the sheet** —
  `373_leave_application_form`'s footer sits 422 pt below the signature row, and leaving that gap
  open "pushed the footer onto a second page, whose tables the model under-measures by the same
  amount".

**History (`git log -S` is unavailable: the clone is `--depth 1`, one commit. The history below is
in the source comments, which are unusually explicit):**

* **7 Nov — tried and reverted: raise `GAP_CAP_TW` itself to 24000 tw (600 pt).** It fixed the class
  it aimed at (300's footer 270.1 → 8.2 pt, 302's signature block 232.0 → 14.0, 311's "Copy
  forwarded to" 162.1 → 27.0, 314's footer 189.7 → 27.0) and G2 passed across 208 documents. It was
  rejected because **`315_gazette_notification` went from one sheet to two**: its three columns are
  still stacked into one flow (D-08), so its content is three columns long and only fitted a sheet
  while the gaps were being clamped. "The ratchet says a document that gets worse rejects the
  change." (comment at 258–283)
* **The follow-up that shipped instead:** `GAP_CAP_SPEND_TW = 20000` (1000 pt), granted only when
  `pageFits(page, ph)` says the page's own content fits the sheet — the measure that separates 315
  (does not fit) from 344 (does). Plus `firstGapCapTw()` = the page height for the first line of a
  sheet (**3973**), which is the same "the page height is the only bound" argument.
* **24 Nov — the census** (`tools/p2w-bench/FINDINGS/ANCHORED-BOX-CENSUS-CAP-IS-16PCT-24NOV.md`)
  measured the whole corpus with an instrumented build (byte-identical XML on 213/213):

  | first site to fire | pages | gap (pt) | `spendGaps` |
  |---|---:|---|---|
  | `flowFromBox/afterTable` | 1 | 123.1 | false |
  | `flowFromBox/pitch` | 7 | 164.6–432.3 | false |
  | `flowRow/afterTable` | 8 | 129.5–552.7 | false |
  | `flowRow/pitch` | 7 | 128.0–309.3 | false |
  | `flowFromBox/zeroGapAnchor` | 11 | 13.6–72.6 (a *miss*) | 9 false, 2 true |
  | `flowRow/zeroGapAnchor` | 1 | 24.4 | true |
  | **total** | **35** (33 docs, 6.2 % of 563 pages) | | |

  and it refuted "just spend everything": forcing `ctx.spendGaps = true` everywhere removes only
  **3,770 of the 23,794** non-space characters inside boxes (−15.9 %) and **displaces** whole pages
  (`330_cad_drawing_sheet` median 3.14 → 16.77 pt, `table-inside-two-column-page` worst 9.17 →
  92.01, `newsletter-3col-header-footer` 6.26 → 28.36). Mechanism: on 28 of the 35 pages the gap is
  white space the page **cannot afford** (+0.4 % to +35.5 % over the paper by the engine's own
  arithmetic); written as `w:before` it enters the flow, the page exceeds its budget, and the
  squeeze shaves the whole page up.

### 1.3 Two corrections to the brief's framing (important for what this patch can claim)

1. **The cap is not the dominant carrier of boxed body text.** By the repo's own census the cap
   accounts for **23 of 35** positioned pages but only **3,770 of 23,794** box characters
   (15.9 %). The `ZERO_GAP_ANCHOR` → `PAGE_POSITION_ON_ANCHOR` cascade (a line whose y is *above*
   the flow, miss ≥ 6 pt) accounts for the other 20,024 — `041122-Account_Opening_Form` (5,553),
   `policy-2col-spanning-section-heading` (2,591), `academic-paper-ieee-2col-abstract` (2,505).
2. **`-Dp2w.pagepos=0` alone does not fix it either** (measured: −4,037 characters, document count
   unchanged at 61/61), because the flow re-syncs and the next line reaches its own negative gap and
   anchors on its own. The census's own conclusion is the one this patch implements:

   > "What the corpus needs is a per-line rule: a line the flow cannot reach must be *written into
   > the flow at the position the page drew* — which is `w:before` … not an anchored box."

   So: **this patch addresses the cap half of the population only.** It will not empty a single
   document on its own, and it will not close all 54. See §5.

---

## 2. Design: which of (a) / (b) / (c), and why

**(a) Raise `gapCapTw` substantially — rejected, measured.** Exactly the 7 Nov experiment
(24000 tw) that was reverted: `315_gazette_notification` 1 → 2 sheets, because a page whose content
is three stacked columns is only held to one sheet by the clamping. The census reproduced the same
failure at 600 pt of spending on 3 more documents. The cap is doing real work; it is the *response*
to the cap (anchor + latch) that is wrong.

**(c) Never anchor `anchorPos` body text, keep anchoring only stamps/shapes — rejected, measured.**
Two independent measurements:
* the latch exists for a reason — `PAGE_POSITION_ON_ANCHOR`'s comment (311–330) records that leaving
  the flow live after an anchored line puts **two positioners on one page**: on
  `policy-2col-spanning-section-heading`, 51 flowed lines + 27 anchored boxes, 21 overlaps,
  median |dy| 105.7 pt;
* `-Dp2w.pagepos=0` over the whole corpus is worth 4,037 characters and **0 documents** (61 → 61
  carrying boxes), because the next line anchors itself.

So "don't latch" is refuted and "don't anchor" is refuted. What is left is not anchoring the line
in the first place.

**(b) Spend the gap as `w:before` instead of anchoring, gated — chosen.** `w:before` is the
construct that states the position without a text box, and the repo already relies on Google
honouring it 1:1 (`18_displacement` findings). The census shows ungated spending is wrong; the
gate is therefore the whole of the design. Three conditions, in the order that rejects the most:

1. **Nothing below it to push.** Only a line in the foot of the sheet (`FOOT_BAND = 0.90` of the
   page height) is safe: the page has already decided where that line goes and no flow runs under
   it. A gap in the body is white space the content must fit around — spending one there is the
   measured `330_cad` / `table-inside-two-column-page` / `newsletter-3col` displacement.
2. **The line lands on the paper** (`lineTop + line ≤ pageHeight`). A gap that puts the line past
   the sheet is a position the paper cannot hold; there the box is the construct that does *not*
   advance the flow past the paper.
3. **The page's budget carries the gap** (`flowTw + gap + line ≤ budgetTw`). This is precisely the
   condition under which `fitPage`'s step 1 does **not** give the gap up. Where the budget cannot
   carry it, spending would be clamped out of `w:before` anyway and the line would land above its
   own baseline — the 130.6 pt footer miss on `27_two_column_left_short_txtpos` that the clamp was
   originally rejected for.

Condition 3 is the piece the repo's own draft (`running-foot-spends-the-gap-1855-fixer.patch`,
`FOOT_BAND` only, uncommitted, in FINDINGS) does not have; it is what stops the patch from turning
a clamped-anchor page into a clamped-spend page.

**Also deliberately not done — the two `afterTablePt` sites (4453 / 3571).** They are the largest
single group (9 of 23 cap pages) and the most tempting, but there the gap is measured from the
**model's** table edge (`ctx.afterTablePt`), and a table's rendered height is the renderer's, not
the model's (that is why the branch exists — see `Ctx.afterTablePt`'s comment and the
`12_stamp_across_page_break` / `mutual-fund-statement` measurement in `fitPage`). Spending that gap
writes `w:before = lineTop − modelTableBottom`, so the renderer lands the line at
`renderTableBottom + (lineTop − modelTableBottom)` — i.e. it re-injects the model's table-height
error into the footer's position. In the `pitch` branches the gap is measured from the **line
above**, whose position the renderer honours exactly, so nothing accumulates. That asymmetry is the
blast-radius argument for scoping the patch to the two pitch sites; the afterTable sites are a
follow-up that needs the table height fixed first.

### What the patch does at each site

* `flowFromBox()` pitch branch (4487): when the gap is over the cap **and** `spendWideGap(...)` is
  true, fall through to `beforeTw = round(extra × 20)` — a flowed paragraph with `w:before`, no
  `positioned`, no box.
* `flowRow()` pitch branch (3594): identical, for a row (footer = label + folio on one baseline).

Everything else — `afterTable`, the zero-gap cascade, `containerOf`, `pinnedBoxes`, stamps,
`anchorShape` — is untouched.

**Why this is minimal:** the patch adds one predicate and two call sites; the code path it opens is
the one that already exists for every other gap (the `beforeTw` write at the end of the same `if`).
There is no new XML, no new state on `Ctx`, no new pass, and `-Dp2w.spendfoot=0` restores HEAD's
behaviour byte for byte for A/B measurement.

---

## 3. The patch

Files changed: **one** — `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`
(+102 / −2). No other engine file needs to change; no import changes.

| where | what |
|---|---|
| constants, before `gapCapTw()` (HEAD 398) | `SPEND_FOOT_GAP` (kill switch, `-Dp2w.spendfoot=0`) and `FOOT_BAND = 0.90f`, with the justification and the measured band |
| after `gapCapTw()` (HEAD 401) | `private static boolean spendWideGap(Ctx ctx, float gapPt, float lineTopPt, float linePt)` — the three conditions, documented against the measurements that set each one |
| `flowFromBox()`, pitch branch (HEAD 4487) | guard becomes `!ctx.inColumn && extra*TP > gapCapTw(ctx) && !spendWideGap(ctx, extra, b.y - LINE_BASE*linePt, linePt)` |
| `flowRow()`, pitch branch (HEAD 3594) | same, with `first.y - LINE_BASE*linePt` for the row's top |

Both call sites use values already in scope (`extra`, `linePt`, `first.y` / `b.y`); no signature
changes, no new fields, no behaviour change anywhere `spendWideGap` returns false.

### Verification performed

* `javalang` parse of the whole file: **OK**.
* **Real compile**: Temurin `javac 17.0.21.1`, `-sourcepath app/src/main/java`, classpath =
  `pdfbox-android-2.0.27.0` `classes.jar` (the only library the engine needs; the Android SDK is
  absent here). Patched file: **6 diagnostics, none in `DocxWriter.java`** — all six are
  `package android.graphics does not exist` in `PdfToWord.java` (lines 5723, 6267, 6344, 6531,
  6532, 6535). Unpatched HEAD, same command: **the same 6 diagnostics, on the same lines**. The
  patch introduces no new diagnostic and `DocxWriter.java` attributes cleanly, including the new
  helper's `double`/`float`/`int` arithmetic against `TWIPS_PER_PT` (`private static final double`).
* Not run (as instructed): corpus conversion, `soffice`, Google Docs, gradle/Android build
  (no SDK), `regress.py`.

---

## 4. Top three risks

**R1 — a spent foot gap inherits the model's own height error, and can add a page.**
Hurt: **`373_leave_application_form`** (footer 422 pt below the signature row, "whose tables the
model under-measures by the same amount"), plus the same class in `12_stamp_across_page_break` and
`mutual-fund-statement` (both measured in `fitPage`'s comment as pages whose table heights the model
gets wrong by 139.6 pt and 263.7 pt). Condition 3 checks the model's ledger, and if the model
under-measures what is above the footer, the *renderer* is further down than the ledger believes —
the footer lands low and can reach a second sheet. This is the ratchet's hardest failure
(page-count regression), and it is exactly the failure the cap's comment records. Mitigation in the
patch is partial by construction: the check cannot see renderer error it does not model.

**R2 — a page that needs squeezing gets squeezed, and every line on it moves.**
Hurt: **`330_cad_drawing_sheet`** (median displacement 3.14 → 16.77 pt under spend-always),
**`table-inside-two-column-page`** (worst 9.17 → 92.01), **`newsletter-3col-header-footer`**
(6.26 → 28.36). If the foot-band spend is enough to push the measuring pass's `writtenTw` past
`pageBudgetTw` (e.g. via the un-charged carrier twips, or an earlier line the ledger
under-charged), the whole page is written at `squeeze < 1` and every gap and box on it shrinks —
a page-wide displacement that the anchored version did not have. Conditions 2 and 3 make this
unlikely (the line is on the paper and the ledger is within budget through it) but do not make it
impossible.

**R3 — on a multi-column page, a "row in the bottom band" is a column's last line, not a footer,
and spending its gap hands the next line to the zero-gap rule.**
Hurt: **`55_sidebar_box_beside_body`**, **`61_two_col_abstract_spanning`**,
**`27_two_column_left_short_txtpos`** (page 1), **`policy-2col-spanning-section-heading`**. The flow
is stacked (D-08), so after the left column's last row the next block is the *right column's first
line*, which sits **above** the flow. Spending instead of anchoring does not remove the problem, it
relocates it: the next line reaches a negative gap, `ZERO_GAP_ANCHOR` fires, `PAGE_POSITION_ON_ANCHOR`
latches, and the page is anchored anyway — now with the overlap risk that rule's own comment
measures (21 overlaps, median |dy| 105.7 pt, when the room above is not there). `FOOT_BAND` is a
page-geometry proxy for "nothing below", and on a columned page it is a proxy, not a fact.

---

## 5. What this patch does *not* do (stated so the corpus run is read honestly)

* It does not stop `ZERO_GAP_ANCHOR` (11 + 1 pages, **20,024 of 23,794** box characters) — a
  different guard with a different fix, per the census.
* It does not touch the two `afterTablePt` sites (9 pages) — reason in §2.
* It will not make any single document "clean" on its own. The expected effect is a reduction in
  `w:txbxContent` on the pitch-branch pages whose wide gap is in the foot band; the class this was
  measured on is `27_two_column_left_short_txtpos` (40/42 → 42/42, `w:txbxContent` 4 → 0, one page
  either way — measured in Google Docs through Drive upload → convert → export, recorded in
  `RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md`), and the same construct is expected on
  `46_chart_coloured_labels_body_text`, `55_sidebar_box_beside_body`,
  `61_two_col_abstract_spanning`.
* The claim "Google Docs rasterises anchored text boxes on import" is the repo's recorded
  measurement on one document, not something re-verified here; nor was the "54 of 65 documents"
  figure (`04_chars_missing-TXBX-CLAIM-REFUTED-54of65-0120-agentB.md`) recomputed.

## 6. Reviewer checklist

1. `-Dp2w.spendfoot=0` must reproduce HEAD's `word/document.xml` byte for byte on the corpus
   (the predicate returns false first, before any other arithmetic — this is the whole A/B).
2. On the pages where the guard fires, `w:txbxContent` should fall and the page count must not
   change; `27_two_column_left_short_txtpos`, `46_chart_coloured_labels_body_text` are the first
   checks.
3. `18_displacement` and `26_text_overlap` are the checks to watch for R2/R3; `00_page_count` for R1.
4. `ctx.flowTw`/`ctx.budgetTw` are the same ledger in the measuring pass and the real pass
   (`fitPage` reads them in both), so the gate is consistent across the two passes — a spent gap is
   measured and written the same way, and cannot make the measure disagree with the page.
