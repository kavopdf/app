# 05_chars_extra was counting Google's tabs: one U+200B per `<w:tab/>`, 141 of 192 documents

**21 Nov 2026 · relay slot 23:19 → · verifier change only, no engine change, no .docx change**

## The answer, first

`05_chars_extra` failed 141 of the 192 scored documents because Google's PDF export writes **one
`U+200B` ZERO WIDTH SPACE for every `<w:tab/>` in the .docx**. The document does not contain that
character. The page does not draw it — it is zero width. The exporter marks a tab *advance* with it.

The check is zero-tolerance on the character multiset, so every tab in the engine's output was one
"character added", and the class it has been blamed for — "the rule's anchor becomes a stray U+200B" —
was the wrong reading of the same symptom. The anchor story is true for a *rule* document; it is not
what the 141 were failing on.

## The census, on all 192 scored documents

`<w:tab/>` counted in each document's own `word/document.xml`, engine built at HEAD `44abc5d` +
`patches/rule-carrier-per-rule-2008.patch`, all 213 converted with `ConvertAll`; `failed` read from
`benchmarks/gverify/*.json`.

| | documents | with tabs > 0 | with tabs == 0 |
|:--|--:|--:|--:|
| **fails** `05_chars_extra` | 141 | **141** | **0** |
| **passes** `05_chars_extra` | 51 | **0** | **51** |

Not one exception in either direction. The separation is total, so the population the check was
failing and the population carrying a tab are the same set.

## Causal, not correlated — one document, one variable

`17_three_column_widths_txtpos` has 23 `<w:tab/>` and read 23 extra characters. Its own `.docx` was
copied with **only** the 23 `<w:tab/>` elements deleted, nothing else touched, and both were uploaded
to Google Docs and exported:

| uploaded | extras over the source text layer |
|:--|:--|
| 23 tabs | **`{'U+200B': 23}`** |
| 0 tabs | **`{}`** |

And in the first export the 23 spans are exactly where tab stops are: `x=75.4` at the left margin and
`x=440–467` at each right-hand stop, one per line of the timetable.

The same exact 1:1 held on every document measured by hand: `17` 23/23, `74` 8/8, `73` 2/2, `53` 1/1,
`45` 1/1, `51` 0/0, `394` 0/0.

## Why this is the instrument and not the engine

* A tab is a legal, correct construct and it is the only way the writer positions a run at a column.
  There is no Google-safe replacement that keeps the position.
* The character has no ink. `_strokes()` and the whole render side already refuse to count what the
  page never drew; `05` counted a character the page never drew.
* The fix is symmetric — stripped from **both** multisets — so it can only ever remove a disagreement.
  It cannot hide missing text (`04_chars_missing` reads the other side) and it cannot mask a
  duplicated line (a duplicate adds real characters).

`U+200C` / `U+200D` are deliberately **not** stripped: they are ZWNJ/ZWJ and they shape Indic text, so
a difference in them is a real difference in the document.

## The change

One regex in `norm_text()` (`verify_google.py:311`): `\u200b` and `\ufeff` added to the stripped
class. `norm_text` is used by 04 and 05 only; no other check and no `.txt` check reads it.

## Before and after, on 11 documents measured through Google in this slot

Google Docs render → PDF export → the 42 checks. Engine at HEAD + `rule-carrier-per-rule-2008.patch`.

| document | before | after | |
|:--|--:|--:|:--|
| `45_coloured_callout_box` | 41/42 | **42/42** | **CLEAN** |
| `394_map_with_legend` | 42/42 | 42/42 | stays clean |
| `51_two_cm_margins` | 42/42 | 42/42 | stays clean |
| `17_three_column_widths_txtpos` | 40/42 | 41/42 | `32` left |
| `18_centred_heading_left_body_txtpos` | 40/42 | 41/42 | `32` left |
| `19_hanging_indent_txtpos` | 40/42 | 41/42 | `32` left |
| `24_address_block_indents_txtpos` | 40/42 | 41/42 | `32` left |
| `26_footnote_marker_bottom_note_txtpos` | 40/42 | 41/42 | `32` left |
| `53_single_space_body_15_headings` | 40/42 | 41/42 | `32` left |
| `74_balance_sheet_indented_subitems` | 40/42 | 41/42 | `32` left |
| `73_marksheet_subject_marks_grade` | 39/42 | 40/42 | `18`, `32` left |

`05` cleared on 11 of 11. **No document's count went down.** `test_checks.py` 44/44 unchanged.

## What this does not do

It does not make a document clean **on its own**: on the 192 committed results, no document fails only
`05`. It is a correction that removes a false signal from 141 documents and leaves the real one
(`32_stroke_lines`) standing alone, which is what makes the next fix measurable.

## What it hands the next run

`45_coloured_callout_box` is now clean only because the carrier patch was in the tree while it was
measured. With `32` as the last check on 7 documents in the table above, the whole class is one
construct away — and the reason they still fail is in
`FINDINGS/32_stroke_lines-ONE-OF-TWO-CARRIERS-IS-PLACED-2350-relay.md`.
