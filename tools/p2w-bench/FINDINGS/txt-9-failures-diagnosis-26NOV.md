# Why 9 of 213 .txt files fail — diagnosis

**Read-only.** Nothing was committed, pushed or edited. The clone at `/scratch/work/app` is
`git status --porcelain` clean at the end of this run; the engine was built and run in a **copy**
(`/scratch/work/appbuild`), so even build artefacts stayed out of the clone.

**How the numbers below were produced.** Store values are quoted from
`tools/p2w-bench/txt/` (the live store — *not* the frozen top-level `tools/p2w-bench/RANKING-TXT.csv`,
which its own `.README` calls STALE). The store carries only pass/fail **counts** and check **ids**, not
measured values, so every `expected / measured` pair here was re-measured: the 213 PDFs were fetched
from the `corpus-v1` release plus `benchmarks/realworld` and `benchmarks/corpus-extra`, the engine was
built with `tools/p2w-bench/build-engine.sh` (JDK 17, PDFBox-Android 2.0.27.0), all 213 converted with
`ConvertAll`, and all 213 scored with `verify_txt.compare()` at HEAD.

That run reproduces the store **exactly**: 213 scored, 204 clean, 9 failing, the same 9 documents, the
same `failed_ids`, and the same `applicable` count on every one of them.

---

## 1. The 9 documents, their failing checks, and the measured value vs the expected value

From `tools/p2w-bench/txt/RANKING-TXT.csv` (store) and re-measured at HEAD (numbers):

| # | document | applicable | failing check | expected (source side) | measured (.txt side) | pass condition |
|--:|---|--:|---|---|---|---|
| 1 | `041122-Account_Opening_Form` | 10 | `t06_encoding` | 47,477 glyphs read | **127** undecodable | 0 |
| | | | `t09_page_furniture` | owed **29** | present **125** | equal |
| | | | `t12_word_invention` | 48,845 source chars | **14** invented chars | 0 |
| 2 | `Account_Opening_Form_Fillable_filled` | 10 | `t06_encoding` | 47,562 glyphs read | **127** | 0 |
| | | | `t09_page_furniture` | owed **29** | present **125** | equal |
| | | | `t12_word_invention` | 48,944 source chars | **14** | 0 |
| 3 | `600_reviewed_invoice_with_annotations` | 8 | `t12_word_invention` | 785 source chars | **83** | 0 |
| 4 | `305_vaccination_certificate` | 7 | `t08_line_order` | **33** comparable lines | **32** in order | all |
| 5 | `334_patent_document` | 7 | `t02_position` | **32** (x, column) pairs | **69 %** within tolerance | ≥ 90 % |
| 6 | `74_balance_sheet_indented_subitems` | 10 | `t02_position` | **50** pairs | **80 %** | ≥ 90 % |
| 7 | `39_small_caps_letter_spacing` | 9 | `t01_word_accuracy` | 100 % | **97.4 %** | ≥ 99 % |
| | | | `t08_line_order` | **22** comparable lines | **21** in order | all |
| 8 | `601_fillable_admission_form` | 7 | `t01_word_accuracy` | 100 % | **97.6 %** | ≥ 99 % |
| 9 | `77_arabic_rtl_document` | 9 | `t01_word_accuracy` | 100 % | **92.1 %** | ≥ 99 % |

Fourteen failing check-instances on nine documents. `t12_word_invention` is the most common single
check (3 documents), as the brief says.

**Store hygiene, worth knowing before anyone works from it.** The store's own files disagree with each
other about how many documents fail:

| file | failing | clean | note |
|---|--:|--:|---|
| `txt/RANKING-TXT.csv`, `txt/STATE-TXT.json` | **9** | 204 | the live numbers, reproduced here |
| `txt/DEFECT-CLASSES-TXT.md`, `txt/UNMEASURED-TXT.json` | 11 | 202 | stale — still lists `332_bom_on_drawing` and `price-list-2col-dense-right-aligned`, which now pass |
| `txt/HISTORY-TXT.jsonl`, last line | 16 | 197 | stale — carries the same `2026-11-22 17:35` timestamp as `STATE-TXT.json`, which says 9 |
| `tools/p2w-bench/RANKING-TXT.csv` (top level) | 64 | — | frozen; its `.README` says STALE |

The 16 → 9 history is reconstructable and matches the prior findings exactly: the `t12` unit change
(tokens → characters, 25 Nov) cleared 5 documents, and the `t02` pairing guard (drop a text whose
occurrences disagree about the column) cleared `332` and `price-list`. 16 − 5 − 2 = **9**.

---

## 2. `t12_word_invention`: the predicate and its threshold

The check is **not** a ratio of words absent from the source, and it is **not** a word count any more.
At HEAD the unit is the character. Quoted from `tools/p2w-bench/verify_txt.py`, the whole predicate:

```python
invented_chars = 0
if len(src_text) >= WORD_INVENTION_MIN_CHARS:            # WORD_INVENTION_MIN_CHARS = 200
    src_c = Counter(ch for ch in src_text if not ch.isspace())
    txt_c = Counter(ch for ch in txt_text if not ch.isspace())
    invented_chars = sum((txt_c - src_c).values())
c["t12_word_invention"] = (len(src_text), invented_chars,
                           invented_chars == 0,
                           len(src_text) >= WORD_INVENTION_MIN_CHARS)
```

- **What makes a word/character "invented":** it is a **multiset surplus of non-space characters** —
  `txt_c - src_c`, summed. Whitespace is excluded because that is exactly where the two sides are
  allowed to disagree (the source side is a glyph walk, the .txt side is the writer's own line model).
- **The threshold is zero.** `invented_chars == 0`. There is no ratio, no percentage, no tolerance.
- **The gate is `WORD_INVENTION_MIN_CHARS = 200`** source characters: below that the check *abstains*
  rather than judges (a "PAID" stamp cannot be judged by a text comparison).
- `ABOUT["t12_word_invention"]` states the same thing in one line: *"the .txt carries no character the
  source never drew"*.

The other failing checks, for reference:

| check | pair reported as (source, txt) | passes when |
|---|---|---|
| `t01_word_accuracy` | `(100, accuracy)` — lost words only, extra words are `t12`'s | `acc >= 99.0` |
| `t02_position` | `(len(pairs), share)`; `mid = median(x/col)`, tol `= max(2, 0.08*col)` | `share >= 90` |
| `t06_encoding` | `(glyphs_read, fffd + bom + enc_err)` | `fffd == 0 and not bom and not enc_err` |
| `t08_line_order` | `(partners, in_order)`, LCS within a column bucket | `in_order == partners` |
| `t09_page_furniture` | `(owed, present)` | `present == owed` |

---

## 3. Where the .txt is emitted, and how it relates to the .docx

**The .txt is not a transform of the .docx, and it is not written independently either. Both are
written from one shared model.** The .txt is a *sibling* of the .docx, produced by a separate writer
over the same `PdfToWord.Result`:

```
PdfToWord.java:10013   public static void writeTxt(Result result, File out)   -> TxtWriter.write(...)
TxtWriter.java:59      public static void write(PdfToWord.Result result, File out)
DocxWriter.java        write()                                    -> the .docx
```

`ReadingOrder.java` documents the pipeline (`ReadingOrder.apply` runs *before* either writer, so the
ordering is the model's decision and not a side effect of which writer ran first):

```
Result r = PdfToWord.convert(pdf, "", null);
PdfToWord.classifyHeadings(r);
ReadingOrder.apply(r);          // one order, for every consumer
DocxWriter.write(r, docx);      // reads it  -> .docx
PdfToWord.writeTxt(r, txt);     // reads the same -> .txt
```

Consequences that matter for the nine:

- `PdfToWord.java` owns `convert()` **and** `writeTxt()`, so an engine edit there moves **both**
  outputs. `TxtWriter.java` moves the .txt only. `DocxWriter.java` moves the .docx only.
  (A historical bug in this area is documented: the docx writer used to write its layout stats *into*
  the shared `Result`, so a .txt written after a .docx described the docx's numbers; that is now
  returned instead of stored — `PdfToWord.java:730-735`.)
- The .txt is a **lossy, re-derived rendering**: it has no coordinates, so `TxtWriter` re-expresses x
  as `round(lineX / charW)` leading spaces, where `charW = 0.6 ×` the document's character-weighted
  median font size (`documentCharWidth`), and y as blank lines from a per-page median pitch. Every
  `t02`/`t08`/`t09` question is therefore a question about that re-expression.
- The .txt carries `U+000C` page separators (one per page boundary) that the .docx does not.
- `TxtWriter` walks `page.blocks` and emits **one line per drawn line**, including one line per table
  cell; `DocxWriter` builds real Word tables. A document that becomes a table in the .docx can
  therefore be padded by a different rule in the .txt (`appendTable` uses the table grid's
  `cellLeft`, the paragraph path uses the line's own `lineX`).
- `DocxWriter.orderStamps()` mutates `page.blocks`, so the dependency runs both ways; the store
  guards this with `txt_gate.py --watch-docx`.

---

## 4. What each failure actually is, with concrete examples

### 4.1 `t12_word_invention` — three documents, three different things

**(a) `600_reviewed_invoice_with_annotations` — 83 invented characters. Engine, one cause, patch
measured.** The .txt opens with three lines that are annotations, not body text:

```
Rate for HSN 8536 confirmed with PO.                                    <- /Text sticky note, xref 84
Checked against PO 4471. Quantity on line 3 raised from 20 to 25.       <- /FreeText, xref 87 (1st copy)
Approved                                                                <- /Stamp /Contents, xref 89
```

The source side (glyph truth + printing annotation types 2 and 13) contains the FreeText sentence
**once**, at the bottom of the page, and `Approved`. It contains no trace of
`Rate for HSN 8536 confirmed with PO.` — the sticky note's `/AP /N` draws an *icon*, not text.

Measured split (mine, and independently by prior work): **20 invented tokens** =
7 (the sticky note: `Rate for HSN 8536 confirmed with PO.`) + 13 (the FreeText sentence emitted
**twice**: txt line 1 at the top, txt line 57 in place). The engine's own model emits the annotation
paragraphs as ordinary `Para`s and `TxtWriter` writes them as body text.

This is **not** a scoring artefact: a reader holding the page sees no "Rate for HSN…" and sees the
FreeText note once.

**(b) `041122-Account_Opening_Form` and (c) `Account_Opening_Form_Fillable_filled` — 14 invented
characters each. Engine, a duplicated line.**

```
source (drawn once):   '                     (Authorised signatory)'
.txt line 626:         '...(Authorised signatory)Y'
.txt line 628:         '...(Authorised signatory)'
```

`(Authorised signatory)` is drawn once on page 4 and appears twice in the .txt — the prior
root-cause census names it precisely: *"`p4 TABLE row0: … [(Authorised signatory)Y]` plus
`p4 PARA line1: (Authorised signatory)`. The paragraph is absorbed into a cell and emitted again, and
a stray `Y` glyph 0.5 pt lower is welded on."*

The 14 characters are the surplus of that second copy, net of boundary shifts that cancel in the other
direction. Example of a cancelling pair, same document:

```
source:  'In case of Term Deposit, interest payable#'      (the # is a drawn footnote marker)
.txt:    line 489 '#'                                       (marker stranded on its own line)
         line 490 'In case of Term Deposit, interest payable'
```

so `payable#` is "lost" and `payable` + `#` are "invented" — same characters, different boundary.
Measured token diff for the document: missing `Applicant`, `2nd`, `payable#`, `Date:` vs invented
`D`, `#`, `payable`, `(Authorised`, `signatory)Y` — 4 and 5 tokens out of 7,448, and 14 characters out
of 48,845 (**0.029 %**). Small, but the duplication is real.

### 4.2 `t06_encoding` — the two forms, 127 characters. Engine (font decoding), shared cause

```
source glyph truth:  'Please \ufffdll up in BLOCK letters only'      (127 × U+FFFD)
.txt:                'Please \ufffdll up in BLOCK letters only'      (127 × U+FFFD)
```

The Effra subset (`REAQAG+Effra-Regular`, Type0/Identity-H) maps the `fi`/`ff`/`ffi`/`ffl` ligature
glyphs to no usable Unicode; PDFBox substitutes U+FFFD and the writer emits it faithfully. Prior
measurement corrected the obvious reading: PyMuPDF passes the garbage through as `U+0124`
(`Ĥ`), i.e. **the page's own `/ToUnicode` is corrupt for these glyphs** — "neither recovers 'fill' from
/ToUnicode". The same 127 characters also sit in the **.docx** (86 occurrences measured), so this is a
user-visible defect, not a .txt-only one.

`t06` is the only check that can see it: the character multiset matches on both sides, so `t12` counts
nothing for these 127.

### 4.3 `t09_page_furniture` — the two forms, owed 29 / present 125. **Scoring artefact**

What t09 calls "furniture" on these forms is the date field. Measured keys and their counts:

| key | pages it appears in the band | owed | present in .txt |
|---|--:|--:|--:|
| `Y` | 3 | 12 | 41 |
| `D` | 3 | 8 | 33 |
| `M` | 3 | 6 | 45 |
| `Date` | 3 | 3 | 6 |

`owed` is counted inside the top/bottom 12 % band; `present` is a `Counter` over **every line of the
whole file**. A one-character key (`D`, `M`, `Y`) therefore matches any line in the document whose
stripped text is that letter. The document's real running furniture is the page number `1`–`9`, which
`_furniture_key` folds to `#` and the `any(ch.isalpha())` filter then discards.

**And the "21 lost values" that prior work reported here is itself a counting artefact — measured, this
run:**

| | source | .txt |
|---|--:|--:|
| lines that are exactly `D` | 40 | 33 |
| `D` characters in the whole document | **261** | **261** |
| lines that are exactly `M` | 52 | 45 |
| `M` characters | **173** | **173** |
| lines that are exactly `Y` | 48 | 41 |
| `Y` characters | **148** | **149** |

Not one `D` or `M` is lost and `Y` is one **over**. The "7 short" is only in the count of lines that
consist of that single letter: the .txt welds some of them onto a neighbouring line (`Date: D`,
`D Address details`). So t09 on these two documents is a **pure check artefact** — there is no missing
furniture and no missing value.

### 4.4 `t08_line_order` — one engine defect, one check defect

**`305_vaccination_certificate` (32/33) — engine.** One inversion: the .txt writes

```
This is a computer generated certificate and does not require a physical signature.   (y = 776.95, the footer)
Issued: 18-03-2022 14:22 IST  |  Certificate ID: 8842-1177-0291-4412                 (y = 272.68, mid-page)
```

The `Issued:` line is written **504.3 pt after** a line that sits above it. The cause is named in the
prior census: the "words inside the ring" rule (`PdfToWord.java:1278-1279`) tests a line's **midpoint**
against the seal's bounding box, with no containment test. The 244 pt-wide `Issued:` line's midpoint
(149.95) falls inside the ring (x 81.22–158.78), so it is absorbed into the seal paragraph, which is
appended at the end of the page's block list — after the footer. Measured selectivity: 7 documents fire
the ring rule, 22 lines are absorbed, 21 are genuinely contained, **only 305's is not**.

**`39_small_caps_letter_spacing` (21/22) — check.** The page draws the title **twice on the same
baseline**: a 1 pt white invisible duplicate at y0 = 65.11 and the 15 pt letter-spaced one at
y0 = 52.64. The engine keeps both in content-stream order; the check's key is the **bbox top**, which
for a 15 pt caps line sits 12.5 pt above a 1 pt line on the same baseline, so it invents a top-to-bottom
relation between two pieces of one visual line. Measured decisive test (prior work, same predicate, only
the vertical key changed): `key=bbox_top` → 22/21 FAIL; `key=baseline` → **22/22 PASS**.

### 4.5 `t02_position` — both remaining documents are artefacts

**`334_patent_document` (32 pairs, 69 %) — the fit, not the .txt.** The ratio distribution is bimodal:
22 pairs at exactly `x/col = 5.600` and 10 at 5.00–5.13. The 22 are all `x = 28.0, col = 5` — the body
margin, where `round(28/5.1) = 5` inflates the ratio to 5.6 by integer rounding. `mid = median(x/col)`
therefore returns **5.600** while the writer used **5.100** (`0.6 × 8.5 pt`). Measured this run:

```
mid = 5.600  ->  22/32 pairs within tolerance (69 %)   <- the check
mid = 5.100  ->  32/32 pairs within tolerance (100 %)  <- the writer's own ruler
```

One ruler explains every line of the .txt. The 9.8 % disagreement is the estimator, against an 8 %
tolerance.

**`74_balance_sheet_indented_subitems` (50 pairs, 80 %) — the source x, not the .txt.** All ten
failures are `x = 56.0` in the source with the .txt at columns 14 and 18. The page encodes the
indentation **inside the text run**:

```
PyMuPDF line: bbox x0 = 56.00, text = '        (a)  Share capital'
PyMuPDF line: bbox x0 = 56.00, text = '                 General reserve'
```

so the first *ink* is at 73.40 and 92.98, which is exactly what the .txt pads to (columns 14 and 18 at
`charW ≈ 5.06`). `_src_runs` takes the bbox x0, which is the space's x, not the ink's. Measured: with
the first-inked-glyph x the document scores **96.3 %** and passes; with the fitted mid (5.057) it
scores 80 %.

The .docx does put those rows in a real table (2 tables, first row `['(a)  Share capital',
'15,00,000.00', '15,00,000.00']`), and the model's table `cellX` records 73.4 / 92.98 with
`colX[0] = 56.0` — i.e. the model agrees with the ink, not with the bbox.

### 4.6 `t01_word_accuracy` — three documents, all boundary or glyph-identity

**`39_small_caps_letter_spacing` (97.4 %) — the .txt is right.**

```
source:  '... M Y S U R U 57 0 0 05'
.txt:    '... M Y S U R U 570 005'
```

lost `57`, `05`, `0`, `0`, `O`, `.`, `D`, `,` (8 tokens); gained `570`, `005`, `O.`, `D,` (4). The
source side inserts a space at 0.15 em, the engine breaks at 0.18 em, and this document's letter
spacing sits between the two. **The .txt is the correct rendering**; the source tokeniser is the thing
that is wrong. 8 lost of 306 = 97.4 %.

**`601_fillable_admission_form` (97.6 %) — engine, and the source misnames the character.**

```
source: two lines that are exactly '3', ZapfDingbats 9 pt, at (48.9, 326.5) and (48.9, 346.5)
.txt:   no such lines
```

Those are **ticked checkboxes**: the marks live in the widget appearance streams
(`/ZaDb 9 Tf (3) Tj`, xrefs 51 and 57), and code 0x33 of ZapfDingbats is a checkmark.
`PDFTextStripper` never walks `/AP /N`, so the engine drops them — **from the .docx too** (two blank
checkboxes where the form was answered). The source side calls the tick `3`, which it is not. Both
sides are wrong in opposite directions; 2 lost of 82 = 97.6 %.

**`77_arabic_rtl_document` (92.1 %) — mostly the check, with one real engine bug underneath.**

```
source:  ':التاريخ5'   '2قهوة'   '4الإجمالي1880000'
.txt:    'التاريخ' + '5'   'قهوة' + '2'   'الإجمالي' + '4' + '1880000'
```

8 lost / 14 gained tokens, all of them the same characters regrouped: the source is in visual
(pre-bidi) order and fuses the digit to the Arabic word; the .txt separates them. 8 of 101 tokens is
7.9 %, so a tiny absolute difference fails a 99 % bar on a 101-word document. Prior work also measured a
genuine engine bug behind it: `logicalOrder()` moves the colon past the number because
`Character.isWhitespace('\u00A0')` is false in Java, so the NBSP is swept into the LTR run.

---

## 5. Prior work: hypotheses already refuted, and by what measurement

`FINDINGS/` at the repo root has 7 files; the real corpus of prior txt work is
`tools/p2w-bench/FINDINGS/` (391 files). These are the ones that bear on the nine, with the measurement
that killed each hypothesis. **None of them needs re-deriving.**

| hypothesis | status | refuted by |
|---|---|---|
| The welded `Y` on `(Authorised signatory)Y` is 041122's t12 cause | **REFUTED** | the carry-on guard was implemented and measured: `corpus-changed.py` → *"1 of 213 documents changed: Account_Opening_Form_Fillable_filled (041122 did not change at all — the rule does not fire there)"*, and **0 rows changed** in `RANKING-TXT.csv`. `25NOV-T12-IS-U-FFFD-NOT-A-WELDED-Y.md` |
| t12's 258 "invented words" on the forms are the engine inventing text | **REFUTED** | they are 127 + 131 U+FFFD from a ligature the font cannot name; the source's own text layer is corrupt (`U+0124`), so *"no such characters on the page"* is technically true but the damage is a decoding gap. `NO-FFFD-THE-LIGATURES-ARE-NOT-MAPPED-25NOV.md` (with its own CORRECTION) |
| Treat U+FFFD as junk in `isJunk()` so `decodeThroughFont` runs | **REFUTED** | measured: surplus **127 → 141** on both forms, U+FFFD still 127 — a document getting **worse**. Reverted |
| Map U+FB00–U+FB06 to ASCII expansions | **REFUTED** | the source maps the ligature to `U+0124`, not to a U+FB0x codepoint; PyMuPDF reads `'Please Ĥll up'`. The surviving lead is a glyph-name fallback, not a codepoint table |
| t12 is a word/token problem | **REFUTED and replaced** | on 5 of the 8 then-failing documents the .txt had *exactly* the source's non-space character multiset (0 extra, 0 missing). Landed: unit changed to characters, 14 → 11 failing, 0 of 213 newly failing. `T12-UNIT-IS-CHARACTER-25NOV.md` |
| 332 / price-list fail t02 because their columns drift | **REFUTED** | the pairing, not the columns: `_ruler` pairs repeated text arbitrarily (`'1'` twice, `'2'` three times). Fix = drop a text whose occurrences disagree about the column → both PASS. **Landed** (that is why the store went 11 → 9) |
| 334 fails t02 because the writer's ruler disagrees with the page | **REFUTED** | least-squares / a single width of 5.100 explains **all 32 pairs**; 22 of 32 pairs are `(28, 5)` so the median returns 5.600. (Confirmed independently this run: 5.100 → 32/32) |
| 74 fails t02 because the writer indents wrongly | **REFUTED** | first-inked-glyph x → 96.3 % PASS. The ink is at 73.40/92.98 and the .txt pads to it; the bbox says 56.00 because the indentation is leading spaces *inside the text run* |
| RTL or rotated lines cause the t02 failures | **REFUTED** | 0 non-upright lines on all four pages; a right-aligned cell still has an x0 |
| t09 = duplicated running heads on the forms | **REFUTED** | the "furniture" is the `D D M M Y Y Y Y` date field; the only real furniture is the page number, which the `isalpha()` filter discards. Fix written and unit-tested: `FINDINGS/t09-FIX-band-scoped-present-and-no-one-char-keys.patch` |
| …and the .txt therefore loses 21 form values | **REFUTED this run** | character counts are equal on both sides (`D` 261/261, `M` 173/173, `Y` 148/149). The 7-per-letter "loss" is lines welded onto neighbours, not characters lost |
| 39's t08 inversion is the engine reordering | **REFUTED** | same predicate, baseline key instead of bbox top → **22/22 PASS** |
| 39's / 77's / 05's / journal's t12 failure is real invention | **REFUTED** | character multisets identical on both sides; the .txt is character-for-character the source for 39 |
| U+0000 tokenisation (391, 392, 406) | **already fixed** | the control-character split in `_words` cleared all three; none of them is in the nine |
| Removing the ring-rule append fixes 305 | **REFUTED** | measured regression: `60_page_border` lost 15 of 64 lines, `318_court_summons_form` 81 → 90 lines. The append is load-bearing |
| Re-sorting the page by block top fixes 305 | **REFUTED** | a carrier paragraph costs 9.6 pt of flow; tried and reverted — fixed `32_stroke_lines` and broke `18_centred_heading_left_body_txtpos` (42/42 → 41/42) |
| 601's lost words include `General` | **already fixed** | the widget-appearance double-count guard; the residual is exactly the two ZapfDingbats ticks (`601-tick-is-a-widget-appearance-2342.md`) |
| 041122 is missing from every corpus release | **true** | it lives in `benchmarks/realworld/`, not in `corpus-v1` — that is why one early census could not measure it |

One thing the prior work asserted that this run contradicts: `T02-RULER-PAIRS-REPEATED-TEXT-WRONGLY-25NOV.md`
concludes that 334 and 74 *"stay failing because their ruler still disagrees with the width the .txt was
written with — a separate fault in the writer"*. For **334** that is right about the ruler but the
attribution is inverted (the writer's ruler is the correct one, the fit is wrong). For **74** it is
wrong outright: the writer agrees with the ink, and the source side is the one reporting the wrong x.

---

## 6. Ranked fixability

The 14 failing instances split **7 pure check artefacts · 1 mixed · 6 engine defects**, across 9
documents. Ceiling, measured or measured-and-counterfactual:

- **instrument edits alone → 207 of 213** (clears 334, 74, 39; and 77's score, whose engine defect stays)
- **+ the 600 patch → 208** · **+ 305 → 209** · **+ 601 → 210** · **+ the forms' t06 (one shared fix) → 213**

| rank | document(s) | failing check | verdict | fix, and what has been measured | blocker |
|--:|---|---|---|---|---|
| 1 | `600_reviewed_invoice_with_annotations` | t12 83 | **engine — one cause** | `PATCHES/txt-meta-annotation-26NOV-relay.patch` (a `Para.meta` flag + one `removeIf` in `TxtWriter`): measured **83 → 0, 8/8 PASS**; `word/document.xml` **byte-identical** (sha256) on 600, 041122, 601. Predicted 204 → 205 | the gate demands a 213-document .docx re-measure for an engine-fingerprint move; `p2w.py` does not finish in one pod (`BLOCKERS.md`) |
| 2 | `334_patent_document` | t02 69 % | **check** | least-squares ruler (or any estimator not dominated by a 22-pair column-5 cluster): **100 %**. Part of a 3-correction set measured at **213/213 pass, 0 regressions**, which still fails a randomised-indent .txt | instrument edit, so needs a full-corpus re-verify (not a cached `restamp --report`) |
| 3 | `74_balance_sheet_indented_subitems` | t02 80 % | **check** | first-inked-glyph x on upright non-RTL lines only: **96.3 %** (the RTL restriction is not optional — applied blindly it newly fails 4 documents) | same |
| 4 | `041122` + `Fillable` | t09 29/125 | **check** | `FINDINGS/t09-FIX-band-scoped-present-and-no-one-char-keys.patch` — one-character keys are not furniture, and `present` is counted in the same band via the U+000C segments. Unit-tested with a falsifiability test on a synthetic 3-page file | not committed (needs the corpus pass). **Note:** this makes both documents' t09 green while their t06/t12 stay red |
| 5 | `39_small_caps_letter_spacing` | t08 21/22 | **check** | key on baseline, not bbox top: **22/22 PASS**. Same one-line change as 39's t01 story (which is the tokeniser, not the order) | same |
| 6 | `305_vaccination_certificate` | t08 32/33 | **engine** | containment test instead of a midpoint test at `PdfToWord.java:1278-1279`: measured over 211 documents, it rejects exactly 1 of 22 absorbed lines (305's) and accepts the other 21, including 305's own `T`, `INDIA`, `2024`. Counterfactual on the .txt: **PASS**. What must not be done is measured (removing the append, re-sorting by top) | engine edit; the selectivity is measured but no patched-engine full run was done |
| 7 | `601_fillable_admission_form` | t01 97.6 % | **engine (and the source side)** | glyph walk over each widget's `/AP /N` (`/ZaDb 9 Tf (3) Tj`), which `PDFTextStripper` never reads — the same code region as `formValuesOf`/`widgetValue`. Both sides must agree that a `/ZaDb` tick is a tick, not `3`. **Not implemented anywhere yet** | real new engine code; also a .docx loss (two blank checkboxes) |
| 8 | `77_arabic_rtl_document` | t01 92.1 % | **mixed** | check side: the character-multiset treatment t01 has not had (the .txt has the same characters, regrouped) — would clear the score. Engine side: `logicalOrder()`'s NBSP bug (`Character.isWhitespace('\u00A0')` is false) is a real bidi defect and stays | an engine bidi fix plus an instrument change |
| 9 | `041122` + `Fillable` | t06 127 + t12 14 | **engine — hard** | two measured attempts failed (carry-on guard: 0 rows changed; `isJunk`+U+FFFD: 127 → 141, worse). The surviving lead is the embedded TrueType cmap read by GID (what MuPDF does to produce `Ĥ`), or a glyph-name fallback — a real cmap-subtable parser. The t12 14 is a separate, easier fix: stop emitting the `(Authorised signatory)` paragraph that the table cell already carries | no known working fix; both are engine-fingerprint moves |

**Cheapest remaining win, stated plainly:** rank 1 is a measured, ready patch that takes a document to
CLEAN with byte-identical .docx output, blocked only by a re-measure the pod cannot afford. Ranks 2–5
are four instrument edits, each individually measured to flip its document, whose combined effect
(213/213, 0 regressions) is already measured for the t02 half.

---

## 7. What I could not determine

- **The store does not contain measured values.** `RANKING-TXT.csv` holds `applicable, passed, failed,
  abstained, failed_ids` only; `RESTAMP-TXT.jsonl` holds the same shape. Every number in §1 is my
  re-measurement, not a quotation. I could not quote a measured value "from the store" because the
  store never recorded one.
- **Engine fingerprint.** `txt/ENGINE-STAMP.json` reads `981ff1fa35e2cf67`; my build is from HEAD
  sources and I did not run `regress.py --check`, so I cannot assert my binary is that stamp. What I
  can assert is that my scoreboard matches the committed store on all 213 rows, including every
  `applicable` count.
- **The 600 patch's effect is quoted, not reproduced.** I did not apply
  `PATCHES/txt-meta-annotation-26NOV-relay.patch` (read-only) — 83 → 0 and the byte-identical .docx are
  the 26 Nov run's measurements.
- **Which line-welding removes the 7 single-letter `D`/`M`/`Y` lines** on the forms. I proved the
  characters are all present (counts equal), but not which .txt lines absorbed them.
- **Exact apportionment of 041122's 14 characters** between the duplicated signatory line and the
  cancelling boundary shifts. The duplication is identified and real; the arithmetic per character
  (e.g. `a` and `n` net to zero because they are surplus in one place and missing in another) I did not
  itemise.
- **Which store file is authoritative on 16 vs 11 vs 9.** `HISTORY-TXT.jsonl`'s last line and
  `STATE-TXT.json` carry the same timestamp and different numbers; `classify_txt.py` was last run when
  the store held 11. The 9 in `RANKING-TXT.csv` is the one every reader (`cronreport.py`, `health.py`,
  `pending.py`, `classify_txt.py`) and `step_txt.py` agree on, and it reproduces — but the store is
  internally inconsistent and nothing in it says why.
- **Whether the fix for `77` clears a document whose .txt is still wrong.** The bidi defect is real and
  independent; I did not measure how much of the 92.1 % is boundary and how much is the NBSP run.
