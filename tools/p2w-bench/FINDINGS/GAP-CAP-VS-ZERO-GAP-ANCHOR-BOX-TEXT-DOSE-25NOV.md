# The 120 pt cap is HALF the trigger: a 2x2 dose over every box carrier in the corpus

**25 Nov 2026, fixer run.** Engine HEAD `b97d8172`, corpus cache `/scratch/work/p2w/out` (133 of 213
documents converted), LibreOffice 7.4 for page counts.

## What was measured, and why

`FINDINGS/DOCS-ROOT-CAUSES-24NOV.md` says: *"the actionable finding is not 'stop using text boxes' - it
is the 120 pt cap. A gap wider than 120 pt flips a page into positioned mode and anchors everything after
it. That is one threshold, in one place, and it decides whether 54 documents carry their body text as
text or as a picture."* That claim was reached by reading the writer, and the file itself says the trigger
was **not traced per page**. This run traced it per document.

Method: every emitted `word/document.xml` was read and the characters inside `<w:txbxContent>` counted.
That is the exposure itself - the text Google's DOCX importer rasterises. It is measurable without Drive,
it is deterministic, and it needs no model.

To dose it without a recompile per value, `-Dp2w.gapcap=<twips>` was added to the engine as an
**instrument** (`DocxWriter.gapCapTwEff`). With no property set it returns exactly what `gapCapTw`
returned; verified on four documents (`43/43`, `43/43`, `176/176`, `246/246` box characters identical to
the pre-instrument cache).

**The instrument is not in HEAD.** It was written, built, validated and used for every number below, then
reverted at the end of the run: the commit gate refuses any engine change whose corpus table has not been
re-measured, and the corpus re-measure (`benchmarks/gate.py --budget 250`, which resumes across calls) did
not finish inside the slot - it converted the cache from 133 to 170 of 213 documents and was killed at the
290 s ceiling. The 75-line patch is committed at `patches/gapcap-instrument.patch`; re-apply it with
`git apply tools/p2w-bench/patches/gapcap-instrument.patch`, rebuild, and every number here reproduces.
The engine is otherwise byte-identical to `b97d8172`, so the measurements stand.

## The population: 37 of 133 cached documents carry any box text

8176 characters in total. But two populations sit in that number and they behave in opposite ways:

- **15 stamp documents** (`03_stamp_vertical_90deg`, `08_two_overlapping_stamps`, `11_stamp_with_signature_image`,
  `01/02/04/06/07/09/13/14/15_stamp*`, `312_affidavit_stamp_paper`, `352_certificate_ornate_border`,
  `371_experience_certificate`, `318_court_summons_form`) - the box IS the construct (a rotated or curved
  stamp). Invariant under every knob below.
- **~14 body-text documents** where ordinary paragraphs and column labels are inside a box. This is the
  defect.

## The dose

| knob | box chars | documents carrying box text |
|---|---:|---:|
| HEAD (`gapcap` unset = 2400, `zganchor` on) | **8176** | 37 |
| `-Dp2w.gapcap=6000` | 7615 | 32 |
| `-Dp2w.gapcap=20000` (cap effectively off) | 7386 | 30 |
| `-Dp2w.zganchor=false` | 2374 | 35 |
| **both** | **1122** | **26** |

Per document (box characters):

| document | HEAD | cap 20k | zganchor off | both |
|---|---:|---:|---:|---:|
| `20_numbered_list_separate_column_txtpos` | 195 | **0** | 195 | **0** |
| `27_two_column_left_short_txtpos` | 43 | **0** | 43 | **0** |
| `330_cad_drawing_sheet` | 65 | **0** | 65 | **0** |
| `46_chart_coloured_labels_body_text` | 57 | **0** | 57 | **0** |
| `55_sidebar_box_beside_body` | 53 | **0** | 53 | **0** |
| `54_two_column_body_full_width_header_footer` | 76 | **0** | 76 | **0** |
| `28_value_overflows_cell_txtpos` | 66 | **0** | 66 | **0** |
| `311_fir_police_form` | 176 | 176 | **0** | **0** |
| `353_admit_card` | 24 | 24 | **0** | **0** |
| `323_credit_card_statement` | 194 | 194 | 26 | 26 |
| `400_comic_page_speech_bubbles` | 246 | 28 | 246 | **0** |
| `331_pid_diagram` | 225 | 208 | 225 | **0** |
| `322_mutual_fund_factsheet` | 311 | 311 | 242 | 16 |
| `041122-Account_Opening_Form` | 5553 | 5553 | 188 | 188 |
| every `*_stamp*` document | 43/41/38/35/30/29/28/24/20/17/16/4 | unchanged | unchanged | unchanged |

## What this says

1. **The cap alone explains 7 of the 12 body-text carriers, not all of them.** `311_fir_police_form` (176
   characters) and `353_admit_card` (24) are boxed by the **negative-gap anchor** (`ZERO_GAP_ANCHOR`), and
   raising the cap does not touch them. A cap-only change ships half a fix.
2. **The negative-gap anchor is the larger term by volume** (-71 % of all box characters on its own, against
   -10 % for the cap), because it also reaches into `041122` and `323`.
3. **The stamp population is untouched by both knobs**, so neither knob risks the constructs that are
   supposed to be boxes. That is the separation the previous investigation could not make.
4. **No page-count cost on this population.** All 14 documents whose box text changed were rendered through
   LibreOffice in both builds: **0 of 14 changed page count**, and every one matches its source PDF's page
   count. (LibreOffice is a proxy; Google's page count is the one check 01 reads, so this is a proxy result
   and is labelled as one.)

## What is NOT established

- **The vertical cost.** Both knobs buy text-as-text by giving up absolute position: `zganchor=false` writes
  `w:before="0"` for a line the page drew above the flow, and a cap of 20000 spends gaps the page budget
  may not hold. That is exactly what `18_displacement` measures, and it is the check that would absorb the
  trade. **Not measured in Google this run** - the run's slot went to the dose and the report. This is the
  number the next run must have before either knob is committed.
- **Population coverage.** 133 of 213 documents were cached. The 12 zeroed carriers are 12 of the 133; the
  full corpus may hold more, and `04_chars_missing` has 65 documents, so at most a fifth of that class is
  addressed by this mechanism.
- Whether Google charges the `w:line="1"` carrier as a full line (open question in
  `ANCHOR-FLOW-ROOT-CAUSE-DOSE-RESPONSE-24NOV.md`) - still untested, and it decides the sign of the
  displacement.

## The next run's first move

Take `27_two_column_left_short_txtpos` - it is the one document with a **committed Google measurement**
(40/42 with its 43 box characters; 42/42 when the boxes are zeroed). Convert it with
`-Dp2w.gapcap=20000 -Dp2w.zganchor=false`, upload it, and score it. If it is 42/42 the trade is real on a
real document and the pair can be built as a rule rather than a flag. If `18_displacement` fires instead,
the trade is a wash and the answer is the band-as-one-paragraph route, which nobody has built.

## The Google measurement: 40/42 -> 42/42, on the one document that has a stored Google verdict

`27_two_column_left_short_txtpos` was converted with `-Dp2w.gapcap=20000 -Dp2w.zganchor=false` (its 43
box characters go to **0**), uploaded to Google Drive, copied to a Google Doc, exported as PDF by Google,
and scored with `verify_google.py` against the source PDF.

| | stored verdict | this probe |
|---|---|---|
| engine | `b7699196` | `b97d8172` + the two flags |
| score | **40/42** | **42/42 PASS** |
| failing | `04_chars_missing`, `44_header_footer` | none |

Both recorded failures were the boxed text. The prediction in
`FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md`
("42/42 PASS once its boxes were driven to zero") reproduces exactly, on a real Google render, at the
current engine.

Probe artefacts, left in place: Drive folder `p2w-probe-25nov`, files `probe-27-both.docx` and
`probe-27-both-gdoc`. Nothing was deleted.

**Why the flags are not committed as the default.** Both knobs move every line the flow could not place,
on every document, not just this one. `regress.py` gates on a corpus-wide comparison measured on the
current engine, and a full-corpus restamp is ~54 minutes; a default flip without it is a change with no
"before and after" over the corpus, which the charter forbids. So this run commits the **instrument** that
made the dose possible and the measurement that proves the trade on a real document, and leaves the
default alone. The next run's move is stated at the top of this file.
