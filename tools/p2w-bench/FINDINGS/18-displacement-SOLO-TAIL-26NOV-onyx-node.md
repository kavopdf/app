# 18_displacement SOLO-TAIL: the 14 carry no spacer — the construct is the table ROW HEIGHT, and the table's own rules decide its sign

**26 Nov 2026, slot 03:1x UTC.** Measurement only. No engine change, no instrument change, no file
deleted. Every number below is read off a **live Google render** of the emitted `.docx`, not modelled.

---

## 0. The answer, in one paragraph

Of the 25 documents that fail only `18_displacement`, 11 carry a refused table spacer and 14 do not.
**On those 14 the displacement is the table row height.** `DocxWriter` declares every row
`<w:trHeight w:val="D" w:hRule="atLeast"/>`; Google does not lay `D`, it lays the declaration snapped
to a **0.75 pt ladder** — and, when the table is *ruled* (`<w:insideH w:val="single"/>`), it charges
**one whole rung on top**. The measured law is

    laid = 0.75 * ( round(D/0.75) + 1 )      table ruled   (insideH single)
    laid = 0.75 * ( round(D/0.75)     )      table unruled (insideH nil)

13 measured (declared, laid) points: **10 exact, 3 off-ladder** (all unruled, content-bound), median
residual 0.00 pt, rms 0.25 pt. Because the error per row is one-signed and repeats on every row, it
accumulates down the table: **+18.50 pt predicted on `320_balance_sheet_statutory`, +17.00 measured**;
**−3.25 predicted on `16_right_aligned_amounts_txtpos`, −3.95 measured**. Across the 11 documents that
have a table, predicted Σ(laid − D) against measured cumulative row excess has **rms residual 2.10 pt**
and agrees in sign on 10 of 11. Two of the 14 (`31_times_body_arial_headings`,
`70_magazine_drop_cap_photo_caption`) have no table at all; their displacement is the per-line
`w:line ... lineRule="exact"` box, measured at **+0.09 pt/line at 11 pt** and **−0.03 pt/line at 9 pt**
against the law `max(0.069·size, (L/240)·lineHeight) − L/20` (+0.109 / −0.029 predicted).

**The class cannot clear by fixing the spacer.** The spacer was one instance of the same family —
a vertical *length* carried in a property Google reads as something else — and the row height is the
general case of it, on every table row of every document, not on one paragraph.

---

## 1. What I believed when I started, and where each belief came from

| # | belief | source | verdict after this run |
|---|---|---|---|
| 1 | the 14 exist, and their displacement is "spread over the whole page rather than stepped" | `FINDINGS/18_displacement-CLAUSE-NOT-DS-074250-71ae.md` §6 | **confirmed**, and now named |
| 2 | the 0.75 pt row ladder is *refuted* for these 14 ("agrees in sign on only 15 of 25") | same file, §6 | **refuted as stated.** It agrees in sign on 10 of 11 here. That check multiplied `0.75 × <w:tr>` — a *per-row constant* — and compared it to a *page-span slope*. Both quantities were wrong; the ladder is real |
| 3 | Google's laid row height is `0.75·(round(D/0.75)+1)`, unconditionally, "hRule never enters it" | `FINDINGS/18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md` §2 | **half right.** The ladder is right; the `+1` is **conditional on the table being ruled**, which that run never varied |
| 4 | the refused-spacer patch is "in flight" | the task brief | **stale.** It landed at `9f0a8207` (02:54 today, ancestor of HEAD). At HEAD **0 of the 25 emit a refused spacer any more** — the census below is re-derived from pre-patch `.docx`, because it can no longer be read out of HEAD |

---

## 2. What I measured, and the command that produced it

### 2.1 The 14, re-derived (not carried over)

    python3 -c "import json,glob; print(sorted(d['name'] for f in glob.glob('benchmarks/gverify/*.json')
                for d in [json.load(open(f))] if d.get('failed')==['18_displacement']))"
    -> 25 documents, exactly the list in 074250-71ae

    python3 /scratch/work/probe/census.py     # strict shape: empty <w:p>, w:before="0", w:line>1,
                                              # w:lineRule="exact", <w:sz w:val="2"/> in the paragraph rPr
    -> 11 of the 25 carry >=1 refused spacer, 14 carry none

My independent census reproduces the committed one to the point: `403_crossword_puzzle` 58.15 pt,
`68_journal_wide_table_spanning` 144.00, `72_bank_statement_no_rules_right_amounts` 18.30,
`bus-timetable-station-left-times-right` 6.35, `electricity-bill` 26.20 (3), `insurance-policy-schedule`
26.80 (3), `marksheet-subject-left-marks-right` 36.30 (2), `mobile-bill` 25.00 (3),
`table-inside-two-column-page` 4.00, `table-with-no-header-row` 12.35,
`two-tables-stacked-with-no-gap` 12.35 — the same 11, the same counts, the same pt.

**The 14:**

    B (spacer present but SPENT, i.e. w:before != 0):  16_right_aligned_amounts_txtpos,
      303_discharge_summary, 320_balance_sheet_statutory, 325_demat_holdings_statement,
      362_price_list_dense, 36_embedded_subset_font, 402_calendar_month_grid,
      74_balance_sheet_indented_subitems, balance-sheet-two-columns-of-figures,
      report-2col-table-spanning-both-columns                                    (10)
    C (no table-top spacer at all):  31_times_body_arial_headings,
      70_magazine_drop_cap_photo_caption, 71_invoice_space_aligned_no_rules,
      price-list-2col-dense-right-aligned                                        ( 4)

### 2.2 A live Google render for all 14 — and it reproduces the store to 0.03 pt

The wall the last three runs hit (`GOOGLEDRIVE_UPLOAD_FILE` needs an `s3key` this project cannot mint)
has a way round it that does not need an upload at all:

1. the engine's `.docx` for these documents is already a blob in Drive (`1qAl4xzz…`, 25 Nov);
2. **`GOOGLEDRIVE_COPY_FILE_ADVANCED` with `mimeType=application/vnd.google-apps.document`** converts a
   blob into a Google Doc;
3. `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` (PDF) exports it.

Before using a blob I hashed its `word/document.xml` against the `.docx` this pod builds from HEAD:
**all 14 are byte-identical** (and for the 5 that already had a 03:11 Google Doc, that one is identical
too). So every render below is a render of the file HEAD emits today, not of an older engine.

    python3 /scratch/work/probe/measure.py <src.pdf> <google-export.pdf> <docx> probe/out/<doc>.json
    # reuses verify_google.compare()'s own matcher by intercepting extra_checks, so it cannot disagree
    # with the instrument it is explaining

| document | stored `med_dy` | measured | stored `worst_dy` | measured | runs |
|---|--:|--:|--:|--:|--:|
| 16_right_aligned_amounts_txtpos | −1.6 | **−1.56** | 3.4 | **3.41** | 64 |
| 303_discharge_summary | −0.2 | **−0.20** | 4.1 | **4.10** | 45 |
| 320_balance_sheet_statutory | 8.2 | **8.24** | 19.4 | **19.37** | 73 |
| 325_demat_holdings_statement | 3.8 | **3.78** | 38.1 | **38.13** | 84 |
| 362_price_list_dense | −2.8 | **−2.81** | 5.4 | **5.37** | 257 |
| 36_embedded_subset_font | 1.7 | **1.71** | 3.5 | **3.52** | 29 |
| 402_calendar_month_grid | 1.4 | **1.42** | 6.5 | **6.49** | 46 |
| 31_times_body_arial_headings | 2.6 | **2.62** | 3.5 | **3.54** | 29 |

Nine of nine documents that carry a stored displacement record reproduce it to ≤0.03 pt on the median
and the worst, with the identical matched-run count. The other five (74, balance-sheet-2col,
report-2col, 70, 71, price-list) carry no stored `displacement` block; their numbers are new.

### 2.3 The shape: no step anywhere, one-signed and cumulative

`python3 /scratch/work/probe/profile.py` collapses each render to its distinct y-levels in reading order
and prints the dy profile. Every one of the 14 is a **ramp**, not a step:

    320  -2.6 -2.0 +0.2 +2.2 +4.2 +6.2 +8.2 +10.2 +12.2 +14.2 +16.1 +17.1 +18.1 +18.9
    325  -3.0 -1.6 -1.5 -1.2 -0.5 +0.0 +0.8 +1.5 +2.3 +3.0 +3.8 +4.5 +5.3 +5.5 +5.8 +7.1 +8.1 +9.1 +10.1 +11.4
    362  -2.6 +1.4 -1.0 -1.3 -1.6 -1.9 -2.2 -2.5 -2.8 -3.1 -3.4 -3.7 -4.0 -4.3 -4.6 -4.9
    16   +0.1 +0.2 +0.2 +0.3 +0.4 +0.5 -0.7 +0.0 -1.2 -0.5 -1.7 -1.9 -2.2 -1.5 -2.7 -2.9 -3.2 -3.4 -2.7 -2.5 -2.3

The largest single step in any of the 14 is **4.72 pt** (`71_invoice_space_aligned_no_rules`, at a
pitch-18.0 row) — against 111 pt for the refused spacer on `68_journal`. **There is no spacer-shaped
discontinuity in this population.** What there is, is a slope: dy changes once per laid vertical unit.

### 2.4 The ledger: dy is flat inside a row and moves only at a row boundary

`python3 /scratch/work/probe/ledger2.py` walks the distinct y-levels, drops the transitions whose step
exceeds 3 pt (those are `Settlement T+1`-style duplicate-text mispairs, not displacement — see §6),
and splits the remaining steps into those whose **source pitch equals a declared `w:trHeight`** and all
others:

| document | table rows | declared D (pt) | E_row | E_other | row share | span |
|---|--:|---|--:|--:|--:|--:|
| 320_balance_sheet_statutory | 21 | 14.0 ×16, 13.0 ×5 | **+17.00** | +4.90 | 0.78 | 21.97 |
| 325_demat_holdings_statement | 12 | 15.0 ×8, 14.0 ×4 | **+8.25** | +6.09 | 0.58 | 44.00 |
| 303_discharge_summary | 5 | 15.0 ×5 | **+3.00** | +4.07 | 0.42 | 7.07 |
| 402_calendar_month_grid | 6 | 62.0 ×6 | +1.58 | +6.04 | 0.21 | 10.75 |
| 36_embedded_subset_font | 7 | 20.0 ×7 | **+2.89** | +0.01 | 1.00 | 3.45 |
| 74_balance_sheet_indented_subitems | 10 | 17.0 ×10 | +1.08 | +3.03 | 0.26 | 4.67 |
| 71_invoice_space_aligned_no_rules | 14 | 18.0 ×10, 16.0 ×4 | −1.65 | +1.63 | 0.50 | 6.57 |
| 16_right_aligned_amounts_txtpos | 13 | 19.0 ×13 | **−3.95** | +1.56 | 0.72 | 3.95 |
| 362_price_list_dense | 29 | 8.4 ×29 | **−4.05** | +1.28 | 0.76 | 6.81 |
| balance-sheet-two-columns-of-figures | 16 | 11.6 ×11, 12.0 ×4, 16.0 | −1.88 | −2.05 | 0.48 | 8.51 |
| price-list-2col-dense-right-aligned | 41 | 16.4 ×37, 12.0 ×4 | 0.00* | +6.87 | — | 7.64 |
| report-2col-table-spanning-both-columns | 7 | 18.0, 19.0 | 0.00* | +8.25 | — | 8.71 |
| 31_times_body_arial_headings | 0 | — | 0.00 | +1.26 | 0 | 2.21 |
| 70_magazine_drop_cap_photo_caption | 0 | — | 0.00 | +2.30 | 0 | 2.48 |

`E_row`/`E_other` are the summed `dy` steps at row-pitch and non-row-pitch transitions; `row share` is
`|E_row| / (|E_row| + |E_other|)`.

\* `price-list-2col-dense-right-aligned` and `report-2col-table-spanning-both-columns` are marked zero
because their **source row pitch is not the declared height** (15.94 against 16.4; 18.4 against 18.0) —
the engine over-declares and the row is content-bound, so the pitch test cannot see the row. Both are
still table rows: their displacement is charged at the dominant repeated pitch (15.94 ×39 for
price-list, 18.4 ×8 and 12.4 ×18 for report-2col), i.e. per row / per cell line, and never at a spacer.

### 2.5 The law: 0.75 pt ladder, and the table's own rules pick the branch

Per-document dominant row pitch, measured in the render, against the declaration:

| document | D | laid (measured) | ruled? (`insideH`) | `round(D/0.75)` | `+1` | law |
|---|--:|--:|---|--:|--:|---|
| 303_discharge_summary | 15.00 | 15.75 | **single** | 20 | 21 | +1 ✓ |
| 320_balance_sheet_statutory | 14.00 | 15.00 | **single** | 19 | 20 | +1 ✓ |
| 320_balance_sheet_statutory | 13.00 | 13.50 | **single** | 17 | 18 | +1 ✓ |
| 325_demat_holdings_statement | 15.00 | 15.75 | **single** | 20 | 21 | +1 ✓ |
| 325_demat_holdings_statement | 14.00 | 15.00 | **single** | 19 | 20 | +1 ✓ |
| 402_calendar_month_grid | 62.00 | 62.89 | **single** | 83 | 84 | +1 ✓ (63.00 predicted, 0.11 res) |
| 16_right_aligned_amounts_txtpos | 19.00 | 18.75 | nil | 25 | 26 | plain ✓ |
| 362_price_list_dense | 8.40 | 8.25 | nil | 11 | 12 | plain ✓ |
| 74_balance_sheet_indented_subitems | 17.00 | 17.25 | nil | 23 | 24 | plain ✓ |
| 71_invoice_space_aligned_no_rules | 18.00 | 18.00 | nil | 24 | 25 | plain ✓ |
| 71_invoice_space_aligned_no_rules | 16.00 | 15.75 | nil | 21 | 22 | plain ✓ |
| 36_embedded_subset_font | 20.00 | 20.57 | nil | 27 | 28 | off-ladder, +0.32 |
| balance-sheet-two-columns-of-figures | 11.60 | 11.28 | nil | 15 | 16 | off-ladder, +0.03 |
| price-list-2col-dense-right-aligned | 16.40 | 15.66 | nil | 22 | 23 | off-ladder, −0.84 |

**10 of 13 exact.** The three misses are all unruled and all content-bound (the cell needs more or less
room than the rung above it). The branch is decided by `w:insideH`: **every ruled table takes the rung,
every unruled table that lands on the ladder does not** — 10 for 10, no counter-example in this
population. That is also exactly the belief `9f0a8207` committed ("charge the 0.75 pt row excess only
to ruled tables"); this run is the independent measurement of it, and it says the belief is right.

**Doc-level residual.** Predicted `Σ(laid − D)` over the document's rows against the measured cumulative
row excess (`python3 /scratch/work/probe/final.py`), 11 documents:

    n=11   rms residual 2.10 pt   max |residual| 4.42 pt (402_calendar_month_grid)   sign agrees 10 of 11

    303 +3.75/+3.00   320 +18.50/+17.00   325 +10.00/+8.25   402 +6.00/+1.58
     16 −3.25/−3.95   362 −4.35/−4.05     74 +2.50/+1.08      36 +1.75/+2.89
     bs −4.10/−1.88    71 −1.00/−1.65     pl +3.70/0.00        (predicted / measured)

### 2.6 The two documents with no table

`31_times_body_arial_headings` and `70_magazine_drop_cap_photo_caption` contain no table. Their dy is a
**constant offset acquired in the first few lines and then flat** (+2.1 → +3.4; +0.8 → +3.1), i.e. no
accumulation at all. What moves is the per-line box, at a rate of

    excess / line = max(0.069·size, (L/240)·lineHeight(face,size)) − L/20

| document | size | `w:line` L | predicted | measured |
|---|--:|--:|--:|--:|
| 31_times_body_arial_headings | 11 pt | 13 tw (0.65) | **+0.109** | **+0.09 / +0.10** |
| 70_magazine_drop_cap_photo_caption | 9 pt | 13 tw (0.65) | **−0.029** | **−0.03** |

Residual ≤0.02 pt per line. This is the *same* law as the refused spacer (`FINDINGS/w-line-exact-GOOGLE-CHARGE-075617-f0cc.md`),
at 1/10 the magnitude, applied to every line instead of one spacer paragraph — which is the point of
the whole family.

---

## 3. What is now true — the cluster table

| cluster | construct (the property in `word/document.xml`) | docs | median `dy` | share of the document's displacement |
|---|---|--:|--:|--:|
| A1 | `<w:trHeight w:hRule="atLeast"/>` on a **ruled** table — Google lays `0.75·(round(D/0.75)+1)` | **4** — 303, 320, 325, 402 | **+2.60 pt** | median **0.50** (0.21–0.78) |
| A2 | `<w:trHeight w:hRule="atLeast"/>` on an **unruled** table — Google lays `0.75·round(D/0.75)`, sign follows the ladder | **7** — 16, 362, 74, 36, balance-sheet-2col, 71, price-list-2col | **+1.06 pt** (range −2.81 … +2.20) | median **0.50** (0.26–1.00) |
| A3 | ruled table whose rows hold **several lines**: the carrier is the cell's `w:line` box, not `w:trHeight` | **1** — report-2col-table-spanning-both-columns | **+2.80 pt** | 0.00 at row pitch; 8.25 pt of the 8.71 span is charged per cell line |
| B | **no table at all**: the per-line `w:line … lineRule="exact"` box | **2** — 31, 70 | **+2.81 pt** | 0.00 at row pitch; whole displacement is the line box + a first-block offset |

**4 + 7 + 1 + 2 = 14.** All four clusters are one construct family — *a vertical length carried in a
property Google resolves by its own rule* — and none of them is the refused spacer.

---

## 4. The measured law, stated so it can be used

    # table rows  (D = w:trHeight w:val/20 pt, hRule="atLeast")
    ruled   (w:insideH w:val="single"):   laid = 0.75 * (round(D/0.75) + 1)
    unruled (w:insideH w:val="nil"):      laid = 0.75 *  round(D/0.75)
    # 13 points, 10 exact, 3 off-ladder (unruled + content-bound): median residual 0.00, rms 0.25 pt
    # doc-level: rms 2.10 pt over 11 documents, max 4.42, sign correct on 10 of 11

    # body / cell lines  (L = w:line tw, size = w:sz/2 pt)
    charged = max(0.069*size, (L/240)*lineHeight(face,size))     # what Google lays
    written = L/20                                               # what the engine places against
    excess  = charged - written                                  # +0.109 at 11 pt, -0.029 at 9 pt
    # residual <= 0.02 pt per line

Consequence for a fixer, stated as arithmetic rather than advice. The target is the row pitch the source
drew, `T`, and `T` must itself be on the 0.75 ladder (18.40 is not; 18.75 is — that is what
`ROW-GROWTH-075-QUANTUM-LAW` proved and it survives this run):

    ruled table   : declare D = T - 0.75   -> round(D/0.75) = T/0.75 - 1 -> laid = 0.75*(T/0.75) = T
                    e.g. T = 15.00, declare 14.25 (285 tw); today 303/325 declare 15.00 and get 15.75
    unruled table : declare D = T          -> laid = 0.75*round(T/0.75) = T
                    e.g. T = 18.75, declare 18.75 (375 tw); today 16 declares 19.00 and gets 18.75

The engine already computes `rowHeightTw = max(rowTwHere, rowLineTw)`; what it never does is subtract
the branch's rung from the result, or round it onto the ladder at all. It emits the source pitch
verbatim (`D = T`), which is correct only for an unruled table whose pitch is already on the ladder —
and even then only if the cell never binds. That is the whole of the 14.

---

## 5. What would prove this wrong

- **A ruled table that lays `0.75·round(D/0.75)`** (no rung). One counter-example kills the branch rule;
  it would also contradict `9f0a8207`'s own premise.
- **An unruled table that gains the rung.** Same.
- **A document whose `dy` is flat across its rows** while `laid ≠ D` — that would mean the row pitch is
  not what carries the displacement.
- **A per-document residual above ~5 pt** on a document whose rows are all one declared height and whose
  cells never wrap. `402_calendar_month_grid` already sits at 4.42 pt and is the one to watch.
- **The line law failing on a size the corpus does not have.** It is fitted on 11 pt and 9 pt only.

---

## 6. What I could not measure, and why

- **`325_demat_holdings_statement`'s `worst_dy` of 38.13 pt is an artefact, not displacement.** The
  document has six cells reading `Settlement T+1`; the matcher pairs them across rows, so one run reads
  +38.13 and its neighbour −29.00 in the same column. The stored record carries the same 38.13. The real
  profile ends at +11.4. Every ledger in this file drops steps > 3 pt for that reason (4 dropped
  transitions, listed in `probe/ledger2.json`).
- **The branch selector for the 3 off-ladder unruled points** (36, balance-sheet-2col, price-list-2col)
  is not determined. They are content-bound; whether the content or the declaration decides, and by how
  much, needs a controlled build with `hRule="exact"` and a varying cell, which is an engine experiment,
  not a reading.
- **The first-line offset.** The first matched line sits at dy −4.3 … +2.1 pt across the 14, and none of
  the four laws here predicts it. It is the page-top `w:before` / `w:pgMar w:top="0"` construct
  (`DOCS-ROOT-CAUSES-24NOV.md` §18_displacement item 2) and it is *not* what these 14 fail on — it is
  ≤4.3 pt, under the check's 4.5 pt cap — but it is unexplained here.
- **The 62-document refused-spacer census cannot be re-derived at HEAD.** `9f0a8207` spends those gaps
  into `w:before`, so at HEAD **0 of the 25 emit the refused shape**. §2.1's census is read out of the
  **pre-patch** `.docx` (Drive blobs of 25 Nov), which is the only place the construct still exists. A
  run that tries to re-derive it from HEAD will get zero and conclude the class is gone; it is not.
- **Google's row law above ~4 rungs.** The largest declaration measured is 62.00 pt (`402`), one point.
  Nothing here tests whether the rung rule holds for very tall rows.

---

## 7. How to reproduce every number in this file

    bash tools/install-gate.sh                      # warm pod; corpus + jdk + libs + engine + scipy

    # 1. the 14 (list, refused-spacer census)         -> probe/census.py, probe/census.json
    # 2. convert the 25 from HEAD
    java -cp out:libs/... ConvertAll /scratch/work/shard25 /scratch/work/docx25
    # 3. a live Google render of each (no upload needed):
    #    GOOGLEDRIVE_FIND_FILE name='<doc>.docx' in folder 1qAl4xzzU-FOl6E2nAv8PuZ6GaBpjsXCA
    #    GOOGLEDRIVE_COPY_FILE_ADVANCED  fileId=<blob>  mimeType=application/vnd.google-apps.document
    #    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE fileId=<copy> mimeType=application/pdf
    # 4. per-line dy in that render                   -> probe/measure.py   -> probe/out/<doc>.json
    # 5. shape / ledger / law                         -> probe/profile.py, probe/ledger2.py,
    #                                                   probe/tablepitch.py, probe/laws.py, probe/final.py

The probe scripts live in `/scratch/work/probe/` in the run's sandbox and are read-only with respect to
the engine: none of them writes to `app/`, `tools/p2w-bench/*.py`, or the corpus.

---

## 8. The one sentence the next run needs

**The 14 carry no spacer — their displacement is `w:trHeight w:hRule="atLeast"` re-laid by Google on a
0.75 pt ladder that adds one whole rung when the table is ruled (`w:insideH` single) and snaps to the
nearest rung when it is not, so a fixer must declare a row height the ladder already lands on, and must
not expect the refused-spacer patch to move any of them.**
