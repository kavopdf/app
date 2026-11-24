# The docx checks, root-caused — first results

**24 Nov 2026.** The docx side has 33 failing checks over 190 scored documents. This file records the
root causes as they are proven, starting with the ten largest classes by document count:

| # | check | docs |
|---:|---|---:|
| 1 | 18_displacement | 102 |
| 2 | 04_chars_missing | 65 |
| 3 | 60_text_column_right_edge | 56 |
| 4 | 59_shape_anchor | 45 |
| 5 | 25_invisible_text | 43 |
| 6 | 45_char_accuracy | 37 |
| 7 | 13_text_colours | 32 |
| 8 | 44_header_footer | 30 |
| 9 | 17_matched_runs | 30 |
| 10 | 47_margins | 25 |

## The class size is sound: 100 of the 102 sit on one engine

The first investigation worried that the verdicts carry three engine stamps and so the class may be
stale. Checked: of the 190 scored verdicts, **186 are on `b7699196`** (the current engine), 3 on
`462353f` and 1 on `5beb8b9d`. Of the 102 `18_displacement` failures, **100 are on `b7699196`** and 2 on
an older engine. So the class is real and current; only 2 documents need re-measuring, not the set.

## 18_displacement — three constructs, 94 of 102, and "the format cannot express it" is refuted

**A .docx CAN carry a per-line vertical position, and this engine does.** `DocxWriter` emits no absolute
position for body text (0 `w:framePr` in 213 emitted files - the construct was removed because Google
ignores it), but it does not need to: `place()` (`DocxWriter.java:4124-4157`) solves each paragraph's
`w:before` from the source baseline against the position the written twips actually produced, and
`resync()` (`:4161`) re-reads that so no error accumulates. A flowing paragraph therefore preserves the
per-line y as an exact **sequence of gaps in `w:before`** - and Google honours `w:before` 1:1 (measured,
`FINDINGS/18_displacement-WBEFORE-IS-1TO1-GOOGLE-1005-agentA.md`).

**What fails the 102 is three places where the engine carries a vertical LENGTH in a property Google does
not read as a length:**

1. **`w:line` + `lineRule="exact"` used as a gap** - the table-gap spacer, `DocxWriter.java:6107-6112`
   (the refused branch of the room guard at `:6098-6103`). Google charges
   `2.5873 x max(L/240, 0.06)` pt for a declared `L/20` pt, i.e. about 22 %, so everything below the
   spacer sits high by about 0.78·G. Dose-response measured live: `68_journal_wide_table_spanning`
   144 pt becomes **-114.28 pt**; `73_marksheet` 16.7 pt becomes **-12.85 pt**.
2. **`w:before` on the first paragraph of a page after an explicit `<w:br w:type="page"/>`** -
   `place()`'s `newPage` branch (`:4124-4135`), also `:3579` and `:4468`. **Google drops it at a page
   top** (55.15 pt asked, 0.33 rendered). The construct that delivers it is `w:pgMar w:top`, and HEAD
   still writes `w:pgMar w:top="0"` (`:2411`). Proven on `bank-statement-5-pages`: -59.5 pt per page
   becomes -4.3, and 37/42 becomes 40/42.
3. **`w:trHeight` declared at the page's own pitch** (`rowHeightTw`, `:6468` and `:6516`). Google
   re-quantises the declaration onto a 0.75 pt (one CSS pixel) ladder and charges the row's own rule on
   top, so a pitch that is not on that ladder lays a rung too tall and the error is one-signed and
   cumulative down a dense table. Eleven published measurement points fit
   `laid = 0.75 x (round(d/0.75) + 1)` (`FINDINGS/18_displacement-ROW-GROWTH-075-QUANTUM-LAW-2354-fixer.md`).

**Coverage, measured at HEAD over all 213 with the constructs read out of the emitted
`word/document.xml`:**

| constructs | documents explained |
|---|---|
| (1) + (2) | **63 of 102** - 54 refused spacers with a modelled loss of 3.1 to 113.0 pt (median 16.2), 16 page-top gaps of 11.5 to 89.5 pt, 7 carrying both |
| (1) + (2) + (3) | **94 of 102** - 66 with more than 4.5 pt of accumulated row drift, max 34.2 |
| none | **8** - sub-tolerance placement offsets |

Against only **8 of the 111 non-failing** documents carrying any of the three. The remaining 8
(`31_times_body_arial_headings`, `601_fillable_admission_form`, `64_newspaper...`, `70_magazine_drop_cap...`,
`78_mixed_english_devanagari_line`, `brochure-3col...`, `gst-invoice-horizontal-rules-only`,
`newspaper-2col...`) carry none of the three - that is the population where the check itself may be at
fault, and `SETTLED.md:385-393` already told the next run to settle the `if not ds` run-matching branch
before believing this class is about vertical position.

### Why "a .docx cannot express per-line position" is wrong - three measurements

1. **Same bytes, other renderer:** of the 102, **83 fail in Google and pass in LibreOffice** on the
   identical .docx. 19 fail in both and are genuine engine placement errors.
2. **The engine's own positioner census** (`-Dp2w.census`, over all 213): across the 102 failing
   documents there is **not one rewind greater than 1 pt** - every baseline the source drew was reachable
   by a forward flow and was written. Only 5 documents contain a single line whose target was above the
   flow by more than 4.5 pt.
3. **`w:before` is 1:1 in Google**, and rewriting the spacer as `w:before` has been measured to take
   6 of 6 solo-18 documents to 42/42
   (`FINDINGS/18_displacement-table-spacer-CONFIRMED-6of16-TWO-PAGES-EXACTLY-FULL-1005-f1x.md`).

### The blocker, stated plainly

**The spacer half cannot ship alone.** The room guard refuses to spend a gap where the page has no slack,
and spending it unguarded pushes `mobile-bill` and `insurance-policy-schedule` onto a second page
(41/42 becomes 38/42). The row-height term has to land with it - and that term moves the LibreOffice proxy
that `regress.py` gates on. That is a sequencing problem for the fixer, not something reading the code can
resolve.

### Not proven

- Google could not be run in that sandbox (no Drive credentials), so the per-document `dy` for the 102 is
  **modelled** from the repo's two measured laws, not re-read. The 22 % spacer charge and the 0.75 pt row
  ladder are the repo's live measurements, not that investigation's.
- For the 8 residual documents, whether the check fails them on the tolerance clause or on `if not ds`
  needs one `verify_google.py --json` per document with the Google side available.
