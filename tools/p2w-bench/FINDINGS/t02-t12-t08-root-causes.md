# t02, t12, t08 — what each one is actually measuring

Found 19 Nov by the agent, offline, no `java`, no engine build. Every number below came from
`verify_txt.py` run against the 213 `.txt` files in `/scratch/work/p2w/out` and the corpus PDFs.
Two of the four findings are bugs **in the checks**, not in the writer, and both are fixed.

---

## t12 — two of its fifteen failures are the check's own fault

`t12_word_invention` counts words the `.txt` carries that the source never drew:

    src_w = Counter(_strip_punct(w) for w in _words(src_text))
    txt_w = Counter(_strip_punct(w) for w in _words(txt_text))
    invented = sum((txt_w - src_w).values())

### The empty-token bug — FIXED

`_strip_punct` strips `.,;:!?()[]{}"'…-` from both ends of a token. **A token made only of those
characters strips to the empty string, and the empty string was then counted as an invented word.**

Measured on `balance-sheet-and-profit-loss`, whose two "invented words" were both `''`: the `.txt`
carries an em dash standing alone exactly where the page draws one, and the check condemned the
document for it. `balance-sheet-two-columns-of-figures` the same.

The fix drops empty results before counting. Both documents now report **0 invented words** and
pass t12.

### The five real causes, from the remaining thirteen

Read off the actual invented words, not guessed:

| document | invented | what it is |
|:--|:--|:--|
| `05_round_company_seal_curved_text` | `i`, `n`, `t` | a curved seal's text is one run on the page and three tokens in the `.txt` — a **word-segmentation** fault on curved text |
| `12_stamp_across_page_break` | `kunigal`, `12`, `aug`, `2025`, `sub-registrar` | the stamp. The page draws it; `glyph_truth` does not see it, so the `.txt` "invents" text the page really has. **A source-side miss, not a writer fault** |
| `311_fir_police_form` | `60067mobile` | two table cells joined with no space. **The table-row fix (`PATCH-t13-table-row-per-line`) changes this path and must be re-measured on this document** |
| `78_mixed_english_devanagari_line` | `क`, `ेवल`, `पंजीक`, `ृत` | Devanagari clusters split mid-word — the page's `केवल` arrives as `क` + `ेवल`. A **shaping** fault |
| `journal-2col-with-footnotes` | `2`, `cent`, `1`, `incorrectly`, `3`, `hard` | footnote markers and a wrapped word (`per cent` split across a line) |
| `392_statistical_console_output` | `0.8412`, `adjusted` | a number and a word wrapped across a line |
| `406_passport_mrz_page` | `photograph` | a form label the source extraction misses |

**So t12 is four different faults wearing one name**: segmentation on curved text, source-side
misses, Devanagari shaping, and line-wrap word splitting. A single fix cannot clear it, and two of
its fifteen were never real.

---

## t02 — the ruler cannot model a proportional font, and the error grows with x

`t02_position` derives one character width `mid` from the source/txt line pairs and asks what share
of lines have `abs(col - round(x/mid)) <= 2`. It passes at 90 %.

Measured across the failing documents — **in every one, the lines that fail sit further right than
the lines that pass:**

| document | pairs | mid | failing x range | passing x range |
|:--|--:|--:|:--|:--|
| `310_court_judgment` | 27 | 6.299 | 261–519 | 57–191 |
| `315_gazette_notification` | 35 | 4.000 | 211–474 | 28–225 |
| `334_patent_document` | 32 | 5.600 | 120–426 | 28 |
| `58_header_rule_footer_rule` | 21 | 6.222 | 424–503 | 56 |
| `magazine-2col-pullquote-spanning` | 42 | 5.669 | 306–452 | 45–207 |
| `policy-2col-spanning-section-heading` | 61 | 5.669 | 308–540 | 51–81 |
| `417_rotate180_and_mirrored` | 8 | 7.000 | 333–379 | 56–277 |

`58_header_rule_footer_rule` is the clearest case: its passing lines are all at x=56, its failing
lines are the two right-aligned running heads at x=423.53 and x=503.06, placed 3 columns right of
where one global width predicts.

**A proportional font has no single character width.** The body text at the left margin dominates
the fit, and a line 400 pt to its right is explained 4–5 % off — 3 to 4 characters. The writer's own
`charW` and the check's `mid` are two estimates of a quantity that does not exist.

**This is a measurement-model defect.** A writer that placed every line perfectly would still fail
these documents. The fix is in the check, and it must be principled — a tolerance that grows with x,
a fit per x-band, or the writer's own ruler published alongside the `.txt`. **Loosening the
tolerance uniformly would hide real defects and is not the fix.**

`310_court_judgment` fails at 89 against a 90 bar — **one line**.

---

## t08 — zero tolerance, and six of eight fail by exactly one line

`t08_line_order` compares, per column bucket, the order of lines whose text is unique on both sides,
using an LCS. It passes only when `in_order == partners` — **100 %, no tolerance.**

| document | partners | in order | short by |
|:--|--:|--:|--:|
| `305_vaccination_certificate` | 33 | 32 | **1** |
| `330_cad_drawing_sheet` | 34 | 33 | **1** |
| `400_comic_page_speech_bubbles` | 20 | 19 | **1** |
| `09_stamp_font_not_embedded` | 16 | 15 | **1** |
| `70_magazine_drop_cap_photo_caption` | 21 | 20 | **1** |
| `itr-computation-with-slab-table` | 88 | 87 | **1** |
| `65_two_col_full_width_figure_caption` | 47 | 42 | 5 |
| `46_chart_coloured_labels_body_text` | 43 | 37 | 6 |

**Six of the ten fail by a single line out of 16 to 88.** Against the 99 % bar the user set, 1 of 88
is 98.9 % — under it — so the check is not wrong to fail them, but it is worth knowing that the
defect on those six is one displaced line, not a broken document.

The displaced lines the instrument points at are the **first lines of the document** in the cases
sampled — a running head or a firm name. That is consistent with a heading being emitted after the
first body block rather than before it. **Not yet confirmed on a rendered page; the fixer should
confirm before acting on it.**

---

## What is fixed and what is not

| finding | state |
|:--|:--|
| t13 `got[0]` — the same amount token in two columns both resolved to its first position | **FIXED** in `verify_txt.py`, proven on `390_wide_data_appendix` (4 → 19 columns preserved, and the .txt is genuinely aligned) |
| t12 empty token counted as an invented word | **FIXED**, proven on both balance-sheet documents |
| t02 proportional-font ruler | **diagnosed, not fixed** — it is a check redesign, not a patch |
| t08 zero tolerance | **diagnosed, not fixed** — the fix is a decision about the bar, not a bug |
| t12's four writer-side faults | **diagnosed with examples**, each needs its own work |

**Both fixes change the `.txt` universe hash**, so `RATCHET-TXT.json` no longer matches and the
whole corpus has to be re-stamped before any of these numbers can be quoted. Do the re-stamp in one
pass and record the before/after, or the two fixes and the re-stamp cannot be told apart.
