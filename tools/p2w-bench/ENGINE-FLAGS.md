# THE ENGINE'S 30 SYSTEM PROPERTIES - the list, and what is not yet known about them

Written 24 Nov 2026. The audit found 30 `p2w.*` properties in the engine and the brief carried one
sentence about them. A run cannot use a diagnostic it does not know exists.

Pass with `-Dp2w.<name>=<value>` on the JVM the conversion runs in.

## The list

| flag | file |
|---|---|
| `p2w.anchorkeep` | DocxWriter.java |
| `p2w.ascent` | DocxWriter.java |
| `p2w.autoEm` | DocxWriter.java |
| `p2w.census` | DocxWriter.java |
| `p2w.clipDbg` | DocxWriter.java |
| `p2w.colMinBand` | PdfToWord.java |
| `p2w.colMinFill` | PdfToWord.java |
| `p2w.colMinLeft` | PdfToWord.java |
| `p2w.colMinLines` | PdfToWord.java |
| `p2w.colcharge` | DocxWriter.java |
| `p2w.debugAnchors` | DocxWriter.java |
| `p2w.debugClip` | PdfToWord.java |
| `p2w.debugCols` | DocxWriter.java |
| `p2w.debugFlow` | DocxWriter.java |
| `p2w.debugGaps` | DocxWriter.java |
| `p2w.debugPin` | DocxWriter.java |
| `p2w.fitreserve` | DocxWriter.java |
| `p2w.lineRule` | DocxWriter.java |
| `p2w.nocol` | PdfToWord.java |
| `p2w.noshave` | DocxWriter.java |
| `p2w.osplit` | PdfToWord.java |
| `p2w.ovf` | PdfToWord.java |
| `p2w.pagepos` | DocxWriter.java |
| `p2w.recut` | PdfToWord.java |
| `p2w.row` | PdfToWord.java |
| `p2w.softmask` | PdfToWord.java |
| `p2w.traceLines` | DocxWriter.java |
| `p2w.wrapgate` | DocxWriter.java |
| `p2w.zganchor` | DocxWriter.java |
| `p2w.zgfloor` | DocxWriter.java |

## WHICH OF THESE CHANGE OUTPUT IS NOT ESTABLISHED, AND THIS FILE DOES NOT PRETEND TO KNOW

An earlier draft of this file classified them into diagnostics and tunables by looking for parseFloat /
parseInt near each reference. That was wrong: `ascent`, `ovf`, `wrapgate` and others read a value through
a helper a few lines further away, so the check missed them and would have told a run that setting
`p2w.ovf` cannot change a document. A wrong classification is worse than none, so the list stands and the
classification is withdrawn until it is measured.

To settle it, for each flag: set it to a non-default value, convert one document, and diff the
`word/document.xml` against the same document converted without it. A byte difference means it changes
output. That is 30 conversions, and it is the only honest way to answer the question.

## Until then

Assume every one of them can change output. Never set any in a run without a full-corpus regression check:
the engine on HEAD must be the engine the corpus was measured on.

## The two that matter most

`-Dp2w.census=<file>` writes, per page, how many lines each of eight writers wrote, how many assignments
moved the flow's y, and `rewind` / `rewindWorst` / `rewindWho` - an assignment that moved the flow's y UP
the page. Displacement counted exactly, in points, with the writer's name. Nothing in p2w-bench or
benchmarks passes it.

`-Dp2w.debugFlow` writes, per page, flowTw / budgetTw / overTw - how far the page overran its budget. The
extra page on 21 documents is that number.
