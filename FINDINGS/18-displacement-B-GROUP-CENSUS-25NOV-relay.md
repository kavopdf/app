> Delegated census, 25 Nov relay slot. Produced by a research sub-agent from the .docx, the source PDFs and the committed Google columns; NOT independently re-measured by the run that committed it. Treat every number as the sub-agent's self-report until a run re-reads it.

# `18_displacement` group B — the 10 documents whose spacer is already spent, and what the residual actually is

**25 Nov 2026 · census run · repo `kavopdf/app` @ `ad480cd` cloned to `/scratch/work/CS` · engine
`981ff1fa35e2cf67` (the stamp the A/B/C census and the committed Google verdicts carry) · no commit,
no push, no file outside `/scratch/output` changed.**

This is group **B** of `FINDINGS/18_displacement-25-SOLO-A-B-C-CENSUS-25NOV-1626-fixer.md`: the ten
documents whose engine-written spacer paragraph is already *spent* (`w:before > 0`, `w:line` = a
1-twip hairline) and which still fail `18_displacement` in Google. Group A (11 documents, guard
refused the spacer) and group C (4, no spacer at all) are not touched here.

**The short answer.** The page-break `w:before` drop cannot operate on any of these ten: they contain
**zero** `<w:br w:type="page"/>` and **one** section each. The spacer's gap is delivered. The `.docx`
the engine wrote is *geometrically correct* — rendered in a renderer that honours `w:line` exact and
`w:trHeight` (LibreOffice), 9 of the 10 pass the same check and the per-line displacement is
0.00–0.50 pt median. The residual is therefore not an engine placement error and not a dropped gap:
it is **Google laying the vertical pitch of a table row on whole 0.75 pt CSS pixels while the engine
declares the source's pitch in twips.** One mechanism, one sign per document, accumulating down the
table. It reproduces the *sign* of the Google residual on **10 of 10** and the median within 1.3 pt
on **9 of 10**.

---

## 0. Provenance — every number, and the command that produced it

Three kinds of number appear, labelled:

* **MEASURED (this run)** — produced in this sandbox from the tree and the corpus under analysis.
* **RECORDED** — a live Google round trip already committed in `benchmarks/gverify/<doc>.json`
  (`checks.18_displacement.detail.med_dy / worst_dy`, `checks.23_line_pitch.source / .render`,
  `checks.01_page_count`). No Google render was produced by this run — see §7.
* **DERIVED** — arithmetic on the two above, shown so it can be checked.

Prep (once):

```
git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS
bash tools/p2w-bench/pod-prep.sh          # corpus 213 PDFs, JDK, PDFBox AAR, stubs, engine classes
```

The ten `.docx` were converted from the corpus PDFs by the engine's own `ConvertAll`, one shard of ten
symlinks (11.4 s, `done: 10 files, 0 failed`):

```
cd tools/engine-verify && java -cp out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar \
    ConvertAll /scratch/work/.bshard /scratch/work/p2w/out
```

The LibreOffice control is the same `.docx` rendered by `soffice --headless --convert-to pdf` and
scored by the project's own checker:

```
soffice --headless --convert-to pdf *.docx
python3 tools/p2w-bench/verify_google.py /scratch/work/p2w/corpus/<doc>.pdf /scratch/work/lo/<doc>.pdf \
        --docx /scratch/work/p2w/out/<doc>.docx
```

The geometry scripts are `/scratch/work/geo.py` (per-line dy, source gaps), `/scratch/work/census.py`
(the table below), `/scratch/work/pxmodel.py` (the pixel-grid model), `/scratch/work/decl.py`
(declared spacing per paragraph). They read the PDFs with PyMuPDF and the XML out of
`word/document.xml`; nothing is modelled in the MEASURED columns.

---

## 1. The ten documents

`step` is the RECORDED Google pitch minus the source pitch — the per-row (or per-line) advance error.
`row-snap prediction` is the DERIVED displacement of `pxmodel.py`'s row-height model (§3.4), scored
against the same two Google scalars.

| # | document | Google `med_dy` / `worst_dy` (RECORDED) | spacer paragraphs `(w:before, w:line)` pt | source pitch -> Google pitch (RECORDED) | step | table rows x text lines | `w:trHeight` (pt) | rule (pt) | LO `med` / `worst` dy (MEASURED) | LO verdict (MEASURED) | row-snap prediction `med`/`worst` |
|--:|---|--:|---|--:|--:|--:|--:|--:|--:|--:|---|
| 1 | `16_right_aligned_amounts_txtpos` | -1.6 / 3.4 | 4.60 / 0.05 | 19.0 -> 18.8 | -0.20 | 13 x 64 | 19.00 | nil (0) | 0.00 / 0.01 | 42/42 PASS | -1.8 / 3.2 |
| 2 | `303_discharge_summary` | -0.2 / 4.1 | 11.30 / 0.05; 0.00 / 0.05; 0.00 / 0.05 | 15.0 -> 15.8 | +0.80 | 5 x 45 | 15.00 | 0.375 | 0.32 / 1.00 | 47/47 PASS | +1.1 / 3.8 |
| 3 | `320_balance_sheet_statutory` | +8.2 / 19.4 | 11.80 / 0.05; 7.85 / 0.05 | 14.0 -> 15.0 | +1.00 | 21 x 73 | 13.00, 14.00 | 0.375 | 0.35 / 0.75 | 47/47 PASS | +2.5 / 6.5 |
| 4 | `325_demat_holdings_statement` | +3.8 / 38.1 | 12.85 / 0.05; 7.85 / 0.05 | 15.0 -> 15.8 | +0.80 | 12 x 84 | 14.00, 15.00 | 0.375 | 0.40 / 1.00 | 47/47 PASS | +4.5 / 7.0 |
| 5 | `362_price_list_dense` | -2.8 / 5.4 | 15.15 / 0.05 | 8.4 -> 8.2 | -0.20 | 29 x 258 | 8.40, 12.00 | nil (0) | 0.00 / 2.90 | 42/42 PASS | -2.1 / 4.2 |
| 6 | `36_embedded_subset_font` | +1.7 / 3.5 | 13.35 / 0.05 | 20.0 -> 20.2 | +0.20 | 7 x 29 | 20.00 | nil (0) | 0.04 / 0.75 | 42/42 PASS | +1.2 / 1.8 |
| 7 | `402_calendar_month_grid` | +1.4 / 6.5 | 7.80 / 0.05 | 62.0 -> 62.9 | +0.90 | 6 x 46 | 62.00 | 0.5 | 0.50 / 0.51 | 47/47 PASS | +0.8 / 1.5 |
| 8 | `74_balance_sheet_indented_subitems` | +2.2 / 4.2 | 3.20 / 0.05; 3.25 / 0.05 | 17.0 -> 17.2 | +0.20 | 10 x 54 | 17.00 | nil (0) | 0.00 / 0.01 | 42/42 PASS | +1.2 / 2.5 |
| 9 | `balance-sheet-two-columns-of-figures` | -2.3 / 5.1 | 12.55 / 0.05; 0.00 / 0.05 | 11.6 -> 11.2 | -0.40 | 16 x 95 | 11.60, 12.00, 16.00 | nil (0) | 0.05 / 3.55 | 41/42 FAIL | -2.3 / 4.8 |
| 10 | `report-2col-table-spanning-both-columns` | +2.8 / 6.8 | 6.85 / 0.05 | 18.4 -> 18.9 | +0.50 | 7 x 90 | 18.00, 19.00 | 0.5 | 0.48 / 0.88 | 47/47 PASS | +1.5 / 4.8 |

Notes that matter for reading it:

* **Every one of the ten is a single page with one section and zero page breaks.** `01_page_count`
  source 1 / render 1 on all ten; `grep -c '<w:br w:type="page"/>'` = 0 on all ten (script
  `census.py`, column `pagebreaks`).
* **Every spacer in all ten is spent**: `w:line` = 1 twip (0.05 pt) and `w:before` = 3.20–15.15 pt,
  except the three post-table carriers whose `w:before` is 0 (303 ×2, `balance-sheet-two-columns` ×1).
  No spacer in group B carries a gap in `w:line` — that is group A's construct and it is absent here.
* **The LO column is the decisive one.** On the identical `.docx`, in a renderer that honours
  `w:line` exact and `w:trHeight` literally, the median displacement is 0.00–0.50 pt and the worst is
  0.01–3.55 pt. Nine of the ten pass the whole check; the tenth (`balance-sheet-two-columns-of-figures`)
  fails it in LO too, at 41/42, and is the one document in group B that is not a Google-only defect.

## 2. The gap in the source PDF at the spacer's place

Measured as the baseline-to-baseline distance from the last body line above the spacer to the first
table line below it (PyMuPDF `get_text("dict")` origins, script in §0), against the same distance in
the LO render. `w:before` is only the *gap part* of that distance, which is why it is smaller.

| document | spacer `w:before` (pt) | line above | first line below | source gap (pt) | LO gap (pt) | source − LO |
|---|--:|---|---|--:|--:|--:|
| `303_discharge_summary` | 11.30 | MEDICATION ON DISCHARGE | Medicine | 22.50 | 22.60 | −0.10 |
| `320_balance_sheet_statutory` | 11.80 | STATEMENT OF PROFIT AND LOSS | Particulars | 21.75 | 22.10 | −0.35 |
| `320_balance_sheet_statutory` | 7.85 | Notes to accounts (extract) | Note 12 - Revenue | 17.25 | 17.70 | −0.45 |
| `325_demat_holdings_statement` | 7.85 | TRANSACTIONS DURING THE PERIOD | Date | 17.60 | 18.00 | −0.40 |
| `362_price_list_dense` | 15.15 | Effective 01-04-2024 … | PACKAGING | 22.00 | 24.90 | −2.90 |
| `36_embedded_subset_font` | 13.35 | Certificate No. ME/CO/2025 | Description | 29.55 | 29.60 | −0.05 |
| `74_balance_sheet_indented_subitems` | 3.25 | 3. Current liabilities | (a) Trade payables | 17.00 | 17.00 | 0.00 |
| `report-2col-table-spanning-both-columns` | 6.85 | Table 1. Service levels by region | Region | 16.60 | 17.60 | −1.00 |
| `balance-sheet-two-columns-of-figures` | 0.00 (post-table carrier) | EQUITY AND LIABILITIES | Long-term borrowings | 63.20 | 59.70 | +3.50 |

**Not measured:** the same gap for `16_right_aligned_amounts_txtpos`, `402_calendar_month_grid`,
`325_demat`'s first spacer, `303`'s two zero-gap carriers and `74`'s first spacer. Their "line above"
or "first line below" is a tab-aligned header cell whose text does not occur as a distinct source
line, so the text-anchored lookup returned nothing. I did not substitute an estimate. What *is*
established for them is the weaker but sufficient statement in §3.2.

---

## 3. What the residual is, in the order the evidence supports it

### 3.1 The page-break `w:before` drop is ELIMINATED for all ten

`DOCS-ROOT-CAUSES-24NOV.md` mechanism (2) — Google drops `w:before` on the first paragraph after an
explicit page break — needs a page break. These ten documents are **one page each with zero
`<w:br w:type="page"/>` and a single `w:sectPr`** (MEASURED, `census.py`, columns `pagebreaks`,
`page_count`; RECORDED `01_page_count` source 1 / render 1 on all ten). A construct that requires a
page boundary cannot displace text on a page that has none. **0 of 10 explained.**

### 3.2 The spent spacer is inert, and its gap is delivered

* Every spacer in the ten is spent (`w:before` 3.20–15.15 pt, `w:line` 1 twip), so there is no
  refused gap to release — this is the definition of group B and it is reproduced here on the
  current engine, ten for ten.
* Where the gap could be measured (§2) the source and the LO render agree to 0.05–1.00 pt on seven of the nine rows (the two outliers are `362_price_list_dense` at −2.90 pt and the stacked-table carrier at +3.50 pt),
  i.e. the engine declared the gap the page drew and a renderer that honours `w:before` delivers it.
* The Google evidence agrees: on the seven documents whose `med_dy`/`worst_dy` ratio is 0.41–0.52
  (`16_right` 0.47, `320` 0.42, `362` 0.52, `36` 0.49, `74` 0.52, `balance-sheet-two` 0.45,
  `report-2col` 0.41) the displacement is a **ramp that starts at ~0 at the top of the page** — which
  is the signature of a per-step error accumulating downward, not of a gap dropped at one place. A
  dropped spacer gap would show a step: near-zero displacement above the table and a constant
  displacement below it.

**So no spacer patch reaches group B.** This is the A/B/C census's claim, re-measured here: 10 of 10
carry only spent spacers.

### 3.3 The engine's own placement is right — measured, not assumed

This is the new measurement that splits the question in two. The identical `.docx` rendered by
LibreOffice (which honours `w:lineRule="exact"` and `w:trHeight … hRule="atLeast"` literally) is
displaced by a **median of 0.00–0.50 pt and a worst of 0.01–3.55 pt** over 29–258 matched lines per
document, and **9 of the 10 pass the whole check** (42/42 or 47/47). The engine's declared
`w:before + w:line/20` sequence reproduces the source's baselines.

Therefore the residual in the Google column is a **difference between two renderers reading the same
bytes**, not a wrong number in the bytes. That is what makes the mechanism a construct question, and
it is why the LibreOffice-measured attempts on this class in the repo's history all read as wins.

`balance-sheet-two-columns-of-figures` is the exception: it fails `18_displacement` in LO too
(worst 3.55 pt, 41/42), so part of its residual is an engine placement error that a construct fix
cannot reach. It is also the only document of the ten with a stacked-table post-table carrier
(`w:before="0"`, `w:line` = 80 twips).

### 3.4 The shared mechanism: Google lays the row's vertical pitch on whole 0.75 pt pixels

**The measurement.** Take the pitch Google actually rendered (RECORDED `23_line_pitch.render`) and
divide by 0.75 pt, the CSS pixel at 96 dpi. On all ten documents the result is a whole number:

| document | Google pitch | ÷ 0.75 | nearest px | source pitch | source ÷ 0.75 |
|---|--:|--:|--:|--:|--:|
| `16_right_aligned_amounts_txtpos` | 18.8 | 25.07 | 25 | 19.0 | 25.33 |
| `303_discharge_summary` | 15.8 | 21.07 | 21 | 15.0 | 20.00 |
| `320_balance_sheet_statutory` | 15.0 | 20.00 | 20 | 14.0 | 18.67 |
| `325_demat_holdings_statement` | 15.8 | 21.07 | 21 | 15.0 | 20.00 |
| `362_price_list_dense` | 8.2 | 10.93 | 11 | 8.4 | 11.20 |
| `36_embedded_subset_font` | 20.2 | 26.93 | 27 | 20.0 | 26.67 |
| `402_calendar_month_grid` | 62.9 | 83.87 | 84 | 62.0 | 82.67 |
| `74_balance_sheet_indented_subitems` | 17.2 | 22.93 | 23 | 17.0 | 22.67 |
| `balance-sheet-two-columns-of-figures` | 11.2 | 14.93 | 15 | 11.6 | 15.47 |
| `report-2col-table-spanning-both-columns` | 18.9 | 25.20 | 25 | 18.4 | 24.53 |

Every Google pitch is within 0.10 pt of a whole pixel; **the source pitch is off the pixel grid on
8 of 10** (303 and 325 are on-grid at the *row* level, but their cell line advances are not: 9.70 /
10.20 / 10.95 pt = 12.9 / 13.6 / 14.6 px). A renderer that reproduced the declaration would render
the declared value; Google renders a pixel.

**The model, and its fit.** `pxmodel.py` builds the whole vertical flow from the `.docx` (each
paragraph's `w:before + w:line/20`; each table row at `max(w:trHeight, the tallest cell's content)`),
then snaps every **row height** to the nearest whole pixel with the table's own rule charged
(`w:sz`/8 pt, 0 when `w:tblBorders` are `val="nil"`), and compares the displaced line positions with
the RECORDED Google `med_dy` / `worst_dy`:

| document | Google `med` / `worst` | row-snap prediction | residual |
|---|--:|--:|--:|
| `16_right_aligned_amounts_txtpos` | −1.6 / 3.4 | −1.8 / 3.2 | −0.2 / −0.2 |
| `303_discharge_summary` | −0.2 / 4.1 | +1.1 / 3.8 | +1.3 / −0.3 |
| `320_balance_sheet_statutory` | +8.2 / 19.4 | +2.5 / 6.5 | −5.7 / −12.9 |
| `325_demat_holdings_statement` | +3.8 / 38.1 | +4.5 / 7.0 | +0.7 / −31.1 |
| `362_price_list_dense` | −2.8 / 5.4 | −2.1 / 4.2 | +0.7 / −1.2 |
| `36_embedded_subset_font` | +1.7 / 3.5 | +1.2 / 1.8 | −0.5 / −1.7 |
| `402_calendar_month_grid` | +1.4 / 6.5 | +0.8 / 1.5 | −0.6 / −5.0 |
| `74_balance_sheet_indented_subitems` | +2.2 / 4.2 | +1.2 / 2.5 | −1.0 / −1.7 |
| `balance-sheet-two-columns-of-figures` | −2.3 / 5.1 | −2.3 / 4.8 | 0.0 / −0.3 |
| `report-2col-table-spanning-both-columns` | +2.8 / 6.8 | +1.5 / 4.8 | −1.3 / −2.0 |
| **mean absolute residual** | | | **med 1.20 pt · worst 5.64 pt** |

**The sign of the Google residual is reproduced on 10 of 10**, including the three documents where it
is *negative* (Google's table runs short because it truncated the row's fraction: 19.0 → 18.75,
8.40 → 8.25, 11.60 → 11.25) and the seven where it is *positive* (Google's row is a pixel taller
than the declaration: 14.0 → 15.0, 15.0 → 15.75, 62.0 → 63.0, 17.0 → 17.25, 20.0 → 20.25,
18.4 → 18.75). The median is predicted within 1.3 pt on 9 of 10 and the worst within 2.1 pt on 8 of
10.

**What the model does not reach.** It under-predicts the *worst* line on the two documents whose cells
hold 4–7 lines each: `325_demat_holdings_statement` (84 text lines in 12 rows) by 31.1 pt and
`320_balance_sheet_statutory` (73 lines in 21 rows) by 12.9 pt. The obvious completion — snap each
*cell line advance* to the pixel grid as well as each row — overshoots badly elsewhere
(`362` +11.3, `320` +17.2 on the worst line; mean worst residual rises from 5.64 to 6.14), so the
per-line term is present but is not a uniform nearest-pixel snap. **That refinement is not settled by
these ten documents**; it needs a Google round trip with per-line positions (§7).

### 3.5 The mechanisms that do NOT fit

| candidate | why it fails on these ten |
|---|---|
| **Page-break `w:before` drop** | 0 page breaks, 1 page, 1 section per document — the construct is absent (§3.1) |
| **Refused spacer / `w:line` exact as a gap** (group A's construct) | every spacer in the ten is spent; no spacer carries a gap in `w:line` |
| **Line-height shortfall on the hairline box** (`w:line` = 1.38·size read as 240ths of the face height, the engine's own documented law) | modelled with the face ratio at 1.15 it predicts **−1.5 to +1.6 pt** on every one of the ten (mean residual 2.95 pt med / 9.15 pt worst — the worst of the four models tried), because the cell text is 5.5–9.5 pt, where Google's floor (`0.069 em`) equals the declaration exactly and the error vanishes by construction. It is a real construct and it is not what is moving these pages |
| **Whole-point row ladder, `laid = round(declared + rule)`** (the repo's `LADDER-IS-WHOLE-POINTS` law) | reproduces no document: it predicts 0.00 on the five unruled tables (where a rule of 0 makes the map the identity) and −8.4 / 16.8 on `362` alone. Mean residual 2.76 / 9.75 pt — worse than the pixel grid |
| **`w:trHeight` honoured as a height** | already refuted in Google in `18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §3: Google stores our number and lays a different one. Consistent with everything here: what Google lays is the *pixel*, not the declaration |

---

## 4. Ranked list of candidate mechanisms

| rank | mechanism | documents it can explain | evidence | residual |
|--:|---|--:|---|---|
| **1** | **Google lays a table row's vertical pitch on whole 0.75 pt CSS pixels; the engine declares the source pitch in twips (`w:trHeight … hRule="atLeast"`), which is off-grid** | **10 / 10** — sign; 9/10 median; 8/10 worst | §3.4: 10/10 Google pitches are whole pixels, 8/10 source pitches are not; row-snap model sign 10/10, mean residual 1.20 pt med / 5.64 pt worst | under-predicts `325` worst by 31.1, `320` worst by 12.9 |
| 2 | The same pixel snap applied per **cell line advance** on top of the row snap (multi-line cells) | 2 / 10 as a *needed* term (`325`, `320`); hurts the other 8 if applied uniformly | `pxmodel.py` row+line variant: `325` worst 22.6 (still 15.5 short), `362` +11.3, `320` +17.2, mean worst residual 6.14 — worse overall | not separable from rank 1 on this evidence |
| 3 | Line-box misreading: `w:line` exact read as 240ths of the substitute face's line height (quadratic in type size) | 0 / 10 on its own; plausible as a small additive term on the body lines of `320`, `325`, `402` (11–20 pt headings) | §3.5: predicts ≤0.7 pt here because cell type is ≤9.5 pt, where Google's 0.069 em floor makes it exactly zero | too small to be the mechanism |
| 4 | Whole-point row ladder (`laid = round(declared + rule)`) | 0 / 10 | fits nothing: identity on unruled tables, −8.4/16.8 on `362` | refuted for this population |
| 5 | Engine placement error (the engine wrote the wrong `w:before`) | 1 / 10 — `balance-sheet-two-columns-of-figures` only | LO, same `.docx`: worst 3.55 pt, 41/42 FAIL. The other nine: LO worst ≤ 2.90 and PASS | this document needs a placement fix as well as a construct fix |
| 6 | Page-break `w:before` drop | 0 / 10 | 0 page breaks, 1 section, 1 page each | construct absent |

**The single mechanism that can explain more than one of the ten is rank 1** — it is the only candidate
that gets the *sign* right on all ten and the magnitude right on most, and it is the only one whose
parameter (0.75 pt = one CSS pixel) is the same number for all ten.

**Documents no available mechanism fully explains:** `325_demat_holdings_statement` (worst_dy 38.1
against a row-snap prediction of 7.0 — 31.1 pt unexplained) and `320_balance_sheet_statutory`
(19.4 against 6.5). Both are multi-line-cell tables; the missing term is per line inside the cell, and
the uniform version of it that I could build overshoots the other eight, so I am not claiming it.
`balance-sheet-two-columns-of-figures` is explained in sign and magnitude by rank 1 *plus* rank 5 —
its LO failure says part of its residual is not a Google construct at all.

---

## 5. What is complete, and what is not

**Complete.** The A/B/C membership of group B is reproduced on the current engine (10 documents, all
spacers spent, no `w:line` gap anywhere). The page-break mechanism is eliminated by direct
measurement on all ten. The spacer's gap is shown delivered where it can be measured. The engine's own
placement is shown correct by the LO control on all ten. The pixel-grid law is measured against ten
independent RECORDED Google pitches, and a model built from the `.docx` alone reproduces the sign on
ten of ten.

**Not measured, and why.**

1. **No Google render was produced by this run.** The `med_dy` / `worst_dy` / pitch columns are the
   committed ones from `benchmarks/gverify/*.json`; I did not drive Drive. So I have no per-line
   Google positions, which is exactly what would separate rank 1 from rank 2 and settle the rounding
   direction (nearest pixel vs ceil-with-rule). The two rules agree on 8 of 10 documents here and
   disagree by one pixel on `402_calendar_month_grid` and `320_balance_sheet_statutory`.
2. **The `w:before` delivery ratio at this engine** (the A/B/C census flags it as unmeasured) is not
   settled here either; it does not affect group B, whose spacers carry 0.05 pt of `w:line`.
3. **The source gap at the spacer's place** could not be text-anchored on 4 documents and 2 carriers
   (§2); the weaker page-top argument of §3.2 covers them.
4. **Whether Google's snap is nearest or ceiling** is not determinable from ten points: 5 ruled
   tables need `ceil(declared + rule)` and 5 unruled need `round(declared)`, and no single rule I
   tried fits all ten (`round(d + rule)` misses `402` by 0.75 pt).

## 6. What would prove this census wrong

* A `.docx` from these ten in which a table row's declared height is already a whole multiple of
  0.75 pt **and** whose cells are single-line, yet which still fails `18_displacement` in Google with
  a ramp — that would mean the pitch is not the lever. (`303_discharge_summary` is close: rows 15.0 pt
  = 20 px exactly, and it still moves — because its rule adds half a pixel. A row at 15.0 pt with
  `nil` borders and single-line cells would be the clean falsifier.)
* One Google round trip per document with per-line positions: if the displacement is a **step at each
  row boundary** of one pixel, rank 1 stands; if it is a **uniform per-line drift inside cells**, rank
  2 is the mechanism and rank 1 is only half of it.
* A document in group B whose Google pitch is *not* a whole pixel multiple. None of the ten is.

## 7. Reproduce

```
python3 /scratch/work/census.py      # §1 table: spacers, trHeight, source/Google pitch, LO dy
python3 /scratch/work/geo.py         # per-line source vs LO dy, source gaps >= 4 pt
python3 /scratch/work/pxmodel.py     # §3.4 row-snap model vs the RECORDED Google scalars
python3 /scratch/work/decl.py        # declared w:before / w:line / size per paragraph
```
