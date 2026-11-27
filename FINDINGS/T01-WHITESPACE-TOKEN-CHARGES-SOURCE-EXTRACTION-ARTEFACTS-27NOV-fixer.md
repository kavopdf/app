# t01: two of the three `.txt` word-accuracy failures are charged on text that is character-identical to the source

**27 Nov 2026, fixer slot 13:54-, repo `kavopdf/app` @ HEAD of this commit.** Engine `d28ca7516c3f9165`
(the fingerprint the converted corpus is stamped with). Corpus converted 213/213 on this pod this run;
`regress.py --check` PASSes on the tree as committed.

Nothing in `app/` was changed. This is an instrument finding: it says what `t01_word_accuracy` is
charging, with the numbers, so the next run can decide whether the check or the writer is wrong.

---

## 1. The claim

`t01_word_accuracy` fails a document when fewer than 99% of the source's words appear in the `.txt`.
`_words()` is `re.findall(r"\S+", ...)` (`tools/p2w-bench/verify_txt.py:278-279`) - **a whitespace
token, not a word**. The source side of that comparison is `glyph_truth()`, which rebuilds the text from
the drawn glyphs, and the glyph runs it rebuilds are separated by the whitespace the PDF *declares*, not
the whitespace a reader sees.

Two of the three documents failing `t01` therefore fail on a token boundary, not on lost text. Measured
character-for-character, both carry **every alphanumeric character the source carries, with none extra**:

| document | t01 | source chars | txt chars | missing | extra | identical |
|:--|--:|--:|--:|--:|--:|:--|
| `77_arabic_rtl_document` | 92.1 | 546 | 546 | 0 | 0 | **yes** |
| `39_small_caps_letter_spacing` | 97.4 | 930 | 930 | 0 | 0 | **yes** |
| `601_fillable_admission_form` | 97.6 | 451 | 449 | 2 | 0 | no - two `3` |

(The character census is `Counter(c for c in s if c.isalnum())` over `page.get_text()` of the source
against the `.txt`, both sides read in this run. All numbers here and below are LibreOffice-free: the
`.txt` half needs no renderer, so nothing in this finding is a proxy number.)

## 2. What the eight "lost words" actually are

Read out of the instrument itself (`glyph_truth` + `_words` + `Counter(sw) - Counter(tw)`, run from
`/tmp/lost.py` this run):

`77_arabic_rtl_document` - source 101 tokens, `.txt` 107 tokens, 8 charged lost:

```
':التاريخ5'  'سبتمبر2025'  '2قهوة'  '3شحن'  '4الإجمالي1880000'  ':إجمالي'  'الفاتورة1,880,000'  'دولار'
```

Every one but `دولار` is **an Arabic word glued to a Latin digit or a comma in the source's own
extraction** - a bidi artefact of how the PDF's glyph runs were laid down, not a word boundary anyone
reads. The `.txt` writes `الفاتورة` and `1,880,000` as two tokens, which is the faithful thing to do, and
the check charges the difference as a lost word.

`39_small_caps_letter_spacing` - source 306 tokens, `.txt` 302, 8 charged lost:

```
'0'x2  'O'  'D'  '.'  ','  '57'  '05'
```

Single characters and two-digit groups: the small-caps run is set with letter-spacing, the source's glyph
runs break at every gap, and the `.txt` writes the word whole. Again the source's extraction is the
outlier, not the `.txt`.

## 3. The other six `.txt` failures, for the ledger

Same character census, all eight failing documents:

| document | class | source chars | txt chars | missing | extra | what it really is |
|:--|:--|--:|--:|--:|--:|:--|
| `305_vaccination_certificate` | t08_line_order | 624 | 624 | 0 | 0 | order, not content - real |
| `74_balance_sheet_indented_subitems` | t02_position | 948 | 948 | 0 | 0 | indent, not content - real |
| `600_reviewed_invoice_with_annotations` | t12_word_invention | 593 | 681 | 0 | **88** | 88 characters invented - real |
| `601_fillable_admission_form` | t01 | 451 | 449 | **2** | 0 | two `3` dropped - real, small |
| `041122-Account_Opening_Form` | t06/t09/t12 | 36143 | 36021 | **134** | 12 | real |
| `Account_Opening_Form_Fillable_filled` | t06/t09/t12 | 36223 | 36096 | **139** | 12 | real |
| `39_small_caps_letter_spacing` | t01 | 930 | 930 | 0 | 0 | **token boundary only** |
| `77_arabic_rtl_document` | t01 | 546 | 546 | 0 | 0 | **token boundary only** |

So the `.txt` half is **205 clean of 213**, and 2 of the 8 failures are not text loss at all. The largest
single real defect is `600_reviewed_invoice_with_annotations`: 88 characters in the `.txt` that the page
never drew.

## 4. Why nothing was changed

The repair is in `t01`'s unit, not in the writer: compare characters, or fold the source token through
the same normalisation `t12` already uses. But `t01` is the truth instrument, and the last run's own
lesson on `18_displacement` applies here verbatim - **do not flip an instrument without counting how many
verdicts move in each direction**. That count is corpus-wide `glyph_truth` over 213 documents, which did
not fit this slot after the corpus conversion (see §5). A half-measured instrument change is worse than a
named defect, so it is recorded as a lead, not attempted.

The experiment the next run should run, in one pass:

1. For all 213 documents, compute `t01` twice: current whitespace tokens, and a character-multiset
   accuracy with the same 99% floor.
2. Report the confusion matrix (pass->fail, fail->pass, unchanged) and the document names in the two
   changed cells.
3. Only then decide. If the character reading clears `77` and `39` and nothing else, the check was
   charging the source's extraction; if it also clears `601`'s two `3`, it is too lax and the token unit
   has to stay for that document.

## 5. What this run did do, and the one number that changed

The corpus was converted from **41 to 213 of 213** on this pod (`corpus-slice.py`, four slices, stamp
written for engine `d28ca7516c3f9165`), which is what the commit gate needs and what the previous runs
recorded as their blocker. `regress.py --check` now returns **PASS** - "docx: no document worse than
baseline; txt: no document worse than baseline; google-safe: no construct Google ignores has spread" -
in seconds instead of timing out at 200 s on an unbuilt corpus. The pre-commit hook is installed.

That is a pipeline unblock, not a document moved: **0 documents became clean in this run.** Recorded as
`lead`.

## 6. Not done

* No Google render, no `.docx` measurement: this run's whole measured surface is the `.txt` half.
* The corpus-wide `t01` counterfactual in §4.
* `regress.py --check` was run to PASS on the tree as committed, but the `.docx` numbers it compares are
  the stored ones - no document was re-measured in Google this run.
