# The dominant remaining sub-cause of `18_displacement` is the baseline's placement inside the hairline exact line box

**27 Nov 2026, measurement slot · repo `kavopdf/app` @ HEAD `7f118dab`, engine fingerprint
`74a152e7d3fb3d26` (printed by `_engine_head()` on this tree, so it is the same engine every Google
row quoted below was scored by) · corpus 213/213 fetched, engine compiled, `pod-prep.sh` clean.**

**One named document: `31_times_body_arial_headings`.** Every line on it is displaced by **+1.70 to
+3.25 pt**, median **+2.70**, and the displacement is a **rigid shift, not a drift**: the fit against
page height is `dy = +2.48 − 0.00031·y` (0.2 pt across the 748 pt the matched runs span). The number that names the
construct: the renderer puts the baseline **0.312 em** below the top of the exact line box
(min 0.292, max 0.331, n=19), while the engine charges **0.050 em** — `LINE_BASE` (0.8) × a box that
is a hairline. 0.26 em at 10.5 pt type is 2.7 pt, and that is what was measured.

**Instrument warning, up front.** The Google half of this run could not be made: the platform `upload`
tool is not in this session's tool list, so no `.docx` can be imported into Drive as a Google Doc
(`GOOGLEDRIVE_CREATE_FILE` and `GOOGLEDRIVE_UPLOAD_FILE` both answer *"the file key does not belong to
this project or session"* for a sandbox path; see §8). **Every per-item number below is LibreOffice —
proxy-only, labelled as such.** The Google side is the stored row in `benchmarks/gverify/`, quoted, on
the same engine, and it agrees with this run's proxy median to 0.1 pt on the proof document.

---

## 0. What the check actually asserts

Read from `tools/p2w-bench/verify_google.py`, not from its name. It is **not** a per-document median
and **not** a fixed tolerance: it is a per-page budget over every matched upright run.

```python
5863	    def _tol(size):
5864	        return min(max(0.35 * size, 1.5), 4.5)
```
```python
5888	        n_out = sum(1 for d, sz in ds if abs(d) > _tol(sz))
...
5892	        worst_here = max(abs(d) / _tol(sz) for d, sz in ds)
5893	        if (n_out > max(2, -(-len(ds) * 5 // 100)) or n_out == len(ds)
5894	                or worst_here > TAIL_FACTOR):
5895	            bad_pages.append(pg)
```
```python
5904	    checks["18_displacement"] = (0, len(bad_pages), not bad_pages, {
5905	        "med_dy": med_dy, "worst_dy": worst_dy, "med_dx": med_dx,
5906	        "bad_pages": bad_pages, "runs_matched": len(pairs),
```

with `TAIL_FACTOR = 2.0` (`:5869`) and the population filtered to upright runs only
(`:5860-5861`: `abs(math.sin(math.radians(r["angle"]))) <= 0.02`).

So, in words — the three ways a page is displaced, exactly as the code decides them:

| clause | what it counts as displaced | line |
|:--|:--|--|
| budget | `n_out > max(2, ceil(0.05·n))` — more than 5 % of the page's runs out, with a 2-run grace | `:5893` |
| block move | `n_out == len(ds)` — every run on the page out, however few runs | `:5893` |
| tail | `max(|dy| / tol) > 2.0` — one run more than twice its own tolerance out | `:5892-5894` |

and the tolerance is **0.35 em clamped to [1.5, 4.5] pt**, i.e. per type size, not per document. On
the proof document that is 2.80 pt at 8 pt type, 3.15 at 9, 3.50 at 10, 3.67 at 10.5, 4.20 at 12
(computed: `measure.py` §C). `dy` is `g["ry"] − r["ry"]` (`:5874`), reading-space y, so **a positive
dy means the built line sits lower down the page than the source drew it.**

Two consequences that decide this whole file:

1. **A rigid page shift is exactly what the budget clause punishes**, because every run is out by the
   same amount, and the tail clause punishes it again once it is more than twice the tolerance.
2. **A displacement smaller than the tolerance is invisible** — which is why a construct can be
   present, measurable and wrong on every line of a page and still pass on the type sizes where the
   tolerance is widest.

---

## 1. The premise, corrected from the store (`measure.py` §A)

`classpick.py --leverage` on this tree prints **`18_displacement 55.5`** (run this slot; next is
`60_text_column_right_edge 22.6`) — confirmed, and it is a *worth in CLEAN documents*, not a failure
count. The counts the store actually holds:

| source | what it counts | number |
|:--|:--|--:|
| `benchmarks/gverify/*.json`, scored rows | documents failing `18_displacement` | **109** |
| same, `failed == ["18_displacement"]` | **documents failing only this check** | **29** |
| same, restricted to the tree's engine `74a152e7d3fb3d26` | scored rows / failing 18 / failing **only** 18 | **63 / 32 / 9** |
| the 29 minus the 9 | sole-18 rows **not re-measured since the 27 Nov row-rung landed** | **20** |

**So "29 documents fail only this check" is 9 documents on the engine in the tree and 20 stale rows**
on `a4d8fca4`/`025fe9de`. This matters for what follows: the measurement below is over the 9, which is
the only set whose Google verdict belongs to the current engine.

The shape of the whole current-engine population (`measure.py` §D, 32 documents):

* **31 of 32 are single-page**, and the one multipage document (`324_loan_amortisation_schedule`, 7
  pages) also fails `27_text_off_page` — it is a different fault, not this one.
* **30 of 32 have `|worst_dy| ≤ 15 pt`**; median `|worst_dy|` **5.8 pt**, max 276.6 (that is 324).
* every one of the 9 sole-18 documents fails **page 0 only** (`bad_pages == [0]`).

That is the single most useful fact this run produced: **the class is no longer page-scale.** Whatever
is left is a few points, on one page, at the top of the document — not a page top that moved, not a
page that re-flowed, not a lost page.

---

## 2. Every sub-cause already eliminated, and the measurement that eliminated it

Quoted from the FINDINGS named in the last column — **not re-measured by this run**; the only numbers
this run computed are in §1, §5, §6 and §7.

| # | sub-cause | the measurement that eliminated it | where |
|--:|:--|:--|:--|
| R1 | snap the row's border box to a 0.75 pt rung (`ROW_BOX_SNAP_TW`) | `320_balance_sheet_statutory` in Google `med_dy` **+8.2 → +8.2**, no check changed state; and the probe was void (292 tw and 280 tw round to the same rung) | `18-displacement-ROW-SNAP-FALSIFIED-25NOV-fixer.md`; correction in `18-displacement-ROW-HEIGHT-IS-CONTENT-DRIVEN-26NOV-fixer.md` |
| R2 | `w:hRule="atLeast" → "exact"` on content rows | exported PDF position-for-position identical (73 lines, same y); byte-patching every row moved `68_journal` **0.0 pt**, `mobile-bill` **0.0**, `bank5` **0.0** — Google does not read `hRule` | `ROW-HEIGHT-IS-CONTENT-DRIVEN` probe A; `18-displacement-GAP-CARRIER-25NOV-relay.md` item 4 |
| R3 | shorten `w:trHeight` instead of the cell's line | `electricity-bill` 18.0/19.0 → **17.5/18.5**; 18 gained fewer documents than it fixed | `DocxWriter.java:6467-6474` |
| R4 | make the cell's content equal the row's height, form 1 (`w:before = rowLineTw − box`) | `18_median_dy` **64 → 100** | `DocxWriter.java:6867` |
| R5 | same construct, form 2 (raise one-line cells' `w:before` to `w:trHeight`) | corpus rebuild 204/212: **13 better, 91 worse**, mean `median_pt` 2.274 → **2.641** | `18-displacement-ROWH-CONTENT-EQUAL-TRHEIGHT-REFUTED-27NOV-relay.md` |
| R6 | carry the page-top gap in a 1×1 table row instead of `w:before` | 4 documents: **none becomes clean**; `mobile-bill` `worst_dy` 10.0 → **33.8** | `18-displacement-GAP-CARRIER-25NOV-relay.md` + `res-18-gapcarrier/` |
| R7 | Google charges a **constant** 5–10 pt for a refused exact-line spacer | `330_cad_drawing_sheet` asks 143.95 pt, loses **110.1** — the charge is **proportional** (21.6 % of the ask) | `18-displacement-SINGLE-PAGE-SPACER-MEASURED-26NOV-explore.md` §4 |
| R8 | the page-scale half is one thing (the dropped page-top `w:before`) | **8 of 17 are single page**, no `<w:br w:type="page"/>`, `pgMar top=0` — structurally unreachable; 3 carry no spacer at all | `18-displacement-PAGE-SCALE-IS-THE-DROPPED-PAGE-TOP-26NOV-explore.md` §1-2 |
| R9 | the check fails because Google adds / drops / splits a line | 14 documents: **0 source runs lost on 11 of 14**; the surplus is U+200B (one per cell) | `18DISPLACEMENT-COUNT-0125-27NOV.md` §3 |
| R10 | `attribution = table-row` predicts the displacement | `med_dy` vs `docx_table_rows` slope **−0.108, r²=0.00** over 207 rows | ledger 26 Nov 14:59 |
| R11 | the multi-row family is the page-fit reserve | `p2w.fitreserve 96→300`: `word/document.xml` **byte-identical** on all 8 largest multi-row documents | ledger 26 Nov 15:48 |
| R12 | `-Dp2w.lineRule=autoflow` fixes the class | `electricity-bill` −7.2 → **+0.08** but `72_bank_statement` +1.1 → **+3.51**, worst 4.8 → 8.44 — opposite signs | ledger 26 Nov 11:49 |
| R13 | the hairline deficit (`w:line` exact short by 0-1.8 pt) **orders** the solo documents | measured 0-1.8 pt and **does not order them** — a ranking claim, refuted as a ranking claim | ledger 26 Nov 11:38 |
| R14 | `w:trHeight w:val` is only a floor the content absorbs | three values in one render, prediction first: 300 → **15.75**, 280 → **15.00**, 260 → **13.50**. Three for three | `ROW-HEIGHT-IS-CONTENT-DRIVEN` "CORRECTION, SAME RUN" |
| R15 | the 0.75 pt law is "+1 rung, ceiling, upward only" | `16_right_aligned_amounts_txtpos` declares 19.00 pt and Google lays **18.75** — a negative delta; nearest rung, not ceiling | `18DISPLACEMENT-COUNT-0125` §5 |
| R16 | a floating table (`w:tblpPr`) or `w:framePr` as the page-top carrier | `framePr`: **0 in 213 emitted files**; `tblpPr` wraps text around the table (file 01's BILL TO moved x=64 → 528) | `PAGE-SCALE` §2; `DocxWriter.java:6185-6205` |
| P1 | `w:pBdr` in the cell paragraph (the ruled-row branch) | **PARKED, not to be re-opened.** Source draws five rules at 273.38/288.38/303.38/318.38/333.37/348.37 and the **unmodified engine already reproduces them** (273.2/288.2/303.2/318.2/333.2/348.2). The construct is placeable on **2 of 77** documents. Also a method correction: measure a rule's absolute y, never the pitch between rules | `BLOCKERS.md` 27 Nov 09:28; `18_displacement-PBDR-IN-CELL-PARAGRAPH-REFUTED-IN-LIBREOFFICE-27NOV-relay.md` |
| L1 | the row rung + spacer spend (landed 27 Nov) | `mobile-bill` **46/47 → 47/47**, `electricity-bill` **46/47 → 47/47** in Google; `price-list-2col-dense-right-aligned` byte-identical; gate passes | `TABLE-GAP-IS-BEFORE-RUNG-IS-10-27NOV-fixer.md` |
| L2 | "the row rung is a constant, apply it everywhere" | −10 tw on every row: four documents do not move, `price-list-2col-dense-right-aligned` loses `46_text_crossing_rule` (41/42 → **40/42**). Hence the `FOOT_ROOM_MIN_TW = 100` gate | `18-displacement-ROW-RUNG-IS-A-TRADE-27NOV-fixer.md` §3 |

Also already eliminated by the *shape* of the population in §1: **page-top / page-break / spacer /
`pgMar` carriers, row-box snapping, `hRule`, content-equals-row, gap-carrier rows, the fit reserve,
`autoflow`, and line add/drop.** 31 of 32 remaining documents are single-page and 30 of 32 are within
15 pt: none of the page-scale constructs can be producing that.

**What is left, then, is not a carrier of the page but the placement of a line inside its own box.**

---

## 3. The sub-causes that survive, ranked

### Survivor 1 (dominant) — the baseline is charged at `LINE_BASE × box`, and the box is a hairline

`DocxWriter.java:220` — the constant, and the measurement behind it:

```java
220	    private static final float LINE_BASE = 0.8f;
```
> "A one-paragraph probe with zero margins was rendered through LibreOffice at seven box heights and
> four faces — 9.2, 11, 13, 14.95, 15.18, 20, 23, 34.5, 37 pt … **one box shorter than its own em** —
> and in every case `boxHeight - baselineY` came to 0.2 of the box … **The ratio does not follow the
> font size or the face; it follows the box.**" — `DocxWriter.java:207-219`

The engine writes a flowing line's box as `w:line` = the **hairline**, 11–13 twips = 0.55–0.65 pt
(`DocxWriter.java:155-160`, `spacing()`), while the type in that box is 8–12 pt. So:

* the engine's model puts the baseline at `0.8 × 0.65 = 0.52 pt` = **0.050 em** below the box top;
* the renderer, measured on the proof document, puts it at **0.312 em** (min 0.292, max 0.331, n=19) —
  i.e. at the face's own descent, not at a fraction of a box that is 1/16 of the em.

The probe behind `LINE_BASE` never covered this case: its shortest box (9.2 pt) was still **0.88 em**
for a 10.5 pt line, and the one box "shorter than its own em" was 15.18 pt against a 16 pt face. A
0.65 pt box is **0.062 em** — an order of magnitude outside the measured range, and the ratio there
is not 0.8 of the box, because no renderer can put a 10.5 pt baseline 0.5 pt under a box top.

The engine already knows the size of this term, in its own words (`DocxWriter.java:164-171`):

> "Auto's box is 1.15 em against the hairline's 0.069 em, so at the same `before` its baseline lands
> `LINE_BASE * (box - line)` lower — measured on the 211-document corpus as a **−3.1 pt median shift
> of the first line of every page and a −1.9 pt median on the lines below it, which is what
> `18_displacement` was reading.**"

**Why it survives.** It is the only construct left that produces what §1 measures: a per-line constant,
scaling with type size, that does **not** accumulate (the pitch `before + line` is exact — on the proof
document the declared sums are 29.05, 16.60, 16.60 pt against source pitches of 29.06, 16.58, 16.58),
and that is therefore a **rigid shift of the page**, exactly the shape all 9 current-engine sole-18
documents show in §5's proxy table. And it is renderer-dependent — Google places the baseline a shade
differently from LibreOffice — which is why 8 of those 9 pass in the proxy and fail in Google.

### Survivor 2 — the pitch-bound row is declared 10 twips under the page's pitch, on purpose

`DocxWriter.java:6601`:

```java
6601	            if (pitchBinds && footRoom && rowHeightTw > ROW_RUNG_UNDER_TW) rowHeightTw -= ROW_RUNG_UNDER_TW;
```

`ROW_RUNG_UNDER_TW = 10` (`:54`) is a **trade, not a fix**: Google lays a declared row **+0.75 pt**
(`TABLE-GAP-IS-BEFORE-RUNG-IS-10` §2: 340 → 18.15, 350 → 18.40, 360 → 19.15, against an 18.40 pt
pitch), so declaring 10 twips under the pitch lands Google on the pitch. **LibreOffice honours the
declaration** (`atLeast`, content below it), so it lays exactly 0.50 pt short per row, and that
accumulates. Measured in §6 on `306_clinical_protocol_synopsis`: **−0.50 pt per row, exactly, over 11
rows**, and a one-knob probe (330 → 340 tw) takes the page from 61 of 75 runs out to **0**.

**Why it ranks second.** It explains **1** of the 9 documents, and it is a documented, deliberate trade
whose cost was known when it landed. It is not a discovery; it is the invoice.

---

## 4. The proof target, and why this document

**`31_times_body_arial_headings`** — one of the 9, `41/42` in Google, failing only `18_displacement`
(engine `74a152e7d3fb3d26`, the tree's own), `med_dy` **2.6**, `worst_dy` **3.5**, `bad_pages [0]`,
`runs_matched 29`.

Chosen for five reasons, in order:

1. **It has no table, no rule, no image and no page break** — 0 `<w:tbl>`, 0 `w:pBdr`, 0
   `w:trHeight`, one page, 24 paragraphs (counted on the emitted `word/document.xml`: 24 `<w:p>`, 0 `<w:tbl>`, 0 `<w:trHeight>`, 0 `<w:pBdr>`, 0 page break). Every
   construct eliminated in §2 is *absent from this file*, so nothing measured on it can be attributed
   to any of them. It is the one document in the 9 where the surviving sub-cause is the only thing
   left standing.
2. **It is pure flow**, which is where Survivor 1 lives; and the same `before + hairline` declaration
   is what every table cell in the other 8 carries, so a number measured here is not a special case.
3. **Its type sizes span 8, 9, 10, 10.5, 11 and 12 pt on one page**, so the size law can be tested
   inside one document instead of across documents.
4. **Its Google row is on the tree's engine** and its median agrees with this run's proxy to **0.1 pt**
   (§5) — so the proxy is not inventing the displacement here, which is the usual objection to it.
5. The parked ruled-row branch (`BLOCKERS.md` 27 Nov 09:28) used a different document, so nothing here
   re-opens it.

---

## 5. The measurement: source y, built y, delta, for every item

Commands, in order (all local; no Drive):

```bash
cd /scratch/work/CS && bash tools/p2w-bench/pod-prep.sh                       # corpus 213/213, JDK, libs, engine
cd tools/engine-verify && java -cp "out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
     ConvertAll /scratch/work/shard /scratch/work/out                          # 9 sole-18 documents
soffice --headless -env:UserInstallation=file://$prof --convert-to pdf --outdir /scratch/work/lo <docx>
python3 /scratch/work/boxbase.py <src.pdf> <lo.pdf> <docx> --csv 31-items.csv  # the table below
python3 tools/p2w-bench/dy.py <src.pdf> <lo.pdf>                               # the dy ~ y fit
python3 /scratch/work/measure.py                                               # populations, proxy table, verdicts
```

`boxbase.py` reuses `verify_google.py`'s own matcher by spying on `extra_checks` — the same pairs the
check scores — so these rows cannot disagree with the instrument. `built_y` is the renderer's baseline
for the matched run; `delta = built_y − source_y`, positive = lower down the page.

**PROXY-ONLY (LibreOffice).** Full table, all 29 matched runs:

| # | source y | built y | delta | size | `w:before` tw | `w:line` tw | box pt | baseline below box top (em) | text |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|
| 1 | −371.79 | −368.54 | **+3.25** | 12.0 | 1230 | 13 | 0.65 | 0.314 | THE UNITED COFFEE ESTATES COMPANY LIMITED |
| 2 | −353.55 | −351.34 | **+2.21** | 8.0 | 269 | 11 | 0.55 | 0.331 | Registered Office: Kadur Post, Chikkamagaluru… |
| 3 | −342.55 | −340.34 | **+2.21** | 8.0 | 209 | 11 | 0.55 | 0.331 | CIN L01131KA1936PLC001147 · Telephone… |
| 4 | −310.43 | −307.74 | **+2.69** | 11.0 | 687 | 13 | 0.65 | 0.292 | NOTICE OF THE EIGHTY NINTH ANNUAL GENERAL… |
| 5 | −280.94 | −278.24 | **+2.70** | 10.5 | 568 | 13 | 0.65 | 0.307 | NOTICE is hereby given that the Eighty Ninth… |
| 6 | −264.36 | −261.64 | **+2.72** | 10.5 | 319 | 13 | 0.65 | 0.309 | held at the registered office of the Company… |
| 7 | −247.78 | −245.04 | **+2.74** | 10.5 | 319 | 13 | 0.65 | 0.310 | day of September, two thousand and twenty five… |
| 8 | −205.39 | −202.84 | **+2.55** | 10.0 | 823 | 13 | 0.65 | 0.307 | ORDINARY BUSINESS |
| 9 | −188.00 | −185.24 | **+2.76** | 10.5 | — | — | — | — | 1. |
| 10 | −186.94 | −185.24 | **+1.70** | 10.5 | — | — | — | — | To receive, consider and adopt the audited… |
| 11 | −170.91 | −168.14 | **+2.77** | 10.5 | 329 | 13 | 0.65 | 0.313 | 31 March 2025, together with the reports… |
| 12 | −144.00 | −141.24 | **+2.76** | 10.5 | — | — | — | — | 2. |
| 13 | −142.94 | −141.24 | **+1.70** | 10.5 | — | — | — | — | To declare a dividend of Rs. 12 per equity… |
| 14 | −100.00 | −97.24 | **+2.76** | 10.5 | — | — | — | — | 3. |
| 15 | −98.95 | −97.24 | **+1.71** | 10.5 | — | — | — | — | To appoint a director in place of Sri K. R.… |
| 16 | −82.91 | −80.14 | **+2.77** | 10.5 | 329 | 13 | 0.65 | 0.313 | for re-appointment. |
| 17 | −56.00 | −53.24 | **+2.76** | 10.5 | — | — | — | — | 4. |
| 18 | −54.95 | −53.24 | **+1.71** | 10.5 | — | — | — | — | To appoint the auditors and to fix their… |
| 19 | +9.05 | +11.76 | **+2.71** | 10.5 | 1288 | 13 | 0.65 | 0.308 | A member entitled to attend and vote… |
| 20 | +25.64 | +28.36 | **+2.72** | 10.5 | 319 | 13 | 0.65 | 0.309 | himself, and such proxy need not be a member… |
| 21 | +42.22 | +44.96 | **+2.74** | 10.5 | 319 | 13 | 0.65 | 0.310 | stamped and signed, must be deposited… |
| 22 | +58.81 | +61.56 | **+2.75** | 10.5 | 319 | 13 | 0.65 | 0.311 | commencement of the meeting. |
| 23 | +108.00 | +110.76 | **+2.76** | 10.5 | 971 | 13 | 0.65 | 0.312 | By order of the Board |
| 24 | +138.09 | +140.76 | **+2.67** | 10.5 | 587 | 13 | 0.65 | 0.304 | S. Vedavathi |
| 25 | +152.52 | +155.16 | **+2.64** | 10.0 | 267 | 13 | 0.65 | 0.316 | Company Secretary |
| 26 | +164.52 | +167.16 | **+2.64** | 10.0 | 227 | 13 | 0.65 | 0.316 | Bengaluru, 28 August 2025 |
| 27 | +199.58 | +201.96 | **+2.38** | 9.0 | 667 | 12 | 0.60 | 0.318 | Note: Members are requested to bring… |
| 28 | +376.52 | +378.56 | **+2.04** | 8.0 | — | — | — | — | United Coffee Estates Company Limited · Notice… |
| 29 | +376.52 | +378.56 | **+2.04** | 8.0 | — | — | — | — | Page 1 |

**All 29 of 29 items are displaced, all in the same direction.** min **+1.70**, max **+3.25**, median
**+2.70** pt.

The three numbers that make it a construct rather than a coincidence:

1. **It does not accumulate.** `dy.py`'s fit against page height: `dy = +2.48 − 0.00031·y`,
   `rms_resid 0.40 pt` — 0.2 pt of change across the 748 pt the 29 runs span. So it is not a leading
   error, not a per-paragraph advance error, and not a carrier that grows.
2. **It is the em, not the box.** `boxbase.py` reads the renderer's baseline below the same box top:
   **0.292–0.331 em, mean 0.312, n=19** — flat across 8, 9, 10, 10.5, 11 and 12 pt type, which is what
   a face's descent does and is *not* what a fraction of a 0.55–0.65 pt box does. The engine charges
   `0.8 × 0.65 pt = 0.050 em`. Difference **0.262 em** = **2.75 pt** at 10.5 pt; measured **+2.70**.
3. **The pitch is exact, so the error is re-injected, not compounded.** Declared `before + line` sums
   are 29.05 / 16.60 / 16.60 pt against source pitches 29.06 / 16.58 / 16.58. Every line is placed
   right; every baseline inside its box is placed wrong by the same fraction of its own size.

**The check's verdict on this document, both renderers:**

| renderer | verdict | `med_dy` | `worst_dy` | `bad_pages` | runs |
|:--|:--|--:|--:|:--|--:|
| **Google** (stored row, engine `74a152e7`, 27 Nov 02:xx) | **41/42, fails only `18_displacement`** | **2.6** | **3.5** | [0] | 29 |
| **LibreOffice** (this run, same engine) | **42/42 PASS** | **2.7** | **3.2** | [] | 29 |

Read that pair carefully, because it is the most honest thing in this file: **the proxy reproduces
Google's displacement to 0.1 pt on the median and still disagrees on the verdict.** The displacement
is real in both renderers; the difference is the last half point of delivery on the small type. At
8 pt the tolerance is 2.80 pt and the proxy's 8 pt lines sit at +2.21 — inside by 0.59 pt. Google's
`worst_dy` is 3.5, so on Google at least three runs are past their own tolerance (the budget is
`max(2, ceil(0.05·29)) = 2`, so three is a fail). **The 0.59 pt of headroom is the whole difference
between 42/42 and 41/42 on this document** — and that is an inference from the two stored numbers, not
a per-item Google measurement, because §8's instrument is missing.

---

## 6. The second survivor, measured with a control

`306_clinical_protocol_synopsis`, `46/47`, fails only `18` in Google (`med_dy` −2.3, `worst_dy` 5.4),
and it is the **one** document of the 9 that also fails in the proxy — so it can be measured without
appealing to Google at all.

Declarations, read off the emitted `word/document.xml`: **11 rows, `w:trHeight w:val="330"
w:hRule="atLeast"`** on every one; the page's own row pitch is **17.00 pt = 340 tw**.

| | first row delta | last row delta | median | runs out / 75 | fit |
|:--|--:|--:|--:|--:|:--|
| **HEAD, 330 tw (16.50 pt)** | +0.04 | **−4.96** | **−4.56** | **61** | `−4.35 − 0.01219·y`, rms 0.67 |
| probe: 330 → 340 tw (17.00 pt) | +0.04 | **+0.94** | **+0.94** | **0** | `+0.80 + 0.00394·y`, rms 0.19 |

The drift is **exactly −0.50 pt per row** and nothing else: +0.04, −0.46, −0.96, −1.46, −1.96, −2.46,
−2.96, −3.46, −3.96, −4.46, −4.96 down the eleven rows. 0.50 pt is the 10 twips `ROW_RUNG_UNDER_TW`
takes off the declaration; LibreOffice honours `atLeast` and gives nothing back. The probe is one knob
on one document (a copy of the `.docx` with `w:val` 330→340 — **the engine was not touched**), and it
removes the whole of it.

**PROXY-ONLY (LibreOffice), and the Google half of the same construct is the +0.75 pt rung already
measured in `TABLE-GAP-IS-BEFORE-RUNG-IS-10` §2.** So on this document the engine is 0.50 pt short per
row in the proxy and, by that law, 0.25 pt long per row in Google. Neither is a defect in isolation;
over eleven rows it is 4.5 pt of page.

---

## 7. Verdict

**SUPPORTED — Survivor 1 is the dominant remaining sub-cause, and here is the number.**

> On `31_times_body_arial_headings`, **every one of the 29 matched runs is displaced downward, +1.70 to
> +3.25 pt, median +2.70**, with a fit against page height of `dy = +2.48 − 0.00031·y` (rms 0.40) — a
> rigid shift, not a drift. The renderer places each baseline **0.312 em** below the top of its exact
> line box (0.292–0.331 over six type sizes, n=19); the engine charges `LINE_BASE × box` = **0.050 em**
> because the box it writes is the hairline `w:line` (11–13 tw). The 0.26 em difference is 2.7 pt at
> 10.5 pt type, it is the same on every line, and it is the only construct left on a page with no
> table, no rule, no image and no page break.

What the number does **not** say, stated so it cannot be read as more than it is:

* It is **proxy-measured**. The Google-side evidence for this document is the stored row (`med_dy 2.6`,
  `worst_dy 3.5`, 41/42), which agrees with the proxy's median to 0.1 pt but disagrees on the verdict.
* The dominance is **over the 9 documents that fail only `18_displacement` on the tree's engine**, of
  which 8 are rigid and this construct explains them and 1 (306) is the rung. **The other 20 of the
  29 sole-18 rows are stale** and were not re-measured here (§1).
* 2 of the 32 current-engine documents that fail `18` at all are still page-scale (`324` at 276.6 pt,
  `330` at 83.9 pt). They are not this construct and are not claimed as such.
* No engine change is proposed here. This is a measurement: `app/` is untouched, nothing is committed
  to the engine, nothing was deleted, and the user's Drive was not written to (no file was imported).

---

## 8. What this run could not do, and why (the instrument, not the physics)

**The Google render is unreachable in this session.** The repo's Google loop is `gverify.py --stage`
then a platform `upload` then `GOOGLEDRIVE_CREATE_FILE` / `EXPORT` / `DOWNLOAD`. The platform `upload`
tool — the only thing that produces the `s3key` those Drive calls take — **is not in this session's
tool list**, and it cannot be reached through `tool_search`. Four attempts, all refused at the same
place:

| attempt | result |
|:--|:--|
| `GOOGLEDRIVE_CREATE_FILE(..., file_to_upload.s3key=/scratch/work/p2w/gverify/stage/…docx)` | `HTTP 403 … the file key does not belong to this project or session` |
| same, file copied to `/scratch/output/gv/…docx` | same 403 |
| same, file at `/scratch/output/…docx` (the exact path `GVERIFY-BRIEF.md` prescribes) | same 403 |
| `GOOGLEDRIVE_UPLOAD_FILE` / `RESUMABLE_UPLOAD` | same `file_uploadable` contract, same key |

So: **no Google Doc was created, no Drive file was written, and every per-item number in §5 and §6 is
LibreOffice — proxy-only.** The Google numbers quoted are the stored rows in `benchmarks/gverify/`,
stamped `74a152e7d3fb3d26`, which is this tree's own engine fingerprint — quoted, not measured here.

Two smaller limits: `tablechecks.py` is not on this pod, so checks 62-66 abstain in every `compare()`
run (it does not touch 18); and `collect_lo`'s stored rows in `benchmarks/gverify-lo/` are all stamped
`a4d8fca469bba636`, so **they cannot be compared with this run's LO renders** — the 47/47 the store
holds for `306` is a pre-rung render, and on the current engine that document is 61-of-75 out in the
proxy. That is the rung's cost, visible for the first time in an LO row.

---

## 9. Open questions — things only the repo's owners can settle

1. **Is the platform `upload` tool available to the run that reads this?** If it is, the one thing
   worth doing next is this exact measurement again through Drive on `31_times_body_arial_headings`:
   the proxy and Google agree on the median to 0.1 pt, so the per-item Google table is the only thing
   that would turn §5's last paragraph from an inference into a measurement.
2. **`LINE_BASE` has never been probed with a box shorter than the em.** The 27 Nov probe covered
   9.2–37 pt boxes at 10.5–16 pt type — every one of them at or above the em. The engine writes 0.55 pt
   boxes. Should the hairline be given a *baseline-carrying* minimum (a box of, say, 1.0 em with the
   gap moved into `w:before`, where it is honoured 1:1), or should `LINE_BASE` become a function of
   `box/em`? Both are engine decisions and neither is measured here.
3. **Does the `regress.py` gate see the rung's proxy cost?** `306_clinical_protocol_synopsis` is 47/47
   in the stored LO row (`a4d8fca4`) and 61-of-75-out in the proxy on `74a152e7`. If the gate compares
   against a stale LO row, the rung's −0.50 pt/row cannot be refused by it.
4. **Which of the 20 stale sole-18 rows still fail on `74a152e7`?** They carry `a4d8fca4` and
   `025fe9de`. Until they are re-measured, "29 documents fail only this check" overstates the current
   engine by a factor of three, and any projection of the class's worth inherits the error.
