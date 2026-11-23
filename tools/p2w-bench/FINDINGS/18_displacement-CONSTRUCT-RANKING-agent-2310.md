# Which source constructs cause `18_displacement` in Google Docs — measured, ranked, and the minimal patch

**Read-only analysis.** Clone at `kavopdf/app`, commit **`f904f62`** (depth 1). Engine built from that clone
(`tools/p2w-bench/build-engine.sh`, 41 s), corpus fetched whole (213/213), all 213 converted with
`ConvertAll`. Nothing in the repo was modified, no Drive probe was created, nothing was pushed.
Every number below is either (a) a measurement this run made on `f904f62` from the emitted
`word/document.xml` or the source PDF, (b) a recorded Google round trip quoted from `FINDINGS/`, or
(c) marked **not measured**.

---

## 0. Correction to the premise, before anything is ranked

The task says "~30 affected corpus documents". **That number is wrong, and it is wrong in the
direction that changes the ranking.** Measured from `benchmarks/gverify/*.json`:

| | documents |
|---|---:|
| results in `gverify/` | 213 |
| scored (`status: ok`) — the only ones that carry a `failed` list | **190** |
| of those, **fail `18_displacement` in Google** | **100** |
| fail it and nothing else | 13 |
| also fail it in LibreOffice (so not Google-specific) | 18 |
| Google-only `18_displacement` | **82** |

`benchmarks/DEFECT-CLASSES-GOOGLE.md` says the same thing (`18_displacement | open 101 | libreoffice 20 |
google 101`). **~30 is the count of documents that PASS all 42 checks in Google** —
"Google Docs 30 of 190 pass all 42" (`benchmarks/GOOGLE-VS-LIBREOFFICE.md:6`). It is the clean set, not
the affected set. Everything below is ranked over the **100** affected documents, with the 13
"fails it alone" documents called out separately because only those can be made fully clean.

**Second correction — the stored results carry no displacement numbers.** `gverify/*.json` holds
`name/status/passed/total/failed/engine` only; `verify_google.py` computes `med_dy`, `worst_dy`, `med_dx`
at lines 5653–5655 and **never writes them out** (`--json` dumps `res["checks"]`, and `DETAIL` is only
populated for `47_margins`, `verify_google.py:4225`). That is why `tools/p2w-bench/dy.py` exists — its
own docstring calls itself "the measurement `18_displacement` never prints"
(`tools/p2w-bench/dy.py:2-3`). So per-document displacement is **not measured** for 90 of the 100
documents; the only per-page dy numbers in the repo are the 28 pages of 10 documents in
`FINDINGS/18_displacement-dy-shape-101323-4fa7.md` plus the hand-recorded figures in the 18-class
FINDINGS. Where a document has no recorded dy, this report says **not measured** and falls back to the
construct's measured charge law, marked as a prediction.

---

## 1. The ranked table

Populations: **P1** = the 100 documents that fail `18_displacement` in Google. **P2** = the 13 that fail
it alone. "Could explain" = the construct is present in the `.docx` today's HEAD emits for that document
**and** its measured magnitude exceeds `18_displacement`'s own floor tolerance
(`clamp(0.35*size, 1.5, 4.5)` pt, `verify_google.py:5723-5724`) on at least 5 % of a page's runs.

| # | construct (where the writer emits it) | Google's behaviour | present in P1 | could explain P1 | present in P2 | measured to FIX a doc | confidence |
|--:|:--|:--|---:|---:|---:|---:|:--|
| **1** | **Table-gap spacer: empty paragraph whose whole height is `w:line` + `w:lineRule="exact"` on an `w:sz=2` mark, `w:before=0`** — `DocxWriter.table()`, emission `:6107-6112` | **charges 21.6 % of it** (law: `2.5873 * max(L/240, 0.06)` pt, `DocxWriter.java:6083`; probe TOPB 1103 tw → 11.89 pt, `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md`) | **53** | **53** | **7** | **6 documents to 42/42** (recorded, 22 Nov, spacer moved to `w:before`) | **high** |
| **2** | **Row height: `w:trHeight w:hRule="atLeast"` + the cell's own exact line box** — `:6557-6559`, cell box `:6892` | lays `max(declared, cell line box)`; `hRule="exact"` is normalised back to `atLeast` on import (read back from Google's own .docx export) | 89 | **74** (≥7 rows ⇒ ≥5.25 pt at the engine's 0.75 pt/row quantum) | **12** | **0 measured** — the declaration change is refuted | medium (magnitude measured on 2 docs only) |
| **3** | **Page-top gap: `w:before` on the first paragraph after `<w:br w:type="page"/>`** — `spacing(..., pageFirst)`, `:149-170` | **drops it entirely**: 55.15 pt asked → 0.33 pt rendered | **16** (all multi-page; **0** of P2, which are all single-page) | **16** | **0** | **1 document improved 37→40/42** (`bank-statement-5-pages`), none made clean | high on mechanism, low on prize |
| **4** | **First-row cell `w:before`** (a table's header row placed from its own top box) — `:6892` | honours `w:before` 1:1 (`FINDINGS/18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md`: 66 probes, error 0.000000 pt) — the fault is the *value* (248 tw emitted where 174 is right) | 1 identified (`balance-sheet-two-columns-of-figures`) | 1 | 1 | 0 | low |
| 5 | Anchored text box (`<w:drawing><wp:anchor>…<wps:txbx>`) — `anchorShape()`, `:5580-5685` | **rasterises it**; the text inside is lost, not moved | 93 | **0** | 12 | n/a — charged to `04_chars_missing` (54 of 65) and `25_invisible_text` (48 of 48), never to 18 | high (perfect separator, `FINDINGS/04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent.md`) |
| 6 | `w:ind w:left` (horizontal) — `:3766` | honoured; and it moves **x**, which `18_displacement` does not read (it reads `ry`, `verify_google.py:5734`) | 100 | **0** | 13 | n/a | high |
| 7 | `w:tabs w:pos` (horizontal) — `:3760` | **honoured exactly**: 216.0 pt asked, 216.00 pt rendered, origin = left margin (`FINDINGS/47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md`) | 81 | **0** | 12 | n/a | high |
| 8 | `w:framePr` — removed from the writer; only historical comments remain (`:3227-3250`, `:3487`) | renders as body text at the left margin (`google_safe.py:47-50`) | **0** | 0 | 0 | n/a | high |
| 9 | Section margins / gutter — `sectPrXml`, `:2410-2414` (`w:pgMar` all zero, `w:gutter="0"`) | honoured — which is exactly why the *proven* fix for #3 is to use this field | 0 (all zeros) | 0 | 0 | 1 doc, 3 checks (SECTMARGIN variant, `…page-top-gap-sectmargin-PROVEN-075600-f1x.md`) | high |
| 10 | `w:docGrid w:linePitch="360"` — `:2414` | not measured as a position term; every paragraph carries `w:snapToGrid w:val="0"` (`:3761`), which opts out | 100 | **not measured** | 13 | n/a | low |

### Why the ordering is what it is

* **#1 is first on the column that matters — documents measured to go clean.** It is the only construct
  in this class with a *recorded* 42/42: six documents
  (`16_right_aligned_amounts_txtpos`, `22_invoice_four_columns_txtpos`, `29_dot_leaders_txtpos`,
  `41_coloured_headings_white_bg`, `68_journal_wide_table_spanning`, `73_marksheet_subject_marks_grade`)
  scored clean in Google when the spacer alone moved from `w:line` to `w:before`
  (`FINDINGS/18_displacement-ELEVEN-NON-RULED-IS-THREE-FAULTS-CENSUS-2354-fixer.md` §"Group A").
  It is also present in 53 of the 100, which is second only to row height.
* **#2 has the widest reach (89 present, 74 with magnitude to spare) but is the weakest as a fix.**
  Its *declaration* form is refuted by measurement: rewriting `w:trHeight`/`hRule` moved **no rule on
  the page** (`FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §1, all 24 rows read
  identical), and `w:before` inside a cell does not enter the row's height either (§2, 26 rule gaps
  identical). What is left as a lever is the cell's own line box (`:6892`), which no run has yet
  converted into a clean document. It is ranked second because "could explain" is large and the
  evidence for the mechanism is real, not because it is a one-line win.
* **#3 is the largest per-document magnitude in the corpus** — 48.5–67.6 pt of uniform shift, measured
  on 15 pages — but it is a *page-break* construct, so it cannot touch a single one of the 13 documents
  that fail `18_displacement` alone: **all 13 are single-page** (measured from the source PDFs this run;
  the same table is in `FINDINGS/18_displacement-page-top-gap-sectmargin-PROVEN-075600-f1x.md` §"The
  correction the next run needs"). Page 1's `w:before` is delivered — measured page-0 dy on the 10
  dy-shape documents is −2.0, +1.8, −2.4, −8.6, −14.1 pt while their pages 1+ read −48.5 … −67.6 pt.
* **#4–#10 cannot move `18_displacement` at all**, for the reasons in the last column: horizontal only,
  dropped outright and charged to a different check, or absent from the emitted bytes.

---

## 2. The measured evidence, construct by construct

### 2.1 #1 — the dropped table-gap spacer (53 of 100; 7 of 13)

**What is emitted** (`DocxWriter.java:6107-6112`, the `else` arm of the guard, reached when the page has
no slack):

```xml
<w:p><w:pPr><w:snapToGrid w:val="0"/>
  <w:spacing … w:before="0" w:after="0" w:line="2880" w:lineRule="exact"/>
  <w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>
```

The value is computed at `:6033` (absolute branch, `Math.min(2880L, round(extraAbs*20))`) and `:6047`
(baseline branch), both capped at 2880 twips = 144 pt.

**Why Google gets it wrong.** `w:line` with `lineRule="exact"` is a *length* to Word and LibreOffice and
a *multiple of the substitute face's line height, floored at 0.069 em*, to Google — the engine states the
law itself at `DocxWriter.java:75-107` and the delivered value at `:6083`
(`2.5873 * max(L/240, 0.06)` pt on an `sz=2` mark). Two independent measurements agree:

| document | spacer written | predicted shortfall 0.784 × spacer | measured Google dy | source |
|:--|--:|--:|--:|:--|
| `68_journal_wide_table_spanning` | 144.0 pt | −112.9 | **−114.28** | `FINDINGS/…ELEVEN-NON-RULED…-2354-fixer.md` |
| `73_marksheet_subject_marks_grade` | 16.70 pt | −13.0 | **−12.85** | same |

That is a dose–response across a factor of nine in the written value, with the sign, the magnitude and
the block boundary all matching: on `68` the runs above the spacer read +0.09 and every run below it
−114 to −115.

**Presence, measured this run** on the 213 `.docx` HEAD emits (empty `sz=2` paragraph, no text,
`lineRule="exact"`, `w:line > 20` twips, `w:before="0"`): **53 of the 100**, of which **45 are
single-page**. Spacer size: median **20.70 pt**, max **144.00 pt**; 28 documents carry ≥20 pt
(predicted dy ≥15.7 pt).

| document | spacer (pt) | pages |
|:--|--:|--:|
| `330_cad_drawing_sheet` | 144.00 | 1 |
| `360_restaurant_menu` | 144.00 | 1 |
| `68_journal_wide_table_spanning` | 144.00 | 1 |
| `80_gstin_pan_cin_ifsc_table` | 113.45 | 1 |
| `bank-statement-5-pages` | 81.00 | 5 |
| `gst-invoice-multipage-item-table` | 80.20 | 4 |
| `374_org_chart` | 74.80 | 1 |
| `25_signature_block_underscores_txtpos` | 62.65 | 1 |
| `13_stamp_non_english` | 55.35 | 1 |
| `56_table_indented_from_margin` | 46.45 | 1 |
| `340_bill_of_lading` | 39.70 | 1 |
| `itr-computation-with-slab-table` | 36.30 | 1 |
| `marksheet-subject-left-marks-right` | 36.30 | 1 |
| `very-long-single-column-table` | 35.55 | 3 |
| `eway-bill` | 30.95 | 1 |

**The 7 of the 13 solo documents that carry it** (measured, `f904f62`): `68_journal` 144.0,
`insurance-policy-schedule` 26.8, `mobile-bill` 25.0, `72_bank_statement` 18.3,
`table-with-no-header-row` 12.35, `two-tables-stacked-with-no-gap` 12.35,
`bus-timetable-station-left-times-right` 6.35. The other 6 carry **no** dropped spacer — four already
carry a *spent* one (`16` 4.6, `362` 15.15, `36_embedded_subset_font` 13.35, `balance-sheet` 12.55), and
`31_times_body_arial_headings` has no table at all and `71_invoice_space_aligned_no_rules` has none.
This reproduces the "7 of 13" in `FINDINGS/18_displacement-WRITER-CONSTRUCT-1330-A1.md:96` exactly.

> One correction to that finding: it states at `:98-101` that "the guarded `w:before` arm fired on 0 of
> the 13 documents at HEAD". On `f904f62` the guard **does** fire on 4 of the 13 — `16` emits
> `w:before="92" w:line="1"`, `362` `w:before="303" w:line="1"`, `73` `w:before="333" w:line="1"`,
> `36` `w:before="267" w:line="1"`. So the construct is not uniformly refused; it is refused on the
> pages where the room test fails, which is where the two costs live.

**Why it is still open**: spending the gap unguarded costs two documents — `mobile-bill` and
`insurance-policy-schedule` are exactly-full pages that overflow to two (`46/47 → 43/47`, content lost),
measured in Google both ways.

### 2.2 #2 — row height (89 present, 74 with magnitude)

`w:trHeight w:hRule="atLeast"` is written at `:6557-6559`; the cell's paragraph carries its own exact
line box at `:6892` (`spacing(cellBeforeTw, cellBoxTw, cellSz, …)`). Google lays
`max(declared, cell line box)` and normalises `hRule="exact"` back to `atLeast` on import — read back
from Google's own `.docx` export of a document the engine wrote as `exact`
(`FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §1).

Measured magnitude: `mobile-bill` source row pitch **18.40 pt** → Google **19.10 pt** (+0.70/row over 24
rows); `362_price_list_dense` 29 rows read **−3.5 at the top → −19.4 at the foot** (Google's rows
*shorter*, ~0.55/row); the dy-shape fit gives b = +1.85 … +3.6 pt per 100 pt of page depth, i.e. Google's
rows 2–3.6 % taller. The engine's own guard charges **0.75 pt per row** (`rowExcessTw = 15 * rows`,
`:6093`). At that quantum, 74 of the 100 documents have ≥7 rows ⇒ ≥5.25 pt of cumulative error, above
the 4.5 pt cap.

Presence measured this run: 89 of the 100 carry `w:trHeight`; median rows 12, max 246
(`324_loan_amortisation_schedule`).

### 2.3 #3 — the page-top gap (16 present, 0 of 13)

`w:before` on the first paragraph after `<w:br w:type="page"/>`. Google renders **0.33 pt of 55.15 pt**
(probe TOPA, `FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md`). On the real corpus the
shift equals the page's own top gap: `bank-statement-5-pages` emits `w:before="1103"` (55.15 pt) and reads
−56.9 / −57.1 / −57.1 / −57.1 pt on pages 1–4 (`dy-shape` table; also `…page-top-gap-sectmargin-PROVEN`
per-page table, BASE column −59.5 on pages 1–4 vs −4.3 on page 0).

Only **17 of the 100** failing documents are multi-page at all; **83 are single-page** (measured from the
source PDFs). Of the 17, **16** carry a page-top gap >2 pt on pages 2+
(gap median **55.0 pt**, min 11.5, max 89.5). All 16, with pages and gap:

| document | pages | page-top gap (pt) |
|:--|--:|--:|
| `416_many_tiny_pages` | 300 | 89.50 |
| `57_centred_title_page_left_body_pages` | 2 | 69.50 |
| `602_bookmarked_annual_report` | 3 | 69.50 |
| `412_page_labels_roman` | 5 | 61.35 |
| `417_rotate180_and_mirrored` | 2 | 61.35 |
| `very-long-single-column-table` | 3 | 60.50 |
| `academic-paper-ieee-2col-abstract` | 2 | 59.65 |
| `bank-statement-5-pages` | 5 | 55.15 |
| `one-page-rotated-180-degrees` | 2 | 54.85 |
| `balance-sheet-and-profit-loss` | 2 | 52.00 |
| `gst-invoice-multipage-item-table` | 4 | 51.15 |
| `form16-part-b` | 2 | 50.00 |
| `mutual-fund-statement` | 2 | 49.15 |
| `table-across-page-break-repeated-header` | 3 | 49.15 |
| `58_header_rule_footer_rule` | 2 | 47.55 |
| `324_loan_amortisation_schedule` | 7 | 11.50 |

**0 of the 13** solo documents — all single-page, so page 1's `w:before` is delivered and there is no page
break for the construct to sit on.

The proven remedy is `w:pgMar w:top` (SECTMARGIN variant: −59.5 → −4.3, pages unchanged at 5, three
checks flip to pass, `bank-statement-5-pages` 37 → 40/42), and the 1×1 `trHeight` row is **refuted**
(5 pages → 6, `31_pages_lost_their_text` 5 → 1, matched runs 585 → 220).

### 2.4 #4 — first-row cell `w:before` (1 document)

`balance-sheet-two-columns-of-figures`: 248 tw emitted where 174 is right; the two column-header rows sit
**+3.69 pt** in LibreOffice while rows 2+ land within 0.4 pt, and Google reads a median +1.06 pt, max
+6.69, 29 of 72 runs out (`FINDINGS/…ELEVEN-NON-RULED…-2354-fixer.md` rows 11 and 9). One document, one
value.

### 2.5 The constructs that provably cannot be the cause

* **`w:ind w:left` (`:3766`)** — horizontal. `18_displacement` reads `ry` only
  (`ds = [(g["ry"] - r["ry"], r["size"]) …]`, `verify_google.py:5734-5735`). 100 of 100 documents carry
  non-zero `w:ind`, and it is irrelevant to this check.
* **`w:tabs w:pos` (`:3760`)** — horizontal, and honoured exactly: 216.0 pt asked → 216.00 pt rendered,
  origin at the left margin (`FINDINGS/47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md`, probes A and C).
* **Anchored text boxes (`wp:anchor`, `:5580-5685`)** — Google rasterises them and the *text* goes
  missing, which is `04_chars_missing` (54 of 65) and `25_invisible_text` (48 of 48), not displacement.
  93 of the 100 carry at least one; not one Google-clean document carries either construct
  (`FINDINGS/04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent.md` §1).
* **`w:framePr`** — no longer emitted (0 of 213); Google ignores it outright (`google_safe.py:47-50`).
* **Section margins/gutter** — emitted as hard zeros (`:2411-2412`), so they place nothing today.

---

## 3. The minimal patch for the highest-value construct (#1)

**File** `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java`
**Method** `private static void table(StringBuilder sb, PdfToWord.Table t, Ctx ctx)` — declared `:5948`
**Lines to change** `:6092-6112` (the guard and the two emission arms)

### The change

The guard is binary: spend the whole gap in `w:before`, or spend none of it. Make the spend **partial** —
spend what the page can still hold, leave the remainder in `w:line`. `before + line` is preserved to the
twip in every case, so LibreOffice and Word render the page they always rendered.

```java
 6092             int spacerHairTw = 1;
 6093             int rowExcessTw = 15 * Math.max(0, ctx.pageRowCount);
 6094             int slackTw = ctx.budgetTw - Math.round(ctx.pageInkBottomPt * (float) TWIPS_PER_PT);
 6095             int roomWantTw = Math.max(0, spacerTw - 20);
 6096             int wantTw = Math.max(0, spacerTw - spacerHairTw);
+6097             // PARTIAL SPEND: give Google as much of the gap as the page can still hold and
+                  // leave the rest in w:line. before + line is unchanged, so LibreOffice and Word
+                  // see the page they always saw; Google draws min(gap, slack) instead of none.
+                  int partialTw = Math.max(0, Math.min(wantTw, slackTw - ctx.spacerSplitTw - rowExcessTw));
+                  boolean spendable = slackTw > 0
-6098                         && ctx.spacerSplitTw + roomWantTw + rowExcessTw <= slackTw;
+6098                         && partialTw > 0;
 6099             if (spendable) {
 6100                 … .append(wantTw)                              →  .append(partialTw)
 6104                 … .append(Math.min(spacerHairTw, spacerTw))    →  .append(Math.max(spacerHairTw, spacerTw - partialTw))
 6106                 ctx.spacerSplitTw += roomWantTw;               →  ctx.spacerSplitTw += partialTw;
 6107             } else { … unchanged … }
```

Three integers and one condition. No new element, no new attribute, and every document the guard refuses
stays byte-identical to today's output.

### Expected effect, in pt, per document

Google's charge for the paragraph is `before/20 + 2.5873*max(line/240, 0.06)` pt. The shift removed is
that sum after the patch minus the same sum before it (`2.5873*max(spacerTw/240, 0.06)`). Computed for the
7 solo documents that carry the construct, with `slack` read from each source PDF's lowest ink and
`rowExcess = 15 × rows` (the engine's own terms, `:6093-6094`):

| document | spacer (pt) | shortfall today 0.784×spacer | partial spend (pt) | shift removed (pt) | residual | verdict |
|:--|--:|--:|--:|--:|--:|:--|
| `72_bank_statement_no_rules_right_amounts` | 18.30 | 14.35 | 18.25 (full) | **14.46** | 0.1 | **predicted clean** |
| `bus-timetable-station-left-times-right` | 6.35 | 4.98 | 6.30 (full) | **5.09** | 0.1 | **predicted clean** |
| `two-tables-stacked-with-no-gap` | 12.35 | 9.68 | 12.30 (full) | **9.79** | 0.1 | **predicted clean** |
| `68_journal_wide_table_spanning` | 144.00 | 112.90 | 29.03 | 22.77 | 90.1 | still fails — see below |
| `insurance-policy-schedule` | 26.80 | 21.00 | 7.48 | 5.86 | 15.1 | still fails (no overflow) |
| `mobile-bill` | 25.00 | 19.60 | 5.98 | 4.69 | 14.9 | still fails (no overflow) |
| `table-with-no-header-row` | 12.35 | 9.68 | 4.48 | 3.51 | 6.2 | still fails |

So the one-attempt expectation is **+3 documents clean, 0 regressions, 4 documents improved but not
cleared** — against the unguarded split's 6 clean and 2 documents losing content.

**The limitation the numbers expose, stated so the next run does not re-derive it.** The room test reads
`ctx.pageInkBottomPt` — the **source** page's lowest ink — not the render's own flow position. On
`68_journal` that is why the guard refuses 2880 twips against 688 twips of slack: the source page has
34 pt of white space below its last line, but the *render* is 114 pt high, so there is really ~2968 twips
of room. Replacing `:6094` with the flow's own remaining room

```java
 6094             int slackTw = ctx.budgetTw - ctx.flowTw - rowExcessTw;
```

makes `68` spendable and, with `partialTw = min(2880, 2968)`, delivers **+113.1 pt** against a 112.9 pt
shortfall — the recorded measurement of the unguarded split on that document is −114.28 → −3.08, i.e.
111.2 pt removed, which agrees. This variant is the higher-value one but it is **not measured in
LibreOffice**, and it is the variant that puts `mobile-bill` and `insurance-policy-schedule` at risk of
overflow. Apply the `:6092-6106` patch first, measure, then decide.

### How to measure it in one attempt

```bash
bash tools/p2w-bench/build-engine.sh
cd tools/engine-verify && CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -cp "$CP" ConvertOne /scratch/work/p2w/corpus/72_bank_statement_no_rules_right_amounts.pdf /tmp/o
unzip -p /tmp/o/72_bank_statement_no_rules_right_amounts.docx word/document.xml | grep -o 'w:before="[0-9]*" w:after="0" w:line="[0-9]*" w:lineRule="exact"'
#   expect before="365" line="1"  (full spend)  -> Google shift +14.46 pt
soffice --headless --convert-to pdf --outdir /tmp/lo /tmp/o/*.docx
python3 ../p2w-bench/verify_google.py /scratch/work/p2w/corpus/72_*.pdf /tmp/lo/72_*.pdf   # must still pass 42/42
```

Structural check first (free, no Drive), then **one** Drive round trip per document — the four-call loop
is written down at `FINDINGS/18_displacement-GOOGLE-IGNORES-TRHEIGHT-1045-relay.md` §"The measurement loop".

---

## 4. What is not measured

* **Per-document displacement for 90 of the 100.** The stored results do not carry dy (see §0). The only
  per-page dy in the repo is 28 pages of 10 documents (`FINDINGS/18_displacement-dy-shape-101323-4fa7.md`)
  plus hand-recorded numbers in the 18-class FINDINGS.
* **Whether the patch clears the 3 documents in Google.** Predicted from the charge law, which is
  corroborated at two points (68, 73); not measured — no Drive round trip was made.
* **`68_journal` under the partial patch.** Predicted residual 90 pt; only the flow-based room test
  reaches it.
* **The Google side of the 46 non-solo spacer documents.** They carry other failures, so clearing 18
  does not make them clean; their dy is not recorded.
* **Whether `w:docGrid w:linePitch="360"` (`:2414`) places anything in Google.** Every paragraph opts
  out with `w:snapToGrid w:val="0"`, so it was not separable in this read-only pass.
* **The 4 solo documents that already carry a spent spacer** (`16`, `362`, `36`, `balance-sheet`) and
  still fail 18 on their recorded engine: whether they pass at `f904f62` is not measured — their verdicts
  are stamped `5beb8b9d`/`462353f9`, and the tree is `f904f62`.
* **Engine stamping.** Of the 100 failing results, 51 are stamped `5beb8b9d`, 35 `462353f`, 7 `98be7c3c`,
  5 `462353f9`, 2 `b7699196`. The construct census in this report is on the `.docx` **today's HEAD
  (`f904f62`) emits**; the verdicts are older. `DEFECT-CLASSES-GOOGLE.md` says the same in its own header.
