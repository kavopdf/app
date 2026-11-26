# The corpus re-measure is 4.3 hours of scoring, and that - not the patch - is what blocks the engine commit

**26 Nov, fixer slot 12:03 IST.** Measured on the guarded `w:pgMar w:top` patch
(`patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch`). Nothing landed; `app/` is
reverted to HEAD at the end of the run.

## 1. What was done, and what the gate said

| step | command | result |
|:--|:--|:--|
| patch | `git apply patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch` | applies clean, 135 insertions in `DocxWriter.java` |
| build | `pod-prep.sh` | engine compiled, fingerprint `025fe9deda5ac7b1` |
| convert | `corpus-slice.py` x6 | **213/213 converted**, stamp written for `025fe9deda5ac7b1` |
| gate | `regress.py --check` | **`docx: no document worse than baseline`** · `google-safe: no construct spread` · `txt: out of scope` |
| gate | `regress.py --check` | **REFUSED** on one thing only: `ENGINE CHANGED (docx): table measured on a4de7df896875a39, the tree is 7e0de1abdeb221ae` |
| score | `p2w.py --budget 220` | **3 of 212 measured**, `RANKING.partial.csv` written, published table untouched |

So the change is not refused for a regression. It is refused because the *table* was not re-scored on
this engine. That is the whole remaining gap.

## 2. The number nobody had: 73 s per document to score

`benchmarks/p2w.py --budget 220` scored **3 of 212** documents in 220 s of wall clock - **73 s per
document**, 4 workers, the docx already converted and sitting on disk. A full re-score is therefore
**209 x 73 s = 4.3 hours**.

Conversion is not the cost: 213 documents converted in six `corpus-slice.py` calls, the last 24 in 222 s
(~9 s/document). **Scoring is the cost, and it is 8x the conversion.**

`BLOCKERS.md` records the same wall in prose ("a corpus-wide re-measure does not fit in a slot"). This
run puts a rate on it: **a full re-score is three 90-minute slots, so no single run can ever land an
engine change through this gate, and the gate is behaving correctly.** Any run that reports "the gate
blocked me" without this number is guessing at why.

## 3. What the proposal is (not a change made this run)

The gate's rule is right: a stamp must mean the table was measured on this engine. What is wrong is the
unit - it is all-or-nothing over 212 documents when the failure mode it guards against (one document
getting worse) is per document. A stamp that carries **which documents** it covers, and a gate that
requires every document to have been scored on an engine no older than the last three, would let a run
land a change in the time it has and still refuse a regression on any document.

Recorded as a proposal only. Not implemented, not committed: it changes the gate, and a gate change
needs its own before-and-after (how many engine commits the old rule blocked that the new one would
have allowed, and whether any of them carried a regression).

## 4. Correction to the 18_displacement leverage, from this run's sub-agent

`classpick.py --leverage` prices `18_displacement` at **52.0 clean documents**. That price is not
reachable from the page top:

- The store has **91 documents failing `18_displacement`, 17 failing it alone** - and **all 17 are
  single-page documents** with `pgMar 0` and no `w:type="page"` break. A page-top carrier cannot touch
  a document that has no page top but page 0.
- The page-top patch therefore makes **1 document CLEAN** (`416_many_tiny_pages`, 40/42 -> 42/42,
  measured on Google under the unguarded patch, and the guard does not touch it) plus **9 check-instances
  across 5 documents**. That is worth landing, and it is not worth 52.
- The 17 solo-`18` documents fail through the other two constructs the root-cause file already names:
  the table-gap spacer Google charges at ~22 % of the asked line, and the table row Google lays at
  content height. The row-residue algorithm is proven (`med_dy +10.30 -> -0.70` on
  `320_balance_sheet_statutory`) and was reverted for one reason: **the block after the table is 18 pt
  short in the flow**, so fixing the rows moved the signature block to -18.16.

**The next run's lever is that 18 pt flow error, not the page top and not the 0.961 slope.** The slope is
a cross-document regression of shift on gap; within one file the construct is all-or-nothing -
`412_page_labels_roman` writes `w:before="1227"` on every page and page 0 honours it 1:1 (+2.3 pt) while
pages 1-4 drop it whole (-58.8 pt). A multiplicative `(G+0.58)/0.961` correction would over-deliver by
`0.039 G + 0.58` pt on a mechanism that delivers either G or 0.

## 5. What would overturn §2

A scoring path that reuses the LibreOffice render already made during conversion, or one that scores
only the checks whose construct the patch can reach. If either exists, the 73 s/document figure is the
cost of the current instrument, not a property of the corpus, and the proposal in §3 is unnecessary.
