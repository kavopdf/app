# 18_displacement / A - the dy shape

Asked: for the documents that fail `18_displacement` in the GOOGLE render and PASS it in
       LibreOffice - same engine, same .docx, two renderers - what does the displacement
       actually look like? Which of UNIFORM PAGE SHIFT / PROGRESSIVE DRIFT / FIRST-LINE
       OFFSET / SCATTER / TAIL dominates, and is the magnitude proportional to font size
       (em-relative line height) or constant in points (a fixed margin/spacing value)?

Claim: It is a block displacement, never a per-run scatter. On all 28 failing Google pages dy
       (= render_ry - src_ry, negative = drawn higher on the page) is fit by a constant plus a
       monotone drift down the page, dy = a + b*y, with residual sd 0.0-5.5 pt. UNIFORM PAGE
       SHIFT dominates: 15 of 28 pages, and 14 of those 15 sit 48.5-67.6 pt above their source
       position with the drift contributing only 0.1-23.2 pt (the fifteenth, 302_radiology, is a
       plain 8.9 pt move with 7.4 pt of drift). PROGRESSIVE DRIFT is a real but
       secondary shape - 12 pages, 1.8-19.4 pt of offset and 7.4-23.2 pt of monotone drift
       (b = +1.85 to +3.6 pt per 100 pt of page depth where the ramp is material, i.e. Google's
       table rows are ~2-3.6 % TALLER than the source's, so the block grows as you go down the
       page). The magnitude is CONSTANT IN POINTS, not proportional to font size: on
       bank-statement-5-pages p1 type from 6.0 pt to 13.0 pt is displaced by -55.7 to -56.7 pt,
       so |dy|/size falls from 9.29 to 4.36 across the page's own size range.

Evidence:

PROVENANCE. The exported render PDFs are NOT in the repository: `benchmarks/gverify/` holds 212
summary-only JSONs (name/status/passed/failed, no `checks`) plus one full one, `benchmarks/`
contains 5 source PDFs and 0 .docx, and no file on disk records a per-page dy. So both renders
were REGENERATED for this finding rather than read:
  engine      built from this repo's head with tools/p2w-bench/build-engine.sh (javac, 36 s)
  sources     10 PDFs from the public corpus-v1 release (gh release download)
  .docx       ConvertOne, one JVM per document, exactly as p2w.py does
  LibreOffice soffice --headless --convert-to pdf
  Google      upload .docx -> copy as application/vnd.google-apps.document -> export PDF,
              i.e. exactly the three Drive steps grender.py documents
  measurement a copy of verify_google.py with a per-page probe added and NO other change. It
              reuses the real `pairs`, `flat` and `_tol` objects, so the numbers are the ones
              check 18 itself sees. 10 documents, 28 pages, source PDFs 1-7 pages each.

REPRODUCTION CHECK. The 10 documents were chosen because the recorded JSONs say they fail 18 in
Google and pass it in LibreOffice. The regenerated renders reproduce that exactly:
  Google 18_displacement render-count: 302=1, 324=7, 370=1, 52=1, 602=2, academic=1,
                                       bank=5, gst=4, table-across=3, vlsct=3  (28 pages)
  LibreOffice 18_displacement render-count: 0 on all 10 documents, on every page.
  LibreOffice for contrast: worst per-page |dy| 0.52-4.11 pt, worst_here <= 0.913 on every page
  of every document. Google's worst_here reaches 253.56.

PER-PAGE TABLE - every page check 18 charges in the Google render. dy range is min..max over the
UNAMBIGUOUS pairs (text unique on its page). Repeated cell text can be paired with the wrong
twin; those pairs are excluded from the shape statistics but NOT from n/n_out/worst_here, which
are the check's own numbers.

| document | page | n | n_out | worst_here | dominant shape | dy range (pt) | median dy |
|---|---:|---:|---:|---:|---|---:|---:|
| 302_radiology_report | 0 | 32 | 29 | 3.93 | UNIFORM PAGE SHIFT | -9.9 .. -1.6 | -8.9 |
| 324_loan_amortisation_schedule | 0 | 249 | 238 | 195.639 | PROGRESSIVE DRIFT | -24.1 .. -1.6 | -14.1 |
| 324_loan_amortisation_schedule | 1 | 249 | 231 | 225.189 | PROGRESSIVE DRIFT | -29.4 .. -9.2 | -19.4 |
| 324_loan_amortisation_schedule | 2 | 249 | 231 | 225.189 | PROGRESSIVE DRIFT | -29.4 .. -9.2 | -19.4 |
| 324_loan_amortisation_schedule | 3 | 249 | 231 | 225.189 | PROGRESSIVE DRIFT | -29.4 .. -9.2 | -19.4 |
| 324_loan_amortisation_schedule | 4 | 249 | 231 | 225.189 | PROGRESSIVE DRIFT | -29.4 .. -9.2 | -19.4 |
| 324_loan_amortisation_schedule | 5 | 249 | 231 | 225.189 | PROGRESSIVE DRIFT | -29.4 .. -9.2 | -19.4 |
| 324_loan_amortisation_schedule | 6 | 2 | 2 | 4.971 | TAIL | -14.5 .. -13.1 | -13.8 |
| 370_offer_letter | 0 | 37 | 17 | 3.573 | PROGRESSIVE DRIFT | -10.6 .. +0.2 | -2.5 |
| 52_one_cm_margin_wide_body | 0 | 38 | 26 | 2.807 | PROGRESSIVE DRIFT | -8.3 .. +0.4 | -4.9 |
| 602_bookmarked_annual_report | 1 | 9 | 9 | 21.495 | UNIFORM PAGE SHIFT | -67.7 .. -67.5 | -67.6 |
| 602_bookmarked_annual_report | 2 | 11 | 11 | 45.273 | UNIFORM PAGE SHIFT | -67.7 .. -67.1 | -67.6 |
| academic-paper-ieee-2col-abstract | 1 | 62 | 62 | 24.459 | UNIFORM PAGE SHIFT | -63.4 .. -59.7 | -60.2 |
| bank-statement-5-pages | 0 | 117 | 77 | 4.727 | PROGRESSIVE DRIFT | -11.2 .. +5.4 | -2.0 |
| bank-statement-5-pages | 1 | 117 | 117 | 110.945 | UNIFORM PAGE SHIFT | -66.4 .. -49.8 | -56.9 |
| bank-statement-5-pages | 2 | 117 | 116 | 61.618 | UNIFORM PAGE SHIFT | -66.4 .. -49.8 | -57.1 |
| bank-statement-5-pages | 3 | 117 | 115 | 149.391 | UNIFORM PAGE SHIFT | -66.4 .. -49.8 | -57.1 |
| bank-statement-5-pages | 4 | 117 | 116 | 104.58 | UNIFORM PAGE SHIFT | -66.4 .. -49.8 | -57.1 |
| gst-invoice-multipage-item-table | 0 | 116 | 102 | 20.752 | PROGRESSIVE DRIFT | -13.3 .. +2.7 | -8.6 |
| gst-invoice-multipage-item-table | 1 | 110 | 110 | 73.718 | UNIFORM PAGE SHIFT | -65.8 .. -51.1 | -61.8 |
| gst-invoice-multipage-item-table | 2 | 110 | 110 | 50.21 | UNIFORM PAGE SHIFT | -65.8 .. -51.1 | -61.0 |
| gst-invoice-multipage-item-table | 3 | 37 | 37 | 28.33 | UNIFORM PAGE SHIFT | -65.8 .. -51.1 | -64.3 |
| table-across-page-break-repeated-header | 0 | 215 | 142 | 3.735 | PROGRESSIVE DRIFT | -8.9 .. +5.2 | -2.4 |
| table-across-page-break-repeated-header | 1 | 215 | 215 | 169.685 | UNIFORM PAGE SHIFT | -55.0 .. -40.9 | -48.5 |
| table-across-page-break-repeated-header | 2 | 36 | 36 | 30.525 | UNIFORM PAGE SHIFT | -55.0 .. -49.4 | -54.2 |
| very-long-single-column-table | 0 | 181 | 138 | 10.996 | PROGRESSIVE DRIFT | -8.7 .. +14.5 | +1.8 |
| very-long-single-column-table | 1 | 180 | 173 | 253.56 | UNIFORM PAGE SHIFT | -69.2 .. -46.0 | -58.4 |
| very-long-single-column-table | 2 | 150 | 142 | 218.232 | UNIFORM PAGE SHIFT | -69.2 .. -50.0 | -60.4 |

Tally: UNIFORM PAGE SHIFT 15, PROGRESSIVE DRIFT 12, TAIL 1, SCATTER 0, FIRST-LINE / HEADER
OFFSET 0. The rule, applied to band medians (40 pt vertical bands of the unambiguous pairs):
UNIFORM when the constant part is at least as large as the monotone part (|median dy| >=
max-min of the band medians), PROGRESSIVE when the monotone part is larger, TAIL when at most 2
runs are out and the page fails only on worst_here > 2. Median |dy| across the 28 pages is 33.95
pt; 14 pages read |median dy| >= 20 pt, all of them in the 48.5-67.6 pt band.

THE SHAPE IN FULL - band medians from the top of the page to the bottom:
  very-long-single-column-table p1   -69.17 -> -46.00  (+1.2 pt per 40 pt band)
  table-across-page-break... p1      -55.00 -> -40.87  (+1.1 pt per 40 pt band)
  324_loan_amortisation_schedule p1  -29.45 ->  -9.18  (+1.4 pt per 40 pt band)
  bank-statement-5-pages p1          -66.40 -> -49.78  (+0.75 pt per 40 pt band)
  bank-statement-5-pages p0           -0.05 (header) -> -11.25 (table head) -> +5.37 (footer)
  gst-invoice-multipage-item-table p1 -52.10 (header) -> -65.80 (table head) -> -56.93 (foot)
So on the table pages the whole table is drawn tens of points above where the source puts it,
and the error shrinks monotonically as you go down the page: Google's rows are slightly taller,
so the block stretches and the top of the table is furthest out. Two pure cases confirm the
decomposition - 602_bookmarked_annual_report p1 is a = -67.4 with 0.1 pt of drift (a top-margin
move and nothing else), while very-long-single-column-table p0 is 1.8 pt of offset with 23.2 pt
of drift (a row-pitch move and nothing else). gst-invoice is a third sub-shape: a ~14 pt STEP at
the table head with only a shallow ramp after it, which is why its linear b reads ~0.2.

FONT SIZE. dy is flat in size, so the em term of the tolerance is not what is being violated:
  bank-statement-5-pages p1     size 6.0 -> dy -55.74 ; 6.8 -> -58.77 ; 13.0 -> -56.70
  academic-paper-ieee-2col p1   size 7.2 -> dy -60.19 ; 7.4 -> -60.85 ;  9.2 -> -60.09
  302_radiology_report p0       size 6.5 -> dy  -8.93 ; 8.5 ->  -8.93 ; 12.0 ->  -2.78
  Pearson(|dy|, size) across the 28 pages runs -0.68 to +0.16. A 13.0 pt line and a 6.0 pt line
  on the same page move by the same 56 pt. Constant in points, not proportional to size.

How to test it: rebuild the engine and regenerate a failing document's two renders (the five
steps above, or `python3 benchmarks/p2w.py --diagnose N` for the LibreOffice half), then fit
dy = a + b*y per page over the runs check 18 pairs. The claim predicts, for any document of this
class:
  (1) residual sd of that fit <= ~5.5 pt while |a| is tens of points - i.e. no page is SCATTER;
  (2) b > 0 (+1.85 to +3.6 pt per 100 pt of depth) wherever the drift term is material, and
      b ~ 0 on a page that is a pure top-margin move (602, academic-paper) or a single step at
      the table head (gst-invoice);
  (3) the LibreOffice render of the SAME .docx gives |a| < 4.5 pt and |b| < 0.1 on every page.
A page whose dy does not fit a + b*y is a counterexample and should be reported. A sharper
discriminator: if the mechanism is table top spacing plus row pitch, a page carrying ONE row of
table should read |a| small and b ~ 0, and |a| should grow with the number of rows on the page.

Confidence: high for the shape and for constant-in-points - both are direct per-run measurements
       on 28 pages through the check's own pairing code, and the LibreOffice control reads n_out
       = 0 on every page. Medium for the mechanism sentence (table top spacing plus row pitch):
       the a/b decomposition and the two pure cases are measured, the attribution to Google's
       two spacing values is inferred, not proved against its layout engine. Scope: 28 pages
       from 10 of the 107 documents in this Google-only class; the rest were not measured.

Ruled out:
  SCATTER - 0 of 28 pages. dy fits a + b*y with residual sd 0.0-5.5 pt (worst 5.47, on
    gst-invoice p3, 37 runs). The scatter visible in a raw per-run listing is duplicate-text
    mispairing, not layout: bank-statement p1 has 25 of 117 runs whose text occurs more than
    once, and those pairs read -157.65 / -44.00 / +10.45 while the page's band medians are
    -66.40 .. -49.78. Excluding them the page is a 57 pt block move with a 16.6 pt ramp.
  FIRST-LINE / HEADER OFFSET - 0 of 28 pages, and the inverse is what happens. On
    302_radiology the header's 3 runs read -2.78 / -1.62 / -2.32 (all inside their tolerances)
    and every run from the table down reads -8.93..-9.89, footer included: the header is the
    part that did NOT move. Same on 370_offer_letter (-2.8..-1.1 in the letterhead, -10.6..-3.8
    in the table) and 52_one_cm_margin_wide_body (+0.4 body, -8.4 table, -4.9 after it).
  TAIL - 1 of 28 pages (324_loan p6: 2 runs, both out, worst_here 4.97 - the page carries only
    the last two rows of the table). Everywhere else n_out/n is 0.46-1.00, not one stray run.
  FONT-SIZE PROPORTIONALITY - rejected above: dy is flat across a 6.0-13.0 pt size range on a
    single page and Pearson(|dy|, size) is negative on most pages. It is a fixed point value.
  A LIBREOFFICE-SIDE FAULT - rejected: the same .docx through soffice reads n_out = 0 on all 28
    pages, worst_here <= 0.913, max |dy| 4.11 pt. Nothing in the engine's .docx is displaced;
    only Google's layout of it is.
  A BROKEN INSTRUMENT - rejected for these documents: the probe reuses check 18's own pairs and
    reproduces the recorded verdicts, 10/10 failing in Google and 10/10 passing in LibreOffice.

Status: complete

