# The U+200B at x=291 y=797 is a RULE: a hairline-wide floating shape, written by `DocxWriter.shape()`

Document: `18_centred_heading_left_body_txtpos` (1 page, A4 595.28 x 841.89 pt).
Engine: `origin/main` as cloned at the start of this run (rules are still `<w:drawing>`; there is no
`ruleAsBorder` / `pBdr` anywhere in `app/src/main/java/com/kavopdf/app/engine/`).

## The answer, in one paragraph

The construct is a **rule** - a hairline-wide, fill-only floating `wps` shape - and it is **not** a
table cell border and **not** a paragraph border. It is written by `DocxWriter.shape()`:
`app/src/main/java/com/kavopdf/app/engine/DocxWriter.java:2736` opens the run that carries
`<w:drawing>` (the carrier `<w:p>` opens at line 2733, the paragraph closes at line 2777, and the
method itself is declared at line 2726). `shape()` is reached from line 2235,
`if (!s.consumed) shape(sb, s, ctx);`.

**No Java line writes U+200B.** That is tested, not read: the emitted `word/document.xml` for this
document contains zero `U+200B`, and so do the emitted `.docx` files of all 211 corpus documents
(211/211 checked). The character is Google's own artefact for a floating drawing it refused to
import: it drops the shape and leaves a zero-width placeholder in the carrier paragraph. That is the
mechanism already established in `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`, and this run confirms it
on the emitted XML rather than on the render.

## The selecting condition

Two conditions, one in each file, and neither of them is a border test.

1. `PdfToWord.attachShapes()`, `PdfToWord.java:7089`:
   `boolean rule = Math.min(s.wPt, s.hPt) < 3f;`
   A surviving shape that is thin in one axis is a rule; it is dropped only when a table owns that
   edge (`if (rule && ownedByTable(...)) continue;` at line 7097). This document has no table, so
   nothing is dropped here.
2. `DocxWriter.shape()`, `DocxWriter.java:2726`, has **no** border branch on `origin/main`. Every
   `Shape` that reaches it - rule or band - is written as a page-anchored `<w:drawing>`.
   `isHairline()` (`DocxWriter.java:2799`, `min(w,h) <= 1.5f && max(w,h) > 2f`) is consulted only at
   line 2763, to decide whether a fill-only hairline must keep its fill; it does **not** route the
   shape anywhere else.

So the property that selects the drawing path is simply "the page drew a hairline rule and the shape
pass kept it". The rule's own colour, width, y or page plays no part in choosing the emitter - which
is why a rule at the head of the page and a rule at the foot of the page are written by the same
line.

## What the emitted document actually contains (built and inspected)

```
cd /scratch/work/CS/tools/engine-verify
CP="out:libs/aar/classes.jar:libs/aar/assets:libs/bcprov.jar:libs/bcpkix.jar:libs/bcutil.jar"
java -cp "$CP" ConvertOne /scratch/work/flat/18_centred_heading_left_body_txtpos.pdf /scratch/work/o18
cd /scratch/work/o18 && unzip -oq 18_centred_heading_left_body_txtpos.docx -d u
```

Then `word/document.xml` was parsed paragraph by paragraph (Python, `re.findall(r'<w:p[ >].*?</w:p>')`).
Counts over the whole part:

| construct | count |
|---|---:|
| `<w:tbl>` | 0 |
| `<w:tcBorders>` | 0 |
| `<w:pBdr>` | 0 |
| `<w:txbxContent>` | 0 |
| `<pic:pic>` | 0 |
| `<w:drawing>` | **2** |
| `<wp:anchor` | 2 |
| U+200B | **0** |
| distinct `w:ind w:left` values | 0, 1120, 2047 twips (= 0, 56.0, 102.35 pt) |

Two of the 24 paragraphs carry a drawing, and nothing else in the document is a border or a table.
The two drawings are:

| para | posOffset H | posOffset V | extent | fill | line | hairline? |
|---|---:|---:|---|---|---|---|
| p22 | 711200 EMU = 56.00 pt | 1389380 = **109.40 pt** | 6137605 x 15239 = 483.28 x **1.20 pt** | `0F1F52` | `<a:ln><a:noFill/>` | yes (1.20 <= 1.5, 483.28 > 2) |
| p23 | 711200 EMU = 56.00 pt | 10079228 = **793.64 pt** | 6137605 x 6350 = 483.28 x **0.50 pt** | `BFBFBF` | `<a:ln><a:noFill/>` | yes (0.50 <= 1.5, 483.28 > 2) |

Both are `wps:wsp` with `a:prstGeom prst="rect"`, `behindDoc="1"`, `wp:positionH/V relativeFrom="page"`
- the output of `shape()`, not of `picture()` (2395), `anchoredPicture()` (2429) or `anchor()`
(5401, which is the one that would carry `wps:txbx` / `w:txbxContent`). Confirmed by the counts above:
0 `txbxContent`, 0 `pic:pic`.

### The exact fragment (paragraph 23, the foot rule)

```xml
<w:p><w:pPr><w:snapToGrid w:val="0"/><w:spacing w:beforeAutospacing="0" w:afterAutospacing="0"
 w:before="0" w:after="0" w:line="1" w:lineRule="exact"/><w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/>
 </w:rPr></w:pPr><w:r><w:drawing><wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0"
 relativeHeight="100034466" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">
 <wp:simplePos x="0" y="0"/><wp:positionH relativeFrom="page"><wp:posOffset>711200</wp:posOffset>
 </wp:positionH><wp:positionV relativeFrom="page"><wp:posOffset>10079228</wp:posOffset></wp:positionV>
 <wp:extent cx="6137605" cy="6350"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>
 <wp:docPr id="100002" name="Shape 100002"/><a:graphic><a:graphicData
 uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"><wps:wsp><wps:cNvSpPr/>
 <wps:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="6137605" cy="6350"/></a:xfrm>
 <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="BFBFBF"></a:srgbClr>
 </a:solidFill><a:ln><a:noFill/></a:ln></wps:spPr><wps:bodyPr anchor="t" anchorCtr="0">
 <a:noAutofit/></wps:bodyPr></wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r></w:p>
```

Note what is **absent**: no `w:ind`, no `w:pBdr`, no `w:jc`, no text run. The paragraph exists only to
carry the anchor, and the anchor is the only thing in it - which is exactly the shape of construct
that Google replaces with a zero-width placeholder.

## Where the rule came from in the PDF

`pymupdf` on the source page shows the page draws exactly two things, both **stroked** lines with no
fill:

```
[56.0, 110.0, 539.28, 110.0]  w=483.28  type=s  color=(0.06,0.12,0.32)   -> 0F1F52
[56.0, 793.89, 539.28, 793.89] w=483.28 type=s  color=(0.75,0.75,0.75)  -> BFBFBF
```

The engine carries each as a rule and emits it as a filled band whose thickness is the stroke width
and whose fill is the stroke colour (hence `solidFill` + `a:ln noFill` on a line the page stroked).
That is the construct `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md` describes; nothing new is emitted for
the second rule.

## Which of the two the y=797 anchor is - and why y=797 is not either rule's own y

The two carrier paragraphs carry `w:before="0"`, so their position is decided by **flow**, not by the
`wp:positionV` inside them. Summing the emitted spacing for paragraphs 0..21:

```
sum of w:before  = 15840 twips = 792.0 pt
sum of w:line    =   278 twips =  13.9 pt
flow after p21   = 16118 twips = 805.9 pt
```

So both anchors are laid out at the foot of the page, at y ~ 806 pt, one 0.05 pt apart - while one of
the rules they carry belongs at y = 110. This is the same number the first `pBdr` attempt reported
("both landed at the foot of the page (y 807 and 808)" in `RULES-PBDR-IMPLEMENTATION.md`), which is an
independent confirmation of the flow arithmetic. Google's own line metrics put its placeholder at
y = 797 rather than 806; that 9 pt is Google's layout, not the engine's.

The x is not derivable from the engine at all: no `w:ind` in this document is 291 pt (the only values
are 0, 56.0 and 102.35 pt), and a text anchor at the paragraph's left indent would sit at x = 0.
291 pt is within 7 pt of the page centre (297.6) and of the rule's own centre (56.0 + 483.28/2 =
297.6), so the horizontal placement is Google's placement of the dropped object, not a coordinate the
`.docx` specifies.

Consequently the anchor at (291, 797) cannot be assigned to rule #1 or rule #2 by its y: the two
carrier paragraphs are stacked on the same flow line at the foot of the page, so **both** rules'
anchors land there. What the y=797 does tell us, and it is the useful part, is that the anchor's
position is the *flow* position of an empty carrier paragraph and has nothing to do with the rule's
own y.

## The part of the brief I have to contradict

The brief says the leftover anchor "is NOT produced by the two rules the pBdr change converted", i.e.
that a third construct exists. **I could not find one, and the emitted document says there is none.**

* The document has exactly two `<w:drawing>` elements and both are rules from `shape()`.
* Both satisfy the documented `ruleAsBorder` test verbatim: `isHairline` true, `|h| <= |w|`, and
  `rgb >= 0` (`fillRgb` is `0F1F52` and `BFBFBF`, `lineRgb` is -1).
* There is no table, no cell border, no paragraph border, no text box and no picture in the part - so
  the other two candidate constructs in the brief are absent by count, not by inference.

So either the measured `pBdr` build was made from a tree that differed from this one, or the "1 of 2
lost" in `RULES-PBDR-FIX-MEASURED.md` is a **positional** loss (a border drawn at y 807/808 where the
page has one at y 110) rather than a construct that survived. The repo does not say which, and I did
not rebuild the `pBdr` variant (the patch is not in the tree and the engine was not to be edited), so
I cannot test it. What I can state as tested is that on `origin/main` this document contains no
construct at that location other than the two `shape()` drawings.

## The mechanism, as one sentence that predicts other documents

> Any document in which a page draws a hairline rule that no table owns gets that rule emitted as a
> page-anchored floating `<w:drawing>` by `DocxWriter.shape()`, and Google Docs drops the shape on
> import and leaves a U+200B in the empty carrier paragraph - so the rule vanishes, one extra
> character appears, and the anchor surfaces at the *flow* position of the carrier paragraph rather
> than at the rule's own y.

Measured corpus-wide support for the prediction (all 211 PDFs converted with `ConvertAll`, then every
`word/document.xml` parsed):

```
docx scanned                                   211
docx whose document.xml contains U+200B          0     <- no engine line writes it
total <w:drawing>                             7905
rule-shaped drawings (min(w,h)<=1.5pt,
  max>2pt, <a:ln><a:noFill/>)                 4721
documents with >= 1 rule-shaped drawing        183
```

183 of 211 documents carry at least one construct of exactly this kind, which is the right order of
magnitude for the 28-document `32_stroke_lines` population in `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`
(that count is the documents where the lost rule is also *counted* as a stroke line; many of the 183
carry rules that sit on top of a table or off the measured area). A fix has to change the emitter for
all 4,721 of those shapes, not for a special case at y=797.

## Provenance of each claim

| claim | how obtained |
|---|---|
| no `U+200B` literal in the engine | `grep -rn '200B\|200b\|8203\|ZWSP' app/src/main/java/` - 0 hits in `DocxWriter.java`/`PdfToWord.java` (**reading**) |
| line numbers of the writer | `grep -n` on `DocxWriter.java` (**reading**) |
| 0 `pBdr`, 0 `tbl`, 0 `tcBorders`, 0 `txbxContent`, 2 drawings, 0 U+200B, indents 0/1120/2047 | `ConvertOne` + `unzip` + parse of `word/document.xml` (**built and inspected**) |
| the two rules' geometry and paint | same XML; source PDF via `pymupdf.get_drawings()` (**built and inspected**) |
| the anchor's y is the flow position | sum of the emitted `w:before`/`w:line`, cross-checked against the 807/808 recorded in `RULES-PBDR-IMPLEMENTATION.md` (**computed from the emitted XML**) |
| 211/211 docx contain no U+200B; 183 documents / 4721 rule-shaped drawings | `ConvertAll` over `/scratch/work/flat` then a parse of every `word/document.xml` (**built and inspected**) |
| Google drops the drawing and leaves U+200B | **not re-measured here** - taken from `RULES-ARE-DRAWINGS-GOOGLE-DROPS-THEM.md`, which measured it through Google |

The engine was not edited. The only file this run writes to the repository is this one.
