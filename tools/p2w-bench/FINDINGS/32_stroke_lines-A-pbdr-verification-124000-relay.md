# Verification: `RULES-PBDR-IMPLEMENTATION.md` against the current `DocxWriter.java`

**Tree examined:** `https://github.com/kavopdf/app` @ `bd6845b` (shallow clone, 21 Nov 2026).
`app/build.gradle` reports `versionCode 316`, `versionName "3.53.26"`.
**Read-only:** nothing was modified, nothing was built, no measurement was run.

Files read in full: `tools/p2w-bench/FINDINGS/RULES-PBDR-IMPLEMENTATION.md` (121 lines),
`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` (7,431 lines, the regions quoted below),
`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java` (the shape attach pass),
`tools/p2w-bench/google_safe.py` (217 lines), and the three later findings that follow the
implementation doc in the same directory.

**Headline:** every symbol the finding uses still exists, and the insertion point is still valid —
the change is mechanically appliable with **one required edit** (a missing `(int)` cast that will not
compile) — but as written it is **inert on this tree**: it cannot place a single border, because the
precondition the finding assumes (a rule is written while the flow is still above it) does not hold.
That is measured in `FINDINGS/content-present-partly-displaced-rules-cannot-flow-044000-f1x.md`, and
two later findings then rule the construct itself out.

---

## 1. Does `shape(StringBuilder sb, Shape s, Ctx ctx)` still exist?

**Yes — the signature is byte-for-byte what the finding assumes.** `DocxWriter.java:2772`:

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
                .append("<w:rPr><w:sz w:val=\"2\"/><w:szCs w:val=\"2\"/></w:rPr></w:pPr>")
                .append("<w:r><w:drawing>")
                .append("<wp:anchor distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\"")
```

It is the only `shape(` declaration in the file. The finding's "before the drawing path" is therefore
line **2779** (`sb.append("<w:p><w:pPr>...`) — or, equivalently and preferably, before line 2773 so the
`ctx.shapeSeq++` is not spent on a rule that never becomes a drawing. `REPORT.md:81` and
`HANDOFF.md:33` both say "first statement of `DocxWriter.shape()` at line 2772 (return before line
2779)", which still matches.

**Single call site** (`DocxWriter.java:2281`, inside `emitBlock`):

```java
            if (s.stampFrame
                    && ctx.stampText.containsKey(s.mergedHost == null ? s : s.mergedHost)) {
                return;
            }
            if (!s.consumed) shape(sb, s, ctx);
```

So a `return` at the top of `shape()` is reached for every rule that is not `consumed` and not a
stamp frame already drawn by its text box — i.e. the hook is still complete.

---

## 2. Does `Ctx` still carry `flowY`, `flowBoxPt`, `newPage`, `pageWidthPt`?

**All four exist, with the same names and types.** `Ctx` is still `private static final class Ctx`
(`DocxWriter.java:749`). `DocxWriter.java:787`, `:793`, `:795`:

```java
        float flowY = -1f;
        /**
         * The height of the last line box AS WRITTEN (through the squeeze and the twip
         * rounding), in points. Its lower {@code 1 - LINE_BASE} is what is left below the
         * baseline before the next paragraph's space-before starts.
         */
        float flowBoxPt = 0f;
        /** Set at a page break so the first line on a page carries no gap. */
        boolean newPage = true;
```

and `DocxWriter.java:913`:

```java
        /** The page's own width in points, so a tab stop can tell when it is at the paper edge. */
        float pageWidthPt = 595f;
```

Nothing missing, nothing renamed, none of them `final`. The only drift is cosmetic: the finding quotes
`flowBoxPt`'s doc comment as one line ("The height of the last line box AS WRITTEN, in points."); the
current comment is the longer form above. `flowY` is also still written by the flow owners the finding
relies on (`DocxWriter.java:3492-3493`, `:3983-3984`, `:4013-4014`) and reset per page
(`:1084-1085`, `:1210-1211`, `:2111-2112`).

---

## 3. Do `isHairline`, `hex(int)`, `LINE_BASE`, `TWIPS_PER_PT` exist?

**All four exist.** Two are constants whose types matter to the snippet:

`DocxWriter.java:2845`:
```java
    private static boolean isHairline(Shape s) {
        float lo = Math.min(s.wPt, s.hPt), hi = Math.max(s.wPt, s.hPt);
        return lo <= 1.5f && hi > 2f;
    }
```

`DocxWriter.java:2690`:
```java
    private static String hex(int rgb) {
        String h = Integer.toHexString(rgb & 0xFFFFFF).toUpperCase(java.util.Locale.ROOT);
        while (h.length() < 6) h = "0" + h;
        return h;
    }
```

`DocxWriter.java:214`:
```java
    private static final float LINE_BASE = 0.8f;
```

`DocxWriter.java:51-52`:
```java
    /** 1 point in twips, for every w:* length. */
    private static final double TWIPS_PER_PT = 20.0;
```

**Note the type:** `TWIPS_PER_PT` is a **`double`**, not an `int`. That is what makes the snippet's
`beforeTw` line fail to compile (see §7). `LINE_BASE` is a `float` as the snippet assumes. All four are
`private static` members of the same class, so a `private static boolean ruleAsBorder(...)` placed in
`DocxWriter` reaches them without any new import.

---

## 4. Does `Shape` have `hPt`, `wPt`, `xPt`, `topPt`, `lineRgb`, `fillRgb`, `lineWidthPt`?

**All seven exist** — `Shape` is still `public static final class Shape` at `DocxWriter.java:2512`, and
the geometry is still one four-field declaration plus the paint fields:

```java
    public static final class Shape {
        public float xPt, topPt, wPt, hPt;
        /** Fill colour 0xRRGGBB, or -1 when the path is only stroked. */
        public int fillRgb = -1;
        /** Fill opacity 0..1, from the PDF's own {@code ca}. */
        public float fillAlpha = 1f;
        /** Outline colour 0xRRGGBB, or -1 when the path is only filled. */
        public int lineRgb = -1;
        public float lineWidthPt;
```

So `s.xPt`, `s.topPt`, `s.wPt`, `s.hPt`, `s.fillRgb`, `s.lineRgb`, `s.lineWidthPt` all resolve, and the
`-1` sentinel convention the snippet tests for (`s.lineRgb >= 0 ? s.lineRgb : s.fillRgb`, `rgb < 0`)
is still the live convention.

---

## 5. Is there already ANY rule/border code path in `DocxWriter`?

**No paragraph-border path exists at all.** `rg -n "pBdr|ruleAsBorder" app/src/main/java` returns
**nothing** — the string `pBdr` does not occur anywhere in the Java sources, and `ruleAsBorder` exists
only in the findings, the two prior-attempt patches under `tools/p2w-bench/FINDINGS/`, and the handoff
text. The 19 Nov attempt (`RULES-PBDR-FIX-MEASURED.md`) was reverted and is not in the tree.

What *does* exist is table borders, which are a different construct and do not touch rules:

* `DocxWriter.java:2068-2070` — a "no border" table default, all four sides `w:val="none"`:
  ```java
        String noBorder = "<w:top w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:left w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
                + "<w:bottom w:val=\"none\" w:sz=\"0\" w:space=\"0\" w:color=\"auto\"/>"
  ```
* `DocxWriter.java:6419-6422` — the only *drawn* border in the writer: a per-cell bottom border for a
  row separator stroke that is heavier/darker than the table's `insideH` (fed from the table model's
  `t.rowStroke`, `:6303-6314`, not from a `Shape`):
  ```java
                if (sepSz > 0 && sepColour != null) {
                    inner.append("<w:tcBorders><w:bottom w:val=\"single\" w:sz=\"").append(sepSz)
                         .append("\" w:color=\"").append(sepColour).append("\"/></w:tcBorders>");
                }
  ```

So a horizontal rule on the page still leaves `shape()` as a floating `<w:drawing>`/`<wp:anchor>`
(quoted in §1) and nothing else. The cause the finding names is intact.

---

## 6. `tools/p2w-bench/google_safe.py` — what it treats as ignored by Google

The file is where the caller expected it: `tools/p2w-bench/google_safe.py` (217 lines). Its ignored
list is `IGNORED`, and it is a **ratchet keyed on document counts**, not a ban:

```python
IGNORED = [
    ("w:framePr", "framePr",
     re.compile(r"<w:framePr\b"),
     "PLAN-DECISIONS F2 / LESSONS.md: Google renders the paragraph as body text at the left margin. "
     "Shipped as 3.53.5 and broke every stamp."),
    ("w:drawing", "floating-drawing",
     re.compile(r"<w:drawing>"),
     "FINDINGS/RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md: Google does not lay out floating drawings from "
     "an imported .docx. It drops the shape and leaves the anchor."),
    ("wp:anchor", "anchored-object",
     re.compile(r"<wp:anchor\b"),
     "Same as above: an anchored object is the wrapper a floating drawing arrives in."),
    ("w:w", "char-width",
     re.compile(r"<w:w\s+w:val="),
     "FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424.md: measured four ways, Google honours no "
     "character-width control at all."),
    ("w:spacing-letter", "letter-spacing",
     re.compile(r"<w:spacing\b[^>]*w:val=\"-?\d+\""),
     "Same finding: w:spacing is ignored along with w:w."),
    ("w:position", "vertical-raise",
     re.compile(r"<w:position\b"),
     "Google ignores w:position; a raised or lowered run renders on the baseline."),
    ("w:before-page-top", "page-top-gap",
     re.compile(r"<w:spacing\b[^>]*w:before=\""),
     "FINDINGS/18_displacement-page-top-before-DROPPED: Google drops w:before at the top of a page - "
     "55.15 pt asked, 0.33 pt rendered."),
]
```

Plus an out-of-band check, `EMBEDDED_FONT`, for a `word/fonts/` part in the zip.

Plainly, for the three constructs the caller named:

* **`w:pBdr` — NOT in the list.** There is no `pBdr` pattern in `google_safe.py` at all
  (`rg -n "pBdr" tools/p2w-bench/*.py` finds it only in a comment in `regress.py:152`). The construct the
  finding proposes is not counted as Google-ignored, which is consistent with `RULES-PBDR-FIX-MEASURED.md`
  having verified a minimal `w:pBdr` .docx renders in Google.
* **`w:ind` — NOT in the list.** No pattern matches `w:ind`; `rg -n "w:ind\b" tools/p2w-bench/*.py` finds
  it only in comments inside `verify_google.py`. So the `w:ind w:left/right/firstLine` the snippet emits
  is invisible to this gate.
* **`w:spacing` — partially.** It is not one entry but **two**, and only one of them can bite:
  `w:spacing-letter` matches `<w:spacing ... w:val="N">` (character spacing), which the snippet does
  **not** emit; `w:before-page-top` matches `<w:spacing ... w:before="...">`, which the snippet
  **does** emit on every carrier paragraph. `[^>]*` cannot cross the tag's `>`, so nothing else in the
  document is caught by accident.

Consequence worth stating, since it is the only gate interaction: each carrier paragraph adds one
`w:before-page-top` instance, and marks its document as a carrier of that construct. In practice this
changes nothing, because `shape()`'s existing drawing paragraph already writes
`w:before="0"` (`DocxWriter.java:2780`, quoted in §1), so every document that has a shape is already a
carrier today. It would only refuse a document that currently carries no `w:spacing w:before` at all —
i.e. one with no paragraphs and no shapes, which the corpus does not contain.

---

## 7. Verdict

**APPLICABLE WITH EDITS — mechanically. But NOT APPLICABLE AS A FIX: as written it is inert on this
tree, and it is a construct two later findings in the same directory rule out.**

### 7a. The edit that is required to compile

One line of the snippet does not compile against the current `DocxWriter`, because `TWIPS_PER_PT` is a
`double` and `Math.round(double)` returns `long`, so `Math.max(0, <long>)` resolves to
`Math.max(long,long)` and its `long` result cannot be assigned to `int` without a cast. (Static reading
of JLS 5.1.3 / `Math`'s overload set — no JDK is installed in this sandbox, so this is not a compiler
run; the other three arithmetic lines in the snippet already carry the explicit `(int) Math.max(0L, …)`
form, which is the same fix.)

```
OLD:  beforeTw = Math.max(0, Math.round((s.topPt - ctx.flowY - below) * TWIPS_PER_PT));
NEW:  beforeTw = (int) Math.max(0L, Math.round((s.topPt - ctx.flowY - below) * TWIPS_PER_PT));
```

Everything else type-checks: `szEighth` and `leftTw`/`rightTw` already cast; `hex(rgb)` takes an `int`;
`LINE_BASE` is a `float` and the expression with it promotes to `double` fine; `ctx.shapeSeq` is not
touched if the `return` goes before line 2773.

### 7b. Where the code goes, exactly

1. **New method** `private static boolean ruleAsBorder(StringBuilder sb, Shape s, Ctx ctx)` — add it
   inside `DocxWriter`, immediately above `shape()`, i.e. before line **2772**. No new imports needed
   (`StringBuilder`, `Math` are already used in this file).
2. **The call**, at the top of `shape()`:
   ```
   insert after line 2772 (the signature) / before line 2773:   if (ruleAsBorder(sb, s, ctx)) return;
   ```
   (or, matching what `REPORT.md`/`HANDOFF.md` say, before line 2779, the first `sb.append` of the
   drawing paragraph — but that wastes one `ctx.shapeSeq` id per rule).

### 7c. Why it is inert here — the finding's premise no longer holds

The finding's whole mechanism is `if (!ctx.newPage && ctx.flowY >= 0 && s.topPt > ctx.flowY)`; it
assumes the rule is written while the flow is still *above* the rule. On the current tree every shape
is written **after** the page's paragraphs and tables, so the flow has already run past every rule and
the guard always yields `beforeTw = 0` — which reproduces exactly the "both landed at the foot of the
page" failure the finding is trying to fix. Verified in the current source, not inferred:

* `PdfToWord.java:7122` — `page.blocks.add(s);`, at the end of the shape attach pass, after the
  paragraphs have already been added (`page.blocks.add(p)` at `:951`, `:963`, `:981`, `:1007`).
* `DocxWriter.java:1333-1335` — the page emit loop walks that list in list order, with no re-sort:
  ```java
        for (int bi = 0; bi < page.blocks.size(); bi++) {
            Object block = page.blocks.get(bi);
  ```
* `sortByTop` is called **only** on the newspaper-column path (`DocxWriter.java:1983-1984`, inside
  `columnPage`, which `pageXml` returns from at `:1321`), never on the ordinary page path.

This is exactly what `FINDINGS/content-present-partly-displaced-rules-cannot-flow-044000-f1x.md`
records ("The implementation is correct and it is inert … Both rules are **behind** the flow"), and its
number for the probe document (`flow after p21 = 805.9 pt`, rule 1 at `y = 110.0`, rule 2 at
`y = 793.89`) is the same tree behaviour that is still present.

### 7d. And the construct itself was ruled out afterwards

The finding is not the latest word in its own directory. In filename-timestamp order the chain is
`RULES-PBDR-FIX-MEASURED` (19 Nov attempt) → **`RULES-PBDR-IMPLEMENTATION`** (the doc under test) →
`…rules-cannot-flow-044000` → `…rules-flush-works-displaces-055000` →
`…rules-are-flow-neutral-065000`. The last of these ends with:

> * **The pBdr carrier paragraph.** 9.6 pt, measured four ways. Never.

Its table measures the carrier paragraph on `18_centred_heading_left_body_txtpos` at **+10.60 pt** of
displacement with the border, **+10.40** with the `w:pBdr` replaced by an inert element, **+10.60** with
no run at all, and **+11.60** with `w:line="20"` — against a +1.00 control with no carrier paragraph.
A fixed ~9.6 pt charge per rule that the finding's gap formula does not account for. The 05:50 finding
adds that when the precondition *was* met, `18_displacement` went PASS → **FAIL** in both Google and
LibreOffice on a document that had been clean, and that the `flowBoxPt` term the finding leans on is 0
at the moment a rule is flushed, "so the term contributes nothing".

Note the 06:50 measurement did not vary `w:before`; it establishes a constant per-carrier charge, not
that the gap is irrelevant. So the honest reading is: the finding's gap formula is not *wrong*, it is
incomplete — it accounts for the gap and not for the carrier paragraph's own minimum advance.

### 7e. Also stale

`REPORT.md:81` and `HANDOFF.md:33` / `HANDOFF.json:741` still queue "Land the pBdr rule replacement:
FINDINGS/RULES-PBDR-IMPLEMENTATION.md" as the next action, and the 06:50 finding's own conclusion is
that the class needs a human decision (gate it in Google, declare it out of scope, or authorise a
stated tolerance). The queue and the findings disagree; the findings are later.

---

## Missing symbols

**None.** Every symbol the finding's snippet references — `isHairline`, `hex(int)`, `LINE_BASE`,
`TWIPS_PER_PT`, `Ctx.flowY`, `Ctx.flowBoxPt`, `Ctx.newPage`, `Ctx.pageWidthPt`, `Shape.xPt/topPt/wPt/hPt`,
`Shape.fillRgb/lineRgb/lineWidthPt`, and the `shape()` hook itself — still exists with the same name,
type and visibility. The only defects are the one missing cast (§7a) and the fact that the runtime
precondition the guard tests is never true on this tree (§7c).

## What I did not do

No file was modified, nothing was compiled, no conversion or measurement was run, and `google_safe.py`
was read but not executed (its `--corpus` mode needs an output directory of `.docx` files that this
clone does not contain).
