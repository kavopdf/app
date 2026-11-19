# content-partly-lost — the justified line, measured on this engine

Written by the fixer run of 19 Nov 16:11. **The change is implemented and screened but NOT
ratcheted**, so it is not kept. It lives in `patches/PATCH-justified-lines-spacing.patch`, which
applies cleanly to `d51faf8`/`30aecd9` (`git apply --check` passes) and is NOT applied in the tree.

## The mechanism, confirmed independently twice

A line the page **justified** is emitted **left-aligned**. The page spreads the line's inter-word
spaces and leaves the glyph advances alone; the writer puts the words down with the face's natural
space and stops, so the line ends short of its measure by exactly the width the page added, and every
word on it slides left by a share of that.

Confirmed by a background subagent (`content-partly-lost-SPAN-162250-a999.md`) on the four
two-column "spanning" documents, and again here by measurement on the source PDF:

    academic-paper-ieee-2col-abstract, page 2, body lines
      y=95.5   ext 243.8  natural 206.6  shortfall 37.2 pt
      y=107.1  ext 243.8  natural 228.4  shortfall 15.4 pt
      y=118.7  ext 243.8  natural 232.3  shortfall 11.5 pt
      y=130.3  ext 243.8  natural 225.7  shortfall 18.1 pt

The subagent also ruled out, with numbers: block placement (the spanning block lands within 0.16 pt
horizontally and 1.2 pt vertically — it was never the defect), vertical drift, re-wrapping, and font
metric incompatibility (width/em ratio 0.9969-0.9992).

## What was built, and the three things that cost a pass each

`PdfToWord`: `Box.stretchPt` / `Line.stretchPt` carry the measured shortfall;
`toParagraphs()` computes a per-page gap floor (3rd percentile of the page's inter-word gaps) and
`buildPara()` sets `box.stretchPt = stretchOf(line, gapFloor)`. `DocxWriter`: `stretchTw()` turns it
into `w:spacing` (character spacing, twips) emitted in `flowFromBox()` and `lineParagraph()`.

1. **A 0.06 em cap on the spacing truncated the fix** — 26 pt of missing measure over 45 characters is
   11 twips a character, and 0.06 em at 9 pt is exactly 11. The screen barely moved: 8.09 -> 6.54.
   The cap is now 0.30 em.
2. **A SPACE IS A GLYPH on most of this corpus.** Measuring the word gap as
   `next.x - (prev.x + prev.width)` counted nothing on any line of
   `academic-paper-ieee-2col-abstract`: its spaces are glyphs, so the gap between two glyph boxes is
   ~0 and every justified line reported `med=NaN`. Measured with `P2W_STRETCH_DEBUG`: 11 `nogaps`,
   39 `tight`, 0 accepted on that document. Measuring from the last **non-space** glyph's advance end
   to the next non-space glyph's start — which counts the space's own width — turned it into 56
   accepted lines.
3. The gap floor must be a **percentile, not a mean** — see `SPEC-justified-lines.md` §2.

## The measurement that exists (screen, 10 documents, this engine)

    policy-2col-spanning-section-heading     5.37 -> 1.76   -3.61
    academic-paper-ieee-2col-abstract        8.09 -> 5.02   -3.07
    magazine-2col-pullquote-spanning         3.49 -> 1.45   -2.04
    304_package_insert_small_print           3.41 -> 2.47   -0.94
    landscape-page-inside-portrait-document  1.45 -> 0.62   -0.83
    10 measured, 5 same, 5 better, 0 worse

**SCREEN PASS.** It is NOT a kept fix: the corpus ratchet was not run.

## What the next run must do

1. `git apply patches/PATCH-justified-lines-spacing.patch`; `bash tools/p2w-bench/build-engine.sh`
2. `screen.py --class "content-partly-lost"` — should reproduce 5 better, 0 worse.
3. **The corpus pass is the whole job**: `screen.py --docs "<every document in RANKING.csv>"` in
   about nine calls of ~4.5 minutes (22-24 documents per call, resumable), then write
   `benchmarks/RANKING.csv` and `benchmarks/STATE.json` from `screen-out/dist/*.json`.
   Measured this run: 46 of 213 in three calls before the run ended.
4. `scope.py` says **BOTH**, because the model classes changed. The `.txt` must therefore be
   re-scored too (`txt_gate.py --score`), or byte-identity of the `.txt` proved the way 411's was.
   Nothing in the patch reads `stretchPt` outside `DocxWriter`, so the `.txt` is *expected* to be
   byte-identical — that is a claim about the code, not a measurement.
5. `regress.py --check` then `--stamp`, then commit. There is no override.

## What is still weaker than the spec's own numbers

`SPEC-justified-lines.md` (the lost `855f443`) claims 8.09 -> 0.83 and 5.37 -> 0.01 with
`w:jc="distribute"` + a right indent. This implementation gets 5.02 and 1.76. The difference is
that `w:spacing` spreads the missing width over **every character**, while the page spent it at
**spaces** only. A version that splits each space into its own run carrying the spacing, or that
emits `w:jc="distribute"` with a right indent at the line's own ink edge, should close the rest.
Do not assume it will: measure it.
