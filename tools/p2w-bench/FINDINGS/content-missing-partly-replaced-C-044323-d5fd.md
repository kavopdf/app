# content-missing-partly-replaced / C - the engine code path

Asked: `041122-Account_Opening_Form.pdf` page 7, table row 2 cell 2 holds SIX distinct source
       text lines (the heading block: `Annexure-1` right-aligned at x 513.6, then
       `Income-tax Rules, 1962`, `FORM NO.60`, `[See second proviso to rule 114B]`, and the two
       lines of `Form for declaration to be filed by an individual or a person ...` /
       `account number and who enters into any transaction specified in rule 114B`). The .docx
       carries them as ONE `w:p` welded by spaces, with no `w:br` and no per-line paragraphs,
       even though `parasOfLines(pieces.get(rr).get(cc))` at `PdfToWord.java:8753` is supposed
       to give that cell its own paragraph per source line. Why does that path not fire - is it
       (a) `parasOfLines` returning fewer than 2 entries, (b) the cell's `pieces` list never
       receiving the lines, (c) `DocxWriter` ignoring `t.paras`, or (d) something else?

Answer: **(d) something else.** The path DOES fire and `parasOfLines` DOES return 6 - but the six
       paragraphs are attached to the cell one column to the RIGHT of the cell that owns the
       lines, because `pieces` is never carried through the empty-column trim that remaps every
       other per-cell array. Cell 2 therefore keeps its welded string (its `pieces` entry reads
       an empty column, `parasOfLines` returns 0, the `if (cp.size() >= 2)` guard is false), and
       cell 3 - a 456-twip sliver - is written with the six paragraphs that belong to cell 2.

Claim (mechanism, with lines): `buildTables` fills `pieces` for all `cols` columns of the ruled
       grid at `PdfToWord.java:8645-8651` (`pieces.get(r).get(c).add(line);`). Immediately after,
       the pass drops columns nobody wrote in: `keep` is built at `:8672-8680` and, when
       `keep.size() < cols` (`:8682`), `cells`, `faces`, `firstX`, `firstY` and `colours` are
       re-indexed through `keep` and rebound at `:8697-8701`; `colX` is remapped the same way at
       `:8720` (`int src = c < keep.size() ? keep.get(c) : c;`). **`pieces` is not remapped and is
       not rebound** - it keeps its pre-trim width and its pre-trim column indices. `t.shapeParas`
       at `:8750` then builds `t.paras` with the TRIMMED `cols`, and the loop at `:8751-8755`
       indexes the UNTRIMMED list with the trimmed index: `parasOfLines(pieces.get(rr).get(cc))`.
       For this table `keep == [1, 2, 3]`, so trimmed cell `cc` is original column `keep[cc] =
       cc + 1`, and `t.paras[r][cc]` receives the lines of the cell one column to the LEFT of the
       cell it is written into. Row 1 (the heading row): `cc = 1` reads `pieces[1][1]`, original
       column 1, which holds nothing -> 0 -> guard false -> cell 2 keeps the welded string;
       `cc = 2` reads `pieces[1][2]`, original column 2, which holds the six lines -> 6 CellParas
       -> written into cell 3. `DocxWriter` honours `t.paras` correctly
       (`DocxWriter.java:6379-6408`, `parasAt(r, c).size() >= 2` -> one `w:p` per CellPara,
       `continue` past the string path), so the defect is entirely the `pieces`/`keep` desync.
       Note the comment already sitting at `DocxWriter.java:6410-6425` measures THIS cell as the
       welded one ("page 7, row 2, cell 2: tcW 10636 twips, inset 9452 ... twenty-seven lines"),
       i.e. the writer's own record of the cell agrees with what the .docx shows.

Evidence - MEASURED, this run, engine built at HEAD, instrumented copy of the sources outside
       the clone (repo engine files untouched):

```
cd /scratch/work/app && bash tools/p2w-bench/build-engine.sh          # engine built - ConvertAll ready (42s)
mkdir -p /scratch/work/one && cp benchmarks/realworld/041122-Account_Opening_Form.pdf /scratch/work/one/
E=/scratch/work/app/tools/engine-verify
CP="$E/out:$E/libs/aar/classes.jar:$E/libs/aar/assets:$E/libs/bcprov.jar:$E/libs/bcpkix.jar:$E/libs/bcutil.jar"
JH=/scratch/work/.p2w-jdk/jdk
cd $E && JAVA_HOME=$JH PATH=$JH/bin:$PATH \
  JAVA_TOOL_OPTIONS="-XX:CompressedClassSpaceSize=64m -XX:MaxMetaspaceSize=200m" \
  java -Xmx700m -cp "$CP" ConvertAll /scratch/work/one /scratch/work/one-out
# -> 041122-Account_Opening_Form  pages=9  paragraphs=480  ...  (the .docx is 157442 bytes)
```

       1. The .docx itself (`word/document.xml`, unzipped) has ONE table on page 7 (TBL#18,
          24 rows, 3 `gridCol` widths 363 / 10636 / 456 twips) and it reads:

```
  r0 c0 nparas=1
  r0 c1 nparas=1
  r0 c2 nparas=1
  r1 c0 nparas=1
  r1 c1 nparas=1  Annexure-1 Income-tax Rules, 1962 ...
  r1 c2 nparas=6  Annexure-1 | Income-tax Rules, 1962 | FORM NO.60 | [See second proviso to rule 114B] | Form for declaration to be ...
  r2 c0 nparas=1  1
  r2 c1 nparas=1  First Name Middle Name Surname
  r2 c2 nparas=1
```

           Row 2 cell 2 (`r1 c1`) is the welded `w:p` with all six lines and no `w:br`; row 2
           cell 3 (`r1 c2`) carries the same six lines as SIX separate `w:p`. The six
           paragraphs exist in the file - in the wrong cell.

       2. Instrumented copy (a copy of `app/src/main/java/com/kavopdf/app/engine` plus
          `tools/engine-verify/{stubs,ConvertAll.java}` under `/scratch/work/instr`, compiled
          against the same libs), printing `colsBeforeTrim`, `colsAfterTrim`, `keep`,
          `pieces.get(0).size()` and, per cell of the first three rows, the welded string,
          `pieces.get(rr).get(cc).size()`, `parasOfLines(...)` and `t.paras.get(rr).get(cc).size()`:

```
DBG table top=0.0 rows=24 colsBeforeTrim=4 colsAfterTrim=3 keep=[1, 2, 3] piecesCols=4
DBG  cell r0 c0 welded=null pieces=0 parasOfLines=0 t.paras=0  (origCol=1)
DBG  cell r0 c1 welded=null pieces=0 parasOfLines=0 t.paras=0  (origCol=2)
DBG  cell r0 c2 welded=null pieces=0 parasOfLines=0 t.paras=0  (origCol=3)
DBG  cell r1 c0 welded=null pieces=0 parasOfLines=0 t.paras=0  (origCol=1)
DBG  cell r1 c1 welded='Annexure-1 Income-tax Rules, 1962 FORM N' pieces=0 parasOfLines=0 t.paras=0  (origCol=2)
DBG  cell r1 c2 welded=null pieces=6 parasOfLines=6 t.paras=6  (origCol=3)
DBG  cell r2 c0 welded='1' pieces=0 parasOfLines=0 t.paras=0  (origCol=1)
DBG  cell r2 c1 welded='First Name Middle Name Surname' pieces=1 parasOfLines=0 t.paras=0  (origCol=2)
DBG  cell r2 c2 welded=null pieces=3 parasOfLines=0 t.paras=0  (origCol=3)
```

          (`pieces` in that dump is `pieces.get(rr).get(cc)`, i.e. the untrimmed array the buggy
          loop actually reads; `origCol` is `keep.get(cc)`, the column the cell really is.)
          `colsBeforeTrim=4`, `keep=[1,2,3]`, `colsAfterTrim=3`, `pieces` still 4 wide: trimmed
          cell 1 is original column 2, yet the loop reads `pieces[1][1]`. Cell 2's `pieces`
          entry reads 0 while cell 3's reads the six lines, and `t.paras` follows `pieces`, not
          the cell. `parasOfLines` returns 6 on those six lines - the function is fine.

       3. Intervention (the falsifier, run): patched ONLY the copy, changing `:8753` to read
          `pieces.get(rr).get(keep.get(cc))` (bounds-checked), rebuilt and re-ran:

```
DBG  cell r1 c0 welded=null pieces(own)=0 parasOfLines=0 t.paras=0  (origCol=1)
DBG  cell r1 c1 welded='Annexure-1 Income-tax Rules, 1962 FORM N' pieces(own)=0 parasOfLines=0 t.paras=6  (origCol=2)
DBG  cell r1 c2 welded=null pieces(own)=6 parasOfLines=6 t.paras=0  (origCol=3)
```

          and the emitted .docx, same extraction as (1):

```
===== one-out (HEAD)
  r1 c1 nparas=1  Annexure-1 Income-tax Rules, 1962
  r1 c2 nparas=6  Annexure-1 | Income-tax Rules, 1962 | FORM NO.60 | [See second proviso to rule 114B] | ...
===== instr-fix (pieces remapped through keep)
  r1 c1 nparas=6  Annexure-1 | Income-tax Rules, 1962 | FORM NO.60 | [See second proviso to rule 114B] | ...
  r1 c2 nparas=1
```

          One re-indexing moves the six paragraphs from cell 3 into cell 2 and empties cell 3.
          That is the whole mechanism, confirmed by changing it and watching the symptom move.

Ruled out:
       - **(a) `parasOfLines` returning fewer than 2 entries.** Measured: it returns 6 for this
         cell's six lines (`parasOfLines=6` in dump (2), and the six `w:p` in cell 3 of the
         shipped .docx are its output). `PdfToWord.java:7998-8037` also reads correctly: it
         sorts by baseline and merges only lines within 2 pt of each other, and these six are on
         six distinct baselines (y 22.6, 36.1, 48.1, 60.1, 77.6, 89.6 per PyMuPDF on page
         index 6).
       - **(b) `band()`/column assignment dropping or misrouting the lines.** The six lines are
         all in `pieces[1][2]` (original column 2) - the column whose cell carries the welded
         string. Nothing was dropped: `cells[1][2]` (original) holds all six welded, and
         `pieces[1][2].size() == 6`. `band()` (`:9622-9627`) did assign them to one column; the
         error is downstream of it, in which `pieces` entry the paragraph loop reads.
       - **(c) `DocxWriter` ignoring `t.paras`.** It does not: `DocxWriter.java:6379-6408` takes
         `parasAt(r, c)` and, when `size() >= 2`, emits one `w:p` per CellPara and `continue`s
         past the welded-string path. Cell 3 of the shipped .docx proves it - six `w:p` with
         distinct `w:before` values (24 / 246 / 216 / 216 / 326 ...) that could only come from
         `cellParaXml`. `parasAt` itself (`PdfToWord.java:346-353`) is a plain bounds-checked
         get and is not at fault.
       - Not the "empty cell" / `w:trHeight` path, not `recutPages`, not `rowTables`: the table
         reaches the writer with the right welded text in the right cell; only `t.paras` is
         shifted.

What observation would prove me WRONG:
       - If the instrumented dump printed `colsBeforeTrim == colsAfterTrim` (no trim, `keep`
         empty of interest) for this table, the index shift would not exist and the mechanism
         would be wrong. It prints 4 -> 3, `keep=[1,2,3]`.
       - If `pieces[1][2]` held 0 lines and cell 2's own `pieces` entry held the six, then the
         lines really were misrouted by `band()` and this file is wrong.
       - If the remap intervention left the six paragraphs in cell 3 (or moved something else
         and lost them), the shift is not the operative cause.
       - A second, independent falsifier: any OTHER table in this corpus that trims a column
         (`keep.size() < cols`) should show the same one-column-left displacement of its
         paragraph cells. If such a table is found where `t.paras` lands in the correct cell
         despite a trim, the claim is incomplete and the remap is not the only path.

Also worth knowing (side observation, not part of this mechanism): `buildTables` runs twice per
       page - `PdfToWord.java:1016` on `rawLines` and `:1270` on the split `lines` - so the
       instrumented dump prints the identical block twice. Only one of the two tables reaches the
       .docx.

Confidence: high. The mechanism is read at file:line, observed in a built engine's output, and
       confirmed by an intervention that moves the symptom.

Status: complete
