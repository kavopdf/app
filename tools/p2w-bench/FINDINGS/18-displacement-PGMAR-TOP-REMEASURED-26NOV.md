# 18_displacement: the pgMar-top patch re-measured on the whole corpus — Google improves, LibreOffice is an exact identity, and the commit is blocked by a regression that was already in the engine

**Run:** fixer, 26 Nov 01:16 IST · **Engine measured:** `771234e164611275` (tree = HEAD `85b8735f` + the patch)
**Patch:** `tools/p2w-bench/patches/18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch`
**Verdict:** mechanism CONFIRMED and SAFE. Not committed: the gate refuses on a 3-document regression that
this patch did not cause.

This run did what `18-displacement-PGMAR-TOP-MEASURED-IN-GOOGLE-25NOV.md` asked the next run to do — apply
the patch, convert all 213 documents, re-measure, and find out whether it holds. It holds. It also found
something else, which is the more important result.

## 1. The patch is an EXACT identity in the .docx, on all 213 documents

Read back from the emitted `word/document.xml`, old corpus vs new, every document:

| | documents |
|---|---|
| `w:before` on a page-first paragraph reduced by exactly `pgMar w:top` | **213 of 213** |
| a change that is neither that exact difference nor a floor at 0 | **0** |
| paragraph count changed | **0** |
| documents whose `pgMar w:top` is 0 (byte identity) | **0** |

The 25 Nov finding predicted 197 documents change bytes; measured, it is 213 — every document's first
paragraph carries some `w:before`. No page needed the floor, so the identity
`pgMar_after + before_after == before_before` holds on every page of every document, not 211 of 213.

## 2. LibreOffice: 212 of 212 documents identical to the digit

`benchmarks/p2w.py` on the patched corpus, compared with the committed `RANKING.csv`:
**0 worse, 0 better, 212 unchanged.** That is what an exact identity must produce in a renderer that
honours `w:before` at a page top. It is also the reason this change is safe to land: it cannot move a
document for a reader that honours both constructs, and it moves the one construct Google drops into the
one it keeps.

## 3. Google: 5 documents, before and after, same method, same store

Before = `benchmarks/gverify/<doc>.json` at engine `981ff1fa35e2cf67`. After = a fresh Drive conversion of
the patched `.docx` (`UPLOAD_FROM_URL` → Google Doc → export PDF → `gverify.py --collect`). Evidence copies
in `FINDINGS/evidence-26NOV/gverify/`.

| document | before | after | fixed | new failures |
|---|---|---|---|---|
| `416_many_tiny_pages` | 40/42 | **42/42** | `18_displacement`, `27_text_off_page` | none |
| `602_bookmarked_annual_report` | 38/42 | **41/42** | `04_chars_missing`, `18_displacement`, `27_text_off_page` | none |
| `bank-statement-5-pages` | 42/47 | **46/47** | `25_invisible_text`, `27_text_off_page`, `44_header_footer`, `59_shape_anchor` | none |
| `324_loan_amortisation_schedule` | 44/47 | **46/47** | `27_text_off_page`, `59_shape_anchor` | none |
| `412_page_labels_roman` | 40/42 | 40/42 | — | none |

**Nine check-instances fixed, one document CLEAN, nothing worse on any of the five.**

### Correction to the 25 Nov finding: `412_page_labels_roman` does not move at this tree

The 25 Nov file records `412` as 40/42 → **42/42 CLEAN**. Re-measured today on the same engine id it does
not move at all: still failing `18_displacement` and `27_text_off_page`. The other three reproduce exactly.
`412` is the one document of the four whose page-first gap is 1227 twips, and it is the one that does not
respond, so the mechanism is not uniform across documents and the 25 Nov `42/42` should not be quoted.
Everything else in that file reproduced to the check.

## 4. THE BLOCKER, AND IT IS NOT THIS PATCH

The commit gate refuses, and the reason is worth more than the patch:

    REGRESSION: 3 document(s) worse than baseline
      newsletter-3col-header-footer    0.2  -> 86.3   (+86.1)
      601_fillable_admission_form     52.39 -> 55.32  (+2.93)
      401_trifold_brochure             0.03 ->  0.79  (+0.76)

`share5` is a DEFECT share — the percentage of ink outside tolerance — so higher is worse. These three are
worse than the last published baseline, and **this patch cannot be the cause**: the patch is an exact
identity in the .docx (§1) and produces 0 changed scores in LibreOffice (§2). The regression is in the
engine that is already committed, and it has been invisible because nobody re-measured the corpus since
the changes landed. The published baseline is stamped `b7699196+00e99cabf1`; the tree is `85b8735f`.
`85b8735f` is *"fixer: foot-band four-site patch - anchored running foot becomes flowed text"* — the
foot-band change is the first suspect, and `newsletter-3col-header-footer` going from 0.2 % to 86.3 %
displaced ink is not a small effect.

**So the next run's first job is not this patch.** It is to re-measure `newsletter-3col-header-footer`,
`601_fillable_admission_form` and `401_trifold_brochure` against the engine at `b7699196` and find which
of the two commits since then moved them. Until that is answered, every engine change is uncommittable,
which is exactly the state this run found itself in.

## 5. What the next run does with this patch

It is proven and it is safe. Apply it, and land it **in the same commit as the answer to §4**, because a
commit that publishes a table is a commit that must be able to say why the table is worse than the last one.

    git apply tools/p2w-bench/patches/18-displacement-PGMAR-TOP-CARRIES-THE-PAGE-GAP.patch
    python3 tools/p2w-bench/corpus-convert.py --force -j 4      # 213 docs, 4.6 min
    python3 benchmarks/p2w.py --budget 230                      # repeat until 212/212
    python3 benchmarks/gate.py --budget 200                     # writes STATE.json

The patch file's diff headers were rewritten this run (`a/` and `b/` paths) — as committed on 25 Nov it
carried an absolute `+++ /scratch/input/DocxWriter.java`, which `git apply` refuses. That fix is the one
thing about this patch that is in the repository now.
