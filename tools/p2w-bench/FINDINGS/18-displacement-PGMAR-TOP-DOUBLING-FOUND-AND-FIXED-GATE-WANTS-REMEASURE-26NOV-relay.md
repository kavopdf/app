# The `w:pgMar w:top` patch's three-document regression is a DOUBLING, it is fixed, and the gate now refuses only on the re-measure

**26 Nov, relay slot 06:48.** Engine built, corpus converted (213/213), `regress.py --check` run.
Nothing was landed. `app/` is reverted to HEAD at the end of this run; the whole change is
`patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch`.

## 1. The contradiction in the two 26 Nov findings is resolved: `401_trifold_brochure` doubles

`18-displacement-diagnosis-26NOV.md` §5.3 could not say whether the patch causes the three-document
regression. It does, and the mechanism is the one that finding guessed from the diff. Measured here,
unpatched vs patched, `w:pgMar w:top` and the first `w:before` of `word/document.xml`:

| document | base pgMar / first `w:before` | patched, patch as published | sum |
|:--|:--|:--|--:|
| `401_trifold_brochure` | 0 / 1790 | **1190 / 1790** | **2980** vs 1790 |
| `601_fillable_admission_form` | 0 / 1230 | 1230 / 0 | 1230 (identity) |
| `416_many_tiny_pages` | 0 / 1790 | 1790 / 0 | 1790 (identity) |
| `412_page_labels_roman` | 0 / 1227 | 1227 / 0 | 1227 (identity) |

`401`'s body opens with a `w:tbl`, so the sheet's first *paragraph* lives inside a cell: the table's
spacer paragraph consumed `ctx.newPage` before it was written, `pageFirstBeforeTw()` never fired, and
the margin was added on top of an untouched 1790 tw. The page's top gap is counted twice. That is
sufficient to explain the regression with no claim about either renderer, which is what §5.3 asked for.

## 2. The fix, and why it is safe by construction

Two guards, both in the patch file:

1. `sectionTopTw()` now reads **only the page's first block** and returns 0 unless that block is a
   non-pinned `Para` with text, or a `Box` with text - i.e. unless the construct that lands at the top
   of the sheet is the one `pageFirstBeforeTw()` subtracts from. A page opening with a table, a shape or
   a pinned paragraph writes `w:pgMar w:top="0"`.
2. The final `sectPr` claims the margin only when the emitted body actually opens with `<w:p`
   (`sb.indexOf("<w:body><w:p") >= 0`), which is the same predicate read off the bytes rather than the
   model.

Both are identities when they fire: zero margin means every byte is what the unpatched engine wrote.

**Measured after the fix** (`ConvertOne`, same corpus PDF, same JDK):

| document | result |
|:--|:--|
| `401_trifold_brochure` | **byte-identical** to the unpatched engine |
| `601_fillable_admission_form` | **byte-identical** to the unpatched engine |
| `416_many_tiny_pages` | pgMar 1790 / first `w:before` 0 - the intended move, unchanged by the guard |
| `412_page_labels_roman` | pgMar 1227 / first `w:before` 0 - the intended move, unchanged by the guard |

`601` and `401` are two of the three documents the corpus gate refused on 26 Nov. `newsletter-3col-header-footer`
is the third; its body opens with a paragraph and it carries pgMar 1200 with first `w:before` 0, so it is
not doubled - it was not re-scored here and its status is **unmeasured, not cleared**.

## 3. What the corpus gate says now

All 213 documents converted with the patched engine (engine `f81978c9a5499201`), then:

```
docx: no document worse than baseline
google-safe : no construct Google ignores has spread
txt: out of scope - scope.py proved this change cannot move it
ENGINE CHANGED (docx): table measured on 9e2b3e4d7869ea86, the tree is c3714267bf15e71f
             An unmeasured change is not a pass. Re-measure, then --stamp.
REFUSED. This commit would land a regression or an unmeasured engine.
```

**The doubling is gone: nothing is worse than baseline, on the LibreOffice proxy, across the whole
corpus.** The only remaining refusal is that the docx table was measured on the previous engine and a
corpus-wide re-measure does not fit in a slot - the same wall `BLOCKERS.md` already records for the
212-document re-score.

## 4. What the next run should do

1. Apply `patches/18-displacement-PGMAR-TOP-GUARDED-AGAINST-DOUBLING-26NOV.patch`, build, and run the
   corpus re-measure that produces the docx table.
2. Google-verify `416_many_tiny_pages` first: it was measured **40/42 -> 42/42 CLEAN** under the
   unguarded patch (`18-displacement-PGMAR-TOP-REMEASURED-26NOV.md` §3), and the guard does not touch
   it - its body opens with a paragraph. Then `401_trifold_brochure`, which the guard now makes
   byte-identical, so it must read exactly as baseline.
3. Do **not** re-derive the doubling. It is measured above.

## 5. One more measurement this run, from the first subagent

`16_right_aligned_amounts_txtpos` is **not** a row-pitch ramp. Its per-row dy is flat at +0.82 pt over
13 rows all declaring the same `w:trHeight 380`, and the document's own residual is the refused
table-gap spacer (4.65 pt declared, ~1.0 pt laid). RC3's row-ladder lever loses its best document;
RC1's spacer is present on it. The Google per-run series was not taken - the subagent's sandbox had no
Drive write path - so that verdict rests on the stored Google summary (med -1.6, worst 3.4) plus a
LibreOffice render, and it is recorded as a lead, not a proof.
