# Re-base of `PATCH-justified-lines-spacing` — the change is already in the engine

Tree: `/scratch/work/CS`, branch `main`, HEAD `85da217` ("p2w fixer: slot released").
Original patch: `tools/p2w-bench/patches/PATCH-justified-lines-spacing.patch` (288 lines).
Re-based patch: `tools/p2w-bench/patches/PATCH-justified-lines-spacing-REBASED.patch`.

**Bottom line.** The whole mechanism the patch describes — `Box.stretchPt` / `Line.stretchPt`, the
per-page 3rd-percentile gap floor, `stretchOf()`, the non-space-glyph word-gap measurement, the
0.30 em cap, and `w:spacing` emitted from both `lineParagraph()` and `flowFromBox()` — is **already
present in the current engine, character for character**. It was landed on 19 Nov 11:55 as commit
`4147d54` *"engine: a justified line is written justified - 7 documents newly clean, 0 worse"*,
whose message credits this very patch ("the fixer found and measured this mechanism first (16:58
run) and could not land it … The patch is its `patches/PATCH-justified-lines-spacing.patch`").

So the original patch fails `git apply --check` for the one reason a patch can fail after landing:
its `+` lines are already in the file. It applies cleanly (`exit 0`) to `4147d54^` (`2756ccb`),
which I verified in a throwaway worktree.

There is therefore **no code to re-implement**. The re-based patch carries **no behavioural
change**; what it does contain is recorded in §2, and the one genuine semantic difference between
the original patch and the current engine is in §5.

---

## 1. What already existed, and what is missing

Grepped for `stretchPt|w:spacing|spacingTw|gapFloor|stretchOf|collectWordGaps|medianWordGap|
stretchTw|isLeader|hasComplexScript` across `app/src/main/java/com/kavopdf/app/engine/`.
Every element of the mechanism is present, at these current sites:

| mechanism element (per the original patch) | current site | present |
|---|---|---|
| `Box.stretchPt` field + javadoc | `PdfToWord.java:245` (javadoc 232–244) | yes, verbatim |
| `Line.stretchPt` field + javadoc | `PdfToWord.java:3268` (javadoc 3267) | yes, verbatim — but never written or read (see §5) |
| `collectWordGaps()` — gap from the last **non-space** glyph's advance end to the next non-space glyph's start (trap 2) | `PdfToWord.java:4162–4182` | yes, verbatim |
| `medianWordGap()` | `PdfToWord.java:4184–4190` | yes, verbatim |
| `isLeader()` (dot-leader guard) | `PdfToWord.java:4192–4195` | yes, verbatim |
| `hasComplexScript()` (complex-script guard) | `PdfToWord.java:4197–4211` | yes, verbatim |
| `stretchOf()` — shortfall, `< 3 pt` guard, half-length bound | `PdfToWord.java:4213–4270` | yes, verbatim **plus a fourth guard at `:4250–4268`** (§5) |
| per-page gap floor: 3rd percentile of the page's inter-word gaps, `gaps.size() >= 8` | `PdfToWord.java:4963–4979`, inside `toParagraphs()` (`:4934`) | yes, verbatim |
| `buildPara(..., float gapFloor)` signature + both call sites | `PdfToWord.java:5276–5277`, calls at `:5061` and `:5067–5068` | yes, verbatim |
| `box.stretchPt = stretchOf(line, gapFloor);` | `PdfToWord.java:5405` | yes, verbatim |
| `stretchTw()` — twips per character, **0.30 em** cap (trap 1) | `DocxWriter.java:4422–4445`; cap at `:4443` (`Math.round(b.size * 0.30f * TWIPS_PER_PT)`, `TWIPS_PER_PT = 20.0` at `:52`) | yes, verbatim |
| `runXml(...)` 4-argument overload carrying `spacingTw` | `DocxWriter.java:4475–4476`; 1-, 3-arg overloads at `:4448`, `:4452` | yes, verbatim |
| `w:spacing w:val` emitted after `w:color`, before `w:sz` | `DocxWriter.java:4498–4503` | yes, verbatim |
| emission site 1: the anchored line paragraph | `DocxWriter.lineParagraph()` `:3559`, `int spacingTw = p.align == 0 ? stretchTw(b) : 0;` at `:3576`, passed at `:3579` | yes, verbatim |
| emission site 2: the flow paragraph | `DocxWriter.flowFromBox()` `:4154`, `:4392` and `:4395` | yes, verbatim |

**Missing: nothing of the mechanism.** Three things are worth naming anyway:

1. **`Line.stretchPt` is a dead field** — declared at `PdfToWord.java:3268`, and the only
   `.stretchPt` references in either file are `box.stretchPt` (`PdfToWord.java:5405`) and the two
   reads in `DocxWriter.stretchTw()` (`:4434`, `:4437`). The original patch is identical in this
   respect, so it is a carried-over wart, not a re-base gap.
2. **`DocxWriter.flowParagraph()` (`:4400`) emits no spacing** — it calls
   `runXml(sb, run, p.heading > 0)` at `:4417`. It takes a `Para`, not a `Box`, so there is no
   `stretchPt` to emit; the original patch also left it alone. Same behaviour, not a gap.
3. **The fourth guard** in `stretchOf()` (`PdfToWord.java:4250–4268`) is *not* in the original
   patch. It is the one place where the current engine differs semantically (§5).

---

## 2. The re-based patch

Path: `tools/p2w-bench/patches/PATCH-justified-lines-spacing-REBASED.patch` (34 lines, 2 hunks,
+12 lines, 0 deletions, engine behaviour unchanged).

Because every `+` line of the original patch is already in the tree, a re-base of it is the empty
diff, and `git apply` rejects a file with no valid patch in it (`error: No valid patches in input
(allow with "--empty")`, exit 128 — I checked). The re-based patch is therefore anchored at the two
sites the original patch rewrote, and records there, in the code, that this mechanism *is* that
patch and where its two traps live. No executable line is added, removed or reordered.

Hunk 1 — `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, hunk header
`@@ -4429,6 +4429,11 @@`:

* **before:** the javadoc of `stretchTw()` ends at the sentence "…a line 1-2 pt short of its edge
  is short of it for that reason and not for this one." (`:4431`) and the method begins at `:4433`.
* **after:** five javadoc lines are inserted after `:4431` recording that this is the emission half
  of `PATCH-justified-lines-spacing.patch`, that it is already in the tree at `4147d54`, and that
  the 0.30 em cap is trap 1 of the finding (a 0.06 em cap is 11 twips/char at 9 pt). The method
  body is untouched; `private static int stretchTw(...)` moves from `:4433` to `:4438` (verified by
  applying the patch and grepping).

Hunk 2 — `app/src/main/java/com/kavopdf/app/engine/PdfToWord.java`, hunk header
`@@ -4230,6 +4230,13 @@`:

* **before:** the javadoc of `stretchOf()` lists three guards and closes with `</ul>` (`:4232`);
  the method begins at `:4234`.
* **after:** seven javadoc lines are inserted after `:4232` recording that this method,
  `collectWordGaps()` and the gap floor in `toParagraphs()` are the change proposed by the original
  patch, that it is already in the tree, and that the guard which follows is *not* part of it. The
  method body is untouched; `private static float stretchOf(...)` moves from `:4234` to `:4241`
  (verified the same way).

Why not a behavioural patch: the only behavioural delta available is the *removal* of the fourth
guard (§5), which would restore the original patch's semantics exactly — and re-introduce the one
regression the landing commit measured and killed. I did not ship that. The hunk that would do it is
quoted in §5 so the decision stays with you.

---

## 3. `git apply --check`

```
cd /scratch/work/CS && git apply --check tools/p2w-bench/patches/PATCH-justified-lines-spacing-REBASED.patch
```
printed nothing and exited 0 (checked twice: against the clean tree, and again after the build and
`git checkout --`).

---

## 4. Build

`git apply` of the re-based patch succeeded (12 insertions, 2 files), then
`bash tools/p2w-bench/build-engine.sh`, exit 0, engine built in 34 s. Last 10 lines verbatim:

```
== fetching PDFBox-Android and its dependencies ==
== compiling stubs, engine and ConvertAll ==
Picked up JAVA_TOOL_OPTIONS: -XX:CompressedClassSpaceSize=64m -XX:ReservedCodeCacheSize=64m
Picked up JAVA_TOOL_OPTIONS: -XX:CompressedClassSpaceSize=64m -XX:ReservedCodeCacheSize=64m
Note: ../../app/src/main/java/com/kavopdf/app/engine/PdfEngine.java uses or overrides a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
Picked up JAVA_TOOL_OPTIONS: -XX:CompressedClassSpaceSize=64m -XX:ReservedCodeCacheSize=64m
engine built - ConvertAll ready (34s)
```

The two `Note:` lines and the deprecation warning are pre-existing; they are not caused by the
patch, which changes only comment text.

The tree was then left clean with `git checkout -- app/src/main/java/com/kavopdf/app/engine/`; the
build's own `trace.py` had touched `tools/p2w-bench/RUN-LOG.md` and `tools/p2w-bench/TRACE.md`, and
those two were reverted as well. `git status --porcelain` now reports exactly one entry — the new
patch file, untracked:

```
?? tools/p2w-bench/patches/PATCH-justified-lines-spacing-REBASED.patch
```

Nothing was committed, nothing pushed, no `screen.py`, no measurement.

---

## 5. What makes the current engine's semantics differ from the original patch

**One thing: a fourth guard inside `stretchOf()` — `PdfToWord.java:4250–4268`, 19 lines.** It is an addition,
not a change: every line of the original patch is present unchanged, and this block follows the
`shortfall > 0.5 * length` guard and precedes `return shortfall;`.

```java
List<Float> gaps = new ArrayList<>();
collectWordGaps(ln, gaps);
if (gaps.size() >= 2) {
    float explained = gaps.size() * Math.max(0f, med - gapFloor);
    float slack = Math.max(2f, 0.35f * shortfall);
    if (Math.abs(shortfall - explained) > slack) return 0f;
}
```

Effect on the semantics: the original patch stretches a line whenever the measured shortfall is
≥ 3 pt and bounded by half the line's length. The current engine additionally requires that the
shortfall be *explained* by the line's own word-gap inflation (`gaps × (median gap − gapFloor)`),
within `max(2 pt, 35 % of the shortfall)`; otherwise it returns 0 and the line is left alone.

Why it exists, in the landing commit's own words (`4147d54`): `natural` sums glyph **advances**, and
an advance does not include letter-spacing, so on `39_small_caps_letter_spacing` the shortfall was
tracking, not justification; the original patch took that document from 0.72 to 3.74 — "the only
regression the patch had out of 25 documents it moved". With the guard, that document does not
change and the commit reports 22 improved / 0 worse over 213 documents in both formats.

Consequence for a re-base: the current engine accepts a **strict subset** of the lines the original
patch would stretch. Nothing else differs — I diffed the original patch's post-image (patched onto
its base `2756ccb`) against HEAD and every other element listed in §1 came out byte-identical
(`collectWordGaps`, `medianWordGap`, `isLeader`, `hasComplexScript`, `stretchTw` and all
`stretchPt` / `spacingTw` / `buildPara` / `gapFloor` call sites and fields; the only diff hunk in
either file is the guard block above).

If you want the original patch's semantics *exactly*, this is the hunk to apply — I have **not**
applied it, and I recommend against it:

This hunk is real and applies to the current tree (`git diff` of the edit, then reverted; I did
not leave it applied):

```diff
diff --git a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
index 4f0e6a5..c235664 100644
--- a/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
+++ b/app/src/main/java/com/kavopdf/app/engine/PdfToWord.java
@@ -4247,25 +4247,6 @@ public final class PdfToWord {
         // A line cannot have been stretched by more than a fraction of its own length; past
         // that the measurement is describing something else - a tab run out, a clipped line.
         if (shortfall > 0.5f * Math.max(1f, ln.right - ln.x)) return 0f;
-        // THE SHORTFALL MUST BE THE WORD GAPS, NOT THE LETTER SPACING.
-        //
-        // `natural` sums each glyph's ADVANCE, and an advance does not include letter-spacing: a
-        // page that sets 39_small_caps_letter_spacing puts its characters further apart than their
-        // advances say, so `ln.right - (first.x + natural)` counts that extra tracking as a
-        // shortfall the writer then fills by stretching the word gaps. It filled a line that was
-        // never justified, and the document went 0.72 -> 3.74 - the only regression the patch had
-        // out of 25 documents it moved.
-        //
-        // A justified line's shortfall IS its word-gap inflation times the number of gaps, so
-        // compare the two. When they disagree the line was not justified and the difference is
-        // tracking, which the writer must leave alone.
-        List<Float> gaps = new ArrayList<>();
-        collectWordGaps(ln, gaps);
-        if (gaps.size() >= 2) {
-            float explained = gaps.size() * Math.max(0f, med - gapFloor);
-            float slack = Math.max(2f, 0.35f * shortfall);
-            if (Math.abs(shortfall - explained) > slack) return 0f;
-        }
         return shortfall;
     }
 
```

Two smaller differences, neither semantic:

* `Line.stretchPt` is declared and never assigned or read (in both versions). The model carries the
  shortfall on `Box`, not `Line`; the `Line` field is inert.
* `halfPointsDown()` still floors the run size (`9.2 → 9.0`, `8.8 → 8.5`). The SPAN finding
  attributes 29–90 % of the residual drift to that floor, but it is outside this patch's mechanism
  and neither the original patch nor the current engine touches it. So a line whose stretch is
  emitted can still come out a few per cent narrow for a *different* reason, which is exactly what
  the patch's own `< 3 pt` guard is about.

---

## 6. What I did not do, and what I am not claiming

* No measurement. No `screen.py`, no corpus pass, no `regress.py`. Every performance number above
  (`7 documents newly clean`, `39_small_caps 0.72 → 3.74`, `22 improved / 0 worse`, the 5.37 → 1.76
  and 8.09 → 5.02 screens) is quoted from `FINDINGS/content-partly-lost-JUSTIFY-170800-fixer.md`
  or from commit `4147d54`'s message — **I did not observe any of them**, and none of them is a
  claim about what the re-based patch does, because the re-based patch changes no behaviour.
* No commit, no push, no change to `benchmarks/`.
* I did not re-derive whether the landed mechanism is *correct*; I only established that it is
  present, that it is the same code the patch proposed, and that the tree still compiles.

## Open questions

* Whether the parent wants a patch that restores the original patch's semantics exactly (the guard
  removal quoted in §5, which re-introduces the measured `39_small_caps_letter_spacing` regression)
  or the no-behaviour-change re-base delivered here. That is a call for whoever owns the ratchet;
  the guard-free variant is one hunk and I can produce it on request.
* Whether `PATCH-justified-lines-spacing.patch` should now be marked as landed (e.g. moved to
  `patches/` with a `LANDED-` prefix, as the other landed patches are) — not stated anywhere I
  read, and not something I did.
