# t08_line_order was reading paint order, not reading order - confirmed by falsification, fixed

**Measured 21 Nov 21:47-21:53 IST. Verifier change only; no engine change, no .docx change.**

## The question the last run left

"Judge the t08 verifier question before touching the engine: is t08_line_order measuring line order or
drawing order? The agent's proposed one-line sort of `_src_pages` is NOT obviously right - it would
compare sorted-vs-sorted."

## The answer, with the falsification both ways

`t08` built its ground truth as `src_seq` - every upright line of `_src_pages(src_pdf)` in the order
PyMuPDF returned it. `_src_pages` sorts nothing: that is the page's CONTENT-STREAM order, i.e. the order
the PDF painted its glyph runs. The check then scored `difflib.SequenceMatcher` against the `.txt`
within each column bucket. So it asked the `.txt` to reproduce the painter's order and called the result
line order. Its own ABOUT string said as much: "lines arrive in the order the page drew them".

Two falsifications, run on `46_chart_coloured_labels_body_text` (whose axis is painted bottom-up):

| case | .txt | before | after |
|:--|:--|:--|:--|
| real output | engine's .txt, correct reading order | **FAIL 37/43** | **PASS 43/43** |
| swapped | two lines of the SAME column deliberately transposed | PASS | **FAIL 42/43** |
| real output | `39_small_caps_letter_spacing` - source paints y=65.11 BEFORE y=52.64 | PASS | **FAIL** (a real inversion, now caught) |

The second row is the one that matters: after the change the check still fires on a genuinely inverted
`.txt`. It is not quiet, it is not comparing sorted-with-sorted.

`39_small_caps` is the only document that gains a failing check, and the source proves it is a real
fault: the PDF paints the doubled heading "T H E M Y S O R E..." at y=52.64 *after* the line at
y=65.11, and our `.txt` follows the paint order. The check now catches that. The document already
failed t01 and t12, so nothing that was clean became dirty.

## The change

Four lines inside the t08 block only - sort each page's upright lines by `(round(y,1), x)` before
extending `src_seq`, page-major. `_src_pages` itself is untouched, so t09 and t13 (whose amount list is
deliberately in draw order) cannot move.

The flat whole-document sort the sub-agent proposed is rejected on its own measurements: it interleaves
pages (a correct two-page synthetic FAILS 7/10; `041122` reads 351/461, worse than before).

## Before and after, all 213 documents

Corpus rebuilt from `corpus-v1` + `benchmarks/realworld` (the 2 documents the release does not carry),
engine built at HEAD `2975f84`, 213 of 213 converted with ConvertAll, scored with `restamp_txt.py --run
--force`.

| | before | after |
|:--|--:|--:|
| clean .txt (every applicable check passes) | **190** | **197** |
| documents failing t08_line_order | **10** | **2** |
| documents improved | - | **9** |
| documents newly clean | - | **7** |
| documents newly failing a check | - | **1** (`39_small_caps`, real inversion, already failing) |
| documents that got worse in clean/not-clean terms | - | **0** |

The seven that became clean: `09_stamp_font_not_embedded`, `330_cad_drawing_sheet`,
`400_comic_page_speech_bubbles`, `46_chart_coloured_labels_body_text`,
`65_two_col_full_width_figure_caption`, `70_magazine_drop_cap_photo_caption`,
`itr-computation-with-slab-table`. Two more improved but stay open on other checks:
`041122-Account_Opening_Form` and `Account_Opening_Form_Fillable_filled` (4 -> 3).

**Cross-check that the instrument reproduces before it is trusted:** the unpatched verifier, run on the
same freshly converted corpus, reproduced `RANKING-TXT.csv` exactly - 211 unchanged, and the only two
differences were the two documents the corpus release does not carry, which were missing rather than
mismeasured.

## What this is not

It is not an engine fix and it moves no Google number. The .docx half is untouched (0 bytes changed;
the verifier is not in the conversion path). The remaining t08 failures are `305_vaccination_certificate`
(a seal-ring paragraph with no `y`, so it cannot be ordered) and `39_small_caps_letter_spacing` (the
TxtWriter emits the doubled heading in paint order - that one is a real engine bug worth a slot).
