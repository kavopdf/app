# A line drawn more than once at one place is one line — both sides

Measured 21 Nov 2026, fixer slot 13:53. Class: `t01_word_accuracy` (.txt half).

## The defect

Faux bold is a page drawing the same string two or three times at the identical bounding box —
two fills and a stroke. Two independent things were wrong with it, and each hid the other:

* **the writer** built more than one paragraph from the overlapping draws, so
  `38_faux_bold_italic_synthesised` carried the line
  `Study of self-compacting concrete using quarry dust as partial replacement` **twice in a row**
  (lines 7 and 8 of the .txt);
* **the checker** built its source word list from `get_text()`, which counts every copy, so the
  same document was charged 4 lost words — 98.0 % against a 99 % bar — for a line the writer had
  in fact emitted.

## What was measured

`.txt` outputs held fixed, only the checker changed (clip-off already committed at 14:21):

| configuration | clean of 213 | newly failing |
|---|---:|---|
| checker dedupe only (writer untouched) | 188 | `38` gains `t12_word_invention` — the fault moved, it did not go |
| writer dedupe only (checker untouched) | 188 | none — and no gain either: the checker still charges it |
| **writer + checker together** | **189** | **none** |

Writer-only was neutral *because* the checker was still counting the copies. Checker-only moved the
failure to `t12` *because* the .txt still had the duplicate. Neither half is a fix on its own, which
is why they land in one commit.

## The proof that the .docx cannot move

`scope.py` names `TxtWriter.write` and `TxtWriter.appendPara` — scope `txt`. Proved rather than
trusted: the whole corpus converted to `.docx` on the patched tree and on `HEAD`, then every zip
member compared:

    213 of 213 .docx carry identical content on both trees, 0 differing

(The `.docx` files differ *byte for byte* between any two runs — a zip stores entry timestamps — so
the comparison is on zip members, not on file bytes. A byte diff on a .docx directory always shows
213 and proves nothing.)

## Blast radius on the .txt

    1 of 213 .txt files changed: 38_faux_bold_italic_synthesised (one repeated line removed)
    212 of 213 byte-identical

An earlier, looser version of the writer guard (0.5 pt tolerance) also collapsed
`text-held-twice-shadow-text` and `312_affidavit_stamp_paper`, and `text-held-twice` then failed
t01 — a shadow copy is a real second line at a *different* position, not a doubled draw. The guard
therefore requires an **identical** position (<= 0.01 pt), which is what a doubled draw is.

## Still open in this class

`39_small_caps_letter_spacing` 97.4 %, `601_fillable_admission_form` 97.6 %,
`77_arabic_rtl_document` 92.1 %. None is a writer loss:

* `39` and `77` are **word-boundary disagreements** between PyMuPDF and PDFBox. `39` draws every
  glyph as its own show on a uniform 1.20 pt advance, so PyMuPDF splits `O.` into `O` + `.` while
  PDFBox keeps them; `77` is the opposite — RTL labels glued to adjacent digits. Both already fail
  `t12` as well, which is the signature of segmentation, not missing content. A segmentation change
  moves both t01 and t12 on every RTL and letter-spaced document and needs its own blast radius.
* `601` is the only genuine writer-side content loss: the two ticks exist only in widget `/AP`
  streams (`/ZaDb 9 Tf (3) Tj`), and PDFBox never walks appearances. `glyph_truth()` already reads
  widget streams, so the source counts the ticks and the writer emits none.

## A stale comment corrected

`verify_txt.py`'s widget guard comment claims `601_fillable_admission_form` "scores 100.0" with the
guard. Measured 21 Nov: **97.6 %, 2 lost (`3` twice), FAIL** — and `RANKING-TXT.csv` agrees. The
comment was written against an engine that drew the value in the content stream too.
