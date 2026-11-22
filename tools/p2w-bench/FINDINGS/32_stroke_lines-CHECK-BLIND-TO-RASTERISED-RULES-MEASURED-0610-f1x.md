# 32_stroke_lines — the check was blind to rules Google rendered as images. Measured, fixed.

**Slot 05:56 · 22 Nov 2026 · fixer · class `32_stroke_lines` (36.5 clean documents, the largest lever)**

## The measurement

Six documents, converted with `ConvertOne` at HEAD (`462353f9`), uploaded to
`KavoPDF-Verify` as Google Docs, exported back as PDF, scored, probe documents deleted.
The export PDFs are Google's own output — nothing here is a LibreOffice proxy.

| document | before | after | what changed |
|:--|:--|:--|:--|
| `394_map_with_legend` | 41/42 FAIL | **42/42 PASS** | 3 lost rules → 0 |
| `17_three_column_widths_txtpos` | 41/42 FAIL | **42/42 PASS** | 2 lost rules → 0 |
| `315_gazette_notification` | 41/42 FAIL | **42/42 PASS** | 5 lost rules → 0 |
| `407_id_card_front_back` | 41/42 FAIL | 41/42 FAIL | 46 lost rules → 8; still loses its card borders |
| `311_fir_police_form` | 42/47 FAIL | 43/47 FAIL | 32 now passes; 4 Google checks still fail |
| `382_architecture_diagram` | 42/42 PASS | 42/42 PASS | clean control, held |

Before and after are the same command on the same export PDF, and the before column was
re-taken with the pre-change file so the comparison is not against a remembered number.

## The full measurement — 20 documents

Six documents first (the two that failed `32_stroke_lines` alone, two that failed
`{05,32}`, a clean control, and one with rules but other failures). The result was clear
enough to spend the rest of the slot on the fourteen documents that failed exactly
`{05_chars_extra, 32_stroke_lines}`:

| | |
|:--|:--|
| documents re-measured through Google | **20** |
| clean at HEAD, from the committed table | **7** of 192 |
| clean after this change, measured | **23** of 192 |
| documents that flipped to 42/42 | **16** |
| documents that got worse | **0** |
| probes left in Drive | **0** — all 20 deleted |

The 16: `17_three_column_widths_txtpos`, `18_centred_heading_left_body_txtpos`,
`19_hanging_indent_txtpos`, `24_address_block_indents_txtpos`,
`26_footnote_marker_bottom_note_txtpos`, `315_gazette_notification`,
`32_serif_nondefault_body`, `334_patent_document`, `34_monospace_document`,
`37_font_not_embedded_substitution`, `394_map_with_legend`, `45_coloured_callout_box`,
`47_grey_body_black_headings`, `53_single_space_body_15_headings`,
`74_balance_sheet_indented_subitems`, `product-catalogue-code-left-price-right`.

Thirteen of the fourteen `{05,32}` documents came back 42/42. `05_chars_extra` passed on
all fourteen — the table's record of it is stale, which the 05:14 run already suspected
from three documents and this run confirms on fourteen more.

Still failing on 32: `49_coloured_background_block_paragraph` (41/42) and
`407_id_card_front_back`. `407` is the real engine loss described below.

## What the check was doing

`verify_google.py:_rule_segments()` reads `page.get_drawings()` — vector paths only.
`_stroke_pictures()` already existed in the same file, was already called by `_strokes()`,
and was never called by `_rule_segments()`. So a rule that Google rendered perfectly but
exported as an image read as **zero** segments and was counted LOST.

Google Docs exports an anchored shape as a small raster image at the shape's own
geometry. From the exports of this run, printed straight out of `page.get_image_info()`:

    394_map_with_legend   rule y=691.89 x 395.28..415.28 t=1.6  ->  image 21.00 x 2.25 at (394.9, 690.7)
                          rule y=707.89 x 395.28..415.28 t=3.0  ->  image 21.00 x 3.75 at (394.9, 706.0)
    315_gazette           5 source rules, 5 image bands, each at its own coordinates
    17_three_column       2 source rules, 2 image bands, each at its own coordinates

Every rule the check called LOST was present in the document the user opens. The check
was not measuring the document; it was measuring the export's encoding.

## The change

`_rule_segments(page, band=None, pictures=False)` gains an image-band pass, threaded
through `_rules` / `_doc_rules`. Check 32 alone passes `pictures=True`, with
`band=RULE_BAND_REN` — the same width limit the vector path uses.

That width matters: `_stroke_pictures()` was hardcoded at 1.5 pt, and two of
`394_map_with_legend`'s three rules are 2.25 pt and 3.75 pt. At 1.5 pt the fix recovers
1 of 3 and the document still fails; at `RULE_BAND_REN` it recovers 3 of 3. A 3 pt rule
counted when Google drew it as a vector band and not when Google drew it as an image band
would be the instrument contradicting itself, so the two limits are now the same number.

Also removed a duplicated `c["32_stroke_lines"] = ...` assignment in `extra_checks()`.

## Why no document can get worse

The change only ADDS render segments. `_rules_lost()` matches 1:1 greedily by nearest
perpendicular residual, and the verdict is `not s_lost`. More candidate segments can only
match more source rules, never fewer. `regress.py --check` passes and
`google-gate.sh` passes; neither was relied on for this argument.

## What this does not fix

`407_id_card_front_back` is a real loss, not an instrument one: 46 source rules, 18 image
bands, and its card borders (a 228 pt horizontal at y=220, x 46..274) are in none of them.
That is the engine construct — a rule emitted as a floating `<w:drawing>` that Google
drops — and it needs `w:tcBorders` on a 1×1 floating table carrier, not a check change.

## Correction to the brief's denominator

`311_fir_police_form` is recorded 42/42 in `benchmarks/gverify/` and measures 43/47 here:
`--docx` makes five more checks applicable, and they were not applied when that row was
written. Rows with different `total` values are not comparable, and the "all 42 checks"
in the charter is a per-document denominator that varies from 42 to 47.
