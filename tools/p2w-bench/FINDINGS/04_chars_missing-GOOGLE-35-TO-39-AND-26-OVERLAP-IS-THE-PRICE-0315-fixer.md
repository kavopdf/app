# 69_two_col_legal_numbered_clauses in Google: 35/42 -> 39/42, five of the named classes pass, and 26_text_overlap is the price

**25 Nov 2026, 03:15 IST, fixer.** A real Google render of a real build. This is the strongest measurement of
the anchored-text-box line of work so far, and it says the direction is right and the guard is what is
missing.

## The build measured

    git apply FINDINGS/04_chars_missing-GAPCAP-PATCH-0225-agent.patch   (spendWideGap(), +102 lines)
    FOOT_BAND = 0.0f                                                     (the guard removed, line 418)
    ConvertOne -Dp2w.pagepos=0 -Dp2w.anchorkeep=0 -Dp2w.zganchor=false

`word/document.xml` of the emitted .docx: **36 `<wps:txbx>` / 1358 characters at HEAD -> 0 / 0.**
No anchored text box remains. Page count unchanged (1 page, both builds).

## The Google render

`GOOGLEDRIVE_CREATE_FILE(mimeType=application/vnd.google-apps.document, parents=[KavoPDF-Verify])` ->
`GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(application/pdf)` -> `verify_google.py <source> <export> --docx`.

| | recorded HEAD (`b7699196`) | this build |
|---|---|---|
| score | **35/42** | **39/42** |
| failing | 04_chars_missing, 10_font_sizes, 13_text_colours, 17_matched_runs, 38_list_markers, 44_header_footer, 45_char_accuracy | 18_displacement (source=0 render=1), 26_text_overlap (source=0 **render=11**), 60_text_column_right_edge (source=1 render=0) |

**Six checks the brief names as one construct now PASS:** `04_chars_missing`, `45_char_accuracy`,
`13_text_colours`, `44_header_footer`, `17_matched_runs` — plus `10_font_sizes` and `38_list_markers`.

**Three new failures are the cost:** `18_displacement`, `26_text_overlap` and `60_text_column_right_edge`.
`26_text_overlap` at **11** rendered overlaps is the serious one: spending a wide gap as `w:before`
anywhere on the page lets a line land on content the page had already drawn. That is exactly what the
foot-band guard was protecting, and why `FOOT_BAND = 0.90` made the patch a no-op here.

## Why the guard is the whole problem

The signature block of this document sits mid-page, after a wide gap, so `FOOT_BAND = 0.90` never lets the
gap be spent and the block stays anchored. Dropping the band to 0 spends it and the block becomes real
paragraphs — and three lines then land on top of something.

The condition the patch is missing is not a band, it is a **look-ahead**: spend the gap only if no line
remaining on this page has a target baseline below this one. On the last block of a two-column page that is
true; in the body of a drawing sheet it is false, which is why spending everywhere cost `330_cad` its
displacement in the earlier measurement. The engine already knows every remaining box at that point — it
has the page in hand — so this is a comparison, not a new pass.

## Not established

- Whether the look-ahead guard keeps the 39/42 while removing the 11 overlaps. Not measured.
- Whether `18_displacement` (source=0 render=1) and `60` (source=1 render=0) are caused by this build or
  were already true of the recorded HEAD row under a different check numbering. HEAD recorded neither, so
  they are new on this build.
- One document, one build. This is not a class result and nothing was committed to the engine.

## The state of the tree

The engine change was **reverted**. The gate refused it as an unmeasured engine and `26_text_overlap = 11`
is a real regression on a real document; neither is something to commit. The patch, the guard constant and
the three switches are all in this handoff so the next run starts at the look-ahead guard, not at the
beginning.
