# Step 1-3 findings — displacement ranking, diagnosis, priority

Instrument: `benchmarks/p2w.py`. Gate 14/14 (reads known truth within 1 px).
Corpus: 211 of 211 measured. Reproduced 4 times across full sandbox wipes:
median 14.88 pt, p90 57.12 pt, worst 654.24 pt.

## Step 1 — completeness
211/211 measured. The previously missing document is now included.

## Step 2 — diagnosis of the worst 19 (per-page, rendered side by side)

### A. Two "failures" are NOT defects — the metric mis-scores a correct fix
* `417_rotate180_and_mirrored` (654.24 pt, p1). Source page dict says
  `/Rotate 180`; a reader shows it upside down. Our output is upright. The
  document itself states: "A converter that ignores /Rotate outputs an upright
  document - which is what the user wants." **We did the right thing.**
* `one-page-rotated-180-degrees` (509.28 pt, p2). Source page is an upside-down
  scan; the page itself says "Rotating it by 180 degrees restores the reading
  order." Our output is upright. **We did the right thing.**

Cause: the source is rendered through PyMuPDF, which honours `/Rotate`, while
our output is already corrected. The comparison is therefore between a rotated
page and a corrected one. Fix is in the INSTRUMENT, not the engine.

### B. One genuine content loss
* `415_inline_images` (153.12 pt). Source has four black bars drawn as an
  inline image (`BI ... ID ... EI`) plus two text lines. Our output has the text
  and NO image, and the text has moved up into the freed space.
  **Cause: inline images (BI/ID/EI) are not extracted at all.**

### C. Geometry drift (systematic misalignment, not loss)
* `itr-computation-with-slab-table`, `table-inside-two-column-page`, and most of
  the 30-60 pt band. Content is present; table rules and column edges sit a few
  px off, distributed across the page.

## Step 3 — the discriminator that separates B from C

Sweeping the match tolerance and reading the SHAPE of the curve separates
missing content from misalignment, with no new threshold:

| document | @1px | @2px | @3px | @5px | @10px | median | verdict |
|---|---|---|---|---|---|---|---|
| 415_inline_images | 89.0 | 89.0 | 89.0 | 89.0 | 89.0 | 92.85 pt | CONTENT LOSS |
| itr-computation | 88.6 | 83.4 | 79.0 | 71.5 | 56.8 | 8.97 pt | GEOMETRY DRIFT |
| table-inside-two-column | 67.0 | 57.5 | 51.0 | 44.0 | 34.2 | 5.28 pt | GEOMETRY DRIFT |

Flat curve = the ink is absent, tolerance cannot help.
Falling curve = the ink is present but displaced.

## Weakness found in the metric itself

`worst_pt` (the max distance) is dominated by a single outlier pixel. On
`itr-computation` it reads 134 pt while the pages look nearly identical. The
honest headline is the pair (share at 1 px, shape of the tolerance curve), with
max reported only as an outlier indicator.

## Priority (damage x frequency, not worst number)

1. Inline images not extracted — content is LOST. Fix the mechanism, not the
   document. Highest damage per user: their image simply disappears.
2. Instrument false positives (/Rotate, corrected upside-down scan) — fix the
   comparison so the ranking stops blaming the engine for doing the right thing.
3. Geometry drift of table rules / column edges — affects the 30-60 pt band,
   35 documents, the largest block.
4. Element-level displacement (stamps) — small share, large distance, 12+
   documents.
