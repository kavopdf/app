# The 18-page OCR screenshot: measured at last, and it is clean

`Screenshot_20261029_143058_KavoPDF_searchable.pdf` was the one document the
corpus never measured. One measurement exceeded the sandbox's per-command
budget, so it was excluded and the exclusion was recorded as a coverage gap, not
a pass. It is now measured.

## Why it could not be measured before

    18 pages, each 508 x 2000 pt (about 70 cm tall)
    at 150 dpi that is 1042 x 4167 px per page -- 4.3 M pixels each

Rendering and comparing all 18 in one process ran past the per-command ceiling.
Measured page by page with progress saved after each, it completes.

## Result

    share@5px    median 0.0 %    worst 0.0 %    best 0.0 %
    clean (<1 %) 18 of 18 pages
    text recall  median 100 %    min 100 %
    max_pt       about 85 pt on every page

Every one of the 18 pages reads `none`.

## The number that would have lied

`max_pt` sits at roughly 85 on all eighteen pages. Read alone it says "85 points
out -- badly broken". Read beside `share@5px 0.0 %` it says what is actually
true: **less than one per cent of the ink is that far out**, and the bulk of the
page is exact.

This is the case the instrument was rebuilt for. An earlier version reported the
max as its headline and would have called this document a failure. The sweep and
the share are what make the reading honest; `max_pt` is kept only as an outlier
indicator.

## What it closes

The coverage gap in `REALWORLD-FINDINGS.md` listed this document as unmeasured.
It is measured. It is the only scanned multi-page document in the set, and it is
the one that comes out best -- 18 of 18 pages clean, text intact.

That is worth stating plainly because it cuts against the rest of the picture:
the two nine-page bank forms score 98.7 % and 97.6 %, while an eighteen-page OCR
screenshot scores 0.0 %. The failure is not "long documents" or "scanned
documents". It is specific to what those two forms contain, and finding out what
is the fixer's work, not the instrument's.
