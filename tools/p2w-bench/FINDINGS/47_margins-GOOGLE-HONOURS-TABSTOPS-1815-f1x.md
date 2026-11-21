# Google Docs honours `w:tabs` in a flow paragraph — measured, not inferred

**21 Nov 2026 · relay/fixer slot 18:19 · engine `462353f` · one question, three documents, one export each**

## The question this answers

`FINDINGS/47_margins-CELL-BORDER-PAID-TWICE-034500-f1x.md` and the `47_margins` docx-half investigation
both ended at the same wall: a tab stop is **not** on `google_safe.py`'s ignored list, but *not listed* is
not *honoured*, and neither run could take the measurement, because staging a local `.docx` into Drive
needs a platform `upload` tool that a sub-agent does not have. Every proposal in this family has therefore
been stuck at "predicted Google: NOT VERIFIED".

That wall is gone. The relay has the `upload` tool. The measurement below was taken through Google Docs
itself, not through LibreOffice.

## What was measured

Three `.docx` files, each one paragraph, 11 pt, built with python-docx so nothing about the engine is
involved. Each was uploaded to Drive as `application/vnd.google-apps.document`, exported back as PDF, and
the ink x of each span read with PyMuPDF. Page 612 × 792 pt.

| probe | page setup | what the .docx asks for | what Google rendered | verdict |
|:--|:--|:--|:--|:--|
| **A — tab** | `w:pgMar` left = 0 | `<w:tabs><w:tab w:pos="4320" w:val="left"/></w:tabs>`, `STEP` + `<w:tab/>` + `VALUE` | `STEP` x0 = 0.00, **`VALUE` x0 = 216.00** | honoured, exactly |
| **B — spaces** | `w:pgMar` left = 0 | `STEP` + 30 spaces + `VALUE` | one merged span, 0.00 → 131.05 | spaces do not pin |
| **C — tab, with a margin** | `w:pgMar` left = 72 pt | the same tab stop at `w:pos="4320"` (216 pt) | `STEP` x0 = 72.00, **`VALUE` x0 = 288.00** | honoured, from the **margin** |

4320 twips ÷ 20 = **216.0 pt**. Probe A delivered 216.00. Probe C asked for the same 216 pt with a 72 pt
left margin and delivered 288.00 = 72 + 216.

### Two facts, both with a number

1. **Google Docs resolves `w:tab w:pos` exactly.** Requested 216.0 pt, measured 216.00 pt — error 0.00 pt
   at the precision the PDF reports. This is the construct the `47_margins` docx half wants to emit, and
   the renderer that matters honours it.
2. **The origin is the left margin, not the page edge.** Probe C separates the two hypotheses, which
   probe A cannot: 288.00 matches *margin + stop* and refutes *page edge* (216.0) outright. The engine
   writes `w:pgMar` as a hard zero (`DocxWriter.sectPrXml`), so today the two origins coincide and a
   `w:pos` equal to the run's page x is correct **only because the margin is zero**. Any future change
   that gives a page a real margin silently shifts every tab stop by that margin. That is a trap worth
   writing down before it is stepped in.

### What probe B shows about the mechanism

With spaces, Google delivered a gap of 131.05 − 24.41 = **106.6 pt** where 30 spaces at 11 pt were asked
for. With a tab stop it delivered exactly the 216.0 pt requested. So the 2 pt-scale errors `47_margins`
measures are not a rounding artefact — a run whose position is carried by spaces is placed at wherever
the renderer's space advance happens to land, and a tab stop is placed where the document says. That is
the whole thesis of the flowing-text model, confirmed on one construct.

## What this does NOT establish

Stated plainly, because the last four constructs in this family died on a detail like one of these:

* **Not measured: a tab inside a table cell.** The `47_margins` proposal guards on `!ctx.inColumn`
  partly for this reason. Untested here.
* **Not measured: right / centre / decimal tab alignment.** Only `w:val="left"` was sent.
* **Not measured: more than one tab stop in a paragraph**, or a stop that is reached by more than one
  tab. Google's behaviour when a tab overshoots the last stop is untested.
* **Not measured: a tab whose stop is to the left of the current position**, which is what a guard bug
  would produce.
* **Not measured: whether the 42 checks agree.** This is an ink-position measurement, not a score. A
  document can honour the tab and still fail `47_margins` for the anchor clause, or gain a failure in
  `60_text_column_right_edge` because everything after the tab moved. The score still has to be taken
  document by document through `gverify.py`.

## What it re-opens, and what it does not

* **It does not re-open** the refuted `w:pgMar + indents` family (`40/42 → 32/42`). That was a change to
  the margin and to the indent; this measures a tab stop and changes neither.
* **It does unblock** the tab-stop construct for a future fixer: the decisive falsifier in
  `47-margins-docx-half.md` §4 ("Google says no") can no longer kill it on the construct itself. What is
  left is the ordinary question of reach and of whether the score moves.
* **It makes the `w:pgMar = 0` coupling explicit.** If anyone lands page margins, every `w:tab w:pos`
  already in the tree shifts. `flowRow` has shipped tab stops since before this finding and would shift
  with it.

## How to repeat it

The probe documents are three paragraphs of python-docx and are not worth keeping; the procedure is:

    python-docx -> build one paragraph with the construct
    upload(path=..., toolkit="googledrive", tool_slug="GOOGLEDRIVE_CREATE_FILE")   # -> s3key
    GOOGLEDRIVE_CREATE_FILE(mimeType="application/vnd.google-apps.document",
                            file_to_upload={name,mimetype,s3key})
    GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE(fileId=..., mimeType="application/pdf")
    pymupdf: page.get_text("dict") -> spans -> bbox[0]

Two traps for the next run: `upload` refuses a path outside `/scratch/output`, so the probe has to be
copied there first; and Google emits a zero-width-space span (`\u200b`) at the tab position, so read the
span whose text is the *word after* the tab, not the first span on the line.
