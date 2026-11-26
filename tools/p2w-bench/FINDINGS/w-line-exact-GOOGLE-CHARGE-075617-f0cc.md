# Google's exact charge for `w:line` + `lineRule="exact"`: **2.7466 x max(L/240, 0.06) pt**, not 2.5873

**26 Nov 2026, slot 07:56 IST.** Measurement only. No engine code touched, no file deleted, nothing
committed but this file. Every Google number below is a Google export, measured in the exported PDF.

## 0. The answer in one paragraph

Google lays an exact line box of `L` twips as

```
charge(L) = K x max(L/240, 0.06)   pt          K = 2.74663  (w:sz=2 mark, docDefaults Calibri)
```

with a hard floor at `L = 14.40 twips` and a **6.16 % larger coefficient than the number the tree
carries**. `2.5873` is not wrong arithmetic, it is the coefficient of a *different face*:
`2.5873 = 1.14991 x 2.25`, the Arial/Liberation-Sans ratio. The engine's spacer paragraph carries
**no `w:rFonts` at all** (checked on all 140 in the corpus), so Google substitutes the document
default Calibri -> Carlito at `r = 1.220709`, and the coefficient is `1.220709 x 2.25 = 2.74658`.
The *form* of the claimed law is exactly right -- linear in `L/240`, floored at `0.06`, with an
effective minimum size of `2.25 pt` -- and the delivered fraction of a declared gap is
`K/12 = 0.228886`, so a refused table spacer still puts everything below it high, by
**0.771114 x gap** (the 07:42 finding said 0.78: right mechanism, right sign, 1.2 % high on the
shortfall, 5.8 % low on the coefficient). `DocxWriter.java:6122-6136` is the right emitter and I
verified it: `:6122` is `boolean spendable`, `:6136` closes the refused arm. The engine emits
`lineRule="exact"` from **twelve** sites, not one, and the census below says how many of the 213
corpus documents each of them reaches.

## 1. Method

### 1.1 Why the measurement needs no assumption about where a baseline sits

A probe block is `marker A | n identical probe paragraphs | marker B`, each block on its own page.
Whatever fraction `f_i` of box `i` the baseline sits at, the advance from one baseline to the next
is `y_{i+1} - y_i = (1-f_i) H_i + f_{i+1} H_{i+1}`, and that telescopes:

```
y(B) - y(A) = (1-f_A) H_A + SUM(n probe boxes) + f_B H_B
```

so with the same markers in every block, `H_probe = (Delta(n) - Delta(0)) / n`, where `Delta(0)` is
the same block with `n = 0`. No baseline model, no line-height model, no assumed descent: `f` and
the marker boxes cancel **exactly**. Measured `Delta(0)` across the four control blocks of probe A:
13.4278, 13.4278, 13.4278, 13.4258 pt (spread 0.0020); across probes B and C: 13.4278 twice, spread
0.0000.

That control is also an independent calibration: the marker is 11 pt Calibri on `w:line="240"
w:lineRule="auto"`, and `13.4278 / 11 = 1.220709` -- the substituted face's line height, measured
without being asked for.

### 1.2 The probe paragraph is the engine's, byte for byte

```
<w:p><w:pPr><w:snapToGrid w:val="0"/>
  <w:spacing w:beforeAutospacing="0" w:afterAutospacing="0" w:before="0" w:after="0"
             w:line="L" w:lineRule="exact"/>
  <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>
```

(no runs, `sz=2` on the mark -- identical to `DocxWriter.java:6133-6136`). `word/styles.xml` is the
engine's own `stylesXml()` copied verbatim, so `docDefaults` is `Calibri` / `w:sz=22` /
`w:spacing w:after=120`, exactly as every corpus document is written.

### 1.3 The Drive route, and one step that is not possible from here

`GOOGLEDRIVE_CREATE_FILE(file_to_upload={s3key: <a /scratch path>})` is **refused**: *"The file key
does not belong to this project or session"* (Apollo 403). This sandbox has no `upload` tool to mint
an `s3key`. What works -- and what `gh-to-drive.py` in this tree already documents -- is a temporary
public release asset plus `GOOGLEDRIVE_UPLOAD_FROM_URL(..., mime_type="application/vnd.google-apps.document")`,
which converts to a Google Doc on the way in. Three probe documents went up that way, each exported
to PDF with `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE`, and all three were deleted afterwards
(section 11). Every number below is from those exports, not from LibreOffice.

LibreOffice was run on the same three files first, as a control on the *method*: it returns
`L/20` exactly at every one of the 19 values of `L` and every size (0.05 pt at L=1, 300.00 pt at
L=6000), which is what "exact" means to it and confirms the instrument measures the quantity it
claims to. **No LibreOffice number is used as a Google number anywhere in this file.**

## 2. The measured law

```
charge(L, sz, face) = r_face x max(size_pt, 2.25) x max(L/240, 0.06)   pt
```

* `r_face` -- the substituted face's line height in em: **Calibri 1.220709** (default),
  Arial 1.14991, Times New Roman 1.14991, Courier New 1.13281 (all measured, table 5).
* `size_pt` -- the size of the paragraph mark (`w:sz`/2), floored at **2.25 pt** (table 4).
* `max(L/240, 0.06)` -- a multiple of that line height, floored at **0.06 of it** (tables 2, 3).
* `w:before` is charged **exactly**, `before/20` pt, and adds to the above (table 6).
* `w:line="0"` is **not** zero: it is charged as one full line (2.7466 pt at sz=2), i.e. Google
  reads it as "not set", so a zero box cannot be written this way.

For the engine's construct (`sz=2`, no `rFonts`), the whole law is one number:

```
charge(L) = 2.74663 x max(L/240, 0.06) pt          (2.74658 .. 2.74666 across the sweep)
```

## 3. The probe: 19 values of L, `sz=2`, empty paragraph, `before=0`

Least squares through the origin over the 17 points at `L >= 15`: **K = 2.74663**; per-point
`H/(L/240)` spans 2.74658 .. 2.74666. Google's measured charge is the 4th column; the claim is the
5th; the last two columns are this file's law and its residual.

| declared L (twips) | declared L/20 (pt) | Google measured (pt) | predicted by 2.5873 x max(L/240,0.06) | residual | residual % | measured law 2.74663 x max(L/240,0.06) | residual |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.05 | 0.1648 | 0.1552 | +0.0096 | +6.16% | 0.1648 | +0.0000 |
| 8 | 0.40 | 0.1648 | 0.1552 | +0.0096 | +6.16% | 0.1648 | +0.0000 |
| 20 | 1.00 | 0.2289 | 0.2156 | +0.0133 | +6.16% | 0.2289 | +0.0000 |
| 60 | 3.00 | 0.6866 | 0.6468 | +0.0398 | +6.16% | 0.6867 | -0.0000 |
| 120 | 6.00 | 1.3733 | 1.2936 | +0.0797 | +6.16% | 1.3733 | -0.0000 |
| 180 | 9.00 | 2.0600 | 1.9405 | +0.1195 | +6.16% | 2.0600 | -0.0000 |
| 240 | 12.00 | 2.7466 | 2.5873 | +0.1593 | +6.16% | 2.7466 | -0.0000 |
| 300 | 15.00 | 3.4332 | 3.2341 | +0.1991 | +6.16% | 3.4333 | -0.0001 |
| 360 | 18.00 | 4.1199 | 3.8809 | +0.2389 | +6.16% | 4.1199 | -0.0001 |
| 480 | 24.00 | 5.4932 | 5.1746 | +0.3186 | +6.16% | 5.4933 | -0.0001 |
| 600 | 30.00 | 6.8665 | 6.4682 | +0.3982 | +6.16% | 6.8666 | -0.0001 |
| 720 | 36.00 | 8.2397 | 7.7619 | +0.4778 | +6.16% | 8.2399 | -0.0001 |
| 960 | 48.00 | 10.9864 | 10.3492 | +0.6372 | +6.16% | 10.9865 | -0.0001 |
| 1200 | 60.00 | 13.7330 | 12.9365 | +0.7965 | +6.16% | 13.7332 | -0.0001 |
| 1800 | 90.00 | 20.5997 | 19.4047 | +1.1950 | +6.16% | 20.5997 | -0.0000 |
| 2400 | 120.00 | 27.4663 | 25.8730 | +1.5933 | +6.16% | 27.4663 | -0.0000 |
| 3600 | 180.00 | 41.1994 | 38.8095 | +2.3899 | +6.16% | 41.1994 | -0.0000 |
| 4800 | 240.00 | 54.9321 | 51.7460 | +3.1861 | +6.16% | 54.9326 | -0.0005 |
| 6000 | 300.00 | 68.6665 | 64.6825 | +3.9840 | +6.16% | 68.6658 | +0.0007 |

The claimed formula is wrong by the **same relative amount at every point**, which is the signature
of a wrong constant and not of a wrong shape: `1.220709 / 1.14991 = 1.06157`.

## 4. Where 2.5873 comes from -- it is the Arial coefficient, and the spacer has no face

The tree's cell-paragraph law (`FINDINGS/18_displacement-RESIDUAL-2.5PT-ARITHMETIC-0355-fixer.md`
section 2) is `before + max((L/240) x 1.1499 x size, 0.069 x size)`. Take that law, apply it to an
`sz=2` mark with a 2.25 pt effective size, and it gives exactly the number in the in-tree comment:

```
1.1499 x 2.25 = 2.587275   ->  2.5873     and    0.06 x 2.5873 = 0.1552
```

Both of those appear verbatim at `DocxWriter.java:6101-6105` (0.2156 pt at L=20, 0.1552 pt at L=1).
The constant was carried across from a **cell** paragraph, whose runs name a face, to the **table
spacer**, which names none. Measured on the 213 corpus `.docx`: all **140** paragraphs of the
refused-spacer signature carry `w:rPr><w:sz w:val="2"/>` and **no `w:rFonts`**, so the substituted
face is `docDefaults` -> Calibri -> Carlito, `r = 1.220709`, `K = 2.74658`. That is the whole 6.16 %.

The 07:42 finding's one corroborating point outside the corpus, the TOPB variant of
`FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md` (`w:line="1103"`, `sz=2`, Google
y = 12.22), reads 11.89 pt in that file's text. This law gives 12.62 pt. I cannot reconcile that
single point -- that probe's `styles.xml` was not preserved in the tree, and its y is a marker
position with `w:pgMar` all zeros, not a telescoped block -- so I am naming the disagreement rather
than fitting it. The 19-point sweep above is a controlled measurement in a document whose
`docDefaults` I copied from the engine; the TOPB point is one number whose face is not recorded.

## 5. The floor, the knee, and the size clamp

### Table 2 -- where the floor stops binding (`sz=2`)

| L | Google (pt) | law | residual |
|---:|---:|---:|---:|
| 0 | 2.7466 | (0.1648 if floored) | **+2.5818 -- `w:line="0"` is charged as a full line, not zero** |
| 10 | 0.1648 | 0.1648 | -0.0000 |
| 12 | 0.1648 | 0.1648 | -0.0000 |
| 13 | 0.1648 | 0.1648 | -0.0000 |
| 14 | 0.1648 | 0.1648 | -0.0000 |
| 15 | 0.1717 | 0.1717 | -0.0000 |
| 16 | 0.1831 | 0.1831 | -0.0000 |
| 18 | 0.2060 | 0.2060 | -0.0000 |
| 24 | 0.2747 | 0.2747 | -0.0000 |

The floor is flat through `L = 14` and linear from `L = 15`. `floor / K = 0.16480 / 2.74663 = 0.060000`
and the knee is `240 x 0.06 = 14.40` twips: the floor is exactly `0.06` of the line height, as the
claim says.

### Table 3 -- the floor at three sizes (L=1)

| size | Google (pt) | `0.06 x r x max(size,2.25)` | residual |
|---:|---:|---:|---:|
| 1.0 pt (sz=2) | 0.1648 | 0.1648 | +0.0000 |
| 10.0 pt (sz=20) | 0.7324 | 0.7324 | -0.0000 |
| 22.0 pt (sz=44) | 1.6113 | 1.6113 | -0.0000 |

### Table 4 -- size dependence, and a minimum SIZE of 2.25 pt (not a minimum line height)

| w:sz | size (pt) | L | Google (pt) | law | residual |
|---:|---:|---:|---:|---:|---:|
| 4 | 2.0 | 240 | 2.7466 | 2.7466 | +0.0000 |
| 4 | 2.0 | 1200 | 13.7330 | 13.7330 | +0.0001 |
| 5 | 2.5 | 240 | 3.0518 | 3.0518 | -0.0000 |
| 5 | 2.5 | 1200 | 15.2588 | 15.2589 | -0.0001 |
| 6 | 3.0 | 240 | 3.6621 | 3.6621 | -0.0000 |
| 6 | 3.0 | 1200 | 18.3105 | 18.3106 | -0.0001 |
| 7 | 3.5 | 240 | 4.2725 | 4.2725 | -0.0000 |
| 7 | 3.5 | 1200 | 21.3623 | 21.3624 | -0.0001 |
| 8 | 4.0 | 240 | 4.8828 | 4.8828 | -0.0000 |
| 8 | 4.0 | 1200 | 24.4141 | 24.4142 | -0.0001 |
| 20 | 10.0 | 240 | 12.2070 | 12.2071 | -0.0000 |
| 20 | 10.0 | 1200 | 61.0352 | 61.0355 | -0.0002 |
| 44 | 22.0 | 240 | 26.8555 | 26.8556 | -0.0001 |
| 44 | 22.0 | 1200 | 134.2775 | 134.2780 | -0.0005 |

`sz=2` (1 pt) and `sz=4` (2 pt) charge the **same** coefficient, 2.7466. `sz=5` (2.5 pt) does not:
it charges 3.0518 = 1.220709 x 2.5. So the clamp is on the **size**, at **2.25 pt**
(2.74663 / 1.220709 = 2.2500), not on the line height -- a minimum line height would have made
`sz=5` read 2.7466 too. Above 2.25 pt the charge is linear in the size, `r x size x max(L/240,0.06)`.

### Table 5 -- the face (`sz=20`, 10 pt), which is where the claimed constant came from

| face named on the run | L | Google (pt) | implied r | implied `r x 2.25` |
|---|---:|---:|---:|---:|
| Arial | 240 | 11.4991 | 1.14991 | **2.5873** |
| Arial | 1200 | 57.4953 | 1.14991 | **2.5873** |
| Times New Roman | 240 | 11.4991 | 1.14991 | **2.5873** |
| Times New Roman | 1200 | 57.4953 | 1.14991 | **2.5873** |
| Courier New | 240 | 11.3281 | 1.13281 | 2.5488 |
| Courier New | 1200 | 56.6406 | 1.13281 | 2.5488 |
| (no rFonts: Calibri) | 240 | 12.2070 | 1.220709 | **2.7466** |
| (no rFonts: Calibri) | 1200 | 61.0352 | 1.220709 | **2.7466** |

Arial and Times New Roman land on `1.14991`, and `1.14991 x 2.25` is `2.5873` to four decimals.
That is the number in the tree, and it is right for any paragraph whose runs name Arial or Times --
including the cell boxes -- and wrong for the spacer, which names nothing.

### Table 6 -- `w:before` is exact and additive (probe C, `sz=2`)

| block | before (tw) | L | Google advance (pt) |
|---|---:|---:|---:|
| X1 | 0 | 600 | 6.8664 |
| X2 | 240 | 600 | 18.8664 |
| X3 | 240 | 1 | 12.1648 |
| X4 | 1000 | 2880 | 82.9590 |
| X5 | 1 | 1 | 0.2148 |

`X2 - X1 = 12.0000` for 240 twips; `X3 - floor = 12.0000`; `X5 - floor = 0.0500` for a single
twip; `X4 - 50.00 = 32.9590` against `K x 2880/240 = 32.9596`. `w:before` has no floor and no
snapping, and the two charges add.

## 6. Verdict on the claimed formula

**The form holds exactly, everywhere, over the whole range measured (L = 1 .. 6000 twips, sizes
1 .. 22 pt, four faces). The constant does not.**

* Holds: `charge = C x max(L/240, 0.06)`, with a flat floor below `L = 14.40` and exact linearity
  above it. Residual against the measured law is `<= 0.0007 pt` at every one of the 19 points.
* Fails: `C`. The claimed `2.5873` is 5.80 % low. Measured `2.74663` for the construct the engine
  actually writes. The claimed formula's residual against Google is `+6.16 %` at *every* point --
  it never crosses zero, so it is not a fit that is good in places and bad in others.
* Consequence for the 07:42 finding: a declared gap `G = L/20` is delivered as
  `0.228886 x G`, so everything below a refused spacer sits high by **0.771114 x G**, not
  `0.784 x G`. The mechanism, the sign, the step-not-drift character and the "one signed constant"
  reading are all **confirmed**; the constant is 1.2 % smaller than stated.

Corroboration from the corpus, with the caveat that it cannot settle the constant: the step the
07:42 finding measured is a table's *whole* geometry, not the spacer alone. My model's spacer term
for `68_journal_wide_table_spanning` (gap 144 pt) is -111.04 pt against the measured -115.09;
`403_crossword_puzzle` (gap 58.15 pt) is -44.84 against -42.99. The old constant predicts -112.32
and -45.36 on the same two documents. Both constants sit inside the scatter of those two steps, so
the probe decides it and the corpus does not.

## 7. The inverse: what L to emit for a gap of G points

```
L = 240 x G / K = 87.3797 x G   twips          (sz=2, no rFonts, docDefaults Calibri)
L = round(87.3797 x G)                         for an integer w:line
```

and, for any other mark size or face,

```
L = 240 x G / (r_face x max(size_pt, 2.25))
```

| desired Google charge G (pt) | L to emit (twips) | delivered (pt) | residual (pt) |
|---:|---:|---:|---:|
| 0.1648 (= the floor) | 14 | 0.1648 | 0.0000 |
| 0.50 | 44 | 0.5035 | +0.0035 |
| 1.00 | 87 | 0.9957 | -0.0043 |
| 2.00 | 175 | 2.0028 | +0.0028 |
| 4.00 | 350 | 4.0055 | +0.0055 |
| 6.35 | 555 | 6.3516 | +0.0016 |
| 12.35 | 1079 | 12.3484 | -0.0016 |
| 18.30 | 1599 | 18.2994 | -0.0006 |
| 58.15 | 5081 | 58.1484 | -0.0016 |
| 144.00 | 12583 | 144.0035 | +0.0035 |

Three constraints the fixer must carry with it:

1. **There is no `L` that delivers less than 0.1648 pt.** Below the floor every `L <= 14` charges
   the same 0.1648 pt, so a gap smaller than that cannot be written as `w:line` at all. The
   integer rounding residual is at most `K/480 = 0.0057 pt`.
2. **`w:line="0"` is a full line (2.7466 pt), not an empty box.** A zero-height exact line cannot be
   written; use `w:before` (which is exact and has no floor) for anything below 0.1648 pt.
3. **`w:line` cannot be made to agree with LibreOffice and Google at the same time, except in the
   floor.** Solving `before + L/20 = G` (what Word and LibreOffice lay) together with
   `before/20 + K x max(L/240,0.06) = G` (what Google lays) gives
   `K x max(L/240, 0.06) = L/20`, whose only solution is inside the floor:
   `L* = 20 x K x 0.06 = 1.2 x K = 3.296` twips -> `L = 3`, delivering 0.1648 pt in Google against
   0.15 pt in LibreOffice (0.0148 pt apart). Any `L` above 14.4 is charged 22.888 % by Google while
   LibreOffice charges 100 %. So the only joint-safe recipe for a gap is
   `w:before = 20G - 3`, `w:line = 3`: Google gets `G - 0.15 + 0.1648`, LibreOffice gets `G`.

## 8. Every place the engine emits `lineRule="exact"`

Twelve emission sites in one file, `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`. The
grep that finds them is `grep -n 'lineRule' ... | grep exact` -- a plain
`grep 'w:lineRule="exact"'` misses every one of them, because the Java source writes
`w:lineRule=\"exact\"` and the first grep I ran returned only comments. `:6122-6136`, the reference
the 07:42 finding gives, is **correct**: `:6122` is `boolean spendable`, `:6130` closes the spend arm
and `:6136` closes the refused arm.

`-Dp2w.lineRule=auto|autoflow` (`:135`) replaces sites 1 and 2 with `w:lineRule="auto"`; the census
below is the default (HEAD) mode.

| # | file:line | construct | `w:line` written | charge vs declared (Google) | documents | instances |
|---|---|---|---:|---|---:|---:|
| 1 | `DocxWriter.java:152-153` (`spacing()`, called at `:3787` tabbed flow line and `:4638` flow line) | every flow line, as a hairline | `1.38 x size` twips | median +0.040 pt per line at Calibri, 0 at Arial/Times (the floor is `0.06 x r`, and `0.069 = 0.06 x 1.1499`) | **199** | 3813 |
| 2 | `:6917` and `:7207` (`spacing()` for cells; `cellParaXml` at `:7214`) | table-cell box, one per cell paragraph | `paraBoxTw` (a hairline, 1 .. 12 tw in practice) | median 0.017 pt; worst -7.71 (a declared 10.5 pt box charged 9.6) | **136** | 11846 |
| 3 | `:6125-6130` | **table-top spacer, SPEND arm** (`before=wantTw`, `line=min(1,spacerTw)`, `sz=2`) | 1 | +0.1148 pt each (0.1648 laid, 0.05 declared) | **76** | 1541 |
| 4 | `:6133-6136` | **table-top spacer, REFUSED arm** (`before=0`, whole gap in `w:line`, `sz=2`) | `spacerTw` | **-2.24 .. -111.04 pt each; median -9.95** -- 22.888 % of the gap delivered | **54** | 128 |
| 5 | `:2934` (`SHAPE_PARA_PPR`), `:2625` (`anchoredPicture`), `:5651` (`anchorShape`) | anchored shape / picture carrier paragraph | 1 | +0.1148 pt each | **186** | 1109 |
| 6 | `:7036-7037` | post-table carrier paragraph (`POST_TABLE_TW = 80` at `:7246`, `_STACKED = 1` at `:7255`) | 80 (4 pt) or 1 | **-3.0845 pt each** (0.9155 laid for 4.00 declared) | **10** | 390 |
| 7 | `:3818-3819` (`lineParagraph`), `:5409-5410` (text-box inner line) | a line inside a text box / drawn line | `1.15 x size` | median 2.05 pt; worst **+28.04** (`08_two_overlapping_stamps`, 22 pt run: declared 25.30, charged 53.34) | **37** | 519 |
| 8 | `:692` (`breakPage`), `:1135` (empty-page carrier) | page-break carrier | 1 | +0.1148 pt (irrelevant: the page ends there) | **20** | 348 |
| 9 | `:1115` | section-close paragraph (`w:sectPr` + `nextPage`) | 1 | +0.1148 pt | (2) | 3 |
| 10 | `:2256` | empty table-cell filler (`sz=2`, line 1) | 1 | +0.1148 pt each | **9** | 17 |
| 11 | `:7207` with a 1-twip box and no run | empty cell paragraph, hairline box (`pStyle TableText`, so 10 pt) | 1 | **+0.6824 pt each** (0.7324 laid for 0.05 declared) | **46** | 967 |
| 12 | `:3787`/`:4638`/`:7207` at `size <= 1 pt` | the flow-line / cell-box construct at the smallest type: `sz=2` mark, 1-twip box, text in a 1 pt run | 1 | +0.1148 pt each (0.1648 laid for 0.05 declared) | **15** | 74 |

**How the count was made.** All 213 `.docx` were downloaded from the Drive corpus folder
`1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA` (213 distinct names; the folder also holds 215 duplicate
revisions, deduped by newest `modifiedTime`), `word/document.xml` was parsed, and every paragraph
carrying `w:lineRule="exact"` was classified by the XML signature the emitter writes -- `w:sz=2` on
the mark, `w:line=1` / `=80` / `>1`, `w:before` zero or not, a `w:drawing` or `w:br` in the
paragraph, and whether the paragraph sits inside a `w:tbl`/`w:tc` or a `w:txbxContent` (depth
tracked over the whole document). "Documents" is the number of the 213 containing at least one
instance. **202 of the 213 documents carry at least one `lineRule="exact"` paragraph** (the 11 that
carry none are image-only pages), and the constructs that can move a page are 4, 6, 7 and 11.

**What that last column does and does not mean.** It is presence, not effect. A cell box's charge
is mostly absorbed by the row height the engine writes, so the -225.84 pt sum on
`041122-Account_Opening_Form` does not appear as a 225 pt shift; the refused spacer and the
post-table carrier are different, because a spacer *is* the gap and a post-table carrier *is* the
space under a table. The per-document sums of construct 4 run -2.24 to -524.59 pt
(`041122-Account_Opening_Form`, 21 spacers), median -17.58; construct 6 is a flat -3.0845 pt per
table; construct 11 is a flat +0.6824 pt per empty cell paragraph (+117.38 pt on that same
document, 172 of them); construct 7 is a median 2.05 pt per text-box line. Construct 6 has never
been looked at at all -- 10 documents, 390 tables, 3.08 pt each -- and construct 7 grows
quadratically with the type size, so it is the one to check on any document whose text boxes carry
large type.

## 9. What would prove me wrong

1. **A probe document whose `docDefaults` names a face other than Calibri.** My whole coefficient
   rests on the spacer having no `w:rFonts` and the document default being Calibri. Table 5 shows
   the charge follows the named face by 6.16 % between Calibri and Arial; if Google actually
   resolves a faceless `sz=2` mark to something other than the document default, the number moves
   and my `K` is a property of this `styles.xml`, not of the construct. One probe with
   `docDefaults` = `Times New Roman` and the same `sz=2` spacer would settle it in one number:
   it must read 2.5873 if I am right.
2. **A re-run of the TOPB probe with its `styles.xml` preserved.** That file records 11.89 pt for
   `w:line="1103"` on an `sz=2` mark; this law says 12.62 pt. If 11.89 reproduces in a document
   whose defaults are Calibri, my coefficient is 6 % high and the tree's is right.
3. **A Google export in which a refused spacer's step is measured with the table removed.** The
   doc-level steps in the corpus (115.09, -42.99, -7.62 ...) include the table's own geometry and
   cannot separate the two constants; a spacer with no table under it can.
4. **Any evidence that Google reads `w:line` as a fraction of the *run's* size rather than the
   mark's.** Table 4 was built with the size on the mark and no runs. A block with a 10 pt run in a
   `sz=2` paragraph would show whether the box follows the mark (this law) or the largest run.
5. **A second export of the same probe on another day.** All three probes agree with themselves to
   0.0007 pt; if Google changed its line model, one re-export would show it.

## 10. Provenance of every number

* The law, `K = 2.74663`, the floor, the knee, the 2.25 pt clamp, the face ratios, the `before`
  additivity: three hand-built probe `.docx` (`/scratch/work/probe/wline_probe*.docx`), uploaded to
  Drive as Google Docs, exported to PDF by `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE`, and measured
  with PyMuPDF span origins in `/scratch/work/measure.py` and `measure2.py`
  (`/scratch/work/probe/measured*.json`).
* The control `Delta(0) = 13.4278 pt` and `r = 1.220709`: the marker paragraphs of the same probes.
* The 213-document census: `/scratch/work/census.py` and `/scratch/work/leverage.py` over the
  `word/document.xml` of all 213 downloaded `.docx` (`/scratch/work/probe/census.json`,
  `leverage.json`).
* `DocxWriter.java` line numbers: read from the file at the commit this finding is written against.
* The LibreOffice numbers quoted in section 1.3 (L/20 exactly at all 19 values): the same three
  `.docx` through `soffice --headless --convert-to pdf`. They are a control on the instrument and
  are labelled as LibreOffice wherever they appear. No other LibreOffice number is used.

## 11. Commit mechanics, and what was created and deleted

* Committed: this file only. `git status` shows one new file; no engine code, no patch.
* Created in Drive, inside the corpus folder (never in the root): the folder `p2w-probe-wline-0a7f`
  and the three Google Docs `wline-probe-a` / `-b` / `-c` in it. All four were deleted after the
  exports; nothing else was touched.
* Created on GitHub: the temporary release `probe-wline-0a7f` on `kavopdf/app`, used only because
  `GOOGLEDRIVE_CREATE_FILE` refuses a sandbox path as `s3key`. Deleted after the uploads.
* Nothing in the corpus folder was modified, and no file that this run did not create was deleted.
