# Lead (not an attempt): carry a two-field baseline as a tab stop at the source x, not as spaces

**26 Nov 2026, relay/fixer run claimed 19:24 IST. Measured nothing; proposed and staged only.**

## The construct

When a PDF draws two fields on one baseline with a wide gap - a console column, a right-aligned
amount, a label/value pair - `PdfToWord.runsOf()` (emission at 5528-5535) collapses the gap to a
single U+0020 when `gap > size * 0.18`, with no upper bound. The position is then carried by the
*substitute face's space advance*, and Google does not have the face the engine names.

Proof it is a face question, not a rounding question, on `392_statistical_console_output`: the
emitted line is one run of `DejaVuSansMono` at `w:sz=13`, and the source PDF puts `Multiple` at
x=28.0 pt and `Adjusted` at x=143.22 pt on the same baseline (pymupdf `get_text('words')`,
page 0). The gap is 115 pt and the engine writes it as spaces.

## Why tab stops and not the alternatives

* Renaming the face to `Courier New` reached 42/42 in Google but was reverted: it moved the
  LibreOffice metric 1.61 -> 2.91 and `regress.py` refused
  (`FINDINGS/47_margins-DEJAVU-MONO-…-081500-f1x.md`).
* Embedding the face is ignored by Google.
* A right indent from the source margin bounds a ragged line but does not pin it
  (`FINDINGS/60_text_column_right_edge-…-24NOV-agentA.md` §3c).
* Tab stops are **measured** to be honoured: `FINDINGS/47_margins-GOOGLE-HONOURS-TABSTOPS-1815-f1x.md`
  probe A - 216.0 pt requested, **216.00 delivered**; probe C - the origin is the left margin, so
  with this engine's zero `w:pgMar` a `w:pos` is the page x; probe B - 30 spaces delivered 106.6 pt
  where asked, i.e. spaces do not pin.

## Six documents that become CLEAN if it works

`392_statistical_console_output`, `380_runbook_terminal_output`, `365_recipe_card`,
`317_rti_response`, `21_form_labels_x60_values_x300_txtpos`, `table-of-contents-dot-leaders`.
Four of the six have a Google-measured mechanism; the two `47+60` pairs are expected, not measured.

## The falsifier, one document, under ten minutes - NOT RUN THIS RUN

`/scratch/work/probe392_tab.docx` was built: the `Multiple R-squared` paragraph of `392` split into
two runs with `<w:tabs><w:tab w:val="left" w:pos="2864"/></w:tabs>` (143.22 pt x 20 twips) and a
`<w:tab/>` between them. Upload -> create as Google Doc -> export PDF -> read the x0 of `Adjusted`.
**Pass** if 143.22 +/- 1.5 pt; **refuted** if it stays near 109 pt, i.e. Google normalised the tab.

The Google half could not be run: `GOOGLEDRIVE_CREATE_FILE` returns 400 Bad Request on this pod (see
`FINDINGS/RANKING-NEVER-PUBLISHED-26NOV-relay.md`). The staged docx is the whole remaining step.

## What earlier runs tried, so this is not a repeat

`ATTEMPTS.json` 13:34 space-as-indent (moved 3) and 14:35 `anchorBox` (moved 0) - "the right idea
and the wrong site" (`FINDINGS/47_margins-SPACE-ADVANCE-TAB-STOP-073000-f1x.md`).
