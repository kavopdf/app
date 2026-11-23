# `04_chars_missing` × anchored text box — verdict on the carried-over claim

**Claim tested:** *"Google drops `wps:txbx` text; the missing-character multiset in check
`04_chars_missing` is fully explained by anchored text boxes on 9 documents."*

**Verdict: REFUTED as stated.** The construct is real and one document proves it causally in
Google, but the claim's number is wrong (the construct's population is 54 of 65, not 9), its
"fully" is wrong (11 of the 65 carry no shape text at all, and 2 of those lose characters in
LibreOffice too), and the per-character equality it asserts has never been measured on more
than one document. The number **9** does appear in this data — it is the size of the group the
text box mechanism does **not** explain.

Everything below is computed from the clone at `kavopdf/app` (shallow, HEAD of the default
branch). No build was run, no engine file was touched, nothing was deleted. The corpus of 213
PDFs is not in the repository (208 are release assets) and `.docx` outputs are not committed,
so **no per-document count of `w:txbxContent` could be recomputed here** — that census exists
only as a written claim in one FINDINGS file, and is marked as such wherever it is used.

---

## 1. The failing population, recomputed

- `benchmarks/gverify/*.json` holds 213 verdict files. Documents whose `failed` list contains `04_chars_missing`: **65**.
- Those verdicts were measured across **4 different engine builds** (`b7699196` 40, `462353f` 17, `98be7c3c` 6, `5beb8b9d` 2), so the 65 is a mixed-build set, not one engine's result.
- A second committed result set disagrees by one document: `benchmarks/blast-carrier-2008.json`
  (engine `c55e1916`) records **66** documents failing `04_chars_missing`. The difference is
  exactly `353_admit_card`, which passes all checks in `gverify/` and fails `04` in
  `blast-carrier-2008.json`. **The denominator is 65 or 66 depending on which committed file you
  read.**
- No document fails `04_chars_missing` alone: the minimum failed-check count in the group is 2, and 4 documents fail exactly two checks (one of which is `04`).
  So no document isolates this check, and no attribution is single-cause by construction.

## 2. How many characters are missing — what is and is not committed

`benchmarks/gverify/*.json` carries **pass/fail only**. Its keys are exactly `name, status, rc,
passed, total, failed, engine` (plus `measured`/`method`/`export_sha256` on 9 freshly measured
files). There is **no count and no detail text** for `04_chars_missing` in the Google verdicts,
and no Google render or text-layer dump is committed. **The Google-side missing-character count
per document is therefore not determinable from committed data.** Three committed proxies exist,
and they measure three different things:

| committed source | what it compares | value for the 65 |
|---|---|---|
| `RANKING.csv` `chars_missing` | source PDF vs the **.docx** (text recall) | 0 on 63 of 65; 19 on `38_faux_bold_italic_synthesised`; 2 on `601_fillable_admission_form`; **sum 21** |
| `CENSUS.csv` `src_chars - docx_chars` | source PDF vs **python-docx extraction** of the .docx | covers only 25 of 65 documents; **sum 13,062** over those 25 |
| `gverify-lo/*.json` `checks['04_chars_missing']['render']` | source PDF vs the **LibreOffice** render | 0 on 63 of 65; 2 on `601_fillable_admission_form`; 19 on `38_faux_bold_italic_synthesised` |

Two consequences, both load-bearing:

1. **63 of the 65 documents pass `04_chars_missing` in LibreOffice with a render count of 0.**
   The characters are present in the `.docx` and survive one importer. Whatever removes them is
   specific to Google's import — which is consistent with the text-box mechanism but does not
   single it out from any other construct Google's importer mishandles.
2. `RANKING.csv` says the `.docx` keeps **100.00 % of the source's characters** on 63 of the 65
   (`chars_missing` 0). The only two with a docx-side deficit are the two that also fail in
   LibreOffice. So the census's larger deficits are **not** evidence of loss — see §5.

## 3. Per-document table

Columns: `chars_missing` = `RANKING.csv` (source vs .docx, the only committed per-document
character deficit); `census def.` = `CENSUS.csv` `src_chars - docx_chars` where the document is
censused; `LO 04` = the LibreOffice render's `04_chars_missing` count (0 = LibreOffice keeps
every character); `mech.` = the mechanism group from §4.

| # | document | chars_missing (vs .docx) | text_recall | census def. | LO 04 | mech. | evidence |
|---:|---|---:|---:|---:|---:|:--:|---|
| 1 | `01_stamp_rotated_15deg_upright` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 2 | `02_stamp_rotated_15deg_upleft` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 3 | `03_stamp_vertical_90deg` | 0 | 100.0 | 144 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 4 | `04_stamp_180deg_upside_down` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 5 | `06_rect_paid_stamp_red_transparent` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 6 | `07_stamp_over_table` | 0 | 100.0 | 93 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 7 | `08_two_overlapping_stamps` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 8 | `09_stamp_font_not_embedded` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 9 | `11_stamp_with_signature_image` | 0 | 100.0 | 64 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 10 | `13_stamp_non_english` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 11 | `14_stamp_chars_positioned_td` | 0 | 100.0 | 83 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 12 | `15_stamp_on_scanned_page` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 13 | `20_numbered_list_separate_column_txtpos` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 14 | `25_signature_block_underscores_txtpos` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 15 | `27_two_column_left_short_txtpos` | 0 | 100.0 | 72 | 0 | (a) | carries `w:txbxContent` (FINDINGS census); **construct proven causal in Google (43 chars, txbx 4->0, 40/42 -> 42/42)** |
| 16 | `28_value_overflows_cell_txtpos` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 17 | `311_fir_police_form` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 18 | `312_affidavit_stamp_paper` | 0 | 100.0 | 90 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 19 | `318_court_summons_form` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 20 | `322_mutual_fund_factsheet` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 21 | `323_credit_card_statement` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 22 | `330_cad_drawing_sheet` | 0 | 100.0 | 113 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 23 | `331_pid_diagram` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 24 | `344_customs_declaration` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 25 | `352_certificate_ornate_border` | 0 | 100.0 | 75 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 26 | `364_event_ticket` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 27 | `371_experience_certificate` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 28 | `381_incident_report_timeline` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 29 | `383_api_docs_page` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 30 | `38_faux_bold_italic_synthesised` | 19 | 98.01 | 63 | 19 | (c) | font/glyph — faux-bold triple draw; loss reproduces in LibreOffice (render 19) |
| 31 | `400_comic_page_speech_bubbles` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 32 | `411_nested_xobject_transforms` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 33 | `417_rotate180_and_mirrored` | 0 | 100.0 | 8 | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 34 | `43_red_stamp_over_black_text` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 35 | `46_chart_coloured_labels_body_text` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 36 | `54_two_column_body_full_width_header_footer` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 37 | `55_sidebar_box_beside_body` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 38 | `58_header_rule_footer_rule` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 39 | `601_fillable_admission_form` | 2 | 99.58 | 23 | 2 | (d) | something else — /ZaDb tick glyph in a widget /AP/N stream is never extracted; also fails in LibreOffice (render 2) |
| 40 | `602_bookmarked_annual_report` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 41 | `61_two_col_abstract_spanning` | 0 | 100.0 | 100 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 42 | `62_two_col_newsletter_pull_quote` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 43 | `65_two_col_full_width_figure_caption` | 0 | 100.0 | 672 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 44 | `66_two_col_footnotes_bottom` | 0 | 100.0 | 477 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 45 | `67_two_col_with_sidebar` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 46 | `69_two_col_legal_numbered_clauses` | 0 | 100.0 | 1,403 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 47 | `70_magazine_drop_cap_photo_caption` | 0 | 100.0 | 76 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 48 | `80_gstin_pan_cin_ifsc_table` | 0 | 100.0 | 43 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 49 | `academic-paper-ieee-2col-abstract` | 0 | 100.0 | 3,070 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 50 | `admit-card` | 0 | 100.0 | 116 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 51 | `delivery-challan` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 52 | `form16-part-b` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 53 | `gst-invoice-horizontal-rules-only` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 54 | `magazine-2col-pullquote-spanning` | 0 | 100.0 | 2,221 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 55 | `newsletter-3col-header-footer` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 56 | `newspaper-2col-fullwidth-headline` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 57 | `one-page-rotated-180-degrees` | 0 | 100.0 | 67 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 58 | `policy-2col-spanning-section-heading` | 0 | 100.0 | 3,101 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 59 | `property-tax-receipt` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 60 | `report-2col-table-spanning-both-columns` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 61 | `table-across-page-break-repeated-header` | 0 | 100.0 | — | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |
| 62 | `table-inside-two-column-page` | 0 | 100.0 | 244 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 63 | `table-of-contents-dot-leaders` | 0 | 100.0 | 143 | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 64 | `table-with-rotated-header` | 0 | 100.0 | — | 0 | (a) | carries `w:txbxContent` (FINDINGS census) |
| 65 | `very-long-single-column-table` | 0 | 100.0 | 501 | 0 | (e) | not determinable — no shape text, passes 04 in LibreOffice, no committed mechanism |

## 4. Verdict per document group

**(a) Anchored / text-box construct — 54 documents.** Every one of these is
named, in the previous run's own census, as carrying `wps:txbx` / `w:txbxContent` text
(`tools/p2w-bench/FINDINGS/04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent.md`,
§1 table "54 of 65" and §4 census row "54/65"). **This presence count is not recomputable from
the clone** — it needs the 213-PDF corpus and an engine build, both excluded here — so it is a
single-source claim, not an independently verified fact. Within the group the mechanism is
*proven* for exactly one document and *correlated* for the other 53:

- **Proven (n = 1):** `27_two_column_left_short_txtpos`. `RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md`
  records a controlled change measured in Google (Drive upload → Google Doc → PDF export →
  `verify_google.py`): the document's only two text boxes hold the only two missing lines, the
  missing count is 43 characters, and driving `w:txbxContent` from 4 to 0 took the document from
  **40/42 FAIL to 42/42 PASS** with the footer lines reappearing in Google's text layer. That is
  the one place in the repository where the missing-character multiset and the text-box multiset
  are shown to be the same set, and it is exact.
- **Correlated (n = 53):** construct present, check fails, LibreOffice clean. Necessary-condition
  evidence at population scale, not a per-character match.

Within group (a) a sub-split is worth naming, because it is the reason the claim is
over-generalised: the stamps and rotated pages (`01`, `02`, `03`, `04`, `06`, `07`, `08`, `09`,
`11`, `13`, `14`, `15`, `43`, `411`, `one-page-rotated-180-degrees`, …) put text in a shape
because OOXML has no other construct that carries a rotation angle. For those the construct is
unavoidable, and "Google drops `wps:txbx` text" is a statement about a trade the writer made
deliberately, not a defect it can simply drop.

**(b) Table cell construct — 0 documents.** No committed file attributes a `04_chars_missing`
failure to a table cell. The one document where a cell-vs-box confusion was investigated and
**refuted** is `041122-Account_Opening_Form` (`content-missing-partly-replaced-B-1300.md`: "the
20-line wrap is inside a `wps:txbx` text box" — on this document it is not; both copies of the
heading live in table cells). That document does **not** fail `04_chars_missing`, so it neither
supports nor refutes the claim; it is a recorded instance of the text-box premise being applied
where it did not hold.

**(c) Font / encoding — 1 document:** `38_faux_bold_italic_synthesised`.
`RANKING.csv` gives `chars_missing` 19 (text recall 98.01 %), and the LibreOffice render loses
**19** characters — the same 19. (`CENSUS.csv` records a 63-character deficit for the same file;
that is the census extractor's own shortfall — see §5 — not 63 lost characters, since the
LibreOffice render, which reads the same `.docx`, loses only 19.) Because the
loss reproduces in LibreOffice, it is **engine-side, not a Google import behaviour**, and the
text-box mechanism cannot be its cause (the document carries no shape text per the FINDINGS
census). Mechanism files: `38-faux-bold-TRIPLE-DRAW-0225-fixer.md` (the same line drawn three
times: fill, fill, stroke) and `content-missing-partly-replaced-D-110200-a7c4.md`. The exact
sub-mechanism — which of the three draws is dropped and why 19 characters and not 57 — is **not
stated** in a committed file, so the group label is established and the sub-mechanism is not.

**(d) Something else — 1 document:** `601_fillable_admission_form`.
`RANKING.csv` `chars_missing` 2, census deficit 23, LibreOffice render **2** — again a loss that
reproduces outside Google, so not an import behaviour. `601-tick-is-a-widget-appearance-2342.md`
measures the cause: the missing mark is a tick drawn in a **checkbox widget's `/AP /N` appearance
stream**, and `PDFTextStripper` does not process annotation appearance streams — "530 glyphs,
every one Helvetica or Helvetica-Bold, no Zapf face at all" in the page content streams. This is
an extraction gap in the annotation layer, not a font-map or encoding failure, which is why it
is (d) rather than (c).

**(e) Not determinable — 9 documents:** `25_signature_block_underscores_txtpos`, `381_incident_report_timeline`, `383_api_docs_page`, `417_rotate180_and_mirrored`, `58_header_rule_footer_rule`, `602_bookmarked_annual_report`, `form16-part-b`, `table-across-page-break-repeated-header`, `very-long-single-column-table`.
Each of these: fails `04_chars_missing` in Google; carries **no** shape text per the FINDINGS
census; **passes** `04_chars_missing` in LibreOffice with a render count of 0 (so the characters
are in the `.docx`); and has **no** committed mechanism note. `18disp-prize-sizing-agentA.md`
lists four of them in a table whose last column reads, literally, `not stated`. The previous
run's own §8 records the same gap: *"None of the candidate families in §4 fires on them either,
so whatever they are, it is not in that list."* **No mechanism is assigned here.**

## 5. What the committed numbers say about the claim's three parts

**Part 1 — "9 documents".** Wrong. The construct's population is **54 of 65** by the
previous run's own census, and 11 documents are explicitly named as carrying no shape text. No
committed file anywhere states 9 for this check (`grep` over the repo finds "9 documents" only
in unrelated findings — one-check-away counts, fill counts, a nine-document patch). The one 9 in
this data is exactly **9**: the documents that carry no shape text **and** pass in LibreOffice —
that is, the group the text box mechanism does **not** explain.

**Part 2 — "fully explained".** False at the population level: 9 documents are
undetermined and 2 more are engine-side, so at most 54 of 65 can even be candidates, and
none of the 11 is explained by the construct. "Fully" also fails on magnitude inside group (a):
the previous run measures **14,449 of 84,364 characters (17.1 %)** living inside `w:txbxContent`
across the 54 documents. For the construct to explain the missing multiset *fully*, Google would
have to drop exactly the text-box characters and nothing else on every one of the 54 — which is
the untested part. On 53 of them the two multisets have never been compared.

**Part 3 — "the missing-character multiset".** The multiset is not in the data. A per-character
comparison needs Google's export text layer per document; `gverify/*.json` stores pass/fail only
and no export is committed. The single document where the comparison was made and recorded
(`27_two_column_left_short_txtpos`, 43 characters, exact) is n = 1.

### A trap in the census, recorded so it is not re-found as evidence

`benchmarks/census.py` computes `docx_chars` with python-docx over `document.paragraphs` and
table cells. That walk **does not see text inside `w:txbxContent`**, so the census's deficit is
text-box-blind by construction. On the five shape-heavy documents where both numbers are
committed, the census deficit exceeds the published `w:txbxContent` character count by a small,
consistent margin — i.e. the deficit *is* essentially the text-box text, which corroborates the
construct but cannot be read as text loss:

| document | chars in `w:txbxContent` (FINDINGS) | census deficit | difference | difference as % of deficit |
|---|---:|---:|---:|---:|
| `policy-2col-spanning-section-heading` | 3,041 | 3,101 | +60 | 1.9 % |
| `academic-paper-ieee-2col-abstract` | 2,942 | 3,070 | +128 | 4.2 % |
| `magazine-2col-pullquote-spanning` | 2,182 | 2,221 | +39 | 1.8 % |
| `69_two_col_legal_numbered_clauses` | 1,358 | 1,403 | +45 | 3.2 % |
| `66_two_col_footnotes_bottom` | 448 | 477 | +29 | 6.1 % |

(`400_comic_page_speech_bubbles` and `331_pid_diagram` also appear in the FINDINGS table but are
not among the 62 censused documents, so no comparison exists for them.)

## 6. What is already measured in `tools/p2w-bench/FINDINGS/`

Grep of the directory: 18 files mention `04_chars_missing`, 14 mention `txbx`/`txbxContent`, 24
mention text box. The load-bearing ones:

| file | what it measures |
|---|---|
| `04_chars_missing-25_invisible_text-TXBX-IS-RASTERISED-1750-agent.md` | **the claim's source.** 127 documents re-converted at HEAD; `w:txbxContent` present in 54/65 `04` failures, 14/48 `25` failures, **0/30** Google-clean; 14,449 of 84,364 chars (17.1 %) inside shape text; per-document character counts for 7 documents; §8 lists the **11** failures with no shape text and states the mechanism inside Google is *inferred, not observed* |
| `RUNNING-FOOT-IS-A-ROW-GOOGLE-DROPS-THE-BOX-1855-fixer.md` | **the only causal Google measurement.** `27_two_column_left_short_txtpos`: 43 characters missing, both missing lines in the document's only 2 text boxes, `txbx` 4→0 → 40/42 → 42/42 PASS. Also names a second, untouched site (`flowFromBox`) and records that `55_sidebar_box_beside_body` and `61_two_col_abstract_spanning` still carry 4 boxes each |
| `00-READ-FIRST-audit-23nov-agent.md` | the standing count, "documents failing 04_chars_missing: 65" |
| `00_page_count-ANCHORSHAPE-CARRIERS-1615-agent.md` | which documents carry `anchorShape` output, and the text-box variants |
| `00_page_count-EMPTY-PARAGRAPH-COSTS-THE-PAGE-0530-fixer.md` | "Google does not drop the shape. It **rasterises** it: 108 vector drawings in the source become 108 images" |
| `00_page_count-SHAPE-RUNS-NOT-PARAGRAPHS-LANDED-0730-fixer.md` | the white-masthead case, i.e. the `25_invisible_text` face of the same construct |
| `content-missing-partly-replaced-B-1300.md` | the **refutation** of a text-box premise on `041122-Account_Opening_Form`: the wrap lives in table cells, not in a `wps:txbx` |
| `38-faux-bold-TRIPLE-DRAW-0225-fixer.md`, `content-missing-partly-replaced-D-110200-a7c4.md` | the faux-bold triple draw, i.e. the (c) document |
| `601-tick-is-a-widget-appearance-2342.md` | the tick in the widget `/AP /N` stream, i.e. the (d) document |
| `18disp-prize-sizing-agentA.md` | per-document failed-check sets; `04_chars_missing` is the only failure on **0** documents (recomputed here: still 0) and one-of-exactly-two on **2** (recomputed here: **4** — `27_two_column_left_short_txtpos`, `38_faux_bold_italic_synthesised`, `411_nested_xobject_transforms`, `61_two_col_abstract_spanning`, so that table is stale by 2); four of the (e) documents are annotated `not stated` |
| `DEFECT-CLASSES-GOOGLE.md`, `GOOGLE-VS-LIBREOFFICE.md` | the class counts: 65 in Google, **2** in LibreOffice, 63 fixed-in-LibreOffice-only |

## 7. What would prove this verdict wrong

Any one of these would overturn it:

1. **A Google text-layer dump per document.** For any document in group (e) — say
   `very-long-single-column-table` or `table-across-page-break-repeated-header` — a Google export
   whose missing characters are shown to sit inside a shape would move it to (a) and take the
   undetermined count down. Nothing in the repository rules that out; nothing in it supports it
   either.
2. **A re-census at HEAD finding `w:txbxContent` in the 11.** The presence census is the one
   load-bearing number I could not recompute. If it is wrong — if, for instance, `anchorShape()`
   also writes text through an `mc:Fallback` VML `w:pict` path, or a second emitter exists — the
   population changes and the 54/11 split collapses.
3. **A per-character equality on the 54.** Extract, for each of the 54, the character multiset
   inside `w:txbxContent` from the `.docx` and the missing multiset from Google's export text
   layer. If they match exactly on all 54, part 2 of the claim ("fully") is proven for group (a)
   and only the population error stands. If any document's missing multiset contains characters
   that are **not** in a text box, the claim fails even inside group (a) — and the 17.1 % figure
   says the room for that is large.
4. **A Google render of `66_two_col_footnotes_bottom` or `322_mutual_fund_factsheet`.** The
   previous run names both as ready-made separators of the two sub-mechanisms (rasterisation vs
   clipping). Either result would firm up the *why*, neither would change the population.
5. **`353_admit_card`.** A fresh Google measurement of that one document settles whether the
   denominator is 65 or 66 and whether it belongs in group (a) or (e).

What would **not** change this verdict: a LibreOffice measurement. LibreOffice passes
`04_chars_missing` on 63 of 65; the check is a Google-import
instrument, and only a Google round trip can move any document between groups.

---

## 8. Method and limits

- Source: `git clone --depth 1 https://github.com/kavopdf/app`, HEAD of the default branch. The
  clone succeeded; no fallback was needed.
- Computed, not estimated: the failing set (`benchmarks/gverify/*.json`), the 65/66 discrepancy
  (`benchmarks/blast-carrier-2008.json`), every `chars_missing` and `text_recall` value
  (`benchmarks/RANKING.csv`), every census deficit (`benchmarks/CENSUS.csv`), every LibreOffice
  `04_chars_missing` render count (`benchmarks/gverify-lo/*.json`, 213 files, full coverage of the
  65), the group sizes, and the deficit-vs-`w:txbxContent` comparison in §5.
- **Not recomputed, quoted from a committed claim:** the per-document presence of
  `w:txbxContent` (54/65, 11 named non-carriers) and the 14,449/84,364 character total. Both need
  the 213-PDF corpus (208 files are release assets, not in the repo) and an engine build, both
  excluded by the task. Every place they are used is labelled.
- **Not determinable from committed data:** the Google-side missing-character count for any
  document; the mechanism for the 9 group-(e) documents; the sub-mechanism inside group (a) —
  the previous run states plainly that rasterisation and clipping fit its counts equally.
- No build, no Google Drive call, no engine edit, no deletion. The clone is under
  `/scratch/work/CS` and is untouched.
