# `18_displacement`, the COUNT clause: what it actually counts, and the one engine number it is measuring

**27 Nov 2026, 01:25 IST · explore run · repo `kavopdf/app` @ HEAD (shallow clone) · Google Docs, not LibreOffice**
**Nothing under `app/src/`, `tools/` or `benchmarks/` was touched. No engine change, no commit, no push.**

This file answers one question: the documents that fail `18_displacement` and nothing else, with a
displacement inside 7 pt, are failing the check's **count** clause — *what* is being counted, and *which
engine number* produces the count. The answer is measured on Google's own render of the same `.docx`
the stored verdicts were taken on, not modelled.

**Headline.** The count clause counts displaced **runs**, and no run is missing, duplicated or split:
every one of the 14 documents lays the same text lines as its source. What moves is the **vertical
pitch**, and 10 of the 14 carry the movement in a table: Google lays a table row at
`0.75 x round((w:trHeight + rule) / 0.75)` pt, while the engine declares the page's own pitch and charges
the page budget that declared number (`DocxWriter.java:6541`, `:6550`, written at `:6631`). The
difference is up to +0.75 pt a row and one-signed, so it accumulates down the table and pushes every line
below it out of tolerance.

---

## 1. The predicate, in words and in code

`tools/p2w-bench/verify_google.py`, the `18_displacement` block. Per page, over the **upright** source
runs (`|sin(angle)| <= 0.02`) that have a matched render run:

    tol(size)   = clamp(0.35 * size, 1.5, 4.5)              # verify_google.py:5863-5864
    ds          = [(g.ry - r.ry, r.size) for each matched pair on the page]   # :5874-5875
    if not flat_src: continue            # nothing upright on the page: not this check's page  # :5880-5881
    if not ds:      bad page             # upright text and none of it matched: lost page      # :5885-5887
    n_out       = count of runs with |dy| > tol(size)                          # :5888
    worst_here  = max(|dy| / tol(size))                                        # :5892
    bad page if  n_out > max(2, ceil(0.05 * n))      <- THE COUNT CLAUSE       # :5893
              or n_out == n                          <- every run out
              or worst_here > 2.0                    <- THE TAIL CLAUSE        # :5894 (TAIL_FACTOR = 2.0, :5869)

So the **count clause** is, in words:

> *a page fails when more than `max(2, ceil(5% of the page's matched upright runs))` of those runs sit
> further than `clamp(0.35 x font-size, 1.5, 4.5)` pt from the baseline the source drew — i.e. more than
> two runs out on any page with 40 or fewer runs, and 5% of them above that.*

The **tail clause** is a different question: it is a **ratio**, not a distance — one run past **twice its
own tolerance**. That is the distinction that matters below, because "within 7 pt" is not the same
statement as "the tail clause did not fire".

## 2. The population — and one correction to the premise

Store: `benchmarks/gverify/*.json` (213 rows, `displacement` block carries `med_dy`, `worst_dy`,
`bad_pages`, `runs_matched`; the clause itself is **not** stored, which is why it had to be re-measured).

    documents whose ONLY failing check is 18_displacement           25
    of those, worst_dy <= 7.0 pt (the "within 7 pt" population)     14

All 14 were then re-rendered through Google and re-run through the check's own matcher, per page, with
each clause evaluated separately (`/scratch/work/analyze.py`, which imports `verify_google.py` and spies
on `extra_checks`, exactly as `dy.py` does — it cannot disagree with the instrument).

| # | document | stored med/worst/runs | re-measured med/worst/runs | n | n_out | allowance | worst_here | clause |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | `16_right_aligned_amounts_txtpos` | -1.6 / 3.4 / 64 | -1.56 / 3.41 / 64 | 64 | 7 | 4 | 1.08 | **COUNT** |
| 2 | `303_discharge_summary` | -0.2 / 4.1 / 45 | -0.20 / 4.10 / 45 | 45 | 9 | 3 | 1.67 | **COUNT** |
| 3 | `31_times_body_arial_headings` | 2.6 / 3.5 / 29 | 2.62 / 3.54 / 29 | 29 | 4 | 2 | 1.20 | **COUNT** |
| 4 | `362_price_list_dense` | -2.8 / 5.4 / 257 | -2.81 / 5.37 / 257 | 257 | 181 | 13 | 2.56 | COUNT + TAIL |
| 5 | `36_embedded_subset_font` | 1.7 / 3.5 / 29 | 1.71 / 3.52 / 29 | 29 | 8 | 2 | 1.26 | **COUNT** |
| 6 | `402_calendar_month_grid` | 1.4 / 6.5 / 46 | 1.42 / 6.49 / 46 | 46 | 5 | 3 | 2.65 | COUNT + TAIL |
| 7 | `70_magazine_drop_cap_photo_caption` | 3.0 / 3.3 / 24 | 3.00 / 3.27 / 24 | 24 | 8 | 2 | 1.18 | **COUNT** |
| 8 | `71_invoice_space_aligned_no_rules` | 1.1 / 6.7 / 72 | 1.06 / 6.69 / 72 | 72 | 29 | 4 | 2.39 | COUNT + TAIL |
| 9 | `72_bank_statement_no_rules_right_amounts` | 1.1 / 4.8 / 80 | 1.13 / 4.79 / 80 | 80 | 11 | 4 | 1.71 | **COUNT** |
| 10 | `74_balance_sheet_indented_subitems` | 2.2 / 4.2 / 54 | 2.20 / 4.23 / 54 | 54 | 12 | 3 | 1.51 | **COUNT** |
| 11 | `balance-sheet-two-columns-of-figures` | -2.3 / 5.1 / 94 | -2.34 / 5.14 / 94 | 94 | 47 | 5 | 2.10 | COUNT + TAIL |
| 12 | `bus-timetable-station-left-times-right` | 1.8 / 3.8 / 177 | 1.79 / 3.84 / 177 | 177 | 35 | 9 | 1.70 | **COUNT** |
| 13 | `price-list-2col-dense-right-aligned` | 2.1 / 5.3 / 253 | 2.09 / 5.32 / 253 | 253 | 82 | 13 | 2.24 | COUNT + TAIL |
| 14 | `report-2col-table-spanning-both-columns` | 2.8 / 6.8 / 90 | 2.80 / 6.79 / 90 | 90 | 49 | 5 | 2.77 | COUNT + TAIL |

**Every one of the 14 fires the count clause — and 6 of them also fire the tail clause.** That is the
correction the premise needs: *"fails only the count clause"* is true of **8** documents, not 14. The
other 6 sit inside 7 pt but their worst run is 6.5-6.8 pt on 7-8 pt type, whose tolerance is 2.45-2.8 pt,
so `|dy|/tol` crosses 2.0 and the tail clause fires on the same runs the count clause counts. The
`worst_dy <= 7 pt` filter is a *distance* filter and the tail clause is a *ratio* filter; they are not
the same cut, and no future run should treat them as one.

## 3. The count delta — there is none, and that is the finding

The check's count is a count of **runs**, and the run census says the render carries every run the source
draws. Per document: source runs / render runs / source runs with no counterpart / render runs with no
counterpart, and the text of every uncounterparted render run:

| document | src runs | gd runs | src unmatched | gd unmatched | what the unmatched render runs are |
|---|---:|---:|---:|---:|---|
| `16_right_aligned_amounts_txtpos` | 64 | 70 | 0 | 6 | 6 x U+200B |
| `303_discharge_summary` | 45 | 50 | 0 | 5 | 5 x U+200B |
| `31_times_body_arial_headings` | 29 | 34 | 0 | 5 | 5 x U+200B |
| `362_price_list_dense` | 258 | 259 | 1 | 2 | `'HANDLIN'`, `'G'` — one word split across runs |
| `36_embedded_subset_font` | 29 | 31 | 0 | 2 | 2 x U+200B |
| `402_calendar_month_grid` | 46 | 52 | 0 | 6 | 6 x U+200B |
| `70_magazine_drop_cap_photo_caption` | 24 | 25 | 0 | 1 | 1 x U+200B |
| `71_invoice_space_aligned_no_rules` | 73 | 79 | 1 | 7 | 4 x U+200B + 3 runs of real text re-split |
| `72_bank_statement_no_rules_right_amounts` | 80 | 81 | 0 | 1 | 1 x U+200B |
| `74_balance_sheet_indented_subitems` | 54 | 62 | 0 | 8 | 8 x U+200B |
| `balance-sheet-two-columns-of-figures` | 96 | 98 | 2 | 4 | 2 x U+200B + `'(  in crore unless'` |
| `bus-timetable-station-left-times-right` | 177 | 182 | 0 | 5 | 5 x U+200B |
| `price-list-2col-dense-right-aligned` | 254 | 256 | 1 | 4 | 2 x U+200B + `'Cable Gland 3/4 in'` |
| `report-2col-table-spanning-both-columns` | 90 | 94 | 0 | 4 | 4 x U+200B |

**Zero source runs are lost on 11 of the 14**, and the 1-2 losses on the other three are a word split
across two runs (`HANDLIN` + `G`), not a lost line. The surplus render runs are **U+200B zero-width
spaces** — Google's DOCX importer emits one per table cell and per some paragraph joins. They carry no
ink and no width; they are the mechanism by which a naive line count reads "google 47 lines vs source 45"
and concludes a line was added. It was not.

So the answer to *"is Google adding a line, dropping a line, or splitting one line into two?"* is
**none of the three**. There is no count delta in lines at all. The delta is in the **vertical gaps
between the same lines**, and the check counts the runs whose baselines that displacement has pushed
past their tolerance.

## 4. Three rendered pages, measured — where the gap appears

Measured with PyMuPDF on the corpus PDF and on **Google's own PDF export of the same `.docx`**, matched
line by line, and confirmed against a 150 dpi render of the medication table on `303_discharge_summary`
(the two crops differ only in that Google's rows get progressively taller and its rules thicker).

### 4a. `303_discharge_summary` — the delta is inside a 4-row table, +0.75 pt a row

    source pitch 15.00 pt   ->   Google pitch 15.75 pt      (4 rows: +3.00 pt total)
    dy by line:  -0.20 (table header) -> +0.55 -> +1.30 -> +2.05 -> +2.80 (last row) -> +4.10 (footer)
    everywhere else on the page the pitch matches to +-0.5 pt

Declared in the `.docx`: `<w:trHeight w:val="300" w:hRule="atLeast"/>` — 300 twips = **15.00 pt**, which
is exactly the source pitch. The table is ruled (`w:tblBorders` `sz=3` = 0.375 pt a side). Google lays
**15.75 pt**. 9 of 45 runs out against an allowance of 3: the count clause, and the tail clause does not
fire (worst 4.10 pt against a 2.45 pt tolerance = ratio 1.67).

### 4b. `74_balance_sheet_indented_subitems` — same construct, +0.25 pt a row, unruled

    source pitch 17.00 pt   ->   Google pitch 17.25 pt      (7 body rows, one-signed)
    declared: <w:trHeight w:val="340" w:hRule="atLeast"/>   (340 tw = 17.00 pt), table unruled
    dy by line: +0.12 at the title, +3.62 at the footnote — the ramp is the table, nothing else

### 4c. `31_times_body_arial_headings` — no table, and the whole displacement is a +0.1 pt line gap

    rows = 0, no w:trHeight anywhere in the file
    every inter-line gap is +0.08 to +0.12 pt too tall (4 x +0.08, 3 x +0.11, 2 x +0.10, 2 x +0.12)
    dy: +2.10 at the top of the body -> +3.54 at the signature block; 4 of 29 runs out, allowance 2

This is the flow-line term, not the row term: a uniform, one-signed ~+0.1 pt per line advance that
accumulates ~1.3 pt down 13 lines. It is a **different construct** and the row rule below cannot reach
it.

## 5. The construct, with file:line

`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`, `emitTable` (the content-table writer):

| line | code | why it matters |
|---|---|---|
| **`:6299`** | `int rowTw = extentPt > 0f ? Math.round(extentPt / rowCount * TWIPS_PER_PT) : 0;` | the page's own row pitch, **unrounded** — this is the number that will not survive Google's 0.75 pt rung |
| **`:6444`** | `int rowTwHere = rowTw;` (then `exactRows` overrides it per row from `t.rowEdge`, `:6446-6450`) | same value, per row, still unrounded |
| **`:6462`** | `int ruleTwHere = Math.round((szAbove + szBelow) * TWIPS_PER_PT / 16.0);` | the rule the row pays — the term Google adds *on top* of the box |
| **`:6475`** | `int pitchTwHere = rowTwHere;` | the pitch the flow is charged for |
| **`:6541`** | `int rowHeightTw = Math.max(rowTwHere, rowLineTw);` | **the value written to `w:trHeight`** |
| **`:6550-6551`** | `writtenRowsTw += Math.max(0, Math.max(pitchTwHere, Math.max(rowTwHere, rowLineTw) + ruleTwHere));` | **the flow charge after the table** — it models content + rule, but not the rung the renderer snaps to |
| **`:6631`** | `inner.append("<w:trPr><w:trHeight w:val=\"").append(rowHeightTw).append("\" w:hRule=\"atLeast\"/>...")` | where the declaration reaches the file |

The engine's model of the renderer, stated in its own comments at `:6452` and `:6464`, is
`row = max(w:trHeight, cell content + rule)`. **Measured on 12 documents, the renderer does that and then
snaps the result onto a 15-twip (0.75 pt) grid, and for a ruled row it adds the rule outside the snap.**

### The law, fitted on 10 documents that are `trHeight`-bound (cell content at or below the declared height in every row sampled — `71_invoice`'s 360-twip rows carry 16.2 pt of content against an 18.0 pt declaration, and its 320-twip rows 14.5 against 16.0)

    laid pitch (pt) = 0.75 * round( (trHeight + rule) / 0.75 )

| document | trHeight (tw) | rule (tw) | predicted laid | predicted delta | **measured delta (modal)** | fits |
|---|---:|---:|---:|---:|---:|---|
| `303_discharge_summary` | 300 | 15 | 15.75 | **+0.75** | **+0.75** (4 gaps) | yes |
| `16_right_aligned_amounts_txtpos` | 380 | 0 | 18.75 | **-0.25** | **-0.25** (5 gaps) | yes |
| `74_balance_sheet_indented_subitems` | 340 | 0 | 17.25 | **+0.25** | **+0.25** (7 gaps) | yes |
| `72_bank_statement_no_rules_right_amounts` | 340 | 0 | 17.25 | **+0.25** | **+0.25** (16 gaps) | yes |
| `bus-timetable-station-left-times-right` | 328 | 0 | 16.50 | **+0.10** | **+0.10** (32 gaps) | yes |
| `price-list-2col-dense-right-aligned` | 328 | 0 | 16.50 | **+0.10** | **+0.10** (29 gaps) | yes |
| `36_embedded_subset_font` | 400 | 0 | 20.25 | **+0.25** | **+0.25** (2 gaps) | yes |
| `71_invoice_space_aligned_no_rules` | 360 | 0 | 18.00 | **0.00** | **0.00** (6 gaps) | yes |
| `report-2col-table-spanning-both-columns` | 360 | 20 | 18.75 | **+0.75** | **+0.75** (4 gaps) | yes |
| `402_calendar_month_grid` | 1240 | 20 | 63.00 | +1.00 | +0.64 / +0.89 | within 0.36 |

Three consequences, each of which contradicts something already on disk:

1. **The snap goes DOWN as well as up.** `16_right_aligned` is the clean case: its cell content is
   15.3-17.1 pt against a 19.00 pt declaration, so `w:trHeight` binds every row, and Google lays **18.75**
   — 0.25 pt *below* the declaration. The `+1 rung` form of the 0.75 pt law
   (`FINDINGS/18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`) and the "floor, and only ever
   upward" conclusion of `FINDINGS/18-displacement-ROW-HEIGHT-IS-CONTENT-DRIVEN-26NOV-fixer.md` cannot
   produce a negative delta. Nearest-rung can. (`362_price_list_dense` -0.15 and
   `balance-sheet-two-columns` -0.35 are also negative, but both are content-bound on the rows sampled,
   so they show the negative sign without isolating the declaration as its cause.)
2. **`w:trHeight` is the binding number on these ten** — the sampled cell content is 11.0-18.0 pt against
   declared 15.0-62.0 pt, so `max(trHeight, content + rule)` is `trHeight` in every row. The 25 Nov
   falsification (`...ROW-SNAP-FALSIFIED-25NOV-fixer.md`) was taken on `320_balance_sheet_statutory`,
   where the content *exceeded* the declaration — that document cannot see the declaration at all, and
   it is not representative of these ten.
3. **A ruled row pays its rule outside the snap.** `303`'s box is already 15.00 = exactly 20 rungs;
   Google lays 15.75 = 21. The +0.75 is the rule, not rounding.

## 6. The proposed change — one rule, no document named

> **Rule.** When a table row's height is written, declare the height that the renderer will *lay*,
> net of the rule and on the renderer's own 0.75 pt grid; and charge the page budget, and the
> `w:before` that places the paragraph after the table, with that same laid number rather than with the
> page's ideal pitch.

In `DocxWriter.java`, immediately after `:6541` and before the write at `:6631`:

```java
// What the renderer will actually lay for this row. Measured on 12 documents:
//   laid = 15 * round((trHeight + rule) / 15) twips
// so the number the renderer lays is a whole number of 15-twip (0.75 pt) rungs, and the
// declaration only survives the round trip when (trHeight + rule) is already on one.
// Take the rung nearest what the row has to occupy, and declare it NET OF THE RULE, so
// the number Google lays is the number the page drew.
final int RUNG_TW = 15;                            // 0.75 pt: one CSS pixel
int wantTw = Math.max(rowTwHere, rowLineTw + ruleTwHere);   // what the row must occupy
int laidTw = RUNG_TW * Math.round(wantTw / (float) RUNG_TW);
rowHeightTw = Math.max(typeFloorTw, laidTw - ruleTwHere);
```

and at `:6550`, charge `laidTw` instead of `pitchTwHere`:

```java
writtenRowsTw += Math.max(0, laidTw);              // what is laid, not what was asked for
```

Worked on the measured cases, with the same constant:

| document | today: declare -> lay | after the rule: declare -> lay | residual a row |
|---|---|---|---|
| `303_discharge_summary` | 300 -> **315** (+0.75) | **285 -> 300** | **0.00** |
| `report-2col-table-spanning-both-columns` | 360 -> 375 (+0.75) | **340 -> 360** | **0.00** |
| `16_right_aligned_amounts_txtpos` | 380 -> 375 (-0.25) | 375 -> 375 | -0.25 |
| `74_balance_sheet_indented_subitems` | 340 -> 345 (+0.25) | 345 -> 345 | +0.25 |
| `bus-timetable-station-left-times-right` | 328 -> 330 (+0.10) | 330 -> 330 | +0.10 |

The rule kills the ruled-row term exactly (both ruled tables measured here go to 0.00) and leaves the
unruled rows at the nearest rung, `<= 0.375 pt`.
That residue is why the second half — charging `laidTw` — is not optional: with it the residue is taken
out of the `w:before` of the paragraph after the table, which Google honours 1:1, instead of being added
to every line below the table.

**Predicted effect, stated so the next run can falsify it.** Removing the accumulated row term takes
**12 of the 14** inside the count allowance in the model (fit `dy = c + slope*y`, remove the ramp,
re-count against each run's own tolerance). Of those 12, **10 carry a table** and are reachable by this
rule; the 2 that are not (`31_times_body_arial_headings`, `70_magazine_drop_cap_photo_caption`) have no
`w:trHeight` at all and are the flow-line term of §4c. The two that stay failing after ramp removal
(`71_invoice_space_aligned_no_rules`, `balance-sheet-two-columns-of-figures`) have residual structure
that is not a single ramp and need their own measurement.

**If this works, these 10 documents become CLEAN:**
`16_right_aligned_amounts_txtpos`, `303_discharge_summary`, `362_price_list_dense`,
`36_embedded_subset_font`, `402_calendar_month_grid`, `72_bank_statement_no_rules_right_amounts`,
`74_balance_sheet_indented_subitems`, `bus-timetable-station-left-times-right`,
`price-list-2col-dense-right-aligned`, `report-2col-table-spanning-both-columns`.

It also removes the row term from the other 62 `18_displacement` failures that carry a `w:trHeight`, so
its reach is much wider than these 10 — but the count of documents it takes to CLEAN is the number that
matters and it is 10, measured, not modelled upward.

**What this rule is not.** It is not "declare the +1 rung" (falsified twice, and negative on three
documents here) and it is not a per-document constant. It is the same arithmetic for every table:
*declare what the renderer lays, and charge what the renderer lays.*

## 7. How the measurements were validated

* **The `.docx` is the one the verdicts were taken on.** The engine was built from HEAD in this sandbox
  and all 14 documents converted (`ConvertOne`). For 12 of the 14, `word/document.xml` from the Google
  Doc's own uploaded `.docx` in Drive is **byte-identical** to the local build (md5 of
  `word/document.xml`); the other 2 (`72_bank_statement...`, `bus-timetable...`) were re-rendered from the
  `gv-`-prefixed Google Docs created 4-5 minutes before their stored verdict.
* **The renders reproduce the stored numbers.** All 14 re-measured `med_dy` / `worst_dy` / `runs_matched`
  match `benchmarks/gverify/*.json` to the tenth of a point (table in §2). The first attempt at `72` and
  `bus-timetable` used newer Google Docs and did **not** reproduce the store (-12.96 / -28.21 vs 1.1 /
  4.8) — that mismatch is what identified the right document to export, and it is the reason a render
  should always be checked against the stored `med_dy` before its clause verdict is believed.
* **The clause arithmetic is the check's own.** `/scratch/work/analyze.py` imports `verify_google.py`
  and intercepts `extra_checks` to get the real `pairs`, exactly as `tools/p2w-bench/dy.py` does; the
  three clauses are then evaluated separately from that one list.
* **Not done, and not claimed:** no engine change was built; no LibreOffice regression was run; the
  post-fix Google re-measure does not exist. The "10 CLEAN" is a model of the ramp removal, and the next
  run must re-render and re-count rather than trust it.

## 8. What the next run should know

* The store does not record **which clause** failed a page. `checks["18_displacement"]` carries
  `bad_pages` and `worst_dy` and nothing else (`verify_google.py:5904-5907`). One extra field —
  `{"n_out": .., "allowance": .., "clause": "count|allout|tail"}` per bad page — would cost nothing and
  would stop every future run from re-deriving this file's §2 by hand. It is an instrument change: no
  verdict can move because of it.
* `worst_dy <= 7 pt` and "fails only the count clause" are **not** the same set: 14 vs 8. State which
  filter a population was taken with.
* The flow-line term (+0.08 to +0.12 pt per line advance, §4c, and the alternating +0.51 / -0.46 pt jitter
  on `303`'s non-table lines) is untouched and is the next construct in this class. It is the
  `w:line` hairline box (`DocxWriter.java:4113 hairlinePt()`, written by `spacing()` at `:149-154`) and
  the `max((w:line/240) * lineHeight(face, size), 0.069 * size)` charge Google applies to it.
