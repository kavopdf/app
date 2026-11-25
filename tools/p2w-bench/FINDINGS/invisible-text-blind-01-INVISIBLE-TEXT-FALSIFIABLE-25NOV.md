# `25_invisible_text` can fail again: 2 of 37 real Google renders, and the radius is settled

**25 Nov 2026.** Engine built from `tools/install-gate.sh` on a fresh clone; every number below is
from a Google PDF exported out of Drive, not from LibreOffice and not from a synthetic mutation.

Supersedes nothing. It settles the open question left by
`FINDINGS/25_iinvisible-text-blind-25NOV.md`, which ended: *"The next step is to settle the sampling
radius on `301` and `340` before it ships."* This is that step, and the answer is that the radius was
never the problem.

---

## 1. The verdict

| | HEAD | with the patch in this tree |
|---|---|---|
| documents measured | 37 | 37 |
| documents that FAIL | **0** | **2** |
| which documents | none | `eway-bill`, `mutual-fund-statement` |
| `301_lab_report_panel` | PASS | PASS |
| `340_bill_of_lading` | PASS | PASS |
| `test_checks.py` | 44/44 | **44/44** |

The check can be made to fail. It fails on two real corpus documents, on a real Google render, for a
defect that is visible by eye in the exported PDF. The two documents the 24 Nov run used as
false-positive probes both stay clean.

## 2. Why it could not fail, restated with the count

`_visual_counts()` compared each run's colour to the fill behind it, taking fills from
`page.get_drawings()`. On a Google export that list is empty of bands:

    document                 page-sized fills   non-sheet fills   runs
    eway-bill                     1                 0            132
    mutual-fund-statement         2                 0            276
    301_lab_report_panel          1                 0            100
    340_bill_of_lading            1                 0             65

Every page carries exactly **one** filled rect and it is the sheet Google paints itself. The 0.90
sheet filter drops it, nothing remains, `behind` is `None` for every run, and the count is 0 on both
sides — so `invisible <= s_invisible` is `0 <= 0` and the check passes. Google *does* draw the bands;
it rasterises them, so they exist only in the pixels.

## 3. The exact numeric condition

A run is **invisible** when all three hold, measured on a 100 dpi RGB render of the page:

1. **Region** — sample the ring of pixels immediately outside the run's ink box: **0.5 pt** wide,
   grown only until it holds 12 pixels and **never past 1.5 pt**. Never inside the box (the glyph's
   own antialiased edge is not background), never further out (see §5).
2. **Uniformity** — the modal colour of that ring must cover **≥ 90 %** of the sampled pixels
   (`BG_PURITY`). A mixed background is not a background: the run **abstains** instead of being
   compared to whichever colour wins the vote.
3. **Colour** — the run's colour must be within **0.08 per channel** (≈ 20/255) of that modal colour
   (`BG_TOL`, unchanged from the vector rule).

The check then fails when `invisible(render) > invisible(source)` — the same identity as HEAD, which
is the point: only the *measurement of a run's background* changed, not the rule that scores it.

## 4. The evidence: a real Google render

Both documents were rendered by Google, exported as PDF, and measured against their corpus source.

**`mutual-fund-statement`, page 1, `Table 5. Bank mandate and contact details`.** Source: navy band,
white `Field`/`Value`. Google render: the band is gone; the labels are white on white paper.

    4 runs, colour #FFFFFF, background #FFFFFF, purity 1.00  ->  INVISIBLE
    source side: same 4 runs, background #1F3B62 (navy), purity 1.00 -> visible

**`eway-bill`, `Table 1. Consignment particulars`.** Same shape:

    3 runs, colour #FFFFFF, background #FFFFFF, purity 0.95  ->  INVISIBLE
    (the 4th `Field` run reads purity 0.89 and abstains — a table rule clips its ring)
    source side: all 4 runs on #1F3B62 -> visible

Both were confirmed by eye: rendering the region from source and from export side by side shows the
header row as navy-with-white-text in the source and as blank paper in the export.

**Through the verifier's own CLI**, not just the function — the check reports itself:

    $ python3 verify_google.py corpus/mutual-fund-statement.pdf gpdf/mutual-fund-statement.pdf
    mutual-fund-statement.pdf              37/42 FAIL
        25_invisible_text            source=0        render=4

    $ python3 verify_google.py corpus/eway-bill.pdf gpdf/eway-bill.pdf
    eway-bill.pdf                          40/42 FAIL
        25_invisible_text            source=0        render=3

And the two probes the 24 Nov patch broke do **not** list it:

    $ python3 verify_google.py corpus/301_lab_report_panel.pdf gpdf/301_lab_report_panel.pdf
    301_lab_report_panel.pdf               40/42 FAIL
        18_displacement              source=0        render=1
        60_text_column_right_edge    source=0        render=1

    $ python3 verify_google.py corpus/340_bill_of_lading.pdf gpdf/340_bill_of_lading.pdf
    340_bill_of_lading.pdf                 39/42 FAIL
        18_displacement              source=0        render=1
        59_shape_anchor              source=50       render=33
        60_text_column_right_edge    source=0        render=1

Both still fail other checks (18, 59, 60) — they are not clean documents, they are documents that
`25_invisible_text` must not fire on, and it does not.

## 5. Settling the sampling radius — the radius is not the knob

The 24 Nov run sampled 8 points 2–3.5 pt outside the ink box and reported false positives on `301`
and `340`. The measurement below replaces that with a continuous ring at a fixed radius, so the
answer does not depend on which 8 points happen to be chosen.

**`340_bill_of_lading`, run `SHJ202400871`, ring colour by radius** — this is the whole finding:

    rad=0.5   n=166   000000:61%  ffffff:39%
    rad=0.8   n=166   000000:61%  ffffff:39%
    rad=1.0   n=166   000000:61%  ffffff:39%
    rad=1.5   n=340   000000:61%  ffffff:39%
    rad=2.0   n=522   000000:61%  ffffff:39%
    rad=3.5   n=910   000000:61%  ffffff:39%

That run sits on a barcode. Its neighbourhood is **61 % black / 39 % white at every radius from 0.5
pt to 3.5 pt**. A bigger radius does not find a better background — it reaches further into the same
neighbour. Black text against a 61 %-black vote reads as black-on-black, which is the false positive.
Shrinking the radius cannot fix it either, because the mix is already there at the smallest radius
that clears the glyphs.

The true positive is uniform at every radius:

    mutual-fund-statement, run 'Field'
    rad=0.5 .. 3.5   n=76..460   ffffff:100%

So the separating property is **uniformity, not distance**. Radius is therefore fixed at the
*smallest* value that yields pixels (0.5 pt, capped at 1.5 pt) — chosen to stay as far as possible
from neighbours, since going further out has no upside and a known downside — and `BG_PURITY` does
the discrimination.

**Document-level verdict by geometry** (`s/g` = source count / render count, `!` = the render
exceeds the source, i.e. FAIL):

    document                 inset    ring@1.5  ring@2.0  ring@2.5  ring@3.0  ring@3.5
    301_lab_report_panel     0/0      0/0       0/0       0/0       0/0       0/0
    340_bill_of_lading       0/0      0/1!      0/1!      0/1!      0/1!      0/1!
    mutual-fund-statement    0/0      0/4!      0/4!      0/4!      0/4!      0/4!
    eway-bill                0/0      0/4!      0/4!      0/4!      0/4!      0/4!

Every ring radius reproduces `340`'s false positive; the inset geometry avoids it only by missing
`mutual-fund-statement` entirely (short labels are ≥85 % ink inside their own box, so there is no
background to read). Neither extreme is usable — which is why the shipped rule is ring + purity.

**Tolerance and purity grid**, 37 documents, count of documents that FAIL:

    purity   t=0.04  t=0.06  t=0.08  t=0.10  t=0.12
    0.80       2       2       2       2       2
    0.85       2       2       2       2       2
    0.90       2       2       2       2       2
    0.95       2       2       2       2       2
    0.99       1       1       1       1       1

Identical verdicts across the whole 0.04–0.12 tolerance range and 0.80–0.95 purity range; at 0.99 the
`eway-bill` runs (purity 0.95) drop out and only 1 document fails. `0.90` is chosen as the middle of
the stable band, with `0.08` kept because HEAD already used it — no constant moved without reason.

**DPI stability** (tol 0.08, purity 0.90):

    document                72 dpi    100 dpi   150 dpi
    eway-bill               0/3!      0/3!      0/4!
    mutual-fund-statement   0/4!      0/4!      0/4!

Same two documents at all three resolutions. The run *count* moves with dpi on `eway-bill` (3 → 4,
the fourth run crossing the purity bar); the verdict does not.

## 6. Source side, all 213 corpus PDFs

The exemption `invisible(render) <= invisible(source)` is only as good as the source-side count, so
the source was re-measured across the whole corpus:

    documents: 213
    src count differs HEAD vs PATCH: 1
      text-held-twice-shadow-text   0 -> 8
    nonzero on source under PATCH: 3
      gst-invoice-with-qr-code      1 -> 1
      salary-slip-corporate         1 -> 1
      text-held-twice-shadow-text   0 -> 8

One document moves, and it moves **up**: `text-held-twice-shadow-text` genuinely carries invisible
text that the vector rule could not see. That widens its own exemption and cannot cause a failure.
No document's source count falls, so no document can fail that did not fail before because of the
source side.

## 7. The patch

`tools/p2w-bench/verify_google.py`, **uncommitted, in the working tree** (122 insertions, 26
deletions). `_visual_counts()` keeps its signature and its scoring line; the background is now read
from pixels.

    BG_DPI      = 100     one render per page
    BG_RING_PT  = 0.5     ring width outside the ink box
    BG_RING_MAX = 1.5     hard cap on how far out it may grow
    BG_PURITY   = 0.90    a mixed background abstains
    BG_TOL      = 0.08    per channel, unchanged
    BG_MIN_PX   = 12

The vector rule is kept as a fallback when numpy is unavailable, so a pod without numpy degrades to
the old behaviour rather than crashing.

**Cost.** First cut allocated a full-page boolean mask per run: 26.7× the old check on a 2-page
document. Slicing the window around the run instead brings it to **6.6×** (`mutual-fund-statement`
39.6 ms → 259.9 ms) and **3.1×** on `340_bill_of_lading` (25.5 ms → 77.8 ms). At ~260 ms for a 2-page
document the 213-document corpus costs roughly 4 minutes for this one check.

## 8. Regression tests

    python3 tools/p2w-bench/test_checks.py     ->  44/44 cases behave as claimed

This includes the two cases that cover this check directly — *"text turned invisible by the
conversion"* (must fire `25_invisible_text`) and *"invisible text the source already had"* (must not
fire) — so the synthetic known-invisible input still produces a FAIL and the exemption still holds.
`falsify.py` was not run: it needs `--corpus`, `--render` and `--docx` directories over the whole
corpus, and building those is a full corpus conversion, not a check of this change.

## 9. Command lines

    git clone https://github.com/kavopdf/app /scratch/work/CS
    bash tools/install-gate.sh                      # pod-prep: 213 PDFs, JDK 17, engine -> out/

    # convert the probes through the engine
    cd tools/engine-verify && CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
    java -cp "$CP" ConvertOne /scratch/work/p2w/corpus/<doc>.pdf /scratch/work/probe

    # the Google render: Drive export of the Google Doc -> PDF
    #   GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId, mimeType="application/pdf")
    # 34 corpus documents exported this way, plus 301/340/eway-bill/mutual-fund-statement = 37

    python3 probe25.py   /scratch/work/gpdf /scratch/work/p2w/corpus    # fill census + HEAD counts
    python3 sweep.py     /scratch/work/gpdf /scratch/work/p2w/corpus <doc...>   # radius x tolerance
    python3 stability.py                                                # tolerance x purity x dpi
    python3 before_after.py                                             # HEAD vs PATCH, 37 docs
    python3 src_side.py                                                 # source side, 213 docs
    python3 tools/p2w-bench/test_checks.py

## 10. Per-document table (37 documents, real Google renders)

`s/g` = invisible count on source / on Google render.

    document                               | HEAD s/g | PATCH s/g | HEAD -> PATCH
    01_stamp_rotated_15deg_upright         |  0/0     |  0/0      | PASS -> PASS
    02_stamp_rotated_15deg_upleft          |  0/0     |  0/0      | PASS -> PASS
    03_stamp_vertical_90deg                |  0/0     |  0/0      | PASS -> PASS
    041122-Account_Opening_Form            |  0/0     |  0/0      | PASS -> PASS
    04_stamp_180deg_upside_down            |  0/0     |  0/0      | PASS -> PASS
    05_round_company_seal_curved_text      |  0/0     |  0/0      | PASS -> PASS
    06_rect_paid_stamp_red_transparent     |  0/0     |  0/0      | PASS -> PASS
    07_stamp_over_table                    |  0/0     |  0/0      | PASS -> PASS
    08_two_overlapping_stamps              |  0/0     |  0/0      | PASS -> PASS
    09_stamp_font_not_embedded             |  0/0     |  0/0      | PASS -> PASS
    10_stamp_as_image                      |  0/0     |  0/0      | PASS -> PASS
    11_stamp_with_signature_image          |  0/0     |  0/0      | PASS -> PASS
    12_stamp_across_page_break             |  0/0     |  0/0      | PASS -> PASS
    13_stamp_non_english                   |  0/0     |  0/0      | PASS -> PASS
    14_stamp_chars_positioned_td           |  0/0     |  0/0      | PASS -> PASS
    15_stamp_on_scanned_page               |  0/0     |  0/0      | PASS -> PASS
    16_right_aligned_amounts_txtpos        |  0/0     |  0/0      | PASS -> PASS
    17_three_column_widths_txtpos          |  0/0     |  0/0      | PASS -> PASS
    18_centred_heading_left_body_txtpos    |  0/0     |  0/0      | PASS -> PASS
    19_hanging_indent_txtpos               |  0/0     |  0/0      | PASS -> PASS
    20_numbered_list_separate_column_txtpos|  0/0     |  0/0      | PASS -> PASS
    21_form_labels_x60_values_x300_txtpos  |  0/0     |  0/0      | PASS -> PASS
    22_invoice_four_columns_txtpos         |  0/0     |  0/0      | PASS -> PASS
    23_timetable_grid_txtpos               |  0/0     |  0/0      | PASS -> PASS
    24_address_block_indents_txtpos        |  0/0     |  0/0      | PASS -> PASS
    25_signature_block_underscores_txtpos  |  0/0     |  0/0      | PASS -> PASS
    26_footnote_marker_bottom_note_txtpos  |  0/0     |  0/0      | PASS -> PASS
    27_two_column_left_short_txtpos        |  0/0     |  0/0      | PASS -> PASS
    28_value_overflows_cell_txtpos         |  0/0     |  0/0      | PASS -> PASS
    29_dot_leaders_txtpos                  |  0/0     |  0/0      | PASS -> PASS
    300_prescription_rx                    |  0/0     |  0/0      | PASS -> PASS
    301_lab_report_panel                   |  0/0     |  0/0      | PASS -> PASS
    302_radiology_report                   |  0/0     |  0/0      | PASS -> PASS
    303_discharge_summary                  |  0/0     |  0/0      | PASS -> PASS
    340_bill_of_lading                     |  0/0     |  0/0      | PASS -> PASS
    eway-bill                              |  0/0     |  0/3      | PASS -> FAIL
    mutual-fund-statement                  |  0/0     |  0/4      | PASS -> FAIL

    documents 37 | HEAD fails 0 | PATCH fails 2 | PATCH regressions vs HEAD 2

## 11. What this does not establish

- **The false-positive rate is measured, not proven zero.** 35 of 37 documents are unchanged, and the
  two probes that broke the 24 Nov patch are clean, but 37 documents is a sample. The remaining 351
  Google exports were not re-exported and measured here.
- **The 43 historical failures were not reproduced.** They predate the 24 Nov fix; this patch makes
  the check capable of failing again, which is a precondition for re-testing them, not a re-test.
- **`eway-bill` is 3 of 4, not 4 of 4.** The fourth `Field` run reads purity 0.89 against the 0.90
  bar and abstains. The document fails either way.
- **`falsify.py` was not run** (needs a full corpus render, see §8). `test_checks.py` 44/44 is the
  regression evidence used instead.
- **The renders are Google Docs already in the corpus Drive folder** (modified 21–23 Nov, exported
  25 Nov), not a fresh upload of this clone's own `.docx`. Uploading a fresh one was attempted and
  blocked: the Drive upload tools require a platform file key, and a sandbox path is rejected with
  *"The file key does not belong to this project or session"*. The engine in this clone was used to
  convert the probes for inspection, and it is the same engine lineage as the Docs behind these
  renders, but a render of this exact clone's output was not obtained. This does not affect the
  finding — the check reads the PDF, and these are real Google PDFs of real corpus documents — but
  it does mean the renders are not byte-for-byte from this build.
- Nothing was committed, pushed or deleted. `git status` shows one modified file:
  `tools/p2w-bench/verify_google.py`.
