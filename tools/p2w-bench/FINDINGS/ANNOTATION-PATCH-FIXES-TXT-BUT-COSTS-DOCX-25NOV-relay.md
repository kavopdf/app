# The annotation patch: txt PASS reproduced, and a docx position cost that was not in the record

**25 Nov 2026 · fixer slot 19:17 (relay) · engine `8449650b7b903356` (patched), `8039ea9b058bfbce` (HEAD, unpatched)**

## What was taken from the last run

The 17:16 report's FIRST ATTEMPT was the annotation `/Contents` hoist:
`PdfToWord.pageText()` (it is `readPage()`, `PdfToWord.java:884`) hoists every annotation's
`/Contents` as a body paragraph at `:956`, guarded only by `flat.contains(...)` against the content
stream. `tools/p2w-bench/PATCHES/600-annotation-runs-subtype-25NOV.patch` already existed, unapplied,
carrying both halves: the `drawnByAppearance(apDrawn, ...)` guard and the FreeText/Stamp subtype filter.

## The txt half is reproduced, on one engine, patch the only difference

Converted with `ConvertOne` twice, same box, same corpus PDF, only `PdfToWord.java` differing:

```
600_reviewed_invoice_with_annotations   before: pages=1 paragraphs=14
                                        after : pages=1 paragraphs=12
```

`verify_txt.py <source.pdf> <out.txt>` (note the argument order - source first):

```
BEFORE  8/12 applicable, 7 passed, 4 abstained  FAIL   t12_word_invention source=785 txt=83
AFTER   8/12 applicable, 8 passed, 4 abstained  PASS
```

The whole `.txt` diff is two lines, both gone:

```
< Rate for HSN 8536 confirmed with PO.                                  the note: nothing draws it
< Checked against PO 4471. Quantity on line 3 raised from 20 to 25.     the FreeText, a second time
```

So the patch closes one `.txt` document, and the finding that recorded it
(`ANNOTATION-CONTENT-IS-NOT-BODY-TEXT-25NOV.md`) is correct on the txt side.

## The population, measured by bytes rather than by the tool being changed

`corpus-changed.py --record` after rebuilding the whole corpus on the patched engine:
**1 changed of 213, 0 never measured** - `600_reviewed_invoice_with_annotations`, and nothing else.
That is the strongest form of the claim: 212 documents are byte-identical outputs, so no score of
theirs can differ, and the one that moved is the one that was measured.

## What the record did not say: the docx position cost

`benchmarks/p2w.py` on the patched tree (`P2W_ENGINE_SRC=/scratch/work/CS`) measured 600 as:

| | share1 | share2 | share3 | share5 | share10 | median_pt | p90_pt | max_pt | text_recall |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| committed row (engine `9e2b3e4d`, 13:47) | 73.32 | 69.97 | 67.94 | **51.68** | 48.96 | 11.04 | 48.96 | 62.88 | 100.0 |
| patched tree | 65.47 | 61.30 | 58.72 | **38.97** | 38.97 | 6.72 | 32.64 | 37.44 | 100.0 |

The two removed paragraphs sat at the **top** of the page (`1,2d0` in the txt diff), so removing them
moves the whole body up and every pixel-overlap share falls. `median_pt`, `p90_pt` and `max_pt` all
improve, `text_recall` is unchanged at 100 and `chars_missing` stays 0 - the ink is not lost, it moved.

**That is a docx regression by the gate's own statistic (`share5` -12.71), and rule 3 refuses it.**
This is why the patch could not land, and it is the reason the 10:10 run's patch was never applied:
not the txt, the flow.

## The confound, stated

The `before` column is the committed RANKING row, measured on engine `9e2b3e4d7869ea86`. The `after`
column is this tree. Any engine drift between 13:47 and now is inside that difference, so the -12.71
is **not yet proved to be the patch's cost**. The txt half above *is* clean (one engine, patch only).
To settle the docx half: revert the patch, convert 600 with HEAD `8039ea9b`, measure it, and compare
against the patched run of the same day. One document, two conversions.

## The next move this suggests

The cost comes from *where* the hoisted paragraphs are emitted, not from removing them. A hoist
appended **after the page's own blocks** rather than at the top would let the note and the duplicate
be dropped without moving a single glyph, and would then be flow-neutral on the docx side. That is a
different patch from this one and it has not been written.

## State left behind

Engine reverted (`git checkout`), `out/` recompiled to HEAD, 600 reconverted into the corpus so the
corpus is again the unpatched engine's output. The patch file is untouched in `PATCHES/`.
