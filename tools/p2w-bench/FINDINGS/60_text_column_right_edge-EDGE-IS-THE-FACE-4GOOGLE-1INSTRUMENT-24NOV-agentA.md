# `60_text_column_right_edge` — the edge moves by `k x (line width)`, and none of the five sole-failure documents is an engine defect

**Measured 24 Nov 2026, read-only analyst slot.** Engine built in-sandbox from this tree
(`tools/p2w-bench/build-engine.sh`, javac from Adoptium, 40 s). Corpus fetched
(`corpus-fetch.sh`: 213 PDFs, 212 scored, 0 missing). Five documents converted with `ConvertOne`,
rendered with LibreOffice, and measured with the shipped check's own `columns()` / `edge()` code,
copied verbatim into `probe60.py` and instrumented to print the numbers the check throws away.

**What this run could not do, said first.** There is no file-staging operation in this session: every
Drive write path (`GOOGLEDRIVE_CREATE_FILE`, `GOOGLEDRIVE_UPLOAD_FILE`, `GOOGLEDRIVE_RESUMABLE_UPLOAD`)
takes a `file_to_upload.s3key` produced by an upload step that this agent does not have, and the
platform `upload` tool is not present (`TOOL_NOT_FOUND`). `GOOGLEDRIVE_UPLOAD_FROM_URL` needs a public
HTTPS URL for the `.docx` and nothing in this session can publish one. So **no live Google render was
made in this run.** The Google leg below is the stored `benchmarks/gverify/*.json` verdicts plus the two
live measurements already in `FINDINGS/`, and every number taken from those is labelled *recorded*. The
engine leg and the source leg are measured here, first-hand.

---

## 0. What was believed

1. The last fixer run's handoff: *"60_text_column_right_edge is worth 19.8 clean documents and 5
   documents fail only it — the second-largest single-check leverage, and nothing has been measured
   against it."*
2. `FINDINGS/60_...-GOOGLE-HAS-NO-DEJAVU-0830`: four of the five sole-failure documents fail because
   Google has no DejaVu; the fifth (`79_inr_indian_digit_grouping_table`) is *"the one document here
   with an engine defect"*.
3. `FINDINGS/60_...-IT-FIRES-UNDER-...-2322`: the check fires **under** (the render's column is
   narrower), with a suspicious constant −65.6 pt on two unrelated documents.
4. `FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` §60: the engine never puts a right edge in the file; 28 of 56
   are the DejaVu wall, the other 27-28 are a half-point size floor plus a single-line estimator; the
   two live measurements disagree on the **sign** and no stored record can settle it.

## 1. What was measured

### 1a. The population, from the store (not from prose)

`benchmarks/gverify/*.json`: **190 rows with `status:"ok"`**, 213 files. **56** fail
`60_text_column_right_edge` (54 on engine `b7699196`, 2 on `462353f`). **Five** fail nothing else:

   302_radiology_report   41/42     313_power_of_attorney      41/42
   316_contract_with_schedules 46/47 321_auditors_report        41/42
   79_inr_indian_digit_grouping_table 41/42

The leverage figure is real but it is **fractional**, not documents:
`sum(1/len(failed))` over the 56 = **19.80**; the number of documents that go CLEAN if 60 alone were
cleared is **5**. Both are computed from the store in this run. Anyone reading "19.8 clean documents"
as "19.8 documents" is reading the wrong column.

### 1b. The source page: what the PDF actually draws

| document | page | body column left → right edge | is the edge *drawn*? | page's own right margin |
|:--|--:|:--|:--|--:|
| `302_radiology_report` | A4 595.28 x 841.89 | 34.00 → **543.74** | no — ragged: next line ends 536.62 (−7.1 pt), then 529.04 | 51.54 pt |
| `313_power_of_attorney` | A4 | 56.69 → **538.61** | **yes** — 8+ line ends within 0.03 pt of 538.60 (justified) | 56.67 pt |
| `316_contract_with_schedules` | A4 | 56.69 → **538.61** | **yes** — justified; table box drawn 77.6 → 517.6 | 56.67 pt |
| `321_auditors_report` | A4 | 56.69 → **538.61** | **yes** — 8+ line ends within 0.02 pt | 56.67 pt |
| `79_inr_indian_digit_grouping_table` | A4 | 56.00 → 475.70 (body), table rules drawn 56.0 → 540.0 | partly — rules, and a justified "Amount in words" line | 55.3 pt |

Read from the PDF's own operators, not from the text layer alone: `get_drawings()` on `302` gives two
rules (28.0 → 567.3 at y 58.0, 300.0 → 567.3 at y 681.9); on `316` a table box and row rules
(77.6 → 517.6); on `79` ten rules and cell rectangles 56.0 → 540.0. **No vertical rule sits at the
column edge on 313/321** — the right edge there is the justified line ends, which is what the check
reads and what a reader sees.

The three DejaVu serif documents are all **2 cm margins, justified body**: the column's right edge is
the paper minus 56.69 pt, stated by the page to ±0.03 pt over eight or more lines. That is a precise
reference, and it is the same 56.69 pt on three documents built by different authors — a page
constant, not a coincidence.

### 1c. Our `.docx`: the construct that decides the right edge

Unzipped `word/document.xml` for all five:

    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/>
             <w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0"
                      w:header="0" w:footer="0" w:gutter="0"/>
             <w:cols w:space="0"/><w:docGrid w:linePitch="360"/></w:sectPr>

* `w:pgSz w:w="11906"` = **595.30 pt**; `w:pgMar w:right="0"` → the text area's right edge is the
  **paper's**, 595.30 pt, on all five.
* **Every** `w:ind` in all five carries `w:right="0"` (21, 30, 42, 34 and 33 occurrences). `w:jc` appears
  only as `center`, on headings. **Tab stops: 0 in `302`/`313`/`316`/`321`, 2 in `79`** — and neither
  of `79`'s is a right-aligned stop at the column edge. Tables: `w:tblW` 7813 / 8800 twips, `w:tblInd`
  560 / 1553, fixed `w:tcW` per cell — the cell widths are the source's cell widths.
* **One `<w:p>` per source text line and zero `<w:br/>`** (313: 30 paragraphs / 30 lines; 321: 34 / 34).

So the file states no right edge anywhere. The gap between what the page draws and what the file
declares is exact and document-independent:

    text-area right edge (595.30) - source column edge (538.61) = 56.69 pt   (313, 316, 321)
    text-area right edge (595.30) - source column edge (543.74) = 51.56 pt   (302)

**That gap is not the cause of the failure, and this run measured that.** With the declared face
present in the renderer, a left-aligned, hard-broken line ends where its glyphs end, not where the text
area ends — so the 56.69 pt of unclaimed width changes nothing. Table in §1d.

### 1d. The render, face present: the edge lands where the page drew it

LibreOffice render of the engine's own `.docx`, measured with the check's own `columns()` / `edge()`
(`probe60.py`, page 1, every column the check judges):

| document | column left | source edge `rs` | render edge `rg` | Δ | slack | verdict |
|:--|--:|--:|--:|--:|--:|:--|
| `302_radiology_report` | 28.00 | 543.74 | 543.26 | **−0.48** | 32.68 | pass |
| `302_radiology_report` | 250.00 | 328.73 | 328.72 | −0.01 | 22.48 | pass |
| `313_power_of_attorney` | 56.69 | 538.63 | 539.85 | **+1.22** | 40.00 | pass |
| `316_contract_with_schedules` | 56.69 | 538.61 | 537.79 | −0.83 | 19.27 | pass |
| `316_contract_with_schedules` | 83.64 | 166.40 | 166.76 | +0.37 | 33.26 | pass |
| `316_contract_with_schedules` | 382.71 | 421.64 | 422.00 | +0.36 | 13.29 | pass |
| `321_auditors_report` | 56.69 | 538.61 | 539.21 | **+0.60** | 28.49 | pass |
| `79_...grouping_table` | 56.00 | 475.70 | 475.56 | −0.14 | 19.12 | pass |
| `79_...grouping_table` | **132.27** | **289.97** | **149.70** | **−140.27** | 17.72 | **UNDER** |
| `79_...grouping_table` | 198.60 | 228.00 | 226.70 | −1.30 | 29.40 | pass |
| `79_...grouping_table` | 268.50 | 288.37 | 289.70 | +1.33 | 20.28 | pass |
| `79_...grouping_table` | 323.10 | 372.37 | 417.69 | +45.32 | 40.00 | pass |
| `79_...grouping_table` | 399.06 | 445.96 | 443.90 | −2.06 | 39.90 | pass |
| `79_...grouping_table` | 483.24 | 535.94 | 533.52 | −2.42 | 40.00 | pass |

**Four of the five are exact to ±1.22 pt in a renderer that has the declared face.** The engine's
column model is right on these four documents; nothing in the `.docx` needs changing to reproduce the
page's right edge, and the 56.69 pt of unclaimed text area costs nothing while the face is present.

### 1e. The render, face substituted: the edge moves by `k x (line width)`

Same `.docx` bytes, one attribute changed — `w:ascii` `DejaVuSans`→`Arial`, `DejaVuSerif`→`Times New
Roman` — rendered by the same LibreOffice, which resolves those names to Liberation Sans/Serif, i.e.
**Arial's and Times New Roman's advance widths**. This is the closest local stand-in for what Google
does with a face it does not have, and §2 shows it reproduces Google's recorded direction and magnitude.

| document | column left | `rs` | `rg` (Arial metrics) | Δ | slack | verdict |
|:--|--:|--:|--:|--:|--:|:--|
| `302_radiology_report` | 28.00 | 543.74 | 431.53 | **−112.21** | 32.68 | **UNDER** |
| `302_radiology_report` | 250.00 | 328.73 | 324.59 | −4.14 | 22.48 | pass |
| `313_power_of_attorney` | 56.69 | 538.63 | 450.98 | **−87.65** | 40.00 | **UNDER** |
| `316_contract_with_schedules` | 56.69 | 538.61 | 439.70 | **−98.91** | 19.27 | **UNDER** |
| `316_contract_with_schedules` | 83.64 | 166.40 | 156.52 | −9.88 | 33.26 | pass |
| `316_contract_with_schedules` | 382.71 | 421.64 | 416.84 | −4.81 | 13.29 | pass |
| `321_auditors_report` | 56.69 | 538.61 | 442.00 | **−96.62** | 28.49 | **UNDER** |

A third probe, `DejaVu*`→`Verdana` (which LibreOffice resolves to Noto Sans), gives −42.09, −37.46 and
−35.44 on the same three columns — inside the 40 pt slack on two of them and outside on `302`. **The
verdict is a function of which face the renderer picks, and of nothing else.**

Per line, the movement is *inside* the line and proportional to it — the signature of an advance-width
difference, not of any indent:

| `313` line (y) | source `x1` | DejaVu render `x1` | Arial render `x1` | `k` (DejaVu) | `k` (Arial) |
|:--|--:|--:|--:|--:|--:|
| 82.3 | 538.60 | 536.42 | 450.98 | 0.9955 | 0.8182 |
| 97.3 | 538.60 | 537.01 | 447.34 | 0.9967 | 0.8106 |
| 112.3 | 538.58 | 539.85 | 446.25 | 1.0026 | 0.8084 |
| 127.3 | 529.03 | 528.55 | 428.45 | 0.9990 | 0.7871 |
| 163.3 | 528.08 | 527.65 | 421.75 | 0.9991 | 0.7744 |

and the `k` measured for a line equals the advance-width ratio of the two faces **for that line's own
string**, computed from the font files:

    'THIS POWER OF ATTORNEY is exec…' at 10.00 pt   DejaVu 464.13 pt, Liberation 378.55 pt
                                                    metric k = 0.8156   measured k = 0.8182
    'To the Members of Shreeji Logi…' at 9.50 pt    DejaVu 252.29 pt, Liberation 201.30 pt
                                                    metric k = 0.7979   measured k = 0.7975

### 1f. The law

**`rg = left + k x (rs - left)`**, one parameter per render, `k` = the advance-width ratio of the
renderer's face to the source's face, fitted by least squares through the origin on `(rs - left)`:

| render | columns | fitted `k` | r | max abs residual | rms residual |
|:--|--:|--:|--:|--:|--:|
| LibreOffice, DejaVu present | 13 | **1.0019** | **0.9952** | 45.23 (one column, `79`'s split header — see §3) / 2.52 excluding it | 12.61 / 1.32 on the other 12 |
| LibreOffice, Arial metrics | 7 | **0.7998** | **0.9983** | 11.62 | 7.10 |
| LibreOffice, Noto metrics (Verdana name) | 4 | **0.9221** | **0.9998** | 2.09 | 1.45 |
| **Google, recorded** (`FINDINGS/60_...-2322`, 3 docs) | 3 | **0.8718** | 0.26 (see note) | 3.81 | 2.79 |

Note on the Google row: `r` is **not** informative there and is reported so nobody reads it as a fit.
The three recorded columns are 482-516 pt wide, so the fitted predictions span only 1 pt while the
residuals span 7 pt; a correlation on three points that close together measures noise, not agreement.
What the row does establish is that one `k` reproduces all three recorded edges to within 3.81 pt.

The residuals are largest on short columns (`302` col@250, `316` col@83.6), which is where the widest
line is a different *string* on the two sides — the law is about the same string, and a column whose
maximum changes identity is the one place it cannot hold exactly.

**The law in words, true of any document:** the check compares the source's widest line and the
render's widest line; a line's right edge is its left edge plus the sum of its glyphs' advance widths;
so when the renderer draws the line in a different face, the edge moves by `(k - 1) x (line width)`,
with `k` the ratio of the two faces' advance widths — **nothing in the `.docx` enters that expression**,
because the engine writes `w:ind right="0"`, no `w:jc`, no tab stop, `w:pgMar right="0"`, and one
paragraph per source line, so no construct in the file states where a line should stop.

The one constant in this class is therefore not an offset but a **ratio**: −65.6 pt on two unrelated
documents (`2322`'s observation) is `(k - 1) x 482` with `k` = 0.864 and 0.879 on the two — they agree
to 4 pt because their *columns* agree (both are the 2 cm column, 481.9 and 481.9 pt wide), not because
the fault is a constant. `302`, whose column is 515.74 pt wide and whose body is 8.5 pt, moves −112.21
under the same substitution.

---

## 2. The Google leg: what the stored record says, and what it cannot say

* `benchmarks/gverify/*.json` stores only `passed`/`total`/`failed` — **no `(over, under)` pair, no
  edge value, no rendered page** for any of the 213. So the store can say *that* `302` fails 60 in
  Google and cannot say *how far* or *which way*.
* `benchmarks/gverify-lo/*.json` is the same check on the LibreOffice render. On these five it agrees
  with §1d exactly (four pass, `79` fails).
* Two live Google measurements exist in `FINDINGS/` and they disagree on the sign: `b0601de` (23 Nov)
  measured the substituted face 10-15 % **narrower**, column under by 58-66 pt; `f43e86b` (24 Nov)
  measured the same document **+4.8 % wider**, 35 lines instead of 33, one column over by 28.5 pt.
  `DOCS-ROOT-CAUSES-24NOV.md` records both and says neither sign has been established for the class.
* What this run adds: **every face substitution available to be measured here is narrower than
  DejaVu** (k = 0.774-0.927 across 11 columns and three substitutions), so the *under* branch is the
  reproducible one, and the over branch requires a face wider than DejaVu — which the recorded Google
  export (`Calibri, Calibri-Bold, Verdana, Verdana-Bold, ArialMT`) would have to supply through real
  Verdana. **Not measured here; not measurable here.**

The `k = 0.8718` fit on Google's three recorded points is the useful part: it sits **between** Arial's
0.7998 and Noto's 0.9221, which is exactly what a mixed Calibri/Verdana/Arial export should give, and
it reproduces all three recorded edges to within 3.81 pt. That is a ratio law confirmed on Google's own
numbers even though this run could not make one.

---

## 3. What is now true

**The five sole-failure documents split 4 / 1, and neither part is the engine.**

**(a) Four are `Google cannot do it`.** `302`, `313`, `316`, `321` declare the source's own faces
(`DejaVuSans` / `DejaVuSerif`, 27-34 runs each, read back from `document.xml`), Google has no DejaVu,
and no face it has is metrically DejaVu. Measured here: with the face present the column lands within
±1.22 pt; with Arial's metrics it lands 87.65-112.21 pt short. `FINDINGS/GOOGLE-IGNORES-CHARACTER-WIDTH-2424`
already measured that `<w:w>` and `<w:spacing>` are ignored outright (380.1 pt, "no effect"), so the
substitute face cannot be stretched back to the source's widths, and `0830` §4 measured that an embedded
`.odttf` face is ignored too. **There is no construct left.** 103 of the 213 corpus documents are set
in DejaVu (`GOOGLE-IGNORES-CHARACTER-WIDTH-2424`'s face table); 59 of the 190 measured here have a
DejaVu source face and **28 of those 59 fail 60 (47 %), against 28 of 131 (21 %) for the rest** — the
face doubles the rate but does not explain the class, which is the same 28-of-56 split
`DOCS-ROOT-CAUSES-24NOV` reached by conversion.

**(b) `79_inr_indian_digit_grouping_table` is `instrument wrong`, and the earlier record calling it
"the one document here with an engine defect" is refuted.** The failing column at left 132.27 is the
table's header row. The page draws the same three cells in the same places on both sides:

| | source | render | Δ |
|:--|:--|:--|--:|
| `Lots` | 132.27 → 150.00 | 132.40 → 149.24 | left +0.13, right −0.76 |
| `Metres processed Rate per metre` | 156.60 → 289.97 | 156.60 → 282.77 | left 0.00, right −7.20 |

PyMuPDF's line extractor joins `Lots` to the rest of the header in the **source** (inter-cell gap
6.60 pt) and splits it in the **render** (gap 7.40 pt) — because `Lots` is 0.76 pt narrower in
Liberation Sans Bold than in Liberation Sans Bold as the source embedded it. One line in one text layer
and two in the other. The check takes the **widest line** of the column, so the render's column reads
149.24 instead of 282.77 and the column is charged 140.27 pt of movement that is not on the page.

Word-level proof that the page is unchanged: **170 of 170 words matched, left edge mean −0.70 pt (max
8.61), right edge mean −1.15 pt (max 9.07)**. The ink is where the page drew it; only the extractor's
grouping moved.

So the class's five sole-failure documents are **4 x Google cannot do it + 1 x instrument, 0 x engine** —
and the fifth is a fault of a different kind from the other four, which is why it fails in *both*
renderers while they fail in one.

**(c) The engine's missing right edge is real and is not this check's cause.** 595.30 pt text area
against a 538.61 pt column on every document, `w:ind right="0"` on every paragraph, no tab stops. That
is a defect — it is what lets a *wider* substitute run past the column and re-break the page (`f43e86b`
measured 33 → 35 lines on `302`), and it is what the check's own comment describes as "57 documents
overrun the right edge". But §1d measures that it does **not** move the edge when the face is present,
and `DOCS-ROOT-CAUSES-24NOV`'s four-construct experiment measures that a right indent **bounds but does
not pin** a ragged line (A, B and C all land at 352.4 / 329.4 pt). **Writing `w:pgMar right` or
`w:ind right` would move this check by 0.0 pt and is not a candidate.** (It is also the change
`FIXER-BRIEF` forbids for `47_margins`.)

---

## 4. The exact candidate change

**No engine change.** The four Google-only documents have no construct available (face named: measured
both ways in §1e and `0830` §3; face embedded: measured in `0830` §4; character width: measured in
`GOOGLE-IGNORES-CHARACTER-WIDTH-2424`; right indent / cell width: measured in
`DOCS-ROOT-CAUSES-24NOV` §60 — bounds, does not pin; justified multi-line paragraph: pins to −0.4 pt
but contradicts the one-paragraph-per-source-line model that `17_matched_runs`, `23_line_pitch` and
`18_displacement` rest on, and the engine has no justified alignment to emit).

**One instrument change, and it is small enough to state exactly.**

* **File:** `tools/p2w-bench/verify_google.py`
* **Function:** `extra_checks2()`, the nested `edge()` helper and the
  `c["60_text_column_right_edge"] = (over, under, ...)` block that begins at line 2497 and ends at 2690
  (`def edge(col, left, words)` is at 2608).
* **Condition and new number:** `edge()` returns `v[-1]` — the widest **line** bbox of the column. A
  line bbox is a property of the text extractor, not of the page: `79`'s header is one line on one side
  and two on the other for a 0.76 pt word-width difference. Replace the edge with the widest **word**
  right edge among the words that belong to the column's own lines — i.e. build `v` from
  `page.get_text("words")` restricted to the words whose left edge is within `COL`-membership of the
  column's left and whose baseline lies within one of the column's line bands — and keep the existing
  slack (`one_word`, median word width, `SLACK_CAP = 40.0`) unchanged. On `79` that reads
  289.97 → 282.77 (−7.20, slack 17.72) and the document passes; the over branch is untouched, because a
  line that runs past the column is made of words and its last word still sets the maximum.

  This is a rule about *what a column's edge is*, not about a document. **It is not committed, and it
  must not be, until it has been re-measured over all 213** — the same discipline `INSTRUMENT.md`
  requires, and the change can only *reduce* firings on columns whose lines split differently, which
  is exactly the population `79` is in.

* **Second, cheap, and independent: store the pair.** `gverify.py`'s `collect()` writes `failed` only.
  Writing `checks["60_text_column_right_edge"]` (the `(over, under)` tuple it already receives) into the
  per-document JSON costs nothing and makes every future reading of this class falsifiable in one place;
  the absence of it is why two runs could report opposite signs for the same document and neither could
  be checked. `DOCS-ROOT-CAUSES-24NOV` §"A data gap worth closing" asks for the same thing.

* **What must not be done:** do not widen the slack for these documents. The movements are 87-140 pt
  against a 17-40 pt allowance — 2.2 to 7.9 times the whole tolerance — and a slack that covers them
  would make the check blind to a real 60 pt overrun on every document in the corpus.

---

## 5. What would prove this wrong

1. **A Google export of `302`, `313`, `316` or `321` whose embedded faces are the declared
   `DejaVuSans`/`DejaVuSerif`** and whose column edge is 538.6/543.7 pt — that would put the fault back
   in the engine. (`0830` §4 tried the embedded-face route and the export was unchanged; the naming
   route is §1e.)
2. **A Google export whose column edge is *past* the source's by more than one word on these four** —
   that would mean the substitution is wider than DejaVu, the over branch is the real one, and the sign
   in `f43e86b` is the class's sign. This run could not make an export, so the sign is still open. The
   `k` fit in §1f predicts a narrower render for every face measured here; one export with the column
   edges printed would settle it.
3. **A `79` render whose header row is extracted as one line** (a word-level check showing the render's
   `Lots` gap at 6.6 pt rather than 7.4 pt) — then `79` would not fire and the instrument reading in §3b
   would be wrong.
4. **A `79` whose words are *not* within 9.07 pt of the source's** — then it is an engine defect after
   all and the word-level match in §3b is the error.
5. **A construct that pins a ragged line's right edge and survives a face substitution, at a cost of
   zero to `17_matched_runs`, `23_line_pitch` and `18_displacement`.** `DOCS-ROOT-CAUSES-24NOV` found
   exactly one that pins (justified multi-line paragraph, −0.4 pt under substitution) and measured its
   price. If a cheaper one exists, §4's "no engine change" is wrong.

---

## 6. Data this finding leaves behind

    columns60.csv     25 measured columns x {doc, variant, page, left, rs, rg, delta, slack,
                      over, under, n_src_lines, n_ren_lines} for the DejaVu / Arial / Noto renders
    census60.json     190 measured documents x {doc, dejavu source face, fails 60, checks offered}
    img/313_right_edge.png   source page, DejaVu render, Arial render, cropped at the column's right
                      edge, with the 538.61 pt edge drawn

    reproduce:  bash tools/p2w-bench/build-engine.sh
                java -cp out:libs/... ConvertOne <corpus>/<doc>.pdf <outdir>
                soffice --headless --convert-to pdf --outdir lo <doc>.docx
                python3 probe60.py <corpus>/<doc>.pdf lo/<doc>.pdf

**Provenance of every number.** §1a, §1b, §1c, §1d, §1e, §1f and §3b are measured in this run on the
engine built from this tree and the corpus fetched by `corpus-fetch.sh`. The Google column of §1f's
last row is *recorded*, from `FINDINGS/60_...-2322`'s live round trips, and is labelled as recorded. No
live Google render was made in this run and none is claimed.

---

**Agent:** `60ed60_text_column_right_edge-01` - deployed by the 24 Nov 18:28 fixer slot, landed here. `HANDOFF.json` carries the same id and this path.
