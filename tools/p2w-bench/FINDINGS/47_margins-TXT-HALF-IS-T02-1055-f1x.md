# `47_margins` has no `.txt` half - the `.txt` analogue is `t02_position`, and 4 of its 5 documents are the instrument

**21 Nov, fixer run 07:58, subagent `684N7DBKF88E7AP7DZN6N2CWXZ` (partial: hit its time budget with the work done).**

`classpick.py` said "next run: the .txt half" of `47_margins`. That premise is wrong and it is worth
one line to kill: `verify_txt.py --list-checks` has 12 ids and `47_margins` is not one of them;
`grep -c 47_margins` returns **0** in `tools/p2w-bench/RANKING-TXT.csv`, `txt/RANKING-TXT.csv`,
`txt/CENSUS-TXT.csv` and `txt/RANKING-TXT-BASELINE.csv`. The `.txt` analogue of "a horizontal position
is wrong" is **`t02_position`**, which holds **5 documents**, not 14 or 26.

Measured by rebuilding the engine, converting all 213 documents to `.txt` (`-Dp2w.noDocx=true`) and
re-running `verify_txt.compare` over all 213 - the stored table reproduced exactly.

| document | unregistered | mechanism | engine defect? |
|:--|:--|:--|:--|
| `one-page-rotated-180-degrees` | 61 of 122 (50 %) | page turned 180 deg but its glyphs are not flagged `rotated`; the guard bails and the model x is mirrored | **yes** |
| `332_bom_on_drawing` | 11 of 52 | `.txt` verifier pairs repeated cell texts in encounter order; sorted pairing -> 52/52 | no |
| `price-list-2col-dense-right-aligned` | 35 of 252 | same pairing collision, 86 duplicate span texts ("Nos" 41x) -> 1 residual | no |
| `74_balance_sheet_indented_subitems` | 10 of 54 | engine already reads ink (73.40); the check reads the span's bbox (56.0) | no |
| `334_patent_document` | 10 of 32 | engine x equals the source x to the hundredth on 10 of 10; the check's fitted ruler is 9 % coarse | no |

**The one engine defect, with the measured diff and its blast radius.** `uprightIfPageIsUpsideDown`
(`PdfToWord.java:3675-3681`) returns false on the first glyph with `!g.rotated`; on this page the
glyphs come back `rotated=false, dirx=-1.0`, so the turn is never recognised. Two lines fix it -
`if (g.mirror) return false;` then `if (!g.rotated && g.dirx >= 0f) return false;` - and the `mirror`
guard is load-bearing: without it `417_rotate180_and_mirrored` page 2 (a true reflection) is flipped
and its correct x destroyed.

Measured over all 213: `one-page-rotated-180-degrees` 50 % -> **100 %**, `t02_position` failures
5 -> 4, documents failing any `.txt` check 27 -> 26, and **1 of 213** documents changed at all. The
only other pages carrying `dir == (-1,0)` spans are `401_trifold_brochure`, `417` and
`04_stamp_180deg_upside_down`, and all three are byte-identical after the patch.

**Not landed this run, deliberately:** the `.docx` side of that patch was not measured (the subagent
converted with `--noDocx`), and `regress.py` scopes a `PdfToWord` change to both formats. The diff,
the four numbers and the three named regression candidates are above; a run with a slot for a second
attempt should build it and take the `.docx` measurement before the `.txt` one.
