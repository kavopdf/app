# t09: the band arm reads 0 of 29, and the patch already sitting in FINDINGS is refuted twice

**Measured 26 Nov 2026, fixer slot 19:59.** Engine `025fe9deda5ac7b1` (this tree, `pod-prep.sh` warm:
213 corpus PDFs, JDK, `out/ConvertAll.class`). Every number below was computed here, in this pod,
against the converted corpus — nothing is copied from another run's report.

## Why this was worked

Two documents fail `t09_page_furniture` and nothing else in the `.txt` population of the same
shape: `041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled`, both `owed=29
present=125 FAIL` (live store `tools/p2w-bench/txt/RANKING-TXT.csv`). It is the carry-over from the
run before this one, and a patch for it was already written into
`FINDINGS/t09-FIX-band-scoped-present-and-no-one-char-keys.patch` and never landed.

## 1. The patch in FINDINGS cannot work: the `.txt` has no page separators

The patch recovers the band on the `.txt` side as *the first and last `FURNITURE_TXT_EDGE_LINES`
non-empty lines of each U+000C-delimited segment*. It carries a comment saying a unit test on a
synthetic three-page file caught a form-feed bug in that split.

On the real `.txt` the split finds **one segment**, because the writer emits no form feeds at all:

    python3 /tmp/armtest.py            # this run, both documents
    041122-Account_Opening_Form: owed=29 whole=125 ordinal3=0 segs=1
       per-key owed/whole/ordinal3: {'D': (8, 33, 0), 'Date': (3, 6, 0), 'M': (6, 45, 0), 'Y': (12, 41, 0)}

So the patch's band is the first and last three lines of a **5684-line file**, it holds none of the
29 owed occurrences, and the document would read **0 of 29** instead of 125 of 29. The synthetic
test passed because a synthetic file has form feeds; the corpus file does not. A unit test built
from the writer's intended output is not a test of the writer's actual output.

## 2. And the second half of the patch does not finish it either

The patch also drops one-character keys from the furniture population. Alone, with `present` left on
the whole file as it is today:

    elements left = {'Date': owed 3}     present (whole file) = 6     → FAIL, 6 vs 3

`Date` occurs three times in the band (one per date box on pages 0-2) and three times in the body (a
"Date" column header). Dropping the one-character keys does not remove that surplus and the band
restriction is the only thing that can — and §1 shows the band restriction as written cannot.

**A correct version needs both halves plus a real aligner**, i.e. each `.txt` line mapped to the drawn
line it came from so it can inherit that line's `y`. That is the align-then-band arm, it is a larger
change than the patch, and it was not landed here (see §4).

## 3. The "the .txt loses 21 values" claim is not established

`FINDINGS/T09-CALLS-FORM-VALUES-PAGE-FURNITURE-25NOV.md` refused this change on the ground that the
`.txt` loses seven `Y`, seven `D` and seven `M` against the PDF's own draw. The per-key counts do
reproduce — measured here with `verify_txt`'s own `_src_pages` and `_furniture_key`:

| key | drawn | in band | `.txt` |
|:--|--:|--:|--:|
| `Y` | 48 | 12 | 41 |
| `D` | 40 | 8 | 33 |
| `M` | 52 | 6 | 45 |
| `Date` | 6 | 3 | 6 |
| `Yes` | 53 | 3 | 53 |

But the two sides are **not the same population**, so the difference is not a loss. The PDF draws
`DDMMYYYY` as one `Tj` with letter-spacing (`1.45 Tc`), and `_src_pages` inherits PyMuPDF's per-glyph
line model, so the source side counts one drawn occurrence per *glyph*. The `.txt` side is
`Counter(_furniture_key(line))` over 5684 lines, of which **274 are single-character** — and those
are mostly letter-spaced words the writer exploded one character per line. `M`, `Y` and `D` in the
`.txt` are therefore counts of *letters inside exploded words*, not copies of the date box.

Two independent facts say the 21 are not missing text:

* `t01_word_accuracy` and `t04_structure` **pass** on this document (store row: `failed =
  t06_encoding t09_page_furniture t12_word_invention`, 10 applicable, 7 passed). A `.txt` that had
  dropped 21 real glyphs from a form would not pass both.
* the `.txt` is 5684 lines against 1193 source lines — the explosion is 4.8x, in the direction that
  *adds* single-character lines, not one that loses them.

So the 25 Nov file's fault 2 is a comparison of two populations, not a measurement of loss. Fault 1
(the check is asymmetric) stands and is what this run's §1 and §2 are about.

## 4. What was not done, and why

The align-then-band arm was measured by a sub-agent this run (band-restricted `present` = 29 = `owed`,
element for element, on both documents) but **its implementation was not reproduced here**, and an
instrument change that moves two documents needs the whole 213-document `.txt` table re-measured
before and after — a conversion pass that does not fit in the slot that was left. An unmeasured
instrument change is a guess, so it was not committed. The next run starts from: build the aligner,
then re-measure `restamp_txt.py --force` over all 213 and only then land it.
