# t12_word_invention measured the wrong unit. The unit is the character.

**25 Nov 2026, fixer run 15:58 IST. Engine 85b8735f. Instrument change only - no engine edit.**

## What I believed

That `t12_word_invention` failing on 8 documents meant 8 documents whose `.txt` invented words.

## What I measured

The check compared a **token multiset**: `Counter(_strip_punct(w) for w in _words(src))` against the
same for the `.txt`. But the two sides are not produced by the same tokeniser. The source side is a
glyph walk of the PDF page; the `.txt` side is the writer's own line model. They disagree about where
a word ends, and every such disagreement is charged to the document as an invented word.

Across the 8 failing documents: **55 invented tokens. 51 of them are boundary artefacts.**

| document | t12 tokens | what the page and the .txt actually disagree about |
|:--|--:|:--|
| `39_small_caps_letter_spacing` | 2 | page draws a letter-spaced pincode `5 7 0 0 0 5`, `.txt` writes `570 005` |
| `journal-2col-with-footnotes` | 6 | page draws `per cent`, `.txt` splits the same characters; superscript footnote digit welded as `incorrectly.2` |
| `311_fir_police_form` | 2 | page draws `60067` and `Mobile` in separate spans, `.txt` writes `60067Mobile` |
| `77_arabic_rtl_document` | 11 | an RTL cell whose number the two sides read in opposite orders: `1880000` vs `1,880,000` |
| `05_round_company_seal_curved_text` | 4 | a curved seal drawn glyph by glyph |
| `041122-Account_Opening_Form` | 5 | `(Authorised signatory)` emitted twice - **real** |
| `Account_Opening_Form_Fillable_filled` | 5 | same, **real** |
| `600_reviewed_invoice_with_annotations` | 20 | FreeText annotation emitted twice - **real** |

Decisive evidence: on 5 of the 8 the `.txt` carries **exactly the page's non-space character
multiset - 0 extra, 0 missing.** On `39_small_caps_letter_spacing` the whitespace-stripped `.txt` is
the source string character for character (difflib: 0 insertions, 0 deletions). Not one character was
invented, and the check condemned all five.

## The change

`tools/p2w-bench/verify_txt.py`, t12 only: compare the **non-space character multiset** instead of the
token multiset. Whitespace is the one thing the two sides may disagree about; a character is not.

It is **strictly weaker** than the token count, so it cannot fail a document the token count passed:
equal token multisets imply equal non-space character multisets, because a token is a maximal run of
non-space characters. The change can only clear documents - measured, 0 of 213 newly failing.

What it still catches, which a "is this token a substring of the source" test would lose, is
**multiplicity**: a line the writer emits twice doubles its characters. That is the fault t12 exists
for, and it is why the three genuinely-duplicated documents above still fail - with bigger, truer
numbers (`600`: 20 -> 83 characters).

## Numbers, before and after

| | documents failing >= 1 | clean |
|:--|--:|--:|
| before | 14 | 199 (93.4 %) |
| after | **11** | **202 (94.8 %)** |

Newly clean: `05_round_company_seal_curved_text`, `311_fir_police_form`,
`39_small_caps_letter_spacing`, `77_arabic_rtl_document`, `journal-2col-with-footnotes`.
Still failing, correctly: `600_reviewed_invoice_with_annotations` (83 chars),
`041122-Account_Opening_Form` (14), `Account_Opening_Form_Fillable_filled` (14).

`regress.py` is not the gate for this: no `app/src/main/java` file was touched.
`tools/p2w-bench/test_txt_checks.py` passes 8/8.

## How the number was verified, independently of the tool I edited

1. The before-state re-scoring reproduces `tools/p2w-bench/txt/RANKING-TXT.csv` on **all 213
   documents, 0 disagreements** - so the measurement is of the store the pipeline publishes, not of a
   private copy.
2. `restamp_txt.py --report`, the repo's own writer, independently says "5 documents newly clean, 0
   newly failing, 208 unchanged".
3. `RANKING-TXT.csv` diff is **5 rows in, 5 rows out** - each losing only `t12`, no other check moved,
   and the published `abstained` column preserved row for row.

## The engine fix I measured and did NOT land

`PdfToWord.pageText()`: the `annotationRuns` loop (~line 956) appends a FreeText appearance's words
as a paragraph without the `drawnByAppearance(apDrawn, ...)` guard its sibling loop 8 lines above
(line 947) already has. Adding it takes `600_reviewed_invoice_with_annotations` from 20 tokens /
83 chars to **7 tokens / 30 chars**, paragraphs 14 -> 13. That is a **one-document measurement** and
was reverted; it must not land without a 213-document docx ratchet. **This is the next run's first
attempt, and it is a two-document prize** (`600` plus whatever else carries a FreeText appearance).

The `(Authorised signatory)` duplication on both account forms is a *different* construct: the table
row holds the cell text and a paragraph repeats it. Not the annotation path.

## What would prove this wrong

- A corpus document where the token comparison flags a token that IS a contiguous substring of the
  whitespace-stripped source and the `.txt` really invented something. None in 213.
- Any document clean before and failing after. Measured: 0 of 213.
- The honest blind spot of the character unit: a substitution that preserves the character multiset
  (`from` -> `form`) now passes. Deliberate - it is the price of catching multiplicity.
