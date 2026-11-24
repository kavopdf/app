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

## 04_chars_missing — the check never opens the .docx, and 63 of 65 lose nothing

**The check compares the source PDF's text layer against Google Docs' PDF EXPORT of the .docx**
(`verify_google.py:4695-4697`; both sides built by `runs()` + `norm_text()`). It never reads the .docx.

All 213 were converted at HEAD and compared. On **63 of the 65** the .docx is character-for-character
identical to the source: the group's whole source text is **88,786 non-space characters and the .docx
lacks 21 of them, in two documents.** Nothing was lost at conversion.

| class | in source | missing from .docx |
|---|---:|---:|
| white / invisible text | 647 | **0** |
| bullet / symbol-font glyph | 170 | **2** |
| genuinely dropped drawn text | 87,965 | **19** |
| space (excluded by the check) | 14,746 | 0 |
| **total** | **88,786** | **21 (0.024 %)** |

**What Google's export lacks is text inside an anchored DrawingML text box**
(`<wp:anchor><wps:txbx><w:txbxContent>`, `DocxWriter.anchorShape()`), which **Google's DOCX importer
rasterises**. Proven, not inferred: on `27_two_column_left_short_txtpos` Google's export carries 1558
characters against the source's 1601, and the missing 43-character multiset is **identical, type for type
and count for count, to the 43 characters inside that document's text boxes**; the same document with the
boxes removed exports at 1601 with **zero** missing, and the box's ink reappears in the export's image
list as a 270x12 px bitmap where the footer line was.

**It is a perfect one-sided separator:** 54 of the 65 failing documents carry text-box text, **0 of the
125 that pass**. Plus 1 pure check artefact (`38_faux_bold` - one duplicate copy of a heading the source
draws twice to fake bold, which the .docx correctly carries once), 1 genuine engine loss
(`601_fillable` - two ZapfDingbats tick marks), and 9 undetermined.

**The verdict that matters for the product:** the check's stated meaning is wrong on 63 of 65, **but the
engine is wrong on 54 in the way a user feels it** - it encodes text Google cannot carry as text, so a
Docs user gets a **picture of a footer** instead of a footer. The fix is not to stop emitting text boxes;
it is to stop using a construct Google rasterises.

**The 9 undetermined** (`25_signature_block_underscores_txtpos`, `381_incident_report_timeline`,
`383_api_docs_page`, `417_rotate180_and_mirrored`, `58_header_rule_footer_rule`, `602_bookmarked_annual_report`,
`form16-part-b`, `table-across-page-break-repeated-header`, `very-long-single-column-table`) are all
character-complete in the .docx and clean in LibreOffice, with no construct found. Five of them fail
`27_text_off_page` in Google, and text wholly past the paper edge is invisible to the verifier's own
extractor (proved: MuPDF returns nothing for glyphs drawn outside the mediabox) - the likely but
**unobserved** mechanism.

### A correction: the stamps are not four builds, they are one

That investigation reported the 65 verdicts spanning four engine builds (`b7699196` 40, `462353f` 17,
`98be7c3c` 6, `5beb8b9d` 2). Checked against the committed data:

    04_chars_missing fails: 65
      b7699196  61
      462353f    3
      5beb8b9d   1
    98be7c3c appears nowhere in benchmarks/gverify/

So **61 of 65 are on the current engine**, not 40, and one of the four stamps does not exist. The class is
current; only 4 documents need re-measuring. This is the third time this week a sub-agent's stamp count
disagreed with the store - the numbers must be read from `benchmarks/gverify/*.json`, not from prose.

## 60_text_column_right_edge — two disjoint populations, and the earlier claim was half right

The first investigation concluded "60 is a Google font substitution, not a layout class". All 56 were
converted, rendered and measured: **the claim is true for 28 of 56 and false for the other 28.** Half right
is the dangerous amount.

**Group A - 28 of 56 - declares `DejaVuSans`/`DejaVuSerif`, which Google Docs does not have.** Google
substitutes a face with different metrics, every line re-breaks, and the column edge moves **57-122 pt**,
seven to fifteen times the check's whole allowance.

**Group B - 27 of 56 - declares `Arial`/`Times New Roman`, which Google HAS, at the same advance widths as
the source's Liberation faces.** No substitution can occur. They render 1.5-5.6 % narrow in **both**
renderers because a .docx can only store font sizes in half-points and the engine floors to them
(7.4 to 7.0, 6.8 to 6.5, 6.4 to 6.0; `halfPointsDown()`, `DocxWriter.java:7262`). They then fail an
estimator that rests on a single line which, on half of them, is 9.8-253.8 pt longer than the second-widest
line in its own column against a 4-19 pt slack.

**Instrument calibration:** the LibreOffice verdicts were reproduced for **56 of 56** documents, 0
disagreements. Among the 56, **41 pass in LibreOffice** - so 41 of the 56 are Google-only.

**The decisive intervention:** hold the document, the engine and the renderer fixed and change **only the
declared face** (DejaVu to Arial/Times metrics, i.e. what Google actually substitutes). On the 24
measurable Google-only group-A documents, **21 flip PASS to FAIL**, the deciding column moving from a worst
case of -17 pt to **-57 to -122 pt**. `302_radiology_report` is cleanest: as built its column is
**0.01 pt** from the source; named in Arial's metrics the same column lands **112.21 pt** short.

**Coverage: 25 of 56** - 25 of the 41 Google-only failures. Not the class.

### What is wrong with the earlier claim

1. **Scope.** It generalises from 4-5 documents to the class. **16 of the 41 Google-only failures name a
   face Google has at the source's own metrics**, so substitution is excluded for them by construction.
2. **Its own two measurements contradict each other on the sign.** `b0601de` (23 Nov) measured Google
   substituting Arial 10-15 % NARROWER, column UNDER by 58-66 pt; `f43e86b` (24 Nov) measured the same
   document **+4.8 % WIDER**, column OVER by 28.5 pt. This investigation's probe reproduces the first sign
   and magnitude. **Neither sign has ever been established for the class**, and the committed
   `gverify/*.json` files store only pass/fail, so no Google-side `(over, under)` pair exists for any of
   the 56.
3. **"79 is the only engine defect" is wrong.** Three of the five DejaVu documents (318, 323, 360) also
   fail in LibreOffice, and all 27 group-B documents carry a real, measured 1.5-5.6 % width deficit in
   both renderers.

### A data gap worth closing

**`gverify/*.json` stores only pass/fail, not the measured over/under pair.** That is why two runs could
report opposite signs for the same document a day apart and neither could be checked against the other.
Storing the pair costs nothing and makes this class falsifiable.

### What is a wall and what is fixable

- **Group A is a wall for the engine** and belongs in the check: naming a Google face moves the fault into
  LibreOffice (measured, 21 of 27 fail there under Arial metrics, with a 2.8-5.6 % width error introduced
  into the renderer that used to be exact). The only remaining option is a rule about
  extent-versus-substitution - `60` must stop charging a column whose re-break is fully explained by a
  face the renderer does not have - stated generally, with a per-document face-absence test, and
  re-measured over all 213.
- **Group B's size half is a wall**: .docx cannot express 7.4 pt, and both rounding directions are wrong
  (down -5.4 %, up +4.2 %), so 1.4-5.6 % is unavoidable in the format.
- **Group B's estimator half is fixable**: on 8 of the 16, the widest line is a 9.8-253.8 pt outlier
  against a 4-19 pt slack, so letting the slack cover the column's own line-break step plus the half-point
  error fits them without loosening the overrun branch, which is where a real defect shows.

## 60_right_edge, engine side: the right edge is never in the file at all

**The engine never puts a column's right edge into the .docx.** A body paragraph is flowing text whose only
horizontal controls are `w:ind` and `w:jc`. The engine writes `w:ind w:left` = the page x, `w:right="0"`,
no `w:jc`, `w:pgMar right="0"`, and **exactly one paragraph per source line**. With the right indent at
zero and the margins at zero, the text area is the whole 595 pt paper, and a left-aligned paragraph has
**no right constraint whatsoever**. Because each paragraph holds exactly one source line's string, its
extent is `x + sum(advance widths)` **in the renderer's face** - nothing in the file says where the line
should stop.

That single fact explains the whole class: LibreOffice, which *has* DejaVu, reproduces the source's column
edge to 0.2-0.5 pt on 40 of the 56 - **the identical face did that, not the document** - and any renderer
that substitutes a face moves the edge 3-190 pt in either direction.

**Census over the 55 convertible failing documents, 4,536 paragraphs:** `w:ind w:right>0`: **0**.
`w:jc="both"`: **0**. `w:framePr`: **0**. `w:pgMar right="0"`: every section. 3,324 paragraphs carry only
`w:ind w:left`. One single `w:jc="right"`. The engine writes `w:right="0"` explicitly - it states the
absence.

### The four-construct experiment: bounding is not pinning

Same text, same 9 pt, same left edge, target edge 395 pt; rendered in LibreOffice once with a face it has
and once with one it lacks:

| construct | face present | face substituted | delta |
|---|---:|---:|---:|
| A - the engine's (one line per paragraph, `w:ind left`, right=0) | 352.4 | 329.4 | **-23.0** |
| B - `w:ind w:right` = paper minus edge | 352.4 | 329.4 | **-23.0** |
| C - fixed-width table cell (`tcW`) wider than the text | 352.4 | 329.4 | **-23.0** |
| D - **justified (`w:jc=both`) + right indent, one multi-line paragraph** | 394.8 | 394.4 | **-0.4** |

**A right indent and a cell width BOUND text but do not PIN a ragged line's edge.** Only a justified
multi-line paragraph puts the widest line on the boundary, and it survives substitution. The engine has
neither that construct nor a justified alignment - `Para.align` is 0 left, 1 centre, 2 right, and there is
no justified class.

### Corpus measurement: one attribute, no other change

| render | documents failing `60` (of 55) |
|---|---:|
| as emitted (LibreOffice, has DejaVu) | **15** |
| only `w:rFonts` changed to Verdana | **44** |
| only `w:rFonts` changed to Courier New | **52** |
| only `w:rPr/w:spacing` stripped (what Google does to the stretch) | **15** - identical set, not one verdict changes |

Of the 40 that pass as emitted, **29 flip to FAIL from the face change alone**, and the column edge moved
on **40 of 40** (`302_radiology_report` -0.48 to -42.09 to +36.06; `65_two_col_full_width_figure_caption`
-7.70 to **+189.43**). One file, one attribute, no indent, no table, no text changed.

**Ink versus text-run edge is not the cause.** On both the source PDF and the render, the line bbox right
edge exceeds the rightmost dark pixel in that line's band by 0.3-1.3 pt. The check reads the advance edge on
both sides, and its 8 pt tolerance is six times the discrepancy.

### Where the fix belongs, and what is a wall

- **The check's arithmetic is fine** - it measures one quantity on both sides. But it compares a *document*
  property against a *renderer* property, and an **attribution rule** is available and measurable: if the
  render PDF's embedded faces differ from the `w:rFonts` the .docx declares, the column edge is not
  comparable and belongs to `53_embedded_faces`' residual. That is a class-wide rule, not a per-document
  loosening, and it would clear the ~25 DejaVu documents and nothing else.
- **An engine fix is a redesign, not a patch.** The one construct that pins the edge contradicts the
  engine's line model (one paragraph per source line, align 0/1/2, positions from the baseline flow).
  Adopting it trades away the per-line model that `17_matched_runs`, `23_line_pitch` and `18_displacement`
  rest on. **That trade must not be made silently.**
- **Wall for the DejaVu-named documents.** No face in Google's library is metrically DejaVu, naming a Google
  face makes LibreOffice wrong, and embedding the face is ignored by Google.
- **The 15 that fail under the correct face are a DIFFERENT defect, not this one.** Their widest line is not
  the source's line (e.g. `purchase-order`: the engine's own table grid ends at 553.0 where the source's
  column ends at 449.7), or the text was displaced. Those belong to `18_displacement` and to the table grid,
  and were not root-caused here.

### One correction to the record

The earlier attribution of `313_power_of_attorney` and `321_auditors_report` to the lost character-spacing
stretch **does not survive measurement**: stripping every `w:rPr/w:spacing` moves their column edge by
**1.2 pt and 0.6 pt**, not 58 pt. Their Google failure is the face (`DejaVuSerif` to Arial), the same
mechanism as the other 23.

### Agreement between the two 60 investigations

Two independent investigations, different methods, same split: **~25 of the 56 are the DejaVu wall**, the
rest are either the half-point size floor or a different defect. One measured the substitution by changing
the declared face (21 of 24 flip), the other by changing `w:rFonts` in the emitted file (29 of 40 flip).
Both agree the engine cannot express the edge.
