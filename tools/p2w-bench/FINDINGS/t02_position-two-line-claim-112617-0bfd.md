# The two-line claim for `t02_position`: the `.txt` half is real, the "same mechanism, clears both" half is not

**21 Nov, 11:26 IST. Verification only — no engine file touched, nothing measured.** Checking
`FINDINGS/47_margins-TXT-HALF-IS-T02-1055-f1x.md`, which claims `t02_position` (`.txt`) and
`47_margins` (`.docx`) are one mechanism and that a two-line change in
`PdfToWord.uprightIfPageIsUpsideDown` clears both.

**Verdict: REFUTED as stated, SUPPORTED in the narrow `.txt` sense.**

* The *diagnosis* is right and is in the code, exactly where the finding says: the two guards on
  that page contradict each other, `flippedPage` can never be true, and the `.txt` writes the
  mirrored model x. Confirmed by reading `PdfToWord.java:1033` against `:3677` (§1).
* The *claim of shared mechanism* is wrong. `.txt` and `.docx` place a line's x by two different
  code paths with two different mirror predicates; the change reaches `Para.lineX`/`lineY` only,
  and `lineX` is read by `TxtWriter` and by nothing else (§1).
* The *claim that it clears `47_margins`* is wrong on the evidence that exists: `47_margins`
  **already passes on all five `t02_position` documents**, including
  `one-page-rotated-180-degrees`, in the stored LibreOffice table. There is nothing there for it
  to clear (§3).
* The two lines as written are **not safe to apply verbatim**: they delete the only guard
  protecting `15_stamp_on_scanned_page`, whose page is 100 % rotated glyphs at 9° (§2).

---

## 1. The two code paths, and where they diverge

### The `.txt` half — leading spaces

| step | file:line | what it does |
|:--|:--|:--|
| the page is turned | `PdfToWord.java:1031-1034` | `pageTurn()` sees ≥ 90 % of glyphs at `dirx < -0.5`, returns `(rot+180)`, and **clears `rotated` on every turned glyph** |
| the page is asked again | `PdfToWord.java:1256` | `boolean flippedPage = uprightIfPageIsUpsideDown(glyphs);` — called *after* the flags were already cleared |
| the guard that bails | `PdfToWord.java:3677` | `if (!g.rotated) return false;` — every glyph is now `rotated=false`, so this returns on the first one; `flippedPage` is **always false** on a page `pageTurn` already handled |
| the line's x is written | `PdfToWord.java:5342-5345` | `turnedFrame = flippedPage \|\| (line.rotated && \|angle\|≈180 && !ring)` → `p.lineX.add(turnedFrame ? pageWidth - line.right : line.x)`; on this page all three are false, so `lineX = line.x`, the **mirrored** model x |
| leading spaces | `TxtWriter.java:501`, `:507`, `:524` | `lx = para.lineX.get(li)` → `int pad = column(lx, charW)` → `pad` spaces |
| the ruler | `TxtWriter.java:733-739` | `column(x, charW) = round(x / charW)`, one **global** character width for the whole document, clamped to `MAX_INDENT = 400`, no page margin subtracted |

That the collision is real is not an inference: `:1033` runs inside `readPage` (declared at `:884`)
and `:1256` is 223 lines later in the same method, on the same `glyphs` list. The comment at
`:3684-3694` even records what the mirroring is worth — *"one-page-rotated-180-degrees 395.92 vs
395.90"* — which was measured when `flippedPage` still fired for it. `:1033` landed later and
pre-empted it. That is the whole defect, and the finding's diagnosis of it is correct.

### The `.docx` half — the line's x

| step | file:line | what it does |
|:--|:--|:--|
| the box's x | `PdfToWord.java:5386` | `box.x = line.x;` — the **same** `line.x`, taken straight, **not** through `buildPara`'s `turnedFrame` |
| the mirror | `DocxWriter.java:4648-4657` | `mirrored(b)` = `b.rotated && \| \|b.angle\|-180 \| < 1 && !b.ring` — **no `flippedPage` disjunct exists here** |
| the placement | `DocxWriter.java:4682-4686` | `frameOfLine` mirrors: `px = pageW - b.x` |
| a flowed line | `DocxWriter.java:4204`, `:4433` | `leftTw = round(b.x * TWIPS_PER_PT)` → `w:ind w:left = leftTw - bandLeftTw(...)` — continuous twips, measured from the page edge |

### Where they diverge — three separate places, not one

1. **The mirror predicate.** `buildPara:5342` has a `flippedPage` disjunct; `DocxWriter.mirrored:4648`
   does not. The two writers can therefore disagree about whether the same line is mirrored, which
   is exactly what happens today on `one-page-rotated-180-degrees`.
2. **The unit.** `.txt` throws x away into an integer column count against one global character
   width (`TxtWriter:733-739`); `.docx` keeps x to the twip (`DocxWriter:4204`). A proportional
   face has no single character width, so `.txt` loses information `.docx` never loses. This is why
   `t02_position` fits its own ruler (`verify_txt.py:840-858`) while `47_margins` does not need to.
3. **The origin.** `.txt` divides the absolute x; `.docx` subtracts the column's band left
   (`:4433`). A page whose left margin moves shifts `47_margins` and can leave `t02_position`
   unmoved, and vice versa.

**And the change cannot reach the `.docx` by any route.** `flippedPage` has exactly four uses
(`:1257`, `:1472`, `:5061`, `:5068`); `:1257` feeds a `turnedPage` parameter that `toLines`
declares at `:3702` and **never reads**; the other three all end in `buildPara`, which writes
`Para.lineX`/`lineY`. `lineX` is read only in `TxtWriter` (`:180-182`, `:215`, `:267-270`, `:284-286`)
— the single hit in `DocxWriter:3275` is a debug string reading `p.boxes.get(0).x`, not `lineX`.
So the claim "the same mechanism, one change clears both" fails on the code, not on a measurement.

`47_margins`'s own failures are a different fault: `FINDINGS/47_margins-REACH-140500.md` measures
`360_restaurant_menu` at median 0.1 pt with the page anchor **source 52 / render 40** — a
`w:ind w:left` margin offset, on a page whose `w:pgMar` is 0. Nothing about a 180-degree mirror.

---

## 2. The two lines — verbatim, and the defect in them

`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java`, inside `uprightIfPageIsUpsideDown`
(declared `:3673`). Two lines change: `:3677` and `:3679`.

**Before — `PdfToWord.java:3675-3681`**

```java
        for (Glyph g : glyphs) {
            if (g.text == null || g.text.trim().isEmpty()) continue;
            if (!g.rotated) return false;               // an upright glyph: an ordinary page
            if (Math.abs(g.diry) > 0.25f) return false; // the baseline is not horizontal
            if (g.dirx >= 0f) return false;             // not turned round
            turned++;
        }
```

**After — the change as the finding states it**

```java
        for (Glyph g : glyphs) {
            if (g.text == null || g.text.trim().isEmpty()) continue;
            if (g.mirror) return false;                    // a reflection is not a turn
            if (Math.abs(g.diry) > 0.25f) return false;    // the baseline is not horizontal
            if (!g.rotated && g.dirx >= 0f) return false;  // an upright glyph: an ordinary page
            turned++;
        }
```

`g.mirror` is a real field (`PdfToWord.java:1890`, assigned `:2183`), so this compiles. The mirror
guard is load-bearing exactly as the finding says: `417_rotate180_and_mirrored` page 2 is drawn
under `-1 0 0 1 595 0 cm`, so its text-matrix determinant is negative and `g.mirror` is true.

**The defect.** `:3679` as it stands (`dirx >= 0`) is the *only* thing today that stops a page of
9-degree stamps from being declared upside down: a 9° glyph has `rotated = true`, `diry = 0.156`
(under the 0.25 bar) and `dirx = +0.987`. Under the proposed third line, `!g.rotated` is false, so
that glyph passes all three tests and `turned` reaches the whole page.
`15_stamp_on_scanned_page` is exactly that page — `PdfToWord:3912-3916` records that its 20
rotated glyphs are **100 % of the page's glyphs** — and `pageTurn:8846-8860` does not protect it
(it counts only `dirx < -0.5`, so it returns 0). Every flag would be cleared, `line.rotated`
(`:3905`, `allRotated`) would go false, `box.rotated` (`:5402`) would go false, and the stamp would
reach the `.docx` as upright text at angle 0. That is the fault the angle fix at `:3905-3931` was
written to repair, reintroduced.

**The second line that does what the finding means, without that hole:**

```java
            if (g.dirx > -0.5f) return false;              // not turned round
```

`dirx <= -0.5` plus `|diry| <= 0.25` is a baseline within ~14.5° of 180°, which is the set the
original `dirx >= 0` test was approximating, and it does not consult the `rotated` flag at all —
which is the whole point, since `:1033` has already cleared it. Recommended over the finding's
literal `if (!g.rotated && g.dirx >= 0f) return false;`.

---

## 3. What `t02_position` should read, per document

Before, from `tools/p2w-bench/txt/RANKING-TXT.csv` (columns: document, applicable, passed, failed,
abstained, failed_ids):

| line | document | row | `t02_position` before |
|--:|:--|:--|:--|
| 194 | `one-page-rotated-180-degrees` | `10,9,1,1,t02_position` | **61 of 122 pairs = 50 % → FAIL** |
| 60 | `332_bom_on_drawing` | `8,7,1,1,t02_position` | 11 of 52 = 21 % → FAIL |
| 62 | `334_patent_document` | `7,6,1,1,t02_position` | 10 of 32 = 31 % → FAIL |
| 154 | `74_balance_sheet_indented_subitems` | `10,9,1,1,t02_position` | 10 of 54 = 19 % → FAIL |
| 197 | `price-list-2col-dense-right-aligned` | `10,9,1,1,t02_position` | 35 of 252 = 14 % → FAIL |

The CSV carries only pass/fail per check, not the share; the pair counts are the finding's measured
numbers, which is what my prediction rests on for the numerator.

**Predicted after the change:**

| document | `t02_position` after | row after |
|:--|:--|:--|
| `one-page-rotated-180-degrees` | **122 of 122 = 100 % → PASS** | `10,10,0,1,` |
| `332_bom_on_drawing` | unchanged, 11 of 52 = 21 % → FAIL | `8,7,1,1,t02_position` |
| `334_patent_document` | unchanged, 10 of 32 = 31 % → FAIL | `7,6,1,1,t02_position` |
| `74_balance_sheet_indented_subitems` | unchanged, 10 of 54 = 19 % → FAIL | `10,9,1,1,t02_position` |
| `price-list-2col-dense-right-aligned` | unchanged, 35 of 252 = 14 % → FAIL | `10,9,1,1,t02_position` |

Class total: **5 failing documents → 4**; documents failing any `.txt` check 27 → 26. That matches
the finding's own four numbers, which I am not re-deriving — I am checking them against the code.

**What the 100 % rests on.** `t02` fits one ruler as the median of `x / col` over the pairs
(`verify_txt.py:855`) and then asks `|col - round(x/mid)| <= max(2, 0.08*col)`. Today the page's
pairs are `(source x, column of the mirrored x)`, so the ratios are two populations and the median
lands between them; only the pairs where the two happen to agree fall inside the tolerance, which
is why 61 of 122 fail and 61 pass rather than all 122 failing. After the change `lineX` becomes
`pageWidth - line.right`, i.e. the page-frame left edge the source draws — `:3692` records this
document measuring 395.92 against 395.90 drawn — so the ratios collapse to one population and the
median explains every line. Residual risk: on a proportional face `mid` is an estimate, and the
8 % tolerance is a bound on two estimates disagreeing, so a line or two could still sit outside;
100 % is the expected value, not a proof. The finding reports it as measured, and I have not
re-measured it.

**And the `.docx` half, from the stored tables** (`benchmarks/gverify-lo/*.json`, `checks.47_margins`):

| document | `47_margins` today |
|:--|:--|
| `one-page-rotated-180-degrees` | `ok: true` (its 5 failures are 43, 59, 60, 62, 63 — not 47) |
| `332_bom_on_drawing` | `ok: true` |
| `334_patent_document` | `ok: true` |
| `74_balance_sheet_indented_subitems` | `ok: true` |
| `price-list-2col-dense-right-aligned` | `ok: true` |

The Google table agrees where it records the check: `47_margins` is absent from
`benchmarks/gverify/one-page-rotated-180-degrees.json`'s failed list. **All five already pass.**
`47_margins`'s failing set is 16 documents in the LibreOffice table, and none of them is a
180-degree page. Expected `.docx` movement from this change on those five: **none** — and on the
class: **none**, which is the strongest form of "it does not clear `47_margins`".

---

## 4. What is still owed before anyone lands this

1. **`.docx` measurement is mandatory, not optional.** `scope.py` derives scope from changed
   *methods*; `uprightIfPageIsUpsideDown` is not in its table (`SETTLED.md`, "A change it cannot
   name a method for is BOTH"), so the scope is BOTH. The finding converted with `--noDocx`, so the
   `.docx` side was never measured — and it is not provably neutral, because clearing `g.rotated`
   propagates to `line.rotated:3905` → `box.rotated:5402` → `DocxWriter.mirrored:4648`.
   `15_stamp_on_scanned_page` is the document to watch, and it is watchable for exactly the reason
   in §2.
2. **Apply the second line as `if (g.dirx > -0.5f) return false;`**, not
   `if (!g.rotated && g.dirx >= 0f) return false;`. The first is the same fix with the 9° hole
   closed; the second is the finding's text and it opens that hole.
3. **Do not expect a `47_margins` movement.** `SETTLED.md`'s arithmetic stands: the leading-space
   construct reaches 3 of that class's 25 (the class file's current count) or 26 (the 20 Nov
   trace), against a 25 % bar of 7. This change is a `.txt` fix that happens to be worth one
   document; it is not a two-format fix.

**Not done here, deliberately:** no corpus pass, no `--diagnose` (the corpus PDFs are not in the
clone — `benchmarks/corpus-extra/` holds only the real-world documents, and
`/scratch/work/p2w/corpus` does not exist in this sandbox, so the five documents could not be
converted), no engine edit, no edit to `verify_txt.py`, `verify_google.py` or
`tools/p2w-bench/txt/`. The engine was built (`tools/p2w-bench/build-engine.sh`, 37 s) only to
confirm the tree compiles as read.
