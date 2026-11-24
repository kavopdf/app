# `25_invisible_text` is blind: 0 of 392 Google exports can fail it

**25 Nov 2026, from a sub-agent working on a live clone, measured against real Google exports in the
user's Drive.** Recorded by the fixer run that deployed it.

## The claim under test

`FIXER-BRIEF.md` carries: *"`25_invisible_text` was fixed on 24 Nov at 01:41 and the fix left it blind -
after the sheet filter, `fills` is empty on every Google page, so the check can only ever pass."*

## It is blind, and here is the measurement

- Scored at `verify_google.py:6002` as `invisible <= s_invisible`, both numbers from `_visual_counts()`
  (`verify_google.py:800-844`).
- Commit `79ef7075` (24 Nov 01:41) added `fills = [f for f in fill_rects(p) if f["rect"].w*f["rect"].h <
  0.90*sheet_area]` - it keeps only fills SMALLER than the sheet.
- On 14 pages of 12 corpus documents exported from Drive as PDF: **14 filled rects, all 14 page-sized,
  0 survive the filter.** `behind` is `None` for every run on every page, so the check returns 0 always.
- Across 392 Google exports (400 Docs reachable): the pre-fix rule counts **239** invisible runs, HEAD
  counts **0 on all 392**, the patched rule counts 1274.
- Paired against their sources (187 documents where both exist): rule A fails 48, **HEAD fails 0 of 187**,
  patched fails 18 - while `benchmarks/gverify/*.json` still records 43 documents failing this check, every
  one predating the fix. Nothing has moved because the check cannot move.

## What it hides

Real defects. In `eway-bill` the header cells "Document type"/"Document no." and in
`mutual-fund-statement` "Field"/"Value" render **white on white** in Google (the navy band did not come
through; confirmed by rendering the export and looking at it). Pre-fix counted 6 and 4; HEAD counts 0;
both documents are recorded PASS.

## The patch, and why it is NOT committed

The agent wrote a replacement signal: render each page once at 100 dpi and take the modal colour of eight
points just outside each run's ink box (`BG_DPI = 100`, `_bg_behind()`), invisible when
`colour_close(run_colour, background, 0.08)`. Same measurement on the source, so the source-side exemption
survives. It is stable across 72/100/150 dpi (11/11/11 over 211 source PDFs) and
`test_checks.py` still reports 44/44.

**Not committed because it makes 18 documents worse, and at least two of those look like false
positives** (`301_lab_report_panel` - black table text on a pale row fill, where a sample 2-3.5 pt outside
the ink box lands on neighbouring dark text; `340_bill_of_lading` - black ID text under a barcode). A
stricter "no contrast at all" variant zeroed both but lost part of `eway-bill` and became dpi-unstable at
150 dpi.

`regress.py` refuses a change that makes documents worse, and it is right to here: the patch restores the
*ability* to fail, with an unquantified false-positive rate. The next step is to settle the sampling
radius on `301` and `340` before it ships - not to ship it and call the 18 a finding.

The patched file was returned with the run as `verify_google.py` (373,240 bytes). Nothing was committed,
pushed, or deleted; the probe exports are in the user's Drive under the existing corpus folders, untouched.
