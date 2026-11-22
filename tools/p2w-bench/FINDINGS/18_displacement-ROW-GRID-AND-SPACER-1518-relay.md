# 18_displacement — the row grid, the table spacer, and why fixing one alone makes a document worse

**22 Nov 2026 · relay fixer slot 14:18 → · every number a live Google round trip on this sandbox
(ConvertOne → Drive create-as-Google-Doc → export PDF → `verify_google.py` / `dy.py`) · every probe
Doc deleted after scoring, Drive root left empty**

Probe documents: `two-tables-stacked-with-no-gap` (1 page, 13 ruled rows, source pitch 18.40 pt) and
`mobile-bill` (1 page, 24 rows in two ruled blocks). Both fail only `18_displacement` at HEAD.

## 1. What Google does with a declared row height — measured, and it is a grid

A purpose-built probe (three pages, one table each, **nine identical rows per page**, so the pitch is
read to ±0.06 pt instead of the ±0.5 pt a rule-position read gives):

| declared `w:trHeight` | pitch Google laid | charge |
|--:|--:|--:|
| 17.00 | 18.00 | +1.00 |
| 17.40 | 18.00 | +0.60 |
| 17.80 | 18.75 | +0.95 |
| 18.20 | 18.75 | +0.55 |
| 18.60 | 19.50 | +0.90 |

    laid = 0.75 * (round(declared / 0.75) + 1)

Five points, one law, exact to the last digit: the declaration is snapped to the nearest 0.75 pt and
**one whole 0.75 pt quantum is added**. `hRule` does not enter it (`atLeast` and `exact` laid the same
pitch) and neither does the border weight (0.5 pt and 1.0 pt laid the same pitch).

It reproduces the three engine builds the 13:18 slot left behind, which that run read as "the charge
grows with the declaration and is not affine":

    18.00 declared -> 19.1 laid (its build 1)   law 18.75   [it measured mixed 360/380 rows: 18.75/19.5, mean 19.1]
    17.40 declared -> 18.0 laid (its build 3)   law 18.00   exact
    18.40 declared -> 19.5 laid (its build 2)   law 19.50   exact

**So 18.40 pt is not reachable by any single declaration.** The reachable ladder is 0.75 apart. That
part of the 13:18 finding stands; the "grows with the declaration" reading does not - it was the
0.75 pt quantum seen through a 0.5 pt rule-position measurement.

## 2. The diffusion — declaring so the error cannot accumulate

`18_displacement` charges a page per **run** (`|dy| > clamp(0.35*size, 1.5, 4.5)`), not cumulatively,
so what matters is never the pitch but the accumulated position. A declaration per row is therefore
chosen by error diffusion on the 0.75 grid: each row is declared so that the height laid so far is the
closest 0.75 multiple to the height the page has drawn so far. The laid height then never drifts more
than 0.375 pt from the page, however long the table. Implementation:
`patches/18-displacement-SPACER-BEFORE-plus-ROW-PITCH-DITHER.patch`.

## 3. Alone, it made two documents WORSE — and that is the useful part

| document | HEAD dy median / n_out | diffusion only | 
|:--|--:|--:|
| two-tables-stacked-with-no-gap | -4.66 / 55 of 72 | **-9.43 / 69** |
| mobile-bill | -6.73 / 100 of 112 | **-12.73 / 108** |

The reason is a compensation, and it is exact. On two-tables at HEAD the table's header row lands at
**dy -10.18** and the pitch error is **+0.7 pt/row** over 13 rows: the two cancel by the foot of the
table, where dy is -0.54. Removing the pitch error leaves the -10.18 step naked.

**The lesson is not "do not diffuse". It is that a pitch error can be cancelling a position error, and
a run that measures only the pitch will call the compensation the defect.**

## 4. The -10.18 pt step: the table spacer was a no-op in Google

The paragraph the engine writes before a table carried its height in `w:line=247` with `w:sz=2` and no
run. `calibrate.py` (10 Nov) measured that Google charges `w:line` as
`(w:line/240) * lineHeight(face, size)` — a 1 pt face is charged ~1.2 pt for a 12.35 pt gap. So every
table started ~10 pt above the page's rule. `w:before` is the construct Google honours exactly.

Moving the height to `w:before` with a hairline `w:line=1`: header dy -10.18 -> -0.5.

## 5. Both together — one document clean, one much closer

| document | before | after (spacer + diffusion) |
|:--|:--|:--|
| two-tables-stacked-with-no-gap | 41/42, n_out 55, med -4.66, span 10.31 | **42/42 PASS**, n_out **0**, med +0.05, span 3.34, rms 0.64 |
| mobile-bill | 41/42, n_out 100, med -6.73, rms 2.05 | 41/42, n_out **39**, med +2.35, rms 0.54 |

`mobile-bill`'s residual is **+2 to +5 pt low**, and it is the same construct over-correcting: it holds
two small spacers (128 and 124 tw, 6.4 and 6.2 pt) which were previously charged ~0 and are now charged
in full. That is the next lead in this class, and it is one build away.

## What is now true that was not

* The declared-to-laid row map is **`0.75 * (round(h/0.75) + 1)`**, a constant quantum, not a growing
  charge. Anything built on "subtract the charge" must subtract one quantum, not a per-row estimate.
* The table spacer in this engine **was invisible to Google**. Every ruled table in the corpus starts
  at the wrong y because of it, and that is a position error the pitch cannot fix.
* A document can fail `18_displacement` with a **near-perfect pitch** — mobile-bill's table body at HEAD
  has slope 0.0085 and a -6.7 pt block shift. The check must be read per run, never as a slope.

## What would prove this wrong

A second document where the spacer fix alone moves dy by more than the 10 pt it moved here (it would
mean the gap arithmetic is not general), or a document whose small spacers (< 200 tw) are charged
correctly at HEAD (it would mean the +2..+5 residual on mobile-bill is something else).
