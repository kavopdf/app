# The anchored-text-box census: the 120 pt cap is 16 % of it, and `ZERO_GAP_ANCHOR` is the rest

**24 Nov 2026, fixer slot 15:03.** A sub-agent instrumented a private copy of the engine to print, per
page, the `pageFits` result, the `spendGaps` state, which of the six `ctx.positioned = true` sites fired
first, the gap in points and every box `anchorBox()` wrote.

**Instrument validity first.** The instrumented build re-converted the whole corpus and produced
**byte-identical `word/document.xml` on 213 of 213** documents. Everything below is HEAD, not a variant.

## The size of the construct

| | |
|---|---:|
| corpus | 213 PDFs → 213 `.docx`, 563 pages, 7,588,002 non-space body characters |
| documents carrying `w:txbxContent` | **61** |
| anchored boxes | **1,037** |
| non-space characters inside boxes | **23,794** (0.31 % of body text) |

## Who enters `ctx.positioned`

**33 documents, 35 pages (6.2 % of 563).** No page enters the mode twice.

| first site to fire | pages | gap (pt) | `spendGaps` |
|---|---:|---|---|
| `flowFromBox/afterTable` | 1 | 123.08 | false |
| `flowFromBox/pitch` | 7 | 164.6 – 432.3 | false |
| `flowRow/afterTable` | 8 | 129.5 – 552.7 | false |
| `flowRow/pitch` | 7 | 128.0 – 309.3 | false |
| `flowFromBox/zeroGapAnchor` | 11 | 13.6 – 72.6 (a *miss*, not a wide gap) | 9 false, 2 true |
| `flowRow/zeroGapAnchor` | 1 | 24.4 | true |
| **total** | **35** | | |

**23 of 35 pages are the 120 pt cap** (every one `spendGaps = false`, gap 123–553 pt). **12 of 35 are the
`ZERO_GAP_ANCHOR` → `PAGE_POSITION_ON_ANCHOR` cascade** (miss ≥ `ZERO_GAP_FLOOR_PT` = 6 pt). Corpus-wide
53 pages are `pageFits = false`; only 35 become positioned, so `pageFits = false` is necessary and not
sufficient.

## The experiment: spend every gap (`ctx.spendGaps = true`, rebuilt, all 213 re-converted)

| | HEAD | spend-always |
|---|---:|---:|
| documents carrying `w:txbxContent` | 61 | 41 |
| boxes | 1,037 | 924 |
| non-space characters in boxes | **23,794** | **20,024** (−15.9 %) |
| pages entering `ctx.positioned` | 35 | 15 |
| page-count changes (soffice, all 23 changed documents) | — | **0** |

Page counts hold on all 23 changed documents, so pagination is not what refutes it. **Displacement is:**

| document | HEAD median / max | spend median / max |
|---|---|---|
| `330_cad_drawing_sheet` | 3.14 / 60.5 | **16.77** / 41.4 |
| `table-inside-two-column-page` | 5.37 / 9.17 | 5.37 / **92.01** |
| `newsletter-3col-header-footer` | 0.30 / 6.26 | 0.30 / **28.36** |
| `magazine-2col-pullquote-spanning` | 0.25 / 1.20 | 0.05 / 1.20 (better) |
| the other 19 | ≤ 0.51 median | unchanged to 0.02 pt |

**Mechanism:** on 28 of the 35 pages the gap is white space the page cannot afford (+0.4 % to +35.5 % over
the paper by the engine's own arithmetic). Written as `w:before` it enters the flow, the page exceeds its
budget, and the squeeze/`fitReserve` shave pulls the whole page up — that is exactly the 330 and
table-inside-two-column-page signature.

## What this overturns

**The brief's headline is wrong about where the box text is.** It says the 120 pt gap cap is "the largest
engine defect anyone has found, ~166 document-failures". The cap is real and exactly attributable — 23 of
35 positioned pages — but **spending every gap removes 3,770 of 23,794 box characters: 15.9 %.** The four
largest carriers are not cap-triggered at all:

| document | box characters | site |
|---|---:|---|
| `041122-Account_Opening_Form` (p3, p9) | 5,553 | `zeroGapAnchor` |
| `Account_Opening_Form_Fillable_filled` (p3, p9) | 5,553 | `zeroGapAnchor` |
| `policy-2col-spanning-section-heading` | 2,591 | `zeroGapAnchor` |
| `academic-paper-ieee-2col-abstract` | 2,505 | `zeroGapAnchor` |

**The prize is the `ZERO_GAP_ANCHOR` cascade, not the cap**, and it is a different guard with a different
fix. The cap's own pages carry 3,770 characters; the zero-gap pages carry the other 20,024.

`331_pid_diagram` (208), `400_comic_page_speech_bubbles` (28) and `65_two_col_full_width_figure_caption`
(532) keep boxes under any cap change because their text really is drawn inside outlines — `containerOf`'s
question, not this one.

## The candidate that is written but NOT measured

Charge the 12 pt table reserve only on a page that holds a table, so a page whose content fits is not
denied `spendGaps` by a reserve that does not apply to it. Compiled, never converted — **not a result**.

## Not established

- On `311_fir_police_form`, `323_credit_card_statement` and `353_admit_card` the re-evaluated `required`
  (792.8 / 808.8 / 813.7 pt) is below the paper, yet the engine's own `pageFits` returned false. The
  split of `pageFits` into `requiredPt` + comparison is therefore not bit-identical to the engine's
  decision on those three. **Unresolved** — the suspicion is that `page.blocks` differs at the two call
  sites.
- The Google side was not measured for any of this: the effect on `04_chars_missing` / `45_char_accuracy`
  is predicted from the character count, not re-verified in Docs.

## The cascade, measured on its own: `-Dp2w.pagepos=0` is worth 4,037 characters

`DOCS-ROOT-CAUSES-24NOV.md` recorded that disabling the cascade "moved the box count only 495 to 483, so
that flag is not the driver". That number is a **box count on a subset**, and it understates the flag by a
factor of five. Re-measured at HEAD this run, over all 213 documents, by reading `word/document.xml` out of
both builds:

| build | documents carrying `w:txbxContent` | boxes | non-space characters in boxes |
|---|---:|---:|---:|
| HEAD | 61 | 1,037 | 23,794 |
| `-Dp2w.pagepos=0` | 61 | 897 | **19,757** (−17.0 %, −4,037) |

Per document, HEAD → `pagepos=0`:

| document | boxes | characters |
|---|---|---|
| `041122-Account_Opening_Form` | 189 → 125 | 5,553 → **3,871** |
| `policy-2col-spanning-section-heading` | 62 → 60 | 2,591 → 2,488 |
| `academic-paper-ieee-2col-abstract` | 51 → 51 | 2,505 → 2,505 |
| `331_pid_diagram` | 25 → 25 | 225 → 225 |
| `27_two_column_left_short_txtpos` | 2 → 2 | 43 → 43 |

**The cascade is real (4,037 characters) and it is not sufficient:** the document count carrying boxes does
not move at all, 61 → 61. After the flow is resynced, the next line reaches its own negative gap and anchors
on its own, so the construct survives one line at a time. `041122` still keeps 3,871 characters in boxes.

**And the three flags do not compose into a fix.** cap-spend removes 3,770 characters (agent), the cascade
removes 4,037 (this measurement), and neither empties a single document. What the corpus needs is a
per-line rule: a line the flow cannot reach must be *written into the flow at the position the page drew*
- which is `w:before`, the construct `18_displacement`'s findings already proved Google honours 1:1 - not
an anchored box. Nothing in this run measured that, so it is a proposal, not a result.

## Method, so the next run can repeat it

    export PATH=/scratch/work/jdk/jdk-17.0.21.1+2/bin:$PATH
    CC_OUT=/scratch/work/p2w/out-pagepos0 \
      JAVA_TOOL_OPTIONS="-Dp2w.pagepos=0" python3 /scratch/work/cc2.py   # 213 docx in ~200 s, 6 shards
    # then count <w:txbxContent> characters in word/document.xml of each build

The HEAD build in `/scratch/work/p2w/out` was **not** overwritten: the variant writes to its own directory,
so both sides of the comparison exist at once.
