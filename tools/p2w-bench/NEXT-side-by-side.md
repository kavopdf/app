# NEXT: the side-by-side field fix

Three documents still fail, all for one cause. This note is the whole trace so the
next pass does not have to rediscover it.

## The three documents, at `b90577f`

```
salary-slip-corporate     median dy 57.5 pt   worst 259.5   within 10pt 30 %   order 47 %
admit-card                median dy 17.2 pt   worst  19.4   within 10pt 15 %   order 35 %
gst-invoice-with-qr-code  median dy 11.1 pt   worst  28.7   within 10pt 19 %   order 72 %
```

## What the page has, and what we emit

All three are single-column pages full of label/value pairs on one baseline:

```
PDF   Employee code ············ 107 pt ············ MT-2016-1188
DOCX  Employee code
      MT-2016-1188          <- two paragraphs, stacked
```

`salary-slip` also has four-column table rows read as one line:
`EARNINGS · 166 pt · AMOUNT (RS) · 157 pt · DEDUCTIONS`.

## The trace, complete

```
PdfToWord.assignSegments (~2546)
  measures every inter-glyph gap on the line
  median of those gaps
  outlier = max(6, median * 0.85)
  gapPts  = g.x - (prev.x + prev.width)      signed, not positive
  wideGap = gapPts > outlier
  -> cuts the line into segments             CORRECT
  -> each segment becomes its own Line
  -> line.hardEnd = true                     CORRECT (means: do not merge upward)

PdfToWord.keep0 (~2218) / the Para builder
  each Line becomes its own Para             <- THE DEFECT
  so each Para holds exactly one Box

DocxWriter.flowRow (~2267)
  reads p.boxes
  if 1 box  -> flowFromBox, a normal paragraph
  if 2+ box -> one paragraph, w:tab at each field's measured x   CORRECT
```

So the tab machinery is right and never gets used. `flowRow` receives one box
because the paragraph builder made one paragraph per line.

## The fix

Two `Line`s that share a baseline (same page, y within tolerance, same column)
must become **one `Para` with two `Box`es**, not two `Para`s.

`hardEnd` must keep its current meaning — it stops a line merging into the line
*above* it. It must not stop two lines on the *same* baseline from sharing a
paragraph.

Do not lower `outlier` or change the gap test. The segments are already correct;
the grouping after them is what is wrong.

## How to verify

```
1  build at the current HEAD
2  convert the three documents
3  verify_visual.py on each — median dy should fall well under 10 pt
4  gate.py --check on all 208 — no document worse
5  the protected set unchanged: 62, 63, 16, 20, 80, 23, 02,
   table-with-merged-cells, boq-tender, 352, marksheet
```

Expected: the label/value pairs stop stacking, so the page stops growing and the
drift disappears. `salary-slip` should also stop reading its four-column table
rows as single lines.

## After that

The APK. Nothing else is outstanding at `b90577f`.
