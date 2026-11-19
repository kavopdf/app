# The pBdr rule fix cannot work as written — a rule is emitted after the flow has passed it

Follows `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` (a rule is a floating `<w:drawing>`; Google drops it),
`RULES-PBDR-FIX-MEASURED.md` (pBdr drew both rules but put both at the foot of the page) and
`RULES-PBDR-IMPLEMENTATION.md` (the code, with the `w:before` gap and `ctx.flowY = s.topPt`).

**The implementation is correct and it is inert.** Not because the gap formula is wrong — because there
is never a gap to measure. Read this before spending a build on it.

## What was tested, and how

    * reading      DocxWriter.java:1315-1340 (the page emit loop), :2219-2241 (emitBlock)
    * reading      PdfToWord.java:7100-7123 (the shape attach pass, `page.blocks.add(s)`)
    * built+parsed the emitted `word/document.xml` of 18_centred_heading_left_body_txtpos
                   (done by the A agent this run, FINDINGS/content-present-partly-displaced-
                   zerowidth-040040-7c1e.md)
    * NOT built    the pBdr variant itself. There is no reason to: the precondition it needs is
                   absent by construction, and the numbers below say so without a compile.

## The mechanism

A paragraph border is placed by **flow**. `ruleAsBorder()` therefore emits the carrier paragraph with

    w:before = (s.topPt - ctx.flowY - below) * 20      only when  s.topPt > ctx.flowY

and then sets `ctx.flowY = s.topPt`. That is right, and it is what the 19 Nov attempt left out.

The flow has already gone past the rule by the time the rule is written:

1. `PdfToWord.attachShapes()` appends every surviving shape to `page.blocks` — `PdfToWord.java:7122`,
   `page.blocks.add(s)` — in a pass that runs **after** the page's paragraphs and tables are in that
   list.
2. `DocxWriter.pageXml()` writes `page.blocks` in list order (`DocxWriter.java:1324-1332`,
   `emitBlock(sb, block, ctx)`). There is no re-sort by top on this path: the only `sortByTop` calls
   are inside `columnPage()` (:1937-1939), for the newspaper-column layout table.
3. So every shape is written **last on its page**, when `ctx.flowY` is at the bottom of the page's
   text — and `s.topPt > ctx.flowY` is false for every rule on the page.

Measured on 18_centred_heading_left_body_txtpos, from its own emitted spacing:

    sum of w:before over paragraphs 0..21   15840 tw = 792.0 pt
    sum of w:line                           278   tw =  13.9 pt
    flow after p21                                  = 805.9 pt

    rule 1   y = 110.0      rule 2   y = 793.89      flow when both are written = 805.9

Both rules are **behind** the flow. `w:before` cannot place a paragraph at a y the flow has already
passed, so the guard yields `beforeTw = 0` and the border falls wherever the previous paragraph ended —
which is exactly the "both landed at the foot of the page (y 807 and 808)" that
`RULES-PBDR-IMPLEMENTATION.md` records, and it is why the 19 Nov measurement read *rules drawn 2,
lost 1 of 2*: one border was drawn at a y the page does not have.

**Without a guard, pBdr is a LibreOffice regression.** The drawing path pins the rule absolutely, so
LibreOffice draws it at y=110 today and `32_stroke_lines` fails 0 documents in LibreOffice. A border at
y=807 puts a rule on the footer and takes one off the head, in the renderer the gate reads.

## What the next run should do, in this order

The precondition is not "a better gap formula". It is **the rule must be written before the text that
follows it**. One bounded change, no re-sort of the page:

    in pageXml()'s emit loop, before writing each Para/Table block, flush any not-yet-written
    Shape whose s.topPt <= that block's top, in top order; then, after the loop, flush the rest.

That keeps the paragraph/table order exactly as it is today (the order the column pass and the budget
guard depend on) and only moves shapes earlier, into the flow position the page drew them at. Then
`ruleAsBorder()`'s `s.topPt > ctx.flowY` test starts being true, the `w:before` gap is real, and
`ctx.flowY = s.topPt` is what stops every line below the rule drifting up.

**Then and only then** measure — and expect the guard to decline on the rules it still cannot place
(a rule that overlaps text drawn after it), which is the correct outcome and leaves the drawing path
untouched there.

## What this rules out, so the next run does not re-derive it

* **The gap formula is not the bug.** `flowBoxPt * (1 - LINE_BASE)` is right; there is simply no gap
  to compute when the flow is already below the rule.
* **There is no third construct emitting the U+200B.** Checked on the emitted XML of
  18_centred_heading_left_body_txtpos: 0 tables, 0 `tcBorders`, 0 `pBdr`, 0 `txbxContent`, 2
  `<w:drawing>`, and **0 U+200B in all 211 corpus `.docx` files**. No Java line writes the character;
  it is Google's own placeholder for a floating drawing it refused to import. (Agent A, this run.)
* **Corpus scale of the target:** 4721 rule-shaped drawings across 183 of 211 documents. A fix that
  works changes the emitter for all of them, not a page.

## Confidence

**High** that pBdr-without-the-flow-fix is inert, and that the 19 Nov "both at the foot" number has
this cause: it is derived from the emitted spacing of the document that produced that number, and it
matches the y the earlier attempt reported independently (807/808 against a computed 805.9).

**Medium** that the flush-by-top change is enough on its own: a rule that sits *under* a block of text
which is written after it in list order (an ad box, a masthead) will still be behind the flow when its
turn comes. The change makes the common case work; the guard keeps the rest honest.
