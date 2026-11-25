# A minimal-repro generator: four single-construct `.docx` files, and what they do and do not prove

**24 Nov 2026 · agent slot 23:05 · engine untouched (`90e9b03b`) · nothing in `app/src/main/java/` changed**

## 0. The claim, up front

`tools/p2w-bench/minimal-repro.py` builds four `.docx` files, each carrying exactly ONE construct, and
prints the OOXML it emitted and the construct count. Each file opens, parses, and is counted by
`google_safe.py`'s own `scan()`. Each is deterministic: two runs produce byte-identical files.

**None of them has been through Google Docs.** This sandbox has no Google access, so no repro here is
a verified reproduction of a Google failure. What is verified is the structure of the file, that a
renderer honours the construct, and - by simulation - that `verify_google.py` reads the construct's
absence as the target check's failure. Section 4 says per repro what could still make it unfaithful.

## 1. What was built, and where

    tools/p2w-bench/minimal-repro.py     the generator (this branch)

    python3 tools/p2w-bench/minimal-repro.py --list
    python3 tools/p2w-bench/minimal-repro.py --check 18_displacement
    python3 tools/p2w-bench/minimal-repro.py --all --render --simulate --out /scratch/work/repro

| flag | what it does |
|:--|:--|
| (default) | writes the `.docx`, prints the OOXML verbatim, the construct count, and `scan()` |
| `--render` | converts with LibreOffice and measures what the renderer did with the construct |
| `--simulate` | renders a second copy with the construct neutralised, scores the pair with `verify_google.py` |
| `--json` | the same, machine-readable |

The generator writes OOXML by hand rather than through `python-docx`, because the point of the file is
the bytes: a repro built by a library that silently adds a paragraph or a default border is not minimal
and nobody can see what it carries. The package is four parts (`[Content_Types].xml`, `_rels/.rels`,
`word/_rels/document.xml.rels`, `word/document.xml`) with fixed timestamps, and no `styles.xml` -
both LibreOffice 7.4 and python-docx open it, and the `document.xml` is 937-1872 bytes.

Every repro sets `w:pgMar` all zero on a 12240x15840 page, as the page-top probe did: with a non-zero
top margin, "Google dropped the gap" and "Google kept the margin" are the same measurement.

## 2. The four repros, and their exact OOXML

### 2.1 `18_displacement` / `before-page-top`

Construct: **one** `w:before` on the first paragraph after a hard page break. Path:
`w:document/w:body/w:p[2]/w:pPr/w:spacing/@w:before`. Asked: 1103 twips = 55.15 pt, the value
`bank-statement-5-pages` emits and the value the probe measured.

```xml
<w:p><w:r><w:t xml:space="preserve">P1MARK</w:t><w:br w:type="page"/></w:r></w:p>
<w:p>
  <w:pPr><w:spacing w:before="1103" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>
  <w:r><w:t xml:space="preserve">P2MARK</w:t></w:r>
</w:p>
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>
  <w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0" w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>
```

Construct count **1** (`w:before` attributes). `scan()` → `{"w:before-page-top": 1}`.

### 2.2 `32_stroke_lines` / `drawing-rule` — the failure candidate

Construct: a rule as a floating `w:drawing` / `wp:anchor`, a 300 x 2 pt filled rectangle with
`a:ln noFill` (a rule is a FILL on this corpus, not a stroke -
`FINDINGS/32_stroke_lines-FLOATING-CARRIER-DRAWS-BUT-STACKS-2050-f1x.md`). Path:
`w:document/w:body/w:p[2]/w:r/w:drawing/wp:anchor/a:graphic/a:graphicData/wps:wsp/wps:spPr`.
25400 EMU = 2 pt, 3810000 EMU = 300 pt, 1440000 EMU = 113.4 pt from the page top.

```xml
<w:p><w:r><w:drawing>
  <wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="1"
             behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">
    <wp:simplePos x="0" y="0"/>
    <wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>
    <wp:positionV relativeFrom="page"><wp:posOffset>1440000</wp:posOffset></wp:positionV>
    <wp:extent cx="3810000" cy="25400"/><wp:effectExtent l="0" t="0" r="0" b="0"/>
    <wp:wrapNone/><wp:docPr id="1" name="Rule 1"/><wp:cNvGraphicFramePr/>
    <a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
      <wps:wsp><wps:cNvSpPr/><wps:spPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="3810000" cy="25400"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:ln><a:noFill/></a:ln>
      </wps:spPr><wps:bodyPr/></wps:wsp>
    </a:graphicData></a:graphic>
  </wp:anchor>
</w:drawing></w:r></w:p>
```

Construct count **1** (`w:drawing`). `scan()` → `{"w:drawing": 1, "wp:anchor": 1}`.

### 2.3 `32_stroke_lines` / `cell-border-rule` — the control

Construct: a rule as a table cell's `w:top` border, **one side only**. Path:
`w:document/w:body/w:tbl/w:tr/w:tc/w:tcPr/w:tcBorders/w:top`.

One side and not all four is a deliberate correction to the brief: a full cell box is not an
*isolated* segment - each edge runs into the next at the corner - so `verify_google._rules(isolated=True)`
does not count it, and a repro built with four borders would carry a rule the check never asks about.
`w:tblBorders` are all `nil` and `w:tblCellMar` is zeroed so no default grid is added.

```xml
<w:tbl>
  <w:tblPr><w:tblW w:w="6000" w:type="dxa"/><w:tblLayout w:type="fixed"/>
    <w:tblBorders><w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/>
      <w:right w:val="nil"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>
    <w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>
      <w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>
  <w:tblGrid><w:gridCol w:w="6000"/></w:tblGrid>
  <w:tr><w:tc><w:tcPr><w:tcW w:w="6000" w:type="dxa"/>
    <w:tcBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/></w:tcBorders></w:tcPr>
    <w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">CELLMARK</w:t></w:r></w:p>
  </w:tc></w:tr>
</w:tbl>
```

Construct count **1** (`w:tcBorders`, one edge inside). `scan()` → **clean, no known-ignored
construct**. That is the result the pair needs: the control carries the rule with nothing
`google_safe.py` objects to, and the failure candidate carries the same rule with `w:drawing` on it.

### 2.4 `04_chars_missing` / `anchored-textbox`

Construct: one paragraph of text inside an anchored text box. Path:
`w:document/w:body/w:p[2]/w:r/w:drawing/wp:anchor/a:graphic/a:graphicData/wps:wsp/wps:txbx/w:txbxContent/w:p`.

```xml
<w:p><w:r><w:drawing>
  <wp:anchor ... behindDoc="0" ...>
    <wp:positionV relativeFrom="page"><wp:posOffset>1440000</wp:posOffset></wp:positionV>
    <wp:extent cx="2286000" cy="457200"/><wp:wrapNone/><wp:docPr id="2" name="TextBox 2"/>
    <a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
      <wps:wsp><wps:cNvSpPr txBox="1"/><wps:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/><a:ln><a:noFill/></a:ln></wps:spPr>
        <wps:txbx><w:txbxContent>
          <w:p><w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">TXBXMARK</w:t></w:r></w:p>
        </w:txbxContent></wps:txbx>
        <wps:bodyPr rot="0" wrap="none" lIns="0" tIns="0" rIns="0" bIns="0"/>
      </wps:wsp></a:graphicData></a:graphic>
  </wp:anchor>
</w:drawing></w:r></w:p>
```

`BODYMARK` sits outside the box on purpose: with only the box's text in the document, "the characters
are missing" and "the document is empty" are the same measurement, and a check that fails on an empty
document tells you nothing about the box. Construct count **1** (text-box bodies). `scan()` →
`{"w:drawing": 1, "wp:anchor": 1}`.

## 3. What was run, and what it said

Everything in this table was produced by running the tool in this sandbox.

| repro | construct count | `scan()` | LibreOffice 7.4.7.2 render | control: real vs real | simulated: real vs neutralised |
|:--|--:|:--|:--|:--|:--|
| 18_displacement | 1 | `w:before-page-top: 1` | 2 pages, `P2MARK` at **y = 58.1 pt** (asked 55.15) | **42/42 PASS** | **41/42**, fails **`18_displacement` only**, source=0 render=1 |
| 32 / drawing-rule | 1 | `w:drawing: 1`, `wp:anchor: 1` | 1 page, **1 isolated rule**, y 114.4, len 300.0, t 2.0 | **42/42 PASS** | **40/42**, fails `32_stroke_lines` **and** `14_filled_shapes`, source=1 render=1 |
| 32 / cell-border-rule | 1 | clean | 1 page, **1 isolated rule**, y 15.5, len 300.0, t 1.0 | **42/42 PASS** | **41/42**, fails **`32_stroke_lines` only**, source=1 render=1 |
| 04 / anchored-textbox | 1 | `w:drawing: 1`, `wp:anchor: 1` | 1 page, `TXBXMARK` **is in the text layer** | **42/42 PASS** | **39/42**, fails `04_chars_missing` (8 chars), `17_matched_runs`, `45_char_accuracy` |

Read it in three parts.

**The control column is the load-bearing one.** Each repro compared against itself passes all 42
checks. So nothing in these documents fails by accident, and any failure the simulated column shows is
caused by the one thing that was changed - not by the page margins, the fonts, or a missing style.

**The simulated column is a simulation.** The neutralised copy is rendered by LibreOffice with the
construct removed the way Google is *measured* to remove it (`w:before` at a page top set to 0; the
rule deleted; the box's text made non-text). It proves the construct is what the target check is
reading, and that the target check fires when it goes. It says nothing about Google: a LibreOffice
render that drops the rule is not evidence that Google drops it.

**The neutralised variant must change ONLY the construct, and this was got wrong first.** My first
version deleted the whole anchor paragraph for the drawing variant and the whole table for the border
variant. That moved the text one line, and the pair failed `18_displacement`, `04_chars_missing`,
`17_matched_runs`, `44_header_footer` and `45_char_accuracy` as well - a neutralised variant that
changes the flow is not a control, it is a second defect. Keeping the anchor paragraph (empty) and
keeping the table's cell and text, and removing only the border, took the border variant's simulation
from six failing checks to one.

### `google_safe.py scan()` on the generated files - the question that could be answered

| file | `scan()` |
|:--|:--|
| `18_displacement--before-page-top.docx` | `{"w:before-page-top": 1}` |
| `32_stroke_lines--drawing-rule.docx` | `{"w:drawing": 1, "wp:anchor": 1}` |
| `32_stroke_lines--cell-border-rule.docx` | `{}` - clean |
| `04_chars_missing--anchored-textbox.docx` | `{"w:drawing": 1, "wp:anchor": 1}` |

Yes: `scan()` counts the construct in every generated file that is supposed to carry one, and reports
the border variant clean. The scan is called by importing `google_safe` and calling its `scan()`, not by
re-implementing its patterns.

## 4. What could make each repro unfaithful

Stated per repro, because a repro that does not reproduce is worse than none: a patch "fixed" against
it would be believed for no reason.

**18_displacement.** (a) The failure is a *displacement between two renders*, so it needs a reference.
A hand-built `.docx` has no source PDF; the reference has to be the LibreOffice render, which is what
the original probe compared - but it means the repro measures "Google vs LibreOffice" while the check
on a corpus document measures "Google vs the source PDF". Where those two references differ, the repro
and the corpus are not the same question. (b) The magnitude is right (55.15 pt asked, and LibreOffice
honours it to within the line box) but the *shape* of the failure on a real document is a whole page
block moving, header included, with enough matched runs for the per-page budget to be evaluated. A
two-paragraph document has two runs on page 2 and the check fires on the tail clause
(`worst_here > 2.0`), not on the budget - so the repro tests a different clause of the same check.
(c) If the patch changes where `w:before` is emitted, this repro tests that; it cannot test whether the
*page fill budget* is charged correctly, which is the second half of the same defect
(`FINDINGS/18_displacement-page-top-before-DROPPED-105000-f1x.md`, "Second result").

**32_stroke_lines / drawing-rule.** **This is the one that is contested, and the repo's own data
contests it.** `verify_google.py:_rule_segments` is called with `pictures=True` for check 32 precisely
because Google exports an anchored shape as a **raster image at the shape's own geometry**, and on
22 Nov that reading took 16 documents from FAIL to 42/42
(`FINDINGS/32_stroke_lines-CHECK-BLIND-TO-RASTERISED-RULES-MEASURED-0610-f1x.md`). So when Google
rasterises the shape, the check finds the rule as an image band and this repro **PASSES**. It
reproduces a lost rule only if Google *drops* the shape rather than painting it, which happened on
`73_marksheet` (0 of 2 rules drawn) and not on `394_map_with_legend` (3 of 3 recovered as images). That
difference is document-dependent and nothing in this sandbox can decide which this file is.

A census run here, over the committed `benchmarks/gverify/*.json` joined to
`benchmarks/GOOGLE-PREDICT.json`: **182 of 191 scored documents PASS 32_stroke_lines**, and **163 of
those 182 carry `w:drawing`**; 9 fail it. So the sentence "a rule carried only as a floating
`w:drawing` has never passed 32_stroke_lines" - which is in `google_safe.py --predict`'s docstring and
in the brief - does not hold of the committed data at the document level. It may hold at the level of
an individual rule, which is what the check scores and what this census cannot see; but as written it
is a claim about documents that 163 documents contradict. Anyone pricing a patch against 32 from that
sentence should price it from the 9, not from 192.

**32_stroke_lines / cell-border-rule.** It is a control, so the unfaithfulness that matters is that it
might fail: if a renderer does not honour `w:tcBorders` here, the pair proves nothing and the
"drawing is worse than border" comparison is between two things that both fail. LibreOffice draws it
(1 isolated rule, 1.0 pt thick - the 0.5 pt `w:sz="8"` = 1 pt) and Google is measured to honour
`w:tcBorders` (`FINDINGS/32_stroke_lines-CELL-BORDER-HONOURED-1830-f1x.md`), but that finding is about
a cell border on a document that also has a table, not a one-cell table alone on a page.

**04_chars_missing / anchored-textbox.** (a) 04 is a character multiset test with zero tolerance, so
*any* defect that loses a single glyph anywhere also fires it - it is the easiest check in the 42 to
reproduce and the least informative about which construct caused a given document's failure. A patch
tested only against this repro is shown not to lose the text of one text box, and nothing more. (b) It
depends on the box's text reaching the *reference* text layer. LibreOffice puts it there (measured:
`TXBXMARK` in the text layer), and if a future LibreOffice did not, the repro would fire 04 with no
Google involvement at all - a false reproduction. (c) Real documents' boxes carry the page's actual
type in the page's actual face; whether Google rasterises a box is measured to be independent of its
contents, but the character count that comes back (8 here) is not the corpus's.

**All four.** The repro carries one construct and one page. Nothing here tests the interactions that
dominate the corpus: a page-top `w:before` **plus** a floating rule **plus** an anchored box on the
same page is what 15 documents look like, and the three co-occur. A patch that fixes each repro can
still leave every one of those documents failing.

## 5. Not run

* Any Google Docs upload, conversion or export. Not available in this sandbox. Every statement about
  Google in this document is quoted from `FINDINGS/` and labelled as such.
* `python3 benchmarks/p2w.py` and any full-corpus restamp: the corpus PDFs are not in this sandbox and
  a restamp is ~54 minutes by the pipeline's own record.
* `screen.py` on the repros: it screens corpus documents by name.
* Any engine build. `app/src/main/java/com/kavopdf/app/engine/` was not read for change and not
  modified; `git status` on that tree is clean.

## 6. What this changes for the next run

1. **The repros are only worth what a Google round trip says they are.** Four uploads, four exports,
   `verify_google.py` against each - that is the cheapest 10 minutes in the pipeline and it either
   turns this tool into a 5-second patch gate or deletes it. Until then a patch tested against a repro
   is a patch tested against a hypothesis.
2. **`32_stroke_lines` should be re-priced.** 9 of 191 documents fail it, not 36.
3. **The pair, not the file, is the instrument.** The drawing variant and the border variant carry the
   same rule and differ in one element; a patch that makes the drawing variant behave like the border
   variant has done the thing. That comparison is available in LibreOffice today, at no Google cost,
   and it is the only use of these files that does not depend on a Google measurement.
