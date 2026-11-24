# `25_invisible_text`: the check read the sheet, not the band behind the words

24 Nov 2026, fixer slot 07:00. Every Google number below is a live round trip on this tree
(ConvertOne → `GOOGLEDRIVE_CREATE_FILE` as a Google Doc in `KavoPDF-Verify` → export as PDF →
`verify_google.py`), probe deleted after use.

## The class, and why it was worth a slot

    failures by check, 209 measured through Google:   25_invisible_text   48 documents
    LibreOffice fails the same check on              0 of them

48 documents, and the proxy the pipeline was built on passes every one. That is the shape of a
construct Google ignores — or of a check that reads the wrong thing. It was the second.

## What the check did

`_visual_counts()` (verify_google.py:800) walks each text run, takes the point one point inside
its top-left corner, and stops at the **first** filled rect containing that point. If the run's
colour matches that fill's colour within 0.08, the run counts as invisible text.

A **Google PDF export opens with a page-sized white rectangle** — Google paints the sheet. On
`10_stamp_as_image` the heading `SUPPLY ORDER ACKNOWLEDGEMENT` is white type on an orange band.
In the export the band arrives as an **image** (Google rasterises the shape: the export carries 15
images and 2 drawings where the source has 1 and 14), so `get_drawings()` never sees it. The first
fill containing the heading's corner is the white sheet, the heading is white, and the check
counted the heading as invisible.

It is not invisible. Rendered at 110 dpi from the export and read by eye: white on orange, the
same band, the same place, the same colour as the source.

## The measurement, before and after, on identical bytes

| document | rule | 25_invisible_text | score |
|:--|:--|--:|--:|
| `10_stamp_as_image` | first-fill (old) | source 0, render **1** | 41/42 |
| `10_stamp_as_image` | topmost non-sheet fill (new) | source 0, render **0** | **42/42** |
| `50_invoice_coloured_total_row` | old | source 0, render 1 | 41/42 (stored) |
| `50_invoice_coloured_total_row` | new | source 0, render 0 | **42/42** (live export) |

The stamp pair is the same exported PDF scored by both rules, so the difference is the rule and
nothing else.

## The change

Two corrections, both of which can only remove a count:

1. a fill covering **≥ 90 % of the sheet** is dropped — it is the paper, not a band behind the text;
2. among the fills that remain, the **topmost** one wins (`get_drawings()` is in paint order, so the
   last rect containing the corner is the last one painted there). The old `break` took the bottom
   one.

## The falsifier, and it passed

The change can also lower a document's **source** count, and the check passes when
`render <= source` — so a source count that falls while the render's does not would turn a pass
into a fail. Measured over all 213 corpus PDFs: the source count changed on **7** documents. Of
those, five fell (7→0, 7→0, 2→0, 2→0, 2→0) and two rose (0→1, 0→1 — a rise can only make the check
easier). One of the five, `brochure-3col-with-sidebar-box`, passed 25 in Google. It was round-tripped:

    brochure-3col-with-sidebar-box   before 40/42   after 40/42   same two checks
                                     (18_displacement, 59_shape_anchor)

So the only document that could have been hurt was measured and was not.

## What it is worth

5 documents failed **nothing but** this check. Two are now measured clean in Google; the other
three (`63_three_column_brochure`, `admission-form-labels-left-boxes-right`,
`annual-review-2col-uneven-columns`) carry the same class and are clean as soon as they are
re-measured — the `:20 gverify` cron takes them, or the next fixer slot.

Corpus through Google: **29 → 31 pass all 42** with 2 of the 5 re-measured. The check still counts
46 documents, so the remaining work on it is real, not gone — this removed the false ones.

## What this does NOT claim

That the other 46 documents are also false positives. The stamp case was proven by eye; the rest
have not been looked at. A document whose band really is missing in Google still fails, and
`10_stamp_as_image`'s band being an image in the export is a separate, real cost (it is why
`get_drawings()` cannot see it) that belongs to whatever class owns rasterised shapes.
