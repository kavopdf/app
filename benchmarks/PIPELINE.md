# P2W measurement pipeline — the authoritative truth

Everything below is measured, not assumed. Where a number came from a guess or
an untested instrument, it says so.

## Entry point

    python3 benchmarks/p2w.py --validate     # ground-truth gate, no measuring
    python3 benchmarks/p2w.py --budget 250   # rebuild what is missing, then measure
    python3 benchmarks/p2w.py --status
    python3 benchmarks/p2w.py --diagnose 20  # per-page breakdown + rendered pairs

One file, no other dependency. A sandbox wipe costs one `git clone`.

## What is measured, and the two axes

POSITION  how far ink sits from where the source put it.
CONTENT   whether the characters are the ones the source has.

Both are required. Position alone passes a page where every glyph is swapped
for a different one of the same width. Content alone passes a page with the
right words in the wrong places.

### Position is a SWEEP, not a number

    share@1px, share@2px, share@3px, share@5px, share@10px, median_pt, p90_pt, max_pt

Two earlier instruments reported a single number and both were wrong:

* a p90 inside a tolerance radius read **0.000 on a 5 pt rigid shift**, because
  91.7 % of a moved square still overlaps — it was never measuring displacement.
* a bare `max` read **134 pt on a document whose pages looked nearly identical**,
  because one outlier pixel dominated it.

The sweep is a measurement: its SHAPE identifies the defect.

    flat curve    share barely falls as tolerance grows  -> the ink is ABSENT
    falling curve share drops sharply                    -> the ink is DISPLACED
    near zero     share ~0 at 1 px                       -> the page is RIGHT

`signature` is derived from the shape alone, with no new threshold:
`content-loss`, `displacement`, `mixed`, `clean`.

### Ranking uses share@5px, not share@1px

`share@1px` is inflated by text antialiasing: glyph edges never align to the
pixel grid, so a near-perfect text page can read 40 % at 1 px. Ranking by it
would order documents by how much text they contain. `share@5px` is above the
antialiasing band and still catches real errors. Both are reported.

## The ground-truth gate

`validate()` sets displacement BY CONSTRUCTION on synthetic pages and refuses
to measure if the instrument cannot read it back:

    1/2/5/10/20/40 pt horizontal   1/5/10 pt vertical
    diagonal (3,4) pt must read 5.00 -- proves Euclidean, not Manhattan
    identical pages must read 0.000
    ink removed must be flagged, not scored
    1 px jitter must read 0.000 -- the raster floor

Tolerance is 1 px at 150 dpi = 0.48 pt, which is the raster's own resolution,
not a chosen threshold. A run that fails this exits 3 and measures nothing.

## /Rotate

The converter deliberately ignores `/Rotate`: a page stored upright with
`/Rotate 180` must come out upright, which is what the user wants. The source
is therefore rendered with rotation forced to 0 as well. Comparing a rotated
render against an unrotated one produced a **654 pt "failure" on a document we
had handled correctly** — a defect in the instrument, not the engine.

## Ink threshold

68. Measured: paper mode 255, ink mode 51, valley 68.

## What a document that failed to measure looks like

It is written to RANKING.csv as a row with `signature = MEASURE-ERROR`.
It is never silently omitted. A ranking with a hole is not a ranking.

## Current baseline — 211 of 211

    210 measured + 1 MEASURE-ERROR (416_many_tiny_pages: soffice timeout)

    share@5px   median 0.3 %   p75 5.2 %   p90 13.1 %
    clean  (<1 %)   120 documents
    under 5 %       156 documents

    signature:  clean 68 | displacement 132 | mixed 8 | content-loss 2
    text recall below 100 %: 8 documents;  below 90 %: 0

The single most important line: **no document loses more than 10 % of its
characters.** The engine gets the words right. What it does not get right is
where the ink sits.

## Worst documents, and what each one is

    89.0 %@5  content-loss  415_inline_images
    81.6 %@5  content-loss  one-page-rotated-180-degrees
    68.8 %@5  mixed         itr-computation-with-slab-table
    63.1 %@5  mixed         600_reviewed_invoice_with_annotations
    52.4 %@5  mixed         601_fillable_admission_form
    42.0 %@5  displacement  table-inside-two-column-page
    34.4 %@5  displacement  360_restaurant_menu
    34.3 %@5  mixed         text-held-twice-shadow-text
    31.1 %@5  displacement  411_nested_xobject_transforms

`415_inline_images` is the only true content loss: four bars drawn as an inline
image (`BI ... ID ... EI`) are not extracted at all, and the text moves up into
the freed space.

`one-page-rotated-180-degrees` needs a caveat. Its text recall is 100 % and its
signature is content-loss, because the source page is an upside-down SCAN and
our output is typeset text. The ink cannot match — it is a different medium.
This is a scan-to-text conversion, and the ink metric is not the right judge of
it. Do not treat it as a defect on this number alone.

## Known limitations — stated, not hidden

1. **Position is not content.** The text axis here is a character-multiset
   recall, not an order- or word-level check. A page with correct characters in
   the wrong order scores 100 %.
2. **The corpus is 211 synthetic test PDFs.** A clean result on it does not
   prove real-world PDFs convert correctly. Real-world coverage is unproven.
3. **`/Rotate` appears on exactly one corpus document.** The handling is
   verified on that one case, not broadly.
4. **LibreOffice is the renderer proxy.** There is no Word binary in this
   environment; every score is a LibreOffice reading of the .docx.

## Rules for anything that consumes this

* Never rank by a single number. Use `signature` + `share@5px` + `max_pt`.
* Never compare two runs made with different instrument code. The instrument
  version is the thing being held constant.
* A document whose score gets worse is a regression, whatever else improved.
* Never silence a finding without first proving it is a false positive. Two of
  the three worst "failures" in the first ranking were false positives.
