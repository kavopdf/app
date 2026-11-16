# Census v2 - the displacement axis, and a path bug

## What the first census run showed

The baseline measured 213/213, advanced the phase to `classify` for the first time, and
gate.py ran the census. It censused 92 defective documents. The signals were:

    none-identified        79
    text-missing           12
    annotations-present     1

Then the numbers behind `none-identified` were checked: **48 of those 79 kept at least 95 %
of the source's characters.** Nothing was missing. Everything had moved.

The two nine-page bank forms make it plain:

    041122-Account_Opening_Form   share@5 98.65   max 937.92 pt   page 9
      src_chars 48837 -> docx_chars 48623   (99.6 % of the text is there)
      src_images 1    -> docx_images 1      (the image is there)
      signal: none-identified

The census counted what was MISSING, and the dominant defect was what MOVED. That is a
blind spot, not a bug, and it is now closed.

## The displacement axis

Four new columns, computed for the worst documents only (each one is a LibreOffice
round-trip, so the census spends its time where the fixer will look first):

    dx_pt        the rigid shift that best explains the page. Positive = output is RIGHT.
    dy_pt        the same vertically. Positive = BELOW, i.e. down the page.
    explains     how much of the overlap that one translation accounts for, in percent.
    moved_gt20   share of ink still more than 20 pt from any output ink AFTER the shift.

Read together:

    big dx/dy AND high explains         an offset or margin bug - one origin is wrong and
                                        every element inherits it, usually one small fix
    small dx/dy AND low explains        a layout bug - elements disagree, no single
                                        translation fixes the page
    high moved_gt20 with high explains  the page moved and part of it moved further

## The first method was wrong, and looked right

The first version matched every source ink pixel to its nearest output ink pixel and took
the median offset. On a block moved **+10 right, +6 down** it answered **+6, +2** - off by
40 %, because a solid block's pixels all map to the nearest EDGE of the output block rather
than to their own counterpart. The answer collapsed toward the middle and looked plausible.

Cross-correlation asks the question actually being asked - what single translation makes
these two ink masks line up - and on the same test returns exactly **+10, +6**.

    +10 right, +6 down   -> (10, 6)     exact
    -12 right, +3 down   -> (-12, 3)    exact
    identical            -> (0, 0)      exact

## The path bug

The first run recorded `census: exit1`. It still wrote valid files, which is the worst of
both - a failure that looks like a success. The cause:

    os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)

Output paths defaulted to `benchmarks/CENSUS.csv` relative to the **cwd**, and gate.py runs
the census from the repo root while the ranking lives in `/scratch/output`. Now both output
paths are derived from the `--ranking` file's own directory, so they land beside the table
they describe wherever the caller happens to be.

## Verified

Three real PDFs with real .docx outputs, end to end:

    01_stamp_rotated_15deg_upright   dx  24.0  dy  -7.7  explains 2%  moved_gt20 44%
    23_timetable_grid_txtpos         dx -34.1  dy  49.9  explains 2%  moved_gt20 65%
    62_two_col_newsletter_pull_quote dx  35.0  dy 216.0  explains 5%  moved_gt20 39%

Those .docx files were plain reflowed paragraphs, so the layout genuinely differs and a low
`explains` is the honest answer: no single translation explains those pages. The columns
are measuring the right thing - the test was designed to prove the pipeline runs and the
sign convention is right, not to grade our engine.
