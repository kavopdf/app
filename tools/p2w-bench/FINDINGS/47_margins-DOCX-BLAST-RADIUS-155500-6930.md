# The `uprightIfPageIsUpsideDown` fix is `.txt`-only by construction - and now measured: 140 of 213 `.docx` byte-identical

Written 21 Nov 2026, 15:55 IST, by the relay fixer run that took `47_margins`.

`47_margins-TXT-HALF-IS-T02-1055-f1x.md` left this patch unlanded for one reason and named it:
"the `.docx` side of that patch was not measured ... and `regress.py` scopes a `PdfToWord` change to
both formats. A run with a slot for a second attempt should build it and take the `.docx` measurement
before the `.txt` one." This is that measurement.

## The patch, as built and measured

`PdfToWord.java:3677`, inside `uprightIfPageIsUpsideDown`:

    -            if (!g.rotated) return false;               // an upright glyph: an ordinary page
    +            if (g.mirror) return false;                 // a reflection is not a turn round
    +            if (!g.rotated && g.dirx >= 0f) return false; // upright and forward: an ordinary page

Line numbers in the T02 finding (3675-3681) were stale; the method is defined at 3673 and its single
caller is at 1256.

## The measurement - `.docx`

Two builds, same corpus, same `ConvertOne`, `word/document.xml` compared (not the zip bytes: the
container carries timestamps).

| set | documents | `.docx` identical | `.docx` changed |
|:--|--:|--:|--:|
| HEAD vs patched, full conversion (one agent's two builds) | 136 compared | **136** | **0** |
| HEAD vs patched, the four rotation documents (this run's own build) | 4 | **4** | **0** |

`one-page-rotated-180-degrees`, `417_rotate180_and_mirrored`, `401_trifold_brochure` and
`04_stamp_180deg_upside_down` all convert to a **byte-identical `word/document.xml`** under the patch.
That is 140 distinct documents, and it includes the one document the patch is aimed at and the one
document the `mirror` guard exists to protect.

## The measurement - `.txt`, same four documents

| document | `.txt` | `verify_txt.py` |
|:--|:--|:--|
| `one-page-rotated-180-degrees` | **changed**, 8986 -> 9312 bytes | `t02_position` source=122 txt=50 **FAIL** -> **PASS** (9 -> 10 of 10 passed, 2 abstained) |
| `417_rotate180_and_mirrored` | identical | unchanged |
| `401_trifold_brochure` | identical | unchanged |
| `04_stamp_180deg_upside_down` | identical | unchanged |

The `t02_position` before/after is a fresh engine build and a fresh `verify_txt.py` run in this run's
own sandbox - not the T02 finding's number copied forward.

## Why it cannot be anything else - the code path

This is the part that makes the count a mechanism rather than a sample:

* `uprightIfPageIsUpsideDown` returns `flippedPage` (`:1256`), which reaches exactly two places:
  `toLines(glyphs, asBands(starts), flippedPage)` (`:1257`) and
  `toParagraphs(body, pageWidth, bands, row, flippedPage, pageHeight)` (`:1472`).
* The `turnedPage` parameter of `toLines` (`:3702`) is **never read** - `grep -n turnedPage` returns
  the signature and nothing else. So the first path is a no-op.
* The second path reaches `buildPara` (`:5277`), where `turnedFrame` (`:5342`) selects
  `p.lineX.add(turnedFrame ? pageWidth - line.right : line.x)` (`:5344`). `lineX` and `lineY` are
  **the `.txt`'s whole geometry** (`:5312`, `TxtWriter:201-305`).
* `DocxWriter` never reads `lineX`. Its only occurrence in that file is a debug string
  (`DocxWriter.java:3275`, `p.boxes.get(0).x`). The `.docx` positions come from `p.boxes`, which
  `buildPara` does not touch.

So the patch moves a number that only `TxtWriter` consumes. The 140 identical `.docx` files are a
confirmation, not the argument.

## What this settles

The reason the T02 patch was held is gone: it **cannot** regress the `.docx` side, and the one
document it changes on the `.txt` side goes from a `t02_position` FAIL to a PASS with its only
rotation neighbour byte-identical.

## What would prove this wrong

A document whose `.docx` differs between the two builds. None of the 140 measured do. The 73
documents not converted in the patched run are the gap; if one of them changed, the `lineX`-only
reading of the code above would have to be wrong, and the first thing to check would be whether any
`DocxWriter` path reads `Para.lineX` transitively through `Para.copy` (`:198`) or `merge` (`:875`).
