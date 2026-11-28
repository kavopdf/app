# The annotation hoist has two doors, and neither one alone clears the document

**28 Nov 2026, fixer slot 13:53 IST. Engine in the tree `a05b20eb05fe0fc8`; reverted to it at the end
of this run (`git status app/` clean). Nothing committed to the engine.**

## Why this run went here

The `.txt` half of the goal is the cheap half. `tools/p2w-bench/txt/RANKING-TXT.csv` has **5 failing
documents of 214**, and `t12_word_invention` ("the .txt carries no character the source never drew")
is the failing check on **3** of them. Two previous runs had each closed ONE of the two doors that
feed `t12`, measured it, and recorded `MEASURED NO CLEAR`:

| run | door closed | `600` invented chars, before -> after |
|:--|:--|--:|
| 25 Nov relay | `drawnByAppearance(apDrawn, v)` on the annotation loop | 83 -> **30** |
| 27 Nov relay | `"FreeText".equals(ann.getSubtype())` inside `annotationRuns()` | 83 -> **49** |

Both were reverted. Neither was measured against the other. That is the gap this run closed.

## The measurement, before and after, same reader

The patch is `FINDINGS/annotation-both-doors-28NOV.patch` (20 lines): both guards, together.

    java ConvertOne /scratch/work/p2w/corpus/<doc>.pdf <outdir>
    python3 tools/p2w-bench/verify_txt.py /scratch/work/p2w/corpus/<doc>.pdf <outdir>/<doc>.txt

| document | before | after both doors |
|:--|:--|:--|
| `600_reviewed_invoice_with_annotations` | 7/8 applicable passed, **FAIL** (`t12` 83 invented chars) | 8/8 applicable passed, **PASS** |
| `601_fillable_admission_form` | 6/7 passed, FAIL (`t01_word_accuracy`) | 6/7 passed, FAIL - **unchanged**, `t12` was never its failing check |
| `Account_Opening_Form_Fillable_filled` | 7/10 passed, FAIL (`t12` 14) | 7/10 passed, FAIL (`t12` **14**, unchanged) |
| `Prakashan_Print_Fidelity_Handbook` | 7/11 passed, FAIL (`t12` 88) | 7/11 passed, FAIL (`t12` **88**, unchanged) |

`.txt` line count on `600`: **75 -> 72**. The three lines that leave are the annotation hoists the two
guards each claim, plus the one neither guard reaches alone.

**So the two doors are not alternatives, they are a conjunction.** Closing either one leaves a
document that still fails `t12` and looks like a failed fix; closing both clears it. Both prior runs
measured correctly and drew the right conclusion from a one-door experiment.

## What this does and does not prove

* PROVES: on `600_reviewed_invoice_with_annotations`, both guards together take `t12` from 83 to 0 and
  the document from FAIL to PASS, and change no other document's verdict among the three other `t12`
  failures in the corpus.
* DOES NOT PROVE: that the change is safe corpus-wide. **The change is in `PdfToWord.java`, which is
  in the docx fingerprint**, so landing it costs a full 213-document docx re-score (measured today at
  ~13 min conversion + ~26 min measurement, ~10 slices) plus a Google verification of the documents
  whose paragraph count moves. That is more than the slot had left, which is why this is a `lead`
  and not a kept attempt.
* DOES NOT PROVE: that `Account_Opening_Form_Fillable_filled` (14) and `Prakashan` (88) are reachable
  at all. Both are unchanged by both doors, so their invented characters come from a **third**
  duplication this run did not find. `Prakashan`'s extras are concentrated in upper-case letters
  (`2` x7, `e` x7, `I` x6, `S` x5, `E` x4, `T` x4, `A` x3, `N` x3, `C` x3) - the shape of a heading or
  a running head emitted twice, not of a single hoisted paragraph. That is the next lead.

## The one-command check for the next run

    git apply FINDINGS/annotation-both-doors-28NOV.patch
    bash tools/p2w-bench/pod-prep.sh
    for i in 1 2 3 4; do python3 tools/p2w-bench/corpus-slice.py --budget 240 -j 4; done
    for i in 1 2 3 4 5 6; do python3 benchmarks/p2w.py --budget 250; done
    python3 benchmarks/gate.py && python3 tools/p2w-bench/regress.py --stamp
    python3 tools/p2w-bench/regress.py --check      # must exit 0

Do not spend the re-score on the `.txt` half alone: the same re-score carries the docx half, so the
run that pays it should also verify `600` in Google and record whether the two hoisted paragraphs
were costing it a docx check as well.
