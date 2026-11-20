# Two source-side repairs for t01, measured, and why only one of them is worth keeping

**Measured 20 Nov 21:45-21:55 on the 213 freshly converted documents. Neither is committed.**

Both repairs are on the SOURCE side of `verify_txt.py`, both can only remove source tokens,
and both were restamped over the whole corpus with `restamp_txt.py --run --force` (49 s).

## 1. One line drawn twice is one line - REJECTED, it is a trade

Faux bold is a stroke drawn again at the same place. On `38_faux_bold_italic_synthesised`
the trace carries `PROJECT REPORT - CIVIL` three times and `Study of self-compacting...`
three times, at **identical bboxes**, while `get_text()` declares the first twice. The
`.txt` writes each once, so t01 read 4 lost words of 201 (98.0) for a writer that was
right. The repair collapsed a consecutive trace span whose `(text, bbox)` matched the
previous one to within 0.5 pt - the same tolerance `PdfToWord.dedupe()` uses - and
consumed its copy from the declared string.

    t01   98.0 -> PASS
    t12   PASS -> FAIL, 10 invented words: study, self-compacting, concrete, using,
          quarry, dust, as, partial, replacement, of

It does not work, and the reason is the useful part. **The two lines are not the same
shape.** The heading is over-counted by the source (trace 3, declared 2, .txt 1) and the
abstract line is not (trace 3, declared 2, .txt 2). Neither the trace nor the declaration
can tell them apart - both carry three spans at one bbox and two declared copies - so a
rule that collapses duplicates fixes t01 on the heading and breaks t12 on the abstract. The
corpus says the same thing from the other side: `text-held-twice-shadow-text` newly FAILS
t12 under this rule, which is a document whose duplicated text the `.txt` correctly writes
twice.

Full-corpus result of the rule: **0 newly clean, 1 newly failing.** A trade, and the gate
refuses trades. Do not re-try this without a rule that can separate the two lines, and
note that the `.txt` writer's own answer is positional, which is exactly what the trace
does not give here (every copy has the same bbox).

## 2. A widget's value is counted once, wherever it was read - CORRECT, NOT ENOUGH, NOT COMMITTED

`glyph_truth()` appends each widget's `/AP` text to the page text, on the stated ground
that "the filled values `get_text()` never reads". On this PyMuPDF `get_text()` DOES read
them, from the appearance stream, so every filled value was counted twice - source 2,
`.txt` 1 - and a `.txt` that writes the value once, correctly, was charged a lost word per
field. The repair is one condition:

    if t.strip() and t.strip() not in walked:      # was: if t.strip():

Measured on `Account_Opening_Form_Fillable_filled`: eight values - jalapur, hsjw862,
Gautam, 12/01/2000, 25/10/1999, 8469164578494949, jsw246444946, 726bwksii - each present
in the `.txt` exactly once, each read as source 2 / txt 1. That is 18 of the document's 145
lost tokens.

   601_fillable_admission_form        96.4 -> 97.6   still FAIL
   Account_Opening_Form_Fillable_filled 98.1 -> 98.2  still FAIL
   full corpus: 0 newly clean, 0 newly failing

It is correct, monotone, and moves no document past the 99 % bar on its own, so it is
recorded as reverted rather than landed - an unproven change in the tree is what the
ledger exists to prevent. **Land it with the engine fix below, not before it.**

## What is left in this class, with numbers

| document | t01 | what it needs |
|:--|--:|:--|
| `Account_Opening_Form_Fillable_filled` | 98.1 | the engine `/ToUnicode` fix (127 U+FFFD) + the widget fix above -> 99.76 |
| `041122-Account_Opening_Form` | 98.2 | the engine `/ToUnicode` fix alone -> 99.95 |
| `601_fillable_admission_form` | 96.4 | the widget fix gets 97.6; the remaining 2 lost tokens are field values the writer drops |
| `38_faux_bold_italic_synthesised` | 98.0 | rejected above - it is a t01/t12 trade, not a fix |
| `39_small_caps_letter_spacing` | 97.4 | source and writer disagree on word boundaries inside letterspaced runs: source `57 0 0 05`, .txt `570 005`; source `N O . 4,`, .txt `N O. 4,` |
| `77_arabic_rtl_document` | 92.1 | **no character-level difference at all** (source-only characters: none). Same characters, different token boundaries - RTL order, not text |
| `411_nested_xobject_transforms` | 90.0 | the page draws rotated text, so `get_texttrace` yields `S` and `O` on separate lines; the `.txt` writes `SO`, which is the better answer. 20 source words, so 2 lost is 90 % |

### The engine fix, and why it did not happen this run

`041122` and its filled variant carry **127 tokens with U+FFFD** where the source declares
U+0124/U+0126/U+0123. That is the engine failing to read `/ToUnicode` for
`REAQAG+Effra-Regular` (Type0 / Identity-H) and falling back to the replacement character.
Fixing it takes both documents to 99.95 % and 99.76 % and is the single largest win left
in this class. It was not attempted here because the same mapping feeds `DocxWriter`, so
it moves the docx engine fingerprint and `regress.py --check` then demands a full docx
re-measure - 213 documents of rendering, which this slot did not have. **Give it a whole
slot and it is two documents.**
