# content-missing-partly-replaced / A2 - why `parasOfLines` yields 0 for the page-7 heading cell

Asked: on `041122-Account_Opening_Form.pdf`, the page-7 heading cell holds six `Line` objects
       ("Annexure-1" / "Income-tax Rules, 1962" / "FORM NO.60" / "[See second proviso to rule
       114B]" / the two proviso lines) in `pieces`, yet the .docx emits ONE welded `w:p` with
       `w:ind w:left="9452"`. Which condition inside `parasOfLines` rejects those six lines, and
       which of the six lines' properties (size, face, colour, y-gap, x, rule proximity) makes it
       fail?

Claim: **None of them.** No property of the six lines is looked at, because the six lines never
       reach `parasOfLines` for that cell. `parasOfLines` is handed an EMPTY list and returns at
       `PdfToWord.java:8000` (`if (ls == null || ls.size() < 2) return none;`). The mechanism is a
       column index-space mismatch introduced by the "drop the columns nobody wrote in" trim:
       `PdfToWord.java:8682-8703` rebuilds `cells`, `faces`, `firstX`, `firstY` and `colours`
       through `keep.get(k)` and then sets `cols = keep.size()` (:8702), but the parallel
       `List<List<List<Line>>> pieces` (:8640, filled at :8651) is **not** re-indexed. The
       consumption loop (:8751-8756) therefore reads `pieces.get(rr).get(cc)` with a TRIMMED `cc`
       into an UNTRIMMED third index. On this document the grid is 4 columns wide with
       `keep = [1, 2, 3]`, so every kept column reads the pieces of the column to its LEFT:

         - the cell that DISPLAYS original column 2 (the heading column, trimmed `cc = 1`) reads
           `pieces[1][1]`, which holds 0 lines -> `ls.size() < 2` -> `none` -> the cell falls back
           to the welded string path, which is the `w:ind w:left="9452"` paragraph you see;
         - the six heading lines ARE turned into six `CellPara` - by the cell that displays
           original column 3 (trimmed `cc = 2`), i.e. the EMPTY cell to the right of the heading,
           which reads `pieces[1][2]`. So the six paragraphs are not lost by a predicate, they are
           written one column to the right of their own text, and the heading text is emitted
           twice: welded in its own cell and split into six paragraphs in its neighbour.

       The exact predicate that "rejects" the six lines for the heading cell is line 8000, and it
       fires because `ls.size() == 0`, not because of any line property.

Evidence (MEASURED, this run, HEAD 6dbb50e, engine built with `tools/p2w-bench/build-engine.sh`):

   1. Baseline reproduction. `java ConvertAll` on the single PDF -> 9 pages, 480 paragraphs. The
      page-7 table (`<w:tbl>` #18, 24 rows x 3 cells) row 1 cell 1 is one `w:p`, `w:ind
      w:left="9452"`, text "Annexure-1 Income-tax Rules, 1962 FORM NO.60 [See second proviso to
      rule 114B] Form for declaration ..." - the six lines welded by single spaces.

   2. Instrumented COPY of `PdfToWord.java` (a copy outside the repo; no engine change committed),
      printing at the consumption loop: grid geometry, every original column's piece count and
      `parasOfLines` result, and the per-line values. Output, verbatim:

        [DBG grid] colsOrig=4 keep=[1, 2, 3] cols=3 rows=24 pieces rows=24 pieces cols row0=4
        [DBG cell] rows=24 cols=3 colsOrig=4 rr=1 cc=1 pieces.get(rr).size=4
                   linesReadByParasOfLines=0 cp.size=0 welded=Annexure-1 Income-tax Rules, 1962 ...
        [DBG origcol 0] n=0 parasOfLines=0
        [DBG origcol 1] n=0 parasOfLines=0
        [DBG origcol 2] n=6 parasOfLines=6
           text="Annexure-1"                                  y=34.852905 x=513.5645 right=566.95447 size=1.0 face=DRVFMI+Effra-Bold    bold=true  colour=2760822 glyphs=10
           text="Income-tax Rules, 1962"                      y=48.352905 x=253.69452 right=355.70453 size=1.0 face=REAQAG+Effra-Regular bold=false colour=2760822 glyphs=22
           text="FORM NO.60"                                  y=60.352905 x=276.2145 right=333.18454 size=1.0 face=EIMQAG+Effra-Regular bold=false colour=2760822 glyphs=10
           text="[See second proviso to rule 114B]"           y=72.352905 x=232.43451 right=376.9645 size=1.0 face=EIMQAG+Effra-Regular bold=false colour=2760822 glyphs=33
           text="Form for declaration to be filed by ..."     y=89.852905 x=46.304504 right=564.9044 size=1.0 face=REAQAG+Effra-Regular bold=false colour=2760822 glyphs=120
           text="account number and who enters into ..."      y=101.852905 x=144.8845 right=464.51443 size=1.0 face=REAQAG+Effra-Regular bold=false colour=2760822 glyphs=72
        [DBG origcol 3] n=0 parasOfLines=0

      `pieces` row 1 has FOUR columns (`pieces.get(rr).size=4`) while `cols` is 3: the third index
      was never trimmed. `parasOfLines` on the very same six lines returns **6**, not 0 - the six
      lines pass every predicate in the function.

   3. The six paragraphs are present in the wrong cell. Parsing both .docx files with
      ElementTree and comparing `w:tc` paragraph counts, the page-7 table's row 1 differs exactly
      as the mechanism predicts (flat cell index = document order):

        flat 251  tbl 18 row 1 cell 1   BEFORE n=1  ['Annexure-1 Income-tax Rules, 1962 FORM NO.60 ...']  (welded)
                                       AFTER  n=6  ['Annexure-1', 'Income-tax Rules, 1962', 'FORM NO.60', ...]
        flat 252  tbl 18 row 1 cell 2   BEFORE n=6  ['Annexure-1', 'Income-tax Rules, 1962', 'FORM NO.60', ...]  (WRONG cell, empty on the page)
                                       AFTER  n=1  ['']

      Cell 252 is the empty third column of that row: it is carrying the heading's six paragraphs.

   4. Controlled experiment (copy only, one line): in the consumption loop of the copy, map the
      column back through `keep` before indexing pieces -
      `int srcCol = keep.get(cc);` instead of `cc` - rebuild, convert. Result: the heading cell
      emits six `w:p` (one per line, `Annexure-1` carrying `<w:b/>`, the rest not, all
      `w:ind w:left="9452"`, `w:before` 210/246/216/216/326/216 twips, `w:line="24"`), and cell
      252 goes back to a single empty paragraph. Nothing else about the page changed. 14 of the
      document's 632 table cells change paragraph count under that one-line remap, in 7
      before/after pairs, i.e. the defect is not page-7-specific and is not about these six lines:
      every trimmed grid shifts its whole paragraph matrix one column left.

Code, read at HEAD 6dbb50e (`app/src/main/java/com/kavopdf/app/engine/PdfToWord.java`):

  - `pieces` declared :8640-8645, sized by the UNTRIMMED `cols`, filled at :8651
    (`pieces.get(r).get(c).add(line)` with `c = band(xs, cx)` from the untrimmed `xs`).
  - the trim that shifts the index space :8681-8703; note :8690-8694 read through `keep.get(k)`
    for the five matrices and :8702 sets `cols = keep.size()`; `pieces` is absent from both.
  - the consumption loop :8751-8756 reads `pieces.get(rr).get(cc)` with the trimmed `cc`.
  - the other consumer of `parasOfLines` (:9096-9099) is NOT affected: it iterates
    `for (List<Line> cell : pieces)` positionally with no `keep` trim in that path.

## (1) `parasOfLines` in full, with line numbers (`PdfToWord.java:7998-8028`)

```
 7998|    private static List<Table.CellPara> parasOfLines(List<Line> ls) {
 7999|        List<Table.CellPara> none = new ArrayList<>();
 8000|        if (ls == null || ls.size() < 2) return none;
 8001|        List<Line> sorted = new ArrayList<>(ls);
 8002|        Collections.sort(sorted, new Comparator<Line>() {
 8003|            @Override
 8004|            public int compare(Line a, Line b) {
 8005|                if (Math.abs(a.y - b.y) > 2f) return Float.compare(a.y, b.y);
 8006|                return Float.compare(a.x, b.x);
 8007|            }
 8008|        });
 8009|        List<Table.CellPara> out = new ArrayList<>();
 8010|        Table.CellPara cur = null;
 8011|        float curY = Float.NaN;
 8012|        for (Line ln : sorted) {
 8013|            String piece = ln.text == null ? "" : ln.text.trim();
 8014|            if (piece.isEmpty()) continue;
 8015|            if (cur != null && Math.abs(ln.y - curY) <= 2f) {
 8016|                cur.text = cur.text.isEmpty() ? piece : cur.text + " " + piece;
 8017|                if (!Float.isNaN(ln.right) && ln.right > cur.right) cur.right = ln.right;
 8018|                continue;
 8019|            }
 8020|            cur = new Table.CellPara(piece, fontOf(ln.glyphs), sizeOf(ln.glyphs),
 8021|                    colourOfLine(ln.glyphs), boldOf(ln.glyphs), italicOf(ln.glyphs),
 8022|                    visibleX(ln.glyphs, ln.x), ln.right, ln.y);
 8023|            curY = ln.y;
 8024|            out.add(cur);
 8025|        }
 8026|        if (out.size() < 2) return none;
 8027|        return out;
 8028|    }
```

The function has exactly four decision points, and only two of them can discard anything:

  - :8000  `ls.size() < 2`          - too few lines handed in;
  - :8014  `piece.isEmpty()`        - a line with no text is skipped;
  - :8015  `Math.abs(ln.y - curY) <= 2f` - merge into the current paragraph;
  - :8026  `out.size() < 2`         - fewer than two baselines produced.

`size`, `face`, `colour`, `bold`, `italic`, `x`, `right` and rule proximity are **not** predicates
here at all - they are only copied into the `CellPara` at :8020-8022, and `x` is used only for
ordering (:8006). No threshold on any of them exists to be crossed.

## (2) The predicate that rejects, quoted

    app/src/main/java/com/kavopdf/app/engine/PdfToWord.java:8000
        if (ls == null || ls.size() < 2) return none;

and it fires with `ls.size() == 0` because of

    app/src/main/java/com/kavopdf/app/engine/PdfToWord.java:8753
        List<Table.CellPara> cp = parasOfLines(pieces.get(rr).get(cc));

where `cc` is an index into the TRIMMED grid (`cols = keep.size()`, :8702) and
`pieces.get(rr)` is still indexed by the UNTRIMMED grid (`pieces cols row0=4` against `cols=3`).
The trim at :8682-8703 remaps `cells`, `faces`, `firstX`, `firstY`, `colours` through
`keep.get(k)` and does not remap `pieces`; `pieces` is the only one of the six per-cell matrices
that the loop at :8751-8756 reads by column index.

## (3) Per-line values for that cell, as the instrumented copy prints them

Grid: `rows=24`, `colsOrig=4`, `keep=[1, 2, 3]`, `cols=3`. The heading lines live in original
column 2, row 1 (the column that displays as trimmed cell `cc = 1`):

| # | text | y (pt) | x (pt) | right (pt) | size | face | bold | colour | glyphs |
|---|------|--------|--------|-----------|------|------|------|--------|--------|
| 1 | Annexure-1 | 34.852905 | 513.5645 | 566.95447 | 1.0 | DRVFMI+Effra-Bold | true | 2760822 | 10 |
| 2 | Income-tax Rules, 1962 | 48.352905 | 253.69452 | 355.70453 | 1.0 | REAQAG+Effra-Regular | false | 2760822 | 22 |
| 3 | FORM NO.60 | 60.352905 | 276.2145 | 333.18454 | 1.0 | EIMQAG+Effra-Regular | false | 2760822 | 10 |
| 4 | [See second proviso to rule 114B] | 72.352905 | 232.43451 | 376.9645 | 1.0 | EIMQAG+Effra-Regular | false | 2760822 | 33 |
| 5 | Form for declaration to be filed by an individual or a person (not being a company or firm) who does not have a permanent | 89.852905 | 46.304504 | 564.9044 | 1.0 | REAQAG+Effra-Regular | false | 2760822 | 120 |
| 6 | account number and who enters into any transaction specified in rule 114B | 101.852905 | 144.8845 | 464.51443 | 1.0 | REAQAG+Effra-Regular | false | 2760822 | 72 |

(`size` is `sizeOf()`'s max non-empty glyph size; all six report 1.0, and the emitted runs are
`<w:sz w:val="2"/>`. `colour` 2760822 = 0x2A2076, the same on all six.)

Read against the four decision points:

  - **y-gap**: consecutive gaps are 13.5, 12.0, 12.0, 17.5, 12.0 pt. Every one is `> 2f`, so
    :8015 never merges and :8026 sees six paragraphs. `parasOfLines` on these six lines returns
    **6** - printed, `[DBG origcol 2] n=6 parasOfLines=6`.
  - **empty text**: none of the six is blank; :8014 skips nothing.
  - **size / face / colour / bold**: 1.0 / mixed (Bold on #1 only) / identical / mixed - none of
    these is a predicate, so none of them can be the answer.
  - **x / right**: wildly different (46.3 to 566.95) because the block is centred on three
    different widths. `x` is only the secondary sort key at :8006; it cannot reject.
  - **rule proximity**: `parasOfLines` never sees a rule, a cell rectangle or a table - its whole
    input is `List<Line>`. There is no rule-proximity test anywhere in it.
  - **list length**: `linesReadByParasOfLines=0`. This is the only one that fires.

## (4) The single binding condition

`PdfToWord.java:8000` - `if (ls == null || ls.size() < 2) return none;` - with `ls.size() == 0`.

Upstream of it, the binding defect is the un-remapped `pieces` third index: :8702 changes `cols`
to `keep.size()` while `pieces` keeps `colsOrig` columns, so :8753 reads
`pieces[rr][cc]` where the cell it is filling is `cells[rr][keep[cc]]`. Because `keep` is strictly
increasing and drops at least column 0 here, `keep[cc] > cc` for every kept column, and the
paragraph matrix is shifted one (or more) columns LEFT of its text: the heading cell is fed the
pieces of the column to its left (0 lines -> welded fallback), and the heading's own six
paragraphs are handed to the cell on its right.

## (5) Ruled out, and how

  - **y-gap / baseline merging (:8015).** Ruled out by measurement: the six baselines are 12-17.5
    pt apart, and `parasOfLines` on the six lines returns 6. Also ruled out by the .docx: the six
    paragraphs exist, one per line, in the neighbouring cell.
  - **The 2-line floor at :8026.** Cannot fire on six paragraphs; and the paragraphs are emitted,
    just elsewhere.
  - **Empty-piece skip (:8014).** All six have text (10-120 glyphs).
  - **size / face / colour / bold / italic disagreement.** Not predicates. Verified by reading
    :7998-8028: they are only constructor arguments at :8020-8022. A cell whose six lines differ in
    face (Bold vs Regular) and agree in colour would be *supported* by the model, not rejected -
    and the remap run writes them with `<w:b/>` on the first line only.
  - **`x` / right-alignment / `visibleX`.** Only a sort key and a copied field. The six x values
    span 46-567 pt and still produce six paragraphs when the right list is read.
  - **Rule proximity / cell width / `w:ind w:left="9452"`.** `parasOfLines` has no geometry beyond
    the lines' own y/x; the 9452-twip indent is the *consequence* of the welded single-paragraph
    path using `firstX` of the cell, not a cause. (The indent is unchanged at 9452 after the
    remap - the six paragraphs carry the same `w:ind`.)
  - **`filled < 2` (:8667) and `keep.size() < 2` (:8681).** The table survives both: it has 24
    rows x 3 kept cells with text in most rows.
  - **The other `parasOfLines` consumer (:9096-9099).** Reads `pieces` positionally, no `keep`
    trim on that path, so it does not carry this mismatch - which is why the defect is confined to
    the ruled-grid path and not to every cell in the document.
  - **`shapeParas` (:8750).** It shapes `t.paras` to the trimmed `(rows, cols)` and is called
    before the fill loop, so it is consistent with the trimmed index space; the mismatch is
    between that trimmed space and `pieces`, not between `shapeParas` and the loop.
  - **Writer-side loss.** Ruled out by the controlled remap: with the same `DocxWriter`, the same
    table emits six `w:p` in the correct cell. Nothing downstream drops cell paragraphs.

## (6) What would prove me wrong

  1. A run in which `pieces.get(rr).get(cc)` holds six lines for the heading cell (i.e.
     `linesReadByParasOfLines=6`) and `parasOfLines` still returns 0. That would put the failure
     back inside :8000-8026 and falsify the index-space claim. My instrument prints exactly this
     counter, so it is a one-run check.
  2. A grid on which `keep.size() == cols` (nothing trimmed) and a multi-line cell STILL emits one
     welded `w:p`. If such a grid exists on this or another document, there is a second mechanism
     and this finding is incomplete. On this document both ruled grids are trimmed
     (4 -> 3 on page 7, 8 -> 7 on the later table), so this document cannot supply the negative
     control; another document with an untrimmed multi-line ruled grid would.
  3. A remap that does NOT restore the six paragraphs. I ran it (`srcCol = keep.get(cc)`) and it
     did: six `w:p`, correct bold, correct `w:ind`, and the 14 shifted cells in 7 pairs returned
     to their own rows.
  4. Proof that the heading lines are NOT in `pieces` column 2 but somewhere else and are lost
     before the fill loop - contradicted by the dump: `[DBG origcol 2] n=6`.

## Notes for whoever picks this up

  - The blast radius is every ruled grid the column trim touches, not this cell: 14 of 632 table
    cells on this document change paragraph count under the one-line remap, in 7 before/after
    pairs. The visible symptom is two-fold - a multi-line cell welded into one paragraph with
    space-joined text and the cell's own `firstX` as its indent, AND the same text re-emitted as
    per-line paragraphs inside the cell to its right (here an empty cell, so the .docx shows the
    Annexure heading twice).
  - The mechanism predicts which other documents change: any document whose ruled grid drops at
    least one empty column AND holds a cell with two or more baselines in a kept column at or
    right of the first dropped column. It predicts no change on documents whose grids are not
    trimmed (`keep.size() == cols`).
  - This finding deliberately proposes no patch; the one-line remap above is a *test*, applied to
    a copy, and it is not committed.
  - Observation, not part of the claim: this page's runs carry `<w:sz w:val="2"/>` (1 pt) and the
    heading `sizeOf()` reports 1.0 for every line, while the source sets the heading at ~11 pt.
    That is a separate size-reporting question and is not what this file is about.

Status: complete - mechanism named, measured, and falsified-and-restored in a copy.
