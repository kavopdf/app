# Two patches, written offline, not yet built

The agent wrote these on 19 Nov with no `java` in its sandbox: it could read the engine and the
corpus but could not compile, convert or measure. **Neither patch has been built, screened or
ratcheted.** They are starting points with a proved diagnosis behind them, not verified fixes.

    /scratch/output/PATCH-411-ctm-size.patch           engine: PdfToWord.java
    /scratch/output/PATCH-t13-table-row-per-line.patch  engine: TxtWriter.java
    tools/p2w-bench/SPEC-justified-lines.md             spec only, no code - see section 3

Both apply cleanly to `8e8fdd2`.

---

## 1. PATCH-411-ctm-size — the fix three runs found and lost

**What it fixes.** `411_nested_xobject_transforms` scores 31.05. PDFBox hands back a glyph's
**size** in text space and its **advance** in device space: `getFontSize()` and
`getFontSizeInPt()` are the `Tf` operand scaled by the text matrix and never by the CTM. The page
sets 10 pt inside `q 1.6 0 0 1.6 cm` and draws 16 pt; the model held 10 pt from a correct origin,
so the ink compressed toward the origin and the error grew along the line to 97.92 pt at the far
end. 1731 of 5574 ink pixels displaced.

**The change.** `GlyphCollector.ctmScale()` reads
`getGraphicsState().getCurrentTransformationMatrix()` and returns the geometric mean of the
matrix's two column lengths. `processTextPosition` multiplies both `g.sizePt` and `g.size` by it
when it differs from 1 by more than 1e-4.

**Why that formula and not another.** `size` already carries the text matrix. Multiplying by
|Trm| as well double-counts it and sends `041122-Account_Opening_Form` from 98.65 to **97.81** —
a regression the 00:58 run recorded and could not explain. That single measurement separates the
right formula from a plausible one, and it is in the 22:51 run's own report.

**What is already measured about its reach.** A sweep of all 213 corpus PDFs finds exactly one
that draws text under a CTM whose scale differs from 1. The other 212 cannot enter the branch.
The advance is not scaled — `getWidthDirAdj()` already includes the CTM.

**What the fixer must do.** Build it, `screen.py --docs 411_nested_xobject_transforms`, then a
full corpus pass, then both ratchets. Expected: 411 → 0.00, 212 unchanged, `.txt` byte-identical
(the 22:51 run measured that on this exact change and got an empty diff and the same md5).

---

## 2. PATCH-t13-table-row-per-line — the largest single lever in the .txt

**What it fixes.** `t13_amount_columns` holds **30 of the 64 failing .txt documents, and 24 of
those fail on nothing else.** The cause is not the check.

`TxtWriter.appendTable()` ended **every cell** with a newline, so a nine-column invoice row came
out as nine lines, each starting further right than the last. The page draws one row. Option A for
this format is "rows on one line, columns aligned by spaces", and the writer was emitting a shape
no reader can use and no column check can pass.

Measured on `gst-invoice-3line-items`, whose source column at end-column 133 holds
`32,745.00 / 7,522.50 / 13,806.00`: in the `.txt` they ended at **134 / 133 / 134**, because each
amount sat alone on its own line and an amount's end column was simply its own length.

**The change.** One page row is one line. A cell whose text wrapped (`"a\nb"`) contributes part 0
to line 0 and part 1 to line 1, so a row of wrapped cells becomes a block of lines that share
their columns — which is what the page drew. A cell that cannot fit behind the text already on the
line gets one space rather than overwriting it. Trailing spaces are trimmed, because `t13` reads
the amount a line **ends** with and a line ending in padding hides its own last column.

**What the fixer must do — and this one is not optional.**

1. Build it.
2. `screen.py --docs` over a table-heavy sample, not one document. This changes the shape of every
   table in the corpus.
3. **Check `t02_position` and `t08_line_order` as carefully as `t13`.** They are not obviously safe:
   `t02` derives a ruler from leading spaces, and a row that now carries nine cells on one line has
   a different leading-space profile than nine lines each carrying one. The 15 documents under
   `t02` and the 10 under `t08` may move either way.
4. Only then a full `.txt` pass and the ratchet.

If `t02` or `t08` gets worse on net, the fix is still right and the check is measuring the old
shape — but that has to be established by measurement, not assumed. Do not ship this on the
strength of `t13` alone.

---

## A second defect in the check, found while proving the first

`verify_txt.compare()` keys the `.txt`'s amounts by **token** and keeps only the first end
position:

    txt_ends.setdefault(ln[span[0]:span[1]], []).append(span[1])
    got = txt_ends.get(tok)
    ends.append(got[0])          # always the FIRST occurrence

On an invoice the CGST and SGST columns often hold the same values. Here `2,497.50`, `1,053.00`,
`12,825.00`, `9,652.50` and `26,601.75` each occur twice, ending at 109 and at 120. Both source
columns look up the same list and both take `got[0]`, so the SGST column is judged against the
CGST position and passes for the wrong reason.

**Fixing it will make more documents fail, not fewer.** Do it deliberately, in its own commit,
with the baseline re-stamped — and **after** the writer patch, so it is possible to tell which of
the two moved a number.

---

## 21 Nov 19:26 — the rule carrier for `32_stroke_lines`, measured in Google and ready to apply

`tools/p2w-bench/patches/rule-carrier-tblppr-2008.patch` — 186 lines, one file, `DocxWriter.java`.

`394_map_with_legend` is **41/42 in Google today** (committed record, engine `7112d76`) and **42/42 with
this patch**, measured through Drive in this run. LibreOffice reads 42/42 both ways. The evidence, the two
numbers the probe did not know (`w:tblCellMar` zeroed, and a 4.0 pt predicate to match `RULE_THIN`), and
what is still unmeasured are in `FINDINGS/32_stroke_lines-RULE-CARRIER-LANDED-2008.md`.

**It is a patch and not a commit because the corpus measurement does not fit a slot.** `regress.py --check`
refuses an engine change the tables were not measured on, and measuring 213 documents costs ~21 s of JVM
per document to convert alone — measured here, not estimated. To land it:

    git apply tools/p2w-bench/patches/rule-carrier-tblppr-2008.patch
    # rebuild tools/engine-verify, then:
    python3 benchmarks/gate.py --budget 250      # repeat until it reports complete
    python3 tools/p2w-bench/regress.py --check   # must pass
    git commit                                   # the hook runs regress.py itself

The patch rebuilds to a `.docx` whose `word/document.xml` is byte-identical to the one Google scored 42/42.
