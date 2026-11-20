# t12_word_invention is not one construct, and three of its twelve documents are the instrument's own artifact

20 Nov 2026, fixer, second attempt in the same slot. No engine change landed. The measurement below
is the deliverable: it stops the next run treating `t12_word_invention` as a single mechanism.

The check (`verify_txt.py`, unmodified) counts `txt_words - src_words` as a multiset, after stripping
surrounding punctuation and folding case, and fails on any invented word. The source side is
`page.get_text()`.

## The census: the invented words are not one fault

| document | invented | what the invented tokens actually are |
|---|---:|---|
| `600_reviewed_invoice_with_annotations` | 21 | **annotation content.** The six review notes ("rate for hsn 8536 confirmed with po. checked against po 4471...") are drawn by the page as annotations. `page.get_text()` does not read annotation content; the engine does. Measured: `confirmed` is absent from `page.get_text()` and present in the annotation stream. |
| `77_arabic_rtl_document` | 11 | RTL. The Arabic tokens arrive in a different order/segmentation than the source's extraction. |
| `journal-2col-with-footnotes` | 6 | a two-column page with footnotes: the .txt carries a word one time more than the source does. |
| `12_stamp_across_page_break` | 5 | **duplication across the break.** `KUNIGAL` is drawn once, on page 1; the .txt carries it twice. t09's territory, not t12's. |
| `05_round_company_seal_curved_text` | 4 | curved text arrives as single letters (`i`, `n`, `t`). |
| `391_survey_questionnaire_grid` | 4 | **U+0000 in the source.** See below. |
| `311_fir_police_form` | 2 | **welding.** The .txt carries `60067Mobile` as one token; the page draws `60067` and `Mobile` on two lines. |
| `392_statistical_console_output` | 2 | **U+0000 in the source.** See below. |
| `39_small_caps_letter_spacing` | 2 | `570`, `005` - letter-spaced small caps re-tokenise against the source. |
| `406_passport_mrz_page` | 1 | **U+0000 in the source.** See below. |
| `041122-Account_Opening_Form` | - | no PDF in any corpus-v1 release zip; carried, not measured. |
| `Account_Opening_Form_Fillable_filled` | - | same. |

## The U+0000 artifact, measured across the whole corpus

The PDF text layer carries U+0000 where the page draws a zero-width cell separator, and `_words`
splits on `\S+`, so NUL is **not** whitespace and glues itself to the token beside it:

    source  'PASSPORT / \x00\x00\x00\x00\x00\x00\x00\x00PHOTOGRAPH'   -> token '\x00\x00\x00photograph'
    source  'DisagreeStrongly\x00disagree'                            -> token 'disagreestrongly\x00disagree'
    source  'Multiple R-squared:  0.8412,\x00Adjusted R-squared: 0.8371' -> '0.8412,\x00adjusted'

`_strip_punct` strips `.,;:!?()[]{}"'-` and nothing else, so the NUL survives and the clean token in
the .txt is counted as a word the writer invented. The writer emitted the right word; the source side
split the wrong way.

Measured by replacing U+0000 with a space in the source text and recounting, over every document with
a PDF and at least 200 source characters:

    would clear ................ 3   391_survey_questionnaire_grid, 392_statistical_console_output,
                                     406_passport_mrz_page
    would break ................ 0   (no passing document gains an invented word)
    still failing .............. 7   the other mechanisms above

So three of the twelve are entirely an artifact of the instrument's tokenisation of the source, and
zero documents are harmed by treating NUL as whitespace. **This is not edited into `verify_txt.py` -
the verifier is the instrument and a check is not moved by changing the check.** It is recorded so the
next run knows that at most nine of the twelve are the writer's, and which nine.

## What that leaves, and what the next run should not do

The nine are at least five different faults: annotation content, RTL order, page-break duplication,
cell welding, letter-spaced caps. There is no single construct here, and the class cannot be closed by
one change the way `t13` was. The two that are worth an engine slot:

* **`311_fir_police_form`, cell welding.** `60067` and `Mobile` are two drawn lines in one cell and
  arrive as `60067Mobile` with no separator. Same family as the welded cell t13 was closed on, but the
  fix is in `PdfToWord`'s cell model, which owns the .docx and needs a .docx measurement.
* **`12_stamp_across_page_break`, duplication.** A stamp drawn once arrives twice. That is
  `t09_page_furniture`'s question and should be worked there, where four documents already sit, not
  under t12 where it counts as one.

`600_reviewed_invoice_with_annotations` should probably not be worked at all until someone decides
whether annotation content belongs in a .txt. The engine emits it, a reader of the PDF sees only a note
icon, and the instrument cannot see it either way.
