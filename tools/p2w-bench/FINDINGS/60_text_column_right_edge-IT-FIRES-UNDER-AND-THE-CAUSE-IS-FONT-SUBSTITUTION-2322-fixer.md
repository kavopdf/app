# 60_text_column_right_edge — it fires UNDER, not over, because Google substitutes the font: DejaVu declared, Arial rendered

**23 Nov 2026 · fixer slot 18:58 → · engine unchanged · live Google round trips this slot**

## What the check actually says

`verify_google.py:2673` reports **two** numbers, not one:

```python
c["60_text_column_right_edge"] = (over, under, over == 0 and under == 0)
# source = pages whose column overruns the source's
# render = pages whose column is narrower than the source's
```

All four documents report **`source=0 render=1`**. That is `over=0, under=1` — the check is firing on
the **UNDER** branch (`rg < rs - RIGHT_UNDERRUN - slack`, `:2668`). **The render's text column is
NARROWER than the source's.** Every reading of this class as "text runs past the right edge" is
backwards.

## The geometry, measured on the four documents

Re-implemented the check's own `columns()` / `edge()` and ran it against the exports from this slot:

| document | source edge | render edge | delta | slack | branch |
|:--|--:|--:|--:|--:|:--|
| `302_radiology_report` col@28 | 543.7 | 478.1 | **−65.6** | 32.7 | under |
| `313_power_of_attorney` | 538.6 | 480.1 | **−58.5** | 40.0 | under |
| `321_auditors_report` | 538.6 | 473.0 | **−65.6** | 28.5 | under |

Two unrelated documents land on the **same −65.6 pt**. A layout defect does not repeat to the tenth of
a point across a radiology report and an auditor's report; a constant does.

## The constant is a font substitution

`w:pgSz` is A4 and `w:pgMar` is **all zeros** on all three documents, so the text area is the whole page
and the margin is not the cause. The font is:

| document | font declared in the .docx | font Google rendered | median line width |
|:--|:--|:--|:--|
| `313_power_of_attorney` | `DejaVuSerif` | `ArialMT` / `Arial-BoldMT` | 432.0 → **372.9** |
| `321_auditors_report` | `DejaVuSerif` | `Arial-BoldMT` | 227.4 → **193.2** |
| `316_contract_with_schedules` | `DejaVuSans` | `Arial-BoldMT` | 163.1 → **138.0** |
| `302_radiology_report` | `DejaVuSans` + `DejaVuSerif` | `ArialMT` | 81.9 → 83.7 (mixed) |

The writer emits **DejaVuSerif / DejaVuSans** correctly. Google Docs does not have that family and
substitutes **Arial**, which is 10–15 % narrower at the same point size. Every line therefore wraps
earlier, the column's widest line comes up short by 58–66 pt, and `60_text_column_right_edge` fires
**under** on four documents that have no column problem at all.

**This is a font-substitution defect wearing a layout check's name.** It is the same root as
`53_embedded_faces` and it is invisible to `45_char_accuracy` and `10_font_sizes`, which is why these
documents pass everything else.

## Why this matters more than the four documents

`60_text_column_right_edge` is worth **17.0 clean documents** — third in the leverage table — and it
appears in 4 of the 8 common failing shapes. If the mechanism is a font family Google does not carry,
then the class is not 17 layout bugs; it is one font-selection decision, and the same decision is
likely present in every document whose source uses DejaVu.

## The test the next run should make, and it is one round trip

The engine has to choose between two things and nothing in the repo has measured which is right:

1. **Embed the face** (`fontTable.xml` `w:embedRegular`) so Google imports DejaVu rather than
   substituting. Unmeasured whether Google Docs honours docx font embedding.
2. **Declare a family Google has whose advance widths match DejaVu.** Arial is 15 % narrow. The
   candidate is whichever installed Google family measures closest to DejaVu Serif at 10 pt —
   measurable locally against the source PDF's own advance widths before anything is uploaded.

Measure (2) locally first: take `313_power_of_attorney`, compute the advance width of its widest source
line in DejaVu Serif and in each candidate family, and pick the family within 1 %. Then one round trip
says whether the column edge closes. **No engine change was made this attempt — 0 moved, recorded as
`lead`.**
