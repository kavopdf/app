# Constant 12-twip `w:line`: patch, build and measurement

Repo: `https://github.com/kavopdf/app`, cloned to `/scratch/work/f15` at `29f89a6`.
Nothing committed, nothing pushed; the working tree is clean at the end (`git status --short` → empty).

Deliverables: `docxwriter-linebox.patch` (this folder) and this note.

---

## 0. Corrections, first

**0.1 The brief's items 2 and 3 cannot both hold, and the patch says which one gives.**
Item 3 wants `w:before = advance - 0.069*size` with `w:line = 12`. Item 2 wants
`before + line` to stay equal to the advance the fitter charged. Those two are
incompatible by `0.069*size - 0.6` twips-worth of points:

- Google reads the line box as `max((12/240)*r*size, 0.069*size)` = `0.069*size`.
- Word reads it as `12/20` = `0.6` pt.
- One emitted pair, two renderers, two different values for the same box. `before + line`
  can equal the advance for at most one of them.

I kept **Google exact** (it is the gated renderer) and kept the *charge* at the advance.
What the XML sums to is therefore `advance - (floorTw - 12)`, i.e. the **Word** height,
which is the true height for a Word reader. Concretely, on the 46-line probe page the
engine's own debug channel reports:

```
FLOW page=1 flowTw=16190 budgetTw=16838 overTw=-648 needTw=16190 writtenTw=15924 overheadTw=0 f=1.0
```

`flowTw` (what `fitPage` charged, and what Google will really advance) is 16190;
`writtenTw` (what `spacingTw` re-reads out of the XML) is 15924. The 266 twips / 13.3 pt
gap is exactly the Word-side shortfall summed down the page. The page guard's *primary*
number (`needTw`, which decides the squeeze) is unchanged; only its re-measurement of the
document is now the Word height. If you would rather have `spacingTw` agree and Google be
off by `0.069*size - 0.6` instead, it is a one-line change: `lineBox` returns
`{advanceTw - LINE_BOX_TW, LINE_BOX_TW}`. I did not do that, because it makes the gated
renderer wrong at every size.

**0.2 I introduced and then fixed a bug, and the fix is in the patch.**
My first cut scaled both terms by `ctx.squeeze` after `fitPage` had already scaled them.
That double-scaled the gap on any page the guard had to squeeze, and moved
`350_question_paper` by 4016 twips (200 pt of a one-page document). The committed patch
scales nothing: `advanceTw` is already the squeezed advance, and Google's floor is a
constant Google knows nothing about our squeeze. After the fix the same document moves
+87 twips (+4.35 pt) in total. The comment in the patch records this.

**0.3 `resync` is fed the charged pair, not the emitted pair.** `resync` is what carries
the flow's position down the sheet (`LINE_BASE` arithmetic on `before` and `line`), so
feeding it the 12-twip box would walk every later absolute gap up the page by
`0.069*size - 0.6` per line. It is called before the remap, with the pair whose sum is
the advance — the same number it saw before the patch.

**0.4 Not done: the other three sites are untouched.** See §2. The brief says "use it at
the flow site", so the column row (2602), the stamp text box (3653) and the table cell
(4419) still emit the old pair. A constant box for a table cell would be wrong anyway —
a cell's height is carried by `w:trHeight`, not by its line box.

---

## 1. What the current emission is

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, four `<w:spacing>` sites:

| line | site | what it writes |
|---|---|---|
| 2602 | `flowFromColumns` (a row of tab-stopped fields) | `before=beforeTw line=lineTw`, box = `flowLinePt` |
| 3065 | `flowFromBox` — **the flow site** | same |
| 3653 | the stamp's text box, per line | `before=before line=lpt[i]` |
| 4419 | the table cell | `before=0 line=rowLineTw` |

The flow site builds its box at 2950-2951 (`float linePt = flowLinePt(pitch, b.size, ctx.lastLinePt)`),
solves the gap at 3010-3031, hands both to `fitPage` at 3032, and writes
`beforeTw = fit[0]; lineTw = fit[1]` at 3049-3050. `linePt` is `1.15 * size` clamped to the
em (`LINE_FACTOR`, line 70) and solved against the page's own pitch, so the emitted pair is
`(pitch - 1.15*size, 1.15*size)` in the steady state: `before + line` is the pitch, and
`w:line` scales with the type.

Read back from the *unpatched* build of a page whose pitch I set to 1.2 em
(`python3 mkprobe.py`, 12/10/24 pt in Liberation Serif/Sans), `word/document.xml` holds:

```
('10', '230')   ('12', '276')   ('24', '552')   ('152','552')   ('849','230')   ('1219','276')
```

i.e. 12 pt → `before=12 w:line=276` (sum 288 tw = 14.40 pt, the pitch), 10 pt → `10/230`
(240 tw = 12.00 pt), 24 pt → `24/552` (576 tw = 28.80 pt).

---

## 2. The patch

`docxwriter-linebox.patch` — 75 insertions, 1 deletion, one file. Three hunks:

1. **Constants** after `LINE_BASE` (line 93): `LINE_BOX_TW = 12` and `GOOGLE_FLOOR = 0.069f`,
   with the derivation of the size-free floor test in the javadoc.
2. **The helper** `lineBox(int advanceTw, float size)`, placed above `resync`, returning
   `{advanceTw - round(0.069*size*20), 12}`.
3. **The flow site**: capture `advanceTw = beforeTw + lineTw` from what `fitPage` returned,
   call `resync` with that pair (unchanged behaviour), then replace `beforeTw`/`lineTw` with
   `lineBox(advanceTw, b.size)` for the emission.

The helper as written:

```java
private static int[] lineBox(int advanceTw, float size) {
    int floorTw = (int) Math.max(1L, Math.round(GOOGLE_FLOOR * size * TWIPS_PER_PT));
    return new int[]{Math.max(0, advanceTw - floorTw), LINE_BOX_TW};
}
```

The rule it implements, stated in the patch's javadoc: Google's advance is
`before + max((line/240)*r*size, 0.069*size)`; the box beats the floor only while
`line > 16.56/r`, and `16.56/12 = 1.38` is above every measured `r` (1.049 Courier,
1.2 Times metric family, 1.277 Liberation Serif). `w:line = 1.38*size` is inside the floor
only below `12/r` = 11.44 / 10.00 / 9.40 pt, so 12 pt body text falls outside it.

---

## 3. Does it compile

```
$ bash tools/p2w-bench/build-engine.sh
== no javac on this image, fetching a JDK ==
== fetching PDFBox-Android and its dependencies ==
== compiling stubs, engine and ConvertAll ==
Note: ../../app/src/main/java/com/kavopdf/app/engine/PdfEngine.java uses or overrides a deprecated API.
engine built - ConvertAll ready
```

Clean — warnings only, no errors, and `out/ConvertAll.class` exists. The patch also
applies to a pristine clone: `git apply --check docxwriter-linebox.patch` → exit 0,
`git apply --stat` → `1 file changed, 75 insertions(+), 1 deletion(-)`.
`verify_google.py` and `verify_txt.py` were not touched (`git status --short` lists only
`DocxWriter.java`, and the tree is clean now that it is reverted).

I did **not** run `tools/verify-engine.sh` (the 39-check behavioural suite). The brief
asked for the build, not the suite, and the patch is not being applied.

---

## 4. The emitted pair

Patched build, same probe, `word/document.xml`:

```
<w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="1478" w:after="0" w:line="12" w:lineRule="exact"/>
<w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="271"  w:after="0" w:line="12" w:lineRule="exact"/>
distinct (before, line): [(226, 12), (271, 12), (543, 12), (671, 12), (1065, 12), (1478, 12)]
```

Steady state, one pair per size, `w:line` constant:

| size | charged advance | emitted `w:before` | `w:line` | sum in XML | Google advance (computed) |
|---|---|---|---|---|---|
| 10 pt | 240 tw (12.00 pt) | 226 | 12 | 238 tw = 11.90 pt | 226/20 + 0.690 = **11.990** |
| 12 pt | 288 tw (14.40 pt) | 271 | 12 | 283 tw = 14.15 pt | 271/20 + 0.828 = **14.378** |
| 24 pt | 576 tw (28.80 pt) | 543 | 12 | 555 tw = 27.75 pt | 543/20 + 1.656 = **28.806** |

Google's column is computed from the measured formula, not rendered — see §5.
Residual against the charged advance is twip rounding of `w:before`: 0.010, 0.022, 0.006 pt.

Exactness sweep, sizes 8-48 pt in 0.5 pt steps × the three faces, Google's advance minus the
charged advance: **max |error| 0.025 pt**. Every size, every face.

---

## 5. The LibreOffice pitch, before and after

`python3 measure.py <docx> <outdir>` renders through `soffice --headless --convert-to pdf`
and reads span origins with PyMuPDF. The probe page's own pitch was verified first
(`mkprobe.py` prints the gaps it wrote: 14.4, 12.0, 28.8 exactly).

**Before** (unpatched build):

```
y=  72.001 size=12.00  Line 01 ...   gap 14.40 (x19)
y= 400.001 size=10.00  Line 01 ...   gap 12.00 (x19)
y= 660.001 size=24.00  Line 01 ...   gap 28.80 (x5)
modal pitch by size: {(12.0, 14.4): 19, (10.0, 12.0): 19, (24.0, 28.8): 5}
```

**After** (patched build):

```
y=  74.401 size=12.00  Line 01 ...   gaps 14.10 / 14.20 alternating
y= 397.101 size=10.00  Line 01 ...   gap 11.90
y= 657.301 size=24.00  Line 01 ...   gaps 27.80 / 27.70 alternating
modal pitch by size: {(12.0, 14.1): 10, (12.0, 14.2): 9, (10.0, 11.9): 19, (24.0, 27.8): 3, (24.0, 27.7): 2}
```

| size | pitch before | pitch after | delta | predicted `0.069*size - 0.6` |
|---|---|---|---|---|
| 10 pt | 12.00 | 11.90 | -0.10 | -0.09 |
| 12 pt | 14.40 | 14.10/14.20 | -0.20 to -0.30 | -0.23 |
| 24 pt | 28.80 | 27.70/27.80 | -1.00 to -1.10 | -1.06 |

The render quantises to 0.1 pt, which is why the 12 pt case alternates. The formula and the
render agree to the resolution of the instrument.

Two things I checked rather than assumed:

- **No clipping.** `w:lineRule="exact"` with a 0.6 pt box does not clip glyphs in
  LibreOffice: glyph bounding-box heights are `[(10.0,10.0),(12.0,12.0),(24.0,24.0)]` in
  both renders (identical), and the crops `crop-base.png` / `crop-pat.png` are both legible
  at 110 dpi. Whatever the Word-side cost is, it is not lost text.
- **`LINE_BASE` survives a 0.6 pt box.** `boxprobe.py` builds twelve one-paragraph files
  (zero margins, `w:before = 1000` tw, `w:line` either 12 or `1.15*size`) and measures where
  the baseline lands: `x/box` is 0.803, 0.804, 0.796, 0.798, 0.801, 0.801 for boxes of
  7.35-33.1 pt, and 0.501 pt (i.e. 0.8 of 0.6, inside the 0.1 pt resolution) at `w:line=12`
  for every size from 8 to 36 pt. So the engine's `LINE_BASE = 0.8` still describes the
  renderer, and the first-line displacement on the probe (+2.40 pt at 12 pt, -2.90 at 10 pt,
  -2.70 at 24 pt) is the *accumulated* shortfall of the lines above it, not a new artifact.

**Google's side is computed, not rendered.** Drive is unreachable from this sandbox, so
there is no Google export of anything here; the Google column in §4 is
`before/20 + max((12/240)*r*size, 0.069*size)` evaluated in Python from the measured
formula and the measured `r` values, on the pair this patch actually emitted. It is an
arithmetic prediction, not a render.

### Real documents, before and after

Three PDFs from `tools/engine-verify/real/pdfs/`, converted by both builds:

| document | paragraphs | Σ(`w:before`+`w:line`) before → after | page count | LibreOffice line count |
|---|---|---|---|---|
| `300_prescription_rx` | 99 → 99 | 24694 → 24681 (−13 tw, −0.65 pt) | 1 → 1 | 50 → 50 |
| `311_fir_police_form` | 140 → 140 | 31228 → 31239 (+11 tw, +0.55 pt) | 1 → 1 | 71 → 71 |
| `350_question_paper` | 122 → 122 | 37051 → 37138 (+87 tw, +4.35 pt) | 3 → 3 | 185 → 434 |

`w:line` becomes 12 on every flowed line; the surviving other values are the table row
(`2448`), the stamp boxes and the one-twip break carrier. The worst single-paragraph change
is −24 tw (−1.20 pt) on `300`, on a 26 pt line: exactly `floorTw - 12` = 36 − 12.

`350_question_paper` needs a caveat rather than a claim: both builds render it as 3 pages
from a 1-page source, and the *baseline* build's export yields 323 extractable words of the
source's 505 against the patched build's 677. Both renders are already wrong there for
reasons this patch does not touch, so I am not reading that as an improvement — only as
"no text-loss regression, page count unchanged".

---

## 6. The Word-side cost, stated

Per line, Word and LibreOffice come up **short by `0.069*size - 0.6` pt**:

| size | shortfall per line | over 40 lines |
|---|---|---|
| 8 pt | +0.05 (Word is *long* below 8.7 pt, where `0.069*size < 0.6`) | +2.0 |
| 10 pt | 0.09 | 3.6 |
| 12 pt | 0.23 | 9.1 |
| 24 pt | 1.06 | 42.2 |

Measured, not just computed: −0.10 / −0.23 / −1.05 pt on the probe (§5), and
`flowTw 16190` vs `writtenTw 15924` (13.3 pt over 46 lines) from the engine's own guard.

Google is the gated renderer. Word is unmeasured anywhere in this repo — there is no Word
render in `tools/p2w-bench`, and `verify_google.py` compares against a Google export, not a
Word one. So this trade is: exact on the renderer the gate scores, short by the numbers
above on the renderer nobody measures. If Word ever becomes gated, this patch is the thing
to revert, and the revert is deleting three hunks.

---

## 7. Confidence

- **Compiles, applies cleanly, emits `w:line = 12` with `w:before = advance - 0.069*size`** — high.
  Built from a clean clone, XML read back, pair matched against arithmetic for every line.
- **Google exact at every size and face** — high on the *arithmetic* (0.025 pt worst case over
  8-48 pt × 3 faces, computed from the emitted pairs), **unverified on Drive**: no Google
  export was produced or read here. If `0.069` or the `r` table is wrong, this conclusion
  falls with them, and nothing in this run would have caught that.
- **LibreOffice pitch after the patch** — high. Rendered, measured, and it matches the
  predicted shortfall to the 0.1 pt the render quantises to, at three sizes.
- **Behaviour on real documents** — medium. Three documents, spacing sums and page counts
  checked, nothing else. The 39-check suite was not run, so a ratchet regression is possible
  and unmeasured.
- **"`spacingTw` sees the same number it saw before"** — **false, and stated as false** in §0.1.
  The number that decides the squeeze is unchanged; the re-measurement of the written page is
  now the Word height, 266 tw lower on the probe page.

---

## 8. Evidence index

| claim | how |
|---|---|
| repo state | `git clone https://github.com/kavopdf/app f15`, HEAD `29f89a6`; `git status --short` empty at the end |
| the four sites | `sed -n '2602p;3065p;3653p;4419p' DocxWriter.java` → all four are the `w:line="` append of a `<w:spacing>` |
| baseline pairs | `unzip -p base/probe.docx word/document.xml` → `('12','276')`, `('10','230')`, `('24','552')` |
| patched pairs | same, `patched/probe.docx` → `(271,12)`, `(226,12)`, `(543,12)`, all `w:line=12` |
| compiles | `bash tools/p2w-bench/build-engine.sh` → `engine built - ConvertAll ready` |
| patch applies | `git apply --check docxwriter-linebox.patch` → exit 0 |
| LO pitch before/after | `python3 measure.py base/probe.docx lo-base` and `… patched/probe.docx lo-pat` |
| guard numbers | `java -Dp2w.debugFlow=1 … ConvertOne` → `flowTw=16190 … writtenTw=15924` |
| no clipping | span bbox heights identical in both renders; `crop-base.png` / `crop-pat.png` |
| `LINE_BASE` at 0.6 pt | `python3 boxprobe.py` → `x/box` 0.796-0.804 for 7.35-33.1 pt boxes, 0.501 pt at `w:line=12` |
| Google arithmetic | Python, `before/20 + max((12/240)*r*size, 0.069*size)`, sizes 8-48 pt × {1.049, 1.2, 1.277} |
| real docs | `java ConvertOne real/pdfs/*.pdf` on both builds; spacing sums and page counts above |
