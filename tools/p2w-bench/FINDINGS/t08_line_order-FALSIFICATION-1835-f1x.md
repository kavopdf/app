# `t08_line_order` — the falsification was run, and it refutes BOTH sides as written

**21 Nov 2026 · relay/fixer slot 18:19 · engine `462353f` · four synthetic documents, nothing committed to the engine or the verifier**

The last run's handoff left one instruction, in its own words:

> The agent's proposed one-line sort of `_src_pages` is NOT obviously right - it would compare
> sorted-vs-sorted. Decide with a falsification: construct a .txt whose lines are deliberately swapped in
> y and confirm t08 still fires after the change.

That was run. Two things came out of it, and the second one was not expected.

## The method

Four documents, built with PyMuPDF so the page's **draw order** is under control and nothing about the
engine is involved. Each has four lines in one column at x = 0, y = 100/120/140/160, plus one line at
x = 100 that exists only so `_ruler()` can fit a characters-per-point ruler (without it the check
abstains and measures nothing). Each `.txt` is written by hand in a chosen order.

| case | what the page draws | what the `.txt` says | what it is for |
|:--|:--|:--|:--|
| **c1** | top-down: A B C D | A B C D | control — must pass |
| **c2** | **bottom-up: D C B A** | A B C D — the correct reading order | the defect — must fail today |
| **c3** | bottom-up: D C B A | **B A D C** — deliberately wrong | the falsifier — must still fail after any fix |
| **c4** | two pages, both top-down | A B C D, correct | does a fix survive more than one page |

## The result

Three variants of `verify_txt.py`: the tree's, the handoff's proposed **global** sort of `src_seq`, and a
**per-page** sort of each page's lines before appending.

| case | current tree | handoff's global sort | per-page sort |
|:--|:--|:--|:--|
| c1 control | PASS | PASS | PASS |
| c2 defect | **FAIL** `source=5 txt=2` | **PASS** | **PASS** |
| c3 falsifier (txt order wrong) | **FAIL** `source=5 txt=3` | **FAIL** `source=5 txt=3` | **FAIL** `source=5 txt=3` |
| c4 two pages, correct `.txt` | t08 PASS | **FAIL** `source=5 txt=4` | t08 PASS |

### What each column says

**The current check is wrong on c2, and c2 is the real-world case.** The page draws its lines bottom-up
— a footnote block drawn last, a chart whose axis labels are drawn upwards, a speech bubble drawn after
the bubble beneath it. The `.txt` lists them top-down, which is what a reader wants and what the engine's
geometric order produces. The check calls that a defect: `source=5 txt=2`. It is not a defect. The check's
own docstring states the semantics it implements — *"line order: the lines arrive in the order the page
drew them"* — so this is a deliberate spec, not a slip, and the spec is the thing that is wrong for a
`.txt`.

**The handoff's worry about the global sort is refuted.** It said a sort would "compare sorted-vs-sorted".
On c3, whose `.txt` is deliberately in the wrong reading order, the sorted variant still fails with
**exactly the same score as the current tree**, `source=5 txt=3`. The sort does not blind the check,
because it changes the *source's* order while the `.txt`'s order is independent. A check you have now
seen fail twice is not decoration.

**The handoff's proposed implementation is wrong anyway, and c4 is the number.** `src_seq` is a flat list
accumulated across pages, and the check groups partners by **column bucket, never by page**. A global
`src_seq.sort(...)` therefore puts page 2's `y=100` above page 1's `y=200`. On c4 — two pages, both drawn
top-down, a correct `.txt` — the global sort reports `t08 source=5 txt=4` and **FAILS a document that is
right**, while the per-page sort passes it. The one-line fix manufactures the defect it was written to
remove. Anyone who applies it will move documents in the wrong direction and blame the corpus.

## The patch, and why it is NOT in this commit

The per-page version is the one that is correct, and it is four lines:

    src_seq = []
    for pg in _src_pages(src_pdf):
        upright = [ln for ln in pg["lines"] if ln.get("upright", True)]
        upright.sort(key=lambda ln: (round(ln["y"], 1), ln["x"]))   # PER PAGE
        src_seq.extend(upright)

It was applied to the tree, and **reverted**, because it cannot be measured here. It changes what
`verify_txt.py` says about all 213 documents, and re-scoring them needs the engine built and the corpus
converted — the build downloads a JDK and the library set, and the conversion pass is over an hour. This
slot had under 70 minutes left when the patch was ready.

`regress.py --check` **passed** on the patched tree and that is not evidence: it compares the *engine*
against the stamped table, and a verifier change moves no engine byte, so it never re-runs the verifier.
A gate that answers PASS without measuring the thing that changed is the failure this project has
recorded four times. Landing it on that PASS would be the fifth.

### What would land it

    python3 tools/p2w-bench/build-engine.sh
    python3 tools/p2w-bench/restamp_txt.py --run --budget 260    # resumable, repeat until done
    python3 tools/p2w-bench/restamp_txt.py --report              # diff old against new, per document
    python3 tools/p2w-bench/restamp_txt.py --apply               # only if --report is clean
    python3 tools/p2w-bench/regress.py --check

**The prediction, stated before the fact.** The 10 documents in `txt/RANKING-TXT.csv` whose `failed_ids`
carry `t08_line_order` should clear it — `09_stamp_font_not_embedded`, `305_vaccination_certificate`,
`330_cad_drawing_sheet`, `400_comic_page_speech_bubbles`, `46_chart_coloured_labels_body_text`,
`65_two_col_full_width_figure_caption`, `70_magazine_drop_cap_photo_caption`,
`itr-computation-with-slab-table`, `041122-Account_Opening_Form`,
`Account_Opening_Form_Fillable_filled` — taking the `.txt` table from **190 clean of 213** to **200**,
with **no document newly failing**. If `--report` shows any document worse, the per-page sort is wrong
too and the whole idea is dead; the c4 result is the one to re-read first.

## The honest accounting of what this is worth

**No document improves.** The ten documents are not broken; the instrument's spec is. Clearing
`t08_line_order` on them moves the `.txt` score by ten and moves the product by zero. That is worth doing
— ten documents have been chased for a month for a fault that is not in them — but it must not be
reported as ten documents fixed, and it must not be counted toward the user's 99% bar.

The real question the handoff asked is therefore answered: **the `.txt` half of `t08` is not a fixer
target, it is an instrument repair.** What is still genuinely open is the `.docx` side, where a reader
does follow the page and the engine's geometric order may really lose an author's intent — and there is
no measurement of that here.

## Repeat it

    python3 /scratch/work/t08/build2.py     # c1 c2 c3
    python3 /scratch/work/t08/build3.py     # c4, two pages
    python3 verify_txt.py c<1-4>.pdf c<1-4>.txt

The scripts are 25 lines each and are the record: `insert_text` in a chosen order makes the draw order,
and the `.txt` order is written by hand. A page needs one line with leading spaces or `_ruler()` returns
None and `t08` abstains — the first attempt at this measured nothing for exactly that reason and reported
all three cases as passing.
