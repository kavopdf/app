# `32_stroke_lines`: the check cannot see a rule Google drew as a picture

Read-only investigation plus two Google round trips. No engine file was edited, `verify_google.py`
was not edited, no table was restamped. This records a **measurement defect** and the exact patch
that fixes it, not a corpus fix.

## The one paragraph

`_rule_segments()` (`verify_google.py:1082`) walks `page.get_drawings()` and nothing else. Google Docs
exports **every anchored shape in a `.docx` as one raster image**, and `get_drawings()` returns vector
paths, so a rule Google drew perfectly reads as **zero segments** on the render side and is scored
LOST. The file already knows this - the comment above `_strokes()` says so in capitals ("AND THE
RENDER SIDE HAS NO VECTOR PATHS AT ALL, 13 Nov") - and `_stroke_pictures()` (`:906`) was written to
fix it, and `_strokes()` (`:856`) does call it. But `_rule_segments()` was written later, is the path
check 32 actually uses, and never calls it. `_strokes()` returns `{rect,width,colour}` and
`_rule_segments()` returns `{o,perp,a,b,t,col}`, so the two were never merged: a picture band has no
`perp`, no `a..b` and no `t`, and merging them naively raises `KeyError: 't'`.

## Falsification, in both directions, on Google's own exports

Ten probe `.docx` were uploaded to Google Docs, exported as PDF and kept. `rule-base.docx` asks for no
rule at all; `rule-v6_pgborder.docx` uses `w:pgBorders`, which Google drops outright. Those two are the
negatives - a correct instrument must still call them LOST. `rule-v1_drawing.docx` is the **engine's own
construct** (`DocxWriter.shape()`: a filled rect inside `<wp:anchor behindDoc="1">` in its own one-twip
carrier paragraph); `rule-v1b_inline.docx` is the same anchor moved inside a body paragraph.

Source rule used for all six: horizontal, y = 140.0 pt, x 72.0 -> 523.0, 0.75 pt.

| Google export | construct | BEFORE | AFTER | must be |
|:--|:--|:--|:--|:--|
| `rule-base` | no rule in the docx | 0 matched / **1 lost** | 0 matched / **1 lost** | stays LOST |
| `rule-v6_pgborder` | `w:pgBorders` - Google dropped it | 0 matched / **1 lost** | 0 matched / **1 lost** | stays LOST |
| `rule-v1_drawing` | the engine's own carrier | 0 matched / 1 lost | **1 matched / 0 lost** | becomes MATCHED |
| `rule-v1b_inline` | same anchor in a body paragraph | 0 matched / 1 lost | **1 matched / 0 lost** | becomes MATCHED |
| `rule-v3_tblppr` | floating table, `tcBorders/bottom` | 1 matched / 0 lost | 1 matched / 0 lost | unchanged |
| `rule-v2_pbdr` | `w:pBdr/w:bottom` | 1 matched / 0 lost | 1 matched / 0 lost | unchanged |

Both negatives held and both positives gained. The change invents no rule where there is none and does
not paper over a rule Google genuinely lost.

**What Google actually did with the rule** - this overturns "Google drops drawings", which the corpus
tables imply and which is now false as a general statement:

| | asked | Google drew | error | chars added (`05` unit) | body text moved |
|:--|--:|--:|--:|--:|--:|
| anchor in its own carrier paragraph (today's engine) | y = 140.0 | y = **139.88** | **-0.12 pt** | 0 | 0.69 pt |
| anchor inside a body paragraph | y = 140.0 | y = **139.88** | **-0.12 pt** | 0 | **0.00 pt** |
| floating table, `tcBorders/bottom` | y = 140.0 | y = **140.50** | +0.50 pt | 0 | 0.00 pt |
| `w:pBdr` on an empty paragraph | y = 140.0 | y = 141.50 | +1.50 pt | 0 | **+19.91 pt** |
| `w:pgBorders` | y = 140.0 | not drawn | - | 0 | 0.00 pt |

Google honours the engine's own construct to a tenth of a point. The carrier paragraph costs 0.69 pt of
displacement; putting the anchor in a body paragraph costs none. The two flow-borne constructs move
everything below them by ~19 pt, which is the same 9.6 pt-per-carrier failure the 17:39 pBdr refutation
measured, and the reason that path keeps dying.

## On real corpus documents the check change is real but does NOT fix them

Two documents that fail **nothing but** `32_stroke_lines` (394_map_with_legend, 407_id_card_front_back)
were converted with the current engine, uploaded to Google Docs, exported as PDF and scored with check
32's own predicate. Source rules from the original PDF, render segments from the Google export.

| document | source rules | BEFORE matched / lost | AFTER matched / lost | clean? |
|:--|--:|:--|:--|:--|
| `394_map_with_legend` | 3 | 0 / **3** | 1 / **2** | **no** |
| `407_id_card_front_back` | 46 | 0 / **46** | 18 / **28** | **no** |

18 of 407's recovered rules are its **vertical** rules, drawn as 15.0 x 1.5 pt raster strips at exactly
the source x positions (173.1, 176.1, 195.1, 212.1, 214.6, 235.6, 246.6, 254.6 against source 174, 177,
196, 210, 214, 216, 235, 246, 254). Its 28 **horizontal** rules are genuinely not drawn. On 394 the one
recovered rule is the long one at y = 461.9 (drawn at 461.0, x 60.0 -> 399.8 against source 60.0 ->
400.0); the two legend rules at x 395.3 -> 415.3 are genuinely not drawn.

**So no document becomes clean from this change, and by the brief's own test it is therefore not a fix.**
It is a measurement correction that makes the class table honest, and it must not be committed as a
corpus fix on an unmeasured corpus.

## The lead this hands the next run

The isolated probe rule draws perfectly on a clean page. The same construct on `394` draws 1 of 3 and on
`407` draws 0 of its 28 horizontal rules. `394` carries **25 images on one page** and `407` carries **41**.
The difference between the probe and the corpus is **the page, not the construct**: Google honours the
anchor until the page is crowded. That is a new, testable hypothesis for the class and it is not the
construct question six previous attempts have been asking.

Cheap test for the next run: put N copies of the same anchored rule on one page for N = 1, 2, 4, 8, 16,
32, export once, and find the count at which Google stops placing them. If there is a threshold, the fix
is to reduce the number of separate anchored objects per page (one drawing carrying many rules), not to
change the rule construct.

## The patch, ready, deliberately not applied

    _rule_segments_with_pictures(page, band)  ->  _rule_segments(page, band) + picture bands

converting each `_stroke_pictures()` entry `{rect,width,colour}` into the segment shape
`{o,perp,a,b,t,col}` with the same band test `_rule_segments()` already applies to a filled band. Saved
as `patches/rule-segments-see-pictures.patch`. **Do not land it until a corpus pass measures the new
`32_stroke_lines` column for all 192 Google documents**, because it can only turn lost -> matched and the
size of that flip across the corpus is unmeasured.

Sources: `rule-construct-census.md` and the ten Google exports in the run's census bundle.
