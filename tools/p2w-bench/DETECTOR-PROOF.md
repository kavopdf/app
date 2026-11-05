# detect.py extension — evidence

Everything below was measured in this sandbox. Commands are given so each number can be
re-run. No figure here is estimated.

## Environment

    JDK 17.0.13 (Temurin) at /scratch/work/jdk
    PDFBox-Android 2.0.27.0 (.aar -> classes.jar, assets/ on the classpath)
    BouncyCastle bcprov/bcpkix/bcutil 1.72
    PyMuPDF 2.1 (MuPDF 1.28.6), lxml 6.1.3, LibreOffice 7.4.7.2
    java flags: -XX:+UseSerialGC -XX:ActiveProcessorCount=1 -XX:CompressedClassSpaceSize=128m
                -XX:MaxMetaspaceSize=512m -Xmx900m -Djava.awt.headless=true, ulimit -v unlimited

Engines built from the repository (a copy at /scratch/work/repos/app, never pushed):

    HEAD         9de9674  3.50.0
    ed55b44      3.49.8   black-as-no-colour FIXED, no shapes
    622e446      3.49.7   black-as-no-colour BUG present, no shapes

**A correction on the brief.** The brief asks for "the OLD engine 3.49.8 (which had no shapes
and the black-as-no-colour bug)". Commit ed55b44, titled "3.49.8", is the commit that FIXED the
colour bug; the state that has both faults is its parent 622e446, "3.49.7". There is also no
`v3.49.8` tag in the repository (tags jump v3.49.2 -> v3.49.9), so the commit was used. Both
builds were made and both were converted over all 80 files.

## The three classes

### SHAPE_LOST
PDF side: `page.get_drawings()`, **one count per painted path** — a filled path is a fill, a
path made only of rectangles and axis-aligned lines is a rule, a curved stroke is skipped (the
converter drops a curve on purpose rather than put a square where a seal's ring is).
.docx side: `wps:wsp` elements that contain **no** `w:txbxContent`, counted per page. A text box
is also a `wps:wsp`, which is exactly why a namespace-blind grep is useless here: 3.49.8 wrote
24 / 29 / 36 / 45 `wps:wsp` on files 39 / 54 / 62 / 63 and not one of them was a shape.
A page that became a real `w:tbl` is judged on its **fills only**, because the table carries its
grid as `w:tblBorders`. Measured: with that rule the current engine reports 0 pages; without it,
19 — every one of them a table grid that is present as borders.

### INVISIBLE_TEXT
Two arms, both checked against the colour the PDF span was painted:
* *inverted* — every run is `#FFFFFF`, the PDF paints that text in another colour.
* *dropped* — no run carries a colour (Word resolves that to black), the PDF paints the text
  white, and a shape sits behind it in the .docx.
White text that the PDF also draws white is **not** flagged: files 54/62/63 set their masthead
title white on a navy band, and those runs are correct.

### ROTATED_CLIP
A leaf whose source PDF line was drawn at an angle (`line["dir"]` not horizontal). If the render
does not hold the whole string but holds a prefix of it, the box lost the tail. Rotated leaves are
removed from CLIPPED/RENDER_MISSING so the defect is named once, not twice.

## Proof against the old engines

| file | engine | known defect | class | result |
|---|---|---|---|---|
| 39 | 3.49.7 (622e446) | title written #FFFFFF, PDF draws it #000000 | INVISIBLE_TEXT | **caught** |
| 54 | 3.49.8 (ed55b44) | masthead band not drawn | SHAPE_LOST | **caught** |
| 62 | 3.49.8 | masthead band not drawn | SHAPE_LOST | **caught** |
| 63 | 3.49.8 | masthead band not drawn | SHAPE_LOST | **caught** |

Literal output:

    SHAPE_LOST     39_... p1  0 filled path(s) and 2 rule(s) painted, .docx carries 0 shape(s)
    INVISIBLE_TEXT 39_... p1  'T H E M Y S O R E C H A M B E R ...' written #FFFFFF,
                              the PDF draws it #000000
    SHAPE_LOST     54_... p1  1 filled path(s) and 2 rule(s) painted, .docx carries 0 shape(s)
    SHAPE_LOST     62_... p1  3 filled path(s) and 2 rule(s) painted, .docx carries 0 shape(s)
    SHAPE_LOST     63_... p1  1 filled path(s) and 6 rule(s) painted, .docx carries 0 shape(s)

Control on the fixed engine (3.50.0): all four files report 0 SHAPE_LOST and 0 INVISIBLE_TEXT.
Independent confirmation of the file-39 hit: the old .docx holds 15 runs of `FFFFFF`; 3.49.8 and
3.50.0 hold none.

The *dropped* arm cannot be reached by a build of the corpus, so it was proved on a mutant: the
`w:color` element was deleted from file 54's white masthead title and the detector reports

    INVISIBLE_TEXT 54_... p1  'INDIAN INSTITUTE OF PLANTATION MANAGEMENT' carries no colour,
                              the PDF draws it white on a band

ROTATED_CLIP is proved on the current engine, because file 03's clip was never fixed:

    ROTATED_CLIP 03_stamp_vertical_90deg p1 'VERIFIED FOR AUDIT'  drawn at -90.0 deg renders as 'VERIFIED'
    ROTATED_CLIP 03_stamp_vertical_90deg p1 'INTERNAL AUDIT CELL' drawn at -90.0 deg renders as 'INTERNAL AUD'

Both were checked against the original PDF: the page really does draw those three lines, all
present, inside the stamp (rendered and inspected). In the .docx the box starts at x=549 on a
595 pt page and the render stops at x=599 / 596 — the page edge — while the three lines also
overlap each other.

## Totals

    engine 3.49.7 (both faults)   125 defect lines    SHAPE_LOST 70 pages / 66 docs, INVISIBLE_TEXT 1
    engine 3.49.8 (no shapes)     124 defect lines    SHAPE_LOST 70 pages / 66 docs, INVISIBLE_TEXT 0
    engine 3.50.0 (HEAD)           59 defect lines    SHAPE_LOST 0, INVISIBLE_TEXT 0, ROTATED_CLIP 2

Per class on 3.50.0, all 80 documents, with --render:

    MISSING_TEXT 30 | MISSING_ROWS 6 | GLUED_WORDS 12 | WRAPPED 0 | DUPLICATED 0 | EMPTY_PAGE 0
    IMAGE_LOST 0 | CLIPPED 5 | RENDER_MISSING 4 | SHAPE_LOST 0 | INVISIBLE_TEXT 0 | ROTATED_CLIP 2

The nine-class detector reported 59 on this engine too: 6 CLIPPED and 5 RENDER_MISSING. One of
each belongs to file 03's rotated stamp and is now named ROTATED_CLIP, so the total is unchanged
and no defect is counted twice.

## The one open defect, and the fix that was reverted

File 03's stamp cannot be placed without rotating the text box. Two OOXML mechanisms were tried
and measured against the render:

1. `<a:xfrm rot="16200000">` on the `wps:wsp` — written, and LibreOffice 7.4.7 ignores it: the
   text stays horizontal at the same place (`dir (1.0, 0.0)` before and after).
2. `<wps:bodyPr vert="vert270">` — honoured, but LibreOffice lays Latin text out as CJK vertical
   text, one character per row, and drops most of the string.

`a:bodyPr rot` was also tried and ignored. The engine change (rotation written for vertical
lines, box centred on the painted line) was built and measured, and it did not move the render,
so it was reverted rather than shipped unvalidated — the exact mistake the brief warns about.
`git status` on the engine shows no modification.

Suite after the revert: `TestPdfToWord 29 passed, 0 failed`, `TestRealDocs 3 passed, 0 failed`
(96.8 / 97.0 / 81.7 — the same figures the repository records for 3.49.8).
Score: unchanged, as expected for an engine that was not modified — char volume 99.91, word
recall 99.67, line count 99.49, exact 98.60, global 98.57, order 93.68, garbage 0.00,
doc pass@95 93.75 (75/80), pass@98 86.25 (69/80), median 100.00.

## Reproducing

    bash /scratch/work/harness/build.sh <source-tree> <classes-out>
    bash /scratch/work/harness/run.sh  <classes-out> <pdf-dir> <docx-out>
    python3 tools/p2w-bench/detect.py --pdf-dir <pdf-dir> --docx-dir <docx-out> \
            --render-dir <rendered> --summary
