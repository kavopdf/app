# The running foot is a ROW, and `flowRow` anchors it — Google then drops the text entirely

**Recorded:** 2026-11-23 ~18:55 IST, fixer slot 17:58. Measured in Google Docs, not LibreOffice.

## The symptom pair, and why it is one cause

`27_two_column_left_short_txtpos` failed exactly two checks in Google at HEAD `b7699196`:
`04_chars_missing` and `44_header_footer`. The charter says a hypothesis that explains one
symptom and ignores the other is wrong. This one explains both, and the proof is a text diff.

At HEAD, Google's own export of that document is missing **two lines and nothing else**:

    source line  (present in the PDF)          present in Google's export?
    "The Kunigal Herald  •  14 September 2025  •  Page 1"     NO
    "Page 1"                                                   NO
    every other line of the document                            YES

Those two lines are the document's **only two DrawingML text boxes** (`w:txbxContent` count = 4
in the .docx, i.e. 2 shapes, each written twice for `mc:Choice`/`mc:Fallback`). Every other line
is a flowed paragraph. So:

* `04_chars_missing` fires because 43 characters of the page are not in the render's text layer;
* `44_header_footer` fires because the bottom-band element that repeated is gone.

One construct, two checks. Not two defects.

## Where the anchor is actually written — and two hypotheses this refutes

The two lines sit on one baseline (y = 805.89 on an 842 pt page), so `isRow()` is true and the
paragraph reaches **`flowRow`**, not the per-box `containerOf` branch in `para()`.

`flowRow`'s pitch branch (`DocxWriter.java`, the `extra > 0f` block) measures the gap to the
previous line, and when that gap is wider than `gapCapTw(ctx)` it does this:

    if (!ctx.inColumn && extra * TWIPS_PER_PT > gapCapTw(ctx)) {
        ctx.positioned = true;
        for (PdfToWord.Box ab : cols) anchorBox(sb, p, ab, ctx);
        return;
    }

The source comment above it already names this document and this gap — 272.8 pt, written as
120 pt, footer 130.6 pt above its own baseline — which is why the branch anchors instead of
truncating. **The anchor is right about the position and wrong about the construct**: Google
Docs does not carry an anchored shape's text into the text layer at all.

Two hypotheses were tested and refuted this run before this one was found. Both are recorded so
the next run does not repeat them:

1. **`containerOf` (the closed-outline branch in `para()`).** Guarded to flow band lines. Built,
   converted: `anchor` count unchanged at 2, `txbx` unchanged at 4 on all four documents. The
   branch never fires for these lines. Reverted.
2. **The `ctx.positioned` blanket latch at `para()` 3126–3133** (proposed by an analysis agent as
   "the dominant site"). The census pass refutes it: `anchorPos=0` on all four 2–3-check
   documents, i.e. not one anchor in them comes from positioned mode. `-Dp2w.census=` reproduces
   this in 15 s per document.

A third hypothesis, that `25_invisible_text` is an instrument bug using a first-match fill lookup
(which `14_filled_shapes` abandoned at `verify_google.py:5356-5361`), was **refuted by
measurement** on `300_prescription_rx`: first-match and nearest-covering-fill agree on both the
source (0/0) and Google's render (2/2). The two invisible runs there are genuine — white text that
`18_displacement` has moved off its band. Not an instrument defect.

## The change

One condition, in `flowRow`'s pitch branch: a row in the page's **bottom tenth** spends the
measured gap instead of anchoring.

    boolean footBand = first.y > 0.90f * ctx.pageHeightPt;
    if (!ctx.inColumn && !footBand && extra * TWIPS_PER_PT > gapCapTw(ctx)) { ...anchor... }
    beforeTw = (int) Math.round(extra * TWIPS_PER_PT);

The cap is right for a gap in the body of a page — a gap wider than the flow may spend means the
flow has drifted, and spending it pushes the rest of the document down. It is wrong for the last
line on the sheet: the page has already decided where that line goes and there is nothing below
it to push. The cap's own justification does not apply, so it does not apply.

## Measured, before and after, in Google

| | HEAD `b7699196` | with `footBand` |
|---|---|---|
| `27_two_column_left_short_txtpos` | **40/42 FAIL** (`04_chars_missing` source 0 / render 43; `44_header_footer` 4 claimed, 2 honoured) | **42/42 PASS** |
| `w:txbxContent` in that .docx | 4 | **0** |
| pages | 1 | **1** |
| footer lines in Google's text layer | absent | **present** |

Reproduced twice through the real path — Drive upload → convert to `application/vnd.google-apps.document`
→ export as PDF → `verify_google.py --docx` — not through `soffice`.

Side effect on `46_chart_coloured_labels_body_text`: `txbx` 4 → 0 (same footer row, same branch).
Not yet scored in Google.

`55_sidebar_box_beside_body` and `61_two_col_abstract_spanning` still carry 4 text boxes each: their
footer rows reach `flowRow` through a different branch (or are single-box paragraphs through
`flowFromBox`, which anchors the same oversized gap). **The same defect therefore has a second
site — `flowFromBox` — which this change does not touch.** That is the next attempt, and it is
worth more documents than this one.

## What this does not establish

The full corpus has not been re-measured, so `regress.py --check` refuses the commit on engine
fingerprint — correctly. Nothing is claimed about the other 211 documents. The one document
measured is measured honestly and became CLEAN.
