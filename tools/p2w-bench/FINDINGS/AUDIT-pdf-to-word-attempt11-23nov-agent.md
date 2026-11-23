# PDF-to-Word — deep audit, attempt 11 of 15

Agent, 23 Nov 2026. Read-only. First of five focused attempts on `DocxWriter` (7,671 lines, 157 methods, of which
the previous ten attempts had read about five). This one is the document body — `documentXml` and `pageBody` — and
it closes the extra-page question that attempt 2 opened.

---

## K1 — the extra-page mechanism is documented in the code, and half-fixed

`pageBody`'s own comment (1335-1345):

> *"Until now a full-width element between the columns was given a section of its own, and the boundaries were
> `<w:type w:val="continuous"/>`. Word and LibreOffice honour that. **Google Docs does not: it turns every
> continuous break into a PAGE break**, so a one-page newsletter arrived as two pages. Measured on
> `62_two_col_newsletter_pull_quote` — six continuous breaks, 474 pt of flow on an 842 pt sheet, two pages in
> Google Docs."*

The chosen fix is to write a column page as a fixed-geometry layout table — one row, one cell per column — so
nothing in the document is a section. That is correct, and it is why the newsletter case is closed.

---

## K2 — but that is not the cause for the 21 single-page documents, and this attempt rules it out

Attempt 2 found 21 documents that are one page in the PDF and two in the `.docx`. The section break cannot be the
cause for them, and the code says why:

    } else if (Math.abs(pw - secW) > 0.5f || Math.abs(ph - secH) > 0.5f || pCols != secCols) {
        ... <w:type w:val="nextPage"/> ...

This branch emits a `nextPage` section break only when the page **size or column count changes** between
consecutive pages. A one-page PDF never reaches it: the first page takes the `if (first)` branch and there is no
second page. **So the +1 page on those 21 documents comes from somewhere else, and the section break is excluded.**

---

## K3 — the cause is the flow guard's third outcome, and it is deliberate

The fitter has three outcomes (632-650):

    1. lineTw <= room          the line fits
    2. room >= ascent          ctx.flowTw = ctx.budgetTw; ctx.fitted++;   the line is shortened to fit
    3. room <  ascent          the line keeps its own height and THE PAGE OVERRUNS

Outcome 3 is the extra page. And it is a decision, not an oversight:

    365:  private static final boolean BREAK_WHEN_UNFITTABLE = false;

Hard-coded `false`, not a system property — so the tool always prefers keeping the line at its true height over
breaking the page. The comment at 645 says the guard "is not allowed to trade" fidelity for page count.

**That is a defensible choice and I am not arguing against it.** Squeezing a line below its ascent deforms the
text, which is worse than an extra page. But it has a consequence that the code does not account for, and that is
K4.

---

## K4 — the one outcome that costs a page is the only one not counted

    ctx.fitted++;      counts outcome 2 (lines shortened to fit)
    (nothing)          counts outcome 3 (page overrun)

`grep` for `overrun` in `DocxWriter` returns **only comments** — no counter, no field, no note. So:

- a document where every line fits and a document where the last line overran produce **the same report**;
- the report's `notes` list, which already carries `skippedPages` and OCR failures, says nothing;
- and the page count is the only symptom, which is why attempt 2 could only see it as "+1 page" without a cause.

**This is the same pattern as every previous attempt, in its sharpest form: the tool makes a decision about the
document and does not record it. Here the decision costs a page, and it is invisible.**

---

## K5 — the diagnostic already exists, and 30 flags with it

    if (System.getProperty("p2w.debugFlow") != null) {
        System.err.println("FLOW page=" + (++ctx.pageSeq)
                + " flowTw=" + ctx.flowTw + " budgetTw=" + ctx.budgetTw
                + " overTw=" + (ctx.flowTw - ctx.budgetTw) + " needTw=" + needTw + ...);
    }

**`-Dp2w.debugFlow` prints, per page, exactly how much the flow exceeded its budget.** That is the number K3
describes, per page, already written. Nobody has to derive it.

And it is not alone — the engine carries **30 `p2w.*` system properties**, of which several are tunables rather
than debug switches (`colMinBand`, `colMinFill`, `colMinLeft`, `colMinLines`, `fitreserve`, `ovf`, `wrapgate`,
`ascent`, `zgfloor`, `zganchor`, `recut`, `noshave`, `nocol`, `lineRule`, `softmask`, `anchorkeep`, `autoEm`,
`clipDbg`, `census`, `debugAnchors`, `debugClip`, `debugCols`, `debugGaps`, `debugPin`, `debugFlow`, `pagepos`,
`row`, `osplit`, `traceLines`, `colcharge`).

**None of them is documented anywhere the fixer reads.** That matters in both directions: a run cannot use the
diagnostics that would tell it why a page overran, and it cannot know which of the tunables change output if set.

---

## For the fixer

1. **K4 first, and it is a few lines:** count the overrun in `Ctx` and put it in `Report.notes` — "page 3 overran
   its budget by 58 pt". Then attempt 2's 21 documents stop being a mystery and become a list with a number each.
2. **K5:** write the 30 flags into a file the fixer reads, marking which are diagnostics and which change output.
3. **Do not set `BREAK_WHEN_UNFITTABLE = true`.** It would fix the page count by deforming text, which is the
   trade this project has already refused.

Verify before changing. This attempt read code; it ran nothing.
