# Audit: the .txt seal-placement fix (relay file of 28 Nov, slot 09:16)

Read-only audit of `FINDINGS/TXT-SPLITS-A-LETTER-SPACED-LINE-INTO-ONE-LINE-PER-GLYPH-28NOV-relay.md`
against `kavopdf/app` at HEAD `2cc463a` (shallow clone, depth 1). Nothing was modified, committed or
pushed; the working tree is clean.

Companion file: `305-placement-fix.patch` (the unified diff, `git apply --check` clean against HEAD).

---

## 1. The sites the hunks target

All line numbers are HEAD `2cc463a`.

`app/src/main/java/com/kavopdf/app/engine/TxtWriter.java`

| line | what |
|--:|:--|
| 95 | `for (Object block : pageOrder(page))` — the only call site |
| 189 | `private static List<Object> pageOrder(PdfToWord.Page page)` — the method Hunk 1 renames |
| 507 | `private static float appendPara(...)` |
| 522 | `float ly = li < para.lineY.size() ? para.lineY.get(li) : 0f;` — **the origin of the 0** |
| 558 | `lastY = ly;` — the line Hunk 2 changes (single occurrence in the file) |
| 526 | `if (blanks > MAX_BLANK_LINES) blanks = MAX_BLANK_LINES;` — `MAX_BLANK_LINES = 10` (line 41) |

`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java` — why the block is last and why `lineY` is empty:

| line | what |
|--:|:--|
| 1629 | `if (ring.size() >= 8) ordered.add(ringPara(ring));` — the seal's ring is appended **after** the page's own text |
| 1636–1643 | stamp overlay: every `Para` with `stamp == true` is removed from `ordered` and re-added at the end |
| 1660 | `page.blocks.add(o)` — `ordered` becomes `page.blocks` verbatim |
| 1668–1669 | `attachShapes` / `attachPictures` — these append `DocxWriter.Shape` / `DocxWriter.Picture` **after** the paras |
| 4101–4140 | `ringPara(...)`: `p.lineX.add(ln.x)` (4125), **`lineY` deliberately left empty** (comment 4118–4124), `p.top = min(ln.y)` (4130) |
| 4130 | `p.top = top == Float.MAX_VALUE ? 0f : top;` — the `0f` sentinel for a para with no lines |
| 5296 | `p.top = group.get(0).y;` — the ordinary paragraph path; **raw, unmirrored** |
| 5345–5346 | `lineX`/`lineY` are mirrored into the page frame for a turned line — **`top` is not** |
| 950, 962, 980, 1006 | form values / annotation runs / annotation text / OCR blocks: `p.top = 0;` and `page.blocks.add(p)` |

So the construct is real and it is two decisions in the model, not a writer bug: the ring paragraph is
appended last on purpose (1629), and it carries `top` but no `lineY` on purpose (4118–4130).

---

## 2. Do the hunks apply as written?

**Hunk 2 — yes, verbatim.** `lastY = ly;` at 558 is unique; the guard drops in with clean context.

**Hunk 1 — no, not as printed.** The relay shows only the new wrapper and says in prose that "Hunk 1
renames the existing `pageOrder` body to `pageOrderByColumn`". A rename is a change to the *declaration
line* (189), and the printed hunk contains no `-` line for it and no `@@` header. Applied literally it
leaves two methods named `pageOrder` (a duplicate-method compile error) and a call to a
`pageOrderByColumn` that does not exist. It is also not a unified diff at all — no hunk headers, no
context, no index line. The relay's stated size (+82/−1) does not match any real patch; the version that
does apply is **+42/−2**.

The diff in `305-placement-fix.patch` supplies the missing rename and is `git apply --check` clean against
HEAD `2cc463a`.

---

## 3. Is ordering by `top` safe for blocks that legitimately have no vertical position?

Mostly yes, for the reason the relay did not state, and there is one hole.

**Covered.** `hoistLastPara` bails on `Float.isNaN(top) || top <= 0f`. Every block in the model that has
no real vertical position carries exactly `top = 0f`: the ring paragraph when its ring is empty
(PdfToWord:4130), form values (950), annotation runs (962), annotation text (980) and OCR blocks (1006).
Those are appended last by `page.blocks.add` and would otherwise be the block the hoist acts on — the
`<= 0f` test is what keeps the fix off every OCR and every form-value page. That is the right guard, and
it is load-bearing: remove it and every scanned page's OCR text would be re-ordered by a y of 0.

Also safe by construction:

* `pageOrderByColumn` returns the `page.blocks` list **itself** in its early-return branches, but
  `hoistLastPara` copies into a new `ArrayList` before reordering, so `page.blocks` is never mutated and
  a second call cannot compound. This is the axis on which the `.docx` is provably untouched: `pageOrder`
  has exactly one caller (TxtWriter:95) and `DocxWriter` never calls it.
* The two-column path returns `Piece` objects; `hoistLastPara` finds no `Para`/`Table`, `last` stays `-1`,
  and it returns unchanged. Two-column pages are out of scope, as the relay claims.
* A `Table` in last position is refused by the `instanceof` test, and the `run` walk-back stops at any
  non-`Para`, so a hoist can never cross a table.

**The hole: `Para.top` is not in the page frame for a turned line.** `buildPara` sets
`p.top = group.get(0).y` (5296) from the raw `Line.y`, and the file's own comment at 5322–5346 says a
180-degree line's coordinates come out of PDFBox mirrored about the page ("the page draws CANCELLED at
x=337.6 and the model holds x=151.01"). `lineX`/`lineY` are corrected at 5345–5346; **`top` is never
corrected.** `pageOrderByColumn` already knows this — it orders by `paraTop(p)` (TxtWriter:322, computed
from the corrected `lineY`), not by `p.top`. The new `hoistLastPara` uses the uncorrected `p.top` on both
sides of the comparison. Measured in simulation: a `CANCELLED` stamp drawn at y≈700 on an 842-pt page
presents `top ≈ 142` and is hoisted to the *top* of the flow instead of near the foot where it is drawn.

The reason the relay's code has to use `p.top` is the ring: `paraTop()` returns `NaN` when `lineY` is
empty, which is exactly the seal. A one-line refinement exists (`paraTop`, falling back to `p.top`) but it
is **not** in the delivered patch, because the delivered patch is the one that was measured to PASS.

---

## 4. The `lastY` guard

The relay calls it "the proposed `lastY > 0` guard". It is not that: the code is `if (ly > 0f) lastY = ly;`
— the test is on **`ly`**, the current line's baseline, not on `lastY`.

What it does. `ly` is `0f` whenever the paragraph has no `lineY` at all (TxtWriter:522). `lastY` is the
flow's y as the blank-line model sees it; the next paragraph charges
`round((ly - lastY)/pitch) - 1` blank lines (525) against it. Letting `0` become `lastY` tells that model
the flow has jumped to the top of the page, so the next real baseline at y≈304 is charged
`round(304/10) - 1`, capped at `MAX_BLANK_LINES = 10`.

Does it prevent the blank lines? **Yes.** Simulated against the real constants on the 305 shape
(`signed` at 264, seal with no `lineY`, `verify` at 304, pitch 10): without the guard, 10 blank lines
before "Verify online"; with it, 3 — which is the three-line gap the page actually drew. That matches the
relay's "took the file from 30 blanks to 37".

Scope: it only affects lines whose `ly <= 0`. It does not touch the seal's own 48 lines (all `ly = 0`, so
`ly > lastY` is false and no gap is ever opened inside the ring), and it does not touch any line with a
real baseline. A real line drawn at exactly y=0 would lose its `lastY` update; the consequence is a stale
(earlier) `lastY` and therefore fewer blanks, never more.

Two things the relay got wrong about it:

* It is **not** only "load-bearing for Hunk 1". At HEAD, a page carrying both a ring paragraph (appended
  at 1629) and a rotated stamp (the overlay at 1643 is added *after* the ring) already has a `lineY`-less
  paragraph followed by a `lineY`-carrying one, and already inserts up to 10 spurious blank lines. Hunk 2
  changes HEAD output on those pages with no hoist involved. The relay's 27-of-214 blast radius is the
  **union** of the two hunks; no hoist-only A/B was run, so "305 is the only document that moves" is a
  statement about the pair, not about the hoist.
* `ly > 0f` conflates "no baseline" with "baseline at y = 0". The exact predicate is
  `li < para.lineY.size()`, which is what line 522 already tests to produce the `0f`. The delivered patch
  keeps `ly > 0f` because that is the measured form.

---

## 5. Risks the relay file missed

1. **`top` is in the wrong frame for a 180-degree line** (§3). The `.txt` path already had to correct
   `lineY` for this and `pageOrderByColumn` avoids `top` for this reason. The hoist reintroduces it.
2. **The hoist un-does a documented design decision for every ring/stamp page, not just 305.** `ringPara`
   exists because "leaving them inline tore the body text apart — on file 60 the sentence 'in recognition
   of the first rank…' was split by four border letters" (PdfToWord:1625–1629), and the stamp overlay
   exists because "a reader meets it after the page's own words". The fix moves 27 pages' rings and stamps
   from the end of the file into the middle of the body. `t04`/`t08` cannot see this: both are
   line-count and line-order checks, and neither tests that a block stayed contiguous with itself. For a
   *circular* seal, `top` is the topmost glyph of the circle, not the seal's reading start, so the seal's
   ~40 single-character lines now split the body text in the `.txt` — the exact fault `ringPara` was
   written to prevent. "No check regressed on the other 26" is true and is not the same as "no document
   got worse".
3. **"The last block" is not always the appended ring/stamp.** `attachShapes`/`attachPictures`
   (PdfToWord:1668–1669) append `Shape`/`Picture` blocks after the paras, so on pages with a picture or a
   drawn box the hoist acts on the last *`Para`/`Table`*, which may be an ordinary body paragraph. The
   `top <= 0f` and "move up only" conditions make that mostly inert, but the code's own comment ("a
   paragraph the model appended last") describes a narrower contract than the code implements.
4. **The guard's scope is wider than the comment says** (§4, second bullet).
5. **No `.txt` re-conversion was run for the delivered pair in this audit** — this is a static audit plus
   a simulation of the two functions against the real constants, not a rebuild. `305`'s PDF is not in the
   repo (`benchmarks/gverify/305_vaccination_certificate.json` only), so `ConvertOne` could not be re-run
   here; and there is no JVM in this sandbox (`java`/`javac` absent), so the patch was verified with
   `git apply --check` and a Java parser, not `javac`.

---

## 6. Verdict

The construct is real and the placement half is the right half to fix: merging is refuted by the relay's
own `t04` measurement, and re-ordering by `top` keeps the line count at 85. Hunk 2 is correct and
necessary. Hunk 1 is correct for the 305 shape and safe against every block with no vertical position
(`top = 0`), but it is (a) not applicable as printed — it needs the declaration rename the relay only
described, and (b) ordering by the raw `Para.top` is wrong for turned lines, and it moves rings and stamps
into the body of 26 other documents on a rationale `ringPara` argues against.

Ship it as `305-placement-fix.patch`, re-convert all 213, re-stamp, and treat `305` as the only *check*
mover — then look at the 26 by eye before the commit gate, because the checks cannot see what changed in
them.
