# 00_page_count: 21 of the 23 unscored documents are right in LibreOffice and wrong in Google

**Measured 24 Nov 2026, fixer slot claimed 00:56 IST.** Corpus fetched fresh (213 PDFs),
engine built from HEAD (`b97d8172ce642eb0`), every number below from a run in this pod.

## The class, counted from the record

`benchmarks/gverify/*.json` carries `status=page_count_refused` on **23 of 213** documents.
A refused document is not scored at all: all 42 Google checks are skipped, so these 23 are
invisible to the whole pipeline. `classpick.py --leverage` prices the class at **23.0 clean
documents**, second only to `18_displacement`.

| | |
|---|---|
| 1-page source rendered as 2 by Google | **21** |
| 9-page source rendered as 14 by Google | **2** (the two bank forms) |

## The measurement that matters

I converted all 23 on the HEAD engine (`ConvertOne`), rendered every `.docx` through
LibreOffice, and counted pages against the source PDF:

| | LibreOffice | source PDF | Google (from the record) |
|---|---|---|---|
| 21 documents | **1** | 1 | **2** |
| 041122-Account_Opening_Form | 10 | 9 | 14 |
| Account_Opening_Form_Fillable_filled | 11 | 9 | 14 |

**21 of 23 are the correct number of pages in LibreOffice and one too many in Google.** The
LibreOffice proxy - which is what the corpus pass, the ratchet and `regress.py` all read -
cannot see this defect on 21 documents. This is non-negotiable #1 with a number on it, not
a caution.

## "A few points of overflow" is refuted

If the cause were content reaching the bottom edge, the page's bottom slack would be small.
Measured on the LibreOffice render, bottom-most ink against the 841.9 pt page:

| document | bottom-most ink | slack |
|---|---|---|
| 350_question_paper | 838.50 pt | **3.39 pt** |
| 60_page_border | 823.95 pt | **17.94 pt** |
| 305_vaccination_certificate | 783.60 pt | **58.29 pt** |

`305_vaccination_certificate` has **58 pt of slack** and still costs Google a second page.
So the general cause is not the last line spilling: it is something Google charges that
LibreOffice does not, and the size of it varies by document. A fix aimed at "trim a few
points off the bottom" would reach 350 and nothing else.

## The trailing-paragraph hypothesis is also refuted, for the group

The obvious candidate is an anchor-only paragraph at the end of the body paying a line box
Google honours and LibreOffice does not. Counted over all 23: the last body paragraph holds
1 `w:drawing` on **7** documents, but 21-400 drawings on the other **16** (405_sheet_music
has 144 drawings in 13 paragraphs). There is no single trailing-paragraph construct.

What the two families do share is that the ink is **mostly anchored shapes**: 16 of the 23
draw more shapes than they draw text lines.

## One construct is already named, and it is real

`00_page_count-350-INLINE-PICTURE-CARRIES-THE-LINE-1120-agent.md` charges
`DocxWriter.java:2549` for `350`: an inline picture paragraph emitted with **no `w:pPr` at
all**, so it inherits `stylesXml()`'s docDefaults - an **11 pt paragraph mark plus 6 pt
`w:after`** - on a page that is already one paragraph tall. `spacingTw()` cannot see it,
because it sums only `w:before`, `w:line` and `w:trHeight`.

That is one document's construct and it is checkable. It is **not** evidence for the other
20: 350's last paragraph is one of the 7 with a single drawing, and the other 6 in that
family are not inline-picture pages.

## What the next run should do

Do not spend a slot on "page count" as one thing. Split it, because the record already
splits it and the split is now measured:

1. **`350_question_paper` (3.39 pt slack, inline picture, no `w:pPr`)** - apply the patch
   beside the finding above and re-run `gverify` on 350 alone. One document, falsifiable.
2. **`305_vaccination_certificate` (58.29 pt slack)** - this one cannot be an overflow at
   all. It is the cleanest probe for "what does Google charge that LibreOffice does not",
   precisely because there is 58 pt of room for the answer to live in.
3. The two bank forms are a **different** class: they are wrong in LibreOffice too (10 and
   11 against 9), so they are a genuine engine pagination fault and belong with
   `18_displacement`, not here.
