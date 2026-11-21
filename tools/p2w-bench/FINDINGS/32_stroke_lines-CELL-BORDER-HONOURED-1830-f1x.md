# A rule CAN be a cell border: Google honours `w:tcBorders`, and it drops the floating drawing

**21 Nov 2026 · relay/fixer slot 18:19 · engine `462353f` · five probe `.docx`, one export each, through Google Docs**

## Why this was measured

The dominant Google failure shape on 21 Nov is not one check, it is three that always travel together:

    docs  checks
      15  05_chars_extra, 18_displacement, 32_stroke_lines
      15  05_chars_extra, 32_stroke_lines
       8  05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor
       5  05_chars_extra, 18_displacement, 32_stroke_lines, 59_shape_anchor, 60_text_column_right_edge
       4  05_chars_extra, 18_displacement, 25_invisible_text, 32_stroke_lines
       4  05_chars_extra, 18_displacement, 32_stroke_lines, 60_text_column_right_edge

`classpick.py --leverage` prices 32_stroke_lines at **36.3 clean documents**, 05_chars_extra at 35.0 and
18_displacement at 28.6 — the top three, and the shape above is where they co-occur. So one construct
that clears all three is the largest single prize in the pipeline. The question this run answered is
whether the construct that replaces a rule — a **table cell border** — survives Google at all.

## 1. The shape is Google-only, so it is not the space advance

The 15 documents that fail exactly `05+18+32` in Google, against the LibreOffice result on disk. **Read the engine column in §1a before trusting a pair** — the committed results carry two different stamps and four pairs do not match:

| document | Google | LibreOffice |
|:--|:--|:--|
| `16_right_aligned_amounts_txtpos` | 39/42 — 05, 18, 32 | **42/42** |
| `22_invoice_four_columns_txtpos` | 39/42 — 05, 18, 32 | **42/42** |
| `29_dot_leaders_txtpos` | 39/42 — 05, 18, 32 | **42/42** |
| `31_times_body_arial_headings` | 39/42 — 05, 18, 32 | **42/42** |
| `41_coloured_headings_white_bg` | 39/42 — 05, 18, 32 | **42/42** |
| `68_journal_wide_table_spanning` | 39/42 — 05, 18, 32 | 40/42 — 18, 59 |
| `71_invoice_space_aligned_no_rules` | 39/42 — 05, 18, 32 | 41/42 — 18 |
| `72_bank_statement_no_rules_right_amounts` | 39/42 — 05, 18, 32 | **42/42** |
| `73_marksheet_subject_marks_grade` | 39/42 — 05, 18, 32 | **42/42** |
| `balance-sheet-two-columns-of-figures` | 39/42 — 05, 18, 32 | 41/42 — 18 |
| `bus-timetable-station-left-times-right` | 39/42 — 05, 18, 32 | **42/42** |
| `insurance-policy-schedule` | 44/47 — 05, 18, 32 | **47/47** |
| `mobile-bill` | 44/47 — 05, 18, 32 | **47/47** |
| `table-with-no-header-row` | 44/47 — 05, 18, 32 | **47/47** |
| `two-tables-stacked-with-no-gap` | 44/47 — 05, 18, 32 | **47/47** |

Read from `benchmarks/gverify/*.json` and `benchmarks/gverify-lo/*.json`.

**Twelve of the fifteen pass every one of their checks in LibreOffice.** That makes the explanation the
`47_margins` work would otherwise suggest unlikely: a space's advance is the same in both renderers when
both substitute the same face, so if space advance were the cause LibreOffice would fail too. It does not.
Something Google does and LibreOffice does not is producing all three symptoms at once, on documents that
are otherwise perfect.

### 1a. Which pairs are actually comparable

Only **three** of the fifteen pairs carry the same known `engine` stamp on both sides. Four carry
different stamps (`16`, `22`, `29`, `31`: Google on `462353f`, LibreOffice on `7112d76`) and eight carry
no stamp at all. Stated as a table rather than smoothed over, because a pair on two engines is not a
controlled comparison:

| pair | Google stamp | LO stamp | comparable |
|:--|:--|:--|:--|
| `41_coloured_headings_white_bg` | `7112d76` | `7112d76` | **yes** — LO 42/42, Google 39/42 on 05+18+32 |
| `71_invoice_space_aligned_no_rules` | `7112d76` | `7112d76` | **yes** — LO 41/42, Google 39/42 |
| `73_marksheet_subject_marks_grade` | `7112d76` | `7112d76` | **yes** — LO 42/42, Google 39/42 on 05+18+32 |
| `16`, `22`, `29`, `31` | `462353f` | `7112d76` | no — different engines |
| the other 8 | none | none | no stamp to compare |

The hard evidence is therefore **two documents** — `41` and `73` — where the same engine, the same
`.docx` bytes and the same 42 checks give 42/42 under LibreOffice and 39/42 under Google failing exactly
`05+18+32`. Two is enough to establish that the shape is renderer-specific and not a space advance; the
other ten are consistent with it and are not proof of it. A run that wants the stronger statement should
re-measure the LibreOffice column on `462353f`, which the `:00` baseline cron already owns.

These are the `*_txtpos` and space-aligned families — layouts whose columns are held by padding and whose
rules the source draws. `FINDINGS/32_stroke_lines-google-drop-113048-9597.md` already identified the
construct: a rule leaves this writer only as a floating `<w:drawing>` inside a `<wp:anchor>`
(`DocxWriter.shape()`, `DocxWriter.java:2772`, `<w:drawing>` at `:2782`), and `google_safe.py` lists both
`w:drawing` and `wp:anchor` as constructs Google does not honour. `05_chars_extra` and `18_displacement`
are its two companions, because the anchor keeps something and the shape does not.

## 2. Measured: Google drops the anchored drawing, and the extra characters are NOT the anchor

Two hand-built `.docx`, identical except that one carries a floating anchored 400 × 1 pt black rectangle
in an empty one-twip paragraph between `ABOVE` and `BELOW`. Both uploaded to Drive as Google Docs and
exported back as PDF.

| | WITH the anchored drawing | WITHOUT it |
|:--|:--|:--|
| thin segments drawn | **0** | 0 |
| images | 0 | 0 |
| spans | `ABOVE` y=0.47 · space y=1.36 x=37.86 sz10 · space y=4.52 sz10 · `BELOW` y=14.07 | **identical** |
| `BELOW` y | 14.07 | 14.07 |

Two things follow, and the second one corrects the record:

* **The drawing is dropped.** No segment, no picture, nothing. `32_stroke_lines` fails on a rule carried
  this way, confirmed on the renderer rather than inferred from `google_safe.py`'s list.
* **The extra characters are not the anchor.** The two exports are *byte-for-byte identical in their
  spans*. Both carry two 10 pt space spans that this run's `.docx` never wrote. They come from the
  **empty carrier paragraph**, not from the drawing's anchor, and they survive the drawing's removal.
  `FINDINGS/32_stroke_lines-google-drop-113048-9597.md` says the character Google leaves at an anchor is
  `U+200B`; on this probe the extras are plain spaces and they are there whether or not a drawing is
  present. That matters practically: **deleting the drawing alone will not clear `05_chars_extra`.** The
  one-twip carrier paragraph has to go as well, or `05` stays failing and the document still does not
  reach clean.

## 3. Measured: Google honours a cell border, both axes

This is the answer the pipeline needed. Two more `.docx`, each one 1 × 1 table with every table border
set to `nil` and exactly one `w:tcBorders` edge set to `single`.

**Horizontal — `<w:tcBorders><w:bottom w:val="single" w:sz="8"/>`:**

| | measured in the Google export |
|:--|:--|
| segments drawn | **1** |
| geometry | `Rect(-6.0, 49.5, 462.0, 49.5)` — width **468.00 pt**, height 0.00 |
| stroke | black `(0, 0, 0)` |

**Vertical — `<w:tcBorders><w:left w:val="single" w:sz="8"/>` on a row with `w:trHeight w:val="1440" w:hRule="exact"`:**

| | measured in the Google export |
|:--|:--|
| segments drawn | **1** |
| geometry | `Rect(-5.5, 25.0, -5.5, 97.0)` — height **72.00 pt**, width 0.00 |
| requested height | `1440` twips ÷ 20 = **72.0 pt** |

Requested 72.0 pt, delivered 72.00 pt. Both axes render, at the requested weight and the requested
length. `google_safe.py` does not list `w:tcBorders`, and this is the measurement behind that omission
rather than an assumption.

### What this settles and what it does not

**Settled.** The construct that must replace the floating drawing *is* honoured by the renderer that
matters. The route named in the last run's handoff — "`DocxWriter.java:6420` already writes
`<w:tcBorders><w:bottom>` and can carry the vertical rules" — is alive. The `w:pBdr` route is dead on
placement, not on rendering, and this finding does not re-open it.

**Not settled by §3: PLACEMENT.** Both borders landed where the *table* put them, not where a coordinate
said. So the question became "can a 1 × 1 table be put at an arbitrary x, at an arbitrary length, without
moving the text" — and §4 answers two of those three with an exact number.

## 4. Measured: a cell-border rule can be placed EXACTLY in x and in length. Flow is the open problem.

Four more probes, same procedure, all with `w:pgMar` at zero and every table border `nil` except one
`w:tcBorders` edge. Requested `w:tblInd` = 1000 twips = 50.0 pt in every case; requested length =
2000 twips = 100.0 pt where a length was requested.

| probe | what the `.docx` asked for | segment measured in the Google export |
|:--|:--|:--|
| P1 | `tblInd` 50 pt, `tblW` 100 pt, cell margins 0 | x0 = **50.00**, x1 = 518.00, **w = 468.00** |
| P2 | as P1 but one `w:tblW` (python-docx's default removed) and `trHeight` 0 exact | x0 = **50.00**, w = **468.00** |
| P3 | as P2 plus `w:tblLayout w:type="fixed"` and `w:tblGrid`/`w:gridCol` = 2000 twips | x0 = **50.00**, x1 = 150.00, **w = 100.00** |

* **`w:tblInd` places the left edge exactly.** 50.0 pt requested, 50.00 pt measured, in all three.
* **Length needs `w:tblLayout="fixed"` AND a `w:tblGrid`.** `w:tblW` alone is ignored: P1 and P2 both
  stretched the border to 468.00 pt, the full text width. Adding fixed layout and a 2000-twip grid
  column made it **100.00 pt**, exactly as asked. The 100 pt bar in P3 starts at 50.00 and ends at
  150.00 — position and length both exact to 0.00 pt.
* **Flow is NOT solved, and it is now the only thing standing in the way.** `BELOW` sits at
  y = **52.31** under every one of these tables, against y = **14.07** in the identical document with no
  table at all (the §2 control). The row consumed about 38 pt of vertical flow, and `w:trHeight
  w:val="0" w:hRule="exact"` did **not** prevent it — P2 and P3 ask for a zero-height row and both still
  displace the following paragraph by the same amount. A `behindDoc` drawing displaced nothing, which is
  the one thing it had over a table.

So the next run's problem is a single one, and it is not rendering, not x, and not length: **make a table
occupy no flow space.** Untried and plausible: a nested table inside a cell of an outer zero-height row, a
`w:tblpPr` floating table (`tblpPr` positions a table absolutely, which is the OOXML feature built for
this), or a table in a paragraph marked `w:framePr`. Note that `w:framePr` is on `google_safe.py`'s ignored
list, so the third is the least likely of the three.

## 5. The tab stop, measured separately

`FINDINGS/47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md` in this same commit: Google resolves
`w:tab w:pos` exactly (216.0 pt requested, 216.00 pt measured) and resolves it from the **left margin**
(72 pt margin + 216 pt stop → 288.00 pt). Worth reading together with this one, because it is the same
question — which flow constructs survive the renderer — answered for a different construct.

## 6. How to repeat it

    python-docx (or raw OOXML) -> build one paragraph / one table with the construct
    upload(path=..., toolkit="googledrive", tool_slug="GOOGLEDRIVE_CREATE_FILE")     # -> s3key
    GOOGLEDRIVE_CREATE_FILE(mimeType="application/vnd.google-apps.document",
                            file_to_upload={name, mimetype, s3key})
    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=..., mimeType="application/pdf")
    pymupdf: page.get_drawings() for segments, page.get_text("dict") for spans

Traps, all hit this run: `upload` refuses a path outside `/scratch/output`, so copy the probe there
first; `GOOGLEDRIVE_CREATE_FILE`'s result is `content[0].text` JSON when called as a tool but not when
imported into a program, so do not parse it blind; and Google emits its own zero-width and space spans
around empty paragraphs, so a span you did not write is not evidence of a construct you did write.

**Cleanup.** Six probe documents were created in Drive and all six were deleted. Two older
`p2w-probe-392` / `p2w-probe-392-courier` documents from a 06:31 run are still in Drive — not created by
this run, left alone, and named here so someone can decide about them.
