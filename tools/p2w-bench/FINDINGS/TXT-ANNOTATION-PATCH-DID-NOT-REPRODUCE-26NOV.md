# The txt annotation patch did not reproduce — applied, rebuilt, measured, reverted

A sub-agent reported that removing non-printing annotations from the txt model took the .txt corpus
from **204 clean to 205** (`600_reviewed_invoice_with_annotations` 7/8 → 8/8, 0 invented chars, no
regression on 204). It shipped a two-hunk patch to `PdfToWord.java` in the annotation path.

## It was applied and measured here, and it moved nothing

    git apply fix.patch                       # applied clean
    bash tools/p2w-bench/pod-prep.sh          # engine rebuilt: 12 sources + ConvertAll + ConvertOne
    pod-prep: 213 converted, stamp written for engine 6af7df086a8898d6
    python3 tools/p2w-bench/restamp_txt.py --run --force
    python3 tools/p2w-bench/restamp_txt.py --report
      213 scored | 0 documents newly clean, 0 newly failing, 213 unchanged

And the document itself, after the rebuild:

    grep -c "Rate for HSN"      600_..._annotations.txt   ->  1   (the source draws it 0 times)
    grep -c "Checked against PO" 600_..._annotations.txt  ->  2   (the source draws it 1 time)

The invented text is still there. The patch is behaviourally inert in this tree: either the hoist it
guards is not the path that emits those paragraphs, or a second route writes them. The first rebuild
attempt is the tell — the corpus had been converted at 22:16 with a **stale class directory**, so the
first "0 moved" was uninformative; the second run, after `pod-prep.sh` recompiled the engine, reproduced
"0 moved" with the patch demonstrably in the build. That second measurement is the one that counts.

## The .docx side was measured too, and is a clean identity

The patch touches the model both writers read, so the .docx had to be checked. Only **one** of the 213
corpus PDFs carries any annotation at all (counted with PyMuPDF over `page.annots()` across the corpus:
`600_reviewed_invoice_with_annotations`, 6 annots; every other document 0). For the other 212 the guard
is inside a loop that never executes, so their .docx cannot differ. For `600` the .docx was measured on
the patched build against the committed row:

| | committed | patched build |
|:--|--:|--:|
| share1 / share5 / share10 | 73.32 / 62.46 / 51.68 | **73.32 / 62.46 / 51.68** |
| median_pt / p90_pt / max_pt | 11.04 / 48.96 / 62.88 | **11.04 / 48.96 / 62.88** |

Identical on every field. The .docx writer was already not printing those paragraphs; only the .txt was.

## Disposition

Reverted. `app/src/main/java/com/kavopdf/app/engine/PdfToWord.java` is back at HEAD, the engine is back
on the measured fingerprint, and no unmeasured change is left in the tree. The patch and the sub-agent's
report are recorded here rather than landed, because a change that moves nothing is not a fix — and a
claim that does not reproduce is the finding.

**Lesson for the next run:** a sub-agent's 213-document score is a self-report. Re-score the corpus in
the tree before it becomes a commit, and rebuild the engine before you believe a "0 moved".
