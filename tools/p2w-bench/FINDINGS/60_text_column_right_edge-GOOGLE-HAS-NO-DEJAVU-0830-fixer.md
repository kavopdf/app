# `60_text_column_right_edge`: four of its five single-check documents fail because Google has no DejaVu

**Measured 24 Nov 2026, fixer slot 07:57.** Engine `b7699196`, built in-sandbox from this tree.
Every Google number below is a live round trip (upload → `GOOGLEDRIVE_CREATE_FILE` as a Google Doc
in `KavoPDF-Verify` → `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE` → `gverify.py --collect`). The probe
Doc was deleted after the measurement; nothing outside the folder was touched.

## The question

Five documents fail **only** `60_text_column_right_edge` — 5 clean documents if it can be fixed:
`302_radiology_report`, `313_power_of_attorney`, `316_contract_with_schedules`,
`321_auditors_report`, `79_inr_indian_digit_grouping_table`. All five are 41/42 (316 is 46/47).

## 1. Four of the five are already correct in LibreOffice

All five converted on the current engine, rendered with LibreOffice, and scored against their own
source PDF with the unmodified `verify_google.py`:

| document | LibreOffice | Google (committed) |
|:--|:--|:--|
| `302_radiology_report` | **42/42 PASS** | 41/42, fails 60 |
| `313_power_of_attorney` | **42/42 PASS** | 41/42, fails 60 |
| `316_contract_with_schedules` | **42/42 PASS** | 46/47, fails 60 |
| `321_auditors_report` | **42/42 PASS** | 41/42, fails 60 |
| `79_inr_indian_digit_grouping_table` | 41/42, fails 60 | 41/42, fails 60 |

So the class is **two disjoint things**, exactly as `18_displacement` turned out to be:

* **A — the Google-only half** (4 documents). The proxy says the render is right; Google disagrees.
* **B — the shared half** (`79` only). Fails in both renderers, so the engine really is wrong there
  and it can be iterated locally. `79`'s failing column was located: page 0, column left 132.3,
  source right edge 289.97 pt, render right edge **149.70 pt**, slack (one word) 17.72 pt — the render
  stops 140 pt short of a line the source draws. That is `79`'s own defect and it is not the subject
  of the rest of this file.

## 2. The Google-only half is a font substitution, measured

One live round trip on `302_radiology_report` (the hardest of the four: it is the only one that also
carries two source families).

| | source PDF | LibreOffice | **Google** |
|:--|:--|:--|:--|
| pages | 1 | 1 | 1 |
| text lines on page 0 | **33** | 33 | **35** |
| first line width, pt | **257.62** | 257.41 | **270.00** |
| embedded faces | DejaVuSans, DejaVuSans-Bold, DejaVuSerif, Helvetica | DejaVuSans, DejaVuSans-Bold, DejaVuSerif | **Calibri, Calibri-Bold, Verdana, Verdana-Bold, ArialMT** |

The `.docx` declares `w:ascii="DejaVuSans"` (27 runs) and `w:ascii="DejaVuSerif"` (6 runs) — the
source's own faces. **LibreOffice has DejaVu and renders it: 33 lines, first line 257.41 pt, the
source's width to 0.2 pt.** **Google has no DejaVu**, substitutes a face it does have, and the
substitute is **+4.8 % wider** (270.00 against 257.62), which re-breaks page 0 into **two more
lines**, which moves the column right edges — by up to **28.6 pt** on one column (source 174.28,
Google 202.82) — and `60` convicts the movement.

`60`'s slack is one word of the column's own text, and a face 4.8 % wider widens the word too, so the
slack grows with the fault instead of absorbing it. That is why the check cannot pass it.

The declared faces of all five, read back from `word/document.xml`:

| document | declared | source PDF embeds | Google has it |
|:--|:--|:--|:--|
| `302_radiology_report` | DejaVuSans, DejaVuSerif | DejaVuSans, DejaVuSerif | **no** |
| `313_power_of_attorney` | DejaVuSerif | DejaVuSerif | **no** |
| `316_contract_with_schedules` | DejaVuSans, DejaVuSerif | DejaVuSans, DejaVuSerif | **no** |
| `321_auditors_report` | DejaVuSerif | DejaVuSerif | **no** |
| `79_inr_indian_digit_grouping_table` | Arial, Times New Roman | Liberation Sans, Liberation Serif | yes |

`79` is the one document in the five that names faces Google **does** have — and it is the one that
fails in LibreOffice too. The four that name DejaVu are the four that fail **only** in Google. That
is the split, and it is four for four.

## 3. Naming a face Google has is not the fix — the two renderers want opposite things

Probe: the same `302` `.docx`, `word/document.xml` hand-edited so the only change is
`DejaVuSans → Verdana` and `DejaVuSerif → Georgia` (both in Google's library). No engine rebuild, so
the probe measures the name and nothing else.

| | source | `302` as built (LO) | probe `Verdana/Georgia` (LO) |
|:--|--:|--:|--:|
| text lines, page 0 | 33 | 33 | 33 |
| first line width, pt | 257.62 | 257.41 | **227.63** |
| faces LibreOffice renders | DejaVu | DejaVu | **NotoSans, NotoSerif** |

LibreOffice has no Verdana either, so it substitutes Noto, and the render is **11.6 % narrower** than
the source — a worse document in the renderer that used to be exact. The check still passes 42/42 in
LibreOffice (a uniform narrowing is inside `60`'s slack), which is the point: **the proxy cannot see
this fault in either direction.**

So the choice is binary, and it is the same shape as the spacer half of `18_displacement`:

* name the source's face → LibreOffice exact, **Google substitutes and re-breaks**;
* name a face Google has → **Google closer to uniform**, LibreOffice substitutes and the render is no
  longer the source's face at all.

No font **name** can satisfy both, because no face in Google's library is metrically DejaVu.

## 4. Google ignores an embedded font, so there is no construct left — measured

The `.docx` for `302` was rebuilt with the source's two faces **embedded** in the package
(`word/fontTable.xml` + `word/fonts/font1.odttf` / `font2.odttf` carrying DejaVuSans.ttf and
DejaVuSerif.ttf, `w:embedRegular` on both `<w:font>` entries, `<w:embedTrueTypeFonts/>` and
`<w:saveSubsetFonts/>` in `settings.xml`, plus the content-type and relationship parts). Uploaded,
converted and exported as a Google Doc, same as every other measurement here:

| | source | as built, in Google | **embedded face, in Google** |
|:--|--:|--:|--:|
| text lines, page 0 | 33 | 35 | **35** |
| first line width, pt | 257.62 | 270.00 | **270.00** |
| faces in the export | DejaVuSans, DejaVuSerif | Calibri, Verdana, ArialMT | **Calibri, Verdana, ArialMT** |
| `60_text_column_right_edge` | — | FAIL | **FAIL** |

**The export is the same render.** Google did not read the embedded faces: the same three substituted
families, the same 35 lines, the same 270.00 pt first line. `GOOGLEDRIVE_EXPORT_GOOGLE_WORKSPACE_FILE`
returned 81,521 bytes against 81,526 for the unembedded build — 5 bytes, i.e. the substitution is
identical and only the container metadata differs.

So the binary in §3 has no third arm: **a `.docx`-embedded face is not a construct Google honours.**

## 5. What this means for the class

1. **The four Google-only documents cannot be moved by any construct in the `.docx`.** Not by a font
   name (§3, measured both ways) and not by an embedded face (§4, measured in Google). This is a
   **`Google cannot do it`** verdict, and it is the third of the three places a defect can live.
2. **Do not work them as a layout class.** Nothing in the engine's column model is wrong: the columns
   in LibreOffice are the source's columns to 0.2 pt, and the engine declared the source's own face.
3. **`79` is the one document here with an engine defect**, and it is reproducible locally in both
   renderers. Its failing column is named in §1. Take that one; the other four are parked.
4. **The honest close for the four is an attribution, not a check change made to pass them.** They
   should be read as `53_embedded_faces`' residual — that check currently PASSES them, because the
   engine did declare the right face and the substitution is the renderer's. Whether `60` should
   therefore exclude a column whose re-break is fully explained by a face the renderer does not have
   is a decision with a measurement behind it now, and it is the next run's to take. **It is not a
   loosening of `60` for the four documents in isolation — any such change must be stated as a rule
   about extent-versus-substitution and re-measured on the whole class.**

## What would prove this wrong

* A Google Doc exported from a `.docx` that names `DejaVuSans`, or carries it embedded, whose PDF
  export carries `DejaVuSans` rather than Calibri/Verdana/Arial. **Tried and refuted in §4 for the
  embedded case; the naming case is what §2 and §3 measure.**
* A face name that both renderers resolve to DejaVu metrics (then §3's binary is false).
* A `302` whose Google export has 33 lines on page 0 and a first line of 257.6 pt while still failing
  `60` — that would put the fault back in the engine.
