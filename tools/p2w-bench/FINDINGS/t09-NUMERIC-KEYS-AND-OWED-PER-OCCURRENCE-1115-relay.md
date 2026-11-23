# t09_page_furniture charged two correct .txt files. The check was wrong, twice, and both faults are measured on all 213.

**23 Nov 2026 · relay slot 10:17 → IST · verify_txt.py only, no engine rebuild**

## Why this run went here

`18_displacement` is priced at 34.5 clean documents and holds an open lead, but two
sub-agent diagnoses came back in the first half hour and neither produced a landable
engine change: the class's `.txt` half turned out to be **unrelated to it** (below), and
what was left of it was instrument faults in the `.txt` verifier. Those are landable in
minutes and they are worth documents, so the slot went there.

## The measurement that redirected the run

Of the **101** documents that fail `18_displacement` in Google, **95 are `.txt`-clean**
(94.1%); only 6 fail any t-check, against 5.3 expected if the two populations were
independent (Fisher p = 0.752, OR 1.34). All **13** documents that fail `18` and nothing
else are `.txt`-clean, 13 of 13. `t08_line_order`, the only positional `.txt` check,
fails **0 of the 101**. A block displacement cannot reach the `.txt` instrument:
`_txt_lines` (verify_txt.py:851-853) discards blank lines and the only positional signal
it keeps is leading spaces. **The `.txt` half of `18_displacement` is not `18_displacement`.**

## Fault 1 - a furniture key with no letter in it is not furniture

`_furniture_key` folds every digit to `#`, so a page of numeric table cells folds to a
handful of keys that repeat on every page and clear `FURNITURE_MIN_PAGES`.

| document | owed (before) | present (before) | owed (after) | present (after) |
|:--|--:|--:|--:|--:|
| `324_loan_amortisation_schedule` | 66 | 1485 | **48** | **48** |
| `041122-Account_Opening_Form` | 21 | 197 | 12 | 125 |
| `Account_Opening_Form_Fillable_filled` | 21 | 199 | 12 | 125 |

On `324` the 1437 surplus decomposes exactly into three numeric keys - `'#'` present 240,
`'#,#,#.#'` present 423, `'#,#.#'` present 774 - while all 8 real running heads match
exactly, 6/6 on each of their six pages. The bottom band of every page is blank (rendered
and read): the document has no footer, so nothing is missing.

Fix: `elements` keeps only keys with at least one letter. Removing an element removes its
`owed` and its `present` by the same amount, so **this cannot turn a pass into a fail**.

## Fault 2 - owed was counted per page, not per drawn occurrence

`gst-invoice-multipage-item-table` draws `Page N of 4` **twice on every page** (y=75.4 top
band, y=811.4 bottom band) and its `.txt` carries all **8** copies. The check owed one copy
per *page* - 4 - and charged a 4-copy surplus for a duplication the page really makes.

| document | owed (before) | present | owed (after) | present |
|:--|--:|--:|--:|--:|
| `gst-invoice-multipage-item-table` | 39 | 43 | **43** | **43** |

Fix: `owed += sum(pgs.values())` over a per-page occurrence count. A writer that drops a
second copy now shows as a **deficit**, which is the fault the check is for; the old cap
comment above `present` still holds.

## Blast radius, measured on all 213

Each variant was re-scored over the full corpus with the real `verify_txt.compare()` on a
fresh conversion of all 213 (engine built from this tree, `ConvertOne` per document):

| variant | clean | flips | regressions (ok -> fail) |
|:--|--:|:--|:--|
| head | 197 | - | - |
| keys with a letter (fault 1) | **198** | `324` FAIL->PASS | **none** |
| owed per occurrence (fault 2) | **198** | `gst-invoice-multipage-item-table` FAIL->PASS | **none** |
| digit/letter word split | 197 | none | none |

`t09` changes on 3 documents under fault 1 and 4 under fault 2; the overlap is `324`,
`041122` and `Account_Opening_Form_Fillable_filled`. The last two still fail `t09`
afterwards (their keys are `'D'`/`'M'`/`'Y'` date boxes, owed 12 against present 125), so
they are a different fault, not this one.

The two fixes were landed **together**. For the four documents the two touch, the
combination is bounded and cannot regress against baseline: `041122` and the filled form
fail before and after; `gst` keeps its `'Page # of #'` key (it has letters) and passes;
`324` is a pass under fault 1 and can only stay a pass or stay failing under the
combination, never fall below its baseline. **The combination was not re-scored as a
combination** - the corpus conversion is 20+ minutes and the slot had 20. The next run
that re-stamps `RANKING-TXT.csv` should score it and record whether `324` held.

## Not landed, and why

* **`77_arabic_rtl_document`** - `t01` + `t12`. The date's every character is present and
  bidi-reordered, not lost (8 tokens lost, 14 gained, all date/number fragments). A
  digit/letter split in `_words()` alone changes **nothing** (measured, 0 flips): `t01`
  also compares unstripped punctuation (`':التاريخ'` vs `'التاريخ'`), so it needs the
  punctuation strip applied to both sides too. Not measured, not landed.
* **`601_fillable_admission_form`** - `t01` charges two ZapfDingbats `0x33` (rendered:
  checkmarks) as two words `'3'`. **Decoding ZapfDingbats does not fix it and makes it
  worse** - it substitutes `✓`, which the `.txt` does not carry either, and newly fires
  `t03`/`t07`. Only abstention clears it. But the corpus has exactly two ZapfDingbats
  documents and they need *opposite* treatments (`Account_Opening_Form_Fillable_filled`
  reports exactly 5 invented words, consistent with the writer emitting `✓`), so one
  change cannot be right for both. Parked with this evidence.
* **`311_fir_police_form`** (`60067Mobile`, the `5` is gone from the `.docx` too) and
  **`600_reviewed_invoice_with_annotations`** (21 invented tokens from 7 sticky-note
  `/Contents` words never drawn) are **real engine text faults**, not instrument faults.

## Consequence for the table

`RANKING-TXT.csv` still carries the 197 scored with the old instrument and is now stale
against `verify_txt.py`. It must be re-stamped (`restamp_txt.py --run --apply`) by a run
with the corpus and the engine built. The measured answer is **198** for each fault alone;
the two together should give 199 if `324` holds under the combination.
