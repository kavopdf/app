# FINDING — how Google Docs charges `w:before` on a thin spacer paragraph before a table

**Run:** 22 Nov 2026, Google as sole renderer of record. 66 synthetic `.docx` probes, each
uploaded to Google Drive, converted to a Google Doc, exported back as PDF, and measured from
the PDF text layer with PyMuPDF. No LibreOffice measurement appears anywhere in this document.

## Headline

`w:before` on the spacer paragraph is charged **exactly `V/20` points — 1:1, with no floor, no
threshold, no cap and no scale factor**, over the whole tested range `V = 1 … 4320` twips
(0.05 pt … 216 pt). The largest deviation from `V/20` across 25 values is **0.000000 pt**, which is
the coordinate-read floor, not a real residual. A 6.4 pt gap is laid as 6.4 pt; a 6.2 pt gap is
laid as 6.2 pt; even a 0.05 pt gap is laid as 0.05 pt.

Two consequences that matter for the two real documents:

* `w:before` is **not** over-charging the small spacers. It is the first construct in this
  position that charges them correctly at all.
* The change from `w:line` to `w:before` **did** add a real, large amount of gap to those
  spacers: at 124 twips the charge went **1.3368 → 6.2000 pt (+4.8632)**, and at 128 twips
  **1.3799 → 6.4000 pt (+5.0201)**. That is exactly the size of the reported +2…+5 pt residual,
  and it is a *correction of an under-charge*, not the introduction of an over-charge.

## The fitted rule

For a spacer paragraph carrying `w:spacing w:before="V" w:line="1" w:lineRule="exact"`
(mark `w:sz=2`, with or without a run):

```
height_of_spacer_paragraph  =  V/20  +  L(V_line, s_mark)          [points]

  V/20                    =  the w:before charge, EXACTLY, for all V >= 1 twip
  L(1, sz=2)              =  0.1552 pt   (the paragraph's own line box; constant in V)
```

so the *change* between two documents that differ only in `V` is

```
delta_gap  =  (V2 - V1) / 20      pt        residual <= 0.00005 pt
```

and the *absolute* cost of the spacer paragraph (against a document with no spacer paragraph at
all) is `V/20 + 0.1552` pt.

## Measured table

Probe: one `ANCHOR` line → spacer paragraph → single-cell table containing `TBLMARK` → `AFTER`
line. Column *laid gap* is the `TBLMARK` text baseline minus the same baseline in the `V=0`
document, so page margins, the anchor line, the table's own cell metrics and every default
spacing cancel out. Column *abs h* is against a control document with **no spacer paragraph at
all** (`E0`), so it is the whole cost of the spacer paragraph.

| V (twips) | V/20 (pt) | laid gap (pt) | delta (pt) | abs h (pt) |
|---:|---:|---:|---:|---:|
| 0 | 0.00 | 0.0000 | 0.00000 | 0.1552 |
| 1 | 0.05 | 0.0500 | 0.00000 | 0.2052 |
| 2 | 0.10 | 0.1000 | 0.00000 | 0.2552 |
| 3 | 0.15 | 0.1500 | 0.00000 | 0.3052 |
| 4 | 0.20 | 0.2000 | 0.00000 | 0.3552 |
| 6 | 0.30 | 0.3000 | 0.00000 | 0.4552 |
| 8 | 0.40 | 0.4000 | 0.00000 | 0.5552 |
| 10 | 0.50 | 0.5000 | 0.00000 | 0.6552 |
| 20 | 1.00 | 1.0000 | 0.00000 | 1.1552 |
| 40 | 2.00 | 2.0000 | 0.00000 | 2.1552 |
| 60 | 3.00 | 3.0000 | 0.00000 | 3.1552 |
| 80 | 4.00 | 4.0000 | 0.00000 | 4.1552 |
| 100 | 5.00 | 5.0000 | 0.00000 | 5.1552 |
| 124 | 6.20 | 6.2000 | 0.00000 | 6.3552 |
| 128 | 6.40 | 6.4000 | 0.00000 | 6.5552 |
| 160 | 8.00 | 8.0000 | 0.00000 | 8.1552 |
| 200 | 10.00 | 10.0000 | 0.00000 | 10.1552 |
| 240 | 12.00 | 12.0000 | 0.00000 | 12.1552 |
| 320 | 16.00 | 16.0000 | 0.00000 | 16.1552 |
| 480 | 24.00 | 24.0000 | 0.00000 | 24.1552 |
| 720 | 36.00 | 36.0000 | 0.00000 | 36.1552 |
| 960 | 48.00 | 48.0000 | 0.00000 | 48.1552 |
| 1440 | 72.00 | 72.0000 | 0.00000 | 72.1552 |
| 2880 | 144.00 | 144.0000 | 0.00000 | 144.1552 |
| 4320 | 216.00 | 216.0000 | 0.00000 | 216.1552 |

Every laid gap is an exact multiple of 0.05 pt (one twip); every delta is zero to the printed
precision. `abs h - V/20 = 0.1552` for all 25 rows. The `delta` column is `laid gap - V/20`.

### Residuals

* Model `gap = V/20`: **max |residual| = 0.000000 pt** over 25 values of V (V = 1, 2, 3, 4, 6, 8, 10,
  20, 40, 60, 80, 100, 124, 128, 160, 200, 240, 320, 480, 720, 960, 1440, 2880, 4320 plus the
  V = 0 reference). RMS residual 0.00000.
* The rule has **no free parameters**: no intercept, no slope to fit. It is not a fit that
  happens to pass; it is an identity on the data.
* Repeatability: two probe documents were uploaded twice under different names. Both re-runs
  reproduced their first measurement **exactly** (`A_before0128` 100.1841 vs `R1` 100.1841;
  `A_before0000` 93.7841 vs `R2` 93.7841, difference 0.000000 pt).

## Run present vs run absent

Same spacer, one variant with a `<w:r>` holding a single space at `w:sz=2`, one with no run at
all (paragraph mark only). Five values of V:

| V | no run: `TBLMARK` y (pt) | with 1 pt run: `TBLMARK` y (pt) | difference |
|---:|---:|---:|---:|
| 0 | 93.7841 | 93.7841 | 0.000000 |
| 40 | 95.7841 | 95.7841 | 0.000000 |
| 128 | 100.1841 | 100.1841 | 0.000000 |
| 240 | 105.7841 | 105.7841 | 0.000000 |
| 960 | 141.7841 | 141.7841 | 0.000000 |

**The run makes no difference at all** — identical to the last digit of the PDF's coordinate
precision. Google renders a 2.25 pt space glyph in the spacer paragraph in both variants, so the
line box is the same whether the run is there or not.

## Does the 1 pt mark's own line box add a fixed offset? Yes — and it is 0.1552 pt

Control `E0` has no spacer paragraph at all (`TBLMARK` baseline 93.6289). `A_before0000` has the
spacer with `w:before="0" w:line="1" w:lineRule="exact"` (baseline 93.7841). The spacer
therefore costs **0.1552 pt of its own** with no `w:before` at all.

That offset is **constant in V** (see the `abs h - V/20` column above, 0.1552 in all 25 rows), so
it cancels in any delta between two spacers but it does **not** cancel against the page: a real
document pays `V/20 + 0.1552` pt, i.e. every spacer over-delivers by 0.16 pt. That is 30x smaller
than the ~5 pt effect being chased here, but it is real and one-sided (it always adds gap).

The line box depends on the mark size, not on `V`:

| `w:sz` | declared pt | effective pt in Google's PDF | h(`w:line=240`,exact) | h(`w:line=1`,exact) = floor | 0.06 x h(240) |
|---:|---:|---:|---:|---:|---:|
| 2 | 1.0 | 2.25 | 2.5873 | 0.1552 | 0.1552 |
| 4 | 2.0 | 2.25 | 2.5873 | 0.1552 | 0.1552 |
| 8 | 4.0 | 4.00 | 4.5996 | 0.2760 | 0.2760 |
| 20 | 10.0 | 10.00 | 11.4990 | 0.6899 | 0.6899 |
| 24 | 12.0 | 12.00 | 13.7988 | 0.8279 | 0.8279 |

Two things fall out of that table. `w:sz=2` (1 pt) and `w:sz=4` (2 pt) are both rendered at
**2.25 pt** — Google's importer clamps the tiny sizes up to 2.25 pt, which is why the mark's
line box is 2.587 pt and not 1.15 pt. And the `w:line=1` floor is exactly 6 % of the `w:line=240`
line box at every size, i.e. Google's minimum honoured line spacing for `lineRule="exact"` is
**6 % of single spacing = 14.4 twips**.

## The `w:line` construct, re-measured — the "~0.22x" claim is right in size and wrong in cause

`w:before="0"`, `w:line="L"`, `w:lineRule="exact"`, `w:sz=2`, no run:

| L (twips) | L/20 (pt asked) | laid h (pt) | h0 x max(L/240, 0.06) | residual | laid / asked |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.05 | 0.1552 | 0.1552 | -0.00004 | 3.1040 |
| 10 | 0.50 | 0.1552 | 0.1552 | -0.00004 | 0.3104 |
| 14 | 0.70 | 0.1552 | 0.1552 | -0.00004 | 0.2217 |
| 16 | 0.80 | 0.1725 | 0.1725 | 0.00001 | 0.2156 |
| 20 | 1.00 | 0.2156 | 0.2156 | -0.00001 | 0.2156 |
| 30 | 1.50 | 0.3234 | 0.3234 | -0.00001 | 0.2156 |
| 40 | 2.00 | 0.4312 | 0.4312 | -0.00001 | 0.2156 |
| 124 | 6.20 | 1.3368 | 1.3368 | 0.00004 | 0.2156 |
| 128 | 6.40 | 1.3799 | 1.3799 | 0.00002 | 0.2156 |
| 240 | 12.00 | 2.5873 | 2.5873 | 0.00002 | 0.2156 |
| 276 | 13.80 | 2.9754 | 2.9754 | 0.00003 | 0.2156 |
| 480 | 24.00 | 5.1746 | 5.1746 | 0.00004 | 0.2156 |
| 960 | 48.00 | 10.3491 | 10.3491 | -0.00002 | 0.2156 |
| 1440 | 72.00 | 15.5237 | 15.5237 | 0.00002 | 0.2156 |
| 2880 | 144.00 | 31.0474 | 31.0474 | 0.00004 | 0.2156 |

Fit: **`h = h0 * max(L/240, 0.06)` with `h0 = 1.1499 * s_eff = 2.5873 pt`** for the 1 pt mark
(`s_eff = 2.25 pt`). Max |residual| over the 15 points: **0.00004 pt**.

So Google does **not** apply a 0.22 scale factor to `w:line`. It reads `w:line` as a *multiple
of 240* — a number of "single lines" — and multiplies by **the paragraph mark's own single-line
height**, ignoring `lineRule="exact"` for the purpose of the magnitude. For a 1 pt mark that
line is 2.5873 pt, so one 240-twip unit buys 2.5873 pt instead of 12 pt. The observed ratio is
therefore `h0 / 12 = 0.2156` — **the repo's "~0.22x" number is confirmed**, and it is a
*face- and size-dependent constant*, not a Google fudge factor. The patch comment's claim that
"`w:line` is a multiple of the PARAGRAPH MARK's line height" is exactly right.

At the engine's real construct, `w:line=276` asked 13.8 pt and Google laid **2.9754 pt**
(ratio 0.2156). The 12 Nov note in the patch records 3.16 pt on a different document; same law,
slightly different document constant. Either way the table rose ~10 pt, as that run saw.

## Stacking and additivity

| probe | spacer paragraphs | abs h (pt) |
|:--|:--|---:|
| `E0` | none | 0.0000 |
| `G3` | `before=0`, `before=0` | 0.3105 |
| `G2` | `before=0`, `before=128` | 6.7105 |
| `G1` | `before=64`, `before=64` | 6.7105 |
| `A_before0128` | `before=128` | 6.5552 |
| `F1` | `before=128`, `w:line=240` exact | 8.9873 |

`G1` = `G2` to the last digit (6.7105): two 64-twip spacers cost exactly what one 128-twip
spacer costs. Each spacer paragraph contributes its own 0.1552 pt line box (`G3` = 2 x 0.1552 =
0.3105), and `w:before` adds on top of it linearly. A document that emits *n* spacer paragraphs
pays `n * 0.1552` pt of line box in total — which is why the engine's one-spacer-per-gap
construct is the cheap choice.

Also confirmed: `w:before` adds on top of the *natural* line box when `w:line` is absent or
`auto` — `F1` (`line=240` exact), `D3` (`line=240` auto) and `D4` (no `w:line`) all give
**8.9873 pt** = 6.4 + 2.5873. And `w:before=128` with a 10 pt mark (`D5`, `D6`) gives
**7.0899 pt** = 6.4 + 0.6899: the `w:before` charge is unchanged by the mark size.

## What this means for the two real documents

| spacer | declared | `w:line` charged | `w:before` charged | change |
|---:|---:|---:|---:|---:|
| 124 tw | 6.20 pt | 1.3368 pt | 6.2000 pt | **+4.8632 pt** |
| 128 tw | 6.40 pt | 1.3799 pt | 6.4000 pt | **+5.0201 pt** |

Both real spacers moved by ~5 pt, which brackets the reported +2…+5 pt residual on `mobile-bill`
(one 128 and one 124 twip spacer, so ~+9.9 pt total if both are on the same page). The
measurement says the new construct is **arithmetically correct**: 6.4 pt asked, 6.4 pt laid. So
the residual is *not* Google over-charging small `w:before`. The plausible readings, in order of
what this probe can support:

1. **The gap is now double-counted.** The old `w:line` construct was silently contributing
   ~1.38 pt of the ~6.4 pt the page needed; the other ~5 pt was coming from somewhere else in
   the flow (the table's top row grid, or a second element). Nothing in this probe rules that
   out, and it fits the finding-18 observation that a pitch error can be cancelling a position
   error.
2. the engine's `spacerTw` for these two spacers is larger than the drawn gap, so a correct 1:1
   charge now shows the engine's own arithmetic error;
3. the page's drawn gap really is 6.4 pt and the old build was simply wrong by ~5 pt there, in
   which case the +2…+5 residual is a *different* defect that the spacer change unmasked.

This probe cannot distinguish 1, 2 and 3 — it only establishes that the charge itself is 1:1 and
that the +5 pt is real, so the residual must be sought in the flow arithmetic, not in Google.

## Method — the exact calls

Build (local, no renderer involved):

```
python3 /scratch/work/build_all.py       # raw OOXML .docx, one per probe, into /scratch/work/docs
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
git -C /scratch/work/CS push origin HEAD:refs/heads/probe/gapcurve-1122
```

Google round trip — **two** Drive calls per probe, not the three in `TOOLBOX.md`, because
`GOOGLEDRIVE_UPLOAD_FROM_URL` can convert on the way in:

```
GOOGLEDRIVE_UPLOAD_FROM_URL(
    source_url = 'https://raw.githubusercontent.com/kavopdf/app/<sha>/tools/p2w-bench/gapcurve/<probe>.docx',
    name       = 'GC_<probe>',
    mime_type  = 'application/vnd.google-apps.document')     # <- upload + convert in one call
GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(
    fileId   = '<id from the upload>',
    mimeType = 'application/pdf')                            # -> /scratch/downloads/composio/<name>.pdf
```

The public `.docx` source is committed on branch `probe/gapcurve-1122` of `kavopdf/app`,
commits `5033e67` (batch 1), `bf1b35d` (batch 2), `055c905` (batch 3), `c95f9b2` (batch 4),
`fa074ad` (batch 5), under `tools/p2w-bench/gapcurve*/`. All 66 probe Google Docs were moved to
trash after scoring (`GOOGLEDRIVE_TRASH_FILE`); nothing else in Drive was touched.

Measure (`/scratch/work/measure.py`), PyMuPDF 2.1 / MuPDF 1.28.6:

```python
spans = [s for b in page.get_text('dict')['blocks'] for l in b['lines'] for s in l['spans']]
baseline = next(s['origin'][1] for s in spans if s['text'].strip() == 'TBLMARK')
```

### Precision and what cancels

* **No DPI.** The PDF text layer is vector; `span['origin'][1]` is a coordinate in points read
  from the content stream, not a rasterised pixel. Google writes 4 decimal places
  (e.g. `81.3799`), so the read floor is 0.00005 pt.
* **Layout quantisation is 1 twip = 0.05 pt.** Every measured delta is an exact multiple of
  0.05 pt (0.5, 1.0, 6.2, 6.4, 216.0 …), which is the real resolution of the experiment.
* **Repeatability is exact** (see above), so there is no run-to-run noise to average out.
* **Table borders were not used as the position reference.** Google snaps a table's top border
  to a 0.5 pt grid (measured border y values are all `x.5`), which would have hidden the
  0.05 pt quantisation. The in-cell text baseline does not snap and was used instead.
* **Everything else cancels.** All probes share page size, margins, `sectPr`, the `ANCHOR` line,
  the table's width/borders/cell margins/`trHeight`, and the `AFTER` line. Only the spacer
  paragraph differs, and every number above is a difference between two exports of that pair.
  Cross-check: the `AFTER` baseline moved by the same delta as the `TBLMARK` baseline in every
  document (agreement 0.0000 pt in 63 of 66, 0.0001 pt in the three 10 pt-mark controls), and
  `ANCHOR` sat at 81.3799 in all 66.

### Limits of this probe

* One face only: Arial. The `w:before` result is pure geometry (`V/20`) so it should be
  face-independent, and the patch comment says the same — but **that was not tested here**.
* One page size (US Letter), one margin set (1 in), one body size (10 pt), one table shape.
* Nothing here tests `w:before` on a paragraph that has real text in it, or `beforeAutospacing`,
  or `contextualSpacing`, or a spacer immediately before a *paragraph* rather than a table.
* The `w:line` law was measured with `lineRule="exact"` only; `auto` and `atLeast` were not
  swept.

## What would prove this wrong

Any one of these, reproduced through Google with the calls above, would falsify the fitted rule.

1. **A single `V` where the laid gap is not `V/20`.** The rule claims a floor of *zero*. Upload a
   spacer with `w:before="1"` (0.05 pt) and one with `w:before="4"` and find either laid as 0 —
   that would mean a sub-twip threshold exists and my `V=1` row (0.0500 pt) is wrong.
2. **A `w:before` charge that scales with the mark.** Set `w:sz=20` and `w:before="128"`; if the
   gap is not 6.4000 pt (my `D5` measured 6.4 + 0.6899 = 7.0899 total) the charge is coupled to
   the line box and the additive model collapses.
3. **A document whose spacer is the *first* body element**, or that sits after a page break. The
   rule is stated for a spacer in mid-flow; if `w:before` is swallowed at the top of a page or
   after a break (as Word does with `before` at a page top), a real document with a table at the
   top of a page would not follow the rule.
4. **A non-Arial face where the `w:line` constant is not `1.1499 * s_eff`.** That would not touch
   the `w:before` result, but it would break the claim that the "0.22x" is `h0/12` and make it a
   per-face accident instead of a law.
5. **A second `w:before` sweep run on a different day reproducing a different number.** The
   strongest evidence here is exact repeatability of duplicate uploads; if a later run of the
   *same* bytes disagreed by even 0.05 pt, the whole table would be a snapshot of one Drive
   conversion, not a property of Google.
6. **A real `mobile-bill`-style document where the two small spacers are charged 6.4 and 6.2 pt
   and the page is nevertheless correct.** That would mean my inference in "What this means for
   the two real documents" is backwards and the +2…+5 pt comes from a construct this probe never
   emitted.

