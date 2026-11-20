# t08_line_order: seven of its eight measurable documents are ONE displaced line, and the line is always secondary text

20 Nov 2026, fixer, third attempt in the same slot. Census only - no engine change, no measurement to
claim. Recorded so the next run does not start from "line order is broken in ten documents".

The check (`verify_txt.py`, unmodified) buckets lines by page column, pairs only lines whose text is
unique on both sides, and takes the longest common subsequence per bucket. It fails unless EVERY
paired line is in order, so one displaced line fails a document exactly as a shuffled page would.

## The census

| document | partners | in order | out |
|---|---:|---:|---:|
| `041122-Account_Opening_Form` | - | - | no PDF in any corpus-v1 release zip |
| `Account_Opening_Form_Fillable_filled` | - | - | same |
| `09_stamp_font_not_embedded` | 16 | 15 | 1 |
| `305_vaccination_certificate` | 33 | 32 | 1 |
| `330_cad_drawing_sheet` | 33 | 32 | 1 |
| `400_comic_page_speech_bubbles` | 20 | 19 | 1 |
| `46_chart_coloured_labels_body_text` | 43 | 37 | 6 |
| `65_two_col_full_width_figure_caption` | 47 | 43 | 4 |
| `70_magazine_drop_cap_photo_caption` | 21 | 20 | 1 |
| `itr-computation-with-slab-table` | 89 | 88 | 1 |

Six of the eight measurable documents are off by exactly one line. Two are off by more.

## The line that moves, in six of them

Read out of the same bucket the check uses, the displaced line is:

* `09_stamp_font_not_embedded` - "Note: stamp applied in a non-embedded Helvetica face..."
* `305_vaccination_certificate` - "This is a computer generated certificate and does not require a physical signature."
* `330_cad_drawing_sheet` - "ALL DIMENSIONS IN MILLIMETRES UNLESS NOTED. DO NOT SCALE THIS DRAWING."
* `400_comic_page_speech_bubbles` - "I will fix it"
* `70_magazine_drop_cap_photo_caption` - "T" (the drop cap)
* `itr-computation-with-slab-table` - "Computation prepared on 12 August 2026 · AY 2027-28"

Every one is **secondary text the page set among its body lines**: a note, a disclaimer, a drawing
note, a speech bubble, a drop cap, a sub-caption. Not one is a body line, and in every case the line
is present in the .txt and in the right column - it is emitted at a different point in the sequence,
which is what a writer that lays out its primary block first and its secondary blocks afterwards
does.

## What this means for the next run

This is a plausible single mechanism: order the secondary block by its own baseline instead of
emitting it after the flow. It is NOT proven - six examples of one shape is a strong lead, not a
measurement, and the two documents off by more than one line (`46_chart_coloured_labels_body_text`,
6; `65_two_col_full_width_figure_caption`, 4) may be a different fault.

A change to block order in `TxtWriter` cannot be proven on six documents: it reorders lines in every
document that has secondary text, so it needs the whole corpus re-converted and re-scored, which is
about twenty minutes of conversion across five calls on this pod. That is why it was not attempted in
what was left of this slot, and it is written down rather than left to be rediscovered.

Also worth knowing: `t08_line_order` has zero tolerance, so any single inversion fails a document. A
fix that moves 88 of 89 paired lines into order and leaves one will read as no movement at all.
