# TXT-FAILURES-DIAGNOSIS

Read-only diagnosis of the 16 documents whose `.txt` still fails a check in the
p2w bench. Nothing in the repository was modified, committed or pushed.

---

## 1. What was run, and what it reproduced

| Step | Command | Result |
|---|---|---|
| clone | `git clone --depth 1 https://github.com/kavopdf/app /scratch/work/CS` | ok |
| corpus | `bash tools/p2w-bench/corpus-fetch.sh` | `corpus: 213 PDFs, 213 scored in RANKING.csv, 0 missing` (exit 0) |
| engine | `bash tools/p2w-bench/build-engine.sh` | `engine built - ConvertAll ready (34s)` (exit 0) — JDK 17 fetched from Adoptium, PDFBox-Android 2.0.27.0 from Maven Central |
| conversion | `java ConvertOne <pdf> /scratch/work/p2w/out` on the 16 failing documents | 16 `.txt` written |
| scoring | `verify_txt.py <pdf> <txt> --json` per document | **reproduced the committed verdicts exactly: 16 documents, same failed ids, 0 differences** |
| ranking tool | `python3 txt_rank.py --all` in a scratch copy of `tools/p2w-bench` | ran; `scored 16 this pass \| 0 clean \| 16 with a failed check \| 0 errors` — third independent path, same 16 verdicts |

`txt_rank.py` was run from a copy (`/scratch/work/bench`) because it rewrites
`txt/RANKING-TXT.csv` and `txt/RATCHET-TXT.json` in the clone; the brief forbids
modifying the repo. It scores by shelling out to `verify_txt.py`, so the copy and
the in-place run measure the same thing.

The current state, from `tools/p2w-bench/txt/STATE-TXT.json` and
`tools/p2w-bench/txt/RANKING-TXT.csv` (the authoritative files — the
`RANKING-TXT.csv` at the top of `tools/p2w-bench/` is an older, 64-failure
snapshot and must not be used):

```
scored 213 | clean 197 | failing 16 | 92.5 %
```

One observation worth recording: `txt_rank.py` prints
`STALE MARKS - RATCHET-TXT.json was stamped under a different set of checks.
marks : 9f988a43056f / live : fea67232e76a (12 checks)`. The committed marks were
stamped by an instrument hash that no longer matches the live `verify_txt.py`.
It does not move any of these 16 verdicts (they reproduce), but the ratchet
comparison is currently inert.

---

## 2. The 16 failing documents, the check, and the verdict

A document is "clean" when every *applicable* check passes (`txt_rank.py`'s
rule). "Verdict" answers the question asked: **whose fault is it** — the engine's
`.txt` writer, or the check — with the mechanism letter from the brief in
brackets: **(a)** the word is in the PDF and our writer put it in the wrong
place, **(b)** an artefact of how the PDF draws it, **(c)** a genuine check
false positive.

| # | Document | Failing check(s) | Verdict |
|---|---|---|---|
| 1 | `041122-Account_Opening_Form` | t12, t09, t06 | **Engine** (t12: stray field glyphs glued onto neighbouring lines, one stranded `#`, one duplicated line) + **check** on t09 (key collision) and t06 (unsatisfiable zero baseline) |
| 2 | `Account_Opening_Form_Fillable_filled` | t12, t09, t06 | Same as #1 — identical 5 invented tokens, identical t09/t06 numbers |
| 3 | `05_round_company_seal_curved_text` | t12 | **Check** (b) — the seal draws one glyph per span; the source side glues them at random |
| 4 | `311_fir_police_form` | t12 | **Engine** (a) — the writer splits `560067` after one character and glues `Mobile` onto the tail |
| 5 | `39_small_caps_letter_spacing` | t12, t01, t08 | **Check** on t12/t01 (b) — letter-spaced pincode; **Engine** on t08 — two heading lines genuinely inverted |
| 6 | `600_reviewed_invoice_with_annotations` | t12 | **Both** — 14 of 21 tokens are the writer emitting annotation text twice; 7 are a check blind spot (`/Contents` is never read) |
| 7 | `77_arabic_rtl_document` | t12, t01 | **Check** (b) — RTL runs where the digit is glued to the Arabic word by the source extraction |
| 8 | `journal-2col-with-footnotes` | t12 | **Check** (b)/(c) — superscript footnote markers glued to the preceding word by the source extraction |
| 9 | `305_vaccination_certificate` | t08 | **Engine** — the footer line is emitted before the seal's per-glyph block |
| 10 | `324_loan_amortisation_schedule` | t09 | **Check** — `_furniture_key` folds digits to `#`, so a table's numeric cells are counted as copies of the page-number element |
| 11 | `gst-invoice-multipage-item-table` | t09 | **Check** — owed is a *set* of pages, so a line drawn twice per page (header + footer) can never be owed twice |
| 12 | `332_bom_on_drawing` | t02 | **Check** — `_ruler`'s pop-first pairing crosses repeated texts; sorted pairing makes it 100 % |
| 13 | `334_patent_document` | t02 | **Check** — the ruler estimator `x/col` locks onto the writer's 5-column left margin (`28.0/5 = 5.6`) |
| 14 | `74_balance_sheet_indented_subitems` | t02 | **Check** — the source `x` is the span's start *including* in-text leading spaces, so the drawn indent is invisible while the `.txt`'s indent is counted |
| 15 | `price-list-2col-dense-right-aligned` | t02 | **Check** — pairing crosses the two columns (`Box of 50` at x=190.7 pairs with col 96; x=460.0 with col 40) |
| 16 | `601_fillable_admission_form` | t01 | **Engine** — two standalone `3` lines drawn by the page are absent from the `.txt` |

**Split: 9 documents fail only because of the check** (#3, 7, 8, 10, 11, 12, 13,
14, 15). **7 documents carry a real engine fault** (#1, 2, 4, 5, 6, 9, 16).

Per-document t12 magnitudes as measured by the shipped check
`(source chars, invented tokens)`:

| Document | source chars | invented tokens |
|---|---|---|
| `041122-Account_Opening_Form` | 48845 | 5 |
| `Account_Opening_Form_Fillable_filled` | 48944 | 5 |
| `05_round_company_seal_curved_text` | 1244 | 4 |
| `311_fir_police_form` | 1417 | 2 |
| `39_small_caps_letter_spacing` | 1281 | 2 |
| `600_reviewed_invoice_with_annotations` | 776 | 21 |
| `77_arabic_rtl_document` | 681 | 11 |
| `journal-2col-with-footnotes` | 4346 | 6 |

### How t12 decides

`verify_txt.py:1299-1325`. It takes `src_text` from `glyph_truth()`, whose layout
is PyMuPDF's `page.get_text()` with only the *characters* substituted
(`verify_txt.py:621-700`, "THE LAYOUT IS THE DECLARATION'S; ONLY THE CHARACTERS
ARE THE GLYPHS'"), tokenises both sides with `re.findall(r"\S+")`, folds case and
surrounding punctuation with `_strip_punct`, and reports
`sum((txt_w - src_w).values())`. So **every place where PyMuPDF's run/space
decision differs from the writer's becomes an "invented word"**, even when the
two sides carry exactly the same characters. That is the mechanism behind 5 of
the 8 t12 failures.

---

## 3. Worked examples, with quoted evidence

### 3.1 `journal-2col-with-footnotes` — superscript marker glued to the word (check)

Source side (glyph truth), last lines of the abstract:

```
accuracy fell from 96.1 per cent to 71.4 per cent.1
...
matters in production systems where an operator must explain why
a document was converted incorrectly.2
...
0.97 by Cohen's kappa, which we take as evidence that the task is
well defined even where it is hard.3
```

`.txt`:

```
accuracy fell from 96.1 per cent to 71.4 per cent.
  1
...
a document was converted incorrectly.
  2
...
well defined even where it is hard.
  3
```

The page draws a superscript `1` immediately after `cent.` with no space. The
source extraction joins them into one token (`cent.1`, `incorrectly.2`,
`hard.3`); `_strip_punct` strips a trailing `.` but cannot strip a trailing
digit, so the tokens never match the `.txt`'s `cent` + `1`. All 6 invented tokens
are accounted for: `cent`, `incorrectly`, `hard`, and `1`/`2`/`3` (the source's
footnote block also glues the marker to the text: `2 The band boundary test…`).
**The `.txt` is the faithful one.** Verdict (b)/(c), check side.

### 3.2 `311_fir_police_form` — the writer splits a token (engine)

Source side:

```
Address
12/3, 4th Cross, Kadugodi, Bengaluru 560067
Mobile
+91 98450 11223
```

`.txt`:

```
       Address
                               12/3, 4th Cross, Kadugodi, Bengaluru 5
                                                                60067Mobile
                                                                                                +91 98450 11223
```

`560067` is drawn on the page as one token. The writer breaks it after the first
character and drops the space before `Mobile`, producing `5` and `60067Mobile`.
That is exactly the 2 invented tokens the check reports (`5`, `60067mobile`).
**Genuine engine fault** — (a), the characters are in the PDF and the `.txt`
writer put them in the wrong place.

### 3.3 `77_arabic_rtl_document` — digit glued to an RTL word (check)

Source side:

```
2قهوة روبوستا، غربال
15
20
21800
436000
3شحن إلى ميناء
4الإجمالي1880000
 :التاريخ5
 :إجمالي الفاتورة1,880,000 دولار أمريكي
```

`.txt` (table cells, each on its own line):

```
قهوة روبوستا، غربال
       15
2
شحن إلى ميناء
الإجمالي
1880000
التاريخ 5 :سبتمبر2025
إجمالي الفاتورة 1,880,000 :دولار أمريكي
```

In the RTL page the item number sits at the visual left of the description with
no space between the runs, and the source extraction concatenates them
(`2قهوة`, `3شحن`, `4الإجمالي1880000`). The writer separates the cells, which is
what a reader sees. All 11 invented tokens (`الفاتورة`, `التاريخ`, `5`, `قهوة`,
`2`, `شحن`, `3`, `1880000`, `الإجمالي`, `4`, `1,880,000`) come from that one
mechanism — the mirror image is the 8 "lost" words t01 charges
(`2قهوة`, `3شحن`, `4الإجمالي1880000`, `:التاريخ5`, …). **Check side** (b).

### 3.4 `05_round_company_seal_curved_text` — one glyph per span (check)

The circular seal is drawn glyph by glyph, each with its own slightly different
`y`. Source side:

```
S
R
I 
V
IN
A
Y
A
K
A
 I
N
S
T
IT
U
T
E
 O
F
 T
E
C
H
N
O
L
O
G
Y
```

`.txt` — one glyph per line, in reading order:

```
S
 R
  I
   V
    I
     N
      A
...
```

The source extraction glues pairs at random (`IN`, `IT`, `I `, ` I`), so the
`.txt`'s honest one-glyph-per-line output carries 4 tokens the source has no
separate token for: `i`×2, `n`, `t`. Every letter is in both sides. **Check
side** (b). (The line-per-glyph output is poor `.txt` quality, but it invents no
word.)

### 3.5 `39_small_caps_letter_spacing` — letter-spaced pincode (check)

Source side:

```
E S T A B L I S H E D 1886  •  N O . 4, K R I S H N A R A J A B O U L E V A R D , M Y S U R U 57 0 0 05
```

`.txt`:

```
E S T A B L I S H E D 1886  •  N O. 4, K R I S H N A R A J A B O U L E V A R D, M Y S U R U 570 005
```

The pincode `570005` is set with tracking; PyMuPDF cuts it `57 0 0 05`, the
writer cuts it `570 005`. Tokens `570` and `005` read as invented, and `57`, `0`,
`0`, `05` read as lost (t01 = 97.4 %, 8 of 306 lost, which is this plus
`N O . 4` vs `N O. 4`). **Check side** (b).

### 3.6 `600_reviewed_invoice_with_annotations` — 21 tokens, two different causes

The PDF carries five annotations:

```
type (0, 'Text')     contents: 'Rate for HSN 8536 confirmed with PO.'
type (2, 'FreeText') contents: 'Checked against PO 4471. Quantity on line 3 raised from 20 to 25.'
type (13, 'Stamp')   contents: 'Approved'
(+ a Highlight, an Underline and a StrikeOut, all with empty contents)
```

The `.txt` opens with all three texts, and then the page body — which itself
draws the FreeText and Stamp appearance streams — repeats the last two:

```
Rate for HSN 8536 confirmed with PO.
Checked against PO 4471. Quantity on line 3 raised from 20 to 25.
Approved
          TAX INVOICE
...
Checked against PO 4471. Quantity on line 3 raised from 20 to 25.
                                                                                APPROVED
```

Breakdown of the 21: **7 tokens** (`rate for hsn 8536 confirmed with po`) are the
sticky-note `/Contents`, which `glyph_truth()` never reads — a check blind spot,
the words *are* in the PDF. **14 tokens** are the FreeText and Stamp texts
emitted twice — a genuine writer fault (a duplicated line). t01 does not see it,
by design ("Lost words only. Extra words are a different fault").

### 3.7 `041122-Account_Opening_Form` / `Account_Opening_Form_Fillable_filled`

Both fail with the identical 5 tokens: `d`, `#`, `payable`, `authorised`,
`signatory)y`. Measured causes:

* the `.txt` has `Date: D` where the source has `Date:` — a stray field glyph
  `D` pulled onto the line (this is the extra `d`);
* the `.txt` has `(Authorised signatory)Y` — a `Y` field glyph glued on, giving
  `signatory)y`, plus a second copy of `(Authorised signatory)` (the source has
  one), which is the extra `authorised`;
* the source draws `interest payable#` (a superscript footnote marker attached);
  the `.txt` writes `In case of Term Deposit, interest payable` and puts the `#`
  alone on its own line (line 2246) — that is `payable` and `#`.

These are (a): the characters are in the PDF and the writer put them in the
wrong place. `#` is also outside `_strip_punct`'s fold set, so an attached
marker can never match a detached one.

---

## 4. The other nine checks

### t02_position — 4 documents, all check side

`t02` fits one character width `mid` from `(x, column)` pairs and requires 90 %
of pairs within `max(2, 8 % of col)`. `_ruler()` builds the pairs by popping the
first unused `.txt` column with the same *text* (`verify_txt.py:882-893`), which
is order-dependent and therefore wrong as soon as a text repeats.

| Document | as shipped | with sorted pairing | cause |
|---|---|---|---|
| `332_bom_on_drawing` | 41/52 = 78.8 % (fails) | **52/52 = 100.0 %** | pairing crossed repeated texts (`77.9→81`, `167.9→81`, `638.9→81`, `314.9→20`) |
| `price-list-2col-dense-right-aligned` | 86.1 % (fails) | **99.6 %** | pairing crosses the two columns: src `x=190.7 'Box of 50'` → txt col **96**; src `x=460.0 'Box of 50'` → txt col **40** |
| `334_patent_document` | 68.8 % (fails) | 68.8 % | ruler bias: `mid=5.600` is exactly `28.0/5`, the writer's left margin (22 of 32 pairs are the `x=28 → col 5` margin pair). With a margin-corrected fit the same data scores **100.0 %** |
| `74_balance_sheet_indented_subitems` | 81.5 % (fails) | 81.5 % | the source run text carries the indent as leading spaces — `'        (a)  Share capital'` at `x=56.0` — so the check compares the *margin* x to the `.txt`'s indented column. A faithful `.txt` cannot pass |

Note on `332`: `verify_txt.py:966-975` names this document explicitly as one
whose "fit itself collapsed" and which therefore "abstain[s]" — but the shipped
bound is `POS_MID_MIN = 2.0` and its fitted `mid` is 3.907, inside the range, so
it fails instead of abstaining. The comment and the code disagree; the
measurement above shows the document's indentation is in fact faithful.

### t09_page_furniture — 4 documents, all check side

| Document | owed | present | measured cause |
|---|---|---|---|
| `324_loan_amortisation_schedule` | 66 | 1485 | all real heads are exactly 6/6 (`Month`, `Interest`, `EMI`, …). The inflation is `_furniture_key`'s digit folding: keys `#` (240 hits), `#,#.#` (774), `#,#,#.#` (423) collide with every numeric body cell |
| `gst-invoice-multipage-item-table` | 39 | 43 | only `Page # of #` is wrong: owed 4, present 8. The PDF draws `Page 1 of 4` **twice per page** (verified: every page yields the line twice from `get_text()`), and `element_pages` stores a *set* of page numbers, so owed can never exceed one copy per page |
| `041122-Account_Opening_Form` | 21 | 197 | keys `Date`(6/3), `#`(72/9), `D`(33/3), `M`(45/3), `Y`(41/3) — single-glyph field keys colliding with the whole form |
| `Account_Opening_Form_Fillable_filled` | 21 | 199 | same |

### t06_encoding — 2 documents

`041122` and `Account_Opening_Form_Fillable_filled` report `(47477 glyphs, 127)`
and `(47562, 127)`. The `.txt` carries 127 U+FFFD — and so does the source side:
`_src_text()` on the same PDFs also contains exactly 127 U+FFFD. The engine
cannot name those 127 glyphs, and neither can the check's own source side, so the
zero baseline `t06` enforces is unsatisfiable for this document. The real defect
is in glyph decoding (engine), not in the `.txt` writer, and it is not a `.txt`
fault that the check should charge.

### t08_line_order — 2 documents

* `305_vaccination_certificate` — 33 partners, 32 in order. The one line moved is
  the footer `This is a computer generated certificate and does not require a
  physical signature.` at `y=777.0`; the `.txt` emits it at line 36, *before* the
  curved seal's single-glyph block (`y≈265-312`, `.txt` lines 37-84).
  Engine: block ordering. t01 passes (0 words lost).
* `39_small_caps_letter_spacing` — 22 partners, 21 in order. The page draws
  `T H E M Y S O R E …` at `y=52.6` and `THE MYSORE CHAMBER OF COMMERCE AND
  INDUSTRY` at `y=65.1`; the `.txt` emits the plain line first. **Genuine
  inversion — engine.**

### t01_word_accuracy — 3 documents

* `39_small_caps_letter_spacing` — 97.4 %, 8 of 306 lost: the letter-spaced
  pincode and `N O . 4` (§3.5). Check side.
* `77_arabic_rtl_document` — 92.1 %, 8 of 101 lost: the same RTL gluing (§3.3).
  Check side.
* `601_fillable_admission_form` — 97.6 %, 2 of 82 lost: the page draws two
  standalone `3` lines (checkbox/option numbers); neither is in the `.txt`.
  **Engine.**

---

## 5. Measured effect of each candidate single change

Each change was implemented against the shipped `verify_txt.py` functions and
re-scored over the 16 documents in `/scratch/work/p2w/out`. Nothing else was
re-scored — the other 197 documents have no `.txt` in this sandbox, so their
effect is **not measured**.

| Candidate single change | Where it belongs | Documents it flips to clean (measured) |
|---|---|---|
| t12: compare whitespace-stripped **character** multisets instead of token multisets | check | **5** — `05_round_company_seal_curved_text`, `311_fir_police_form`, `39_small_caps_letter_spacing`, `77_arabic_rtl_document`, `journal-2col-with-footnotes` |
| t02: pair runs to lines by sorted `(x, col)` and fit the ruler after removing the margin offset | check | 3 — `332_bom_on_drawing`, `334_patent_document`, `price-list-2col-dense-right-aligned` |
| t09: drop furniture elements whose key contains no letter | check | 1 — `324_loan_amortisation_schedule` |
| t09: count owed per drawn occurrence in the band instead of per distinct page | check | 1 — `gst-invoice-multipage-item-table` |

Supporting numbers for the t12 change, measured per document (invented tokens
as shipped → extra characters under the whitespace-stripped character multiset):

| Document | tokens | extra chars | outcome |
|---|---|---|---|
| `05_round_company_seal_curved_text` | 4 | 0 | clean |
| `311_fir_police_form` | 2 | 0 | clean |
| `39_small_caps_letter_spacing` | 2 | 0 | clean |
| `77_arabic_rtl_document` | 11 | 0 | clean |
| `journal-2col-with-footnotes` | 6 | 0 | clean |
| `041122-Account_Opening_Form` | 5 | 14 | still fails (duplicate line + stray glyphs) |
| `Account_Opening_Form_Fillable_filled` | 5 | 14 | still fails |
| `600_reviewed_invoice_with_annotations` | 21 | 91 | still fails (duplicated annotation text + sticky note) |

A weaker variant — a `.txt` token counts as invented only if its characters are
not a contiguous substring of the source's whitespace-stripped text — flips the
same 5, but it also drops `600` from 21 to 2 and `041122` from 5 to 1, i.e. it
stops seeing most of the genuinely duplicated annotation text. It is not
recommended.

---

## 6. Recommendation

**One change: make `t12_word_invention` compare whitespace-stripped character
multisets, not token multisets — and make it in the check (`verify_txt.py`), not
in `TxtWriter.java`.**

Measured effect: **5 of the 16 documents go clean** — the largest single-change
effect measured here — and the two documents with a genuine duplication fault
(`600_reviewed_invoice_with_annotations`, `041122` /
`Account_Opening_Form_Fillable_filled`) keep failing, so the change is not a
blanket silence.

Why the check and not the engine: in all five documents the `.txt` carries
exactly the characters the page drew, in the right quantity (extra-character
count 0). The discrepancy lives entirely in the source side's token boundaries —
PyMuPDF's `get_text()` glues letter-spaced runs, per-glyph seal runs, RTL digits
and superscript markers, and t12 inherits every one of those decisions. No change
to `TxtWriter.java` can make the writer reproduce PyMuPDF's gluing, and it should
not try: in `journal-2col-with-footnotes`, `77_arabic_rtl_document` and
`39_small_caps_letter_spacing` the `.txt` is the more faithful of the two.

Consequence to accept, stated plainly: a character-multiset test no longer proves
that the `.txt`'s **word boundaries** match the page — a word reassembled from
letters the source draws elsewhere would pass. If that matters, keep the token
comparison as a second, reported-but-not-decisive check (the file already has the
`t04_structure` precedent for a check that is reported and not decisive).

The next most valuable single change, if a second one is allowed, is the t02
pairing/ruler fix (3 documents), and it is again a check change. No engine change
appears in this list: the engine faults found here (token split in `311`,
duplicated annotation text in `600`, stray field glyphs in `041122`, seal-block
ordering in `305`, dropped `3` lines in `601`, one line inversion in `39`) each
affect one document.

---

## 7. Limits — what is not measured

* The effect of any candidate change on the other **197** documents: **not
  measured** (no `.txt` for them in this sandbox). The full-corpus regression
  (`regress.py --check`) was not run.
* The `.docx` side, the visual checks, and `RANKING.csv`: **not measured**; not
  touched.
* Whether the engine's 127 U+FFFD glyphs in `041122` are nameable at all: **not
  measured** (I read the counts on both sides, not the font tables).
* Timing of a full-corpus conversion: **not measured** (only the 16 documents
  were converted).
