  already records: DocxWriter.java is 451 KB and the only working commit path,
  GITHUB_COMMIT_MULTIPLE_FILES, takes file contents inline. The change is 14 lines at
  `patches/carry-ceiling-span.patch`; apply with `git apply
  patches/carry-ceiling-span.patch` from the repository root and rebuild. It was built,
  converted over the whole corpus, diffed entry by entry and measured on all three documents it
  changes before being set aside, so applying it needs no new measurement - only the
  three-document check that it still applies and still gives 10 pages.
  recorded: 2026-11-17 19:00

- MEASURED, THIS RUN - the LAST spurious page of 041122 is a FOLIO WRITTEN AS A TABLE ROW, and
  it is why both form documents still read 99.02 with a page count of 10 against the source's 9.
  evidence: the table that holds the declaration form (24 rows) ends with a single-cell row whose
  whole text is "7". Rendered, that row is the only content of our page 8 (y 25.3-35.3, 1
  character), so pages 8-10 are compared against source pages 8-9 shifted by one: our page 8
  reads share@5 99.02 with text_recall 0.04, and the Annexure-2 page lands on page 11 of 11. The
  flow-line folio rule (the `b.y > 0.88 * pageHeightPt && isFolio(p)` anchor, which exists and
  names this document in its own comment) cannot fire because this folio is not a flow line - it
  is a row of the table. Until it is a position instead of a row, no amount of table arithmetic
  moves this document's number.
  recorded: 2026-11-17 19:00

- UNTESTED - A table's last row that is a folio in the page's bottom band should be anchored, not
  emitted as a row, exactly as a flow-line folio already is.
  evidence: the row is single-cell, its text matches isFolio, and its top is in the bottom band
  (0.88 x 842 = 741 pt; the page drew the folio at y 805.2). The flow path already does this and
  its comment measures the same document: anchoring the folio "lands at the y the page drew it
  at and costs no sheet". The table path needs the same, and the two are the same statement: a
  folio is a POSITION. Implementation is contained - detect it before the row loop, skip that
  row, set the last-row bookkeeping from row-1, and emit the text after `</w:tbl>` where the
  post-table carrier paragraph already goes. `anchor(sb, ctx, x, yTop, w, h, inner)` takes a
  hand-built paragraph and needs no Para/Box model. NOT built this run: the row loop carries
  per-row state (rowEdge may be baselines rather than edges on the whitespace pass, recut tables
  renumber rows, spans move c) and the slot ran out before it could be done and measured. It is
  the single change that should turn 041122 and Account_Opening_Form_Fillable_filled from 10
  pages to the source's 9, which is what moves the class.
  recorded: 2026-11-17 19:00


## content-missing-partly-replaced — the nine-page account-opening form class

- CONFIRMED - Every Run in a text box carried the raw `Tf` operand as its point size, not the
  size the glyph was drawn at, so a PDF that puts its scale in the TEXT MATRIX renders at 1 pt
  evidence: 16 Nov 2026 fixer, engine (clean) + patches/run-size-from-sizePt-not-Tf.patch.
  `041122-Account_Opening_Form` p1 content stream: `/TT0 1 Tf` with `6 0 0 6 71.3 493.7 Tm`,
  so PDFBox reports getFontSize()=1.000 and getFontSizeInPt()=6.000 (probe, 25 glyphs, page 1).
  The .docx carried 4088 runs ALL at `w:sz w:val="2"` (1 pt) - `halfPointsDown` floors
  sizePt*2 with a minimum of 2 - and the LibreOffice render was boxes with no words.
  Cause: `runsOf()` and the paragraph/ring paths built `new Run(..., first.size, ...)` from
  `Glyph.size` = getFontSize() (raw Tf), never `Glyph.sizePt` = getFontSizeInPt(). On every
  document where Tf carries the size the two are equal, which is why 211 synthetic documents
  never showed it; a form PDF is exactly the shape that separates them.
  Measured on the class's two real documents (soffice render, benchmarks/p2w.py position()):
  `041122` pages 1-6 mean share@5 82.1 -> 18.3 (p1 40.0->9.4, p3 92.9->10.6, p4 87.1->20.4,
  p5 97.0->15.5, p6 96.8->1.6); worst-page 98.65 -> 94.92. `Account_Opening_Form_Fillable_filled`
  worst-page 97.62 -> 90.31, mean over 9 pages 72.5. No page of `041122` got worse.
  NOT KEPT: the class does not pass and the full 213-document ratchet was not run in this slot,
  so the engine is reverted and the patch is saved at
  patches/run-size-from-sizePt-not-Tf.patch. NEXT WORK, in order:
  (1) run the ratchet on the patch across the corpus - it touches every run in every text box;
  (2) THE REMAINING BLOCKER IS A PAGE SPILL, and it is now the class's real cause. With the
  text at its true 6 pt, `041122` still emits 10 pages against the source's 9 and the fillable
  form 11: source page 7 overflows, everything after it shifts one page, and pages 7-9 read
  74-95 %@5 purely because page i is compared against page i. Fix the spill and the same
  documents should fall from ~90 %@5 to the pages 1-6 range. Do not re-derive the size bug.

- CONFIRMED - The per-cell paragraph matrix (`pieces`) was indexed in the UNTRIMMED column
  space after the empty-column trim, so the multi-line cell path read another column's lines.
  evidence: 17 Nov 2026 fixer. `PdfToWord.buildTables` (~:8686) remaps cells/faces/firstX/
  firstY/colours through `keep` and left `pieces` alone, while the consumer at :8800 reads
  `pieces.get(rr).get(cc)` with `cc` in the trimmed space. 041122 p7 grid is 24x4 with
  keep=[1,2,3]: the heading is original column 2 = trimmed cell 1, but pieces.get(1).get(1) is
  original column 1 (empty), so parasOfLines returned 0, the cell fell back to the welded
  string, and the SIX paragraphs were written into the empty cell to their right - which is
  why the heading appeared twice on that page. Fixed by trimming `pieces` with everything
  else. Predicts every table that drops a column.

- CONFIRMED - The point size is `scalingFactorY` of PDFBox's TextPosition text matrix, and it
  is a SIZE, not a multiplier on the Tf operand. evidence: 17 Nov 2026, probe over three
  documents: 041122 fontSize=1.000 scaleY=10.000 inPt=10.000; 48_form 12/12/12;
  01_stamp fontSize=8.500 scaleY=8.500 inPt=8.000. Multiplying the two squared every ordinary
  page and regressed 192 of 213 documents (12 x 12 = 144 pt) - that wrong version was measured
  and thrown away, not reasoned about. Taking scaleY itself keeps the 8.5 that inPt rounds to
  8, and is 13.0 on text rotated 90 degrees. Full 213-document ratchet WITH the fix:
  208 unchanged, 2 improved (411_nested_xobject_transforms 31.05 -> 0.00;
  041122 98.65 -> 97.62, median displacement 477.6 -> 138.24 pt), 1 regression
  (39_small_caps_letter_spacing 0.72 -> 3.78) and one nil change (05_round_company_seal
  0.19 -> 0.20). This supersedes the reverted patches/run-size-from-sizePt-not-Tf.patch,
  which used the ROUNDED inPt.

- CONFIRMED - `parasOfLines` records each line's own x, `addRecutRow` (:8380) turns it into
  `indentPt`, and the pieces path added the paragraphs WITHOUT it, so indentPt stayed NaN and
  the writer applied one inset - the cell's first-line x - to every paragraph in the cell.
  evidence: 17 Nov 2026. 041122 p7 row 1 wrote all six heading lines at `w:ind 9452`
  (472.6 pt) inside a 10636-dxa cell: 59 pt of usable width, so "Income-tax Rules, 1962"
  (drawn at x 253.7) wrapped inside a 59 pt column. After the fix the six carry
  9452/4255/4705/3830/107/2079 and the row renders at its declared height.

- CONFIRMED (measured, engine change still owed) - the 041122 page spill is a WRAP, not a
  paragraph property, and the wrap is caused by the reference renderer substituting a
  different font. evidence: 17 Nov fixer. Rendered bottom rules of table 17's 24 rows
  against their declared `w:trHeight`, in twips/20: r1 23.2/23.15, r2 93.1/84.1 (+9.0),
  r3-r15 17.3-17.6 each = declared, r16 40.9/40.95, r17 17.3/17.3, r18 17.3/17.25,
  r19 37.6/29.15 (+8.5), r20 61.7/41.0 (+20.7), r21 41.0/41.0, r22 40.8/40.8,
  r23 340.4/231.5 (+108.9) -> spills to our page 9, r24 41.6/41.35. THE ROWS THAT GROW GROW
  BY WHOLE LINES: r23 carries 20 source lines and rendered 26, and its own `w:before` values
  are 0-4 pt each (sum 24.1 pt) with `w:line` exact 240 tw = 12 pt - the source's own pitch.
  So neither `w:before`, nor `w:line exact`, nor `w:cantSplit` is what grows it; the extra
  lines are the growth. The cause of the extra lines: the .docx names Effra (the source's
  font, correctly), the renderer has no Effra, and substitutes Noto Sans - 'Verification'
  at 10 pt measures 52.40 pt in the source's Effra-Bold and 61.24 pt in the substitute
  (+16.9 %). The cell leaves the source's longest line 2.9 pt of slack (line ends x 568.8,
  cell edge 571.9 = 0.5 %), so every full-width line wraps its tail. Ruled out by
  measurement: the sizePt bug and the `pieces` index (both fixed; r1's six heading lines
  carry 9452/4255/4705/3830/107/2079 and render at declared height), `w:before` (24 pt, not
  109), `w:line` (12 pt = source pitch), `w:cantSplit` (only moves an already-taller row).
  Also measured: our page 7 is NOT table 17 - it holds page 6's page furniture (the C7EAFB
  heading bar, the footer rule at y 738.2 and the page number at y -7.5) whose anchor
  paragraphs were pushed off page 6; table 17 starts on our page 8.

- CONFIRMED (environment, and it changes what this class's numbers mean) - installing a
  metric clone of the source's own embedded font takes 041122's table from spill to nearly
  exact. evidence: 17 Nov fixer. Built Effra-Regular/Bold from Liberation Sans with the
  advances read out of the PDF's own `/Widths` arrays (FirstChar 32, w/1000 em; space 0.181
  em against Liberation's 0.278), installed to ~/.fonts, re-rendered into an empty dir:
  r2 93.1 -> 84.1 (= declared), r23 340.4 -> 256.4, page 2 of the table no longer starts a
  new page. Ruled out: kerning (stripping GPOS/kern changed nothing), font *shape* (only the
  advances matter for line breaking). NOT yet enough on its own - still 12 pages, because
  the residual is the engine's own line box: r23's 19-20 paragraphs are emitted at
  `w:line` 240 tw (12.0 pt) while the row the engine itself declares is 4630 tw (231.5 pt)
  for 20 lines at the source's 11.6 pt pitch - the engine's row height and the engine's
  line height disagree by 0.4 pt a line, so a 20-line row overflows by ~8 pt + `w:before`
  before any font is involved. NEXT: make the cell-line box carry the source's measured
  pitch in twips (232, not 240) and re-measure r23 against 231.5.

- CONFIRMED and FIXED (17 Nov 14:39 fixer, DocxWriter.table) - A PAGE'S OWN FOLIO IS NOT A
  ROW OF THE TABLE THE PAGE'S RULES BOUND. 041122 page 7 draws a rule above its folio and a
  frame round the sheet, so the ruled pass hands the folio back as the table's LAST ROW
  (row 23 of 24, cells 363/10636/456 tw, trHeight 827 tw, only text "7"); the page's content
  already ends at y=800.4 of 842, so the row cannot fit, the renderer breaks the sheet and
  the folio costs a whole page (ours 11 against the source's 9). The writer now detects a
  trailing row that is nothing but a folio whose baseline is in the page's bottom band
  (>0.88 page height), leaves it out of the table's height and emits it as an anchored line
  at its own x/y - the treatment the FLOW path already gives a folio. Measured: 041122 11
  pages -> 10, doc share5 97.62 -> 86.25, worst page 7 -> 9. No-regression proof: all 213
  documents re-converted with the patched engine, compared entry by entry inside the .docx -
  212 are byte-identical in every zip entry, so their renders and scores cannot have moved;
  only 041122 differs. Ruled out by measurement: that the table's rows are individually too
  tall (the content rows land on the page's own edges), and that the folio is outside the
  table (it IS a real drawn cell - the fix is about where it is drawn, not whether it is a
  cell).

- OPEN (measured, NOT fixed) - THE INSTRUCTION PAGE'S LAST 17 LINES. After the folio fix,
  our p8 (the instruction page) stops at y=683.6 with 158 pt of the sheet unused, and the
  tail of the table (17 lines, ending at the source's own folio "8") goes to p9. Mechanism,
  measured by rewriting only the .docx and re-rendering: `<w:cantSplit/>` is written on
  EVERY row, and it is a promise the engine cannot keep - a row that does not fit the space
  left on its page takes the whole row to the next sheet instead of breaking where the page
  broke it. With cantSplit stripped from the same .docx (86 occurrences) the page takes 166
  lines instead of 154 and the spill falls from 17 lines to 5: so cantSplit is 12 of the 17
  and the remaining 5 are row height. NOT FIXED because the blast radius is 26 of 213
  documents (every document with a table row written taller than 60 pt - 55_sidebar_box,
  61_two_col_abstract_spanning, 64_newspaper, product-catalogue-code-left-price-right, ...)
  and 26 full position measurements is hours of instrument time in one slot; a change that
  cannot be measured must not be kept. NEXT: a NARROW rule - write cantSplit only when the
  row's own top edge plus its written height still lands inside the page
  (rowTopPagePt + rowHeightTw/pt <= pageHeight), which is the promise cantSplit actually
  makes and which can only fire on rows that provably overflow. Count how many documents it
  fires on before measuring them.

- RULED OUT, THIS RUN (measured) - THE NARROW cantSplit RULE DOES NOT CLOSE 041122, AND NO
  HEIGHT-BASED VERSION OF IT CAN. The rule was built exactly as specified - w:cantSplit
  written only when the row's own top edge plus its height lands inside the page - and
  applied twice. First as specified, on the DECLARED w:trHeight: it fired on 1 of 213
  documents (itr-computation-with-slab-table, 68.12 -> 68.12) and NOT on 041122, because
  every one of 041122's 86 rows fits an 842 pt sheet by its declared height. Then on the
  height the renderer actually lays out - max(declared, the w:before + w:line actually
  emitted in the row's cells), which is the only height hRule="atLeast" cannot exceed: it
  fired on 4 of 213 and still does not close the page. All four measured, no movement:
  041122 10/10 pages identical line for line, Account_Opening_Form_Fillable_filled 10/10
  identical, itr-computation 68.12 -> 68.12, 64_newspaper 9.11 -> 9.11.
  THE MEASURED REASON, and it is the whole point: the breaking row is the one carrying
  "Government Department establishing identity and address of such person". Its top edge is
  689.0, it declares 2220 tw (111 pt) and it emits 2558 tw (128 pt) of line boxes, so
  689 + 128 = 817 pt reads as fitting on an 842 pt sheet. It renders ~170 pt (p9's text runs
  y 9.8 -> 163.8) because the RENDERER WRAPS its cell text into ~15 lines where the writer
  emitted 11. The under-charge is in the WRAP, not in the height arithmetic, so any rule
  keyed on a height the writer can compute will call this row safe. Confirmed on the
  document, not inferred: with cantSplit dropped from that one row the render is unchanged,
  because the rule keeps it (817 <= 842) - the row that DOES lose cantSplit is a 66 pt row at
  top 805, which changes nothing visible.
  CONSEQUENCE FOR THE NEXT RUN: stop working the cantSplit angle. The last extra page is a
  cell whose text wraps into more lines than the writer charged, and that is the same
  under-charge as the class it sits in (content-missing-partly-replaced). Charge the cell
  its real line count and the row's height becomes truthful, at which point a cantSplit rule
  keyed on it fires by itself and the page closes.

- KEPT, THIS RUN (measured neutral on all 213) - cantSplit IS NOW WRITTEN ONLY WHERE IT CAN
  BE KEPT. DocxWriter.table() emits the row's cells first, takes
  laidOutTw = max(rowHeightTw, flowTwOf(row)), and writes w:cantSplit only when
  rowTopPagePt + laidOutTw <= pageHeight. 209 of 213 .docx are byte-identical in every zip
  entry; the 4 that differ are the 4 measured above, and none of them moves a number. It is
  kept because it removes a promise the engine cannot keep wherever that is provable, and it
  costs nothing measurable - but it is NOT the fix for 041122 and must not be counted as one.
  IT IS CARRIED AS A PATCH, NOT IN THE ENGINE, and that is a commit-path fact, not a
  judgement: `app/src/main/java/com/kavopdf/app/engine/DocxWriter.java` is 458 KB, git push
  is 403 for everyone, and the only working commit path is the GitHub MCP tool
  GITHUB_COMMIT_MULTIPLE_FILES, which takes file contents inline - a 458 KB file is not a
  payload any run can send. The change is 38 lines and lives at
  `patches/cantsplit-only-where-keepable.patch`; it was verified to apply cleanly to this
  tree (`git apply --check`), built, converted over the whole corpus and measured before
  being set aside. Apply with `git apply patches/cantsplit-only-where-keepable.patch` from
  the repository root and rebuild, exactly as patches/README.md says. Because it moves no
  number, not shipping it costs the project nothing; because the next step below needs it
  (a row charged its true height only closes the page if a cantSplit rule is there to drop
  it), a run that takes that step should apply the patch first.

- MEASURED, THIS RUN - WHERE THE UNDER-CHARGE ACTUALLY IS, IN NUMBERS. The breaking row of
  041122 (docx row 76, the one carrying "Government Department establishing identity and
  address of such person") is ONE cell, 11000 tw (550 pt) wide, holding NINE paragraphs at
  w:line="240" (12 pt) and w:sz="20" (10 pt), 828 characters in total. The writer charges it
  9 x 240 = 2160 tw plus the rule, which is the 2220 tw (111 pt) it declares. The render
  spends ~13 lines on that text (p9's text runs y 9.8 -> 163.8 in twelve baselines, 154 pt
  at 12 pt), i.e. ~156 pt. SO THE ROW IS NOT UNDER-MEASURED BY ARITHMETIC - IT IS
  UNDER-MEASURED BY WRAPPING: the writer emitted one paragraph per source line, and four of
  those paragraphs WRAP INTO TWO LINES in the render, because the source face fits 828
  characters into 550 pt and our DejaVu does not. Nine paragraphs, thirteen lines.
  THE FIX THIS POINTS AT: charge each paragraph the number of lines it will wrap into, using
  the width OUR font gives its text against the cell's own width (ceil(textWidth / cellWidth)),
  instead of assuming one line per source line. That is a real measurement the writer can
  make - it already measures text widths for column widening - and it would put this row at
  ~156 pt, after which top 689 + 156 = 845 > 842 and the cantSplit rule carried in
  patches/cantsplit-only-where-keepable.patch fires by itself and the page closes. It also
  explains, in one mechanism, why this document has resisted eleven attempts: every attempt
  keyed on a height the writer already computes agrees with the writer.

- RULED OUT, THIS RUN (measured, and it made things WORSE) - DROPPING cantSplit ON A
  WRAP-AWARE HEIGHT. The wrap estimate above was built for real: a Helvetica advance-width
  helper (PDType1Font.HELVETICA / HELVETICA_BOLD, the standard-14 metrics PDFBox already
  ships, within a few per cent of the DejaVu Sans these documents are set in), each cell's
  text split on its own paragraph breaks, lines = ceil(textWidth / (spanTw - insetTw)), the
  row charged lines x rowLineTw, and the cantSplit rule keyed on the larger of that, the
  declared height and the emitted line boxes. It compiles and it runs. On 041122 it takes
  the document from 10 pages to ELEVEN: p7 falls from 91 lines to 90, a one-line p8 appears
  (maxy 35.3), and the instruction page is untouched at 683.6 with the same 17 lines spilling
  to p10. So a row that the earlier rule kept whole now breaks, and the break itself costs a
  page. THAT IS THE FINDING, and it redirects the fix: cantSplit is NOT the lever. With
  hRule="atLeast" a split row leaves a fragment the renderer charges again, so removing the
  promise can cost more than it saves. The page has to be closed by charging the row its real
  height in w:trHeight - so the renderer lays the row out at 156 pt and breaks it ITSELF at
  the foot of the sheet - not by removing cantSplit and hoping it breaks well. The engine was
  reverted to HEAD after this measurement; nothing from this experiment is in the tree.

- RULED OUT, THIS RUN (measured) - CHARGING THE ROW ITS WRAPPED HEIGHT CASCADES. Built the
  same way as the previous entry (Helvetica standard-14 advances, per paragraph
  ceil(textWidth / (spanTw - insetTw)), the row charged max(declared, wrapped) x rowLineTw)
  but written into w:trHeight itself - hRule is "atLeast", so the floor is what the renderer
  will not go below - and cantSplit left alone. It works on the row it was aimed at: the
  instruction page's content now runs to 711.5 instead of 683.6, so the breaking row really
  did grow. The document is still ELEVEN pages, and the reason is the cascade: p7 falls from
  91 lines to 90 and a one-line p8 appears, because rows that used to fit the page are now
  charged more and one of them crosses. Charging every under-charged row at once is not a
  one-row fix - it re-lays out every table in the document and the page count is decided by
  the whole sequence, not by the row that overflows. WHAT THAT MEANS FOR THE NEXT RUN: the
  wrap charge is the right mechanism (it is the only one that explains 111 pt charged against
  156 pt laid out), but it cannot be landed blind on one document. Do the corpus diff FIRST -
  re-convert all 213 and count how many .docx change - because this change touches every
  ruled table, not four of them, and the ratchet has to be paid for over the whole corpus in
  a slot that can afford it. The engine was reverted to HEAD after this measurement.

- RULED OUT, THIS RUN (measured at corpus scale) - THE WRAP CHARGE RE-LAYS OUT 47 OF 213 AND
  REGRESSES EVERY DOCUMENT IT TOUCHES. The previous run asked for the corpus diff before
  anything else, and this is it. Built the charge exactly as the handoff specified: a Helvetica
  advance-width helper (PDType1Font.HELVETICA / HELVETICA_BOLD), each cell's text split on its
  own paragraph breaks, lines = ceil(textWidth / (spanTw - insetTw)), the row charged
  max(declared rowHeightTw, lines x rowLineTw) written into w:trHeight, which is hRule="atLeast"
  on the real-table path so the charge is a floor; the flow budget (writtenRowsTw) was made to
  follow it, because a row the renderer lays out taller is taller for the flow after it too.
  Re-converted all 213 with the unmodified HEAD engine and with the charge, and diffed the .docx
  entry by entry:
    * 47 of 213 documents change (22 %), all of them in word/document.xml only; 350 rows grow,
      65 shrink (a table that outgrows its page is squeezed), the largest single row +161 pt
      (360_restaurant_menu).
    * MEASURED, not inferred: the 47 changed documents are the only ones that can move, so they
      were measured against themselves on both engines (46 of 47; 01_stamp_rotated_15deg_upright
      fails to render on both, soffice "no render"). Result: 0 improved, 40 WORSE, 6 flat.
      Mean share@5px loss 10.66 % -> 32.63 % (lower is better). The target document,
      041122-Account_Opening_Form, does not move at all (99.02 both, 11 pages both).
  WHY IT IS WORSE, and this is the part the next run needs: the charge measures a cell's text
  against its w:tblGrid column, and on several documents the grid does not describe the layout.
  41_coloured_headings_white_bg is written as SIX grid columns (8876,570,8876,570,8876,570 tw =
  1416 pt of grid on a 595 pt page) holding TWO cells, so the price column reads 28.5 pt wide
  for the 30.6 pt text "340.00" and every row of a correct price list is charged two lines: the
  page doubles its leading (trHeight 360 -> 500 on every row), which is visible in the render
  and moves share@5px 0.0 -> 70.8. Two structural guards were built and measured and neither
  fires here, because the table's own bounds (t.right - t.left) are wrong in the same way as the
  grid, and spanC exists so the "fewer cells than columns" test passes: a grid this corrupt
  cannot be caught by comparing it with itself. WHAT THAT MEANS: the width the charge needs is
  not the grid, it is the width the RENDERER gives the cell (tcW after spans, or the page's own
  cell rectangle), and until that is the number the charge reads, this mechanism cannot be
  measured, only regressed. The engine was reverted to HEAD after this measurement; nothing from
  it is in the tree. Full numbers in FINDINGS/wrap-charge-corpus-diff.md.

- RULED OUT, THIS RUN (second measurement) - THE SAME CHARGE WITH AN 8 % METRIC ALLOWANCE STILL
  REGRESSES. The first build charged every cell whose text was wider than its column, and
  Helvetica's advances are only within a few per cent of DejaVu Sans, so a cell sitting AT its
  column width - a price column, an amount column, the commonest cell in this corpus - was
  charged a second line by the estimate's own error. 41_coloured_headings_white_bg's price cell
  is 28.5 pt wide for 30.6 pt of text: a 7 % overshoot, and every row of a correct price list
  doubled (360 -> 500 tw). So the charge was rebuilt with the error budget named: avail x 1.08,
  with the grid guards kept (columns must add to the table's width; no row may have fewer cells
  than the grid has columns unless a span table says which cell covers which). Measured:
    * 32 of 213 documents change, down from 47 - the allowance removed the false positives, and
      41_coloured_headings_white_bg is back at 360 tw rows, exactly as the page drew it.
    * 041122 now moves: 6 rows, largest +12.2 pt (the earlier build charged it nothing).
    * and it is still worse: of the 32 changed documents, 0 improve, 28 get worse, 4 are flat.
      Mean share@5px loss 13.85 % -> 30.36 %. Worst: 80_gstin_pan_cin_ifsc_table 2.01 -> 61.11,
      77_arabic_rtl_document 17.14 -> 58.55, 72_bank_statement_no_rules_right_amounts 0.00 ->
      41.02.
  WHAT THAT MEANS, and it is the finding this run exists to deliver: the charge cannot be landed
  as a CHARGE. A table whose rows are already the page's pitch is correct, and every extra twip
  of trHeight moves its rows off the page's own lines - so a rule that raises rows wherever the
  estimate says "these words are wider than this column" loses more than it gains, because the
  estimate fires on rows the renderer was already laying out correctly. The rule that can only
  win is the DIFFERENTIAL one: charge a row only for the lines it will wrap MORE than the page
  itself drew in that cell (the page's drawn line count is already in the model - the cell's own
  boxes, or cellParasTw / rowLineTw), and charge nothing when the two agree. That is the next
  run's first experiment, and both documents it must calibrate against are named in
  FINDINGS/wrap-charge-corpus-diff.md. The engine was reverted to HEAD; nothing from either
  build is in the tree.

- RULED OUT, THIS RUN (third measurement) - THE DIFFERENTIAL CHARGE TOO. The rule was rebuilt to
  charge a row only for the lines it will wrap MORE than the page's own row height affords
  (pageLines = round(rowHeightTw / rowLineTw); charge only when wrapLinesHelv > pageLines), with
  the 8 % metric allowance kept. It calibrates better than either earlier build: 24 of 213
  documents change (11 %, down from 47 and 32), 41_coloured_headings_white_bg is untouched at its
  page pitch (0 of 12 rows move), and 041122-Account_Opening_Form finally moves the row it was
  aimed at - 7 rows, largest +24.9 pt, which is the 156-vs-111 pt gap the earlier run measured.
  And the verdict is the same: of the 23 changed documents measured, 0 improve, 18 get worse, 5
  are flat; mean share@5px loss 16.08 % -> 31.52 %. Worst: 80_gstin_pan_cin_ifsc_table
  2.01 -> 61.11, 77_arabic_rtl_document 17.14 -> 62.35, 76_devanagari_table 19.54 -> 57.90,
  64_newspaper_uneven_columns_ad_boxes 9.11 -> 39.50.
  WHAT THAT MEANS. Three builds - flat, allowed, differential - and 124 document-measurements all
  say the same thing: on this corpus, raising a ruled table's rows loses. The documents that
  change are dominated by tables whose rows the page drew at its own pitch, and the flow after
  the table is then wrong by exactly what was added, which the instrument charges at 5 px. The
  mechanism explains 041122 (111 pt charged against 156 laid out) and is still not a lever that
  can be pulled corpus-wide: 041122's own page count does not change even when its row grows by
  25 pt, because the page's break is decided by the whole sequence. WHAT WOULD BE DIFFERENT: a
  charge that is applied to a table AND to the flow after it with the same number, so the page
  is closed rather than lengthened - i.e. re-flow the page's remaining bands after the charge
  instead of letting them overflow. That is a page-layout change, not a row-height change, and
  it is bigger than a fixer slot. The engine was reverted to HEAD; nothing from any of the three
  builds is in the tree.


## 18 Nov 17:00 — three mechanisms tried on `itr-computation-with-slab-table` (50.80), all refuted

The handoff carried one hypothesis and this run added two of its own. Each was built, screened, and
reverted; the engine is at `1ba86d7` and the document re-screens at 50.80.

**H1 — "the residual is the f=0.974 squeeze; anchor the footer and the squeeze goes away."**
REFUTED, twice. (a) There is nothing to anchor: the running footer is a ROW of table 3, not a flow
paragraph, so `afterTablePt` never sees it and `zeroGap=0` on the trace. An anchor implementation
written into that branch is dead code on this document. (b) Releasing the squeeze directly — capping
a clipped table's charge at the page budget, needTw 17278 -> 16836, f 0.974 -> 0.994 — made the
document WORSE, 50.80 -> 70.85. LESS squeeze is worse, so the squeeze is compensating for a page
that really is too tall; it is a symptom, not the defect.

**H2 — "the cell baseline: `cellBeforeTw`'s fallback treats `rowLineTw` as the row's pitch."**
MECHANISM REAL, SCORE DOES NOT MOVE. `rowLineTw` is the cell's LINE, capped at 200 twips; on this
document it is 190 twips inside a 269 twip row, so every cell is written 3.2-5.2 pt above where the
page draws it. Using the row's pitch as the foot where the row is >1.3x its own line, and only in
the fallback (never for a cell placed from a measured baseline): screened on 4 table documents, 4
measured, 0 better, 0 worse; measured directly on the target, 50.80 -> 51.18 (share1 92.18 -> 69.91
and invent5 62.48 -> 40.41 improve sharply, median 4.80 -> 5.28 and share5 slightly worse). WHAT
WOULD BE DIFFERENT: this is a 3-5 pt move on a page whose remaining error is 100+ pt at the foot —
it needs the header block and the row order fixed at the same time to show up in share5, and it
touches every table on the corpus, so it needs a corpus pass, not a screen.

**H3 — "the footer row's position in the row order is the defect."** NOT YET TESTED, and it is the
cheapest of the three: the page draws the footer last (811.4) while the engine emits it between the
816.4 and 834.8 rows. See FINDINGS/itr-slab-the-squeeze-is-not-the-defect-1645.md for the rendered
line-by-line table that shows all three defects side by side.

## 32_stroke_lines - re-opened 21 Nov, and why the 18 attempts did not settle it

The class was exhausted on 20 Nov with "18 attempts, all reverted; 36 of 39 rules are in table rows and
never reach the pBdr path". **That reason is a finding about ONE approach, not about the class.**

It says the rules are inside table rows. The 18 attempts tried to give them to the PARAGRAPH
(`w:pBdr`), which a rule inside a table cell can never reach - so of course all 18 reverted. **The
untried approach is the one the finding points at: `w:tcBorders`, the cell's own border.**

Until that is tried and measured, the class is open. It is 145 documents - the largest single lever in
the tool - and leaving it parked is the reason the corpus moves one document at a time.

What would settle it: build one document whose rules are in a table row, give the row's cells a
`w:tcBorders` bottom border of the measured width and colour, and look at it in Google. If the rules
appear, the class is winnable and the 18 attempts were aimed at the wrong construct. If they do not, the
class is genuinely unwinnable with what the engine can emit and the exhaust reason becomes true.
