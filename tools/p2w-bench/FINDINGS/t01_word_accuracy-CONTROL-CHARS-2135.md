# t01_word_accuracy - a control character is a separator, not a word

**Measured 20 Nov, 21:35. Kept. 3 of 10 t01 documents, plus a fourth that was failing t12 only.**

## What the ten documents actually lose

Each of the ten was converted with this tree's engine and its lost tokens listed against
`verify_txt.py`'s own source side. They are not one defect - they are at least five:

| document | t01 before | lost | what the lost tokens are |
|:--|--:|--:|:--|
| `79_inr_indian_digit_grouping_table` | 91.9 | 15/185 | 15 tokens that are `\x00` and nothing else |
| `391_survey_questionnaire_grid` | 97.5 | 2/80 | `Strongly\x00agree`, `DisagreeStrongly\x00disagree` |
| `406_passport_mrz_page` | 98.5 | 1/68 | `\x00\x00\x00\x00\x00\x00\x00\x00PHOTOGRAPH` |
| `392_statistical_console_output` | - (t12 only) | 1/135 | `0.8412,\x00Adjusted` |
| `041122-Account_Opening_Form` | 98.2 | 131/7448 | 127 tokens carrying U+FFFD where the source declares U+0124 |
| `Account_Opening_Form_Fillable_filled` | 98.1 | 145/7471 | the same 127, plus 18 form values the source counts twice |
| `38_faux_bold_italic_synthesised` | 98.0 | 4/201 | `PROJECT`, `REPORT`, `CIVIL`, `-` - a heading the page draws twice |
| `39_small_caps_letter_spacing` | 97.4 | 8/306 | single characters and two numbers, `0`, `O`, `D`, `57`, `05` |
| `601_fillable_admission_form` | 96.4 | 3/83 | `3` twice and `General` - form values |
| `77_arabic_rtl_document` | 92.1 | 8/101 | RTL tokens that join a word to a digit, `2قهوة`, `:إجمالي` |
| `411_nested_xobject_transforms` | 90.0 | 2/20 | `S` and `O` |

## The three that were the instrument's fault

`_words()` tokenised with `r"\S+"`. A PDF declares U+0000 for any glyph it has no Unicode
for - the space between two words of a survey row, the bullet in a table, the empty cells
of an MRZ band. `\S` treats U+0000 as an ordinary character, so

* `Strongly\x00agree` became ONE token that no .txt can ever contain;
* `\x00\x00\x00\x00\x00\x00\x00\x00PHOTOGRAPH` welded a word to eight declaration gaps;
* a lone `\x00` became a "word" that is not a word.

A `.txt` cannot carry U+0000 - it is not a character a text file has. So every such token
was a guaranteed lost word on every document that declares one, and t01 was failing these
documents for the file format's limits rather than for the writer's fidelity.

**Splitting is the repair, not dropping.** The glyph sits where a SPACE sits, so
`Strongly\x00agree` is two words the page drew. Dropping the NUL would yield
`Stronglyagree`, which is not on the page either.

    def _words(s):
        return re.findall(r"\S+", _CTL.sub(" ", s or ""))

`_CTL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")`. U+000C is in the class because
`_txt_lines` has already split the .txt on the page separator, so a form feed reaching
`_words` is a stray.

## Proof it cannot regress

`glyph_truth()` was run over all **213** documents. Exactly **6** declare a control
character inside a source token: the three above plus `392_statistical_console_output`,
`balance-sheet-and-profit-loss` and `balance-sheet-two-columns-of-figures`. The change
alters the word list of those six and no other, and it only removes source tokens - it
adds none - so `lost` can only fall.

Full restamp, `restamp_txt.py --run --force` over 213 freshly converted documents:

    213 scored | 4 documents newly clean, 0 newly failing, 209 unchanged

    391_survey_questionnaire_grid         no longer fails t01_word_accuracy, t12_word_invention
    392_statistical_console_output        no longer fails t12_word_invention
    406_passport_mrz_page                 no longer fails t01_word_accuracy, t12_word_invention
    79_inr_indian_digit_grouping_table    no longer fails t01_word_accuracy

Clean 182 of 213 (85.4 %) -> 186 of 213 (87.3 %). `test_txt_checks.py` 8/8 before and after.
`regress.py --check` PASS.

`391` and `406` improve on **t12** as well, for the same reason: a token made of U+0000 was
being counted as a word the writer had invented.

## What is left, and it is not this

The other seven are not one construct and this change reaches none of them:

* **041122 and the filled variant** - 127 tokens reach the .txt as U+FFFD where the source
  declares U+0124/U+0126/U+0123. That is the ENGINE failing to read the font's `/ToUnicode`
  for `REAQAG+Effra-Regular` (Type0/Identity-H), not a tokeniser question. Fixing it takes
  both to 99.95 % and 99.76 % and needs a docx re-measure, because the same mapping feeds
  `DocxWriter`.
* **the filled variant and 601** - `glyph_truth()` appends each widget's `/AP` text to
  `get_text()`, and on this PyMuPDF `get_text()` already returns the appearance-stream
  text, so every filled value is counted twice. 18 of the filled form's 145 lost tokens.
  Measured: removing the append takes it 98.1 -> 98.2 and 601 96.4 -> 97.6 - correct, and
  not enough on its own to pass either.
* **38_faux_bold** - the page draws the heading twice at a 0.3 pt offset; the source counts
  both, the .txt writes one. Needs the same 0.5 pt duplicate suppression on the source side
  that `PdfToWord.dedupe()` already applies on the engine side.
* **77_arabic, 39_small_caps, 411** - not diagnosed. `77` has no character-level difference
  at all (source-only characters: none), so it is token boundary and order on RTL, not text.
