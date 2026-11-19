# Google Docs honours no character-width control — measured, four ways

Source: `310_court_judgment.pdf` (1 p, DejaVu Serif) and `01_stamp_rotated_15deg_upright.pdf`
(1 p, Liberation Serif). Engine as committed at `bb7a33f`. Renderer measured: Google Docs, via
Drive — upload .docx, copy as `application/vnd.google-apps.document`, export as PDF.

## Why this file exists

`FINDINGS/content-missing-partly-replaced-FONT-143300-b7e2.md` established, on 14 Nov, that
**LibreOffice honours `<w:w>` and ignores `<w:fitText>` and an embedded `.odttf` part**. That finding
is correct and it was re-read today and re-tested. It is also about **LibreOffice**, and the pipeline
is supposed to be measured by Google. So the same three mechanisms were tested against Google, plus
`<w:spacing>`, because the whole question is whether a substitute face can be made to occupy the
width the page drew.

**It cannot.** Google Docs ignores every one of them.

## Result

`310_court_judgment`, DejaVu Serif in the page, Noto Serif in the .docx (no Google serif is as wide:
DejaVu sets the same heading at 342.5 pt, Noto at 299.5, Liberation at 292.3):

| variant | Google share@5px | mean long-line width (page: 428.4 pt) |
|---|---:|---:|
| as the engine emits it (DejaVu -> Arial) | 16.28 % | 380.1 |
| `<w:spacing w:val="19"/>` (0.95 pt per character) | 15.16 % | 380.1 |
| `<w:w w:val="114"/>` (character scaling, the LibreOffice answer) | 15.16 % | **380.1 — no effect** |
| `w:sz` x 1.1436 (font size, so the width matches) | 19.82 % | 436.6 — matches, and scores worse |

The third row is the one that matters. `<w:w w:val="114"/>` is honoured by LibreOffice - the same
document renders 446.6 pt wide there instead of 428.4 - and Google ignores it completely: the
exported PDF is byte-for-byte the same layout as without it. `<w:spacing>` likewise. An embedded
font part is likewise ignored (the 14 Nov finding, and Google does not even accept the part).

Font size does move the width, and that is why it scores **worse**: matching the width by growing the
face also grows the glyphs 14 % taller, and share@5px then fails vertically instead of horizontally.

## What this means, stated plainly

A PDF set in a face Google Docs does not have **cannot be reproduced faithfully in Google Docs**, and
there is no docx construct that fixes it. The face is the reader's choice and the reader offers no
override.

Which faces are affected, by how many of the 213 documents:

| source face | docs | Google has it? | note |
|---|---:|---|---|
| Helvetica | 135 | yes (-> Arial) | metric-compatible |
| Liberation Serif | 72 | no -> **Times New Roman** | metric-identical, already mapped |
| Liberation Sans | 56 | no -> **Arial** | metric-identical, already mapped |
| DejaVu Sans | 68 | **no** | no metric match |
| DejaVu Serif | 35 | **no** | no metric match; 12 % wider than any Google serif |

The engine already maps Liberation Serif/Sans (they are what `BASE14` has done all along), so those
128 documents are already correct. **DejaVu - 103 documents - is the part with no answer inside the
.docx.**

## Ruled out — do not retry

- `<w:w>` for Google: no effect at all, though it works in LibreOffice.
- `<w:spacing>` for Google: no effect.
- Embedded TrueType font part: ignored (14 Nov, LibreOffice; Google does not accept it).
- `<w:fitText>`: ignored (14 Nov).
- Scaling `w:sz` to match the width: matches the width and scores worse.

## CORRECTION - the pixel number overstated this, and the 42 checks are the instrument

The share@5px figures above (16.28 % against 1.39 %) read as if the document were 16 % wrong. It is
not. `verify_google.py` runs 42 named checks and it says:

| document | LibreOffice | Google Docs |
|---|---|---|
| `310_court_judgment` | **42/42 PASS** | 39/42 - `43_within_10pt_x`, `47_margins`, `60_text_column_right_edge` |
| `01_stamp_rotated_15deg_upright` | 41/42 - one check | 34/42 - seven checks |

So the renderer difference is **3 checks and 7 checks**, not 16 % of the page. share@5px is a
per-pixel measure and a face that is 12 % narrower moves a great deal of ink a little, which scores
badly without the layout being wrong. **Use the 42 checks. Do not quote share@5px for a cross-renderer
comparison again** - it is the right instrument for one renderer against itself and the wrong one for
two renderers against each other.

The difference is still real and still the point: LibreOffice calls 310 perfect and Google does not.

## Still unexplained

`01_stamp_rotated_15deg_upright` is set in **Liberation Serif**, which the engine maps to **Times New
Roman** - a face Google has and is metric-identical with. It scores:

    LibreOffice  2.09 %
    Google Docs 14.14 %

**14 % with the right font.** That is not substitution. Something else moves the ink in Google's
layout and it is worth more than the DejaVu problem, because it affects every document, not 103 of
them. Finding it is the next step; the DejaVu question is second.

## What would prove this wrong

A Google export of `310_ww.docx` (kept at `/scratch/output/310_ww.docx` while it existed) whose mean
long-line width is nearer 428 than 380. It is 380.
