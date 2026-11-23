# 18_displacement — PAGE-SHIFT CENSUS

**Asked:** does ONE engine construct explain the uniform 48–68 pt upward page shift Google Docs applies
to documents failing `18_displacement`? Name the exact writer value to change.

**Measured:** 2026-11-23, on this pod. Repo `kavopdf/app` @ `83b9b2a` (engine `83b9b2a`), built with
`tools/p2w-bench/build-engine.sh` (37 s, javac from Adoptium). Google is the only renderer of record
here — no LibreOffice number appears anywhere in this document.

---

## Verdict

**No — not for the documents that fail `18_displacement` and nothing else.** Two facts, both measured:

1. **The 48–68 pt uniform shift is one construct, and it is a MULTI-PAGE construct.** It is the
   page-top gap written as `w:spacing w:before` on the first paragraph of a page while
   `w:pgMar w:top="0"`. Google honours that `w:before` at the top of the **body** but **drops it at
   the top of a page created by a page break**, so pages 2..N move up by exactly that gap. Measured
   exact: `one-page-rotated-180-degrees` page 2 carries `w:before="1097"` (54.85 pt) after the break
   and reads **−56.20 pt**, which is that document's own page-1 residual (−1.35 pt) minus 54.85 pt —
   **agreement to 0.01 pt**.

2. **The 13 documents that fail `18_displacement` alone are all SINGLE-PAGE with ZERO page breaks**,
   so the construct cannot fire on them. Measured across 14 engine `.docx` spanning
   `w:before` = 0.00 → 141.50 pt with `w:pgMar w:top="0"`: the topmost run's dy in Google on page 1
   runs **+0.06 … +11.65 pt**, `Pearson(before, dy) = +0.078`, regression **slope +0.011**. If Google
   dropped the body-top `w:before` the slope would be **−1.000**.

**The writer value to change:** `w:pgMar w:top`, currently the hard-coded literal `"0"` at
**`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:2391`**, inside
`sectPrXml(float wPt, float hPt, int cols, float gapPt)`. It must carry the page's top gap in twips,
and the page's first-line `w:before` — computed as `topGap = first.y - LINE_BASE * linePt` at
`DocxWriter.java:3535-3537` and `:3585-3587`, capped by `firstGapCapTw()` (`:3931`), emitted through
`spacing(beforeTw, …)` at `:3720` — must go to 0 for that page.

---

## Population: the documents that fail `18_displacement` and NOTHING ELSE in Google

From `benchmarks/gverify/*.json` (213 summaries), exactly **13** documents have `failed ==
["18_displacement"]` and nothing else:

`16_right_aligned_amounts_txtpos`, `31_times_body_arial_headings`, `362_price_list_dense`,
`36_embedded_subset_font`, `68_journal_wide_table_spanning`, `71_invoice_space_aligned_no_rules`,
`72_bank_statement_no_rules_right_amounts`, `balance-sheet-two-columns-of-figures`,
`bus-timetable-station-left-times-right`, `insurance-policy-schedule`, `mobile-bill`,
`table-with-no-header-row`, `two-tables-stacked-with-no-gap`.

(Their recorded totals differ — 42/42 for the first seven, 47/47 for the last six — so "one check from
clean" means 41/42 and 46/47 respectively. All 13 are recorded on engines `98be7c3c` or `462353f9`,
not on HEAD; this census re-converts all 13 on HEAD.)

## Table 1 — the 13 solo-`18` documents: source vs our `.docx` (all measured here)

Sources from the public `corpus-v1` release; `.docx` from `ConvertOne` on HEAD, one JVM per document.

| document | src pages | src page size (pt) | src topmost baseline y, p1 (pt) | docx `w:pgSz` w×h (twips) | `w:pgMar` top/hdr/ftr | header part | first-para `w:before` (twips) | = pt | page breaks | shift the construct would give (−before) |
|---|---:|---|---:|---|---|---|---:|---:|---:|---:|
| 16_right_aligned_amounts_txtpos | 1 | 595.28 × 841.89 | 60.00 | 11906 × 16838 | 0/0/0 | none | 1190 | 59.50 | 0 | −59.50 |
| 31_times_body_arial_headings | 1 | 595.28 × 841.89 | 62.00 | 11906 × 16838 | 0/0/0 | none | 1230 | 61.50 | 0 | −61.50 |
| 362_price_list_dense | 1 | 595.28 × 841.89 | 40.00 | 11906 × 16838 | 0/0/0 | none | 790 | 39.50 | 0 | −39.50 |
| 36_embedded_subset_font | 1 | 595.28 × 841.89 | 62.00 | 11906 × 16838 | 0/0/0 | none | 1230 | 61.50 | 0 | −61.50 |
| 68_journal_wide_table_spanning | 1 | 595.28 × 841.89 | 58.00 | 11906 × 16838 | 0/0/0 | none | 1150 | 57.50 | 0 | −57.50 |
| 71_invoice_space_aligned_no_rules | 1 | 595.28 × 841.89 | 62.00 | 11906 × 16838 | 0/0/0 | none | 1230 | 61.50 | 0 | −61.50 |
| 72_bank_statement_no_rules_right_amounts | 1 | 595.28 × 841.89 | 62.00 | 11906 × 16838 | 0/0/0 | none | 1230 | 61.50 | 0 | −61.50 |
| balance-sheet-two-columns-of-figures | 1 | 595.28 × 841.89 | 53.35 | 11906 × 16838 | 0/0/0 | none | 1057 | 52.85 | 0 | −52.85 |
| bus-timetable-station-left-times-right | 1 | 595.28 × 841.89 | 50.52 | 11906 × 16838 | 0/0/0 | none | 1000 | 50.00 | 0 | −50.00 |
| insurance-policy-schedule | 1 | 595.28 × 841.89 | 52.52 | 11906 × 16838 | 0/0/0 | none | 1040 | 52.00 | 0 | −52.00 |
| mobile-bill | 1 | 595.28 × 841.89 | 52.52 | 11906 × 16838 | 0/0/0 | none | 1040 | 52.00 | 0 | −52.00 |
| table-with-no-header-row | 1 | 595.28 × 841.89 | 52.52 | 11906 × 16838 | 0/0/0 | none | 1040 | 52.00 | 0 | −52.00 |
| two-tables-stacked-with-no-gap | 1 | 595.28 × 841.89 | 52.52 | 11906 × 16838 | 0/0/0 | none | 1040 | 52.00 | 0 | −52.00 |

What the table shows, uniformly across all 13:

* the section carries **zero** top margin, **zero** header and footer margin, and **no header part at
  all** — the paper's top edge and the text's top edge are declared to be the same line;
* the source's top gap is carried instead as `w:spacing w:before` on the **first paragraph of the
  body**, and it equals the source's own topmost baseline **minus 0.50–0.52 pt** in every single row
  (e.g. `mobile-bill`: 52.00 vs 52.52; `362_price_list_dense`: 39.50 vs 40.00) — that is the twip
  rounding of `topGap = first.y − LINE_BASE × linePt`, not a coincidence;
* **every one is a single page with zero `<w:br w:type="page"/>`**.

So the construct is present in all 13 — as a *body-top* `w:before`, which is exactly the position
where Google honours it. The 48–68 pt band the question quotes is the *neighbourhood* of
`−before` (−39.5 … −61.5 here), which is why the premise looks right; but a shift is only available
where Google drops the value, and on page 1 it does not.

## Table 2 — what Google actually does with that construct (measured, 14 engine `.docx`)

Google renders obtained the way `grender.py` documents: import the `.docx` as
`application/vnd.google-apps.document` (`GOOGLEDRIVE_UPLOAD_FROM_URL`, `mime_type` =
google-apps.document), then `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` to PDF. `dy = render_ry −
source_ry` on exact-text pairs unique on both sides of the page, upright runs only, using
`verify_google.runs()` and `verify_google.norm_word()` so the reading frame and the run model are the
check's own. "topmost dy" is the run highest on the page.

**Provenance caveat, stated plainly:** these 14 `.docx` are the ones published in the
`Onyx-Node/kavopdf-render-probe` artifacts repo by earlier runs, i.e. **older engine builds** — none
is byte-identical to HEAD's output (sha256 compared, all differ). They are used here as a *construct
panel*: every one carries `w:pgMar w:top="0"` and a body-top `w:before`, spanning 0.00 → 141.50 pt,
which is what the law needs. They are not a substitute for the 13 in Table 1.

| document | `w:before` (pt) | pages | page-1 topmost dy (pt) | page-1 median dy (pt) | page-2 topmost dy (pt) | check 18 in Google |
|---|---:|---:|---:|---:|---:|---|
| 401_trifold_brochure | 0.00 | 1 | +11.65 | +8.43 | – | fails |
| 344_customs_declaration | 17.50 | 1 | −2.97 | −15.23 | – | fails |
| 54_two_column_body_full_width_header_footer | 29.50 | 1 | +0.06 | +0.27 | – | **passes** |
| 12_stamp_across_page_break | 43.55 | 2 | +0.13 | +0.63 | −2.17 (before after break = 3.40) | **passes** (fails only 05, 27) |
| admit-card | 50.00 | 1 | −1.45 | −3.14 | – | fails |
| table-with-rotated-header | 52.00 | 1 | −1.36 | −4.35 | – | fails |
| delivery-challan | 54.00 | 1 | −1.46 | −4.15 | – | fails |
| one-page-rotated-180-degrees | 54.85 | 2 | −1.35 | −4.88 | **−56.20** (before after break = 54.85) | fails |
| property-tax-receipt | 54.85 | 1 | −1.44 | −7.34 | – | fails |
| 417_rotate180_and_mirrored | 61.35 | 2 | +2.95 | +2.50 | excluded (180° line, reading-frame) | fails |
| 42_table_coloured_header_alternating_rows | 61.50 | 1 | +0.12 | −7.06 | – | fails |
| 370_offer_letter | 62.50 | 1 | −2.80 | −2.80 | – | fails |
| 364_event_ticket | 77.50 | 1 | −2.41 | −16.14 | – | fails |
| 411_nested_xobject_transforms | 141.50 | 1 | +8.21 | +4.98 | – | **passes** |

**Page 1 does not respond to `w:before` at all.** The most pointed single number: the document with
the *largest* body-top gap in the panel, `411_nested_xobject_transforms`, `w:before = 141.50 pt`,
reads **+8.21 pt** — moved *down*, not up by 141.50. The document with `w:before = 0.00` reads
+11.65 pt. Over the panel, `Pearson(before, page-1 topmost dy) = +0.078` and the regression slope is
**+0.011 pt of dy per pt of `before`**; a dropped `w:before` forces slope −1.000. That is the
refutation, in one number.

**Page 2 does respond, exactly.** `one-page-rotated-180-degrees` page 2: `w:before` after the page
break = 54.85 pt, that document's own page-1 residual = −1.35 pt, so the law predicts
−1.35 − 54.85 = **−56.20 pt**. Measured topmost dy on page 2: **−56.20 pt**. Agreement 0.01 pt.
The second multi-page case is consistent in direction and size at a small value:
`12_stamp_across_page_break` carries 3.40 pt after the break and moves −2.17 pt.

## Mechanism, in one sentence, with the number

**The `.docx` declares `w:pgMar w:top="0"` and puts the page's top gap in `w:spacing w:before` on the
page's first paragraph; Google honours that value at the top of the body (slope +0.011 pt dy per pt
of `before` over 0–141.5 pt, so the top line does not move) but drops it at the top of a page opened
by a page break, which moves the whole page up by exactly the gap — 54.85 pt of `w:before` produces
−54.85 pt of dy, measured as −56.20 pt against a −1.35 pt page-1 residual.**

The alternative sentence the question offered — "the `.docx` top margin is X pt smaller than the
source's content top, and Google honours the margin exactly, so every line moves up by exactly that"
— is **refuted**, and by the panel's own numbers: the top margin is smaller by the full gap
(0 vs 40.00–62.00 pt on the 13 in Table 1), yet the top line on page 1 sits within −2.97 … +11.65 pt
of its source position on every one of the 14 panel documents. Google does not honour a *zero* margin
as "text starts at the paper edge"; it honours the paragraph's own `w:before` above it.

## How many mechanisms, and which documents each covers

**Two, split by population — and only one of them is this construct.**

* **Mechanism A — dropped page-top `w:before` after a page break.** Covers **pages 2..N of multi-page
  documents** that fail 18. This is the population the 48.5–67.6 pt band was measured on in
  `FINDINGS/18_displacement-dy-shape-101323-4fa7.md` (`bank-statement-5-pages` p1–p4, `gst-invoice` p1–p3,
  `table-across-page-break` p1–p2, `very-long-single-column-table` p1–p2, `602_bookmarked_annual_report`
  p1–p2, `academic-paper-ieee-2col` p1). Fixing the writer value above is what closes A.
* **Mechanism B — not this construct.** Covers **the 13 single-page solo-`18` documents**. They have no
  page break (Table 1, last column = 0 for all 13), so A is structurally unavailable to them; their
  page-1 displacement in the panel spans −15.23 … +8.43 pt median with no relation to `before`, i.e.
  the residual is row/line pitch inside the table body, not page-top placement. **I did not isolate
  B** — see "Not measured" below.

So: one construct for the 48–68 pt shift, but it is **not** the reason the 13 documents in Table 1 are
one check from clean. Changing `w:pgMar w:top` will not move any of them.

## What would prove me wrong

* **Refutes the verdict for the 13:** a Google render of any of the 13 Table-1 `.docx` showing a
  uniform page-1 shift near −`before` (i.e. −39.5 … −61.5 pt). My claim predicts page-1 topmost dy
  within roughly −3 … +12 pt for all 13, as the panel shows for the same construct.
* **Refutes the law:** a document with a page break whose post-break paragraph carries `w:before = V`
  and which does *not* move up by V (beyond its own page-1 residual). Predicts dy = page1_dy − V.
  Verified at V = 54.85 (predicted −56.20, measured −56.20).
* **Refutes "Google honours body-top `w:before`":** a positive slope near −1 in
  `dy` vs `before` on page 1 across the panel. Measured slope +0.011 over 0–141.5 pt.

## Not measured — stated plainly

* **The 13 documents of Table 1 were NOT rendered through Google on this pod.** The Google round trip
  needs the `.docx` bytes to reach Drive, and every binary-ingress path available here failed:
  `GOOGLEDRIVE_UPLOAD_FILE` / `CREATE_FILE` / `RESUMABLE_UPLOAD` all take a Composio `s3key` and
  rejected both `/scratch/work/...` and `/scratch/output/...` with *"The file key does not belong to
  this project or session"*; `GOOGLEDRIVE_UPLOAD_FROM_URL` accepts **https only** (a `data:` URI was
  rejected: *"scheme 'data' not in ['https']"*); pushing the `.docx` to the artifacts repo was refused
  (403, read-only App); Hugging Face refused repo creation (*"You don't have the rights to create a
  dataset under the namespace"*); and every anonymous file host is explicitly blocked in the egress
  allowlist (`!pastebin.com`, `!transfer.sh`, `!file.io`, `!tmpfiles.org`, …). So Table 2's law is
  measured on the *same construct* in older-build `.docx`, not on the 13 themselves.
  **The exact test that closes it:** put the 13 `.docx` on any public HTTPS URL, import each with
  `UPLOAD_FROM_URL` as `application/vnd.google-apps.document`, export to PDF, and measure as in
  Table 2. That is one call per document once hosting exists.
* **Mechanism B is not identified.** I can show it is not A; I cannot name its writer value.
* **`w:before` values above `firstGapCapTw()`** (`max(2000 twips, pageHeightPt × 20)`) are clamped by
  the writer; no document here reaches the cap, so the clamp's effect on Google is untested.
* The 2 multi-page panel cases are a thin base for a law; 1 of them is exact to 0.01 pt and 1 agrees
  in sign and rough size at a small value.

## Housekeeping

15 Google Docs were created in Drive by this run (`p2w18-*`, `probe-delivery-challan`,
`duri-*`). Nothing was deleted, per the brief. The cloned repo was used read-only: no commit, no push,
no edit. No secrets are written into this file.

## Reproduction

```bash
git clone https://github.com/kavopdf/app /scratch/work/CS          # @ 83b9b2a
gh release download corpus-v1 --repo kavopdf/app --pattern '*' -D /scratch/work/corpus
bash /scratch/work/CS/tools/p2w-bench/build-engine.sh              # 37 s, fetches its own JDK
# per document, one JVM each, exactly as benchmarks/p2w.py docx() does:
cd /scratch/work/CS/tools/engine-verify && java -Xmx700m -cp "out:libs/aar/classes.jar:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar" \
    ConvertOne <src.pdf> /scratch/work/out18
# Google: upload .docx -> copy as application/vnd.google-apps.document -> export PDF  (grender.py)
python3 /scratch/work/CS/tools/p2w-bench/verify_google.py <src.pdf> <google.pdf> --json out.json
```
