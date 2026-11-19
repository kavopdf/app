# content-partly-lost / SPAN — the spanning block lands; the justified line tails around it do not

Run: 19 Nov 2026, 16:22 IST. Engine at `c8c8ca2` (baseline), built by
`tools/p2w-bench/build-engine.sh`, corpus from the `corpus-v1` release (211 PDFs).

Documents in scope, converted with `ConvertAll` and rendered back through
`soffice --headless --convert-to pdf`:

    policy-2col-spanning-section-heading
    academic-paper-ieee-2col-abstract
    magazine-2col-pullquote-spanning
    61_two_col_abstract_spanning

## The answer in one paragraph

The spanning block is **not** the displaced ink, and the mechanism is **not** a placement
decision. On all four documents the spanning element lands within **0.16 pt horizontally and
1.2 pt vertically** of where the page drew it. What is displaced is the **right tail of every
full-width body line, in both columns**, and the error is **horizontal but intra-line**: the
line's origin is right to 0.1 pt and the deficit accumulates word by word until the last word
sits **15 to 36 pt** left of the source. It accumulates because the engine emits each line as one
anchored text box whose text runs at the substitute face's **natural advance at a floored
half-point size**, with no `w:w` character scale and no `w:spacing`, so neither the page's
justification (expanded word spaces) nor the page's true font size (9.2, 8.8, 8.9 pt) survives
into the run. The box is placed from the source; the ink inside it is not.

---

## Q1 — Which specific ink is displaced, and where

Method: rebuild `position()` from `benchmarks/p2w.py` (150 DPI, `INK=68`, `PT=72/150`,
`scipy.ndimage.distance_transform_edt`) and take the **argmax of the distance transform over
source ink** — the single worst-placed source pixel on the page — then read the source word
under it.

```python
import numpy as np, pymupdf
from scipy.ndimage import distance_transform_edt
DPI=150; PT=72.0/DPI; INK=68
def R(p,n):
    pm=pymupdf.open(p)[n].get_pixmap(matrix=pymupdf.Matrix(DPI/72,DPI/72),colorspace=pymupdf.csGRAY)
    return np.frombuffer(pm.samples,np.uint8).reshape(pm.height,pm.width)
def pad(a,H,W):
    if a.shape==(H,W): return a
    o=np.full((H,W),255,np.uint8); o[:a.shape[0],:a.shape[1]]=a; return o
s=R("corpus/D.pdf",P); o=R("pdf/D.pdf",P)
H=max(s.shape[0],o.shape[0]); W=max(s.shape[1],o.shape[1])
sm=pad(s,H,W)<INK; om=pad(o,H,W)<INK
dd=distance_transform_edt(~om); dd2=np.where(sm,dd,-1)
y,x=np.unravel_index(np.argmax(dd2),dd2.shape)
print(x*PT, y*PT, dd2[y,x]*PT)
```

Result — on every one of the four documents the worst ink is **the last word of a body line in
the right-hand column**, never the spanning element:

| document | worst ink (pt) | distance | source word there |
|---|---|---|---|
| policy-2col-spanning-section-heading p1 | x 543.4, y 132.5 | **24.96** | `certificate` |
| academic-paper-ieee-2col-abstract p1 | x 549.1, y 241.0 | **32.64** | `magazine` |
| academic-paper-ieee-2col-abstract p2 | x 288.0, y 596.2 | **27.59** | `Rep.` |
| magazine-2col-pullquote-spanning p1 | x 548.6, y 373.4 | **21.76** | `channelled` |
| 61_two_col_abstract_spanning p1 | x 514.6, y 236.2 | **15.84** | `find` |

My instrument reproduces the published numbers on the same pages, so it is the same measurement:
`61` share5 2.22 / max 15.84 (published 2.01 / 15.84 — max exact); `policy` share5 5.99 / max
24.96 (published 5.37 / 24.96 — max exact); `academic` p1 share5 8.10 / p90 8.16 (published
8.09 / 8.16).

### The two worst lines, with both rectangles

Source rectangle and our rectangle, for the line that carries the worst ink
(`pymupdf` `get_text("dict")` line bbox, then `get_text("words")` for the word):

**policy-2col-spanning-section-heading, page 1, right column**

| | rect (x0, y0, x1, y1) | width |
|---|---|---|
| source line | (307.56, 129.21, 544.29, 138.41) | 236.73 |
| our line | (307.70, 129.00, **519.45**, 138.00) | 211.75 |
| source word `certificate` | (507.51, 129.21, 544.29, 138.41) | 36.78 |
| our word `certificate` | (**483.55**, 129.00, 519.45, 138.00) | 35.90 |

**academic-paper-ieee-2col-abstract, page 1, right column**

| | rect (x0, y0, x1, y1) | width |
|---|---|---|
| source line | (306.14, 237.67, 549.95, 246.57) | 243.81 |
| our line | (306.30, 237.70, **517.48**, 246.20) | 211.18 |
| source word `magazine` | (515.85, 237.67, 549.95, 246.57) | 34.10 |
| our word `magazine` | (**484.95**, 237.70, 517.48, 246.20) | 32.53 |

The line's left edge is right; the line's **right edge is 24.98 pt and 32.63 pt short**, and the
last word is displaced by exactly that: `certificate` dx **-23.96 pt**, `magazine` dx
**-30.90 pt**.

### And the spanning block itself, for contrast

| document | element | source rect | our rect | dx0 | dy | dW |
|---|---|---|---|---|---|---|
| policy | section heading `4.5 Leave without pay…` | (59.02, 441.54, 382.04, 454.04) | (59.10, 441.00, 381.79, 453.50) | **+0.08** | **-0.54** | -0.32 |
| magazine | pullquote `"A station is not a destination…"` | (162.81, 463.25, 432.47, 478.25) | (162.90, 462.70, 432.22, 477.70) | **+0.09** | **-0.54** | -0.34 |
| 61 | title line 2 | (131.68, 128.42, 463.34, 142.81) | (131.80, 129.60, 463.51, 142.60) | **+0.12** | **+1.18** | **+0.04** |

Three of the four spanning elements are single, ragged-right lines and come out of the engine
**essentially perfect** — width within 0.34 pt on a 269–323 pt line. The fourth (`61`'s abstract,
a five-line justified block that spans both columns) *is* displaced, by -14.99 pt at its last
word — but its sibling body text in the same face at the same size is displaced by -7.36 pt on
lines half as long, and 447.41/228.73 = 1.96 against 14.99/7.36 = 2.04. **The abstract drifts
further only because its lines are twice as long.** Spanning is a red herring.

---

## Q2 — Horizontal or vertical? Both measured separately

Per line: `dx_first` is the offset of the line's first word (the line's origin), `dx_last` the
offset of its last word, `dy` the offset of the first word.

```python
# pymupdf get_text("words") on source and on our render, matched by word text + nearest
# (x0,y0); group source words into lines by y0 and a >10 pt x gap; report
# dx_first = our.x0 - src.x0 for the first word, dx_last for the last, dy likewise.
```

**Horizontal, at the line origin: there is no error.**

| document | dx of line origin (median) | range |
|---|---|---|
| policy p1 | **+0.08** | +0.08 … +0.14 |
| academic p1 | **+0.15** | +0.15 … +0.16 |
| academic p2 | **+0.15** | +0.15 |
| magazine p1 | **+0.15** | +0.09 … +0.16 |
| 61 p1 | **+0.10** | +0.10 … +0.16 |

**Horizontal, inside the line: that is where the error is, and it accumulates.**

| document | dx of last word (median) | worst dx_last |
|---|---|---|
| policy p1 | -6.50 | **-35.79** |
| academic p1 | -6.42 | **-37.83** |
| academic p2 | -17.22 (p1) | -34.58 |
| magazine p1 | -7.69 | **-30.04** |
| 61 p1 | -6.50 | **-14.99** |

Word-by-word, the accumulation is monotone from the line's second word: `policy` line at
y 129.21 — word 1 `+0.08`, mid-line word `-12.22`, last word `-23.96`.

**Vertical: there is no error.**

| document | dy (median) | dy range | words with \|dy\| > 2 pt |
|---|---|---|---|
| policy p1 | -0.21 | -26.01 … +25.59 | 2 of 551 |
| academic p1 | +0.03 | -11.57 … +11.63 | 5 of 672 |
| academic p2 | +0.46 | -0.16 … +1.02 | **0 of 361** |
| magazine p1 | -0.15 | -0.79 … +0.69 | **0 of 457** |
| 61 p1 | +0.93 | +0.69 … +1.18 | **0 of 398** |

The line pitch is identical, so no paragraph spacing was inserted: `policy` source pitch
12.9 pt ×29 lines, our pitch 12.9 pt ×29 lines; `academic` 11.6 pt ×24 in both.

The handful of large `dy` values are a **separate, small defect** and not this one: on
`academic` p1 eight words of the right column's third paragraph (`annotated by two annotators
working independently, with`) are emitted as seven one-word boxes stacked at 0.6 pt pitch
(y 272.50, 273.70, 274.30, 274.90, 275.50 …) instead of on one baseline at 272.47. That is
worth its own finding; it moves 3 pt of ink, not 30.

---

## Q3 — Where in the engine

**Placement is correct and it is not where the fault is.** `DocxWriter.anchorBox`
(`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:2617-2631`) takes the page's own line
box and writes it straight through:

    2629   float wPt = Math.max(4f, advance) * 1.12f + b.size * 1.5f;
    2631   anchor(sb, ctx, b.x, b.y - ASCENT * b.size, wPt, hPt, inner.toString(), 0f, -1, 0.6f);

`anchor()` → `anchorAt()` → `anchorShape()`, which puts `b.x`/`b.y` into
`<wp:positionH relativeFrom="page">` (`DocxWriter.java:5328`) and
`<wp:positionV relativeFrom="page">` (`:5330`). Measured above: +0.08 to +0.16 pt. This is right.

**The fault is in what goes INSIDE the box.** Three lines, in one method each:

1. **`DocxWriter.lineParagraph` — `DocxWriter.java:3551-3566`.** This is the paragraph the anchor
   holds. It writes `w:spacing` (line box), `w:ind` (zeroed, correctly) and `w:rPr/w:sz`, and
   **nothing else**. There is no `w:jc`, no `w:w`, no `w:spacing w:val` on the run. The only
   alignment the writer can express anywhere is `align == 1` → `w:jc="center"` and `align == 2` →
   `w:jc="right"` (`:4340-4341`, `:4359-4360`); **there is no path that emits justification at
   all**, and `wrap="none"` (`:5354`) plus `<a:noAutofit/>` (`:5359`) mean the box's width
   constrains nothing — text overflows it at natural advance. `advance` is measured at `:2628`
   and then used only to size the box (`:2629`); it is never applied to the text.

2. **`DocxWriter.runXml` — `DocxWriter.java:4418-4420`.**
   `int half = halfPointsDown(run.sizePt);` then `<w:sz w:val="18"/>`.

3. **`DocxWriter.halfPointsDown` — `DocxWriter.java:6810-6813`.** `Math.floor(sizePt * 2f)`.
   9.2 → 9.0, 8.8 → 8.5, 8.9 → 8.5. The docstring defends this ("rounding down never makes the
   substitute face wider than the page's"), and that defence is about **tables wrapping**; on a
   one-line anchored box there is nothing to wrap, so the only effect is that every glyph is
   2.2–4.5 % narrower than the page drew it, and the error grows to the end of the line.

**The smallest structural condition that would gate a fix.** Not "does the block span" — all
three spanning elements that are ragged land within 0.34 pt. The condition is on the **line**,
and it is already computed in the engine:

> a line whose source advance `b.right - b.x` exceeds the natural advance of its runs at the
> emitted size, by more than the metric's own tolerance.

Two observable proxies, both in the model already:

* **flushness** — `b.right` equals the paragraph's widest line's right edge within ~0.5 pt and
  this is not the paragraph's last line → the page justified it. Measured discriminator, on
  `academic` p1: **32 flush lines drift -22.67 pt at their last word, 7 ragged paragraph-final
  lines drift -6.05 pt.** On `61`, which has **no** flush lines at all (0 flush, 23 ragged), every
  line drifts -6.88 pt — that document's whole defect is the size floor.
* **size** — `run.sizePt * 2` is not an integer, i.e. `halfPointsDown` lost something. That alone
  accounts for 90 % of `61`'s width deficit (glyphs -13.92 of -15.54 pt) and 29–40 % of the other
  three (glyphs -9.30 of -24.92 on `policy`, -9.39 of -32.63 on `academic` p1, -9.74 of -24.16 on
  `magazine`).

The rest — 60–71 % — is the missing word spacing: source median word gap **3.12 pt** on `policy`
against our **2.21 pt**, `academic` **2.72** against **2.05**, `magazine` **2.75** against
**2.20**, while `61`, which is not justified, reads **2.20** against **2.12**. So the fix is a
`w:w` character scale (or per-line `w:spacing`) on the runs of a flush line, computed as
`(b.right - b.x) / natural advance` and clamped; and either stop flooring the size for an
anchored line or fold the flooring into that same scale.

---

## What I ruled out, and the measurement that ruled it out

**Ruled out: font substitution / glyph advance widths.** This was the falsification the brief
named, and it is the one that had to be measured first. Width per em of the same words in both
renders (`(word.x1 - word.x0) / nominal size`, matched word by word):

| document | source size → our size | width/em src | width/em our | ratio |
|---|---|---|---|---|
| policy | 9.20 → 9.00 | 2.8320 | 2.8290 | **0.99894** |
| 61 | 8.80 → 8.50 | 2.8290 | 2.8260 | **0.99894** |
| academic | 8.90 → 8.50 | 2.8305 | 2.8216 | **0.99687** |
| magazine | 9.20 → 9.00 | 2.3610 | 2.3590 | **0.99915** |

The requested face is `Times New Roman`; LibreOffice substitutes `Liberation Serif`, which is
metric-compatible. **To within 0.1–0.3 % the advances are identical**, so the face is not the
cause — but the *size* the advances are multiplied by is, and that is a writer decision
(`halfPointsDown`), not a renderer one.

**Ruled out: a block-level horizontal placement error** (block emitted at a column x instead of
the content width). dx of every line origin: +0.08 … +0.16 pt. If a block had been emitted at a
column x, that number would be 19.8 pt on `policy` (the gutter is 287.75 → 307.56) or 34.6 pt on
`academic` (289.16 → 306.14). It is 0.15.

**Ruled out: a vertical error / wrong line pitch / inserted paragraph spacing.** dy median
-0.21 … +0.93 pt; 0 words with |dy| > 2 pt on three of the four documents; line pitch 12.9 pt
source and 12.9 pt ours on `policy`, 11.6 and 11.6 on `academic`.

**Ruled out: re-wrapping — the spanning block made column-width and split.** Line counts per
page are unchanged on three of the four (`policy` 61→61, `magazine` 43→43, `61` 39→39). Our
render of `academic` p1 has 76 lines to the source's 69, and the seven extra are the stacked
one-word boxes described under Q2 — a different, vertical, 3 pt defect.

**Ruled out: deletion.** Every source line is matched to one of ours on all four documents
(0 unmatched of 61/43/39/69/61).

**Ruled out: an engine path specific to two-column documents.** The same drift appears in the
single-column footer line (`policy`, `Nirvaan Packaging Industries · Human Resources`, dx_last
-4.54 pt) and in `policy`'s left column at y 349.61, which is 92 pt **above** the spanning
heading at y 441.54 — in a band the span does not open, on a page whose column detector
handled the span correctly.

---

## What would prove this conclusion wrong

1. **A justified line that lands.** If any flush-right line on these four documents had its last
   word within ~2 pt of the source, "justification is not carried" would be wrong. I found none:
   32/32 flush lines on `academic` p1 drift, median -22.67 pt.
2. **A width/em ratio far from 1.0.** If the substituted face's advances differed from the
   embedded font's by more than ~1 %, the mechanism would be font metrics and the writer would be
   innocent. Measured 0.9969–0.9992.
3. **A ragged, whole-half-point line that still drifts > 5 pt.** That would break the
   size-floor half of the story. The best candidate is `policy`'s `waived.` (9.2→9.0, ragged,
   one word): dx **+0.14 pt**.
4. **A spanning block whose dx0 is a column width.** All three ragged spanning elements are at
   +0.08 to +0.12 pt.
5. **Re-measurement at a different DPI.** The 5 px threshold is 2.4 pt; a 2.2 % deficit only
   crosses it on lines longer than ~110 pt, which is why these documents sit at 2–8 % rather than
   50 %. If the class were measured at 300 DPI, `61` would fall below the bar on the same render
   and the ranking would move without the engine changing. That is a property of the metric worth
   knowing, and it does not change the mechanism.

## Not claimed

I did not build or measure a fix. The two changes named under Q3 (`w:w`/`w:spacing` on a flush
line, and not flooring the size inside an anchored box) are unbuilt and unmeasured, and the commit
gate requires a whole-corpus pass in both formats before either could land. Nothing here says the
corpus would improve; it says where the ink goes and why.
