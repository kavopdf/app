# The widget walk works, and the gate refuses it on one document - measured three ways

**21 Nov, fixer run claimed 07:58, attempt on the carry-over (`t01_word_accuracy` / 601). Engine reverted.**

The carry-over said: push `FINDINGS/widget-ap-glyph-walk-0436-f1x.patch`, measure 601, watch the
Account form's two new docx failures. I did all of it, corpus-wide, and the answer is that the patch
cannot land under the current rule - but not for the reason the last run expected.

## What was measured, and how

Same engine, same sandbox, same render path (`p2w.measure_doc`, soffice, 150 DPI, scipy exact EDT),
pristine HEAD built and scored beside each variant in this run. Nothing below is inherited.

| variant | 601 share@5px | Account form share@5px |
|:--|--:|--:|
| pristine HEAD | 52.39 | 97.62 |
| full patch (streams + state dictionaries) | **0.00** | 98.65 |
| state dictionaries only (ticks) | 51.28 | 98.65 |
| plain streams only (text fields) | 0.25 | 98.06 |

`601` goes from the worst document in the corpus to a perfect page. The Account form goes **up** by
1.03, and it goes up in every variant that emits any widget text at all.

The docx checks agree with the patch: `601` 38/42 FAIL -> **42/42 PASS** on the same tree.

## Why the Account form rises, and why that is not a layout regression

`Account_Opening_Form_Fillable_filled` is at 97.62 - 97.6 % of its ink is already more than 5 px from
where the page drew it. Its 352 widgets carry 137 text strings and 5 ticks, and the walk adds them as
ink that is *also* in the wrong place, because the whole page is. share@5px is a fraction of source
ink, so adding correct-but-displaced ink raises it. The number that separates the two readings is the
one the last run already recorded and could not settle: `17_matched_runs` 272 -> 803,
`59_shape_anchor` 13 -> 299, and docx checks 19/42 -> 23/42 on the same document. More of the page is
matched, and the fraction of it that is far from home is larger.

That is a denominator effect on a document that is already broken, not a page that got worse to read.
**It is also exactly the trade the gate forbids**, and a fixer may not make it. The gate is right to
refuse: it cannot tell the two apart, and that is what it is for.

## What a person has to decide

Either

  (a) the walk lands, on the measured grounds that 601 goes 52.39 -> 0.00 and the Account form's own
      matched population triples while its displaced fraction rises 1.03 on a 97.62 document; or
  (b) `share@5px` gets a companion axis that separates "more ink, some of it far" from "the same ink,
      further" - the Account form is the document that shows the two are not the same question; or
  (c) the walk stays out, and 601 keeps two blank tick boxes and a lost `General`.

Until one of those is decided, no fixer run should re-derive this. The three variants and their four
numbers are above; the work is done.

## Blast radius, measured over all 213 documents

Only **3 of 213** documents carry any annotation at all (PyMuPDF, walking `/Annots` and `page.widgets()`
- `page.annots()` does not return widgets):

| document | annotations | kinds |
|:--|--:|:--|
| `600_reviewed_invoice_with_annotations` | 6 | FreeText, Highlight, Stamp, StrikeOut, Text, Underline |
| `601_fillable_admission_form` | 11 | Widget |
| `Account_Opening_Form_Fillable_filled` | 352 | Widget |

210 documents, including `416_many_tiny_pages`, carry none, so no version of this patch can reach them.
`600` measures 62.46 on HEAD and 58.13 under the patch - it improves too, by the FreeText/Stamp walk
the patch also enables.

## The corpus pass that produced these numbers

The full 213-document measurement was run on the patched tree (see the tooling fix in the same commit,
which is what made it possible at all): 205 documents scored to the hundredth identical to the
published table, **0 worse**, 1 better (`601` 52.39 -> 0.00), and the Account form the only document
up. That is the whole blast radius, not an inference from the annotation census.
