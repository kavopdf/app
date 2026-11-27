# `t01_word_accuracy`: counting characters instead of word tokens — REFUTED, 205 → 201

**27 Nov 2026, 06:20 IST · fixer run (relay) · measurement only, nothing patched**

The proposal (ranked first for the txt side on 27 Nov): make `t01_word_accuracy` use the unit
`t12_word_invention` already uses — the **whitespace-stripped character multiset**, at zero tolerance — so
that a document whose characters are identical on both sides but whose *word boundaries* differ stops
failing a check about words. Two documents were named: `39_small_caps_letter_spacing` and
`77_arabic_rtl_document`.

It was measured over the whole corpus before being written. **It clears 2 and fails 6. 205 → 201.**

## The measurement

`/scratch/work/t01_ab.py`, run against the 213 `.txt` files the engine produced at
`a4d8fca469bba636` and the source PDFs. It calls `verify_txt.compare()` untouched for the check set as it
stands, and computes the proposed t01 from the same two texts `compare()` used. Nothing was patched.

| | documents |
|:--|--:|
| scored | **213** |
| clean today | **205** |
| failing today | **8** |
| **CLEARED** by the change | **2** — `39_small_caps_letter_spacing`, `77_arabic_rtl_document` |
| **BROKEN** by the change | **6** |
| clean after | **201** |

The six it breaks, with their character deficit and surplus (all six pass every check today):

| document | chars lost | chars added |
|:--|--:|--:|
| `79_inr_indian_digit_grouping_table` | 15 | 0 |
| `406_passport_mrz_page` | 8 | 0 |
| `391_survey_questionnaire_grid` | 2 | 0 |
| `balance-sheet-and-profit-loss` | 2 | 0 |
| `392_statistical_console_output` | 1 | 0 |
| `balance-sheet-two-columns-of-figures` | 1 | 0 |

## Why the "it can only clear documents" argument does not carry over

The t12 clause carries this comment (`verify_txt.py:1471-1474`):

> It is strictly weaker than the token count, so it cannot fail a document the token count passes: equal
> token multisets imply equal non-space character multisets, because a token is a maximal run of non-space
> characters. The change can only clear documents.

That is true of the **surplus** direction, which is what t12 counts. It is **not** true of a zero-tolerance
**deficit**. The token count is a *ratio* — `acc >= 99.0` — and the character deficit is an *absolute*. A
document of 300 tokens that loses one whole word scores 99.7 % and passes t01 today; a document that loses
one character scores a deficit of 1 and fails under the proposal. Six documents are in that gap. The two
directions are not the same check, and the argument that justifies t12 does not justify this.

`601_fillable_admission_form` is the case that shows why the tolerance cannot simply be loosened instead: its
deficit is **2** characters — the two tick marks its checkboxes carry in `/AP /N` streams that
`PDFTextStripper` never walks. A 99 % character recall would pass it, and that would be the instrument
hiding a real engine defect, not a fix.

## What this leaves

Both forms are refused:

* **zero-tolerance character deficit** — 205 → 201, measured above;
* **99 % character recall** — clears `39`, `77` **and** `601`, i.e. it buys a document by silencing the
  checkbox loss that is `601`'s actual defect.

The two documents are not an instrument problem to be waived. Their word boundaries differ because
`PdfToWord.textOf()` splits at `gap > gs * 0.18f` (`PdfToWord.java:4307-4311`) while the source tokeniser
splits at 0.15 em — a real disagreement about where a word ends, in the engine. **The fix is in the
engine's word-boundary rule, not in t01's unit.** `39`'s `570005` is cut `57 0 0 05` against the source's
`570 005`.

No file was changed by this measurement.
