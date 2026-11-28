# `60_text_column_right_edge` reads a table row as a line — the instrument, not the engine

**28 Nov 2026 · fixer · engine `a05b20eb05fe0fc8` · 3 documents measured through Google before and
after, plus a 62-document census by a research agent · KEPT**

## What I believed

The check's docstring argues that the widest line in a left-edge cluster *is* the column's right edge
"on a column with any full line at all". That holds when a line is a line of text.

## What I measured

**It does not hold when one MuPDF "line" object carries several table cells — and Google's PDF export
puts a whole table row in one line object.**

`341_shipping_manifest`, landscape 841.89 × 595.28. The source draws the failing row as four separate
line objects. The Google export draws it as **one** line object spanning `429.75 → 513.36`, whose spans
are `34.73` (429.75→447.20), a `U+200B`, `Corrugated cartons` (453.00→511.10) and a `U+200B`. The check
took that object's `x1` as the left-hand column's edge and reported **+66.36 pt of overrun**, against a
threshold of 470.45. The source's own ink at that x is **0.18 pt** away: 513.18 vs 513.36.

`56_table_indented_from_margin`: reported overrun **+100.63 pt**; the source's own ink is 3.34 pt away
(507.29 vs 520.63, the difference being the trailing space Google appends).

The engine writes **no right edge at all**, so there was no engine number to be wrong: all 62 failing
`.docx` carry `w:pgMar w:right="0"` (text area = the paper's), 61 of 62 carry `w:ind w:right="0"`, 53 of
62 carry no `w:jc` anywhere, and tab stops are left stops only. This was never (a).

## What is now true

`verify_google.py`'s `page_lines()` splits a line at any internal gap of **2 pt or more** and returns
the box of each run. Everything downstream — `columns()`, `edge()`, the constants, the predicate — is
untouched.

**The split point is measured, not tuned.** Over the 62 Google exports there are 5,843 gaps between
consecutive spans inside a "line": 5,603 under 0.5 pt (kerning inside a run), then 169 at 3–6 pt and 49
at ≥ 6 pt, with only 8 in 1–2 pt and 14 in 2–3 pt. The band 0.5–2 pt is empty, so any threshold in it
gives the same answer.

**The source side is unaffected**, because a source line's internal gaps are all under 2 pt — the source
draws each cell as its own line object. Verified on the three documents below.

## The measurement, through Google, before and after

| document | shipped instrument | patched instrument | shipped `gverify` | patched `gverify` |
|:--|:--|:--|:--|:--|
| `salary-slip-factory-wages` | over=1, **FAIL** | **PASS** | 46/47 | **47/47 CLEAN** |
| `table-with-merged-cells` | over=1, **FAIL** | **PASS** | 46/47 | **47/47 CLEAN** |
| `341_shipping_manifest` | over=1, **FAIL** | **PASS** | 46/47, fails 18+60 | 46/47, fails **18 only** |

The "shipped instrument" column is from `60-right-edge-instrument.py`, an independent script that
reimplements the shipped predicate and the split side by side — not from the file I edited. Both columns
score the *same* Google export PDFs, downloaded from the same Drive export.

## The census

A research agent measured all **62** failing documents through Google on this engine. Every stored
verdict reproduced. Result of the split:

    52  unchanged
    10  over -> PASS
     1  over -> under (still failing: 360_restaurant_menu, +101.13 -> -30.60)
     0  pass -> fail

No document can go pass → fail, because a split can only **shrink** a box: `rg` can only decrease, which
moves an `over` failure towards pass and an `under` failure further under (still a failure).

## Which documents become CLEAN: 2

`salary-slip-factory-wages` and `table-with-merged-cells`, both of which failed `60` and nothing else.
Neither has a competing column complaint: `62_table_columns` and `66_table_cell_width` pass on both.

`classpick.py --leverage` prices `60_text_column_right_edge` at **23.63** clean documents; that figure is
`sum(1/len(failed))` over the 62, fractional. The split recovers **4.82** of it and 2 real documents.
The ledger's 23.63 was never a document count and should not be read as one.

## The other half of the 62, which this does NOT fix

**35 of the 62 fire `under`, and the cause is font substitution, not the column.** The engine names
`DejaVuSerif`/`DejaVuSans`; Google has neither and substitutes Arial, which is 12–20 % narrower at the
same point size. Measured on the widest source line matched to the render line with the *same words*:

    313  538.63 -> 480.14  0.878     321  538.61 -> 443.43  0.802     370  538.62 -> 442.59  0.800
    302  543.74 -> 478.09  0.872     310  538.63 -> 456.78  0.830     340  549.77 -> 479.91  0.867

The renderer had *more* room than the source used (text area 595.30 against a column edge at 538.6), so
a narrower column cannot explain it. **This is a finding, not a fix:** the engine must not name a face
Google does not have, and that is an engine change measured against a different check (`53_embedded_faces`
prices the same population at 1.3). It is the next run's lead, not this run's.

## What would prove this wrong

A document that goes pass → fail under the split (none in 62); a source PDF whose own lines contain a
≥ 2 pt internal gap, which would make the split shrink the *source* edge and could turn a pass into a
fail; or a live Google export where a table row is already drawn as one line per cell.

## Residue

- 3 probe Google Docs created and deleted (`1ST9hzNFU4UTjRodvorCpdr1PbCeKd-0sSbD4ub45GWo`,
  `1NZOrCUzjXxtygaLEIVv2rQo-jb7s3n-_ruQqUI58qOA`, `156VFyP1T5hZyGCuB6xUs5EN4pT52vaj082Fujxk1kD8`).
- A research agent opened a public branch `probe/18-displacement-28nov` on `kavopdf/app` holding six
  synthetic probe `.docx`. **Not deleted** — the brief forbids deleting a branch, so it is recorded here
  and in `BLOCKERS.md` for whoever owns it.
