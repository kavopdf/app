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

## 04_chars_missing, engine side: the trigger is a 120 pt gap cap, and both investigations agree

A second investigation, working from the writer, reached the same 54 and named the mechanism to the line.

**The engine does not lose these characters - it writes them into a DrawingML anchored text box instead
of a paragraph.** `DocxWriter.para()` (`:3101`) routes every line into `anchorBox()` once that page's flow
has entered `ctx.positioned` mode, and `anchorShape()` (`:5580`) emits the text as
`<wps:wsp><wps:cNvSpPr txBox="1"/>...<wps:txbx><w:txbxContent>` at **`DocxWriter.java:5664`**.

**And the trigger is a vertical gap wider than 120 pt.** `ctx.positioned` is set by the gap guards in
`flowFromBox()` (`:4381`, and lines 4453, 4487, 4587) and `flowRow()` (`:3571`, 3594, 3663) when a gap
exceeds `gapCapTw()` - **2400 twips (120 pt)** unless `ctx.spendGaps` is true (`:400`). On a two-column
page, a band boundary or a running footer is wider than that cap, so it becomes "a position, not a gap"
and **every line after it is anchored**.

**Those boxes are body text, not stamps.** 286 of the 341 anchored boxes in the 65 documents are
`anchorPos` (84 %), against 13 stamp boxes, with zero `rot=` on the big carriers. Whole policy clauses,
article paragraphs and column labels are inside them.

**The separation is perfect and has no exception:** `w:txbxContent` present means 54 fail
`04_chars_missing` and **0 pass**; absent means 11 fail and 125 pass.

**And the arithmetic is exact.** Emptying `<w:txbxContent>` and nothing else, then rendering and running
the real check, reproduces the box character count to the character: 2586/2586, 2505/2505, 1811/1811,
1155/1155, 535/535, 246/246, 106/106, 90/90, 59/59, **43/43**. That last is
`27_two_column_left_short_txtpos`, the one document with a committed Google measurement: 43 missing,
40/42 FAIL to **42/42 PASS** once its boxes were driven to zero.

**The engine drops only 19 characters across all 65 documents, all on `38_faux_bold`.** On the other 64 it
drops zero - measured by converting all 213 at HEAD and diffing the check's own source extraction against
`word/document.xml`.

**The U+FFFD hypothesis explains 0 of the 65.** It is a real latent check-side defect - on
`041122-Account_Opening_Form` PyMuPDF reads 127 characters as CIDs where the engine writes U+FFFD, so the
check would report 127 missing characters no reader can see - but that document and its twin are
`page_count_refused` and never reach the 47 checks. Measured over all 65 with the check's own
`runs()`/`norm_text()`, the U+FFFD count is **zero on every one**.

### Who owns the fault, stated precisely

For the 54, the **renderer** drops the text: the .docx is valid and complete, LibreOffice reads every
character, and the diff finds no deficit. **But the engine's writer owns the exposure** - it chooses, for
ordinary body text, a construct its own source already records Google mishandling (the `w:framePr` note at
`DocxWriter.java:5174-5200`, and the off-page-box note at `5590-5600` measuring 123 characters recovered by
moving the anchor back onto the sheet).

**So the actionable finding is not "stop using text boxes" - it is the 120 pt cap.** A gap wider than 120 pt
flips a page into positioned mode and anchors everything after it. That is one threshold, in one place, and
it decides whether 54 documents carry their body text as text or as a picture.

### Not established

- The sub-mechanism of the 19-character loss on `38_faux_bold`: the letters are scattered singles, none off
  the page box, and they do not line up with the document's duplicate-position glyphs.
- Whether `ctx.spendGaps = pageFits(page, ph)` is false on exactly the pages that flip into positioned mode
  was not traced per page. Disabling the `PAGE_POSITION_ON_ANCHOR` cascade (`-Dp2w.pagepos=0`) moved the
  box count only 495 to 483, so that flag is not the driver; the trigger sits in the `gapCapTw` branches.
- The 9 undetermined documents need a Google export text layer, which no sandbox could obtain.

### Two independent investigations, same answer

One worked from the documents and found the missing character multiset identical to the text boxes'
contents; the other worked from the writer and found the routing path and the 120 pt cap. Both say **54 of
65**, and both say the boxes are body text. That is the strongest agreement of any class so far.

## 18_displacement, check side: the engine is wrong, and the fix is measured

A third investigation converted all 102 failing documents, read every emitted `document.xml`, and ran three
constructions against the repo's unmodified `compare()`. Its verdict: **the engine is wrong, not the
check** - though the check is wrong at the margin, and that margin is worth fixing too.

**The engine's .docx does not encode absolute vertical positions at all.** It encodes Word spacing hints
that each renderer resolves differently, and `DocxWriter.java` says so itself (`:78-95`): Word and
LibreOffice advance by `w:before + w:line/20`; Google advances by
`w:before + max((w:line/240) · lineHeight(face, size), 0.069 · size)` - **one sign, every line, so it
accumulates down the page.**

**Two sites, both measured on the corpus:**

1. **The page's whole top gap is emitted as `w:spacing w:before` on the first paragraph after
   `<w:br w:type="page"/>`, and Google DROPS space-before at a page top.** The emitted gap was matched
   against Google's own measured displacement, document by document:

   | document | gap emitted | Google's displacement |
   |---|---:|---:|
   | 412_page_labels_roman | 61.4 pt | **-59.0** |
   | 416_many_tiny_pages | 89.5 | **-87.2** |
   | 602_bookmarked_annual_report | 69.5 | **-67.6** |
   | academic-paper-ieee-2col | 59.7 | **-56.1** |
   | table-across-page-break | 49.2 | **-48.5** |
   | bank-statement-5-pages | 55.2 | **-57.1** |

2. **Every row height is emitted `hRule="atLeast"` - 1,701 of 1,710 `<w:trHeight>` across the 102.** A
   row's laid height is therefore the renderer's own content height, and rows stretch differently in
   Google, giving the progressive drift the repo already censused at +1.85 to +3.6 pt per 100 pt of depth.

**The corpus-wide split settles whose fault it is: 102 of 190 fail in Google, 22 of 213 in LibreOffice on
the same files.** Nothing in the document is misplaced; Google lays it elsewhere.

### Sizing, on the 72 documents that carry a stored Google displacement record

| group | count | cause | side |
|---|---:|---|---|
| page break, fails on a continuation page | **13** | page-top gap as `w:before`, dropped by Google | engine |
| first page only, `worst_dy` 5-400 pt | **40** | per-line advance / `atLeast` row height | engine |
| block offset <= 4.5 pt AND internal spread <= 4.5 pt | **19** | nothing exceeds the check's own cap | **check** |
| `worst_dy` <= 4.5 pt at all | **8** | entirely inside the tolerance band | **check** |

So the engine explains about 53 of the 72 (about 75 of 102 scaled) and the check's over-sensitivity about
19 (about 27). Note 58 of 72 fail on page 0 only, and only 16 of the 102 contain a page break at all - the
page-top family is the **biggest-magnitude** mechanism, not the most numerous.

### The earlier suspicion: true about the instrument, false as the root cause

Both halves reproduced on the unmodified `compare()`:

- **A rigid shift fails.** `370_offer_letter` translated by `1 0 0 1 0 -dy cm` on every page: PASS at 2.0 pt,
  **FAIL at 3.0 pt**, through the `n_out == len(ds)` block clause. Every glyph keeps its position relative
  to every other glyph.
- **A colliding line passes.** 12 lines at 16 pt pitch, source min ink gap 2.26 pt: one line moved 7.0 pt
  gives **PASS with 4.74 pt of ink overlap**; 8.0 pt gives FAIL. The single-run crossover is exactly 2x
  tolerance while a rigid shift is charged at 1x.

**But neither is the root cause of the class.** Every rigid shift this check actually charges in the corpus
is 56-87 pt (2-3 cm), which is a genuine visible fault, and 8 of 72 documents have no run more than 4.5 pt
out at all. **The check is wrong at the margin, not at the centre.**

### The measured fix

**Engine, and it is measured:** make every vertical dimension the .docx carries a *length both renderers
read as a length*.

- **The page-first path** - `spacing(int beforeTw, int lineTw, float size, boolean auto, boolean pageFirst)`
  (`DocxWriter.java:149`) and its caller - must stop carrying the page's top gap as `w:before`. **The repo's
  own controlled probe measured the replacement: a 1x1 `w:tbl` with `w:trHeight w:val="G" w:hRule="exact"`
  delivers 55.83 of 55.15 pt in Google, against 0.33 pt for `w:before`.** It must also be charged to the
  page's fill budget or pages overflow - the 20 Nov attempt turned 6 pages into 10.
- **Row height** must write `hRule="exact"` instead of `"atLeast"`; the file already argues at
  `:2243-2253` that exact is safe inside cells.

**Both are Google-only changes.** LibreOffice is already exact, so `regress.py` cannot see them - which is
exactly the gate conflict `BLOCKERS.md` recorded at 2026-11-24 03:25. That is a sequencing problem for the
fixer, and it is the same wall the other two 18_displacement investigations hit.

**Check, second order:** judge `dy` on the baseline rather than the bbox top - a face swap alone moves the
bbox top 0.20 pt (helv to tiro) and 1.40 pt (helv to cour) at 10 pt, so part of the 1-3 pt medians the
first-page failures carry is the instrument, not the document. And stop forgiving a single colliding line at
2x tolerance while charging a rigid shift at 1x; a rigid translation changes ink contact by zero at every
displacement, so the block clause is measured by nothing in the ink-contact curve that defends the
tolerance.

### Three investigations on 18_displacement, one conclusion

All three name the same two constructs - the page-top `w:before` Google drops, and the row height - and all
three say the fix is engine-side and blocked by the LibreOffice proxy that `regress.py` gates on. The third
adds the measured replacement (1x1 exact table, 55.83 of 55.15 pt) and the sizing split.

**Not measured by any of them: a live Google render.** All three sandboxes hit the same wall - every Drive
write path needs an `s3key` the platform `upload` tool would stage, and that tool is not bound here. The
Google-side numbers come from the stored per-document records and the repo's committed census, not from a
fresh round trip.

## 59_shape_anchor — three charges wearing one name, and a test that was written and never called

**`59_shape_anchor` is not one defect class.** Its conviction logic has three exits and two of them belong
to other checks: text moved inside the same box (that is `18_displacement`'s question), text absent from
the render (that is `04_chars_missing`'s question), and "the outline moved and the text stayed"
(`_box_moved`).

**`_box_moved` has no position term.** It returns True whenever a box of the source box's width and height
exists anywhere on the render - which is exactly the case when the box is still where the page put it.
Demonstrated on a document's only box: `_box_moved(B, source_shapes, source_shapes)` returns **True**, i.e.
"the outline moved" is reported with the outline unmoved. And `_same_box(B, B shifted 2.1 pt)` returns
**False**, so identity is lost at 2.1 pt.

**The test written to stop two unrelated rectangles being compared is dead code.** `_same_object`
(`verify_google.py:2308`) - filled-versus-outline primitive **and** the set of texts the box holds - is
**defined and never called**. `_face` and `_held` likewise. The executed identity gate is `_same_box`
(`:2271`), four corners within 2 pt, with no notion of what the rectangle *is*. And `_box_moved` is a hard
tripwire: one run fails the page, with no 5 % budget.

**Shape populations do not correspond at all:**

| document | source shapes | .docx shapes | reproduced within 2 pt |
|---|---:|---:|---:|
| 48_form_coloured_border_coloured_values | 1 | 14 | 1 |
| 324_loan_amortisation_schedule | 42 | **1483** | 2 |
| 375_attendance_register | 14 | 456 | 2 |
| 77_arabic_rtl_document | 9 | 4 | **0** |
| mutual-fund-statement | 23 | 19 | **0** |

**45 of 45 have a different shape population; 38 have more; 27 do not reproduce at least one source box at
its own geometry.**

**Measured against real Google renders of 11 documents:** the engine is wrong on **7** (proven - six stamp
documents with `MOVED(samebox)` and dy of -7.5 to -41.9 pt verified on the baseline, and `35_rotation`
fires on all six because the writer drops preset shapes under a rotated CTM at `PdfToWord.java:4231`);
the check is wrong on **2** (sole explanation, with all 44 other checks passing); 2 are a duplicate charge
of `04`'s question; and **32 of the 45 also fail `18_displacement`, so 59 is re-asking 18's question in
another frame.**

**Also:** `344_customs_declaration` **passes** 59 against a fresh Google render although the committed
record says it fails - a stale verdict. And the "PDF box drawn as four lines versus a .docx table border"
theory is **falsified as the dominant cause**: the 45 anchor 18 % of 4,327 runs to rule-assembled faces
against 39 % of 9,210 in the passing population.

**Honest limit:** the check-side hole did not fire on any of the 11 real Google renders, so it cannot be
claimed as the majority cause. 27 documents are structurally exposed to it and unrendered.

## 04_chars_missing — one document is unsatisfiable by construction

A third investigation confirms the 54 and adds the decisive facts:

- **62 of 65 have "characters absent from the flow text" that are exactly, multiset-equal to the characters
  inside `wps:txbx`** - 12,289 of 88,786 source characters (13.8 %), on 54 documents.
- **Running the check's own `compare()` against a LibreOffice render of the same .docx returns `04 = 0` on
  63 of 65.** Same code, same file, different renderer, verdict flips.
- **The tuple's "source" field is a hard-coded `0`** (`verify_google.py:4697`) - the check has never
  displayed a source-side number at all.
- **The separation is total in both directions: 0 of the 125 passing documents carry any textbox text,
  54 of 54 failing ones do.**

**`38_faux_bold_italic_synthesised` is unsatisfiable by construction.** Its bold is synthesised by drawing
the same line more than once: at y = 99.5 the headline `PROJECT REPORT - CIVIL` is drawn three times at
identical coordinates (fill navy, fill black, stroke navy), and `runs()` returns it **twice**. The .docx
correctly holds that line once. So 19 characters are reported missing forever, and the missing multiset is
character-for-character one copy of `projectreport-civil`. **No .docx and no renderer draws one visible line
twice - the fault is the source side counting draw operations instead of characters.**

**The white / invisible / off-page hypothesis is refuted:** 0 characters in text-render mode 3, 0 off the
page, 0 clipped-out spans. 16 documents do carry near-white text (647 characters) but none of it is among
the missing, because the .docx holds all of it.

**`601`'s two characters are a fiction of the extraction:** ZapfDingbats code 0x33 is a tick, PyMuPDF
reports the raw code, and the check hunts for the ASCII digit `3`. The engine did drop the two ticks (real),
but the characters the check names cannot be supplied by any renderer.

## 60_right_edge — the fix that works is face identity, and the obvious fix does not work

A third investigation measured the substitution from the font files and then tried three rules.

**The substitution is 4 % to 21 % narrower (median 14 %, k = 0.787 to 0.958), which is 1.5x to 4.8x the
check's entire tolerance (8 pt plus one word).** Because the face is narrower every line is shorter by the
same ratio, the page needs fewer lines, and **the column's widest line becomes a different line of text** -
so the edge lands 40-230 pt inside the source's. The correlation between line width and displacement is
**-0.94 to -0.99**, which is the signature of a substituted face: proportional, not a constant offset and
not last-line-only.

**Controlled experiment:** changing **only the font name** in the .docx and rendering it makes **26 of 28
flip to FAIL**, and the two that survive are exactly the two whose predicted deficit is under tolerance.

### The obvious fix does not work, and that is the useful part

**R1 - scale the expected edge by the document's own k - still fires on 24 of 28 and newly fires on 6 clean
documents.** The fault is a **re-break**, not a scale: a narrower face needs fewer lines, line membership
changes, and the residual `rg - k·rs` reaches +-90 pt even with perfect geometry. A ratio-threshold rule
fixes the substituted set but silently loses 4 real defects. "Scaled and more lines" fails for the same
reason - narrowing *reduces* the line count.

### The rule that holds

**Key on face identity, not a measured ratio.** If every face the .docx declares is one the renderer ships,
run the extent check unchanged; if any is not, the extent check **abstains in that renderer** and the
document is attributed to the substitution, with the real-defect question answered where the face exists.

**Validated: 0 real defects lost** (the 3 DejaVu real defects are all caught by the LibreOffice verdict),
the 12 non-DejaVu real defects still fire, and all 41 clean renders still pass. Cost: it would not catch a
real column bug inside a DejaVu document in Google's verdict - 3 documents of 28.

**The 16 non-DejaVu Google-only failures are untouched by this rule and remain open.** Their slack collapses
to about 4 pt on a table-cell label column holding a single digit.

### Two prior findings contradict each other on the direction

`...GOOGLE-HAS-NO-DEJAVU-0830` measured `302` going **+4.8 % wider** (Verdana, 33 to 35 lines);
`...IT-FIRES-UNDER-2323` measured **10-15 % narrower** (Arial). This investigation's controlled experiment
supports the narrowing arm for Arial. **Both can be true if Google substitutes per run**, which would make
any "scale by k" rule even less viable - and it is another reason face identity is the right key.

### Renderer split, reproduced twice

**41 fail only in Google, 15 fail in both.** The committed `gverify-lo` files and an independent
re-implementation of the check's own `columns()`/`edge()` agree on the same 15. The repo's
`GOOGLE-VS-LIBREOFFICE.md` figure of 18 is an older snapshot.

## 18_displacement, from the real Google renders: the check is right and the encoding is sufficient

This investigation did what the other two could not - it found that the corpus's Google Docs **already
exist in Drive**, exported all 102 to PDF, verified provenance by re-running `verify_google.py`, and
measured real coordinates on both sides: **12,012 matched run pairs in Google, 12,286 in LibreOffice,
434 pages.**

**The distribution settles it.**

| | Google | LibreOffice (same .docx) |
|---|---:|---:|
| \|dy\| median | **6.38 pt** | 0.59 pt |
| \|dy\| p90 | **69.01 pt** | 2.81 pt |
| \|dy\| p99 | **114.53 pt** | 17.76 pt |
| runs out by more than 4.5 pt | **60.5 %** | 3.0 % |

Page boxes are identical on both sides (595.3 x 841.9 against 596 x 842), so this is **not proportional
scaling**. Fitting `dy = a + b·y` gives a residual sd of **0.37 pt** on the 332 continuation pages - **a
constant translation, not scatter and not a ramp.**

**On the 332 continuation pages: `shift = 0.961 x gap - 0.58 pt`, r = 0.975, median ratio 0.96.** The
cleanest control is inside one file: `412_page_labels_roman` writes `w:before="1227"` (61.4 pt) on the first
paragraph of every page. **Page 0 reads +2.3 pt - honoured. Pages 1 to 4 read -58.8 pt - dropped.** Same
value, same file; the only difference is that the paragraph follows a page break. `416_many_tiny_pages`:
89.5 pt becomes -85.6 pt on 299 of 300 pages.

**On page 0 it is a staircase**: 81 pages carry a step over 3 pt (median 7.2, p75 11.5, max 148.8). The
boundary is always the table's first row; above it |dy| is under 1 pt. And **Google delivers 5-10 pt of
whatever exact line height the empty spacer requests, regardless of what was asked** - measured across five
documents asking 15.2 to 23.9 pt.

### Coverage

| cause | documents | exclusive |
|---|---:|---:|
| B - the spacer's exact line height is not honoured | **81** | 71 |
| A - `w:before` dropped after a page break | **16** | 6 |
| A and B in the same document | 10 | - |
| C - row growth under substitution (`hRule="atLeast"`, 99.5 % of 1,710) | 27 drift-dominant | 0 |
| residue only | 15 | 15 |

**Union of A and B: 87 of the 102.**

### "The format cannot express position" is refuted by measurement

None of the 102 has a single `w:framePr`; `w:pgMar` is 0 on all four sides; every body paragraph is
positioned purely by `w:before` plus `w:line ... exact`. **And LibreOffice places that flow at |dy| median
0.59 pt, p90 2.81 pt - well inside the check's own `clamp(0.35·size, 1.5, 4.5)`.** The encoding is
sufficient. Two of the three constructs it relies on are simply not honoured by Google, and constructs that
*are* honoured exist - `w:pgMar w:top` already took `bank-statement-5-pages` from 37/42 to 40/42 and its
pages 1-4 from -59.5 pt to -4.3 pt.

**The engine is wrong; the check is right in substance.**

### The honest caveat

**The 15 residue documents fail on 1.5 to 3 pt**, which is inside what a flowing .docx can hold across
renderers. There the **1.5 pt floor**, not the layout, is the binding constraint. And **20 of the 102 also
fail in LibreOffice** - those are a genuine engine-geometry class and are not explained here.

### Why this one could measure what the others could not

The other two sandboxes hit a wall: every Drive write path needs an `s3key` the platform upload tool would
stage. This one did not need to write - **the Google Docs already existed**, because the gverify cron has
been uploading them for weeks. That is worth remembering: the measurement was available all along, in the
place the pipeline had already put it.

## 45_char_accuracy — the same text-box rasterisation as 04, and the two classes are one fault

**`45_char_accuracy` compares the source PDF's text layer against the text layer of the PDF export of the
Google Doc - not against the .docx.** And Google rasterises every anchored DrawingML text box on import:
text inside `<wps:txbx><w:txbxContent>` is drawn as one small image per line and never enters the exported
PDF's text layer.

**The .docx is not at fault.** On all 34 documents that could be re-converted, the .docx carries **every**
source character with none substituted: source-minus-docx is **0 characters**, and `S~D = 100` on 33 of 34.
The committed `RANKING.csv` independently gives `chars_missing = 0 / text_recall 100.0` for all 37. And
**LibreOffice's render of the same .docx passes this same check on 36 of the 37.**

**Two exact equalities make it proof rather than correlation:**

1. The render's glyph multiset equals the .docx's **non-text-box** text, with only Google's own U+200B added.
2. The set of characters missing from the render is **character-for-character the set inside text boxes** -
   exact on 30 documents, 2,505 of 2,506 on a 31st, and a correlation of **0.996** between box share and
   deficit across 33.

**Character classes, 9,787 characters missing from the render across 33 documents:**

| class | characters | documents |
|---|---:|---:|
| text inside an anchored text box - rasterised, visible as images, absent from the text layer | 9,702 | 31 |
| underscore runs inside a 2-cell table - dropped from the render entirely | 84 | 1 |
| residual: one hyphen | 1 | 1 |
| extra direction: annotation text the .docx adds, plus U+200B | 225 | 23 |

**Ligature, soft hyphen, combining mark, bullet or symbol-font code, small-caps synthesis, U+FFFD,
hyphenation difference, genuinely wrong character: zero of each, measured.** Source-minus-docx is 0 across
all 34, so nothing was normalised or substituted before Google ever saw the file.

**Coverage: 34 of 37 by the text-box mechanism, 35 of 37 outright.**

**And the class is not what its name says.** `45_char_accuracy` is a whitespace-stripped NFKC **multiset**
ratio with a 3 % tolerance, order-blind - so it fires on MISSING characters too, which is why it co-fails
with `04_chars_missing` on **36 of these 37**. It is not a "wrong characters" check at all.

### The consolidation this forces

**`04_chars_missing` (54 of 65) and `45_char_accuracy` (34 of 37) are the same fault.** Both compare against
Google's exported text layer; both are defeated by the engine routing body text into an anchored text box;
both pass in LibreOffice on the identical file.

So the **120 pt gap cap** at `DocxWriter` - which flips a page into `ctx.positioned` and anchors everything
after it - is not a `04` finding. **It is the single largest engine defect found today: 88 document-failures
across two classes, from one threshold in one place.**

### A separate engine defect found in passing

**`table-with-rotated-header` has no HEAD .docx because `PdfToWord` throws on that source.** That is a crash
on a corpus document, not a check fault, and it needs its own investigation.

### 45_char_accuracy, second investigation: the mechanism is proven three ways

A second investigation worked from the documents and reached the same verdict with a sharper proof.

**The smoking gun is a count equality.** In **37 of 37** documents the number of `<w:drawing>` elements in
the .docx equals the number of raster images in Google's export, exactly. And the .docx contains **zero**
`word/media` parts and zero `a:blip` - so those bitmaps **cannot be the file's pictures**. Google created
one image per text box. In **37 of 37** documents the recall of the .docx's *non*-textbox characters in the
export's text layer is **100.0 %**.

**The text is legible in those bitmaps** - it read `STAFF HANDBOOK - REVISION 6 - APRIL 2026` straight out
of one 373x14 px image.

**The LibreOffice control:** 18 of 19 documents read **100.00** against the source where Google reads far
less - `331_pid_diagram` 100.00 against 18.25, `400_comic_page_speech_bubbles` 100.00 against 10.22,
`policy-2col-spanning-section-heading` 100.00 against 8.52, `69_two_col_legal_numbered_clauses` 100.00
against 32.46, `academic-paper-ieee-2col-abstract` 100.00 against 53.99. The committed
`benchmarks/gverify-lo/*.json` agree: **`45` fails on 1 of these 37 on the LibreOffice render (only `600`)
and on 0 of 37 for `04_chars_missing`.**

**A second render-side artefact:** Google's export inserts **136 U+200B ZERO WIDTH SPACE**, and the check's
`_glyphs()` does not strip them because `\s` does not match U+200B.

**Coverage: 36 of 37 are the check's comparison.** 1 (`600_reviewed_invoice_with_annotations`) is a genuine
file-side fault - and it is **extra** text, not wrong characters: the engine writes the PDF's annotation
`/Contents` into the body (92 characters the page's text layer does not contain), which is
`05_chars_extra`'s class, not this one.

**The fix both investigations converge on:** a character-accuracy check must read characters from
`word/document.xml`, not from the exported PDF's text layer. That is a check-side change, it needs no engine
work, and it would clear 34 to 36 of the 37.

**One honest discrepancy between the two:** the first counted 9,787 characters missing from the render
across 33 documents and called 34 of 37 explained; the second counted 11,811 across 37 and called 36 of 37
explained. The mechanisms and the verdict are identical; the difference is the set of Google Docs each
could locate (the second found all 37 among the 460 pre-existing Docs in Drive, the first found 33). The
larger sample is the better number.

## 59_shape_anchor CLOSED: 45 of 45 measured, and not one is a shape-anchor defect

The first investigation stopped at 11 documents and said 34 could not be rendered through Google. **That
blocker was not real** - the corpus's Google Docs were already in Drive (1,292 listed, 1,194 live, 432
distinct names, all 45 present), and every one was exported. Provenance: page count equals the source on
45 of 45, and all 45 reproduce the recorded `59_shape_anchor` failure.

**The class produces 1,003 convictions, and not one is a shape anchored somewhere else while its text
stayed:**

| conviction path | runs | whose question it is |
|---|---:|---|
| `same_box` - the render's box matches the source's on all four corners (<= 2 pt), text moved inside it | **878** | `18_displacement`'s |
| `lost` - text absent from the render | **104** | `04_chars_missing`'s |
| `no_render_box` + `_box_moved` | **14** | the check's own claim - **false in 14 of 14** |
| `box_differs` + `_box_moved` | 7 | genuine, Google's row-height quantisation |

**The proven split, one number per category:**

| category | documents |
|---|---:|
| **Engine** - a real shape-anchoring defect only this check can see | **0** |
| **Check** - proven false positive: `_box_moved` convicted on the same rectangle in the same place | **2** |
| **Duplicate charge of `18_displacement`** - the box did not move, the text did | **32** |
| **Duplicate charge of `04_chars_missing`** - no shape conviction at all, only lost runs | **11** |
| total | **45** |

**The two false positives, in full.** `_box_moved` found "a shape of the source box's width and height
elsewhere on the render" - and the shape it found is the source box, in the source box's own place:
`324_loan_amortisation_schedule`'s box `[0, 0, 595.28, 30.00]` matched `[-0.37, -0.38, 595.88, 30.37]`,
offset 0.37-0.60 pt, `_same_box` True. In both documents the **text** is what moved: the header line is
drawn at y = -12.29 pt, above the top of the page, while the band stayed.

**26 of the 32 also fail `18_displacement` outright.** The other 6 pass it, because 59 applies a flat 3.0 pt
tolerance where the house standard is `clamp(0.35·size, 1.5, 4.5)` pt - so it charges runs that 18's own
budget forgives. A second, narrower fault layered on the duplication.

### The fix, and why `_same_object` alone is not it

Each step was simulated on all 45 real renders:

1. **Call `_same_object` AND add the position term it still lacks.** `_box_moved` must be satisfied only by a
   box that is the same object *and* is **not** at the source box's own position. Without the position term,
   `_same_object` alone still fires on a coincident box. **Measured: clears 2 of 45.**
2. **Stop counting `lost` as an out.** A run whose text is absent is `04`'s conviction; today it increments
   `n_out` and can fail a page alone. **With (1): clears the 11 lost-only documents.**
3. **Stop convicting on the `same_box` path.** When the render's box agrees on all four corners, the check
   has already declared the shape unmoved - and then convicts on the text's offset inside it. Either drop
   the clause or adopt 18's tolerance. **With (1)+(2)+(3): 44 of 45 clear.** The last,
   `373_leave_application_form`, fails on 7 runs where the row band really did move 2.5 pt (row pitch 26 to
   27 pt), already reported by `18_displacement` and `23_line_pitch`.

**So `_same_object` is necessary and not sufficient.** It fixes the 2 documents where the check convicts on a
comparison between rectangles it should never have compared. The other 43 are not shape-anchor defects at
all.

### What this overturns

- "34 of 45 could not be rendered through Google" - **0 could not.**
- "27 structurally exposed" - all 27 are convicted or cleared with evidence.
- "`_box_moved` returns True whenever a box of the source's width and height exists anywhere" - **confirmed**,
  14 of 14 firings matched the source box itself.

### The number that matters for the whole exercise

**Nine classes have now been root-caused, and six of them are the same three faults wearing different
names:** the anchored text box (04, 45, 13, 44, 17), the page-top `w:before` drop (18), and a check reading
the renderer's paper or text layer instead of the document (25, 47, 59, 17). **The engine has exactly one
defect of its own that nobody else's class already covers: the 120 pt gap cap.**
