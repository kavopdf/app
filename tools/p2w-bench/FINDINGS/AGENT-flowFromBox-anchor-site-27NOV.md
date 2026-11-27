# `flowFromBox` IS a second anchor site — but the foot-band guard was never at the first site either, and it is worth one document

**Recorded:** 2026-11-27, engine HEAD `89b0d9c9a41f90b51a5d8df314de423e4fdb5c7a` ("gverify: 60 more
documents measured through Google"), 214 PDFs, 573 pages. Nothing committed; `git status` clean.

**Question asked:** is `flowFromBox` a second anchor site for the same anchored-text-box defect as
`PAGE_POSITION_ON_ANCHOR`, and does the foot-band guard used at the first site transfer to it?

**Answer in one line:** yes it is a second site and one of its three emit points is unguarded, but the
guard is *not* at the `PAGE_POSITION_ON_ANCHOR` site to be transferred from, and applied to
`flowFromBox` it changes exactly **1 of 214 documents, 1 box, 26 characters**.

---

## 1. The engine is C#/Java — it is Java (Android app, pure-JVM engine)

`app/src/main/java/com/kavopdf/app/engine/` — 12 `.java` files, zero `.cs`. The whole defect lives in
`DocxWriter.java` (7,849 lines). Build and corpus fetch are the repo's own
(`tools/p2w-bench/build-engine.sh`, `corpus-fetch.sh`, `corpus-convert.py`); all three work on a bare pod.

## 2. `flowFromBox` — where it is, who calls it, when it anchors

**Declaration:** `DocxWriter.java:4444`

```
    private static void flowFromBox(StringBuilder sb, PdfToWord.Para p, PdfToWord.Box b, Ctx ctx) {
```

**Callers — two, and they are the same path twice:**

- `DocxWriter.java:3210` — `para()`, the ordinary single-column paragraph writer, for every box of a
  paragraph when the page is *not* in positioned mode and the box belongs to no outline.
- `DocxWriter.java:3605` — `flowRow()`, which hands a one-field "row" straight back to it:
  `if (cols.size() == 1) { flowFromBox(sb, p, cols.get(0), ctx); return; }`

So `flowFromBox` is the writer for *every ordinary body line*, which is why the question is worth
asking: it is the highest-traffic path in the engine, not a corner.

**It emits an anchored drawing at three points, all through the same `anchorBox()` (line 2855), which
writes `<wp:anchor … behindDoc="1">` + `<wps:txbx>` — the exact construct Google Docs rasterises
(the writer's own note at line 413 says so).**

| # | line (condition) | branch | `inFootBand` guard? |
|:--|:--|:--|:--|
| A | `4512` — `if (!ctx.inColumn && edgeGap * TWIPS_PER_PT > gapCapTw(ctx) && !inFootBand(ctx, b.y))` | gap below a layout table / column-cell edge (`afterTablePt`), emits at `4517` | **yes** |
| B | `4549` — `if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx) && !inFootBand(ctx, b.y))` | gap wider than the page's pitch, emits at `4551` | **yes** |
| C | `4627` — `if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage)` | the ZERO-GAP rule: the flow has overrun the line's own y by ≥ `ZERO_GAP_FLOOR_PT` (6.0 pt) and the box fits above the previous one (`4642`), emits at `4645`, then sets `ctx.positioned = true` at `4650` | **NO** |

`gapCapTw()` is `DocxWriter.java:405` → `GAP_CAP_TW = 2400` twips = **120 pt** (`:267`), or
`GAP_CAP_SPEND_TW = 20000` when `ctx.spendGaps`. That is the 120 pt threshold the brief names.

`ZERO_GAP_ANCHOR` (`:309`, on unless `-Dp2w.zganchor=false`) landed in `22728b11` (13 Nov), **before**
the foot-band patch; `PAGE_POSITION_ON_ANCHOR` (`:337`, on unless `-Dp2w.pagepos=0`) landed in
`bf2355c9` (15 Nov).

## 3. The foot-band guard — where it actually is

**Helper:** `DocxWriter.java:426–431`

```
    private static boolean inFootBand(Ctx ctx, float y) {
        return y > FOOT_BAND_FRACTION * ctx.pageHeightPt;
    }
    private static final float FOOT_BAND_FRACTION = 0.90f;
```

**It has exactly four call sites** (`git log -S inFootBand` → one commit, `85b8735f`, 25 Nov, "foot-band
four-site patch"):

```
3629:  if (edgeGap * TWIPS_PER_PT > gapCapTw(ctx) && !inFootBand(ctx, first.y)) {      // flowRow, table edge
3656:  if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx) && !inFootBand(ctx, first.y)) {  // flowRow, pitch
4512:  if (!ctx.inColumn && edgeGap * TWIPS_PER_PT > gapCapTw(ctx) && !inFootBand(ctx, b.y)) {    // flowFromBox, table edge
4549:  if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx) && !inFootBand(ctx, b.y)) {      // flowFromBox, pitch
```

**The premise in the question is false at HEAD: there is no foot-band guard at the
`PAGE_POSITION_ON_ANCHOR` site.** `PAGE_POSITION_ON_ANCHOR` is a flag that sets `ctx.positioned = true`
(`:3726`, `:4650`); the boxes it is credited with are written by the *propagation* branch at
`DocxWriter.java:3188–3195`:

```
        if (ctx.positioned && !anyRotated) {
            for (PdfToWord.Box b : p.boxes) {
                if (b.runs.isEmpty()) continue;
                ctx.cenAnchorPos++;
                anchorBox(sb, p, b, ctx);
            }
            return;
        }
```

— no `inFootBand` anywhere in it, and none in `anchorBox()` either. What `85b8735f` guarded is the four
*gap* sites, i.e. the places that **enter** positioned mode for a reason (a gap wider than the cap).
Once a page is in positioned mode, every remaining paragraph on it is anchored unconditionally,
foot band or not. So the guard is an *entry* guard, not an *emit* guard; the emit site is unguarded for
all 975 `anchorPos` boxes.

## 4. Verdict — does the guard transfer to `flowFromBox`?

**Mechanically, yes: it compiles, it runs, and I measured it (below). As a claim about the defect, no —
and there is nothing at the `PAGE_POSITION_ON_ANCHOR` site to transfer from.**

Three separate findings, each with the code or the measurement behind it:

**(a) It is not a "transfer".** The four guard sites and the two zero-gap sites are different branches of
the same class of construct. The guard exists at A and B; it does not exist at C, and it does not exist
at the site the question names. `85b8735f` patched the four *gap* sites and left both *zero-gap* sites
(`flowRow` `:3708`, `flowFromBox` `:4627`) alone — the two `if` conditions are character-for-character
identical:

```
3708:        if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {
4627:        if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {
```

So the earlier finding `44_header_footer-FLOWFROMBOX-ALREADY-GUARDED-AND-INERT-1815-relay.md` was right
about A and B and wrong about the site as a whole: it checked the two gap sites and concluded "the
second site does not exist". C was already in the tree (13 Nov) and was never counted.

**(b) The predicate is the wrong predicate at C, not merely missing.** `inFootBand` says "this line is
page furniture because it is in the bottom tenth". Branch C fires when the flow has *overrun* — the line
landed ≥6 pt BELOW its own y (`err = landY - b.y`, `:4630`). A line in the bottom tenth is normally
*above* the flow (a footer 300 pt below the body), so C does not fire for it; C fires when the body has
been squeezed past the foot, and there the anchor is what holds the line at its own y instead of
letting it drift to the sheet edge. Suppressing it there hands the y back to the flow — the failure the
rule was written to fix (`69_two_col_legal_numbered_clauses`, 16.9 pt and 41.1 pt, quoted at `:4625`).
The two mechanisms coincide only when the overrunning line happens to *be* the foot block, which is
what `353_admit_card` is and what 13 of the other 14 are not.

**(c) It is worth one document.** See §5. The 25 boxes `flowFromBox` writes are 2.4 % of the corpus's
anchors; exactly one of them is in the foot band.

## 5. Measurement — how many anchor boxes come from `flowFromBox`

Instrumented `DocxWriter` (temporary counters, reverted), built with the repo's `build-engine.sh`, and
converted the **whole 214-PDF corpus** with `-Dp2w.census=<file>`, 4 shards of `ConvertAll`, one JVM per
shard, every shard exit 0, 573 pages. Counters aggregated per `(document, page)` keeping the last pass
(a squeezed page is emitted twice and would otherwise double-count).

```
anchor boxes written (anchorBox + pinnedBoxes)      1,042
  anchorPos  - positioned propagation (:3191)         975   93.6 %
  anchorRule - ZERO-GAP rule, flowRow (:3721)           5    0.5 %
  anchorRule - ZERO-GAP rule, flowFromBox (:4644)      14    1.3 %
  flowFromBox edge-gap (:4517)                          1    0.1 %
  flowFromBox pitch-gap (:4551)                        10    1.0 %
  other sites (pinnedBoxes, containerOf, flowRow gaps) 37    3.6 %
```

**`flowFromBox` total: 25 of 1,042 anchor boxes (2.4 %), on 18 of 214 documents.** Of its 14 zero-gap
boxes, **1** has `b.y > 0.90 × pageHeight` — `353_admit_card`, page 1.

**Ablation.** Added the guard at C only, rebuilt, re-converted those 18 documents, diffed
`word/document.xml` (never the `.docx` bytes):

```
17 of 18 documents: document.xml BYTE-IDENTICAL
 353_admit_card   : txbx 1 -> 0,  boxed chars 26 -> 0,  total text 909 -> 909,  paragraphs 39 -> 38
```

The box it removes is `Controller of Examinations`, `wp:positionV relativeFrom="page"`, posOffset
9,721,212 EMU = **765.4 pt** on an A4 page whose foot band starts at 757.7 pt, `behindDoc="1"` — the
exact construct Google rasterises, holding a signature block, not a running foot. The text survives:
same 909 characters, one paragraph fewer.

**Documents affected: 1 of 214** (0.5 %). Nothing else in the corpus moves.

*Honesty note on the run:* a first pass driven through `corpus-convert.py` reported 675 pages / 1,063
anchors because the tool's 280 s per-shard timeout killed shards mid-write and the resumed shard
re-emitted their pages. The numbers above come from a clean single pass with no timeout. If anyone
re-runs this, dedupe on `(doc, page)` keeping the highest `pass=` field.

## 6. The proposed guard, as a unified diff

Minimal, at branch C only. **Not applied** — reverted; `git status` clean.

```diff
--- a/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
+++ b/app/src/main/java/com/kavopdf/app/engine/DocxWriter.java
@@ -4624,7 +4624,8 @@ public final class DocxWriter {
         // here, AFTER the fit clamp, because that clamp is the other thing that can stop a
         // line reaching its own y - on 69_two_col_legal_numbered_clauses one line landed
         // 16.9 pt low and dragged four more with it, and again at 41.1 pt.
-        if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage) {
+        if (ZERO_GAP_ANCHOR && !ctx.inColumn && !ctx.newPage
+                && !inFootBand(ctx, b.y)) {
             float topNow = flowTopPt(ctx) + beforeTw / (float) TWIPS_PER_PT;
             float landY = topNow + LINE_BASE * (lineTw / (float) TWIPS_PER_PT);
             float err = landY - b.y;
```

**Recommendation: do not land it.** 1 document, 1 box, 26 characters, for a predicate that is wrong at
that branch by construction (§4b) and that would suppress the anchor in exactly the case the anchor
exists for. If the class is worth chasing, the honest target is the *emit* site (§3, `:3188`), which
carries 975 of the 1,042 boxes and has no guard at all — but that is a different finding and this run
did not measure what a guard there would cost.

## 7. What would prove this wrong

- **A document whose `document.xml` differs between "C guarded" and "C unguarded" other than
  `353_admit_card`.** I measured 18 of 18 candidates and found one; a 19th would move the count. The 18
  are the complete set of documents the census says write any `flowFromBox` box, so this is a
  corpus-wide claim for this corpus, not a sample.
- **A counter that shows `anchorRuleBox` > 0 on a document my census pass did not see**, e.g. because a
  page was emitted in a squeeze pass and I deduped it away. The dedupe keeps the last pass; if the
  engine's own census counts both passes as anchors, the true per-box total is the 27 from the
  undeduped pass, not 25 — the foot-band count is 1 either way.
- **Evidence that Google rasterises only *some* anchored boxes** (e.g. that a 26-character box survives
  import). Then the whole class is smaller than the brief says, and `353_admit_card` is not affected at
  all. No Google render was taken this run; every number above is `word/document.xml` and the
  converter's own counters.
- **A document where branch C fires on a genuine running foot AND the flow has not overrun** — that
  would show the predicate is right at C more often than the one case I found, and §4b would be wrong.
- **A `flowRow` zero-gap foot-band count.** I instrumented `flowFromBox` only. `flowRow`'s `:3708` is
  character-identical and equally unguarded; its 5 boxes were not split by band. If several of those
  are in the band, the pair of sites is worth more than one document — but that is an opinion, not a
  measurement.

## 8. Provenance

- Engine: `89b0d9c9`, `DocxWriter.java` 7,849 lines. Java, not C#.
- Corpus: `corpus-v1` release via `tools/p2w-bench/corpus-fetch.sh` → "corpus: 214 PDFs, 212 scored in
  RANKING.csv, 0 missing".
- Conversion: `build-engine.sh` (48 s build), 4 × `ConvertAll` shards, `-Dp2w.census=…`, 214/214
  converted, 0 failed.
- Prior work read: `FINDINGS/ANCHORED-BOX-POPULATION-25NOV.md`,
  `FINDINGS/gapcap-latch-census-01-GAPCAP-LATCH-CENSUS-25NOV.md` (via the population finding),
  `FINDINGS/44_header_footer-FLOWFROMBOX-ALREADY-GUARDED-AND-INERT-1815-relay.md`,
  `FINDINGS/FOOTBAND-FOUR-SITES-61-IS-CLEAN-24NOV.md`, `SETTLED.md` (last 200 lines), `INSTRUMENT.md`.
- `anchors.py` was not used: it needs a converted corpus directory keyed to the *uninstrumented* engine,
  and the census counters answer the same question at box granularity, which `anchors.py` (character
  counts inside `w:txbxContent`) cannot attribute to a writer.
